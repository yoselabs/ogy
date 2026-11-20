#!/bin/sh
# Run by the prek pre-commit hook: check the knowledge base as staged for this commit. Every commit, not only one that touches
# docs/kb: a code rename can break a `code:` source (missing-code) without a knowledge-base change.
set -eu
tree=$(git write-tree) || exit 1
parent=$(git rev-parse -q --verify HEAD || true)
commit=$(git commit-tree "$tree" ${parent:+-p $parent} -m staged) || exit 1
# A commit straight on the base branch lands: it must also pass the landing checks.
case $(git symbolic-ref --short -q HEAD || true) in
  main | master) exec just ogy --rev "$commit" check --landing ;;
esac
exec just ogy --rev "$commit" check
