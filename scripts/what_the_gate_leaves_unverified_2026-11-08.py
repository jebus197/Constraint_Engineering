"""Which DONE claims rest on verification the commit gate never runs.

WHY THIS IS A DIFFERENT QUESTION FROM B103's. B103 asks what it would cost to
gate the guards written since 2026-10-29 -- 83 files, chosen by DATE. This asks
what the gate's absence actually leaves unverified, which is chosen by what a
completion claim RESTS ON. The 2 sets barely overlap: 26 of the 154 files the
unsupported DONE claims name are among the 83, so a decision bounded by the
date cut addresses about a sixth of the exposure it is reasoning about.

MEASURED 2026-11-08. 225 DONE entries name at least 1 file under `bench/tests`.
71 have every named test ON the gate, 135 have none of them on it, and 19 are
mixed; the partition closes at 225. So 135 of 225, 0.600000, are completion
claims whose only named verification does not execute at commit time.

WHY THAT IS WORSE THAN AN UNRUN GUARD. A guard nobody runs is a guard. A DONE
marker is a CLAIM, and its evidence field is what the claim rests on. The
project's own `unsupported_done_entries` exists because the DONE-evidence guard
checked that a named test exists, asserts and is collected -- and never that it
PASSES. The 2026-11-04 full board found 44 failures the gate showed 0 of, and
reported 24 DONE entries whose named evidence was failing, which that commit
message calls "a larger fact than the 44". This script measures the standing
exposure that produces such findings, rather than the findings themselves.

COSTS ARE REPORTED ONLY WHERE MEASURED. Durations are not re-derived here: the
cost of gating any subset depends on running it, and this script will not
project from a per-test rate for the reason the project already records -- the
unreached set runs slower per test, and a count-based extrapolation once stood
in for a factor of 18.05. Where a file's cost was measured on 2026-11-08 it is
reported; where it was not, the script says so and sums a FLOOR.
"""
from __future__ import annotations

import pathlib
import re
import sys

import mpmath as mp
from scipy.stats import beta as _beta
from statsmodels.stats.proportion import proportion_confint

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

mp.mp.dps = 40
_Z = mp.mpf("1.959963984540054235524594430520551527955")

#: Attributed seconds measured on 2026-11-08, from a single 211-file run with
#: `--durations=0`, for every file that is BOTH outside the gate AND named by
#: an unsupported DONE claim. Only files reported above pytest's 5 ms floor
#: appear, so the sum is a FLOOR and the rest cost under 5 ms each.
#:
#: ★ THIS TABLE HELD 9 ENTRIES ON ITS FIRST RUN AND 7 OF THEM WERE IN THE
#: SUPPORT SET, so the floor printed as 401.30 s against a measured 441.46 s --
#: understated by 40.16 s because the table carried the 9 SLOWEST files overall
#: rather than every measured file this question needs. A recorded dataset must
#: be complete for the question it answers, not for the question it was copied
#: from; a truncated table makes a floor look like a smaller floor.
MEASURED_2026_11_08 = {
    "bench/tests/test_an_interval_rests_on_two_routes_2026-11-03.py": 174.96,
    "bench/tests/test_raising_an_entry_reaches_every_surface_2026-11-02.py": 57.48,
    "bench/tests/test_tonights_producers_are_reached_2026-11-03.py": 45.92,
    "bench/tests/test_todays_producers_are_reached_2026-11-02.py": 33.27,
    "bench/tests/test_the_two_decision_surfaces_cannot_diverge_2026-11-01.py": 32.09,
    "bench/tests/test_his_annotations_arrive_with_their_context_2026-11-06.py": 29.18,
    "bench/tests/test_what_a_simulated_run_would_test_2026-11-03.py": 28.4,
    "bench/tests/test_what_a_mypy_config_would_reveal_2026-11-04.py": 23.42,
    "bench/tests/test_a_clean_mypy_is_not_an_unchecked_one_2026-11-02.py": 3.32,
    "bench/tests/test_the_weighted_risk_is_not_a_probability_2026-11-04.py": 2.95,
    "bench/tests/test_a_markdown_heading_is_not_his_annotation_2026-11-02.py": 2.85,
    "bench/tests/test_the_fix_comparator_refuses_to_rank_2026-11-02.py": 2.58,
    "bench/tests/test_is_depth_alone_blinkered_2026-11-04.py": 1.25,
    "bench/tests/test_asking_is_not_answering_2026-11-02.py": 1.12,
    "bench/tests/test_the_type_check_task_is_its_own_task_2026-11-01.py": 0.74,
    "bench/tests/test_a_models_word_does_not_close_a_finding_2026-11-03.py": 0.64,
    "bench/tests/test_rule_27_is_enforced_going_forward_2026-10-29.py": 0.55,
    "bench/tests/test_the_template_passes_its_own_validator_2026-11-01.py": 0.33,
    "bench/tests/test_a_bare_clock_is_dated_from_the_header_2026-11-03.py": 0.19,
    "bench/tests/test_the_superlative_has_two_routes_2026-11-03.py": 0.13,
    "bench/tests/test_the_watchdog_events_reach_the_pulse_2026-11-03.py": 0.05,
    "bench/tests/test_a_seat_declares_what_it_is_missing_2026-11-02.py": 0.02,
    "bench/tests/test_the_pause_is_reachable_in_simulation_2026-11-03.py": 0.01,
    "bench/tests/test_the_follow_window_is_per_cycle_2026-11-01.py": 0.01,
}

#: The gate's own measured wall clock and attributed time, 2026-11-08.
GATE_WALL, GATE_ATTRIB = 681.94, 629.21


def _interval(k: int, n: int) -> tuple[float, float, float, float, float]:
    wl, wh = proportion_confint(k, n, 0.05, method="wilson")
    p, N = mp.mpf(k) / n, mp.mpf(n)
    den = 1 + _Z**2 / N
    cen = (p + _Z**2 / (2 * N)) / den
    half = (_Z / den) * mp.sqrt(p * (1 - p) / N + _Z**2 / (4 * N**2))
    cl = 0.0 if k == 0 else float(_beta.ppf(0.025, k, n - k + 1))
    ch = 1.0 if k == n else float(_beta.ppf(0.975, k + 1, n - k))
    dis = max(abs(wl - float(cen - half)), abs(wh - float(cen + half)))
    return wl, wh, cl, ch, dis


def gate_files() -> set[str]:
    hook = (REPO / "hooks" / "pre-commit").read_text(encoding="utf-8")
    m = re.search(r'GUARDS="(.*?)"', hook, re.S)
    if m is None:
        raise SystemExit("could not find the GUARDS list in the hook")
    return {x.strip() for x in m.group(1).split() if x.strip()}


def classify() -> dict:
    import task_list_markers as tlm
    on = gate_files()
    live = {f"bench/tests/{p.name}"
            for p in (REPO / "bench" / "tests").glob("test_*.py")}
    gated = ungated = mixed = 0
    support: set[str] = set()
    for e in tlm.parse_entries():
        if e.state != "DONE" or not e.evidence:
            continue
        tests = [tlm.LINE_REF.sub("", x) for x in e.evidence
                 if tlm.LINE_REF.sub("", x).startswith("bench/tests/")]
        if not tests:
            continue
        has_on = any(t in on for t in tests)
        has_off = any(t not in on for t in tests)
        if has_on and not has_off:
            gated += 1
        elif has_off and not has_on:
            ungated += 1
            support |= {t for t in tests if t in live}
        else:
            mixed += 1
    return {"on_gate": on, "gated": gated, "ungated": ungated, "mixed": mixed,
            "support": sorted(support), "live": live}


def main() -> int:
    c = classify()
    tot = c["gated"] + c["ungated"] + c["mixed"]
    print("1. DONE CLAIMS AND WHERE THEIR VERIFICATION RUNS")
    print(f"   DONE entries naming a bench/tests file : {tot}")
    print(f"     every named test ON the gate         : {c['gated']}")
    print(f"     none of them on the gate             : {c['ungated']}")
    print(f"     mixed                                : {c['mixed']}")
    assert c["gated"] + c["ungated"] + c["mixed"] == tot, \
        "the classification partition does not close"
    print(f"     partition closes at {tot}")
    wl, wh, cl, ch, dis = _interval(c["ungated"], tot)
    print(f"   unverified at commit time: {c['ungated']} of {tot} = "
          f"{c['ungated'] / tot:.6f}")
    print(f"     Wilson [{wl:.6f}, {wh:.6f}]  Clopper-Pearson [{cl:.6f}, {ch:.6f}]")
    print(f"     2-route disagreement {dis:.3e}")
    assert dis < 1e-6, "the interval routes disagree"

    print()
    print("2. WHAT GATING THEM WOULD MEAN, BY SUPPORT RATHER THAN BY DATE")
    sup = c["support"]
    print(f"   distinct files those claims name : {len(sup)}")
    print(f"   already on the gate              : "
          f"{len([f for f in sup if f in c['on_gate']])}  (0 by construction)")
    known = {f: s for f, s in MEASURED_2026_11_08.items() if f in sup}
    floor = sum(known.values())
    print(f"   of those, measured on 2026-11-08 : {len(known)}")
    print(f"   their attributed cost            : {floor:.2f} s")
    print(f"   FLOOR as a share of the gate's {GATE_ATTRIB:.2f} s attributed:"
          f" {floor / GATE_ATTRIB * 100:.1f}%")
    print(f"   UNMEASURED                       : {len(sup) - len(known)} file(s)")
    print("   NO projection is made from a per-test rate: the unreached set runs")
    print("   slower per test, and a count-based extrapolation is how a true 6")
    print("   per cent once stood in for a factor of 18.05. The floor is a floor.")
    return 0


if __name__ == "__main__":
    import pathlib as _pl
    import sys as _sys
    _sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
    from _cli_help import answer_help as _answer_help
    _answer_help(__doc__, __file__, takes_no_arguments=True)
    raise SystemExit(main())
