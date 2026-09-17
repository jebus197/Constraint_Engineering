"""Task 2.2, panel round 16: the exp53 document checks, run on every machine.

THE GAP. 3 of the 8 tests in `test_falsifier_exp53_zero_plant_2026-09-10.py`
take a `doc` fixture that reads `~/CDSFL_review_targets/current/SW-21-REF-04.md`
and SKIPS when that file is absent: the 44-claim count, the 3 scope phrases, and
the check that ZC-20 does not say what C0005 quotes. With the target unreachable
that file gives "5 passed, 3 skipped", so a clone reads green while the 3
adjudications that rest on the document run nowhere.

THE DOCUMENT IS IN THE REPOSITORY ALREADY. A run record stores the prompt as
sent, and the prompt embeds the whole target. `turns[0].content` of the tracked
`bench/logs/exp53_control_zero_live_20260801T005649Z/round1_codex_20260801T014151Z.json`
carries it after the header
`=== TARGET FILE (REVIEW THIS): ... (24,121 chars) ===`. This file rebuilds the
document from that header's own length, checks the bytes against the sha256
`bench/cdsfl_registry/targets/MANIFEST.md` publishes for
`exp53_zone_controller.md` (parsed from the file, never typed here), and then
CALLS the 3 checks from the original file on the rebuilt text, with no skip. The
checks are the original file's own methods, so the 2 cannot drift apart.

WHY THE HASH IS LOAD-BEARING. Without it a truncated or edited record would
still carry 44 claims and the 3 phrases, and this file would vouch for a
document that is not the one the findings were raised against.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import pathlib
import re
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
RECORD = (ROOT / "bench" / "logs" / "exp53_control_zero_live_20260801T005649Z"
          / "round1_codex_20260801T014151Z.json")
MANIFEST = ROOT / "bench" / "cdsfl_registry" / "targets" / "MANIFEST.md"
ORIGINAL = ROOT / "bench" / "tests" / "test_falsifier_exp53_zero_plant_2026-09-10.py"
MANIFEST_KEY = "exp53_zone_controller.md"

HEADER = re.compile(
    r"=== TARGET FILE \(REVIEW THIS\): (?P<path>[^\n]*?) \((?P<n>[\d,]+) chars\) ===\n")


def rebuild(content: str) -> str:
    """The target text, cut by the length its own header states."""
    hits = list(HEADER.finditer(content))
    assert len(hits) == 1, f"expected 1 target header, found {len(hits)}"
    m = hits[0]
    assert m.group("path").endswith("SW-21-REF-04.md"), m.group("path")
    n = int(m.group("n").replace(",", ""))
    doc = content[m.end(): m.end() + n]
    assert len(doc) == n, f"the record holds {len(doc)} chars after the header, not {n}"
    return doc


def published_sha256() -> str:
    text = MANIFEST.read_text(encoding="utf-8")
    blocks = re.findall(r"```json\n(.*?)\n```", text, re.S)
    assert blocks, "MANIFEST.md carries no json block"
    table = {}
    for b in blocks:
        table.update(json.loads(b))
    return table[MANIFEST_KEY]["sha256"]


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


@pytest.fixture(scope="module")
def original():
    spec = importlib.util.spec_from_file_location("exp53_original_2026_09_17", ORIGINAL)
    m = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = m
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def rebuilt():
    rec = json.loads(RECORD.read_text(encoding="utf-8"))
    return rebuild(rec["turns"][0]["content"])


class TestTheDocumentIsRebuiltExactly:
    def test_the_rebuilt_bytes_hash_to_the_published_value(self, rebuilt):
        want = published_sha256()
        assert re.fullmatch(r"[0-9a-f]{64}", want), want
        assert sha256(rebuilt) == want

    def test_a_one_character_edit_fails_the_hash(self, rebuilt):
        """Control: the hash check can fail."""
        i = rebuilt.find("**ZC-20.**") + 2
        tampered = rebuilt[:i] + ("X" if rebuilt[i] != "X" else "Y") + rebuilt[i + 1:]
        assert len(tampered) == len(rebuilt) and tampered != rebuilt
        assert sha256(tampered) != published_sha256()

    def test_a_short_header_count_fails_the_hash(self, rebuilt):
        """Control: cutting 1 character short gives a different document."""
        assert sha256(rebuilt[:-1]) != published_sha256()


class TestTheThreeChecksRunWithoutTheOutOfTreeTarget:
    """The original file's own methods, called on the rebuilt document."""

    def test_it_carries_the_declared_number_of_claims(self, original, rebuilt):
        original.TestTheDocumentIsWhatTheFindingsAttack() \
            .test_it_carries_the_declared_number_of_claims(rebuilt)

    def test_the_claims_name_their_own_scope(self, original, rebuilt):
        original.TestTheDocumentIsWhatTheFindingsAttack() \
            .test_the_claims_name_their_own_scope(rebuilt)

    def test_zc20_does_not_say_what_the_finding_says_it_says(self, original, rebuilt):
        original.TestC0005MisquotesTheClaimItAttacks() \
            .test_zc20_does_not_say_what_the_finding_says_it_says(rebuilt)

    def test_the_called_checks_can_fail(self, original, rebuilt):
        """Control: each of the 3 goes red on a document that breaks it."""
        cls = original.TestTheDocumentIsWhatTheFindingsAttack()
        with pytest.raises(AssertionError):
            cls.test_it_carries_the_declared_number_of_claims(
                rebuilt.replace("**ZC-44", "**XX-44", 1))
        with pytest.raises(AssertionError):
            cls.test_the_claims_name_their_own_scope(
                rebuilt.replace("with non-negative costs", "with any costs"))
        i = rebuilt.find("**ZC-20.**")
        line_end = rebuilt.find("\n", i)
        misquoted = rebuilt[:line_end] + " The schedule never shortens." + rebuilt[line_end:]
        with pytest.raises(AssertionError):
            original.TestC0005MisquotesTheClaimItAttacks() \
                .test_zc20_does_not_say_what_the_finding_says_it_says(misquoted)
