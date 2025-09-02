# Makefile for E-Commerce DDD Project

SHELL := /bin/bash
COMPOSE_PROJECT_NAME ?= ecommerce_ddd
CONTAINER_NAME = ecommerce
POSTGRES_CONTAINER_NAME = ecommerce-postgres
POETRY = poetry

# Ensure this path matches the location of your main FastAPI app
APP_MODULE ?= src.main:app

.PHONY: help build up down restart logs shell-app ps clean lint test seed-data

# Default command: Show help
help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  help           Show this help message."
	@echo "  build          Build or rebuild services."
	@echo "  up             Create and start containers in detached mode."
	@echo "  down           Stop and remove containers, networks, images, and volumes."
	@echo "  restart        Restart services."
	@echo "  logs           Follow log output from services."
	@echo "  shell-app      Access a shell inside the running 'app' service container."
	@echo "  ps             List containers."
	@echo "  clean          Remove build artifacts, Python cache, and Docker volumes."
	@echo "  lint           Run linting checks with ruff."
	@echo "  lint-fix       Run linting checks and auto-fix issues."
	@echo "  format         Format code with ruff."
	@echo "  type-check     Run type checking with mypy."
	@echo "  test           Run tests."
	@echo "  test-coverage  Run tests with coverage report."
	@echo "  seed-data      Run a script to seed initial data (placeholder - implement this)."

# Build services
build:
	docker compose -p $(COMPOSE_PROJECT_NAME) build

# Create and start containers in detached mode
up:
	mkdir -p ./db # Ensure the db directory exists before mounting
	docker compose -p $(COMPOSE_PROJECT_NAME) up -d

dock:
	docker compose up -d && docker attach $(CONTAINER_NAME)

# Stop and remove containers, networks
down:
	docker compose -p $(COMPOSE_PROJECT_NAME) down

# Restart services
restart:
	docker compose -p $(COMPOSE_PROJECT_NAME) restart

# Follow log output
logs:
	docker compose -p $(COMPOSE_PROJECT_NAME) logs -f

# Access a shell inside the 'app' service container
shell-app:
	docker compose -p $(COMPOSE_PROJECT_NAME) exec app bash

# List containers
ps:
	docker compose -p $(COMPOSE_PROJECT_NAME) ps

# Remove Docker build artifacts, Python cache, and optionally Docker volumes
clean:
	@echo "Cleaning up..."
	# Stop and remove containers, networks defined in docker-compose
	-docker compose -p $(COMPOSE_PROJECT_NAME) down --volumes --remove-orphans
	# Remove any remaining Docker images built by compose (optional, can be aggressive)
	# -docker compose -p $(COMPOSE_PROJECT_NAME) rm -fsv
	# Remove python cache files
	find . -type f -name '*.py[co]' -delete
	find . -type d -name '__pycache__' -exec rm -rf {} +
	# Remove .pytest_cache and coverage files
	rm -rf .pytest_cache .coverage htmlcov
	# Remove build artifacts
	rm -rf build dist *.egg-info
	# Remove the local SQLite db directory if it was created
	# Be careful with this if you have important data!
	# rm -rf ./db
	@echo "Cleanup complete."

# Linting and formatting
lint:
	$(POETRY) run ruff check .

lint-fix:
	$(POETRY) run ruff check --fix .

format:
	$(POETRY) run ruff format .

type-check:
	$(POETRY) run mypy src

# Testing
test:
	$(POETRY) run pytest tests/

test-coverage:
	$(POETRY) run pytest --cov=src --cov-report=html --cov-report=term-missing tests/

test-watch:
	$(POETRY) run pytest-watch tests/

# Placeholder for seeding data
seed-data:
	@echo "Data seeding not yet implemented. Create a script and run it here."
	@echo "Example (assuming you have a script src/scripts/seed.py):"
	@echo "  docker compose -p $(COMPOSE_PROJECT_NAME) exec app python src/scripts/seed.py"
	# docker compose -p $(COMPOSE_PROJECT_NAME) exec app python src/scripts/seed.py

psql:
	docker exec -it $(POSTGRES_CONTAINER_NAME) psql -U $(POSTGRES_USER) -d $(POSTGRES_DB)

check-migrations:
	docker exec -it $(CONTAINER_NAME) alembic check

generate-migration:
	@read -p "Enter migration message: " message; \
	docker exec -it $(CONTAINER_NAME) alembic revision --autogenerate -m "$$message"

migrate:
	docker exec -it $(CONTAINER_NAME) alembic upgrade head
