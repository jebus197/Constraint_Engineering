"""The verdict census and the reader must agree, and the agreement must be won the RIGHT way.

THE DEFECT THIS GUARDS, found 2026-11-04. `claim_a_naive_grep_is_blind_to_some_of_them`
counted annotations over files chosen by `is_a_response_file` -- the BROAD READABILITY
predicate -- while `annotations()` yields them from `is_one_of_his_annotated_responses`,
which is strictly narrower. `scripts/cdsfl_recover.py` quotes the census in the FIRST READ
banner, so every session was told the founder had written 1,953 '#' verdicts of which 1,688
were invisible to grep. He wrote 839, of which 583 are. 1,114 of 1,953 -- 0.570405, Wilson
[0.548333, 0.592199] -- was not his writing, 1,103 of it from an 11 MiB PNG wearing a `.md`
extension (780) and a `.zip` (323).

THERE ARE 2 WAYS TO MAKE THE 2 FIGURES AGREE AND ONLY 1 OF THEM IS CORRECT. Narrowing the
ANNOTATION counts to his files is the fix. Narrowing READABILITY would also make them agree,
and would be a regression: the broad predicate feeds `binaries_wearing_a_text_extension` and
`unreadable_but_annotated`, the module's gap detectors, so narrowing it makes an unparseable
file stop being reported as a gap. This file therefore asserts BOTH the agreement AND that
the readability denominator stayed wide, so a future repair cannot satisfy it the wrong way.

THE ANTI-VACUITY CASE IS SYNTHETIC ON PURPOSE. Asserting a non-zero residue over the live
folder would turn this guard red the day he deletes the PNG, and a flaky guard is worse than
a red one. The mechanism is exercised against a temporary folder whose contents are known.

Producer: `scripts/the_census_counts_what_the_reader_excludes_2026-11-04.py`.
"""
import importlib.util
import pathlib
import re

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
READER = REPO / "scripts" / "read_founder_responses_2026-10-11.py"


def _load():
    spec = importlib.util.spec_from_file_location("_rfr_census", READER)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def m():
    return _load()


@pytest.fixture(scope="module")
def census(m):
    return m.claim_a_naive_grep_is_blind_to_some_of_them()


@pytest.fixture(scope="module")
def his(m):
    """`annotations()` costs ~2.5 s over the live corpus and 4 tests want it.

    MODULE-SCOPED FOR COST, NOT CONVENIENCE. The commit gate's own header
    already carries a cost limit this project has measured it exceeding, so a
    guard that recomputes the same corpus 4 times is a cost nobody chose.
    """
    return m.annotations()


@pytest.fixture(scope="module")
def banner():
    """The FIRST READ line, computed ONCE.

    `_responses_label()` shells out to the reader with `--json`, so it costs
    ~12 s a call and 2 tests need it. Both assertions still run against the
    real label; only the subprocess is shared.
    """
    spec = importlib.util.spec_from_file_location(
        "_rec_census", REPO / "scripts" / "cdsfl_recover.py")
    rec = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rec)
    return rec._responses_label()


# ----------------------------------------------------------------- the invariant

def test_the_census_total_equals_what_the_reader_yields(census, his):
    """THE BROKEN INVARIANT. A producer and a consumer that disagree is the defect
    `execute-do-not-grep` names, so this CALLS both and compares outputs."""
    assert census["annotations_total"] == len(his)


def test_the_blind_count_cannot_exceed_the_total(census):
    assert census["annotations_in_blind_files"] <= census["annotations_total"]


def test_the_annotated_file_count_equals_the_reader_s_file_set(census, his):
    files = {a["file"] for a in his}
    assert census["annotated_files"] == len(files)


# ------------------------------------------- the agreement was won the right way

def test_the_readability_denominator_stayed_wide(m, census):
    """A future repair must not make the figures agree by narrowing READABILITY."""
    broad = [p for p in m.RESPONSES.glob("*") if m.is_a_response_file(p)]
    assert census["files"] == len(broad)
    narrow = [p for p in m.RESPONSES.glob("*")
              if m.is_one_of_his_annotated_responses(p)]
    assert len(broad) > len(narrow), (
        "readability has been narrowed to the his-writing set; the gap detectors "
        "`binaries_wearing_a_text_extension` and `unreadable_but_annotated` depend "
        "on it being wider")


def test_the_gap_detectors_still_use_the_broad_predicate(m):
    """Both read the same folder through readability, not through his-writing."""
    src = READER.read_text(encoding="utf-8")
    for fn in ("binaries_wearing_a_text_extension", "unreadable_but_annotated"):
        body = src.split(f"def {fn}(")[1].split("\ndef ")[0]
        assert "is_a_response_file" in body, fn
        assert "is_one_of_his_annotated_responses" not in body, fn


# ------------------------------------------------------- the residue is reported

def test_the_residue_is_named_not_merely_counted(census):
    named = sum(r["annotations"] for r in census["excluded_files"])
    assert census["annotations_excluded_as_not_his"] == named


def test_every_named_residue_entry_carries_its_evidence(census):
    for r in census["excluded_files"]:
        assert set(r) >= {"file", "annotations", "bytes", "suffix"}
        assert r["annotations"] > 0
        assert isinstance(r["file"], str) and r["file"]


def test_nothing_the_broad_pass_saw_is_silently_dropped(m, census):
    """his + residue == what the broad pass would have counted. Exact, by execution."""
    broad_total = 0
    for p in sorted(m.RESPONSES.glob("*")):
        if not m.is_a_response_file(p):
            continue
        broad_total += len(m._annotations_in(p))
    assert (census["annotations_total"]
            + census["annotations_excluded_as_not_his"]) == broad_total


# --------------------------------------------------- the mechanism, synthetically

def _plant(folder: pathlib.Path):
    """A folder holding 1 genuine annotated text file and 3 impostors."""
    (folder / "real_report_2026-01-01.txt").write_text(
        "SECTION 1.\nsome report prose here that is long enough\n"
        "# this is his verdict and it is conversational prose, at length\n"
        "# a second verdict from him, also prose and also long enough to count\n",
        encoding="utf-8")
    # A PNG wearing a .md extension, with markers after the signature.
    # ★ THE MARKERS MUST BE PROSE-SHAPED, with sentence punctuation. A `.md`
    # file's heading-shaped lines are filtered by `_looks_like_a_markdown_
    # heading`, so an earlier version of this fixture yielded 0 markers and the
    # impostor never reached the gate at all -- the test failed for a reason
    # that had nothing to do with the defect. His real annotations are
    # conversational prose, which is exactly why they survive that filter.
    png = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64
    for i in range(40):
        png += (f"\n# binary noise line {i}, not his writing, "
                f"and it ends in a stop.\n").encode()
    (folder / "screenshot_wearing_markdown.md").write_bytes(png)
    (folder / "archive.zip").write_bytes(
        b"PK\x03\x04" + b"\n# compressed noise masquerading as a verdict line\n" * 12)
    (folder / "notes.docx").write_bytes(
        b"PK\x03\x04" + b"\n# a foreign document, not one of his responses\n" * 5)


def test_the_census_excludes_an_impostor_and_names_it(m, tmp_path, monkeypatch):
    """THE ANTI-VACUITY CASE. Without the narrow gate the impostors are counted."""
    folder = tmp_path / "Responses"
    folder.mkdir()
    _plant(folder)
    monkeypatch.setattr(m, "RESPONSES", folder)

    c = m.claim_a_naive_grep_is_blind_to_some_of_them()
    assert c["files"] == 4, "all 4 are READABLE and the denominator must say so"
    assert c["annotated_files"] == 1, "only 1 of the 4 is his writing"
    assert c["annotations_total"] == len(m.annotations())
    assert c["annotations_total"] == 2
    assert c["annotations_excluded_as_not_his"] > 0
    named = {r["file"] for r in c["excluded_files"]}
    assert "screenshot_wearing_markdown.md" in named
    assert "archive.zip" in named


def test_the_impostors_would_dominate_without_the_gate(m, tmp_path, monkeypatch):
    """Quantifies what the gate prevents, so the guard is not merely structural."""
    folder = tmp_path / "Responses"
    folder.mkdir()
    _plant(folder)
    monkeypatch.setattr(m, "RESPONSES", folder)

    c = m.claim_a_naive_grep_is_blind_to_some_of_them()
    broad = c["annotations_total"] + c["annotations_excluded_as_not_his"]
    assert broad > 3 * c["annotations_total"], (
        f"the impostors contribute {c['annotations_excluded_as_not_his']} against "
        f"his {c['annotations_total']}; if this ratio is near 1 the fixture no "
        f"longer exercises the defect")


# ------------------------------------------------------------------- the banner

def test_the_first_read_banner_quotes_his_count(banner, his):
    """The FIRST READ line is where the wrong figure was actually read."""
    label = banner
    if "folder not present" in label:
        pytest.skip("Responses folder absent on this machine")
    n = re.search(r"—\s*(\d+)\s*'#' verdicts", label)
    assert n, f"banner shape changed, cannot locate the count: {label[:120]}"
    assert int(n.group(1)) == len(his)


def test_the_banner_names_the_exclusion_when_there_is_one(banner, census):
    label = banner
    if "folder not present" in label:
        pytest.skip("Responses folder absent on this machine")
    if census["annotations_excluded_as_not_his"]:
        assert "NOT his writing" in label
        assert str(census["annotations_excluded_as_not_his"]) in label
    else:
        assert "NOT his writing" not in label


# ------------------------------------------------------------------ the producer

def test_the_producer_exists_and_is_reachable():
    p = REPO / "scripts" / "the_census_counts_what_the_reader_excludes_2026-11-04.py"
    assert p.is_file()
    src = p.read_text(encoding="utf-8")
    assert "parse_args" in src, "a script with no usage line is unreachable"
    for step in ("step_1_the_predicates_nest", "step_2_the_decomposition",
                 "step_3_the_share", "step_4_the_blind_figure"):
        assert f"def {step}" in src and f"{step}(m)" in src, step
