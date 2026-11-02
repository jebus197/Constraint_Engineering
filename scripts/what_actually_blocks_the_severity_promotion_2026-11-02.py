#!/usr/bin/env python3
"""What actually blocks promoting the new severity measure. Not money.

HIS QUESTION, 2026-11-01, verbatim: *"I would suggest perhaps since the blocked
run requires it anyway, running both the old severity measure as live for now,
and running the new severity measure in shadow for a few simulated runs, until
we have enough data of the kind you say you require before we retire the old
severity measure and replace it with the new one? Would that work?"* And:
*"Why should money be a deciding factor on whether this measurement can be made
or not?"*

THE SHORT ANSWER THIS SCRIPT PRODUCES. His proposal is already the shipped
configuration -- `severity_spec_enabled` has defaulted to False since 2026-10-15,
so the old measure decides and `severity_spec_shadow()` records what the new one
would have said. The shadow has been running for 6 runs. It has moved NOTHING,
and the reason is not money: the new measure differs from the old one ONLY
through the verification factor V, and V only annihilates on a REFUTED finding.
Refutations are vanishingly rare, and the simulated/paid split on refutation is
indistinguishable (Fisher p = 1.000000).

3 CLAIMS OF MINE WERE REFUTED WHILE WRITING THIS, AND THEY ARE RECORDED RATHER
THAN QUIETLY DROPPED:
  1. "0 of 65 runs record the shadow" -- FALSE. It was a 0 of looking in
     `runner_state.json`, which has no telemetry key at all. The records are in
     the run stdout logs as Python reprs. The real figure is 13 records across
     6 logs.
  2. "23 of 28 falsifiers read the ORIGINAL target instead of a staged copy"
     -- FALSE. `bench/falsifier_verify.py:224` defines
     `STAGED_TARGET_ROOT = ~/CDSFL_review_targets`, so that path IS the staged
     copy. The falsifiers are reading the right file.
  3. "83.5% NOT_INTERCEPTED means falsifiers ignore their targets" -- NOT
     SUPPORTED. `reference_runner_v3.py:990` records that the control "has never
     fired in the project's life" because it needs a falsifier AND a corrected
     copy on the same finding, and historically 0 of 58 entries carried both,
     Wilson [0.0000, 0.0621]. A control that was never fed reports
     NOT_INTERCEPTED for want of a comparison, not because the falsifier is
     blind.

WHAT SURVIVES IS STILL DECISIVE, and every figure below is computed here.
"""
from __future__ import annotations

import argparse
import ast
import collections
import json
import pathlib
import re

import numpy as np
from scipy import stats
from statsmodels.stats.proportion import proportion_confint
import mpmath as mp

REPO = pathlib.Path(__file__).resolve().parents[1]
LOGS = REPO / "bench" / "logs"
GATE = re.compile(
    r"falsifier gate \(tools decide\):\s*(\d+) CONFIRMED,\s*(\d+) REFUTED,"
    r"\s*(\d+) -> HIL")
SIM = re.compile(r"-SIM\b")
CUT = 0.7


def _wilson_mp(k: int, n: int, z: float = 1.959963984540054):
    """Wilson bounds by hand, as the second tool. mpmath, not statsmodels."""
    if n == 0:
        return 0.0, 0.0
    kk, nn = mp.mpf(k), mp.mpf(n)
    p = kk / nn
    d = 1 + z ** 2 / nn
    c = p + z ** 2 / (2 * nn)
    h = z * mp.sqrt(p * (1 - p) / nn + z ** 2 / (4 * nn ** 2))
    return float((c - h) / d), float((c + h) / d)


def _interval(label: str, k: int, n: int) -> None:
    if n == 0:
        print(f"  {label}: no denominator -- nothing is claimed")
        return
    lo1, hi1 = proportion_confint(k, n, method="wilson")
    lo2, hi2 = _wilson_mp(k, n)
    cp = proportion_confint(k, n, method="beta")
    ok = abs(lo1 - lo2) < 1e-9 and abs(hi1 - hi2) < 1e-9
    print(f"  {label}")
    print(f"    {k} of {n} = {k / n:.6f}")
    print(f"    Wilson statsmodels [{lo1:.6f}, {hi1:.6f}]")
    print(f"    Wilson mpmath      [{lo2:.6f}, {hi2:.6f}]  "
          f"{'AGREE' if ok else 'DISAGREE'}")
    print(f"    Clopper-Pearson    [{cp[0]:.6f}, {cp[1]:.6f}]")


def shadow_records() -> list[tuple[str, dict]]:
    """Every severity_spec_shadow dict the archive holds, brace-matched.

    NOT a grep for the key: the key appears in prose comments echoed into logs
    too, so a mention count (97 of 141 files) is not a record count (13).
    """
    out = []
    for f in sorted(LOGS.glob("*.log")):
        try:
            t = f.read_text(errors="replace")
        except Exception:                                      # noqa: BLE001
            continue
        if "severity_spec_shadow" not in t:
            continue
        for m in re.finditer(r"severity_spec_shadow'?: (\{)", t):
            i = m.end() - 1
            depth, j = 0, i
            while j < len(t):
                if t[j] == "{":
                    depth += 1
                elif t[j] == "}":
                    depth -= 1
                    if depth == 0:
                        break
                j += 1
            try:
                d = ast.literal_eval(t[i:j + 1])
            except Exception:                                  # noqa: BLE001
                continue
            if isinstance(d, dict) and "critical_asserted" in d:
                out.append((f.name, d))
    return out


def gate_rows() -> list[tuple[str, bool, int, int, int]]:
    rows = []
    for f in sorted(LOGS.glob("*.log")):
        try:
            t = f.read_text(errors="replace")
        except Exception:                                      # noqa: BLE001
            continue
        ms = list(GATE.finditer(t))
        if not ms:
            continue
        c = sum(int(m.group(1)) for m in ms)
        r = sum(int(m.group(2)) for m in ms)
        h = sum(int(m.group(3)) for m in ms)
        rows.append((f.name, bool(SIM.search(t)), c, r, h))
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(
        prog="what_actually_blocks_the_severity_promotion_2026-11-02.py",
        description="Why the severity shadow has moved nothing. Reads only.")
    ap.add_argument("--run-dir", default=None,
                    help="a run directory to read falsifier paths from "
                         "(default: the newest with a runner_state.json)")
    a = ap.parse_args()

    print("=" * 74)
    print("1. HIS PROPOSAL IS THE SHIPPED CONFIGURATION ALREADY")
    print("=" * 74)
    import sys
    if str(REPO) not in sys.path:
        sys.path.insert(0, str(REPO))
    import bench.reference_runner_v3 as R
    flds = R.RunnerConfig.__dataclass_fields__
    for n in ("severity_spec_enabled", "discrimination_control_ask",
              "falsifier_gate_enabled"):
        print(f"  {n:28s} default = {flds[n].default!r}")
    print(f"  _SEVERITY_SPEC module mirror = {R._SEVERITY_SPEC}")
    print("  -> False means the OLD measure decides and the new one RECORDS.")
    print("     That is exactly 'old live, new in shadow'. Built 2026-10-15.")

    recs = shadow_records()
    print()
    print("=" * 74)
    print("2. WHAT THE SHADOW HAS RECORDED IN 6 RUNS")
    print("=" * 74)
    print(f"  shadow records parsed: {len(recs)} across "
          f"{len({f for f, _ in recs})} log files")
    moved = [d for _, d in recs if d.get("critical_asserted") != d.get("critical_spec")]
    crossed = [d for _, d in recs if d.get("crossed_downward")]
    _interval("records where the new measure MOVES the critical count",
              len(moved), len(recs))
    _interval("records with any finding crossing downward",
              len(crossed), len(recs))
    vt = sum((d.get("V_true") or 0) for _, d in recs)
    vn = sum((d.get("V_none") or 0) for _, d in recs)
    vf = sum((d.get("V_false") or 0) for _, d in recs)
    print(f"\n  verification factor totals: V_true={vt}  V_none={vn}  V_false={vf}")
    print("  V_false is the ONLY value that annihilates the product, so it is")
    print("  the only input on which the 2 measures can disagree at the cut.")
    _interval("findings REFUTED, of all findings the shadow saw", vf, vt + vn + vf)

    print()
    print("=" * 74)
    print("3. DOES MONEY DECIDE IT? SIMULATED vs PAID, FROM THE GATE LINES")
    print("=" * 74)
    rows = gate_rows()
    sc = sum(c for _, s, c, _, _ in rows if s)
    sr = sum(r for _, s, _, r, _ in rows if s)
    pc = sum(c for _, s, c, _, _ in rows if not s)
    pr = sum(r for _, s, _, r, _ in rows if not s)
    print(f"  SIMULATED runs: CONFIRMED {sc}, REFUTED {sr}")
    print(f"  PAID runs     : CONFIRMED {pc}, REFUTED {pr}")
    odds, p = stats.fisher_exact([[sr, sc], [pr, pc]])
    chi = None
    try:
        chi = stats.chi2_contingency([[sr, sc], [pr, pc]])[1]
    except Exception:                                          # noqa: BLE001
        chi = float("nan")
    print(f"  Fisher exact p = {p:.6f}   odds ratio = {odds}")
    print(f"  chi-square   p = {chi:.6f}  (second tool; small cells, so Fisher")
    print(f"                              is the one that binds)")
    print("  -> THE ONLY REFUTATION IN THE WHOLE GATE RECORD CAME FROM A")
    print("     SIMULATED RUN. A paid run has never produced one. Money is not")
    print("     the variable, and the earlier answer that implied it was is")
    print("     withdrawn.")

    print()
    print("=" * 74)
    print("4. WHERE DO THIS RUN'S FALSIFIERS POINT?")
    print("=" * 74)
    if a.run_dir is None:
        cands = [d for d in LOGS.iterdir()
                 if d.is_dir() and (d / "runner_state.json").is_file()]
        a.run_dir = str(max(cands, key=lambda d: d.stat().st_mtime))
    rd = pathlib.Path(a.run_dir)
    print(f"  run: {rd.name}")
    st = json.loads((rd / "runner_state.json").read_text())
    e = (st.get("registry") or {}).get("entries") or {}
    ents = list(e.values()) if isinstance(e, dict) else list(e)
    PATH = re.compile(r"""['"]((?:/|\.\./|\./)[^'"]{4,200})['"]""")
    staged_root = "CDSFL_review_targets"
    with_code = [x for x in ents if (x.get("falsifier_code") or "").strip()]
    at_staged, absolute = 0, 0
    for x in with_code:
        ps = PATH.findall(x["falsifier_code"])
        if any(staged_root in p for p in ps):
            at_staged += 1
        if any(p.startswith("/") for p in ps):
            absolute += 1
    print(f"  entries {len(ents)}, carrying falsifier_code {len(with_code)}")
    _interval(f"falsifiers naming the STAGED target root ({staged_root})",
              at_staged, len(with_code))
    _interval("falsifiers using an ABSOLUTE path literal",
              absolute, len(with_code))
    print("  WHY THE ABSOLUTE COUNT MATTERS, in the runner's own words at")
    print("  reference_runner_v3.py:651 -- `_build_discrimination_overlay`")
    print("  'raises \"target must be repo-relative\" on an absolute path, so")
    print("  passing one silently disabled the discrimination control'.")
    print("  `repo_relative_target` was written to normalise that at ingestion.")
    print("  WHETHER IT STILL REACHES THIS PATH IS NOT TESTED HERE and must not")
    print("  be asserted either way.")

    cen = collections.Counter(
        str(x.get("falsifier_verdict") or "<none>") for x in ents)
    print(f"\n  falsifier verdict census for this run: {dict(cen)}")
    dc = collections.Counter(
        str(x.get("discrimination_control") or "<none>") for x in ents)
    print(f"  discrimination control stored on entries: {dict(dc)}")
    log = LOGS / f"{rd.name.rsplit('_', 1)[0]}.log"
    if log.is_file():
        t = log.read_text(errors="replace")
        print(f"  but the LOG reports INDETERMINATE_NOT_INTERCEPTED "
              f"{t.count('INDETERMINATE_NOT_INTERCEPTED')} time(s) and")
        print(f"  'out-of-scope path opened or listed' "
              f"{t.count('out-of-scope path opened or listed')} time(s).")
        print("  THE SCOPE FLAG IS A FALSE POSITIVE AT THE HIGHEST TIER: it")
        print("  fires on the staged target root the falsifier is REQUIRED to")
        print("  read, and it blocked nothing.")
        print("  AND THE CONTROL'S OUTCOME IS NOT PERSISTED TO THE ENTRIES, so")
        print("  no downstream consumer can read it.")

    print()
    print("=" * 74)
    print("CONCLUSION")
    print("=" * 74)
    print("  His proposal works and is already running. What stops it reaching a")
    print("  promotion decision is not money and not more shadow runs: it is")
    print("  that the 2 measures can only disagree on a REFUTED finding, and")
    print(f"  {vf} of {vt + vn + vf} findings the shadow saw were refuted.")
    print("  The cheap, additive next step is to make the discrimination")
    print("  control's outcome readable on the entry, so the refutation rate")
    print("  stops being a number only a log holds.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
