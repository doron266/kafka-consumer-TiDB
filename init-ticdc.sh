#!/bin/sh
set -e


echo "[cdc-task] Waiting for TiCDC to be ready..."
sleep 45

echo "[cdc-task] Creating changefeeds [tests, users, orders]..."
/cdc cli changefeed create \
  --server=http://ticdc:8300 \
  --sink-uri='kafka://kafka:9092/tests?protocol=open-protocol' \
  --changefeed-id="tests"\
  --filter='mydb.tests' || echo "[cdc-task] [changefeed: tests, probably exist]"
  /cdc cli changefeed create \
  --server=http://ticdc:8300 \
  --sink-uri='kafka://kafka:9092/orders?protocol=open-protocol' \
  --changefeed-id="orders"\
  --filter='mydb.orders' || echo "[cdc-task] [changefeed: orders, probably exist]"
  /cdc cli changefeed create \
    --server=http://ticdc:8300 \
  --sink-uri='kafka://kafka:9092/users?protocol=open-protocol' \
  --changefeed-id="users"\
  --filter='mydb.users' || echo "[cdc-task] [changefeed: users, probably exist]"
  echo "[TiCDC-task] [exit code: 0, massage: changefeeds created succesfully]" || echo "exit code 1"
  

echo "[TiCDC] Done. Passing control to TiCDC server..."
wait "$SERVER_PID"
