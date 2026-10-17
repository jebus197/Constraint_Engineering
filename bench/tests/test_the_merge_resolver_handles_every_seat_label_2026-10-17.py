#!/usr/bin/env python3
"""A seat whose label contains a C or an F before a digit must still merge.

HIS CORRECTION, 2026-10-16: *"Stage 1 item 1.2 is marked done on an incomplete
repair. Its own text is the panel's finding word for word, and within its own
stated scope it still fails for 2 of 8 model labels, 25 per cent, interval
7.1479 to 59.0725."*

THE MECHANISM. `_resolve_merge_source` located the finding id with an unanchored
`re.search(r'(?:F|C)(\\d+)')`, which returns the FIRST place a C or an F is
followed by digits. `CC2` is exactly that, so the composed id `CC2_F004`
reduced to `C2`. No alias key holds `C2`, the resolver returned None, and
`cdsfl_topology_formal.md:126-127` MANDATES reading an unresolved merge source
as a CONFIRM on the target. So every merge CC2 proposed was recorded as CC2
agreeing the target is real: the verdict INVERTED rather than being lost.

WHY A DONE MARKER SURVIVED IT. The archive cannot show the fault. A resolved
merge is written `merged_into=...`; a failed one is written as an ordinary
CONFIRM, indistinguishable from a genuine one. All 800 archived MERGE verdicts
are successes by construction, so reading the record can only ever show the
successes. The fault is visible only by calling the resolver.

These tests therefore CALL it, with the alias map populated the way `register()`
populates it -- keyed `model_id:finding_id` where `finding_id` is the PREFIXED
form, which is the whole point of stage 1 item 1.2. A harness registering the
BARE id would make the resolver look correct for the wrong reason.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
for p in (str(REPO), str(REPO / "bench")):
    if p not in sys.path:
        sys.path.insert(0, p)

import reference_runner_v3 as R  # noqa: E402

VENDORS = ("CC2", "DeepSeek", "ChatGPT", "Gemini", "Codex", "Fable")
LABELS = VENDORS + tuple(f"{v}-SIM" for v in VENDORS)

CANON = "C0040"


def _registry(label: str, composed: str) -> "R.FindingRegistry":
    reg = R.FindingRegistry()
    reg.entries[CANON] = {
        "id": CANON, "model": label, "status": "UNCONFIRMED",
        "severity": 0.8, "description": "the target of the merge",
    }
    reg._alias_map[f"{label}:{composed}"] = CANON
    return reg


@pytest.mark.parametrize("label", LABELS, ids=list(LABELS))
def test_every_seat_label_resolves_its_own_composed_id(label):
    composed = f"{label}_F004"
    reg = _registry(label, composed)
    got = R._resolve_merge_source(f"<- {composed} is the same defect", label, reg)
    assert got == CANON, (
        f"{label}: the resolver returned {got!r} for {composed!r}. An "
        f"unresolved source is MANDATED to be read as a CONFIRM on the target, "
        f"so this inverts the verdict rather than dropping it.")


def test_the_label_that_actually_failed_is_covered():
    """CC2 and CC2-SIM, named rather than left to the parametrised sweep.

    Pinned separately because these 2 are the measured failures, and a sweep
    that silently stopped covering them would still look green.
    """
    for label in ("CC2", "CC2-SIM"):
        assert label in LABELS
        composed = f"{label}_F004"
        reg = _registry(label, composed)
        assert R._resolve_merge_source(f"<- {composed}", label, reg) == CANON


def test_the_bare_form_the_finding_format_teaches_still_resolves():
    """`MERGE C0001 <- F001` is the form the dispatch format documents."""
    reg = R.FindingRegistry()
    reg.entries[CANON] = {"id": CANON, "model": "Gemini", "status": "UNCONFIRMED"}
    reg._alias_map["Gemini:F001"] = CANON
    assert R._resolve_merge_source("<- F001", "Gemini", reg) == CANON


def test_a_canonical_only_reference_still_resolves():
    """The third form the 2026-08-18 comment records as working."""
    reg = R.FindingRegistry()
    reg.entries[CANON] = {"id": CANON, "model": "CC2", "status": "UNCONFIRMED"}
    assert R._resolve_merge_source(f"<- {CANON}", "CC2", reg) == CANON


def test_nothing_resolvable_still_returns_none():
    """The repair must not invent a resolution where there is none."""
    reg = R.FindingRegistry()
    reg.entries[CANON] = {"id": CANON, "model": "CC2", "status": "UNCONFIRMED"}
    assert R._resolve_merge_source("<- no identifier here", "CC2", reg) is None
    assert R._resolve_merge_source("<- F999", "CC2", reg) is None


def test_the_repair_is_additive_and_tries_the_historical_match_first():
    """Anything that resolved before must resolve IDENTICALLY.

    The repair widens the candidate set; it must not reorder it. Where the
    historical first match resolves, that answer wins even though a later
    candidate in the same string would also resolve to something else.
    """
    reg = R.FindingRegistry()
    reg.entries[CANON] = {"id": CANON, "model": "Gemini", "status": "UNCONFIRMED"}
    reg.entries["C0099"] = {"id": "C0099", "model": "Gemini", "status": "UNCONFIRMED"}
    reg._alias_map["Gemini:F001"] = CANON
    reg._alias_map["Gemini:F002"] = "C0099"
    # F001 is the historical first match; F002 would also resolve.
    assert R._resolve_merge_source("<- F001 and also F002", "Gemini", reg) == CANON


def test_a_label_ending_in_a_digit_does_not_capture_the_next_token():
    """The lookbehind must reject a candidate starting inside a longer token."""
    reg = R.FindingRegistry()
    reg.entries[CANON] = {"id": CANON, "model": "CC2", "status": "UNCONFIRMED"}
    reg._alias_map["CC2:CC2_F004"] = CANON
    # `C2` must NOT be treated as the id, and `F004` must be found instead.
    assert R._resolve_merge_source("<- CC2_F004", "CC2", reg) == CANON


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
