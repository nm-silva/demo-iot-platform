# Define variables
SHELL := /bin/bash
export PYTHONPATH := $(shell pwd)

# Default target
all: install

# Install dependencies
install:
	@echo "Installing dependencies with Poetry..."
	poetry install

# Install development dependencies
install-dev:
	@echo "Installing development dependencies with Poetry..."
	poetry install --with dev

# Clean up unnecessary files
clean:
	@echo "Cleaning up..."
	rm -rf .mypy_cache .pytest_cache .ruff_cache
	rm -rf .coverage htmlcov test_coverage_report.html coverage.xml
	rm -f resources/database.db
	rm -rf poetry.lock
	rm -rf .venv
	-docker ps -aq --filter "volume=demo-iot-platform_data" | xargs -r docker rm -f
	-docker volume rm -f demo-iot-platform_data || true

# Run the application locally
run:
	poetry run uvicorn app.app:app --host 0.0.0.0 --port 5555 --reload --ws websockets

# Run the application locally with a pre-built database
run-default: resources/database.db
	poetry run uvicorn app.app:app --host 0.0.0.0 --port 5555 --reload --ws websockets

resources/database.db: resources/template_database.db
	cp resources/template_database.db resources/database.db

# Build and run the Docker image
run-docker:
	docker build -t demo-iot-platform .
	docker run -d -p 5555:5555 -v demo-iot-platform_data:/app/resources demo-iot-platform

# Build and run the Docker image with a pre-built database
run-docker-default:
	docker build --build-arg COPY_DB=true -t demo-iot-platform .
	docker run -d -p 5555:5555 -v demo-iot-platform_data:/app/resources demo-iot-platform

# Run the websocket test script
run-ws-test:
	poetry run python tests/ws_client_test.py

test:
	@echo "Running tests with coverage and creating badge..."
	poetry run pytest --cov=./ --cov-report=term --cov-report=xml --cov-report=html:test_coverage_report.html tests/
	poetry run genbadge coverage --input-file=coverage.xml --output-file=coverage-badge.svg

.PHONY: all install install-dev clean run run-docker run-docker-default run-ws-test test