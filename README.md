# zombits-api

## Prerequisites

Need 2 addresses:

1. Receives payments: `addr1v9w53uk45fa6h9ufjw8as235pa0n0h5j7n3d7mrfmduxjxseq4u4s`
2. Contains and sends assets: `addr1v8hzad0cqqxmklk9ckea0sxmfgzpul2anmypacycvh6l3hsstd0rs`

## Setup `cardano-node`

1. Download the Linux executabble from https://github.com/input-output-hk/cardano-node
1. Unzip it
1. Rename the resulting folder to `cardano-node`

## Setup `cardano-db-sync`

### Clone repository

```
git clone https://github.com/input-output-hk/cardano-db-sync.git
```

### Build

```
cd cardano-db-sync
git checkout 10.0.0
nix-build -A cardano-db-sync -o db-sync-node
```

## Run `cardano-node`

Run `cardano-node`:

```
pm2 start ecosystem.config.js --only cardano-node
```

Wait for sync to finish

### Create `cexplorer` database

```
PGPASSFILE=config/pgpass-mainnet scripts/postgresql-setup.sh --createdb
```

## Run `cardano-db-sync` and `app.js`

```
pm2 start ecosystem.config.js
```

### Run the postgresql client

```
psql cexplorer
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
    payment_address character varying := 'addr1v9w53uk45fa6h9ufjw8as235pa0n0h5j7n3d7mrfmduxjxseq4u4s';
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
