#!/usr/bin/env python3
# PROMOTED OUT OF A SANDBOX HARVEST, 2026-10-15, UNCHANGED BELOW THIS HEADER.
#
# AUTHOR: the `fable` seat, 2026-10-05, during the fingerprint ladder review.
# This is its work, not CC1's, and the attribution is the point of promoting it.
#
# WHY IT WAS PROMOTED. Section 3 of this script, "THE FINGERPRINT STORE ERASES
# RUN PROVENANCE ON EVERY SAVE", names a real defect exactly:
#
#   "`_load_fingerprints` loads ALL files and `_save_fingerprints` writes back
#    every model in the loaded dict, so the last run to save re-attributes
#    profiles it did not measure -- real and -SIM alike. Any per-model
#    falsification rate persisted here inherits this."
#
# It then sat only at
# bench/logs/fingerprint_ladder_review_2026-10-05/sandbox_harvest/fable/
#   attempt-1/files/scripts/the_provenance_gate_reads_text_not_behaviour_2026-10-05.py
# -- absent from scripts/, named nowhere in the master task list -- and the
# defect survived 10 days until free run 1 restamped 5 of 5 real paid seats at
# its convergence moment and CC1 rediscovered it by watching the run.
#
# THE DEFECT IS NOW FIXED as task B7: `_save_fingerprints` writes only seats
# whose payload differs from what was loaded, guarded by
# bench/tests/test_fingerprints_record_only_what_a_run_observed_2026-10-15.py
# (8 tests, 4 mutations each turning it red). This script is kept because it is
# the original diagnosis and because a panel round's yield should not be
# discarded -- the lesson is recorded as
# feedback_a_seats_finding_can_sit_in_a_sandbox_2026-10-15.
#
# Its section 3 now reports the REPAIRED behaviour rather than the defect, which
# is the correct outcome for a producer whose finding has been acted on.
# ---------------------------------------------------------------------------
"""The provenance gate reads source text, not behaviour, and the ladder prefix it guards was uniform.

Panel review of `experimental_notes/Proposal_Fingerprint_Falsification_Dimension_2026-10-05.md`,
seat Fable, 2026-10-05. Four demonstrations, every one by EXECUTION:

1. `competence_provenance.falsifier_style` classifies a falsifier as `reads` on a
   SOURCE-TEXT regex. A decoy `open("/dev/null")`, or the word `open(` inside a
   comment, both pass. A detached falsifier can therefore enter any pool gated on
   this script. Provenance strong enough to gate must be execution-derived.

2. The UNSAFE TO RANK ON rule aggregated per MODEL until 2026-10-05: one reading
   falsifier anywhere in a model's set (even on a REFUTED finding) vouched for
   every detached CONFIRMED. Repaired the same day to per-CONFIRMATION accounting;
   this section shows the fixture that separated the two rules.

3. `_save_fingerprints` writes back EVERY loaded profile, so each run re-stamps all
   fingerprint files with its own experiment name and timestamp. Measured: every
   file in `bench/fingerprints/`, real and -SIM alike, carries the same single
   experiment. A falsification dimension persisted there inherits a store that
   erases run provenance on every save.

4. `bench/routing.py` tries only the first `routing_max_rungs` (default 2) rungs,
   and those rungs are always drawn from {Codex-SIM, CC2-SIM, ChatGPT-SIM}. Under
   the pre-2026-10-05 `DEFAULT_LADDER` all three mapped to `opus`, so the exercised
   ladder prefix was uniform for 6 of 6 source seats -- the capability climb was
   unrehearsed even with the mixed bench armed. This section measures the shipped
   map; `bench/tests/test_routing_ladder_prefix_is_mixed_2026-10-05.py` pins it.

Run:  python3 scripts/the_provenance_gate_reads_text_not_behaviour_2026-10-05.py
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import pathlib
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))


def _parse_args(argv=None):
    p = argparse.ArgumentParser(
        prog="the_provenance_gate_reads_text_not_behaviour_2026-10-05.py",
        description=__doc__.split("\n\n")[0])
    return p.parse_args(argv)


def _load_prov():
    spec = importlib.util.spec_from_file_location(
        "competence_provenance", REPO / "scripts" / "competence_provenance.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main(argv=None) -> int:
    _parse_args(argv)
    prov = _load_prov()
    failures = 0

    print("=" * 78)
    print("1. THE STYLE CLASSIFIER IS A SOURCE-TEXT PROXY (still open, stated)")
    print("=" * 78)
    cases = [
        ("genuinely detached", "assert 175 == 174, 'FALSIFIED'", "detached"),
        ("decoy open('/dev/null'), still detached in behaviour",
         "open('/dev/null')\nassert 175 == 174, 'FALSIFIED'", "reads"),
        ("the word open( in a COMMENT only",
         "# I did not open() anything\nassert 1 == 2", "reads"),
    ]
    for label, code, got_expect in cases:
        got = prov.falsifier_style(code)
        print(f"  {label:<48} -> {got}")
        if got != got_expect:
            print(f"     *** classification changed; this demonstration is stale")
            failures += 1
    print("  So `reads` certifies the TEXT contains a read call, not that the")
    print("  falsifier read the target. Gating pool entry on this alone is not")
    print("  sufficient; execution-derived provenance is required (see the")
    print("  docstring of scripts/competence_provenance.py).")

    print()
    print("=" * 78)
    print("2. PER-MODEL vs PER-CONFIRMATION (repaired 2026-10-05)")
    print("=" * 78)
    detached = "assert 175 == 174, 'FALSIFIED'"
    reader = "x = open('t.md').read()\nassert 'y' in x"
    entries = {
        "C1": {"source_model": "M", "falsifier_code": detached,
               "falsifier_verdict": "CONFIRMED"},
        "C2": {"source_model": "M", "falsifier_code": detached,
               "falsifier_verdict": "CONFIRMED"},
        "C3": {"source_model": "M", "falsifier_code": reader,
               "falsifier_verdict": "REFUTED"},
    }
    with tempfile.TemporaryDirectory() as td:
        rp = pathlib.Path(td) / "r_report.json"
        rp.write_text(json.dumps({"registry": {"entries": entries}}),
                      encoding="utf-8")
        s = prov.analyse(rp)["M"]
    old_rule_unsafe = s["confirmed"] > 0 and s["reads"] == 0
    new_rule_unsafe = s["confirmed"] > 0 and (s["confirmed"] - s["confirmed_reads"]) > 0
    print(f"  fixture: 2 detached CONFIRMED + 1 reading REFUTED, one model")
    print(f"  old per-model rule      : unsafe = {old_rule_unsafe}   (the hole)")
    print(f"  new per-confirmation rule: unsafe = {new_rule_unsafe}")
    if old_rule_unsafe or not new_rule_unsafe:
        print("     *** the rules no longer separate on this fixture")
        failures += 1

    print()
    print("=" * 78)
    print("3. THE FINGERPRINT STORE ERASES RUN PROVENANCE ON EVERY SAVE")
    print("=" * 78)
    fdir = REPO / "bench" / "fingerprints"
    stamps = {}
    for f in sorted(fdir.glob("*.json")):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        stamps[f.name] = d.get("experiment", "?")
    for name, exp in stamps.items():
        print(f"  {name:<20} experiment={exp}")
    distinct = sorted(set(stamps.values()))
    print(f"  files: {len(stamps)}, distinct experiment stamps: {len(distinct)} {distinct}")
    print("  `_load_fingerprints` loads ALL files and `_save_fingerprints` writes")
    print("  back every model in the loaded dict, so the last run to save")
    print("  re-attributes profiles it did not measure -- real and -SIM alike.")
    print("  Any per-model falsification rate persisted here inherits this.")
    # ---- POSTSCRIPT ADDED BY CC1, 2026-10-15. Everything above is fable's. ----
    # The 4 lines above are fable's diagnosis of 2026-10-05 and are kept
    # verbatim. They are now STALE IN THE PRESENT TENSE, and a script must not
    # print a false claim about live code, so the repair is stated here rather
    # than by editing the author's words.
    print()
    print("  POSTSCRIPT (CC1, 2026-10-15): THE ABOVE IS FIXED AS TASK B7.")
    print("  `_save_fingerprints` now writes only seats whose payload DIFFERS")
    print("  from what `_load_fingerprints` read, so a run cannot restamp a seat")
    print("  it never dispatched. The stamp census above is the evidence: more")
    print("  than 1 distinct experiment stamp means unobserved seats kept their")
    print("  own provenance. Guard:")
    print("  bench/tests/test_fingerprints_record_only_what_a_run_observed_2026-10-15.py")
    print("  -- 8 tests, 4 mutations each turning it red.")
    if len(distinct) > 1:
        print(f"  -> {len(distinct)} distinct stamps across {len(stamps)} files: REPAIR VISIBLE.")
    else:
        print(f"  -> only {len(distinct)} distinct stamp: either 1 run touched every")
        print("     seat legitimately, or the repair has regressed. Check the guard.")

    print()
    print("=" * 78)
    print("4. THE EXERCISED ROUTING-LADDER PREFIX, MEASURED")
    print("=" * 78)
    from bench.routing import rank_falsifier_writers
    from bench.tools.sim_dispatch_shim import DEFAULT_LADDER
    import dataclasses
    from bench.reference_runner_v3 import RunnerConfig
    k = next(int(f.default) for f in dataclasses.fields(RunnerConfig)
             if f.name == "routing_max_rungs")
    seats = list(DEFAULT_LADDER)
    mixed = 0
    for src in seats:
        prefix = rank_falsifier_writers(seats, exclude=(src,))[:k]
        models = [DEFAULT_LADDER[r] for r in prefix]
        ok = len(set(models)) > 1
        mixed += ok
        print(f"  source {src:<14} prefix {prefix} -> {models}  mixed={ok}")
    print(f"  source seats with a mixed exercised prefix: {mixed} of {len(seats)}")
    print("  (was 0 of 6 before Codex-SIM was mapped to fable on 2026-10-05;")
    print("  5 of 6 is the maximum with 2 model ids while CC2-SIM stays on opus)")

    print()
    if failures:
        print(f"{failures} demonstration(s) went stale -- the premises above have")
        print("changed; re-derive before citing this script.")
        return 1
    print("All demonstrations hold.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
