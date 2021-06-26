# zombits-api

## Prerequisites

Create two keypairs and addresses.

1. One for receiving payments: `addr1v9w53uk45fa6h9ufjw8as235pa0n0h5j7n3d7mrfmduxjxseq4u4s`
2. One for holding and sending Zombits: `addr1v8hzad0cqqxmklk9ckea0sxmfgzpul2anmypacycvh6l3hsstd0rs`

## Build and run `cardano-node`

1. Download the Linux executabble from https://github.com/input-output-hk/cardano-node
2. Unzip it
3. Rename the resulting folder to `cardano-node`
4. Run cardano-node
   ```
   pm2 start ecosystem.config.js --only cardano-node
   ```
5. Wait for sync to finish

## Build and run `cardano-db-sync`

1. Install nix
    ```
    curl -L https://nixos.org/nix/install > install-nix.sh
    chmod +x install-nix.sh
    ./install-nix.sh
    rm install-nix.sh
    ```
2. Clone the Git repository
   ```
   git clone https://github.com/input-output-hk/cardano-db-sync.git
   ```
3. Build version 10.0.0 using nix
   ```
   cd cardano-db-sync
   git checkout 10.0.0
   nix-build -A cardano-db-sync -o db-sync-node
   ```
4. Setup Cardano database
   ```
   PGPASSFILE=config/pgpass-mainnet scripts/postgresql-setup.sh --createdb
   ```
5. Run cardano-db-sync
   ```
   pm2 start ecosystem.config.js --only cardano-db-sync
   ```
6. Wait for sync to finish

## Configure database for Zombits

1. Run the Postgres client for the `cexplorer` database
   ```
   psql cexplorer
   ```
2. Creaste Zombits table
   ```sql
   create table if not exists zombits_reservations (
     price numeric primary key default 10000000 + floor(random() * 1000000),
     asset_name bytea unique not null,
     sold boolean default false,
     expires_at timestamp
   );
   ```
3. Populate Zombits table
   ```sql
   insert into zombits_reservations (asset_name)
     values ('Zombit1');
   insert into zombits_reservations (asset_name)
     values ('Zombit2');
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
