"""Regression pins for the 2026-08-05 repairs to ``scripts/cdsfl_recover.py``.

The governing defect class in every case: a failed lookup rendered as a
confident, quiet "nothing to report". These tests pin the four repairs:

  R1  PENDING WORK reads between ``<!-- SV:PENDING_START -->`` and
      ``<!-- SV:PENDING_END -->`` — the markers ``scripts/cdsfl_sv.py``
      actually writes — instead of ``NEXT STEPS:`` / ``ARCHITECTURAL GAPS``,
      which were deleted from RECOVERY.md in April 2026 (commit f5e73ab) and
      left the section printing "(No pending work section found)" for 113 days.
  R2  A FIRST READ section names the operational tracker and the live work
      queue, and is printed before everything else.
  R3  The live git state is printed BEFORE the echoed docs/CURRENT_STATE.md
      snapshot, and the snapshot is labelled as a point-in-time file rather
      than current truth.
  R4  Every absence branch distinguishes "genuinely nothing there" from
      "the probe failed"; the failure form is prefixed ``!!``.

OFFLINE: nothing here runs git or pytest or dispatches a model. ``main()`` is
deliberately never called — it invokes ``git_state()``, which runs
``git fetch``. Section ORDER is pinned by reading the source of ``main()``,
which needs no execution.
"""

from __future__ import annotations

import inspect
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import cdsfl_recover  # noqa: E402
from cdsfl_recover import (  # noqa: E402
    PENDING_END,
    PENDING_START,
    experiment_absence_lines,
    first_read_lines,
    pending_work_lines,
)

LOUD = "!!"


def _text(lines: list[str]) -> str:
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# R1 — PENDING WORK reads the markers the writer emits
# ─────────────────────────────────────────────────────────────────────────────

def _recovery_file(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "RECOVERY.md"
    path.write_text(
        f"# Recovery\n\nprelude\n\n{PENDING_START}\n{body}\n{PENDING_END}\n\ntail\n",
        encoding="utf-8",
    )
    return path


def test_pending_work_reads_between_the_sv_markers(tmp_path: Path) -> None:
    path = _recovery_file(tmp_path, "## Current Pending Work (test)\n\nfinish the thing")
    out = _text(pending_work_lines(path))
    assert "finish the thing" in out
    assert LOUD not in out


def test_pending_work_ignores_the_dead_april_markers(tmp_path: Path) -> None:
    """The old probe searched for these two strings. Their absence must not
    empty the section, because the marker block is what carries the content."""
    path = _recovery_file(tmp_path, "real pending work")
    assert "NEXT STEPS:" not in path.read_text(encoding="utf-8")
    assert "ARCHITECTURAL GAPS" not in path.read_text(encoding="utf-8")
    assert "real pending work" in _text(pending_work_lines(path))


def test_recover_source_no_longer_chases_the_dead_markers() -> None:
    src = Path(cdsfl_recover.__file__).read_text(encoding="utf-8")
    body = src.split("# ── Loud-failure convention", 1)[1]
    # The dead markers may only appear inside the comment that explains them.
    assert 'read_section(recovery, "NEXT STEPS:"' not in body
    assert '"\\nARCHITECTURAL GAPS"' not in body


def test_pending_work_missing_markers_is_loud_not_empty(tmp_path: Path) -> None:
    path = tmp_path / "RECOVERY.md"
    path.write_text("# Recovery\n\nlots of content, no markers\n", encoding="utf-8")
    out = _text(pending_work_lines(path))
    assert out.startswith(f"  {LOUD} LOOKUP FAILED")
    assert "UNKNOWN, not absent" in out
    assert PENDING_START in out  # names the marker it could not find
    assert "cdsfl_sv.py" in out  # names who writes it


def test_pending_work_missing_file_is_loud(tmp_path: Path) -> None:
    out = _text(pending_work_lines(tmp_path / "nope.md"))
    assert LOUD in out
    assert "UNKNOWN, not absent" in out


def test_pending_work_empty_block_reads_differently_from_failure(tmp_path: Path) -> None:
    """A real absence and a failed lookup must not render identically."""
    empty = _text(pending_work_lines(_recovery_file(tmp_path, "")))
    broken = _text(pending_work_lines(tmp_path / "gone.md"))
    assert LOUD not in empty
    assert LOUD in broken
    assert "real absence" in empty
    assert empty != broken


def test_pending_work_cap_is_stated_not_silent(tmp_path: Path) -> None:
    body = "\n".join(f"line {i}" for i in range(200))
    out = _text(pending_work_lines(_recovery_file(tmp_path, body), max_lines=10))
    assert "line 0" in out
    assert "line 9" in out
    assert "line 10" not in out.split("[CAP")[0]
    assert "CAP: showing the first 10 of 200 lines" in out
    assert "190 lines withheld" in out


def test_pending_work_under_cap_says_nothing_about_a_cap(tmp_path: Path) -> None:
    out = _text(pending_work_lines(_recovery_file(tmp_path, "a\nb\nc"), max_lines=10))
    assert "CAP" not in out


@pytest.mark.skipif(
    not (REPO_ROOT / "resources" / "RECOVERY.md").exists(),
    reason="resources/RECOVERY.md not present in this checkout",
)
def test_pending_work_is_non_empty_against_the_real_recovery_file() -> None:
    """The day-one test that would have caught the 113-day silence."""
    out = _text(pending_work_lines(REPO_ROOT / "resources" / "RECOVERY.md"))
    assert LOUD not in out
    assert "No pending work section found" not in out
    assert len(out.strip()) > 200


# ─────────────────────────────────────────────────────────────────────────────
# R2 — FIRST READ names the tracker and the queue, and comes first
# ─────────────────────────────────────────────────────────────────────────────

def test_first_read_names_tracker_mirror_and_queue() -> None:
    out = _text(first_read_lines(REPO_ROOT))
    assert "Desktop/CDSFL_Agent_Operational_Plan.md" in out
    assert "experimental_notes/CDSFL_Agent_Operational_Plan.md" in out
    assert "experimental_notes/OUTSTANDING_QUEUE_to_BR2.md" in out


def test_first_read_flags_a_missing_required_file_loudly(tmp_path: Path) -> None:
    out = _text(first_read_lines(tmp_path))  # empty tree: mirror + queue absent
    assert f"{LOUD} MISSING" in out
    assert "REQUIRED reading and is absent" in out


def test_first_read_section_is_printed_before_every_other_section() -> None:
    src = inspect.getsource(cdsfl_recover.main)
    first = src.index('"\\n## FIRST READ')
    for later in ("## GIT STATE", "## SAVED SNAPSHOT", "## LATEST EXPERIMENT",
                  "## PENDING WORK", "## KEY FILES"):
        assert first < src.index(later), f"FIRST READ must precede {later}"


# ─────────────────────────────────────────────────────────────────────────────
# R3 — live git before the saved snapshot, and the snapshot labelled
# ─────────────────────────────────────────────────────────────────────────────

def test_live_git_state_is_printed_before_the_echoed_snapshot() -> None:
    src = inspect.getsource(cdsfl_recover.main)
    assert src.index("## GIT STATE") < src.index("## SAVED SNAPSHOT")


def test_snapshot_section_is_labelled_as_a_point_in_time_file() -> None:
    src = inspect.getsource(cdsfl_recover.main)
    assert "## SAVED SNAPSHOT" in src
    assert "NOT current truth" in src
    assert "GIT STATE wins" in src
    # The snapshot is labelled, not deleted — it carries prose the live check lacks.
    assert 'root / "docs" / "CURRENT_STATE.md"' in src
    assert "current_state.read_text" in src


def test_snapshot_section_is_not_titled_current_state() -> None:
    """'## CURRENT STATE' above a contradicting live block is the false label."""
    src = inspect.getsource(cdsfl_recover.main)
    assert '"\\n## CURRENT STATE\\n"' not in src


# ─────────────────────────────────────────────────────────────────────────────
# R4 — absence branches: real absence vs failed lookup
# ─────────────────────────────────────────────────────────────────────────────

def test_experiment_absence_no_logs_dir_is_a_real_absence(tmp_path: Path) -> None:
    out = _text(experiment_absence_lines(tmp_path / "logs"))
    assert LOUD not in out
    assert "no experiment has run" in out


def test_experiment_absence_empty_logs_dir_is_a_real_absence(tmp_path: Path) -> None:
    logs = tmp_path / "logs"
    logs.mkdir()
    (logs / "confer_something").mkdir()
    out = _text(experiment_absence_lines(logs))
    assert LOUD not in out
    assert "no exp<N>_* directories" in out


def test_experiment_absence_with_exp_dirs_present_is_loud(tmp_path: Path) -> None:
    """109 exp dirs on disk while the section printed '(No experiment logs
    found)' is the exact shape this pins against."""
    logs = tmp_path / "logs"
    logs.mkdir()
    for name in ("exp49_live_20260729", "exp53_control_20260801", "exp42_x"):
        (logs / name).mkdir()
    out = _text(experiment_absence_lines(logs))
    assert f"{LOUD} LOOKUP FAILED" in out
    assert "3 exp<N>_* directories" in out
    assert "UNKNOWN, not absent" in out


def test_absence_and_failure_forms_are_distinguishable(tmp_path: Path) -> None:
    logs = tmp_path / "logs"
    logs.mkdir()
    real_absence = _text(experiment_absence_lines(logs))
    (logs / "exp50_run").mkdir()
    failed_lookup = _text(experiment_absence_lines(logs))
    assert real_absence != failed_lookup
    assert LOUD not in real_absence
    assert LOUD in failed_lookup


def test_remaining_absence_branches_are_loud_in_main() -> None:
    """Each of these used to print a quiet message covering both cases."""
    src = inspect.getsource(cdsfl_recover.main)
    for probe in (
        "!! LOOKUP FAILED: git returned no commit",       # git_state sentinels
        "!! LOOKUP FAILED: git log returned no commits",  # empty recent_log
        "!! LOOKUP FAILED: pytest collection",            # test_count() -> None
        "!! LOOKUP FAILED: resources/ONBOARDING.md exists",  # missing section
        "!! MISSING:",                                    # key_files
    ):
        assert probe in src, f"missing loud branch: {probe}"


def test_working_tree_is_unknown_not_clean_when_git_fails() -> None:
    """An empty `git status --porcelain` from a git that answered nothing
    looks exactly like a clean tree. Detached HEAD is NOT a failure, so the
    liveness signal is the commit hash, not the branch name."""
    src = inspect.getsource(cdsfl_recover.main)
    assert 'git_ok = gs["last_hash"] not in ("", "unknown")' in src
    assert "Working tree: UNKNOWN" in src
    assert "detached HEAD" in src


def test_key_files_missing_marker_is_a_word_not_a_bang(tmp_path: Path) -> None:
    """The old marker was a bare '! ' prefix that read as decoration."""
    src = inspect.getsource(cdsfl_recover.main)
    assert 'exists = "  " if full.exists() else "! "' not in src
    assert 'print(f"  !! MISSING: {path} — {desc}")' in src


def test_test_count_line_says_collected_not_passed() -> None:
    src = inspect.getsource(cdsfl_recover.main)
    assert "collection count, NOT a pass count" in src


def test_higher_unreported_experiments_are_named_when_available() -> None:
    """cdsfl_utils.latest_experiment() may report experiment numbers it passed
    over. Reading it with .get() keeps this working against versions of
    cdsfl_utils that do not supply the key."""
    src = inspect.getsource(cdsfl_recover.main)
    assert 'exp.get("skipped_higher")' in src
    assert "UNREPORTED," in src


# ─────────────────────────────────────────────────────────────────────────────
# WHAT main() ACTUALLY PRINTS — added by the adversarial verification pass,
# 2026-08-05, because every test above this line reads the SOURCE of main()
# and a source assertion cannot see a wiring fault.
#
# Measured against this file as first written: three mutations of
# scripts/cdsfl_recover.py left it 24/24 GREEN.
#   1. main() restored to `print("  (No experiment logs found)")` with
#      experiment_absence_lines() still defined and still unit-tested — i.e.
#      the exact R4a defect back in place, suite green.
#   2. The git `!! LOOKUP FAILED` branch made unreachable (`if False and ...`)
#      — the string stays in the source, so the source assertion still passes.
#   3. first_read_lines(root) called and its result discarded — FIRST READ
#      computed, nothing printed.
# That is the project's own "unit-green is not integration-live" failure. The
# tests below drive main() and read stdout, which closes it.
#
# OFFLINE: main()'s only subprocess-backed probes are git_state(),
# latest_experiment() and test_count(); all three are replaced here, so
# nothing below launches a process or opens a socket.
# ─────────────────────────────────────────────────────────────────────────────

_GIT_OK = {
    "branch": "exp39-experimental",
    "clean": False,
    "uncommitted": ["M scripts/cdsfl_recover.py"],
    "last_hash": "abc1234",
    "last_message": "a commit",
    "last_date": "2026-08-05 14:08:53 +0100",
    "remote_sync": "up to date with origin/exp39-experimental",
    "recent_log": ["abc1234 a commit"],
}

_GIT_DEAD = {
    "branch": "",
    "clean": True,          # empty `git status --porcelain` — looks clean
    "uncommitted": [],
    "last_hash": "unknown",
    "last_message": "unknown",
    "last_date": "",
    "remote_sync": "unknown (rev-list vs origin/main failed)",
    "recent_log": [],
}


def _run_main(monkeypatch, capsys, tmp_path: Path, *, gs=None, exp=None) -> str:
    monkeypatch.setattr(cdsfl_recover, "repo_root", lambda: tmp_path)
    monkeypatch.setattr(cdsfl_recover, "git_state", lambda: gs or _GIT_OK)
    monkeypatch.setattr(cdsfl_recover, "latest_experiment", lambda: exp)
    monkeypatch.setattr(cdsfl_recover, "test_count", lambda: None)
    monkeypatch.setattr(sys, "argv", ["cdsfl_recover.py"])
    cdsfl_recover.main()
    return capsys.readouterr().out


def test_main_output_starts_with_first_read_then_live_git_then_snapshot(
    monkeypatch, capsys, tmp_path: Path,
) -> None:
    """R2 + R3 pinned on the OUTPUT, not on the source ordering."""
    out = _run_main(monkeypatch, capsys, tmp_path)
    assert out.index("## FIRST READ") < out.index("## GIT STATE")
    assert out.index("## GIT STATE") < out.index("## SAVED SNAPSHOT")
    assert out.index("## SAVED SNAPSHOT") < out.index("## LATEST EXPERIMENT")
    # FIRST READ must actually name the tracker, not merely compute it.
    assert "CDSFL_Agent_Operational_Plan.md" in out
    assert "OUTSTANDING_QUEUE_to_BR2.md" in out


def test_main_snapshot_banner_warns_beyond_the_git_block(
    monkeypatch, capsys, tmp_path: Path,
) -> None:
    """The echoed snapshot carries a whole stale report — including its own
    'Latest Experiment: No experiment logs found.' — and it is printed ABOVE
    the live LATEST EXPERIMENT section. A banner that names only GIT STATE
    leaves the same false-first ordering R3 exists to remove."""
    out = _run_main(monkeypatch, capsys, tmp_path)
    # [0] is the rest of the heading line; [1] is the banner paragraph.
    banner = out.split("## SAVED SNAPSHOT", 1)[1].split("\n\n")[1]
    assert "GIT STATE wins" in banner
    assert "Latest" in banner and "Recent Commits" in banner


def test_main_prints_the_loud_experiment_branch_not_the_quiet_one(
    monkeypatch, capsys, tmp_path: Path,
) -> None:
    """The R4a headline defect: '(No experiment logs found)' printed while
    109 exp<N>_* directories sat on disk. Pinned at the CALL SITE."""
    logs = tmp_path / "bench" / "logs"
    logs.mkdir(parents=True)
    (logs / "exp53_zero_plant_control").mkdir()
    out = _run_main(monkeypatch, capsys, tmp_path, exp=None)
    assert "(No experiment logs found)" not in out
    assert f"{LOUD} LOOKUP FAILED" in out.split("## LATEST EXPERIMENT", 1)[1]
    assert "1 exp<N>_* directories" in out


def test_main_prints_unknown_not_clean_when_git_is_dead(
    monkeypatch, capsys, tmp_path: Path,
) -> None:
    """An empty `git status --porcelain` from a git that answered nothing is
    indistinguishable from a clean tree. Pinned on the printed line."""
    out = _run_main(monkeypatch, capsys, tmp_path, gs=_GIT_DEAD)
    assert f"{LOUD} LOOKUP FAILED: git returned no commit." in out
    assert "Working tree: UNKNOWN" in out
    assert "Working tree: clean" not in out
    assert f"{LOUD} LOOKUP FAILED: git log returned no commits." in out


def test_main_git_ok_still_reports_a_clean_tree_plainly(
    monkeypatch, capsys, tmp_path: Path,
) -> None:
    """The loud branch must not cry wolf on a healthy repo."""
    healthy = dict(_GIT_OK, clean=True, uncommitted=[])
    out = _run_main(monkeypatch, capsys, tmp_path, gs=healthy)
    assert "Working tree: clean" in out
    assert "git returned no commit" not in out


def test_main_pending_work_body_reaches_the_output(
    monkeypatch, capsys, tmp_path: Path,
) -> None:
    """R1 pinned at the call site: the marker block must reach stdout."""
    (tmp_path / "resources").mkdir()
    (tmp_path / "resources" / "RECOVERY.md").write_text(
        f"# Recovery\n\n{PENDING_START}\nfinish the falsifier work\n{PENDING_END}\n",
        encoding="utf-8",
    )
    out = _run_main(monkeypatch, capsys, tmp_path)
    assert "finish the falsifier work" in out.split("## PENDING WORK", 1)[1]
    assert "No pending work section found" not in out


# ═════════════════════════════════════════════════════════════════════════════
# X1–X4 — the integration-gate residuals, 2026-08-05.
#
#   X1  RECOVERY.md is read ABOVE the sv pending-work markers as well as
#       between them, and NEITHER section claims recency it did not verify.
#       The markers stay where they are: sv owns the region between them.
#   X2  Both gammas are printed and labelled; the gate input is named.
#   X3  The experiment target is existence-checked like the KEY FILES list.
#   X4  A live process/pidfile check exists at all, with three distinct
#       states — running / nothing running / the check itself failed.
#
# OFFLINE: every process probe below is injected. The two tests that let the
# real `ps` run are marked; `ps` is not in the netguard's binary list and
# opens no socket.
# ═════════════════════════════════════════════════════════════════════════════

import json as _json  # noqa: E402
import os as _os      # noqa: E402
import re as _re      # noqa: E402

from cdsfl_recover import (  # noqa: E402
    gamma_lines,
    recovery_head_lines,
    running_experiment_lines,
    target_lines,
)

# A RECOVERY.md with the real file's shape: the NEWEST state block sits above
# the start marker (hand-written), an OLDER one inside it (sv-regenerated).
_SHAPED_RECOVERY = f"""# Recovery Protocol

## CORRECTION — 2026-08-05 14:05 BST: the newest thing in the file

this block is above the marker and was never read

## SESSION STATE — 2026-08-04 03:54 BST (READ THIS FIRST)

nor was this one

{PENDING_START}
## Current Pending Work (2026-06-03, post-divergence-study)

Exp 42 was stopped 2026-06-02.
{PENDING_END}

## Standard Recovery
"""


def _shaped(tmp_path: Path) -> Path:
    path = tmp_path / "RECOVERY.md"
    path.write_text(_SHAPED_RECOVERY, encoding="utf-8")
    return path


# ─────────────────────────────────────────────────────────────────────────────
# X1 — the material above the markers is read, and recency is never asserted
# ─────────────────────────────────────────────────────────────────────────────

def test_head_region_reaches_the_material_above_the_start_marker(tmp_path: Path) -> None:
    """THE X1 defect: everything genuinely current sat above the marker and was
    never printed, so a fresh agent was told the project sits at 3 June."""
    out = _text(recovery_head_lines(_shaped(tmp_path)))
    assert "the newest thing in the file" in out
    assert "READ THIS FIRST" in out
    assert LOUD not in out


def test_head_region_stops_at_the_marker_and_does_not_swallow_pending(
    tmp_path: Path,
) -> None:
    out = _text(recovery_head_lines(_shaped(tmp_path)))
    assert "Exp 42 was stopped" not in out
    assert "Standard Recovery" not in out  # that lives BELOW the end marker


def test_head_region_reports_the_newest_date_it_actually_parsed(tmp_path: Path) -> None:
    out = _text(recovery_head_lines(_shaped(tmp_path)))
    assert "Newest date parsed in this region: 2026-08-05" in out
    assert "line 3" in out  # where that heading really is


def test_pending_region_reports_its_own_newest_date_not_the_files(
    tmp_path: Path,
) -> None:
    """The marked region's newest heading is 2026-06-03. It must say so — the
    contrast with the head region's 2026-08-05 IS the recovery signal."""
    out = _text(pending_work_lines(_shaped(tmp_path)))
    assert "Newest date parsed in this region: 2026-06-03" in out


def test_the_above_is_the_most_recent_claim_is_gone(tmp_path: Path) -> None:
    """It was true of the marked region and false about the document, and it
    was stated as fact either way."""
    src = Path(cdsfl_recover.__file__).read_text(encoding="utf-8")
    assert "the above is the most recent" not in src
    body = "\n".join(f"line {i}" for i in range(200))
    capped = _text(pending_work_lines(_recovery_file(tmp_path, body), max_lines=10))
    assert "most recent" not in capped
    # the cap itself is still stated, and still honestly
    assert "CAP: showing the first 10 of 200 lines" in capped
    assert "190 lines withheld" in capped


def test_pending_provenance_names_the_markers_and_the_line_range(
    tmp_path: Path,
) -> None:
    out = _text(pending_work_lines(_shaped(tmp_path)))
    assert PENDING_START in out and PENDING_END in out
    assert "cdsfl_sv.py regenerates" in out
    assert _re.search(r"lines \d+-\d+", out)


def test_provenance_line_numbers_match_the_file(tmp_path: Path) -> None:
    """Line numbers are measured against the real text, not assumed from the
    marker position — a wrong line number is a confident wrong answer."""
    path = _shaped(tmp_path)
    lines = path.read_text(encoding="utf-8").splitlines()
    start_no = lines.index(PENDING_START) + 1
    end_no = lines.index(PENDING_END) + 1
    head = _text(recovery_head_lines(path))
    pend = _text(pending_work_lines(path))
    assert f"(line {start_no})" in head
    assert f"(line {start_no})" in pend and f"(line {end_no})" in pend
    # head covers 1..last non-blank line above the marker
    assert f"lines 1-{start_no - 2}" in head
    # body covers the first line after the marker to the line before the end
    assert f"lines {start_no + 1}-{end_no - 1}" in pend


def test_head_region_undated_headings_are_counted_not_hidden(tmp_path: Path) -> None:
    """'No heading carries a date' and 'the parser missed them all' must not
    render identically — the count is what separates them."""
    path = tmp_path / "RECOVERY.md"
    path.write_text(f"# R\n\n## Minimum Recovery\n\nx\n\n{PENDING_START}\nb\n{PENDING_END}\n",
                    encoding="utf-8")
    out = _text(recovery_head_lines(path))
    assert "1 '##' heading(s) scanned; 0 carried a parseable date" in out
    assert "No heading in this region carried a parseable date" in out
    assert LOUD not in out


def test_head_region_cap_names_every_withheld_heading(tmp_path: Path) -> None:
    filler = "\n".join(f"body {i}" for i in range(30))
    path = tmp_path / "RECOVERY.md"
    path.write_text(
        f"## First — 2026-08-05\n{filler}\n## Withheld — 2026-07-01\nx\n"
        f"{PENDING_START}\nb\n{PENDING_END}\n",
        encoding="utf-8",
    )
    out = _text(recovery_head_lines(path, max_lines=5))
    assert "CAP: showing the first 5 of" in out
    assert "## Withheld — 2026-07-01" in out       # named, not silently dropped
    assert "2026-07-01" in out


def test_head_region_missing_file_is_loud(tmp_path: Path) -> None:
    out = _text(recovery_head_lines(tmp_path / "nope.md"))
    assert out.startswith(f"  {LOUD} LOOKUP FAILED")
    assert "UNKNOWN, not absent" in out


def test_head_region_missing_marker_is_loud_not_a_silent_whole_file_dump(
    tmp_path: Path,
) -> None:
    """Without the marker the region cannot be delimited. Printing the whole
    file and calling it 'the head' would be a confident wrong answer."""
    path = tmp_path / "RECOVERY.md"
    path.write_text("# Recovery\n\nlots of content, no markers\n", encoding="utf-8")
    out = _text(recovery_head_lines(path))
    assert f"{LOUD} LOOKUP FAILED" in out
    assert PENDING_START in out
    assert "UNKNOWN, not absent" in out
    assert "lots of content" not in out


def test_head_region_empty_above_marker_is_a_real_absence(tmp_path: Path) -> None:
    path = tmp_path / "RECOVERY.md"
    path.write_text(f"{PENDING_START}\nb\n{PENDING_END}\n", encoding="utf-8")
    out = _text(recovery_head_lines(path))
    assert LOUD not in out
    assert "real absence" in out


@pytest.mark.skipif(
    not (REPO_ROOT / "resources" / "RECOVERY.md").exists(),
    reason="resources/RECOVERY.md not present in this checkout",
)
def test_head_region_is_substantial_against_the_real_recovery_file() -> None:
    """The day-one test for X1: the region above the markers must actually be
    read. No claim is pinned about WHICH region is newest — that changes every
    time sv runs, and asserting it here would be the same unverified-recency
    mistake this repair removed."""
    out = _text(recovery_head_lines(REPO_ROOT / "resources" / "RECOVERY.md"))
    assert LOUD not in out
    assert len(out.strip()) > 500
    assert "Newest date parsed in this region:" in out


def test_main_prints_the_head_region_before_the_marked_region(
    monkeypatch, capsys, tmp_path: Path,
) -> None:
    """Pinned on the OUTPUT: a head section computed and not printed is the
    failure mode this file already caught once (first_read_lines discarded)."""
    (tmp_path / "resources").mkdir()
    (tmp_path / "resources" / "RECOVERY.md").write_text(_SHAPED_RECOVERY, encoding="utf-8")
    out = _run_main(monkeypatch, capsys, tmp_path)
    assert "STATE BLOCKS ABOVE THE sv PENDING-WORK MARKERS" in out
    assert out.index("STATE BLOCKS ABOVE") < out.index("## PENDING WORK")
    assert "the newest thing in the file" in out
    assert "READ THIS FIRST" in out
    assert "Exp 42 was stopped" in out          # the marked region still prints
    assert "most recent" not in out


# ─────────────────────────────────────────────────────────────────────────────
# X2 — both gammas, labelled, with the gate input named
# ─────────────────────────────────────────────────────────────────────────────

def _exp_with_report(tmp_path: Path, payload: dict) -> dict:
    log_dir = tmp_path / "exp99_run"
    log_dir.mkdir()
    (log_dir / "exp99_run_report.json").write_text(_json.dumps(payload), encoding="utf-8")
    return {"log_dir": str(log_dir), "gamma": 0.1234}


def test_gamma_prints_both_series_and_names_the_gate_input(tmp_path: Path) -> None:
    """The script printed a bare 'Gamma: 0.7738' — the ALL-FINDINGS value —
    while the gate reads 0.8293. Project memory records this confusion once
    already ('0.240 = all-findings gamma, NOT the gate input')."""
    exp = _exp_with_report(tmp_path, {
        "gamma_history": [0.0, 0.7738],
        "gamma_critical_history": [0.0, 0.8293],
    })
    out = _text(gamma_lines(exp))
    assert "0.7738" in out and "0.8293" in out
    assert "gamma_history[-1]" in out
    assert "gamma_critical_history[-1]" in out
    assert "THE GATE INPUT" in out
    assert LOUD not in out


def test_gamma_says_the_gate_uses_the_critical_series(tmp_path: Path) -> None:
    exp = _exp_with_report(tmp_path, {
        "gamma_history": [0.1], "gamma_critical_history": [0.9],
    })
    out = _text(gamma_lines(exp))
    assert "CRITICAL series" in out
    assert "gamma_alt_threshold" in out
    assert "zero-new-critical" in out
    # gamma is load-bearing: the labels must not demote it to telemetry
    assert "ACTIVE convergence condition" in out


def test_gamma_missing_critical_history_is_loud_not_zero(tmp_path: Path) -> None:
    exp = _exp_with_report(tmp_path, {"gamma_history": [0.5]})
    out = _text(gamma_lines(exp))
    assert f"{LOUD} Gamma (critical, THE GATE INPUT)" in out
    assert "UNKNOWN, not zero" in out
    assert "0.5000" in out          # the value that IS available still prints


def test_gamma_non_numeric_series_is_loud(tmp_path: Path) -> None:
    exp = _exp_with_report(tmp_path, {
        "gamma_history": ["n/a"], "gamma_critical_history": [],
    })
    out = _text(gamma_lines(exp))
    assert out.count(LOUD) == 2
    assert "UNKNOWN, not zero" in out


def test_gamma_no_report_is_loud_and_does_not_relabel_the_carried_value(
    tmp_path: Path,
) -> None:
    out = _text(gamma_lines({"log_dir": str(tmp_path / "gone"), "gamma": 0.77}))
    assert f"{LOUD} LOOKUP FAILED" in out
    assert "UNKNOWN, not zero" in out
    assert "series is NOT identified here" in out


def test_gamma_unparseable_report_is_loud(tmp_path: Path) -> None:
    log_dir = tmp_path / "exp98_run"
    log_dir.mkdir()
    (log_dir / "exp98_run_report.json").write_text("{not json", encoding="utf-8")
    out = _text(gamma_lines({"log_dir": str(log_dir)}))
    assert f"{LOUD} LOOKUP FAILED" in out
    assert "Both gammas are UNKNOWN" in out


_REAL_EXP49 = (
    REPO_ROOT / "bench" / "logs"
    / "exp49_engineering_exam_live_20260729T062320Z"
    / "exp49_engineering_exam_live_report.json"
)


@pytest.mark.skipif(not _REAL_EXP49.exists(), reason="exp49 report not in this checkout")
def test_gamma_against_the_real_report_that_exposed_the_defect() -> None:
    """Values read from the report, not hardcoded, so the pin survives a
    re-archive: whatever the two series say, BOTH must reach the output."""
    data = _json.loads(_REAL_EXP49.read_text(encoding="utf-8"))
    out = _text(gamma_lines({"log_dir": str(_REAL_EXP49.parent)}))
    assert f"{data['gamma_history'][-1]:.4f}" in out
    assert f"{data['gamma_critical_history'][-1]:.4f}" in out
    assert data["gamma_history"][-1] != data["gamma_critical_history"][-1]


def test_main_no_longer_prints_a_bare_unlabelled_gamma(
    monkeypatch, capsys, tmp_path: Path,
) -> None:
    exp = dict(_FAKE_EXP, **_exp_with_report(tmp_path, {
        "gamma_history": [0.7738], "gamma_critical_history": [0.8293],
    }))
    out = _run_main(monkeypatch, capsys, tmp_path, exp=exp)
    assert "  Gamma: " not in out
    assert "THE GATE INPUT" in out
    assert "0.8293" in out


# ─────────────────────────────────────────────────────────────────────────────
# X3 — the experiment target is existence-checked
# ─────────────────────────────────────────────────────────────────────────────

def test_target_missing_gets_the_same_marker_as_key_files(tmp_path: Path) -> None:
    """The KEY FILES list has been existence-checked all along; the experiment
    target was printed unchecked, and the current one does not resolve."""
    out = _text(target_lines({"target": "/nope/exp49_engineering.md"}, tmp_path))
    assert out.startswith(f"  {LOUD} MISSING: Target:")
    assert "does not resolve on disk now" in out


def test_target_present_prints_plainly(tmp_path: Path) -> None:
    real = tmp_path / "target.md"
    real.write_text("x", encoding="utf-8")
    out = _text(target_lines({"target": str(real)}, tmp_path))
    assert out == f"  Target: {real}"
    assert LOUD not in out


def test_target_relative_path_resolves_against_the_repo_root(tmp_path: Path) -> None:
    (tmp_path / "bench").mkdir()
    (tmp_path / "bench" / "evidence.py").write_text("x", encoding="utf-8")
    out = _text(target_lines({"target": "bench/evidence.py"}, tmp_path))
    assert LOUD not in out
    out_bad = _text(target_lines({"target": "bench/gone.py"}, tmp_path))
    assert f"{LOUD} MISSING" in out_bad
    assert "(checked: " in out_bad          # names the path it actually tested


def test_target_absent_from_report_is_unknown_not_blank(tmp_path: Path) -> None:
    out = _text(target_lines({"target": ""}, tmp_path))
    assert LOUD in out
    assert "UNKNOWN, not absent" in out


_FAKE_EXP = {
    "name": "exp99_fake", "number": 99, "status": "CONVERGED", "topology": "star",
    "target": "/definitely/not/here.md", "total_rounds": 7, "total_findings": 40,
    "models": ["CC2"], "per_model": {"CC2": 6}, "log_dir": "/nonexistent",
    "skipped_higher": [],
}


def test_main_flags_a_missing_target_at_the_call_site(
    monkeypatch, capsys, tmp_path: Path,
) -> None:
    out = _run_main(monkeypatch, capsys, tmp_path, exp=dict(_FAKE_EXP))
    section = out.split("## LATEST EXPERIMENT", 1)[1]
    assert f"{LOUD} MISSING: Target: /definitely/not/here.md" in section


# ─────────────────────────────────────────────────────────────────────────────
# X4 — is an experiment running? three states, never conflated
# ─────────────────────────────────────────────────────────────────────────────

_PS_IDLE = "  501 00:03 /usr/sbin/notifyd\n  777 12:00 /bin/zsh\n"
_PS_RUNNING = _PS_IDLE + (
    " 4242 01-02:03:04 python3 bench/launch_exp42.py --config bench/configs/exp54.toml\n"
)


def test_running_check_nothing_running_is_a_completed_check(tmp_path: Path) -> None:
    out = _text(running_experiment_lines(pid_dir=tmp_path, ps_reader=lambda: _PS_IDLE))
    assert LOUD not in out
    assert ">>" not in out
    assert "nothing running" in out
    assert "completed check, not a failed one" in out
    # a bare "nothing" is not evidence; it must say what it scanned
    assert "2 process(es) scanned" in out
    assert "0 pidfile(s)" in out


def test_running_check_names_a_live_runner_with_pid_and_elapsed(tmp_path: Path) -> None:
    out = _text(running_experiment_lines(pid_dir=tmp_path, ps_reader=lambda: _PS_RUNNING))
    assert ">> RUNNING: PID 4242, elapsed 01-02:03:04" in out
    assert "launch_exp42.py" in out
    assert "nothing running" not in out
    assert "Do NOT launch another runner" in out


def test_running_check_finds_a_live_pidfile_whose_process_does_not_match(
    tmp_path: Path,
) -> None:
    """A pidfile is evidence in its own right: the standing detached-launch
    rule writes one beside every log."""
    (tmp_path / "exp54_launch.pid").write_text("777\n", encoding="utf-8")
    out = _text(running_experiment_lines(pid_dir=tmp_path, ps_reader=lambda: _PS_IDLE))
    assert ">> RUNNING (from pidfile" in out
    assert "PID 777" in out
    assert "nothing running" not in out


def test_running_check_matches_both_pidfile_globs(tmp_path: Path) -> None:
    (tmp_path / "exp54.pid").write_text("777", encoding="utf-8")
    (tmp_path / "exp54_launch_2.pid").write_text("777", encoding="utf-8")
    out = _text(running_experiment_lines(pid_dir=tmp_path, ps_reader=lambda: _PS_IDLE))
    assert "2 pidfile(s)" in out


def test_running_check_stale_pidfile_is_reported_and_is_not_running(
    tmp_path: Path,
) -> None:
    (tmp_path / "exp54_launch.pid").write_text("999999", encoding="utf-8")
    out = _text(running_experiment_lines(pid_dir=tmp_path, ps_reader=lambda: _PS_IDLE))
    assert "stale pidfile" in out
    assert "nothing running" in out
    assert LOUD not in out          # a stale file is a finding, not a failure
    assert "(1 stale)" in out


def test_running_check_ps_failure_is_unknown_not_nothing(tmp_path: Path) -> None:
    """THE X4 defect class: a check that could not run must never render as
    'nothing is running'. That is how a duplicate launch happens."""
    def boom() -> str:
        raise OSError("ps exited 1: permission denied")

    out = _text(running_experiment_lines(pid_dir=tmp_path, ps_reader=boom))
    assert f"{LOUD} CHECK INCOMPLETE" in out
    assert "UNKNOWN" in out
    assert "nothing running" not in out
    assert "ps -Ao pid,etime,args" in out       # tells the reader how to check


def test_running_check_empty_ps_output_is_a_parse_failure(tmp_path: Path) -> None:
    """`ps` lists at least itself. An empty table is a broken probe, and a
    broken probe that returns 'nothing' is the whole defect class."""
    out = _text(running_experiment_lines(pid_dir=tmp_path, ps_reader=lambda: ""))
    assert f"{LOUD} CHECK INCOMPLETE" in out
    assert "not an empty machine" in out
    assert "nothing running" not in out


def test_running_check_unreadable_pidfile_is_unknown_not_nothing(
    tmp_path: Path,
) -> None:
    (tmp_path / "exp54_launch.pid").write_text("not-a-pid", encoding="utf-8")
    out = _text(running_experiment_lines(pid_dir=tmp_path, ps_reader=lambda: _PS_IDLE))
    assert f"{LOUD} CHECK INCOMPLETE" in out
    assert "holds no readable PID" in out
    assert "nothing running" not in out


def test_running_check_missing_pid_dir_is_a_failure_not_an_absence(
    tmp_path: Path,
) -> None:
    out = _text(running_experiment_lines(
        pid_dir=tmp_path / "gone", ps_reader=lambda: _PS_IDLE))
    assert f"{LOUD} CHECK INCOMPLETE" in out
    assert "pidfile scan could not run" in out
    assert "nothing running" not in out


def test_running_check_still_reports_a_live_run_when_the_other_probe_failed(
    tmp_path: Path,
) -> None:
    """Partial failure must not suppress a positive finding, and a positive
    finding must not suppress the incompleteness."""
    (tmp_path / "exp54_launch.pid").write_text("junk", encoding="utf-8")
    out = _text(running_experiment_lines(pid_dir=tmp_path, ps_reader=lambda: _PS_RUNNING))
    assert ">> RUNNING: PID 4242" in out
    assert f"{LOUD} CHECK INCOMPLETE" in out


def test_running_check_does_not_report_this_very_process(tmp_path: Path) -> None:
    """The scan excludes its own PID by identity, not by guessing at argv."""
    me = _os.getpid()
    ps = f"{me} 00:01 python3 scripts/cdsfl_recover.py --launch_exp\n" + _PS_IDLE
    out = _text(running_experiment_lines(pid_dir=tmp_path, ps_reader=lambda: ps))
    assert f"PID {me}" not in out
    assert "nothing running" in out


def test_running_check_real_ps_runs_and_answers_one_of_the_three_states(
    tmp_path: Path,
) -> None:
    """Integration: the default reader must actually work on this machine.
    `ps` opens no socket and is not in the netguard's binary list."""
    out = _text(running_experiment_lines(pid_dir=tmp_path))
    assert ("nothing running" in out) or (">> RUNNING" in out) \
        or (f"{LOUD} CHECK INCOMPLETE" in out)
    assert "process(es) scanned" in out or f"{LOUD} CHECK INCOMPLETE" in out


def test_main_prints_the_running_section_early(
    monkeypatch, capsys, tmp_path: Path,
) -> None:
    """A duplicate launch against a live checkpoint is the expensive mistake,
    so the section must be printed, and printed before the long dumps."""
    out = _run_main(monkeypatch, capsys, tmp_path)
    assert "## RUNNING NOW" in out
    assert out.index("## FIRST READ") < out.index("## RUNNING NOW")
    assert out.index("## RUNNING NOW") < out.index("## SAVED SNAPSHOT")


def test_running_check_claims_a_match_not_a_proven_runner(tmp_path: Path) -> None:
    """Found by running the real check: the pattern also matches a shell
    tailing an experiment log or an editor with detached_launch.sh open. The
    bias toward over-reporting is deliberate — a false positive costs one
    glance, a false negative costs a duplicate launch — but the output may
    only claim what it tested, which is a command-line match."""
    out = _text(running_experiment_lines(pid_dir=tmp_path, ps_reader=lambda: _PS_RUNNING))
    assert "MATCHES the runner pattern" in out
    assert "monitoring shell or editor" in out
    # and the evidence for the claim is printed, not summarised away
    assert "bench/launch_exp42.py --config bench/configs/exp54.toml" in out


# ─────────────────────────────────────────────────────────────────────────────
# FINAL-GATE REPAIR — the uncommitted-file listing named its own remainder
#
# Found by the final integration gate, not by review: with 26 entries in
# `git status --short`, the report printed 20 and said nothing about the
# other 6 — three of which were new test files and one the audit note. A
# reader would have concluded the tree held only what was shown. This is the
# same silent-truncation fault the report already guards against in its
# RECOVERY.md [CAP: ...] blocks and that OpenBrain's _print_overflow closes;
# the git block was the one listing that still had it.
#
# OFFLINE: uses the _run_main harness above — git_state is replaced, so no
# subprocess and no socket.
# ─────────────────────────────────────────────────────────────────────────────


def _gs_with(n_files: int) -> dict:
    gs = dict(_GIT_OK)
    gs["uncommitted"] = [f"M file_{i:03d}.py" for i in range(n_files)]
    return gs


def test_a_truncated_uncommitted_listing_names_the_remainder(
    monkeypatch, capsys, tmp_path: Path,
) -> None:
    out = _run_main(monkeypatch, capsys, tmp_path, gs=_gs_with(26))
    assert "Uncommitted (26 file(s)):" in out
    assert "... and 6 more not shown" in out
    # the total is stated, so the listing can never disagree with its own count
    assert "file_000.py" in out and "file_019.py" in out


def test_a_complete_uncommitted_listing_claims_no_remainder(
    monkeypatch, capsys, tmp_path: Path,
) -> None:
    """The notice must appear only when something was actually withheld —
    an overflow line on a complete listing would be its own false report."""
    out = _run_main(monkeypatch, capsys, tmp_path, gs=_gs_with(20))
    assert "Uncommitted (20 file(s)):" in out
    assert "more not shown" not in out
    assert "file_019.py" in out


def test_the_stated_count_is_the_real_number_of_uncommitted_files(
    monkeypatch, capsys, tmp_path: Path,
) -> None:
    """Pins the count to len(uncommitted), not to the number of lines printed
    — the two diverging silently is the whole defect."""
    for n in (1, 19, 20, 21, 60):
        out = _run_main(monkeypatch, capsys, tmp_path, gs=_gs_with(n))
        assert f"Uncommitted ({n} file(s)):" in out
        shown = sum(1 for ln in out.splitlines()
                    if ln.startswith("    M file_"))
        assert shown == min(n, 20)
        if n > 20:
            assert f"... and {n - 20} more not shown" in out
