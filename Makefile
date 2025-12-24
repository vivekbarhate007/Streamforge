.PHONY: setup up down demo logs test reset clean

setup:
	@echo "Setting up StreamForge..."
	@if [ ! -f .env ]; then cp .env.example .env; echo "Created .env file"; fi
	@echo "Setup complete. Edit .env if needed."

up:
	@echo "Starting StreamForge stack..."
	@which docker-compose > /dev/null && docker-compose up --build -d || docker compose up --build -d
	@echo "Waiting for services to be healthy..."
	@sleep 10
	@echo "StreamForge is running!"
	@echo "UI: http://localhost:3000"
	@echo "API: http://localhost:8000"
	@echo "Kafka UI: http://localhost:8080"

down:
	@echo "Stopping StreamForge stack..."
	@which docker-compose > /dev/null && docker-compose down || docker compose down

demo: up
	@echo "Running demo pipeline..."
	@sleep 15
	@DOCKER_COMPOSE=$$(which docker-compose || echo "docker compose"); \
	echo "1. Starting event producer..."; \
	$$DOCKER_COMPOSE exec -d producer python producer.py; \
	sleep 5; \
	echo "2. Running batch load..."; \
	$$DOCKER_COMPOSE exec spark spark-submit --master local[*] /app/jobs/batch_csv_to_postgres.py; \
	sleep 5; \
	echo "3. Running dbt transformations..."; \
	$$DOCKER_COMPOSE exec dbt python /dbt/run_dbt_with_tracking.py || true; \
	sleep 5; \
	echo "4. Running data quality checks..."; \
	$$DOCKER_COMPOSE exec dbt python /dbt/run_quality.py || true; \
	echo "Demo complete! Check the UI at http://localhost:3000"

logs:
	@which docker-compose > /dev/null && docker-compose logs -f || docker compose logs -f

test:
	@echo "Running tests..."
	@DOCKER_COMPOSE=$$(which docker-compose || echo "docker compose"); \
	$$DOCKER_COMPOSE exec api pytest /app/tests/ -v; \
	echo "Running linter..."; \
	$$DOCKER_COMPOSE exec api flake8 /app --max-line-length=100 --ignore=E501,W503

reset:
	@echo "WARNING: This will delete all data volumes!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		DOCKER_COMPOSE=$$(which docker-compose || echo "docker compose"); \
		$$DOCKER_COMPOSE down -v; \
		echo "Volumes deleted."; \
	fi

clean:
	@DOCKER_COMPOSE=$$(which docker-compose || echo "docker compose"); \
	$$DOCKER_COMPOSE down -v; \
	docker system prune -f

