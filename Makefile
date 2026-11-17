COMPOSE      = docker compose
DEMO         = $(COMPOSE) -f docker-compose.yml -f docker-compose.demo.yml

.PHONY: help demo up down logs seed test lint

help:
	@echo "make demo   build and start JikUp with demo data at http://localhost:8080"
	@echo "make up     start the development stack (hot reload, http://localhost:5173)"
	@echo "make down   stop everything (data is kept)"
	@echo "make logs   follow backend and worker logs"
	@echo "make seed   load and index the demo postings again"
	@echo "make test   run backend and frontend tests"
	@echo "make lint   run all linters and type checks"

.env:
	@echo "Missing .env. Run: cp .env.example .env" && exit 1

demo: .env
	@if grep -q '^ADMIN_TOKEN=$$' .env; then \
		token=$$(openssl rand -hex 32); tmp=$$(mktemp); \
		awk -v t="$$token" '/^ADMIN_TOKEN=$$/ {print "ADMIN_TOKEN=" t; next} {print}' .env > $$tmp && mv $$tmp .env; \
		echo "Generated ADMIN_TOKEN in .env"; \
	fi
	$(DEMO) up -d --build --wait
	$(DEMO) exec -T backend python -m app.cli seed
	@echo "JikUp is running at http://localhost:8080"

up: .env
	$(COMPOSE) up -d --build

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f backend worker

seed:
	$(COMPOSE) exec -T backend python -m app.cli seed

test:
	cd backend && uv run pytest
	cd frontend && npm test

lint:
	cd backend && uv run ruff check . && uv run ruff format --check . && uv run mypy app tests alembic scripts eval
	cd frontend && npm run typecheck && npm run lint && npm run format:check
