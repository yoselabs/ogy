Restored board prototypes lab27, lab28 (the Codex one, not the later `lab28-redraw`) and lab29; each file is one self-contained HTML page (CSS, JS, data inlined).
`lab2N-standalone.html` uses the tool-library fixture (the "START HERE" variant); `lab2N-ogy-standalone.html` uses ogy's own KB.
Method: replayed, in time order, the Claude Bash cells (board.tpl.html through lab25, python patch scripts) and every Codex exec/apply_patch cell of the lab25 to lab29-stage-9 sessions (`~/.codex/sessions/2026/11/21-22`), then ran the recorded builds (`__DATA__` substitution; `lab29-build.py` for lab29).
Fidelity checks: lab28.tpl.html has 546 lines, as the Codex `wc -l` recorded; the replay fails on exactly the same cells the originals failed on (467, 471, 547, 792, 817); lab29-graph-tool.json is 191626 bytes, as the original build printed.
The tool-library variants are therefore close to exact (the fixture and the replayed templates match the recorded checks).
The ogy-KB variants are NOT the original data: `graph2.json` / lab29's ogy graph were exported from the KB of 21 Nov, and were regenerated from the KB of today (lab29 ogy graph 2398136 bytes, the original build printed 1814257), so those boards show more entries.
Not recovered: the exact original `graph2.json`; `view-contract` / `vocabulary` JSON were replayed from the Codex cells, not from the originals; lab29 test harness pages, screenshots and the Codex reports; later hand edits by the owner (none known).
Shell commands that launched Chromium, `uv` or `ogy` were stubbed during the replay; none of them wrote template files.
Verified: each file opened in headless Chromium 156 renders the canvas (workflow frames, steps, cards) with no console errors. lab29's default view is crowded, as lab30 later tried to fix.
Replay engine: a throwaway script set kept outside the repo (scratchpad `rp/`).
