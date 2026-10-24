from functools import lru_cache

from policyrag.config import RERANK_MODEL


@lru_cache(maxsize=1)
def _model():
    from sentence_transformers import CrossEncoder

    return CrossEncoder(RERANK_MODEL)


def rerank(query: str, hits, top_k: int = 5):
    """Score (query, chunk) pairs with the cross-encoder; score is a 0-1 relevance probability."""
    if not hits:
        return []
    scores = _model().predict([(query, h.text) for h in hits], show_progress_bar=False)
    for hit, score in zip(hits, scores):
        hit.score = float(score)
    return sorted(hits, key=lambda h: h.score, reverse=True)[:top_k]
