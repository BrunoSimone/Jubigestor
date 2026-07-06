-- JubiGestor schema (Postgres + pgvector).
-- Idempotent: safe to run multiple times.

CREATE EXTENSION IF NOT EXISTS vector;

-- Bibliographic record of each official document (source of the CITATIONS).
CREATE TABLE IF NOT EXISTS documents (
    id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    title        text NOT NULL,
    source_url   text NOT NULL UNIQUE,
    published_at date,
    created_at   timestamptz NOT NULL DEFAULT now(),
    updated_at   timestamptz NOT NULL DEFAULT now()
);

-- Text chunks + their vector. Text and embedding live TOGETHER.
CREATE TABLE IF NOT EXISTS chunks (
    id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id  uuid NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index  int NOT NULL,
    content      text NOT NULL,
    embedding    vector(768) NOT NULL,
    created_at   timestamptz NOT NULL DEFAULT now(),
    UNIQUE (document_id, chunk_index)
);

-- HNSW index for similarity search (cosine distance).
CREATE INDEX IF NOT EXISTS chunks_embedding_hnsw
    ON chunks USING hnsw (embedding vector_cosine_ops);
