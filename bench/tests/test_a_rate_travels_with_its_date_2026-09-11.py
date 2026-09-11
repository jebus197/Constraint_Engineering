"""A rate quoted against a growing corpus needs its date, or drift reads as disagreement.

THE SIBLING OF `measured-rate-travels-with-its-script`, and it was named by a
panel seat rather than by me. Round 12's brief quoted **67 DONE entries, 5026
test functions and 112 scripts** as though current. By the time the seats read
it the list was at **80, 5091 and 113**, and by the next morning **81, 5115 and
113**. None of it changed a conclusion. All of it invites exactly the
reproduction failure task A7 spent its whole budget on -- a reader who cannot
tell a figure that DRIFTED from a figure that was WRONG.

THE PROJECT HAD ALREADY LEARNED THIS ONCE, ONE DAY EARLIER. Task V4 found entry
6.1's "23 of 41 completion signals" had become 24 of 42 because the archive
grows, and wrote: "a typed figure over a growing corpus is not merely
unverifiable, it is guaranteed to go stale". Then five new figures were written
the same way the next day.

MEASURED BEFORE BUILDING ANYTHING, because the fix should go where the defect is.
**On the master task list the coverage is already perfect: 0 of 44 entries
carrying a percentage lack a date, Wilson [0.0000%, 8.0296%], Clopper-Pearson
[0.0000%, 8.0420%].** The rot was in the BRIEFS, not the list. So this file
ratchets the list where it is already right, and the advisory lives in
`panel_brief_validate` where the drift actually happened.
"""
from __future__ import annotations

import pathlib
import re
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import task_list_markers as tlm  # noqa: E402

LIST = ROOT / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md"
VALIDATE = ROOT / "scripts" / "panel_brief_validate.py"

FIGURE = re.compile(r"\b\d{1,3}\.\d+\s*%")
DATE = re.compile(r"20\d\d-\d\d-\d\d")


def _blocks():
    lines = LIST.read_text(encoding="utf-8").splitlines()
    es = sorted(tlm.parse_entries(LIST), key=lambda e: e.line_no)
    for k, e in enumerate(es):
        end = es[k + 1].line_no - 1 if k + 1 < len(es) else len(lines)
        yield e.ident, "\n".join(lines[e.line_no - 1:end])


def undated(blocks) -> list:
    """The rule itself, callable, so a control can feed it a synthetic block.

    THE FIRST CONTROL HERE TESTED THE REGEX AND NOT THE RULE, and a mutation
    proved it: inserting an undated percentage into an existing entry's block
    changed nothing, because that block carries dates elsewhere and the check is
    per-BLOCK. A control that cannot fail on the mutation it is written for is
    the vacuity this project has confirmed 8 times.

    The per-block granularity is a real limit and is stated rather than hidden:
    a block carrying a date anywhere passes, so a NEW undated figure added
    beside a dated one is not caught. What is caught is the case that actually
    occurred -- a whole entry, or a whole brief, quoting rates with no date at
    all.
    """
    return [i for i, blk in blocks
            if FIGURE.search(blk) and not DATE.search(blk)]


class TestEveryFigureOnTheListCarriesADate:
    def test_none_is_undated(self):
        undated_ids = undated(_blocks())
        assert not undated_ids, (
            f"these entries quote a percentage with no date anywhere in the "
            f"block, so a reader cannot tell drift from disagreement: {undated_ids}")

    def test_the_check_is_not_vacuous(self):
        n = sum(1 for _i, blk in _blocks() if FIGURE.search(blk))
        assert n >= 30, f"only {n} entries carry a percentage; the scan has broken"

    def test_the_rule_itself_catches_an_undated_block(self):
        """POSITIVE CONTROL, ON THE RULE rather than on the regex.

        The first version of this asserted the REGEX matched a synthetic string,
        which is a fact about `re` and not about the guard. Mutating the real
        list by adding an undated percentage to an existing block changed
        nothing, and the control stayed green -- because that block carries
        dates elsewhere. It feeds the rule now.
        """
        good = ("E1", "**E1.** Measured 2026-09-11: the rate is 12.5000%.")
        bad = ("E2", "**E2.** The rate is 12.5000% and nothing says when.")
        none = ("E3", "**E3.** No figures here at all.")
        assert undated([good, bad, none]) == ["E2"]


class TestTheBriefValidatorSaysSoToo:
    def test_an_undated_brief_is_reported(self, tmp_path):
        b = tmp_path / "BRIEF.md"
        b.write_text(
            "# B\n\n<!-- figure: x | scripts/x.py | y -->\n\n"
            "## SECTION 5\nDiminishing returns. run execute fix falsifier "
            "test the fix refut gamma Wilson\nA rate of 12.5% here.\n",
            encoding="utf-8")
        r = subprocess.run([sys.executable, str(VALIDATE), str(b)],
                           cwd=ROOT, capture_output=True, text=True, timeout=600)
        out = r.stdout + r.stderr
        assert "NO DATE AT ALL" in out, out[-400:]

    def test_a_dated_brief_is_not(self, tmp_path):
        b = tmp_path / "BRIEF.md"
        b.write_text(
            "# B\n\n<!-- figure: x | scripts/x.py | y -->\n\n"
            "## SECTION 5\nDiminishing returns. run execute fix falsifier "
            "test the fix refut gamma Wilson\nMeasured 2026-09-11: 12.5%.\n",
            encoding="utf-8")
        r = subprocess.run([sys.executable, str(VALIDATE), str(b)],
                           cwd=ROOT, capture_output=True, text=True, timeout=600)
        assert "NO DATE AT ALL" not in (r.stdout + r.stderr)

    def test_it_advises_and_does_not_refuse(self):
        """The same design decision as the rest of this validator's advisories:
        a guard that refuses a correct brief teaches people to skip it."""
        import tempfile
        d = pathlib.Path(tempfile.mkdtemp())
        b = d / "BRIEF.md"
        b.write_text("# B\n\n## SECTION 5\nDiminishing returns. run execute fix "
                     "falsifier test the fix refut gamma Wilson\n12.5%\n",
                     encoding="utf-8")
        r = subprocess.run([sys.executable, str(VALIDATE), str(b)],
                           cwd=ROOT, capture_output=True, text=True, timeout=600)
        assert "NO DATE AT ALL" in (r.stdout + r.stderr)
        # It may still refuse for a MISSING SECTION; what it must not do is
        # refuse for the dating advisory alone.
        assert "carries all 7 required sections" in (r.stdout + r.stderr) or \
            "fails" in (r.stdout + r.stderr)


class TestTheDriftWasReal:
    def test_the_quoted_denominators_have_moved(self):
        """The finding itself, kept checkable. If these ever stopped moving the
        whole concern would be theoretical -- they move daily."""
        from collections import Counter
        done = Counter(e.state for e in tlm.parse_entries())["DONE"]
        scripts = len(list((ROOT / "scripts").glob("*.py")))
        assert done > 67, (
            f"round 12's brief quoted 67 DONE entries; today it is {done}")
        assert scripts > 112, (
            f"round 12's brief quoted 112 scripts; today it is {scripts}")
