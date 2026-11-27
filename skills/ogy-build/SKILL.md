---
name: ogy-build
description: Build what an ogy knowledge base describes and prove it built - pick a work item, implement it, write the test
  that proves it, name that test as the entry's proof, and let a test run write the built line. Use when implementing,
  fixing or re-proving entries that `ogy work` lists as unbuilt or changed, or when asked what proving or stamping means.
---

# OGY build (draft, 2026-11-27)

Status: **proposed, untested as a skill** (evals/ledger.md). Decisions behind it: `software/ontology/decision/built-line-writer`
(the test run writes the lines), `software/ontology/decision/stamping-across-languages` (this skill for now; a deterministic
writer for every language later), `software/ontology/decision/which-kinds-need-proof`, `done-is-rolled-up`. The knowledge
base says what to build and why; this skill says how a build becomes "built" in it. Never write a built line or kb YAML by hand.

## 1. What "built" means

| word | what it is |
|---|---|
| proof | a field on an entry: the tests that show it works, each `<path>::<function>` (`<path>::<Class>::<method>`); the file must exist and define it (`ogy check` refuses otherwise) |
| built line | a line ogy keeps under `docs/kb/built/`: the entry's build hash when its proofs last passed, and the hashes of its `src` |
| built | the entry's line matches the entry now; `ogy work` stops listing it |
| changed | the entry, its proofs or a build input changed after its line was written: prove it again |
| done (planned, `ogy-d6h`) | a workflow, capability or goal whose provable entries are all built; computed, never written |

Kinds that need a proof: the rows of a workflow (choice, case, timeout), a rule, an interface, a setting, a workaround, and an
entity while it has transitions. A step, a handler, a quantity, a goal, a capability, a pain, a decision or a principle never
carries one: what is above the provable entries is done when they are (`ogy kinds <kind>` says which).

## 2. The loop

1. **Pick** a work item from `ogy work <layer>` under "build" (unbuilt or changed). Read it whole: `ogy show <address>`, its
   workflow, the goal and pains above it, the decisions that set it and the rules it is held to (`ogy work <address>` will print
   all of it, `ogy-i6v`). An item with a why or a description still missing is not build work: it goes back to design.
2. **Implement** the behaviour the entry states. The entry's sentence is the contract; if the code must do otherwise, the entry
   is wrong: change it through `ogy put` (the owner sees it again), never the code alone.
3. **Prove**: write the test at the highest level that shows the behaviour (`docs/agents/testing.md`), one scenario per row or
   rule. See it red before it is trusted: break the code, watch it fail, restore.
4. **Name it**: `ogy put '[{"address": "<entry>", "proof": ["tests/test_x.py::test_y"]}]'`. Several tests may prove one entry;
   all must pass for it to be built.
5. **Stamp**: run the tests with stamping (section 3). Commit the built lines with the code and the entry.
6. **Hand over**: `ogy work <layer>` no longer lists the entry; `ogy check` is clean.

## 3. Stamping

Only a test run writes built lines; no command does, so a line always means a test passed.

- **Python (pytest)**: `pytest --ogy-stamp` (`just stamp` in ogy). Before the tests it reads the knowledge base; at the end it
  writes the line of every entry whose every proof passed in that run. A proof that failed, for any parameter, deletes the
  entry's line. Skipped, expected-to-fail and not-run proofs leave the entry as it was, so a partial run (`-k`, one file) is safe.
  Under pytest-xdist only the controller writes. The gate does not stamp: it runs in the Git hooks, and writing there would leave
  files uncommitted.
- **Other languages (TypeScript, Rust)**: no writer yet (`ogy-93t`). Write the proof and name it all the same; the entry stays
  unbuilt in `ogy work` until a writer exists. Do not stamp by hand and do not write a built line.

## 4. When something is off

| you see | do |
|---|---|
| `missing-proof ... names no test` | the test was renamed or moved: point the proof at it with `ogy put` |
| an entry stays unbuilt after a green run | one of its proofs did not run, was skipped or is not named; run them all |
| `changed` after a refactor | the entry, its proofs or an input changed: run its proofs with stamping again |
| `code changed since captured` | the `src` symbol changed: check the entry still says what the code does, then stamp |
| a test fails | its entry's line is deleted on the next stamping run: fix the code, or change the entry with the owner |

## 5. What this skill does not do

It does not decide what to build (that is `ogy work` and the owner's decisions), it does not capture requirements
(`ogy-capture`), and it does not make proofs deterministic for every language: that is decided later.
