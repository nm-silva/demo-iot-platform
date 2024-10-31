# Define variables
VENV_DIR := .venv
SHELL := /bin/bash
export PYTHONPATH := $(shell pwd)

# Default target
all: install

venv:
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "Creating virtual environment in $(VENV_DIR)..."; \
		python3 -m venv $(VENV_DIR); \
		$(VENV_DIR)/bin/pip install --upgrade pip setuptools; \
	fi

# Install dependencies
install: venv
	@echo "Installing requirements from requirements.txt..."
	$(VENV_DIR)/bin/pip install -r requirements.txt

# Install development dependencies
install-dev: venv
	@echo "Installing requirements from requirements-dev.txt..."
	$(VENV_DIR)/bin/pip install -r requirements-dev.txt

# Clean up unnecessary files
clean:
	@echo "Cleaning up..."
	rm -rf $(VENV_DIR)
	rm -rf .mypy_cache .pytest_cache .ruff_cache
	rm -rf .coverage htmlcov test_coverage_report.html coverage.xml
	rm -f resources/database.db
	-docker ps -aq --filter "volume=demo-iot-platform_data" | xargs -r docker rm -f
	-docker volume rm -f demo-iot-platform_data || true

# Run the application locally
run:
	uvicorn app.app:app --host 0.0.0.0 --port 5555 --reload --ws websockets

# Run the application locally with a pre-built database
run-default: resources/database.db
	uvicorn app.app:app --host 0.0.0.0 --port 5555 --reload --ws websockets

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
	python tests/ws_client_test.py

test: venv
	@echo "Ensuring dev dependencies are installed..."
	$(VENV_DIR)/bin/pip install -r requirements-dev.txt
	@echo "Running tests with coverage and creating badge..."
	$(VENV_DIR)/bin/pytest --cov=./ --cov-report=term --cov-report=xml --cov-report=html:test_coverage_report.html tests/
	$(VENV_DIR)/bin/genbadge coverage --input-file=coverage.xml --output-file=coverage-badge.svg

.PHONY: all install venv install-dev clean run run-docker run-docker-default run-ws-test test