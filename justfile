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
