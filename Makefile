.PHONY: up ingest eval eval-live test lint serve mcp
up:
	docker compose up -d db
ingest:
	python -m policyrag.ingest
eval: ingest
	python -m eval.run
test:
	pytest -q
lint:
	ruff check .
serve:
	uvicorn policyrag.api:app --reload
mcp:
	python -m policyrag.mcp_server
eval-live: ingest
	python -m eval.live
