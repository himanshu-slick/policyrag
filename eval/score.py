"""Pure scoring helpers for the retrieval and answer evals."""


def is_gold(hit, question: dict) -> bool:
    return hit.doc == question["doc"] and hit.section == question["section"]


def recall_at_k(hit_lists: list[list], questions: list[dict], k: int = 5) -> float:
    """Share of questions whose gold (doc, section) appears in the top k hits."""
    found = sum(any(is_gold(h, q) for h in hits[:k]) for hits, q in zip(hit_lists, questions))
    return found / len(questions) if questions else 0.0


def mrr(hit_lists: list[list], questions: list[dict]) -> float:
    total = 0.0
    for hits, q in zip(hit_lists, questions):
        total += next((1 / r for r, h in enumerate(hits, 1) if is_gold(h, q)), 0.0)
    return total / len(questions) if questions else 0.0


def answer_match(answer: str, expected: str) -> bool:
    return expected.lower() in answer.lower()


def rate(flags: list[bool]) -> float:
    return sum(flags) / len(flags) if flags else 0.0
