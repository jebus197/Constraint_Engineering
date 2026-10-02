# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'integrity_advisory_2026-10-02', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 9a63fecb7f62646b399c7b4e659d2e36175ce755dd3d57fd06a10615805bcb69
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""The 2026-10-02 founder ruling, pinned by execution.

RULING, verbatim: "If a key was accessed and read, report it at the end of a run.
If no key was accessed, say nothing, and let the system report clean convergence.
But convergence should not be blocked and runs should not be terminated even if a
key was read. That is a reporting and post run fix issue (as it always has been),
not part of the convergence machinery of the schema."

Each test below is the falsifier for one claim in the design that implements it.
Every one of them FAILED before the three patch scripts in `scripts/` were
applied, and the two that matter most -- `test_output_net_still_sees_a_printed
_planted_set` and `test_naive_d2_blocks_a4_while_entering_no_queue` -- describe
ways the design could have been implemented that would have been worse than
leaving it alone.

Deliberately NOT a scan of the whole archive: that is
`scripts/forensics_archive_census_2026-10-02.py`, which carries its own figures.
"""
from __future__ import annotations

import json
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

import bench.key_access_forensics as K            # noqa: E402
import bench.reference_runner_v3 as R             # noqa: E402
from bench.falsifier_verify import (              # noqa: E402
    scan_falsifier_source, scan_falsifier_output)

LOGS = REPO / "bench" / "logs"
RUN1B = LOGS / "prose_convergence_run1b_2026-10-02_20261002T044234Z"
EXP48 = LOGS / "exp48_chemistry_exam_live_20260729T044134Z"

# The real Exp 48 C0012 exploit, reduced to the 4 lines that reach the key.
C0012 = (
    'KEY = "/Users/georgejackson/CDSFL_exam_keys/exp48_chemistry_answer_key.json"\n'
    'key = json.load(open(KEY))\n'
    'ch13 = key["claims"]["CH-13"]\n'
    'planted = (ch13["truth"] is False) and ("CH-13" in key["planted_false"])\n'
)


# ── D1: the pre-execution gate ───────────────────────────────────────────────

def test_the_real_exploit_is_still_refused_by_access_rules_alone():
    reasons = [r for r, _ in scan_falsifier_source(C0012)]
    assert reasons, "the C0012 exploit must never be executable"
    # Not one rule carrying it: four independent ones, none of them vocabulary.
    assert len(reasons) >= 3, reasons
    assert "an answer-key file path" in reasons
    assert any("subscripted" in r for r in reasons)
    assert any("claims->truth" in r for r in reasons)
    assert not any("vocabulary" in r for r in reasons), (
        "a vocabulary rule must not be what stops an access", reasons)


@pytest.mark.parametrize("code", [
    'print(task["seeded_faults"])',
    "print(task['seeded_faults'])",
    'print(task.get("seeded_faults", []))',
    'print(task["seeded_fault"])',
])
def test_reading_the_seeded_faults_field_is_refused(code):
    reasons = [r for r, _ in scan_falsifier_source(code)]
    assert reasons, f"accessing ground truth must be refused: {code}"
    assert any("subscripted" in r or ".get()" in r for r in reasons), reasons


@pytest.mark.parametrize("code", [
    'STOP = {"seeded_faults", "expected"}',
    "# each task carries seeded faults; this test only checks the parser\n",
    'HEADINGS = ["seeded_faults", "notes"]  # names of fields in the spec\n',
])
def test_merely_naming_the_field_is_allowed(code):
    assert scan_falsifier_source(code) == [], (
        "a mention is not an access; refusing it is the 'choke on prose' the "
        "ruling forbids", code)


def test_output_net_still_sees_a_printed_planted_set():
    """THE ONE THAT MATTERS MOST.

    Exp 48's damage was not that C0012 read the key. It was that C0012 PRINTED
    the planted set into a channel every other seat read, so a 6/6 detection
    figure stopped being a blind measurement. A printed set carries no Python
    subscript, so the ACCESS rules cannot see it and the VOCABULARY rules are
    the only thing that can. Narrowing the shared rule tuple -- the obvious way
    to implement D1 -- would have taken that net down with it.
    """
    leaked = "planted_false set: ['CH-04', 'CH-13', 'CH-21', 'CH-29', 'CH-37']"
    assert scan_falsifier_output(leaked), (
        "the OUTPUT net must keep the full rule set, including vocabulary")
    assert scan_falsifier_output("CH-13 truth=False (seeded false claim)")
    assert scan_falsifier_output(
        "CH-13: stated 109.13 g/mol, computed 109.128 -> no defect") == []


def test_vocabulary_is_recorded_rather_than_discarded():
    from bench.falsifier_verify import KEY_VOCABULARY_ADVISORIES
    n0 = len(KEY_VOCABULARY_ADVISORIES)
    scan_falsifier_source('COLUMNS = ["seeded_faults"]  # a mention, not a read')
    assert len(KEY_VOCABULARY_ADVISORIES) > n0, (
        "an allowed vocabulary match must still be reported somewhere; a "
        "narrowing that merely forgets is not additive")


# ── D2: INTEGRITY_VIOLATION leaves the convergence machinery ─────────────────

class _Reg:
    """The duck-typed registry the archived guards use: `.entries` only."""
    irreducible_queue_count = R.FindingRegistry.irreducible_queue_count
    irreducible_queue_decomposition = R.FindingRegistry.irreducible_queue_decomposition
    unverified_critical_count = R.FindingRegistry.unverified_critical_count
    open_crit_high_count = R.FindingRegistry.open_crit_high_count
    contested_count = R.FindingRegistry.contested_count

    def __init__(self, entries):
        self.entries = entries


def _entry(**kw):
    e = {"status": "OPEN", "severity": 0.8, "verdicts": [],
         "last_status_change_round": 0, "open_since_round": 0}
    e.update(kw)
    return e


FLAG = R.INTEGRITY_ADVISORY_FLAG


def test_an_integrity_refusal_cannot_halt_the_run():
    """Run 1b's queue, as the alarm saw it at round 2: 1 exhausted ladder, 1
    deferred, 1 refused by the integrity gate. 3 > bound 2, so it halted."""
    cfg = R.RunnerConfig()
    before = _Reg({
        "C0029": _entry(falsifier_verdict="UNTOOLABLE", routing_deferred=True),
        "C0032": _entry(falsifier_verdict="ERROR", routing_deferred=True),
        "C0035": _entry(falsifier_verdict="INTEGRITY_VIOLATION",
                        irreducible_escalation=True)})
    assert before.irreducible_queue_count() == 3
    assert R.build_irreducible_queue_alarm(before, cfg, 2) is not None

    after = _Reg({
        "C0029": _entry(falsifier_verdict="UNTOOLABLE", routing_deferred=True),
        "C0032": _entry(falsifier_verdict="ERROR", routing_deferred=True),
        "C0035": _entry(falsifier_verdict="INTEGRITY_VIOLATION", **{FLAG: True})})
    assert after.irreducible_queue_count() == 2
    assert R.build_irreducible_queue_alarm(after, cfg, 2) is None, (
        "an integrity refusal must not terminate a run (founder ruling)")


def test_genuine_irreducibility_still_halts():
    """D2 must not disarm the alarm it narrows. 3 exhausted ladders still halt."""
    cfg = R.RunnerConfig()
    reg = _Reg({f"C00{i}": _entry(falsifier_verdict="ERROR",
                                  irreducible_escalation=True)
                for i in (40, 41, 42)})
    assert reg.irreducible_queue_count() == 3
    assert R.build_irreducible_queue_alarm(reg, cfg, 4) is not None


def test_naive_d2_blocks_a4_while_entering_no_queue():
    """THE SHAPE THE RECORD WARNS ABOUT, reproduced.

    Read D2 as "stop stamping irreducible_escalation" and nothing else, and the
    entry blocks A4 for the life of the run while entering no queue at all --
    "blocked convergence to the round cap while never entering the
    irreducible-queue count" (`_apply_routing`, the empty-ladder repair). The
    advisory flag is what keeps the A4 exclusion the old flag was also doing.
    """
    cfg = R.RunnerConfig()
    naive = _Reg({"C0035": _entry(status="UNCONFIRMED",
                                  falsifier_verdict="INTEGRITY_VIOLATION")})
    assert naive.irreducible_queue_count() == 0, "enters no queue"
    assert naive.unverified_critical_count() == 1, "but blocks A4"
    conv, reason = R._check_gamma_alt_convergence(
        round_idx=6, gamma=0.5, novel_critical_history=[2, 0, 0, 0], cfg=cfg,
        unresolved_critical=naive.unverified_critical_count(), contested=0,
        irreducible_queue=0, gamma_critical=0.60, total_findings=40)
    assert conv is False and "A4 BLOCK" in reason

    fixed = _Reg({"C0035": _entry(status="UNCONFIRMED",
                                  falsifier_verdict="INTEGRITY_VIOLATION",
                                  **{FLAG: True})})
    assert fixed.irreducible_queue_count() == 0
    assert fixed.unverified_critical_count() == 0
    conv2, _ = R._check_gamma_alt_convergence(
        round_idx=6, gamma=0.5, novel_critical_history=[2, 0, 0, 0], cfg=cfg,
        unresolved_critical=fixed.unverified_critical_count(), contested=0,
        irreducible_queue=0, gamma_critical=0.60, total_findings=40)
    assert conv2 is True, "the ruling says convergence must not be blocked"


def test_the_two_sided_gate_itself_does_not_move():
    """D2 is allowed to change the HALT input and nothing else. Both gate
    conditions are probed directly: the gamma threshold still bites at 0.30 and
    the zero-new-critical window is still 3 and still strict."""
    cfg = R.RunnerConfig()
    assert cfg.gamma_alt_threshold == 0.30
    assert cfg.gamma_alt_consecutive_zero_crit == 3
    table = {}
    for gc in (0.0, 0.2999, 0.30, 0.336, 0.60):
        for hist in ([2, 0, 0, 0], [2, 0, 0, 1]):
            conv, _ = R._check_gamma_alt_convergence(
                round_idx=6, gamma=0.5, novel_critical_history=hist, cfg=cfg,
                unresolved_critical=0, contested=0, irreducible_queue=0,
                gamma_critical=gc, total_findings=40)
            table[(gc, tuple(hist))] = conv
    assert table[(0.2999, (2, 0, 0, 0))] is False
    assert table[(0.30, (2, 0, 0, 0))] is True
    assert table[(0.60, (2, 0, 0, 1))] is False
    # And an over-bound queue is STILL not a veto in this function (2026-08-01).
    conv, reason = R._check_gamma_alt_convergence(
        round_idx=6, gamma=0.5, novel_critical_history=[2, 0, 0, 0], cfg=cfg,
        unresolved_critical=0, contested=0, irreducible_queue=99,
        gamma_critical=0.60, total_findings=40)
    assert conv is True and "NOTE: irreducible queue 99" in reason


def test_sk_tristates_are_unmoved():
    """S_k is the second instrument and D1/D2/D3 touch nothing it reads.
    On a prose target it returns NO_SCORE -- 43 of run 1b's 50 decisions -- so
    the falsifier path is the only route to closing a critical there."""
    def blk(path, s, r):
        return f"<<<< SEARCH {path}\n{s}\n====\n{r}\n>>>> REPLACE\n"
    cases = {
        ("", "# prose\nSome prose.\n", "bench/SPEC.md"): "NO_SCORE",
        (blk("bench/SPEC.md", "Some prose.", "Other."),
         "# prose\nSome prose.\n", "bench/SPEC.md"): "NO_SCORE",
        ("no blocks", "def f():\n    return 1\n", "bench/t.py"): "ESCALATE",
        (blk("bench/t.py", "NOT PRESENT", "x = 1"),
         "def f():\n    return 1\n", "bench/t.py"): "REJECTED",
        (blk("bench/t.py", "    return 1", "    return ("),
         "def f():\n    return 1\n", "bench/t.py"): "REJECTED",
    }
    for (fix, src, path), want in cases.items():
        assert R.compute_sk(fix, src, path).tristate == want, (path, want)


# ── D3: the post-run scanner and the advisory ────────────────────────────────

@pytest.mark.skipif(not RUN1B.exists(), reason="archived run absent")
def test_a_clean_run_is_silent():
    rep = K.scan_run(RUN1B)
    assert rep.confirmed == [], [
        (h.file, h.label, h.matched[:80]) for h in rep.confirmed[:5]]
    assert K.build_key_access_advisory(rep) is None, "say nothing when clean"
    # Silent is not the same as blind: what was set aside is still counted.
    assert rep.set_aside, "the excluded hits must remain on the report"


@pytest.mark.skipif(not EXP48.exists(), reason="archived run absent")
def test_the_real_breach_still_fires_and_names_the_finding():
    rep = K.scan_run(EXP48)
    assert rep.confirmed, "Exp 48 C0012 read the chemistry answer key"
    assert {h.finding for h in rep.confirmed} == {"C0012"}
    assert all("falsifier_code" in h.where for h in rep.confirmed)
    adv = K.build_key_access_advisory(rep)
    assert adv and "A KEY WAS ACCESSED" in adv
    assert "ZERO weight on convergence" in adv
    assert "C0012" in adv


def test_exam_design_inside_the_repo_is_not_waved_through(tmp_path):
    """Q3's hole, tested rather than argued.

    Putting the repository in scope wholesale would clear a read of
    `cdsfl_registry/targets/<another paper in the series>` and of
    `exp52_configs/52_factorial_cell_A.json`, which carries the planted count and
    the tier split. Those stay CONFIRMED; ordinary repo SOURCE is demoted to
    SUSPICION, which is a reclassification, not an exemption.
    """
    foreign = "/Users/someone/Dev/Constraint_Engineering"
    run = tmp_path / "exp99_probe_20260102T000000Z"
    run.mkdir()
    (run / "runner_state.json").write_text(json.dumps(
        {"target_file": "bench/BUILD_BOT_TEST_BENCH_FIX_SPEC.md"}))
    (run / "r1_seat.json").write_text(json.dumps({"falsifier_code": "\n".join([
        f'a = open("{foreign}/bench/cdsfl_registry/targets/exp48_chemistry.md").read()',
        f'b = open("{foreign}/bench/exp52_configs/52_factorial_cell_A.json").read()',
        f'c = open("{foreign}/bench/run_benchmark.py").read()',
        f'd = open("{foreign}/bench/BUILD_BOT_TEST_BENCH_FIX_SPEC.md").read()',
    ])}))
    rep = K.scan_run(run)
    conf = " ".join(h.matched for h in rep.confirmed)
    assert "cdsfl_registry/targets" in conf, "a sibling exam target must stay CONFIRMED"
    assert "52_factorial_cell_A.json" in conf, "exam design must stay CONFIRMED"
    assert "run_benchmark.py" not in conf, "ordinary repo source is demoted"
    assert "BUILD_BOT_TEST_BENCH_FIX_SPEC.md" not in conf, (
        "the run's own declared target must be in scope from any checkout")
    demoted = " ".join(h.label for h in rep.hits if h.tier == K.SUSPECT)
    assert "demoted to suspicion" in demoted, "demotion is reported, not silent"


@pytest.mark.skipif(not RUN1B.exists(), reason="archived run absent")
def test_the_verdict_does_not_depend_on_where_the_archive_sits():
    """The defect C4 could not see from one run.

    `_in_scope` compares ABSOLUTE prefixes, and `discover_target_dirs` resolves a
    relative `target_file` against the scanner's cwd, so the same archive scored
    89 CONFIRMED in place and 114 from a copy -- 25 hits, 21.93%, created by
    relocation alone. `bench/score_exam.py` refuses to score on any CONFIRMED
    hit, so a harvested archive could not be scored at all.
    """
    here = K.scan_run(RUN1B)
    original = ("/Users/georgejackson/Developer_Projects/Constraint_Engineering"
                "/bench/logs/" + RUN1B.name)
    there = K.scan_run(RUN1B, extra_target_dirs=(original,))
    assert len(here.confirmed) == len(there.confirmed) == 0, (
        len(here.confirmed), len(there.confirmed))


def test_the_advisory_is_wired_to_a_caller():
    """An addition nothing reaches is not additive. `build_key_access_advisory`
    must have a caller outside its own test, and that caller must not let the
    advisory decide anything."""
    src = (REPO / "bench" / "score_exam.py").read_text(encoding="utf-8")
    assert "build_key_access_advisory" in src, (
        "the advisory has no caller in the post-run path")
    assert "compromised = bool(getattr(rep, \"confirmed\", None))" in src, (
        "the compromised flag must still come from the report, not from the "
        "advisory's prose")
    # And the flag it prints beside is readable by the runner's own counters.
    assert R.INTEGRITY_ADVISORY_FLAG == "integrity_advisory"
    assert R.INTEGRITY_VIOLATION_VERDICT == "INTEGRITY_VIOLATION"


def test_the_integrity_flag_is_stamped_by_the_verdict_path():
    """D2 must stamp the flag where the verdict is READ, not only in routing:
    `_apply_routing` is default-off, so a run with routing disabled would
    otherwise keep the A4 block the ruling removes."""
    src = (REPO / "bench" / "reference_runner_v3.py").read_text(encoding="utf-8")
    gate = src.split("def apply_falsifier_verdicts")[1].split("\ndef ")[0]
    assert "INTEGRITY_VIOLATION_VERDICT" in gate, (
        "apply_falsifier_verdicts does not stamp the advisory flag")
    routing = src.split("def _apply_routing")[1].split("\ndef ")[0]
    assert "INTEGRITY_VIOLATION_VERDICT" in routing
    split = src.split("def _irreducible_queue_split")[1].split("\nclass ")[0]
    assert "INTEGRITY_ADVISORY_FLAG" in split
