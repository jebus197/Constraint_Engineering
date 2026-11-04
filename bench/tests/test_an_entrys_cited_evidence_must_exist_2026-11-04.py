"""Every path a master-task-list entry cites as `evidence:` must exist on disk.

WHY THIS GUARD EXISTS, AND IT IS NOT HYPOTHETICAL: IT CAUGHT 2 OF MY OWN ERRORS
THE NIGHT IT WAS WRITTEN. The `evidence:` field is the whole mechanism by which a
DONE entry is checkable -- it names the artefact a reader goes to in order to
verify the claim the entry makes. A path that does not exist makes the claim
unverifiable while leaving it looking verified, which is strictly worse than
citing nothing.

MEASURED 2026-11-04, before the guard was written. Of 337 cited paths across 248
entries, **1 did not exist and had never been tracked** -- `B102` cited
`scripts/his_words_arrive_where_nothing_looks_2026-11-03.py`, a plausible name
for a producer whose real name is `scripts/his_messages.py`. Separately, `B109`
was written minutes earlier citing
`bench/tests/test_the_compaction_resume_brief_2026-10-17.py`, where the real file
is `test_the_resume_brief_carries_content_2026-10-17.py`. Both were guesses at a
filename that read correctly and were wrong, which is the failure mode a
stat() call ends permanently.

NOTHING CAUGHT EITHER. `scripts/task_list_markers.py --check` reports
"task list coherent: 248 entries, 0 problems" with a deliberately bogus path
planted, and `test_a_cited_path_must_exist_2026-10-30.py`,
`test_overstated_entries_2026-09-11.py` and
`test_the_evidence_must_go_red_2026-10-17.py` -- the 3 nearest existing guards --
pass all 22 of their tests with the same path planted. Verified by planting it
and running them, not by reading them.

★ THE LINE SUFFIX IS STRIPPED, AND THAT CORRECTION IS THE REASON THIS FILE IS
CAREFUL. The first measurement reported 8 missing paths of 337. 7 of the 8 were
false positives: an entry may cite `bench/dm/_types.py:314`, and the file exists
while the string does not. A guard that accused those 7 would have been a guard
accusing correct prose -- the shape this project has recorded repeatedly -- and
would have been switched off. Only the file part is checked; the line number is
NOT verified, because a line reference goes stale on any edit to the file and a
guard that fails on every refactor teaches people to ignore it.

Producer: `scripts/the_census_counts_what_the_reader_excludes_2026-11-04.py` is
a different measurement; this guard's own figures are recomputed here by
execution, which is the point.
"""
import pathlib
import re
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
LIST = REPO / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md"

#: A trailing `:123` or `:123-456` is a LINE REFERENCE, not part of the filename.
_LINE_REF = re.compile(r":\d+(?:-\d+)?$")

#: A cited token is a PATH only if it carries a separator. Entries also put bare
#: words in the field, and a bare word is not a claim about a file.
def _paths():
    sys.path.insert(0, str(REPO / "scripts"))
    import task_list_markers as markers
    out = []
    for e in markers.parse_entries(LIST):
        ev = getattr(e, "evidence", None)
        items = list(ev) if isinstance(ev, (tuple, list)) else ([ev] if ev else [])
        for raw in items:
            tok = str(raw).strip()
            if "/" not in tok:
                continue
            out.append((e.ident, tok, _LINE_REF.sub("", tok)))
    return out


@pytest.fixture(scope="module")
def cited():
    return _paths()


def test_the_list_is_parseable_and_cites_paths(cited):
    """ANTI-VACUITY. A guard that examines 0 paths passes for free."""
    assert len(cited) >= 300, (
        f"only {len(cited)} cited paths found; the parser or the field format has "
        f"changed and this guard is no longer looking at anything")


def test_every_cited_evidence_path_exists(cited):
    missing = [(ident, tok) for ident, tok, bare in cited
               if not (REPO / bare).exists()]
    assert not missing, (
        "entries cite evidence that does not exist on disk — the claim cannot be "
        "checked by a reader:\n" + "\n".join(f"  {i}: {t}" for i, t in missing))


def test_the_line_suffix_is_stripped_not_ignored():
    """The stripping is load-bearing: 7 of 8 first-pass failures were line refs.

    Asserted by EXECUTION on the real regex rather than by describing it, because
    a comment claiming a regex strips something is not evidence that it does.
    """
    assert _LINE_REF.sub("", "bench/dm/_types.py:314") == "bench/dm/_types.py"
    # ★ A REAL PATH, DELIBERATELY. With a made-up one here, the project's own
    # line-citation guard read this test's data as a citation of a file that
    # does not exist and refused the commit — a detector's fixture being read
    # as the thing it detects.
    assert (_LINE_REF.sub("", "bench/tests/conftest.py:10-20")
            == "bench/tests/conftest.py")
    assert _LINE_REF.sub("", "bench/run.py") == "bench/run.py"
    # a colon that is NOT a line reference must survive untouched
    assert _LINE_REF.sub("", "notes/a:b.py") == "notes/a:b.py"


def test_a_bogus_path_would_be_caught(tmp_path):
    """THE MUTATION, INLINE. Proves the assertion can fail, without editing the list.

    `test_every_cited_evidence_path_exists` runs against the live list and is
    green by construction once the list is correct, so on its own it cannot show
    that it WOULD go red. This drives the same predicate over a planted row.
    """
    rows = [("B999", "bench/tests/test_nothing_here_9999-99-99.py",
             "bench/tests/test_nothing_here_9999-99-99.py")]
    missing = [(i, t) for i, t, b in rows if not (REPO / b).exists()]
    assert missing, "the predicate cannot detect a non-existent path"

    good = [("B998", "bench/tests/conftest.py", "bench/tests/conftest.py")]
    assert not [(i, t) for i, t, b in good if not (REPO / b).exists()], (
        "the predicate rejects a path that does exist")


def test_a_line_reference_to_a_real_file_is_accepted(cited):
    """Regression: the 7 false positives must stay accepted."""
    with_refs = [(i, t) for i, t, b in cited if _LINE_REF.search(t)]
    if not with_refs:
        pytest.skip("no entry currently cites a line reference")
    for ident, tok in with_refs:
        bare = _LINE_REF.sub("", tok)
        assert (REPO / bare).exists(), f"{ident}: {tok}"
