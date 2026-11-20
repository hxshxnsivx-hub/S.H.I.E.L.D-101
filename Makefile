.PHONY: test run demo console docker-build docker-run compose-up

test:
	python -m unittest discover -s tests -p "test_*.py"

console:
	python -m kavach.console.server

demo:
	python scripts/demo.py
	python scripts/demo_sdk.py
	python scripts/demo_audit.py

docker-build:
	docker build -t kavach:latest .

docker-run:
	docker run --rm -p 8765:8765 kavach:latest

compose-up:
	docker compose up --build
