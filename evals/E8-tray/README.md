# E8: is a tray-shaped ontology more intuitive for an AI? (2026-11-17)

Question (owner): does the ontology's shape make an AI notice what is missing? Arms, 5 Sonnet runs each, one pass:
A = spec-v3 prose; B = kind cards with companions ([cards.md](cards.md)); C = cards + fill-in skeleton
([skeleton.yml](skeleton.yml)). Input: [scenario.md](scenario.md) (owner's words, 13 planted holes, [key.md](key.md),
hidden from runs). Scored blind by one Opus agent ([scores-blind.md](scores-blind.md), [blind-map.txt](blind-map.txt)).

| Arm | Holes noticed (of 65) | Fabricated | Misfiled | Owner questions (mean) | Output size (mean) |
|---|---|---|---|---|---|
| A prose | 63 | 0 | 0 | 22 | 12.7 KB |
| B cards | 65 | 4 | 1 | 22 | 18.2 KB |
| C cards + skeleton | 64 | 1 | 0 | 25 | 19.5 KB |

Reading:
- **Ceiling.** Every arm found nearly every hole, so the test cannot tell the arms apart. Likely causes: a short
  scenario (12 sentences) with obvious holes, and the prompt asked outright for "every gap". The intuitiveness question
  is still open.
- **Fabrication came from a slot.** All four B fabrications are the same: `attendees` given `max: room capacity` as
  fact. The card shows `?max: value/`, and agents filled it. C's skeleton lists `?open` beside each slot and had 1.
  A slot without an explicit "unknown" option invites invented answers.
- **Cost.** Cards and skeleton make the output 45-55% longer.

Next test, to escape the ceiling: a longer, realistic scenario (about 1500 words, several workflows) where holes appear
only through companions (a field nobody reads, an input no rule limits, an external with no failure answer), and a
prompt that asks only for the capture, so noticed holes are counted unprompted.
