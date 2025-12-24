#!/bin/bash
# Run Great Expectations data quality checks

echo "Running data quality checks..."

docker compose exec dbt python /dbt/run_quality.py

echo "Quality checks completed!"

