# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'the_quiet_run_is_not_the_lever_2026-10-25', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 371fb5ea0744d0fd2ffa9bcc6aed1395263a1b93bbeadf2c1c935300eb8b0fbf
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""The required quiet run must be a value the harness can actually reach.

WHY THIS TEST EXISTS. `REQUIRED_QUIET_RUN` was raised from 3 to 7 on 2026-10-17
on the strength of the K=7 row of the table in
`bench/the_false_quiet_rate_is_not_the_gates_rate_2026-10-08.py`, which reads
"0 of 99 -> 0.000000". That row's 0 is a NUMERATOR going to zero because its
CONDITION never fires, not a measured absence of premature closes. Measured
2026-10-25 over the same 63 archived reports by
`bench/the_gate_fires_once_per_run_2026-10-25.py`:

    longest run of consecutive zero-novel-critical rounds observed
    ANYWHERE in the archive                                            6
    reports containing a quiet run of 7 or more                        0
    reports long enough to HOLD a 7-round window                      22
    of those 22, reports that reached a 7-round quiet run              0
    reports shorter than 7 usable rounds                        41 of 63

So at K=7 the quiet arm of the convergence gate did not have a single firing
opportunity in the archive. Clopper-Pearson on 0 of 22 bounds
P(reach a 7-quiet run | run is long enough) at 0.154373, and 22/63 of runs are
long enough, so P(the quiet arm can ever fire at K=7) <= 0.053908 against 30/63
= 0.476190 observed at K=3 -- a factor of 8.8.

That matters because the hardened gate is a CONJUNCTION whose condition (C) is
this quiet run, and the documented small-pool fallback is the count-based
zero-novel-critical criterion ALONE, which reads the same constant. An
unreachable condition (C) therefore removes the convergence path rather than
tightening it, and the founder's standing additive standard permits removing a
feature only on a committed measurement showing a replacement dominates. No
such measurement exists; the gamma arm blocked 0 of 23 premature windows, so
there is no second arm to carry the gate.

WHAT THIS TEST PINS, and what it does NOT. It pins the REACHABILITY CEILING
only: the constant may not exceed the longest quiet run this project has ever
observed. It does not pin 3, so lowering to 2 or raising to 4, 5 or 6 all pass.
Anyone raising it above 6 must first commit an archive measurement showing a
quiet run of that length occurring, which is exactly the evidence that was
missing in October 2026.

HERMETIC BY CONSTRUCTION. `bench/logs` was pruned mid-session on 2026-10-25 and
the recursive glob for `*report*.json` that both producers depend on returned 0
files afterwards, so no test may depend on the archive being present. The
sequence fixtures below are literals and the gate logic under test is pure.
"""
from __future__ import annotations

import importlib.util
import pathlib
import re

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
RUNNER = REPO / "bench" / "reference_runner_v3.py"
PRODUCER = REPO / "bench" / "the_gate_fires_once_per_run_2026-10-25.py"

#: The longest run of consecutive zero-novel-critical rounds observed anywhere
#: in the 63-report archive, measured 2026-10-25. A required quiet run above
#: this has no firing opportunity on any evidence the project holds.
LONGEST_QUIET_RUN_EVER_OBSERVED = 6


def _declared_quiet_run() -> int:
    """Read the constant from source rather than importing the runner.

    `bench/reference_runner_v3.py` is 1.2 MB and importing it for one integer
    would pull in its module-level work. The assignment is a bare literal, so a
    regex is sufficient and cannot be confused by a later reassignment: the
    test asserts exactly one top-level assignment exists.
    """
    src = RUNNER.read_text()
    hits = re.findall(r"^REQUIRED_QUIET_RUN\s*=\s*(\d+)\s*$", src, re.M)
    assert len(hits) == 1, (
        f"expected exactly 1 top-level REQUIRED_QUIET_RUN assignment, "
        f"found {len(hits)}: {hits}")
    return int(hits[0])


def test_required_quiet_run_is_within_the_reachable_range():
    """RED at 7, GREEN at 3 -- and at any value the archive has ever reached."""
    k = _declared_quiet_run()
    assert k >= 2, f"a quiet run of {k} is not a run"
    assert k <= LONGEST_QUIET_RUN_EVER_OBSERVED, (
        f"REQUIRED_QUIET_RUN = {k} exceeds {LONGEST_QUIET_RUN_EVER_OBSERVED}, "
        f"the longest consecutive zero-novel-critical run ever observed in the "
        f"63-report archive. The quiet arm of the convergence gate would have "
        f"had 0 firing opportunities on that evidence, so the value removes the "
        f"convergence path rather than tightening it. Raising it above "
        f"{LONGEST_QUIET_RUN_EVER_OBSERVED} requires a committed measurement "
        f"showing a quiet run of that length actually occurring.")


def test_the_gamma_alt_default_tracks_the_same_constant():
    """The dataclass default must not drift away from the module constant.

    Both arms read `REQUIRED_QUIET_RUN`: the legacy arm via
    `gamma_alt_consecutive_zero_crit` and condition (C) of the hardened
    conjunction. If someone lowers the constant but hard-codes the field, the
    revert is inert -- which is this project's commonest defect class, 11
    confirmed additions that nothing reached since 2026-08-01.
    """
    src = RUNNER.read_text()
    assert re.search(
        r"gamma_alt_consecutive_zero_crit\s*:\s*int\s*=\s*REQUIRED_QUIET_RUN",
        src), ("gamma_alt_consecutive_zero_crit no longer defaults to "
               "REQUIRED_QUIET_RUN, so changing the constant would not reach "
               "the legacy quiet arm")


# --------------------------------------------------------------------------- #
# The mechanism, not just the number: a quiet run of K cannot fire on a
# sequence whose longest quiet stretch is under K. Shown on literal fixtures so
# the claim is executed rather than asserted.
# --------------------------------------------------------------------------- #
def _load_producer():
    spec = importlib.util.spec_from_file_location("gate_fires_once", PRODUCER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _recs(novel_per_round):
    """Collector-shaped records: (round, n_responded, n_raising, gamma)."""
    return [(i, 6, h, 0.4) for i, h in enumerate(novel_per_round)]


# (sequence of novel-critical seat counts per round, longest quiet stretch)
SEQUENCES = [
    ([2, 1, 0, 0, 0, 0, 0, 0], 6),      # the archive's own maximum
    ([3, 0, 0, 0, 1, 0, 0, 0], 3),      # a burst after a 3-round lull
    ([1, 0, 0, 0, 0, 0], 5),
    ([0, 0, 0, 2, 0, 0, 0], 3),
]


@pytest.mark.parametrize("seq,longest", SEQUENCES)
def test_a_quiet_run_longer_than_the_data_cannot_fire(seq, longest):
    mod = _load_producer()
    assert mod.max_quiet_run(_recs(seq)) == longest
    for k in range(longest + 1, longest + 4):
        i, _ = mod.first_fire(_recs(seq), k, earliest=0)
        assert i is None, (
            f"a required quiet run of {k} fired on a sequence whose longest "
            f"quiet stretch is {longest}; the gate cannot be satisfied here")


def test_the_quiet_arm_still_fires_at_the_reverted_value():
    """A revert must RESTORE a capability, not merely lower a number.

    Each fixture above contains a quiet stretch of at least 3, so the arm fires
    on every one at K=3. This is the capability K=7 removes.
    """
    mod = _load_producer()
    for seq, _ in SEQUENCES:
        i, _ = mod.first_fire(_recs(seq), 3, earliest=0)
        assert i is not None, f"K=3 failed to fire on {seq}"


def test_a_lull_before_a_burst_is_what_any_count_based_rule_gets_wrong():
    """The premature close a longer K is meant to prevent, and does not.

    `[3, 0, 0, 0, 1, 0, 0, 0, 0]` has a 3-round lull at rounds 1-3 followed by a
    further critical at round 4. K=3 fires at round 3 and IS premature. K=4
    cannot fire until round 8 and is not premature on this sequence -- which is
    the whole intuition behind raising the constant, and it is correct here.

    THE SAME FIXTURE SHOWS THE COST, which is why the shorter form of it is kept
    too. `[3, 0, 0, 0, 1, 0, 0, 0]` -- one round shorter -- has no quiet stretch
    of 4 anywhere, so K=4 NEVER FIRES on it and the run cannot close at all.
    Avoiding one premature close and removing every close are the same operation
    at different run lengths, which is the mechanism by which K=7 reached 0
    firing opportunities in 63 reports.

    AND THE INTUITION DOES NOT SURVIVE AGGREGATION. Measured first-firing
    premature rates RISE with K: 8/30 = 0.266667 at K=3 against 3/5 = 0.600000
    at K=5, because a longer window only ever fires inside a run that is already
    long and still producing findings late, which selects for runs with findings
    left. This test pins the per-sequence mechanism; the aggregate direction is
    in `bench/the_gate_fires_once_per_run_2026-10-25.py`.
    """
    mod = _load_producer()
    short = _recs([3, 0, 0, 0, 1, 0, 0, 0])
    assert mod.first_fire(short, 3, earliest=0) == (3, True)
    assert mod.first_fire(short, 4, earliest=0) == (None, None), (
        "K=4 fired on a sequence with no 4-round quiet stretch")

    long_ = _recs([3, 0, 0, 0, 1, 0, 0, 0, 0])
    assert mod.first_fire(long_, 3, earliest=0) == (3, True)
    assert mod.first_fire(long_, 4, earliest=0) == (8, False)
