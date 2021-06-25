module.exports = {
  apps: [
    {
      script: "app.js",
      env: {
        NODE_ENV: "development",
        PGDATABASE: "cexplorer",
        CARDANO_NODE_SOCKET_PATH: "cardano-node/mainnet/node.socket",
      },
      env_production: {
        NODE_ENV: "production",
      },
    },
    {
      name: "cardano-node",
      script: "./cardano-node run --socket-path mainnet/node.socket",
      cwd: "./cardano-node",
    },
    {
      name: "cardano-db-sync",
      script:
        "db-sync-node/bin/cardano-db-sync \
      --config config/mainnet-config.yaml \
      --socket-path ../cardano-node/mainnet/node.socket \
      --state-dir ledger-state/mainnet \
      --schema-dir schema/",
      cwd: "./cardano-db-sync",
      env: {
        PGPASSFILE: "config/pgpass-mainnet",
      },
    },
  ],
}
