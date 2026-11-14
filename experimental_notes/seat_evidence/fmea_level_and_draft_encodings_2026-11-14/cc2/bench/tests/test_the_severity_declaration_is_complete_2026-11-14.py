# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'fmea_level_and_draft_encodings_2026-11-14', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: d727f5c48d435958702396f9c75f5bd7a2b04c8eac79e7a33e7758854b0cf63f
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""The severity declaration a seat receives must be COMPLETE and NON-DEGENERATE.

Written for the panel question of 2026-11-14 on the engineering critical level
and the 22 DRAFT encodings. Two independent properties, one guard file because
both are properties of the same delivered declaration.

★ WHY A GUARD AND NOT A PROSE RULE. `bench/directives/universal/
cdsfl_core_formal.md` already instructs every seat: "Report a consequence as a
(value, scale-name) pair, never a bare number. `CVSS v4.0: 7.0` is a report;
`7.0` is not." Measured on 2026-11-14, 7 of the 22 encodings that carry their
own `SEVERITY SCALE:` line named a manifest-declared scale family with NO
edition token in the declaration block -- `FMEA severity applies with critical
at 7`, `CTCAE with critical at Grade 3`, `GHS health hazard category`. The
prose rule did not bind, in the same way the project's own record says a prose
rule does not bind. So it is checked.

★ AND WHY THE SECOND TEST IS THE Q1 PROCEDURE RATHER THAN A NUMBER. The panel
was asked for a mechanism, not a vote between 7 and 9. The mechanism is:
A DECLARED CRITICAL LEVEL MAY NOT BE THE MAXIMAL BAND OF ITS OWN SCALE.
At the maximal band the predicate `c_d(f) >= theta_d` is equivalent to
`c_d(f) == max`, an IDENTITY TEST rather than an ordinal threshold, and the
ordering above the cut carries no information at all. `cdsfl_core_formal.md`
defines theta_d as "a distinguished element OF that ordering"; the maximum
distinguishes nothing, because every scale has one by construction.

IF THE FOUNDER RULES FOR THE 9-10 SAFETY-OR-REGULATORY BAND, this test is the
single place that has to change: delete `test_no_declared_critical_level_is_
the_maximal_band` and record his ruling in its place. That is deliberate. A
loosening of what counts as critical should cost exactly one visible edit to a
named test, not a silent change to a data file.

RUN:  python3 -m pytest bench/tests/test_the_severity_declaration_is_complete_2026-11-14.py -q
"""
from __future__ import annotations

import pathlib
import re
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from bench.cdsfl_registry import domain_vocabulary as V      # noqa: E402

DIRECTIVES = ROOT / "bench" / "directives"

#: The edition token each manifest-declared scale family must carry wherever it
#: is named. DERIVED from the manifest at test time rather than transcribed, so
#: a manifest correction (CVSS v3.1 -> v4.0 happened on 2026-11-12) cannot
#: leave this table behind. The family NAME is the stable part; the pattern is
#: what the manifest currently declares.
_FAMILY_PATTERNS = {
    "FMEA":  r"\b2019\b",
    "CVSS":  r"v4\.0",
    "CTCAE": r"v5\.0",
    "GHS":   r"Rev\.?\s*11",
}


def _declared_families() -> dict[str, str]:
    """Family -> the edition token the MANIFEST declares for it. Fails loudly
    if the manifest's scale name stops containing the token this guard looks
    for, because a silently stale guard is the failure mode it exists against."""
    out: dict[str, str] = {}
    for dom in V.domains():
        scale = V.severity(dom)["scale"]
        if not scale or scale in ("none", "composed"):
            continue
        for fam, pat in _FAMILY_PATTERNS.items():
            if re.search(rf"\b{fam}\b", scale):
                assert re.search(pat, scale, re.I), (
                    f"manifest declares {dom} scale {scale!r} which no longer "
                    f"matches this guard's edition pattern {pat!r} for {fam}. "
                    f"Update _FAMILY_PATTERNS in the same commit as the scale.")
                out[fam] = pat
    return out


def _encodings_with_a_scale_line() -> list[pathlib.Path]:
    return [p for p in sorted(DIRECTIVES.rglob("*.txt"))
            if p.parent.name != "universal"
            and re.search(r"^SEVERITY SCALE:",
                          p.read_text(encoding="utf-8", errors="ignore"), re.M)]


def _scale_block(text: str) -> str:
    """The SEVERITY SCALE declaration, up to the next ALL-CAPS section header.

    Scoped to the DECLARATION and not the whole file on purpose: `SOURCES:` is
    a bibliography, and a seat reporting a (value, scale-name) pair reads the
    scale name off the declaration. Measured 2026-11-14, this distinction is
    load-bearing -- `chemistry_general.txt` carried `Rev. 10` in SOURCES while
    its declaration said a bare `GHS`."""
    m = re.search(r"^SEVERITY SCALE:.*?(?=^[A-Z][A-Z ]{3,}:)", text, re.M | re.S)
    return m.group(0) if m else ""


def _offenders(files: list[pathlib.Path]) -> list[tuple[str, str]]:
    fams = _declared_families()
    bad: list[tuple[str, str]] = []
    for p in files:
        block = _scale_block(p.read_text(encoding="utf-8", errors="ignore"))
        for fam, pat in fams.items():
            if re.search(rf"\b{fam}\b", block) and not re.search(pat, block, re.I):
                try:
                    name = p.relative_to(ROOT).as_posix()
                except ValueError:          # a copy under tmp, in the vacuity test
                    name = p.name
                bad.append((name, fam))
    return bad


def test_the_guard_table_matches_the_manifest():
    fams = _declared_families()
    assert set(fams) == {"FMEA", "CVSS", "CTCAE", "GHS"}, fams


def test_every_named_scale_family_carries_its_edition():
    """A scale name without its edition is not a scale name.

    This project corrected CVSS v3.1 -> v4.0 and GHS Rev. 10 -> Rev. 11 on
    2026-11-12 precisely because an unversioned citation names a superseded
    standard without saying so."""
    bad = _offenders(_encodings_with_a_scale_line())
    assert not bad, (
        "encodings naming a manifest-declared scale family with no edition "
        "token in the declaration block:\n  " +
        "\n  ".join(f"{f} cites {fam}" for f, fam in bad))


def test_the_edition_guard_is_not_vacuous(tmp_path):
    """Prove the guard CATCHES the defect, by reintroducing it on a copy.

    An addition nothing reaches is not additive. A guard that passes because it
    tests nothing is exactly that, so the defect is put back and the guard is
    required to fire."""
    src = DIRECTIVES / "software" / "software_general.txt"
    dst = tmp_path / "software_general.txt"
    text = src.read_text(encoding="utf-8")
    assert "CVSS v4.0 base score" in text
    dst.write_text(text.replace("CVSS v4.0 base score", "CVSS base score"),
                   encoding="utf-8")
    bad = _offenders([dst])
    assert [fam for _f, fam in bad] == ["CVSS"], (
        f"the guard did not fire on a deliberately unversioned CVSS "
        f"citation; it is vacuous. got {bad!r}")


def _band_index(levels: list[str], critical: str) -> int:
    c = str(critical).strip().lower()
    for i, b in enumerate(levels):
        if c in re.findall(r"[A-Za-z0-9.]+", str(b).lower()):
            return i
    hits = [i for i, b in enumerate(levels) if c in str(b).strip().lower()]
    assert hits, f"critical level {critical!r} names no band in {levels!r}"
    return hits[0]


#: Domains whose manifest declares a scale, with the rank of the declared
#: critical level counted from the TOP of its own band list. Rank is a SELECTED
#: order statistic, so it is invariant under every strictly increasing relabel
#: of the scale -- admissible under `cdsfl_core_formal.md`'s own table, unlike
#: a comparison to a fixed real. Verified 2026-11-14 on 2 independent tools:
#: z3 finds no order-preserving relabel that changes a rank, and Wolfram
#: Language showed phi(x) = x^3 + x preserving `Ordering` while changing the
#: count clearing a FIXED cut of 4 from 2 to 4.
def _ranks_from_top() -> dict[str, tuple[int, int, str]]:
    out = {}
    for dom in V.domains():
        sev = V.severity(dom)
        if sev["scale"] in (None, "none", "composed") or not sev["critical_level"]:
            continue
        lv = sev["levels"]
        i = _band_index(lv, sev["critical_level"])
        out[dom] = (len(lv) - i, len(lv), sev["critical_level"])
    return out


def test_no_declared_critical_level_is_the_maximal_band():
    """THE Q1 PROCEDURE, MECHANISED. See the module docstring for the ruling
    path if the founder decides for the 9-10 safety-or-regulatory band."""
    ranks = _ranks_from_top()
    assert ranks, "no domain declares a scale with a critical level"
    degenerate = {d: v for d, v in ranks.items() if v[0] == 1}
    assert not degenerate, (
        "a critical level at the MAXIMAL band makes `c >= theta` equivalent to "
        "`c == max`, an identity test rather than an ordinal threshold:\n  " +
        "\n  ".join(f"{d}: critical={v[2]!r} is band {v[1]} of {v[1]}"
                    for d, v in degenerate.items()))


def test_the_maximal_band_guard_is_not_vacuous():
    """Reintroduce the degenerate cut on a copy of the data and require the
    predicate to fire."""
    levels = ["1 no effect", "2-3 very minor to minor", "4-6 moderate",
              "7-8 high", "9-10 safety or regulatory"]
    assert len(levels) - _band_index(levels, "7") == 2, "7 is band 4 of 5"
    assert len(levels) - _band_index(levels, "9") == 1, (
        "9 must land in the MAXIMAL band for the guard to be meaningful")


def test_a_named_critical_level_cannot_reach_the_numeric_gate():
    """The 2 quantities are distinct, and the distinction bounds Q1.

    `reference_runner_v3.CRITICAL_SEVERITY_THRESHOLD` is a float on [0,1]
    compared against a model-asserted severity. A domain's `critical_level` is
    a STRING naming a rank on an external ordinal scale. Nothing converts one
    into the other, which is why changing the named level is a REPORTING
    change and not a gate change."""
    import ast
    runner = (ROOT / "bench" / "reference_runner_v3.py").read_text(encoding="utf-8")
    thr = None
    for node in ast.parse(runner).body:
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "CRITICAL_SEVERITY_THRESHOLD"
                for t in node.targets):
            thr = ast.literal_eval(node.value)
    assert isinstance(thr, float), thr
    lvl = V.severity("engineering")["critical_level"]
    assert isinstance(lvl, str), lvl
    # The composer is the ONLY route from the named level to anything. Checked
    # by AST and not by substring: the composer MENTIONS the gate constant once,
    # in `_severity_declaration`'s docstring ("The live
    # `CRITICAL_SEVERITY_THRESHOLD` is unchanged"), and a prose mention is not a
    # reference. A substring count cannot tell those apart, and this guard
    # failed on exactly that distinction when first run on 2026-11-14.
    comp_src = (ROOT / "bench" / "cdsfl_registry" / "composer.py").read_text(
        encoding="utf-8")
    refs = [n for n in ast.walk(ast.parse(comp_src))
            if isinstance(n, ast.Name) and n.id == "CRITICAL_SEVERITY_THRESHOLD"]
    attrs = [n for n in ast.walk(ast.parse(comp_src))
             if isinstance(n, ast.Attribute)
             and n.attr == "CRITICAL_SEVERITY_THRESHOLD"]
    assert not refs and not attrs, (
        f"the composer now REFERENCES the numeric gate ({len(refs)} names, "
        f"{len(attrs)} attributes); the 2 quantities may have been conflated")
    conv = (ROOT / "bench" / "convergence_location.py").read_text(encoding="utf-8")
    assert conv.count("critical_level") == 0 and conv.count("severity_scale") == 0, (
        "a domain's named level now reaches the convergence series; Q1 would "
        "then be a convergence change, not a reporting one")


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
