"""A falsifier can be valid, runnable code and still test nothing.

FOUNDER RULING, 2026-08-08 — the DECISIVE form of the false-CONFIRMED control.

THE PROBLEM. `reverify_falsifier` answers "did this code fire" and answers it
correctly. It cannot answer "did it fire BECAUSE OF THE CLAIM", and nothing in
the gate ever asked. C0012 is the archived instance: it fired because it read a
file, not because the chemistry was wrong. The runner saw it fire, marked the
finding CONFIRMED, and closed it AGAINST A CLAIM THAT IS TRUE.

THE TEST. Run the SAME falsifier a second time against a CORRECTED copy of the
target — one where the claim in question has been fixed. A sound falsifier must
now go QUIET. If it STILL FIRES, it is not testing that claim at all.

THREE OUTCOMES, and the third is the founder's refinement and matters most:
  * quiet on the corrected copy -> it discriminates -> CONFIRMED stands.
  * fires on the corrected copy -> IT DISCRIMINATES NOTHING. The finding is not
    closed, and the result is recorded as a MECHANICAL FAULT: "Machinery that
    highlights an established truth as a fault, is something that may indeed
    warrant our attention." Diagnostic output about the INSTRUMENT, not merely a
    veto of one finding.
  * ERRORS on the corrected copy -> cannot tell -> escalate, but DO NOT veto. An
    error is not evidence. "Fires on both" and "crashed" must never render
    identically; that distinction is this project's single most repeated lesson.

WHAT THIS FILE PINS. Every branch above, each proved to take the right path by
running real falsifiers against real files in a real sandbox — no mocking of the
decision, because a mocked sandbox would prove only that the test author agrees
with themselves. Plus the two properties that make the rule safe to promote at
all: a sound falsifier is completely unaffected, and the measured count of
archived findings that would newly fail to close is ZERO.

THE APPARATUS PROVES ITSELF FIRST, and that is tested too. A falsifier that
never reads the target would run against the ORIGINAL file on both passes, fire
twice, and mint a FALSE mechanical fault against a sound instrument — the exact
house failure mode, a failure rendering as a confident success. The control
measures interception, determinism and baseline faithfulness before it is
allowed to say anything, and each of those refusals is pinned here as its own
distinct outcome.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bench.reference_runner_v2 import (  # noqa: E402
    DISC_ABSENT,
    DISC_BASELINE,
    DISC_COPY_UNCHANGED,
    DISC_ERROR,
    DISC_FAILED,
    DISC_INDETERMINATE,
    DISC_NONDETERMINISTIC,
    DISC_NOT_INTERCEPTED,
    DISC_PASSED,
    FindingRegistry,
    RunnerConfig,
    _rejection_lines,
    _retarget_falsifier,
    apply_falsifier_verdicts,
    run_discrimination_control,
)

REPO = Path(__file__).resolve().parents[2]


# ─────────────────────────────────────────────────────────────────────────────
# A miniature repository, so the control is exercised end to end without the
# tests writing anything into the real tree.
# ─────────────────────────────────────────────────────────────────────────────

TARGET_REL = "pkg/spec.py"

DEFECTIVE = '''\
"""Reference values for the SW-21 assembly."""

LEGACY_TABLE = {"rev": "A"}


def clearance_mm():
    # The retracted value. This is the claim under test.
    return 0.29
'''

CORRECTED = '''\
"""Reference values for the SW-21 assembly."""

LEGACY_TABLE = {"rev": "A"}


def clearance_mm():
    # Corrected to the current specification.
    return 0.31
'''

# A corrected copy that also drops a symbol the falsifier imports. This is the
# shape that killed the "synthesise the corrected copy from the model's fix"
# route: the falsifier CRASHES, the crash reads as "still fires", and a genuine
# defect is silently un-confirmed.
CORRECTED_BUT_BREAKS_THE_FALSIFIER = '''\
"""Reference values for the SW-21 assembly."""


def clearance_mm():
    return 0.31
'''

# Fires if and only if the retracted clearance is still stated. The sound one.
SOUND_FALSIFIER = (
    "from pkg.spec import clearance_mm\n"
    "assert clearance_mm() != 0.29, 'the retracted 0.29 mm clearance is still stated'\n"
)

# The C0012 shape: it reaches the target, it runs, it fires — and it fires
# because the file is non-empty, which has nothing to do with the clearance.
NON_DISCRIMINATING_FALSIFIER = (
    "from pathlib import Path\n"
    "import pkg.spec as _s\n"
    "src = Path(_s.__file__).read_text(encoding='utf-8')\n"
    "assert not src.strip(), 'the specification is defective'\n"
)

# Sound against the target, but it also imports a symbol the corrected copy
# removes, so against that copy it crashes instead of deciding.
FRAGILE_FALSIFIER = (
    "from pkg.spec import clearance_mm, LEGACY_TABLE\n"
    "assert LEGACY_TABLE['rev'] == 'A'\n"
    "assert clearance_mm() != 0.29, 'the retracted 0.29 mm clearance is still stated'\n"
)

# Never reads the target at all. Fires on everything, everywhere.
BLIND_FALSIFIER = "assert 1 == 2, 'the specification is wrong'\n"

# Reaches the target, fires — and prints something different every run.
UNSTABLE_FALSIFIER = (
    "import random\n"
    "import pkg.spec as _s\n"
    "print('probe', random.random(), _s.clearance_mm())\n"
    "assert False, 'the specification is wrong'\n"
)

# Exits clean: it does not fire at all, so the control's own baseline check must
# refuse to proceed rather than compare two silences.
SILENT_FALSIFIER = (
    "import pkg.spec as _s\n"
    "print('checked', _s.clearance_mm())\n"
)


@pytest.fixture
def mini_repo(tmp_path):
    """A repo root containing the target, some siblings, and nothing else."""
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "__init__.py").write_text("", encoding="utf-8")
    (tmp_path / "pkg" / "spec.py").write_text(DEFECTIVE, encoding="utf-8")
    (tmp_path / "pkg" / "unrelated.py").write_text("VALUE = 1\n", encoding="utf-8")
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "notes.md").write_text("# notes\n", encoding="utf-8")
    (tmp_path / "README.md").write_text("mini\n", encoding="utf-8")
    return tmp_path


def _control(mini_repo, falsifier, corrected, **extra):
    entry = {"severity": 0.85, "falsifier_code": falsifier,
             "corrected_copy": corrected, "description": "clearance is retracted"}
    entry.update(extra)
    return entry, run_discrimination_control(
        entry, repo_root=str(mini_repo), target_rel=TARGET_REL, timeout=60)


# ─────────────────────────────────────────────────────────────────────────────
# THE THREE OUTCOMES
# ─────────────────────────────────────────────────────────────────────────────

class TestTheThreeOutcomes:
    def test_quiet_on_the_corrected_copy_means_it_discriminates(self, mini_repo):
        _e, rec = _control(mini_repo, SOUND_FALSIFIER, CORRECTED)
        assert rec["outcome"] == DISC_PASSED, rec
        assert rec["baseline_verdict"] == "CONFIRMED", (
            "the falsifier must still fire against an UNCHANGED copy, or the "
            "control is measuring its own apparatus")
        assert rec["corrected_verdict"] == "REFUTED"
        assert rec["intercepted"] is True
        assert rec["deterministic"] is True

    def test_fires_on_the_corrected_copy_means_it_discriminates_nothing(self, mini_repo):
        _e, rec = _control(mini_repo, NON_DISCRIMINATING_FALSIFIER, CORRECTED)
        assert rec["outcome"] == DISC_FAILED, rec
        assert rec["baseline_verdict"] == "CONFIRMED"
        assert rec["corrected_verdict"] == "CONFIRMED", (
            "the point of the case: the runner's own re-run says CONFIRMED "
            "against a copy in which the claim is FIXED")
        assert rec["intercepted"] is True

    def test_the_mechanical_fault_is_reported_as_an_instrument_diagnosis(self, mini_repo):
        """The founder's refinement, and the reason the third outcome exists."""
        _e, rec = _control(mini_repo, NON_DISCRIMINATING_FALSIFIER, CORRECTED)
        assert "Machinery that highlights an established truth as a fault" in rec["detail"], (
            "the finding is not merely vetoed — the INSTRUMENT is the diagnosis, "
            "and the founder's framing is what says so")

    def test_errors_on_the_corrected_copy_cannot_tell_and_must_not_veto(self, mini_repo):
        _e, rec = _control(mini_repo, FRAGILE_FALSIFIER,
                           CORRECTED_BUT_BREAKS_THE_FALSIFIER)
        assert rec["outcome"] == DISC_ERROR, rec
        assert rec["corrected_verdict"] == "ERROR"
        assert "not evidence" in rec["detail"]

    def test_fires_on_both_and_crashed_never_render_identically(self, mini_repo):
        """This project's single most repeated lesson, asserted directly."""
        _e1, fired = _control(mini_repo, NON_DISCRIMINATING_FALSIFIER, CORRECTED)
        _e2, crashed = _control(mini_repo, FRAGILE_FALSIFIER,
                                CORRECTED_BUT_BREAKS_THE_FALSIFIER)
        assert fired["outcome"] != crashed["outcome"]
        assert fired["detail"] != crashed["detail"]
        assert DISC_FAILED not in DISC_INDETERMINATE
        assert DISC_ERROR in DISC_INDETERMINATE


# ─────────────────────────────────────────────────────────────────────────────
# THE APPARATUS PROVES ITSELF BEFORE IT REPORTS
# ─────────────────────────────────────────────────────────────────────────────

class TestTheControlRefusesToSpeakWhenItCannotSee:
    def test_a_falsifier_that_never_reads_the_target_is_not_a_mechanical_fault(
            self, mini_repo):
        """The trap that would have made this control worse than useless.

        BLIND_FALSIFIER genuinely discriminates nothing. But the control cannot
        DEMONSTRATE that by swapping the target, because the falsifier never
        reads it — so a naive implementation would run it against the original
        twice, see it fire twice, and stamp a MECHANICAL FAULT it had not
        earned. Every such stamp would be a false accusation against a possibly
        sound instrument, and the record would not say so.
        """
        _e, rec = _control(mini_repo, BLIND_FALSIFIER, CORRECTED)
        assert rec["outcome"] == DISC_NOT_INTERCEPTED, rec
        assert rec["intercepted"] is False
        assert rec["outcome"] != DISC_FAILED
        assert "NOT a finding against the falsifier" in rec["detail"]

    def test_module_paths_from_the_overlay_are_not_mistaken_for_interception(
            self, mini_repo):
        """The subtlest way this control could accuse a sound instrument.

        Every import resolves through the overlay, so ANY falsifier that prints
        a module path prints a run-specific temporary directory. Two overlays
        are two different directories, so a naive comparison would call every
        such falsifier "intercepted" — including this one, which never reads the
        target at all — and the corrected-copy run would then stamp a mechanical
        fault it had not earned.
        """
        falsifier = (
            "import pkg.unrelated as _u\n"
            "print('resolved from', _u.__file__)\n"
            "assert 1 == 2, 'the specification is wrong'\n"
        )
        entry = {"severity": 0.85, "falsifier_code": falsifier,
                 "corrected_copy": CORRECTED}
        rec = run_discrimination_control(entry, repo_root=str(mini_repo),
                                         target_rel=TARGET_REL, timeout=60)
        assert rec["intercepted"] is False, rec
        assert rec["outcome"] == DISC_NOT_INTERCEPTED, rec

    def test_an_unstable_falsifier_is_refused_rather_than_compared(self, mini_repo):
        _e, rec = _control(mini_repo, UNSTABLE_FALSIFIER, CORRECTED)
        assert rec["outcome"] == DISC_NONDETERMINISTIC, rec
        assert rec["deterministic"] is False

    def test_a_falsifier_that_does_not_fire_at_all_fails_the_baseline(self, mini_repo):
        """If it does not reproduce CONFIRMED here, the apparatus is not faithful."""
        _e, rec = _control(mini_repo, SILENT_FALSIFIER, CORRECTED)
        assert rec["outcome"] == DISC_BASELINE, rec
        assert rec["baseline_verdict"] == "REFUTED"
        assert rec["corrected_verdict"] == "", (
            "no comparison may be attempted once the baseline is unfaithful")

    def test_an_unchanged_corrected_copy_is_refused_rather_than_scored(self, mini_repo):
        """MEASURED 2026-08-08 and this is why the guard exists: with the
        "corrected" copy set to the target's own unchanged text, 12 of 12
        archived CONFIRMED falsifiers came back NO_DISCRIMINATION — every one of
        them a sound instrument. A panel that echoes the target back would mint
        mechanical faults wholesale, and each one would read as a confident
        finding about a healthy tool."""
        _e, rec = _control(mini_repo, SOUND_FALSIFIER, DEFECTIVE)
        assert rec["outcome"] == DISC_COPY_UNCHANGED, rec
        assert rec["outcome"] != DISC_FAILED
        assert "nothing was corrected" in rec["detail"]

    def test_a_copy_that_differs_only_cosmetically_still_reports_no_discrimination(
            self, mini_repo):
        """The honest boundary of the guard: byte equality is decidable, "fixes
        the wrong claim" is not. A cosmetically-different copy passes the guard
        and the sound falsifier then fires, which the control reports as a
        mechanical fault — correctly, on the evidence it was given, and wrongly
        about the instrument. The corrected copy is load-bearing input and this
        test records that it is trusted."""
        _e, rec = _control(mini_repo, SOUND_FALSIFIER,
                           DEFECTIVE + "\n# cosmetic change only\n")
        assert rec["outcome"] == DISC_FAILED, rec

    def test_a_missing_target_yields_an_error_not_a_pass(self, mini_repo):
        entry = {"severity": 0.85, "falsifier_code": SOUND_FALSIFIER,
                 "corrected_copy": CORRECTED}
        rec = run_discrimination_control(
            entry, repo_root=str(mini_repo), target_rel="pkg/absent.py", timeout=60)
        assert rec["outcome"] == DISC_ERROR, rec
        assert rec["outcome"] not in (DISC_PASSED, DISC_FAILED)

    def test_an_absolute_target_path_is_refused_rather_than_guessed(self, mini_repo):
        entry = {"severity": 0.85, "falsifier_code": SOUND_FALSIFIER,
                 "corrected_copy": CORRECTED}
        rec = run_discrimination_control(
            entry, repo_root=str(mini_repo),
            target_rel=str(mini_repo / TARGET_REL), timeout=60)
        assert rec["outcome"] == DISC_ERROR, rec

    def test_the_overlay_leaves_the_real_tree_untouched(self, mini_repo):
        before = (mini_repo / TARGET_REL).read_text(encoding="utf-8")
        sibling = (mini_repo / "pkg" / "unrelated.py").read_text(encoding="utf-8")
        names = sorted(p.name for p in mini_repo.rglob("*"))
        _control(mini_repo, NON_DISCRIMINATING_FALSIFIER, CORRECTED)
        assert (mini_repo / TARGET_REL).read_text(encoding="utf-8") == before
        assert (mini_repo / "pkg" / "unrelated.py").read_text(encoding="utf-8") == sibling, (
            "the overlay mirrors siblings as symlinks; tearing it down must "
            "remove the links, never what they point at")
        assert sorted(p.name for p in mini_repo.rglob("*")) == names

    def test_a_falsifier_that_writes_cannot_reach_the_real_target(self, mini_repo):
        """The overlay strictly REDUCES exposure: the file the falsifier is most
        likely to touch is the one it can no longer touch."""
        falsifier = (
            "from pathlib import Path\n"
            "import pkg.spec as _s\n"
            "Path(_s.__file__).write_text('WIPED\\n', encoding='utf-8')\n"
            "assert False, 'the specification is wrong'\n"
        )
        before = (mini_repo / TARGET_REL).read_text(encoding="utf-8")
        entry = {"severity": 0.85, "falsifier_code": falsifier,
                 "corrected_copy": CORRECTED}
        run_discrimination_control(entry, repo_root=str(mini_repo),
                                   target_rel=TARGET_REL, timeout=60)
        assert (mini_repo / TARGET_REL).read_text(encoding="utf-8") == before

    def test_sandbox_path_noise_is_not_mistaken_for_instability(self, mini_repo):
        """The determinism probe runs in two DIFFERENT throwaway directories, so
        it also validates the output normaliser: if temp-path noise survived
        normalisation, every falsifier would look nondeterministic and the
        control would never speak at all."""
        falsifier = (
            "import pkg.spec as _s\n"
            "print('running from', __file__)\n"
            "assert _s.clearance_mm() != 0.29, 'the retracted clearance is stated'\n"
        )
        entry = {"severity": 0.85, "falsifier_code": falsifier,
                 "corrected_copy": CORRECTED}
        rec = run_discrimination_control(entry, repo_root=str(mini_repo),
                                         target_rel=TARGET_REL, timeout=60)
        assert rec["deterministic"] is True, rec
        assert rec["outcome"] == DISC_PASSED, rec


class TestAbsolutePathFalsifiersAreRedirected:
    """A prose falsifier opens its target by absolute path; PYTHONPATH cannot
    redirect that, so the control substitutes the repo root. The substitution is
    never trusted on its own — the interception probe measures whether it was
    load-bearing — but it must work, or the whole prose class is uncontrollable."""

    def test_an_absolute_path_falsifier_is_controlled_end_to_end(self, mini_repo):
        abs_target = str(mini_repo / TARGET_REL)
        falsifier = (
            f"doc = open({abs_target!r}, encoding='utf-8').read()\n"
            "assert 'return 0.29' not in doc, 'the retracted clearance is still stated'\n"
        )
        entry = {"severity": 0.85, "falsifier_code": falsifier,
                 "corrected_copy": CORRECTED}
        rec = run_discrimination_control(
            entry, repo_root=str(mini_repo), target_rel=TARGET_REL, timeout=60)
        assert rec["outcome"] == DISC_PASSED, rec
        assert rec["retarget_substitutions"] >= 1

    def test_retargeting_reports_zero_when_there_is_nothing_to_redirect(self, mini_repo):
        code, n = _retarget_falsifier(SOUND_FALSIFIER, mini_repo, Path("/nowhere"))
        assert n == 0 and code == SOUND_FALSIFIER


# ─────────────────────────────────────────────────────────────────────────────
# THE GATE: a veto ESCALATES, never deletes
# ─────────────────────────────────────────────────────────────────────────────

def _registry_with(cid, entry):
    reg = FindingRegistry()
    entry.setdefault("canonical_id", cid)
    entry.setdefault("status", "OPEN")
    entry.setdefault("verdicts", [])
    entry.setdefault("source_model", "CC2-SIM")
    entry.setdefault("open_since_round", 0)
    entry.setdefault("last_status_change_round", 0)
    reg.entries[cid] = entry
    return reg


def _gate(mini_repo, falsifier, corrected, severity=0.85, blocks=True):
    """Drive the gate. ``blocks`` selects whether the control is ARMED.

    Added 2026-08-12 with `discrimination_control_blocks`, which defaults OFF.
    The control always runs and records; whether a non-discriminating falsifier
    is REFUSED the right to close a critical is a separate, founder-owned
    decision, because it changes CONFIRM-only. The tests below that assert a
    blocked closure therefore arm it explicitly; `TestDefaultIsRecordNotBlock`
    covers the shipped default.
    """
    entry = {"severity": severity, "falsifier_code": falsifier,
             "description": "the stated clearance is the retracted value"}
    if corrected is not None:
        entry["corrected_copy"] = corrected
    reg = _registry_with("C0001", entry)
    cfg = RunnerConfig(test_article=TARGET_REL, falsifier_gate_enabled=True,
                       discrimination_control_blocks=blocks)
    apply_falsifier_verdicts(reg, 3, cfg=cfg, repo_root=str(mini_repo))
    return reg, reg.entries["C0001"]


class TestDefaultIsRecordNotBlock:
    """Shipped default: the instrument is connected, not armed.

    The wiring that supplies a corrected copy and the decision to act on one are
    different decisions. Arming by default would have settled an open founder
    ruling as a side effect of connecting the supply side — and the panel review
    of 2026-08-12 refuted the blocking design as proposed, on the grounds that it
    tests ACCESS rather than DEPENDENCE and is defeated by opening the target and
    discarding the contents, while reporting full coverage.
    """

    def test_a_non_discriminating_falsifier_still_closes_by_default(self, mini_repo):
        _reg, e = _gate(mini_repo, NON_DISCRIMINATING_FALSIFIER, CORRECTED, blocks=False)
        assert e["verified"] is True, (
            "with blocking off the verdict must be untouched — recording an "
            "observation must never change an outcome")
        assert e["status"] == "CONFIRMED"

    def test_the_observation_is_still_recorded_when_not_blocking(self, mini_repo):
        """Recording is the whole point: it is the evidence the ruling needs."""
        _reg, e = _gate(mini_repo, NON_DISCRIMINATING_FALSIFIER, CORRECTED, blocks=False)
        assert e.get("discrimination", {}).get("outcome") == DISC_FAILED, (
            "the control must still run and record, or there is no evidence on "
            "which to decide whether to arm it")

    def test_arming_it_changes_the_outcome_and_nothing_else_does(self, mini_repo):
        """The flag is the only difference between the two behaviours."""
        _r_off, off = _gate(mini_repo, NON_DISCRIMINATING_FALSIFIER, CORRECTED, blocks=False)
        _r_on, on = _gate(mini_repo, NON_DISCRIMINATING_FALSIFIER, CORRECTED, blocks=True)
        assert off["verified"] is True and on.get("verified") is False
        assert off.get("discrimination", {}).get("outcome") == \
               on.get("discrimination", {}).get("outcome") == DISC_FAILED

    def test_a_sound_falsifier_is_unaffected_either_way(self, mini_repo):
        for blocks in (False, True):
            _reg, e = _gate(mini_repo, SOUND_FALSIFIER, CORRECTED, blocks=blocks)
            assert e["status"] == "CONFIRMED" and e["verified"] is True, (
                f"a discriminating falsifier must close regardless of the flag "
                f"(blocks={blocks})")

    def test_the_flag_defaults_off_on_the_config_itself(self):
        assert RunnerConfig().discrimination_control_blocks is False
        assert RunnerConfig().discrimination_control_ask is False


class TestTheGateAppliesTheControl:
    def test_a_sound_falsifier_still_closes_exactly_as_before(self, mini_repo):
        _reg, e = _gate(mini_repo, SOUND_FALSIFIER, CORRECTED)
        assert e["status"] == "CONFIRMED"
        assert e["verified"] is True
        assert e["falsifier_verdict"] == "CONFIRMED"
        assert not e.get("escalated")
        assert not e.get("mechanical_fault")
        assert e["discrimination"]["outcome"] == DISC_PASSED

    def test_a_non_discriminating_falsifier_does_not_close_the_finding(self, mini_repo):
        reg, e = _gate(mini_repo, NON_DISCRIMINATING_FALSIFIER, CORRECTED)
        assert e.get("verified") is False, (
            "verified=True is what lets _update_finding_statuses close it next "
            "round; withholding it is what keeps the finding out of CLOSED")
        assert e["status"] not in ("CONFIRMED", "CLOSED")
        assert e["falsifier_verdict"] == "NON_DISCRIMINATING"
        assert e["mechanical_fault"] is True
        assert reg.open_crit_high_count() == 1, (
            "the claim is still an unresolved critical and must stay visible to "
            "the convergence machinery, not vanish into a quiet status")

    def test_a_vote_confirmed_critical_is_demoted_exactly_as_the_gate_does(
            self, mini_repo):
        """The gate's own escalation rule, reused rather than re-invented: a
        vote-CONFIRMED critical that the tools do not resolve is demoted to
        UNCONFIRMED and escalated. A discrimination failure is that same
        condition — the demonstration was withdrawn — so it takes the same path
        and lands in the same queue a human already reads."""
        entry = {"severity": 0.85, "falsifier_code": NON_DISCRIMINATING_FALSIFIER,
                 "corrected_copy": CORRECTED, "description": "d",
                 "status": "CONFIRMED"}
        reg = _registry_with("C0001", entry)
        cfg = RunnerConfig(test_article=TARGET_REL, falsifier_gate_enabled=True,
                           discrimination_control_blocks=True)
        apply_falsifier_verdicts(reg, 3, cfg=cfg, repo_root=str(mini_repo))
        e = reg.entries["C0001"]
        assert e["status"] == "UNCONFIRMED"
        assert reg.unverified_critical_count() == 1, (
            "it must land in the queue that blocks the convergence count, "
            "exactly as any other un-demonstrated critical does")

    def test_the_veto_escalates_and_never_deletes(self, mini_repo):
        """CONFIRM-only is the most load-bearing rule here and this is the first
        mechanism that can un-confirm anything. It must fail toward the human."""
        reg, e = _gate(mini_repo, NON_DISCRIMINATING_FALSIFIER, CORRECTED)
        assert "C0001" in reg.entries, "the finding is never removed"
        assert e["status"] not in ("REFUTED", "CLOSED", "DUPLICATE", "MERGED"), (
            "no terminal disposition may be reached by a discrimination failure")
        assert e["severity"] == 0.85, "severity is never silently lowered"
        assert e["description"], "the claim itself is untouched"
        assert e["escalated"] is True and e["hil_escalated"] is True
        assert "MECHANICAL FAULT" in e["hil_reason"]

    def test_an_indeterminate_control_does_not_veto_anything(self, mini_repo):
        _reg, e = _gate(mini_repo, FRAGILE_FALSIFIER,
                        CORRECTED_BUT_BREAKS_THE_FALSIFIER)
        assert e["status"] == "CONFIRMED", "an error is not evidence"
        assert e["verified"] is True
        assert e["falsifier_verdict"] == "CONFIRMED"
        assert e["discrimination"]["outcome"] == DISC_ERROR
        assert e["discrimination_indeterminate"] is True
        assert e.get("mechanical_fault") is not True

    def test_a_blind_falsifier_is_flagged_but_still_closes(self, mini_repo):
        _reg, e = _gate(mini_repo, BLIND_FALSIFIER, CORRECTED)
        assert e["status"] == "CONFIRMED"
        assert e["discrimination"]["outcome"] == DISC_NOT_INTERCEPTED
        assert e["discrimination_indeterminate"] is True

    def test_the_record_survives_in_every_outcome(self, mini_repo):
        """Founder ruling: extend `_record_computed_evidence`, do not build a
        parallel channel — the detective record is preserved in ALL outcomes."""
        for falsifier, corrected, outcome in (
            (SOUND_FALSIFIER, CORRECTED, DISC_PASSED),
            (NON_DISCRIMINATING_FALSIFIER, CORRECTED, DISC_FAILED),
            (FRAGILE_FALSIFIER, CORRECTED_BUT_BREAKS_THE_FALSIFIER, DISC_ERROR),
            (BLIND_FALSIFIER, CORRECTED, DISC_NOT_INTERCEPTED),
        ):
            _reg, e = _gate(mini_repo, falsifier, corrected)
            ce = e.get("computed_evidence") or []
            kinds = [c["kind"] for c in ce]
            assert f"discrimination_control:{outcome}" in kinds, (outcome, kinds)
            assert ce[-1]["falsifier_code"], "the falsifier travels with the record"
            assert e["hil_has_computed_evidence"] is True

    def test_a_crash_inside_the_control_neither_kills_the_round_nor_passes(
            self, mini_repo, monkeypatch):
        """The house failure mode, applied to the control itself. It must not be
        able to take a round down, and it must not be able to go quiet."""
        import bench.reference_runner_v2 as rr
        monkeypatch.setattr(rr, "run_discrimination_control",
                            lambda *a, **k: (_ for _ in ()).throw(
                                RuntimeError("apparatus exploded")))
        _reg, e = _gate(mini_repo, SOUND_FALSIFIER, CORRECTED)
        assert e["discrimination"]["outcome"] == DISC_ERROR
        assert "apparatus exploded" in e["discrimination"]["detail"]
        assert e["status"] == "CONFIRMED" and e["verified"] is True, (
            "a broken control vetoes nothing")
        assert e.get("mechanical_fault") is not True

    def test_the_control_is_not_re_run_on_an_unchanged_pair(self, mini_repo):
        entry = {"severity": 0.85, "falsifier_code": SOUND_FALSIFIER,
                 "corrected_copy": CORRECTED, "description": "d"}
        reg = _registry_with("C0001", entry)
        cfg = RunnerConfig(test_article=TARGET_REL, falsifier_gate_enabled=True,
                           discrimination_control_blocks=True)
        apply_falsifier_verdicts(reg, 3, cfg=cfg, repo_root=str(mini_repo))
        first = dict(reg.entries["C0001"]["discrimination"])
        apply_falsifier_verdicts(reg, 4, cfg=cfg, repo_root=str(mini_repo))
        assert reg.entries["C0001"]["discrimination"]["round"] == first["round"], (
            "an unchanged (falsifier, corrected copy) pair cannot change its own "
            "answer, and re-running it costs four sandbox executions a round")
        assert len(reg.entries["C0001"]["computed_evidence"]) == 1

    def test_a_cached_mechanical_fault_is_re_applied_not_just_remembered(
            self, mini_repo):
        """The drift the cache introduced, and the reason it is not an early
        return. The gate rewrites `falsifier_verdict` to CONFIRMED at the top of
        EVERY round before the control is consulted. A cache that short-circuits
        would leave a known non-discriminating falsifier stamped CONFIRMED —
        which is precisely the stamp the routing ladder reads to decide a
        finding needs no further work, and precisely the state this control
        exists to prevent."""
        entry = {"severity": 0.85, "falsifier_code": NON_DISCRIMINATING_FALSIFIER,
                 "corrected_copy": CORRECTED, "description": "d"}
        reg = _registry_with("C0001", entry)
        cfg = RunnerConfig(test_article=TARGET_REL, falsifier_gate_enabled=True,
                           discrimination_control_blocks=True)
        apply_falsifier_verdicts(reg, 3, cfg=cfg, repo_root=str(mini_repo))
        apply_falsifier_verdicts(reg, 4, cfg=cfg, repo_root=str(mini_repo))
        e = reg.entries["C0001"]
        assert e["falsifier_verdict"] == "NON_DISCRIMINATING", (
            "a cached fault must still be stamped on the entry every round")
        assert e["verified"] is False
        assert e["mechanical_fault"] is True
        assert len(e["computed_evidence"]) == 1, (
            "the measurement is recorded once, not once per round")
        assert e["discrimination"]["round"] == 3, "and it was not re-measured"

    def test_across_realistic_rounds_the_fault_never_reaches_closed(self, mini_repo):
        """The property the whole mechanism exists for, in the real round order.

        `_update_finding_statuses` runs FIRST each round and closes anything
        CONFIRMED-and-verified. The control's only lever is withholding
        `verified`, and it has exactly one round in which to pull it. This drives
        three rounds in the runner's own order and asserts the finding is still
        open to a human at the end.
        """
        from bench.reference_runner_v2 import _update_finding_statuses
        entry = {"severity": 0.85, "falsifier_code": NON_DISCRIMINATING_FALSIFIER,
                 "corrected_copy": CORRECTED, "description": "d"}
        reg = _registry_with("C0001", entry)
        cfg = RunnerConfig(test_article=TARGET_REL, falsifier_gate_enabled=True,
                           discrimination_control_blocks=True)
        for rnd in (1, 2, 3):
            _update_finding_statuses(reg, rnd, cfg=cfg)
            apply_falsifier_verdicts(reg, rnd, cfg=cfg, repo_root=str(mini_repo))
            assert reg.entries["C0001"]["status"] != "CLOSED", f"closed at round {rnd}"
        e = reg.entries["C0001"]
        assert e["status"] not in ("CLOSED", "REFUTED", "DUPLICATE", "MERGED")
        assert e["mechanical_fault"] is True
        assert e["hil_escalated"] is True

    def test_a_sound_finding_still_reaches_closed_across_the_same_rounds(
            self, mini_repo):
        """The control must cost a sound finding nothing — including its close."""
        from bench.reference_runner_v2 import _update_finding_statuses
        entry = {"severity": 0.85, "falsifier_code": SOUND_FALSIFIER,
                 "corrected_copy": CORRECTED, "description": "d"}
        reg = _registry_with("C0001", entry)
        cfg = RunnerConfig(test_article=TARGET_REL, falsifier_gate_enabled=True,
                           discrimination_control_blocks=True)
        for rnd in (1, 2, 3):
            _update_finding_statuses(reg, rnd, cfg=cfg)
            apply_falsifier_verdicts(reg, rnd, cfg=cfg, repo_root=str(mini_repo))
        assert reg.entries["C0001"]["status"] == "CLOSED"

    def test_a_rewritten_target_invalidates_the_cached_answer(self, mini_repo):
        """`apply_fixes_back_enabled` rewrites the reviewed target between
        rounds. A cache keyed on the falsifier alone would keep answering a
        question about a file that no longer exists."""
        entry = {"severity": 0.85, "falsifier_code": SOUND_FALSIFIER,
                 "corrected_copy": CORRECTED, "description": "d"}
        reg = _registry_with("C0001", entry)
        cfg = RunnerConfig(test_article=TARGET_REL, falsifier_gate_enabled=True,
                           discrimination_control_blocks=True)
        apply_falsifier_verdicts(reg, 3, cfg=cfg, repo_root=str(mini_repo))
        first = reg.entries["C0001"]["discrimination"]
        assert first["outcome"] == DISC_PASSED
        assert first["target_sha"], "the target's identity is part of the answer"
        # The target is rewritten (the claim survives, so the falsifier still
        # fires and the control still runs). The cached answer must not be
        # reused, because it was an answer about a different file.
        (mini_repo / TARGET_REL).write_text(
            DEFECTIVE + "\n# revised wording, same claim\n", encoding="utf-8")
        reg.entries["C0001"]["status"] = "OPEN"
        apply_falsifier_verdicts(reg, 4, cfg=cfg, repo_root=str(mini_repo))
        second = reg.entries["C0001"]["discrimination"]
        assert second["round"] == 4, (
            "the cached answer must not survive a rewritten target")
        assert second["target_sha"] != first["target_sha"]


# ─────────────────────────────────────────────────────────────────────────────
# THE RULE IS SAFE TO PROMOTE — measured, not asserted
# ─────────────────────────────────────────────────────────────────────────────

class TestASoundFindingIsCompletelyUnaffected:
    def test_without_a_corrected_copy_the_gate_is_byte_identical(self, mini_repo):
        """Presence-gated. Nothing supplies a corrected copy today, so the whole
        mechanism is inert on every existing config and every archived run."""
        _reg, e = _gate(mini_repo, SOUND_FALSIFIER, None)
        assert e["status"] == "CONFIRMED"
        assert e["verified"] is True
        assert e["falsifier_verdict"] == "CONFIRMED"
        assert "discrimination" not in e
        assert "computed_evidence" not in e
        assert not e.get("escalated")

    def test_a_non_discriminating_falsifier_without_a_copy_still_closes(self, mini_repo):
        """The control is not a substitute for the corrected copy. Without one it
        says nothing — including about a falsifier that in fact discriminates
        nothing. That is the honest boundary, and it is why the corrected copy
        must be ASKED FOR from the panel."""
        _reg, e = _gate(mini_repo, NON_DISCRIMINATING_FALSIFIER, None)
        assert e["status"] == "CONFIRMED" and e["verified"] is True

    def test_a_refuted_non_critical_path_is_untouched(self, mini_repo):
        mini = mini_repo
        (mini / "pkg" / "spec.py").write_text(CORRECTED, encoding="utf-8")
        _reg, e = _gate(mini, SOUND_FALSIFIER, CORRECTED, severity=0.4)
        assert e["status"] == "REFUTED", (
            "the control sits only on the CONFIRMED branch; every other branch "
            "of the gate must be unreachable from it")
        assert "discrimination" not in e


class TestTheArchiveSaysHowAggressiveThisIs:
    """`p-pass`: measure the blast radius against the real archive rather than
    reasoning about it. The question the founder asked is how many archived
    findings would NEWLY fail to close under this rule."""

    @staticmethod
    def _archived_confirmed():
        rows = []
        for f in sorted((REPO / "bench" / "logs").rglob("runner_state.json")):
            try:
                data = json.loads(f.read_text(encoding="utf-8", errors="replace"))
            except Exception:  # noqa: BLE001 — a corrupt archive file is not this test
                continue
            entries = (data.get("registry") or {}).get("entries")
            if not isinstance(entries, dict):
                entries = data.get("entries") if isinstance(data.get("entries"), dict) else None
            if not entries:
                continue
            for cid, e in entries.items():
                if not isinstance(e, dict):
                    continue
                if e.get("falsifier_verdict") == "CONFIRMED" and (
                        e.get("falsifier_code") or "").strip():
                    rows.append((f, cid, e))
        return rows

    def test_the_archive_is_large_enough_for_the_measurement_to_mean_something(self):
        rows = self._archived_confirmed()
        assert len(rows) >= 400, (
            f"only {len(rows)} archived CONFIRMED findings carry a falsifier; "
            f"the promotion measurement below is not worth much on fewer")

    def test_zero_archived_findings_would_newly_fail_to_close(self):
        """MEASURED, 2026-08-08: 525 archived CONFIRMED-with-falsifier findings
        across 37 run states, 383 of them critical. NONE carries a corrected
        copy, so NONE reaches the control, so NONE newly fails to close. The
        rule is inert on the archive — which is what makes it promotable, and
        also exactly why it does nothing until the panel is asked for the
        corrected copy alongside the falsifier."""
        rows = self._archived_confirmed()
        with_copy = [(f, cid) for f, cid, e in rows
                     if (e.get("corrected_copy") or "").strip()]
        assert with_copy == [], (
            f"{len(with_copy)} archived findings carry a corrected copy and "
            f"would now be controlled; re-measure the promotion cost before "
            f"enabling: {with_copy[:5]}")


class TestThePanelIsToldWhatHappened:
    def test_a_passing_control_is_not_described_as_uncleared(self, mini_repo):
        _reg, e = _gate(mini_repo, SOUND_FALSIFIER, CORRECTED)
        lines = _rejection_lines(e)
        assert any("DISCRIMINATION CONTROL PASSED" in x for x in lines)
        assert not any("not cleared automatically" in x for x in lines), (
            "the generic computed-evidence line asserts the finding is NOT "
            "cleared, which is false of a control that passed; a line that "
            "misdescribes its own evidence is worse than no line")

    def test_a_mechanical_fault_tells_the_panel_what_to_do_about_it(self, mini_repo):
        _reg, e = _gate(mini_repo, NON_DISCRIMINATING_FALSIFIER, CORRECTED)
        lines = _rejection_lines(e)
        text = " ".join(lines)
        assert "MECHANICAL FAULT" in text
        assert "Machinery that highlights an established truth as a fault" in text
        assert "goes quiet when the claim is fixed" in text

    def test_an_indeterminate_control_says_nothing_was_vetoed(self, mini_repo):
        _reg, e = _gate(mini_repo, FRAGILE_FALSIFIER,
                        CORRECTED_BUT_BREAKS_THE_FALSIFIER)
        text = " ".join(_rejection_lines(e))
        assert DISC_ERROR in text
        assert "UNCHANGED" in text and "nothing was vetoed" in text

    def test_the_two_renderings_are_not_interchangeable(self, mini_repo):
        _r1, fault = _gate(mini_repo, NON_DISCRIMINATING_FALSIFIER, CORRECTED)
        _r2, err = _gate(mini_repo, FRAGILE_FALSIFIER,
                         CORRECTED_BUT_BREAKS_THE_FALSIFIER)
        assert _rejection_lines(fault) != _rejection_lines(err)


class TestTheCorrectedCopyIsAskedForNeverSynthesised:
    def test_the_reasoning_stays_attached_to_the_code(self):
        src = (REPO / "bench" / "reference_runner_v2.py").read_text(encoding="utf-8")
        i = src.index("DISCRIMINATION CONTROL — the false-CONFIRMED detector")
        block = src[i:i + 4000]
        assert "NEVER" in block and "synthesised" in block, (
            "a later reader will propose deriving the corrected copy from the "
            "model's proposed fix; the reason that fails must be readable here")
        assert "crash reads as" in block

    def test_the_absent_outcome_is_named_rather_than_silent(self, mini_repo):
        entry = {"severity": 0.85, "falsifier_code": SOUND_FALSIFIER}
        rec = run_discrimination_control(
            entry, repo_root=str(mini_repo), target_rel=TARGET_REL, timeout=60)
        assert rec["outcome"] == DISC_ABSENT
        assert "no corrected copy" in rec["detail"]
        assert rec["outcome"] != DISC_PASSED, (
            "'the control did not run' must never read as 'the control passed'")
