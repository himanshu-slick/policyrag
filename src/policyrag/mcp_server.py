"""MCP server exposing PolicyRAG to any MCP client (stdio transport)."""
from mcp.server.fastmcp import FastMCP

from policyrag.answer import answer
from policyrag.retrieve import search

mcp = FastMCP("policyrag")


@mcp.tool()
def search_policies(query: str, top_k: int = 5) -> list[dict]:
    """Search the policy corpus. Returns ranked passages with doc, section and page."""
    return [dict(h.citation(), text=h.content, score=h.score) for h in search(query, top_k=top_k)]


@mcp.tool()
def answer_question(question: str) -> dict:
    """Answer a question about the policies with citations, or say it was not found."""
    return answer(question)


if __name__ == "__main__":
    mcp.run()
