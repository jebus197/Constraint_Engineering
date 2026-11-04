"""`classify_items` must name the same entry on every process, not whichever the set yielded.

THE DEFECT, found 2026-11-04 when the commit gate refused a commit. `scripts/
has_he_already_ruled_on_the_parked_2026-10-13.py:classify_items` built
`idents = {i for i in IDENT_RE.findall(heading)}` -- a SET -- and then took the
FIRST ident that a ruling's text mentions, with a `break`:

    for date, txt in ann_text:
        for ident in idents:            # hash order, randomised per process
            if re.search(...):
                hits.append((date, ident, txt[:150]))
                break

A real parked item's heading names 6 entries -- B20, B21, B22, B56, B76 and
C0001 -- so the reason line recorded whichever of them the set happened to yield
first. Python randomises string hashing per process, so the SAME file regenerated
twice gave different reason lines. Measured over 3 regenerations of the live file:
the B21/B20 split came out 11/4, then 12/3, then 12/3.

WHAT THAT COST. `experimental_notes/PARKED_FOR_THE_FOUNDER.md` stores the reason
line, and `test_every_item_survives_a_real_apply` asserts every stored body
reappears verbatim in a fresh regeneration. So the guard went red reporting
"body lost" for an item that was present in full -- a guard accusing a correct
file, and a FLAKY one, which this project's own record calls worse than a red
one. It had nothing to do with the commit it refused.

THE SIBLING BRANCH ALREADY SORTED. 6 lines below, the undecided route reads
`undecided.append((heading, sorted(idents)))`. The determinism was known and
applied on one path and not the other, which is why the repair is 1 token.

WHY THIS FILE EXISTS RATHER THAN A SOURCE ASSERTION. Hash randomisation is
per-process, so a test running in one process cannot observe the defect at all:
a single process sees one consistent order and passes. The property is only
visible ACROSS processes, so this guard spawns them with different
`PYTHONHASHSEED` values and compares outputs. Asserting on the source text
instead would be the `execute-do-not-grep` failure -- it would prove only that
the module describes itself consistently.

Producer of the split figures: the measurement is reproduced by this file's own
`test_the_chosen_ident_is_stable_across_hash_seeds`.
"""
import os
import pathlib
import subprocess
import sys
import textwrap

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
MEASURE = REPO / "scripts" / "has_he_already_ruled_on_the_parked_2026-10-13.py"

#: A heading naming 6 entries, which is the shape that actually occurs: the live
#: item reads "...the role dimension question (B21, B22), which definition counts
#: as a seat being right (B56), the convergence gate ruling (B76), whether a
#: switched-off finding stays listed (C0001), and B20 whose monitoring arm needs
#: a run that has not happened".
HEADING = ("All 6 remaining open entries wait on a founder decision: the role "
           "dimension question (B21, B22), which definition counts as a seat "
           "being right (B56), the convergence gate ruling (B76), whether a "
           "switched-off finding stays listed (C0001), and B20 whose monitoring "
           "arm needs a run that has not happened")

#: A ruling text mentioning EVERY one of them, so the inner loop's choice is
#: decided purely by iteration order. That is the adversarial case.
RULING = ("on B20 and B21 and B22 and B56 and B76 and C0001 together, "
          "the decision stands")

PROBE = textwrap.dedent('''
    import importlib.util, json, pathlib, sys
    spec = importlib.util.spec_from_file_location("_m", sys.argv[1])
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    heading, ruling = sys.argv[2], sys.argv[3]
    items = [(heading, "body text with no marker")]
    states = {}
    ann_text = [("2026-11-01", ruling)]
    closed, ruled, undecided, body_only = m.classify_items(items, states, ann_text)
    out = [[d, i] for h, hits in ruled for d, i, _ in hits]
    print(json.dumps(out))
''')


def _run(seed: str):
    env = dict(os.environ, PYTHONHASHSEED=seed)
    r = subprocess.run([sys.executable, "-c", PROBE, str(MEASURE), HEADING, RULING],
                       capture_output=True, text=True, cwd=str(REPO), env=env)
    assert r.returncode == 0, r.stdout + r.stderr
    return r.stdout.strip()


SEEDS = ("0", "1", "2", "3", "7", "11", "13", "17")


@pytest.fixture(scope="module")
def answers():
    return {s: _run(s) for s in SEEDS}


def test_the_probe_actually_produces_a_hit(answers):
    """ANTI-VACUITY. A probe returning nothing would make every comparison trivial."""
    for seed, out in answers.items():
        assert out and out != "[]", (
            f"seed {seed} produced no hit; the fixture no longer exercises the "
            f"inner loop and this guard is vacuous")


def test_the_chosen_ident_is_stable_across_hash_seeds(answers):
    """THE PROPERTY. 8 processes, 8 different hash seeds, 1 answer."""
    distinct = set(answers.values())
    assert len(distinct) == 1, (
        "classify_items names a different entry depending on the process hash "
        f"seed, which makes the parked file's reason line nondeterministic: "
        f"{ {s: a for s, a in answers.items()} }")


def test_the_chosen_ident_is_the_lexicographically_first(answers):
    """Pins WHICH answer, so a future change away from sorted() is visible.

    B20 is first among B20, B21, B22, B56, B76, C0001. This does not claim B20 is
    the most informative choice — only that the choice is fixed and stated.
    """
    import json
    out = json.loads(next(iter(answers.values())))
    assert out, "no hit to inspect"
    assert out[0][1] == "B20", f"expected the smallest ident, got {out[0][1]}"


def test_the_sibling_branch_still_sorts():
    """The undecided route's sort is where the determinism was already known.

    Asserted so a future edit cannot quietly make the 2 branches disagree again,
    which is how the defect arose in the first place.
    """
    src = MEASURE.read_text(encoding="utf-8")
    assert "undecided.append((heading, sorted(idents)))" in src
    assert "for ident in sorted(idents):" in src
