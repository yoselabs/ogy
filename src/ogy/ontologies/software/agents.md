## Knowledge base (ogy)

The requirements knowledge base is the folder `docs/kb/`: `constitution/`, `product/<area>/` and `software/<area>/`, nothing else
at its top. Each layer has the area `shared` (`product/shared/`): only the terms, actors and sets that two of its areas use live
there; everything else lives in the area that owns it. Change it only through ogy (CLI or MCP); never edit its YAML by hand.
- Run `{ogy} glossary` first, before reading code or writing a sentence: it prints the constitution (the principles every decision is
  judged against; cite one with `because`), then the glossary: the shared terms, then each area's (`<layer>/<area>/glossary.yml`);
  `{ogy} glossary <layer>/<area>` prints one area's terms with the shared ones it reads. Read both; use the words it prints. A term
  is `word`, `says` (one line of under 15 words) and `avoid`, nothing else; it needs no source. A word one area uses goes in that
  area's glossary, one that two areas use in the `shared` area of their layer. `{ogy} status` shows where things
  stand; `{ogy} find <words>` searches live and removed entries (search before you propose); `{ogy} show <address>` reads one.
- Before you create an entry of a kind, read `{ogy} kinds <kind>`: what it is, its guidance (when to use it rather than its
  neighbours: an actor, a lifecycle state or an attribute; `by` holds an entry to a rule, `because` cites a principle or a decision
  as the reason) and its fields. `{ogy} kinds --map` prints the whole ontology on one screen, with its rules.
- Add and change entries with ONE command, `{ogy} put`: one or many records, JSON or YAML, as arguments, `--file` or standard input
  (`{ogy} put '[{{"address": "<layer>/<area>/<kind>/<id>", "says": "..."}}]'`). An address that exists is changed (`"field": null` removes a
  field), a new one is added; the whole call is checked together (a decision may come with the entries its options set) and written whole
  or not at all. A choice goes in with `{ogy} answer`, a reply to a review round with `{ogy} reply "<grammar line>"`;
  `{ogy} remove --why` always says why (a decision address, or plain words); remove only when a requirement changes,
  never to reorganise. To change an entry's area use `{ogy} move <address> <area>` (`<layer>/<area>` to change the layer too): the id
  and the owner's agreements stay, every address follows in the same write, and nothing is recorded (Git keeps it); never remove
  and put again.
- A newer ogy may rename or drop a field of a kind, or move a kind out of a fixed folder (the kind file says `renamed: {{old: new}}`,
  `dropped: [...]` or `moved_from: <folder>/<file>`); `{ogy} check` then reports `needs-migration`. Run `{ogy} migrate`, never a hand
  edit: it renames and moves in one write and keeps the owner's agreements and the built lines current; a dropped field that held a
  value is printed, and that entry comes back to the owner as changed. What it moved lands in `product/shared`: `{ogy} move` each
  entry to the area that uses it.
- Reads see the worktree by default (`--rev .`); CI reads a commit with `{ogy} --rev HEAD check`. The flags `--repo --rev --ontology`
  go before or after the command: `{ogy} show <address> --rev HEAD`.
- Every write is checked; fix what it refuses. Run `{ogy} check` before you hand over: every finding is an error, there are no
  warnings. Exit codes: 0 ok, 1 findings, 2 usage, 3 refused, 4 not found.
- Every area folder holds its `area.yml` (`says`: what the area covers; `distinct`: what belongs in a neighbouring area); a put
  into a new area brings it in the same call. The first actor is the person:
  `{ogy} put '[{{"address": "product/<area>/area/<area>", "says": "..."}}, {{"address": "product/<area>/actor/human", "says": "...",
  "nature": "human"}}]'`
  (an actor needs no evidence).
- ogy stores no messages and no quotes. When the owner speaks, record the answer at once with a short paraphrase:
  `{ogy} answer <decision> <option> --said "<one plain line>" --where ai:<agent>/<session-id>` (`--note` for a hedge or condition), or
  `{ogy} reply "<grammar line>" --said "..." --where ...` for a review round (`from: human`: only a person agrees). Show each
  paraphrase to the owner in the read-back. A guess that rests on what the owner said carries a paraphrase (`guess.heard: {{said}}`),
  so the review reads "You said (paraphrased): .... Read as B." and one yes records the answer.
- Never answer for the owner. Only when the owner said "decide on my behalf" for a scope (an answer `from: human` of a decision),
  answer with `{ogy} answer ... --delegated <that decision>`; `{ogy} dropped` lists those answers, and you list them to the
  owner at session end.
