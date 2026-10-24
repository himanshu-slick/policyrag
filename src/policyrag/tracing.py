"""Langfuse tracing that quietly does nothing when no keys are configured."""
import os
from functools import lru_cache


@lru_cache(maxsize=1)
def _client():
    if not (os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY")):
        return None
    from langfuse import Langfuse

    return Langfuse()


class Tracer:
    def __init__(self, name: str, input: str):
        client = _client()
        self._trace = client.trace(name=name, input=input) if client else None

    def span(self, name: str, input, output) -> None:
        if self._trace:
            self._trace.span(name=name, input=input, output=output)

    def generation(self, name: str, model: str, input, output) -> None:
        if self._trace:
            self._trace.generation(name=name, model=model, input=input, output=output)

    def finish(self, output) -> None:
        if self._trace:
            self._trace.update(output=output)
            _client().flush()
