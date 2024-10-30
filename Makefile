# Define variables
VENV_DIR=.venv

# Default target
all: install

# Install dependencies
install: install_requirements
	@echo "To activate the virtual environment, run:"
	@echo "source $(VENV_DIR)/bin/activate"

# Install development dependencies
install-dev: install_dev_requirements
	@echo "To activate the virtual environment, run:"
	@echo "source $(VENV_DIR)/bin/activate"

# Create virtual environment and install Python requirements
install_requirements: $(VENV_DIR)/bin/activate

install_dev_requirements: $(VENV_DIR)/bin/activate-dev

$(VENV_DIR)/bin/activate: requirements.txt
	@echo "Creating virtual environment..."
	python3 -m venv $(VENV_DIR)
	@echo "Installing Python requirements..."
	$(VENV_DIR)/bin/pip install -r requirements.txt
	@touch $(VENV_DIR)/bin/activate

$(VENV_DIR)/bin/activate-dev: requirements-dev.txt $(VENV_DIR)/bin/activate
	@echo "Installing development Python requirements..."
	$(VENV_DIR)/bin/pip install -r requirements-dev.txt
	@touch $(VENV_DIR)/bin/activate-dev

# Clean up unnecessary files
clean:
	@echo "Cleaning up..."
	rm -rf $(VENV_DIR)
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

.PHONY: all install install-dev install_requirements install_dev_requirements clean run run-docker