#!/bin/sh
set -e


echo "[cdc-task] Waiting for TiCDC to be ready..."
sleep 45

echo "[cdc-task] Creating changefeeds [tests, users, orders]..."
/cdc cli changefeed create \
  --server=http://ticdc:8300 \
  --sink-uri='kafka://kafka:9092/users?protocol=open-protocol' \
  --changefeed-id="api-user"\
  --config /init-ticdc/ticdc-User-changefeed.toml || echo "[cdc-task] [changefeed: usesr, probably exist]"
  /cdc cli changefeed create \
  --server=http://ticdc:8300 \
  --sink-uri='kafka://kafka:9092/orders?protocol=open-protocol' \
  --changefeed-id="api-order"\
  --config /init-ticdc/ticdc-Orders-changefeed.toml || echo "[cdc-task] [changefeed: orders, probably exist]"
  
  

echo "[TiCDC] Done. Passing control to TiCDC server..."

