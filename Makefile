# Docker
up:
	docker compose up -d --build
down:
	docker compose down
logs:
	docker compose logs -f
migrate:
	docker compose exec api uv run alembic upgrade head
makemigration:
	docker compose exec api uv run alembic revision --autogenerate -m "$(name)"
test:
	docker compose exec api uv run pytest
shell:
	docker compose exec api bash
db:
	docker compose exec postgres psql -U "$${POSTGRES_USER}" -d "$${POSTGRES_DB}"
check:
	docker compose exec api uv run ruff check .
	docker compose exec api uv run ruff format --check .
	docker compose exec api uv run pytest -v -s
fix:
	docker compose exec api uv run ruff check . --fix
	docker compose exec api uv run ruff format .