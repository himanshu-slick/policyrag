"""Answer eval: answer match, citation hit and LLM-judged faithfulness.

Needs GEMINI_API_KEY for the first run; every response is cached in eval/cache,
so later runs (and CI with POLICYRAG_OFFLINE=1) replay without a key.
Run: make eval-live
"""
import json

from eval.run import HERE, load_questions
from eval.score import answer_match, rate
from policyrag.answer import answer, format_sources
from policyrag.llm import generate
from policyrag.retrieve import search

JUDGE = """Sources:
{sources}

Answer: {answer}

Is every claim in the answer directly supported by the sources? Reply with JSON only:
{{"supported": true}} or {{"supported": false}}"""


def faithful(question: str, result: dict) -> bool:
    hits = search(question, top_k=5)
    prompt = JUDGE.format(sources=format_sources(hits), answer=result["answer"])
    return '"supported": true' in generate(prompt).replace('":true', '": true')


def main() -> None:
    questions = load_questions()
    results = [answer(q["question"]) for q in questions]
    match = [answer_match(r["answer"], q["expected"]) for r, q in zip(results, questions)]
    cited = [bool(r["citations"]) for r in results]
    faith = [faithful(q["question"], r) for q, r in zip(questions, results)]
    out = (f"Answers on {len(questions)} questions: answer match {rate(match):.1%}, "
           f"cited {rate(cited):.1%}, faithfulness {rate(faith):.1%}\n")
    (HERE / "results_live.md").write_text(out)
    print(out)
    print(json.dumps([r["answer"] for r in results[:3]], indent=1))


if __name__ == "__main__":
    main()
