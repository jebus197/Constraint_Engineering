"""The prose must agree with the archive, not merely with itself.

WHY THIS EXISTS. `reference_runner_v3.sk_threshold_shadow` carried, in its
docstring, "s_star reads 0.0 in 3181 of 3181 archived records, Wilson
[99.88%, 100.00%]", where the claim intended was 3816. The pair was INTERNALLY
CONSISTENT: [99.88%, 100.00%] is exactly the Wilson interval for 3181 of 3181,
because Wilson's lower bound at k = n is n/(n + z**2) in closed form.

AND 3181 WAS ITSELF A CORRECT MEASUREMENT, which is the part that makes this
worth a permanent test. It is the exact number of gate records whose `s_star`
is the literal float `0.0`; the other 635 carry the STRING "0", confined to the
4 `sim45_*` families, which stringify every numeric. A strict `x == 0.0` gives
3181 and a coercing `float(x) == 0.0` gives 3816. Neither number was a typo:
they are 2 predicates over 1 corpus.

The first draft of this file said 3181 was "the line count of
`dynamic_management.py`", a transcription error. That was a story I invented and
did not test; `bench/dynamic_management.py` is 78 lines. Both panel seats
re-measured independently and refuted it -- including the seat whose own theory
it originally was. The sequence is worth keeping: a strict count was stated, a
seat flagged it, I refuted the seat on a bad measurement, I reversed and adopted
the seat's untested theory, and measurement finally settled what neither
position had. See [[feedback_check_the_whole_set]].

WHAT NO SOURCE-TEXT CHECK COULD HAVE CAUGHT IT WITH. `execute-do-not-grep`:
"A test that asserts on the SOURCE TEXT of a module asserts only that the
module describes itself consistently. It cannot detect a producer and a
consumer that disagree, because each description is individually correct."
That is this defect exactly. The sibling checker
`scripts/wilson_interval_consistency.py` -- which verifies a count against the
interval printed beside it -- returns "every stated interval agrees" on the
original sentence and exits 0. It catches a HALF-DONE correction, which is a
different and also real hazard, but it cannot catch this one, and its own
docstring says so.

The only instrument that can is one that RE-MEASURES THE ARCHIVE and compares
the measurement to the prose: a producer and a consumer, executed against each
other. That is what this file does.

IF THIS TEST FAILS BECAUSE THE ARCHIVE GREW, THE TEST IS RIGHT AND THE PROSE IS
STALE. Restate the claim with the new count AND recompute its interval -- both,
or the pair still lies. Do not widen the assertion to make it pass.
"""
from __future__ import annotations

import math
import pathlib
import re
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))

RUNNER = REPO / "bench" / "reference_runner_v3.py"
LOGS = REPO / "bench" / "logs"

Z = 1.959963984540054


def _wilson(k: int, n: int):
    p = k / n
    d = 1.0 + Z * Z / n
    c = p + Z * Z / (2 * n)
    h = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n))
    return ((c - h) / d, (c + h) / d)


def _measured_total() -> int:
    """The archive's own answer, from the COMMITTED script, not from prose."""
    from measure_sk_threshold_gate_fire_rate import route_1_structured

    return route_1_structured(LOGS)["total"]


def _stated() -> tuple[int, int, float, float]:
    """The (k, n, lo, hi) the docstring asserts."""
    import ast

    tree = ast.parse(RUNNER.read_text(encoding="utf-8"))
    doc = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "sk_threshold_shadow":
            doc = ast.get_docstring(node)
            break
    assert doc, "sk_threshold_shadow has no docstring to check"
    # Collapse wrapping before matching. The sentence is line-wrapped in the
    # source and a pattern that encoded one particular wrap would break on the
    # next reflow -- turning a real check into a spurious failure, which is how
    # checks get deleted.
    doc = " ".join(doc.split())
    m = re.search(
        r"`s_star` is zero in ([\d,]+) of ([\d,]+) gate records in `bench/logs`,"
        r"\s*Wilson\s*\[\s*([\d.]+)%\s*,\s*([\d.]+)%\s*\]",
        doc,
    )
    assert m, (
        "the docstring no longer states its count and interval in the expected "
        "form, so this test can no longer check it. Restore the sentence or "
        "update the pattern -- do not delete the check."
    )
    return (int(m.group(1).replace(",", "")), int(m.group(2).replace(",", "")),
            float(m.group(3)), float(m.group(4)))


@pytest.mark.skipif(not LOGS.is_dir(), reason="archive not present")
def test_stated_count_equals_the_measured_archive():
    k, n, _lo, _hi = _stated()
    measured = _measured_total()
    assert k == n, f"the sentence claims {k} of {n}; it is meant to be all of them"
    assert n == measured, (
        f"THE PROSE AND THE ARCHIVE DISAGREE. sk_threshold_shadow's docstring "
        f"states {n} archived gate records; re-measuring the archive with "
        f"scripts/measure_sk_threshold_gate_fire_rate.py gives {measured}. "
        f"This is the 3181-for-3816 defect recurring. Correct the count AND "
        f"recompute the Wilson interval beside it -- fixing one leaves the "
        f"pair lying."
    )


@pytest.mark.skipif(not LOGS.is_dir(), reason="archive not present")
def test_stated_interval_belongs_to_the_stated_count():
    """The half-fix guard, executed here rather than trusted from the scanner."""
    k, n, lo, hi = _stated()
    elo, ehi = (x * 100.0 for x in _wilson(k, n))
    assert abs(lo - elo) <= 0.005 and abs(hi - ehi) <= 0.005, (
        f"the docstring states [{lo}%, {hi}%] but Wilson for {k} of {n} is "
        f"[{elo:.4f}%, {ehi:.4f}%]. An interval is a FUNCTION of k and n and "
        f"moves when the count is corrected."
    )


def test_the_scanner_cannot_catch_this_and_admits_it():
    """Guard the boundary between the 2 instruments, so neither is over-trusted.

    Executed, not asserted from prose: the original defective sentence is fed
    to the scanner and it must report NO disagreement. If a future change makes
    the scanner catch it, this test fails and the docstrings of both files --
    which tell readers the scanner cannot -- must be corrected.
    """
    sys.path.insert(0, str(REPO / "scripts"))
    from wilson_interval_consistency import scan_text

    # wilson-lint: expected-defect -- deliberate fixture, see the marker's note
    original = ("s_star reads 0.0 in 3181 of 3181 archived records, Wilson "
                "[99.88%, 100.00%]")
    assert scan_text("<probe>", original) == [], (
        "the scanner now flags the original defect. That is an improvement, "
        "but the docstrings in scripts/wilson_interval_consistency.py and in "
        "this file both state that it cannot. Update them."
    )
    # wilson-lint: expected-defect -- deliberate fixture
    half_fixed = ("s_star reads 0.0 in 3181 of 3181 archived records, Wilson "
                  "[99.90%, 100.00%]")
    assert len(scan_text("<probe>", half_fixed)) == 1, (
        "the scanner no longer catches a half-done correction, which is the "
        "one thing it is for."
    )


def test_the_repo_carries_no_count_interval_disagreement():
    """RUN the checker over the repository, so it is not an unreached addition.

    The additive standard binds symmetrically: "an addition that nothing reaches
    is not additive either -- every new flag, gate, subcommand or entry point
    must be wired to a caller and executed by a test." A lint script with no
    caller is exactly the shape this session found 3 other instances of.

    Precedent for the wiring: `scripts/note_vagueness_lint.py` is reached by 3
    test files that execute it. This does the same, and as a live ratchet rather
    than a smoke test -- the repository is at 0 disagreements now, so any future
    count/interval pair that contradicts itself fails here.

    Intervals merely WIDER than computed are reported as notes and do not fail;
    outward rounding weakens a claim and is not a defect. 4 such notes stand.
    """
    import subprocess

    r = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "wilson_interval_consistency.py"),
         str(REPO)],
        capture_output=True, text=True, timeout=300,
    )
    assert r.returncode == 0, (
        "a stated count and its stated interval disagree somewhere in the "
        "repository. Correct BOTH -- fixing one leaves the pair still lying.\n\n"
        + r.stdout[-3000:]
    )
    assert "files scanned" in r.stdout, r.stdout[:500]
