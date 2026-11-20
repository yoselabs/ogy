# runs/: what counts and what does not

- `small/`, `default/`: the runs that count, made by `drive.sh` after the freeze. Empty until then.
- `smoke-*/` (and `../scoring/smoke-*/`): script tests of 2026-11-20, made before the freeze. **Not counted.** Never
  pooled, compared or blinded together with `small/` or `default/`; `blind.py` is only ever called on one tag.
- `models.txt`, `excluded.txt`: one line per run of every tag, smoke tags included; a result reads only the lines
  of `small/` and `default/`.
- Pilot answers are not here: `../pilot/old-runs-small/`. **Not counted** either (`../pilot/RESULT.md`).
