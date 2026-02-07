#!make

# Default target
.DEFAULT_GOAL := help

# Colors for output
YELLOW := \033[33m
GREEN := \033[32m
RED := \033[31m
RESET := \033[0m

# Variables
COVERAGE_THRESHOLD := 95

.PHONY: help
help: ## Show this help message
	@echo "$(GREEN)Available targets:$(RESET)"
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z_-]+:.*##/ { printf "  $(YELLOW)%-20s$(RESET) %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

.PHONY: install-deps
install-deps: ## Install macOS dependencies
	@echo "$(GREEN)Installing dependencies for macOS$(RESET)"
	@command -v brew >/dev/null 2>&1 || { echo "$(RED)Homebrew not found. Please install it first.$(RESET)"; exit 1; }
	@brew install uv

.PHONY: setup
setup: install-deps sync ## Complete setup for new developers
	@echo "$(GREEN)Setup complete!$(RESET)"

.PHONY: sync
sync: ## Sync dependencies with uv
	@echo "$(GREEN)Syncing dependencies$(RESET)"
	@uv sync --all-extras --all-packages --group dev

.PHONY: format
format: ## Format code with ruff
	@echo "$(GREEN)Formatting code$(RESET)"
	@uv run ruff format
	@uv run ruff check --fix

.PHONY: type-check
type-check: ## Run type checking with pyright
	@echo "$(GREEN)Running type checks$(RESET)"
	@uv run pyright .

.PHONY: test
test: ## Run tests
	@echo "$(GREEN)Running tests$(RESET)"
	@uv run pytest

.PHONY: migrate_suggestions
migrate_suggestions: ## Apply Alembic migrations to the suggestions database
	@set -a; [ -f .env ] && . ./.env; set +a; \
	if [ -z "$$SUGGESTIONS_SQL_CONN_STRING" ]; then \
		echo "$(RED)SUGGESTIONS_SQL_CONN_STRING must be set (export it or add it to .env)$(RESET)"; \
		exit 1; \
	fi; \
	echo "$(GREEN)Applying suggestions migrations$(RESET)"; \
	ALEMBIC_SQL_CONN_STRING="$$SUGGESTIONS_SQL_CONN_STRING" uv run alembic upgrade head

.PHONY: revert_migration
revert_migration: ## Revert the last Alembic migration (use STEPS=n to revert n migrations)
	@set -a; [ -f .env ] && . ./.env; set +a; \
	if [ -z "$$SUGGESTIONS_SQL_CONN_STRING" ]; then \
		echo "$(RED)SUGGESTIONS_SQL_CONN_STRING must be set (export it or add it to .env)$(RESET)"; \
		exit 1; \
	fi; \
	STEPS=$${STEPS:-1}; \
	echo "$(YELLOW)Reverting $$STEPS migration(s)$(RESET)"; \
	ALEMBIC_SQL_CONN_STRING="$$SUGGESTIONS_SQL_CONN_STRING" uv run alembic downgrade -$$STEPS

.PHONY: coverage ## Run tests with coverage report
coverage:
	@echo "$(GREEN)Running tests with coverage$(RESET)"
	@uv run coverage run -m pytest
	@uv run coverage xml -o coverage.xml
	@uv run coverage report -m --fail-under=$(COVERAGE_THRESHOLD)

.PHONY: coverage-html
coverage-html: ## Generate HTML coverage report
	@echo "$(GREEN)Generating HTML coverage report$(RESET)"
	@uv run coverage run -m pytest
	@uv run coverage html
	@echo "$(GREEN)Coverage report generated in htmlcov/index.html$(RESET)"

.PHONY: clean
clean: ## Clean up generated files
	@echo "$(GREEN)Cleaning up$(RESET)"
	@rm -rf .coverage htmlcov/ coverage.xml
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete

.PHONY: check
check: format type-check test ## Run all quality checks

.PHONY: ci
ci: check coverage ## Run all CI checks

.PHONY: all
all: sync check coverage ## Run everything (sync, check, coverage)

.PHONY: dev
dev: ## Run the application locally for development
	@echo "$(GREEN)Starting development server$(RESET)"
	@uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
	@echo "$(GREEN)Development server started on http://localhost:8000$(RESET)"

.PHONY: serve
serve: ## Run the application locally (production mode)
	@echo "$(GREEN)Starting production server$(RESET)"
	@uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
	@echo "$(GREEN)Server started on http://localhost:8000$(RESET)"

.PHONY: build
build: ## Build the Docker image
	@echo "$(GREEN)Building the project$(RESET)"
	@docker build -t cold-backend .
	@echo "$(GREEN)Build complete!$(RESET)"

.PHONY: up
up: build ## Start the Docker container
	@echo "$(GREEN)Starting the Docker container$(RESET)"
	@docker run -p 8000:8000 --name cold-backend --rm cold-backend
	@echo "$(GREEN)Container started on port 8000$(RESET)"