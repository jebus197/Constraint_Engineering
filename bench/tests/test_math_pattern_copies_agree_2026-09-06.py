"""2 live copies of the maths-routing pattern disagreed on 0.46% of findings.

Whether a finding routed to mathematical verification depended on WHICH MODULE
ASKED. Measured 2026-09-06 over 8709 distinct archived finding descriptions: the 2
copies disagreed on 40, Wilson [0.34%, 0.62%], and in 100% of those
`immune_agents` routed as MATH while `verification_utils` did not.

THIS TEST EXECUTES BOTH PATTERNS rather than comparing their source text. Under
`execute-do-not-grep`: a test asserting on source proves only that each module
describes itself consistently, which is exactly true of 2 patterns that disagree.
"""
from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

CORPUS = [
    "the bound is exceeded",              # 'bound'    — only the broad form had it
    "this threshold is wrong",            # 'threshold'
    "the inequality does not hold",       # 'inequality'
    "the formula is misstated",           # 'formula'
    "the equation is inconsistent",       # 'equation'
    "log scaling is assumed",             # 'log'
    "exp growth is claimed",              # 'exp'
    "x = y + 1",                          # both
    "sqrt(2) is irrational",              # both
    "a plain english sentence about ducks",   # neither
]


def _patterns():
    vu = importlib.import_module("bench.verification_utils")
    ia = importlib.import_module("bench.immune_agents")
    return vu._MATH_PATTERN, ia._MATH_PATTERN


def test_the_two_copies_agree_on_every_corpus_item():
    a, b = _patterns()
    disagree = [t for t in CORPUS if bool(a.search(t)) != bool(b.search(t))]
    assert not disagree, f"the 2 routing patterns still disagree on: {disagree}"


def test_the_broad_alternatives_are_present_in_both():
    """The 7 that were missing. If one copy loses them again this fails."""
    a, b = _patterns()
    for text in ("the bound is exceeded", "this threshold is wrong",
                 "the inequality does not hold", "the formula is misstated",
                 "the equation is inconsistent", "log scaling", "exp growth"):
        assert a.search(text), f"verification_utils no longer routes {text!r} as maths"
        assert b.search(text), f"immune_agents no longer routes {text!r} as maths"


def test_a_non_mathematical_sentence_still_routes_nowhere():
    """Unifying on the broader form must not make the pattern match everything."""
    a, b = _patterns()
    plain = "a plain english sentence about ducks"
    assert not a.search(plain) and not b.search(plain)
