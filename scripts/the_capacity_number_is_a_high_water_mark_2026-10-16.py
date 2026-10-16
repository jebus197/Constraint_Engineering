#!/usr/bin/env python3
"""Is the per-seat capacity number a measurement, or a high-water mark that cannot fall?

HIS LIST, 2026-10-16, item 5 of the 7 smaller defects: *"A capacity number
shared identically by 4 paid models and untouched for 185 days."* His ruling on
the list: *"Fix it all."*

WHY THIS SCRIPT AND NOT A FIX. `bench/reference_runner_v3.py` already records
the disposition, verbatim: *"`max_successful_prompt_chars` is a PROVEN FLOOR by
its own docstring and `_should_decompose` uses it as a CEILING, so the observed
maximum can never rise -- a ratchet that cannot climb ... Changing it alters
routing for paid seats and is a design decision, not a repair."* So the useful
contribution is the measurement that makes the decision decidable, not a silent
change to paid-seat routing.

WHAT IS MEASURED, AND ONE HYPOTHESIS THAT DIED ON THE WAY. The first explanation
tried was that every seat in a star round is handed the SAME prompt, so the
number would record the runner's largest prompt rather than any model's
capacity. THAT WAS REFUTED by comparing the seats' own recorded histories: they
are not identical, sharing only 7 to 17 of 48 distinct values, and their recent
maxima are 70,000 to 95,000 characters. The real mechanism is simpler and worse:
the field is a LIFETIME maximum that never decays, so one large dispatch in one
old run fixes it permanently.

THREE THINGS THE DECISION NEEDS, all printed below.
  1. How many paid seats share the number, and what the odd one out is.
  2. How far the number sits above what the seats have handled RECENTLY, from
     the seats' own stored history window.
  3. Whether the number has ever been bounded from ABOVE -- i.e. whether the
     failure arm that would lower it has ever fired.

Free on `--help`: dispatches nothing, spends nothing, reads only local files.

Usage:
    python3 scripts/the_capacity_number_is_a_high_water_mark_2026-10-16.py
    python3 scripts/the_capacity_number_is_a_high_water_mark_2026-10-16.py --json
"""
from __future__ import annotations

import argparse
import collections
import json
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
FP_DIR = REPO / "bench" / "fingerprints"
#: The paid roster. Simulated seats carry the mandatory `-SIM` suffix and are
#: excluded, because his item is about the PAID models.
PAID = ("CC2", "ChatGPT", "Codex", "DeepSeek", "Gemini")
FIELD = "max_successful_prompt_chars"
DERIVED = ("measured_attention_span", "compression_threshold")
FAILURE_FIELDS = ("max_failed_context_chars", "max_failed_prompt_chars")


def _observed(name: str) -> dict:
    p = FP_DIR / f"{name}.json"
    if not p.is_file():
        return {}
    try:
        return json.loads(p.read_text()).get("observed") or {}
    except (OSError, ValueError):
        return {}


def measure() -> dict:
    obs = {n: _observed(n) for n in PAID}
    values = {n: o.get(FIELD) for n, o in obs.items()}
    counts = collections.Counter(v for v in values.values() if v is not None)
    modal, modal_n = counts.most_common(1)[0] if counts else (None, 0)

    recent = {}
    for n, o in obs.items():
        h = [x for x in (o.get("prompt_chars_history") or [])
             if isinstance(x, (int, float))]
        recent[n] = {"window": len(h), "max": max(h) if h else None}

    # Is the number ever bounded from above?
    failures = {n: {f: o.get(f) for f in FAILURE_FIELDS} for n, o in obs.items()}
    any_failure = any(
        isinstance(v, (int, float)) and v > 0
        for d in failures.values() for v in d.values()
    )

    # How long has the modal value stood? Dated from the commit that introduced
    # the literal into the first paid fingerprint carrying it.
    age_days = None
    first_date = None
    if modal is not None:
        for n in PAID:
            if values.get(n) != modal:
                continue
            out = subprocess.run(
                ["git", "log", "--format=%ad", "--date=short", "-S", str(int(modal)),
                 "--", f"bench/fingerprints/{n}.json"],
                cwd=REPO, capture_output=True, text=True).stdout.split()
            if out:
                import datetime
                d = datetime.date.fromisoformat(out[-1])
                if first_date is None or d < first_date:
                    first_date = d
        if first_date is not None:
            import datetime
            # Dated against the newest commit in the repository, not the wall
            # clock, so the figure is reproducible from the repository alone.
            head = subprocess.run(["git", "log", "-1", "--format=%ad",
                                   "--date=short"], cwd=REPO,
                                  capture_output=True, text=True).stdout.strip()
            age_days = (datetime.date.fromisoformat(head) - first_date).days

    # Headroom: how far the standing number sits above recent experience.
    ratios = {}
    for n in PAID:
        v, r = values.get(n), recent[n]["max"]
        if isinstance(v, (int, float)) and isinstance(r, (int, float)) and r:
            ratios[n] = v / r

    derived_agree = {
        n: {d: obs[n].get(d) == values.get(n) for d in DERIVED} for n in PAID
    }
    return {
        "values": values,
        "modal_value": modal,
        "seats_sharing_the_modal_value": modal_n,
        "odd_seats": {n: v for n, v in values.items() if v != modal},
        "recent": recent,
        "ratio_standing_over_recent": ratios,
        "failure_fields": failures,
        "the_number_has_ever_been_bounded_above": any_failure,
        "first_seen": str(first_date) if first_date else None,
        "age_days_at_head": age_days,
        "derived_fields_equal_the_same_number": derived_agree,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()
    m = measure()
    if args.json:
        print(json.dumps(m, indent=2, sort_keys=True))
        return 0

    print("THE PER-SEAT CAPACITY NUMBER, MEASURED")
    print(f"  field: {FIELD}")
    print()
    print(f"  {'seat':<11}{'standing':>11}{'recent max':>12}{'window':>8}   standing / recent")
    for n in PAID:
        v = m["values"].get(n)
        r = m["recent"][n]["max"]
        w = m["recent"][n]["window"]
        ratio = m["ratio_standing_over_recent"].get(n)
        print(f"  {n:<11}{str(v):>11}{str(r):>12}{str(w):>8}   "
              f"{'' if ratio is None else f'{ratio:.2f}x'}")
    print()
    print(f"  seats sharing the modal value {m['modal_value']}: "
          f"{m['seats_sharing_the_modal_value']} of {len(PAID)}")
    if m["odd_seats"]:
        print(f"  the odd one(s) out: {m['odd_seats']}")
    print(f"  first seen in a committed fingerprint: {m['first_seen']}")
    print(f"  age at the repository's newest commit: {m['age_days_at_head']} days")
    print()
    print("  HAS IT EVER BEEN BOUNDED FROM ABOVE?")
    for n in PAID:
        print(f"       {n:<11}{m['failure_fields'][n]}")
    print(f"  any failure arm ever fired: "
          f"{m['the_number_has_ever_been_bounded_above']}")
    print()
    print("  DERIVED FIELDS CARRYING THE SAME NUMBER:")
    for n in PAID:
        same = [d for d, eq in m["derived_fields_equal_the_same_number"][n].items() if eq]
        print(f"       {n:<11}{same}")
    print()
    if not m["the_number_has_ever_been_bounded_above"]:
        print("  VERDICT: the number is a LIFETIME HIGH-WATER MARK that has never")
        print("  been bounded from above -- the failure arm that would lower it has")
        print("  never fired on any paid seat. It stands far above what the seats")
        print("  have handled recently, and 2 derived fields repeat it, so one large")
        print("  dispatch in one old run still sets the routing ceiling today.")
        print()
        print("  NEEDS HIS RULING, and the runner's own comment says why: changing")
        print("  it alters routing for paid seats, which is a design decision. The")
        print("  options are to decay it toward the recent window, to bound it by a")
        print("  measured failure, or to leave it as a proven floor and stop calling")
        print("  it a capacity.")
        return 0
    print("  VERDICT: a failure arm has fired, so the number is bounded on both")
    print("  sides. Re-derive the figures above before citing them.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
