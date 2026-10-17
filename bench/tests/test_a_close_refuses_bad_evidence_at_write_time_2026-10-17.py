"""The setter refuses unsound DONE evidence BEFORE it writes the marker.

WHY THIS EXISTS. Every task close in this project was an ad-hoc inline script,
and three in a single session wrote an evidence value the suite then rejected:

  * C16 named a prose annotation in the founder's Responses directory;
  * B15 named a directory;
  * C2 and C9 kept `evidence: Responses annotation dated <date>` because the
    closing script was guarded with `if "evidence:" not in marker` -- which
    SKIPPED entries that already carried a value, leaving the stale one in
    place while reporting success. That is the quietest shape of the three: an
    annotation is provenance for the QUESTION, never verification of the
    ANSWER.

The repair is `scripts/task_list_markers.set_marker`, which calls
`evidence_objections` -- the same function the DONE-evidence guard now
executes -- and raises instead of writing. One definition, two callers, so the
writer and the checker cannot drift apart. Each test here works on a COPY in
tmp_path; none touches the real list.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))

import task_list_markers as M  # noqa: E402

ENTRY_LINE = "**Z9.** A fabricated entry used only by this guard.\n"


@pytest.fixture
def listfile(tmp_path):
    """A minimal task list inside a repo-shaped tmp tree."""
    root = tmp_path
    (root / "experimental_notes").mkdir()
    (root / "bench" / "tests").mkdir(parents=True)
    path = root / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md"
    path.write_text(
        "# List\n\n" + ENTRY_LINE +
        "<!-- task: Z9 | state: OPEN | status: PROPOSED -->\n",
        encoding="utf-8")
    return path


def _plant(listfile, name, body):
    target = listfile.parents[1] / "bench" / "tests" / name
    target.write_text(body, encoding="utf-8")
    return f"bench/tests/{name}"


def test_an_annotation_is_refused_as_evidence(listfile):
    """The exact value that reached the list three times."""
    with pytest.raises(ValueError) as exc:
        M.set_marker("Z9", state="DONE", status="COMMITTED",
                     evidence="Responses annotation dated 2026-10-07",
                     path=listfile)
    assert "does not exist" in str(exc.value)
    assert "state: OPEN" in listfile.read_text(encoding="utf-8"), (
        "the marker was written despite the refusal")


def test_a_directory_is_refused_as_evidence(listfile):
    """B15's shape. `is_file()` alone would have caught this one; the point is
    that the objection now arrives at write time, named."""
    (listfile.parents[1] / "bench" / "tests" / "subdir").mkdir()
    with pytest.raises(ValueError) as exc:
        M.set_marker("Z9", state="DONE", status="COMMITTED",
                     evidence="bench/tests/subdir", path=listfile)
    assert "directory" in str(exc.value)


def test_a_file_that_asserts_nothing_is_refused(listfile):
    rel = _plant(listfile, "test_hollow.py",
                 "def test_hollow():\n    assert True\n")
    with pytest.raises(ValueError) as exc:
        M.set_marker("Z9", state="DONE", status="COMMITTED", evidence=rel,
                     path=listfile)
    assert "asserts anything" in str(exc.value)


def test_a_file_with_no_test_function_is_refused(listfile):
    rel = _plant(listfile, "test_empty.py", "X = 1\n")
    with pytest.raises(ValueError) as exc:
        M.set_marker("Z9", state="DONE", status="COMMITTED", evidence=rel,
                     path=listfile)
    assert "no test function" in str(exc.value)


def test_evidence_outside_the_collected_directory_is_refused(listfile):
    """The traversal shape cc2 used to defeat the first guard: a path that
    matches the prefix `bench/tests/` and resolves outside it."""
    # It must EXIST to be a traversal: a path that does not exist is refused
    # for the duller reason, which is how the first version of this test
    # passed for the wrong cause.
    outside = listfile.parents[1] / "bench" / "elsewhere"
    outside.mkdir(parents=True)
    (outside / "test_away.py").write_text(
        "def test_x():\n    assert 1 == 1\n", encoding="utf-8")
    with pytest.raises(ValueError) as exc:
        M.set_marker("Z9", state="DONE", status="COMMITTED",
                     evidence="bench/tests/../elsewhere/test_away.py",
                     path=listfile)
    assert "outside" in str(exc.value)


def test_a_sound_close_is_written_with_the_fields_in_order(listfile):
    rel = _plant(listfile, "test_real.py",
                 "def test_x():\n    assert 2 + 2 == 4\n")
    line = M.set_marker("Z9", state="DONE", status="COMMITTED", evidence=rel,
                        ruled="2026-10-17", path=listfile)
    assert line == (f"<!-- task: Z9 | state: DONE | status: COMMITTED | "
                    f"evidence: {rel} | ruled: 2026-10-17 -->")
    # And it parses back through the same module that wrote it.
    entries = {e.ident: e for e in M.parse_entries(listfile)}
    assert entries["Z9"].state == "DONE"
    assert entries["Z9"].evidence == (rel,)
    assert entries["Z9"].ruled == "2026-10-17"


def test_advancing_state_alone_does_not_drop_a_ruling(listfile):
    """A ruling the founder gave is the one field a careless close must not
    lose: `ruled:` is what moves an item out of his decision queue."""
    rel = _plant(listfile, "test_real.py",
                 "def test_x():\n    assert 2 + 2 == 4\n")
    M.set_marker("Z9", evidence=rel, ruled="2026-10-16", path=listfile)
    M.set_marker("Z9", state="DONE", status="COMMITTED", path=listfile)
    entries = {e.ident: e for e in M.parse_entries(listfile)}
    assert entries["Z9"].ruled == "2026-10-16", (
        "advancing the state dropped the ruling date, which would put a "
        "settled item back in front of him")
    assert entries["Z9"].evidence == (rel,)


def test_writing_twice_is_idempotent(listfile):
    rel = _plant(listfile, "test_real.py",
                 "def test_x():\n    assert 2 + 2 == 4\n")
    first = M.set_marker("Z9", state="DONE", status="COMMITTED", evidence=rel,
                         path=listfile)
    body = listfile.read_text(encoding="utf-8")
    second = M.set_marker("Z9", state="DONE", status="COMMITTED", evidence=rel,
                          path=listfile)
    assert first == second
    assert listfile.read_text(encoding="utf-8") == body, (
        "a second identical close changed the file; the parked-file generator "
        "failed exactly this way on 2026-10-17, writing 28 marks for 14 items")


def test_an_unknown_identifier_raises_rather_than_appending(listfile):
    before = listfile.read_text(encoding="utf-8")
    with pytest.raises(KeyError):
        M.set_marker("NOPE1", state="DONE", status="COMMITTED", path=listfile)
    assert listfile.read_text(encoding="utf-8") == before


@pytest.mark.parametrize("field,value", [("state", "FINISHED"),
                                         ("status", "SHIPPED")])
def test_an_unrecognised_label_is_refused(listfile, field, value):
    with pytest.raises(ValueError) as exc:
        M.set_marker("Z9", **{field: value}, path=listfile)
    assert value in str(exc.value)


def test_a_non_done_state_needs_no_evidence(listfile):
    """The refusal is scoped to DONE. An OPEN entry with no evidence is
    normal, and making it an error would block every ordinary state change."""
    line = M.set_marker("Z9", state="BLOCKED", status="PROPOSED", path=listfile)
    assert "evidence:" not in line


def test_the_real_list_still_parses_and_its_done_entries_are_sound():
    """The one test here that touches the live file, read-only."""
    entries = M.parse_entries()
    done = [e for e in entries if e.state == "DONE"]
    assert done, "no DONE entries; this guard would be vacuous"
    objections = []
    for e in done:
        objections += M.evidence_objections(e.ident, e.evidence)
    assert not objections, "\n".join(objections)
