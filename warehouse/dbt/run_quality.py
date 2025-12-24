"""
Script to run Great Expectations data quality checks and track runs
"""
import os
import sys
import great_expectations as ge
from great_expectations.core.batch import RuntimeBatchRequest
from great_expectations.data_context import BaseDataContext
from great_expectations.data_context.types.base import DataContextConfig
from datetime import datetime
import psycopg2

# Database connection
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_USER = os.getenv("POSTGRES_USER", "streamforge")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "streamforge123")
POSTGRES_DB = os.getenv("POSTGRES_DB", "streamforge")

CONNECTION_STRING = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

def record_ge_run(status="completed", expectations_passed=0, expectations_failed=0, error_message=None):
    """Record Great Expectations run in pipeline_health table"""
    try:
        conn = psycopg2.connect(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            database=POSTGRES_DB
        )
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO pipeline_health (pipeline_name, last_run_ts, status, rows_processed, error_message)
            VALUES (%s, %s, %s, %s, %s)
        """, ("great_expectations", datetime.utcnow(), status, expectations_passed, error_message))
        
        conn.commit()
        cur.close()
        conn.close()
        print(f"✅ Recorded GE run: {status}")
    except Exception as e:
        print(f"⚠️ Failed to record GE run: {e}")

def main():
    """Run data quality checks"""
    print("Running Great Expectations data quality checks...")
    
    # Initialize context
    context = ge.get_context()
    
    # Create datasource
    datasource_config = {
        "name": "postgres_datasource",
        "class_name": "Datasource",
        "execution_engine": {
            "class_name": "SqlAlchemyExecutionEngine",
            "connection_string": CONNECTION_STRING,
        },
        "data_connectors": {
            "default_runtime_data_connector": {
                "class_name": "RuntimeDataConnector",
                "batch_identifiers": ["default_identifier_name"],
            },
        },
    }
    
    context.add_datasource(**datasource_config)
    
    # Define expectations for raw_events
    batch_request = RuntimeBatchRequest(
        datasource_name="postgres_datasource",
        data_connector_name="default_runtime_data_connector",
        data_asset_name="raw_events",
        runtime_parameters={"query": "SELECT * FROM raw_events LIMIT 1000"},
        batch_identifiers={"default_identifier_name": "default_identifier"},
    )
    
    validator = context.get_validator(batch_request=batch_request)
    
    # Add expectations
    validator.expect_table_row_count_to_be_between(min_value=0)
    validator.expect_column_values_to_not_be_null("ts")
    validator.expect_column_values_to_not_be_null("user_id")
    validator.expect_column_values_to_not_be_null("event_type")
    validator.expect_column_values_to_be_in_set(
        "event_type", ["view", "click", "add_to_cart", "purchase"]
    )
    validator.expect_column_values_to_be_between("price", min_value=0, mostly=0.95)
    validator.expect_column_values_to_be_between("quantity", min_value=0, mostly=0.95)
    
    # Save checkpoint
    checkpoint_config = {
        "name": "raw_events_checkpoint",
        "config_version": 1.0,
        "class_name": "SimpleCheckpoint",
        "validations": [
            {
                "batch_request": batch_request,
                "expectation_suite_name": "raw_events_suite",
            }
        ],
    }
    
    context.add_checkpoint(**checkpoint_config)
    
    # Run checkpoint
    checkpoint_result = context.run_checkpoint(
        checkpoint_name="raw_events_checkpoint",
    )
    
    print("Data quality check completed!")
    print(f"Success: {checkpoint_result['success']}")
    
    # Count passed/failed expectations
    expectations_passed = 0
    expectations_failed = 0
    
    if 'run_results' in checkpoint_result:
        for result in checkpoint_result.get('run_results', {}).values():
            if 'validation_result' in result:
                validation = result['validation_result']
                if 'results' in validation:
                    for exp_result in validation['results']:
                        if exp_result.get('success', False):
                            expectations_passed += 1
                        else:
                            expectations_failed += 1
    
    # Record the run
    if checkpoint_result['success']:
        record_ge_run(status="completed", expectations_passed=expectations_passed, expectations_failed=expectations_failed)
    else:
        record_ge_run(status="failed", expectations_passed=expectations_passed, expectations_failed=expectations_failed, error_message="Some expectations failed")
    
    if not checkpoint_result['success']:
        print("Some expectations failed. Check the results above.")
        sys.exit(1)


if __name__ == "__main__":
    main()

