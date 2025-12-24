#!/bin/bash
# Run Spark streaming job

echo "Starting Spark streaming job..."

docker compose exec spark spark-submit \
  --master local[*] \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.postgresql:postgresql:42.7.1 \
  /app/jobs/streaming_kafka_to_postgres.py

