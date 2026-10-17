"""A19's last sub-part is covered by construction, and this fails if it stops.

HIS DESIGN POINT, 2026-09-10, verbatim: *"Having the admissibility switch off
for prose targets is also questionable, as clearly it should simply mark a
purely prose input as 'inadmissible', while still solving any computationally
reducible elements within that prose! This is STEM. No one will be using CDSFL
to write poetry!"*

THE PER-FIX HALF IS BUILT: `_fix_touches_reducible` asks whether a given fix
edits a fenced listing or only the prose around it, so a prose edit inside a
markdown target is unscored while a code edit inside the same target is scored.

WHAT REMAINED NAMED was finer: PER-HUNK classification, for a fix carrying
several SEARCH/REPLACE blocks that do not all touch the same kind of thing.

MEASURED ACROSS THE WHOLE ARCHIVE, with the project's own parser
`bench.build_acceptance.SEARCH_REPLACE`: of 25,445 fix texts, 13,219 parse as
exactly 1 hunk, 12,226 parse as 0, and 0 parse as more than 1 -- 0.0000%,
Wilson [0.0000%, 0.0151%]. Among PARSEABLE patches that is 13,219 of 13,219
single-hunk, 100.0000%, Wilson [99.9709%, 100.0000%].

SO PER-HUNK AND PER-FIX GIVE THE SAME ANSWER for every patch that exists. A19's
remaining sub-part is covered BY CONSTRUCTION rather than deferred by
judgement, which is the stronger claim and the checkable one -- and this file is
what makes it checkable. The moment a 2-hunk fix appears, the first test here
FAILS and says to build per-hunk classification.

THE FIRST VERSION OF THAT MEASUREMENT MATCHED NOTHING. It used `<{5,7}\\s*SEARCH`
and the real marker is 4 angle brackets, so it reported 0 single-hunk AND 0
multi-hunk across 25,445 texts -- and a predicate returning 0 for everything
looks exactly like a clean result. Hence the project's own parser here rather
than a second copy of the pattern.

AND THE 12,226 ZERO-HUNK TEXTS ARE NOT A HIDDEN DEFECT: they are prose
proposals, some carrying a bare `<<<<` block with no `SEARCH <path>` header,
which the parser correctly refuses. That is the named outcome
REJECTED_NO_PATCH -- a proposal that is not an applicable patch is a different
thing from a patch that fails to apply, and this project's rule is that those 2
must never render identically.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

PRODUCER = REPO / "scripts" / "is_per_hunk_classification_exercisable_2026-10-17.py"
LOGS = REPO / "bench" / "logs"


def _producer():
    spec = importlib.util.spec_from_file_location("_a19", PRODUCER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def counts():
    if not LOGS.exists():
        pytest.skip("no archive in this checkout")
    c = _producer().survey()
    if c["total"] == 0:
        pytest.skip("the archive holds no fix texts")
    return c


def test_no_fix_in_the_archive_carries_more_than_one_hunk(counts):
    """THE RATCHET. This failing is the signal to build per-hunk scoring."""
    assert counts["many"] == 0, (
        f"{counts['many']} of {counts['total']} fixes now carry more than 1 "
        f"hunk, so per-fix and per-hunk classification can disagree and A19's "
        f"remaining sub-part is now exercisable. Build it: classify each "
        f"SEARCH/REPLACE block separately in `_fix_touches_reducible`.")


def test_the_parser_is_not_matching_nothing(counts):
    """THE VACUITY GUARD, and it is first in importance.

    The first version of this measurement used the wrong number of angle
    brackets and matched NOTHING -- 0 single-hunk and 0 multi-hunk across
    25,445 texts -- which is indistinguishable from the clean result it was
    looking for. A predicate that returns 0 for everything proves nothing."""
    assert counts["one"] > 1000, (
        f"only {counts['one']} fixes parsed as a single hunk out of "
        f"{counts['total']}. The parser has stopped matching the archive's "
        f"format, so the 0 multi-hunk figure above is vacuous rather than "
        f"reassuring.")


def test_the_canonical_parser_is_the_one_used():
    """ONE PATTERN, NOT A COPY. A second copy is free to drift from the first,
    and the first version of this measurement drifted immediately."""
    src = PRODUCER.read_text(encoding="utf-8")
    assert "from bench.build_acceptance import SEARCH_REPLACE" in src, (
        "the producer no longer uses the project's own SEARCH_REPLACE pattern, "
        "so its hunk count can disagree with what the acceptance path parses")


def test_the_pattern_really_parses_a_two_hunk_fix():
    """EXECUTED: the parser must be able to SEE 2 hunks, or 'none found' means
    nothing. This is the counterexample the archive does not supply."""
    from bench.build_acceptance import SEARCH_REPLACE
    two = ("<<<< SEARCH a/one.py\nold one\n==== REPLACE\nnew one\n>>>>\n"
           "<<<< SEARCH a/two.md\nold two\n==== REPLACE\nnew two\n>>>>\n")
    hunks = SEARCH_REPLACE.findall(two)
    assert len(hunks) == 2, (
        f"the canonical parser finds {len(hunks)} hunks in a deliberately "
        f"2-hunk fix, so a real 2-hunk fix in the archive would also be "
        f"miscounted and the ratchet above could never fire")
    assert {h[0].strip() for h in hunks} == {"a/one.py", "a/two.md"}


def test_the_per_fix_half_exists_and_distinguishes_the_two_cases():
    """The claim 'per-hunk equals per-fix' is only worth anything if per-fix
    itself does something. Executed on both cases."""
    from bench.reference_runner_v3 import _fix_touches_reducible
    source = ("Some prose about a method.\n\n```python\n"
              "def f():\n    return 1\n```\n\nMore prose.\n")
    code_fix = ("<<<< SEARCH doc.md\ndef f():\n    return 1\n"
                "==== REPLACE\ndef f():\n    return 2\n>>>>\n")
    prose_fix = ("<<<< SEARCH doc.md\nSome prose about a method.\n"
                 "==== REPLACE\nSome clearer prose about a method.\n>>>>\n")
    touches_code, why_code = _fix_touches_reducible(code_fix, source, "doc.md")
    touches_prose, why_prose = _fix_touches_reducible(prose_fix, source,
                                                      "doc.md")
    assert touches_code is True, f"a fix editing the fenced listing: {why_code}"
    assert touches_prose is False, f"a fix editing only prose: {why_prose}"
    assert why_code and why_prose, "both answers must carry a reason"


def test_the_producer_runs_and_refuses_an_unknown_flag():
    import subprocess
    ok = subprocess.run([sys.executable, str(PRODUCER)], capture_output=True,
                        text=True, cwd=str(REPO))
    assert ok.returncode in (0, 1), ok.stderr[-300:]
    bad = subprocess.run([sys.executable, str(PRODUCER), "--bogus"],
                         capture_output=True, text=True, cwd=str(REPO))
    assert bad.returncode != 0
