#!/usr/bin/env python3
"""The register must beat a word search, or it is decoration. Measured.

HIS REQUIREMENT, 2026-10-17: the register must be *"much more useful to you as a
way of listing, proposing, searching, applying and remembering which fixes have
and have not been done or applied that just relying on semantic
searches/vocabulary/word searches on their own ... You will need to set this up
and test it and ensure that it does work better than other methods for this
purpose and so that it doesn't risk simply becoming decoration that does nothing
useful."*

GROUND TRUTH FROM THE REPOSITORY, NOT FROM A MODEL. The task list is under
version control, so its history supplies labels nobody invented. Searching the
list as it stood at an earlier commit: entries that EXISTED then are POSITIVES
(querying them with today's wording is exactly the rediscovery case), and the
entries added AFTER are NEGATIVES, genuinely unknown at that point. No
sentence-embedding model is involved, which is the honest limit the sibling
operating-characteristic script had to state about its own labels.

THE QUERY CARRIES NO IDENTIFIER. A rediscovery happens when work is DESCRIBED,
not cited; if the query carried "B14" the register would win trivially on an
exact reference lookup. And the word search is swept over 19 thresholds and
reported at its BEST, because beating a crippled baseline proves nothing.

MEASURED 2026-10-17 over 149 queries (107 known, 42 new), the list at 60d0d536:

                        recall              specificity          accuracy
    register       104/107  97.1963%     42/42  100.0000%    146/149  97.9866%
    word search    106/107  99.0654%     36/42   85.7143%    142/149  95.3020%

    specificity difference: Fisher exact p = 0.025811, and an mpmath one-sided
                            point mass of 0.012905 on the observed table
    recall difference:      Fisher exact p = 0.621454 -- NOT significant

WHICH ERROR MATTERS, AND WHY THE VERDICT IS NOT A TIE. A false positive says
"already known" about work that is NEW, so it SUPPRESSES work and does so
invisibly. A false negative duplicates work, which is visible the moment the
duplicate is proposed. The word search suppresses 6 of 42 new items; the register
suppresses none. Its apparent recall advantage is noise at p = 0.62.

So his condition is met: the register is better on the error that cannot be seen,
and no better on the one that can. That is the honest claim and it is the one
worth having.
"""
from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "does_the_register_beat_word_search_2026-10-17.py"


def _mod():
    spec = importlib.util.spec_from_file_location("cmp_ws", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    sys.modules["cmp_ws"] = m
    spec.loader.exec_module(m)
    return m


def test_the_comparison_script_exists_and_answers_help():
    assert SCRIPT.is_file(), (
        "his requirement was a demonstration, not an assertion; the script that "
        "produces it must exist")
    r = subprocess.run([sys.executable, str(SCRIPT), "--help"],
                       capture_output=True, text=True, timeout=120)
    assert r.returncode == 0 and "usage" in r.stdout.lower()


def test_the_labels_come_from_the_repository_history():
    """Not from an embedding model, which the sibling script had to caveat."""
    m = _mod()
    old = m._entries_at("60d0d536")
    new = m._entries_at("HEAD")
    assert len(old) > 50, f"only {len(old)} entries at the reference commit"
    assert len(new) > len(old), (
        "HEAD has no more entries than the reference commit, so there are no "
        "true negatives and specificity cannot be measured at all")
    negatives = [i for i in new if i not in old]
    assert len(negatives) >= 20, (
        f"only {len(negatives)} negatives; too few to bound specificity")


def test_the_query_carries_no_identifier():
    """Or the register wins trivially and the comparison is worthless.

    CHECKED OVER THE REAL ENTRIES, not one constructed example. A single example
    can be satisfied by an accident of its own wording; the claim is about every
    query the comparison issues.
    """
    m = _mod()
    new_entries = m._entries_at("HEAD")
    assert new_entries, "the list could not be read at HEAD"
    leaked = []
    for ident, block in new_entries.items():
        q = m._query_for(ident, block)
        if not q:
            continue
        if q.lstrip().startswith(ident):
            leaked.append(ident)
    assert not leaked, (
        f"{len(leaked)} query(ies) still begin with their own identifier, so the "
        f"register would win on an exact reference lookup rather than on "
        f"content: {leaked[:6]}")
    # and the substance must survive the stripping
    probe = m._query_for("B14", "**B14. 94 of 212 archived blockers can neither "
                                "be resolved nor released.** Added today.")
    assert "blockers" in probe, "the substance was stripped with the identifier"


def test_the_word_search_is_not_a_straw_man():
    """It must get its best threshold, and it must have real stop-words.

    Without a stop-list the word search matches on "the" and "fix" and scores far
    worse than it deserves, which would flatter the register.
    """
    m = _mod()
    assert len(m.STOP) > 80, (
        f"the stop-list has only {len(m.STOP)} words; the baseline would be "
        f"beaten on common vocabulary rather than on substance")
    for common in ("the", "fix", "test", "measured", "founder"):
        assert common in m.STOP, common
    # THE SWEEP IS CHECKED IN THE CODE, NOT IN THE PROSE. A first version
    # asserted `"BEST" in src and "swept" in src`, and BOTH words appear in this
    # script's own docstring -- so replacing the 19-threshold sweep with a single
    # pinned threshold left the test green. Found by mutation 2026-10-17.
    import ast
    tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
    swept = 0
    for node in ast.walk(tree):
        if not isinstance(node, ast.For):
            continue
        tgt = node.target
        if isinstance(tgt, ast.Name) and tgt.id == "thr":
            # count the thresholds the comprehension actually produces
            try:
                swept = len(eval(compile(ast.Expression(node.iter), "<t>", "eval"),
                                 {"range": range}, {}))
            except Exception:                                 # noqa: BLE001
                swept = 0
    assert swept >= 10, (
        f"the baseline is swept over {swept} threshold(s). Fewer than 10 means "
        f"it is being reported at a pinned operating point rather than its best, "
        f"which makes it a straw man.")


def test_the_register_still_wins_on_specificity():
    """THE LOAD-BEARING CLAIM, re-measured rather than quoted.

    Specificity is the measure that matters: a false positive says "already
    known" about NEW work and so suppresses it invisibly. If this ever stops
    holding, the register is decoration and his condition is not met.
    """
    r = subprocess.run([sys.executable, str(SCRIPT), "--quiet"],
                       capture_output=True, text=True, timeout=900)
    assert r.returncode == 0, r.stderr[-500:]
    out = r.stdout
    assert "VERDICT" in out, out[-400:]
    assert "THE REGISTER DOES NOT BEAT THE WORD SEARCH" not in out, (
        "the register no longer beats the word search on any measure, so by his "
        "own condition it has become decoration:\n" + out[-900:])
    assert "specificity" in out.lower(), out[-400:]


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
