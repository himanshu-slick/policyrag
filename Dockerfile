FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
      postgresql postgresql-17-pgvector curl \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 1000 user
ENV PATH=/usr/lib/postgresql/17/bin:/home/user/.local/bin:$PATH \
    HF_HOME=/home/user/.cache/huggingface
WORKDIR /app
RUN pip install --no-cache-dir uv

COPY pyproject.toml ./
COPY src ./src
RUN uv pip install --system --no-cache --extra-index-url https://download.pytorch.org/whl/cpu -e .

# Bake both models into the image so the first request is not a download.
RUN python -c "from sentence_transformers import SentenceTransformer, CrossEncoder; \
SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2'); CrossEncoder('BAAI/bge-reranker-base')" \
    && chown -R user:user /home/user/.cache

COPY corpus ./corpus
COPY eval ./eval
COPY start.sh ./
RUN chown -R user:user /app && chmod +x start.sh
USER user
EXPOSE 7860
CMD ["./start.sh"]
