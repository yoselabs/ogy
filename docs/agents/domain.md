# Domain language and decisions

OGY keeps its glossary and its decisions in its own knowledge base, `docs/kb/`, written and checked by `ogy`.

| what | where | rule |
|---|---|---|
| Glossary | `just ogy glossary` (`docs/kb/**/glossary.yml`) | One canonical name per concept; each term has `says` and `avoid`. Use these names in code, tests, beads and commits |
| Decisions | `decision` entries in `docs/kb/` (`just ogy find <words>`, `just ogy show <address>`) | A proposal becomes a decision entry before it is acted on; only the owner answers |
| Writing | `just ogy put`, `just ogy answer`, `just ogy reply` | Never edit the YAML by hand; run `just ogy check` before handing over |

Ask the owner before recording a decision as accepted; draft it as a proposal.
