.PHONY: dev dev-bot dev-app test lint typecheck migrate seed docker-up docker-down

# --- Development ---
dev-bot:
	cd backend && python -m bot.main

dev-app:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-worker:
	cd backend && celery -A realtime.celery_app worker -l info -c 4

# --- Database ---
migrate:
	cd backend && alembic upgrade head

migrate-create:
	cd backend && alembic revision --autogenerate -m "$(name)"

seed:
	cd backend && python -m scripts.seed

# --- Quality ---
test:
	cd backend && pytest -x -v --tb=short

test-cov:
	cd backend && pytest --cov=. --cov-report=term-missing

lint:
	cd backend && ruff check . --fix
	cd backend && ruff format .

typecheck:
	cd backend && mypy .

# --- Docker ---
docker-up:
	docker compose -f infra/docker/docker-compose.yml up -d

docker-down:
	docker compose -f infra/docker/docker-compose.yml down

docker-logs:
	docker compose -f infra/docker/docker-compose.yml logs -f

# --- Full ---
check: lint typecheck test
