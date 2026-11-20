#!/bin/sh
# Run by the prek pre-commit hook: check the knowledge base as staged for this commit. Every commit, not only one that touches
# docs/kb: a code rename can break a `code:` source (missing-code) without a knowledge-base change.
set -eu
tree=$(git write-tree) || exit 1
parent=$(git rev-parse -q --verify HEAD || true)
commit=$(git commit-tree "$tree" ${parent:+-p $parent} -m staged) || exit 1
exec just ogy --rev "$commit" check
