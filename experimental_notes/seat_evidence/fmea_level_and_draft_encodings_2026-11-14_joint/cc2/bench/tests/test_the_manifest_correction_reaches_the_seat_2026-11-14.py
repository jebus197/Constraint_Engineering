# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'fmea_level_and_draft_encodings_2026-11-14_joint', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: b12d08e8df314658af80bf078bb266858ec635f68ea4ca85ff60611a654506e6
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""A manifest severity correction must REACH THE SEAT, not stop at the manifest.

★ WHY THIS EXISTS, AND IT IS A MEASURED DEFECT, NOT A HYPOTHETICAL.
`composer._severity_declaration` returns "" the moment the composed encoding
carries its own `^SEVERITY SCALE:` line, on the stated ground that the encoding
is "the narrower, better-sourced statement". That ground is an ASSUMPTION about
the encoding, and on 2026-11-14 it was false for all 3 biology encodings:

    domain_manifest.toml  biology.severity_scale = "CTCAE v6.0 grade"
                          (primary: NCI CTEP, published 2025-07-22, 312 pp)
    biology_genetics.txt  "SEVERITY SCALE: CTCAE v5.0 grade ..."
                          "SOURCES: ... confirmed current 2026-11-12."

The manifest was corrected to v6.0 after the `fable` seat found v5.0 was
superseded. The ENCODINGS were not. Because the encoding suppresses the
manifest declaration, a biology seat received `CTCAE v5.0` and the correction
reached nobody -- while the encoding additionally asserted a CONFIRMATION wrong
by about 16 months. Reproduced before the repair by importing the real
composer: the seat's text held `CTCAE v5.0` and 0 occurrences of `v6.0`.

THE ROOT CAUSE IS NOT THE SUPPRESSION RULE. Preferring a better-sourced
encoding is defensible, and changing what the composer admits is the founder's
ruling rather than a repair. The root cause is that the version string exists in
2 independently editable places with NOTHING comparing them, so a correction to
one silently fails to propagate. This file is that comparison, wired to pytest
so the next correction either propagates or goes red.

Scope, stated rather than implied: this checks VERSION AGREEMENT for a standard
the manifest and an encoding BOTH name. It does not check whether the version is
current against the publisher -- no test can, and that is the standing residual.
"""
from __future__ import annotations

import re
import sys
import tomllib
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

MANIFEST = REPO / "bench/cdsfl_registry/domain_manifest.toml"
DIRECTIVES = REPO / "bench/directives"

# A standard whose version token is MACHINE-COMPARABLE: family name, and the
# regex for its version as written in this project. Deliberately a short closed
# list -- a family nobody versions consistently would produce false positives,
# which is worse than silence.
VERSIONED = {
    "CTCAE": re.compile(r"CTCAE\s+v(\d+\.\d+)"),
    "CVSS": re.compile(r"CVSS\s+v(\d+\.\d+)"),
}


def _manifest() -> dict:
    return tomllib.loads(MANIFEST.read_text(encoding="utf-8"))


def _severity_block(text: str) -> str:
    """The encoding's own `SEVERITY SCALE:` block -- the text that SUPPRESSES."""
    m = re.search(r"^SEVERITY SCALE:.*$", text, re.M)
    if not m:
        return ""
    rest = text[m.start():].splitlines()
    out = [rest[0]]
    for line in rest[1:]:
        if line[:1].strip():          # a new column-0 key ends the block
            break
        out.append(line)
    return "\n".join(out)


def _pairs() -> list[tuple[str, str, Path, str, str]]:
    """(domain, family, encoding_path, manifest_version, encoding_version)."""
    raw = _manifest()
    found = []
    for domain, d in raw.items():
        if not isinstance(d, dict):
            continue
        scale = d.get("severity_scale")
        if not isinstance(scale, str) or scale in ("none", "composed", ""):
            continue
        for family, rx in VERSIONED.items():
            mm = rx.search(scale)
            if not mm:
                continue
            for _label, sub in (d.get("subdomains") or {}).items():
                path = DIRECTIVES / sub["path"]
                if not path.is_file():
                    continue
                block = _severity_block(path.read_text(encoding="utf-8"))
                if family not in block:
                    continue              # encoding does not name it: fine
                em = rx.search(block)
                if not em:
                    continue              # names it unversioned: other defect
                found.append((domain, family, path, mm.group(1), em.group(1)))
    return found


def test_the_pairs_are_not_empty():
    """Non-vacuity. A green run over 0 pairs would prove nothing at all."""
    assert _pairs(), (
        "0 (manifest, encoding) version pairs found. Either the manifest "
        "declares no versioned scale or the block parser is broken -- either "
        "way the agreement test below is vacuous and must not be trusted.")


@pytest.mark.parametrize("case", _pairs(), ids=lambda c: f"{c[0]}:{c[2].name}")
def test_a_suppressing_encoding_names_the_manifest_version(case):
    domain, family, path, man_v, enc_v = case
    assert enc_v == man_v, (
        f"{path.relative_to(REPO)} declares its own SEVERITY SCALE, which "
        f"SUPPRESSES the manifest declaration in _severity_declaration. It "
        f"names {family} v{enc_v} while domain_manifest.toml declares {family} "
        f"v{man_v} for domain {domain!r}. The seat therefore receives v{enc_v} "
        f"and the manifest's correction reaches nobody -- the 2026-11-14 CTCAE "
        f"defect recurring. Correct the ENCODING too.")


def test_no_encoding_claims_a_confirmation_without_the_version_date():
    """A 'confirmed current' claim with no publication date is unfalsifiable.

    The 2026-11-12 biology claim read "CTCAE v5.0 (2017), confirmed current
    2026-11-12" and was wrong by about 16 months. A reader could not tell WHICH
    publication the confirmation covered. Requiring the version's own
    publication date in the same block makes it re-checkable by inspection.
    """
    offenders = []
    for path in sorted(DIRECTIVES.rglob("*.txt")):
        text = path.read_text(encoding="utf-8")
        head = text[: text.find("[HARD")] if "[HARD" in text else text[:2000]
        for m in re.finditer(r"confirmed current[^\n]*", head):
            window = head[max(0, m.start() - 400): m.end() + 400]
            if not re.search(r"published\s+\d{4}-\d{2}-\d{2}", window):
                offenders.append(f"{path.relative_to(REPO)}: {m.group(0)[:70]}")
    assert not offenders, (
        "a 'confirmed current' claim must name the publication date of the "
        "version it confirms, else it cannot be re-checked:\n  "
        + "\n  ".join(offenders))


def test_the_guard_goes_red_on_the_as_dispatched_text(tmp_path):
    """Mutation proof: restore the as-dispatched v5.0 line and the check fires.

    Operates on a COPY under tmp_path. The artefact is never written.
    """
    src = DIRECTIVES / "biology/biology_genetics.txt"
    mutated = src.read_text(encoding="utf-8").replace("CTCAE v6.0", "CTCAE v5.0")
    copy = tmp_path / "biology_genetics.txt"
    copy.write_text(mutated, encoding="utf-8")

    rx = VERSIONED["CTCAE"]
    man_v = rx.search(_manifest()["biology"]["severity_scale"]).group(1)
    enc_v = rx.search(_severity_block(copy.read_text(encoding="utf-8"))).group(1)
    assert man_v == "6.0"
    assert enc_v == "5.0"
    assert enc_v != man_v, "the mutation did not disagree; the guard is vacuous"
