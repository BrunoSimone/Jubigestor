# JubiGestor

**RAG chat assistant that helps older Argentinians understand ANSES pension
procedures in plain language — every answer cites the official, dated source.**

It acts as a guide, not an authority: answers are grounded in a curated official
corpus, show when the source was last updated, and defer to ANSES when the answer
isn't found — key for a low-digital-literacy audience.

## Highlights

- **Grounded RAG** over pgvector with cited, dated sources and a relevance threshold
  (off-topic questions don't hallucinate).
- **Streaming** responses over NDJSON (citations first, then tokens).
- **Provider-agnostic LLM layer** — swap Gemini ↔ OpenAI ↔ Claude via one env var.
- **Accessibility-first UI** — adjustable large text, high contrast, hyperlegible font.

## Stack

Next.js 16 · React 19 · Tailwind v4 · FastAPI · Python 3.14 · Postgres + pgvector · Gemini

Frontend → FastAPI (RAG · streaming · per-IP rate limiting) → Gemini + pgvector.
Deploy target: Vercel · Render · Neon.

## Run locally

Requires Python 3.14, Node + pnpm, Docker, and a free
[Gemini API key](https://aistudio.google.com/apikey).

```bash
cd backend && cp .env.example .env    # add GEMINI_API_KEY
cd .. && make install
make db-up && make db-init && make ingest
make dev                              # backend :4000 · frontend :3000
```
