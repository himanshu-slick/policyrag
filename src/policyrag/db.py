import psycopg
from pgvector.psycopg import register_vector

from policyrag.config import DATABASE_URL, EMBED_DIM

SCHEMA = f"""
CREATE EXTENSION IF NOT EXISTS vector;
CREATE TABLE IF NOT EXISTS chunks (
    id         serial PRIMARY KEY,
    doc        text NOT NULL,
    title      text NOT NULL,
    section_no int  NOT NULL,
    section    text NOT NULL,
    page       int  NOT NULL,
    content    text NOT NULL,
    embedding  vector({EMBED_DIM}) NOT NULL,
    tsv        tsvector GENERATED ALWAYS AS
               (to_tsvector('english', title || ' ' || section || ' ' || content)) STORED
);
CREATE INDEX IF NOT EXISTS chunks_tsv_idx ON chunks USING gin (tsv);
"""


def connect(url: str = DATABASE_URL) -> psycopg.Connection:
    with psycopg.connect(url, autocommit=True) as boot:
        boot.execute("CREATE EXTENSION IF NOT EXISTS vector")
    conn = psycopg.connect(url)
    register_vector(conn)
    return conn


def init_schema(conn: psycopg.Connection) -> None:
    conn.execute(SCHEMA)
    conn.commit()
