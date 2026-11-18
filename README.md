# ogy

A requirements ontology as one product: a checked YAML knowledge base, the `ogy` library and CLI, a capture skill for
AI agents, and the eval suite that tests every change to them.

| Part | Holds | Where |
|---|---|---|
| Ontology | the shapes: kinds, origin marks, decisions, hazards, receipts | [docs/spec-v4.md](https://github.com/yoselabs/ogy/blob/979df808f576/docs/spec-v4.md) (draft); kinds as data in `src/ogy/ontologies/` |
| Library and CLI | read a knowledge base from Git or the worktree; check, show, impact, diff, work left | `src/ogy`; [docs/mvp-report.md](https://github.com/yoselabs/ogy/blob/979df808f576/docs/mvp-report.md) |
| Skills | `elicit` (generic: find gaps, derive, ask the fewest questions with a recommended answer each, read back) and `ogy-capture` (words, docs or code into entries, hazard pass, uses `elicit`) | [skills/elicit](skills/elicit/SKILL.md), [skills/ogy-capture](skills/ogy-capture/SKILL.md); a Claude plugin (`.claude-plugin/plugin.json`), listed in iorlas-marketplace |
| Eval suite | protocol, what every metric told us, every eval run | [evals/](evals/README.md): [metrics](evals/metrics.md), [ledger](evals/ledger.md) |
| Research | consults and probes behind the design | [docs/consults](https://github.com/yoselabs/ogy/blob/979df808f576/docs/consults), [docs/probes](https://github.com/yoselabs/ogy/blob/979df808f576/docs/probes) |

## Use

```bash
uvx --from git+https://github.com/yoselabs/ogy ogy check
```

Two modes. CLI: agents run `ogy` next to the tracker's own CLIs and MCPs. Library: a program such as the task
factory imports `ogy` and builds tickets from the typed structures it returns; ogy itself has no tracker adapters.
Distribution is not decided (bead ogy-yy9.16).

Set a repository up once with `ogy init [--ontology software]` (below). Settings live in `ogy.yml` at the
repository root (`ontology`, optional `rev`; `$OGY_CONFIG` names another file); a flag overrides it. The knowledge base is always
the folder `docs/kb`: there is no flag or setting that moves it.

Commands. The flags `--repo`, `--rev` and `--ontology` go before or after the command (`ogy --rev HEAD check` or `ogy check --rev HEAD`). `--rev` is a commit,
or `.` for the worktree, which is the default: a read sees what was just written. CI reads a commit with `--rev HEAD`.
A `docs/kb` that is not there, or a commit that does not exist, is a refusal, never a green check.

Exit codes: 0 ok, 1 findings (`check`, `work`, a `reply` with an item refused), 2 usage, 3 refused, 4 not found.
Refusals and usage errors print to stderr. Over MCP codes 2 to 4 are tool errors. Every `ogy.ops` result carries its
`verdict` (`ok`, `findings`, `refused`, `not found`) so a library caller needs no exit code.

| Command | Does |
|---|---|
| `check [area] [--base <commit>] [--landing]` | the problems of the knowledge base (of one area); with a base, also what it forbids changing |
| `status [area] [--coverage]` | counts per layer and area, findings, work left, dropped; saves nothing. `--coverage` also lists, per layer, the kinds with no entry |
| `show <address>` | one entry with its fields, parents, parts, links, status, decision, sources and built line; for a miss, near addresses |
| `find [words] [--kind] [--area] [--state] [--removed] [--parent <address>]` | live and removed entries by words and filters, as a table |
| `impact`, `diagram <address>` | what a change reaches and what reaches it; the flow as Mermaid |
| `diff <before> <after>` | what changed between two commits or the worktree, entry by entry |
| `work [area]` | what the built record says is still to do |
| `review [area] [--all]` | what you are asked (at most 7 cards); it **saves a round** and prints its id |
| `dropped` | what no person has seen (end a session with it) |
| `glossary [layer/area]`, `kinds [kind] [--readers]` | the constitution, then the terms of the product: the shared ones of each layer, then each area's (for one area: its terms and the shared ones it reads, a software area product's too); the kinds of the ontology, or one. `--readers` lists for each field what reads it (the fingerprint, requires, a fingerprint path, flow, settling, links and impact, the review rank, a named check or printer) and ends with the fields nothing reads and those only the fingerprint reads |
| `remove <address> --why <address or words> [--to]` | delete an entry and record it in its `removed.yml` (always the worktree; one write lock). `--why` is always required: the address of the decision that said so, or plain words (an address stays required for an entry a person agreed to); `dropped` lists the plain-words ones |
| `move <address> <area \| layer/area>` | move an entry and what it owns to another area, keeping its kind, id and agreements; in the same write the new address replaces the old one everywhere (links, decisions, answers, removed items' `why`), and an agreement that was current stays current. It records nothing: Git keeps the move, and `check --base` tells it (same kind, id and fingerprint) from a loss |
| `migrate` | rewrite the entries to the field renames, drops and moves out of a fixed folder their kinds declare (see "Kind changes"); one checked write that records nothing |
| `history <address \| layer/area>` | what changed, who said so, what is in force, when it was built; computed from Git |
| `mcp` | serve all of the above as MCP tools over stdio |
| `init` | set the repository up (see "Init") |
| `put [records ...] [--file <path>]` | the one way to add and change entries: one or many records (JSON or YAML, a mapping or an array, as arguments, a file, or `--file -` for standard input; over MCP an array of such texts). A record is `address` (or `kind`, `layer`, `area`, `id`) and the entry's fields; an address that exists is changed (`field: null` removes a field), a new one is added. The batch is validated together (a decision and the entries its options set may arrive in one call) and written under the lock whole, or not at all |
| `answer <decision> <option> --said <paraphrase> --where <uri> [--at <iso>] [--from human\|ai] [--note <text>] [--delegated <decision>]` | choose the option: appends the answer `{chose, said, from, at, where, note?, delegated?}` and applies the option's `sets`; it agrees to no sentence (those entries read "from your words" until a `reply` `yes`). `said` is one short line, the agent's paraphrase of what the person said; `--note` is their hedge or condition, paraphrased. There is no `agree`: only a review round's `yes` agrees to a sentence |
| `reply <grammar line> --said <paraphrase> --where <uri> [--at <iso>] [--round <id>] [--note <text>]` | apply the owner's reply to a review round; nothing is written when nothing applies. The text is the grammar line: the owner's, or the agent's reading of their natural words. Every answer and agreement it writes keeps `said`, `at`, `where` and `from: human` |

### Init

`ogy init` is idempotent and merges, never clobbers. It writes `ogy.yml`; creates `docs/kb` with `constitution/principles.yml` and the area `product/shared` (its `area.yml`);
adds a marked block (managed-region) to `AGENTS.md`, and to `CLAUDE.md` when it exists, that tells agents to change the
knowledge base only through ogy and to run `ogy glossary` first (the constitution, then the glossary); adds the `ogy` server (`ogy mcp`) to `.mcp.json`; adds
`Edit` and `Write` deny rules for `docs/kb/**/*.yml` to `.claude/settings.json`.

### Writing

Agents change the knowledge base only through these commands (CLI or MCP tool of the same name), never by editing YAML.
- Each is one operation in `ogy.ops`, runs on the worktree (`--rev` does not apply) under the ogy lock, and is atomic.
- After the write `ogy check` runs; a new error on the files or entries touched puts every file back and refuses.
- ogy stores no messages and no quotes. An answer is `{chose, said, from, at, where, note, delegated}` appended to the
  decision: `said` is one short line, the agent's paraphrase of what the person said, fitted to the decision; `from` is
  `human` or `ai` (an enum of the answer kind); `at` is when, `where` the session (`ai:claude/<session-id>`). The answer
  with the newest `at` is in force. `note` is the owner's hedge or condition (outside the fingerprint; `show` prints it,
  `dropped` lists answers that have one). Nobody writes a status: it is computed.
- A person's yes in a review round is kept on the entry it agrees to: `agreed: {at, where, from: human, said, hash}`
  (outside the fingerprint, written only by `reply`; `put` refuses it). Only `from: human` agrees. The entry is "decided by
  you" while its fingerprint is `hash`, "changed since you agreed" after. A person's yes is evidence of its own.
- A guess that rests on what the owner said carries a paraphrase: `guess.heard: {said}`. The review card reads
  "You said (paraphrased): .... Read as B." and one `yes` records the answer, chosen option B.
- `ogy review` keeps the cards it showed as a round, by id (the last 10, in the Git directory).
  `ogy reply --round <id>` resolves against that round (required over MCP; on the CLI the newest round is the default): `yes`, `yes 1 3`, `2: <new sentence>` (replaces and agrees), `no 4` (the sentence becomes a
  question; why, paraphrased, goes in `--said`), `Q1 b` (option B or its key), `later`, `yes all` (or `decide`: every question gets its recommended option, the guess, and
  every card is agreed to; a card that changed stays in the queue and is reported; a structural decision stays too, see Layout). A bare `yes` to a round shown with `--all` is
  refused: name the cards, or spell `yes all`. A card whose entry changed since it was shown is refused and stays in
  the queue. Natural words ("Fine, go ahead, I suppose.") are read by the agent as a grammar line (`yes`), with the hedge
  in `--note`; the words themselves are not stored. A bare `yes` (or `yes Q2`) also confirms
  questions whose guess rests on what the owner said (`heard`), except a structural decision. `ogy review` prints, before the reply line,
  what a bare `yes` will change.
- Who confirms (E1, for now): a person, written `from: human`, no name; the actor `human` (`nature: human`) says who they are:
  `ogy put '{"address": "product/<area>/actor/human", "says": "...", "nature": "human"}'`. An actor says who uses the
  product, not a claim, so it needs no evidence. Delegation: only when the owner says "decide on my behalf" for a scope,
  that is the owner's answer to a decision; the agent then answers others with
  `ogy answer ... --from ai --delegated <that decision>`. Such an answer is in force at once, and `ogy dropped` lists it
  so the agent names it at session end for the owner's veto. An `ai` answer without a `delegated` decision whose answer in
  force is a person's is the check `bad-delegation`. A scope is only that decision's question; ogy models no more than
  this.

### Layout

The ontology declares where entries live (`ontologies/software/ontology.yml`) and the loader enforces it; nothing skips a level.
`docs/kb/constitution/principles.yml` holds the principles (a principle is cited with `because`); every other file is `docs/kb/<layer>/<area>/<kind>/<id>.yml` (a list kind:
`<layer>/<area>/<file>`; a single kind: one entry in `<layer>/<area>/<file>` whose id is the area), the layer being `product` or `software`.
Every area holds its `area.yml` (kind `area`: `says`, what the area covers; `distinct`, what belongs in a neighbouring area): the kind
declares `every_area`, so an area folder without it is `missing-entry`, and a write into a new area brings it in the same call. It needs
no proof and is never asked (`asked: false`); which product areas a software area builds is computed from links. The fixed folder
`constitution/` is no area. An area or kind at the top, or an unknown layer, is `bad-path`. A folder that holds only its `removed.yml`
is an area no more.
- The glossary is the kind `term`: each area's words in `<layer>/<area>/glossary.yml`. A term is compressed: `word`, `says` (one
  line of under 15 words, else `term-too-long`) and `avoid`; it keeps no sources (`evidence: none`): where a word is used is read
  from the sentences. Each layer has the reserved area `shared`, a
  normal area with its `area.yml`: a term, an actor or a set that two areas use lives there (`product/shared/glossary.yml`,
  `product/shared/actors.yml`), so every address keeps its area. Only the kinds marked `shared: true` (term, actor, set and area)
  may live there; any other is `bad-path`, and `ogy move` into `shared` refuses it. Which shared entry fewer than two areas use is
  not checked yet.
The folder is the layer's only home: an entry has no `layer` field, each kind lists the layers it may appear in (`layers:`), and an
entry in another one is `bad-layer`. An address is `<layer>/<area>/<kind>/<id>`. A business actor lives in product, a technical one
(CI, a scheduler, a program calling us) in software.
- `doc:` evidence pins a Git revision (`doc:<commit>:<path>#<anchor>`): the file may be deleted later, history stays. An unpinned one is `bad-src`.
- `ogy status --coverage` lists, per layer, the kinds with no entry. An area named like the repository is the finding `product-area`
  (name a topic, not the product). Every finding is an error: ogy prints no warnings.
- A decision with `structure: true` (harm tag `structure`: layout, layers, kinds, paths) is asked on its own card: `yes`, `yes all` and
  `decide` leave it, and `review` says it needs its own letter.

### Kind changes

A kind file may change under a knowledge base that a newer ogy reads. Adding a field changes no fingerprint (an unset field is
outside it), so nothing goes stale. A rename or a drop is declared in the kind file and kept there until the knowledge bases
it serves are migrated: `renamed: {old: new}` (the new name is a field of the kind) and `dropped: [old]`. An entry that still
holds an old name is the finding `needs-migration`. `ogy migrate` writes the migration in one checked write:
- every old name becomes the new one, in the entry, in the items of its list parts (answers) and in the fields an option's
  or a guess's `sets` gives an entry of that kind;
- a pure rename changes no meaning: an agreement or a built line (`own` and `deps`) that was current stays current, its
  hash re-set to the fingerprint after the rename, as `ogy move` does;
- a dropped field that held a value changes the meaning: `migrate` prints the value, and the agreement and the built line of
  the entry (and of entries whose fingerprint reads it) are left, so the owner sees it as changed since agreed and it is work;
- a kind that moved out of a fixed folder declares the file it was in, `moved_from: <folder>/<file>` (the term kind:
  `glossary/terms.yml`). Its entries there are `needs-migration`; `migrate` moves them to the area `shared` of the kind's first
  layer (with that area's `area.yml` when it has none), renames every address under the old folder (links, `sets` keys, the
  removed items of the folder's `removed.yml`, which moves too) and keeps the agreements current. Then `ogy move` each entry to the
  area that uses it;
- `check --base` reads the base migrated, so a migration commit is no edit of an append-only part. Removed items keep the
  names they had; nothing is recorded (Git keeps the old names).
The old fingerprints are computed under the kinds as they were (`kindchange.before`). A changed field type, a renamed kind
key or a renamed part kind is no declared change: it needs a one-off migration on the write path.

### MCP

`ogy mcp` starts a stdio MCP server with one tool per command above (the tools are generated from the CLI, so a new
command appears without an edit). Every tool describes itself (its description is the command's own; `init` and `mcp` are no tools). Agents get tables (`check`, `work`, `find`, `dropped`, `impact`, `diff`) as lean-wire TSV with their header even when empty, and records (`show`, `status`) as YAML; no Python reprs. Add it to
`.mcp.json` at the repository root; the server starts there, so `--repo` defaults to it:

```json
{"mcpServers": {"ogy": {"command": "uvx", "args": ["--from", "git+https://github.com/yoselabs/ogy", "ogy", "mcp"]}}}
```

## The software ontology

The packaged ontology (`src/ogy/ontologies/software`) describes a software product; each kind is a file in `kinds/`.
- Where: `area` (what one area covers).
- Why: `goal`, `actor`, `capability`, `rule`, `term` (the glossary), `principle` (the constitution).
- What it does: `workflow` with its `step`s, `choice`s, `case`s, `timeout`s, `effect`s and `end`s; `view` and `command`
  that serve steps; `operation` that performs them; `guard` on entering.
- What it keeps: `entity` with `attr`, `state` and `transition`; `value` (a number with a unit), `config_key`, `set`.
- What it depends on: `external` and its `deviation`s.
- What is open and what the owner chose: `decision` with `option`, `guess` (and its `heard`) and `answer`.
- Held to: a row, an external, a workflow, an entity, an attribute or a guard names the rules it is held to with `by`; a
  rule has no `on`. `by` is outside the fingerprint of all but the rows, so adding a rule stales no holder; the pin of an
  external held to a rule is part of the rule's fingerprint (`fingerprint.reached`), so a new pin makes its proofs work again.

An entry has its own evidence (`src`: `code:<path>#<symbol>` or `doc:<commit>:<path>#<anchor>`; or a `because` chain
that reaches one; or a decision that settles it; or a person's yes, `agreed`), or `ogy check` says `no-evidence`. `proof` is `<path>.py::<function>`.
A kind or a field may declare `harm:` (what a wrong sentence costs), which ranks the review queue.

## Where the code lives

ogy holds business logic: kinds, checks, status, decisions, the removed ledger and the built record. Technical details
live in [shelf](https://github.com/yoselabs/shelf) packages: Git access (`git-porcelain`), YAML (`any-yaml`, `yaml-merge`),
Markdown anchors (`any-markdown`), hashes (`content-digest`), Python symbols (`py-symbols`), MCP tools (`argparse-mcp` on
FastMCP 3), atomic writes (`atomic-io`), the write lock (`process-lock`), agent tables (`lean-wire`), settings and managed
blocks (`settings-base`, `managed-region`). `test-reach` is a dev dependency with pytest. `ruff.toml` bans the raw libraries
(ruamel, ast, hashlib, coverage, pytest, argparse internals, raw git) in `src`. See [docs/shelf-audit.md](https://github.com/yoselabs/ogy/blob/979df808f576/docs/shelf-audit.md).

## Develop

`just install`, then `just check` and `just test`. `just ogy <args>` runs the CLI from this checkout.

## What goes where

Ask: **would a different capture flow still need it?**
- If yes, it is a shape: the ontology.
- If it is how an agent works, it is the skill: question budget, ranking, read-aloud test, hazard questions.
- If a machine can decide it, it is a checker lint.

Elicitation is split across these three parts:
- the ontology holds its data: `decision` entries, `?open {decision}` and paraphrases of what the owner said;
- the skill holds its procedure: find, derive, group, ask at most 7, read back;
- the checker computes the queue: which slots wait on which decision, and their ranks.

A change to the ontology or the skill names its eval in the [ledger](evals/ledger.md), or is marked untested.

## Origin

Extracted on 2026-11-17 from task-loop (`claude/nice-tu-f34e2d`, epic tl-8bh9.14.172). This folder is a Git repository;
the 7 commits of `src/ogy` history from task-loop are in its history. Tasks are in this folder's bd tracker (epic
`ogy-yy9`). task-loop holds no ogy code.
