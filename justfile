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

ci:
    @poetry run ruff format .
    @poetry run ruff check . --fix --unsafe-fixes
    @poetry run pytest tests/ -q

trial:
    @poetry run python trial_by_fire.py

format:
    @poetry run ruff format .

lint:
    @poetry run ruff check .

fix:
    @poetry run ruff check . --fix --unsafe-fixes

test:
    @poetry run pytest tests/

cov:
    @poetry run pytest --cov=src/protoss tests/

build:
    @poetry build

publish: ci build
    @poetry publish

commits:
    @git --no-pager log --pretty=format:"%h | %ar | %s"
