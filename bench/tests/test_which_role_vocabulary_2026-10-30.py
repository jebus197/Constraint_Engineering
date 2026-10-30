#!/usr/bin/env python3
"""The role-vocabulary survey must not count itself, and must not type its figures.

WHY THIS GUARD EXISTS. Entry B21 turns on a design question the founder has not
answered, and the survey that informs it was written on 2026-10-30 with 2 defects
that both appeared within 2 minutes of writing it:

  1. IT COUNTED ITSELF. The script lives in `scripts/` and quotes every role word
     in order to search for them, so it inflated the very count it computed --
     66 of 73 where an ad-hoc count minutes earlier gave 63 of 67, the whole
     difference being the script's own text. This is the defect the kappa census
     had to be repaired for on 2026-10-17, where it counted its own prose.

  2. IT PRINTED A HARDCODED RATIO ONE LINE BELOW A COMPUTED ONE. "63 to 4" was a
     literal, already wrong when it printed, in a script whose entire purpose is
     that a figure must travel with its producer.

WHAT THIS FILE ALSO DOES. It makes the producer REACHED. A script with no caller
and no test is the addition-nothing-reaches half of the additive standard, which
this project has 12 recorded instances of.
"""
from __future__ import annotations

import importlib.util
import json
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
PRODUCER = REPO / "scripts" / "which_role_vocabulary_does_the_code_speak_2026-10-30.py"


def _mod():
    spec = importlib.util.spec_from_file_location("role_vocab", PRODUCER)
    m = importlib.util.module_from_spec(spec)
    sys.modules["role_vocab"] = m
    spec.loader.exec_module(m)
    return m


def test_the_producer_exists():
    assert PRODUCER.is_file(), f"absent: {PRODUCER}"


def test_help_answers_without_surveying():
    r = subprocess.run([sys.executable, str(PRODUCER), "--help"],
                       capture_output=True, text=True, cwd=str(REPO), timeout=120)
    assert r.returncode == 0, r.stderr[-300:]
    assert "usage:" in r.stdout
    assert "structural share" not in r.stdout, "--help ran the survey"


def test_it_does_not_count_itself():
    """THE DEFECT THAT PROMPTED THIS FILE, pinned by the property not the number.

    The survey must not report its own file among the files it found, whatever
    the counts happen to be as the tree changes.
    """
    m = _mod()
    uses = m.quoted_uses()
    own = PRODUCER.relative_to(REPO).as_posix()
    offenders = sorted({p for w, rows in uses.items() for p, _ in rows
                        if pathlib.PurePosixPath(p).as_posix() == own})
    assert not offenders, (
        f"the survey counted its own file {offenders}, which inflates every "
        f"figure it reports -- the defect measured on 2026-10-30 as 66 of 73 "
        f"against a true 63 of 67")


def test_every_printed_figure_is_derived_not_typed():
    """NO ROLE-COUNT LITERAL IN THE OUTPUT PATH.

    The hardcoded "63 to 4" sat 1 line below a computed figure. This asserts the
    totals the script PRINTS equal the totals it COMPUTES, so a literal
    reintroduced anywhere in the reporting path disagrees with the data.
    """
    m = _mod()
    s, f = m.totals(m.quoted_uses())
    r = subprocess.run([sys.executable, str(PRODUCER)],
                       capture_output=True, text=True, cwd=str(REPO), timeout=300)
    assert r.returncode == 0, r.stderr[-300:]
    assert f"{s}/{s + f}" in r.stdout, (
        f"the printed share does not name the computed totals {s}/{s + f}")
    assert f"{s} to {f}" in r.stdout, (
        f"the printed ratio does not name the computed totals {s} to {f}; a "
        f"literal has been reintroduced beside its own computation")


def test_the_json_flag_is_wired_and_internally_consistent():
    r = subprocess.run([sys.executable, str(PRODUCER), "--json"],
                       capture_output=True, text=True, cwd=str(REPO), timeout=300)
    assert r.returncode == 0, r.stderr[-300:]
    d = json.loads(r.stdout)
    assert d["structural_total"] == sum(d["structural"].values())
    assert d["functional_total"] == sum(d["functional"].values())
    assert d["total"] == d["structural_total"] + d["functional_total"]


def test_both_vocabularies_are_named_so_the_question_stays_visible():
    """ANTI-DRIFT. The entry's question is which vocabulary SHOULD win; a survey
    that silently dropped one side would answer it by omission."""
    m = _mod()
    assert set(m.STRUCTURAL) == {"collator", "player_manager", "participant"}
    assert set(m.FUNCTIONAL) == {"worker", "classifier", "orchestrator"}
