require("dotenv").config()
const { Client } = require("pg")
const fs = require("fs")

const client = new Client()
client.connect()

const populateTable = async () => {
  const result = await client.query(
    `select encode(ma_tx_out.name, 'escape') as asset_name from tx_out
      inner join tx on tx.id = tx_out.tx_id
      inner join ma_tx_out on tx_out.id = ma_tx_out.tx_out_id
      left join tx_in on tx_out.tx_id = tx_in.tx_out_id and tx_out.index = tx_in.tx_out_index
      where tx_in.tx_out_id is null and tx_out.address = 'addr1v8hzad0cqqxmklk9ckea0sxmfgzpul2anmypacycvh6l3hsstd0rs' and policy = '\\xad6290066292cfeef7376cd575e5d8367833ab3d8b2ac53d26ae4ecc';`
  )

  const availableZombits = result.rows
  const zombits = JSON.parse(fs.readFileSync("zombits.json"))

  const availableZombitsWithRarity = availableZombits.map(zombit => {
    const zombitId = parseInt(zombit.asset_name.replace("Zombit", ""))
    const rarity = zombits.find(zombit => zombit.id == zombitId).rarity
    return { asset_name: zombit.asset_name, rarity }
  })
  console.log(availableZombitsWithRarity)

  availableZombitsWithRarity.forEach(async zombitWithRarity => {
    let success = false
    while (!success) {
      try {
        await client.query(
          `insert into zombits_reservations (asset_name, rarity) values ($1, $2);`,
          [zombitWithRarity.asset_name, zombitWithRarity.rarity]
        )
        success = true
      } catch (error) {
        console.log(
          `Failed to insert ${zombitWithRarity.asset_name}, retrying...`
        )
      }
    }
  })
}

populateTable()
