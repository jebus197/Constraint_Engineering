"""`entry["corrected_copy"]` had no writer, so the control had never fired.

WHAT WAS WRONG. The discrimination control — the mechanism that asks whether a
CONFIRMED falsifier fired BECAUSE OF THE CLAIM or for some unrelated reason —
reads its corrected copy from ``entry["corrected_copy"]``. Measured across the
whole tree on 2026-08-12: that key had ZERO writers outside this suite's own
fixtures. Nothing populated it. The apparatus was built, tested, documented and
never connected, and because the control is presence-gated it reported
``NO_CONTROL`` on every finding of every run — a silence that reads, at a
glance, exactly like a pass.

WHAT IS WIRED NOW. The panel is ASKED for the corrected passage alongside the
falsifier, in the SAME labelled form the falsifier itself uses, in all three
prompts that solicit a falsifier (the round directive, the routing ladder, the
post-convergence sweep). The reply is parsed, VERIFIED against the target, and
spliced into a full corrected copy. This path never reads the model's proposed
fix; a second supply that does — reading ONE SEARCH/REPLACE block as an anchored
passage, through the same verified splice — was added on 2026-08-22 because no
panel ever answered the ask, and it is pinned in
`test_corrected_copy_from_proposed_fix.py`. Neither path APPLIES a fix as a
patch, which is the route two reviews killed on 2026-08-04.

WHY A SPLICE RATHER THAN A PASTED DOCUMENT. The field is consumed as the entire
content of the target. A pasted whole document is one truncation away from a
"corrected copy" that is missing most of the target, and a falsifier reading a
mostly-absent document goes quiet — which renders as DISCRIMINATES. That is the
house failure mode: a failure arriving as a confident success. A splice cannot
truncate, and this file proves that property directly rather than asserting it.

WHAT THIS FILE PINS.
  * the field is populated end to end on a constructed round, and the control
    then actually runs and returns a verdict;
  * a run with no corrected copy behaves EXACTLY as before, field-for-field;
  * nothing in the archive changes: no archived reply contains the label, so no
    archived finding acquires a copy and no archived resolution outcome moves;
  * every refusal path is named, loud, and leaves the field unwritten;
  * the ask reaches all three prompts in one identical form.
"""

from __future__ import annotations

import ast
import copy as _copy
import json
import re
import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bench.reference_runner_v3 import (  # noqa: E402
    DISC_ABSENT,
    DISC_PASSED,
    FindingRegistry,
    RunnerConfig,
    _accept_corrected_copy,
    _CORRECTED_ANCHOR_MIN,
    _corrected_copy_instructions,
    _extract_corrected_copies,
    _ingest_corrected_copies,
    _refresh_stale_corrected_copies,
    _rejection_lines,
    _routing_resolve_prompt,
    _runnable_falsifier_s2,
    _splice_corrected_copy,
    _sweep_prompt,
    apply_falsifier_verdicts,
    run_discrimination_control,
)

REPO = Path(__file__).resolve().parents[2]
RUNNER_SRC = (REPO / "bench" / "reference_runner_v3.py").read_text(encoding="utf-8")

TARGET_REL = "pkg/spec.py"

DEFECTIVE = '''\
"""Reference values for the SW-21 assembly."""

LEGACY_TABLE = {"rev": "A"}


def clearance_mm():
    # The retracted value. This is the claim under test.
    return 0.29
'''

# The passage as it stands, and the same passage corrected. This is what a model
# is asked for: text, not a patch.
ORIGINAL_PASSAGE = "    # The retracted value. This is the claim under test.\n    return 0.29"
CORRECTED_PASSAGE = "    # Corrected to the current specification.\n    return 0.31"

SOUND_FALSIFIER = (
    "from pkg.spec import clearance_mm\n"
    "assert clearance_mm() != 0.29, 'the retracted 0.29 mm clearance is still stated'\n"
)


def _reply(key: str = "F001",
           original: str = ORIGINAL_PASSAGE,
           corrected: str = CORRECTED_PASSAGE) -> str:
    """A model reply in the wired convention: falsifier, then corrected copy."""
    return (
        "FIND: the stated clearance is the retracted value.\n"
        "FALSIFIER:\n"
        "```python\n" + SOUND_FALSIFIER + "```\n"
        f"CORRECTED_COPY: {key}\n"
        "<<<CDSFL_ORIGINAL>>>\n"
        f"{original}\n"
        "<<<CDSFL_CORRECTED>>>\n"
        f"{corrected}\n"
        "<<<CDSFL_END>>>\n"
    )


@pytest.fixture
def mini_repo(tmp_path):
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "__init__.py").write_text("", encoding="utf-8")
    (tmp_path / "pkg" / "spec.py").write_text(DEFECTIVE, encoding="utf-8")
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "notes.md").write_text("# notes\n", encoding="utf-8")
    return tmp_path


def _registry(cid="C0001", model="CODEX", local_id="F001", **over):
    reg = FindingRegistry()
    entry = {
        "canonical_id": cid,
        "severity": 0.85,
        "description": "the stated clearance is the retracted value",
        "falsifier_code": SOUND_FALSIFIER,
        "status": "OPEN",
        "verdicts": [],
        "source_model": model,
        "source_aliases": [local_id],
        "open_since_round": 0,
        "last_status_change_round": 0,
    }
    entry.update(over)
    reg.entries[cid] = entry
    reg._alias_map[f"{model}:{local_id}"] = cid
    return reg


# ─────────────────────────────────────────────────────────────────────────────
# 1. THE FIELD IS POPULATED END TO END, AND THE CONTROL THEN ACTUALLY RUNS
# ─────────────────────────────────────────────────────────────────────────────

class TestTheFieldIsPopulatedEndToEnd:
    def test_a_constructed_round_populates_the_field(self, mini_repo):
        reg = _registry()
        cfg = RunnerConfig(test_article=TARGET_REL, falsifier_gate_enabled=True)
        stats = _ingest_corrected_copies(
            reg, {"CODEX": _reply()}, 3, cfg=cfg, repo_root=str(mini_repo))
        assert stats["accepted"] == 1 and stats["refused"] == 0
        e = reg.entries["C0001"]
        assert e["corrected_copy"], (
            "the whole point: before this wiring the field had no writer at all")
        assert e["corrected_copy_source"] == "CODEX"

    def test_the_stored_copy_is_the_whole_target_with_one_passage_replaced(
            self, mini_repo):
        """The splice cannot truncate, and that is checked by reconstruction
        rather than by trusting the construction."""
        reg = _registry()
        cfg = RunnerConfig(test_article=TARGET_REL)
        _ingest_corrected_copies(
            reg, {"CODEX": _reply()}, 3, cfg=cfg, repo_root=str(mini_repo))
        copy = reg.entries["C0001"]["corrected_copy"]
        assert CORRECTED_PASSAGE in copy and ORIGINAL_PASSAGE not in copy
        assert copy.replace(CORRECTED_PASSAGE, ORIGINAL_PASSAGE, 1) == DEFECTIVE, (
            "everything outside the anchor must be the target's own bytes; a "
            "copy that loses text elsewhere makes a sound falsifier go quiet "
            "for the wrong reason and reports it as DISCRIMINATES")

    def test_the_control_reaches_a_verdict_on_the_wired_copy(self, mini_repo):
        """Populate through the production path, then run the real control in a
        real sandbox. No mocking of the decision: a mocked sandbox would prove
        only that the test author agrees with themselves."""
        reg = _registry()
        cfg = RunnerConfig(test_article=TARGET_REL, falsifier_gate_enabled=True)
        _ingest_corrected_copies(
            reg, {"CODEX": _reply()}, 3, cfg=cfg, repo_root=str(mini_repo))
        rec = run_discrimination_control(
            reg.entries["C0001"], repo_root=str(mini_repo),
            target_rel=TARGET_REL, timeout=60)
        assert rec["outcome"] == DISC_PASSED, rec
        assert rec["baseline_verdict"] == "CONFIRMED"
        assert rec["corrected_verdict"] == "REFUTED"
        assert rec["intercepted"] is True

    def test_the_gate_applies_the_control_to_a_wired_copy(self, mini_repo):
        """The full production sequence: ingest, then the falsifier gate."""
        reg = _registry()
        cfg = RunnerConfig(test_article=TARGET_REL, falsifier_gate_enabled=True)
        _ingest_corrected_copies(
            reg, {"CODEX": _reply()}, 3, cfg=cfg, repo_root=str(mini_repo))
        apply_falsifier_verdicts(reg, 3, cfg=cfg, repo_root=str(mini_repo))
        e = reg.entries["C0001"]
        assert e["discrimination"]["outcome"] == DISC_PASSED
        assert e["status"] == "CONFIRMED" and e["verified"] is True

    def test_the_model_may_label_with_the_canonical_id_instead(self, mini_repo):
        reg = _registry()
        cfg = RunnerConfig(test_article=TARGET_REL)
        _ingest_corrected_copies(
            reg, {"CODEX": _reply(key="C0001")}, 3, cfg=cfg,
            repo_root=str(mini_repo))
        assert reg.entries["C0001"]["corrected_copy"]

    def test_an_unresolvable_id_is_reported_not_guessed_at(self, mini_repo):
        reg = _registry()
        cfg = RunnerConfig(test_article=TARGET_REL)
        stats = _ingest_corrected_copies(
            reg, {"CODEX": _reply(key="F999")}, 3, cfg=cfg,
            repo_root=str(mini_repo))
        assert stats["unmatched"] == 1 and stats["accepted"] == 0
        assert "corrected_copy" not in reg.entries["C0001"], (
            "attaching an unlabelled copy to whichever finding is to hand would "
            "control one claim with another claim's correction")


# ─────────────────────────────────────────────────────────────────────────────
# 2. WITHOUT A CORRECTED COPY, NOTHING MOVES
# ─────────────────────────────────────────────────────────────────────────────

class TestWithoutACopyTheRunIsUnchanged:
    def test_a_reply_with_no_corrected_copy_writes_nothing(self, mini_repo):
        reg = _registry()
        before = _copy.deepcopy(reg.entries["C0001"])
        cfg = RunnerConfig(test_article=TARGET_REL)
        stats = _ingest_corrected_copies(
            reg, {"CODEX": "FALSIFIER:\n```python\nassert 1\n```\n"}, 3,
            cfg=cfg, repo_root=str(mini_repo))
        assert stats == {"offered": 0, "accepted": 0, "refused": 0,
                         "unmatched": 0, "resplit": 0, "dropped": 0}
        assert reg.entries["C0001"] == before, (
            "field-for-field identical: the ingest must be invisible on a round "
            "where nothing was offered")

    def test_the_gate_is_byte_identical_without_a_copy(self, mini_repo):
        reg = _registry()
        cfg = RunnerConfig(test_article=TARGET_REL, falsifier_gate_enabled=True)
        _ingest_corrected_copies(
            reg, {"CODEX": "no corrected copy here"}, 3, cfg=cfg,
            repo_root=str(mini_repo))
        apply_falsifier_verdicts(reg, 3, cfg=cfg, repo_root=str(mini_repo))
        e = reg.entries["C0001"]
        assert e["status"] == "CONFIRMED" and e["verified"] is True
        assert e["falsifier_verdict"] == "CONFIRMED"
        assert "discrimination" not in e, (
            "presence-gated: no copy means the control does not run at all")
        assert not e.get("escalated") and not e.get("mechanical_fault")

    def test_the_absent_outcome_still_reads_as_absent_not_as_a_pass(
            self, mini_repo):
        rec = run_discrimination_control(
            {"falsifier_code": SOUND_FALSIFIER}, repo_root=str(mini_repo),
            target_rel=TARGET_REL, timeout=60)
        assert rec["outcome"] == DISC_ABSENT != DISC_PASSED

    def test_an_empty_responses_map_is_a_no_op(self, mini_repo):
        reg = _registry()
        before = _copy.deepcopy(reg.entries["C0001"])
        cfg = RunnerConfig(test_article=TARGET_REL)
        _ingest_corrected_copies(reg, {}, 3, cfg=cfg, repo_root=str(mini_repo))
        assert reg.entries["C0001"] == before


# ─────────────────────────────────────────────────────────────────────────────
# 3. THE ARCHIVE DOES NOT MOVE — measured, not reasoned about
# ─────────────────────────────────────────────────────────────────────────────

def _is_v3_era(run_dir) -> bool:
    """True for a run produced by runner v3 or later.

    Version first: a run that stamps `runner_version` is classified by it.
    Name second: for runs predating that stamp, fall back to exp<N> with N >= 55.
    """
    for name in ("runner_state.json",):
        f = run_dir / name
        if f.is_file():
            try:
                v = json.loads(f.read_text(encoding="utf-8", errors="replace")).get("runner_version")
            except Exception:  # noqa: BLE001
                v = None
            if isinstance(v, str) and re.match(r"v[3-9]", v):
                return True
    # A SIMULATED RUN IS NEVER REAL ARCHIVE, whatever it did or did not write.
    #
    # The version-first/name-second rule above was added because a v3.1 run whose
    # directory was called sim45_* had been misfiled by name. It fixed that
    # instance and not the class: the name fallback learned `exp<N>` and never
    # learned `sim*`, so a simulated run that did not get as far as writing
    # runner_state.json still fell through to "pre-v3 real archive". Measured
    # 2026-09-01: 9 of 11 simulated run directories carry no runner_state.json
    # (81.8%, Wilson [52.3%, 94.9%]) -- most of them, because a run killed or
    # crashed early never writes one. Four of tonight's simulated replies were
    # being counted against a claim about the REAL archive.
    if run_dir.name.startswith("sim"):
        return True
    m = re.match(r"exp(\d+)", run_dir.name)
    return bool(m and int(m.group(1)) >= 55)


class TestTheArchiveIsUntouched:
    """`p-pass`: the claim "no verdict changed anywhere" is only worth what the
    measurement behind it is worth, so it is measured against the real archive."""

    @staticmethod
    def _archived_responses():
        """(path, model_id, response_text) for every archived model reply."""
        out = []
        for f in sorted((REPO / "bench" / "logs").rglob("round_*.json")):
            # PRE-v3 ARCHIVE ONLY. These guards assert a NO-OP claim -- "no
            # archived reply carries the label, so no archived finding can
            # acquire a corrected copy". That claim was always ABOUT THE ARCHIVE
            # THAT PREDATES THE FEATURE. Once the corrected-copy ask was wired
            # on 2026-08-30 and enabled, v3-era runs legitimately carry the
            # label: that is the feature working, not the wiring reaching
            # backwards into the record.
            #
            # Same boundary, and for the same reason, as the one applied to
            # test_corrected_copy_wiring's sibling guard on 2026-08-30. Version
            # first, name second: a run that records its own runner_version is
            # classified by it, because classifying by DIRECTORY NAME misfiled a
            # v3.1 run whose directory was called sim45_* rather than exp*.
            if _is_v3_era(f.parent):
                continue
            try:
                data = json.loads(f.read_text(encoding="utf-8", errors="replace"))
            except Exception:  # noqa: BLE001 — a corrupt archive file is not this test
                continue
            resp = data.get("model_responses")
            if isinstance(resp, dict):
                for model, text in resp.items():
                    # THE -SIM SUFFIX IS THE PROVENANCE MARKER (founder ruling
                    # 2026-08-08), so it settles this at the RECORD level rather
                    # than relying on where the record happens to be filed. A
                    # reply from CC2-SIM is a rehearsal and cannot bear on a
                    # claim about what the real archive contains. Belt and
                    # braces with the directory rule above: a simulated reply
                    # filed anywhere at all is still excluded.
                    if isinstance(model, str) and model.strip().endswith("-SIM"):
                        continue
                    if isinstance(text, str):
                        out.append((f, model, text))
        return out

    def test_the_archive_is_large_enough_to_mean_something(self):
        rows = self._archived_responses()
        assert len(rows) >= 100, (
            f"only {len(rows)} archived model replies were readable; the "
            f"no-op measurement below is not worth much on fewer")

    def test_no_archived_reply_carries_the_label(self):
        """The convention is NEW. If no archived reply contains it, no archived
        finding can acquire a corrected copy, so no archived resolution outcome
        can move — which is the strongest available form of "nothing changed"."""
        hits = [(str(f.relative_to(REPO)), model)
                for f, model, text in self._archived_responses()
                if "CORRECTED_COPY" in text]
        assert hits == [], (
            f"{len(hits)} archived replies already contain the label; the "
            f"no-op claim must be re-measured before this is enabled: {hits[:5]}")

    def test_replaying_every_archived_reply_produces_no_corrected_copy(self):
        """Stronger than a substring scan: run the real extractor over every
        archived reply and assert it yields nothing. A regex that accidentally
        matched prose would show up here and nowhere else."""
        offered = 0
        for _f, _model, text in self._archived_responses():
            offered += len(_extract_corrected_copies(text))
        assert offered == 0, (
            f"the extractor found {offered} corrected passages in archived "
            f"replies; each one would newly reach the discrimination control")

    def test_replaying_every_archived_run_moves_no_resolution_outcome(
            self, monkeypatch):
        """The founder's own P-pass condition, executed rather than argued.

        Every archived run is replayed twice through the real falsifier gate —
        once with the ingest fed that run's actual model replies, once without
        it — and the two resolution states are diffed finding by finding.
        `reverify_falsifier` is pinned to the verdict the ARCHIVE recorded, so
        the gate replays the archive's own decisions deterministically instead
        of re-executing 500 falsifiers against a tree that has moved on.
        """
        import bench.falsifier_verify as _fv
        from bench import reference_runner_v3 as _R

        pinned: dict = {}
        monkeypatch.setattr(
            _fv, "reverify_falsifier",
            lambda code, repo_root=None, timeout=None, **kw: pinned.get(
                (code or "").strip(), "ERROR"))

        fields = ("status", "falsifier_verdict", "verified", "escalated",
                  "hil_escalated", "mechanical_fault", "irreducible_escalation")

        def _registry_from(entries):
            reg = _R.FindingRegistry()
            for cid, e in entries.items():
                if not isinstance(e, dict):
                    continue
                e = _copy.deepcopy(e)
                e.setdefault("status", "OPEN")
                e.setdefault("verdicts", [])
                e.setdefault("open_since_round", 0)
                e.setdefault("last_status_change_round", 0)
                reg.entries[cid] = e
                for alias in e.get("source_aliases") or []:
                    reg._alias_map[f"{e.get('source_model')}:{alias}"] = cid
            return reg

        def _replay(entries, replies, with_ingest, cfg):
            reg = _registry_from(entries)
            if with_ingest:
                for one_round in replies:
                    _R._ingest_corrected_copies(
                        reg, one_round, 0, cfg=cfg, repo_root=str(REPO))
            _R.apply_falsifier_verdicts(reg, 99, cfg=cfg, repo_root=str(REPO))
            return {cid: {k: e.get(k) for k in fields}
                    for cid, e in reg.entries.items()}

        runs = findings = moved = 0
        details = []
        for f in sorted((REPO / "bench" / "logs").rglob("runner_state.json")):
            if _is_v3_era(f.parent):
                continue      # v3-era: corrected copies are the feature working

            try:
                data = json.loads(f.read_text(encoding="utf-8", errors="replace"))
            except Exception:  # noqa: BLE001
                continue
            entries = (data.get("registry") or {}).get("entries")
            if not isinstance(entries, dict) or not entries:
                continue
            pinned.clear()
            for e in entries.values():
                if isinstance(e, dict) and (e.get("falsifier_code") or "").strip():
                    pinned[e["falsifier_code"].strip()] = (
                        e.get("falsifier_verdict") or "ERROR")
            replies = []
            for rf in sorted(f.parent.glob("round_*.json")):
                try:
                    rd = json.loads(rf.read_text(encoding="utf-8", errors="replace"))
                except Exception:  # noqa: BLE001
                    continue
                mr = rd.get("model_responses")
                if isinstance(mr, dict):
                    replies.append({k: v for k, v in mr.items()
                                    if isinstance(v, str)})
            cfg = RunnerConfig(test_article="bench/reference_runner_v3.py",
                               falsifier_gate_enabled=True)
            before = _replay(entries, replies, False, cfg)
            after = _replay(entries, replies, True, cfg)
            runs += 1
            findings += len(before)
            for cid in before:
                if before[cid] != after.get(cid):
                    moved += 1
                    details.append((str(f.relative_to(REPO)), cid))

        assert runs >= 30 and findings >= 2000, (
            f"only {findings} findings across {runs} runs were replayable; the "
            f"no-movement claim needs a bigger denominator than that")
        assert moved == 0, (
            f"{moved} archived resolution outcomes moved: {details[:5]}")

    def test_no_archived_finding_carries_a_corrected_copy(self):
        """Belt and braces on the state files rather than the replies: this is
        the assertion `test_discrimination_control.py` already relies on, and it
        must survive the wiring.
    THE ARCHIVE IS PRE-v3, AND THE BOUNDARY IS PRINCIPLED (2026-08-23). This guard
    was written when NO run had ever produced a corrected copy, and its purpose is
    that the wiring must not reach BACKWARDS into the record. Exp 55 is the first
    run WITH the feature, so it legitimately carries them -- that is the feature
    working, not the wiring reaching backwards.

    The scope therefore excludes exp55 and later, which is the same v3 boundary the
    runner's version banner sets, NOT "whatever happens to be failing". The guard's
    intent is unchanged and its denominator is still every pre-v3 run.
    """
        carried = []
        for f in sorted((REPO / "bench" / "logs").rglob("runner_state.json")):
            if _is_v3_era(f.parent):
                continue      # v3-era: corrected copies are the feature working
            # Classify by the run's OWN recorded version, not by its directory
            # name. The name rule fails CLOSED on anything not called exp<N>:
            # on 2026-08-30 a v3.1 run in sim45_memory_* was filed as pre-v3
            # archive and its 14 legitimate corrected copies read as the wiring
            # reaching backwards into the record. Version first, name second.
            try:
                _v = json.loads(f.read_text(encoding="utf-8",
                                            errors="replace")).get("runner_version")
            except Exception:  # noqa: BLE001
                _v = None
            if isinstance(_v, str) and re.match(r"v[3-9]", _v):
                continue          # v3-era: corrected copies are the feature
            m = re.match(r"exp(\d+)", f.parent.name)
            if m and int(m.group(1)) >= 55:
                continue          # pre-version-stamp v3 runs, by number
            try:
                data = json.loads(f.read_text(encoding="utf-8", errors="replace"))
            except Exception:  # noqa: BLE001
                continue
            entries = (data.get("registry") or {}).get("entries") or {}
            if not isinstance(entries, dict):
                continue
            for cid, e in entries.items():
                if isinstance(e, dict) and (e.get("corrected_copy") or "").strip():
                    carried.append((str(f.relative_to(REPO)), cid))
        assert carried == [], carried[:5]


# ─────────────────────────────────────────────────────────────────────────────
# 4. EVERY REFUSAL IS NAMED, LOUD, AND LEAVES THE FIELD UNWRITTEN
# ─────────────────────────────────────────────────────────────────────────────

class TestARefusalIsLoudAndTotal:
    @pytest.mark.parametrize("original,corrected,needle", [
        ("this passage is nowhere in the target at all",
         "replacement text here", "does not occur in the target"),
        ("return 0.29", "return 0.31", "shorter than"),
        (ORIGINAL_PASSAGE, ORIGINAL_PASSAGE, "identical"),
    ])
    def test_each_refusal_names_its_own_reason(self, original, corrected, needle):
        copy, reason = _splice_corrected_copy(
            DEFECTIVE, original, corrected, TARGET_REL)
        assert copy == ""
        assert needle in reason, reason

    def test_an_ambiguous_anchor_is_refused_rather_than_guessed(self):
        doubled = DEFECTIVE + "\n" + ORIGINAL_PASSAGE + "\n"
        copy, reason = _splice_corrected_copy(
            doubled, ORIGINAL_PASSAGE, CORRECTED_PASSAGE, TARGET_REL)
        assert copy == "" and "occurs 2 times" in reason

    def test_a_corrected_copy_that_does_not_parse_is_refused_before_measurement(self):
        """THE ROUTE TWO REVIEWS KILLED, closed at the door instead of downstream.
        A fix with a bad indent makes the falsifier CRASH; the crash is not a
        verdict, and the copy that caused it never gets to be measured."""
        copy, reason = _splice_corrected_copy(
            DEFECTIVE, ORIGINAL_PASSAGE,
            "# dedented to column zero\nreturn 0.31", TARGET_REL)
        assert copy == ""
        assert "does not parse as Python" in reason

    def test_the_parse_check_does_not_apply_to_a_prose_target(self):
        copy, _reason = _splice_corrected_copy(
            DEFECTIVE, ORIGINAL_PASSAGE,
            "# dedented to column zero\nreturn 0.31", "docs/notes.md")
        assert copy, "a markdown target has no Python syntax to violate"

    def test_a_refusal_writes_the_reason_and_not_the_copy(self, mini_repo):
        e = {"severity": 0.85}
        ok = _accept_corrected_copy(
            e, "a passage that is not present anywhere", "x" * 30, DEFECTIVE,
            target_rel=TARGET_REL, by="CODEX", cid="C0001")
        assert ok is False
        assert "corrected_copy" not in e, (
            "a half-stored copy is worse than none: the control would run "
            "against it and report a verdict about the wrong document")
        assert e["corrected_copy_rejected"]

    def test_the_refusal_reaches_the_panel(self, mini_repo):
        e = {"severity": 0.85}
        _accept_corrected_copy(
            e, "a passage that is not present anywhere", "x" * 30, DEFECTIVE,
            target_rel=TARGET_REL, by="CODEX", cid="C0001")
        lines = " ".join(_rejection_lines(e))
        assert "CORRECTED COPY REFUSED" in lines, (
            "a refusal the model never hears about is a refusal that repeats "
            "every round")
        assert "character for character" in lines

    def test_a_refusal_does_not_destroy_a_copy_an_earlier_round_accepted(self):
        e = {"severity": 0.85}
        assert _accept_corrected_copy(
            e, ORIGINAL_PASSAGE, CORRECTED_PASSAGE, DEFECTIVE,
            target_rel=TARGET_REL, by="CODEX", cid="C0001")
        good = e["corrected_copy"]
        _accept_corrected_copy(
            e, "not present anywhere in this file", "y" * 30, DEFECTIVE,
            target_rel=TARGET_REL, by="GEMINI", cid="C0001")
        assert e["corrected_copy"] == good

    def test_the_minimum_anchor_is_a_real_passage_not_a_token(self):
        assert _CORRECTED_ANCHOR_MIN >= 12
        copy, reason = _splice_corrected_copy(
            DEFECTIVE, "0.29", "0.31", TARGET_REL)
        assert copy == "" and "shorter than" in reason, (
            "a four-character anchor that happens to be unique today is an "
            "accident waiting for the next rewrite")


# ─────────────────────────────────────────────────────────────────────────────
# 5. A COPY TAKEN AGAINST AN OLDER TARGET IS RE-SPLICED OR DROPPED
# ─────────────────────────────────────────────────────────────────────────────

class TestAStaleCopyIsNeverMeasured:
    def test_a_rewritten_target_re_splices_the_stored_anchor(self):
        reg = _registry()
        e = reg.entries["C0001"]
        _accept_corrected_copy(e, ORIGINAL_PASSAGE, CORRECTED_PASSAGE, DEFECTIVE,
                               target_rel=TARGET_REL, by="CODEX", cid="C0001")
        rewritten = DEFECTIVE + "\n# an unrelated later edit\n"
        stats = _refresh_stale_corrected_copies(
            reg, rewritten, target_rel=TARGET_REL)
        assert stats == {"resplit": 1, "dropped": 0}
        assert e["corrected_copy"].endswith("# an unrelated later edit\n"), (
            "the copy must describe the target as it is NOW, or the control "
            "measures the rewrite and reports a verdict about the claim")

    def test_a_copy_whose_anchor_no_longer_exists_is_dropped_not_kept(self):
        reg = _registry()
        e = reg.entries["C0001"]
        _accept_corrected_copy(e, ORIGINAL_PASSAGE, CORRECTED_PASSAGE, DEFECTIVE,
                               target_rel=TARGET_REL, by="CODEX", cid="C0001")
        stats = _refresh_stale_corrected_copies(
            reg, '"""Rewritten from scratch."""\n', target_rel=TARGET_REL)
        assert stats == {"resplit": 0, "dropped": 1}
        assert "corrected_copy" not in e
        assert "no longer applies" in e["corrected_copy_rejected"]

    def test_an_unreadable_target_does_not_drop_anything(self):
        """A transient read failure is not evidence that a copy is stale.
        Dropping every copy on an empty read would be a failure rendering as
        housekeeping."""
        reg = _registry()
        e = reg.entries["C0001"]
        _accept_corrected_copy(e, ORIGINAL_PASSAGE, CORRECTED_PASSAGE, DEFECTIVE,
                               target_rel=TARGET_REL, by="CODEX", cid="C0001")
        stats = _refresh_stale_corrected_copies(reg, "", target_rel=TARGET_REL)
        assert stats == {"resplit": 0, "dropped": 0}
        assert e["corrected_copy"]


# ─────────────────────────────────────────────────────────────────────────────
# 6. THE PANEL FACES ONE CONVENTION, NOT TWO
# ─────────────────────────────────────────────────────────────────────────────

class TestOneConventionInEveryPrompt:
    FORM = _corrected_copy_instructions()

    def _prompts(self):
        residuals = {"C0001": {"severity": 0.85, "status": "OPEN",
                               "description": "the clearance is retracted"}}
        finding = {"id": "C0001", "description": "the clearance is retracted"}
        return {
            # ask_corrected_copy=True (2026-08-12): the ask is now gated and
            # defaults OFF, so no live run silently changes what the panel is
            # asked. This class tests that WHEN asked, every prompt states the
            # convention identically — which is only meaningful with it on.
            "round directive": _runnable_falsifier_s2(ask_corrected_copy=True),
            "routing (python)": _routing_resolve_prompt(
                finding, TARGET_REL, DEFECTIVE, "python"),
            "routing (prose)": _routing_resolve_prompt(
                finding, "docs/notes.md", "# notes\n", "prose"),
            "sweep (python)": _sweep_prompt(residuals, TARGET_REL, DEFECTIVE),
            "sweep (prose)": _sweep_prompt(residuals, "docs/notes.md", "# notes\n"),
        }

    def test_every_falsifier_prompt_asks_for_the_corrected_copy(self):
        for name, prompt in self._prompts().items():
            assert "CORRECTED_COPY:" in prompt, name

    def test_the_literal_form_is_identical_in_every_prompt(self):
        """One string, five renderings. The sweep and routing prompts already
        drifted apart once, on prose targets, and the cost was a whole run."""
        for name, prompt in self._prompts().items():
            assert self.FORM in prompt, (
                f"{name} states the convention in its own words; a model that "
                f"sees two forms will answer in a third")

    def test_the_parser_accepts_exactly_what_the_prompt_asks_for(self):
        """Anti-vacuity: the form in the prompt must round-trip through the real
        extractor with a real payload substituted in."""
        filled = (self.FORM
                  .replace("<the same id>", "C0001")
                  .replace(
                      "<the passage EXACTLY as it stands in the target now, "
                      "copied character for character, long enough to occur "
                      "only once>", ORIGINAL_PASSAGE)
                  .replace(
                      "<the same passage with THIS claim, and only this claim, "
                      "corrected>", CORRECTED_PASSAGE))
        got = _extract_corrected_copies(filled)
        assert got == {"C0001": (ORIGINAL_PASSAGE, CORRECTED_PASSAGE)}

    def test_the_reason_travels_with_the_ask(self):
        for name, prompt in self._prompts().items():
            assert "goes QUIET" in prompt, name
            assert "not a patch" in prompt, name

    def test_the_prompt_never_asks_for_the_proposed_fix(self):
        for name, prompt in self._prompts().items():
            assert "not your FIX block" in prompt, (
                f"{name} must say so explicitly: the synthesise-from-the-fix "
                f"route was rejected twice and a model will offer it otherwise")


# ─────────────────────────────────────────────────────────────────────────────
# 7. THE PARSER'S TOLERANCES, AND ITS LIMITS
# ─────────────────────────────────────────────────────────────────────────────

class TestTheParser:
    def test_markdown_emphasis_and_backticks_around_the_id(self):
        for key in ("`C0001`", '"C0001"', "C0001"):
            got = _extract_corrected_copies(_reply(key=key))
            assert list(got) == ["C0001"], key

    def test_a_payload_containing_markdown_fences_survives(self):
        """The reason the payload is sentinel-delimited and not fenced: a prose
        target carries its own ``` fences, and a fence cannot delimit a passage
        cut out of one."""
        original = "Listing A:\n```python\nx = 1\n```\n"
        corrected = "Listing A:\n```python\nx = 2\n```\n"
        got = _extract_corrected_copies(_reply("C0001", original, corrected))
        assert got["C0001"] == (original, corrected)

    def test_two_labelled_copies_in_one_reply_both_parse(self):
        text = _reply("C0001") + _reply("C0002")
        assert sorted(_extract_corrected_copies(text)) == ["C0001", "C0002"]

    def test_the_first_label_wins_case_insensitively(self):
        text = _reply("C0001") + _reply("c0001", "second passage entirely", "z")
        got = _extract_corrected_copies(text)
        assert got["C0001"] == (ORIGINAL_PASSAGE, CORRECTED_PASSAGE)
        assert len(got) == 1

    def test_prose_that_merely_mentions_the_label_yields_nothing(self):
        assert _extract_corrected_copies(
            "I would supply a CORRECTED_COPY but the passage is unclear.") == {}

    def test_an_unterminated_block_yields_nothing(self):
        truncated = _reply().rsplit("<<<CDSFL_END>>>", 1)[0]
        assert _extract_corrected_copies(truncated) == {}, (
            "a truncated reply must produce NO copy rather than a partial one")


# ─────────────────────────────────────────────────────────────────────────────
# 8. WHAT LIMITS `intercepted`, MEASURED
# ─────────────────────────────────────────────────────────────────────────────

class TestWhatLimitsTheInterceptionAnswer:
    """The founder asked why the control speaks for so few falsifiers. The
    answer is measured here rather than reasoned about.

    MEASURED 2026-08-12 over the archive (525 CONFIRMED findings carrying a
    falsifier, 15 runs):

      * the corrected-copy gate withholds `intercepted` from 525/525 = 100%.
        The probe needs NO corrected copy — it replaces the target with an
        unreadable file and asks whether the falsifier's output changes — but it
        sits behind a return that fires first. INCIDENTAL.
      * 65/525 = 12.4% belong to runs whose target is an ABSOLUTE path outside
        the repo root, where the overlay refuses outright. INCIDENTAL: it is a
        path shape, not a property of the falsifier. Every remaining prose
        experiment ships exactly that shape.
      * run standalone on a 215-finding sample, the probe returned a real
        True/False for 214 — 99.5%. The one abstention was a NONDETERMINISTIC
        falsifier, which is the one ESSENTIAL limit: two runs that disagree with
        themselves cannot be compared with a third.
      * 11 of those 215 (5.1%) had a baseline verdict that was not CONFIRMED, so
        today the control stops at INDETERMINATE_BASELINE and never probes —
        yet the probe answered for 10 of them. Faithful baseline is essential to
        the DISCRIMINATION VERDICT and incidental to INTERCEPTION.
    """

    def test_interception_is_withheld_only_because_no_copy_was_supplied(
            self, mini_repo):
        """Without a copy the control abstains — and the abstention is about the
        copy, not about the falsifier: the probe it never ran would have
        answered, which is demonstrated here by running it."""
        rec = run_discrimination_control(
            {"falsifier_code": SOUND_FALSIFIER}, repo_root=str(mini_repo),
            target_rel=TARGET_REL, timeout=60)
        assert rec["outcome"] == DISC_ABSENT
        assert rec["intercepted"] is None

        # The same probe, standalone, with no corrected copy anywhere in it.
        import shutil as _shutil

        from bench.falsifier_verify import execute_python
        from bench.reference_runner_v3 import (
            DISC_TRIPWIRE_BODY, _build_discrimination_overlay,
            _normalise_probe_output, _retarget_falsifier,
        )
        real = _build_discrimination_overlay(mini_repo, TARGET_REL, DEFECTIVE)
        trip = _build_discrimination_overlay(
            mini_repo, TARGET_REL, DISC_TRIPWIRE_BODY)
        try:
            ca, _ = _retarget_falsifier(SOUND_FALSIFIER, mini_repo, real)
            cb, _ = _retarget_falsifier(SOUND_FALSIFIER, mini_repo, trip)
            a = _normalise_probe_output(
                execute_python(ca, repo_root=str(real), timeout=60),
                (real, mini_repo))
            b = _normalise_probe_output(
                execute_python(cb, repo_root=str(trip), timeout=60),
                (trip, mini_repo))
        finally:
            _shutil.rmtree(real, ignore_errors=True)
            _shutil.rmtree(trip, ignore_errors=True)
        assert (b != a) is True, (
            "the interception answer was obtainable the whole time; the "
            "corrected-copy gate is what withheld it")

    def test_an_out_of_repo_target_cannot_be_controlled_at_all(self, tmp_path):
        """CHARACTERISATION, and the dominant limit on prose.

        `_build_discrimination_overlay` mirrors the repo root and refuses an
        absolute path. Every remaining prose experiment names its target with
        one, so on those runs the control returns INDETERMINATE_ERROR before any
        probe — with or without a corrected copy. Nothing is concluded and
        nothing is vetoed, which is the safe direction, but `intercepted` is
        unobtainable there for a reason that has nothing to do with falsifiers.
        This test goes red when the overlay learns out-of-repo targets, which is
        exactly when someone should re-read the measurement above.
        """
        outside = tmp_path / "outside" / "DOC.md"
        outside.parent.mkdir()
        outside.write_text("the retracted clearance is 0.29 mm\n", encoding="utf-8")
        rec = run_discrimination_control(
            {"falsifier_code": "assert 0, 'x'", "corrected_copy": "corrected\n"},
            repo_root=str(tmp_path), target_rel=str(outside), timeout=30)
        assert rec["intercepted"] is None
        assert "could not be built" in rec["detail"]
        assert "repo-relative" in rec["detail"]

    def test_the_prose_experiments_all_name_an_out_of_repo_target(self):
        """Anti-vacuity for the test above: the shape it describes is the shape
        the remaining experiments actually ship."""
        absolute = []
        for cfg_path in sorted((REPO / "bench").glob("exp5*_configs/*.json")):
            try:
                article = json.loads(
                    cfg_path.read_text(encoding="utf-8")).get("test_article") or ""
            except Exception:  # noqa: BLE001
                continue
            if article and Path(article).is_absolute():
                try:
                    Path(article).relative_to(REPO)
                except ValueError:
                    absolute.append(cfg_path.name)
        assert absolute, (
            "no shipped config names an out-of-repo target any more; if that is "
            "a deliberate change, the prose ceiling above must be re-measured")

    def test_the_ingest_still_works_on_an_out_of_repo_target(self, tmp_path):
        """The supply side is NOT limited by the overlay's path rule. A prose
        run can collect and store corrected copies today; only the control's
        overlay refuses them, and the two limits must not be conflated."""
        outside = tmp_path / "outside" / "DOC.md"
        outside.parent.mkdir()
        outside.write_text(
            "Clause 4.2 states the clearance is 0.29 mm, which was retracted.\n",
            encoding="utf-8")
        reg = _registry()
        cfg = RunnerConfig(test_article=str(outside))
        stats = _ingest_corrected_copies(
            reg,
            {"CODEX": _reply("C0001",
                             "the clearance is 0.29 mm",
                             "the clearance is 0.31 mm")},
            3, cfg=cfg, repo_root=str(tmp_path))
        assert stats["accepted"] == 1
        assert "0.31 mm" in reg.entries["C0001"]["corrected_copy"]


# ─────────────────────────────────────────────────────────────────────────────
# 9. THE WIRING ITSELF — the defect being fixed was "built but never called"
# ─────────────────────────────────────────────────────────────────────────────

class TestTheMechanismHasAProductionWriter:
    def test_the_round_loop_calls_the_ingest_before_the_gate(self):
        """The original defect in one sentence: a mechanism with no caller. A
        test that only exercised the helper directly would have passed against
        the broken tree, so the call site is asserted at source level."""
        i = RUNNER_SRC.index("_ingest_corrected_copies(\n            registry, responses")
        j = RUNNER_SRC.index("apply_falsifier_verdicts(registry, round_idx", i)
        assert i < j, (
            "a copy offered in round K must be ingested before round K's gate, "
            "or the control always runs one round behind the evidence")

    def test_the_field_has_exactly_one_writer_in_production(self):
        """Every write goes through the verification in `_accept_corrected_copy`
        or the re-splice that maintains it. A second, unverified writer is how
        an unchecked copy would reach the control."""
        writers = [ln.strip() for ln in RUNNER_SRC.splitlines()
                   if re.search(r"\[.corrected_copy.\]\s*=", ln)]
        assert len(writers) == 2, writers
        tree = ast.parse(RUNNER_SRC)
        fns = {n.name for n in ast.walk(tree)
               if isinstance(n, ast.FunctionDef)
               and '["corrected_copy"] =' in ast.get_source_segment(RUNNER_SRC, n)}
        assert fns == {"_accept_corrected_copy", "_refresh_stale_corrected_copies"}, fns

    def test_the_ingest_never_reads_the_proposed_fix(self):
        """The ASK path is text-only, and stays that way. The fix is read by
        `_derive_corrected_copy_from_fix`, which is deliberately not one of these
        functions: asserted structurally so the two supplies cannot silently
        merge, and so no edit can re-introduce APPLYING a fix as a patch."""
        tree = ast.parse(RUNNER_SRC)
        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef):
                continue
            if node.name not in {
                    "_ingest_corrected_copies", "_accept_corrected_copy",
                    "_splice_corrected_copy", "_refresh_stale_corrected_copies",
                    "_extract_corrected_copies"}:
                continue
            src = ast.get_source_segment(RUNNER_SRC, node) or ""
            assert "proposed_fix" not in src, node.name

    def test_the_post_convergence_sweep_ingests_what_it_is_offered(
            self, mini_repo, monkeypatch):
        """Run the real sweep against a fake panel. A source-string check would
        prove the call is written; only running it proves the call reaches the
        registry with a verified copy attached."""
        import types

        import bench.falsifier_verify as _fv
        from bench import reference_runner_v3 as _R

        reg = _registry(status="OPEN")
        monkeypatch.setattr(
            _R, "dispatch_to_model",
            lambda mc, p, s, enable_tools=False: (_reply("C0001"), 0.1))
        monkeypatch.setattr(
            _fv, "reverify_falsifier",
            lambda code, repo_root=None, timeout=None, **kw: "ERROR")
        exp = types.SimpleNamespace(
            models=[types.SimpleNamespace(label="SIM-A")])
        cfg = RunnerConfig(test_article=TARGET_REL,
                           post_convergence_sweep_rounds=1)
        _R._post_convergence_sweep(reg, exp, cfg, 9, repo_root=str(mini_repo))
        e = reg.entries["C0001"]
        assert e["corrected_copy_source"] == "SIM-A"
        assert CORRECTED_PASSAGE in e["corrected_copy"]

    def test_the_routing_ladder_attaches_the_resolving_rungs_copy(
            self, mini_repo, monkeypatch):
        """The copy and the falsifier it controls must describe the SAME
        instrument, so only the rung that actually resolved the finding has its
        corrected passage attached."""
        import types

        import bench.falsifier_verify as _fv
        from bench import reference_runner_v3 as _R

        reg = _registry(status="UNCONFIRMED", falsifier_code="",
                        escalated=True, falsifier_verdict="UNTOOLABLE")
        monkeypatch.setattr(
            _R, "dispatch_to_model",
            lambda mc, p, s, enable_tools=False: (
                "```python\nassert 0, 'FALSIFIED'\n```\n" + _reply("C0001"), 0.1))
        monkeypatch.setattr(
            _fv, "reverify_falsifier",
            lambda code, repo_root=None, timeout=None, **kw: "CONFIRMED")
        exp = types.SimpleNamespace(
            models=[types.SimpleNamespace(label="SIM-B")])
        cfg = RunnerConfig(test_article=TARGET_REL, routing_enabled=True,
                           falsifier_gate_enabled=True)
        _R._apply_routing(reg, 4, exp, cfg=cfg, repo_root=str(mini_repo))
        e = reg.entries["C0001"]
        assert e["resolved_by_routing"] == "SIM-B"
        assert e["corrected_copy_source"] == "SIM-B"
        assert CORRECTED_PASSAGE in e["corrected_copy"]

    def test_the_reasoning_stays_attached_to_the_code(self):
        i = RUNNER_SRC.index("CORRECTED-COPY INGEST")
        block = RUNNER_SRC[i:i + 4000]
        for needle in ("HAD NO WRITER", "NEVER a source here", "CANNOT truncate",
                       "EVERY REFUSAL IS LOUD"):
            assert needle in block, needle


# ─────────────────────────────────────────────────────────────────────────────
# 10. ONE MODEL MAY NOT SUPPLY THE COPY THAT UN-CONFIRMS ANOTHER MODEL'S CLAIM
#     (adversarial-pass repair, 2026-08-12)
# ─────────────────────────────────────────────────────────────────────────────

class TestOnlyTheInstrumentsOwnerMaySupplyTheCopy:
    """REPRODUCED BEFORE IT WAS FIXED. The round ingest keyed only on the
    canonical id, so any model could attach a corrected copy to any finding and
    the last writer won. Fed SIM-A's honest passage the control returned
    DISCRIMINATES and the finding stayed CONFIRMED; fed SIM-B's cosmetic passage
    in the same round it returned NO_DISCRIMINATION and the finding was
    un-confirmed to OPEN with `mechanical_fault` set — one model rejecting
    another model's critical, with the log blaming the instrument.

    `responses` is filled by `as_completed`, so which model won was not even
    deterministic. The routing ladder already carried the correct rule ("the copy
    and the falsifier it controls have to describe the same instrument"); this is
    that rule applied to the round path.
    """

    def _reg_and_cfg(self):
        # discrimination_control_blocks=True (2026-08-12): blocking now defaults
        # OFF, because whether a non-discriminating falsifier may close a critical
        # changes CONFIRM-only and is a founder decision, not a wiring consequence.
        # This class demonstrates the harm the ownership rule prevents, which only
        # exists when the control is armed — so it arms it explicitly.
        return _registry(model="SIM-A"), RunnerConfig(
            test_article=TARGET_REL, falsifier_gate_enabled=True,
            discrimination_control_blocks=True)

    def test_a_non_owner_copy_is_refused_and_says_who_may_supply(self, mini_repo):
        reg, cfg = self._reg_and_cfg()
        stats = _ingest_corrected_copies(
            reg, {"SIM-B": _reply("C0001")}, 3, cfg=cfg, repo_root=str(mini_repo))
        e = reg.entries["C0001"]
        assert stats == {"offered": 1, "accepted": 0, "refused": 1,
                         "unmatched": 0, "resplit": 0, "dropped": 0}
        assert "corrected_copy" not in e
        assert "SIM-A" in e["corrected_copy_rejected"]
        assert "CORRECTED COPY REFUSED" in " ".join(_rejection_lines(e))

    def test_the_owners_own_copy_is_still_accepted(self, mini_repo):
        reg, cfg = self._reg_and_cfg()
        stats = _ingest_corrected_copies(
            reg, {"SIM-A": _reply("C0001")}, 3, cfg=cfg, repo_root=str(mini_repo))
        assert stats["accepted"] == 1
        assert reg.entries["C0001"]["corrected_copy_source"] == "SIM-A"

    def test_a_non_owner_cannot_overwrite_an_accepted_copy(self, mini_repo):
        reg, cfg = self._reg_and_cfg()
        _ingest_corrected_copies(
            reg,
            {"SIM-A": _reply("C0001"),
             "SIM-B": _reply("C0001", ORIGINAL_PASSAGE,
                             "    # comment reworded; the value is untouched.\n"
                             "    return 0.29")},
            3, cfg=cfg, repo_root=str(mini_repo))
        e = reg.entries["C0001"]
        assert e["corrected_copy_source"] == "SIM-A"
        assert "return 0.31" in e["corrected_copy"]

    def test_the_veto_it_closes_is_real_and_not_hypothetical(self, mini_repo):
        """The end-to-end consequence, run in a real sandbox: with the non-owner
        copy accepted the control un-confirms a sound finding. Asserting the
        outcome under the fix is only worth something if the harm it prevents is
        demonstrated, so the harmful copy is forced onto the entry directly."""
        reg, cfg = self._reg_and_cfg()
        e = reg.entries["C0001"]
        _accept_corrected_copy(
            e, ORIGINAL_PASSAGE,
            "    # comment reworded; the value is untouched.\n    return 0.29",
            DEFECTIVE, target_rel=TARGET_REL, by="SIM-B", cid="C0001")
        apply_falsifier_verdicts(reg, 3, cfg=cfg, repo_root=str(mini_repo))
        assert e["discrimination"]["outcome"] == "NO_DISCRIMINATION"
        assert e["status"] != "CONFIRMED" and e["mechanical_fault"] is True

        # Now the same round through the production ingest, which refuses it.
        reg2, cfg2 = self._reg_and_cfg()
        _ingest_corrected_copies(
            reg2,
            {"SIM-B": _reply("C0001", ORIGINAL_PASSAGE,
                             "    # comment reworded; the value is untouched.\n"
                             "    return 0.29")},
            3, cfg=cfg2, repo_root=str(mini_repo))
        apply_falsifier_verdicts(reg2, 3, cfg=cfg2, repo_root=str(mini_repo))
        e2 = reg2.entries["C0001"]
        assert e2["status"] == "CONFIRMED" and e2["verified"] is True
        assert not e2.get("mechanical_fault")

    def test_an_entry_with_no_recorded_owner_is_not_guessed_at(self, mini_repo):
        reg = _registry(model="SIM-A")
        reg.entries["C0001"].pop("source_model")
        cfg = RunnerConfig(test_article=TARGET_REL)
        stats = _ingest_corrected_copies(
            reg, {"SIM-B": _reply("C0001")}, 3, cfg=cfg, repo_root=str(mini_repo))
        assert stats["accepted"] == 1

    def test_the_routing_rung_that_replaced_the_falsifier_becomes_the_owner(
            self, mini_repo):
        """After routing, the instrument is the RUNG's, not the reporter's."""
        reg = _registry(model="SIM-A", resolved_by_routing="SIM-C")
        cfg = RunnerConfig(test_article=TARGET_REL)
        assert _ingest_corrected_copies(
            reg, {"SIM-A": _reply("C0001")}, 3, cfg=cfg,
            repo_root=str(mini_repo))["accepted"] == 0
        assert _ingest_corrected_copies(
            reg, {"SIM-C": _reply("C0001")}, 3, cfg=cfg,
            repo_root=str(mini_repo))["accepted"] == 1
