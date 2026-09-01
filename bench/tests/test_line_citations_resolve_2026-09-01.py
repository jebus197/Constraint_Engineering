"""Typed `file.py:NNNN` citations must at least name a real file and a real line.

The QC reference checker deliberately does not check line numbers.
`scripts/cdsfl_utils.py` declares:

    SUPPRESS_LINE = "path:line or path:line-range -- the FILE exists; line
                     numbers NOT checked"

and `_suffix_label` routes every `path:line` citation to it. So every stale line
number in every tracked document is exempt from checking by construction. CC2
identified that as the systemic enabler behind the EXPERIMENT_RUN_LEDGER defect
of 2026-09-01, where a document headed "DERIVED, never typed" cited line 11002 of the file then
called reference_runner_v2.py, for a comment sitting 1,068 lines further down.
(Written out of path:line form on purpose: this file is tracked, so the record of
the defect would otherwise trip the check for the defect -- which is exactly what
happened the first time it was committed.)

THIS TEST DOES NOT CLOSE THAT CLASS, and saying so is the point. 11002 sits
comfortably inside a 12,128-line file, so a wrong-but-in-range citation passes
here exactly as it passed the QC checker. Only anchoring -- matching the
citation to the text it refers to and deriving the number, as
`scripts/experiment_run_ledger.py` now does -- can catch that.

What this does catch is the subset that IS mechanically decidable: a citation
naming a file that does not exist, or a line beyond the end of the file it
names. Measured at the time of writing: 974 non-placeholder citations, zero of
each. This test keeps that at zero.
"""

import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]

CITATION = re.compile(r"([A-Za-z0-9_/]+\.py):(\d{2,5})\b")

# Illustrative names used in prose and test fixtures. They are not citations.
PLACEHOLDER = re.compile(
    r"\b(foo|bar|baz|gone|example|module|file|some_file|path|real|x|toy_target"
    r"|engine|composer|test)\.py$")

# Historical notes name files as they were called when the note was written.
# `experimental_notes/` is frozen by policy; the live tracker and plans in it
# were migrated on 2026-09-01 and are NOT exempt.
FROZEN_PREFIX = "experimental_notes/"
LIVE_IN_NOTES = {
    "experimental_notes/RUNWAY_to_BR2_2026-08-18.md",
    "experimental_notes/CDSFL_Agent_Operational_Plan.md",
    "experimental_notes/Exp40_to_54_Execution_Plan_2026-04-17.md",
    "experimental_notes/EXPERIMENT_RUN_LEDGER.md",
}

SEARCH_BASES = ("", "bench/", "scripts/", "bench/tools/")


def _tracked_text_files():
    out = subprocess.run(["git", "ls-files", "*.md", "*.py", "*.sh"],
                         cwd=str(REPO), capture_output=True, text=True,
                         timeout=180)
    assert out.returncode == 0, out.stderr
    return [f for f in out.stdout.split()
            if not f.startswith(("bench/logs/", "bench/results/"))]


def _is_live(path: str) -> bool:
    return not path.startswith(FROZEN_PREFIX) or path in LIVE_IN_NOTES


_BY_BASENAME = None


def _resolve(target: str):
    """Resolve a citation's path, then fall back to a unique basename match.

    Documents cite bare filenames -- `_feedback.py:228` for
    `bench/dm/_feedback.py`. A resolver that only tries a fixed list of prefixes
    reports those as missing files, which is a false positive in the direction
    that gets a test switched off. The basename fallback is used ONLY when the
    name is unambiguous across the tree.
    """
    global _BY_BASENAME
    for base in SEARCH_BASES:
        p = REPO / (base + target)
        if p.is_file():
            return p
    if _BY_BASENAME is None:
        out = subprocess.run(["git", "ls-files", "*.py"], cwd=str(REPO),
                             capture_output=True, text=True, timeout=180)
        seen = {}
        for f in out.stdout.split():
            seen.setdefault(Path(f).name, []).append(f)
        _BY_BASENAME = {k: v[0] for k, v in seen.items() if len(v) == 1}
    hit = _BY_BASENAME.get(Path(target).name)
    return (REPO / hit) if hit else None


def _citations():
    """(citing file, target, line) for every live, non-placeholder citation."""
    out = []
    for f in _tracked_text_files():
        if not _is_live(f):
            continue
        try:
            txt = (REPO / f).read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for m in CITATION.finditer(txt):
            target, line = m.group(1), int(m.group(2))
            if PLACEHOLDER.search(target):
                continue
            out.append((f, target, line))
    return out


@pytest.fixture(scope="module")
def citations():
    found = _citations()
    assert found, "no line citations found at all -- the pattern has broken"
    return found


class TestEveryCitationNamesSomethingReal:
    def test_no_live_citation_names_a_missing_file(self, citations):
        missing = [(f, t, l) for f, t, l in citations if _resolve(t) is None]
        assert not missing, (
            "line citations in live files naming a file that does not exist:\n  "
            + "\n  ".join(f"{f} -> {t}:{l}" for f, t, l in missing[:20])
            + "\nIf the file was renamed, update the citation. If the name is "
              "illustrative, add it to PLACEHOLDER.")

    def test_no_live_citation_points_past_the_end_of_its_file(self, citations):
        lengths = {}
        past = []
        for f, t, line in citations:
            p = _resolve(t)
            if p is None:
                continue
            if p not in lengths:
                lengths[p] = sum(1 for _ in p.open(encoding="utf-8",
                                                   errors="ignore"))
            if line > lengths[p]:
                past.append((f, t, line, lengths[p]))
        assert not past, (
            "line citations pointing beyond the end of the file they name:\n  "
            + "\n  ".join(f"{f} -> {t}:{l} (file has {n} lines)"
                          for f, t, l, n in past[:20]))


class TestTheLimitIsStated:
    """A test that overstates what it checks is worse than no test."""

    def test_an_in_range_but_wrong_citation_is_NOT_caught(self):
        """Pins the limitation, so nobody mistakes this for the full class.

        The ledger cited line 11002 of a file with 12,128 lines. Both checks
        above pass on that citation. Only anchoring catches it, which is what
        scripts/experiment_run_ledger.py does.
        """
        runner = REPO / "bench" / "reference_runner_v3.py"
        n = sum(1 for _ in runner.open(encoding="utf-8", errors="ignore"))
        assert n > 11002, (
            "the runner is now shorter than the historical bad citation, which "
            "would make this limitation invisible -- pick another example")

    def test_the_generator_anchors_rather_than_types(self):
        src = (REPO / "scripts" / "experiment_run_ledger.py").read_text(
            encoding="utf-8")
        assert "_gamma_alt_comment_line" in src and "_GAMMA_ALT_ANCHOR" in src


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
