from fastapi import APIRouter, HTTPException

from jubigestor.llm import get_provider
from jubigestor.rag import retrieve
from jubigestor.schemas.chat import ChatRequest, ChatResponse

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    message = request.message.strip()
    if not message:
        raise HTTPException(status_code=422, detail="El mensaje no puede estar vacío.")

    provider = get_provider()

    # RAG: recuperar contexto de los documentos oficiales y sus citas.
    context, sources = await retrieve(provider, message)

    try:
        reply = await provider.generate(message, context=context)
    except Exception as exc:  # noqa: BLE001 - el cliente no debe ver el detalle interno
        raise HTTPException(
            status_code=502,
            detail="No pude generar una respuesta en este momento. Probá de nuevo.",
        ) from exc

    return ChatResponse(reply=reply, sources=sources)
