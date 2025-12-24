"""
Spark batch job that reads CSV files and loads them into PostgreSQL.
This job processes daily transaction files and writes to raw_transactions and fact_transactions.
"""
import os
import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_timestamp, date_format, lit, current_timestamp
from pyspark.sql.types import DateType

# Configuration from environment
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_USER = os.getenv("POSTGRES_USER", "streamforge")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "streamforge123")
POSTGRES_DB = os.getenv("POSTGRES_DB", "streamforge")
CSV_PATH = os.getenv("CSV_PATH", "/app/data/batch")

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
    """Main batch job"""
    print("Starting Spark batch job...")
    
    # Create Spark session
    spark = SparkSession.builder \
        .appName("CSVToPostgresBatch") \
        .config("spark.jars.packages", "org.postgresql:postgresql:42.7.1") \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("WARN")
    
    # Read all CSV files from batch directory
    print(f"Reading CSV files from: {CSV_PATH}")
    try:
        transactions_df = spark.read \
            .option("header", "true") \
            .option("inferSchema", "true") \
            .csv(f"{CSV_PATH}/*.csv")
        
        print(f"Loaded {transactions_df.count()} transactions")
        
        # Transform data
        processed_df = transactions_df \
            .withColumn("ts", to_timestamp(col("ts"), "yyyy-MM-dd HH:mm:ss")) \
            .withColumn("price", col("price").cast("double")) \
            .withColumn("quantity", col("quantity").cast("int")) \
            .withColumn("created_at", current_timestamp()) \
            .select(
                col("tx_id"),
                col("ts"),
                col("user_id"),
                col("product_id"),
                col("price"),
                col("quantity"),
                col("country"),
                col("channel"),
                col("created_at")
            )
        
        # Write to raw_transactions
        print("Writing to raw_transactions...")
        write_to_postgres(processed_df, "raw_transactions", mode="append")
        print(f"Wrote {processed_df.count()} rows to raw_transactions")
        
        # Create fact_transactions with revenue calculation
        fact_df = processed_df \
            .withColumn("revenue", col("price") * col("quantity")) \
            .withColumn("date", date_format(col("ts"), "yyyy-MM-dd").cast("date")) \
            .select(
                col("ts"),
                col("user_id"),
                col("product_id"),
                col("price"),
                col("quantity"),
                col("revenue"),
                col("country"),
                col("channel"),
                col("date")
            )
        
        # Write to fact_transactions
        print("Writing to fact_transactions...")
        write_to_postgres(fact_df, "fact_transactions", mode="append")
        print(f"Wrote {fact_df.count()} rows to fact_transactions")
        
        print("Batch job completed successfully!")
        
    except Exception as e:
        print(f"Error in batch job: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    finally:
        spark.stop()


if __name__ == "__main__":
    main()

