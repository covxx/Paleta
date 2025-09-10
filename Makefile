# Makefile for ProduceFlow Label Printer

.PHONY: help install install-dev test lint format clean run deploy

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  [36m%-20s[0m %s
", $$1, $$2}'

install:  ## Install production dependencies
	pip install -r requirements.txt

install-dev:  ## Install development dependencies
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	pre-commit install

test:  ## Run tests
	pytest tests/ -v --cov=app --cov-report=html

lint:  ## Run linting
	flake8 app.py services/ utils/ middleware/ api/
	black --check app.py services/ utils/ middleware/ api/
	isort --check-only app.py services/ utils/ middleware/ api/

format:  ## Format code
	black app.py services/ utils/ middleware/ api/
	isort app.py services/ utils/ middleware/ api/

clean:  ## Clean up temporary files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf htmlcov/
	rm -rf .coverage

run:  ## Run the application
	python app.py

run-dev:  ## Run the application in development mode
	export FLASK_ENV=development
	export FLASK_DEBUG=True
	python app.py

deploy:  ## Deploy to production
	git push origin master
	ssh user@server 'cd /opt/label-printer && git pull && sudo systemctl restart label-printer'

backup:  ## Backup database
	python scripts/backup_database.py

migrate:  ## Run database migrations
	python scripts/migrate_database.py

optimize:  ## Optimize database
	python scripts/optimize_database.py

setup: install-dev  ## Setup development environment
	pre-commit install
	python scripts/optimize_database.py
