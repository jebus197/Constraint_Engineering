# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'fmea_level_and_draft_encodings_2026-11-14', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 61125be87f29ed5fd85d51c7ccab539723559615dd8d1c11b0045605b1e16e2b
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""Guards for the severity declarations and the encoding tier — panel, 2026-11-14.

WHY THIS FILE EXISTS. Measured 2026-11-14 by grep and AST: the file-level
`TIER:` line in bench/directives/*.txt had 0 code consumers, and the manifest's
`encoding_tier` was read only by the loader's validation and a CLI print. A
label nothing reads is an addition nothing reaches. This module is the TIER
line's first consumer, and it is also the tripwire that makes any change to the
engineering critical level a LOUD, reviewed act rather than a quiet edit:
moving `critical_level` off 7, or dropping either landmark band from what a
seat receives, fails a test.

THE INDEPENDENCE FACT IT PINS, measured by execution 2026-11-14: the live gate
`CRITICAL_SEVERITY_THRESHOLD` (reference_runner_v3.py) and the convergence
series (convergence_location.py) contain 0 occurrences of `critical_level` and
0 of `domain_vocabulary` — a domain's named critical level reaches ONLY the
composed prompt text via `composer._severity_declaration`. If someone couples
them later, the coupling must arrive together with a deliberate edit here.

Every check is a plain function over parsed data so the mutation test below can
feed it broken data and confirm the guard goes red — a guard that cannot fail
is not a guard (software_general.txt, HARD constraints).
"""
from __future__ import annotations

import re
import tomllib
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "bench" / "cdsfl_registry" / "domain_manifest.toml"
DIRECTIVES = REPO / "bench" / "directives"
RUNNER = REPO / "bench" / "reference_runner_v3.py"
CONVERGENCE = REPO / "bench" / "convergence_location.py"

#: The non-DRAFT [VERIFY:current] carve-out: a promoted encoding may carry the
#: flag ONLY on a claim its own text marks "not load-bearing" in the same
#: sentence. Anything else is an unresolved verification under a tier that
#: asserts verification happened.
_NOT_LOAD_BEARING = re.compile(r"\[VERIFY:current\].{0,120}?not\s+load-bearing",
                               re.I | re.S)


def _manifest() -> dict:
    with open(MANIFEST, "rb") as fh:
        return tomllib.load(fh)


def _encodings() -> dict[Path, str]:
    return {p: p.read_text() for p in sorted(DIRECTIVES.rglob("*.txt"))
            if p.parent.name != "universal"}


def _header(text: str) -> str:
    """Everything before the first bracketed section — DOMAIN through SOURCES."""
    m = re.search(r"^\[", text, re.M)
    return text[: m.start()] if m else text


def _tier(text: str) -> str | None:
    m = re.search(r"^TIER:\s*(\S+)", text, re.M)
    return m.group(1) if m else None


# ---------------------------------------------------------------- checks


def check_tier_legal(name: str, text: str, allowed: list[str]) -> None:
    t = _tier(text)
    if t is not None and t not in allowed:
        raise AssertionError(f"{name}: TIER {t!r} not in the manifest ladder {allowed}")


def check_no_unresolved_verify_above_draft(name: str, text: str) -> None:
    t = _tier(text)
    if t in (None, "DRAFT"):
        return
    head = _header(text)
    flags = head.count("[VERIFY:current]")
    excused = len(_NOT_LOAD_BEARING.findall(head))
    if flags > excused:
        raise AssertionError(
            f"{name}: TIER {t} with {flags - excused} unresolved [VERIFY:current] "
            "flag(s) in its header — a tier asserting verification cannot carry "
            "an unverified load-bearing citation"
        )


def check_engineering_declaration(decl: str) -> None:
    """The Q1 tripwire. Both published landmarks must reach the seat, and the
    critical level must be 7 — the lowest landmark whose band definition
    (S7 degradation / S8 loss of primary function) entails the project's
    pre-registered materiality rubric. Changing the level is the founder's
    ruling; this test makes the change loud, it does not forbid his making it —
    whoever applies his ruling edits this assertion in the same commit."""
    for needle in ("CRITICAL LEVEL: 7", "7-8 high", "9-10 safety or regulatory"):
        if needle not in decl:
            raise AssertionError(
                f"engineering severity declaration lost {needle!r}; a seat is "
                "no longer told both landmarks and the declared level"
            )


def check_gate_independence(runner_src: str, convergence_src: str) -> None:
    for label, src in (("reference_runner_v3.py", runner_src),
                       ("convergence_location.py", convergence_src)):
        for token in ("critical_level", "domain_vocabulary"):
            if token in src:
                raise AssertionError(
                    f"{label} now references {token!r}: the domain critical "
                    "level and the live gate were independent quantities on "
                    "2026-11-14 — if this coupling is deliberate, it is a gate "
                    "change and needs the founder's ruling recorded here"
                )
    m = re.search(r"^CRITICAL_SEVERITY_THRESHOLD\s*=\s*([0-9.]+)", runner_src, re.M)
    if not m or float(m.group(1)) != 0.7:
        raise AssertionError("CRITICAL_SEVERITY_THRESHOLD moved off the frozen 0.7")


# ---------------------------------------------------------------- tests


def test_tier_values_are_on_the_manifest_ladder():
    allowed = _manifest()["tiers"]
    for p, text in _encodings().items():
        check_tier_legal(p.name, text, allowed)


def test_no_unresolved_verify_flag_above_draft():
    for p, text in _encodings().items():
        check_no_unresolved_verify_above_draft(p.name, text)


def test_superseded_scale_version_cannot_leave_draft():
    """CTCAE v5.0 was superseded by v6.0 (published 2025-07-10, errata
    2026-01-20). An encoding naming v5.0 as its scale stays DRAFT until the
    citation is reconciled against the primary v6.0 document."""
    for p, text in _encodings().items():
        if re.search(r"^SEVERITY SCALE:.*CTCAE v5\.0", text, re.M):
            assert _tier(text) == "DRAFT", (
                f"{p.name}: cites superseded CTCAE v5.0 as its scale but is "
                f"tiered {_tier(text)}"
            )


def test_engineering_seat_receives_both_landmarks_and_level_7():
    from bench.cdsfl_registry.composer import _severity_declaration
    check_engineering_declaration(_severity_declaration("engineering", ""))


def test_every_scale_bearing_domain_delivers_a_declaration():
    """No seat may be forbidden to invent a level and then given none: every
    manifest domain with a declared scale (or an honest none-with-reason) must
    produce non-empty text when its encoding is silent."""
    from bench.cdsfl_registry.composer import _severity_declaration
    man = _manifest()
    for dom, entry in man.items():
        if not isinstance(entry, dict) or "severity_scale" not in entry:
            continue
        decl = _severity_declaration(dom, "")
        assert decl.strip(), f"{dom}: declares a scale yet delivers silence"


def test_gate_and_convergence_independent_of_domain_critical_level():
    check_gate_independence(RUNNER.read_text(), CONVERGENCE.read_text())


def test_guards_go_red_on_mutation():
    """A guard that cannot fail is not a guard: each check must reject the
    defect it exists to catch."""
    with pytest.raises(AssertionError):
        check_tier_legal("x", "TIER: GOLD\n", ["DRAFT", "CROSS_VERIFIED"])
    with pytest.raises(AssertionError):
        check_no_unresolved_verify_above_draft(
            "x", "TIER: CROSS_VERIFIED\nSOURCES: foo. [VERIFY:current]\n\n[HARD]")
    # the excused form passes
    check_no_unresolved_verify_above_draft(
        "x", "TIER: CROSS_VERIFIED\nSOURCES: foo ([VERIFY:current] on the "
             "edition -- not load-bearing).\n\n[HARD]")
    with pytest.raises(AssertionError):
        check_engineering_declaration(
            "SCALE: AIAG-VDA FMEA severity 1-10\n  CRITICAL LEVEL: 9\n"
            "  LEVELS: 7-8 high; 9-10 safety or regulatory")
    with pytest.raises(AssertionError):
        check_gate_independence("CRITICAL_SEVERITY_THRESHOLD = 0.7\n"
                                "x = manifest['critical_level']",
                                "clean")
    with pytest.raises(AssertionError):
        check_gate_independence("CRITICAL_SEVERITY_THRESHOLD = 0.9", "clean")
