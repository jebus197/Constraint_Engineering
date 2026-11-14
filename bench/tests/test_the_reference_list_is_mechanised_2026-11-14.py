"""A generated report's reference list must be derived, and an omission must be loud.

★ HIS INSTRUCTION, verbatim: *"There is a very strong argument that any report
generated for researchers should carry a list of accessed references at the end
of it... I don't trust the models exactly to do this themselves, so perhaps this
could be mechanised."*

★ AND THE DEFECT THIS CLOSES IS AN ADDITION NOTHING REACHED. The layer-3
researcher encoding was built on 2026-11-13. Measured 2026-11-14: **0 code paths
in `bench/`, `scripts/` or `hooks/` read `bench/directives/researchers/`** --
every match was prose in an unrelated file, and the composer has no layer-3
loader. Under `additive-standard`'s symmetric form that is not additive, and the
project has 11 confirmed defects of the same shape. The reference list is the
consumer he had already named.

★ THE 3 PATHS THAT MATTER ARE THE FAILING ONES, and they are exercised on real
temporary encodings rather than asserted:

  * a named encoding ABSENT from disk must be reported MISSING, never omitted;
  * a confirmation older than the encoding's OWN backstop must be OVERDUE;
  * a domain declaring `needs_confirmation = false` must NOT be overdue, or 2
    of the founder's 3 domains become permanent false alarms.

The passing input cannot test any of those, which is why each gets a fixture
that triggers it.

EXECUTES the producer against constructed encodings.
"""
from __future__ import annotations

import datetime as dt
import importlib.util
import pathlib
import sys
import tempfile

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent.parent


def _producer():
    spec = importlib.util.spec_from_file_location(
        "ref_list", REPO / "scripts" / "researcher_reference_list_2026-11-14.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules["ref_list"] = m
    spec.loader.exec_module(m)
    return m


P = _producer()

STD_TEMPLATE = '''schema_version = "1.0"
researcher = "probe"
[domains]
primary = ["software"]
[domains.software]
encoding = "{enc}"
reason = "a probe"
severity_scale = "CVSS v4.0 base score"
critical_level = "High (7.0)"
'''

CONF_TEMPLATE = '''schema_version = "1.0"
researcher = "probe"
[policy]
backstop_days = {backstop}
[confirmed."CVSS v4.0"]
standard = "CVSS v4.0 base score"
publisher = "FIRST"
last_confirmed = "{last}"
{extra}'''


def _encoding(tmp: pathlib.Path, enc_rel: str, backstop: int = 14,
              last: str = "2026-11-12", extra: str = "") -> pathlib.Path:
    base = tmp / "probe"
    base.mkdir(parents=True, exist_ok=True)
    (base / "standards.toml").write_text(STD_TEMPLATE.format(enc=enc_rel), encoding="utf-8")
    (base / "confirmations.toml").write_text(
        CONF_TEMPLATE.format(backstop=backstop, last=last, extra=extra), encoding="utf-8")
    return base


@pytest.fixture
def probe(monkeypatch):
    tmp = pathlib.Path(tempfile.mkdtemp())
    monkeypatch.setattr(P, "RESEARCHERS", tmp)
    return tmp


# ── the real encoding ─────────────────────────────────────────────────────

def test_the_founders_encoding_is_found_and_read():
    """NON-VACUITY ON THE LIVE FILES: a pass on fixtures alone proves nothing."""
    who = P.researchers()
    assert "founder" in who, f"the founder's layer-3 encoding is not discoverable: {who}"
    ref = P.reference_list("founder")
    assert ref["encodings"], "0 domain encodings read, so a clean report would be empty"
    assert not ref["missing"], ref["missing"]
    for e in ref["encodings"]:
        assert (REPO / e["path"]).is_file()
        assert len(e["sha256"]) == 16 and e["bytes"] > 0


def test_the_digest_is_of_the_bytes_actually_read():
    """A report checked against a digest must be checkable, so the digest must
    be of the file and not of its name."""
    import hashlib
    ref = P.reference_list("founder")
    e = ref["encodings"][0]
    actual = hashlib.sha256((REPO / e["path"]).read_bytes()).hexdigest()[:16]
    assert e["sha256"] == actual


# ── the failing paths ─────────────────────────────────────────────────────

def test_a_named_encoding_absent_from_disk_is_reported_MISSING(probe):
    """★ THE LOUD-OMISSION PROPERTY. The point of mechanising this is that a
    gap becomes visible; silently dropping the row would be worse than prose."""
    _encoding(probe, "bench/directives/software/does_not_exist_9fa3.txt")
    ref = P.reference_list("probe")
    assert ref["missing"], "an absent encoding was silently omitted from the list"
    assert ref["missing"][0]["path"].endswith("does_not_exist_9fa3.txt")
    assert "absent from disk" in ref["missing"][0]["why"]
    assert "MISSING" in P.render(ref)


def test_an_encoding_naming_no_file_at_all_is_also_MISSING(probe):
    base = _encoding(probe, "x")
    (base / "standards.toml").write_text(
        'schema_version = "1.0"\n[domains]\nprimary = ["software"]\n'
        '[domains.software]\nreason = "names no file"\n', encoding="utf-8")
    ref = P.reference_list("probe")
    assert ref["missing"] and "names no file" in ref["missing"][0]["why"]


def test_a_confirmation_older_than_the_backstop_is_OVERDUE(probe):
    _encoding(probe, "bench/directives/software/software_general.txt",
              backstop=14, last="2026-10-01")
    ref = P.reference_list("probe", today=dt.date(2026, 11, 14))
    assert ref["overdue"], "a 44-day-old confirmation was not reported overdue"
    assert ref["overdue"][0]["age_days"] == 44
    assert "OVERDUE" in P.render(ref)


def test_a_confirmation_inside_the_backstop_is_not_overdue(probe):
    _encoding(probe, "bench/directives/software/software_general.txt",
              backstop=14, last="2026-11-12")
    ref = P.reference_list("probe", today=dt.date(2026, 11, 14))
    assert not ref["overdue"], ref["overdue"]


def test_the_backstop_is_read_from_the_file_and_not_typed_in_the_script(probe):
    """Changing the policy must change the verdict, or the policy is decoration."""
    _encoding(probe, "bench/directives/software/software_general.txt",
              backstop=90, last="2026-10-01")
    ref = P.reference_list("probe", today=dt.date(2026, 11, 14))
    assert ref["backstop_days"] == 90
    assert not ref["overdue"], "a 90-day backstop did not absolve a 44-day-old check"


def test_a_scale_less_domain_is_never_reported_overdue(probe):
    """★ 2 of the founder's 3 domains declare no scale. Reporting those as
    overdue would manufacture permanent false alarms out of a recorded fact."""
    _encoding(probe, "bench/directives/software/software_general.txt",
              backstop=1, last="2020-01-01",
              extra='\n[confirmed."mathematics: none"]\nstandard = "none"\n'
                    'reason = "no recognised consequence scale"\n'
                    'needs_confirmation = false\n')
    ref = P.reference_list("probe", today=dt.date(2026, 11, 14))
    keys = [o["key"] for o in ref["overdue"]]
    assert "mathematics: none" not in keys, (
        "a domain declaring needs_confirmation = false was reported overdue")


def test_a_standard_needing_confirmation_with_no_date_is_overdue(probe):
    _encoding(probe, "bench/directives/software/software_general.txt")
    base = probe / "probe"
    (base / "confirmations.toml").write_text(
        'schema_version = "1.0"\n[policy]\nbackstop_days = 14\n'
        '[confirmed."GHS"]\nstandard = "GHS"\n', encoding="utf-8")
    ref = P.reference_list("probe", today=dt.date(2026, 11, 14))
    assert ref["overdue"] and "carries no date" in ref["overdue"][0]["why"]


# ── the contract ──────────────────────────────────────────────────────────

def test_an_unknown_researcher_raises_rather_than_returning_empty(probe):
    with pytest.raises(FileNotFoundError):
        P.reference_list("nobody")


def test_the_rendered_block_names_its_own_producer():
    """A reference list that cannot be re-derived is a claim about evidence."""
    out = P.render(P.reference_list("founder"))
    assert "researcher_reference_list_2026-11-14.py" in out
    assert "References accessed" in out


def test_the_producer_exits_zero():
    assert P.main([]) == 0


# ── the wiring, which is the whole point ──────────────────────────────────

def _generator():
    spec = importlib.util.spec_from_file_location(
        "ref_gen", REPO / "scripts" / "build_decisions_file_2026-11-07.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules["ref_gen"] = m
    spec.loader.exec_module(m)
    return m


def test_the_generated_report_actually_carries_the_list():
    """★ ADDED BECAUSE THE MUTATION HARNESS CAUGHT ITS ABSENCE, and it is the
    most important test in this file.

    Every test above exercises the PRODUCER. Disabling the generator's call to
    it left all of them green -- so the guard would not have noticed layer 3
    losing its only caller, which is the precise defect this work exists to
    close. A producer with no consumer is the addition `additive-standard`
    forbids, and 11 confirmed defects in this project are that shape.
    """
    gen = _generator()
    mrb, rows = gen.collect()
    full = gen.render(mrb, rows, spoken=False, detail=True)
    assert "References accessed" in full, (
        "the generated report no longer carries a reference list, so the "
        "layer-3 encoding has no caller again")
    assert "researcher_reference_list_2026-11-14.py" in full, (
        "the list is present but does not name its producer, so a reader "
        "cannot re-derive it")


def test_the_list_names_the_encodings_actually_read_in_the_report():
    """The report's list must match what the producer returns, not a summary."""
    gen = _generator()
    mrb, rows = gen.collect()
    full = gen.render(mrb, rows, spoken=False, detail=True)
    ref = P.reference_list("founder")
    for e in ref["encodings"]:
        assert e["path"] in full, f"{e['path']} was read but is absent from the report"
        assert e["sha256"] in full, f"{e['path']}'s digest is absent from the report"


@pytest.mark.parametrize("token,why", [
    ("`", "backticks are read aloud as noise"),
    ("\u2014", "an em-dash is not spoken"),
    ("*", "an asterisk is read aloud or skipped awkwardly"),
    ("|", "a pipe is not speakable"),
])
def test_the_spoken_render_carries_no_markup(token, why):
    """★ ADDED AFTER THE COMMIT GATE REFUSED, 2026-11-14, AND THE DEFECT WAS
    MINE. The first wiring appended the MARKDOWN block to both renders, and 4
    guards in `test_the_decisions_file_is_generated_2026-11-07.py` caught it at
    once. This file had 15 tests and not 1 of them asked whether the spoken
    output was speakable, so the gate found what the guard did not."""
    out = P.render_spoken(P.reference_list("founder"))
    assert token not in out, f"{why}: {token!r} is in the spoken reference list"


def test_the_spoken_render_carries_no_heading_hash_or_file_path():
    import re as _re
    out = P.render_spoken(P.reference_list("founder"))
    assert not _re.search(r"^#", out, _re.M), "a heading hash is read aloud"
    assert not _re.search(r"\b[\w./-]+\.(?:py|md|txt|toml|json)\b", out), (
        "a file path survived into the spoken render; the paths belong in the "
        "markdown companion, which the spoken text says so")


def test_the_spoken_render_still_carries_the_substance():
    """Speakable must not mean empty: the domains and the staleness must survive."""
    ref = P.reference_list("founder")
    out = P.render_spoken(ref)
    assert "REFERENCES ACCESSED" in out
    for e in ref["encodings"]:
        assert e["domain"].replace("_", " ") in out, (
            f"{e['domain']} was read and is not named in the spoken render")
    assert str(ref["backstop_days"]) in out, "the backstop is not stated"


def test_the_generator_gives_each_audience_its_own_render():
    gen = _generator()
    mrb, rows = gen.collect()
    md = gen.render(mrb, rows, spoken=False, detail=True)
    sp = gen.render(mrb, rows, spoken=True, detail=True)
    assert "## References accessed" in md, "the markdown lost its heading"
    assert "REFERENCES ACCESSED" in sp, "the spoken copy lost its reference list"
    assert "## References accessed" not in sp, (
        "the markdown heading reached the spoken copy, which is the defect the "
        "gate refused on 2026-11-14")


def test_his_short_copy_is_left_alone():
    """★ HIS OWN COMPLAINT BOUNDS THIS. He called 22,902 words an almost
    impossible workload, and the index-alone render exists because of it.
    Appending to that copy would undo the repair it came from."""
    gen = _generator()
    mrb, rows = gen.collect()
    short = gen.render(mrb, rows, spoken=True, detail=False)
    assert "References accessed" not in short, (
        "the reference list reached his short copy, which exists because he "
        "said the full file was an impossible workload")
