"""Capability is measured per hashed identity, and a vendor name decides nothing.

TASK C18. HIS WORDS, 2026-10-16, asking why this had not been built: *"I'm sure
we already just discussed this and you said there had been significant panel
review work on this feature and that replacing model names with hashed model IDs
was gauged by you and the other models to be a sound overall design. ... Why
didn't you do that yet?"* And: *"the only thing that governs capability is
demonstrated measured capability, not model names."*

THE DESIGN, as put to the free panel on 2026-10-14 and quoted from that brief:
*"Key every capability decision on a STABLE IDENTITY -- a hash over (provider,
model identifier, version) -- with the vendor name recorded as PROVENANCE and
deciding nothing."*

WHAT IS BUILT AND WHAT IS NOT. `capability_identity` is the hash;
`capability_provenance` carries the readable triple for a reader;
`falsification_evidence_by_identity` pools a seat's falsification outcomes onto
the identity it resolves to; and `season_strength_order` ranks IDENTITIES and
then orders the seats by the rank of the identity each carries. RETIRING
`DEFAULT_FALSIFIER_STRENGTH` -- the other half of the panel design -- is NOT done
here, because emptying it collides with his earlier 2026-10-07 ruling about
ladder MEMBERSHIP, and that collision is already recorded for him beside the
constant. The fallback therefore still exists, and the measured improvement
below is that it is reached LESS OFTEN.

THE MEASURED JUSTIFICATION, by execution. Two seats of one model against one
seat of another, with falsification outcomes of 2 refuted of 2 and 2 of 2
against 0 of 4:

  * ranked PER SEAT    -- does NOT establish, and falls back to the vendor tuple
  * ranked PER IDENTITY -- DOES establish, returning a measured order

Pooling both raises the sample per identity and cuts the number of comparisons
Holm must correct for -- 1 pair instead of 3 -- so a measurement survives where
it previously did not. And it does not fabricate: with 2 of 2, 1 of 2 and 0 of 4
it still refuses.
"""
from __future__ import annotations

import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]

PAIRED = {"A1": "m-alpha@anthropic", "A2": "m-alpha@anthropic",
          "B": "m-beta@openrouter"}
LABELS = ["A1", "A2", "B"]


class _Registry:
    """The minimum a registry must offer: entries and `resolve_model`."""

    def __init__(self, entries, identity):
        self.entries = entries
        self.model_identity = identity

    def resolve_model(self, label):
        return str(self.model_identity.get(str(label).strip(), label)).lower()


def _registry(counts, identity=None):
    entries, n = {}, 0
    for seat, (refuted, total) in counts.items():
        for k in range(total):
            n += 1
            entries[n] = {
                "source_model": seat,
                "falsifier_verdict": "REFUTED" if k < refuted else "CONFIRMED"}
    return _Registry(entries, dict(identity or PAIRED))


@pytest.fixture(scope="module")
def rt():
    from bench import routing as mod
    return mod


# --------------------------------------------------------------------------
# The identity itself.
# --------------------------------------------------------------------------

def test_the_identity_is_stable_and_normalised(rt):
    base = rt.capability_identity("anthropic", "claude-opus-4-8")
    assert base == rt.capability_identity("Anthropic", " Claude-Opus-4-8 ")
    assert base == rt.capability_identity("ANTHROPIC", "claude-opus-4-8")
    assert len(base) == rt.CAPABILITY_IDENTITY_CHARS
    assert base == rt.capability_identity("anthropic", "claude-opus-4-8")


def test_a_stand_in_shares_the_identity_it_stands_in_for(rt):
    """Under-separating is the conservative direction, so it is chosen."""
    assert (rt.capability_identity("anthropic", "claude-opus-4-8-SIM")
            == rt.capability_identity("anthropic", "claude-opus-4-8"))


@pytest.mark.parametrize("a,b", [
    (("anthropic", "claude-opus-4-8"), ("openrouter", "claude-opus-4-8")),
    (("anthropic", "claude-opus-4-8"), ("anthropic", "claude-opus-4-9")),
    (("anthropic", "claude-opus", "4.8"), ("anthropic", "claude-opus", "4.9")),
])
def test_a_different_triple_is_a_different_identity(rt, a, b):
    assert rt.capability_identity(*a) != rt.capability_identity(*b)


def test_an_empty_identifier_is_refused_not_hashed(rt):
    """An identity derived from nothing is stable, shared, and silently wrong."""
    with pytest.raises(ValueError):
        rt.capability_identity("anthropic", "")
    with pytest.raises(ValueError):
        rt.capability_identity("", "   ")


def test_the_identity_does_not_contain_the_vendor_name(rt):
    """A digest cannot be read as a vendor, which is the whole point.

    If the identity were readable, a ranking keyed on it could smuggle a name
    back into a capability decision -- the practice he has rejected 4 times.
    """
    for vendor in ("anthropic", "openai", "google", "deepseek", "openrouter"):
        ident = rt.capability_identity(vendor, f"{vendor}-model-1")
        assert vendor not in ident.lower()
    assert all(c in "0123456789abcdef"
               for c in rt.capability_identity("anthropic", "claude"))


def test_provenance_carries_the_readable_triple(rt):
    rec = rt.capability_provenance("anthropic", "claude-opus-4-8", "4.8")
    assert rec["identity"] == rt.capability_identity(
        "anthropic", "claude-opus-4-8", "4.8")
    assert rec["provider"] == "anthropic"
    assert rec["model_identifier"] == "claude-opus-4-8"
    assert rec["version"] == "4.8"


# --------------------------------------------------------------------------
# The wiring, which is what makes it additive.
# --------------------------------------------------------------------------

def test_two_seats_of_one_model_pool_their_outcomes(rt):
    reg = _registry({"A1": (6, 6), "A2": (6, 6), "B": (0, 12)})
    per_seat = rt.falsification_evidence_from_registry(reg)
    assert per_seat == {"A1": (6, 6), "A2": (6, 6), "B": (0, 12)}
    pooled, seat_to_identity = rt.falsification_evidence_by_identity(reg, LABELS)
    assert seat_to_identity["A1"] == seat_to_identity["A2"]
    assert seat_to_identity["A1"] != seat_to_identity["B"]
    assert sorted(pooled.values()) == [(0, 12), (12, 12)]
    assert len(pooled) == 2, "the pair did not pool onto one identity"


def test_pooling_recovers_a_measurement_the_seat_route_loses(rt):
    """THE MEASURED JUSTIFICATION. Per seat this defaults; per identity it does not.

    2 refuted of 2 and 2 of 2 against 0 of 4. Per seat there are 3 pairs for Holm
    to correct and none survives, so the vendor tuple is returned. Per identity
    there is 1 pair, it survives, and the order is measured.
    """
    counts = {"A1": (2, 2), "A2": (2, 2), "B": (0, 4)}
    reg = _registry(counts)
    _, seat_established, _ = rt.strength_order_from_evidence(
        rt.falsification_evidence_from_registry(reg), labels=LABELS)
    assert seat_established is False, (
        "the per-seat route now establishes on this evidence, so it no longer "
        "demonstrates the gain; find weaker evidence or retire this assertion")
    order, established, why = rt.season_strength_order(_registry(counts), LABELS)
    assert established is True, why
    assert order == ("A1", "A2", "B"), order
    assert "capability identity" in why


def test_it_still_refuses_when_the_evidence_does_not_separate(rt):
    """ANTI-FABRICATION. The gain must not come from a lowered bar."""
    reg = _registry({"A1": (2, 2), "A2": (1, 2), "B": (0, 4)})
    order, established, why = rt.season_strength_order(reg, LABELS)
    assert established is False, (
        f"a ranking was established on evidence that does not separate: {why}")
    assert tuple(order) == tuple(rt.DEFAULT_FALSIFIER_STRENGTH), (
        "the unestablished path must return the recorded fallback, and say so")
    assert "no measurement" in why or "rests on no" in why


def test_a_frozen_season_still_wins(rt):
    """His season rule outranks all of this: measured once, then kept."""
    reg = _registry({"A1": (6, 6), "A2": (6, 6), "B": (0, 12)})
    order, established, why = rt.season_strength_order(
        reg, LABELS, frozen=("B", "A2", "A1"))
    assert order == ("B", "A2", "A1")
    assert established is True
    assert "stay fixed" in why


def test_an_unresolvable_seat_gets_its_own_identity(rt):
    """Over-separating preserves findings, so an unknown label is not pooled."""
    reg = _registry({"A1": (2, 2), "ZZ": (2, 2)},
                    identity={"A1": "m-alpha@anthropic"})
    pooled, seat_to_identity = rt.falsification_evidence_by_identity(
        reg, ["A1", "ZZ"])
    assert seat_to_identity["A1"] != seat_to_identity["ZZ"]
    assert len(pooled) == 2


def test_the_runner_still_reaches_the_season_order():
    """ANTI-UNWIRED. An identity nothing uses is the failure mode he names."""
    src = (REPO / "bench" / "reference_runner_v3.py").read_text(encoding="utf-8")
    assert "season_strength_order" in src, (
        "the runner no longer calls the season order, so the identity pooling "
        "reaches nothing")


def test_an_unmeasured_identity_is_named_not_silently_defaulted(rt):
    """HIS DESIGN CLAUSE: *"An identity absent from the tables must be LOUD,
    never defaulted."*

    Before this the fallback said it WAS a fallback but not WHICH seats went
    unmeasured, so a roster with no evidence and a roster whose evidence failed
    to separate produced the same sentence -- two different situations a reader
    needs to tell apart.
    """
    reg = _registry({"A1": (2, 2)},
                    identity={"A1": "m-alpha@anthropic",
                              "NEW": "m-new@anthropic"})
    _, established, why = rt.season_strength_order(reg, ["A1", "NEW"])
    assert established is False
    assert "NO falsification evidence" in why, why
    assert "NEW" in why, (
        f"the unmeasured seat is not named, so a reader cannot tell which "
        f"identity was absent: {why}")
    # AND THE IDENTITY TRAVELS WITH IT, so the name is provenance and the
    # digest is what the capability tables are keyed on.
    assert rt.capability_identity("anthropic", "m-new") in why, why


def test_a_measured_order_says_nothing_about_unmeasured_seats(rt):
    """The loud clause must not fire when there is nothing to be loud about."""
    reg = _registry({"A1": (6, 6), "A2": (6, 6), "B": (0, 12)})
    _, established, why = rt.season_strength_order(reg, LABELS)
    assert established is True
    assert "NO falsification evidence" not in why, why
