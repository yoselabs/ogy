# E11: the capture skill end to end (2026-11-17)

Question: does the draft capture skill (read, capture, derive, hazard pass, elicitation, read-back) surface more
hazard holes and settle more with 7 questions than the spec alone? Primary metrics: hazard holes surfaced, must-ask
settled. Adopt if both rise beyond scorer noise at ≤ +25% size.

Arms, 8 Sonnet runs each: A = [spec-v4](../../docs/spec-v4.md) alone; B = spec-v4 + [the skill](../../skills/ogy-capture/SKILL.md).
The prompts are identical apart from the skill line ([prompt-A.md](prompt-A.md), [prompt-B.md](prompt-B.md)): 7
questions, read-back, three sections. The scenario is new: [scenario.md](scenario.md), a food bank in the owner's words, 23
sentences. The hidden [key.md](key.md) holds:
- 11 product holes;
- 12 hazard holes (offline tablet, phone dying mid-route, failed texts, unknown donation outcome, races, the nightly
  job);
- 6 derivable facts;
- 7 must-ask holes.

Scoring followed [the protocol](../README.md): [blind.py](../blind.py) with seed 1117, 4 Opus scorers
([scores-blind.md](scores-blind.md)), and 1 agreement scorer on 4 runs ([scores-agreement.md](scores-agreement.md)).
The agreement scorer stays within ±1 on every count except one "wasted" count, which differs by 2.

| Arm | Hazard holes surfaced (of 12) | Product holes (of 11) | Settled by 7 | Must-ask (of 7) | Invisible invention | Wasted | Mis-cited per citation | Derived (of 6) | Size |
|---|---|---|---|---|---|---|---|---|---|
| A spec-v4 | 6.25 (5-7) | 8.9 | 8.5 (6-11) | 3.5 (3-4) | 0.5 | 3.0 | 1.75 / 65 (2.7%) | 6.0 | 26.5 KB |
| B + skill | 8.9 (7-11) | 9.4 | 10.6 (10-12) | 4.75 (3-6) | 0 | 3.9 | 2.0 / 62 (3.2%) | 6.0 | 27.1 KB |

Reading:
- **The hazard pass works as a skill step.** B surfaced 2.6 more hazard holes. The ranges barely touch: A tops out at 7,
  where B's bottom is.
- **Settled with 7 questions rose again** (8.5 to 10.6; B's worst run beats A's median). Must-ask rose from 3.5 to 4.75.
- **No size cost** (+2%). Spec-v4 alone already carries the origin marks and decisions, so the skill adds only flow.
- **Mis-cites are about 3% per citation in both arms.** E10's rise came from citation volume, not from a worse error
  rate. The rate holds at 3% with and without the skill.
- Wasted asks rose slightly (3.0 to 3.9; scorers disagree on partial cases).
- Derived sits at its ceiling (6 of 6).

Verdict: **adopt the skill flow, hazard pass included.** Open threads: a harder derivation scenario; a review pass to
remove the remaining 3% mis-cites; the hazard pass on code (P17 style) as an A/B.
