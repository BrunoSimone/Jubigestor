from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from jubigestor.config import settings
from jubigestor.db import get_pool
from jubigestor.llm import get_provider

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check liviano en JSON (para monitoreo / keep-warm ping)."""
    return {"status": "ok", "service": "jubigestor"}


async def _db_status() -> str:
    """Estado de la conexión a Postgres, sin romper si la DB no está."""
    if not settings.database_url:
        return "no configurada"
    try:
        async with get_pool().connection() as conn:
            await conn.execute("SELECT 1")
        return "conectada"
    except Exception:
        return "error de conexión"


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
async def root():
    """Página de estado legible en el navegador: confirma que el backend anda."""
    provider = get_provider().name
    db = await _db_status()
    html = f"""<!doctype html>
<html lang="es">
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
    <h1>✅ JubiGestor — Backend <span class="ok">funcionando</span></h1>
    <table>
      <tr><td>Proveedor LLM</td><td>{provider}</td></tr>
      <tr><td>Base de datos</td><td>{db}</td></tr>
    </table>
    <p class="muted">
      Endpoints: <a href="/health">/health</a> (JSON) ·
      <a href="/docs">/docs</a> (API interactiva)<br>
      La app (chat) está en <a href="http://localhost:3000">http://localhost:3000</a>
    </p>
  </div>
</body>
</html>"""
    return html
