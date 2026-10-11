"""The founder's own verdicts must stay readable, and the reader must fail loudly if they stop.

WHAT THIS GUARDS, and what it cost to learn. On 2026-10-11 `grep -E "^#"` returned nothing on
`Responses/Division_Count_And_Relegation_Panel_2026-10-08.txt` and the silence was reported to
the founder as "your verdicts are gone". They were never gone: the file is ISO-8859 with CR-only
line terminators, so grep calls it binary and exits 1 saying nothing. 221 of his 691 annotations
(0.3198) sit in files with that shape.

EVERY ASSERTION HERE CALLS THE READER. A source-text assertion would only prove the module
describes itself consistently (`execute-do-not-grep`).
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
READER = REPO / "scripts" / "read_founder_responses_2026-10-11.py"
RECOVER = REPO / "scripts" / "cdsfl_recover.py"


def _load():
    spec = importlib.util.spec_from_file_location("rfr_guard", READER)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["rfr_guard"] = mod
    spec.loader.exec_module(mod)
    return mod


class TestTheReaderSeesWhatGrepCannot:
    def test_the_reader_exists(self):
        assert READER.is_file(), f"the founder-response reader is missing: {READER}"

    def test_it_decodes_a_cr_only_iso8859_file_that_grep_calls_binary(self, tmp_path):
        """THE EXACT SHAPE OF THE FAILURE, reconstructed: Mac-classic line endings plus a
        high byte from a smart quote. grep exits 1 on this; the reader must not."""
        m = _load()
        f = tmp_path / "fake_response.txt"
        body = ("A heading\r"
                "# I don\x92t know if I said never. That could lock a model in place.\r"
                "More prose\r")
        f.write_bytes(body.encode("iso-8859-1"))
        g = subprocess.run(["grep", "-cE", "^[[:space:]]*#", str(f)],
                           capture_output=True, text=True)
        assert g.returncode != 0 or (g.stdout or "0").strip() == "0", (
            "the fixture no longer reproduces the defect; grep can see it, so this test is blind")
        text = m.read_any(f)
        hits = [l for l in text.splitlines() if l.strip().startswith("#")]
        assert len(hits) == 1, f"the reader missed a CR-only ISO-8859 annotation: {text!r}"
        assert "lock a model in place" in hits[0]

    def test_an_undecodable_byte_costs_one_character_not_the_file(self, tmp_path):
        m = _load()
        f = tmp_path / "bad.txt"
        f.write_bytes(b"# first\r\xff\xfe garbage \r# second\r")
        text = m.read_any(f)
        hits = [l for l in text.splitlines() if l.strip().startswith("#")]
        assert len(hits) == 2, f"a bad byte swallowed an annotation: {text!r}"

    def test_dotfiles_and_word_lock_files_are_not_response_files(self, tmp_path):
        """The false positive the first run produced: .DS_Store contains a '#' byte."""
        m = _load()
        for name in (".DS_Store", "~$something.txt"):
            p = tmp_path / name
            p.write_bytes(b"# not really an annotation")
            assert not m.is_a_response_file(p), f"{name} must not count as a response file"
        real = tmp_path / "real.txt"
        real.write_bytes(b"# a real one\n")
        assert m.is_a_response_file(real)

    def test_the_coverage_claim_is_computed_not_quoted(self):
        """It must report the live folder, not the numbers in its own docstring."""
        m = _load()
        if not m.RESPONSES.is_dir():
            pytest.skip("the founder's Responses folder is not on this machine")
        c = m.claim_a_naive_grep_is_blind_to_some_of_them()
        for key in ("files", "annotated_files", "annotations_total",
                    "annotations_in_blind_files"):
            assert isinstance(c[key], int) and c[key] >= 0, (key, c[key])
        assert c["annotations_total"] >= c["annotations_in_blind_files"]
        assert c["annotated_files"] <= c["files"]

    def test_verify_mode_exits_clean_on_the_live_folder(self):
        r = subprocess.run([sys.executable, str(READER), "--verify"],
                           capture_output=True, text=True, timeout=300)
        assert r.returncode == 0, (
            f"the reader reports a gap it cannot read:\n{r.stderr[-800:]}")

    def test_help_is_free(self):
        r = subprocess.run([sys.executable, str(READER), "--help"],
                           capture_output=True, text=True, timeout=60)
        assert r.returncode == 0 and "responses" in r.stdout.lower()


class TestTheFolderIsAFirstReadResource:
    def test_recover_names_the_responses_folder(self):
        """His instruction of 2026-10-11. An unregistered resource is one nobody reads."""
        r = subprocess.run([sys.executable, str(RECOVER), "--record-restore"],
                           capture_output=True, text=True, timeout=300)
        assert r.returncode == 0, r.stderr[-500:]
        out = r.stdout
        assert "Developer_Projects/Responses" in out, (
            "FIRST READ does not offer the founder's own response folder")
        assert "ANNOTATED RESPONSES" in out
        assert "NEVER with grep" in out, (
            "the entry must carry the reading instruction, or the next reader repeats the error")

    def test_recover_still_names_the_tracker_it_named_before(self):
        """A regression check: adding an entry must not displace the existing ones."""
        r = subprocess.run([sys.executable, str(RECOVER), "--record-restore"],
                           capture_output=True, text=True, timeout=300)
        assert "CDSFL_Agent_Operational_Plan.md" in r.stdout
        assert "CDSFL_MASTER_TASK_LIST.md" in r.stdout
