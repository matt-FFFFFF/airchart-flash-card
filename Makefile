.PHONY: setup build test generate clean

setup:
	uv sync --all-groups

build: setup
	uv build

test: setup
	uv run ruff check .
	uv run basedpyright src tests
	uv run pytest -q

generate: setup
	uv run extract-legend

clean:
	rm -rf .pytest_cache .ruff_cache dist
