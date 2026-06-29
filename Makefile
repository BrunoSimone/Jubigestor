.DEFAULT_GOAL := help
.PHONY: help install install-back install-front dev back front clean

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
