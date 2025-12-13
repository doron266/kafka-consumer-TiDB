#!/bin/sh
set -e

echo "[TiCDC] Starting server..."
/cdc server \
  --pd=http://pd:2379 \
  --addr=0.0.0.0:8300 \
  --advertise-addr=ticdc:8300 \
  --log-file="" \
  --log-level=info \
  --data-dir=/data/ticdc &
SERVER_PID=$!

echo "[TiCDC] Waiting for TiCDC to be ready..."
sleep 45

echo "[TiCDC] Creating changefeed 'db-monitor'..."
/cdc cli changefeed create \
  --sink-uri="kafka://kafka:9092/tests?protocol=canal-json&kafka-version=2.4.0&partition-num=6&max-message-bytes=67108864&replication-factor=1" \
  --changefeed-id="db-monitor" || \
  echo "[TiCDC] Changefeed may already exist — skipping."

echo "[TiCDC] Done. Passing control to TiCDC server..."
wait "$SERVER_PID"
