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
repository root (`ontology`, optional `rev`; `$OGY_CONFIG` names another file); a flag overrides it. `land` names the land
branch, which `ogy init` records and no flag sets: with none, `ogy hook pre-push` and `gate` refuse and `init --check` says so. The knowledge base is always
the folder `docs/kb`: there is no flag or setting that moves it.

Commands. The flags `--repo`, `--rev` and `--ontology` go before or after the command (`ogy --rev HEAD check` or `ogy check --rev HEAD`). `--rev` is a commit,
or `.` for the worktree, which is the default: a read sees what was just written.
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
| `work [area]` | what the built record says is still to do, grouped for a person by cause: the decision that set the entry (or a parent), then what its workflow realizes (`flow.group`); display only, the agents' table stays flat |
| `review [area] [--all]` | what you are asked (at most 7 cards); it **saves a round** and prints its id |
| `dropped` | what no person has seen (end a session with it) |
| `glossary [layer/area]`, `kinds [kind] [--readers \| --map]` | the constitution, then the terms of the product: the shared ones of each layer, then each area's (for one area: its terms and the shared ones it reads, a software area product's too), then for the whole glossary each kind's like and unlike line; the kinds of the ontology, or one: its about, its guidance (how to decide when to use it rather than its neighbours), what it is like and unlike, and its fields. `--map` prints the whole ontology as an indented tree, one line per kind grouped by layer (`!` required, `->` one link, `->>` many links, `[]` a list part, indentation = part of), then its declared rules as sentences, then each kind's like and unlike line. `--readers` lists for each field what reads it (the fingerprint, requires, a build input, flow, settling, links and impact, the review rank, a named check or printer) and ends with the fields nothing reads and those only the fingerprint reads |
| `remove <address> --why <address or words> [--to]` | delete an entry and record it in its `removed.yml` when the base commit (merge base with what has landed: the land branch's upstream, else `origin/<land>`, else the local land branch; else HEAD) had it; one born since is not recorded, Git keeps it, except an entry `ogy init` starts with, which init would add again (always the worktree; one write lock). `--why` is always required: the address of the decision that said so, or plain words (an address stays required for an entry a person agreed to); `dropped` lists the plain-words ones |
| `move <address> <area \| layer/area>` | move an entry and what it owns to another area, keeping its kind, id and agreements; in the same write the new address replaces the old one everywhere (links, decisions, answers, removed items' `why`), and an agreement that was current stays current. It records nothing: Git keeps the move, and `check --base` tells it from a loss: an entry gone with exactly one arrival of the same kind and id has moved, whatever its text (a changed text reads "changed since you agreed"); the fingerprint only breaks ties |
| `migrate` | rewrite the entries to the field renames, drops and moves out of a fixed folder their kinds declare (see "Kind changes"); one checked write that records nothing. It also takes out, and prints, a removed item no removal writes now: its entry was never in the base (Git keeps the item) |
| `history <address \| layer/area>` | what changed, who said so, what is in force, when it was built; computed from Git |
| `serve [--port <number>] [--out <path>]` | board API and MCP in one loopback process (default port 8765); `--out` exports the legacy list page instead. Always reads the worktree. No MCP tool |
| `mcp` | serve the knowledge-base commands as MCP tools over stdio |
| `init` | set the repository up (see "Init") |
| `hook pre-commit \| pre-push \| gate` | what a Git hook or the gate runs (no MCP tool). The one place that decides "is this a land": a push whose remote ref is the land branch (`land` in `ogy.yml`), or the gate with it checked out, gets `check --landing`; anything else, the plain check. `pre-commit` checks the staged tree and is never a land (a merge runs no pre-commit hook; a fresh repository's starters are agreed before its first land, not its first commit). The hooks `ogy init` writes (the pre-commit entry in a prek config, else `.githooks/pre-commit` and `.githooks/pre-push`) and ogy's own gate (`just kb`) call it |
| `put [records ...] [--file <path>]` | the one way to add and change entries: one or many records (JSON or YAML, a mapping or an array, as arguments, a file, or `--file -` for standard input; over MCP an array of such texts). A record is `address` (or `kind`, `layer`, `area`, `id`) and the entry's fields; an address that exists is changed (`field: null` removes a field), a new one is added. The batch is validated together (a decision and the entries its options set may arrive in one call) and written under the lock whole, or not at all |
| `answer <decision> <option> --said <paraphrase> --where <uri> [--at <iso>] [--from human\|ai] [--note <text>] [--delegated <decision>]` | choose the option: appends the answer `{chose, said, from, at, where, note?, delegated?}` and applies the option's `sets`; it agrees to no sentence (those entries read "from your words" until a `reply` `yes`). `said` is one short line, the agent's paraphrase of what the person said; `--note` is their hedge or condition, paraphrased. An option that says no (`null`) removes the entry even while others link to it: each such link is then work in `ogy work` ("links to an entry said no to") until re-pointed or removed, not a finding. There is no `agree`: only a review round's `yes` agrees to a sentence |
| `reply <grammar line> --said <paraphrase> --where <uri> [--at <iso>] [--round <id>] [--note <text>]` | apply the owner's reply to a review round; nothing is written when nothing applies. The text is the grammar line: the owner's, or the agent's reading of their natural words. Every answer and agreement it writes keeps `said`, `at`, `where` and `from: human` |

### Init

`ogy init` is idempotent and merges, never clobbers. It writes `ogy.yml` (with `land`: `--land <branch>`, else the remote's default branch; with no remote it refuses to guess); creates `docs/kb` with `constitution/principles.yml` and the area `product/shared` (its `area.yml`);
adds a marked block (managed-region) to `AGENTS.md`, and to `CLAUDE.md` when it exists, that tells agents to change the
knowledge base only through ogy and to run `ogy glossary` first (the constitution, then the glossary); adds the `ogy` server (`ogy mcp`) to `.mcp.json`; adds
`Edit` and `Write` deny rules for `docs/kb/**/*.yml` to `.claude/settings.json`; and the Git hooks, following the repository: with a prek config
(`.pre-commit-config.yaml`) it merges one pre-commit entry that runs `ogy hook pre-commit` and leaves `core.hooksPath` alone (the
pre-push check stays in the repository's own gate entry); without one it writes `.githooks` and points `core.hooksPath` at it, and
refuses when another tool already owns `core.hooksPath`. Every file it changes is read and checked first: a file that is not UTF-8, a
file where it needs a folder, or a config of the wrong shape is refused by name before anything is written.

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
  you" while what it was agreed as is `hash`, "changed since you agreed" after: its fingerprint, with the fingerprints of the
  rows read with a step (a row is never a card of its own) and, for a term that names an entry, that entry's sentence. A
  person's yes is evidence of its own.
- Two hashes. The fingerprint is the meaning: the kind, the fields that are not notes and the unkeyed parts. Agreements,
  review cards and removed items hold it. The build hash adds the proofs and the build inputs; only the built record and
  work left compare it. A new proof or a changed dependency is work, never a question for the owner.
- Which entries need a proof (a test that shows them built): the rows (choice, case, timeout), a rule, an interface, a setting
  and a workaround; an entity only while it has transitions (`needs_proof: {if_part: transition}`); never a step, a handler
  or a quantity (a number is proved by the rule that `constrains` it). Each is work until its built line matches its build
  hash. A built line on a live entry that needs no proof is removal work, and `ogy migrate` deletes it. A dependency's new
  pin still reaches the rules it is held to (`input_from`); the handler that uses it is no longer built, so its `uses` input
  reads nothing.
- Build inputs (as in Bazel and Make). A link field says what of its targets enters the build hash with `input:` `none`
  (the default when unset), `address` (the target's address: a relink is work; only on a note or common field, as a kind's
  other fields have the address in the meaning already) or `content` (the target's build hash without proofs: a change in the target is
  work). It may pick less: `input: {fields: [pin]}` (only those fields of each target) or `input: {parts: [choice]}` (the
  addresses of those parts of each target). A link field of a kind that needs proof states its input, `none` included,
  its own and the common ones (`ontology.yml` states `none` for `because`). A kind gives the input of a
  common field or of a part kind in its own `input:` map (`input: {because: address}`, `input: {attribute: content}`;
  `address` is allowed there on any common field, as no common field is in the meaning), and reads what links to it with `input_from:` (`input_from: {satisfies: {fields:
  [pin]}}`: the pin of each entry held to it, only where set). `ogy kinds` prints each input. A changed content input reads
  `changed` in `ogy work`, as a changed meaning does: the build hash is one hash, and a built line keeps only it (`own`), what
  the proof covers and the sources it was captured from. Input staleness is never re-stamped automatically: an agent re-proves
  the entry and stamps its line. A built line that still holds the old `deps` key is `needs-migration`; `ogy migrate` drops it.
- Once a decision has an answer, its proposal is inert: nothing compares it with the answer and nobody rewrites it. A decision an
  agent answered under delegation is a card of its own (`delegated`) that marks the option in force, for the owner to confirm or veto.
- A proposal that rests on what the owner said carries a paraphrase: `proposal.heard`, one line, never a quote. The review card reads
  "You said (paraphrased): .... Read as B." and one `yes` records the answer, chosen option B.
- `ogy review` keeps the cards it showed as a round, by id (the last 10, in the Git directory).
  `ogy reply --round <id>` resolves against that round (required over MCP; on the CLI the newest round is the default): `yes`, `yes 1 3`, `2: <new sentence>` (replaces and agrees), `no 4` (the sentence becomes a
  question; why, paraphrased, goes in `--said`), `Q1 b` (option B or its key), `later`, `yes all` (or `decide`: every question gets its recommended option, the proposal, a decision an agent answered under delegation
  gets a person's answer for the option in force, and
  every card is agreed to; a card that changed stays in the queue and is reported; a structural decision stays too, see Layout). A bare `yes` to a round shown with `--all` is
  refused: name the cards, or spell `yes all`. A card whose entry changed since it was shown is refused and stays in
  the queue. Natural words ("Fine, go ahead, I suppose.") are read by the agent as a grammar line (`yes`), with the hedge
  in `--note`; the words themselves are not stored. A bare `yes` (or `yes Q2`) also confirms
  questions whose proposal rests on what the owner said (`heard`), except a structural decision. `ogy review` prints, before the reply line,
  what a bare `yes` will change.
- Who confirms (E1, for now): a person, written `from: human`, no name; the actor `human` (`nature: human`) says who they are:
  `ogy put '{"address": "product/<area>/actor/human", "says": "...", "nature": "human"}'`. An actor says who uses the
  product, not a claim, so it needs no evidence. Delegation: only when the owner says "decide on my behalf" for a scope,
  that is the owner's answer to a decision; the agent then answers others with
  `ogy answer ... --delegated <that decision>`. Such an answer is in force at once, and `ogy dropped` lists it
  so the agent names it at session end for the owner's veto. An `ai` answer without a `delegated` decision whose answer in
  force is a person's is the check `bad-delegation`. A scope is only that decision's question; ogy models no more than
  this.

### Layout

The ontology declares where entries live (`ontologies/software/ontology.yml`) and the loader enforces it; nothing skips a level.
The engine knows no name of the ontology: `ontology.yml` declares the layers, the shared area and its sentence, the fields every
entry may carry and the roles the engine reads them in (`roles`), the harm tags in review order and those asked alone, the
evidence schemes of `src` and the proof form, and the reserved field names; each kind names its `sentence:`, `term` declares the
`glossary:` role and `principle` the `printed_first:` role, and `workflow.yml` and `decision.yml` write out every `flow:` and
`settling:` name. `starts.yml` and `agents.md` beside them are what `ogy init` writes. `--ontology` (or `ontology:` in `ogy.yml`)
names a shipped ontology, or a folder on disk when it holds a `/` (relative to the repository); `tests/fixtures/toy-ontology` is one
in which every name differs.
`docs/kb/constitution/principles.yml` holds the principles (a principle is cited with `because`); every other file is `docs/kb/<layer>/<area>/<kind>/<id>.yml` (a list kind:
`<layer>/<area>/<file>`; a single kind: one entry in `<layer>/<area>/<file>` whose id is the area), the layer being `product` or `software`.
Every area holds its `area.yml` (kind `area`: `says`, what the area covers, ending `Not here: <what>: <area>`; `unlike`, links to the neighbouring areas, so a renamed area follows): the kind
declares `every_area`, so an area folder without it is `missing-entry`, and a write into a new area brings it in the same call. It needs
no proof and is never asked (`asked: false`); which product areas a software area builds is computed from links. The fixed folder
`constitution/` is no area. An area or kind at the top, or an unknown layer, is `bad-path`. A folder that holds only its `removed.yml`
is an area no more.
- The glossary is the kind `term`: each area's words in `<layer>/<area>/glossary.yml`. A term is compressed: `word`, `says` (one
  line of under 15 words, else `term-too-long`) or `names` (the entry that defines the word: an entity, an actor, a state...; the
  glossary and its card print that entry's sentence, length-checked the same; exactly one of the two) and `avoid`; it keeps no sources (`evidence: none`): where a word is used is read
  from the sentences. Each layer has the reserved area `shared`, a
  normal area with its `area.yml`: a term, an actor or an enum that two areas use lives there (`product/shared/glossary.yml`,
  `product/shared/actors.yml`), so every address keeps its area. Only the kinds marked `shared: true` (term, actor, enum and area)
  may live there; any other is `bad-path`, and `ogy move` into `shared` refuses it. Which shared entry fewer than two areas use is
  not checked yet.
The folder is the layer's only home: an entry has no `layer` field, each kind lists the layers it may appear in (`layers:`), and an
entry in another one is `bad-layer`. An address is `<layer>/<area>/<kind>/<id>`. An actor and an interface live in product only:
an actor is always outside the product (CI, Git, an MCP client that calls us included), an interface is where it reaches the product.
- The layers are in order and `ontology.yml` says which way a link may cross them (`link_direction: later-to-earlier`): a link
  stays in its layer or names an earlier one, so software names product and product never names software (`layer-direction`,
  any link field, `delegated` of an answer included, and a decision's `sets` keys: a decision lives in the layer it sets or a
  later one; the constitution is outside the layers). An actor is named by its role (a payment provider), whatever its nature; the
  product's own clock is a workflow `schedule`, its own reaction an `event`. In software the handler `uses` the dependency that
  `realizes` such an actor, and a software workflow behind a product step names it with `details` instead of repeating its actor step.
- `doc:` evidence pins a Git revision (`doc:<commit>:<path>#<anchor>`): the file may be deleted later, history stays. An unpinned one is `bad-src`.
- `ogy status --coverage` lists, per layer, the kinds with no entry. An area named like the repository is the finding `product-area`
  (name a topic, not the product). Every finding is an error: ogy prints no warnings.
- A decision asked again (a proposal newer than its newest answer) is asked on its own card: `yes`, `yes all` and `decide`
  leave it, and `review` says it needs its own letter.

### Kind changes

A kind file may change under a knowledge base that a newer ogy reads. Adding a field changes no fingerprint and no build hash
(an unset field is outside the one, an input that reads nothing outside the other), so nothing goes stale. A rename or a drop is declared in the kind file and kept there until the knowledge bases
it serves are migrated: `renamed: {old: new}` (the new name is a field of the kind) and `dropped: [old]`; a common field renamed
in `ontology.yml` says `renamed: {old: new}` there. A renamed kind says what it was, `was: {kind, file, key}` (its old name, and
its old list file or part key when those changed). A kind that absorbed several kinds lists them, `was: [{kind: view,
defaults: {form: web}}, {kind: command, defaults: {form: cli}}]` (shape `file` only; `interface` says so); `renamed` inside an item names the
fields an entry of that old kind held under another name (also in the `sets` that give it values), and `defaults` fills a field
the new kind requires that the old kind lacked. A kind renamed earlier and not yet migrated everywhere lists every old name. A value given a new form says `revalued: {field: {old value: {field: new
value or null}}}`, and a part folded into a field `folded: {field: inner field}`. An entry that still
holds an old name is the finding `needs-migration`. `ogy migrate` writes the migration in one checked write:
- every old name becomes the new one, in the entry, in the items of its list parts (answers) and in the fields an option's
  or a proposal's `sets` gives an entry of that kind; a revalued or folded value takes its new form;
- a pure rename changes no meaning: an agreement or a built line (`own`) that was current stays current, its
  hash re-set to the fingerprint (a built line's to the build hash) after the rename, as `ogy move` does;
- a dropped field that held a value changes the meaning: `migrate` prints the value, and the agreement and the built line of
  the entry (and the built lines whose build hash reads it) are left, so the owner sees it as changed since agreed and it is work;
- a renamed kind (`ogy.retype`): its entries move to the new folder, list file or part key, and every address that names
  them is rewritten (links, `sets` keys, `reads`, the built record; removed items keep the names they had); `check` reports a
  file that still holds an old kind name as `needs-migration`, and the agreements and built lines stay current;
- a merge of kinds is the same rename for each old kind, with its own field renames. Two entries that would become one (a view
  and a command of one area and id) are `needs-migration` naming both, and `migrate` refuses, moving nothing, until one is
  `ogy move`d to a new id with the ogy version from before the merge (an entry moving onto a file already there is named as
  such). A removed ledger keeps the old names; `check` reads its items under the new ones, so an id stays taken;
- a kind that moved out of a fixed folder declares the file it was in, `moved_from: <folder>/<file>`. Its entries there are `needs-migration`; `migrate` moves them to the area `shared` of the kind's first
  layer (with that area's `area.yml` when it has none), renames every address under the old folder (links, `sets` keys, the
  removed items of the folder's `removed.yml`, which moves too) and keeps the agreements current. Then `ogy move` each entry to the
  area that uses it;
- an agreement written when a step's agreement held only its own fingerprint is re-set to the hash that covers its rows
  only when the step and every row read with it are as they were in the commit that wrote the agreement (found in Git
  history); otherwise the step comes back to the owner as changed since agreed;
- a removed item whose entry the branch changed before removing it has as its snapshot the entry's last version after the
  base (read from Git history, never from the item's `last_seen`); an entry the base never had is no removal;
- `check --base` reads the base migrated, so a migration commit is no edit of an append-only part. Removed items keep the
  names they had; nothing is recorded (Git keeps the old names).
The old fingerprints are computed under the kinds as they were (`kindchange.before`). A changed field type is no declared
change: it needs a one-off migration on the write path.

### MCP

`ogy mcp` starts a stdio MCP server with one tool per command above (the tools are generated from the CLI, so a new
command appears without an edit). Every tool describes itself (its description is the command's own; `init`, `mcp`, `serve` and `hook` are no tools). Agents get tables (`check`, `work`, `find`, `dropped`, `impact`, `diff`) as lean-wire TSV with their header even when empty, and records (`show`, `status`) as YAML; no Python reprs. Add it to
`.mcp.json` at the repository root; the server starts there, so `--repo` defaults to it:

```json
{"mcpServers": {"ogy": {"command": "uvx", "args": ["--from", "git+https://github.com/yoselabs/ogy", "ogy", "mcp"]}}}
```

`ogy serve` binds `127.0.0.1` and prints a browser URL. Opening it exchanges the URL token for an HttpOnly,
SameSite=Strict cookie and redirects to `/` without the token. The board front end is a placeholder until S3.
HTTP clients send `X-Ogy-Token`; the stable token is stored privately (0600) in the repository's Git directory under
`ogy/server.token`. Shelf's `any-local-service` owns browser access, loopback serving and shutdown.
`/healthz` needs no token and reports readiness, stage and version. The authenticated read endpoints are `/api/inspection` (the inspection
library's JSON), `/api/entry/<address>` (one inspection entry), and `/api/version` (content and ontology identities).
Every request reloads current files. `/mcp/` offers the same tools as `ogy mcp`, with `--repo` defaulting to the served
repository. All routes validate Host and Origin. Ctrl-C stops the server and its MCP lifespan.

## The software ontology

The packaged ontology (`src/ogy/ontologies/software`) describes a software product; each kind is a file in `kinds/`.
- Where: `area` (what one area covers).
- Unused (work left `unused`, never a finding, computed from links): a rule nothing `satisfies` and that `constrains`
  nothing; a quantity, an enum, a setting or a dependency nothing links to (`<-*`); a transition no effect fires; a goal no
  capability realizes. Each kind
  declares it as a work requirement with `status: unused`.
- Why: `goal`, `actor`, `capability`, `rule`, `term` (the glossary), `principle` (the constitution). A capability `realizes` a
  goal; one that realizes none is work left (`unrealized` in `ogy work`) until the goal is written, not a finding. A
  workflow `realizes` a capability; a capability no workflow realizes is work left (`no-workflow`).
- What it does: `workflow` with its `step`s, `choice`s, `case`s, `timeout`s, `effect`s and `end`s; `interface`
  (ArchiMate's application interface: where an actor reaches the product; its `form` is web, cli, http, mcp, library, file
  or message) that serves steps; `handler` that performs them. An interface `shows` and `accepts` entities and attributes
  (content inputs: what it displays changes, it is stale); one that accepts serves a step, one that only shows may serve
  none. `includes` names the cards inside it (never a cycle, `link-cycle`); `allows` names who may use one that serves no
  step (authorization harm), else who may use it comes from its steps' actors. A cli interface says `invoked_as`. An actor
  step that no interface serves is work (`unserved` in `ogy work`), not a finding. A refusal is a `case` that leads to a failure end. A `choice` with `when` is offered only while it
  holds (the same screen offers fewer choices; a `case` when the path differs); an actor step keeps one choice without it.
- What it keeps: `entity` with `attribute`, `state` and `transition`; `quantity` (a number with a unit), `setting` (its
  `default` a quantity), `enum`. An attribute has a plain `type` or names what it holds in `of`; `many` makes a list. An
  attribute with `derived` is computed from what its expression reads: no `write` effect names it, and it has no `max`
  and is never `optional`. Any other attribute is written: a `write` effect names it or its entity, a `create` effect its
  entity (owner, 2026-11-20), or an interface `accepts` it or its entity; else `unmet-requirement`
  (never-written).
- Conditions (`when` of a case or a choice; `derived`) may name actors.
- What it depends on: `dependency` and its `workaround`s. A dependency `realizes` the program actor that rows tell (a payment
  provider); a row that tells a program actor has a handler that performs it and `uses` a dependency realizing that actor
  (`actor.nature` is read here). A row that tells a program actor or a dependency owes a no-answer path (status
  `no-answer-path`, work): a timeout, or a case ending in failure, on its step or the step it leads to, and a rule it
  `satisfies` that says whether a repeat is safe. No answer is never a third `end.result`: the workflow ends in failure,
  and the rule makes the rerun safe.
- What is open and what the owner chose: `decision` with `option`, `proposal` (with its `heard`) and `answer`.
- Held to: behaviour (a step, a row, an interface, a handler, a dependency, a workflow) names the rules it is held to with
  `satisfies`; a rule names the data it holds to (a quantity, an enum, a setting, an entity, an attribute, a state) with
  `constrains`, a content input (a changed number makes the rule work). `satisfies` is a content input of the rows and interfaces
  only, so adding a rule stales no other holder; the pin of a dependency held to a rule is part of the rule's build hash (`input_from`), so a new pin makes its
  proofs work again.

A kind declares its graph rules in its file, never in Python: `exactly_one_of`, `one_part` and `requires`. A requirement
has at most one condition (`if_set: <field>`, `if_unset: <field>`, `if_part: <kind>`, `if_equals: {field, value}` with one
value or a list, `if_reaches: <path>`: the path reaches anything), then needs a field (`needs_field`) or reaches along a link
`path` (none: the entry itself), or along any of `or_paths`, an entry of `kinds` that sets none of `without`; with `same: true`
the path must come back to the entry itself (for an item of a list part, the entry holding it). An unmet one is
`unmet-requirement`, or, with `work: true`, work left under the `status` it names (step: `unserved`) rather than a finding.
A path hop is a link field (`field?key=a|b`: only targets whose `key` is a or b), `<-field` backward (`<-field?key=a|b`: only
links whose holder, the entry or the list part item, has `key` a or b; `<-*` by any link field; the key `@kind` is the
entry's kind, so `on?@kind=dependency` keeps only dependencies), `^` the parent or `/kind`
the parts; `kinds: [any]` takes an entry of any kind. So an effect's `do`
names what its `on` may be. A kind lists in `acyclic:` the link fields that never lead back to the entry (`link-cycle`). A
`links` field holds at least one link: leave it out for none. `ogy kinds --map` prints them all.

An entry has its own evidence (`src`: `code:<path>#<symbol>` or `doc:<commit>:<path>#<anchor>`; or a `because` to a
principle or a decision (the reason, never a source); or a decision that settles it; or a person's yes, `agreed`), or `ogy check` says `no-evidence`. `proof` is `<path>.py::<function>`.
Every kind file carries `guidance:`, a short text on how to decide when to use the kind (for an actor, the variation test:
different permitted actions make an actor, a recorded move the product reacts to a state, a fact that changes the outcome an
attribute in a case; a threshold name is never an actor), and `like` and `unlike`, one line each: the mainstream notion
the kind matches and the ones of the same name it does not mean (`ogy kinds`, `--map` and `ogy glossary` print them).
`satisfies` holds behaviour to a rule, `constrains` holds data to it; `because` cites a principle or a
decision as the reason, nothing else. A kind or a field may declare `harm:` (what a wrong sentence costs), which ranks the review queue.

## Where the code lives

ogy holds business logic: kinds, checks, status, decisions, the removed ledger and the built record. Technical details
live in [shelf](https://github.com/yoselabs/shelf) packages: Git access (`git-porcelain`), YAML (`any-yaml`, `yaml-merge`),
Markdown anchors (`any-markdown`), hashes (`content-digest`), Python symbols (`py-symbols`), MCP tools (`argparse-mcp` on
FastMCP 3), atomic writes (`atomic-io`), the write lock (`process-lock`), agent tables (`lean-wire`), settings and managed
blocks (`settings-base`, `managed-region`). `test-reach` is a dev dependency with pytest. the banned-api table in `pyproject.toml` bans the raw libraries
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
