from collections.abc import Sequence

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
    """Fallback sin costo ni red: mantiene la app funcionando cuando no hay API key.

    Replica las respuestas placeholder por palabra clave para que la demo no quede rota.
    """

    name = "echo"

    async def generate(self, message: str, *, context: str | None = None) -> str:
        lowered = message.lower()
        for keyword, reply in _KEYWORD_REPLIES.items():
            if keyword in lowered:
                return reply
        return _DEFAULT_REPLY

    async def embed(self, texts: Sequence[str]) -> list[list[float]]:
        raise NotImplementedError(
            "EchoProvider no genera embeddings. Configurá un proveedor real "
            "(GEMINI_API_KEY) para usar el pipeline de ingesta / RAG."
        )
