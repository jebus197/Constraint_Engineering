#!/usr/bin/env python3
"""The morning report's markdown companion is GENERATED, and the generator is
reachable from a fresh clone.

WHY THIS FILE EXISTS, AND IT CLOSES A GAP I CREATED THE SAME NIGHT. On
2026-10-30 a note-lint finding in `experimental_notes/Morning_Report_2026-10-30.md`
was fixed BY HAND and the next rebuild put it straight back, because the file is
generated from `scripts/rebuild_morning_report_markdown_2026-10-30.py`. The
generator was committed so the fix would survive -- and committed with **0 test
files naming it**, measured by `grep -rl` over `bench/tests/`. That is the
addition-nothing-reaches half of the additive standard, the shape this project
has confirmed 11 times, committed about an hour after a memory about producers
was extended to cover exactly it.

THE SECOND DEFECT WAS WORSE AND LESS VISIBLE. The generator's source was
`~/Desktop/CDSFL_tts/Morning_Report_2026-10-30.txt`, an UNVERSIONED file on one
machine's Desktop. A generated artefact whose source is not in the repository
cannot be rebuilt from a clone, which is entry A2's whole subject, and an
unversioned file on one Desktop is the single point of failure this project
already named when it made the repo copy of the task list canonical. The source
is now the repo copy, with the Desktop copy a fallback that is then brought back
into agreement. Both were byte-identical at 37,058 bytes when this changed.

WHAT THIS PINS. That the committed markdown MATCHES a rebuild, so a hand edit to
it fails here rather than being silently reverted later; that the generator reads
a VERSIONED source; that `--check` writes nothing, so a guard cannot mutate the
tree; and that a deliberate corruption is DETECTED, which is the control that
makes the match assertion worth anything.
"""
from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

GENERATOR = (REPO / "scripts"
             / "rebuild_morning_report_markdown_2026-10-30.py")
DST = REPO / "experimental_notes" / "Morning_Report_2026-10-30.md"


def _gen():
    assert GENERATOR.is_file(), f"generator absent: {GENERATOR}"
    spec = importlib.util.spec_from_file_location("mr_md_rebuild", GENERATOR)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def gen():
    return _gen()


class TestItIsReproducibleFromTheRepository:
    def test_the_source_is_versioned(self, gen):
        """A generated file whose source is not tracked cannot be rebuilt from
        a clone, which is entry A2's subject."""
        src = gen.source()
        assert src == gen.REPO_TXT, (
            f"the generator is reading {src}, not the repository copy "
            f"{gen.REPO_TXT}. If the repo copy has gone, restore it rather "
            f"than letting the Desktop fallback become the source of truth.")
        r = subprocess.run(["git", "ls-files", "--error-unmatch",
                            str(src.relative_to(REPO))],
                           capture_output=True, text=True, cwd=str(REPO))
        assert r.returncode == 0, (
            f"{src.relative_to(REPO)} is not tracked by git: {r.stderr.strip()}")

    def test_the_two_spoken_copies_agree(self, gen):
        """They diverged once already, 85 lines against 115."""
        if not gen.DESKTOP_TXT.is_file():
            pytest.skip("no Desktop copy on this machine; nothing to compare")
        assert gen.REPO_TXT.read_text() == gen.DESKTOP_TXT.read_text(), (
            "the repository and Desktop spoken copies have diverged; run the "
            "generator to bring them back into agreement")


class TestTheCommittedMarkdownMatchesARebuild:
    def test_check_mode_passes_on_the_committed_file(self, gen):
        assert gen.main(["--check"]) == 0, (
            "the committed markdown differs from a rebuild. Fix the GENERATOR, "
            "not the markdown: a hand edit to the .md is undone by the next "
            "rebuild, which is how this guard came to exist.")

    def test_check_mode_writes_nothing(self, gen):
        """A guard that mutates the tree is worse than no guard."""
        before = DST.read_bytes()
        gen.main(["--check"])
        assert DST.read_bytes() == before, (
            "--check modified the markdown file, so running the guard changes "
            "the thing it checks")

    def test_a_corrupted_markdown_is_detected(self, gen):
        """THE CONTROL. Without it, `--check` returning 0 says nothing: a
        generator that always agreed with itself would pass the test above."""
        original = DST.read_bytes()
        try:
            DST.write_text(DST.read_text() + "\na line no rebuild would emit\n")
            assert gen.main(["--check"]) == 1, (
                "an appended line was NOT detected, so --check cannot tell the "
                "committed file from a rebuild and every 0 it returns is "
                "uninformative")
        finally:
            DST.write_bytes(original)
        assert DST.read_bytes() == original, "the control failed to restore"

    def test_render_is_deterministic(self, gen):
        """2 renders of the same source must agree, or the match above is luck."""
        assert gen.render() == gen.render()
