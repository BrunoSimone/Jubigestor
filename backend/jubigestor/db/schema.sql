-- Esquema de JubiGestor (Postgres + pgvector).
-- Idempotente: se puede correr varias veces sin romper nada.

CREATE EXTENSION IF NOT EXISTS vector;

-- Ficha bibliográfica de cada documento oficial (de acá salen las CITAS).
CREATE TABLE IF NOT EXISTS documents (
    id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    title        text NOT NULL,
    source_url   text NOT NULL UNIQUE,
    published_at date,
    created_at   timestamptz NOT NULL DEFAULT now(),
    updated_at   timestamptz NOT NULL DEFAULT now()
);

-- Trozos de texto + su vector. El texto y el embedding viven JUNTOS.
CREATE TABLE IF NOT EXISTS chunks (
    id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id  uuid NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index  int NOT NULL,
    content      text NOT NULL,
    embedding    vector(768) NOT NULL,
    created_at   timestamptz NOT NULL DEFAULT now(),
    UNIQUE (document_id, chunk_index)
);

-- Indice HNSW para busqueda por similitud (distancia coseno).
CREATE INDEX IF NOT EXISTS chunks_embedding_hnsw
    ON chunks USING hnsw (embedding vector_cosine_ops);
