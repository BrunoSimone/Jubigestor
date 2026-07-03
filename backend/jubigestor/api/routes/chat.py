import json
import logging
from collections.abc import AsyncIterator

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from jubigestor.llm import get_provider
from jubigestor.rag import retrieve
from jubigestor.ratelimit import rate_limit
from jubigestor.schemas.chat import ChatRequest

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/chat", dependencies=[Depends(rate_limit)])
async def chat(request: ChatRequest) -> StreamingResponse:
    """Responde en streaming NDJSON: 1 línea de fuentes + N líneas de texto + cierre.

    Formato (una línea JSON por evento):
        {"type": "sources", "sources": [...]}
        {"type": "text", "chunk": "..."}
        {"type": "done"}          (o {"type": "error", "message": "..."})
    """
    message = request.message.strip()
    if not message:
        raise HTTPException(status_code=422, detail="El mensaje no puede estar vacío.")

    provider = get_provider()
    # El retrieve va ANTES del stream: así ya tenemos las citas para emitirlas primero.
    context, sources = await retrieve(provider, message)

    async def event_stream() -> AsyncIterator[str]:
        yield json.dumps(
            {"type": "sources", "sources": [s.model_dump(mode="json") for s in sources]}
        ) + "\n"
        try:
            async for chunk in provider.generate_stream(message, context=context):
                yield json.dumps({"type": "text", "chunk": chunk}) + "\n"
        except Exception:
            logger.exception("Falló la generación en streaming.")
            yield json.dumps(
                {"type": "error", "message": "No pude generar una respuesta. Probá de nuevo."}
            ) + "\n"
            return
        yield json.dumps({"type": "done"}) + "\n"

    return StreamingResponse(event_stream(), media_type="application/x-ndjson")
