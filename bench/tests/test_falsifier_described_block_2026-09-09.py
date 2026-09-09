"""The falsifier intake must accept a description between the label and the fence.

Written 2026-09-09 while closing the halt cause of the 2026-09-08 Exp 45 run.

MEASURED FIRST, BUILT SECOND. Across 6,727 archived reply files there are 6,363
`FALSIFIER:` labels with a fenced block within 3 lines. The existing pattern
captures 5,282 and misses 1,081 -- a 16.99% miss rate, Wilson [16.09%, 17.93%] --
and 1,066 of those misses carry a DESCRIPTION between the label and the fence,
which is essentially the whole of the loss.

THE FIRST PROPOSED FIX WAS REFUTED BEFORE IT WAS APPLIED. The recommendation on
file was to WIDEN the existing pattern. Measured, a widened single pattern
recovered 4,867 blocks against the current 5,295 -- a net loss of 428. So the
repair is a UNION of two patterns, which cannot lose a block the first already
captures, and the invariant is asserted here rather than assumed.

THE GAP IS CONSTRAINED ON PURPOSE. A looser tolerant pattern recovered 507 extra
blocks of which 4 were the label appearing inside test code -- `assert
"FALSIFIER:" not in minimal` -- a 0.8% false-positive rate, Wilson [0.3%, 2.0%].
A false falsifier is worse than a missing one, because the harness EXECUTES it.
Requiring the gap to open with a letter or bracket and carry no quote or backtick
recovers 492 and excludes all 4.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "bench"))
from runner_core import (extract_falsifiers, _FALSIFIER_BLOCK_RE,  # noqa: E402
                         _FALSIFIER_BLOCK_DESCRIBED_RE)

PLAIN = 'FALSIFIER:\n```python\nassert 1 == 1\n```\n'
DESCRIBED = 'FALSIFIER: a test that reproduces the collision\n```python\nassert 2 == 2\n```\n'
CODE_LOOKALIKE = 'FALSIFIER:" not in minimal\n```python\nassert 3 == 3\n```\n'


def test_the_plain_form_still_works():
    _, ordered = extract_falsifiers(PLAIN)
    assert ordered == ["assert 1 == 1"]


def test_a_described_falsifier_is_now_recovered():
    """The 1,066-case class. Before this change it returned nothing."""
    assert _FALSIFIER_BLOCK_RE.findall(DESCRIBED) == [], (
        "the old pattern must NOT match this, or the test proves nothing")
    _, ordered = extract_falsifiers(DESCRIBED)
    assert ordered == ["assert 2 == 2"], ordered


def test_the_label_inside_code_is_NOT_captured():
    """A false falsifier is worse than a missing one: the harness runs it."""
    assert _FALSIFIER_BLOCK_DESCRIBED_RE.search(CODE_LOOKALIKE) is None, (
        "a gap opening with a quote is a code fragment, not a description")


def test_both_forms_together_keep_document_order():
    both = PLAIN + "\nsome prose\n\n" + DESCRIBED
    _, ordered = extract_falsifiers(both)
    assert ordered == ["assert 1 == 1", "assert 2 == 2"], ordered


def test_the_union_never_loses_what_the_old_pattern_found():
    """The invariant that makes this a union rather than a replacement.

    Asserted rather than assumed, because the replacement approach was measured
    LOSING 428 blocks and this is the property that rules that out."""
    samples = [PLAIN, DESCRIBED, PLAIN + DESCRIBED, CODE_LOOKALIKE,
               "no falsifier here at all", PLAIN * 3]
    for s in samples:
        old = [m.group(1).strip() for m in _FALSIFIER_BLOCK_RE.finditer(s)]
        _, new = extract_falsifiers(s)
        assert len(new) >= len(old), f"union lost a block on {s[:40]!r}"
        for o in old:
            assert o in new, f"union dropped {o!r}"


def test_a_fence_far_below_the_label_is_not_swallowed():
    """The gap must stay on the label's own line; an unrelated fence 5 paragraphs
    later must not be attached to it."""
    far = ("FALSIFIER: see below\n\nsome prose\n\nmore prose\n\nyet more\n\n"
           "```python\nassert 4 == 4\n```\n")
    _, ordered = extract_falsifiers(far)
    assert ordered == [], f"a distant fence must not be captured: {ordered}"


@pytest.mark.parametrize("gap", ["a test", "(given two packets)", "*a check*", "A test"])
def test_description_shaped_gaps_are_accepted(gap):
    text = f"FALSIFIER: {gap}\n```python\nassert 5 == 5\n```\n"
    _, ordered = extract_falsifiers(text)
    assert ordered == ["assert 5 == 5"], f"gap {gap!r} should be accepted"


@pytest.mark.parametrize("gap", ['" not in x', "'q'", "`code`"])
def test_code_shaped_gaps_are_rejected(gap):
    text = f"FALSIFIER:{gap}\n```python\nassert 6 == 6\n```\n"
    assert _FALSIFIER_BLOCK_DESCRIBED_RE.search(text) is None, f"gap {gap!r} should be rejected"
