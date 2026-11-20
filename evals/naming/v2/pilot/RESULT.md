# Pilot, 2026-11-20: arm A vs C0, small model (Haiku tier via the Agent tool), 2 runs each, frozen v2 text

Not a result under the pre-registered rule (2 runs per arm, below the 5-run minimum). Information only.

| arm | runs (blind id) | link items of 51 (scorer 1 / scorer 2) | misplacements of 27 |
|---|---|---|---|
| A (eval-before, old names) | A-1 R554, A-2 R698 | 41/41, 46/46; mean 43.5 | 4, 2 |
| C0 (stage-1 names, no like/unlike) | C0-1 R631, C0-2 R495 | 45/45, 41/41; mean 43.0 | 3, 4 |

- Scorers agree on every primary total (disagreement 0); false-friend counts differ by one on R631.
- Both arms are under the ceiling gate (46 of 51), so the small model has room.
- Difference A vs C0: 0.5 items, below the 4-item threshold. No sign that the names alone help at this size.
- Misplaced in every run: [13] (the program that calls us) and [24]. The endpoint [10] misplaced in one run per arm.
- Model id was not recorded by the Agent tool; run.sh records it for the real runs.
