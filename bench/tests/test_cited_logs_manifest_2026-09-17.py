"""A8: every cited log path carries a disposition, and the manifest tells the truth.

FOUNDER RULING 2026-09-17: track the files that notes cite so a reader in a fresh
clone can open them, and label the rest.

THE THIRD STATE IS THE ONE NOBODY HAD COUNTED. A cited path is tracked, present
but untracked, or MISSING -- the file was never kept, so it cannot be opened on
any machine, not merely on someone else's. Of 277 note-cited untracked paths,
only 42 existed on disk. (CORRECTED 2026-09-20: this read "283 ... only 52",
which matched neither the manifest as committed nor the manifest with the
self-citation defect repaired. 277 and 42 are read from the repaired manifest
by the one-liner quoted in the panel record, not typed.)

This test re-derives every disposition from the repository and requires the
committed manifest to match. A stale manifest is worse than none, because it
labels a path recoverable when it is not.

REPAIRED 2026-09-17, AND THE FIRST VERSION SHARED THE PRODUCER'S BLIND SPOT.
The producer called every cited path that was not a FILE "missing", and
`test_no_row_claims_missing_when_the_file_is_present` asked the same question,
`is_file()`, so it could not see the defect: 197 of the 339 "missing" rows were
directories that exist, 78 prefixes of existing paths, 14 templates. (The counts
read 194 of 335 until the Section P panel recomputed them, 2026-09-20.) The
producer now has 6 states and this test CALLS its `disposition` and
`cited_paths` rather than restating them. The manifest records the commit it was
built at, so its rows are compared with the citations at that commit exactly.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "experimental_notes" / "evidence" / "cited_logs_manifest_2026-09-17.json"
PRODUCER = REPO / "scripts" / "orphan_citation_era_2026-09-17.py"


@pytest.fixture(scope="module")
def producer():
    import importlib.util
    spec = importlib.util.spec_from_file_location("orphan_era", PRODUCER)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def document() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def manifest(document) -> dict:
    return document["rows"]


@pytest.fixture(scope="module")
def tracked() -> set[str]:
    out = subprocess.run(["git", "ls-files"], cwd=REPO, capture_output=True, text=True).stdout
    return set(out.split())


def test_the_manifest_exists_and_is_not_empty(manifest):
    assert len(manifest) > 100, len(manifest)


def test_every_row_carries_a_known_state(manifest, producer, document):
    assert tuple(document["states"]) == producer.STATES
    for path, row in manifest.items():
        assert row["state"] in producer.STATES, (path, row)
        assert row["cited_by"], path


def test_the_rows_are_exactly_the_citations_at_the_named_commit(document, producer):
    """Not a count typed into a docstring: the producer, run at the commit the
    manifest names, must derive the same set of paths."""
    rev = document["generated_at_commit"]
    derived = producer.cited_paths(rev)
    assert set(document["rows"]) == set(derived), (
        f"manifest only: {sorted(set(document['rows']) - set(derived))[:5]}; "
        f"producer only: {sorted(set(derived) - set(document['rows']))[:5]}")
    wrong = [p for p, r in document["rows"].items() if r["cited_by"] != sorted(derived[p])]
    assert not wrong, wrong[:5]


def test_tracked_rows_agree_with_git_at_the_named_commit(document, producer):
    at = producer.tracked(document["generated_at_commit"])
    wrong = [p for p, r in document["rows"].items() if (r["state"] == "tracked") != (p in at)]
    assert not wrong, wrong[:8]


class TestDisposition:
    """The classifier itself, on a tree whose every state is known."""

    @pytest.fixture
    def tree(self, tmp_path):
        logs = tmp_path / "bench" / "logs"
        (logs / "panel_round9").mkdir(parents=True)
        (logs / "panel_round9" / "cc2.json").write_text("{}")
        (logs / "exp45_v3_20260801").mkdir()
        (logs / "kept.json").write_text("{}")
        return tmp_path

    def test_an_existing_directory_is_never_missing(self, producer, tree):
        """THE CONTROL THE FIRST VERSION LACKED."""
        assert producer.disposition("bench/logs/panel_round9", set(), tree) == "directory"
        assert producer.disposition("bench/logs/panel_round9/", set(), tree) == "directory"

    @pytest.mark.parametrize("path,tracked,state", [
        ("bench/logs/kept.json", {"bench/logs/kept.json"}, "tracked"),
        ("bench/logs/kept.json", set(), "local_only"),
        ("bench/logs/exp55_XX/round_00.json", set(), "template"),
        ("bench/logs/panel_round.../cc2.json", set(), "template"),
        ("bench/logs/exp45_", set(), "prefix"),
        ("bench/logs/never_kept.json", set(), "missing"),
        ("bench/logs/panel_round9/gone.json", set(), "missing"),
    ])
    def test_each_state(self, producer, tree, path, tracked, state):
        assert producer.disposition(path, tracked, tree) == state


def test_no_row_claims_tracked_when_git_does_not_track_it(manifest, tracked):
    """The direction that matters: a false 'tracked' tells a reader to expect
    a file that is not there."""
    wrong = [p for p, r in manifest.items() if r["state"] == "tracked" and p not in tracked]
    assert not wrong, f"manifest says tracked, git does not: {wrong[:8]}"


def test_no_row_claims_missing_when_the_path_is_present(manifest):
    """`exists()`, not `is_file()`: asking only about files is how 197 existing
    directories came to be labelled "never kept"."""
    wrong = [p for p, r in manifest.items() if r["state"] == "missing" and (REPO / p).exists()]
    assert not wrong, f"manifest says missing, the path exists: {wrong[:8]}"


def test_the_note_cited_recoverable_files_are_readable_from_a_clone(manifest):
    """The ruling's action half: what a note cites must be readable from a clone.

    TURNED AROUND 2026-09-17, AND THE FIRST VERSION ENCODED A SUPERSEDED RULING.
    It demanded that note-cited files be TRACKED, which was the A8 ruling as I
    first carried it out -- force-adding 50 files into git. That starved a
    different guard: the resolver's relocation route is exercised by counting
    cited paths found through a MIRROR rather than through git, and putting the
    files in git directly dropped that count from 41 to 5 against a floor of 10.

    The founder then ruled the reversal: mirror the 36 the existing mirror
    script accepts, leave the 14 it rejects tracked, build no new machinery.
    CORRECTED 2026-09-17: `git show --name-status f22e95e` untracks 37 of the
    50 and leaves 13 tracked, so the 36 and 14 above are 1 off each. So
    the property that matters is not "tracked" -- it is READABLE FROM A CLONE,
    which a mirrored copy satisfies exactly as well.
    """
    import subprocess
    from pathlib import Path as _P
    repo = _P(__file__).resolve().parents[2]
    mirrored = set()
    for line in subprocess.run(["git", "ls-files", "experimental_notes/evidence"],
                               cwd=repo, capture_output=True, text=True).stdout.split():
        mirrored.add(_P(line).name)
        mirrored.add(_P(line).name.removesuffix(".txt"))
    stranded = [p for p, r in manifest.items()
                if "NOTE" in r["cited_by"] and r["state"] == "local_only"
                and _P(p).name not in mirrored]
    assert len(stranded) <= 15, (
        f"{len(stranded)} note-cited files are neither tracked nor mirrored, so a "
        f"fresh clone cannot open the evidence those notes cite: {stranded[:8]}")


def test_missing_paths_are_reported_rather_than_hidden(manifest):
    """A citation to a file nobody kept must stay visible, not be quietly dropped."""
    missing = [p for p, r in manifest.items() if r["state"] == "missing"]
    assert missing, "no missing paths at all is implausible; check the extractor"


def test_the_manifest_is_not_an_input_to_its_own_census(producer, document):
    """THE MANIFEST MAY NOT CITE ITSELF (panel Section P, 2026-09-20).

    The manifest is a tracked file under `experimental_notes/`, so every one of
    its row KEYS is a `bench/logs/...` string in a NOTE-classified source. Until
    `EXCLUDE` named it, the producer read them straight back in: 568 of 575 rows
    were "cited by" the manifest, NOTE-labelling read 575 of 575 -- 100% by
    construction -- and 161 rows carried a `cited_by` the manifest had
    manufactured for itself. That is the rule the A8 entry already states, "a
    classifier that reclassifies a path by being written about is measuring the
    writing", and it is the rule `cited_paths` already applies to `bench/logs`.
    """
    rev = document["generated_at_commit"]
    manifest = "experimental_notes/evidence/cited_logs_manifest_2026-09-17.json"
    assert any("cited_logs_manifest" in x for x in producer.EXCLUDE), producer.EXCLUDE

    # CONTROL: the manifest really does name these paths, so this test is not
    # vacuous -- were it not excluded, there would be something to read back in.
    raw = subprocess.run(["git", "grep", "-I", "-o", "-E", producer.CITE.pattern,
                          rev, "--", manifest], cwd=REPO, capture_output=True, text=True).stdout
    self_named = {l.split(":", 2)[2].strip().rstrip(".,);`'\"") for l in raw.splitlines()
                  if l.count(":") >= 2}
    assert len(self_named) > 100, f"control failed: manifest named {len(self_named)} paths"

    # THE GUARD: with the manifest read back in, NOTE is true of every row by
    # construction. It must not be.
    derived = producer.cited_paths(rev)
    note = {p for p, k in derived.items() if "NOTE" in k}
    assert len(note) < len(derived), (
        f"every one of {len(derived)} rows is NOTE-cited -- the manifest is "
        f"being read as a source of citations to itself")
    assert len(note) == sum(1 for r in document["rows"].values() if "NOTE" in r["cited_by"])


def test_every_row_state_rederives_from_the_classifier(document, producer):
    """PANEL ADDITION 2026-09-20 (Section P review of A8). The module docstring
    promises that this file "re-derives every disposition ... and requires the
    committed manifest to match", but until this test only `tracked` (both
    directions) and the missing-vs-`exists()` direction were re-derived. A
    manifest whose 78 `prefix` rows were flipped to "missing" -- the exact
    false statement the 2026-09-17 repair exists to prevent, restated -- passed
    all 16 tests, because a truncated prefix names no path that `exists()`.
    This test closes that: every row's state must equal `disposition()` run
    against the tracked set at the recorded commit and the tree as it stands.
    It is deliberately disk-dependent, like the 2 tests above it: a manifest
    the tree has drifted from is stale, and a stale manifest is worse than none.
    """
    at = producer.tracked(document["generated_at_commit"])
    wrong = [(p, r["state"], producer.disposition(p, at))
             for p, r in document["rows"].items()
             if r["state"] != producer.disposition(p, at)]
    assert not wrong, f"{len(wrong)} rows disagree with re-derivation: {wrong[:8]}"
