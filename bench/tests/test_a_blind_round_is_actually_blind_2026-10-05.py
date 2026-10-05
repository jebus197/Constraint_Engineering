#!/usr/bin/env python3
"""A blind round's sandbox must not contain the other seat's reply.

PANEL REVIEW RUNS IN STAR TOPOLOGY, as the runners do: each seat answers BLIND
first, and a joint round follows once the blind replies are in. A blind round is
only blind if the seat cannot read what the other seat said.

A sandbox is a whole-repository clone, so a blind round stops being blind the
moment an earlier round's replies are harvested into the tree.

THIS WAS RECORDED AS UNFIXED, THEN RECURRED. The 2026-10-03 session state says:
"ROUND 2 WAS NOT BLIND WITH RESPECT TO ROUND 1: every round-2 sandbox contained
round 1's harvested seat evidence, so its richer output cannot be attributed to
the standards alone. The containment fix is to exclude prior rounds' seat evidence
from a blind round's sandbox copy."

On 2026-10-05 it happened again. A cc2 blind re-run was dispatched at 04:33, after
the fable seat's full reply had been harvested into the tree at 03:18. The sandbox
was checked and carried both
`experimental_notes/seat_evidence/<round>/fable_FULL_REPLY.md` and the mirrored
`experimental_notes/evidence/panel_records_*/<round>/fable.json`. The run was killed
rather than allowed to produce a contaminated comparison.

Every assertion here BUILDS A REAL SANDBOX and looks inside it. None reads the
source of `panel_sandbox`, because the defect being guarded is precisely one where
the code described itself correctly and the artefact on disk disagreed.
"""
import json
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from bench import panel_sandbox  # noqa: E402

ROUND = "panelround_blindprobe_2026_10_05"
OTHER_ROUND = "panelround_unrelated_2026_10_05"


@pytest.fixture
def tree(tmp_path):
    """A miniature repository carrying one round's harvested evidence."""
    src = tmp_path / "repo"
    (src / "experimental_notes" / "seat_evidence" / ROUND).mkdir(parents=True)
    (src / "experimental_notes" / "seat_evidence" / ROUND
     / "fable_FULL_REPLY.md").write_text("the other seat's verdict", encoding="utf-8")
    (src / "experimental_notes" / "evidence" / f"panel_records_{ROUND}").mkdir(parents=True)
    (src / "experimental_notes" / "evidence" / f"panel_records_{ROUND}"
     / "fable.json").write_text('{"response": "the other seat"}', encoding="utf-8")
    (src / "experimental_notes" / "seat_evidence" / OTHER_ROUND).mkdir(parents=True)
    (src / "experimental_notes" / "seat_evidence" / OTHER_ROUND
     / "keepme.md").write_text("an unrelated round", encoding="utf-8")
    # A DERIVATIVE DOCUMENT, NOT NAMED FOR THE ROUND. This is the file the
    # path-only purge missed on 2026-10-05: `Panel_FULL_RECORD_Fingerprint_Ladder_
    # 2026-10-05.md` and `The_Blockers_Were_Shown_As_Settled_2026-10-05.md` both
    # carried the other seat's whole verdict, and neither filename contains the
    # round id. The purge reported 0 survivors while the seat could read everything.
    (src / "experimental_notes" / "Panel_FULL_RECORD_Unrelated_Name.md").write_text(
        "A write-up quoting the seat: the other seat's verdict, in full.",
        encoding="utf-8")
    (src / "bench").mkdir()
    (src / "bench" / "ordinary.py").write_text("x = 1\n", encoding="utf-8")
    return src


def _names(dest):
    return {str(q.relative_to(dest)) for q in dest.rglob("*")}


class TestTheDefectReproducesWithoutTheFix:
    def test_an_unguarded_sandbox_carries_the_other_seats_reply(self, tree):
        """ANTI-VACUITY. If this fails, the fixture no longer reproduces the
        condition and every assertion below would pass over nothing."""
        dest = panel_sandbox.build(tree)
        leaked = [n for n in _names(dest) if ROUND in n]
        assert leaked, (
            "a sandbox built WITHOUT blind_of does not carry the round's "
            "evidence, so this guard is not testing the real defect")
        assert any("fable_FULL_REPLY" in n for n in leaked)


class TestABlindSandboxIsBlind:
    def test_the_named_rounds_evidence_is_gone(self, tree):
        dest = panel_sandbox.build(tree, blind_of=(ROUND,))
        leaked = [n for n in _names(dest) if ROUND in n]
        assert not leaked, (
            f"the sandbox still exposes {len(leaked)} artefact(s) of the round it "
            f"must be blind to: {sorted(leaked)[:4]}")

    def test_the_other_seats_actual_text_is_unreachable(self, tree):
        """Not just the path — the CONTENT must not be readable anywhere.

        THIS TEST USED TO PASS WITH `blind_of` ALONE, and that was an artefact of
        a fixture too weak to carry a derivative document. Once the fixture gained
        `Panel_FULL_RECORD_Unrelated_Name.md` — a file holding the whole verdict
        under a name that does not contain the round id, which is exactly what
        happened on 2026-10-05 — the path-only form failed, correctly. Blindness
        needs `blind_text`.
        """
        dest = panel_sandbox.build(
            tree, blind_of=(ROUND,), blind_text=("the other seat's verdict",))
        for q in dest.rglob("*"):
            if q.is_file():
                try:
                    body = q.read_text(encoding="utf-8", errors="ignore")
                except OSError:
                    continue
                assert "the other seat's verdict" not in body, (
                    f"the other seat's reply is readable at {q.relative_to(dest)}")

    def test_unrelated_rounds_are_untouched(self, tree):
        """Additive: purging one round must not remove the rest of the record."""
        dest = panel_sandbox.build(tree, blind_of=(ROUND,))
        kept = [n for n in _names(dest) if OTHER_ROUND in n]
        assert kept, "an unrelated round's evidence was destroyed"
        assert any("keepme" in n for n in kept)

    def test_ordinary_repository_content_survives(self, tree):
        dest = panel_sandbox.build(tree, blind_of=(ROUND,))
        assert (dest / "bench" / "ordinary.py").is_file(), (
            "the purge removed ordinary repository content")


class TestAPathPurgeAloneIsNotEnough:
    """The defect that survived the first fix: content under another name."""

    def test_a_path_only_purge_leaves_the_verdict_readable(self, tree):
        """ANTI-VACUITY for the content check. If this fails, the fixture no
        longer reproduces the 2026-10-05 condition."""
        dest = panel_sandbox.build(tree, blind_of=(ROUND,))
        leaked = [q for q in dest.rglob("*")
                  if q.is_file()
                  and "the other seat's verdict" in q.read_text(errors="ignore")]
        assert leaked, (
            "a path-only purge no longer leaves the verdict readable, so the "
            "content guard below is not testing the real defect")

    def test_the_content_check_finds_it(self, tree):
        dest = panel_sandbox.build(tree)
        found = panel_sandbox.surviving_round_evidence(
            dest, (), ("the other seat's verdict",))
        assert found, "the content verifier cannot see a file carrying the verdict"

    def test_blind_text_removes_the_derivative_document(self, tree):
        dest = panel_sandbox.build(
            tree, blind_of=(ROUND,), blind_text=("the other seat's verdict",))
        for q in dest.rglob("*"):
            if q.is_file():
                assert "the other seat's verdict" not in q.read_text(errors="ignore"), (
                    f"the verdict is still readable at {q.relative_to(dest)}")

    def test_fingerprints_are_drawn_from_the_real_replies(self, tmp_path):
        """`round_fingerprints` must produce phrases from the seat reply itself."""
        rd = tmp_path / "round"
        rd.mkdir()
        body = ("The ladder tries only the first two rungs and both were the same "
                "model, so the climb rehearsed nothing at all in this round. " * 6)
        (rd / "fable.json").write_text(json.dumps({"response": body}), encoding="utf-8")
        (rd / "fable.tools.json").write_text("[]", encoding="utf-8")
        fps = panel_sandbox.round_fingerprints(rd)
        assert fps, "no fingerprints extracted from a non-empty reply"
        assert all(f in body for f in fps), "a fingerprint is not from the reply"
        assert all(len(f) >= 40 for f in fps)


class TestTheDefaultIsUnchanged:
    """Every existing caller passes no blind_of and must behave exactly as before."""

    def test_no_blind_of_purges_nothing(self, tree):
        dest = panel_sandbox.build(tree)
        assert [n for n in _names(dest) if ROUND in n]
        assert [n for n in _names(dest) if OTHER_ROUND in n]

    def test_an_empty_blind_of_purges_nothing(self, tree):
        dest = panel_sandbox.build(tree, blind_of=())
        assert [n for n in _names(dest) if ROUND in n]


class TestItRefusesRatherThanReturningSomethingThatLooksBlind:
    def test_the_survivor_check_is_wired_and_can_speak(self, tree):
        """The refusal path exists and the verifier reports real survivors.

        Held by calling `surviving_round_evidence` on an UNPURGED copy: it must
        report the leak. A verifier that returns empty on a contaminated tree
        would make the refusal in `build` unreachable."""
        dest = panel_sandbox.build(tree)
        survivors = panel_sandbox.surviving_round_evidence(dest, (ROUND,))
        assert survivors, (
            "the verifier reports no survivors on a tree that demonstrably "
            "carries the round, so build()'s refusal could never fire")

    def test_the_purge_reports_what_it_removed(self, tree):
        dest = panel_sandbox.build(tree)
        n = panel_sandbox.purge_round_evidence(dest, (ROUND,))
        assert n >= 2, f"purge reported {n} removals for 2 planted files"
        assert not panel_sandbox.surviving_round_evidence(dest, (ROUND,))


class TestTheDispatcherCanAskForIt:
    """An option nothing can select is an addition nothing reaches.

    CONVERTED FROM A SOURCE-TEXT ASSERTION, 2026-10-05, after the cc2 seat measured
    that the first version pushed the source-text census to 81 against a cap of 80
    and that `test_the_class_has_not_grown_silently` was RED in the delivered tree
    while the report said the census was back at 80. The report was stale: the
    census was measured BEFORE this file was written and never re-measured after.

    `src.count("blind_of=_BLIND_OF") >= 2` could not detect the thing that matters
    either — a NEW `build` call site added without the keyword would leave the
    count at 2 and pass. The check below counts call sites by AST and compares
    against the total, so an unwired one fails.
    """

    def test_the_env_var_actually_reaches_the_module(self, monkeypatch):
        """EXECUTED: set it, import fresh, read the bound value back."""
        import importlib
        monkeypatch.setenv("PANEL_BLIND_OF", "round_alpha,round_beta")
        monkeypatch.setenv("PANEL_BRIEF_UNCHECKED", "1")
        sys.modules.pop("confer_maths_panel_2026-09-05", None)
        spec = importlib.util.spec_from_file_location(
            "confer_maths_panel_probe",
            REPO / "bench" / "confer_maths_panel_2026-09-05.py")
        mod = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(mod)
        except SystemExit:
            pass
        assert tuple(getattr(mod, "_BLIND_OF", ())) == ("round_alpha", "round_beta"), (
            f"PANEL_BLIND_OF did not reach the module; _BLIND_OF = "
            f"{getattr(mod, '_BLIND_OF', None)!r}")

    def test_every_build_call_site_passes_blind_of(self):
        """AST, not a literal count: a NEW unwired call site must fail this."""
        import ast
        src = (REPO / "bench" / "confer_maths_panel_2026-09-05.py").read_text(
            encoding="utf-8")
        total = wired = 0
        for node in ast.walk(ast.parse(src)):
            if not isinstance(node, ast.Call):
                continue
            f = node.func
            if getattr(f, "attr", None) != "build":
                continue
            if getattr(getattr(f, "value", None), "id", None) != "panel_sandbox":
                continue
            total += 1
            if any(k.arg == "blind_of" for k in node.keywords):
                wired += 1
        assert total >= 2, f"only {total} panel_sandbox.build call site(s) found"
        assert wired == total, (
            f"{total - wired} of {total} panel_sandbox.build call site(s) do not "
            f"pass blind_of, so a sandbox built there can never be made blind")
