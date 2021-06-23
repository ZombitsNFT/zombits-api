# zombits-api

## Prerequisites

Need 2 addresses:
1. Receives payments: `addr_test1vr3jr8rjt47ah4spvhjm3jkq9gn65657thvsn64jvxtaatgx6pgwf`
2. Contains and sends assets: `addr_test1vpjhck8puveya5qgd4uxe4arjzahxf4c2rkkstvt38c285q40majy`

## Setup .env

```
PGDATABASE=testnet
CARDANO_NODE_SOCKET_PATH=cardano-node/state-node-testnet/node.socket
```

## Setup Cardano Node

### Clone Cardano Node

### 

### Start Cardano Node

```
./testnet-node-local/bin/cardano-node-testnet
```

## Setup Cardano DB Sync

### Start Cardano DB Sync

```
PGPASSFILE=config/pgpass-testnet db-sync-node/bin/cardano-db-sync --schema-dir schema --socket-path ../cardano-node/state-node-testnet/node.socket --state-dir ledger-state/testnet --config config/testnet-config\ 2.json
```

### Run the postgresql client

```
PGPASSFILE=config/pgpass-testnet psql testnet
```

### Create Zombits table

```sql
create table if not exists zombits_reservations (
  price numeric primary key default 10000000 + floor(random() * 1000000),
  asset_name bytea unique not null,
  sold boolean default false,
  expires_at timestamp
);
```

### Populate Zombits table

```sql
insert into zombits_reservations (asset_name)
  values ('Zombit1');
...
insert into zombits_reservations (asset_name)
  values ('ZombitX');
```

### Create function

```sql
create or replace function notify_block_payments_received() returns trigger as $$
  declare
    payment_address character varying := 'addr_test1vr3jr8rjt47ah4spvhjm3jkq9gn65657thvsn64jvxtaatgx6pgwf';
    valid_payments json;
    invalid_payments json;
  begin
    -- Create JSON array of valid payments received in block
    select json_agg(json_build_object('sender_address', input.address, 'asset_name', encode(zombits_reservations.asset_name, 'escape'))) into valid_payments from tx_out
      inner join tx on tx.id = tx_out.tx_id
      inner join tx_in on tx_out.tx_id = tx_in.tx_in_id
      inner join tx_out as input on input.tx_id = tx_in.tx_out_id and input.index = tx_in.tx_out_index
      inner join zombits_reservations on tx_out.value = zombits_reservations.price
      where tx.block_id = new.id and tx_out.address = payment_address and zombits_reservations.sold is false;

    -- Create JSON array of invalid payments received in block
    select json_agg(json_build_object('sender_address', input.address, 'amount', tx_out.value, 'tx_hash', tx.hash, 'tx_index', tx_out.index)) into invalid_payments from tx_out
      inner join tx on tx.id = tx_out.tx_id
      inner join tx_in on tx_out.tx_id = tx_in.tx_in_id
      inner join tx_out as input on input.tx_id = tx_in.tx_out_id and input.index = tx_in.tx_out_index
      left join zombits_reservations on tx_out.value = zombits_reservations.price
      where tx.block_id = new.id and tx_out.address = payment_address and (zombits_reservations.price is null or zombits_reservations.sold is true);

    if valid_payments is not null then
      -- Set paid-for Zombits as sold
      update zombits_reservations
        set sold = true
        where encode(asset_name, 'escape') in (select valid_payments_json->>'asset_name' from json_array_elements(valid_payments) valid_payments_json);
      perform pg_notify('valid_payment_received', valid_payments::text);
    end if;

    if invalid_payments is not null then
      perform pg_notify('invalid_payment_received', invalid_payments::text);
    end if;

    return new;
  end;
$$ language plpgsql;
```

### Create trigger

```sql
create constraint trigger block_insert
  after insert on block
  deferrable initially deferred
  for each row
  execute procedure notify_block_payments_received();
```
