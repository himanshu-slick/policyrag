FROM python:3.12-slim
WORKDIR /app
RUN pip install --no-cache-dir uv
COPY pyproject.toml ./
COPY src ./src
COPY corpus ./corpus
COPY eval ./eval
RUN uv pip install --system --no-cache -e .
CMD ["sh", "-c", "python -m policyrag.ingest && uvicorn policyrag.api:app --host 0.0.0.0 --port 8000"]
