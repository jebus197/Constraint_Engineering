#!/usr/bin/env python3
"""The 2026-10-02 ruling, pinned by execution.

FOUNDER RULING under test:

    "Just make it accurate. If a key was accessed and read, report it at the end
    of a run. If no key was accessed, say nothing, and let the system report
    clean convergence. But convergence should not be blocked and runs should not
    be terminated even if a key was read. That is a reporting and post run fix
    issue (as it always has been), not part of the convergence machinery of the
    schema."

Four properties, each asserted against a REAL archived run or the real
production readers -- never against a retyped copy:

  1. SILENT WHEN CLEAN. prose_convergence_run1b (no key was read) produces no
     advisory, and the residual CONFIRMED hits are all on the audit channel.
  2. LOUD WHEN NOT. exp48_chemistry_exam_live (finding C0012 opened the
     chemistry answer key by absolute path) produces an advisory naming the
     file and the location.
  3. THE EXAM CONFINEMENT SURVIVES THE PRECISION FIX. exp48 stays
     `repo_in_scope=False` and keeps C0017's repo-resident target reads, which
     the blanket "repo is always in scope" alternative erases (12 -> 10).
  4. NEITHER GATE INPUT MOVES, AND NEITHER COUNTER CAN HALT OR BLOCK ON A
     KEY-ACCESS REFUSAL -- while the refusal is still REPORTED.

Run:  python3 -m pytest bench/tests/test_key_access_advisory_2026-10-02.py -q
"""
from __future__ import annotations

import json
import os
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from bench import key_access_forensics as kf  # noqa: E402
from bench import reference_runner_v3 as rr  # noqa: E402
from bench.falsifier_verify import INTEGRITY_VIOLATION  # noqa: E402

LOGS = REPO / "bench" / "logs"
RUN1B = LOGS / "prose_convergence_run1b_2026-10-02_20261002T044234Z"
EXP48 = LOGS / "exp48_chemistry_exam_live_20260729T044134Z"

# THE CANONICAL TREE, NOT `REPO`. A panel seat runs in a sandbox COPY at a temp
# path, while the archived artefacts name the canonical absolute path. The
# scanner's scope test compares path literals, so scanning an archived run with
# repo_root=<sandbox> cannot resolve them and every repository read reports out
# of scope. Passing the tree the artefacts were WRITTEN under is what makes this
# test mean the same thing in both places; the path need not exist, because
# nothing here touches the filesystem at that location.
CANONICAL_REPO = pathlib.Path(
    "/Users/georgejackson/Developer_Projects/Constraint_Engineering")


def _scan(run_dir: pathlib.Path) -> kf.Report:
    return kf.scan_run(run_dir, repo_root=CANONICAL_REPO)


# -- 1 & 2: the ruling itself ------------------------------------------------

@pytest.mark.skipif(not RUN1B.is_dir(), reason="run 1b not archived here")
# ── AST RESOLUTION, NOT SUBSTRING MATCHING ──────────────────────────────────
# `execute-do-not-grep`, applied to a wiring check. A substring assertion over a
# module's source proves a string exists SOMEWHERE in the file; it cannot tell a
# live call site from the same words in a comment, and it breaks on reformatting
# that changes nothing. These resolve the CALL, which is the property the
# additive standard actually asks for: "an addition that nothing reaches is not
# additive". They also keep this file out of the source-text assertion census,
# which stood at 82 against a cap of 80.

def _runner_tree():
    import ast as _ast
    return _ast.parse((REPO / "bench" / "reference_runner_v3.py").read_text(
        encoding="utf-8", errors="replace"))


def _calls_named(tree, name):
    """Every function whose body contains a CALL to `name`."""
    import ast as _ast
    out = []
    for fn in _ast.walk(tree):
        if not isinstance(fn, (_ast.FunctionDef, _ast.AsyncFunctionDef)):
            continue
        for node in _ast.walk(fn):
            if isinstance(node, _ast.Call):
                f = node.func
                if getattr(f, "attr", None) == name or getattr(f, "id", None) == name:
                    out.append(fn)
                    break
    return out


def test_advisory_is_silent_on_a_run_where_no_key_was_read():
    rep = _scan(RUN1B)
    advisory = kf.build_end_of_run_advisory(rep)
    assert advisory is None, (
        "run 1b read no key, so the advisory must be SILENT. Got an advisory "
        f"over {len(rep.advisory_confirmed)} hit(s): "
        f"{[(h.file, h.where) for h in rep.advisory_confirmed][:5]}")
    # Silent is not the same as empty: nothing was dropped to achieve it.
    assert rep.audit_confirmed, (
        "the carried-source hits must be RETAINED on the audit channel, not "
        "excluded. An empty audit channel means the evidence was discarded.")
    assert all(f.endswith(".py") for f in {h.file for h in rep.audit_confirmed})


@pytest.mark.skipif(not EXP48.is_dir(), reason="exp 48 not archived here")
def test_advisory_fires_and_names_the_location_on_the_real_breach():
    rep = _scan(EXP48)
    advisory = kf.build_end_of_run_advisory(rep)
    assert advisory is not None, "the Exp 48 C0012 breach must produce an advisory"
    assert advisory["fires"] is True
    assert advisory["weight_on_convergence"] == 0.0
    assert advisory["weight_on_completion_status"] == 0.0
    files = {loc["file"] for loc in advisory["locations"]}
    wheres = {loc["where"] for loc in advisory["locations"]}
    findings = {loc["finding"] for loc in advisory["locations"]}
    assert "C0012" in findings, f"C0012 must be named; got {findings}"
    assert any("report.json" in f or "runner_state" in f for f in files), files
    assert any("falsifier_code" in w for w in wheres), wheres
    json.dumps(advisory)  # it goes into a run artefact


# -- 3: the precision fix does not reopen the 2026-07-29 exam hole -----------

@pytest.mark.skipif(not EXP48.is_dir(), reason="exp 48 not archived here")
def test_exam_run_stays_confined_and_keeps_its_repo_resident_reads():
    rep = _scan(EXP48)
    assert rep.repo_in_scope is False, (
        "an exam run records an ABSOLUTE staged-target path outside the tree, "
        "so it must still be confined after the relative-path fix")
    labels = [h.label for h in rep.confirmed]
    assert sum(l == "out-of-scope path opened or listed" for l in labels) >= 2, (
        "C0017 reads the exam document out of bench/cdsfl_registry/targets/ in "
        "the repository. Those hits are exactly what a blanket 'the repo is "
        "always in scope' rule erases (measured: 12 CONFIRMED -> 10), and they "
        "are the route the 2026-07-29 adversarial audit added confinement for.")
    assert {h.finding for h in rep.confirmed} >= {"C0012", "C0017"}


@pytest.mark.skipif(not RUN1B.is_dir(), reason="run 1b not archived here")
def test_a_relative_discovered_target_dir_is_resolved_against_the_repo():
    raw = kf.discover_target_dirs(RUN1B.resolve())
    assert any(not os.path.isabs(d) for d in raw), (
        "this run's runner-authored record carries a REPOSITORY-RELATIVE "
        f"target dir; if that stops being true this test is moot. Got {raw}")
    fixed = kf.resolve_target_dirs(raw, CANONICAL_REPO)
    assert all(os.path.isabs(d) for d in fixed), fixed
    assert _scan(RUN1B).repo_in_scope is True, (
        "a CODE review must have its own repository in scope; the relative "
        "string could never satisfy the `confined` test, so it did not")


def test_resolve_target_dirs_leaves_absolute_paths_alone():
    out = kf.resolve_target_dirs(["/Users/nobody/CDSFL_review_targets", "bench"],
                                 pathlib.Path("/repo"))
    assert "/Users/nobody/CDSFL_review_targets" in out
    assert "/repo/bench" in out


def test_a_model_authored_file_at_a_repo_path_is_retained_not_excluded():
    """The hole in the briefed exclusion list, pinned shut.

    The design on the table excluded "harvested copies of the detector's own
    source". Measured in run 1b: that file's SHA1 is 4a0416f2b663... against the
    repository's 234caeac9cea... -- it is MODEL-AUTHORED, because seats are told
    to deliver fixes at exactly that path. An exclusion keyed on the name would
    exclude arbitrary model-authored code from the scan that checks it.
    """
    # SHARPENED AT MERGE TIME, IN THE DIRECTION THIS DOCSTRING ARGUES FOR.
    # The assertion below used to send every carried `.py` hit to the audit
    # channel, which is the exclusion-by-name this docstring objects to: a
    # model-authored key reader delivered at that very path would never fire
    # the advisory. The merged form asks whether the matched text is VERBATIM
    # in the committed file at the same path. Our own code quoting itself goes
    # to audit; MODEL-AUTHORED text fires the advisory. A hand-built Hit
    # carries `carried_verbatim=False`, i.e. model-authored, so it is
    # advisory-bearing -- which is this docstring's own conclusion.
    h = kf.Hit(kf.CONFIRMED, "answer-key file path",
               "panel_worktree_harvest/files/bench/falsifier_verify.py",
               "line 1", None, "snip", (0, 1))
    rep = kf.Report(run_dir=pathlib.Path("/tmp/x"), hits=[h])
    assert rep.confirmed == [h], "the hit must never be dropped"
    assert rep.advisory_confirmed == [h], (
        "a model-authored hit at a repository path was routed to the audit "
        "channel, so the advisory stays silent on it -- the bypass this "
        "docstring names")
    assert rep.audit_confirmed == []
    # And a FAITHFUL quote of our own code goes the other way.
    verbatim = h._replace(carried_verbatim=True)
    rep_v = kf.Report(run_dir=pathlib.Path("/tmp/x"), hits=[verbatim])
    assert rep_v.audit_confirmed == [verbatim] and rep_v.advisory_confirmed == []
    # ... and a hit in a run ARTEFACT is advisory-bearing, so the split is not
    # "everything is audit".
    h2 = h._replace(file="runner_state.json", where="/registry/entries/C1/falsifier_code")
    rep2 = kf.Report(run_dir=pathlib.Path("/tmp/x"), hits=[h2])
    assert rep2.advisory_confirmed == [h2] and rep2.audit_confirmed == []
    assert kf.build_end_of_run_advisory(rep2) is not None


def test_an_unclassifiable_suffix_fails_toward_reporting():
    """Misclassification must fail LOUD, not silent."""
    h = kf.Hit(kf.CONFIRMED, "answer-key file path", "weird.unknownext",
               "line 1", None, "snip", (0, 1))
    rep = kf.Report(run_dir=pathlib.Path("/tmp/x"), hits=[h])
    assert rep.advisory_confirmed == [h]


# -- 4: the convergence machinery -------------------------------------------

# A REALISTIC CRITICAL HISTORY, AND THE REASON IT IS NOT [0, 0, 0].
#
# `_check_gamma_alt_convergence` has a VACUOUS-CURVE branch (2026-07-29): when
# the cumulative critical count over the WHOLE history is zero and the panel
# produced findings of some severity, the gamma side is satisfied BY VACUITY and
# the function returns converged=True whatever `gamma_critical` is. So a test
# using [0, 0, 0] never reaches the two-sided comparison it claims to exercise,
# and its gamma-below-threshold control passes for the wrong reason. Caught by
# that control failing on first execution. The tail is still 3 zeros -- the
# window condition the gate reads -- with a non-zero head, which is run 1b's
# own shape (criticals found early, none in the closing rounds).
HISTORY = [2, 1, 0, 0, 0]


def _reg(**entry_kw):
    e = {"status": "UNCONFIRMED", "severity": 0.8, "falsifier_verdict": "",
         "falsifier_code": "", "description": "d", "verdicts": []}
    e.update(entry_kw)
    r = rr.FindingRegistry()
    r.entries = {"C0001": e}
    return r


def test_the_runner_and_the_gate_agree_on_the_refusal_verdict_string():
    """A rename in falsifier_verify must fail here, not silently un-handle."""
    assert rr.INTEGRITY_REFUSED_VERDICT == INTEGRITY_VIOLATION
    # Deliberately NOT an equipment failure: membership there stamps
    # routing_deferred, which the halt bound counts.
    assert rr.INTEGRITY_REFUSED_VERDICT not in rr.EQUIPMENT_FAILURE_VERDICTS
    assert rr.INTEGRITY_REFUSED_VERDICT not in rr.ROUTABLE_INSTRUMENT_FAULTS


def test_a_key_access_refusal_cannot_halt_the_run():
    cfg = rr.RunnerConfig()
    r = rr.FindingRegistry()
    r.entries = {
        f"C{i:04d}": {"status": "UNCONFIRMED", "severity": 0.8,
                      "falsifier_verdict": INTEGRITY_VIOLATION,
                      "falsifier_code": "", "description": "d", "verdicts": [],
                      "integrity_refused": True}
        for i in range(1, 6)
    }
    assert r.irreducible_queue_count() == 0, (
        "5 integrity-refused criticals against a bound of "
        f"{cfg.max_irreducible_queue} must not reach the halt bound")
    assert rr.build_irreducible_queue_alarm(r, cfg, 2) is None, (
        "the alarm HALTS the run; it must not fire on key-access refusals")


def test_a_key_access_refusal_cannot_block_the_a4_gate():
    r = _reg(falsifier_verdict=INTEGRITY_VIOLATION, integrity_refused=True)
    assert r.unverified_critical_count() == 0
    cfg = rr.RunnerConfig()
    converged, reason = rr._check_gamma_alt_convergence(
        round_idx=3, gamma=0.432, novel_critical_history=HISTORY, cfg=cfg,
        unresolved_critical=r.unverified_critical_count(), contested=0,
        irreducible_queue=r.irreducible_queue_count(),
        gamma_critical=0.336, total_findings=40)
    assert converged is True, reason
    assert "A4 BLOCK" not in reason


def test_without_the_flag_it_still_blocks_so_the_test_above_is_not_vacuous():
    """The control. If A4 ignored the verdict outright this would also pass.

    This is also the executed measurement behind refusing HALF of the briefed
    design: drop the verdict from the HALT counter only, and A4 blocks here,
    bounded by the `exhausted` valve -- which requires len(verdicts) > 0, and
    MEASURED over the 57 archived runner_state registries, 58 of 86 UNCONFIRMED
    criticals carry ZERO verdicts: 67.4419%, Wilson [56.9779%, 76.4143%],
    statsmodels and mpmath agreeing to 1e-9. Producer:
    scripts/integrity_exclusion_figures_2026-10-02.py.

    THIS SEAT'S OWN FIGURE FOR IT DID NOT REPRODUCE. It cited "156 of 263
    (59.32%)"; the population is 86, not 263 -- most likely the report/state
    double-count this project already records as having corrupted 2
    measurements in 1 night. The ARGUMENT survives either reading, both being
    a majority, so the argument stands and the number is replaced.

    THE CONTRAST CHANGED AT MERGE TIME, AND THE PURPOSE DID NOT. This seat
    excluded an entry only when the ROUTING BRANCH had stamped
    `integrity_refused`; the other seat excluded on the VERDICT itself. The
    merged predicate takes the verdict, because the founder's ruling is about
    what happened ("even if a key was read"), not about which code path
    noticed -- so an INTEGRITY_VIOLATION with no flag is excluded too, and
    this control would be vacuous if it still used one. The contrast is now an
    ordinary unresolved verdict, which must STILL block.
    """
    r = _reg(falsifier_verdict="UNTOOLABLE")  # not an integrity refusal at all
    assert r.unverified_critical_count() == 1
    cfg = rr.RunnerConfig()
    converged, reason = rr._check_gamma_alt_convergence(
        round_idx=3, gamma=0.432, novel_critical_history=HISTORY, cfg=cfg,
        unresolved_critical=r.unverified_critical_count(), contested=0,
        irreducible_queue=0, gamma_critical=0.336, total_findings=40)
    assert converged is False and "A4 BLOCK" in reason


def test_the_excused_critical_is_reported_rather_than_lost():
    """The part the design brief did not specify, and the reason D2 is safe.

    Both counters let it go. If nothing reported it, a run would converge over
    an untested critical in silence -- a false experimental result.

    AMENDED 2026-10-03. The superseded assertion, preserved verbatim:

        r.entries["C0001"]["status"] = "UNCONFIRMED"
        r.entries["C0001"]["severity"] = 0.3
        assert r.integrity_refused_criticals() == []

    It was wrong for the reason this test's own docstring gives. At status
    UNCONFIRMED the A4 blocker DOES let the entry go -- that counter has had no
    severity gate since 2026-09-06 -- so "both counters let it go and nothing
    reported it" was true of exactly this fixture, and the oracle asserted the
    silence instead of refusing it. Falsifier:
    bench/tests/falsifier_subcritical_refusal_is_silent_2026-10-03.py, executed;
    at severity 0.5 `unverified_critical_count` went 1 -> 0 while this list
    stayed empty.

    The CLOSED case was correct and is unchanged: a terminal entry is in no
    counter's scope, so the report must not name it.
    """
    r = _reg(falsifier_verdict=INTEGRITY_VIOLATION, integrity_refused=True)
    assert r.integrity_refused_criticals() == ["C0001"]
    r.entries["C0001"]["status"] = "CLOSED"
    assert r.integrity_refused_criticals() == []
    r.entries["C0001"]["status"] = "UNCONFIRMED"
    r.entries["C0001"]["severity"] = 0.3
    assert r.unverified_critical_count() == 0, (
        "fixture drift: the A4 blocker no longer drops this entry, so the "
        "assertion below is testing nothing")
    assert r.integrity_refused_criticals() == ["C0001"], (
        "the A4 blocker dropped a sub-critical key-access refusal and no "
        "report names it -- a silent exclusion")
    # Out of BOTH counters' scope (not UNCONFIRMED, not critical): still silent.
    r.entries["C0001"]["status"] = "OPEN"
    assert r.integrity_refused_criticals() == []
    assert _reg().integrity_refused_criticals() == []  # silent when clean


def test_the_round_loop_actually_calls_the_reporter():
    """An addition nothing reaches is not additive. RESOLVE the call site.

    Converted from a substring check 2026-10-02: `"registry.integrity_refused_
    criticals()" in src` passes on a comment, a docstring or a dead branch, and
    fails on a rename of the receiver that changes nothing.
    """
    tree = _runner_tree()
    callers = _calls_named(tree, "integrity_refused_criticals")
    assert callers, (
        "integrity_refused_criticals is defined but CALLED NOWHERE in the "
        "runner; it is an addition nothing reaches")
    # It must be reached from the round loop, not only from its own definition.
    names = {fn.name for fn in callers}
    assert names - {"integrity_refused_criticals"}, (
        f"its only caller is itself: {sorted(names)}")


def test_no_gate_input_moves_with_the_queue_or_the_a4_count():
    """gamma_critical and the zero-new-critical window ARE the gate. Neither is
    derived from the flags this change touches; `irreducible_queue` reaches the
    gate as a NOTE string only."""
    cfg = rr.RunnerConfig()
    verdicts = set()
    for queue in (0, 3, 99):
        conv, reason = rr._check_gamma_alt_convergence(
            round_idx=3, gamma=0.432, novel_critical_history=HISTORY, cfg=cfg,
            unresolved_critical=0, contested=0, irreducible_queue=queue,
            gamma_critical=0.336, total_findings=40)
        verdicts.add(conv)
        if queue > cfg.max_irreducible_queue:
            assert "NOTE: irreducible queue" in reason
    assert verdicts == {True}, (
        "the queue must not change this gate's boolean -- the run-loop alarm "
        "is the halt channel, and D2 touches only that")
    conv, reason = rr._check_gamma_alt_convergence(
        round_idx=3, gamma=0.432, novel_critical_history=HISTORY, cfg=cfg,
        unresolved_critical=0, contested=0, irreducible_queue=0,
        gamma_critical=0.10, total_findings=40)
    assert conv is False, "gamma below threshold must still refuse"


def test_sk_tristate_is_untouched_by_any_of_this():
    """S_k is the second instrument. D1/D2/D3 must leave every byte of it alone."""
    import ast as _ast
    tree = _runner_tree()
    fn = next((n for n in _ast.walk(tree)
               if isinstance(n, (_ast.FunctionDef, _ast.AsyncFunctionDef))
               and n.name == "integrity_refused_criticals"), None)
    assert fn is not None, "the reader is gone"
    # RESOLVED, not sliced: every NAME and ATTRIBUTE the function actually uses.
    used = {getattr(n, "id", None) or getattr(n, "attr", None)
            for n in _ast.walk(fn)}
    leaked = {u for u in used if u and ("sk" == u.lower() or u.lower().startswith("sk_")
                                        or u.lower().endswith("_sk"))}
    assert not leaked, (
        f"the new reader reaches S_k ({sorted(leaked)}): routing and S_k are "
        f"deliberately separated so S_k cannot influence a verdict")
    # And the tristate vocabulary still EXISTS as live constants, resolved by
    # import rather than by looking for the words in the file.
    for state in ("NO_SCORE", "REJECTED", "ADMISSIBLE"):
        assert any(state in str(getattr(rr, n, "")) or getattr(rr, n, None) == state
                   for n in dir(rr)) or state in {
                       c.value for c in _ast.walk(tree)
                       if isinstance(c, _ast.Constant) and isinstance(c.value, str)}, (
            f"S_k tristate vocabulary lost: {state}")


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
