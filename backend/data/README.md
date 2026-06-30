# Datos de JubiGestor

```
data/
├── sources/   PDFs originales (locales, en .gitignore — NO se suben al repo)
└── corpus/    Documentos .md con frontmatter (fuente de verdad, versionados)
```

## Flujo

```
PDF (sources/)  ──extracción──►  .md (corpus/)  ──make ingest──►  chunks+vectores (DB)
   local, gitignored            en git, revisable           Postgres + pgvector
```

- **`sources/`** — PDFs originales. Viven localmente (PC / Drive); no van al repo.
- **`corpus/`** — el texto extraído como `.md` con frontmatter. Esto es lo que lee
  el pipeline de ingesta (`make ingest`) y lo que garantiza la trazabilidad.

## Formato de cada documento del corpus

```markdown
---
title: Moratoria previsional
source_url: https://www.anses.gob.ar/moratoria
published_at: 2026-01-15
---

Texto del documento oficial, en lenguaje claro...
```

- `title` *(obligatorio)* — nombre del documento (aparece en la **cita**).
- `source_url` *(obligatorio)* — link oficial. Es único: re-ingestar el mismo
  URL **actualiza** el documento en vez de duplicarlo.
- `published_at` *(opcional)* — fecha de "última actualización" del documento.

## Notas

- La ingesta es **idempotente**: corré `make ingest` las veces que quieras.
- Empezamos angosto (MVP): jubilación ordinaria + moratoria. El resto es fase 2.
