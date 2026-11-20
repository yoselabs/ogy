"""Unblind and tally the scorers' marks by the README's rules (naming eval v2).

Usage: python3 -I tally.py SCORING_DIR      (e.g. evals/naming/v2/scoring/small)
Reads SCORING_DIR/map.txt and SCORING_DIR/scores/*.md (per-fact lines `n: K F | items | wrong links: n | note`).
A run's marks are the mean of its two scorers. Prints per arm: link items of 51, common homes of 45, names subset
of 19, misplacements of 27, false friends, wrong links; the things given apart; scorer disagreement both ways;
per item hits; A against C0 with the gates, the counting rule and the 90% Welch interval.
"""

import argparse
import math
import re
import sys
from itertools import pairwise
from pathlib import Path
from statistics import mean, stdev
from typing import Any


def say(*parts: object) -> None:
    sys.stdout.write(" ".join(str(part) for part in parts) + "\n")


LINE = re.compile(r"^(\d+): ([01-]) ([01-]) \|(.*?)\| wrong links: (\d+)")  # fact [1] has no K or F
ITEM = re.compile(r"(\d+[a-z])=([01])")
NOT_45 = {"10a", "10b", "18a", "18b", "20b", "13b"}
NAME_ITEMS = ["4b", "6b", "7a", "9b", "15b", "19a", "22c", "26a"]
NAME_FACTS = [2, 5, 8, 10, 12, 13, 14, 16, 20, 25, 27]
ABSENCE = ["9b", "11b", "21c", "25b"]
ARMS = ["A", "C0", "C", "B"]
# Welch t, two-sided 90% (0.95 quantile), by degrees of freedom; linear between rows.
T95 = [
    (1, 6.314),
    (2, 2.920),
    (3, 2.353),
    (4, 2.132),
    (5, 2.015),
    (6, 1.943),
    (7, 1.895),
    (8, 1.860),
    (9, 1.833),
    (10, 1.812),
    (12, 1.782),
    (15, 1.753),
    (20, 1.725),
    (30, 1.697),
]


def parse(path: Path) -> dict[str, dict[int, dict[str, Any]]]:
    runs: dict[str, dict[int, dict[str, Any]]] = {}
    current: dict[int, dict[str, Any]] | None = None
    for line in path.read_text().splitlines():
        if line.startswith("## R"):
            current = runs.setdefault(line[3:].strip(), {})
        elif current is not None and (m := LINE.match(line)):
            fact = int(m.group(1))
            k, f = (int(g.replace("-", "1")) for g in (m.group(2), m.group(3)))
            current[fact] = {"K": k, "F": f, "wrong": int(m.group(5)), "items": {k: int(v) for k, v in ITEM.findall(m.group(4))}}
    return runs


def marks(facts: dict[int, dict[str, Any]]) -> dict[str, Any]:
    items = {k: v for f in facts.values() for k, v in f["items"].items()}
    scored = {k: v for k, v in items.items() if k not in ("1a", "15b") and 2 <= int(k[:-1]) <= 28}
    return {
        "items": items,
        "link51": sum(scored.values()),
        "n51": len(scored),
        "common45": sum(v for k, v in scored.items() if k not in NOT_45),
        "names19": sum(items.get(k, 0) for k in NAME_ITEMS) + sum(facts[f]["K"] for f in NAME_FACTS if f in facts),
        "namesF": sum(facts[f]["F"] for f in NAME_FACTS if f in facts),
        "mis": sum(1 - f["K"] for n, f in facts.items() if 2 <= n <= 28),
        "ff": sum(1 - f["F"] for f in facts.values()),
        "wrong": sum(f["wrong"] for f in facts.values()),
        "K": {n: f["K"] for n, f in facts.items()},
    }


def t95(df: float) -> float:
    for (d0, t0), (d1, t1) in pairwise(T95):
        if df <= d1:
            return t0 + (t1 - t0) * (max(df, d0) - d0) / (d1 - d0)
    return 1.645


def welch(a: list[float], b: list[float]) -> tuple[float, float, float, float]:
    va, vb = stdev(a) ** 2 / len(a), stdev(b) ** 2 / len(b)
    diff = mean(b) - mean(a)
    se = math.sqrt(va + vb)
    if se == 0:
        return diff, diff, diff, float("inf")
    df = (va + vb) ** 2 / (va**2 / (len(a) - 1) + vb**2 / (len(b) - 1))
    return diff, diff - t95(df) * se, diff + t95(df) * se, df


def load(scoring: Path) -> tuple[dict[str, str], dict[str, dict[str, Any]], list[float], dict[str, int]]:
    arm_of = {}
    for line in (scoring / "map.txt").read_text().splitlines():
        label, blind = line.split()
        arm_of[blind] = label
    by_run = {}
    for path in sorted((scoring / "scores").glob("*.md")):
        for run, facts in parse(path).items():
            by_run.setdefault(run, []).append(marks(facts))
    keys = ["link51", "common45", "names19", "namesF", "mis", "ff", "wrong"]
    per_run: dict[str, dict[str, Any]] = {}
    gaps: list[float] = []
    diff_items: dict[str, int] = {}
    for run, pair in sorted(by_run.items()):
        if len(pair) != 2:
            msg = f"{run}: {len(pair)} scorers"
            raise SystemExit(msg)
        if not all(p["n51"] == 51 for p in pair):
            msg = f"{run}: not 51 items"
            raise SystemExit(msg)
        per_run[run] = {k: mean(p[k] for p in pair) for k in keys}
        per_run[run]["items"] = {k: mean(p["items"].get(k, 0) for p in pair) for k in pair[0]["items"]}
        per_run[run]["K"] = {n: mean(p["K"].get(n, 0) for p in pair) for n in range(1, 29)}
        gaps.append(abs(pair[0]["link51"] - pair[1]["link51"]))
        differ = [k for k in pair[0]["items"] if k not in ("1a", "15b") and pair[0]["items"].get(k) != pair[1]["items"].get(k)]
        per_run[run]["ndiff"] = len(differ)
        for k in differ:
            diff_items[k] = diff_items.get(k, 0) + 1
    return arm_of, per_run, gaps, diff_items


def main(scoring: Path) -> None:
    arm_of, per_run, gaps, diff_items = load(scoring)
    keys = ["link51", "common45", "names19", "namesF", "mis", "ff", "wrong"]
    arm_runs = {a: sorted(r for r in per_run if arm_of[r].rsplit("-", 1)[0] == a) for a in ARMS}
    say(
        f"# {scoring.name}\n\n| arm | n | link items (of 51) | common homes (of 45) | names subset (of 19) | "
        "names F (of 11) | misplacements (of 27) | false friends | wrong links |\n|---|---|---|---|---|---|---|---|---|"
    )
    for a in ARMS:
        rs = arm_runs[a]
        cells = [f"{mean(per_run[r][k] for r in rs):.2f}" for k in keys]
        say(f"| {a} | {len(rs)} | " + " | ".join(cells) + " |")
    say("\nPer run, link items of 51:")
    for a in ARMS:
        say(f"  {a}: " + " ".join(f"{per_run[r]['link51']:g}" for r in sorted(arm_runs[a], key=lambda r: arm_of[r])))
    dis = mean(gaps)
    say(
        f"\nScorer disagreement: mean |difference| {dis:.2f} of 51; mean items differing per run "
        f"{mean(per_run[r]['ndiff'] for r in per_run):.2f}"
    )
    third = len(per_run) / 3
    named = sorted(k for k, n in diff_items.items() if n > third)
    say(f"Items differing in more than a third of {len(per_run)} runs: {named or 'none'}")
    say("\nApart, mean per arm:")
    for a in ARMS:
        rs = arm_runs[a]

        def it(k: str, rs: list[str] = rs) -> float:
            return mean(per_run[r]["items"].get(k, 0) for r in rs)

        say(
            f"  {a}: K12 {mean(per_run[r]['K'][12] for r in rs):.2f} 12a {it('12a'):.2f} 12b {it('12b'):.2f} "
            f"15b {it('15b'):.2f} absence {sum(it(k) for k in ABSENCE):.2f}/4 1a {it('1a'):.2f}"
        )
    allitems = sorted({k for r in per_run for k in per_run[r]["items"]}, key=lambda s: (int(s[:-1]), s[-1]))
    say("\nPer item, hits (mean of two scorers) summed over runs:\n| item | " + " | ".join(ARMS) + " |\n|---|---|---|---|---|")
    for k in allitems:
        say(f"| {k} | " + " | ".join(f"{sum(per_run[r]['items'].get(k, 0) for r in arm_runs[a]):g}" for a in ARMS) + " |")
    say("\nK per fact, summed over runs:\n| fact | " + " | ".join(ARMS) + " |\n|---|---|---|---|---|")
    for n in range(1, 29):
        say(f"| {n} | " + " | ".join(f"{sum(per_run[r]['K'][n] for r in arm_runs[a]):g}" for a in ARMS) + " |")
    a = [per_run[r]["link51"] for r in arm_runs["A"]]
    c0 = [per_run[r]["link51"] for r in arm_runs["C0"]]
    ma = mean(a)
    say(f"\nGates: A mean {ma:.2f} (ceiling at 46, floor under 26)", "CEILING" if ma >= 46 else "FLOOR" if ma < 26 else "pass")
    diff, lo, hi, df = welch(a, c0)
    say(f"C0 minus A: {diff:+.2f}, 90% Welch interval [{lo:+.2f}, {hi:+.2f}], df {df:.1f}")
    better, worse = (c0, a) if diff > 0 else (a, c0)
    bn, wn = ("C0", "A") if diff > 0 else ("A", "C0")
    overlap = sum(x <= max(worse) for x in better)
    mis = {x: mean(per_run[r]["mis"] for r in arm_runs[x]) for x in ("A", "C0")}
    ff = {x: mean(per_run[r]["ff"] for r in arm_runs[x]) for x in ("A", "C0")}
    say(
        f"Counting rule: |diff| {abs(diff):.2f} >= 4 and > 2x{dis:.2f}: {abs(diff) >= 4 and abs(diff) > 2 * dis}; "
        f"runs of {bn} at or below best of {wn}: {overlap} (<= 1: {overlap <= 1}); "
        f"{bn} worse by >1 on misplacements or false friends: "
        f"{mis[bn] - mis[wn] > 1 or ff[bn] - ff[wn] > 1}"
    )
    na = [per_run[r]["names19"] for r in arm_runs["A"]]
    nc = [per_run[r]["names19"] for r in arm_runs["C0"]]
    say(f"Names subset C0 minus A: {mean(nc) - mean(na):+.2f}")
    if named:

        def drop(r: str) -> float:
            return float(per_run[r]["link51"]) - sum(per_run[r]["items"].get(k, 0) for k in named)

        d2, l2, h2, _ = welch([drop(r) for r in arm_runs["A"]], [drop(r) for r in arm_runs["C0"]])
        say(f"Without {named}: C0 minus A {d2:+.2f}, 90% [{l2:+.2f}, {h2:+.2f}]")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Unblind and tally the scorers' marks of one scoring folder.")
    parser.add_argument("scoring", type=Path, help="the scoring folder (map.txt and scores/)")
    main(parser.parse_args().scoring)
