from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from policyrag.answer import answer

app = FastAPI(title="PolicyRAG")

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
def ask(body: Ask) -> dict:
    return answer(body.question, body.top_k)


@app.get("/", response_class=HTMLResponse)
def demo() -> str:
    return PAGE
