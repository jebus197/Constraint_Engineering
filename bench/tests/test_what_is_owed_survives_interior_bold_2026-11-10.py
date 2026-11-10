"""A derived WHAT-IS-OWED statement survives interior bold, and a bold
sentence in prose cannot fake the marker.

★ MEASURED ON THE LIVE LIST, 2026-11-10, free panel. Entry B103's owed
statement carries `**1.35 times that stated limit**` mid-sentence. The
pre-repair capture in `scripts/build_decisions_file_2026-11-07.py` ended at
the FIRST interior `**` after 30 characters, so the derivation returned
"...taking it to about 891 s --" with NO ellipsis -- a fragment presented as
complete under the heading *what is still owed*, in the file he decides from,
with the operative clause "which gives way is yours" silently dropped. Three
sibling defects shared the mechanism: a statement under 30 characters dragged
the NEXT heading's text in under the owed heading; `re.I` let a lowercase
bold sentence beginning "what is owed..." act as a marker; and last-marker-
wins then preferred such a fake over a real earlier marker.
"""
import importlib.util
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def bdf():
    sys.path.insert(0, str(REPO / "scripts"))
    spec = importlib.util.spec_from_file_location(
        "bdf_owed_guard", REPO / "scripts" / "build_decisions_file_2026-11-07.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["bdf_owed_guard"] = mod
    spec.loader.exec_module(mod)
    return mod


class TestInteriorBoldIsNotAStop:

    def test_the_b103_shape_keeps_its_operative_clause(self, bdf):
        """The live defect, reduced: emphasis mid-sentence is not the end."""
        got = bdf.derive_still_owed(
            "**B103. T.** **WHAT IS OWED TO YOU.** The gate needs a decision "
            "taking it to 891 s -- **1.35 times the limit**, and which gives "
            "way is yours. **3 OPTIONS.** (a) all. (b) none.")
        assert "which gives way is yours" in got, repr(got)
        assert "3 OPTIONS" not in got, repr(got)

    def test_a_short_statement_does_not_swallow_the_next_heading(self, bdf):
        got = bdf.derive_still_owed(
            "**B1. T.** **WHAT IS STILL OWED:** a test. "
            "**DO NOT DELETE THE LEDGER.** The ledger holds 52 rows.")
        assert got == "a test.", repr(got)

    def test_a_bold_prose_sentence_cannot_fake_the_marker(self, bdf):
        """`re.I` admitted this; the marker is the authors' capitals."""
        got = bdf.derive_still_owed(
            "**B1. T.** The note said **what is owed is recorded in the "
            "entry and nothing more needs saying here today**. "
            "**THE REAL OWED MARKER NEVER EXISTED.**")
        assert got == "", repr(got)

    def test_a_fake_marker_cannot_beat_a_real_earlier_one(self, bdf):
        got = bdf.derive_still_owed(
            "**B1. T.** **WHAT IS STILL OWED:** his ruling on the tier "
            "split, which is a budget question. Later prose quotes a file: "
            "**what is owed is recorded in the entry and nothing more "
            "follows from it**. tail text.")
        assert "tier split" in got, repr(got)

    def test_no_sentence_punctuation_still_derives_via_the_fallback(self, bdf):
        """The 2 committed cut tests use punctuation-less bodies; the
        fragment capture remains their path and no entry derives less."""
        body = "**B1. T.** **WHAT IS STILL OWED:** " + ("word " * 200) + "**E**"
        got = bdf.derive_still_owed(body)
        assert got and len(got) <= bdf.STILL_OWED_MAX_CHARS + 8

    def test_the_live_b103_entry_derives_its_ask(self, bdf):
        """Against the real list -- skipped where the entry has moved on."""
        sys.path.insert(0, str(REPO / "scripts"))
        import task_list_markers as tlm
        ent = {e.ident: e.text for e in tlm.parse_entries()}.get("B103")
        if not ent or "WHAT IS OWED TO YOU" not in ent.replace("\n", " "):
            pytest.skip("B103 no longer carries the marker")
        got = bdf.derive_still_owed(ent)
        assert got.rstrip().endswith((".", "!", "?", "...")), repr(got[-60:])
        assert not got.rstrip().endswith("s --"), repr(got[-60:])


# ─────────────────────────────────────────────────────────────────────────────
# THE SEAT'S OWN PRODUCER MUST BE EXECUTED BY SOMETHING — see the sibling note
# in `test_what_is_still_owed_is_quoted_whole_2026-11-10.py`. The commit gate
# refused the adoption of both seat producers because no test ran either.
#
# ★ AND THIS ONE ALSO FAILED THIS PROJECT'S `--help` RULE ON ADOPTION. It had
# no argument parsing, so `--help` ran the whole measurement. The seat's work
# is kept in full; only the flag is answered, and both halves are asserted
# here so the repair cannot be undone silently.
# ─────────────────────────────────────────────────────────────────────────────

def test_the_seats_producer_runs_in_this_tree():
    import pathlib
    import subprocess
    import sys as _sys
    repo = pathlib.Path(__file__).resolve().parents[2]
    prod = repo / "scripts" / "a_true_sub_claim_admits_an_unexamined_fix_2026-11-10.py"
    assert prod.is_file(), f"the adopted producer is absent: {prod}"
    r = subprocess.run([_sys.executable, str(prod)], capture_output=True,
                       text=True, timeout=300, cwd=str(repo))
    assert r.returncode == 0, r.stdout[-1500:] + r.stderr[-600:]
    assert r.stdout.strip(), "the producer printed nothing"


def test_the_seats_producer_answers_help_for_free():
    import pathlib
    import subprocess
    import sys as _sys
    import time as _time
    repo = pathlib.Path(__file__).resolve().parents[2]
    prod = repo / "scripts" / "a_true_sub_claim_admits_an_unexamined_fix_2026-11-10.py"
    t0 = _time.monotonic()
    r = subprocess.run([_sys.executable, str(prod), "--help"],
                       capture_output=True, text=True, timeout=30,
                       cwd=str(repo))
    assert r.returncode == 0, r.stderr[-600:]
    assert "usage" in r.stdout.lower(), (
        "the flag was ignored, so --help ran the measurement")
    assert _time.monotonic() - t0 < 5.0, "a --help must never cost minutes"
