"""Pins for the 2026-08-05 repairs to resources/RECOVERY.md, resources/MEMORY.md
and resources/MEMORY_EXCLUSIONS.md.

Every one of those defects had the same shape: a document stated something with
confidence that was not true of the thing it described. A pass-count that had
gone stale, a process check that could not match any current runner, a stated
count of "two" over a list of four, a stale model version, a measured FAILURE
rate described as a target, and an exclusion ledger that accounted for 65 files
when 100 were on disk. These tests re-derive each fact from the artefact it
describes, so the next drift is a red test rather than a confident sentence.

Offline: pure filesystem reads. No sockets, no subprocesses.
"""

from __future__ import annotations

import pathlib
import re

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
RECOVERY = REPO / "resources" / "RECOVERY.md"
MIRROR = REPO / "resources" / "MEMORY.md"
import sys as _sys
_sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _private_memory  # noqa: E402

EXCLUSIONS = REPO / "resources" / "MEMORY_EXCLUSIONS.md"
PRIVATE_MEMORY = (
    pathlib.Path.home()
    / ".claude/projects/-Users-georgejackson-Developer-Projects/memory"
)


def _section(text: str, heading: str, stop: str = "\n## ") -> str:
    """Text from `heading` up to the next `stop` marker (or end of file)."""
    start = text.index(heading)
    rest = text[start + len(heading):]
    end = rest.find(stop)
    return rest if end == -1 else rest[:end]


# ---------------------------------------------------------------------------
# M1 — the "current figure" block states a COMMAND, never a pass-count.
# ---------------------------------------------------------------------------

class TestNoPassCountInTheOfflineCorrectionBlock:
    def test_block_states_the_command(self):
        block = _section(
            RECOVERY.read_text(), "## TEST-SUITE OFFLINE CORRECTION"
        )
        assert "python3 -m pytest bench/tests/ -q --netguard-strict" in block

    def test_block_defers_the_number_to_current_state(self):
        block = _section(
            RECOVERY.read_text(), "## TEST-SUITE OFFLINE CORRECTION"
        )
        assert "docs/CURRENT_STATE.md" in block

    def test_block_does_not_send_the_reader_there_for_a_pass_count(self):
        """Added by the adversarial verification pass, 2026-08-05.

        The first repair removed the stale pass-count and told the reader
        "the number lives in docs/CURRENT_STATE.md". It does not. That file
        records a COLLECTION count and says so explicitly, then sends the
        reader back to the command. So the repair moved the confident-wrong
        pointer one document downstream instead of removing it: an agent
        following it lands on a collected figure and can quote it as a pass
        figure. The block must say what CURRENT_STATE.md actually holds.
        """
        current_state = (REPO / "docs" / "CURRENT_STATE.md").read_text()
        if "not a pass count" not in current_state:
            pytest.skip(
                "docs/CURRENT_STATE.md no longer disclaims a pass count — "
                "re-check what the RECOVERY.md block should say about it"
            )
        block = _section(
            RECOVERY.read_text(), "## TEST-SUITE OFFLINE CORRECTION"
        )
        assert "COLLECTION count" in block, (
            "the block names docs/CURRENT_STATE.md without saying that what "
            "lives there is a COLLECTION count, not a pass count"
        )

    def test_block_asserts_no_pass_count_of_its_own(self):
        """The block argued that documents should cite the command and defer
        the number — then stated `2099 passed, 3 skipped` itself. Measured
        2026-08-05 at HEAD 624b39a the true figure was 2549 passed / 7 skipped,
        so the number had been wrong for days while reading as authoritative.
        """
        block = _section(
            RECOVERY.read_text(), "## TEST-SUITE OFFLINE CORRECTION"
        )
        offenders = re.findall(r"\b\d{3,5}\s+(?:passed|skipped|failed)\b", block)
        assert offenders == [], (
            f"the offline-correction block states a pass-count again: "
            f"{offenders}. It must cite the command and defer the number to "
            f"docs/CURRENT_STATE.md, which is regenerated against a commit."
        )


# ---------------------------------------------------------------------------
# M2 — Minimum Recovery item 4 can actually detect a detached runner.
# ---------------------------------------------------------------------------

class TestMinimumRecoveryRunningExperimentCheck:
    def _min_recovery(self) -> str:
        return _section(RECOVERY.read_text(), "## Minimum Recovery")

    def test_no_recovery_command_greps_for_run_round_robin(self):
        """`grep run_round_robin` matches only bench/run_round_robin.py, the
        Bench Run 1 driver. Every Exp 40-54 runner is reference_runner_v3 via
        bench/launch_exp42.py, so the old check reported silence during a live
        run — and silence reads as "nothing is running".

        The name may still appear in the prose that explains why the old check
        was wrong; what must not survive is a COMMAND that uses it.
        """
        commands = [
            ln for ln in self._min_recovery().splitlines()
            if ln.startswith("    ") and ln.strip()
        ]
        offenders = [ln for ln in commands if "run_round_robin" in ln]
        assert offenders == [], (
            f"a runnable recovery command still greps for run_round_robin: "
            f"{offenders}"
        )

    def test_both_current_checks_are_present(self):
        body = self._min_recovery()
        assert "/tmp/exp*_launch*.pid" in body
        assert "reference_runner_v3|detached_launch|launch_exp" in body

    def test_the_pid_glob_matches_both_observed_pidfile_shapes(self):
        """detached_launch.sh writes `${LOG%.log}.pid`, so the pidfile name
        follows the log's. Both `/tmp/exp47_launch_20260728.pid` (underscore)
        and `/tmp/exp53_launch.20260801T015649.pid` (dot) are on the record.
        A glob of `exp*_launch_*.pid` silently misses the second.
        """
        glob = "/tmp/exp*_launch*.pid"
        assert glob in self._min_recovery()
        for observed in (
            "/tmp/exp47_launch_20260728.pid",
            "/tmp/exp53_launch.20260801T015649.pid",
        ):
            assert pathlib.PurePath(observed).match(glob), (
                f"{observed} is not matched by the documented glob {glob}"
            )

    def test_detached_launch_rule_is_cross_referenced(self):
        body = self._min_recovery()
        assert "detached_launch.sh" in body
        assert "CDSFL_Agent_Operational_Plan.md" in body

    def test_items_5_to_8_are_headed_as_superseded_and_item_9_is_not(self):
        body = self._min_recovery()
        banner = body.index("SUPERSEDED HISTORICAL MATERIAL")
        end = body.index("End of superseded block")
        superseded = body[banner:end]
        for n in (5, 6, 7, 8):
            assert re.search(rf"^{n}\. ", superseded, re.M), (
                f"item {n} is not inside the superseded block"
            )
        assert not re.search(r"^9\. ", superseded, re.M), (
            "item 9 (Exp 36 ground truth) is still current and must NOT be "
            "marked superseded"
        )
        assert re.search(r"^9\. ", body[end:], re.M)

    def test_the_dead_plans_path_is_marked_dead(self):
        """`~/.claude/plans/` does not exist; checked 2026-08-05."""
        assert not (pathlib.Path.home() / ".claude" / "plans").exists(), (
            "~/.claude/plans/ now exists — re-check the item-6 annotation "
            "before trusting it"
        )
        body = self._min_recovery()
        idx = body.index("agile-wondering-hejlsberg.md")
        assert "does not exist" in body[idx:idx + 400]


# ---------------------------------------------------------------------------
# M3 — stated counts agree with the lists they introduce.
# ---------------------------------------------------------------------------

class TestStatedCountsMatchTheirLists:
    def test_standing_corrections_count_matches_the_subsections(self):
        """This read "Two directives" over four ### subsections."""
        body = _section(
            RECOVERY.read_text(),
            "## Standing Corrections (Load-Bearing Directives)",
            stop="\n---",
        )
        headings = re.findall(r"^### ", body, re.M)
        words = {1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five"}
        assert body.lstrip().startswith(f"{words[len(headings)]} directives"), (
            f"the section opens with a count that disagrees with the "
            f"{len(headings)} ### subsections that follow it"
        )

    def test_divergence_test_class_count_matches_its_own_list(self):
        """"52 tests across 7 classes" was followed by nine class names."""
        text = RECOVERY.read_text()
        idx = text.index("test_divergence_directive.py` — 52 tests across")
        stated = re.search(r"across\s+(\d+)\s*\n?\s*classes", text[idx:idx + 200])
        assert stated, "could not read the stated class count"
        listed = re.findall(r"Test[A-Za-z0-9]+", text[idx:idx + 500])
        assert int(stated.group(1)) == len(listed), (
            f"stated {stated.group(1)} classes, listed {len(listed)}: {listed}"
        )


# ---------------------------------------------------------------------------
# M4 — the exclusion ledger accounts for every file on disk.
# ---------------------------------------------------------------------------

def _bucket_names(section: str) -> list[str]:
    return sorted(set(re.findall(r"`([a-z0-9_.-]+\.md)`", section)))


class TestMemoryExclusionsAccounting:
    def _doc(self) -> str:
        return EXCLUSIONS.read_text()

    def _stated(self, label: str) -> int:
        row = re.search(rf"\|[^|\n]*{label}[^|\n]*\|\s*\**(\d+)\**\s*\|",
                        self._doc())
        assert row, f"no accounting row for {label!r}"
        return int(row.group(1))

    def test_declared_excluded_entries_are_named_and_counted(self):
        named = _bucket_names(
            _section(self._doc(), "## Excluded Entries")
        )
        assert len(named) == self._stated("Named as excluded"), (
            f"the accounting table and the Excluded Entries section disagree: "
            f"table says {self._stated('Named as excluded')}, section names "
            f"{len(named)}"
        )

    def test_unclassified_entries_are_named_and_counted(self):
        named = _bucket_names(
            _section(self._doc(), "## Unclassified — awaiting review")
        )
        assert len(named) == self._stated("Unclassified"), (
            f"table says {self._stated('Unclassified')} unclassified, section "
            f"names {len(named)}"
        )

    def test_the_four_buckets_sum_to_the_stated_total(self):
        parts = sum(
            self._stated(label)
            for label in (
                "Mirrored", "Named as excluded", "Session handoffs",
                "Unclassified",
            )
        )
        assert parts == self._stated("total")

    def test_no_file_sits_in_two_buckets(self):
        excluded = set(_bucket_names(_section(self._doc(), "## Excluded Entries")))
        unclassified = set(
            _bucket_names(_section(self._doc(), "## Unclassified — awaiting review"))
        )
        assert not (excluded & unclassified)

    def test_every_named_file_exists_on_disk(self):
        _ok, _why = _private_memory.probe(PRIVATE_MEMORY)
        if not _ok:
            # is_dir() alone is NOT a readability test: measured 2026-08-26,
            # it returned True while iterdir() raised PermissionError.
            pytest.skip(_why)
        on_disk = {p.name for p in PRIVATE_MEMORY.iterdir() if p.is_file()}
        named = set(
            _bucket_names(_section(self._doc(), "## Excluded Entries"))
        ) | set(
            _bucket_names(_section(self._doc(), "## Unclassified — awaiting review"))
        )
        missing = sorted(named - on_disk)
        assert not missing, f"named in the ledger but absent from disk: {missing}"

    def test_the_accounting_matches_the_directory(self):
        """The whole point of this document. If a memory file is added and
        nobody classifies it, the residual (files in no named bucket) stops
        equalling the stated "mirrored" count and this goes red.
        """
        _ok, _why = _private_memory.probe(PRIVATE_MEMORY)
        if not _ok:
            # is_dir() alone is NOT a readability test: measured 2026-08-26,
            # it returned True while iterdir() raised PermissionError.
            pytest.skip(_why)
        on_disk = sorted(p.name for p in PRIVATE_MEMORY.iterdir() if p.is_file())
        individual = [n for n in on_disk if n != "MEMORY.md"]
        assert len(individual) == self._stated("total"), (
            f"{len(individual)} individual memory files on disk, ledger states "
            f"{self._stated('total')}"
        )

        excluded = set(_bucket_names(_section(self._doc(), "## Excluded Entries")))
        unclassified = set(
            _bucket_names(_section(self._doc(), "## Unclassified — awaiting review"))
        )
        handoffs = {n for n in individual if n.startswith("handoff_")}
        assert len(handoffs) == self._stated("Session handoffs")

        residual = set(individual) - excluded - unclassified - handoffs
        assert len(residual) == self._stated("Mirrored"), (
            f"{len(residual)} files are in no named bucket, so they should be "
            f"the mirrored ones, but the ledger states "
            f"{self._stated('Mirrored')} mirrored. Newly added memory files "
            f"must be classified: mirror them in MEMORY.md, or name them "
            f"under Excluded Entries or Unclassified."
        )


# ---------------------------------------------------------------------------
# M5 — the public mirror's stale rows and figures.
# ---------------------------------------------------------------------------

class TestPublicMirrorShorthandAndFigures:
    def _doc(self) -> str:
        return MIRROR.read_text()

    def test_cc2_route_is_the_current_panel_version(self):
        """The panel rotated 4.6 -> 4.7 on 2026-05-10; the mirror still said
        4.6. `.claude/CLAUDE.md` is authoritative.
        """
        claude_md = (REPO / ".claude" / "CLAUDE.md").read_text()
        assert "Opus 4.7" in claude_md
        shorthand = _section(self._doc(), "## Shorthand (Metacognitive Commands) Deltas")
        assert "Opus 4.7" in shorthand
        assert "Claude Opus 4.6\n" not in shorthand
        assert "Opus 4.6 CLI" not in shorthand

    def test_gemini_route_is_openrouter_not_google_direct(self):
        shorthand = _section(self._doc(), "## Shorthand (Metacognitive Commands) Deltas")
        assert "Google GenAI" not in shorthand
        assert "Gemini 3.1 Pro Preview via OpenRouter" in shorthand

    @pytest.mark.parametrize("cmd", ["`cy`", "`pr`"])
    def test_missing_shorthand_rows_are_present(self, cmd):
        """Both are in the project .claude/CLAUDE.md MC table and were absent
        from the public mirror entirely.
        """
        shorthand = _section(self._doc(), "## Shorthand (Metacognitive Commands) Deltas")
        assert re.search(rf"^- {re.escape(cmd)} —", shorthand, re.M), (
            f"{cmd} is defined in .claude/CLAUDE.md but missing from the mirror"
        )

    def test_falsification_rate_is_not_described_as_a_target(self):
        """0-13% is the MEASURED P-pass rate — a failure the gate exists to
        close. The mirror called it "the target range for successful
        falsification", which is the project's signature defect in miniature:
        a failure rendered as a success.
        """
        doc = self._doc()
        assert "target range for successful falsification" not in doc
        idx = doc.index("**Falsification gate**")
        entry = doc[idx:idx + 700]
        assert "0–13%" in entry
        assert "MEASURED FAILURE" in entry

    def test_nu_k_correction_count_is_derived_not_asserted(self):
        """The private index summarises this as "2 confer rounds, 12
        corrections". Its own body records 7 (3 hard + 4 soft) then 8
        (5 hard + 3 soft) — 15. The mirror must not repeat the 12 as the total.
        """
        doc = self._doc()
        idx = doc.index("**ν_k novelty metric**")
        entry = doc[idx:idx + 600]
        assert "2 confer rounds, 12 corrections" not in entry
        assert "7 corrections" in entry and "15 in total" in entry

    def test_every_repo_path_named_in_the_mirror_exists(self):
        """A mirror entry that points at a deleted file is a confident lie
        about where the evidence lives. Globs (`experimental_notes/*`) are
        directory references, not files, and are checked as directories.
        """
        refs = set(re.findall(
            r"`((?:docs|resources|scripts|bench|experimental_notes)/[^`\s]+)`",
            self._doc(),
        ))
        missing = []
        for ref in sorted(refs):
            target = REPO / (ref[:-1] if ref.endswith("/*") else ref)
            if not target.exists():
                missing.append(ref)
        assert not missing, f"mirror names paths that do not exist: {missing}"
