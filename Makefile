.DEFAULT_GOAL := help
.PHONY: help install install-back install-front dev back front clean \
        db-up db-down db-reset db-init db-smoke

help: ## Muestra esta ayuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

install: install-back install-front ## Instala TODO (backend + frontend). Correr una sola vez.

install-back: ## Crea el venv e instala deps del backend
	cd backend && python3 -m venv .venv && \
		.venv/bin/pip install --upgrade pip && \
		.venv/bin/pip install -e .

install-front: ## Instala deps del frontend
	cd frontend && pnpm install

dev: ## Levanta backend + frontend juntos (Ctrl-C corta los dos)
	@echo "Backend  -> http://localhost:8000"
	@echo "Frontend -> http://localhost:3000"
	@trap 'kill 0' INT TERM EXIT; \
		$(MAKE) back & \
		$(MAKE) front & \
		wait

back: ## Levanta solo el backend (FastAPI, :8000)
	cd backend && .venv/bin/uvicorn jubigestor.main:app --reload --port 8000

front: ## Levanta solo el frontend (Next.js, :3000)
	cd frontend && pnpm dev

clean: ## Borra venv y node_modules (para reinstalar de cero)
	rm -rf backend/.venv frontend/node_modules

db-up: ## Levanta Postgres + pgvector en Docker (:5432)
	docker compose up -d

db-down: ## Apaga la DB (conserva los datos)
	docker compose down

db-reset: ## Apaga la DB y BORRA todos los datos (volumen incluido)
	docker compose down -v

db-init: ## Aplica el esquema SQL a la DB
	cd backend && .venv/bin/python scripts/init_db.py

db-smoke: ## Prueba end-to-end: inserta chunks con embeddings y busca
	cd backend && .venv/bin/python scripts/smoke_db.py
