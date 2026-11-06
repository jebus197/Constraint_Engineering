#!/usr/bin/env python3
"""His annotations must arrive WITH the text they answer, by default.

★ HIS OBSERVATION, 2026-11-06: *"There has been a problem that recently
emerged, where you were reading my tts responses, but ignoring the body of text
that came before them and that I was responding too."*

He was right, and the cause was a DEFAULT rather than an oversight in any turn.
The reader already printed each annotation with the 6 lines above it, but only
when asked; its default was a per-file tally of counts. Measured over 1 session:
572 invocations, 12 passing the flag, 0.020979, Wilson [0.012041, 0.036308].

THIS GUARD PINS THE INVERTED DEFAULT, so restoring the old one goes red. It also
pins that `--text` is still ACCEPTED, because removing a flag that every
recorded command uses would break callers for no gain.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
if not (REPO / "bench").is_dir():
    REPO = Path("/Users/georgejackson/Developer_Projects/Constraint_Engineering")
READER = REPO / "scripts" / "read_founder_responses_2026-10-11.py"
RESPONSES = Path("~/Developer_Projects/Responses").expanduser()


def run(*args: str):
    return subprocess.run([sys.executable, str(READER), *args],
                          cwd=REPO, capture_output=True, text=True, timeout=600)


@pytest.fixture(scope="module")
def corpus():
    if not READER.is_file():
        pytest.skip(f"reader absent at {READER}")
    if not RESPONSES.is_dir():
        pytest.skip(f"his Responses corpus is absent at {RESPONSES}")
    return True


class TestTheDefaultCarriesHisWords:
    def test_the_default_prints_annotations_not_only_counts(self, corpus):
        r = run("--since", "2026-11-01")
        assert r.returncode == 0, r.stderr[-600:]
        assert "HIS WORDS:" in r.stdout, (
            "the default output carries no annotation of his. The default was "
            "inverted on 2026-11-06 precisely so that it would; if this fails, "
            "the tally-only default has been restored.")

    def test_the_default_also_carries_the_text_he_answered(self, corpus):
        """The context lines are the whole point of his observation."""
        r = run("--since", "2026-11-01")
        assert "with the report lines it attaches to" in r.stdout, (
            "the context header is gone, so an annotation may be arriving "
            "without the body it answers")

    def test_counts_still_gives_the_old_tally_only_output(self, corpus):
        r = run("--since", "2026-11-01", "--counts")
        assert r.returncode == 0, r.stderr[-600:]
        assert "annotations read:" in r.stdout
        assert "HIS WORDS:" not in r.stdout, (
            "--counts must give the tally alone; it is the opt-in route to the "
            "behaviour that used to be the default")

    def test_the_text_flag_is_still_accepted(self, corpus):
        """A flag every recorded command passes must not start erroring."""
        r = run("--since", "2026-11-01", "--text")
        assert r.returncode == 0, (
            "--text was retained as a no-op so existing callers keep working; "
            f"it now errors:\n{r.stderr[-400:]}")
        assert "HIS WORDS:" in r.stdout

    def test_context_defaults_to_six_lines(self, corpus):
        """The context setting was already correct and must stay so."""
        src = READER.read_text(encoding="utf-8")
        m = re.search(r'"--context",\s*type=int,\s*default=(\d+)', src)
        assert m and int(m.group(1)) == 6, (
            "the context default is no longer 6; it is what makes the subject "
            "of an annotation visible")

    def test_zero_context_still_restores_the_old_shape(self, corpus):
        r = run("--since", "2026-11-01", "--context", "0")
        assert r.returncode == 0, r.stderr[-400:]
