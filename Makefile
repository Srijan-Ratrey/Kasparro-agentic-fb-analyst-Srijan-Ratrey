# Kasparro Agentic Facebook Performance Analyst Makefile

.PHONY: help install run test clean setup lint format

# Default target
help:
	@echo "Available targets:"
	@echo "  setup     - Set up the project environment"
	@echo "  install   - Install dependencies"
	@echo "  run       - Run the agent system"
	@echo "  test      - Run tests"
	@echo "  lint      - Run linting"
	@echo "  format    - Format code"
	@echo "  clean     - Clean up generated files"

# Set up project environment
setup:
	@echo "Setting up project environment..."
	python -m venv .venv
	@echo "Virtual environment created. Activate with:"
	@echo "  source .venv/bin/activate  # Linux/Mac"
	@echo "  .venv\\Scripts\\activate     # Windows"

# Install dependencies
install:
	pip install -r requirements.txt

# Run the agent system
run:
	python src/run.py "Analyze ROAS drop in last 7 days"

# Run tests
test:
	pytest tests/ -v --cov=src --cov-report=html --cov-report=term

# Run linting
lint:
	flake8 src/ tests/
	mypy src/

# Format code
format:
	black src/ tests/

# Clean up generated files
clean:
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf logs/*.log
	rm -rf reports/*.md
	rm -rf reports/*.json
	rm -rf reports/*.png
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
