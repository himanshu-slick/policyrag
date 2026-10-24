import os
import time

from policyrag.cache import cached
from policyrag.config import GEMINI_MODEL


def _gemini(prompt: str, model: str) -> str:
    from google import genai
    from google.genai import errors, types

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    config = types.GenerateContentConfig(temperature=0)
    for attempt in range(5):
        try:
            return client.models.generate_content(
                model=model, contents=prompt, config=config
            ).text or ""
        except errors.APIError as err:
            if err.code != 429 or attempt == 4:
                raise
            time.sleep(2**attempt * 4)  # free-tier rate limit: back off and retry
    return ""


def generate(prompt: str, model: str = GEMINI_MODEL) -> str:
    return cached(model, prompt, lambda: _gemini(prompt, model))
