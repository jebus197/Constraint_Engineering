"""The decisions file he reads must carry the 4 fields he asked for.

★ HIS REQUEST, 2026-11-16, verbatim: *"Issue ID  -> actual hash value recorded
on disk -> brief but comprehensible descriptor and why it matters (with enough
detail to allow me to make a sane and reasoned choice) -> your recommendation
and why?"*

★ MEASURED ON THE 2026-11-14 DELIVERY BEFORE THIS GUARD EXISTED, which is why
it exists: the entry code appeared in **0 of 19** headings, Wilson [0.000000,
0.168179], and the hash carried its kind prefix in **0 of 19**. 2 of his 4
fields were absent from every block, while the other 2 were present in all 19.
The file was not wrong so much as missing the half that lets him look an item
up — and he cannot look one up, which is the whole reason he asked.

★ WHY THE KIND PREFIX IS NOT DECORATION. `tid_of` digests the kind, so one
sentence recorded as a question and as a proposed fix takes 2 DISTINCT
identities. `[4f09b9135a60]` is therefore ambiguous on disk in a way
`pf:4f09b9135a60` is not, and `scripts/register.py --kind` cannot be driven
from the bare form.

★ IT ASSERTS THE PROPERTY, NOT A COUNT. The number of decisions moves with the
queue — it was 29, then 18, then 19 — so a pinned 19 would fail on the system
working correctly. What is pinned is that EVERY rendered decision carries all 4
fields, plus a non-vacuity floor so an empty render cannot pass.
"""
from __future__ import annotations

import glob
import importlib.util
import pathlib
import re
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
KINDS = ("pf", "qs", "fr", "frx", "stm", "disc", "dis", "ds", "wr")
#: ★ SEPARATOR-AGNOSTIC, AND THAT IS A REPAIR OF THIS FILE'S OWN FIRST VERSION.
#: It pinned " — " between the code and the heading. Hours later the em-dash had
#: to go, because `hd` is shared with the SPOKEN render and Rule 5 of the note
#: standard forbids an em-dash in a file read aloud -- so this guard went red on
#: a change that FIXED a defect. A guard that pins a cosmetic choice punishes
#: the repair. What matters is that the code and the heading are both present
#: and separated; which mark separates them is not this guard's business.
HEAD = re.compile(r"^## DECISION (\d+)\. ([A-Z]\d{1,4})\s*[,:;.\u2014-]\s+(.+?) "
                  r"`\[((?:" + "|".join(KINDS) + r"):[0-9a-f]{12})\]`\s*$", re.M)


def _newest_decisions_file() -> pathlib.Path | None:
    c = sorted(glob.glob(str(REPO / "experimental_notes"
                             / "Decisions_Awaiting_You_*_GENERATED.md")))
    return pathlib.Path(c[-1]) if c else None


@pytest.fixture(scope="module")
def mrb():
    spec = importlib.util.spec_from_file_location(
        "mrb_fields", REPO / "scripts" / "morning_report_build_2026-10-12.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules["mrb_fields"] = m
    try:
        spec.loader.exec_module(m)
    except SystemExit:
        pass
    return m


class TestTheOnDiskHashAccessor:
    def test_ticket_ref_returns_the_kind_and_the_digest(self, mrb):
        """EXECUTED, not read. The bare form and the on-disk form must differ."""
        bare = mrb.ticket_id("B77")
        full = mrb.ticket_ref("B77")
        if not bare:
            pytest.skip("B77 carries no ticket in this checkout")
        assert full != bare, (
            "ticket_ref returned the bare digest; the kind prefix is the whole "
            "point of the sibling function")
        assert full.endswith(bare)
        assert full.split(":", 1)[0] in KINDS, full

    def test_ticket_id_still_returns_the_bare_digest(self, mrb):
        """ADDITIVE: the sibling must not have changed the original's contract.

        2 assertions in `test_a_listed_item_carries_its_ticket_id_2026-11-08.py`
        pin `ticket_id`, and changing it rather than adding beside it would have
        broken them for a gain a new function delivers for nothing.
        """
        bare = mrb.ticket_id("B77")
        if not bare:
            pytest.skip("B77 carries no ticket in this checkout")
        assert ":" not in bare, f"ticket_id now carries a prefix: {bare}"
        assert re.fullmatch(r"[0-9a-f]{12}", bare), bare

    def test_an_unknown_entry_returns_empty_rather_than_guessing(self, mrb):
        assert mrb.ticket_ref("ZZ9999") == ""
        assert mrb.ticket_id("ZZ9999") == ""


class TestEveryRenderedDecisionCarriesAllFour:
    def test_the_file_exists_and_is_not_empty(self):
        """NON-VACUITY. A scan that matches nothing passes forever."""
        f = _newest_decisions_file()
        if f is None:
            pytest.skip("no generated decisions file in this checkout")
        blocks = re.split(r"(?=^## DECISION \d+\.)", f.read_text(encoding="utf-8"),
                          flags=re.M)[1:]
        assert len(blocks) >= 1, (
            f"{f.name} rendered 0 decision blocks, so every check below would "
            f"pass on an empty file")

    def test_field_one_and_two_are_in_every_heading(self):
        f = _newest_decisions_file()
        if f is None:
            pytest.skip("no generated decisions file in this checkout")
        text = f.read_text(encoding="utf-8")
        heads = [ln for ln in text.splitlines()
                 if ln.startswith("## DECISION ")]
        bad = [h for h in heads if not HEAD.match(h)]
        assert not bad, (
            f"{len(bad)} of {len(heads)} heading(s) lack his field 1 (the entry "
            f"code) or field 2 (the hash as recorded on disk, kind and digest). "
            f"First: {bad[0][:160]}")

    def test_the_hash_in_every_heading_exists_on_disk(self):
        """A hash he cannot look up is worse than no hash: it reads as checked."""
        f = _newest_decisions_file()
        if f is None:
            pytest.skip("no generated decisions file in this checkout")
        store = REPO / "bench" / "tickets" / "tickets.jsonl"
        if not store.is_file():
            pytest.skip("no ticket store in this checkout")
        import json
        on_disk = set()
        for line in store.read_text(encoding="utf-8", errors="replace").splitlines():
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except Exception:                                   # noqa: BLE001
                continue
            if row.get("tid"):
                on_disk.add(f"{row.get('kind')}:{row['tid']}")
        refs = [m.group(4) for m in HEAD.finditer(f.read_text(encoding="utf-8"))]
        assert refs, "no heading matched, so this check is vacuous"
        missing = [r for r in refs if r not in on_disk]
        assert not missing, (
            f"{len(missing)} heading hash(es) name no ticket on disk: {missing[:4]}")

    def test_fields_three_and_four_are_in_every_block(self):
        f = _newest_decisions_file()
        if f is None:
            pytest.skip("no generated decisions file in this checkout")
        blocks = re.split(r"(?=^## DECISION \d+\.)", f.read_text(encoding="utf-8"),
                          flags=re.M)[1:]
        for b in blocks:
            head = b.splitlines()[0][:90]
            assert "**WHAT IT IS.**" in b, f"{head}: no descriptor (his field 3)"
            assert "**WHY IT MATTERS.**" in b, f"{head}: no 'why it matters'"
            assert "**RECOMMENDED.**" in b, f"{head}: no recommendation (field 4)"
            rec = b.split("**RECOMMENDED.**", 1)[1]
            assert re.search(r"simplest sufficient|additive|composab", rec, re.I), (
                f"{head}: the recommendation names no formal standard, so it "
                f"gives him a verdict without the reasoning he asked for")

    def test_the_descriptor_is_brief_as_he_asked(self):
        """*"brief but comprehensible"*. Measured before this guard: 1 of 19 ran
        to 812 words, which is not a glance surface."""
        f = _newest_decisions_file()
        if f is None:
            pytest.skip("no generated decisions file in this checkout")
        blocks = re.split(r"(?=^## DECISION \d+\.)", f.read_text(encoding="utf-8"),
                          flags=re.M)[1:]
        long = []
        for b in blocks:
            m = re.search(r"\*\*WHAT IT IS\.\*\*\n(.+?)(?=\n\*\*|\Z)", b, re.S)
            if m and len(m.group(1).split()) > 300:
                long.append((b.splitlines()[0][:70], len(m.group(1).split())))
        assert not long, (
            f"{len(long)} descriptor(s) over 300 words: {long[:3]}. The detail "
            f"belongs in the task-list entry, which each block names.")
