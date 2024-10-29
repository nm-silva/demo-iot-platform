# Define variables
VENV_DIR=.venv

# Default target
all: install

# Install dependencies
install: install_requirements

# Install development dependencies
install-dev: install_dev_requirements

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

.PHONY: all install install-dev install_requirements install_dev_requirements clean