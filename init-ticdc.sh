#!/bin/sh
set -e


echo "[TiCDC] Waiting for TiCDC to be ready..."
sleep 45

echo "[TiCDC] Creating changefeed 'db-monitor'..."
/cdc cli changefeed create \
  --server=http://ticdc:8300 \
  --sink-uri='kafka://kafka:9092/tests?protocol=canal-jason' \
  --changefeed-id="tests"
  --filter='mydb.tests' &&\
  /cdc cli changefeed create \
  --server=http://ticdc:8300 \
  --sink-uri='kafka://kafka:9092/orders?protocol=canal-jason' \
  --changefeed-id="orders"
  --filter='mydb.orders' &&\
  /cdc cli changefeed create \
    --server=http://ticdc:8300 \
  --sink-uri='kafka://kafka:9092/users?protocol=canal-jason' \
  --changefeed-id="users"
  --filter='mydb.users' && \
  echo "[TiCDC-task] [exit code: 0, massage: changefeeds created succesfully]" || ech "exit code 1"
  

echo "[TiCDC] Done. Passing control to TiCDC server..."
wait "$SERVER_PID"
