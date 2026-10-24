import time
from collections import defaultdict, deque

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from policyrag.answer import answer

app = FastAPI(title="PolicyRAG")

LIMIT, WINDOW = 10, 60  # requests per IP per minute: keeps a public demo inside free-tier quota
_seen: dict[str, deque] = defaultdict(deque)


def check_rate(ip: str, now: float | None = None) -> bool:
    now = time.monotonic() if now is None else now
    recent = _seen[ip]
    while recent and now - recent[0] > WINDOW:
        recent.popleft()
    if len(recent) >= LIMIT:
        return False
    recent.append(now)
    return True

PAGE = """<!doctype html><title>PolicyRAG</title>
<h1>PolicyRAG</h1>
<form onsubmit="ask(event)"><input id=q size=60 placeholder="Ask about a policy">
<button>Ask</button></form><pre id=out></pre>
<script>async function ask(e){e.preventDefault();
const r=await fetch('/ask',{method:'POST',headers:{'content-type':'application/json'},
body:JSON.stringify({question:q.value})});
out.textContent=JSON.stringify(await r.json(),null,2)}</script>"""


class Ask(BaseModel):
    question: str
    top_k: int = 5


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/ask")
def ask(body: Ask, request: Request) -> dict:
    ip = request.headers.get("x-forwarded-for", request.client.host).split(",")[0]
    if not check_rate(ip):
        raise HTTPException(429, "Too many requests, try again in a minute.")
    return answer(body.question, body.top_k)


@app.get("/", response_class=HTMLResponse)
def demo() -> str:
    return PAGE
