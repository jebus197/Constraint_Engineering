"""Nothing may leave the convergence machinery without entering the report.

THE DEFECT THIS EXISTS FOR, found while MERGING the 2 panel fixes rather than
in either of them. The 2026-10-02 star round settled that the cc2 and fable
variants are complementary: fable's supplies the UNOBSERVED carve-out, without
which a machine-wide observer failure could let a run converge having verified
nothing; cc2's supplies the REPORT, without which a convergence over an excused
critical is silent. Merging them naively keeps both halves and still fails,
because the 2 halves key on DIFFERENT fields:

    fable's exclusion  : falsifier_verdict == INTEGRITY_VIOLATION
    cc2's reporter     : e["integrity_refused"], set by the routing branch

An entry refused by VERDICT that never passed through the routing branch is
therefore excluded from both counters and absent from the report -- a SILENT
exclusion, which is the one outcome the founder's ruling forbids by its own
wording ("If no key was accessed, say nothing" -- so if one was, say something).

The repair is that `integrity_refused_criticals` calls the SAME predicate the
exclusions call. This file asserts the resulting invariant by EXECUTING both
over randomised registries, because the 2 halves are each individually correct
and only their JOINT behaviour is wrong -- the producer-and-consumer-disagree
shape that reading cannot catch (`execute-do-not-grep`).

D-6 is asserted here too: the ladder-side residual, where `_apply_routing` left
a stale `UNTOOLABLE` in `falsifier_verdict` and the real verdict only in
`routing_verdict_unreconciled`. That is how C0029 was read as untoolable when it
had been integrity-refused, and neither seat's fix covered it.
"""
from __future__ import annotations

import itertools
import pathlib
import random
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
RUNNER = ROOT / "bench" / "reference_runner_v3.py"

pytestmark = pytest.mark.skipif(not RUNNER.is_file(), reason="runner absent")


@pytest.fixture(scope="module")
def rv():
    """Import the REAL module, not a detached copy.

    `spec_from_file_location` + `exec_module` without registering the module in
    `sys.modules` makes every dataclass in the runner fail to construct --
    `dataclasses` resolves `sys.modules[cls.__module__]` and gets None. The
    package import is also what the sibling test files use, so all 3 exercise
    one object.
    """
    sys.path.insert(0, str(ROOT))
    from bench import reference_runner_v3 as rr
    return rr


def _entry(**kw):
    e = {"status": "UNCONFIRMED", "severity": 0.9}
    e.update(kw)
    return e


class _Reg:
    """A registry carrying only `.entries`, as the project's other fixtures do."""
    def __init__(self, entries):
        self.entries = entries


class TestExcludedImpliesReported:

    #: Every combination of the 4 fields the predicate and the reporter read.
    FIELDS = ("integrity_refused", "integrity_unobserved",
              "falsifier_verdict", "routing_verdict_unreconciled")

    def test_every_excluded_critical_is_reported(self, rv):
        """EXHAUSTIVE over the field space, not a sample."""
        values = {
            "integrity_refused": (None, True),
            "integrity_unobserved": (None, True),
            "falsifier_verdict": (None, "UNTOOLABLE", "INTEGRITY_VIOLATION",
                                  "CONFIRMED"),
            "routing_verdict_unreconciled": (None, "REFUTED", "INTEGRITY_VIOLATION"),
        }
        combos = list(itertools.product(*(values[f] for f in self.FIELDS)))
        assert len(combos) == 48, len(combos)
        entries, excluded = {}, set()
        for i, combo in enumerate(combos):
            e = _entry(**{f: v for f, v in zip(self.FIELDS, combo) if v is not None})
            cid = f"C{i:04d}"
            entries[cid] = e
            if rv._integrity_violation_excluded(e):
                excluded.add(cid)
        reported = set(rv.FindingRegistry.integrity_refused_criticals(_Reg(entries)))
        assert excluded, "ANTI-VACUITY: no combination excluded anything"
        assert excluded <= reported, (
            "these criticals left the convergence machinery WITHOUT entering "
            f"the report: {sorted(excluded - reported)}")
        assert reported <= excluded, (
            "these are reported as excused but are NOT excluded, so the report "
            f"overstates: {sorted(reported - excluded)}")

    def test_a_terminal_entry_is_neither_and_a_subcritical_one_IS_REPORTED(self, rv):
        """AMENDED 2026-10-03, and the amendment is the finding.

        SUPERSEDED ASSERTION, preserved verbatim rather than deleted:

            entries = {C1 terminal, C2 severity=0.1, C3 critical}
            assert integrity_refused_criticals(...) == ["C3"]

        and its docstring, "The reporter is scoped to NON-TERMINAL CRITICALS,
        LIKE THE COUNTERS."  That last clause is false and this oracle pinned
        it. `_irreducible_queue_split` is scoped to non-terminal criticals;
        `unverified_critical_count` is scoped to `status == "UNCONFIRMED"` at
        ANY severity, because its severity gate was removed on 2026-09-06 on
        the founder's ruling that a model-assigned float must not decide
        convergence. `_entry()` above defaults to status UNCONFIRMED, so C2 was
        an entry the A4 blocker DID drop and this list did NOT name -- a silent
        exclusion, pinned green.

        Falsifier:
        bench/tests/falsifier_subcritical_refusal_is_silent_2026-10-03.py
        (executed; at severity 0.5 the counter went 1 -> 0 while the report
        stayed empty). The terminal half of the old assertion was correct and
        is kept unchanged.
        """
        entries = {
            "C1": _entry(status="CLOSED", falsifier_verdict="INTEGRITY_VIOLATION"),
            "C2": _entry(severity=0.1, falsifier_verdict="INTEGRITY_VIOLATION"),
            "C3": _entry(falsifier_verdict="INTEGRITY_VIOLATION"),
        }
        assert rv.FindingRegistry.integrity_refused_criticals(_Reg(entries)) == ["C2", "C3"]
        # A terminal entry is still neither excluded nor reported.
        terminal_only = {"C1": entries["C1"]}
        assert rv.FindingRegistry.integrity_refused_criticals(_Reg(terminal_only)) == []
        # A sub-critical entry that is NOT UNCONFIRMED is outside both counters'
        # scope and must stay out of the report, or the report overstates.
        open_subcrit = {"C4": _entry(status="OPEN", severity=0.1,
                                     falsifier_verdict="INTEGRITY_VIOLATION")}
        assert rv.FindingRegistry.integrity_refused_criticals(_Reg(open_subcrit)) == []

    def test_randomised_registries_agree(self, rv):
        """400 random registries, same invariant. A field order or a short-circuit
        that holds on the exhaustive grid but not under mixed severities and
        statuses would show here."""
        rng = random.Random(20261002)
        for _ in range(400):
            entries = {}
            for i in range(rng.randint(1, 12)):
                e = _entry(
                    status=rng.choice(["UNCONFIRMED", "OPEN", "CLOSED", "CONFIRMED"]),
                    severity=rng.choice([0.0, 0.3, 0.7, 0.9, 1.0]))
                if rng.random() < 0.4:
                    e["falsifier_verdict"] = rng.choice(
                        ["INTEGRITY_VIOLATION", "UNTOOLABLE", "CONFIRMED", ""])
                if rng.random() < 0.3:
                    e["routing_verdict_unreconciled"] = rng.choice(
                        ["INTEGRITY_VIOLATION", "REFUTED"])
                if rng.random() < 0.2:
                    e["integrity_refused"] = True
                if rng.random() < 0.2:
                    e["integrity_unobserved"] = True
                entries[f"C{i:04d}"] = e
            reg = _Reg(entries)
            term = {"MERGED", "CLOSED", "REFUTED", "DUPLICATE", "CONFIRMED"}
            # AMENDED 2026-10-03. The superseded expectation was
            #     ... and e["severity"] >= rv.CRITICAL_SEVERITY_THRESHOLD}
            # alone, which re-derived the REPORTER's own 0.7 gate and therefore
            # compared the reporter against itself. The disjunct below is the
            # A4 blocker's scope, which has carried no severity gate since
            # 2026-09-06. See
            # test_whatever_the_A4_counter_drops_is_named_in_the_report for the
            # invariant that holds the two consumers against each other rather
            # than against a re-derivation.
            excluded = {
                cid for cid, e in entries.items()
                if rv._integrity_violation_excluded(e)
                and e["status"] not in term
                and (e["severity"] >= rv.CRITICAL_SEVERITY_THRESHOLD
                     or e["status"] == "UNCONFIRMED")}
            got = set(rv.FindingRegistry.integrity_refused_criticals(reg))
            assert got == excluded, (entries, sorted(got), sorted(excluded))

    def test_whatever_the_A4_counter_drops_is_named_in_the_report(self, rv):
        """THE INVARIANT THIS FILE CLAIMED AND DID NOT HOLD (added 2026-10-03).

        Every assertion above compares `integrity_refused_criticals` against a
        RE-DERIVATION of its own rule. None compares it against a CONSUMER. The
        four readers of `_integrity_violation_excluded` genuinely call one
        predicate -- and they quantify over different entries, so one predicate
        with two scopes behaves as two predicates and a grid over the predicate
        is blind to it.

        This measures the thing itself: for each registry, count A4 WITH the
        predicate live and AGAIN with it neutralised. The difference is exactly
        what the exclusion dropped, and every one of those ids must be named in
        the report. A severity floor re-entering either side fails here.
        """
        rng = random.Random(20261003)
        witnessed = 0
        for _ in range(400):
            entries = {}
            for i in range(rng.randint(1, 10)):
                e = _entry(
                    status=rng.choice(["UNCONFIRMED", "OPEN", "CLOSED", "CONFIRMED"]),
                    severity=rng.choice([0.0, 0.3, 0.5, 0.7, 0.9]))
                e["falsifier_code"] = rng.choice(["", "assert False"])
                if rng.random() < 0.5:
                    e["falsifier_verdict"] = rng.choice(
                        ["INTEGRITY_VIOLATION", "UNTOOLABLE", "CONFIRMED", ""])
                if rng.random() < 0.25:
                    e["integrity_refused"] = True
                if rng.random() < 0.15:
                    e["integrity_unobserved"] = True
                entries[f"C{i:04d}"] = e
            reg = rv.FindingRegistry()
            reg.entries = entries

            dropped = set()
            _orig = rv._integrity_violation_excluded
            for cid, e in entries.items():
                if not _orig(e):
                    continue
                solo = rv.FindingRegistry()
                solo.entries = {cid: e}
                with_pred = solo.unverified_critical_count()
                rv._integrity_violation_excluded = lambda _e: False
                try:
                    without_pred = solo.unverified_critical_count()
                finally:
                    rv._integrity_violation_excluded = _orig
                if without_pred > with_pred:
                    dropped.add(cid)
            reported = set(reg.integrity_refused_criticals())
            witnessed += len(dropped)
            assert dropped <= reported, (
                "the A4 blocker dropped these and the report names none of "
                f"them: {sorted(dropped - reported)} / entries={entries}")
        assert witnessed > 0, "ANTI-VACUITY: no registry ever exercised a drop"


class TestTheCarveOutAndTheResidual:

    def test_an_unobserved_run_still_blocks(self, rv):
        """THE SAFETY PROPERTY. A machine-wide observer failure makes every
        falsifier return INTEGRITY_VIOLATION; if those were excused, a run could
        converge having verified nothing."""
        e = _entry(falsifier_verdict="INTEGRITY_VIOLATION", integrity_unobserved=True)
        assert not rv._integrity_violation_excluded(e)
        assert rv._irreducible_queue_split(
            {"C1": _entry(falsifier_verdict="INTEGRITY_VIOLATION",
                          integrity_unobserved=True,
                          irreducible_escalation=True)}) == (1, 0)

    def test_the_unobserved_flag_beats_the_refused_flag(self, rv):
        """Order matters: an entry carrying BOTH must block, because the
        carve-out is the safety side."""
        e = _entry(integrity_refused=True, integrity_unobserved=True)
        assert not rv._integrity_violation_excluded(e)

    def test_the_ladder_side_residual_is_covered(self, rv):
        """D-6: C0029's shape -- a STALE `UNTOOLABLE` in `falsifier_verdict`
        with the real verdict only in `routing_verdict_unreconciled`."""
        e = _entry(falsifier_verdict="UNTOOLABLE",
                   routing_verdict_unreconciled="INTEGRITY_VIOLATION")
        assert rv._integrity_violation_excluded(e), (
            "the ladder-side refusal is still counted; neither panel seat's fix "
            "covered this path and the merge was supposed to")

    def test_a_stale_residual_beside_a_RESOLVED_falsifier_is_not_excused(self, rv):
        """THE PRECISION CASE, found in run 1b's own registry rather than in
        either seat's fix. C0029 ends the run with
        `routing_verdict_unreconciled == "INTEGRITY_VIOLATION"` beside
        `falsifier_verdict == "CONFIRMED"`, because a later pass DID test it.
        Reading the stale field unconditionally would report a tested, confirmed
        critical as excused from the gate -- an overstatement in the record that
        exists to prevent silence."""
        e = _entry(falsifier_verdict="CONFIRMED",
                   routing_verdict_unreconciled="INTEGRITY_VIOLATION")
        assert not rv._integrity_violation_excluded(e)
        assert rv.FindingRegistry.integrity_refused_criticals(_Reg({"C1": e})) == []

    def test_an_integrity_refusal_LEAVES_THE_HALT_BOUND(self, rv):
        """THE GAP MUTATION TESTING FOUND, 2026-10-02, in a seat's own guard.

        The cc2 seat shipped `test_a_key_access_refusal_cannot_halt_the_run`,
        whose fixture entries carry NEITHER `irreducible_escalation` NOR
        `routing_deferred` -- and `_irreducible_queue_split` counts only
        entries carrying one of those. So the queue is 0 whether or not the
        skip exists, and deleting the skip left that test green: a guard that
        cannot fail against the defect it names. Verified by mutation (M6).

        This asserts the skip itself: an escalated critical that was
        integrity-refused must leave the halt bound, while the identical entry
        without the refusal must stay in it.
        """
        refused = {"C1": _entry(irreducible_escalation=True,
                                falsifier_verdict="INTEGRITY_VIOLATION")}
        plain = {"C1": _entry(irreducible_escalation=True,
                              falsifier_verdict="UNTOOLABLE")}
        assert rv._irreducible_queue_split(refused) == (0, 0), (
            "an integrity-refused critical still counts toward the halt bound")
        assert rv._irreducible_queue_split(plain) == (1, 0), (
            "ANTI-VACUITY: the identical entry without the refusal must count")
        # The DEFERRED arm too, which is the other half of the same split.
        d_refused = {"C1": _entry(routing_deferred=True,
                                  falsifier_verdict="INTEGRITY_VIOLATION")}
        d_plain = {"C1": _entry(routing_deferred=True,
                                falsifier_verdict="UNTOOLABLE")}
        assert rv._irreducible_queue_split(d_refused) == (0, 0)
        assert rv._irreducible_queue_split(d_plain) == (0, 1)

    def test_an_ordinary_untoolable_is_untouched(self, rv):
        """ANTI-OVERREACH: the predicate must not swallow the ordinary case."""
        assert not rv._integrity_violation_excluded(_entry(falsifier_verdict="UNTOOLABLE"))
        assert not rv._integrity_violation_excluded(_entry())
        assert rv._irreducible_queue_split(
            {"C1": _entry(irreducible_escalation=True)}) == (1, 0)


class TestGammaIsUntouched:
    """GAMMA IS LOAD-BEARING (standing directive). The ruling moves a HALT
    INPUT; it must not move the decay curve or the zero-new-critical window."""

    def test_the_predicate_names_no_gamma_field(self, rv):
        import inspect
        src = inspect.getsource(rv._integrity_violation_excluded)
        for forbidden in ("gamma", "rho", "s_k", "sk_", "duane"):
            assert forbidden not in src.lower().replace("gamma is", ""), forbidden
