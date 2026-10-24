"""Cited answers with an abstain path when retrieval is weak."""
import re

from policyrag.config import GEMINI_MODEL, MIN_RERANK_SCORE
from policyrag.llm import generate
from policyrag.retrieve import Hit, search
from policyrag.tracing import Tracer

NOT_FOUND = "Not found in the policy documents."
PROMPT = """You answer questions about insurance policies using ONLY the numbered sources.
Cite every claim with its source number in square brackets, like [1].
If the sources do not contain the answer, reply with exactly NOT_FOUND.

Sources:
{sources}

Question: {question}
Answer:"""


def format_sources(hits: list[Hit]) -> str:
    return "\n\n".join(
        f"[{i}] {h.title}, section {h.section_no} ({h.section}), page {h.page}:\n{h.content}"
        for i, h in enumerate(hits, 1)
    )


def cited_hits(text: str, hits: list[Hit]) -> list[Hit]:
    numbers = sorted({int(n) for n in re.findall(r"\[(\d+)\]", text)})
    return [hits[n - 1] for n in numbers if 1 <= n <= len(hits)]


def is_weak(hits: list[Hit]) -> bool:
    return not hits or hits[0].score < MIN_RERANK_SCORE


def _result(text: str, hits: list[Hit], abstained: bool) -> dict:
    cites = [] if abstained else [h.citation() for h in cited_hits(text, hits)]
    return {"answer": text, "citations": cites, "abstained": abstained}


def answer(question: str, top_k: int = 5) -> dict:
    tracer = Tracer("ask", question)
    hits = search(question, mode="rerank", top_k=top_k)
    tracer.span("retrieve", question, [dict(h.citation(), score=h.score) for h in hits])
    if is_weak(hits):
        result = _result(NOT_FOUND, hits, abstained=True)
    else:
        prompt = PROMPT.format(sources=format_sources(hits), question=question)
        text = generate(prompt).strip()
        tracer.generation("answer", GEMINI_MODEL, prompt, text)
        abstained = "NOT_FOUND" in text
        result = _result(NOT_FOUND if abstained else text, hits, abstained)
    tracer.finish(result)
    return result
