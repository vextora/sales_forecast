APP_SERVICE=app
DB_PATH=db
ALEMBIC=alembic.ini

build: ## Build all image in docker-compose
	docker-compose build

run: ## Run container
	docker-compose up $(APP_SERVICE)

dev: ## Build and run container
	docker-compose up --build

down: ## Stop everything

migrate-init: ## Prepare migrations file
	docker-compose run --rm $(APP_SERVICE) alembic -c $(DB_PATH)/$(ALEMBIC) revision --autogenerate -m "auto"

migrate: ## Run migration
	docker-compose run --rm $(APP_SERVICE) alembic -c $(DB_PATH)/$(ALEMBIC) upgrade head

seed: ## Run all seeds
	docker-compose run -e PYTHONPATH=/$(APP_SERVICE) --rm $(APP_SERVICE) python scripts/seeds.py

forecast: ## Run forecast
	docker-compose run -e PYTHONPATH=/$(APP_SERVICE) --rm $(APP_SERVICE) python scripts/lstm_forecast.py --mode=forecast

backtest: ## Run backtest
	docker-compose run -e PYTHONPATH=/$(APP_SERVICE) --rm $(APP_SERVICE) python scripts/lstm_forecast.py --mode=backtest

eval: ## Evaluate forecast
	docker-compose run -e PYTHONPATH=/$(APP_SERVICE) --rm $(APP_SERVICE) python scripts/eval_forecast.py

help: ## Show all commands
	@echo ""
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-10s %s\n", $$1, $$2}'
	@echo ""