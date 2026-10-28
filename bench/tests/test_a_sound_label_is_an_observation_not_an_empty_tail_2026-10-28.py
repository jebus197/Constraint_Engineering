# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'joint_the_nine_changes_2026-10-28', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: cb5c7f6a3303d544be749da95b2869e21a0bbe5e07b6fa171c6391b24b514c41
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""A `premature` label is evaluated over a tail, and an empty tail is not sound.

WHAT THIS PINS, and why it was not noticed. `fire_points` labels a gate-fire
position with

    premature = any(h > 0 for rounds recorded AFTER that position)

`any([])` is False. So a fire point with NO recorded round after it is labelled
SOUND -- not because the run was observed to be clean, but because it was not
observed at all. Measured on the archive on 2026-10-28 (joint panel round):

  * 10 of 30 fire points have an EMPTY tail. All 10 are labelled sound and 0 of
    them could have been labelled premature, by construction.
  * 10 more have a tail of exactly 1. All 10 are labelled sound.
  * Not one of the 8 premature labels comes from a tail shorter than 2.
  * Tail length ALONE predicts the label at AUC 0.9716 [0.8882, 1.0000] --
    higher than every signal the producer scores, `findings_count` (0.9058)
    included. Spearman(tail, premature) rho = 0.7515, p = 1.70e-06.

The consequence is not cosmetic. `findings_count` and `registry_total` both grow
with the number of rounds a run records, and so does the tail. The AUC table is
therefore, in part, length scored against length, and the 0.266667 false-quiet
rate is computed over a denominator two thirds of which could not have been
refuted. Any rule fitted to these labels -- the adaptive `T` of the 2026-10-27
pre-registration among them -- inherits that.

THE REPAIR IS ADDITIVE AND CHANGES NO PUBLISHED NUMBER. `tail_rounds` is carried
on every row, the unobserved count is printed unconditionally, and `--min-tail`
lets a caller drop labels that could not have been refuted. The default is 0, so
every figure that has been cited still comes out of the default invocation.

These tests EXECUTE the producer rather than reading it.
"""
from __future__ import annotations

import importlib.util
import json
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
PRODUCER = REPO / "bench" / "can_any_signal_see_a_premature_close_2026-10-27.py"


def _mod():
    spec = importlib.util.spec_from_file_location("_prem_tail", PRODUCER)
    m = importlib.util.module_from_spec(spec)
    sys.modules["_prem_tail"] = m
    spec.loader.exec_module(m)
    return m


def _rows():
    m = _mod()
    rows = m.fire_points(m.collect(), 3)
    if not rows:
        pytest.skip("no archived reports in this tree")
    return m, rows


def test_every_fire_point_carries_the_tail_its_label_was_computed_over():
    _, rows = _rows()
    missing = [r for r in rows if "tail_rounds" not in r]
    assert not missing, (
        f"{len(missing)} fire point(s) carry a label with no record of the "
        "window it was evaluated over")


def test_an_empty_tail_can_only_ever_be_labelled_sound():
    """Not a prediction -- a property of `any([])`. If this ever fails, the
    label definition has changed and the figures below must be re-derived."""
    _, rows = _rows()
    empty = [r for r in rows if r["tail_rounds"] == 0]
    assert empty, "the archive no longer contains an unobserved fire point"
    assert all(not r["premature"] for r in empty), (
        "an empty-tail fire point was labelled premature, which `any([])` "
        "cannot produce")


def test_the_label_set_is_disclosed_as_part_observation_and_part_silence():
    """The count of unobserved labels must reach the reader of the default run.

    A figure of '8 premature of 30' with 10 of the 30 unobservable is a claim
    about evidence, not evidence.
    """
    out = subprocess.run(
        [sys.executable, str(PRODUCER)], capture_output=True, text=True,
        timeout=300, cwd=str(REPO))
    assert out.returncode == 0, out.stderr[-2000:]
    assert "EMPTY tail" in out.stdout, (
        "the default invocation does not tell the reader how many of its "
        f"labels rest on no observation:\n{out.stdout[:1500]}")


def test_tail_length_outranks_every_scored_signal():
    """The strongest available signal is not in the table: it is the table's
    own denominator."""
    m, rows = _rows()
    p = [r["tail_rounds"] for r in rows if r["premature"]]
    q = [r["tail_rounds"] for r in rows if not r["premature"]]
    tail = m.auc_mw(p, q)
    assert tail is not None and tail["auc"] > 0.9, tail
    best = 0.0
    for s in m.SIGNALS:
        a = [r["signals"][s] for r in rows
             if r["premature"] and r["signals"].get(s) is not None]
        b = [r["signals"][s] for r in rows
             if not r["premature"] and r["signals"].get(s) is not None]
        got = m.auc_mw(a, b)
        if got:
            best = max(best, abs(got["auc"] - 0.5))
    assert abs(tail["auc"] - 0.5) >= best, (
        f"tail length separates at |AUC-0.5|={abs(tail['auc']-0.5):.4f}, which "
        f"no longer exceeds the best scored signal at {best:.4f}")


def test_min_tail_is_wired_and_the_default_changes_no_published_figure():
    """The flag must be reachable from the command line AND must be inert by
    default -- an addition nothing reaches is not additive, and an addition that
    silently moves a cited number is worse."""
    base = json.loads(subprocess.run(
        [sys.executable, str(PRODUCER), "--json"], capture_output=True,
        text=True, timeout=300, cwd=str(REPO)).stdout)
    assert base["min_tail"] == 0
    assert base["dropped_by_min_tail"] == 0
    assert base["fire_points"] == base["fire_points_before_min_tail"]
    assert base["labelled_sound_on_an_EMPTY_tail"] > 0

    cut = json.loads(subprocess.run(
        [sys.executable, str(PRODUCER), "--json", "--min-tail", "1"],
        capture_output=True, text=True, timeout=300, cwd=str(REPO)).stdout)
    assert cut["fire_points"] < base["fire_points"], (
        "--min-tail 1 dropped nothing; the flag is not reached")
    assert cut["premature"] == base["premature"], (
        "dropping unobserved labels removed a premature label, which it must "
        "not: no premature label can come from an empty tail")
    assert cut["sound"] < base["sound"]
