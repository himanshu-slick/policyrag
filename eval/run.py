"""Retrieval eval: recall@5 and MRR for vector-only vs hybrid vs hybrid+rerank.

Needs only Postgres (no API key). Writes eval/results.md.
Run: make eval
"""
import json
from pathlib import Path

from eval.score import mrr, recall_at_k
from policyrag.db import connect
from policyrag.retrieve import search

HERE = Path(__file__).parent
MODES = [("vector", "Vector only"), ("hybrid", "Hybrid (RRF)"), ("rerank", "Hybrid + rerank")]


def load_questions() -> list[dict]:
    return [q for q in json.loads((HERE / "questions.json").read_text()) if q["doc"]]


def run_mode(mode: str, questions: list[dict], conn) -> list[list]:
    return [search(q["question"], mode=mode, top_k=5, conn=conn) for q in questions]


def table(rows: list[tuple[str, float, float, float]], n: int) -> str:
    lines = [f"Retrieval on {n} answerable questions (gold = doc + section).", "",
             "| Method | recall@1 | recall@5 | MRR |", "|---|---|---|---|"]
    lines += [f"| {name} | {r1:.1%} | {r5:.1%} | {m:.3f} |" for name, r1, r5, m in rows]
    return "\n".join(lines) + "\n"


def main() -> None:
    questions = load_questions()
    rows = []
    with connect() as conn:
        for mode, name in MODES:
            hits = run_mode(mode, questions, conn)
            rows.append((name, recall_at_k(hits, questions, 1), recall_at_k(hits, questions),
                         mrr(hits, questions)))
    out = table(rows, len(questions))
    (HERE / "results.md").write_text(out)
    print(out)


if __name__ == "__main__":
    main()
