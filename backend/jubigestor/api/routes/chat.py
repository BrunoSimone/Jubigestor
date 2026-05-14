from fastapi import APIRouter

from jubigestor.schemas.chat import ChatRequest, ChatResponse

router = APIRouter()

PLACEHOLDER_RESPONSES = {
    "jubilacion": "Para iniciar tu jubilación ordinaria necesitás 30 años de aportes y haber cumplido la edad (60 mujeres, 65 varones). ¿Querés que te explique los requisitos en detalle?",
    "pami": "PAMI es la obra social para jubilados y pensionados. Podés afiliarte apenas te jubilás. ¿Necesitás info sobre algún trámite específico de PAMI?",
    "pension": "Las pensiones derivadas incluyen pensión por viudez, PUAM y pensiones no contributivas. ¿Sobre cuál querés saber más?",
}

DEFAULT_REPLY = (
    "Soy Jubigestor, tu asistente para trámites jubilatorios argentinos. "
    "Puedo ayudarte con jubilaciones, pensiones, PAMI, cobros y aumentos. "
    "¿En qué te puedo ayudar?"
)


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    message_lower = request.message.lower()
    for keyword, response in PLACEHOLDER_RESPONSES.items():
        if keyword in message_lower:
            return ChatResponse(reply=response, sources=["placeholder"])
    return ChatResponse(reply=DEFAULT_REPLY, sources=[])
