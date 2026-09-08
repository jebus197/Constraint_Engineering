"""The exam arc's containment gates must traverse the WHOLE tree, not its top level.

WHAT THESE GATES ARE FOR. `bench/arc_sequencer.sh` launches the withheld-exam legs
(Exp 48-53). Each leg must be able to see exactly one document: if a leg can read a
sibling paper, the exam is no longer blind and the arc's results are worthless. Two
checks enforce that, and until 2026-09-08 both counted only the top level:

    check_staging()   N=$(find "$PCWD" -maxdepth 1 -type f | wc -l)
    run_leg()      SIBS=$(find ~/CDSFL_review_targets -mindepth 1 -maxdepth 1 -type d | wc -l)

The first could not see a second document one directory down. The second did not
count a sibling staged as a FILE rather than a directory. Both are the shape that
produced 5 defects in `vault_keys.sh` the night before: a bounded traversal standing
in for a complete one.

WHY THIS FILE EXECUTES RATHER THAN READS. `execute-do-not-grep`: a test asserting on
the source text of a shell script proves only that the script describes itself
consistently. So this EXTRACTS each `find` invocation from the live script and RUNS
it against fixtures built to defeat the bounded form. Revert either gate and the
corresponding test goes red, because the extracted command is the one that runs.
"""
import pathlib
import re
import subprocess

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = REPO / "bench" / "arc_sequencer.sh"


def _extract(assign: str) -> str:
    """Pull one `VAR=$(find ...)` command out of the script as executable text."""
    src = SCRIPT.read_text()
    m = re.search(rf"^\s*{assign}=\$\((find .*?)\)\s*$", src, re.MULTILINE)
    assert m, f"no `{assign}=$(find ...)` line in {SCRIPT}; the gate was renamed or removed"
    return m.group(1)


def _count(cmd: str, target: str) -> int:
    """Run the real command with its directory replaced by the fixture."""
    cmd = re.sub(r'(find\s+)("\$PCWD"|~/CDSFL_review_targets)', rf'\1"{target}"', cmd, count=1)
    r = subprocess.run(["bash", "-c", cmd], capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr
    return int(r.stdout.strip())


def test_panel_cwd_gate_sees_a_document_hidden_one_level_down(tmp_path):
    """A second document in a subdirectory must be counted, and so must halt the leg."""
    pcwd = tmp_path / "current"
    pcwd.mkdir()
    (pcwd / "SW-21-REF-04.md").write_text("the paper this leg is meant to sit")
    assert _count(_extract("N"), str(pcwd)) == 1, "the legitimate single-document layout must count 1"

    (pcwd / "notes").mkdir()
    (pcwd / "notes" / "SW-22-REF-05.md").write_text("a second paper the leg must never see")
    n = _count(_extract("N"), str(pcwd))
    assert n == 2, (
        f"the gate counted {n}; a bounded `-maxdepth 1` traversal counts 1 here and lets "
        "the leg launch with two documents reachable"
    )


def test_sibling_gate_counts_a_document_staged_as_a_file(tmp_path):
    """A stray file beside `current/` must count; `-type d` skipped it entirely."""
    stage = tmp_path / "CDSFL_review_targets"
    (stage / "current").mkdir(parents=True)
    (stage / "current" / "SW-21-REF-04.md").write_text("the staged paper")
    assert _count(_extract("SIBS"), str(stage)) == 1, "one staged document must count 1"

    (stage / "SW-22-REF-05.md").write_text("a sibling paper staged as a bare file")
    n = _count(_extract("SIBS"), str(stage))
    assert n == 2, (
        f"the gate counted {n}; with `-type d` a sibling staged as a FILE is invisible "
        "and the leg launches believing one document is staged"
    )


@pytest.mark.parametrize("assign,forbidden", [("N", "-maxdepth 1"), ("SIBS", "-type d")])
def test_the_bounded_forms_do_not_come_back(assign, forbidden):
    """A ratchet. Restoring either bound silently re-opens the evasion above."""
    cmd = _extract(assign)
    assert forbidden not in cmd, (
        f"`{forbidden}` is back in the {assign} gate: {cmd!r}. That bound is what made "
        "the check unable to see the thing it exists to detect."
    )
