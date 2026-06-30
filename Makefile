.DEFAULT_GOAL := help
.PHONY: help install install-back install-front dev back front clean clean-cache \
        db-up db-down db-reset db-init db-smoke ingest query extract

# Puerto del backend. 4000 para no chocar con otros proyectos en 8000.
# Override puntual: make back BACKEND_PORT=9000
BACKEND_PORT ?= 4000

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
	@echo "Backend  -> http://localhost:$(BACKEND_PORT)"
	@echo "Frontend -> http://localhost:3000"
	@trap 'kill 0' INT TERM EXIT; \
		$(MAKE) back & \
		$(MAKE) front & \
		wait

back: ## Levanta solo el backend (FastAPI, :4000)
	cd backend && .venv/bin/uvicorn jubigestor.main:app --reload --port $(BACKEND_PORT)

front: ## Levanta solo el frontend (Next.js, :3000)
	cd frontend && pnpm dev

clean: ## Borra venv, node_modules y caché de Next (reinstalar de cero)
	rm -rf backend/.venv frontend/node_modules frontend/.next

clean-cache: ## Borra solo la caché de Turbopack/Next (si el front se cuelga compilando)
	rm -rf frontend/.next

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

ingest: ## Ingesta data/corpus/*.md (chunk + embed + upsert en pgvector)
	cd backend && .venv/bin/python scripts/ingest.py

query: ## Prueba el retrieve: make query Q="tu pregunta"
	cd backend && .venv/bin/python scripts/query.py "$(Q)"

extract: ## Extrae un PDF a un borrador .md para revisar: make extract PDF=data/sources/foo.pdf
	cd backend && .venv/bin/python scripts/extract_pdf.py "$(PDF)"
