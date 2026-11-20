set allow-duplicate-recipes
import '.blueprint/base.just'
import '.blueprint/python.just'
import '.blueprint/shell.just'

set shell := ["bash", "-euo", "pipefail", "-c"]

# Install the locked environment.
install:
    uv sync --frozen

# The CLI from this checkout: just ogy check --rev .
[positional-arguments]
ogy *args:
    uv run --frozen --no-sync python -I -m ogy "$@"

# Import edges (import-linter contracts in pyproject.toml): the MCP libraries stay in the server module, the layers point one way, no cycles.
[group('gate')]
arch:
    uv run lint-imports

# The gate's one extension point (see .blueprint/base.just).
[private]
check-extra: arch
