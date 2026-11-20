# Agent instructions

- Python 3.15+, `uv`, `just`. `just install`, `just check` and `just test` are the gates.
- No `subprocess` in `src/` or `tests/`; Git goes through shelf's `git-porcelain`. YAML goes through shelf's `any-yaml`;
  hashes, Python symbols, Markdown anchors, test reach and MCP tools through shelf too. `ruff.toml` bans the raw libraries.
- Caps: 400 lines per source file, 80 per function, 800 per test file. Tests are pytest functions or classes.
- Ontology, skill and checker changes: read [README](README.md) "What goes where". Every change names its eval in
  [evals/ledger.md](evals/ledger.md) or says it is untested. Every eval follows [evals/README.md](evals/README.md) and
  updates the ledger and [metrics](evals/metrics.md).
- A kind file change keeps `tests/test_tool_library.py` green: the tool library fixture (`tests/fixtures/tool-library`, written
  through ogy) holds every kind and fills every field, with its findings and work written down; a new kind or field goes into
  it, or into `UNEXERCISED` with why. A rename or a drop is declared in the kind file for `ogy migrate` (README, "Kind changes").
- Proposed decisions stay proposed until the owner decides. Do not commit, push or publish without the owner's word.
- Consult and capture sessions (v5, proposed; details in `skills/ogy-capture/SKILL.md`):
  - A proposal becomes a `decision` entry (or a new option of the one that asks that question) before it is acted on.
    "No", "not now" and "removed" are an option that sets the address to `null`; nothing is dropped silently.
  - A consult never ends with "open points". The session that receives it writes each proposal as a decision with a
    proposal before it reports; the owner is asked from `ogy review`, never from a pasted list.
  - Live capture: ogy stores no messages and no quotes. When the owner speaks, record the answer at once with a short
    paraphrase (`said`: one plain line in your words, fitted to the decision) and show it to the owner in the read-back:
    `ogy reply "<grammar line>" --said ... --where ...` for a review round, `ogy answer <decision> <option> --said ...
    --where ...` for a choice (one per decision when one sentence decides several). Never rebuild answers from a
    transcript later. Words that fit two options, or a bare `no`: ask at once.
  - Natural words that do not parse as the reply grammar ("Fine, go ahead, I suppose."): give your reading as the grammar
    line, `ogy reply "yes all" --said "<paraphrase>" --where ... --round <id> --note "<hedge, paraphrased>"`.
  - Search before proposing (`ogy find`, `ogy history`). Deleting a mechanism lists its jobs and where each one goes.
  - Change an entry's area only with `ogy move <address> <area>`; remove-and-put loses its agreements. A move records
    nothing (Git keeps it) and rewrites every address in the same write; a migration never removes anything.
  - Remove only when a requirement changes, with `ogy remove --why <decision or words>`; never edit a `removed.yml`,
    never reuse an id. Bringing something back is a proposal for the owner, not an edit.
  - Never edit an answer or answer for the owner. Questions and answers live in decision entries; a bead only mirrors.
  - Hand over: no error you may fix is left in `ogy check`; show the owner the waiting count (a term awaiting the owner's
    yes is not yours to clear) and what `ogy dropped` lists.
  - Session end: `ogy check`, `ogy dropped`, then the read-back opens with "Recorded today: N answers, M with a note",
    listing the answers recorded live with their paraphrases and any given for the owner under a delegation, so the owner
    can correct or veto one.
  - Write with `ogy put` (one batch for create and update; new, untested). Never write kb YAML by hand.
- AGENTS.md and CLAUDE.md are separate files with the same content: mirror every edit.

<!-- BEGIN BEADS INTEGRATION v:1 profile:minimal hash:1105d646 -->
## Beads Issue Tracker

This project uses **bd (beads)** for issue tracking. Run `bd prime` to see full workflow context and commands.

### Quick Reference

```bash
bd ready              # Find available work
bd show <id>          # View issue details
bd update <id> --claim  # Claim work
bd close <id>         # Complete work
```

### Rules

- Use `bd` for ALL task tracking — do NOT use TodoWrite, TaskCreate, or markdown TODO lists
- Run `bd prime` for detailed command reference and session close protocol
- Use `bd remember` for persistent knowledge — do NOT use MEMORY.md files

**Architecture in one line:** issues live in a local Dolt DB; sync uses `refs/dolt/data` on your git remote; `.beads/issues.jsonl` is a passive export. See https://github.com/gastownhall/beads/blob/main/docs/core-concepts/sync-concepts.md for details and anti-patterns.

## Agent Context Profiles

The managed Beads block is task-tracking guidance, not permission to override repository, user, or orchestrator instructions.

- **Conservative (default)**: Use `bd` for task tracking. Do not run git commits, git pushes, or Dolt remote sync unless explicitly asked. At handoff, report changed files, validation, and suggested next commands.
- **Minimal**: Keep tool instruction files as pointers to `bd prime`; use the same conservative git policy unless active instructions say otherwise.
- **Team-maintainer**: Only when the repository explicitly opts in, agents may close beads, run quality gates, commit, and push as part of session close. A current "do not commit" or "do not push" instruction still wins.

## Session Completion

This protocol applies when ending a Beads implementation workflow. It is subordinate to explicit user, repository, and orchestrator instructions.

1. **File issues for remaining work** - Create beads for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Close finished work, update in-progress items
4. **Handle git/sync by active profile**:
   ```bash
   # Conservative/minimal/default: report status and proposed commands; wait for approval.
   git status

   # Team-maintainer opt-in only, unless current instructions forbid it:
   git pull --rebase
   git push
   git status
   ```
5. **Hand off** - Summarize changes, validation, issue status, and any blocked sync/commit/push step

**Critical rules:**
- Explicit user or orchestrator instructions override this Beads block.
- Do not commit or push without clear authority from the active profile or the current user request.
- If a required sync or push is blocked, stop and report the exact command and error.
<!-- END BEADS INTEGRATION -->

<!-- BEGIN BEADS CODEX SETUP: generated by bd setup codex -->
## Beads Issue Tracker

Use Beads (`bd`) for durable task tracking in repositories that include it. Use the `beads` skill at `.agents/skills/beads/SKILL.md` (project install) or `~/.agents/skills/beads/SKILL.md` (global install) for Beads workflow guidance, then use the `bd` CLI for issue operations.

### Quick Reference

```bash
bd ready                # Find available work
bd show <id>            # View issue details
bd update <id> --claim  # Claim work
bd close <id>           # Complete work
bd prime                # Refresh Beads context
```

### Rules

- Use `bd` for all task tracking; do not create markdown TODO lists.
- Run `bd prime` when Beads context is missing or stale. Codex 0.129.0+ can load Beads context automatically through native hooks; use `/hooks` to inspect or toggle them.
- Keep persistent project memory in Beads via `bd remember`; do not create ad hoc memory files.

**Architecture in one line:** issues live in a local Dolt DB; sync uses `refs/dolt/data` on your git remote; `.beads/issues.jsonl` is a passive export. See https://github.com/gastownhall/beads/blob/main/docs/core-concepts/sync-concepts.md for details and anti-patterns.
<!-- END BEADS CODEX SETUP -->

<!-- BEGIN OGY -->
## Knowledge base (ogy)

The requirements knowledge base is the folder `docs/kb/`: `constitution/`, `product/<area>/` and `software/<area>/`, nothing else
at its top. Each layer has the area `shared` (`product/shared/`): only the terms, actors and enums that two of its areas use live
there; everything else lives in the area that owns it. Change it only through ogy (CLI or MCP); never edit its YAML by hand.
- Run `just ogy glossary` first, before reading code or writing a sentence: it prints the constitution (the principles every decision is
  judged against; cite one with `because`), then the glossary: the shared terms, then each area's (`<layer>/<area>/glossary.yml`);
  `just ogy glossary <layer>/<area>` prints one area's terms with the shared ones it reads. Read both; use the words it prints. A term
  is `word`, `says` (one line of under 15 words) and `avoid`, nothing else; it needs no source. A word one area uses goes in that
  area's glossary, one that two areas use in the `shared` area of their layer. `just ogy status` shows where things
  stand; `just ogy find <words>` searches live and removed entries (search before you propose); `just ogy show <address>` reads one.
- Before you create an entry of a kind, read `just ogy kinds <kind>`: what it is, its guidance (when to use it rather than its
  neighbours: an actor, a lifecycle state or an attribute; `satisfies` holds an entry to a rule, `because` cites a principle or a decision
  as the reason) and its fields. `just ogy kinds --map` prints the whole ontology on one screen, with its rules.
- Add and change entries with ONE command, `just ogy put`: one or many records, JSON or YAML, as arguments, `--file` or standard input
  (`just ogy put '[{"address": "<layer>/<area>/<kind>/<id>", "says": "..."}]'`). An address that exists is changed (`"field": null` removes a
  field), a new one is added; the whole call is checked together (a decision may come with the entries its options set) and written whole
  or not at all. A choice goes in with `just ogy answer`, a reply to a review round with `just ogy reply "<grammar line>"`;
  `just ogy remove --why` always says why (a decision address, or plain words); remove only when a requirement changes,
  never to reorganise. To change an entry's area use `just ogy move <address> <area>` (`<layer>/<area>` to change the layer too): the id
  and the owner's agreements stay, every address follows in the same write, and nothing is recorded (Git keeps it); never remove
  and put again.
- A newer ogy may rename or drop a field of a kind, rename a kind, or move a kind out of a fixed folder (the kind file says
  `renamed: {old: new}`, `dropped: [...]`, `was: {kind: <old>}` or `moved_from: <folder>/<file>`); `just ogy check` then reports `needs-migration`. Run `just ogy migrate`, never a hand
  edit: it renames and moves in one write and keeps the owner's agreements and the built lines current; a dropped field that held a
  value is printed, and that entry comes back to the owner as changed. What it moved lands in `product/shared`: `just ogy move` each
  entry to the area that uses it.
- Reads see the worktree by default (`--rev .`); a gate script reads a commit with `just ogy --rev HEAD check`. The flags `--repo --rev --ontology`
  go before or after the command: `just ogy show <address> --rev HEAD`.
- Every write is checked; fix what it refuses. Run `just ogy check` before you hand over: every finding is an error, there are no
  warnings. Exit codes: 0 ok, 1 findings, 2 usage, 3 refused, 4 not found.
- Every area folder holds its `area.yml` (`says`: what the area covers; `unlike`: what belongs in a neighbouring area); a put
  into a new area brings it in the same call. The first actor is the person:
  `just ogy put '[{"address": "product/<area>/area/<area>", "says": "..."}, {"address": "product/<area>/actor/human", "says": "...",
  "nature": "human"}]'`
  (an actor needs no evidence).
- ogy stores no messages and no quotes. When the owner speaks, record the answer at once with a short paraphrase:
  `just ogy answer <decision> <option> --said "<one plain line>" --where ai:<agent>/<session-id>` (`--note` for a hedge or condition), or
  `just ogy reply "<grammar line>" --said "..." --where ...` for a review round (`from: human`: only a person agrees). Show each
  paraphrase to the owner in the read-back. A proposal that rests on what the owner said carries a paraphrase (`proposal.heard`),
  so the review reads "You said (paraphrased): .... Read as B." and one yes records the answer.
- Never answer for the owner. Only when the owner said "decide on my behalf" for a scope (an answer `from: human` of a decision),
  answer with `just ogy answer ... --delegated <that decision>`; `just ogy dropped` lists those answers, and you list them to the
  owner at session end.
<!-- END OGY -->

<!-- BEGIN SHELF RESOLVER BLOCK — managed by shelf's onboarding; safe to re-run -->
### The shelf — shared micro-software you consume

This project consumes **the shelf** (`github.com/yoselabs/shelf`) — shared, ownable,
contract-guaranteed software pieces, pinned in `pyproject.toml` by git tag. Reach for it before
hand-rolling substrate; adopt only if **DEEP · STABLE · WINS**; contribute back by *promotion*.

**Three things fire the loop**, not one: substrate glue you are about to write; a bug whose root
cause was a *dependency's* behaviour; and — the quiet one — a dependency that worked fine and was
merely **verbose**, where you wrote an expression and thought "why isn't this a method?". "Stop
caring about X" includes how much you must type to use X. Promote the **thing** a domain has (a type
the consumer holds), name it `any-<domain>`, never `<lib>-extra`.

**Full behaviour = the shelf loop.** Resolve it **once per session, lazily** — the first time you
consider adopting or promoting substrate, never at startup:

1. Find the local clone: `$SHELF_HOME` → `../shelf` → `~/Workspaces/shelf`.
2. If absent (greenfield), clone it once: `git clone https://github.com/yoselabs/shelf ~/Workspaces/shelf`.
3. Read `<shelf>/docs/agent-loop.md` and follow it. Load once; cache for the session.

Never hit GitHub to start a session or to write code — only to clone (once) or during an actual
adopt/promote (a lazy `git pull` at that checkpoint). Never commit a local `path=`/editable shelf
source (the commit guard blocks it).
<!-- END SHELF RESOLVER BLOCK -->
