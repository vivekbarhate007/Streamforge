#!/bin/bash
# Run dbt transformations

echo "Running dbt transformations..."

docker compose exec dbt dbt run --project-dir /dbt --profiles-dir /dbt

echo "dbt run completed!"

