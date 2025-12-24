#!/bin/bash
# Run Spark batch job

echo "Starting Spark batch job..."

docker compose exec spark spark-submit \
  --master local[*] \
  --packages org.postgresql:postgresql:42.7.1 \
  /app/jobs/batch_csv_to_postgres.py

