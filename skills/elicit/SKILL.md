---
name: elicit
description: Find what a spec, plan, ticket or set of requirements leaves undecided, settle what can be derived, and ask
  the owner the fewest questions that settle the most, with a recommended answer for each. Use when requirements have
  gaps, before building, or when asked to "grill", "interview" or "find what is missing".
---

# Elicit (draft, 2026-11-17)

Status: **proposed**. Generic: works on any written requirements. Its output is plain Markdown; `ogy-capture` turns it
into ontology entries. Evidence: E9-E11 in ogy's `evals/` (decisions with fill-ins, ranking and a budget settled
more with the same 7 questions). The borrowed parts are marked with their source and are not yet evaluated.

## 1. Read and find gaps
List every slot the sources leave open:
- numbers, limits and durations;
- who may do what;
- who is told;
- what happens on failure, on a repeat, or when two people act at once;
- what ends for good.

Ask the premortem question of the whole thing: "It is three months later and this failed. What happened?" (from
iorlas-brainstorm).

## 2. Derive, look up, never ask facts
- What the sources entail, write down as derived, with its sources.
- Facts from the environment (code, docs, data) are your job: send a subagent and do not block on it. Only the
  questions that wait on that fact wait (from grilling).

Work goes in stages: settle what the layer you work in must say (the business first, then the build), and leave what a
later layer owes it (which service, which screen) to that layer as work, not as a question asked now. With ogy, stop at
your layer and hand over with `ogy work <your layer>` (untested).

## 3. Group into decisions
- One decision per sentence the owner could say to settle several gaps (same subject or same policy).
- A choice: 2-4 options, each setting the same gaps.
- A fill-in: the owner gives the values (one price list settles every amount).
- Map the decision tree: a decision whose answer can remove or change others is their parent (from grilling).
- "No", "not now" and "remove it" are options of the decision, never a silent omission. If you recommend against
  something a source proposes, the card still shows it, with "no" as the recommended option (untested).
- Before you write a decision, look for an earlier one that asks the same question and for an earlier removal of the
  same thing. Add an option to the old decision; do not open a second one (untested).
- Structure (layout, layers, kinds, paths): before recommending to remove or change it, search the owner's earlier answers
  (`ogy find`, `ogy history`); a conflict goes into the proposal's `heard` (a paraphrase), so the card shows "You said (paraphrased): ....". "Unused in captures" is never by
  itself a reason to remove structure the owner asked for. A structural decision (`structure: true`) is asked on its own
  card, never in an accept-all (`yes`, `yes all`, `decide`).

## 4. Rank and pick the round
- The frontier is every decision whose parents are settled (from grilling).
- Rank the frontier: money moved, an outside party told, an irreversible end, a permission; then by gaps settled.
- Ask at most 7 per round. Everything else gets a proposed answer for the read-back batch.
- Open with one open question when the goal itself is unclear (from superpowers brainstorming).

## 5. Show each question as a card
One form, shared with `ogy review` (letters, the recommendation first, "yes" accepts it):
```
Q<n>. <short title>
   Why it comes up: <what happened or what is missing, so the card reads alone>
   <the question, with the gap and its sources in one line>
   A. <option>   (recommended: <one-line reason>)
      then <what becomes true under A>
   B. <option>
      then <what becomes true under B>
   Settles: <the gaps this answers>
   Reply: yes | Q<n> b | <n>: <words> | no <n> | later
```
- Each card reads alone, out of the chat: why it comes up, the question, and every option with what it makes true.
  Never show only the recommended or the in-force option; for a delegated answer, show what the owner chose before and
  what the agent changed (owner, 2026-11-19).
- A structural question (kinds, links, workflows) is explained with a common web application first: sign-in, password
  reset, an admin page of users, an event that starts a flow. Draw it (before and after) and map it to the owner's
  product in a table (owner, 2026-11-19: a familiar product makes the model easy to absorb).
- Word each card so "yes" accepts the recommendation (from grilling). Every card is a stored `decision` with its
  proposal (see `ogy-capture` section 4); do not ask what is not stored.
- If the owner's answers are short, switch to two options (from iorlas-brainstorm).
- If the owner is in the chat, ask the round. If the owner is away, send the round and the read-back as one message.

## 6. Read back
- Play back what you understood in plain sentences, in three groups: what they said, what you concluded (and from
  what), and what you assumed (one batch to confirm or correct) (playback from superpowers).
- Commands the owner may use: `skip`, `decide` (accept every recommendation; in a round it is `ogy reply "decide"`), `map decisions` (show the tree)
  (from iorlas-brainstorm).

## 7. Next round and end
- Live capture, before your next action: record the answer with a short paraphrase at once and show it to the person in
  the read-back. ogy stores no messages and no quotes: `said` is one plain line in your words, fitted to the decision,
  never theirs verbatim. `ogy reply "<grammar line>" --said "<paraphrase>" --where <session>` for a round (natural words:
  give your reading as the grammar line), `ogy answer <decision> <option> --said "<paraphrase>" --where <session>` for a
  choice outside a round (one sentence deciding several questions: one `answer` per decision). What leans without
  choosing goes to `proposal.heard` as a paraphrase, never into prose.
  Words that fit two options, or a bare `no`, are asked again at once, while the owner is there (untested).
- Answers reshape the tree. Recompute the frontier, then ask the next round.
- Never answer for the owner and never change an answer they gave. A reversal is a new answer with its own paraphrase,
  who, when and where; the old one stays.
- Done when the frontier is empty and nothing is silently assumed or silently dropped.
- For large work, a fresh subagent reads the result as a builder. It sorts its own questions into three groups (from
  superpowers):
  - already answered;
  - minor, settled by you and marked as yours;
  - the owner's, asked in one more round.

## Output
- Decisions asked: each with its card, and the answer once given, with its paraphrase, who answered, when and where.
- Derived facts, each with its sources.
- Assumed: each with its proposed answer.
- Still open.
- Dropped: every proposal you decided against without asking, each with its reason.
