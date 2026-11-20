#!/bin/sh
# Run by the prek pre-commit hook: check the knowledge base as staged for this commit.
set -eu
git diff --cached --quiet -- docs/kb && exit 0
tree=$(git write-tree) || exit 1
parent=$(git rev-parse -q --verify HEAD || true)
commit=$(git commit-tree "$tree" ${parent:+-p $parent} -m staged) || exit 1
exec just ogy --rev "$commit" check
