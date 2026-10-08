# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'rung_promotion_and_model_ids_2026-10-08', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 34dd4412442b974954e5c5a5f2720162581b9cfde5b575b09cea6c0df46dccdc
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""Falsifiers for bench/stream_idle_timeout.py. Real subprocesses, no mocks.

Run: python3 -m pytest bench/test_stream_idle_timeout.py -q -s
"""
from __future__ import annotations

import sys

import pytest

from bench.stream_idle_timeout import (
    derive_ceiling, harvest, min_samples_for_ceiling)

SLOW_BUT_WORKING = (
    "import time,sys\n"
    "for i in range(8):\n"
    "    print('line', i); time.sleep(0.4)\n"
    "print('DONE')\n")

CHATTY_HANG = (
    "import time\n"
    "while True:\n"
    "    print('retrying...'); time.sleep(0.2)\n")

SILENT_HANG = "import time\nwhile True: time.sleep(5)\n"

BLOCK_BUFFERED = (          # would emit nothing until exit without -u/UNBUFFERED
    "import sys,time\n"
    "for i in range(6):\n"
    "    sys.stdout.write('x%d\\n' % i); time.sleep(0.3)\n")


def _run(src, idle, ceiling):
    return harvest([sys.executable, "-c", src], idle_timeout=idle, ceiling=ceiling)


def test_idle_timeout_does_not_kill_a_slow_but_working_process():
    r = _run(SLOW_BUT_WORKING, idle=1.0, ceiling=30.0)
    print(f"\n  slow-but-working under idle cap: {r['reason']} at {r['elapsed']}s, "
          f"{len(r['lines'])} lines, last={r['lines'][-1]!r}")
    assert r["reason"] == "exit" and r["lines"][-1] == "DONE"


def test_a_total_cap_alone_kills_that_same_working_process():
    """The founder's objection to an arbitrary wall clock, demonstrated."""
    r = _run(SLOW_BUT_WORKING, idle=30.0, ceiling=1.5)
    print(f"\n  same process under a 1.5s total cap: {r['reason']} at "
          f"{r['elapsed']}s, {len(r['lines'])} lines (work discarded)")
    assert r["reason"] == "ceiling" and "DONE" not in r["lines"]


def test_idle_timeout_catches_a_silent_hang_fast():
    r = _run(SILENT_HANG, idle=1.0, ceiling=30.0)
    print(f"\n  silent hang: {r['reason']} at {r['elapsed']}s")
    assert r["reason"] == "idle" and r["elapsed"] < 3.0


def test_idle_timeout_ALONE_never_catches_a_hung_process_that_keeps_talking():
    """WHAT BREAKS THE IDLE TIMEOUT. Falsified if the idle cap trips here."""
    r = _run(CHATTY_HANG, idle=1.0, ceiling=2.5)
    print(f"\n  chatty hang (prints every 0.2s, idle cap 1.0s): {r['reason']} at "
          f"{r['elapsed']}s, {len(r['lines'])} lines -- only the ceiling ends it")
    assert r["reason"] == "ceiling", "idle cap tripped -> no ceiling needed"
    assert len(r["lines"]) > 5


def test_block_buffering_is_defeated_so_a_working_child_is_not_read_as_idle():
    r = _run(BLOCK_BUFFERED, idle=1.0, ceiling=30.0)
    print(f"\n  block-buffered writer under idle cap 1.0s: {r['reason']} at "
          f"{r['elapsed']}s, {len(r['lines'])} lines")
    assert r["reason"] == "exit" and len(r["lines"]) == 6


def test_the_composition_is_justified_because_neither_control_covers_both_cases():
    idle_only_on_chatty = _run(CHATTY_HANG, idle=1.0, ceiling=2.5)["reason"]
    ceiling_only_on_slow = _run(SLOW_BUT_WORKING, idle=30.0, ceiling=1.5)["reason"]
    both_on_slow = _run(SLOW_BUT_WORKING, idle=1.0, ceiling=30.0)["reason"]
    both_on_chatty = _run(CHATTY_HANG, idle=1.0, ceiling=2.5)["reason"]
    print(f"\n  idle-only on chatty hang: {idle_only_on_chatty} (not 'idle')")
    print(f"  ceiling-only on slow work: {ceiling_only_on_slow} (work lost)")
    print(f"  composed: slow work -> {both_on_slow}; chatty hang -> {both_on_chatty}")
    assert idle_only_on_chatty != "idle"      # idle alone misses case 1
    assert ceiling_only_on_slow == "ceiling"  # ceiling alone misses case 2
    assert both_on_slow == "exit" and both_on_chatty == "ceiling"


def test_the_sample_size_needed_to_place_a_ceiling_is_itself_derived():
    m05 = min_samples_for_ceiling(0.05)
    m20 = min_samples_for_ceiling(0.20)
    print(f"\n  runs needed before a ceiling sits below the observed max: "
          f"{m05} at kill_budget=0.05, {m20} at 0.20")
    assert (m05, m20) == (73, 16)
    # closed form cross-check
    z = 1.959963984540054
    assert m05 == int((z * z * 0.95 * 0.05) / 0.05 ** 2) + 1


def test_below_that_sample_size_the_ceiling_errs_long_rather_than_guessing():
    small = [2.0, 2.4, 3.1, 3.3, 4.0, 4.1, 5.2, 6.0, 8.1, 9.0,
             10.0, 11.5, 12.0, 14.0, 21.0, 22.0, 30.0, 41.0, 55.0, 90.0]
    c = derive_ceiling(small, kill_budget=0.05)
    print(f"\n  m={len(small)} < {min_samples_for_ceiling(0.05)}: ceiling {c}s "
          f"= observed max {max(small)}s (errs long, preserves work)")
    assert c == max(small)


def test_at_an_adequate_sample_size_the_ceiling_sits_strictly_below_the_max():
    import numpy as np
    rng = np.random.default_rng(909)
    obs = list(np.round(rng.lognormal(mean=2.0, sigma=0.8, size=400), 2))
    c = derive_ceiling(obs, kill_budget=0.05)
    loose = derive_ceiling(obs, kill_budget=0.20)
    killed = float(np.mean(np.asarray(obs) > c))
    print(f"\n  m={len(obs)}: ceiling {c}s < max {max(obs)}s; "
          f"fraction of legitimate runs it would kill {killed:.4f} <= 0.05; "
          f"kill_budget=0.20 gives the tighter {loose}s")
    assert c < max(obs) and loose < c and killed <= 0.05
    with pytest.raises(ValueError):
        derive_ceiling([], kill_budget=0.05)
