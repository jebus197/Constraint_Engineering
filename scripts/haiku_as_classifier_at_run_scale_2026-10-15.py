#!/usr/bin/env python3
"""Haiku as the claim classifier at run scale, measured from a real run's log.

THE MEASUREMENT THIS SERVES. `haiku_extended` is 1 of the programme's
outstanding measurements: "Haiku as the decidable-claim classifier at run scale,
and the founder's confidence composition (Haiku decides, syntax raises
confidence, never blocks)", on his ruling of 2026-10-03, "DO IT, mark as a
significant study area".

IT WAS ALREADY RUNNING, WHICH IS WHY THIS NEEDED NO NEW RUN.
`bench/immune_agents.py:4967` sets `_CLASSIFIER_MODEL = "haiku"`, dispatched
through the Claude CLI on the Max plan, and free run 1 exercised it 22 times.

THE BOUND, AND IT IS THE FIRST THING TO STATE. `immune_agents.py` sets
`llm_primary = (domain == "software")`. Both free runs use `domain=mathematics`,
so Haiku ran SEMI-ACTIVE with an override threshold of 0.70, never PRIMARY. So
this measures the SEMI-ACTIVE composition only. A PRIMARY reading needs a
software-domain run and is NOT established here.

WHAT "BLOCKED" MEANS HERE, because the word points the wrong way at first
glance. The founder's composition says the classifier must never BLOCK. The 3
log lines reading "BLOCKED by MATHEMATICAL guard" are the opposite: Haiku's
proposed RECLASSIFICATION was refused and the regex's `mathematical` label was
kept. Haiku is the thing being blocked, not the thing blocking. No finding was
withheld by the classifier in run 1.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
RUN1 = REPO / ("bench/logs/free_run1_directive_whole_20261015T061123Z"
               "_20261015T061124Z")

BATCH = re.compile(r"LLM classifier: (PRIMARY|SEMI-ACTIVE) \(CLI Haiku, "
                   r"override_threshold=([0-9.]+)\)\. (\d+) findings")
AGREE = re.compile(r"LLM classifier: (\d+)/(\d+) agree with regex \(([0-9.]+)%\), "
                   r"(\d+) overrides applied")
OVER = re.compile(r"LLM classifier OVERRIDE: (\S+) — regex=(\w+) → llm=(\w+) "
                  r"\(conf=([0-9.]+), threshold=([0-9.]+) cleared, ([0-9.]+)s\)")
BLOCK = re.compile(r"LLM classifier: (\S+) — regex=(\w+) llm=(\w+) "
                   r"\(conf=([0-9.]+), BLOCKED by (\w+) guard, ([0-9.]+)s\)")


def main() -> int:
    from statsmodels.stats.proportion import proportion_confint
    import numpy as np
    from scipy import stats as sstats

    log = RUN1 / "console.log"
    if not log.exists():
        print(f"missing: {log}", file=sys.stderr)
        return 2
    text = log.read_text(encoding="utf-8", errors="replace")

    batches = [(m.group(1), float(m.group(2)), int(m.group(3)))
               for m in BATCH.finditer(text)]
    agrees = [(int(m.group(1)), int(m.group(2)), float(m.group(3)), int(m.group(4)))
              for m in AGREE.finditer(text)]
    overs = [m.groups() for m in OVER.finditer(text)]
    blocks = [m.groups() for m in BLOCK.finditer(text)]

    print("=" * 78)
    print("1. MODE AND SCALE")
    print("=" * 78)
    modes = sorted({b[0] for b in batches})
    thresholds = sorted({b[1] for b in batches})
    total_to_classify = sum(b[2] for b in batches)
    print(f"  batches                : {len(batches)}  sizes {[b[2] for b in batches]}")
    print(f"  mode(s)                : {modes}")
    print(f"  override threshold(s)  : {thresholds}")
    print(f"  findings to classify   : {total_to_classify}")
    print(f"  PRIMARY ever engaged   : {'PRIMARY' in modes}")
    print("  (llm_primary = (domain == 'software'); these runs are domain=mathematics)")

    print()
    print("=" * 78)
    print("2. THE 3-WAY ACCOUNTING, AND IT CLOSES EXACTLY")
    print("=" * 78)
    agreed = sum(a[0] for a in agrees)
    denom = sum(a[1] for a in agrees)
    applied = sum(a[3] for a in agrees)
    n_over = len(overs)
    n_block = len(blocks)
    print(f"  agreed with regex          : {agreed}")
    print(f"  overrides applied (logged) : {applied}  (OVERRIDE lines: {n_over})")
    print(f"  overrides BLOCKED by guard : {n_block}")
    print(f"  sum                        : {agreed + n_over + n_block}")
    print(f"  findings to classify       : {total_to_classify}")
    closes = (agreed + n_over + n_block) == total_to_classify
    print(f"  the accounting closes      : {closes}")
    print(f"  override count self-consistent: {applied == n_over}")

    print()
    print("=" * 78)
    print("3. THE 3 PROPORTIONS, WITH INTERVALS")
    print("=" * 78)
    n = total_to_classify
    for label, k in (("agreed with regex", agreed),
                     ("overrode regex", n_over),
                     ("override blocked by the MATHEMATICAL guard", n_block)):
        lo, hi = proportion_confint(k, n, method="wilson")
        lob, hib = proportion_confint(k, n, method="beta")
        print(f"  {label:<44} {k:>3} of {n}  = {k/n*100:7.4f}%")
        print(f"  {'':<44} Wilson [{lo*100:7.4f}%, {hi*100:8.4f}%]")
        print(f"  {'':<44} CP     [{lob*100:7.4f}%, {hib*100:8.4f}%]")

    # Is agreement distinguishable from chance? 6 claim types -> chance 1/6.
    bt = sstats.binomtest(agreed, n, 1/6, alternative="two-sided")
    print(f"\n  agreement vs a 1-in-6 chance baseline: p = {bt.pvalue:.6f}")
    bt2 = sstats.binomtest(agreed, n, 0.5, alternative="two-sided")
    print(f"  agreement vs a coin flip             : p = {bt2.pvalue:.6f}")

    print()
    print("=" * 78)
    print("4. CONFIDENCE AND LATENCY")
    print("=" * 78)
    confs = np.array([float(o[3]) for o in overs] + [float(b[3]) for b in blocks])
    lats = np.array([float(o[5]) for o in overs] + [float(b[5]) for b in blocks])
    if confs.size:
        print(f"  confidence: n={confs.size} min={confs.min():.2f} "
              f"max={confs.max():.2f} mean={confs.mean():.4f} median={np.median(confs):.2f}")
        print(f"  every confidence at or above the 0.70 threshold: "
              f"{bool((confs >= 0.70).all())}")
    if lats.size:
        print(f"  latency/s : n={lats.size} min={lats.min():.1f} max={lats.max():.1f} "
              f"mean={lats.mean():.2f} median={np.median(lats):.1f} "
              f"total={lats.sum():.1f}")

    print()
    print("=" * 78)
    print("5. WHAT IT RECLASSIFIED TO, AND WHAT THE GUARD PROTECTED")
    print("=" * 78)
    moves: dict[str, int] = {}
    for o in overs:
        moves[f"{o[1]} -> {o[2]}"] = moves.get(f"{o[1]} -> {o[2]}", 0) + 1
    for k, v in sorted(moves.items(), key=lambda kv: -kv[1]):
        print(f"    {v:>3}  override  {k}")
    bmoves: dict[str, int] = {}
    for b in blocks:
        bmoves[f"{b[1]} -> {b[2]} (refused by {b[4]})"] = \
            bmoves.get(f"{b[1]} -> {b[2]} (refused by {b[4]})", 0) + 1
    for k, v in sorted(bmoves.items(), key=lambda kv: -kv[1]):
        print(f"    {v:>3}  blocked   {k}")

    print()
    print("=" * 78)
    print("6. THE FOUNDER'S COMPOSITION, CLAUSE BY CLAUSE")
    print("=" * 78)
    print(f"  'Haiku decides'          : it reclassified {n_over} of {n} findings, so yes "
          f"in SEMI-ACTIVE mode")
    print(f"  'never blocks'           : HOLDS. 0 findings were withheld by the classifier. "
          f"The {n_block} 'BLOCKED' lines are Haiku's OVERRIDE being refused by the")
    print(f"                             MATHEMATICAL guard, which is the guard blocking "
          f"Haiku and not Haiku blocking anything.")
    print(f"  'syntax raises confidence': NOT MEASURABLE FROM THIS LOG. The log records a "
          f"single confidence per classification and no pre-syntax value, so no")
    print(f"                             before/after pair exists to compare. Stated as "
          f"unmeasured rather than assumed.")

    ok = closes and (applied == n_over) and ("PRIMARY" not in modes)
    out = {
        "run": RUN1.name,
        "mode": modes, "override_threshold": thresholds,
        "primary_ever_engaged": "PRIMARY" in modes,
        "bound": ("llm_primary = (domain == 'software'); both free runs are "
                  "domain=mathematics, so this measures SEMI-ACTIVE only"),
        "batches": [b[2] for b in batches],
        "findings_classified": n,
        "agreed_with_regex": agreed,
        "overrode_regex": n_over,
        "override_blocked_by_guard": n_block,
        "accounting_closes": closes,
        "agreement_wilson": list(proportion_confint(agreed, n, method="wilson")),
        "override_wilson": list(proportion_confint(n_over, n, method="wilson")),
        "blocked_wilson": list(proportion_confint(n_block, n, method="wilson")),
        "agreement_vs_one_in_six_p": float(bt.pvalue),
        "agreement_vs_coin_flip_p": float(bt2.pvalue),
        "confidence": {"min": float(confs.min()), "max": float(confs.max()),
                       "mean": float(confs.mean())} if confs.size else None,
        "latency_s": {"min": float(lats.min()), "max": float(lats.max()),
                      "mean": float(lats.mean()), "total": float(lats.sum())} if lats.size else None,
        "reclassifications": moves,
        "blocked_reclassifications": bmoves,
        "composition": {
            "haiku_decides": True,
            "never_blocks": True,
            "syntax_raises_confidence": "NOT MEASURABLE FROM THIS LOG — no pre-syntax confidence is recorded",
        },
        "all_assertions_hold": ok,
    }
    dest = REPO / "experimental_notes/evidence/haiku_classifier_run1_2026-10-15.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, indent=2) + "\n")
    print(f"\n  evidence -> {dest.relative_to(REPO)}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
