set dotenv-load

install:
	uv sync

build:
	uv build

publish: clear build
	uv publish --token $PYPI_TOKEN

dev:
	uv sync

format:
	uv run ruff format .

lint:
	uv run ruff check .

fix:
	uv run ruff check --fix .

demo:
	uv run python demo/demo.py

simple-demo:
	uv run python demo/simple_demo.py

clear:
	rm -rf dist
