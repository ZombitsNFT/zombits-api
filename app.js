require("dotenv").config()
const { Client } = require("pg")
const { exec, execSync } = require("child_process")
const express = require("express")
const cors = require("cors")
const { v4: uuid } = require("uuid")

const app = express()
app.use(cors())
const client = new Client()
client.connect()

const SERVER_PORT = 3000

const RESERVATION_DURATION = "10 minutes"

const PAYMENT_ADDRESS = // Address that should receive payments
  "addr1v9w53uk45fa6h9ufjw8as235pa0n0h5j7n3d7mrfmduxjxseq4u4s"
const ZOMBITS_ADDRESS = // Address that should have the Zombits
  "addr1v8hzad0cqqxmklk9ckea0sxmfgzpul2anmypacycvh6l3hsstd0rs"
const POLICY_ID = "ad6290066292cfeef7376cd575e5d8367833ab3d8b2ac53d26ae4ecc" // Policy ID of Zombits
const PROTOCOL_PARAMS = "cli/protocol.json"

const RESERVE_QUERY = {
  text: `update zombits_reservations
set expires_at = now() + interval '${RESERVATION_DURATION}'
where price = (select price from zombits_reservations
  where not sold and (expires_at is null or expires_at < now())
  limit 1
  for update
)
returning price, expires_at;`,
}

const LISTEN_VALID_PAYMENT_QUERY = {
  text: `listen valid_payment_received;`,
}

const LISTEN_INVALID_PAYMENT_QUERY = {
  text: `listen invalid_payment_received;`,
}

client.query(LISTEN_VALID_PAYMENT_QUERY)
client.query(LISTEN_INVALID_PAYMENT_QUERY)

client.on("notification", async notification => {
  try {
    const payload = JSON.parse(notification.payload)

    switch (notification.channel) {
      case "valid_payment_received":
        await processValidPayment(payload)
        break
      case "invalid_payment_received":
        processInvalidPayment(payload)
        break
    }
  } catch (err) {
    console.log(err)
    console.log({
      error: "An error has occured while receiving a notification.",
    })
  }
})

const processValidPayment = async payload => {
  try {
    // Send Zombit (payload.asset_name) to payload.address
    console.log("VALID PAYMENT RECEIVED:", payload)

    const param1 = payload
      .map(payment => `ma_tx_out.name != '${payment.asset_name}'`)
      .join(" and ")

    const param2 = payload
      .map(payment => `name = '${payment.asset_name}'`)
      .join(" or ")

    const result1 =
      await client.query(`select tx.hash::text || '#' || tx_out.index as tx, encode(ma_tx_out.name, 'escape') as asset_name, tx_out.value::int from tx_out
  inner join tx on tx.id = tx_out.tx_id
  inner join ma_tx_out on tx_out.id = ma_tx_out.tx_out_id
  left join tx_in on tx_out.tx_id = tx_in.tx_out_id and tx_out.index = tx_in.tx_out_index
  where tx_in.tx_out_id is null and tx_out.address = '${ZOMBITS_ADDRESS}' and (${param1}) and policy = '\\x${POLICY_ID}' and ma_tx_out.tx_out_id in (
    select tx_out_id from ma_tx_out
    where (${param2}) and policy = '\\x${POLICY_ID}'
  );`)

    const io = result1.rows.reduce((rv, x) => {
      const tx = x.tx.substring(2)
      ;(rv[`${tx},${x.value}`] = rv[`${tx},${x.value}`] || []).push(
        `1 ${POLICY_ID}.${x.asset_name}`
      )
      return rv
    }, {})

    const result2 =
      await client.query(`select distinct on (tx.hash::text || '#' || tx_out.index) tx.hash::text || '#' || tx_out.index as tx, tx_out.value::int from tx_out
  inner join tx on tx.id = tx_out.tx_id
  inner join ma_tx_out on tx_out.id = ma_tx_out.tx_out_id
  left join tx_in on tx_out.tx_id = tx_in.tx_out_id and tx_out.index = tx_in.tx_out_index
  where tx_in.tx_out_id is null and tx_out.address = 'addr1v8hzad0cqqxmklk9ckea0sxmfgzpul2anmypacycvh6l3hsstd0rs' and (${param2}) and policy = '\\x${POLICY_ID}';`)
    result2.rows.forEach(row => {
      const key = `${row.tx.substring(2)},${row.value}`
      if (!Object.keys(io).includes(key)) {
        io[key] = []
      }
    })

    const inputs = Object.keys(io).map(key => {
      const values = key.split(",")
      return [values[0], parseInt(values[1])]
    })
    const outputsToUs = Object.values(io).filter(value => value.length !== 0)
    const outputsToThem = payload.map(payment => {
      return [`1 ${POLICY_ID}.${payment.asset_name}`]
    })

    // Get a non-multi-asset transaction which has at least 3 ADA (to cover fees)
    const result3 =
      await client.query(`select tx.hash::text || '#' || tx_out.index as tx, value::int from tx_out
  inner join tx on tx_out.tx_id = tx.id
  left join tx_in on tx_out.tx_id = tx_in.tx_out_id and tx_out.index = tx_in.tx_out_index
  left join ma_tx_out on tx_out.id = ma_tx_out.tx_out_id
  where tx_in.tx_out_id is null and tx_out.address = '${ZOMBITS_ADDRESS}' and ma_tx_out.tx_out_id is null and value > 3000000 limit 1;`)

    result3.rows.map(result => {
      inputs.push([result.tx.substring(2), result.value])
    })

    const inputsString = inputs.map(input => `--tx-in='${input[0]}'`).join(" ")

    console.log("io:", io)
    console.log("inputs:", inputs)
    console.log("inputsString:", inputsString)
    console.log("outputsToUs:", outputsToUs)
    console.log("outputsToThem:", outputsToThem)

    const totalInputAdaValue = inputs.reduce((prev, curr) => [
      undefined,
      prev[1] + curr[1],
    ])[1]

    let totalMinValue = 0
    const outputsToUsString = outputsToUs.map(output => {
      const outputString = output.join(" + ")

      const minValue = parseInt(
        execSync(
          `./cardano-node/cardano-cli transaction calculate-min-value --protocol-params-file=${PROTOCOL_PARAMS} --multi-asset='${outputString}'`
        )
          .toString()
          .split(" ")[1]
      )
      totalMinValue += minValue
      return `--tx-out='${ZOMBITS_ADDRESS} + ${minValue} lovelace + ${outputString}'`
    })
    const outputsToThemString = outputsToThem.map((output, i) => {
      const outputString = output.join(" + ")

      const minValue = parseInt(
        execSync(
          `./cardano-node/cardano-cli transaction calculate-min-value --protocol-params-file=${PROTOCOL_PARAMS} --multi-asset='${outputString}'`
        )
          .toString()
          .split(" ")[1]
      )
      totalMinValue += minValue
      return `--tx-out='${payload[i].sender_address} + ${minValue} lovelace + ${outputString}'`
    })

    const txOutputsDraft = `${outputsToThemString.join(
      " "
    )} ${outputsToUsString.join(" ")} --tx-out='${ZOMBITS_ADDRESS}+0'`

    // console.log(outputsToUsString)
    // console.log(outputsToThemString)
    // console.log(totalMinValue)

    const PAYMENT_ID = uuid()
    const TX_DRAFT_FILENAME = `cli/tx/${PAYMENT_ID}-tx-draft`
    const TX_FINAL_FILENAME = `cli/tx/${PAYMENT_ID}-tx-final`
    const TX_SIGNED_FILENAME = `cli/tx/${PAYMENT_ID}-tx-signed`
    const SIGNING_KEY_FILE = "cli/keys/zombits.skey" // SIGNING KEY OF ZOMBITS ADDRESS

    execSync(
      `./cardano-node/cardano-cli transaction build-raw ${inputsString} ${txOutputsDraft} --fee=0 --out-file=${TX_DRAFT_FILENAME}`
    )
    const fee = parseInt(
      execSync(
        `./cardano-node/cardano-cli transaction calculate-min-fee --tx-body-file=${TX_DRAFT_FILENAME} --tx-in-count=${
          inputs.length
        } --tx-out-count=${
          outputsToThemString.length + outputsToUsString.length + 1
        } --witness-count=1 --protocol-params-file=${PROTOCOL_PARAMS}`
      )
        .toString()
        .split(" ")[0]
    )

    const changeToUs = totalInputAdaValue - totalMinValue - fee
    const txOutputsFinal = `${outputsToThemString.join(
      " "
    )} ${outputsToUsString.join(
      " "
    )} --tx-out='${ZOMBITS_ADDRESS}+${changeToUs}'`

    execSync(
      `./cardano-node/cardano-cli transaction build-raw ${inputsString} ${txOutputsFinal} --fee=${fee} --out-file=${TX_FINAL_FILENAME}`
    )

    console.log(
      `./cardano-node/cardano-cli transaction build-raw ${inputsString} ${txOutputsFinal} --fee=${fee} --out-file=${TX_FINAL_FILENAME}`
    )

    execSync(
      `./cardano-node/cardano-cli transaction sign --tx-body-file=${TX_FINAL_FILENAME} --signing-key-file=${SIGNING_KEY_FILE} --out-file=${TX_SIGNED_FILENAME} && ./cardano-node/cardano-cli transaction submit --tx-file=${TX_SIGNED_FILENAME} --mainnet`
    )
  } catch (err) {
    console.log(err)
    console.log({
      error: "An error has occured while processing a valid payment.",
    })
  }
}

const processInvalidPayment = payload => {
  try {
    // Refund payment Zombit (payload.amount) to payload.address
    console.log("INVALID PAYMENT RECEIVED:", payload)
    // Create input parts of CLI command
    const txInputsFinal = payload
      .map(
        payment => `--tx-in=${payment.tx_hash.substring(2)}#${payment.tx_index}`
      )
      .join(" ")

    const txOutputsDraft = payload
      .map(payment => `--tx-out=${payment.sender_address}+0`)
      .join(" ")

    const REFUND_ID = uuid()
    const TX_DRAFT_FILENAME = `cli/tx/${REFUND_ID}-tx-draft`
    const TX_FINAL_FILENAME = `cli/tx/${REFUND_ID}-tx-final`
    const TX_SIGNED_FILENAME = `cli/tx/${REFUND_ID}-tx-signed`
    const SIGNING_KEY_FILE = "cli/keys/payment.skey" // SIGNING KEY OF PAYMENT ADDRESS

    const buildDraftTxCommand = `./cardano-node/cardano-cli transaction build-raw ${txInputsFinal} ${txOutputsDraft} --fee=0 --out-file=${TX_DRAFT_FILENAME}`
    exec(buildDraftTxCommand, (error, stdout, stderr) => {
      console.log(
        `${REFUND_ID} Draft transaction created:`,
        error,
        stderr,
        stdout
      )

      const calculateMinFeeCommand = `./cardano-node/cardano-cli transaction calculate-min-fee --tx-body-file=${TX_DRAFT_FILENAME} --tx-in-count=${payload.length} --tx-out-count=${payload.length} --witness-count=1 --protocol-params-file=${PROTOCOL_PARAMS}`
      exec(calculateMinFeeCommand, (error, stdout, stderr) => {
        console.log(
          `${REFUND_ID} Minimum fee calculated:`,
          error,
          stderr,
          stdout
        )

        const fee = parseInt(stdout.split(" ")[0])
        const splitFee = Math.floor(fee / payload.length)
        const remainderFee = splitFee + (fee % payload.length)

        const txOutputsFinal = payload
          .map((payment, i) => {
            if (i === payload.length - 1) {
              return `--tx-out=${payment.sender_address}+${
                payment.amount - remainderFee
              }`
            }
            return `--tx-out=${payment.sender_address}+${
              payment.amount - splitFee
            }`
          })
          .join(" ")
        const buildFinalTxCommand = `./cardano-node/cardano-cli transaction build-raw ${txInputsFinal} ${txOutputsFinal} --fee=${fee} --out-file=${TX_FINAL_FILENAME}`
        console.log(buildFinalTxCommand)
        exec(buildFinalTxCommand, (error, stdout, stderr) => {
          console.log(
            `${REFUND_ID} Final transaction created:`,
            error,
            stderr,
            stdout
          )

          const signTxCommand = `./cardano-node/cardano-cli transaction sign --tx-body-file=${TX_FINAL_FILENAME} --signing-key-file=${SIGNING_KEY_FILE} --out-file=${TX_SIGNED_FILENAME} && ./cardano-node/cardano-cli transaction submit --tx-file=${TX_SIGNED_FILENAME} --mainnet`
          exec(signTxCommand, (error, stdout, stderr) => {
            console.log(
              `${REFUND_ID} Final transaction signed and submitted:`,
              error,
              stderr,
              stdout
            )
          })
        })
      })
    })
  } catch (err) {
    console.log(err)
    console.log({
      error: "An error has occured while processing a valid payment.",
    })
  }
}

app.post("/reservations", async (req, res) => {
  try {
    const result = await client.query(RESERVE_QUERY)
    if (result.rowCount == 0) {
      res.status(503).send({ error: "No Zombits are available." })
    } else {
      res.status(201).send({
        price: result.rows[0].price,
        paymentAddress: PAYMENT_ADDRESS,
        expiresAt: result.rows[0].expires_at,
      })
    }
  } catch (err) {
    console.log(err)
    res
      .status(500)
      .send({ error: "An error has occured while making a reservation." })
  }
})

app.get("/reservations/:price", async (req, res) => {
  try {
    if (isNaN(parseInt(req.params.price))) {
      res.status(404).send({ error: "Zombit not sold." })
      return
    }
    const result = await client.query(
      `select encode(asset_name, 'escape') as asset_name, rarity from zombits_reservations as asset_name where price = $1 and sold is true`,
      [parseInt(req.params.price)]
    )
    if (result.rowCount == 0) {
      res.status(404).send({ error: "Zombit not sold." })
    } else {
      res.status(200).send({
        assetName: result.rows[0].asset_name,
        rarity: result.rows[0].rarity,
      })
    }
  } catch (err) {
    console.log(err)
    res
      .status(500)
      .send({ error: "An error has occured while checking a reservation." })
  }
})

app.get("/reservations/common/count", async (req, res) => {
  try {
    const result = await client.query(
      `select count(*) from zombits_reservations where rarity = 'Common' and sold is false;`
    )
    res.status(200).send({ common: parseInt(result.rows[0].count) })
  } catch (err) {
    console.log(err)
    res.status(500).send({
      error: "An error has occured while getting Common Zombits count.",
    })
  }
})

app.get("/reservations/uncommon/count", async (req, res) => {
  try {
    const result = await client.query(
      `select count(*) from zombits_reservations where rarity = 'Uncommon' and sold is false;`
    )
    res.status(200).send({ uncommon: parseInt(result.rows[0].count) })
  } catch (err) {
    console.log(err)
    res.status(500).send({
      error: "An error has occured while getting Uncommon Zombits count.",
    })
  }
})

app.get("/reservations/rare/count", async (req, res) => {
  try {
    const result = await client.query(
      `select count(*) from zombits_reservations where rarity = 'Rare' and sold is false;`
    )
    res.status(200).send({ rare: parseInt(result.rows[0].count) })
  } catch (err) {
    console.log(err)
    res.status(500).send({
      error: "An error has occured while getting Rare Zombits count.",
    })
  }
})

app.get("/reservations/epic/count", async (req, res) => {
  try {
    const result = await client.query(
      `select count(*) from zombits_reservations where rarity = 'Epic' and sold is false;`
    )
    res.status(200).send({ epic: parseInt(result.rows[0].count) })
  } catch (err) {
    console.log(err)
    res.status(500).send({
      error: "An error has occured while getting Epic Zombits count.",
    })
  }
})

app.get("/reservations/legendary/count", async (req, res) => {
  try {
    const result = await client.query(
      `select count(*) from zombits_reservations where rarity = 'Legendary' and sold is false;`
    )
    res.status(200).send({ legendary: parseInt(result.rows[0].count) })
  } catch (err) {
    console.log(err)
    res.status(500).send({
      error: "An error has occured while getting Legendary Zombits count.",
    })
  }
})

app.get("/reservations/theonlyone/count", async (req, res) => {
  try {
    const result = await client.query(
      `select count(*) from zombits_reservations where rarity = 'The Only One' and sold is false;`
    )
    res.status(200).send({ theOnlyOne: parseInt(result.rows[0].count) })
  } catch (err) {
    console.log(err)
    res.status(500).send({
      error: "An error has occured while getting The Only One Zombits count.",
    })
  }
})

app.listen(SERVER_PORT, () =>
  console.log(`Listening on port ${SERVER_PORT}...`)
)
