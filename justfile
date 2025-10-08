default:
    @just --list

clean:
    @echo "Cleaning protoss..."
    @rm -rf dist build .pytest_cache .ruff_cache __pycache__ .venv test-*
    @find . -type d -name "__pycache__" -exec rm -rf {} +
    @find . -type d -name ".pytest_cache" -exec rm -rf {} +

install:
    @poetry lock
    @poetry install

ci: format fix test

trial:
    @poetry run python trial_by_fire.py

format:
    @poetry run ruff format .

lint:
    @poetry run ruff check .

fix:
    @poetry run ruff check . --fix --unsafe-fixes

test:
    @poetry run python -m pytest tests/ -v

build:
    @poetry build

publish: ci build
    @poetry publish

cov:
    @poetry run pytest --cov=src/protoss tests/

commits:
    @git --no-pager log --pretty=format:"%h | %ar | %s"