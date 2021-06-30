# Zombits Server and API Setup

## Requirements

- Linux machine with at least 16GB RAM, 80GB storage

## Prerequisites

1. Create two keypairs and addresses.
   - One for receiving payments: `addr1v9w53uk45fa6h9ufjw8as235pa0n0h5j7n3d7mrfmduxjxseq4u4s`
   - One for holding and sending Zombits: `addr1v8hzad0cqqxmklk9ckea0sxmfgzpul2anmypacycvh6l3hsstd0rs`
2. Install `pm2`
   ```bash
   npm install -g pm2
   ```

## Build and run `cardano-node`

1. Download and unzip the latest hydra binary from https://github.com/input-output-hk/cardano-node/releases
2. Rename the resulting folder to `cardano-node`
3. Run cardano-node
   ```bash
   pm2 start ecosystem.config.js --only cardano-node
   ```
4. Wait for sync to finish

## Build and run `cardano-db-sync`

1. Install nix
   ```bash
   curl -L https://nixos.org/nix/install > install-nix.sh
   chmod +x install-nix.sh
   ./install-nix.sh
   rm install-nix.sh
   ```
2. Clone the Git repository
   ```bash
   git clone https://github.com/input-output-hk/cardano-db-sync.git
   ```
3. Build latest release using nix
   ```bash
   cd cardano-db-sync
   git checkout 9.0.0 # latest release
   nix-build -A cardano-db-sync -o db-sync-node
   ```
4. Setup Cardano database
   ```bash
   PGPASSFILE=config/pgpass-mainnet scripts/postgresql-setup.sh --createdb
   ```
5. Run cardano-db-sync
   ```bash
   pm2 start ecosystem.config.js --only cardano-db-sync
   ```
6. Wait for sync to finish

## Configure database for Zombits

1. Run the Postgres client for the `cexplorer` database
   ```bash
   psql cexplorer
   ```
2. Creaste Zombits table
   ```sql
   create table if not exists zombits_reservations (
     price numeric primary key default 10000000 + floor(random() * 1000000),
     asset_name bytea unique not null,
     rarity character varying not null,
     sold boolean default false,
     expires_at timestamp
   );
   ```
3. Populate Zombits table
   ```sql
   insert into zombits_reservations (asset_name, rarity)
     values ('Zombit1', 'Common');
   insert into zombits_reservations (asset_name, rarity)
     values ('Zombit2', 'Common);
   ...
   ```
4. Create notification function

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

5. Create trigger

   ```sql
   create constraint trigger block_insert
     after insert on block
     deferrable initially deferred
     for each row
     execute procedure notify_block_payments_received();
   ```
