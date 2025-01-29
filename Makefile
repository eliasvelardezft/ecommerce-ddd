.PHONY: start

start:
	uvicorn src.main:app --reload --port 9000 