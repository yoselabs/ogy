PROVENANCE (business kinds; technical kinds are sourced by their uplinks and need none)
- quote {by: persona/, on, text, source: <sentence numbers>, ?answers: decision/, ?chose: key, ?confirms: [id],
  ?replaces: quote/}: the owner's exact words, copied verbatim, never edited or merged.
- Every business entry carries exactly one of:
  said: [quote/]      a quote states it; you interpreted nothing. A value's number and unit are in the quote.
  because: [id|quote/] it follows from these and no other answer would fit them. ?by: persona/ if a human derived it.
  ?open               the sources do not settle it.
- Test before writing `because`: could the owner answer otherwise without contradicting a quote? If yes, it is a
  choice: use ?open. Numbers, limits, timeouts, permissions, who is told, and failure behaviour are choices unless said.
- Parts and required slots inherit the entry's mark. A part that differs carries its own.
- Every optional slot you fill (?max, ?timeout, ?conflict, ?optional, ?wait, ?key) needs its own mark in the entry's
  origins: {<part path>: {said: [..]} | {because: [..]} | {open: {..}}}. An optional slot left out needs nothing.
- Never write `origin`; the tool computes it: said | derived-human | derived-ai | assumed | open.
- Technical entry with no uplink (serves, performs, binds): add affects: [business ids] | none, and rationale.
ELICITATION
- decision {question, asks: persona/, options:{key:{label, sets:{<slot address>: value}}}, ?default: key, rationale}:
  one owner question that settles several slots. Every option sets the same slots. Plain words, no kind names,
  2 to 4 options, recommended option first.
- A slot waiting on it: ?open: {decision: decision/<id>} and no value; the default option's `sets` is in force.
  No default = the slot is empty until answered. Single slot shorthand: ?open: {question, ?assumed: true}.
- Before asking, derive: anything entailed, anything technical, anything a stated rule already covers.
- Group: slots share a decision when one owner sentence would settle all of them (same subject, same policy:
  on failure / who may / how long / how many / what is said).
- Rank decisions: (entries that reference the slots) x (business 3, technical 1) x (2 if an option tells an
  external, moves money, ends an entity for good, or removes data; else 1).
- Budget: list at most 7 decisions under `ask:`, highest rank first; decisions with no safe default go first.
  Every other decision keeps its default and goes under `assumed:` for one batch read-back.
- Do not ask when: the answer is entailed; no persona would notice the difference; at most 2 entries depend on it
  and risk is 1; a broader decision in `ask` would settle it.
- Always ask: money, messages to externals, permissions, irreversible effects.
CHECKS (added): business entry with no said/because/?open; filled optional slot with no origins mark; value, set
member, quality target or rule body marked because without by: persona/; said value whose number is not in the
quote; because that reaches no quote and has no rationale; option sets differ within a decision.
