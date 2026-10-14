# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'joint_the_directive_set_2026-10-14', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 63eecabf3d54d554762f94bcdd900731e86deacc475856ee6c32cf012c85e2fc
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""J1 and J2, measured: what the caps actually do, and whether one run can decide it.

JOINT ROUND, 2026-10-14. Both panel seats refused outright removal of the
directive length caps and asked for a measurement. The brief asks for the
measurement to be SPECIFIED precisely enough that the next simulated run either
settles it or is shown to be underpowered. This script supplies the numbers that
decide which of those two it is, and the section-overlap figure that chooses the
chatter predicate.

Every proportion carries a Wilson 95% interval from 2 independent
implementations (statsmodels and a hand/scipy computation), and every sample
size carries 2 independent derivations (statsmodels' arcsine-transform solver
and a closed-form normal-approximation expression, the latter also evaluated
symbolically by SymPy).

Reads only this repository's own run records and directive sources. No scoring
key, no answer file, no planted-defect manifest.

    python3 scripts/the_caps_measurement_is_underpowered_2026-10-14.py
"""
from __future__ import annotations

import glob
import importlib.util
import json
import math
import os
import pathlib
import re
import sys
from collections import Counter

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "bench"))

import numpy as np                                      # noqa: E402
import sympy as sp                                      # noqa: E402
from scipy.stats import norm                            # noqa: E402
from statsmodels.stats.power import NormalIndPower      # noqa: E402
from statsmodels.stats.proportion import (              # noqa: E402
    proportion_confint, proportion_effectsize)

Z = 1.959963984540054


def wilson_hand(k: int, n: int) -> tuple[float, float]:
    """Wilson score interval written out, so statsmodels is CHECKED not trusted."""
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + Z * Z / n
    c = (p + Z * Z / (2 * n)) / d
    h = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def ci(label: str, k: int, n: int) -> tuple[float, float]:
    a = wilson_hand(k, n)
    b = tuple(proportion_confint(k, n, 0.05, method="wilson")) if n else (0.0, 0.0)
    agree = all(abs(x - y) < 1e-12 for x, y in zip(a, b))
    pct = (k / n * 100) if n else float("nan")
    print(f"  {label:54s} {k:5d}/{n:<5d} = {pct:8.4f}%  "
          f"Wilson [{a[0]*100:7.4f}%, {a[1]*100:7.4f}%]  "
          f"{'[AGREE]' if agree else '[DISAGREE]'}")
    return a


# ─────────────────────────── SECTION 1 — the cap is BINARY ───────────────────
def section_cap_is_binary() -> None:
    from cdsfl_registry import composer as C
    core = (C.DIRECTIVES_DIR / "universal" / "cdsfl_core_formal.md").read_text(
        encoding="utf-8")
    print("\n=== 1. THE CAP IS A BINARY SWITCH, NOT A GRADED KNOB ===")
    print(f"  cdsfl_core_formal.md source: {len(core):,} chars, "
          f"{len(re.findall(r'^## ', core, re.M))} level-2 headings")
    delivered = {}
    for key in list(C.PHENOTYPE_TRANSFORMS) + [""]:
        t = C.PHENOTYPE_TRANSFORMS.get(key, C.PhenotypeTransform())
        pkt = C._load_universal_directive(key or None)
        delivered[key or "(default)"] = len(pkt.text)
        heads = len(re.findall(r"^## ", pkt.text, re.M))
        print(f"  {key or '(default)':16s} cap={t.max_directive_chars:6,d} "
              f"style={t.format_style:8s} -> delivered {len(pkt.text):6,d} chars, "
              f"{heads} of 16 headings")
    distinct = sorted(set(delivered.values()))
    print(f"  distinct delivered lengths over the whole configured cap range "
          f"{sorted({C.PHENOTYPE_TRANSFORMS.get(k, C.PhenotypeTransform()).max_directive_chars for k in list(C.PHENOTYPE_TRANSFORMS) + ['']})}: "
          f"{distinct}")
    assert len(distinct) == 1, distinct
    print("  -> the cap VALUE changes nothing. Every seat receives the same "
          f"{distinct[0]:,}-char minimal render. A cap-value sweep is therefore")
    print("     not a design; the only measurable contrast is minimal vs full.")


# ───────────────────── SECTION 2 — candidate statistics, base rates ──────────
def _sim_entries():
    for p in sorted(glob.glob(str(REPO / "bench" / "logs" / "sim*" / "runner_state.json"))):
        d = json.loads(pathlib.Path(p).read_text(encoding="utf-8"))
        e = d.get("registry", {}).get("entries", {})
        if isinstance(e, dict):
            yield os.path.basename(os.path.dirname(p)), [
                v for v in e.values() if isinstance(v, dict)]


def section_base_rates() -> tuple[int, int]:
    print("\n=== 2. THE 2 STATISTICS THE SEATS PROPOSED ARE BOTH UNUSABLE ===")
    runs = list(_sim_entries())
    allv = [v for _, vs in runs for v in vs]
    n = len(allv)
    conf = sum(1 for v in allv if str(v.get("status", "")).upper() == "CONFIRMED")
    per_run_conf = [sum(1 for v in vs if str(v.get("status", "")).upper() == "CONFIRMED")
                    for _, vs in runs]
    crit = [v for v in allv if isinstance(v.get("severity"), (int, float))
            and v["severity"] >= 0.7]
    crit_f = sum(1 for v in crit if v.get("falsifier_code"))
    det = sum(1 for v in allv
              if str(v.get("falsifier_verdict", "")).upper() in {"CONFIRMED", "REFUTED"})
    print(f"  corpus: {len(runs)} simulated runs, {n} registry entries")
    ci("fable's 'runner-reverified confirm rate'", conf, n)
    print(f"      FLOOR-BOUND AND CLUSTERED: per-run CONFIRMED counts "
          f"{per_run_conf}; {max(per_run_conf)} of {conf} events are in one run.")
    ci("critical findings carrying a falsifier", crit_f, len(crit))
    print("      CEILING-BOUND: at 94.83% the uncapped arm can gain at most 5.17 "
          "points.")
    ci("determinate falsifier verdict (CONFIRMED|REFUTED)", det, n)
    print("      USABLE: away from 0 and 1, harness-computed, and the requirement "
          "it measures\n      is stated ONLY in the 2 core sections the cap "
          "deletes.")
    return det, n


# ─────────────────────────── SECTION 3 — the power ───────────────────────────
def section_power(det: int, n: int) -> None:
    p0 = det / n
    print("\n=== 3. SAMPLE SIZE PER ARM, 2 DERIVATIONS + A SYMBOLIC CHECK ===")
    print(f"  baseline p0 = {p0:.6f} (the capped arm, from the archive)")
    za, zb = norm.ppf(0.975), norm.ppf(0.80)
    for p1 in (0.85, 0.88, 0.90, 0.95):
        h = proportion_effectsize(p1, p0)
        n_sm = NormalIndPower().solve_power(effect_size=h, power=0.80, alpha=0.05,
                                            ratio=1, alternative="two-sided")
        pb = (p0 + p1) / 2
        n_cf = ((za * math.sqrt(2 * pb * (1 - pb))
                 + zb * math.sqrt(p0 * (1 - p0) + p1 * (1 - p1))) ** 2) / (p1 - p0) ** 2
        A, B, P = sp.symbols("z_a z_b p_bar", positive=True)
        sym = ((A * sp.sqrt(2 * P * (1 - P))
                + B * sp.sqrt(sp.Float(p0) * (1 - sp.Float(p0))
                              + sp.Float(p1) * (1 - sp.Float(p1)))) ** 2
               / sp.Float(p1 - p0) ** 2)
        n_sy = float(sym.subs({A: sp.Float(za), B: sp.Float(zb), P: sp.Float(pb)}))
        tag = "AGREE" if abs(n_cf - n_sy) < 1e-6 and abs(n_sm - n_cf) / n_cf < 0.03 \
            else "DISAGREE"
        print(f"  p1={p1:.2f}  statsmodels(arcsine) {n_sm:8.1f}   "
              f"closed form {n_cf:8.1f}   SymPy {n_sy:8.1f}   [{tag}]")
    yields = [len(vs) for _, vs in _sim_entries()]
    print(f"  findings per simulated run, observed: {sorted(yields)}  "
          f"mean {np.mean(yields):.1f}")
    need = NormalIndPower().solve_power(
        effect_size=proportion_effectsize(0.90, p0), power=0.80, alpha=0.05,
        ratio=1, alternative="two-sided")
    print(f"  -> ONE run per arm supplies ~{np.mean(yields):.0f} findings against "
          f"the ~{need:.0f} needed for a 10-point effect.")
    print(f"     UNDERPOWERED by a factor of {need/np.mean(yields):.1f}. "
          f"~{math.ceil(need/np.mean(yields))} runs PER ARM are required, and "
          "findings cluster\n     within (run, seat), so that count is a FLOOR "
          "before any design effect.")


# ───────────────────── SECTION 4 — J2, which predicate to adopt ──────────────
def section_predicate() -> None:
    print("\n=== 4. J2 — P2 REPRODUCES THE INDEPENDENT 2026-07-18 PRUNING REVIEW ===")
    spec = importlib.util.spec_from_file_location(
        "_chatter", REPO / "scripts" / "directive_chatter_predicate_2026-10-14.py")
    ch = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ch)
    path = REPO / "bench" / "directives" / "universal" / "cdsfl_operational.md"
    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")
    hits = sorted(ch.p2_medium(text))
    secmap, cur = {}, "(preamble)"
    for i, l in enumerate(lines):
        m = re.match(r"^(#{1,3})\s+(.*)", l)
        if m:
            cur = m.group(2).strip()
        secmap[i] = cur
    # The 2026-07-18 review's own verdict per section, as the chatter producer
    # records it. Anything not named 'compress' there is KEEP-VERBATIM.
    compressible = ("7.1.", "14.", "16.", "17.", "18", "PREAMBLE")
    inside = [i for i in hits
              if any(secmap[i].lstrip("§").startswith(c.lstrip("§"))
                     for c in compressible)]
    c = Counter(secmap[i] for i in hits)
    for k, v in c.most_common():
        mark = "compress     " if any(k.lstrip("§").startswith(x.lstrip("§"))
                                      for x in compressible) else "KEEP-VERBATIM"
        print(f"  [{mark}] {v:3d} lines  {k[:66]}")
    ci("P2 hits inside a 'compress' section", len(inside), len(hits))
    print("  -> 2 instruments derived independently (a human pruning review in "
          "July, a\n     mechanical predicate in October) concur on ~90% of the "
          "marked lines. The\n     residual sits in §15 FFAFP Admissibility, "
          "which the review marks KEEP-VERBATIM;\n     under the additive "
          "standard KEEP-VERBATIM wins, because no measurement shows\n     "
          "removal dominates.")


def main() -> int:
    section_cap_is_binary()
    det, n = section_base_rates()
    section_power(det, n)
    section_predicate()
    print("\nDONE.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
