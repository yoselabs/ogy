# E9: provenance and elicitation (2026-11-17)

Question (owner): do provenance marks and decision-shaped questions stop invisible invention and cut the owner's
decisions without losing coverage? Arms, 8 Sonnet runs each, one pass: A = spec-v3; B = spec-v3 + Fable's addition
([spec-addition.md](spec-addition.md), from [the consult](../../docs/consults/provenance-elicitation-fable.md)). Input:
[scenario.md](scenario.md), a tool library in the owner's words, 46 numbered sentences; hidden [key.md](key.md):
24 holes in 5 clusters, 8 derivable facts. Prompt: "capture, then list the questions you would put to the owner, most
important first" (no "find every gap"). Scored blind by 4 Opus agents ([rubric.md](rubric.md),
[scores-blind.md](scores-blind.md), [blind-map.txt](blind-map.txt)); a 5th re-scored 4 runs
([scores-agreement.md](scores-agreement.md)): the scorers differ by ±1 on most counts.

| Arm | Invisible invention | Visible (assumed) values | Holes covered (of 24) | Questions | Must-ask in top 7 (of 6) | Wasted questions | Cited a sentence that does not say it | Derived (of 8) | Size |
|---|---|---|---|---|---|---|---|---|---|
| A spec-v3 | 0.38 | 12.6 | 18.8 | 17.5 | 4.0 | 0.13 | 1.5 | 7.9 | 31.8 KB |
| B + provenance, elicitation | 0.13 | 7.9 | 19.3 | 18.6 | 4.75 | 0.38 | 1.0 | 7.6 | 50.5 KB |

If the owner answered only 7 ([scores-top7.md](scores-top7.md); A = first 7 questions, B = the KB's `ask:` decisions):

| Arm | Holes settled | Must-ask settled (of 6) | B's assumed batch |
|---|---|---|---|
| A | 10.4 | 3.9 | none |
| B | 9.75 | 2.75 | 2.9 holes |

Reading:
- **Invention is at the floor in both arms.** spec-v3's `?open {question, assumed}` already stops invisible invention
  for prose capture (as in E8 arm A). Provenance did not make it measurably lower; the difference is within scorer noise.
- **The decision kind did not beat a plain ranked list.** B's 7 decisions settled slightly fewer holes than A's first 7
  questions. B left money amounts outside decisions (a decision picks between options; an amount is a number), so the
  most important question, "what does everything cost", fell out of the budget; B also spent slots on non-holes.
- **The question-count metric is contaminated:** the prompt asked B for a full question list too, so both arms
  listed about 18. The budget of 7 held only inside the KB's `ask:`.
- **Mis-cited "said" happens in both arms**, and A runs cited sentences without being told to. The typical error is a
  generalisation labelled as said ("in repair cannot be reserved" became "only available tools can be reserved"). A
  lint that checks numbers against the quote cannot catch it; it is exactly the said-vs-derived line the owner wants.
- **Cost:** B is 59% larger (Fable's own adoption limit was +25%).

Verdict against the consult's adoption rule: not adopted as written. What still stands: provenance as a
read-only, tool-computed view (who said what) and the one-question-many-slots idea; what failed: the decision kind's
options shape for amounts, and the cost of writing marks on every entry.
