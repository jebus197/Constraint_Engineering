# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'falsifier_supply_and_integrity_r2_2026-10-02', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 8aafe6ab3a20b5dacd172cab58d303434f8a8ac6be82759f9567622bc76a6610
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""The 2026-10-02 integrity merge, attacked and repaired. FOUR GUARDS.

These exist because the shipped guard for that merge
(test_one_predicate_excludes_and_reports_2026-10-02.py) asserts
`excluded <=> reported` with `excluded` computed from the REPORT's own scope --
predicate AND non-terminal AND `severity >= CRITICAL_SEVERITY_THRESHOLD`. It
therefore compares the report against itself and never against the COUNTERS.
Two of the three consumers do gate severity themselves; `unverified_critical_count`
has not since 2026-09-06 (founder ruling 23). Nothing noticed.

D-A  A SUB-CRITICAL REFUSAL LEFT THE A4 BLOCKER IN SILENCE. Measured by
     differential execution over the real field domain: 225,280 single-entry
     registries, 970 drains, every one severity < 0.7, none of them reported.
     The shipped grid pins severity at 0.9 on all 48 combinations.

D-B  THE CARVE-OUT'S A4 HALF WAS INERT. `integrity_unobserved` makes the
     predicate return False "so unobserved entries keep blocking" -- and that
     False is also what routes the entry into `_apply_routing`'s `else`, which
     stamps `irreducible_escalation`, which `unverified_critical_count` skips
     BEFORE it consults the predicate. Driven through the real `_apply_routing`:
     A4 blocker 0, advisory empty, halt queue 2 against a bound of 2, so the run
     converges having verified nothing -- the exact outcome the carve-out's
     docstring says it prevents.

D-C  THE INTEGRITY STAMPS OUTLIVED THEIR INSTRUMENT. `clear_stale_resolution_stamps`
     retracts mechanical_fault/irreducible_escalation/hil_escalated and left
     `integrity_refused` standing, so a critical rescued by a later rung and
     reopened was excused from both counters and advertised as "UNTESTED" after
     a tool had confirmed it.

D-D  A SHELL COMMAND IS NOT A PATH. The observer's spawn hook resolved the whole
     command line as one path, so `subprocess.run("cat <path>", shell=True)` read
     a protected file that `open(<path>)` was refused. Guarded in
     test_the_sandbox_refuses_a_shell_built_read_2026-10-02.py, which needs a
     child process and lives beside its own decoy.
"""
from __future__ import annotations

import itertools
import pathlib
import random
import sys
import types

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
RUNNER = ROOT / "bench" / "reference_runner_v3.py"

pytestmark = pytest.mark.skipif(not RUNNER.is_file(), reason="runner absent")


@pytest.fixture(scope="module")
def rv():
    sys.path.insert(0, str(ROOT))
    from bench import reference_runner_v3 as rr
    return rr


class _Reg:
    def __init__(self, entries):
        self.entries = entries


def _entry(**kw):
    e = {"status": "UNCONFIRMED", "severity": 0.9, "falsifier_code": ""}
    e.update(kw)
    return e


# ── the field domain, read off the consumers rather than handpicked ──────────
STATUSES = ("OPEN", "CONTESTED", "REOPENED", "UNCONFIRMED", "CORROBORATED",
            "WITHHELD", "CONFIRMED", "CLOSED", "REFUTED", "MERGED", "DUPLICATE")
SEVERITIES = (0.0, 0.1, 0.3, 0.5, 0.69, 0.7, 0.9, 1.0)
VERDICTS = (None, "", "CONFIRMED", "REFUTED", "UNTOOLABLE", "ERROR",
            "NON_DISCRIMINATING", "INTEGRITY_VIOLATION")
LADDER = (None, "", "REFUTED", "CONFIRMED", "INTEGRITY_VIOLATION")
FLAGS = ("integrity_refused", "integrity_unobserved", "irreducible_escalation",
         "routing_deferred", "exhausted")


def _report_readers(rv):
    """Discovered, not listed: a fix that adds a reader is counted, and one that
    renames a reader is not silently lost."""
    return sorted(n for n in dir(rv.FindingRegistry)
                  if n.startswith("integrity_")
                  and callable(getattr(rv.FindingRegistry, n)))


def _report_surface(rv, entry):
    reg = _Reg({"C0001": entry})
    out = []
    for name in _report_readers(rv):
        out.extend(getattr(rv.FindingRegistry, name)(reg))
    return sorted(set(out))


def _neutralise(rv, e):
    """The identical entry with the predicate's trigger made false.

    Only the 4 fields the predicate reads are touched, and INTEGRITY_VIOLATION
    becomes UNTOOLABLE -- also outside `_FALSIFIER_RESOLVED_VERDICTS` -- so every
    other consumer branch sees exactly what it saw before.
    """
    n = dict(e)
    n.pop("integrity_refused", None)
    n.pop("integrity_unobserved", None)
    for f in ("falsifier_verdict", "routing_verdict_unreconciled"):
        if (n.get(f) or "").strip().upper() == rv.INTEGRITY_REFUSED_VERDICT:
            n[f] = "UNTOOLABLE"
    return n


def _consumers(rv, entry):
    reg = _Reg({"C0001": entry})
    locked, deferred = rv._irreducible_queue_split(reg.entries)
    return {"A4_blocker": rv.FindingRegistry.unverified_critical_count(reg),
            "halt_bound": locked + deferred}


def _drain_defect(rv, entry):
    """Return a description when `entry` leaves a counter without being reported."""
    neutral = _neutralise(rv, entry)
    assert not rv._integrity_violation_excluded(neutral), "_neutralise failed"
    before, after = _consumers(rv, entry), _consumers(rv, neutral)
    drained = sorted(k for k in before if before[k] < after[k])
    if not drained:
        return None
    if _report_surface(rv, entry):
        return None
    return {"entry": dict(entry), "drained_from": drained,
            "as_written": before, "neutralised": after}


class TestDrainedImpliesReported:
    """D-A. The invariant stated against the COUNTERS, by differential execution."""

    def test_exhaustive_over_the_real_field_domain(self, rv):
        flagsets = list(itertools.product((False, True), repeat=len(FLAGS)))
        n, bad, drains = 0, [], 0
        for status in STATUSES:
            for sev in SEVERITIES:
                for fv in VERDICTS:
                    for lad in LADDER:
                        for fc in ("", "x"):
                            for fl in flagsets:
                                e = {"status": status, "severity": sev,
                                     "falsifier_code": fc}
                                if fv is not None:
                                    e["falsifier_verdict"] = fv
                                if lad is not None:
                                    e["routing_verdict_unreconciled"] = lad
                                for name, on in zip(FLAGS, fl):
                                    if on:
                                        e[name] = True
                                n += 1
                                if _consumers(rv, e) != _consumers(
                                        rv, _neutralise(rv, e)):
                                    drains += 1
                                d = _drain_defect(rv, e)
                                if d is not None:
                                    bad.append(d)
        assert n > 200000, n
        assert drains > 0, (
            "ANTI-VACUITY: the predicate drained nothing anywhere, so this "
            "sweep cannot detect a silent drain")
        assert not bad, (
            f"{len(bad)} finding(s) left a convergence counter without entering "
            f"the report. First: {bad[0]}")

    def test_randomised_registries(self, rv):
        rng = random.Random(20261002)
        bad = []
        for _ in range(4000):
            e = {"status": rng.choice(STATUSES),
                 "severity": rng.choice(SEVERITIES),
                 "falsifier_code": rng.choice(("", "x")),
                 "falsifier_verdict": rng.choice(VERDICTS),
                 "routing_verdict_unreconciled": rng.choice(LADDER)}
            e = {k: v for k, v in e.items() if v is not None}
            for f in FLAGS:
                if rng.random() < 0.3:
                    e[f] = True
            d = _drain_defect(rv, e)
            if d is not None:
                bad.append(d)
        assert not bad, bad[0]

    def test_the_subcritical_witness_by_name(self, rv):
        """The exact shape the 48-combo grid cannot reach, named so a regression
        reads as itself rather than as 1 of 970."""
        e = _entry(severity=0.3, integrity_refused=True,
                   falsifier_verdict="INTEGRITY_VIOLATION")
        reg = _Reg({"C0001": e})
        # It IS excused from the A4 blocker -- which does not gate on severity.
        assert rv.FindingRegistry.unverified_critical_count(reg) == 0
        assert rv.FindingRegistry.unverified_critical_count(
            _Reg({"C0001": _neutralise(rv, e)})) == 1, "ANTI-VACUITY"
        # ... and the report must therefore name it SOMEWHERE.
        assert _report_surface(rv, e) == ["C0001"]
        # The critical reader stays scoped to criticals, as its name says.
        assert rv.FindingRegistry.integrity_refused_criticals(reg) == []

    def test_the_subcritical_reader_does_not_overstate(self, rv):
        """It must name only what actually left the counter."""
        R = rv.FindingRegistry.integrity_refused_subcriticals
        # tested and confirmed -> would not have counted -> claim nothing
        assert R(_Reg({"C1": _entry(severity=0.3, integrity_refused=True,
                                    falsifier_code="x",
                                    falsifier_verdict="CONFIRMED")})) == []
        # critical -> the other reader's business
        assert R(_Reg({"C1": _entry(severity=0.9, integrity_refused=True)})) == []
        # no refusal at all
        assert R(_Reg({"C1": _entry(severity=0.3)})) == []
        # exhausted, so the counter had already let it go for another reason
        assert R(_Reg({"C1": _entry(severity=0.3, integrity_refused=True,
                                    exhausted=True)})) == []
        # and the positive case, or the three above prove nothing
        assert R(_Reg({"C1": _entry(severity=0.3,
                                    integrity_refused=True)})) == ["C1"]


class _Cfg:
    routing_enabled = True
    models = ["SEAT-A", "SEAT-B"]
    test_article = ""
    routing_max_rungs = 2
    max_irreducible_queue = 2


class _ExpCfg:
    models = ["SEAT-A", "SEAT-B"]


@pytest.fixture
def routed(rv, monkeypatch):
    """Drive the REAL `_apply_routing`; only transport is stubbed.

    A hand-stamped entry would not have found D-B, because the defect is in WHICH
    BRANCH the carve-out sends an unobserved entry to.
    """
    import bench.routing as routing

    def _run(entries, resolved=False):
        def route(finding, models, confirmed, resolve_fn, reverify, sim, **kw):
            resolve_fn(models[0] if models else "SEAT-A", finding)
            return types.SimpleNamespace(
                resolved=resolved,
                verdict="CONFIRMED" if resolved else "INTEGRITY_VIOLATION",
                model_used="SEAT-B",
                falsifier_code="assert False  # fresh, runner-verified",
                duplicate_of=None, rungs_tried=1)
        monkeypatch.setattr(routing, "route", route)
        monkeypatch.setattr(rv, "dispatch_to_model", lambda *a, **k: ("", {}))
        monkeypatch.setattr(rv, "_declared_models", lambda ec, cfg: [
            types.SimpleNamespace(label=m) for m in _Cfg.models])
        monkeypatch.setattr(rv, "_log", lambda *a, **k: None)
        reg = rv.FindingRegistry()
        reg.entries.update(entries)
        rv._apply_routing(reg, 1, _ExpCfg(), cfg=_Cfg(), repo_root=str(ROOT))
        return reg
    return _run


class TestTheCarveOutActuallyBlocks:
    """D-B. The carve-out's claim is about the A4 BLOCKER, so test the blocker."""

    def _crits(self):
        return {
            f"C{i:04d}": {
                "canonical_id": f"C{i:04d}", "status": "UNCONFIRMED",
                "severity": 0.9, "description": "a critical claim",
                "source_model": "SEAT-A", "escalated": True,
                "falsifier_code": "assert True",
                "falsifier_verdict": "INTEGRITY_VIOLATION",
                "integrity_unobserved": True, "verdicts": [],
            } for i in (1, 2)
        }

    def test_a_machine_wide_observer_failure_blocks_a4(self, rv, routed):
        reg = routed(self._crits())
        assert all(e.get("irreducible_escalation") for e in reg.entries.values()), (
            "the fixture no longer reproduces the branch under test: the "
            "carve-out is supposed to route these into `else`")
        assert reg.unverified_critical_count() == 2, (
            "a machine-wide observer failure DRAINED the A4 blocker despite the "
            "carve-out -- the run can converge having verified nothing")

    def test_and_it_is_reported(self, rv, routed):
        reg = routed(self._crits())
        assert reg.integrity_unobserved_criticals() == ["C0001", "C0002"], (
            "nothing anywhere says these criticals were never measured; the "
            "static-HIL-queue line files them as 'ladder-exhausted', i.e. a "
            "machine tried and failed, which is not what happened")
        assert reg.integrity_refused_criticals() == [], (
            "an equipment fault must not be reported as a key-access refusal: "
            "the two have opposite consequences")

    def test_a_plain_key_access_refusal_still_leaves_both_counters(self, rv, routed):
        """ANTI-OVERREACH: the 2026-10-02 ruling is not partially reverted."""
        ents = self._crits()
        for e in ents.values():
            e["integrity_unobserved"] = False
        reg = routed(ents)
        assert all(e.get("integrity_refused") for e in reg.entries.values())
        assert reg.unverified_critical_count() == 0
        assert rv._irreducible_queue_split(reg.entries) == (0, 0)
        assert reg.integrity_refused_criticals() == ["C0001", "C0002"]

    def test_the_block_is_releasable(self, rv):
        """NOT FOR EVER. The `exhausted` valve the sibling counter already
        honours applies here too, so a transient equipment fault cannot pin a
        run to its round cap once review activity has exhausted the finding."""
        e = _entry(integrity_unobserved=True,
                   falsifier_verdict="INTEGRITY_VIOLATION",
                   irreducible_escalation=True)
        assert rv.FindingRegistry.unverified_critical_count(
            _Reg({"C1": dict(e, exhausted=False)})) == 1
        assert rv.FindingRegistry.unverified_critical_count(
            _Reg({"C1": dict(e, exhausted=True)})) == 0


class TestTheStampsDoNotOutliveTheInstrument:
    """D-C. `clear_stale_resolution_stamps` retracts the integrity stamps too."""

    def test_a_rescued_critical_is_no_longer_excused(self, rv, routed):
        ent = {"C0001": {
            "canonical_id": "C0001", "status": "UNCONFIRMED", "severity": 0.9,
            "description": "a critical claim", "source_model": "SEAT-A",
            "escalated": True, "falsifier_code": "assert True",
            "falsifier_verdict": "INTEGRITY_VIOLATION", "verdicts": [],
        }}
        reg = routed(ent)                      # round 1: the gate refuses
        e = reg.entries["C0001"]
        assert e.get("integrity_refused") is True, "setup"
        e["escalated"] = True
        reg2 = routed({"C0001": e}, resolved=True)   # round 2: a rung resolves it
        e = reg2.entries["C0001"]
        assert e.get("falsifier_verdict") == "CONFIRMED"
        assert e.get("integrity_refused") is False, (
            "the refusal stamp survived a replacement falsifier the runner "
            "verified; it now describes an instrument the entry does not carry")
        # The real CLOSED -> REOPENED transition is where the stale stamp bit.
        reg2.resolve("C0001", "CLOSED", 3)
        reg2.resolve("C0001", "REOPENED", 4)
        assert not rv._integrity_violation_excluded(e), (
            "a tested, CONFIRMED critical is excused from the convergence "
            "machinery by a stale flag -- the predicate guards exactly this for "
            "`routing_verdict_unreconciled` and must guard it for the flag")
        assert reg2.integrity_refused_criticals() == [], (
            "the advisory calls a confirmed claim UNTESTED")

    def test_the_retraction_is_recorded(self, rv):
        """A retraction nobody can see is how a rejected reading survives."""
        e = {"integrity_refused": True, "integrity_unobserved": True,
             "irreducible_escalation": True}
        cleared = rv.clear_stale_resolution_stamps(e)
        assert set(cleared) >= {"integrity_refused", "integrity_unobserved"}
        assert e["stamp_retractions"][-1]["cleared"] == cleared

    def test_it_clears_nothing_it_was_not_given(self, rv):
        """ANTI-OVERREACH: a LIVE refusal must not be erased by a call on an
        entry that was never rescued."""
        assert rv.clear_stale_resolution_stamps({}) == []
        e = {"integrity_refused": True}
        assert rv.clear_stale_resolution_stamps(e) == ["integrity_refused"]
        # and a later refusal re-stamps it through the branch that owns it
        e["integrity_refused"] = True
        assert rv._integrity_violation_excluded(
            {"integrity_refused": True, "status": "UNCONFIRMED",
             "severity": 0.9})


class TestTheAdvisoryWiringNamesEveryReader:
    """The end-of-run site must consume every reader, or a reader that reports
    nothing is the same as no reader at all."""

    def test_every_integrity_reader_is_called_at_the_advisory_site(self, rv):
        import inspect
        src = inspect.getsource(rv.run_experiment)
        for name in _report_readers(rv):
            assert f"registry.{name}()" in src, (
                f"{name} exists but the run never calls it, so whatever it "
                f"reports is never reported")

    def test_no_reader_feeds_a_gate(self, rv):
        """ZERO WEIGHT, which is the founder's ruling. The advisory names are
        logged and nothing branches on them."""
        import inspect
        src = inspect.getsource(rv.run_experiment)
        for var in ("_integrity_refused", "_integrity_sub", "_integrity_unobs"):
            for line in src.splitlines():
                st = line.strip()
                if st.startswith(("if ", "elif ", "while ")) and var in st:
                    assert st.startswith(f"if {var}"), (
                        f"{var} reached a compound condition: {st!r}")
