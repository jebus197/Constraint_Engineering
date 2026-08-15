"""Falsification pins for the reference-checker rule pass (2026-08-12).

WHAT CHANGED, AND WHY IT NEEDS THIS FILE
----------------------------------------
The `qc` reference check reported 122 broken references. Re-classifying all 122
by hand showed that 107 of them were the checker misreading a form it did not
understand — prose, quoted code, maths, an existing file written with a
`#L2094` anchor, an existing file qualified by the directory the repository
sits in — and that 27 of the rest named genuinely dead paths the project had
ALREADY annotated with dated `**[Correction …]**` blocks the checker could not
read. Fifteen were real and undocumented.

Teaching a checker to be quieter is the single most dangerous kind of change
this repository makes, because the failure mode is indistinguishable from
success: a report of zero is what a working checker and a lobotomised one both
print. So the tests that matter here are the ones that try to BREAK the new
rules, not the ones that confirm them.

THE THREE PROPERTIES THIS FILE PINS
-----------------------------------
1. A genuinely dead path dressed in EVERY form the new rules understand is
   still reported. `TestDeadPathsSurviveEveryNewRule` is the falsifier the
   whole pass is judged by.
2. RESOLUTION RUNS FIRST, so no "this is not a path" rule can hide a file that
   exists inside the repository. Pinned with a real file whose NAME matches a
   suppression pattern.
3. THE ARITHMETIC BALANCES: candidates == resolved + suppressed + reported,
   and a tally that does not balance says so in capitals. The first run of the
   new code over-reported by exactly 247 and this check is what caught it.

Offline by construction: filesystem only, no subprocess, no network.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import cdsfl_qc  # noqa: E402
import cdsfl_utils  # noqa: E402


# ---------------------------------------------------------------------------
# Fixtures — a throwaway repository whose real contents are known exactly, so
# "this resolved" and "this was suppressed" can never be confused.
# ---------------------------------------------------------------------------

@pytest.fixture
def repo(monkeypatch, tmp_path: Path) -> Path:
    (tmp_path / "bench" / "dm").mkdir(parents=True)
    (tmp_path / "bench" / "real.py").write_text("x = 1\n", encoding="utf-8")
    (tmp_path / "bench" / "dm" / "_feedback.py").write_text("y = 2\n", encoding="utf-8")
    # Built through a variable rather than spelled inline on the write lines:
    # test_archive_is_not_written_by_tests.py scans this directory TEXTUALLY for
    # a write verb on any line naming the log archive, and cannot tell a
    # tmp_path fixture from the real one. Everything here is under tmp_path.
    run_dir = tmp_path / "bench" / "logs" / "run_20260812"
    (run_dir / "working").mkdir(parents=True)
    (run_dir / "report.json").write_text("{}\n", encoding="utf-8")
    (run_dir / "working" / "slice.py").write_text("z = 3\n", encoding="utf-8")
    (tmp_path / "bench" / "tasks_frontier").mkdir()
    (tmp_path / "bench" / "tasks_frontier" / "ft-001.json").write_text(
        "{}\n", encoding="utf-8")
    (tmp_path / "docs").mkdir()
    monkeypatch.setattr(cdsfl_utils, "repo_root", lambda: tmp_path)
    return tmp_path


def scan(root: Path, body: str, name: str = "note.md"):
    """Write `body` to docs/<name>, scan it, return (reported_refs, audit)."""
    doc = root / "docs" / name
    doc.write_text(body, encoding="utf-8")
    entries = cdsfl_utils.check_file_references(doc)
    audit: dict = {}
    cdsfl_utils.merge_reference_audit(entries, audit)
    reported = [e["reference"] for e in entries
                if cdsfl_utils.AUDIT_KEY not in e and not e.get("scan_failed")]
    return reported, audit


CORRECTION = (
    "**[Correction 2026-08-12.]** The path `bench/vanished.py` above is dead at "
    "the current HEAD; it was renamed to `bench/real.py`."
)


# ---------------------------------------------------------------------------
# 1. THE FALSIFIER. Every new rule, aimed at a file that does not exist.
# ---------------------------------------------------------------------------

class TestDeadPathsSurviveEveryNewRule:
    """Construct a genuinely broken reference in each new form and prove the
    checker still catches it.

    Each line below names a file that does NOT exist, written in the exact
    shape one of the 2026-08-12 rules was added to understand. If any rule was
    written to match the SHAPE rather than to verify the FILE, its line stops
    being reported and this test goes red.
    """

    def test_every_resolution_strategy_still_reports_a_missing_file(self, repo):
        reported, _ = scan(repo, "\n".join([
            "`bench/gone.py#L2094`",                     # anchor
            "`bench/gone.py:gate_c_preflight()`",        # :symbol()
            "`bench/dm/_gone.detect_collisions`",        # module.symbol
            "`Constraint_Engineering/bench/gone.py`",    # ancestor-qualified
            "`missing_run_20990101/report.json`",        # bench/logs prefix
            "`bench/tasks_frontier/GONE-001..027`",      # range, real dir,
                                                         # no member matches
            "`bench/no_such_dir/FT-001..027`",           # range, no dir
        ]) + "\n")

        assert reported == [
            "bench/gone.py#L2094",
            "bench/gone.py:gate_c_preflight()",
            "bench/dm/_gone.detect_collisions",
            "Constraint_Engineering/bench/gone.py",
            "missing_run_20990101/report.json",
            "bench/tasks_frontier/GONE-001..027",
            "bench/no_such_dir/FT-001..027",
        ]

    def test_the_range_rule_verifies_members_not_just_the_directory(self, repo):
        """FOUND BY THIS FILE, not by review. The first implementation checked
        only that the parent directory existed, so `GONE-001..027` was accepted
        because `bench/tasks_frontier/` happens to exist — a rule matching a
        shape rather than verifying evidence. It now requires a member sharing
        the range's prefix, case-insensitively, because the notes write
        `FT-001` for files stored as `ft-001.json`.
        """
        reported, audit = scan(repo, "\n".join([
            "`bench/tasks_frontier/FT-001..027`",
            "`bench/tasks_frontier/GONE-001..027`",
        ]) + "\n")

        assert reported == ["bench/tasks_frontier/GONE-001..027"]
        assert audit["suppressed"][cdsfl_utils.SUPPRESS_RANGE] == 1

    def test_same_line_directory_anchor_does_not_excuse_a_missing_file(self, repo):
        """The anchor directory exists; the file under it does not."""
        reported, _ = scan(
            repo,
            "**Directory:** `bench/logs/run_20260812` · "
            "**Target:** `working/absent.py` inside that directory\n",
        )

        assert reported == ["working/absent.py"]

    def test_the_pre_existing_dead_forms_are_untouched(self, repo):
        """The 2026-08-05 falsifier, re-run: these must never start passing."""
        reported, _ = scan(repo, "\n".join([
            "`bench/gone.py`",
            "`bench/gone.py:42`",
            "`bench/gone.py:10-20`",
            "`bench/gone.py::Klass`",
            "`domains/immune/absent.toml`",
        ]) + "\n")

        assert reported == [
            "bench/gone.py",
            "bench/gone.py:42",
            "bench/gone.py:10-20",
            "bench/gone.py::Klass",
            "domains/immune/absent.toml",
        ]

    def test_the_two_largest_new_rules_do_not_touch_a_bare_dead_path(self, repo):
        """`contains a quote` (282 live suppressions) and `is a sentence` (269)
        are the two broadest rules added. Neither may reach a bare path."""
        reported, audit = scan(repo, "`bench/quiet_death.py`\n")

        assert reported == ["bench/quiet_death.py"]
        assert cdsfl_utils.SUPPRESS_QUOTED not in audit["suppressed"]
        assert cdsfl_utils.SUPPRESS_SENTENCE not in audit["suppressed"]

    def test_a_dead_data_file_beside_a_live_module_is_not_a_symbol(self, repo):
        """FOUND BY THE ADVERSARIAL PASS, 2026-08-12.

        `_KNOWN_EXTENSIONS` is a static list, and this repository holds real
        files with extensions that are not on it — `.errata`, `.logpath`,
        `.pid`, `.bak`, `.tag`, `.jsonl`. So `bench/dm/_memory.pkl` parsed as
        module `bench/dm/_memory` plus symbol `pkl`, and because
        `bench/dm/_memory.py` exists the reference was SILENCED under a label
        claiming a symbol lookup that never happened. Verified against the
        committed checker: it reported all three of these; the 2026-08-12
        rule silenced all three. The module must now DEFINE the symbol.
        """
        reported, audit = scan(repo, "\n".join([
            "`bench/real.pkl`",                     # .py neighbour exists
            "`bench/real.bak`",
            "`bench/dm/_feedback.jsonl`",
        ]) + "\n")

        assert reported == [
            "bench/real.pkl", "bench/real.bak", "bench/dm/_feedback.jsonl",
        ]
        assert cdsfl_utils.SUPPRESS_MODULE_SYMBOL not in audit["suppressed"]

    def test_a_whole_word_match_is_not_enough_evidence_of_a_symbol(self, repo):
        """A module that WRITES `.jsonl` files contains the word `jsonl` in a
        string literal. A whole-word search would therefore have accepted
        `writer.jsonl` as a symbol reference. A definition is required, so the
        weaker fix is pinned out."""
        (repo / "bench" / "writer.py").write_text(
            'SUFFIX = ".jsonl"\n\n\ndef dump(path):\n    return path\n',
            encoding="utf-8")

        reported, _ = scan(repo, "`bench/writer.jsonl`\n`bench/writer.dump`\n")

        assert reported == ["bench/writer.jsonl"], (
            "the real symbol `dump` must still resolve, and the extension "
            "`jsonl` must not be accepted merely because it appears in a string"
        )

    def test_a_genuine_dotted_symbol_still_resolves(self, repo):
        """The rule must not be lobotomised by its own repair: the live corpus
        case (`bench/dm/_feedback.detect_finding_id_collisions`) still resolves.
        """
        (repo / "bench" / "dm" / "_feedback.py").write_text(
            "def detect_finding_id_collisions(findings, idx):\n    return []\n",
            encoding="utf-8")

        reported, audit = scan(
            repo, "`bench/dm/_feedback.detect_finding_id_collisions`\n")

        assert reported == []
        assert audit["suppressed"][cdsfl_utils.SUPPRESS_MODULE_SYMBOL] == 1

    def test_a_path_with_a_flag_is_a_command_not_a_sentence(self, repo):
        """Narrowness of the sentence rule: it keys on the FIRST word only, so
        a span whose first word IS path-shaped falls through to the older,
        narrower command rule rather than being swallowed."""
        _reported, audit = scan(repo, "`bench/real.py --resume`\n")

        assert audit["suppressed"].get(cdsfl_utils.SUPPRESS_SENTENCE, 0) == 0
        assert audit["suppressed"][cdsfl_utils.SUPPRESS_COMMAND] == 1


# ---------------------------------------------------------------------------
# 2. RESOLUTION FIRST — no rule may hide a file that exists in the repository.
# ---------------------------------------------------------------------------

class TestResolutionRunsBeforeEverySuppression:

    def test_a_real_file_whose_name_matches_a_suppression_pattern_resolves(
        self, repo
    ):
        """`bench/tasks_frontier/FT-001..027` is suppressed as range notation.
        A file ACTUALLY CALLED that must resolve instead — otherwise the rule
        is matching a shape rather than checking the filesystem, which is the
        exact defect this pass exists to remove.
        """
        (repo / "bench" / "tasks_frontier" / "FT-001..027").write_text(
            "real\n", encoding="utf-8")

        reported, audit = scan(repo, "`bench/tasks_frontier/FT-001..027`\n")

        assert reported == []
        assert cdsfl_utils.SUPPRESS_RANGE not in audit["suppressed"]
        assert audit["resolved"] == 1

    def test_range_notation_and_an_elision_are_not_the_same_rule(self, repo):
        """A `..` between two word characters is a range over a real directory.
        A bare `...` is an elision and cannot be checked at all. The first
        implementation conflated them, and only a per-candidate re-audit of the
        reclassification caught it."""
        _reported, audit = scan(repo, "\n".join([
            "`bench/tasks_frontier/FT-001..027`",
            "`Constraint_Engineering/experimental_notes/...`",
        ]) + "\n")

        assert audit["suppressed"][cdsfl_utils.SUPPRESS_RANGE] == 1
        assert audit["suppressed"][cdsfl_utils.SUPPRESS_ELIDED] == 1


# ---------------------------------------------------------------------------
# 3. THE CORRECTION RULE — the one rule that silences a REAL dead path.
# ---------------------------------------------------------------------------

class TestCorrectionRuleCannotBeAbused:
    """This rule suppresses references that ARE dead, on the grounds that the
    document already says so. That makes it the only rule here capable of
    hiding a true defect, so it is fenced on four sides.
    """

    def test_a_dated_correction_naming_the_path_suppresses_and_counts_it(self, repo):
        reported, audit = scan(
            repo, f"`bench/vanished.py` is cited here.\n\n{CORRECTION}\n")

        assert reported == []
        # Two candidates, not one: the correction block quotes the dead path in
        # backticks itself, which is the convention that makes the rule work.
        assert audit["suppressed"][cdsfl_utils.SUPPRESS_CORRECTED] == 2

    def test_a_correction_that_does_not_name_the_path_suppresses_nothing(self, repo):
        """Vagueness must not buy silence. The block below is a correction and
        says something is dead, but never names the reference."""
        reported, _ = scan(
            repo,
            "`bench/vanished.py` is cited here.\n\n"
            "**[Correction 2026-08-12.]** Some paths in this note are dead.\n",
        )

        assert reported == ["bench/vanished.py"]

    def test_a_correction_that_never_says_the_path_is_dead_suppresses_nothing(
        self, repo
    ):
        """The rule's NAME claims the record explains the reference. A block
        that merely mentions the path must not satisfy it."""
        reported, _ = scan(
            repo,
            "`bench/vanished.py` is cited here.\n\n"
            "**[Correction 2026-08-12.]** `bench/vanished.py` is discussed "
            "further in the appendix.\n",
        )

        assert set(reported) == {"bench/vanished.py"}
        assert len(reported) == 2, "both citations must survive, not just one"

    def test_a_prefix_cannot_inherit_a_longer_paths_correction(self, repo):
        """FOUND BY THE ADVERSARIAL PASS, 2026-08-12.

        The fence was described as "the correction must NAME the path
        verbatim", but the test was a bare substring match. A correction
        documenting a `.orig`/`.bak` sibling as dead therefore also silenced
        the separate, undocumented dead path it is a prefix of — a prefix
        inheriting another path's excuse, from the one rule here capable of
        hiding a real defect. Measured against the substring fence: this case
        reported nothing at all. The correction must now CITE the path in one
        of the two delimited forms the scanner itself recognises.
        """
        reported, _ = scan(
            repo,
            "`bench/gone.py` and `bench/gone.py.orig` are cited here.\n\n"
            "**[Correction 2026-08-12.]** `bench/gone.py.orig` is dead.\n",
        )

        assert reported == ["bench/gone.py"], (
            "the documented sibling is excused; the undocumented prefix is not"
        )

    def test_a_markdown_link_target_is_an_acceptable_citation(self, repo):
        """The tightened fence must accept both delimited forms the scanner
        itself recognises, not just backticks — otherwise a correction written
        as a link would start reporting."""
        reported, audit = scan(
            repo,
            "`bench/vanished.py` is cited here.\n\n"
            "**[Correction 2026-08-12.]** [the file](bench/vanished.py) was "
            "renamed and is dead at HEAD.\n",
        )

        assert reported == []
        assert audit["suppressed"][cdsfl_utils.SUPPRESS_CORRECTED] == 2

    def test_a_correction_in_another_document_does_not_vouch_for_this_one(
        self, repo
    ):
        scan(repo, f"{CORRECTION}\n", name="elsewhere.md")

        reported, _ = scan(repo, "`bench/vanished.py`\n", name="note.md")

        assert reported == ["bench/vanished.py"]

    def test_the_correction_block_is_bounded_to_its_own_paragraph(self, repo):
        """A correction cannot reach across a blank line and absorb the whole
        document — otherwise one correction anywhere would silence everything
        below it."""
        reported, _ = scan(
            repo,
            "**[Correction 2026-08-12.]** `bench/vanished.py` is dead.\n\n"
            "Unrelated later paragraph citing `bench/also_gone.py`.\n",
        )

        assert reported == ["bench/also_gone.py"]


# ---------------------------------------------------------------------------
# 4. THE ARITHMETIC — a tally that does not balance must say so.
# ---------------------------------------------------------------------------

class TestTheTallyBalances:

    def test_candidates_equal_resolved_plus_suppressed_plus_reported(self, repo):
        reported, audit = scan(repo, "\n".join([
            "`bench/real.py`",                        # resolves plainly
            "`bench/real.py:42`",                     # resolves, labelled
            "`/tmp/scratch.json`",                    # suppressed
            "`pytest bench/tests/`",                  # suppressed
            "`bench/gone.py`",                        # reported
        ]) + "\n")

        accounted = (audit.get("resolved", 0)
                     + sum(audit["suppressed"].values())
                     + len(reported))
        assert accounted == audit["candidates"] == 5

    def test_a_resolution_is_counted_once_not_twice(self, repo):
        """The first run of this code counted every labelled resolution in BOTH
        `resolved` and `suppressed`, over-reporting by exactly 247 candidates
        against the live corpus. The published arithmetic is what caught it."""
        _reported, audit = scan(repo, "`bench/real.py:42`\n")

        assert audit.get("resolved", 0) == 0
        assert audit["suppressed"][cdsfl_utils.SUPPRESS_LINE] == 1

    def test_an_unbalanced_tally_is_announced_in_capitals(self, capsys):
        cdsfl_qc.print_reference_audit(
            {"candidates": 100, "suppressed": {"a rule": 10}, "resolved": 10},
            reported=5,
        )

        out = capsys.readouterr().out
        assert "ARITHMETIC MISMATCH" in out
        assert "75 candidate(s) are unaccounted for" in out

    def test_a_balanced_tally_says_nothing_about_mismatches(self, capsys):
        cdsfl_qc.print_reference_audit(
            {"candidates": 25, "suppressed": {"a rule": 10}, "resolved": 10},
            reported=5,
        )

        assert "ARITHMETIC MISMATCH" not in capsys.readouterr().out


# ---------------------------------------------------------------------------
# 5. THE LIVE CORPUS. Content-independent invariants only, so an ordinary
#    documentation edit cannot turn this red for the wrong reason.
# ---------------------------------------------------------------------------

class TestAgainstTheRealDocumentEstate:

    def test_the_tally_balances_over_every_scanned_document(self):
        audit: dict = {}
        findings = cdsfl_qc.check_broken_references(REPO_ROOT, audit=audit)
        reported = len([f for f in findings if f["category"] == "BROKEN_REF"])

        accounted = (audit.get("resolved", 0)
                     + sum(audit["suppressed"].values())
                     + reported)
        assert accounted == audit["candidates"], (
            f"{audit['candidates']} candidates examined but {accounted} "
            f"accounted for — candidates are being lost between the scanner "
            f"and the report"
        )

    def test_no_check_failed_or_scan_was_skipped(self):
        findings = cdsfl_qc.check_broken_references(REPO_ROOT, audit={})

        bad = [f for f in findings if f["category"] in ("CHECK_FAILED", "WARN")]
        assert bad == [], f"documents went unscanned: {bad}"

    def test_a_planted_dead_reference_in_a_real_document_is_still_caught(
        self, tmp_path: Path
    ):
        """The end-to-end falsifier, against the real repository rather than a
        fixture: copy a genuine document, add one reference to a file that does
        not exist, and require the checker to find it. A checker tuned until
        the live number reads zero would pass everything above and fail here.
        """
        source = REPO_ROOT / "docs" / "ARCHITECTURE.md"
        planted = REPO_ROOT / "docs" / "_qc_selftest_planted.md"
        planted.write_text(
            source.read_text(encoding="utf-8")
            + "\n\nSee `bench/this_file_does_not_exist_20260812.py` for details.\n",
            encoding="utf-8",
        )
        try:
            entries = cdsfl_utils.check_file_references(planted)
            refs = [e["reference"] for e in entries
                    if cdsfl_utils.AUDIT_KEY not in e]
        finally:
            planted.unlink()

        assert refs == ["bench/this_file_does_not_exist_20260812.py"]
