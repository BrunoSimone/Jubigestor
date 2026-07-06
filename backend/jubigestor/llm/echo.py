from collections.abc import AsyncIterator, Sequence

from jubigestor.llm.base import LLMProvider

_KEYWORD_REPLIES = {
    "jubilacion": (
        "Para iniciar tu jubilación ordinaria suelen pedir 30 años de aportes y la edad "
        "cumplida (60 las mujeres, 65 los varones). Es información orientativa: el dato "
        "final confirmalo en ANSES (anses.gob.ar o llamando al 130)."
    ),
    "pami": (
        "PAMI es la obra social de jubilados y pensionados. Te podés afiliar apenas te "
        "jubilás. Para el trámite puntual, verificá los requisitos en ANSES o PAMI."
    ),
    "pension": (
        "Existen distintas pensiones (por viudez, PUAM, no contributivas). Cada una tiene "
        "sus requisitos. Conviene que confirmes tu caso en ANSES."
    ),
}

_DEFAULT_REPLY = (
    "Soy JubiGestor, tu asistente para trámites jubilatorios argentinos. "
    "Puedo orientarte con jubilaciones, pensiones, PAMI, cobros y aumentos. "
    "(Nota: todavía no tengo un modelo de IA conectado; estoy respondiendo de forma "
    "básica. Configurá GEMINI_API_KEY para activar las respuestas completas.)"
)


class EchoProvider(LLMProvider):
    """Zero-cost, network-free fallback: keeps the app working with no API key.

    Mirrors the keyword placeholder replies so the demo never breaks.
    (Reply strings stay in Spanish: they are shown to the end user.)
    """

    name = "echo"

    async def generate(self, message: str, *, context: str | None = None) -> str:
        lowered = message.lower()
        for keyword, reply in _KEYWORD_REPLIES.items():
            if keyword in lowered:
                return reply
        return _DEFAULT_REPLY

    async def generate_stream(
        self, message: str, *, context: str | None = None
    ) -> AsyncIterator[str]:
        # No real model means no tokens to stream: emit the reply in one shot.
        yield await self.generate(message, context=context)

    async def embed(
        self, texts: Sequence[str], *, task_type: str = "RETRIEVAL_DOCUMENT"
    ) -> list[list[float]]:
        raise NotImplementedError(
            "EchoProvider does not generate embeddings. Configure a real provider "
            "(GEMINI_API_KEY) to use the ingestion pipeline / RAG."
        )
