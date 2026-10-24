"""Hybrid retrieval: pgvector + Postgres full-text, fused with RRF, re-ranked."""
import re
from dataclasses import dataclass, field

from policyrag.config import CANDIDATES
from policyrag.db import connect
from policyrag.embed import embed

COLUMNS = "id, doc, title, section_no, section, page, content"
VECTOR_SQL = f"SELECT {COLUMNS} FROM chunks ORDER BY embedding <=> %s::vector LIMIT %s"
FTS_SQL = f"""SELECT {COLUMNS} FROM chunks, to_tsquery('english', %s) q
WHERE tsv @@ q ORDER BY ts_rank_cd(tsv, q) DESC LIMIT %s"""


@dataclass
class Hit:
    id: int
    doc: str
    title: str
    section_no: int
    section: str
    page: int
    content: str
    score: float = field(default=0.0)

    @property
    def text(self) -> str:
        return f"{self.title}. {self.section}. {self.content}"

    def citation(self) -> dict:
        return {"doc": self.doc, "section": f"{self.section_no}. {self.section}", "page": self.page}


def rrf(rankings: list[list[int]], k: int = 60) -> list[int]:
    """Reciprocal rank fusion: ids ordered by sum of 1 / (k + rank)."""
    scores: dict[int, float] = {}
    for ranking in rankings:
        for rank, item in enumerate(ranking, 1):
            scores[item] = scores.get(item, 0.0) + 1.0 / (k + rank)
    return sorted(scores, key=lambda i: scores[i], reverse=True)


def or_query(text: str) -> str:
    """Turn a question into an OR tsquery so any matching term can retrieve."""
    return " | ".join(dict.fromkeys(re.findall(r"[a-z0-9]+", text.lower())))


def _rows(conn, sql: str, params: tuple) -> list[Hit]:
    return [Hit(*row) for row in conn.execute(sql, params).fetchall()]


def vector_search(conn, query: str, limit: int = CANDIDATES) -> list[Hit]:
    return _rows(conn, VECTOR_SQL, (embed([query])[0], limit))


def keyword_search(conn, query: str, limit: int = CANDIDATES) -> list[Hit]:
    terms = or_query(query)
    return _rows(conn, FTS_SQL, (terms, limit)) if terms else []


def hybrid_search(conn, query: str, limit: int = CANDIDATES) -> list[Hit]:
    lists = [vector_search(conn, query, limit), keyword_search(conn, query, limit)]
    by_id = {h.id: h for hits in lists for h in hits}
    return [by_id[i] for i in rrf([[h.id for h in hits] for hits in lists])]


def search(query: str, mode: str = "rerank", top_k: int = 5, conn=None) -> list[Hit]:
    """mode: vector | hybrid | rerank."""
    owned = conn is None
    conn = conn or connect()
    try:
        if mode == "vector":
            return vector_search(conn, query)[:top_k]
        hits = hybrid_search(conn, query)
    finally:
        if owned:
            conn.close()
    if mode == "hybrid":
        return hits[:top_k]
    from policyrag.rerank import rerank

    return rerank(query, hits, top_k)
