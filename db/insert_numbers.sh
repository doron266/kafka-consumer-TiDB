#!/bin/bash

i=1

while true; do
  mysql -h tidb -P 4000 -u root -e "
    USE test;
    INSERT INTO numbers (num) VALUES ($i);
  "

  echo "Inserted: $i"
  i=$((i+1))
  sleep 1
done
