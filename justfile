# Protoss - Distributed AI coordination
default:
    @just --list

# Run development server
dev:
    @echo "🔹 Nexus online - Pylon grid powered"
    @poetry run python tests/integration/test_nexus.py

# Format code  
format:
    @poetry run ruff format .

# Lint code
lint:
    @poetry run ruff check .

# Run tests
test:
    @echo "⚔️ Zealots engaging in righteous tests"
    @poetry run python -m pytest tests/ -v

# CI pipeline
ci: format lint test

# Deploy the swarm
deploy:
    @poetry build && poetry publish