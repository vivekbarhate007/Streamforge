# Quick Start Guide

## Prerequisites

1. **Install Docker Desktop**
   - macOS: Download from https://www.docker.com/products/docker-desktop/
   - Windows: Download from https://www.docker.com/products/docker-desktop/
   - Linux: Install Docker Engine and Docker Compose

2. **Start Docker Desktop**
   - Make sure Docker Desktop is running before proceeding

3. **Verify Installation**
   ```bash
   docker --version
   docker compose version
   ```

## Running the Project

### Step 1: Start All Services

```bash
# Option 1: Using Makefile
make up

# Option 2: Using Docker Compose directly
docker compose up --build -d
```

This will start:
- Zookeeper & Kafka (streaming)
- PostgreSQL (database)
- Spark (ETL jobs)
- Producer (event generator)
- dbt (transformations)
- FastAPI (backend API)
- Next.js (frontend UI)

### Step 2: Wait for Services to Initialize

Wait approximately 30-60 seconds for all services to be healthy. You can check status with:

```bash
docker compose ps
```

### Step 3: Run the Demo Pipeline

```bash
# Option 1: Using Makefile
make demo

# Option 2: Manual steps
# 1. Start event producer
docker compose exec -d producer python producer.py

# 2. Run batch load
docker compose exec spark spark-submit --master local[*] /app/jobs/batch_csv_to_postgres.py

# 3. Run dbt transformations
docker compose exec dbt dbt run --project-dir /dbt --profiles-dir /dbt

# 4. Run quality checks
docker compose exec dbt python /dbt/run_quality.py
```

### Step 4: Access the Application

- **Dashboard UI**: http://localhost:3000
  - Login: `admin` / `admin`
  
- **API Documentation**: http://localhost:8000/docs

- **Kafka UI**: http://localhost:8080

## Troubleshooting

### Services won't start
```bash
# Check logs
docker compose logs

# Check specific service
docker compose logs kafka
docker compose logs postgres
docker compose logs api
```

### Port conflicts
If ports 3000, 8000, 8080, or 5432 are already in use:
- Stop the conflicting service
- Or modify ports in `docker-compose.yml`

### Database connection errors
```bash
# Wait for database to be ready
docker compose exec postgres pg_isready -U streamforge

# Check database logs
docker compose logs postgres
```

### Reset everything
```bash
# Stop and remove all containers and volumes
make reset
# OR
docker compose down -v
```

## Useful Commands

```bash
# View logs
make logs
# OR
docker compose logs -f

# Stop services
make down
# OR
docker compose down

# Run tests
make test

# Check service status
docker compose ps

# Access a service shell
docker compose exec api bash
docker compose exec postgres psql -U streamforge -d streamforge
```

## Next Steps

1. Explore the dashboard at http://localhost:3000
2. Check the API docs at http://localhost:8000/docs
3. View Kafka topics at http://localhost:8080
4. Read the full README.md for architecture details

