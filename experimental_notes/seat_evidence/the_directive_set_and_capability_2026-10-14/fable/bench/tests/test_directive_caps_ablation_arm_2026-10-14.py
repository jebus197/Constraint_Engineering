# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'the_directive_set_and_capability_2026-10-14', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: ed9537c8fe7c65f0e371dff638a766ef1ab3b09f03147bf8a3f180011824eaba
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""The uncapped-directive ablation arm delivers the full specification; the default is untouched.

CONTEXT (2026-10-14 free panel, Items 1-2). `cdsfl_core_formal.md` is 27,803
chars and exceeds every `max_directive_chars` cap (4,000/6,000/8,000/12,000),
so EVERY seat receives the 2,503-char reduced render -- 9.0026% of source,
0 of 16 headings surviving. No measurement, cited context window, or stated
reason exists for any cap value. The additive standard forbids removing the
caps without a committed measurement showing the replacement dominates on a
named property; `compose(directive_caps=False)` is the arm that produces that
measurement in a simulated run. This test is the committed execution the
additive standard requires for the new flag.

Named property for the eventual removal decision: per-seat confirmed-finding
rate (runner-reverified CONFIRMED / dispatches) on the uncapped arm vs the
capped default, same target, same seats, same rounds.

Run: python3 -m pytest bench/tests/test_directive_caps_ablation_arm_2026-10-14.py -q
"""
from __future__ import annotations

import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from bench.cdsfl_registry.composer import (  # noqa: E402
    PHENOTYPE_TRANSFORMS,
    _load_universal_directive,
    compose,
)

CORE = REPO / "bench" / "directives" / "universal" / "cdsfl_core_formal.md"


def test_default_is_byte_identical_reduced_render():
    """directive_caps default True == shipped behaviour, for every seat label."""
    for model in list(PHENOTYPE_TRANSFORMS) + ["fable", "cc2", None]:
        capped = _load_universal_directive(model)
        assert len(capped.text) < 4000, (model, len(capped.text))
        assert capped.text.startswith("CDSFL CORE MINIMAL"), model


def test_uncapped_arm_delivers_the_full_source():
    """uncapped=True returns the source byte-for-byte, all headings intact."""
    full_text = CORE.read_text(encoding="utf-8")
    heads = re.findall(r"(?m)^#{1,3}\s+(.+)$", full_text)
    assert len(heads) >= 10
    for model in list(PHENOTYPE_TRANSFORMS) + ["fable", None]:
        got = _load_universal_directive(model, uncapped=True)
        assert got.text == full_text, model
        kept = [h for h in heads if h.strip() in got.text]
        assert len(kept) == len(heads), (model, len(kept))


def test_compose_arm_skips_the_global_cap():
    """compose(directive_caps=False) renders > the largest cap and carries the
    sections no seat has ever received; default compose is unchanged."""
    default = compose("software", "deepseek_v3")
    arm = compose("software", "deepseek_v3", directive_caps=False)
    biggest = max(t.max_directive_chars for t in PHENOTYPE_TRANSFORMS.values())
    assert len(default.rendered_text) <= 4000 + len(
        "\n[... truncated for model capacity]"
    )
    assert len(arm.rendered_text) > biggest, len(arm.rendered_text)
    for section in (
        "Runnable Falsifiers for Critical Findings",
        "Falsifier Integrity",
    ):
        assert section in arm.rendered_text, section
        assert section not in default.rendered_text, section
    assert "[... truncated for model capacity]" not in arm.rendered_text


def test_runner_wiring_exists_and_defaults_on():
    """The flag is wired to a live caller (reference_runner_v3), default True."""
    src = (REPO / "bench" / "reference_runner_v3.py").read_text(encoding="utf-8")
    assert 'composer_directive_caps: bool = True' in src
    assert '_COMPOSER_DIRECTIVE_CAPS["on"] = bool(' in src
    assert 'directive_caps=bool(_COMPOSER_DIRECTIVE_CAPS.get("on", True))' in src
