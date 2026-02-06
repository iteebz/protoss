default:
    @just --list

install:
    @uv sync

ci:
    @uv run ruff format .
    @uv run ruff check . --fix
    @uv run ruff check .
    @uv run pyright
    @uv run pytest tests/ -q

trial:
    @uv run python trial_by_fire.py

lint:
    @uv run ruff check .

format:
    @uv run ruff format .

fix:
    @uv run ruff check . --fix

test:
    @uv run pytest tests/

cov:
    @uv run pytest --cov=src/protoss tests/

build:
    @uv build

publish: ci build
    @uv publish

clean:
    @rm -rf dist build .pytest_cache .ruff_cache __pycache__ .venv test-*
    @find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    @find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true

commits:
    @git --no-pager log --pretty=format:"%h | %ar | %s"
