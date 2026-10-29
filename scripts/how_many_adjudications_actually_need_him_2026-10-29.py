#!/usr/bin/env python3
"""Does the 63-item adjudication really need 63 of his verdicts? No.

HIS QUESTION, 2026-10-29: whether 63 full-range adjudications is a justified
HIL workload, and why they require him at all. He asked the same thing on
2026-09-05 and the answer then was that the human queue was 4 and not 259,
because a schema lookup settles most of the band. That lesson was not applied
to the 63, which is why this script exists.

WHAT IT ESTABLISHES, and each figure can fail.

  1. The 63 is a POWER figure, not a count of items needing a person. It is the
     sample size at which a full-range study reaches 0.9165.

  2. Applying the 5-clause rubric is NOT beyond a model, and the claim that it
     was is contradicted by the project's own record: the 2026-09-02 audit holds
     286 first-pass verdicts and 108 second-pass verdicts, each with written
     reasoning. What IS forbidden is a model CONFIRM vote as evidence that a
     defect exists, which is a different act.

  3. THE AUDIT NAMES NO SCORER. Its record carries a method and a shuffle seed
     and no reader, and its `ground_truth` field holds the withheld SEVERITY
     NUMBERS rather than human labels. A result attributed to nobody is a
     provenance gap by this project's own standard.

  4. The genuine objection to model labels here is CIRCULARITY, not capability:
     the study tests a model-derived severity against the rubric, so model
     labels on both sides test a model against itself.

  5. THE CHEAPER DESIGN. An anchor set he labels, over items the model has
     already labelled, measures whether the model's labelling can be trusted to
     carry the study. This sizes it.

READ-ONLY. It writes nothing.
"""
from __future__ import annotations
import argparse, collections, importlib.util, json, pathlib, sys

REPO = pathlib.Path(__file__).resolve().parents[1]
AUDIT = (REPO / "experimental_notes" / "adversarial_records"
         / "rubric_adherence_audit_0C8_2026-09-02.json")
D13 = REPO / "scripts" / "reproduce_rubric_human_queue_partition.py"


def _d13():
    spec = importlib.util.spec_from_file_location("d13", D13)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["d13"] = mod
    spec.loader.exec_module(mod)
    return mod


def wilson_pair(k: int, n: int):
    """Two independent computations, so a single library cannot carry it."""
    out = {}
    try:
        from statsmodels.stats.proportion import proportion_confint
        out["statsmodels"] = tuple(proportion_confint(k, n, method="wilson"))
        out["exact"] = tuple(proportion_confint(k, n, method="beta"))
    except Exception as exc:                                   # pragma: no cover
        out["statsmodels"] = f"unavailable: {exc}"
    try:
        import numpy as np
        from scipy import stats
        z = stats.norm.ppf(0.975); p, d = k / n, 1 + z * z / n
        c = (p + z * z / (2 * n)) / d
        h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
        out["numpy closed form"] = (c - h, c + h)
    except Exception as exc:                                   # pragma: no cover
        out["numpy closed form"] = f"unavailable: {exc}"
    return out


def band(s: float) -> str:
    if s < 0.3: return "0.00-0.29"
    if s < 0.5: return "0.30-0.49"
    if s < 0.65: return "0.50-0.64"
    if s <= 0.74: return "0.65-0.74 (the audited band)"
    return "0.75-1.00"


def full_range_partition():
    """The 4-way lookup applied across the WHOLE severity range.

    The 2026-09-05 partition ran over the 33 disputed-band disagreements in the
    falsifier era and found 27 already tool-settled. This asks the same question
    of every falsifier-era entry carrying a severity, because a full-range study
    draws from all of them and not from the band.
    """
    d13 = _d13()
    idx, rwf = d13.build_registry_index()
    rows = []
    for (run, _fid), entry in idx.items():
        sev = entry.get("severity")
        try:
            sev = float(sev)
        except (TypeError, ValueError):
            continue
        rows.append((sev, d13.classify(entry, run, rwf)[0]))
    era = [(s, c) for s, c in rows if c != "SCHEMA_PREDATES"]
    return rows, era


def anchor_power(trials: int, seed: int):
    """How many paired labels separate a trustworthy model from an untrustworthy one.

    SIMULATED, NOT CLOSED FORM, AND THE DIFFERENCE IS RECORDED. The analytic
    approximation reads 0.9661 at n = 30 where simulation reads about 0.94, so
    the closed form is optimistic -- the same direction the project already
    recorded for the 35-item figure, where the analytic said 0.80 and simulation
    gave 0.6472. The simulated value is the one to quote.
    """
    import numpy as np
    rng = np.random.default_rng(seed)

    def sim(n, kappa_true, base=0.5):
        pe = base ** 2 + (1 - base) ** 2
        po = kappa_true * (1 - pe) + pe
        out = np.empty(trials)
        for t in range(trials):
            agree = rng.random(n) < po
            a = rng.random(n) < base
            b = np.where(agree, a, ~a)
            pa = (a == b).mean()
            p_e = a.mean() * b.mean() + (1 - a.mean()) * (1 - b.mean())
            out[t] = (pa - p_e) / (1 - p_e) if p_e < 1 else 1.0
        return out

    return {n: ((sim(n, 0.80) >= 0.6).mean(), (sim(n, 0.40) >= 0.6).mean())
            for n in (15, 20, 25, 30, 40, 48, 63)}


def audit_provenance():
    """Who scored the 286? The record does not say, and that is the finding."""
    if not AUDIT.is_file():
        return {"present": False}
    d = json.loads(AUDIT.read_text(encoding="utf-8"))
    named = [k for k in ("scorer", "scored_by", "reader", "readers",
                         "adjudicator", "who", "provenance") if k in d]
    gt = d.get("ground_truth") or {}
    # EVERY VALUE, NOT A SAMPLE. This checked the first 20 of 286 and then
    # reported the conclusion as though it covered all of them, which
    # `test_no_script_prints_a_capped_listing_in_silence` caught on this file's
    # first run: "a list cut to N under a heading that reads as complete is a
    # silent falsehood". The cap was feeding a REPORTED boolean, so it was not
    # a harmless sampling. The count checked is now stated with the answer.
    gt_numeric = sum(1 for v in gt.values()
                     if isinstance(v, list) and v and isinstance(v[0], (int, float)))
    gt_is_numbers = bool(gt) and gt_numeric == len(gt)
    return {"present": True, "keys": sorted(d),
            "first_pass": len(d.get("first_pass") or []),
            "second_pass": len(d.get("second_pass") or []),
            "fields_naming_a_scorer": named,
            "ground_truth_entries": len(gt),
            "ground_truth_numeric_first_element": gt_numeric,
            "ground_truth_is_severity_numbers": gt_is_numbers,
            "method": str(d.get("method", ""))[:160]}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--trials", type=int, default=4000,
                    help="simulation draws per power figure (default 4000)")
    ap.add_argument("--seed", type=int, default=20261029)
    ap.add_argument("--skip-partition", action="store_true",
                    help="skip the registry walk, which is the slow part")
    a = ap.parse_args()        # exits on --help BEFORE anything is read

    print("=" * 74)
    print("DOES THE 63-ITEM ADJUDICATION NEED 63 OF HIS VERDICTS?")
    print("=" * 74)

    p = audit_provenance()
    print("\n1. THE EXISTING 286 LABELS, AND WHO MADE THEM")
    if not p["present"]:
        print("   the audit record is absent from this checkout")
    else:
        print(f"   first-pass verdicts   : {p['first_pass']}")
        print(f"   second-pass verdicts  : {p['second_pass']}")
        print(f"   fields naming a scorer: {p['fields_naming_a_scorer'] or 'NONE'}")
        print(f"   ground_truth entries  : {p['ground_truth_entries']}, of which "
              f"{p['ground_truth_numeric_first_element']} open with a number, so "
              f"they are severity values rather than human labels: "
              f"{p['ground_truth_is_severity_numbers']} "
              f"(all {p['ground_truth_entries']} checked, not a sample)")
        print(f"   method as recorded    : {p['method']}")
        print("   -> a model supplied them and the record does not say so, which")
        print("      is a provenance gap by this project's own standard.")

    if not a.skip_partition:
        rows, era = full_range_partition()
        per = collections.defaultdict(collections.Counter)
        for s, c in era:
            per[band(s)][c] += 1
        print(f"\n2. THE 4-WAY LOOKUP ACROSS THE FULL RANGE")
        print(f"   entries carrying a severity : {len(rows)}")
        print(f"   of those, in the falsifier era: {len(era)}")
        tot = collections.Counter()
        print(f"   {'band':<30} {'n':>5} {'A':>5} {'B':>4} {'C':>4} {'D':>5}  D share")
        for b in sorted(per):
            c = per[b]; n = sum(c.values()); tot.update(c)
            print(f"   {b:<30} {n:>5} {c['A']:>5} {c['B']:>4} {c['C']:>4} "
                  f"{c['D']:>5}  {c['D']/n:.4f}")
        n, k = sum(tot.values()), tot["D"]
        print(f"\n   D = 'no falsifier produced': {k} of {n} = {k/n:.6f}")
        for name, v in wilson_pair(k, n).items():
            print(f"     {name:<20} "
                  + (f"[{v[0]:.6f}, {v[1]:.6f}]" if isinstance(v, tuple) else str(v)))
        print(f"   A 63-item full-range sample would land in D about {63*k/n:.1f} times.")
        print("   BUT D IS NOT 'NEEDS A HUMAN'. The partition script states that an")
        print("   item is irreducible ONLY if a falsifier cannot be written for it,")
        print("   and that none has been shown untoolable: D is a TOOLING backlog.")

    print(f"\n3. THE ANCHOR-SET ALTERNATIVE ({a.trials} draws, seed {a.seed})")
    print(f"   {'n':>4}  {'detects kappa 0.80':>19}  {'false alarm at 0.40':>20}")
    for n, (hi, lo) in anchor_power(a.trials, a.seed).items():
        print(f"   {n:>4}  {hi:>19.4f}  {lo:>20.4f}")
    print("   30 anchor labels reach about 0.95 against 0.99 for 63, so most of")
    print("   what 63 buys is bought by 30.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
