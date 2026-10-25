# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'the_quiet_run_is_not_the_lever_2026-10-25', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 8f257cd320525504b4e15da7254c09d0a48b2fa4c707a33bd54b79bd86802f7e
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""The required quiet run is 3, and a future raise must re-argue its case here.

PANEL SEAT DELIVERABLE, C12, 2026-10-25. The raise from 3 to 7 (carried out
2026-10-17 under the founder's 2026-10-08 ruling) was justified by the figure
0.126374 from `bench/the_false_quiet_rate_is_not_the_gates_rate_2026-10-08.py`,
which is P(K quiet rounds | criticals demonstrably remained) -- the detector's
false-negative rate -- not P(criticals remained | the gate fired), which is the
quantity a stopping decision needs. Re-measured over the same 63 archived
reports with the gate's actual event semantics (the gate fires ONCE, at the
FIRST K-quiet position, so overlapping windows after it never occur):

    K=3 first-fire premature rate:  8 of 30 = 0.266667
                                    Wilson (0.141827, 0.444480)
                                    [statsmodels + Wolfram Language agree]
    K=5 first-fire:                 3 of 5           (unusably thin)
    K=7 first-fire:                 0 of 0           (UNESTIMABLE: the event
                                                      never occurs in the archive)

and 7 consecutive quiet rounds occur 0 times in 409 usable rounds, including
0 times in the 22 runs long enough to hold such a window. Under the smallest
round cap C13 records (`max_rounds` = 8), K=7 leaves a run that raises any
critical after its first round UNABLE to close on the quiet arm at all, which
is not a stricter gate but a disabled one -- and replacing a working value
without a committed measurement showing the replacement dominates violates the
additive standard. No measurement in the record estimates the premature rate
AT K=7; the "0.000000 at K=7" that justified the raise is a numerator over a
condition that never fires.

THIS FILE IS THE RE-ARGUING POINT. If the quiet run is to move off 3 again,
the committed measurement the additive standard requires is a FIRST-FIRE
premature rate at the proposed K, estimated on data where a K-quiet window can
actually occur, plus a feasibility count under the live round caps. Edit the
pins below only together with that measurement.

PINNED AT SOURCE LEVEL VIA `ast`, NOT BY IMPORT, deliberately: importing
`bench.reference_runner_v3` requires its sibling modules (`hil_review_trigger`,
`runner_mode_detection`), which a staged review tree may not carry, and a pin
that cannot run where it is reviewed protects nothing. The ast pin also checks
something an import cannot: that the config field's DEFAULT is the NAME
`REQUIRED_QUIET_RUN`, not a frozen literal -- the half-derivation that a
mutation check caught on 2026-10-25.
"""
import ast
import pathlib

RUNNER = pathlib.Path(__file__).resolve().parents[1] / "reference_runner_v3.py"

#: The smallest live round cap recorded by C13 on 2026-10-18 (`max_rounds` of
#: 8 or 16 across the configs it enumerated). The feasibility pin below uses
#: the smaller, which is the binding one.
SMALLEST_RECORDED_ROUND_CAP = 8


def _tree():
    return ast.parse(RUNNER.read_text())


def _required_quiet_run(tree):
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for tgt in node.targets:
                if getattr(tgt, "id", None) == "REQUIRED_QUIET_RUN":
                    assert isinstance(node.value, ast.Constant), (
                        "REQUIRED_QUIET_RUN is no longer a literal constant; "
                        "this pin must be rewritten against the new shape")
                    return node.value.value
    raise AssertionError("REQUIRED_QUIET_RUN not found in reference_runner_v3.py")


class TestTheRequiredQuietRunIsThree:
    def test_the_constant_is_three(self):
        k = _required_quiet_run(_tree())
        assert k == 3, (
            f"REQUIRED_QUIET_RUN is {k}, not 3. The raise to 7 rested on a "
            f"conditional rate that answers the wrong question (see this "
            f"file's docstring); raising it again requires a committed "
            f"FIRST-FIRE premature-rate measurement at the proposed value, "
            f"cited beside this pin when it is edited.")

    def test_the_gate_field_reads_the_constant_not_a_frozen_literal(self):
        # `gamma_alt_consecutive_zero_crit` must default to the NAME
        # REQUIRED_QUIET_RUN. A literal here is the half-derivation that lets
        # the constant and the field the gate reads desynchronise silently.
        tree = _tree()
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "RunnerConfig":
                for stmt in node.body:
                    if (isinstance(stmt, ast.AnnAssign)
                            and getattr(stmt.target, "id", None)
                            == "gamma_alt_consecutive_zero_crit"):
                        assert (isinstance(stmt.value, ast.Name)
                                and stmt.value.id == "REQUIRED_QUIET_RUN"), (
                            "gamma_alt_consecutive_zero_crit no longer "
                            "defaults to REQUIRED_QUIET_RUN; the 2 gate paths "
                            "can now disagree on the quiet run")
                        return
        raise AssertionError(
            "gamma_alt_consecutive_zero_crit not found on RunnerConfig")

    def test_the_quiet_arm_stays_reachable_under_the_smallest_round_cap(self):
        # A critical in round 1 is the EARLIEST a finding can arrive. If even
        # that run cannot fit REQUIRED_QUIET_RUN later quiet rounds under the
        # smallest recorded cap with working rounds to spare, the quiet arm is
        # an off switch for every capped run, not a gate. At 3 this leaves 4
        # working rounds (8 - 1 - 3); at 7 it left 0, which is how the archive
        # came to hold 0 occurrences of a 7-quiet window in 409 rounds.
        k = _required_quiet_run(_tree())
        spare = SMALLEST_RECORDED_ROUND_CAP - 1 - k
        assert spare >= 4, (
            f"REQUIRED_QUIET_RUN={k} leaves only {spare} working rounds under "
            f"the smallest recorded cap of {SMALLEST_RECORDED_ROUND_CAP}; the "
            f"quiet arm is unreachable for most real runs (measured "
            f"2026-10-25: K=7 feasible in 16-21 of 53 archived runs that "
            f"raised a critical, against 32-34 at K=3)")
