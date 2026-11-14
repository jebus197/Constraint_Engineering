# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'fmea_level_and_draft_encodings_2026-11-14_joint', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 98468109b3f12e28295c762fb3e46e532b6ce5103c5b4d35469e300358f6085b
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""The file-level TIER line is evidenced, and the 2026-11-14 adjudication is executed.

WHY THIS TEST EXISTS. The joint panel round of 2026-11-14 established by AST
that the manifest field `encoding_tier` is consumed by 0 code decisions, and
by reading `composer.py` (the DirectivePacket at the manifest-vocabulary
resolution path sets `text=cand.read_text(...)`) that the file-level `TIER:`
line IS consumed -- verbatim, by every seat whose dispatch composes that
domain layer. A tier is therefore a claim made to a model, and an unevidenced
claim to a model is the defect class the CTCAE v5.0 "confirmed current
2026-11-12" line realised: that confirmation was wrong by about 16 months
(CTCAE v6.0, MedDRA 28.0, published 2025-07-22, primary-verified 2026-11-14).

Before this file, no test executed any TIER line. Under the additive
standard a field nothing reaches is not additive; this test is the TIER
line's first executable consumer, written BEFORE the promotions it guards
were recorded as settled.

The adjudicated split (joint round 2026-11-14, recorded in
experimental_notes/Joint_Round_Fmea_Level_And_Draft_Encodings_Adjudication_2026-11-14.md):
15 of the 22 severity-bearing encodings are CROSS_VERIFIED on primary-confirmed
current citations; 7 stay DRAFT, each for a named reason. Moving any tier now
requires editing the expected set below -- a conscious act in a reviewed file,
not silent drift.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
DIRECTIVES = REPO / "bench" / "directives"
sys.path.insert(0, str(REPO / "bench"))

from cdsfl_registry import domain_vocabulary as dv  # noqa: E402

#: The 7 encodings the 2026-11-14 joint round adjudicated as staying DRAFT,
#: each with its named reason. An 8th name appearing here, or one leaving,
#: is a tier decision and must be made visibly.
EXPECTED_DRAFT = {
    "biology_genetics",          # v6.0 correction is 2 days old; primary read at ladder only
    "biology_natural_world",     # same CTCAE v6.0 recency
    "biology_zoology",           # standing [VERIFY:current] on the animal-welfare scale
    "cross_general",             # founder's internal rule; no published standard to cross-verify
    "mathematics_proof",         # "No standards body governs proof" -- route up is VALIDATED (HIL)
    "information_science_retrieval",  # primary basis is unnamed practice
    "logistics_warehousing",     # honest absence of any primary standard
}
EXPECTED_CROSS_VERIFIED_COUNT = 15


def _tier_files() -> dict:
    """Every encoding carrying a TIER line, mapped to its declared tier."""
    out = {}
    for p in sorted(DIRECTIVES.rglob("*.txt")):
        m = re.search(r"^TIER:\s*(\S+)\s*$", p.read_text(encoding="utf-8"), re.M)
        if m:
            out[p] = m.group(1)
    return out


def _header(text: str) -> str:
    """The declaration block: everything before the first blank line."""
    return text.split("\n\n", 1)[0]


def test_every_tier_line_is_on_the_manifest_ladder():
    ladder = set(dv.tiers())
    files = _tier_files()
    assert files, "no TIER lines found -- the glob or the tree moved"
    bad = {p.name: t for p, t in files.items() if t not in ladder}
    assert not bad, f"tier values off the manifest ladder: {bad}"


def test_no_encoding_above_draft_carries_an_unresolved_currency_flag():
    """CROSS_VERIFIED asserts the citations were verified against the current
    published standard. A [VERIFY:current] in the declaration block says the
    opposite; both cannot stand."""
    offenders = []
    for p, tier in _tier_files().items():
        if tier == "DRAFT":
            continue
        if "[VERIFY:current]" in _header(p.read_text(encoding="utf-8")):
            offenders.append(p.name)
    assert not offenders, (
        f"encodings above DRAFT with an unresolved currency flag: {offenders}")


#: Current scale versions, matching the manifest declarations (primary-verified
#: 2026-11-14). The pattern matches the scale family cited WITH a version token;
#: a version token differing from the current one is the CTCAE-v5.0 defect.
_CURRENT = {
    "CTCAE": (re.compile(r"CTCAE\s+v(\d+\.\d+)"), "6.0"),
    "CVSS": (re.compile(r"CVSS\s+v(\d+\.\d+)"), "4.0"),
}


def _asserted(head: str) -> str:
    """Drop ★ CORRECTED notes: project practice preserves the REFUTED text
    verbatim inside a correction, and a version token quoted there is not
    asserted as current. First run of this guard went red on exactly that --
    the biology correction notes quoting the superseded v5.0 line."""
    return head.split("★ CORRECTED", 1)[0]


def test_no_header_asserts_a_version_the_manifest_has_superseded():
    offenders = []
    for p in _tier_files():
        head = _asserted(_header(p.read_text(encoding="utf-8")))
        for family, (pat, current) in _CURRENT.items():
            for ver in pat.findall(head):
                if ver != current:
                    offenders.append(f"{p.name}: {family} v{ver} (current v{current})")
    assert not offenders, f"superseded scale versions in declaration blocks: {offenders}"


def test_the_adjudicated_split_is_the_one_on_disk():
    files = _tier_files()
    severity = {p: t for p, t in files.items()
                if re.search(r"^SEVERITY SCALE:", p.read_text(encoding="utf-8"), re.M)}
    assert len(severity) == 22, f"expected 22 severity-bearing encodings, found {len(severity)}"
    draft = {p.stem for p, t in severity.items() if t == "DRAFT"}
    cv = {p.stem for p, t in severity.items() if t == "CROSS_VERIFIED"}
    assert draft == EXPECTED_DRAFT, (
        f"DRAFT set moved without editing this test: "
        f"unexpected={sorted(draft - EXPECTED_DRAFT)} missing={sorted(EXPECTED_DRAFT - draft)}")
    assert len(cv) == EXPECTED_CROSS_VERIFIED_COUNT


# ---------------------------------------------------------------------------
# Non-vacuity: each guard goes red on the defect it exists to catch. The text
# below is the biology_genetics declaration block AS DISPATCHED on 2026-11-14
# (sha256 of the file then: see the panel brief's stamp table) -- the defect
# that was live on disk when this test was written.
# ---------------------------------------------------------------------------
_AS_DISPATCHED_BIOLOGY_HEADER = (
    "DOMAIN: Biology — Genetics and Molecular\n"
    "VERSION: 1.0\n"
    "TIER: DRAFT\n"
    "SEVERITY SCALE: CTCAE v5.0 grade, critical at Grade 3, where the work bears on\n"
    "       a person. Research-only work inherits the application's scale.\n"
    "SOURCES: NCI CTEP CTCAE v5.0 (2017), confirmed current 2026-11-12.\n"
)


def test_the_version_guard_is_not_vacuous():
    pat, current = _CURRENT["CTCAE"]
    stale = [v for v in pat.findall(_AS_DISPATCHED_BIOLOGY_HEADER) if v != current]
    assert stale == ["5.0", "5.0"], (
        "the guard no longer fires on the as-dispatched defect it was built from")


def test_the_flag_guard_is_not_vacuous():
    flagged = "SOURCES: x. [VERIFY:current] -- unresolved.\nTIER: CROSS_VERIFIED\n"
    assert "[VERIFY:current]" in _header(flagged), (
        "the header scoping stopped seeing a flag in the declaration block")


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
