# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'the_directive_set_and_capability_2026-10-14', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: a9dca2426aa4070dda31e47f8de10c34beed6d551d0cc72bd83f6d14c69d213b
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""`max_directive_chars` is inert over its configured range, and `Fable` is unmapped.

Companion producer: `scripts/directive_cap_is_inert_2026-10-14.py`.

WHAT IS PINNED, AND WHY EACH ASSERTION IS SHAPED AS IT IS
---------------------------------------------------------
The 2026-10-13 guard `test_falsifier_C0040_universal_directive_2026-09-10.py`
established that the universal directive is reduced for every seat. It did not
establish WHY, and the difference decides the fix. This file separates three
claims that were being argued as one:

  A. The cap's VALUE is inert. Delivery is identical at 4000, 6000, 8000 and
     12000. So the four values carry one behaviour between them, and no
     measurement can distinguish them -- which is the "addition nothing
     reaches" class the additive standard names. Asserted as a derived
     property of the transfer function, not as a hardcoded 2503.

  B. The cap RAISES below the minimal render's own length. Any cap under
     ~2.5k -- an entirely plausible value for a genuinely small-context model,
     i.e. the case the parameter exists to serve -- makes composition raise
     ValueError. So the parameter is inert where it is used and raises where it
     would matter.

  C. `Fable` resolves through NEITHER name-keyed table. This is the realised
     2026-08-30 failure ("Fable had no COMPOSER_MODEL_MAP entry and no .toml,
     so it composed to FileNotFoundError -> 0 chars"), still present in a
     quieter form: the label now silently inherits the 8000 default.

ON PINNING A DEFECT RATHER THAN A FIX. A, B and C assert the CURRENT measured
behaviour, deliberately. Each will fail the moment the behaviour changes, and
that failure is the signal to REPLACE the assertion with the sharper
post-change one named in its own docstring -- never to loosen it. The
post-change properties are stated in `test_delivery_audit_is_the_instrument`,
which holds in both regimes and is the assertion to keep.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from bench.cdsfl_registry.composer import (  # noqa: E402
    COMPOSER_MODEL_MAP,
    KNOWN_SEAT_LABELS,
    PHENOTYPE_TRANSFORMS,
    PhenotypeTransform,
    DIRECTIVES_DIR,
    _extract_hard_behavioural_directives,
    _load_universal_directive,
    _render_universal_minimal,
    directive_delivery_audit,
    directive_delivery_record,
)

_PROBE = "__cap_inert_test_probe__"


def _deliver_at(cap: int) -> int:
    """Deliver Layer 1 with only `max_directive_chars` varied."""
    PHENOTYPE_TRANSFORMS[_PROBE] = PhenotypeTransform(
        max_directive_chars=cap, format_style="concise"
    )
    try:
        return len(_load_universal_directive(_PROBE).text)
    finally:
        PHENOTYPE_TRANSFORMS.pop(_PROBE, None)


def _configured_caps() -> list[int]:
    return sorted({t.max_directive_chars for t in PHENOTYPE_TRANSFORMS.values()}
                  | {PhenotypeTransform().max_directive_chars})


# -- A. the cap's value is inert ------------------------------------------

def test_cap_value_is_inert_across_every_configured_value():
    """Every configured cap yields the SAME delivery, so the value decides nothing.

    WHEN THIS FAILS: the caps have become live (or been removed). Replace this
    assertion with one that pins the intended per-seat delivery lengths
    directly, naming the measurement that chose them.
    """
    caps = _configured_caps()
    assert len(caps) > 1, "expected several configured cap values to compare"
    delivered = {cap: _deliver_at(cap) for cap in caps}
    assert len(set(delivered.values())) == 1, (
        f"cap values now differentiate delivery: {delivered} -- the inertness "
        f"finding is REFUTED and this test must be replaced, not relaxed"
    )


def test_configured_caps_all_sit_inside_the_flat_interval():
    """Derived, not hardcoded: the flat interval is [len(minimal), len(source)).

    dDelivery/dCap = 0 for any cap in that interval, and every configured value
    lies in it. This is the derivation behind the inertness, so it is asserted
    separately from the observation.
    """
    minimal_len = len(_render_universal_minimal())
    source_len = directive_delivery_record("opus_4_6")["source_chars"]
    assert minimal_len < source_len
    # Stated over the EFFECTIVE cap. Sharpened 2026-10-14 after the derived
    # floor landed: deepseek_v3's configured 4,000 now sits BELOW the interval,
    # and the old form of this assertion read that as the derivation breaking
    # when in fact the clamp was working. The invariant that actually holds --
    # and the one worth pinning -- is over the value the loader uses.
    for transform in PHENOTYPE_TRANSFORMS.values():
        cap = transform.effective_cap
        assert minimal_len <= cap < source_len, (
            f"effective cap {cap} is outside the flat interval "
            f"[{minimal_len}, {source_len}) -- the derivation no longer holds"
        )
        assert _deliver_at(cap) == minimal_len


def test_delivery_is_a_step_function_with_one_step_at_the_source_length():
    minimal_len = len(_render_universal_minimal())
    source_len = directive_delivery_record("opus_4_6")["source_chars"]
    assert _deliver_at(source_len - 1) == minimal_len
    assert _deliver_at(source_len) == source_len
    assert _deliver_at(source_len + 10_000) == source_len


# -- B. the cap raises where it would matter ------------------------------

@pytest.mark.parametrize("cap", [1, 500, 1000, 2000])
def test_a_cap_below_the_floor_is_clamped_and_still_delivers_every_directive(cap):
    """REPLACES a weaker assertion, and the replacement is stated in place.

    The first version of this test asserted that a cap below the minimal
    render's length RAISES ValueError, which is what the code did on
    2026-10-14. That assertion pinned a crash as if it were a contract. It was
    REPLACED, not relaxed, when `PhenotypeTransform.effective_cap` derived a
    floor from the render's own length: the sharper property is that NO cap,
    however small, can cost a seat a HARD directive. That is strictly stronger
    -- it holds for cap=1, which the old test never covered -- and it is the
    property the parameter should always have had.
    """
    floor = len(_render_universal_minimal())
    assert cap < floor
    PHENOTYPE_TRANSFORMS[_PROBE] = PhenotypeTransform(
        max_directive_chars=cap, format_style="concise"
    )
    try:
        transform = PHENOTYPE_TRANSFORMS[_PROBE]
        assert transform.effective_cap == floor, "the cap must be clamped up"
        text = _load_universal_directive(_PROBE).text
    finally:
        PHENOTYPE_TRANSFORMS.pop(_PROBE, None)
    assert len(text) == floor
    # Every HARD behavioural directive must survive the smallest possible cap.
    for directive in _extract_hard_behavioural_directives(
        (DIRECTIVES_DIR / "universal" / "cdsfl_core_formal.md").read_text(
            encoding="utf-8"
        )
    ):
        assert directive in text, (
            f"cap={cap} dropped a HARD directive: {directive[:60]!r}"
        )


def test_the_floor_is_derived_from_the_render_not_typed():
    """A typed floor would fall behind the next added directive. On 2026-10-14
    the render went from 2,503 to 4,603 characters when the worked-proof and
    falsifier-integrity directives were added, which immediately exceeded
    deepseek_v3's configured 4,000. A derived floor tracks that; a constant
    would have had to be re-typed, which is how the 4,000 got stale."""
    floor = len(_render_universal_minimal())
    for transform in PHENOTYPE_TRANSFORMS.values():
        assert transform.effective_cap >= floor
        assert transform.effective_cap == max(
            transform.max_directive_chars, floor
        )
    # The floor is live: at least one CONFIGURED cap is below it, so the clamp
    # is doing work rather than being decoration.
    assert any(t.max_directive_chars < floor for t in PHENOTYPE_TRANSFORMS.values()), (
        "no configured cap is below the floor -- the clamp is now unreached, "
        "which makes it an addition nothing reaches. Either a cap moved or a "
        "directive was removed; say which here."
    )


def test_a_composition_failure_is_recorded_not_swallowed():
    """If composition ever DOES raise, `directive_delivery_record` must report
    it rather than return a short prompt as if nothing happened. The 2026-08-30
    incident was a silent 0-char prompt; an unrecorded exception is the same
    class of event. Driven by monkeypatching the renderer, because the floor now
    makes the natural route unreachable -- which is the point of the floor."""
    import bench.cdsfl_registry.composer as comp

    original = comp._render_universal_minimal

    def boom(*a, **k):
        raise ValueError("Minimal universal directive too large: synthetic")

    comp._render_universal_minimal = boom
    PHENOTYPE_TRANSFORMS[_PROBE] = PhenotypeTransform(
        max_directive_chars=1000, format_style="minimal"
    )
    try:
        rec = directive_delivery_record(_PROBE)
    finally:
        comp._render_universal_minimal = original
        PHENOTYPE_TRANSFORMS.pop(_PROBE, None)
    assert rec["error"], "a raising composition must surface in the record"
    assert "ValueError" in rec["error"]
    assert "delivered_chars" not in rec, (
        "a failed composition must not report a delivered length"
    )


def test_the_added_operative_directives_reach_every_seat():
    """The ADD half of Item 1, verified by executing the composer.

    An addition to `cdsfl_core_formal.md` outside the two extracted sections
    would be an addition nothing reaches -- the defect class this project has
    recorded 11 times. These five requirements are checked at the seat, not at
    the source file.
    """
    required = (
        "Show the working for every number you state",
        "Use the residual-risk model to set severity",
        "DERIVE every mathematical result you assert",
        "Attach a runnable falsifier to every critical finding",
        "Never derive a verdict from material that encodes the answer",
    )
    audit = directive_delivery_audit()
    assert audit["records"], "no seats audited"
    for label, rec in audit["records"].items():
        text = _load_universal_directive(rec["resolved_to"]).text
        for phrase in required:
            assert phrase in text, f"{label} never receives: {phrase!r}"


def test_no_delivered_directive_carries_a_section_boundary():
    """A heading, rule or blockquote bleeding into a bullet both corrupts a HARD
    directive and spends the budget the floor protects. Observed 2026-10-14."""
    text = _render_universal_minimal()
    for line in text.splitlines():
        if not line.startswith("behaviour."):
            continue
        assert "##" not in line, f"heading bled into a directive: {line[:80]!r}"
        assert "---" not in line, f"rule bled into a directive: {line[:80]!r}"
        assert ">" not in line, f"blockquote bled into a directive: {line[:80]!r}"


# -- C. Fable resolves through neither table ------------------------------

def test_fable_is_absent_from_both_name_keyed_tables():
    """WHEN THIS FAILS: Fable has been given an entry, or name-keying has been
    replaced by the stable identity of `bench/capability_identity.py`. Replace
    this with an assertion that EVERY roster identity resolves, which is the
    property that actually matters and does not need updating per vendor."""
    assert "Fable" not in COMPOSER_MODEL_MAP
    assert "Fable" not in PHENOTYPE_TRANSFORMS
    assert "fable" not in PHENOTYPE_TRANSFORMS
    assert "Fable" in KNOWN_SEAT_LABELS, (
        "Fable is a live seat label; if it has left the roster say so here"
    )


def test_every_seat_receives_the_identical_reduced_text():
    """One render across all seats. The phenotype layer differentiates nothing."""
    audit = directive_delivery_audit()
    assert audit["distinct_delivered_chars"] == [len(_render_universal_minimal())]
    assert all(r["delivered_headings"] == 0 for r in audit["records"].values())
    assert all(r["source_headings"] > 0 for r in audit["records"].values())


# -- the instrument itself, which must hold in BOTH regimes ---------------

def test_delivery_audit_is_the_instrument():
    """The audit must agree with the dispatch path it claims to measure.

    This is the assertion to KEEP when the others are replaced: it pins
    producer/consumer agreement rather than any particular delivery size, so it
    holds whether the caps stay, change, or go.
    """
    audit = directive_delivery_audit()
    assert set(audit["records"]) == set(KNOWN_SEAT_LABELS)
    for label, rec in audit["records"].items():
        resolved = COMPOSER_MODEL_MAP.get(label, label)
        assert rec["resolved_to"] == resolved
        # Execute the consumer and compare, rather than trusting the record.
        assert rec["delivered_chars"] == len(
            _load_universal_directive(resolved).text
        ), f"audit disagrees with the live loader for {label}"
        assert rec["reduced"] == (
            rec["delivered_chars"] != rec["source_chars"]
        )
    # The roll-ups must be derivable from the records, not separately computed.
    assert audit["unmapped"] == [
        l for l, r in audit["records"].items() if l not in COMPOSER_MODEL_MAP
    ]
    assert audit["silently_defaulted"] == [
        l for l, r in audit["records"].items() if not r["has_transform_entry"]
    ]


def test_audit_accepts_an_explicit_label_set():
    """Wired for the runner, which knows its own roster and should pass it."""
    audit = directive_delivery_audit(["CC2", "Gemini"])
    assert set(audit["records"]) == {"CC2", "Gemini"}
    assert audit["unmapped"] == []
