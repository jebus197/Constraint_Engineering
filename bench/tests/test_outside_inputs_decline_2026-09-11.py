"""A script whose input lives OUTSIDE the repository must decline, not traceback.

WHY THIS IS AN A2 PROPERTY. A clone has the repository and nothing else. Three
scripts read a workflow transcript from the agent session directory --
`~/.claude/projects/.../journal.jsonl` -- which is outside the tree, is specific
to one machine and one session, and is absent everywhere else. Measured
2026-09-11 by pointing all 3 at an absent path:

    founder_decision_ledger.py         exit 1   FileNotFoundError traceback
    salvage_task_reconstruction.py     exit 2   "no journal at ..."
    triage_open_founder_decisions.py   exit 2   "no journal at ..."

2 of the 3 already declined by name. The 3rd raised a bare FileNotFoundError,
which reads as a BROKEN SCRIPT rather than as a missing input -- and the
difference matters to a reader deciding whether the repository is sound.

THE PATHS ARE NOT A DEFECT AND ARE DELIBERATELY NOT REWRITTEN. A workflow
transcript genuinely lives outside the repository; there is nowhere inside it
for the constant to point. Two other scripts DID hardcode the maintainer's
checkout as their repository root, which is a different thing entirely, and
those were changed to `Path(__file__).resolve().parents[1]` the same day.

WHAT IS ASSERTED. Non-zero exit, because a missing input is not success. And no
traceback, because a traceback is a report about the program rather than about
the input.
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]

#: (script, the absolute prefix it reads from outside the repository)
OUTSIDE_INPUTS = (
    ("scripts/founder_decision_ledger.py",
     "/Users/georgejackson/.claude/projects/-Users-georgejackson-Developer-Projects"),
    ("scripts/salvage_task_reconstruction.py",
     "/Users/georgejackson/.claude/projects/-Users-georgejackson-Developer-Projects"),
    ("scripts/triage_open_founder_decisions.py",
     "/Users/georgejackson/.claude/projects/-Users-georgejackson-Developer-Projects"),
    # FOUND BY A PANEL SEAT, and it was worse than the 3 above. This one builds
    # its path as `Path.home() / ".claude/projects/-Users-georgejackson-..."`,
    # so the machine-specific part is a DIRECTORY NAME rather than a leading
    # absolute path -- and the scan that found the first 3 required the literal
    # `"/Users/georgejackson`, so it reported a false zero for this form. The
    # 11th instance this session of a scanner resolving 1 form of a thing.
    #
    # With the transcript absent it did not traceback: it printed
    # "Sources written BEFORE at least 1 later founder message: 0 of 5 = 0.0%"
    # with a Wilson interval and its conclusion, and exited 0. An authoritative
    # no-staleness result manufactured from no data, which is worse than a
    # crash because it reads as a measurement.
    ("scripts/decision_label_staleness_2026-09-09.py",
     "-Users-georgejackson-Developer-Projects"),
)


def _run_with_absent_input(rel: str, prefix: str) -> subprocess.CompletedProcess:
    """Run a copy of the script whose outside input cannot exist.

    A COPY rather than an environment override, because the path is a module
    constant and these scripts offer no flag for it. The copy lives in
    `scripts/` so its own `sys.path[0]` imports still resolve.
    """
    src = (REPO / rel).read_text(encoding="utf-8")
    assert prefix in src, (
        f"{rel} no longer names {prefix}; if the input moved inside the "
        f"repository, delete this row rather than editing the prefix")
    patched = src.replace(prefix, "/cdsfl-nonexistent-outside-input")
    fh = tempfile.NamedTemporaryFile("w", suffix=".py", dir=REPO / "scripts",
                                     delete=False, encoding="utf-8")
    fh.write(patched)
    fh.close()
    try:
        return subprocess.run([sys.executable, fh.name], cwd=REPO,
                              capture_output=True, text=True, timeout=600)
    finally:
        os.unlink(fh.name)


@pytest.mark.parametrize("rel,prefix", OUTSIDE_INPUTS,
                         ids=[r.split("/")[-1] for r, _ in OUTSIDE_INPUTS])
class TestItDeclinesByName:
    def test_it_exits_non_zero(self, rel, prefix):
        r = _run_with_absent_input(rel, prefix)
        assert r.returncode != 0, (
            f"{rel} reported success with its input absent; a missing input "
            f"that reads as a clean run is how an empty result becomes a "
            f"finding")

    def test_it_does_not_traceback(self, rel, prefix):
        r = _run_with_absent_input(rel, prefix)
        assert "Traceback (most recent call last)" not in r.stderr, (
            f"{rel} raised rather than declining:\n{r.stderr[-600:]}")

    def test_it_names_what_is_missing(self, rel, prefix):
        r = _run_with_absent_input(rel, prefix)
        blob = (r.stdout or "") + (r.stderr or "")
        assert "/cdsfl-nonexistent-outside-input" in blob, (
            f"{rel} declined without saying WHICH path it wanted, so a reader "
            f"cannot tell whether to supply it or ignore the script")


class TestTheProbeItselfWorks:
    """ANTI-VACUITY. If the substitution silently did nothing, all 9 cases above
    would be running the REAL script against the REAL journal and passing or
    failing for reasons unconnected to the property."""

    def test_the_prefix_substitution_changes_the_source(self):
        """The SAME substitution the runner performs, not a lookalike.

        The first version asserted `prefix.replace("/Users", "/cdsfl") not in
        src`, which assumed every prefix is a leading absolute path. The 4th row
        builds its path as `Path.home() / ".claude/projects/-Users-george..."`,
        so its prefix is a DIRECTORY NAME with no "/Users" in it at all, and the
        assertion compared the prefix with itself and failed. Comparing against
        the real substitution cannot drift from the runner."""
        sentinel = "/cdsfl-nonexistent-outside-input"
        for rel, prefix in OUTSIDE_INPUTS:
            src = (REPO / rel).read_text(encoding="utf-8")
            assert src.count(prefix) >= 1, rel
            patched = src.replace(prefix, sentinel)
            assert patched != src, (
                f"substituting {prefix!r} in {rel} changed nothing, so every "
                f"case for it runs the REAL script against the REAL input")
            assert sentinel in patched

    def test_the_unpatched_script_behaves_differently(self):
        """The real journal exists on this machine, so the unpatched script must
        NOT print the decline message. If it does, the probe proves nothing."""
        rel = "scripts/founder_decision_ledger.py"
        journal = Path(
            "/Users/georgejackson/.claude/projects"
            "/-Users-georgejackson-Developer-Projects"
            "/a07b3790-0a2a-4978-aedb-bd842c0493d3/subagents/workflows"
            "/wf_a33f50d2-519/journal.jsonl")
        if not journal.is_file():
            pytest.skip("the workflow transcript is absent on this machine, "
                        "which is exactly the condition the rows above model")
        r = subprocess.run([sys.executable, str(REPO / rel)], cwd=REPO,
                           capture_output=True, text=True, timeout=600)
        assert r.returncode == 0, r.stderr[-500:]
        assert "no journal at" not in r.stderr
