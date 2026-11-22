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

# Every tracked shell script passes shellcheck at its default severity (same behaviour as .blueprint/shell.just).
[group('gate')]
scripts scope="changed":
    #!/usr/bin/env bash
    set -euo pipefail
    command -v shellcheck >/dev/null || { echo "scripts: shellcheck is not installed -- run just tools" >&2; exit 2; }
    list=$(mktemp); trap 'rm -f "$list"' EXIT
    uv run python -m any_gate changed --scope {{ scope }} --config .shellcheckrc '*.sh' > "$list"
    [ -s "$list" ] || { echo "skipped scripts: no shell script changed"; exit 0; }
    xargs -0 shellcheck < "$list"

# Shell formatting: shfmt -d over every tracked script (style in .editorconfig); a diff and exit 1 when unformatted.
[group('gate')]
shfmt:
    #!/usr/bin/env bash
    set -euo pipefail
    command -v shfmt >/dev/null || { echo "shfmt: not installed -- run just tools" >&2; exit 2; }
    git ls-files -z '*.sh' | xargs -0 -r shfmt -d

# Shell tests: bats over tests/shell, scripts run in a temporary folder with their external binaries stubbed.
[group('gate')]
shell-test:
    #!/usr/bin/env bash
    set -euo pipefail
    command -v bats >/dev/null || { echo "shell-test: bats is not installed -- run just tools" >&2; exit 2; }
    bats tests/shell

# The knowledge base, through `ogy hook` (src/ogy/hooks.py), which runs the landing checks (an unfinished layer, a word nobody
# agreed) only on a land: in a push (prek's variables name its first ref), when the remote ref is the land branch (`land` in
# ogy.yml); else when the branch checked out is. An ordinary branch gets the plain `ogy check`. The hooks `ogy init` writes call the same entry point.
[group('gate')]
kb:
    #!/usr/bin/env bash
    set -euo pipefail
    ogy=(uv run --frozen --no-sync python -I -m ogy)
    if [ -n "${PRE_COMMIT_REMOTE_BRANCH:-}" ]; then
        printf '%s %s %s %s\n' "$PRE_COMMIT_LOCAL_BRANCH" "$PRE_COMMIT_TO_REF" "$PRE_COMMIT_REMOTE_BRANCH" "${PRE_COMMIT_FROM_REF:-0}" | "${ogy[@]}" hook pre-push
    else
        "${ogy[@]}" hook gate
    fi

# The gate's one extension point (see .blueprint/base.just).
[private]
check-extra: arch shfmt shell-test kb board-css-check board-js

# Standalone Tailwind; the built stylesheet ships in the Python package.
board-css:
    #!/usr/bin/env bash
    set -euo pipefail
    command -v tailwindcss >/dev/null || { echo "board-css: not installed -- run just tools" >&2; exit 2; }
    tailwindcss -i assets/board/board.css -o src/ogy/web/static/board.css --minify

# Rebuild without touching the shipped stylesheet; stale output is a gate failure.
[group('gate')]
board-css-check:
    #!/usr/bin/env bash
    set -euo pipefail
    command -v tailwindcss >/dev/null || { echo "board-css-check: not installed -- run just tools" >&2; exit 2; }
    built=$(mktemp); trap 'rm -f "$built"' EXIT
    tailwindcss -i assets/board/board.css -o "$built" --minify
    cmp "$built" src/ogy/web/static/board.css || { echo "board-css-check: stale CSS -- run just board-css" >&2; exit 1; }

[group('gate')]
board-js:
    #!/usr/bin/env bash
    set -euo pipefail
    command -v biome >/dev/null || { echo "board-js: not installed -- run mise install" >&2; exit 2; }
    biome format src/ogy/web/static/js

# The release gate: `check`, then every test with the coverage floor (`fail_under` in pyproject.toml).
[group('gate')]
check-all: check
    uv run pytest --cov
