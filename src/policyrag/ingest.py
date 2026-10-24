"""Parse every PDF in the corpus, embed the chunks and load them into Postgres."""
from pathlib import Path

from policyrag.chunk import Chunk, parse_pdf
from policyrag.config import CORPUS_DIR
from policyrag.db import connect, init_schema
from policyrag.embed import embed

INSERT = """INSERT INTO chunks (doc, title, section_no, section, page, content, embedding)
VALUES (%s, %s, %s, %s, %s, %s, %s)"""


def load_chunks(corpus: Path = CORPUS_DIR) -> list[Chunk]:
    return [c for pdf in sorted(corpus.glob("*.pdf")) for c in parse_pdf(pdf)]


def ingest(corpus: Path = CORPUS_DIR) -> int:
    chunks = load_chunks(corpus)
    vectors = embed([c.search_text for c in chunks])
    with connect() as conn:
        init_schema(conn)
        conn.execute("TRUNCATE chunks RESTART IDENTITY")
        rows = [
            (c.doc, c.title, c.section_no, c.section, c.page, c.content, v)
            for c, v in zip(chunks, vectors)
        ]
        conn.cursor().executemany(INSERT, rows)
    return len(chunks)


if __name__ == "__main__":
    print(f"ingested {ingest()} chunks")
