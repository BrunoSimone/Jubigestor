from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from jubigestor.config import settings
from jubigestor.db import get_pool
from jubigestor.llm import get_provider

router = APIRouter()


@router.get("/health")
async def health_check():
    """Lightweight JSON health check (for monitoring / keep-warm ping)."""
    return {"status": "ok", "service": "jubigestor"}


async def _db_status() -> str:
    """Postgres connection status, without failing if the DB is down."""
    if not settings.database_url:
        return "not configured"
    try:
        async with get_pool().connection() as conn:
            await conn.execute("SELECT 1")
        return "connected"
    except Exception:
        return "connection error"


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
async def root():
    """Browser-readable status page (dev-facing): confirms the backend is up."""
    provider = get_provider().name
    db = await _db_status()
    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>JubiGestor · Backend</title>
  <style>
    body {{ font-family: system-ui, sans-serif; background: #f9fafb; color: #111827;
           display: flex; min-height: 100vh; margin: 0; align-items: center; justify-content: center; }}
    .card {{ background: #fff; border: 1px solid #e5e7eb; border-radius: 12px;
             padding: 2rem 2.5rem; box-shadow: 0 1px 3px rgba(0,0,0,.08); max-width: 28rem; }}
    h1 {{ margin: 0 0 .25rem; font-size: 1.25rem; }}
    .ok {{ color: #047857; font-weight: 600; }}
    table {{ width: 100%; border-collapse: collapse; margin: 1rem 0; }}
    td {{ padding: .35rem 0; border-bottom: 1px solid #f3f4f6; }}
    td:last-child {{ text-align: right; font-weight: 600; }}
    a {{ color: #2563eb; text-decoration: none; }}
    .muted {{ color: #6b7280; font-size: .85rem; }}
  </style>
</head>
<body>
  <div class="card">
    <h1>✅ JubiGestor — Backend <span class="ok">running</span></h1>
    <table>
      <tr><td>LLM provider</td><td>{provider}</td></tr>
      <tr><td>Database</td><td>{db}</td></tr>
    </table>
    <p class="muted">
      Endpoints: <a href="/health">/health</a> (JSON) ·
      <a href="/docs">/docs</a> (interactive API)<br>
      The app (chat) is at <a href="http://localhost:3000">http://localhost:3000</a>
    </p>
  </div>
</body>
</html>"""
    return html
