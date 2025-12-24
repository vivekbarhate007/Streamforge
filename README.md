# StreamForge — End-to-End Data Engineering Pipeline

A production-quality, full-stack data engineering project demonstrating batch and streaming data pipelines with a modern analytics dashboard.

## 🎯 Project Overview

StreamForge is a complete data engineering solution that:
- **Ingests** real-time events via Kafka and batch transactions via CSV
- **Processes** data using Apache Spark (streaming + batch)
- **Stores** raw data in a data lake (PostgreSQL)
- **Transforms** data using dbt to build a star schema
- **Validates** data quality with Great Expectations
- **Serves** metrics through a FastAPI backend
- **Visualizes** KPIs in a Next.js dashboard

## 🏗️ Architecture

```
┌─────────────┐
│   Producer  │──┐
│  (Python)   │  │
└─────────────┘  │
                 │
┌─────────────┐  │    ┌──────────────┐    ┌─────────────┐
│ Batch CSV  │  │    │    Kafka     │    │    Spark     │
│   Files    │──┼───▶│   Broker     │───▶│  Streaming  │
└─────────────┘  │    └──────────────┘    └─────────────┘
                 │                              │
                 │                              ▼
                 │                        ┌─────────────┐
                 │                        │ PostgreSQL  │
                 └──────────────────────▶│ Data Lake   │
                                          └─────────────┘
                                                 │
                    ┌────────────────────────────┼────────────────────────────┐
                    │                            │                            │
                    ▼                            ▼                            ▼
            ┌──────────────┐            ┌──────────────┐            ┌──────────────┐
            │     dbt      │            │   Great      │            │   FastAPI    │
            │ Transformations│          │ Expectations │            │    API      │
            └──────────────┘            └──────────────┘            └──────────────┘
                    │                            │                            │
                    └────────────────────────────┼────────────────────────────┘
                                                 │
                                                 ▼
                                          ┌──────────────┐
                                          │   Next.js    │
                                          │   Dashboard  │
                                          └──────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Make (optional, for convenience commands)

### One-Command Setup

```bash
# Clone the repository
git clone <repository-url>
cd StreamForge

# Start all services
make up
# OR
docker compose up --build -d

# Wait ~30 seconds for services to initialize, then run demo
make demo
```

### Access the Application

- **Dashboard UI**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Kafka UI**: http://localhost:8080
- **PostgreSQL**: localhost:5432

**Default Login**: `admin` / `admin`

## 📋 Available Commands

```bash
make setup      # Create .env file from template
make up         # Start all services
make down       # Stop all services
make demo       # Run full demo pipeline
make logs       # View logs
make test       # Run tests and linting
make reset      # Wipe all data volumes
```

## 🔄 Running the Demo

The `make demo` command will:

1. Start all services (Kafka, PostgreSQL, Spark, API, UI)
2. Generate 1000 events via the producer
3. Load batch transaction CSVs
4. Run dbt transformations
5. Execute data quality checks

After running, visit http://localhost:3000 to see the dashboard with data.

## 📊 Dashboard Features

### Overview Page
- Total users, events, revenue
- Conversion rate
- Real-time metrics (events/hour, revenue today)

### Events Analytics
- Real-time event stream visualization
- Events per hour chart (last 24 hours)
- Live indicator for streaming data

### Revenue Analytics
- Daily revenue trends
- Configurable time range (7/30/90 days)
- Bar chart visualization

### Top Products
- Revenue by product
- Quantity and order counts
- Interactive charts and tables

### Data Quality
- Latest Great Expectations checkpoint results
- Pass/fail status
- Failed expectations list

### Pipeline Health
- Pipeline status (streaming, batch)
- Table row counts
- Last run timestamps
- Lag monitoring

## 🗂️ Project Structure

```
StreamForge/
├── docker-compose.yml          # Orchestration
├── Makefile                     # Convenience commands
├── README.md                    # This file
├── services/
│   ├── producer/               # Kafka event producer
│   ├── spark/                  # Spark ETL jobs
│   ├── api/                    # FastAPI backend
│   └── ui/                     # Next.js frontend
├── warehouse/
│   └── dbt/                    # dbt models and seeds
├── quality/
│   └── great_expectations/     # Data quality configs
├── data/
│   ├── batch/                  # CSV transaction files
│   └── schemas/                # JSON schemas
├── scripts/                    # Database init scripts
└── .github/
    └── workflows/              # CI/CD pipeline
```

## 🔧 Configuration

All configuration is environment-driven. Copy `.env.example` to `.env` and customize:

```bash
# Database
POSTGRES_USER=streamforge
POSTGRES_PASSWORD=streamforge123
POSTGRES_DB=streamforge

# Kafka
KAFKA_BROKER=kafka:29092
KAFKA_TOPIC=user_events

# API
API_SECRET_KEY=your-secret-key-change-in-production
DEFAULT_ADMIN_USER=admin
DEFAULT_ADMIN_PASSWORD=admin
```

## 🧪 Testing

```bash
# Run API tests
make test

# Or manually
docker compose exec api pytest /app/tests/ -v
docker compose exec api flake8 /app --max-line-length=100
```

## 📈 Adding a New Metric

1. **Create dbt model** (`warehouse/dbt/models/marts/your_metric.sql`)
2. **Add API endpoint** (`services/api/app/metrics.py`)
3. **Add route** (`services/api/app/main.py`)
4. **Create UI page** (`services/ui/src/app/dashboard/your-metric/page.tsx`)
5. **Add nav link** (`services/ui/src/components/Nav.tsx`)

## ☁️ Extending to Cloud

### AWS
- Replace Kafka with MSK
- Use S3 for data lake
- EMR for Spark
- RDS for PostgreSQL
- ECS/Fargate for containers

### GCP
- Replace Kafka with Pub/Sub
- Use Cloud Storage for data lake
- Dataproc for Spark
- Cloud SQL for PostgreSQL
- Cloud Run for containers

### Azure
- Replace Kafka with Event Hubs
- Use Data Lake Storage
- HDInsight for Spark
- Azure SQL for PostgreSQL
- Container Instances for containers

## 🐛 Troubleshooting

### Kafka won't start
```bash
# Check logs
docker compose logs kafka

# Ensure Zookeeper is healthy
docker compose ps zookeeper
```

### PostgreSQL connection errors
```bash
# Wait for database to be ready
docker compose exec postgres pg_isready -U streamforge

# Check connection from API
docker compose exec api python -c "from app.db import wait_for_db; wait_for_db()"
```

### Port conflicts
If ports 3000, 8000, 8080, or 5432 are in use:
- Stop conflicting services
- Or modify ports in `docker-compose.yml`

### Spark job fails
```bash
# Check Spark logs
docker compose logs spark

# Ensure Kafka is accessible
docker compose exec spark ping kafka
```

### UI not loading
```bash
# Check if API is running
curl http://localhost:8000/health

# Check UI logs
docker compose logs ui

# Rebuild UI
docker compose up --build ui
```

## 📝 Data Model

### Raw Tables
- `raw_events`: All ingested events from Kafka
- `raw_transactions`: Batch-loaded transactions

### Dimension Tables
- `dim_users`: User attributes
- `dim_products`: Product catalog
- `dim_time`: Time dimension

### Fact Tables
- `fact_events`: Curated event data
- `fact_transactions`: Transaction facts with revenue

### Metrics Tables
- `metrics_daily_kpis`: Aggregated daily metrics

## 🔐 Security Notes

- Default credentials are for **development only**
- Change `API_SECRET_KEY` in production
- Use environment variables for secrets
- Enable HTTPS in production
- Implement proper authentication/authorization

## 📄 License

MIT License - see LICENSE file

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📧 Support

For issues and questions, please open a GitHub issue.

---

**Built with ❤️ for data engineers**

