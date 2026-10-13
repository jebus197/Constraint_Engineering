# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'his_rulings_2026-10-13', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 49169770e828db170f6d26eb77916a7861045dd10dc83abd148de7dfa4415ece
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""study_run1b's irreducible queue is 0, not 2. The ITEM 3 premise fails.

FREE PANEL, 2026-10-13, ITEMS 2 and 3. Executed against the live predicate and
the archived registry, not read off a comment.

THE CLAIM UNDER TEST, from the 2026-10-13 brief and from the paragraph that
stood at bench/reference_runner_v3.py:3427-3434: "Measured on
study_run1b_2026-10-03, the 2 never-read survivors put the queue at exactly 2",
therefore the alarm's strict `>` against max_irreducible_queue = 2 is what keeps
it silent, therefore a smaller bound would make it fire.

MEASURED: the queue is ZERO. `_irreducible_queue_split` returns (0, 0) on that
registry. The alarm does not fire at a bound of 2, nor 1, nor 0, because
`count > bound` is False for every non-negative bound when count is 0. So the
brief's ITEM 3 fix -- a per-class bound of 1 for never-read findings -- fires on
0 of the entries in the only run it cites. It is an addition nothing reaches,
which is the failure mode this project has recorded 11 times since 2026-08-01.

WHY THE QUEUE IS EMPTY, and this is the root cause for ITEM 2 as well. The
never-read arm (reference_runner_v3.py:2603-2606) opens with
`bool(e.get("routing_history"))`. The 3 non-terminal entries carry
routing_history None. They were never ROUTED AT ALL, so:

  * routing_deferred was never set      -> the deferred arm does not admit them
  * routing_history is empty            -> the never-read arm does not admit them
  * severity 0.45 / 0.45 / 0.50 < 0.7   -> the severity skip excludes them

Three independent exclusions, any one sufficient. `_never_read` does not mean
"nothing read it"; it means "it was routed and every rung declined". A finding
that never reached a rung has no name in this machinery and no path into either
the count or the evidence bundle.

THE ASYMMETRY, WHICH IS THE ACTUAL DEFECT. The same entries DO block
convergence: `unverified_critical_count()` returns 2 on the same registry, via a
different predicate with a different severity rule (:3476-3477, which releases a
sub-critical only when its severity is PROVEN; both carry severity_proof.status
SKIP). So the run was refused convergence by findings the halt machinery could
not see, and exited at max_rounds with stop_reason UNRECORDED_STOP. That is
neither honest convergence nor an honest halt; it is the third state, silence.

WHAT THIS MEANS FOR THE BRIEF'S TWO ITEMS. ITEM 2's horns are both real, but
neither is the live case: no ladder was ever consulted on this registry, so
"should an empty ladder excuse a sub-critical" does not arise and answering it
leaves the blockage in place. ITEM 3's bound is not the binding constraint; it
is evaluated against a count the findings never enter, so lowering it is free
and useless.

THE SIMPLEST SUFFICIENT REPAIR IS NEITHER A NEW BOUND NOR A NEW EXCUSAL DOOR.
It is to require the 2 predicates to agree on their population: every entry
`unverified_critical_count` treats as a blocker must be visible to
`build_irreducible_queue_alarm`'s evidence bundle. Any entry that can refuse
convergence and cannot reach a halt path is, by construction, a silent
max_rounds exit. That is a conservation property, it is one assertion, it adds
no configuration, and it cannot be used to make convergence easier -- it can
only convert a silent exit into a named one. Pinned by
bench/tests/test_a_blocker_must_be_able_to_reach_a_halt_2026-10-13.py.

Usage: python3 scripts/the_queue_is_zero_not_two_2026-10-13.py
"""
import json
import os
import pathlib
import sys
import types

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _cli_help import answer_help  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[1]
RUN = REPO / "bench" / "logs" / "study_run1b_2026-10-03_20261003T100439Z"
STATE = RUN / "runner_state.json"
REPORT = RUN / "study_run1b_2026-10-03_report.json"
TERMINAL = {"MERGED", "CLOSED", "REFUTED", "DUPLICATE", "CONFIRMED"}


def main() -> int:
    answer_help(__doc__, __file__)
    if not STATE.exists():
        print(f"registry absent in this clone: {STATE}")
        return 3

    sys.path.insert(0, str(REPO))
    sys.path.insert(0, str(REPO / "bench"))
    import importlib
    rr = importlib.import_module("bench.reference_runner_v3")

    entries = json.loads(STATE.read_text())["registry"]["entries"]
    reg = rr.FindingRegistry()
    reg.entries = entries

    print("=" * 78)
    print("THE COUNT, FROM THE LIVE PREDICATE")
    print("=" * 78)
    locked, deferred = rr._irreducible_queue_split(entries)
    total = locked + deferred
    print(f"\n  registry entries           : {len(entries)}")
    print(f"  _irreducible_queue_split   : (locked={locked}, deferred={deferred})")
    print(f"  irreducible_queue_count()  : {reg.irreducible_queue_count()}")
    print(f"\n  THE BRIEF SAYS : 2")
    print(f"  MEASURED       : {total}")
    print(f"  agreement      : {total == 2}")
    print("\n  does the alarm fire, at each candidate bound? (rule is count > bound)")
    for bound in (0, 1, 2, 3):
        print(f"    bound={bound}  ->  {total} > {bound}  =  {total > bound}")
    print("\n  So the per-class bound proposed for ITEM 3 fires on 0 of these entries.")

    print()
    print("=" * 78)
    print("WHY: THE THREE INDEPENDENT EXCLUSIONS")
    print("=" * 78)
    nonterm = [(c, e) for c, e in entries.items() if e.get("status") not in TERMINAL]
    print(f"\n  non-terminal entries: {len(nonterm)}")
    for c, e in nonterm:
        sev = e.get("severity") or 0.0
        print(f"\n    {c}  status={e.get('status')}  severity={sev}")
        print(f"      routing_history        = {e.get('routing_history')!r}"
              f"   never-read arm admits: {bool(e.get('routing_history'))}")
        print(f"      routing_deferred       = {e.get('routing_deferred')!r}"
              f"   deferred arm admits: {bool(e.get('routing_deferred'))}")
        print(f"      irreducible_escalation = {e.get('irreducible_escalation')!r}"
              f"   locked arm admits: {bool(e.get('irreducible_escalation'))}")
        print(f"      severity >= {rr.CRITICAL_SEVERITY_THRESHOLD} ?"
              f"              severity skip passes: "
              f"{sev >= rr.CRITICAL_SEVERITY_THRESHOLD}")

    print()
    print("=" * 78)
    print("THE ASYMMETRY -- BLOCKS CONVERGENCE, INVISIBLE TO THE HALT PATH")
    print("=" * 78)
    blockers = reg.unverified_critical_count()
    cfg = types.SimpleNamespace(max_irreducible_queue=2)
    alarm = rr.build_irreducible_queue_alarm(reg, cfg, 8)
    print(f"\n  unverified_critical_count()  (REFUSES convergence) : {blockers}")
    print(f"  irreducible_queue_count()    (reaches the alarm)   : {total}")
    print(f"  build_irreducible_queue_alarm(...)                 : {alarm}")
    print(f"\n  can refuse convergence but cannot reach a halt path: "
          f"{max(blockers - total, 0)}")
    if REPORT.exists():
        rep = json.loads(REPORT.read_text())
        print(f"\n  rounds {rep.get('total_rounds')}/{rep.get('max_rounds')}"
              f"  converged={rep.get('converged')}  halted={rep.get('halted')}")
        print(f"  stop_reason: {str(rep.get('stop_reason'))[:100]}")

    print()
    print("=" * 78)
    print("THE CONSERVATION PROPERTY THE REPAIR SHOULD ESTABLISH")
    print("=" * 78)
    print("""
  Over any registry:

      blockers(reg) > 0  =>  the run can reach a NAMED terminal state
                             (converged, or halted with an evidence bundle)

  Today that implication is false and the counterexample is archived. No new
  bound and no new excusal door is required: it is an agreement condition
  between 2 predicates that already exist, which is why it is the simplest
  sufficient repair and why it cannot make convergence easier.
""")
    return 0


if __name__ == "__main__":
    sys.exit(main())
