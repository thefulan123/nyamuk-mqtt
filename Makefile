# Nyamuk Makefile
.PHONY: help install dev test lint format build clean docker-build docker-run docker-stop

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install for production
	pip install -r requirements.txt
	pip install .

dev:  ## Install for development
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	pre-commit install

test:  ## Run tests
	pytest tests/ -v

test-cov:  ## Run tests with coverage
	pytest tests/ -v --cov=nyamuk --cov-report=html

lint:  ## Run linter
	ruff check nyamuk/
	ruff format --check nyamuk/

format:  ## Format code
	ruff format nyamuk/
	ruff check --fix nyamuk/

typecheck:  ## Run type checker
	mypy nyamuk/ --ignore-missing-imports

build:  ## Build package
	python -m build

clean:  ## Clean build artifacts
	rm -rf dist/ build/ *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage

docker-build:  ## Build Docker image
	docker build -t nyamuk:latest .

docker-run:  ## Start with docker-compose
	docker-compose up -d

docker-stop:  ## Stop docker-compose
	docker-compose down

docker-logs:  ## View logs
	docker-compose logs -f nyamuk

docker-restart:  ## Restart services
	docker-compose restart

docker-ps:  ## Show running containers
	docker-compose ps

run-tui:  ## Run TUI dashboard
	python -m nyamuk tui

run-web:  ## Run web dashboard
	python -m nyamuk web --port 8080

run-web-debug:  ## Run web dashboard in debug mode
	python -m nyamuk web --port 8080 --debug
