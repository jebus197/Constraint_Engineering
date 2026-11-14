# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'fmea_level_and_draft_encodings_2026-11-14_joint', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 3c5d7f9c30bdda5beb75531a3fa8094affce5ce97aa72209d3e9679bc7820cd8
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""THE TIER LINE IS PROMPT-DELIVERED, AND A STALE CITATION IN AN ENCODING IS A
STALE STATEMENT IN EVERY SEAT'S DIRECTIVE.

Joint panel round `fmea_level_and_draft_encodings_2026-11-14`. The round's brief
said `encoding_tier` is "consumed by 0 decisions anywhere in the tree", verified
by AST. That is true of the MANIFEST field and FALSE of the file-level `TIER:`
line, and the difference was measured rather than argued: for every domain whose
declared default encoding carries a `TIER:` line, `composer.compose()` delivers
that line verbatim in `rendered_text` -- the text a seat reads. The consumer the
AST sweep cannot see is the seat model itself. So a tier promotion is not a
label edit; it is a change to what every seat is told about the authority of its
own constraint box, and a WRONG tier is prompt-delivered misinformation.

Test 2 exists because of CTCAE. The manifest's biology entry was corrected to
v6.0 on 2026-11-14 after the `fable` seat refuted the 2026-11-12 "confirmed
current" claim against the primary document -- but the 3 biology ENCODINGS still
cited v5.0, 2 of them carrying the refuted confirmation verbatim, and those
files are prompt-delivered. EXECUTED RED before the repair: on the as-dispatched
tree this test failed with 3 offending files. A declaration that records a
confirmation is only as current as the day it was checked, and nothing
re-checked it; this test is the re-check for the specific failure shape.
"""
from __future__ import annotations

import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
BENCH = HERE.parent
sys.path.insert(0, str(BENCH))

from cdsfl_registry import composer  # noqa: E402
from cdsfl_registry import domain_vocabulary as dv  # noqa: E402

DIRECTIVES = BENCH / "directives"


def _tier_line(path: pathlib.Path) -> str | None:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("TIER:"):
            return line.strip()
    return None


def test_the_default_encodings_tier_line_reaches_rendered_text():
    """For every domain whose DEFAULT encoding carries a TIER line, that exact
    line is in compose().rendered_text. This wires the measured delivery path
    to a test, so a future composer change that silently strips the line (or a
    tier edit that never reaches a prompt) fails loudly instead of quietly."""
    checked = 0
    for dom in dv.domains():
        enc = dv.encoding_path(dom)
        if not enc.is_file():
            continue
        tier = _tier_line(enc)
        if tier is None:
            continue  # logistics' default carries none; absence is not a defect here
        rendered = composer.compose(dom, "fable_5_1").rendered_text
        assert tier in rendered, (
            f"{dom}: default encoding {enc.name} declares {tier!r} but the "
            f"composed rendered_text does not carry it -- the tier stopped "
            f"reaching the seat")
        checked += 1
    assert checked >= 8, f"only {checked} domains checked; the wiring is not exercised"


def _cites_v5_live(text: str) -> bool:
    """True iff CTCAE v5.0 appears as a LIVE citation. Project practice
    preserves a refuted claim verbatim inside its correction, so v5.0 is
    permitted ONLY where the same file carries a CORRECTED marker and a live
    v6.0 citation, and never on the SEVERITY SCALE line itself."""
    if not re.search(r"CTCAE\s*v?5(\.0)?\b", text):
        return False
    for line in text.splitlines():
        if line.startswith("SEVERITY SCALE:") and re.search(r"v5(\.0)?\b", line):
            return True  # the operative scale line names the superseded version
    quoted_in_correction = ("CORRECTED" in text) and re.search(r"CTCAE\s*v?6(\.0)?\b", text)
    return not quoted_in_correction


def test_no_directive_cites_ctcae_v5_as_current():
    """CTCAE v5.0 was superseded by v6.0 (MedDRA 28.0, published 2025-07-22,
    read from the primary at dctd.cancer.gov; manifest corrected 2026-11-14).
    No prompt-delivered encoding may cite v5.0 as live -- in particular none
    may carry the refuted 'confirmed current 2026-11-12' claim outside a
    correction note that quotes it as refuted. EXECUTED RED on the
    as-dispatched tree: all 3 biology encodings offended (no CORRECTED marker
    existed), so the guard's silence after repair is a measurement."""
    offenders = [str(p.relative_to(BENCH.parent))
                 for p in sorted(DIRECTIVES.rglob("*.txt"))
                 if _cites_v5_live(p.read_text(encoding="utf-8"))]
    assert not offenders, (
        "directives still citing superseded CTCAE v5.0 as live "
        f"(prompt-delivered): {offenders}")


def test_every_declared_scale_source_carries_a_version_token():
    """Every manifest-declared severity scale's source names an edition,
    revision, version or year -- the CVSS v3.1 and CTCAE v5.0 corrections were
    both version-name staleness, and an unversioned citation cannot even BE
    checked for staleness."""
    version_token = re.compile(
        r"(v\d+(\.\d+)?|Rev\.?\s*\d+|\b(1st|2nd|3rd|\dth)\s+edition|"
        r"\bedition\b|\b(19|20)\d{2}\b)", re.IGNORECASE)
    for dom in dv.domains():
        d = dv.entry(dom)
        scale = d.get("severity_scale")
        if scale in (None, "none", "composed"):
            continue
        src = d.get("severity_scale_source") or ""
        assert version_token.search(src), (
            f"{dom}: declared scale {scale!r} has a source with no version/"
            f"edition/year token: {src!r}")


def test_the_v5_guard_is_not_vacuous():
    """The CTCAE regex fires on the exact as-dispatched wording -- proven on a
    reconstruction, so the guard's silence after repair is evidence and not a
    hole in the pattern."""
    sample = ("SEVERITY SCALE: CTCAE v5.0 grade, critical at Grade 3\n"
              "SOURCES: NCI CTEP CTCAE v5.0 (2017), confirmed current 2026-11-12.\n")
    assert _cites_v5_live(sample), (
        "the guard does not fire on the as-dispatched wording it was built to catch")
    corrected = sample + "CORRECTED 2026-11-14 to CTCAE v6.0 (MedDRA 28.0).\n"
    # the SEVERITY SCALE line still names v5.0, so even a correction note does
    # not excuse an operative scale line:
    assert _cites_v5_live(corrected), (
        "a v5.0 SEVERITY SCALE line must offend even beside a correction note")
    repaired = corrected.replace("SEVERITY SCALE: CTCAE v5.0",
                                 "SEVERITY SCALE: CTCAE v6.0")
    assert not _cites_v5_live(repaired), (
        "a v5.0 mention quoted inside a correction, beside a live v6.0 "
        "citation, must NOT offend -- preserving the refuted claim verbatim "
        "is project practice")


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-q"]))
