# Backend image for production (Render). Pins Python 3.14 regardless of the
# platform's native runtimes and installs with pip from pyproject.
FROM python:3.14-slim

# Unbuffered logs (visible in Render's log stream) and no .pyc clutter.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Only what the runtime needs: project metadata + the package itself.
# Corpus/scripts are not copied: ingestion runs against the DB from a dev machine.
COPY pyproject.toml ./
COPY jubigestor ./jubigestor
RUN pip install --no-cache-dir .

# Render injects $PORT at runtime; 4000 is the local fallback.
ENV PORT=4000
EXPOSE 4000

CMD ["sh", "-c", "uvicorn jubigestor.main:app --host 0.0.0.0 --port ${PORT}"]
