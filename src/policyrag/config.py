import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parents[2]
CORPUS_DIR = ROOT / "corpus" / "pdfs"
CACHE_DIR = ROOT / "eval" / "cache"

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://policyrag:policyrag@localhost:5432/policyrag"
)
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBED_DIM = 384
RERANK_MODEL = "BAAI/bge-reranker-base"

CANDIDATES = 20  # per retriever, before fusion
# top rerank probability below this means "not found"
MIN_RERANK_SCORE = float(os.getenv("MIN_RERANK_SCORE", "0.3"))
