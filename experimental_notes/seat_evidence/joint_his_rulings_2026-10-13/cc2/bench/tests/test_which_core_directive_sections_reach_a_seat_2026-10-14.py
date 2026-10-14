# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'joint_his_rulings_2026-10-13', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 2a94d78892bfc79952da04b9331c248f855f4f8dfdc85234cf26ec7c3ba913d9
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""J4, 2026-10-14: WHICH core-directive sections reach a seat, measured.

THE FACT THIS PINS, AND IT IS A DEFECT, NOT A DESIGN

`bench/directives/universal/cdsfl_core_formal.md` is 27,803 characters in 15
`## ` sections. `_load_universal_directive` (bench/cdsfl_registry/composer.py)
compares that length against the model's `max_directive_chars` -- the largest
cap is 12,000 -- so `use_minimal` is True for EVERY model on EVERY compose, and
every seat receives `_render_universal_minimal()` instead: 2,503 characters,
which is 2503/27803 = 9.0026% of the file and reproduces the recorded C0040
figure exactly. 0 of the 15 section headings survive.

This is the `max_directive_chars` transport cap on the universal layer. It is
NOT `_prune_for_coherence`, so retiring the pruner on 2026-10-13 did not touch
it, and the retirement must not be read as having closed C0040.

WHAT REACHES A SEAT AND WHAT DOES NOT -- the two-sided part, which is the point

Measured on the real assembly (composer rendered_text + the operational
directive, which is appended in full and is exempt from the caps):

  * The RUNNABLE-FALSIFIER MANDATE *does* reach seats -- but via
    `_gate_falsifier_directive`, not via the directive file. With the falsifier
    gate on (`_FALSIFIER_GATE = {"on": True}`, the live default) the §2 rewrite
    injects "falsifier" x2, "FALSIFIED" x1 and "execute_python" x1. So the
    brief's framing that the falsification machinery "was not reaching any
    seat" is too strong, and this file asserts the gate path keeps working: if
    that rewrite ever regresses, the mandate reaches nobody by any route and
    this test goes red.

  * The FALSIFIER-INTEGRITY SECTION reaches NO seat by ANY route. "Falsifier
    Integrity -- Do Not Reach for the Answer" exists only in
    cdsfl_core_formal.md (0 occurrences in cdsfl_operational.md), and the
    minimal rendering drops it. Its content is the do-not-read-the-scoring-key,
    do-not-weaken-a-test, do-not-assert-an-uncomputed-verdict and
    do-not-terminate-early prohibitions -- the ones the section itself says
    cannot be carried by a principle because "do not cheat" is filtered out by
    the very reasoning it was meant to catch. The gate rewrite does not
    substitute for them.

WHY THESE ASSERTIONS ARE WRITTEN THE WAY THEY ARE

They pin the MEASURED CURRENT STATE, including the state that is wrong. That is
this project's idiom for a defect whose repair is a policy decision the founder
owns (what text every seat must receive is his call, and changing it changes
every prompt and every future run's comparability). The assertion on the
integrity section is written to FAIL LOUDLY WHEN THE DEFECT IS FIXED, and says
so in its own message: when delivery is repaired, REPLACE that assertion with
its positive form (integrity text present) and cite the ruling here. Do not
delete it and do not loosen it.
"""

from __future__ import annotations

import warnings

import pytest

from bench.cdsfl_registry import composer as C
from bench.cdsfl_registry.composer import PHENOTYPE_TRANSFORMS

CORE = C.DIRECTIVES_DIR / "universal" / "cdsfl_core_formal.md"
OPER = C.DIRECTIVES_DIR / "universal" / "cdsfl_operational.md"


def _assembled(model: str = "deepseek_v3", gate: bool = True) -> str:
    """The prompt a seat actually receives, assembled as the runner assembles it.

    Mirrors bench/reference_runner_v3.py: composer rendered_text, then the
    operational directive appended in full, then the gate's §2 rewrite.
    """
    import bench.reference_runner_v3 as rr

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        composed = C.compose(
            task_domain="software", model=model,
            review_target="bench/dm/_convergence.py", code_extracts="x = 1")
    text = composed.rendered_text + "\n\n" + OPER.read_text(encoding="utf-8")
    return rr._gate_falsifier_directive(text, False) if gate else text


class TestTheUniversalLayerIsTruncatedForEverySeat:
    def test_the_file_still_exceeds_every_cap(self):
        """ANTI-VACUITY: if a trim ever lands, this is the first thing to know."""
        full = len(CORE.read_text(encoding="utf-8"))
        caps = {m: t.max_directive_chars for m, t in PHENOTYPE_TRANSFORMS.items()}
        assert full > max(caps.values()), (
            "cdsfl_core_formal.md now fits the largest cap (%d <= %d) -- the "
            "minimal rendering may no longer be unconditional; re-measure "
            "before trusting the rest of this file" % (full, max(caps.values()))
        )

    def test_every_seat_gets_the_same_universal_text(self):
        """The founder's determinism ground for retiring the pruner, as a test.

        He retired it partly so "the models get fed the same set of core
        directives every single time". On the universal layer that now holds:
        the delivered text is byte-identical across all five seats.
        """
        texts = {m: C._load_universal_directive(model=m).text
                 for m in PHENOTYPE_TRANSFORMS}
        assert len(set(texts.values())) == 1, (
            "seats receive DIFFERENT universal text: %s"
            % {m: len(t) for m, t in texts.items()})

    def test_the_delivered_share_is_the_recorded_C0040_figure(self):
        """9.0026% of the universal directive, and no heading at all."""
        full = CORE.read_text(encoding="utf-8")
        delivered = C._load_universal_directive(model="opus_4_6").text
        share = len(delivered) / len(full)
        assert abs(share - 0.090026) < 1e-5, (
            "delivered share moved to %.6f%% -- C0040's recorded 9.0026%% is "
            "stale and every document quoting it needs re-measuring"
            % (100 * share))
        headings = [l.strip("# ").strip() for l in full.splitlines()
                    if l.startswith("## ")]
        assert len(headings) == 15
        survivors = [h for h in headings if h in delivered]
        assert survivors == [], (
            "headings now survive the minimal rendering: %s -- this is an "
            "IMPROVEMENT; replace this assertion with the positive form"
            % survivors)


class TestWhatTheGatePathDoesAndDoesNotCarry:
    def test_the_runnable_falsifier_mandate_reaches_the_seat_via_the_gate(self):
        """POSITIVE assertion. The mandate arrives -- by the gate, not the file."""
        gated = _assembled(gate=True)
        plain = _assembled(gate=False)
        assert gated != plain, (
            "the §2 falsifier rewrite is a no-op on the assembled prompt -- the "
            "runnable-falsifier mandate now reaches seats by NO route at all"
        )
        assert gated.count("falsifier") >= 2
        assert "execute_python" in gated
        assert "FALSIFIED" in gated

    def test_the_integrity_section_reaches_no_seat_by_any_route(self):
        """PINS THE DEFECT. Fails loudly when it is fixed -- read the message.

        "Falsifier Integrity -- Do Not Reach for the Answer" is in the core
        formal file only, and the minimal rendering drops it.
        """
        core = CORE.read_text(encoding="utf-8")
        oper = OPER.read_text(encoding="utf-8")
        assert "Falsifier Integrity" in core
        assert "Falsifier Integrity" not in oper, (
            "the integrity section now exists in the operational directive, "
            "which IS delivered in full -- the defect is fixed; replace this "
            "whole test with the positive form and cite the ruling")
        gated = _assembled(gate=True)
        # The section's own load-bearing prohibitions, by their own words.
        for phrase in ("Falsifier Integrity",
                       "Do Not Reach for the Answer",
                       "scoring key"):
            assert phrase not in gated, (
                "%r now reaches the seat -- the delivery defect is REPAIRED. "
                "Replace this assertion with its positive form (assert the "
                "phrase IS present) and cite the ruling that repaired it. Do "
                "not delete this test and do not loosen it." % phrase)

    def test_the_sections_that_never_arrive_are_enumerated_not_summarised(self):
        """A count is not evidence of which sections are missing."""
        full = CORE.read_text(encoding="utf-8")
        headings = [l.strip("# ").strip() for l in full.splitlines()
                    if l.startswith("## ")]
        gated = _assembled(gate=True)
        missing = [h for h in headings if h not in gated]
        # 14 of 15: "1. Constraint Classification" survives because the minimal
        # rendering reproduces that phrase, not because the section arrives.
        assert len(missing) >= 14, (
            "more sections now reach the seat than when this was measured "
            "(%d of 15 missing) -- re-measure and update in place"
            % len(missing))
        assert "Runnable Falsifiers for Critical Findings" in missing
        assert "Falsifier Integrity — Do Not Reach for the Answer" in missing


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
