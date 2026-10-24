"""Disk cache for model responses, keyed by (model, prompt hash).

POLICYRAG_OFFLINE=1 turns a cache miss into an error, which is how CI runs.
"""
import hashlib
import json
import os
from collections.abc import Callable

from policyrag.config import CACHE_DIR


class CacheMiss(RuntimeError):
    pass


def _path(model: str, prompt: str):
    digest = hashlib.sha256(prompt.encode()).hexdigest()[:32]
    return CACHE_DIR / model.replace("/", "_") / f"{digest}.json"


def cached(model: str, prompt: str, call: Callable[[], str]) -> str:
    path = _path(model, prompt)
    if path.exists():
        return json.loads(path.read_text())["text"]
    if os.getenv("POLICYRAG_OFFLINE"):
        raise CacheMiss(f"no cached response for {model} / {path.name}")
    text = call()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"model": model, "prompt": prompt, "text": text}, indent=1))
    return text
