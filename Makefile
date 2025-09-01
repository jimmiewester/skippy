.PHONY: help install test run-server run-worker run-beat clean setup

help: ## Show this help message
	@echo "Skippy - FastAPI Webhook Service"
	@echo "================================"
	@echo ""
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

setup: ## Initial setup of the project
	@echo "🚀 Setting up Skippy project..."
	@./start.sh

install: ## Install Python dependencies
	@echo "📦 Installing dependencies..."
	pip install -r requirements.txt

test: ## Run tests
	@echo "🧪 Running tests..."
	pytest tests/ -v

run-server: ## Start the FastAPI server
	@echo "🌐 Starting FastAPI server..."
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-worker: ## Start the Celery worker
	@echo "👷 Starting Celery worker..."
	celery -A app.workers.celery_app worker --loglevel=info

run-beat: ## Start the Celery beat scheduler
	@echo "⏰ Starting Celery beat scheduler..."
	celery -A app.workers.celery_app beat --loglevel=info

docker-up: ## Start Docker services
	@echo "🐳 Starting Docker services..."
	docker-compose up -d

docker-down: ## Stop Docker services
	@echo "🐳 Stopping Docker services..."
	docker-compose down

docker-logs: ## Show Docker logs
	@echo "📋 Showing Docker logs..."
	docker-compose logs -f

format: ## Format code with black
	@echo "🎨 Formatting code..."
	black app/ tests/

lint: ## Lint code with flake8
	@echo "🔍 Linting code..."
	flake8 app/ tests/

type-check: ## Type check with mypy
	@echo "🔍 Type checking..."
	mypy app/

clean: ## Clean up generated files
	@echo "🧹 Cleaning up..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/

example: ## Run the example webhook script
	@echo "📝 Running example webhook script..."
	python examples/send_webhook.py

test-sms: ## Test SMS functionality
	@echo "📱 Testing SMS functionality..."
	python examples/test_sms_webhook.py
