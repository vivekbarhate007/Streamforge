#!/bin/bash
# Start Spark pipelines

echo "🚀 Starting Spark Streaming Job..."
docker compose exec -d spark bash -c "spark-submit --master 'local[*]' --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.1,org.postgresql:postgresql:42.7.1 /app/jobs/streaming_kafka_to_postgres.py"

sleep 5

echo "📦 Starting Spark Batch Job..."
docker compose exec spark bash -c "spark-submit --master 'local[*]' --packages org.postgresql:postgresql:42.7.1 /app/jobs/batch_csv_to_postgres.py"

echo "✅ Pipelines started! Check the dashboard to see updated status."

