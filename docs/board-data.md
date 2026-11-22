# Board inspection adapter (S3, stage 2)

`js/api.js` reads inspection **v2** with the current cookie exchange and ETag.
`model/adapt.js` keeps the original document, every field, every part and every
relation witness. `model/descriptor.js` reads the ontology delivered with that
document. No copied vocabulary or snapshot is shipped. This follows
`one-owner-per-fact`: the inspection document owns the facts.

The area inventory was the acceptance surface for stage 2. Every addressable
entry has exactly one `data-address`; unaddressable list parts have local locator
identities, never invented addresses. The constitution is included. Counts include
addressable parts (steps, choices, options), as inspection does.

## Every lab node field and its inspection source

The inventory covers `lab31.tpl.html` and its build inputs (`lab29` descriptor,
models, renderers, levels, walk and interactions; `lab31` layout and edges).
The build inputs are read as reference, not copied wholesale into production.

| Lab field | Inspection v2 source / adapter meaning |
|---|---|
| `id` | `entries[].address`; list parts use `parts[].locator` (owner, field, index), scoped to this document |
| `key` | `entry.key`, falling back to the last address segment for single parts; list parts use their slot |
| `kind` | `record.kind`, never a renamed kind label |
| `layer`, `area` | `record.layer`, `record.area`; the adapter qualifies area with layer; constitution has no layer |
| `parent`, `top` | `record.parent`; a tagged root-entry becomes null, and only that makes `top` true |
| `says` | `record.sentence`, using `record.sentence_field`; no truncation and no guess that the field is called says |
| `title`, `word` | `record.title`, `fields.word`; the single identity path then uses option/choice label or a humanized key |
| `label`, `question`, `context` | Authored `fields.label`, `fields.question`, `fields.context`, unchanged in `detail.fields` |
| `result`, `order` | Authored `fields.result`, `fields.order`; no exporter default or sort order is substituted |
| `nature`, `form` | Authored `fields.nature`, `fields.form` |
| `atype`, `invoked` | Presentation aliases of `fields.type`, `fields.invoked_as`; authored names remain in `detail.fields` |
| `of` | The resolved target of that node's `relations[].field == of`; the original short spelling remains in fields |
| `optional`, `members` | Authored fields; enum members are text values, **not entry addresses**; render them as literals |
| `when`, `reads` | `fields.when.text`; resolved `when` relation targets; all original expression text and reads retained |
| `fx[].do`, `fx[].on`, `fx[].onid` | Effect list parts' `fields.do`, original `fields.on`, and resolved `on` target whose source is that exact part locator |
| `detail.fields`, `availability` | All `record.fields`, including unfamiliar fields and explicit null; `record.absent_fields` separately means unset |
| `detail.sentenceField`, `sentence`, `sentenceAvailability` | Corresponding record fields and their reserved tagged absence envelopes |
| `detail.parts` | Ontology kind's `parts` and each child's `key` identify the owner slot; all matching child records are indexed |
| `detail.effects` | Every effect list part's complete fields, locator, source path and slot index; no persistent id is invented |
| `detail.expressions` | Authored `when` / `derived` text, resolved reads, and the exact relation witnesses |
| `detail.source` | `record.source` and optional part locator; source line is explicitly unavailable in inspection |
| `detail.provenance` / legacy snapshot pointers | Replaced by the retained record source and relation witness; no graph-export filename or fake source line |
| `ghost` | Absent: the lab's scripted draft overlay is not inspection data |
| `x`, `y`, `w`, `h`, measured positions | Future view state, never authored node facts; no layout in stage 2 |

Edges retain one occurrence per `relations[]`: `s` is the real address or local
source locator, `t` the resolved target (null with an explicit unresolved marker
when missing), `f` the exact field, and `source` the witness's owner and path.
An effect link's source remains the effect, not its parent case. Stage 3 must use
the parent's `fx` for E1 badges and retain that occurrence when drawing relations.

Descriptors expose all common and kind fields, roles, declared part slots and link
fields, with the raw ontology still available. Typed YAML envelopes remain intact
in fields. Missing, explicit null and unavailable transport data are distinct.
The lab's exporter evidence panel is omitted: its export-specific witnesses have
no job in a live inspection client. Actual source witnesses remain in the model.

## Standing

`GET /api/standing` returns computed totals (waiting questions, owed work,
unagreed entries, changed entries, dropped items and findings), area status
counts, every decision's computed status and newest answer, classified entries,
work items and dropped items. Answer options and delegations are full addresses;
dates are ISO strings and absent answer fields are null. Dropped rows preserve
each category occurrence, including multiple rows for one decision.

Because `one-owner-per-fact`, the status overview supplies entry classifications,
the existing show status function supplies decision status, and the status,
work and dropped operations supply the remaining facts. CLI formatting is unchanged.
Waiting counts questions, not the separate count of terms awaiting agreement.

Standing is computed once per input identity: the same stat signature as the
inspection cache, which covers the KB files (built records included), `ogy.yml` and
the ontology. A request with an unchanged signature is served from memory; concurrent
requests share one computation (single flight). The repository lock is held only
to read the KB files into a snapshot; the four operations (status, work, dropped,
option reach) then run on that one snapshot with the lock released, so a trial
write never waits for them. Evidence files outside the KB (code, documents a proof
names) are not in the signature: a change to one shows after the next KB change.
`computed: true` distinguishes these facts from authored fields. `version` is
the inspection snapshot version captured in that same locked read; conditional
requests use the usual private, per-route ETag (a 304 needs no recomputation). It
identifies KB/configuration/ontology input changes, not evidence-file changes.
The browser checks for this stage leave the current board unchanged.

## Inspection cache and state

Every read still takes the hardening run's repository lock, even a cache hit.
A stat signature (path, size, mtime, ctime, inode) checks the KB, configuration and
ontology files. A change recomputes the content identity and encodes inspection
once. Restoring identical input bytes restores the same version. Responses keep
private cache headers, per-route validators and 304 handling from the server.

`state.js` owns document, version, selection, pins, spotlight and camera. Applying
a document compares nodes by address/locator, preserves surviving view state and
clears identities that disappeared. Selection changes no positions. There is no
canvas, URL interaction, streaming connection or server write in this stage.

## Verification and stage 3 prerequisites

The scratchpad `s3-data-check.mjs` checks both KBs in real Chromium through the
server's one-use exchange URL. It checks inventories, descriptors, effects,
immutability, conditional requests, errors and view-state preservation, and saves
`s3-data-tool.png`, `s3-data-ogy.png`, and `s3-data-results.json`.
Its server helper injects an ephemeral credential in memory; it never opens a
credential file. Node is used only by this scratchpad CDP harness, not the build,
package or runtime. Like a2kay, the shipped assets are plain ES modules, without
a bundler; a2kay's npm Tailwind recipe is replaced by the standalone binary here.

No authored-field gap blocks stage 3. Drawing is described in [board-draw.md](board-draw.md).
Source text/line, built records and removed
ledgers are explicitly unavailable; do not synthesize them. Rendering must handle
enum members as text and list parts as local identities. Before drawing, finish
the stage-1 toolchain gate: install and lock Biome 2.6.8 (Linux arm64 release asset
`biome-linux-arm64` from `biomejs/biome`, tag `@biomejs/biome@2.6.8`).

Stage 3 draws without edges and carries the fixed lab31 behaviour forward:
positions depend on data and detail class, selection moves only the camera, and
real mouse clicks on buttons/mentions survive mouseup. Keep the existing lab
tokens: orange workflow frames, sticky goal/capability notes, blue entities, E1
effect badges and one mention identity path. The inherited CSS is unchanged apart
from the temporary area inventory's shell rules. No draw/interaction acceptance
is claimed by this stage.

## Shell (stage 2 of the rebuild)

`index.html` is a shell: header, standing strip, breadcrumb, main column, right rail. Hash routes are the whole view state
(`#/<path>?level=&sel=&rail=`; `js/shell/router.js`): a route no entry in `main.js` claims is the not-found page, and the
canvas stays at `#/` and `#/board` until the Map replaces it. The header names the repository and revision (`repository`
and `revision` of `/api/standing`: the repository folder, and `worktree` or the commit) and when the page last saw the
standing change; the strip shows `totals` and links a fact only once its list route exists. `js/ui/mention.js` is the one
function that draws an entry's name (`data-renderer="mention"`); `js/ui/authored.js` marks KB text with `data-authored`;
`js/ui/words.js` is the viewer's own fixed list. `assets/board/tokens.css` holds the five type sizes (11/13/15/18/24), the
8px grid, the lab28 neutrals and the status colours for light and dark; `js/model/icons.js` gives every kind, effect
operation and mark one glyph (`tests/test_web_shell.py` keeps them apart).
## The waiting list (stage 3 of the rebuild)

`js/views/waiting.js` draws the decisions whose `status` in `/api/standing` is `waiting`, grouped by layer and area; titles and
first question lines come from the inspection model (a row whose model entry has not arrived yet is named by its key).
It is mounted twice from one function: the page at `#/waiting` and, compact, in the rail's Waiting tab. A row is the
decision's mention (a link to `#/<decision address>`, the route the decision page claims), the kind word, the question's
first line (authored) and, when the decision has an answer date, "last answered ...". The standing has no asked-at date for a
question, so a waiting row shows no age otherwise. While standing loads (several seconds on a large KB) the list says so; a
failed load offers "Try again"; no waiting decision shows "Nothing waits for you." Keys: `g` then `w` opens the page, `j` and
`k` move between rows of the list that holds focus (else the page's), Enter opens the focused row. Back remounts the page
and focuses the row last opened. Nothing polls: the list repaints when standing or the inspection model changes.

### Option reach

Each decision row also holds `options`: option address -> `{sets, reach, count, truncated}`.
`sets` are the existing entries the option sets (an option that sets nothing, or only entries
not written yet, has `sets: []`). `reach` is what `ogy impact` returns for them: the union of what
each set entry reaches and what reaches it, the set entries left out, sorted, at most 50;
`count` is the full number and `truncated` says the list was cut. It is computed on the current
knowledge base and cached with the inspection input identity. It never says what the new value
would link to. Options of one decision must name the same addresses, so their lists are equal.

### Decision page and answering

`#/<layer>/<area>/decision/<id>` is `js/views/decision.js` (parts under `js/views/decision/`). It reads the authored fields
(question, context, options, proposal, answers) from the inspection document and status, the chosen option and option reach
from `/api/standing`; until standing arrives its status line and reach say "Loading…". Options are one radio group; the answer
form below owns them through the `form` attribute. A click is an answer: choosing an option fills the paraphrase with the
option's label, the owner edits it, and the form shows the exact record before it is written. `Record` posts
`{decision, option, said, note?, version}` to `/api/answer` (version: the inspection snapshot the page shows); a refusal (stale
version, blank `said`) is shown as the server wrote it and nothing is written. After a write the page reads inspection and
standing again (the header count drops without a reload) and the read-back links the next waiting decision. Options of one
decision currently reach the same entries, so "Potentially affects" is shown once, as "same for every option", and per option
only when the lists differ. The page's own fixed words live in `js/views/decision/words.js`; every KB text is `data-authored`.
`docs/design/board/qa/decision-check.mjs` is its real-mouse check (answering only on a temporary copy of the tool library).
