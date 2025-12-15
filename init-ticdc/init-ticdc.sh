#!/bin/sh
set -e


echo "[cdc-task] Waiting for TiCDC to be ready..."
sleep 45

echo "[cdc-task] Creating changefeeds [tests, users, orders]..."
/cdc cli changefeed create \
  --server=http://ticdc:8300 \
  --sink-uri='kafka://kafka:9092/users?protocol=canal-json' \
  --changefeed-id="api-user"\
  --config /init-ticdc/ticdc-users-changefeed.toml || echo "[cdc-task] [changefeed: usesr, probably exist]"
  /cdc cli changefeed create \
  --server=http://ticdc:8300 \
  --sink-uri='kafka://kafka:9092/logins?protocol=canal-json' \
  --changefeed-id="api-login"\
  --config /init-ticdc/ticdc-logins-changefeed.toml || echo "[cdc-task] [changefeed: logins, probably exist]"
  
  

echo "[TiCDC] Done. Passing control to TiCDC server..."

