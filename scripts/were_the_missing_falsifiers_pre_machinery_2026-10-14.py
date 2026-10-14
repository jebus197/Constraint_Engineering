#!/usr/bin/env python3
"""Are the falsifier-less findings concentrated BEFORE the machinery existed?

THE FOUNDER'S QUESTION, 2026-10-14, and it is precisely falsifiable: *"one thing
you keep rediscovering is that a large part of the project never carried any
falsifiers at all. But when you look at this more closely, you have tended to
find that the large number you often discover relates to a period before much of
the falsification machinery of the project even existed, and where the models
were 'voting' and where the principles of the project existed mostly as prose,
and indeed in many cases, even before our current maths model existed."*

His hypothesis predicts a CONCENTRATION: the falsifier-less share should be high
before the machinery landed and low after. If instead the share is flat across
the milestones, the finding is NOT an artefact of the pre-machinery era and the
rediscovery concern does not apply to it.

MILESTONE DATES ARE TAKEN FROM GIT, not from recollection -- the first commit
that added each file:

    2026-03-12  repository begins
    2026-03-14  bench/directives/universal/cdsfl_core_formal.md
    2026-03-19  docs/MATHEMATICAL_APPENDIX.md          (the maths model)
    2026-06-03  bench/falsifier_verify.py              (falsifier VERIFICATION)
    2026-07-12  bench/routing.py                       (the routing ladder)
    2026-09-01  bench/reference_runner_v3.py           (runner v3)
    2026-09-07  bench/dm/_rk_proof.py                  (the worked-proof gate)

THE PREDICATE IS NOT RE-DERIVED. It is the one that produced the 58.7629%
headline, copied from `scripts/never_attempted_findings_2026-10-14.py` (fable,
panel of 2026-10-14): a finding has a falsifier iff `falsifier_code` is a
non-empty string, and it was ATTEMPTED iff it carries any of 5 named markers.
This script's first act is to reproduce that script's 3 totals exactly; if it
cannot, the stratification is measuring a different corpus and it says so and
stops rather than reporting a rate.

TWO CORPUS DEFECTS ARE HANDLED, both found on 2026-10-14:
  * `bench/logs/exp36_evidence_latest` is a SYMLINK to a real run directory, so a
    naive recursive glob counts 217 findings twice (cc2's catch).
  * 304 rows sit under `sandbox_harvest`/`seat_evidence`, which are frozen copies
    of OTHER runs' registries. For a question about WHEN a finding was made, a
    harvest copy carries the harvesting round's date, not the finding's, so it is
    reported separately rather than silently pooled.

RUN: python3 scripts/were_the_missing_falsifiers_pre_machinery_2026-10-14.py
`--help` is free and dispatches nothing.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import sys
from collections import defaultdict

REPO = pathlib.Path(__file__).resolve().parents[1]
LOGS = REPO / "bench" / "logs"

# Copied verbatim from the producer of the 58.7629% headline.
ATTEMPT_MARKERS = ("routing_history", "error_routed", "bugzilla_attempted",
                   "fix_efficacy_attempted", "routing_deferred")

MILESTONES = [
    ("repo begins",            "2026-03-12"),
    ("core formal directive",  "2026-03-14"),
    ("maths appendix",         "2026-03-19"),
    ("falsifier_verify.py",    "2026-06-03"),
    ("routing ladder",         "2026-07-12"),
    ("reference_runner_v3",    "2026-09-01"),
    ("worked-proof gate",      "2026-09-07"),
]

_TS = re.compile(r"(20\d\d)(\d\d)(\d\d)T\d{6}Z")
_ISO = re.compile(r"(20\d\d)-(\d\d)-(\d\d)")


def run_date(name: str):
    """The date a run directory's name declares, or None."""
    m = _TS.search(name)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    m = _ISO.search(name)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    return None


def collect():
    """Every finding, de-duplicated, with its run name, date and status."""
    seen_hash, rows, files = set(), [], []
    for fp in sorted(LOGS.glob("**/runner_state.json")):
        real = fp.resolve()
        try:
            raw = real.read_bytes()
        except OSError:
            continue
        h = hashlib.sha256(raw).hexdigest()
        if h in seen_hash:                 # the symlink, and harvest duplicates
            continue
        seen_hash.add(h)
        try:
            state = json.loads(raw)
        except ValueError:
            continue
        reg = (state.get("registry") or {}).get("entries") or {}
        if not isinstance(reg, dict):
            continue
        files.append(fp)
        # The run directory is the first path component under bench/logs.
        rel = fp.relative_to(LOGS).parts
        harvested = ("sandbox_harvest" in rel) or ("seat_evidence" in rel)
        run = rel[0]
        for cid, e in reg.items():
            if not isinstance(e, dict):
                continue
            if not isinstance(e.get("severity"), (int, float)):
                continue
            has_code = bool((e.get("falsifier_code") or "").strip())
            attempted = any(e.get(m) for m in ATTEMPT_MARKERS)
            rows.append({
                "run": run, "cid": cid, "date": run_date(run),
                "harvested": harvested, "has_code": has_code,
                "attempted": attempted,
                "severity": float(e["severity"]),
            })
    return rows, files


def wilson(k, n):
    """Wilson 95%, computed twice with independent tools; returns both."""
    a = b = None
    try:
        from statsmodels.stats.proportion import proportion_confint
        a = tuple(float(x) for x in proportion_confint(k, n, 0.05, method="wilson"))
    except Exception:
        pass
    try:
        import mpmath as mp
        mp.mp.dps = 40
        z = mp.mpf("1.959963984540054235524594430520551527955")
        N, p = mp.mpf(n), mp.mpf(k) / n
        c = p + z ** 2 / (2 * N)
        d = z * mp.sqrt(p * (1 - p) / N + z ** 2 / (4 * N ** 2))
        den = 1 + z ** 2 / N
        b = (float((c - d) / den), float((c + d) / den))
    except Exception:
        pass
    return a, b


def pct(k, n):
    if n == 0:
        return "n=0"
    a, b = wilson(k, n)
    s = f"{k}/{n} = {k/n*100:7.4f}%"
    if a:
        s += f"  [{a[0]*100:7.4f}%, {a[1]*100:7.4f}%]"
    if a and b and max(abs(a[0]-b[0]), abs(a[1]-b[1])) > 1e-9:
        s += "  ** TOOLS DISAGREE **"
    return s


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if not LOGS.is_dir():
        print(f"no logs at {LOGS}")
        return 2

    rows, files = collect()
    print(f"=== CORPUS ===")
    print(f"  distinct runner_state.json by content: {len(files)}")
    print(f"  findings carrying a numeric severity : {len(rows)}")
    harv = [r for r in rows if r["harvested"]]
    live = [r for r in rows if not r["harvested"]]
    print(f"    of which in harvest/seat_evidence  : {len(harv)}")
    print(f"    live run registries                : {len(live)}")

    # ── REPRODUCE THE HEADLINE, OR STOP ──
    no_code = [r for r in rows if not r["has_code"]]
    never = [r for r in no_code if not r["attempted"]]
    print(f"\n=== REPRODUCING THE 2026-10-14 HEADLINE (fable's producer) ===")
    print(f"  entries           : {len(rows)}  (published 3298)")
    print(f"  no falsifier code : {len(no_code)}  (published 1938)")
    print(f"  never attempted   : {len(never)}  (published 1639)")
    ok = (len(rows) == 3298 and len(no_code) == 1938 and len(never) == 1639)
    print(f"  SAME CORPUS       : {ok}")
    if not ok:
        print("\n  ** The stratification below is on a DIFFERENT corpus from the")
        print("     published headline, so it is NOT comparable to it. Reported")
        print("     anyway, labelled, rather than presented as the same measure.")

    # ── DATING ──
    dated = [r for r in rows if r["date"]]
    undated = [r for r in rows if not r["date"]]
    print(f"\n=== DATING, FROM RUN DIRECTORY NAMES ===")
    print(f"  dated   : {len(dated)}")
    print(f"  UNDATED : {len(undated)}  (excluded from the stratification below)")
    if undated:
        byrun = defaultdict(int)
        for r in undated:
            byrun[r["run"]] += 1
        for run, n in sorted(byrun.items(), key=lambda kv: -kv[1])[:12]:
            print(f"      {n:5d}  {run}")

    # ── THE TEST ──
    print(f"\n=== HIS HYPOTHESIS: IS THE FALSIFIER-LESS SHARE CONCENTRATED EARLY? ===")
    print(f"  (dated findings only; 'before' is strictly before the milestone date)")
    results = {}
    for label, date in MILESTONES:
        before = [r for r in dated if r["date"] < date]
        after = [r for r in dated if r["date"] >= date]
        kb = sum(1 for r in before if not r["has_code"])
        ka = sum(1 for r in after if not r["has_code"])
        print(f"\n  --- {label} ({date}) ---")
        print(f"    before: {pct(kb, len(before))}")
        print(f"    after : {pct(ka, len(after))}")
        results[label] = (kb, len(before), ka, len(after))
        if len(before) and len(after):
            try:
                from scipy.stats import fisher_exact, chi2_contingency
                table = [[kb, len(before) - kb], [ka, len(after) - ka]]
                orr, p = fisher_exact(table)
                chi2, p2, _, _ = chi2_contingency(table, correction=True)
                print(f"    Fisher exact OR={orr:.4f}  p={p:.6e}   "
                      f"chi-square (Yates) p={p2:.6e}")
                if p < 0.05 and kb/len(before) > ka/len(after):
                    print(f"    -> CONCENTRATED BEFORE this milestone (his direction)")
                elif p < 0.05:
                    print(f"    -> concentrated AFTER this milestone (AGAINST his direction)")
                else:
                    print(f"    -> NO significant difference across this milestone")
            except Exception as exc:
                print(f"    (scipy unavailable: {exc!r})")

    # ── PER-YEAR-MONTH, so the shape is visible rather than inferred ──
    print(f"\n=== BY MONTH, so the shape is visible ===")
    bym = defaultdict(lambda: [0, 0])
    for r in dated:
        k = r["date"][:7]
        bym[k][1] += 1
        if not r["has_code"]:
            bym[k][0] += 1
    print(f"  {'month':9s} {'no-falsifier / total':28s} share")
    for m in sorted(bym):
        k, n = bym[m]
        print(f"  {m:9s} {k:6d} / {n:<6d}{'':12s} {k/n*100:7.4f}%   {'#'*int(k/n*40)}")

    if args.json:
        print(json.dumps({"milestones": results,
                          "by_month": {m: bym[m] for m in sorted(bym)},
                          "reproduced_headline": ok}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
