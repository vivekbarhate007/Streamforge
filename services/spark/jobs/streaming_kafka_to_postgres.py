"""
Spark Structured Streaming job that reads from Kafka and writes to PostgreSQL.
This job processes real-time events and writes them to both raw_events and fact_events tables.
"""
import os
import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, from_json, to_timestamp, lit, current_timestamp, date_format, when, regexp_replace
)
from pyspark.sql.types import (
    StructType, StructField, StringType, DoubleType, IntegerType, TimestampType
)

# Configuration from environment
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:29092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "user_events")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_USER = os.getenv("POSTGRES_USER", "streamforge")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "streamforge123")
POSTGRES_DB = os.getenv("POSTGRES_DB", "streamforge")
CHECKPOINT_DIR = os.getenv("SPARK_CHECKPOINT_DIR", "/tmp/spark-checkpoints/kafka-streaming")

# Define schema for events
EVENT_SCHEMA = StructType([
    StructField("ts", StringType(), True),
    StructField("user_id", StringType(), True),
    StructField("session_id", StringType(), True),
    StructField("event_type", StringType(), True),
    StructField("product_id", StringType(), True),
    StructField("price", DoubleType(), True),
    StructField("quantity", IntegerType(), True),
    StructField("metadata", StringType(), True),
])

POSTGRES_URL = f"jdbc:postgresql://{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
POSTGRES_PROPERTIES = {
    "user": POSTGRES_USER,
    "password": POSTGRES_PASSWORD,
    "driver": "org.postgresql.Driver"
}


def write_to_postgres(df, table_name, mode="append"):
    """Write DataFrame to PostgreSQL table"""
    df.write \
        .mode(mode) \
        .jdbc(
            url=POSTGRES_URL,
            table=table_name,
            properties=POSTGRES_PROPERTIES
        )


def main():
    """Main streaming job"""
    print("Starting Spark Structured Streaming job...")
    
    # Create Spark session
    spark = SparkSession.builder \
        .appName("KafkaToPostgresStreaming") \
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.1,org.postgresql:postgresql:42.7.1") \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("WARN")
    
    # Read from Kafka
    print(f"Reading from Kafka topic: {KAFKA_TOPIC}")
    kafka_df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA_BROKER) \
        .option("subscribe", KAFKA_TOPIC) \
        .option("startingOffsets", "earliest") \
        .option("failOnDataLoss", "false") \
        .load()
    
    # Parse JSON from Kafka value
    events_df = kafka_df.select(
        from_json(col("value").cast("string"), EVENT_SCHEMA).alias("event")
    ).select("event.*")
    
    # Transform and clean data
    # Handle timestamp parsing - support both with and without microseconds
    processed_df = events_df \
        .withColumn("ts", 
            when(col("ts").rlike("\\.[0-9]{6}Z$"), 
                to_timestamp(col("ts"), "yyyy-MM-dd'T'HH:mm:ss.SSSSSS'Z'")
            ).otherwise(
                to_timestamp(col("ts"), "yyyy-MM-dd'T'HH:mm:ss.SSS'Z'")
            )
        ) \
        .withColumn("created_at", current_timestamp()) \
        .withColumn("metadata_json", col("metadata").cast("string")) \
        .select(
            col("ts"),
            col("user_id"),
            col("session_id"),
            col("event_type"),
            col("product_id"),
            col("price"),
            col("quantity"),
            col("metadata_json"),
            col("created_at")
        )
    
    # Write to raw_events table
    def write_raw_events(batch_df, batch_id):
        """Write batch to raw_events"""
        try:
            write_to_postgres(batch_df, "raw_events", mode="append")
            print(f"Batch {batch_id}: Wrote {batch_df.count()} events to raw_events")
        except Exception as e:
            print(f"Error writing batch {batch_id} to raw_events: {e}")
    
    # Write to fact_events table (curated)
    def write_fact_events(batch_df, batch_id):
        """Write batch to fact_events"""
        try:
            fact_df = batch_df \
                .withColumn("date", date_format(col("ts"), "yyyy-MM-dd").cast("date")) \
                .select(
                    col("ts"),
                    col("user_id"),
                    col("session_id"),
                    col("event_type"),
                    col("product_id"),
                    col("price"),
                    col("quantity"),
                    col("date")
                )
            write_to_postgres(fact_df, "fact_events", mode="append")
            print(f"Batch {batch_id}: Wrote {fact_df.count()} events to fact_events")
        except Exception as e:
            print(f"Error writing batch {batch_id} to fact_events: {e}")
    
    # Start streaming query
    query = processed_df.writeStream \
        .outputMode("append") \
        .foreachBatch(lambda df, batch_id: (
            write_raw_events(df, batch_id),
            write_fact_events(df, batch_id)
        )) \
        .option("checkpointLocation", CHECKPOINT_DIR) \
        .trigger(processingTime="10 seconds") \
        .start()
    
    print("Streaming query started. Waiting for termination...")
    query.awaitTermination()


if __name__ == "__main__":
    main()

