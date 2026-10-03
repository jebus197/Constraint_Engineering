#!/usr/bin/env python3
"""Compute every pending study measurement from a finished run, in one pass.

WHY THIS EXISTS. Five of the programme's measurements can only be answered from
a finished run's registry: whether the voided-verification field populated,
whether refused falsifier bodies are retained in full, what the discrimination
control's reach was, whether the launcher's declaration matches what fired, and
the round-2 discriminator below. Doing them by hand at run end is how a step
gets skipped; this runs them together and reports what it could NOT compute
rather than leaving a gap silent.

THE ROUND-2 DISCRIMINATOR, which is the reason this was written before the run
finished. In study run 1b the cannot-fail share of decidable falsifiers jumped
from 0 of 6 in round 1 to 5 of 6 in round 2. Two explanations were recorded at
the time and deliberately not chosen between:

  MECHANISM -- as the sandbox target accumulates applied fixes, a corrected copy
               DERIVED from a proposed fix becomes nearly indistinguishable from
               an already-fixed target, so the falsifier fires on both and the
               comparison degenerates. The existing guard only refuses a
               BYTE-IDENTICAL copy, so it would miss this.
  CONTENT   -- by round 2 the well-specified defects are resolved and the
               survivors are vaguer claims, which genuinely yield weaker
               instruments.

They make different predictions, which is what makes this a test rather than a
narrative: MECHANISM predicts the correction touches a SMALLER FRACTION of the
target as the rounds advance, because the target is being rewritten toward
already-fixed text; CONTENT predicts no such trend.

THE FIRST DESIGN WAS UNWORKABLE AND THAT WAS FOUND BEFORE IT WAS NEEDED. It
computed a difflib similarity between each entry's `corrected_copy` and the
target text as the entry recorded it -- and NO SUCH FIELD EXISTS. Entries carry
`corrected_copy_target_sha`, a hash, not the text, so the ratio was
uncomputable and the discriminator returned "0 entries in each group" on real
data. Writing it early is what caught that; at run end it would have looked like
an absent effect rather than an absent field.

WHAT IS COMPUTED INSTEAD, from the run's own log, which records both numbers at
every splice: `corrected passage of N chars spliced into <target> (M chars)`.
The touched fraction is N/M. Its trend across rounds is tested with a Spearman
rank correlation (scipy) against the round index, cross-checked by numpy on the
same ranks. A NEGATIVE correlation supports MECHANISM.

ITS LIMIT, stated: the touched fraction is a proxy for similarity, not
similarity itself. A small correction can still be the decisive one. So a
negative trend is EVIDENCE FOR mechanism rather than proof of it, and the
absence of a trend leaves content the better-supported explanation without
establishing it.

Usage:  python3 scripts/run_end_study_harvest_2026-10-03.py --run <dir> [--json]
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))


def wilson(k: int, n: int) -> dict:
    if n == 0:
        return {"k": k, "n": n, "pct": None}
    from statsmodels.stats.proportion import proportion_confint
    import mpmath as mp
    lo, hi = proportion_confint(k, n, method="wilson")
    z = mp.mpf("1.959963984540054")
    p = mp.mpf(k) / n
    d = 1 + z**2 / n
    c = (p + z**2 / (2 * n)) / d
    h = z * mp.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / d
    assert abs(float(c - h) - lo) < 1e-9 and abs(float(c + h) - hi) < 1e-9, (
        f"statsmodels and mpmath disagree on Wilson for {k}/{n}")
    return {"k": k, "n": n, "pct": round(100.0 * k / n, 4),
            "wilson": [round(100 * lo, 4), round(100 * hi, 4)]}


def _entries(run: pathlib.Path) -> tuple[dict, dict]:
    for name in ("runner_state.json",):
        f = run / name
        if f.is_file():
            d = json.loads(f.read_text(encoding="utf-8", errors="replace"))
            return ((d.get("registry") or {}).get("entries") or {}), d
    for f in sorted(run.glob("*_report.json")):
        d = json.loads(f.read_text(encoding="utf-8", errors="replace"))
        return ((d.get("registry") or {}).get("entries") or {}), d
    return {}, {}


def voided_verification(es: dict) -> dict:
    """Did the 2026-10-03 legibility field populate on a live run?"""
    nd = [c for c, e in es.items() if isinstance(e, dict)
          and (e.get("falsifier_verdict") or "") == "NON_DISCRIMINATING"]
    voided = [c for c in nd if es[c].get("verification_voided")]
    reasons = [c for c in voided if (es[c].get("verification_voided_reason") or "").strip()]
    still_verified = [c for c in nd if es[c].get("verified") is True]
    return {
        "non_discriminating": sorted(nd),
        "carrying_verification_voided": wilson(len(voided), max(len(nd), 1)),
        "carrying_a_reason": len(reasons),
        "still_marked_verified": sorted(still_verified),
        "verdict": ("the field populated on every voided entry"
                    if nd and len(voided) == len(nd) else
                    "NO voided entries in this run, so the field is untested here"
                    if not nd else
                    "the field did NOT populate on every voided entry -- a defect"),
        "note": ("`verified` STAYING True is correct and deliberate: withholding it "
                 "is the blocking behaviour the founder deferred. The field exists "
                 "to make the contradiction legible, not to change the outcome."),
    }


def refusal_visibility(es: dict) -> dict:
    """Are refused falsifier bodies retained in full, not just truncated?"""
    recs = full = cut_only = 0
    for e in es.values():
        if not isinstance(e, dict):
            continue
        for r in (e.get("routing_history") or []):
            body_full = (r.get("last_falsifier_code_full") or "").strip()
            body_cut = (r.get("last_falsifier_code") or "").strip()
            if not (body_full or body_cut):
                continue
            recs += 1
            if body_full:
                full += 1
            else:
                cut_only += 1
    return {"routing_records_with_a_body": recs,
            "carrying_the_full_body": wilson(full, max(recs, 1)),
            "truncation_only": cut_only,
            "verdict": ("every recorded body is retained in full"
                        if recs and not cut_only else
                        "no routing record carries a body in this run"
                        if not recs else
                        f"{cut_only} record(s) exist only as a truncation")}


def round2_discriminator(run: pathlib.Path) -> dict:
    """MECHANISM or CONTENT for the cannot-fail jump. See the module docstring.

    Reads the RUN LOG, not the registry, because the registry stores a hash of
    the target a copy was made against and never the text itself.
    """
    import numpy as np
    from scipy.stats import spearmanr
    log = run / "console.log"
    if not log.is_file():
        return {"verdict": "UNDECIDABLE: no console.log in this run directory"}
    text = log.read_text(encoding="utf-8", errors="replace")

    # Attribute each splice to the round it fell in, by counting round headers
    # seen so far. The round index is what the trend is tested against.
    rnd, rows = 0, []
    for line in text.splitlines():
        if re.search(r"^\[[0-9:]+\] Round (\d+)/", line):
            rnd = int(re.search(r"Round (\d+)/", line).group(1))
            continue
        m = re.search(r"corrected passage of (\d+) chars spliced into \S+ \((\d+) chars\)",
                      line)
        if m:
            n_chars, m_chars = int(m.group(1)), int(m.group(2))
            if m_chars > 0:
                rows.append((rnd, n_chars / m_chars))
    out = {"splices": len(rows),
           "rounds_covered": sorted({r for r, _ in rows})}
    if len(rows) < 6 or len(out["rounds_covered"]) < 2:
        out["verdict"] = ("UNDECIDABLE: fewer than 6 splices or only 1 round, so no "
                          "trend can be tested. This is a DATA limit, not a result.")
        return out
    rounds = np.array([r for r, _ in rows], dtype=float)
    frac = np.array([f for _, f in rows], dtype=float)
    rho, p = spearmanr(rounds, frac)
    # numpy cross-check of the same rank correlation
    def _rank(a):
        order = a.argsort()
        rk = np.empty_like(order, dtype=float)
        rk[order] = np.arange(len(a), dtype=float)
        return rk
    rr, rf = _rank(rounds), _rank(frac)
    rho_np = float(np.corrcoef(rr, rf)[0, 1])
    out["touched_fraction_by_round"] = {
        int(r): round(float(np.median(frac[rounds == r])), 6)
        for r in sorted(set(rounds))}
    out["spearman_rho_scipy"] = round(float(rho), 6)
    out["spearman_rho_numpy_on_ranks"] = round(rho_np, 6)
    out["p_two_sided"] = float(p)
    out["verdict"] = (
        "MECHANISM supported: the correction touches a significantly SMALLER "
        "fraction of the target as rounds advance" if rho < 0 and p < 0.05 else
        "MECHANISM contradicted: the touched fraction GROWS with the round"
        if rho > 0 and p < 0.05 else
        "no trend at alpha = 0.05; CONTENT remains the better-supported "
        "explanation, though an absent trend is weaker evidence than a trend")
    out["limit"] = ("the touched fraction is a PROXY for similarity, not similarity; "
                    "a small correction can still be the decisive one")
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--run", default=None, help="a finished run directory")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    if not a.run:
        ap.error("--run is required")

    run = pathlib.Path(a.run)
    if not run.is_absolute():
        run = REPO / run
    es, whole = _entries(run)
    if not es:
        print(f"no registry under {run} -- the run has not written one yet",
              file=sys.stderr)
        return 1

    out = {
        "run": run.name,
        "entries": len(es),
        "voided_verification": voided_verification(es),
        "refusal_visibility": refusal_visibility(es),
        "round2_discriminator": round2_discriminator(run),
        "declared_config_present": bool(whole.get("_declared_config")),
    }
    # measurement 10 is a separate committed producer; call it rather than
    # reimplement it, so there is one definition of the comparison.
    rep = next(iter(sorted(run.glob("*_report.json"))), None)
    if rep:
        r = subprocess.run(
            [sys.executable, str(REPO / "scripts" / "declared_vs_observed_2026-10-03.py"),
             "--report", str(rep), "--json"],
            capture_output=True, text=True, timeout=600)
        try:
            out["measurement_10"] = json.loads(r.stdout)
        except ValueError:
            out["measurement_10"] = {"error": r.stderr[-400:] or "no JSON returned"}
    else:
        out["measurement_10"] = {"error": "no report file in this run directory"}

    if a.json:
        print(json.dumps(out, indent=2, sort_keys=True))
        return 0
    print(f"RUN-END STUDY HARVEST — {out['run']}  ({out['entries']} entries)")
    for key in ("voided_verification", "refusal_visibility", "round2_discriminator"):
        print(f"\n  {key}")
        for k, v in out[key].items():
            print(f"    {k:34s} {v}")
    print(f"\n  declaration present for measurement 10: "
          f"{out['declared_config_present']}")
    m10 = out["measurement_10"]
    if "totals" in m10:
        print(f"  measurement 10 totals: {m10['totals']}")
    else:
        print(f"  measurement 10: {m10.get('error')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
