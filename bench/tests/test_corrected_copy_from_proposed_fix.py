"""The discrimination control had an input it never got, and the input existed.

WHAT WAS WRONG. `run_discrimination_control` — the mechanism that asks whether a
CONFIRMED falsifier fired BECAUSE OF THE CLAIM or for some unrelated reason — is
presence-gated on ``entry["corrected_copy"]``. The ask path built on 2026-08-12
solicits that passage from the panel in a labelled form. No panel has ever
answered in it: measured across the whole archive, zero replies carry the label,
so the control has reported NO_CONTROL on every finding of every run and has
never once fired. A gate that never runs reads, at a glance, exactly like a gate
that always passes.

WHAT IS WIRED NOW. The passage the control needs is ALREADY in the registry. A
finding's `proposed_fix` in SEARCH/REPLACE form IS an anchored passage: `search`
is the passage as it stands, `replace` is the same passage with the claim
corrected — the two halves `_splice_corrected_copy` already takes. Measured on
the archive: 954 of 1503 findings that carry a fix parse to exactly one such
block. The runner now reads one, splices it through the SAME verification a
model-supplied passage goes through, and the control runs.

WHY THIS IS NOT THE ROUTE TWO REVIEWS KILLED ON 2026-08-04. They killed APPLYING
a fix as a patch and handing the result to the control unchecked: a bad indent or
a missing import makes the falsifier CRASH, and the crash reads as "still fires",
silently un-confirming a real defect. That door was closed on 2026-08-12 for its
own reasons — a copy that does not parse as Python is REFUSED before it is ever
measured, as is one whose anchor does not occur, occurs twice, or changes
nothing. A derived copy is refused by those same checks and is privileged in no
way. Both refusals are pinned below.

WHAT THIS FILE PINS.
  * the field is populated from a finding's own fix, end to end;
  * the control then returns DISCRIMINATES for a falsifier that goes quiet on
    the corrected copy and NO_DISCRIMINATION for one that does not — the same
    two entries, the same derived supply, opposite verdicts, in a real sandbox;
  * without the supply the very same entries report NO_CONTROL, which is what
    the runner has been reporting since the control was built;
  * a model-supplied passage always wins;
  * every decline is named, leaves the field unwritten, and is NOT rendered back
    to the panel as though a model had sent something;
  * the round loop actually calls it — the defect being fixed here is one
    mechanism built and never fed, and a helper tested only in isolation would
    have passed against the broken tree.
"""

from __future__ import annotations

import ast
import copy as _copy
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bench.reference_runner_v2 import (  # noqa: E402
    DISC_ABSENT,
    DISC_FAILED,
    DISC_PASSED,
    FindingRegistry,
    RunnerConfig,
    _accept_corrected_copy,
    _derive_corrected_copy_from_fix,
    _refresh_stale_corrected_copies,
    _rejection_lines,
    _supply_corrected_copies_from_fixes,
    apply_falsifier_verdicts,
    parse_search_replace_blocks,
    run_discrimination_control,
)

REPO = Path(__file__).resolve().parents[2]
RUNNER_SRC = (REPO / "bench" / "reference_runner_v2.py").read_text(encoding="utf-8")

TARGET_REL = "pkg/spec.py"

DEFECTIVE = '''\
"""Reference values for the SW-21 assembly."""

LEGACY_TABLE = {"rev": "A"}


def clearance_mm():
    # The retracted value. This is the claim under test.
    return 0.29
'''

ORIGINAL_PASSAGE = ("    # The retracted value. This is the claim under test.\n"
                    "    return 0.29")
CORRECTED_PASSAGE = ("    # Corrected to the current specification.\n"
                     "    return 0.31")


def _fix(search: str = ORIGINAL_PASSAGE,
         replace: str = CORRECTED_PASSAGE,
         path: str = TARGET_REL) -> str:
    """A proposed fix in the SEARCH/REPLACE form the runner already parses."""
    return (f"FIX — state the current clearance.\n"
            f"<<<< SEARCH {path}\n{search}\n====\n{replace}\n>>>> REPLACE\n")


# Fires if and only if the retracted clearance is still stated.
SOUND_FALSIFIER = (
    "from pkg.spec import clearance_mm\n"
    "assert clearance_mm() != 0.29, 'the retracted 0.29 mm clearance is stated'\n"
)

# The C0012 shape: it reaches the target, it runs, it fires — and it fires
# because the file is non-empty, which has nothing to do with the clearance.
NON_DISCRIMINATING_FALSIFIER = (
    "from pathlib import Path\n"
    "import pkg.spec as _s\n"
    "src = Path(_s.__file__).read_text(encoding='utf-8')\n"
    "assert not src.strip(), 'the specification is defective'\n"
)


@pytest.fixture
def mini_repo(tmp_path):
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "__init__.py").write_text("", encoding="utf-8")
    (tmp_path / "pkg" / "spec.py").write_text(DEFECTIVE, encoding="utf-8")
    (tmp_path / "pkg" / "unrelated.py").write_text("VALUE = 1\n", encoding="utf-8")
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "notes.md").write_text("# notes\n", encoding="utf-8")
    return tmp_path


def _registry(**entries):
    """`{cid: (falsifier, proposed_fix)}` -> a registry the gate can run on."""
    reg = FindingRegistry()
    for cid, (falsifier, fix) in entries.items():
        reg.entries[cid] = {
            "canonical_id": cid,
            "severity": 0.85,
            "description": "the stated clearance is the retracted value",
            "falsifier_code": falsifier,
            "proposed_fix": fix,
            "status": "OPEN",
            "verdicts": [],
            "source_model": "SIM-A",
            "source_aliases": ["F001"],
            "open_since_round": 0,
            "last_status_change_round": 0,
        }
    return reg


def _cfg(**over):
    kw = {"test_article": TARGET_REL, "falsifier_gate_enabled": True}
    kw.update(over)
    return RunnerConfig(**kw)


# ─────────────────────────────────────────────────────────────────────────────
# 1. THE FIELD IS POPULATED FROM THE FINDING'S OWN FIX
# ─────────────────────────────────────────────────────────────────────────────

class TestTheFixSuppliesTheCopy:
    def test_a_finding_with_a_fix_acquires_a_corrected_copy(self, mini_repo):
        reg = _registry(C0001=(SOUND_FALSIFIER, _fix()))
        stats = _supply_corrected_copies_from_fixes(
            reg, cfg=_cfg(), repo_root=str(mini_repo))
        assert stats == {"candidates": 1, "derived": 1, "declined": 0}
        e = reg.entries["C0001"]
        assert e["corrected_copy"], (
            "the whole point: the control is presence-gated on this field and "
            "nothing had ever supplied one")
        assert e["corrected_copy_source"] == "proposed_fix"
        assert e["corrected_copy_from_fix"]["used"] is True

    def test_the_copy_is_the_whole_target_with_one_passage_replaced(self, mini_repo):
        """A derived copy must not be able to truncate: everything outside the
        anchor is the target's own bytes. Checked by reconstruction rather than
        by trusting the construction — a copy that loses text elsewhere makes a
        sound falsifier go quiet for the wrong reason and reports DISCRIMINATES."""
        reg = _registry(C0001=(SOUND_FALSIFIER, _fix()))
        _supply_corrected_copies_from_fixes(
            reg, cfg=_cfg(), repo_root=str(mini_repo))
        copy = reg.entries["C0001"]["corrected_copy"]
        assert CORRECTED_PASSAGE in copy and ORIGINAL_PASSAGE not in copy
        assert copy.replace(CORRECTED_PASSAGE, ORIGINAL_PASSAGE, 1) == DEFECTIVE

    def test_a_path_less_block_defaults_to_the_target_under_review(self, mini_repo):
        reg = _registry(C0001=(SOUND_FALSIFIER, _fix(path="")))
        assert _supply_corrected_copies_from_fixes(
            reg, cfg=_cfg(), repo_root=str(mini_repo))["derived"] == 1

    def test_the_derived_copy_survives_a_rewrite_of_the_target(self, mini_repo):
        """`apply_fixes_back_enabled` rewrites the reviewed target between
        rounds. A derived copy stores its anchor like any other, so the existing
        re-splice maintains it instead of leaving a document that no longer
        exists to be measured."""
        reg = _registry(C0001=(SOUND_FALSIFIER, _fix()))
        _supply_corrected_copies_from_fixes(
            reg, cfg=_cfg(), repo_root=str(mini_repo))
        moved = DEFECTIVE.replace('{"rev": "A"}', '{"rev": "B"}')
        stats = _refresh_stale_corrected_copies(
            reg, moved, target_rel=TARGET_REL)
        assert stats == {"resplit": 1, "dropped": 0}
        assert '{"rev": "B"}' in reg.entries["C0001"]["corrected_copy"]


# ─────────────────────────────────────────────────────────────────────────────
# 2. THE CONTROL NOW DECIDES — BOTH WAYS, IN A REAL SANDBOX
# ─────────────────────────────────────────────────────────────────────────────

class TestTheControlReachesBothVerdicts:
    """No mocking of the decision: a mocked sandbox would prove only that the
    test author agrees with themselves. Two falsifiers, one supply path, and the
    outcomes must come out opposite — a control that could only ever return one
    of them would be indistinguishable from a rubber stamp."""

    def _supplied(self, mini_repo):
        reg = _registry(C0001=(SOUND_FALSIFIER, _fix()),
                        C0002=(NON_DISCRIMINATING_FALSIFIER, _fix()))
        assert _supply_corrected_copies_from_fixes(
            reg, cfg=_cfg(), repo_root=str(mini_repo))["derived"] == 2
        return reg

    def test_a_falsifier_that_goes_quiet_discriminates(self, mini_repo):
        reg = self._supplied(mini_repo)
        rec = run_discrimination_control(
            reg.entries["C0001"], repo_root=str(mini_repo),
            target_rel=TARGET_REL, timeout=60)
        assert rec["outcome"] == DISC_PASSED, rec
        assert rec["baseline_verdict"] == "CONFIRMED"
        assert rec["corrected_verdict"] == "REFUTED"
        assert rec["intercepted"] is True and rec["deterministic"] is True

    def test_a_falsifier_that_keeps_firing_does_not(self, mini_repo):
        reg = self._supplied(mini_repo)
        rec = run_discrimination_control(
            reg.entries["C0002"], repo_root=str(mini_repo),
            target_rel=TARGET_REL, timeout=60)
        assert rec["outcome"] == DISC_FAILED, rec
        assert rec["baseline_verdict"] == "CONFIRMED"
        assert rec["corrected_verdict"] == "CONFIRMED", (
            "the point of the case: the runner's own re-run says CONFIRMED "
            "against a copy in which the claim is FIXED")

    def test_without_the_supply_both_report_no_control(self, mini_repo):
        """The state of the tree before this wiring, measured rather than
        recalled: the same two entries, no supply, and the control declines to
        speak about either — a silence that reads exactly like a pass."""
        reg = _registry(C0001=(SOUND_FALSIFIER, _fix()),
                        C0002=(NON_DISCRIMINATING_FALSIFIER, _fix()))
        for cid in ("C0001", "C0002"):
            rec = run_discrimination_control(
                reg.entries[cid], repo_root=str(mini_repo),
                target_rel=TARGET_REL, timeout=60)
            assert rec["outcome"] == DISC_ABSENT != DISC_PASSED, cid


# ─────────────────────────────────────────────────────────────────────────────
# 3. THE PRODUCTION SEQUENCE — SUPPLY, THEN GATE
# ─────────────────────────────────────────────────────────────────────────────

class TestTheGateConsumesTheDerivedCopy:
    def test_a_sound_falsifier_is_untouched_and_stays_confirmed(self, mini_repo):
        reg = _registry(C0001=(SOUND_FALSIFIER, _fix()))
        cfg = _cfg(discrimination_control_blocks=True)
        _supply_corrected_copies_from_fixes(reg, cfg=cfg, repo_root=str(mini_repo))
        apply_falsifier_verdicts(reg, 3, cfg=cfg, repo_root=str(mini_repo))
        e = reg.entries["C0001"]
        assert e["discrimination"]["outcome"] == DISC_PASSED
        assert e["status"] == "CONFIRMED" and e["verified"] is True
        assert not e.get("mechanical_fault")

    def test_a_non_discriminating_falsifier_is_escalated_not_deleted(self, mini_repo):
        """A veto ESCALATES. The finding is not closed and not dropped: it goes
        back to the human with the instrument named as the fault."""
        reg = _registry(C0002=(NON_DISCRIMINATING_FALSIFIER, _fix()))
        cfg = _cfg(discrimination_control_blocks=True)
        _supply_corrected_copies_from_fixes(reg, cfg=cfg, repo_root=str(mini_repo))
        apply_falsifier_verdicts(reg, 3, cfg=cfg, repo_root=str(mini_repo))
        e = reg.entries["C0002"]
        assert e["discrimination"]["outcome"] == DISC_FAILED
        assert e["status"] != "CONFIRMED"
        assert e["mechanical_fault"] is True and e["hil_escalated"] is True
        assert e["falsifier_verdict"] == "NON_DISCRIMINATING"
        assert e in list(reg.entries.values()), "escalation is not deletion"

    def test_the_default_records_the_fault_without_blocking(self, mini_repo):
        """Blocking is a founder decision and stays default-off; the supply must
        not change that by the back door. The outcome is still recorded."""
        reg = _registry(C0002=(NON_DISCRIMINATING_FALSIFIER, _fix()))
        cfg = _cfg()
        _supply_corrected_copies_from_fixes(reg, cfg=cfg, repo_root=str(mini_repo))
        apply_falsifier_verdicts(reg, 3, cfg=cfg, repo_root=str(mini_repo))
        e = reg.entries["C0002"]
        assert e["discrimination"]["outcome"] == DISC_FAILED
        assert e["status"] == "CONFIRMED"


# ─────────────────────────────────────────────────────────────────────────────
# 4. EVERY DECLINE IS NAMED, TOTAL, AND ADDRESSED TO NOBODY
# ─────────────────────────────────────────────────────────────────────────────

class TestADeclineIsLoudAndTotal:
    def _decline(self, mini_repo, fix):
        reg = _registry(C0001=(SOUND_FALSIFIER, fix))
        stats = _supply_corrected_copies_from_fixes(
            reg, cfg=_cfg(), repo_root=str(mini_repo))
        e = reg.entries["C0001"]
        assert stats["derived"] == 0 and stats["declined"] == 1
        assert "corrected_copy" not in e
        assert e["corrected_copy_from_fix"]["used"] is False
        return e["corrected_copy_from_fix"]["reason"]

    def test_a_fix_whose_anchor_is_not_in_the_target(self, mini_repo):
        reason = self._decline(
            mini_repo, _fix("this passage is nowhere in the target at all"))
        assert "does not occur in the target" in reason

    def test_a_fix_that_would_not_parse_is_declined_before_measurement(
            self, mini_repo):
        """THE ROUTE TWO REVIEWS KILLED, closed at the door. A fix with a bad
        indent makes the falsifier CRASH; the crash is not a verdict, and the
        copy that caused it never gets to be measured."""
        reason = self._decline(
            mini_repo, _fix(replace="# dedented to column zero\nreturn 0.31"))
        assert "does not parse as Python" in reason

    def test_a_fix_that_changes_nothing(self, mini_repo):
        reason = self._decline(mini_repo, _fix(replace=ORIGINAL_PASSAGE))
        assert "identical" in reason

    def test_a_fix_with_two_blocks_against_the_target(self, mini_repo):
        reason = self._decline(mini_repo, _fix() + _fix('LEGACY_TABLE = {"rev": "A"}',
                                                        'LEGACY_TABLE = {"rev": "B"}'))
        assert "2 SEARCH/REPLACE blocks" in reason

    def test_a_fix_for_a_different_file_is_not_used(self, mini_repo):
        reason = self._decline(mini_repo, _fix(path="pkg/unrelated.py"))
        assert "no SEARCH/REPLACE block against" in reason

    def test_prose_with_no_block_at_all_is_not_used(self, mini_repo):
        reason = self._decline(mini_repo, "FIX — state the current clearance.")
        assert "no SEARCH/REPLACE block against" in reason

    def test_a_decline_is_never_rendered_to_the_panel_as_a_refusal(self, mini_repo):
        """`corrected_copy_rejected` is read back to the models. Telling one that
        its passage was refused when it never sent a passage is a message about
        a thing that did not happen."""
        reg = _registry(C0001=(SOUND_FALSIFIER, _fix("nowhere in this target")))
        _supply_corrected_copies_from_fixes(
            reg, cfg=_cfg(), repo_root=str(mini_repo))
        e = reg.entries["C0001"]
        assert "corrected_copy_rejected" not in e
        assert "CORRECTED COPY REFUSED" not in " ".join(_rejection_lines(e))

    def test_a_finding_with_no_fix_is_left_exactly_as_it_was(self, mini_repo):
        reg = _registry(C0001=(SOUND_FALSIFIER, ""))
        before = _copy.deepcopy(reg.entries["C0001"])
        stats = _supply_corrected_copies_from_fixes(
            reg, cfg=_cfg(), repo_root=str(mini_repo))
        assert stats == {"candidates": 0, "derived": 0, "declined": 0}
        assert reg.entries["C0001"] == before

    def test_an_unreadable_target_derives_nothing_and_stamps_nothing(
            self, mini_repo):
        reg = _registry(C0001=(SOUND_FALSIFIER, _fix()))
        before = _copy.deepcopy(reg.entries["C0001"])
        stats = _supply_corrected_copies_from_fixes(
            reg, cfg=_cfg(test_article="pkg/absent.py"), repo_root=str(mini_repo))
        assert stats == {"candidates": 0, "derived": 0, "declined": 0}
        assert reg.entries["C0001"] == before, (
            "a target that cannot be read is not evidence about any finding")


# ─────────────────────────────────────────────────────────────────────────────
# 5. THE ASK STILL OUTRANKS THE DERIVATION
# ─────────────────────────────────────────────────────────────────────────────

class TestAModelSuppliedPassageWins:
    def test_an_accepted_passage_is_never_overwritten(self, mini_repo):
        reg = _registry(C0001=(SOUND_FALSIFIER, _fix(
            replace="    # derived from the fix.\n    return 0.99")))
        _accept_corrected_copy(
            reg.entries["C0001"], ORIGINAL_PASSAGE, CORRECTED_PASSAGE,
            DEFECTIVE, target_rel=TARGET_REL, by="SIM-A", cid="C0001")
        stats = _supply_corrected_copies_from_fixes(
            reg, cfg=_cfg(), repo_root=str(mini_repo))
        e = reg.entries["C0001"]
        assert stats["candidates"] == 0
        assert e["corrected_copy_source"] == "SIM-A"
        assert "return 0.31" in e["corrected_copy"]
        assert "return 0.99" not in e["corrected_copy"]

    def test_the_derivation_fills_the_gap_a_refused_passage_left(self, mini_repo):
        reg = _registry(C0001=(SOUND_FALSIFIER, _fix()))
        _accept_corrected_copy(
            reg.entries["C0001"], "a passage that is nowhere in the target",
            "something else", DEFECTIVE, target_rel=TARGET_REL,
            by="SIM-A", cid="C0001")
        assert "corrected_copy" not in reg.entries["C0001"]
        assert _supply_corrected_copies_from_fixes(
            reg, cfg=_cfg(), repo_root=str(mini_repo))["derived"] == 1
        assert "return 0.31" in reg.entries["C0001"]["corrected_copy"]


# ─────────────────────────────────────────────────────────────────────────────
# 6. THE WIRING ITSELF — the defect being fixed is "built but never fed"
# ─────────────────────────────────────────────────────────────────────────────

class TestTheMechanismIsActuallyCalled:
    def test_the_round_loop_supplies_between_the_ask_and_the_gate(self):
        """A helper exercised only by its own tests would have passed against the
        broken tree, which is exactly how the control came to be built, tested,
        documented and never run. So the call site is asserted at source level,
        in order."""
        ask = RUNNER_SRC.index(
            "_ingest_corrected_copies(\n            registry, responses")
        supply = RUNNER_SRC.index(
            "_supply_corrected_copies_from_fixes(\n            registry", ask)
        gate = RUNNER_SRC.index("apply_falsifier_verdicts(registry, round_idx", ask)
        assert ask < supply < gate, (
            "the ask must win over the derivation, and a copy derived in round K "
            "must reach the control in round K rather than one round late")

    def test_the_single_writer_of_the_field_is_unchanged(self):
        """A derived copy is not privileged: it is stored by the same verified
        writer as a model's own passage, so it passes the same checks."""
        tree = ast.parse(RUNNER_SRC)
        fns = {n.name for n in ast.walk(tree)
               if isinstance(n, ast.FunctionDef)
               and '["corrected_copy"] =' in (ast.get_source_segment(RUNNER_SRC, n) or "")}
        assert fns == {"_accept_corrected_copy", "_refresh_stale_corrected_copies"}, fns
        derive = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
                      and n.name == "_derive_corrected_copy_from_fix")
        src = ast.get_source_segment(RUNNER_SRC, derive) or ""
        assert '["corrected_copy"] =' not in src


# ─────────────────────────────────────────────────────────────────────────────
# 7. THE SHAPE EXISTS IN THE REAL ARCHIVE — anti-vacuity
# ─────────────────────────────────────────────────────────────────────────────

class TestTheArchiveActuallyCarriesThisShape:
    def test_the_fixes_this_project_produces_parse_as_anchored_passages(self):
        """The mini-repo above proves the mechanism works on a fix of the right
        shape. It says nothing about whether real panels write that shape, and a
        supply path fed by a form nobody uses would be the same defect over
        again. Measured on the archive: 954 of 1503."""
        single = total = 0
        for f in sorted((REPO / "bench" / "logs").rglob("runner_state.json")):
            try:
                data = json.loads(f.read_text(encoding="utf-8", errors="replace"))
            except Exception:  # noqa: BLE001 — a corrupt archive file is not this test
                continue
            entries = (data.get("registry") or {}).get("entries") or {}
            if not isinstance(entries, dict):
                continue
            for e in entries.values():
                if not (isinstance(e, dict) and (e.get("proposed_fix") or "").strip()):
                    continue
                total += 1
                if len(parse_search_replace_blocks(e["proposed_fix"])) == 1:
                    single += 1
        assert total >= 500, f"only {total} archived fixes were readable"
        assert single >= 100, (
            f"only {single} of {total} archived proposed fixes parse to exactly "
            f"one SEARCH/REPLACE block; the supply path would be fed by a form "
            f"the panel does not write")

    def test_the_derivation_is_a_no_op_on_a_target_that_has_moved_on(self):
        """And the guard that makes the above safe: an anchor is located by exact
        match, so a fix written against a revision that no longer exists derives
        NOTHING rather than something approximate."""
        target = (REPO / "bench" / "reference_runner_v2.py").read_text(
            encoding="utf-8", errors="replace")
        entry = {"proposed_fix": _fix(path="bench/reference_runner_v2.py")}
        assert not _derive_corrected_copy_from_fix(
            entry, target, target_rel="bench/reference_runner_v2.py", cid="C9999")
        assert "corrected_copy" not in entry
