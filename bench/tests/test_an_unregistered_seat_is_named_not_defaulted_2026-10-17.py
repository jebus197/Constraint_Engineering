"""A seat missing from a per-model table is NAMED on the POST screen.

TASKS B13 AND B21. HIS RULING, 2026-10-16: *"adding and removing models can
become much simpler, because the only thing that governs capability is
demonstrated measured capability, not model names"*, and *"The ideal scenario is
that ... this should become a trivial feature of the harness for a researcher to
do."*

THE MEASURED PROBLEM, from
`scripts/how_many_places_must_change_to_add_a_model_2026-10-16.py`: a researcher
adding a seat must edit **12 per-model tables across 6 live-harness files** and
add 1 registry `.toml`, and of the 10 steps a new seat passes through, **9 fail
SILENTLY and 1 fails loudly -- 90.0000%, Wilson [59.5850%, 98.2124%],
Clopper-Pearson [55.4984%, 99.7471%]**. That producer's own conclusion is that
*"the real problem is not the count, it is the failure mode"*, and that making
admission trivial means making the misses LOUD first.

WHAT IS BUILT HERE AND WHAT IS NOT. A single registration point changes how
every seat is configured and is recorded as needing his ruling. Making the
misses loud changes no configuration at all, so the POST screen now carries
`every seat is fully registered`, which names each absent table per seat.

IT RETURNS PASS, AND THAT IS DELIBERATE. The screen is 2-state and halts at the
first FAIL, with `scripts/post_semantics_2026-10-06.py` reasoning over that order
in z3. A missing entry degrades a seat rather than invalidating a run, and a
check that refused every run with an unregistered stand-in would be switched off
-- the same reasoning the suite gate already applies to STALE. So the absences
travel in the headline and the notes, which the screen prints on a PASS as well
as a FAIL.

THE FIRST VERSION REPORTED A FALSE POSITIVE, pinned here. It keyed every table
through `base_model_label` and so reported CC2 and ChatGPT as absent from
`PHENOTYPE_TRANSFORMS`, when both are present under the composer's own keys
(`opus_4_6`, `chatgpt_5_4`). The mapping is `composer.COMPOSER_MODEL_MAP`, which
the measuring producer already used -- the instrument existed and the check
reinvented its key derivation and got it wrong.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
POST = REPO / "scripts" / "preflight_health_check_2026-10-06.py"
SEMANTICS = REPO / "scripts" / "post_semantics_2026-10-06.py"
CHECK_NAME = "every seat is fully registered"


def _load(path, name):
    sys.path.insert(0, str(REPO / "scripts"))
    sys.path.insert(0, str(REPO))
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def post():
    return _load(POST, "post_under_test")


@pytest.fixture(scope="module")
def semantics():
    return _load(SEMANTICS, "post_semantics_under_test")


def test_a_registered_seat_is_not_reported_absent(post):
    """NO FALSE POSITIVE. This is what the first version got wrong."""
    status, headline, notes = post.check_every_seat_is_fully_registered(
        ["CC2", "ChatGPT"])
    assert status == post.PASS, headline
    assert "MISSING" not in headline, headline
    for seat in ("CC2", "ChatGPT"):
        line = next(n for n in notes if n.startswith(f"{seat}:"))
        assert "present in all" in line, line


def test_an_unregistered_seat_is_named_with_every_absent_table(post):
    """A researcher who misses a table must be told WHICH, not just that."""
    status, headline, notes = post.check_every_seat_is_fully_registered(
        ["CC2", "Kimi"])
    assert status == post.PASS, "the screen must stay 2-state and not refuse"
    assert "MISSING" in headline and "SILENT default" in headline, headline
    line = next(n for n in notes if n.startswith("Kimi:"))
    assert "absent from" in line
    for table in ("runner_core.MODEL_SPECS", "runner_core.INITIAL_FINGERPRINTS",
                  "composer.PHENOTYPE_TRANSFORMS",
                  "composer.MODEL_COHERENCE_BUDGETS"):
        assert table in line, f"{table} not named in: {line}"
    # AND THE REGISTERED SEAT IS STILL REPORTED CLEAN in the same call.
    assert any(n.startswith("CC2:") and "present in all" in n for n in notes)


def test_no_seats_is_a_failure_not_a_pass(post):
    """A screen that passes on an empty roster is checking nothing."""
    status, headline, _ = post.check_every_seat_is_fully_registered([])
    assert status == post.FAIL, headline


def test_the_check_is_on_the_screen_and_last(post):
    """ANTI-UNWIRED, and the position matters under halt-on-first-failure."""
    names = [name for name, _, _ in post.CHECKS]
    assert CHECK_NAME in names, "the check is not on the POST screen"
    assert names[-1] == CHECK_NAME, (
        "a check that cannot FAIL on a degraded seat must not sit above one "
        f"that can; order is {names}")
    wants_seats = dict((n, w) for n, _, w in post.CHECKS)[CHECK_NAME]
    assert wants_seats is True, "it needs the roster to check anything"


def test_the_semantics_map_knows_about_it(semantics):
    """The z3 order proof must reason over the screen as it actually is."""
    assert CHECK_NAME in semantics.DEPENDENCIES
    assert semantics.DEPENDENCIES[CHECK_NAME] == []
    assert CHECK_NAME in semantics.POST_ORDER
    assert semantics.part2_order_is_topological() is True


def test_the_halt_cost_illustration_tracks_the_screen(semantics):
    """A typed 5 became wrong the moment a 6th check landed.

    The illustration now derives from `POST_ORDER`, so the sentence stays true
    as checks are added. Asserted because the figure is quoted on the screen.
    """
    src = SEMANTICS.read_text(encoding="utf-8")
    assert "halt_runs.subs(k, _k)" in src, (
        "the halt-cost illustration substitutes a literal again, so it will go "
        "stale the next time a check is added")
    assert "_k = len(POST_ORDER)" in src


def test_the_table_list_is_not_empty(post):
    """ANTI-VACUITY. With no tables the check passes everything for ever."""
    status, headline, notes = post.check_every_seat_is_fully_registered(["CC2"])
    line = next(n for n in notes if n.startswith("CC2:"))
    import re
    found = re.search(r"present in all (\d+) table", line)
    assert found, line
    assert int(found.group(1)) >= 4, (
        f"only {found.group(1)} per-model table(s) are checked; the measured "
        f"count a researcher must edit is 12, so this is a floor and it may "
        f"not fall")
