"""A DONE marker must name tests that exist, hold assertions, and are collected.

THE MECHANISM THE FOUNDER ASKED FOR AND DID NOT GET. His question, verbatim:
*"But you were supposed to have built a mechanism that ensured you could complete
this work mechanically, and in such a way that it would survive future compaction
events until all the work was complete. Did you do this?"*

Half of it existed. The compaction half works: 5 `UserPromptSubmit` hooks are
wired, one reports task-list state, and it fired on every turn after the
2026-09-09 19:19:57 compaction. The completion half did not exist at all.
`task_list_markers.CONTRADICTORY` refuses an entry only when its own 2 labels
disagree — DONE beside PROPOSED. **Nothing compared a DONE marker against the
repository**, so the engine recorded what the assistant CLAIMED.

WHAT THAT COST, MEASURED. On 2026-09-10, 18 adversarial agents re-checked all 19
DONE entries by running the tests rather than reading the claims, with a second
reviewer on every disputed one: **11 of 19 were overstated — 57.89%, Wilson
[36.3%, 76.9%], Clopper-Pearson [33.5%, 79.7%]** — 2 reviewers agreeing on every
one. **One was not an overstatement but a live regression at HEAD**: task 6.3
sent every production run into a single shared directory, and its 8 tests were
green throughout because each built a fake config by hand.

WHAT THIS GUARD DOES AND DELIBERATELY DOES NOT DO. It requires each DONE entry to
NAME its evidence, and checks that each named file exists, parses, holds at least
1 real test function, and is inside the directory the suite collects. It does NOT
prove the tests would fail against a reverted fix — that is per-item mutation
testing and cannot be done generically here. So this closes the "named nothing",
"named a file that is gone", "named an empty file" and "named a file nothing
runs" holes, and the remaining hole is stated rather than papered over.

AND IT does not bind the named test to the task. cc2 rewrote all 19 evidence
fields to point at one unrelated pre-existing file and both this guard and the
marker engine stayed green. A reader of the first docstring could believe the
named file at least CONCERNS the entry; it need not. Naming is cheap and this
guard only raises the price.

CC2'S WIDER POINT, ADOPTED RATHER THAN ARGUED WITH: "The hole was never 'DONE
markers name no evidence.' It was that the author of the claim is also the
auditor of the claim." What produced the 57.89% figure was 18 adversarial agents
RUNNING the tests, not a missing field. This guard raises the cost of a hollow
claim; it does not change who is grading. That is a real limit on what V1 answers
of the founder's question, and it is recorded here rather than in a reply he may
not re-read.

The `evidence:` field is OPTIONAL in the marker regex and REQUIRED here, so an
older entry cannot be broken by the format while a DONE entry without it fails.
"""

import ast
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))

import task_list_markers as M  # noqa: E402

LIST = REPO / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md"
DONE = [e for e in M.parse_entries(LIST) if e.state == "DONE"]


def test_the_list_and_its_done_entries_exist():
    """Guards every test below against passing on an empty collection."""
    assert LIST.is_file()
    assert len(DONE) >= 10, f"only {len(DONE)} DONE entries — is the list intact?"


@pytest.mark.parametrize("entry", DONE, ids=lambda e: e.ident)
def test_a_done_entry_names_its_evidence(entry):
    """THE PROPERTY. Before 2026-09-10, 18 of 19 named nothing at all."""
    assert entry.evidence, (
        f"task {entry.ident} is marked DONE and names no test file. A DONE "
        f"marker without evidence records a claim, not a result — which is how "
        f"11 of 19 came to be overstated. Add `| evidence: <path>` to its marker.")


@pytest.mark.parametrize("entry", DONE, ids=lambda e: e.ident)
def test_every_named_file_exists(entry):
    gone = [f for f in entry.evidence if not (REPO / f).is_file()]
    assert not gone, f"task {entry.ident} names files that do not exist: {gone}"


@pytest.mark.parametrize("entry", DONE, ids=lambda e: e.ident)
def test_every_named_file_holds_a_real_test(entry):
    """A NAMED FILE THAT ASSERTS NOTHING IS NOT EVIDENCE.

    Parsed rather than grepped: a file can contain the string `def test_` in a
    docstring. This counts function definitions and requires at least one to
    contain an assertion or a pytest.raises."""
    for f in entry.evidence:
        src = (REPO / f).read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(src, filename=f)
        funcs = [n for n in ast.walk(tree)
                 if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                 and n.name.startswith("test_")]
        assert funcs, f"task {entry.ident}: {f} defines no test function"
        # A TRUTHY CONSTANT IS NOT AN ASSERTION. `def test_hollow(): assert True`
        # satisfied the first version — cc2, panel review 2026-09-10.
        def _real_assert(node):
            for k in ast.walk(node):
                if isinstance(k, ast.Assert):
                    t = k.test
                    if isinstance(t, ast.Constant) and bool(t.value):
                        continue          # assert True / assert 1 / assert "x"
                    return True
            return "raises" in (ast.get_source_segment(src, node) or "")

        with_assert = [n for n in funcs if _real_assert(n)]
        assert with_assert, (
            f"task {entry.ident}: {f} has {len(funcs)} test function(s) and not "
            f"one of them asserts anything")


@pytest.mark.parametrize("entry", DONE, ids=lambda e: e.ident)
def test_every_named_file_is_somewhere_the_suite_collects(entry):
    """A test the suite never runs is not evidence either.

    RESOLVED CONTAINMENT, NOT A STRING PREFIX. cc2 defeated the first version in
    panel review with `bench/tests/../../../../../../tmp/.../test_outside.py`,
    which passes `startswith("bench/tests/")` and resolves outside the
    repository entirely. This is the project's own bounded-traversal defect
    class, in a guard written to close a different one."""
    collected = (REPO / "bench" / "tests").resolve()
    for f in entry.evidence:
        target = (REPO / f).resolve()
        assert collected in target.parents or target.parent == collected, (
            f"task {entry.ident} names {f}, which resolves to {target} — "
            f"outside {collected}, so nothing in the suite runs it")


def test_no_entry_carries_an_unrecognised_state():
    """A WRONG-CASE STATE LEAVES THIS GUARD'S UNIVERSE SILENTLY.

    fable found it in panel review on 2026-09-10: `state: Done` parses as the
    literal "Done", which is not in `STATES`, so every test above — all of which
    filter on `state == "DONE"` — stops seeing the entry. The marker engine's own
    `check()` does refuse it, and fable observed the pulse hook crashing on it
    too, but both are separate mechanisms: this guard was relying on an
    accidental chain rather than on its own universe being sound.

    Asserted here so the guard cannot be escaped by a typo in the one field that
    decides whether it looks at an entry at all."""
    bad = [(e.ident, e.state) for e in M.parse_entries(LIST)
           if e.state is not None and e.state not in M.STATES]
    assert not bad, (
        f"entries carry a state outside {M.STATES}: {bad}. Any entry whose state "
        f"is not exactly DONE is invisible to every check in this file.")


def test_every_entry_carries_a_marker_at_all():
    """The other way out of the universe: no marker means no state means no
    scrutiny. `check()` reports it; this makes the guard's own dependence on it
    explicit."""
    unmarked = [e.ident for e in M.parse_entries(LIST) if e.state is None]
    assert not unmarked, f"entries with no marker, and so no state: {unmarked}"


def test_the_evidence_field_is_optional_in_the_format_and_required_here():
    """The format must not break entries that predate it.

    An OPEN entry carrying no evidence must still parse; only DONE is held to
    the requirement. If this fails, adding the field has broken the list."""
    entries = M.parse_entries(LIST)
    assert entries, "the list no longer parses at all"
    open_without = [e for e in entries if e.state == "OPEN" and not e.evidence]
    assert open_without, (
        "every OPEN entry now carries evidence, which would mean the field has "
        "become mandatory for work not yet done")


def test_what_this_guard_does_not_prove_is_written_down():
    """THE STATED LIMIT, pinned so it cannot quietly be forgotten.

    A GUARD THAT AUDITS ITSELF CANNOT FAIL, and the first version of this test
    was one. It read `Path(__file__).read_text()` — the file that contains the
    needle inside this very assert statement — so the search always succeeded on
    its own source literal. cc2 demonstrated it in panel review on 2026-09-10:
    deleting the ENTIRE module docstring left the file at 79 passed, and direct
    measurement showed the needle never matched the prose at all, because the
    sentence wraps across lines. It now reads `__doc__` with whitespace
    normalised, so a wrapped sentence still matches and the source literal is
    not in scope."""
    doc = " ".join((__doc__ or "").split())
    assert "does NOT prove the tests would fail against a reverted fix" in doc, (
        "the stated limit has left the module docstring")
    assert "does not bind the named test to the task" in doc, (
        "the wider limit cc2 identified has left the module docstring")
