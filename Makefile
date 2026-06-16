.PHONY: help dev dev-backend dev-frontend build up down test test-backend test-frontend lint migrate logs clean

# ==============================================================================
# Variables
# ==============================================================================
DOCKER_COMPOSE = docker compose
BACKEND_DIR = backend
FRONTEND_DIR = frontend
DATA_DIR = data

# ==============================================================================
# Help
# ==============================================================================
help: ## Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ==============================================================================
# Development
# ==============================================================================
dev: ## Start all services in development mode
	$(DOCKER_COMPOSE) up --build

dev-backend: ## Start backend in development mode (local)
	cd $(BACKEND_DIR) && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend: ## Start frontend in development mode (local)
	cd $(FRONTEND_DIR) && npm run dev

# ==============================================================================
# Docker
# ==============================================================================
build: ## Build all Docker images
	$(DOCKER_COMPOSE) build

up: ## Start all services (detached)
	$(DOCKER_COMPOSE) up -d

down: ## Stop all services
	$(DOCKER_COMPOSE) down

logs: ## View logs from all services
	$(DOCKER_COMPOSE) logs -f

ps: ## Show running services
	$(DOCKER_COMPOSE) ps

# ==============================================================================
# Testing
# ==============================================================================
test: test-backend test-frontend ## Run all tests

test-backend: ## Run backend tests
	cd $(BACKEND_DIR) && python -m pytest -v

test-frontend: ## Run frontend tests
	cd $(FRONTEND_DIR) && npm run test

test-e2e: ## Run end-to-end tests
	cd e2e && npx playwright test

# ==============================================================================
# Linting & Formatting
# ==============================================================================
lint: ## Run all linters
	cd $(BACKEND_DIR) && ruff check . && ruff format --check .
	cd $(FRONTEND_DIR) && npm run lint

format: ## Format all code
	cd $(BACKEND_DIR) && ruff format .
	cd $(FRONTEND_DIR) && npm run format

# ==============================================================================
# Database
# ==============================================================================
migrate: ## Run database migrations
	cd $(BACKEND_DIR) && alembic upgrade head

migrate-new: ## Create a new migration (usage: make migrate-new MSG="description")
	cd $(BACKEND_DIR) && alembic revision --autogenerate -m "$(MSG)"

migrate-down: ## Rollback last migration
	cd $(BACKEND_DIR) && alembic downgrade -1

# ==============================================================================
# Utilities
# ==============================================================================
clean: ## Remove all build artifacts and caches
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name node_modules -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name dist -exec rm -rf {} + 2>/dev/null || true
	rm -rf frontend/dist frontend/build

install: ## Install all dependencies
	cd $(BACKEND_DIR) && pip install -e ".[dev]"
	cd $(FRONTEND_DIR) && npm install
	cd e2e && npm install
