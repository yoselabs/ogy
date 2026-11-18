set shell := ["bash", "-euo", "pipefail", "-c"]

# Install the locked environment.
install:
    uv sync --frozen

# Lint.
check:
    uvx -q ruff@0.17.2 check src tests evals

# Tests.
test:
    uv run --frozen --no-sync pytest -q

# The CLI from this checkout: just ogy check --rev .
[positional-arguments]
ogy *args:
    uv run --frozen --no-sync python -I -m ogy "$@"
