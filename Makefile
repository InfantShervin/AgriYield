# 🌾 AgriYield AI - Professional Automation Makefile

.PHONY: help install lint test test-unit test-e2e security check-all clean

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install all dependencies (Backend + Frontend)
	pip install -r requirements.txt
	npm install

lint: ## Run professional linting and formatting (Ruff + ESLint)
	ruff check . --fix
	ruff format .
	@if [ -d "frontend" ]; then npx eslint frontend/*.js --fix; fi

test: test-unit test-e2e ## Run all tests

test-unit: ## Run backend and ML unit tests
	pytest backend/tests ml_pipeline/tests -v

test-e2e: ## Run Playwright End-to-End tests
	npx playwright test

security: ## Run security vulnerability scanning (Bandit)
	bandit -r backend/ ml_pipeline/

check-all: lint security test-unit ## Run all quality gates (Lint + Security + Unit Tests)

clean: ## Clean up cache files
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
