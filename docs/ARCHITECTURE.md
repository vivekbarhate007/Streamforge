# StreamForge Architecture

## System Overview

StreamForge implements a modern data engineering pipeline with the following components:

### Data Flow

1. **Ingestion Layer**
   - **Streaming**: Python producer → Kafka → Spark Structured Streaming
   - **Batch**: CSV files → Spark Batch Processing

2. **Storage Layer**
   - PostgreSQL as data lake (raw tables)
   - PostgreSQL as data warehouse (curated tables)

3. **Transformation Layer**
   - dbt for SQL-based transformations
   - Star schema modeling
   - Metrics aggregation

4. **Quality Layer**
   - Great Expectations for data validation
   - Schema checks, null thresholds, uniqueness constraints

5. **Serving Layer**
   - FastAPI REST API
   - JWT authentication
   - Cached endpoints

6. **Presentation Layer**
   - Next.js dashboard
   - Real-time charts (Recharts)
   - Responsive UI (Tailwind CSS)

## Technology Stack

- **Streaming**: Kafka, Spark Structured Streaming
- **Batch**: Spark Batch Processing
- **Storage**: PostgreSQL
- **Transformations**: dbt
- **Quality**: Great Expectations
- **Backend**: FastAPI (Python)
- **Frontend**: Next.js (React/TypeScript)
- **Charts**: Recharts
- **Styling**: Tailwind CSS
- **Orchestration**: Docker Compose

## Data Model

### Raw Layer
- `raw_events`: All events from Kafka
- `raw_transactions`: Batch-loaded transactions

### Staging Layer (dbt)
- `stg_raw_events`: Cleaned events
- `stg_raw_transactions`: Cleaned transactions

### Dimension Tables
- `dim_users`: User attributes
- `dim_products`: Product catalog
- `dim_time`: Time dimension

### Fact Tables
- `fact_events`: Event facts
- `fact_transactions`: Transaction facts

### Metrics Tables
- `metrics_daily_kpis`: Daily aggregated metrics

## Pipeline Execution

### Streaming Pipeline
1. Producer generates events → Kafka topic
2. Spark Structured Streaming reads from Kafka
3. Data is parsed and validated
4. Written to `raw_events` and `fact_events`

### Batch Pipeline
1. CSV files are loaded
2. Spark batch job processes files
3. Data is validated and transformed
4. Written to `raw_transactions` and `fact_transactions`

### Transformation Pipeline
1. dbt runs staging models
2. dbt builds dimension tables
3. dbt creates fact tables
4. dbt calculates metrics

### Quality Pipeline
1. Great Expectations runs validations
2. Results are stored
3. API serves quality status

## API Endpoints

- `POST /auth/login` - Authentication
- `GET /metrics/overview` - Overview KPIs
- `GET /metrics/events_timeseries` - Event time series
- `GET /metrics/revenue_timeseries` - Revenue time series
- `GET /metrics/top_products` - Top products
- `GET /quality/latest` - Latest quality check
- `GET /health/pipelines` - Pipeline health

## Security

- JWT-based authentication
- Password hashing (bcrypt)
- CORS configuration
- Environment-based secrets

## Scalability Considerations

- Spark can scale horizontally
- Kafka supports multiple partitions
- PostgreSQL can be replicated
- API can be load-balanced
- UI can be CDN-hosted

