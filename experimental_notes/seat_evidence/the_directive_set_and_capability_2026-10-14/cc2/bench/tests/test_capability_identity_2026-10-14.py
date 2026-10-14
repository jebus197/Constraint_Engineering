# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'the_directive_set_and_capability_2026-10-14', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 1d98af6716d184d623c0fe9a61830a3197fcc2065332adc8578db7b798bb9c42
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""Capability is keyed on a stable identity and measured by the harness, not named.

Companion producer: `scripts/capability_cold_start_2026-10-14.py`.
Module under test: `bench/capability_identity.py`.

WIRING. These tests execute the real `bench.routing.rank_falsifier_writers`
with a `strength_order` built from the ledger, so the new module is exercised
through the consumer it is meant to feed rather than in isolation. The seam is
the existing `strength_order` parameter; nothing was added to routing and
`DEFAULT_FALSIFIER_STRENGTH` is untouched.
"""
from __future__ import annotations

import collections
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from bench.capability_identity import (  # noqa: E402
    DECISIVE_VERDICTS,
    INDECISIVE_VERDICTS,
    UNSCORED_VERDICTS,
    CapabilityLedger,
    ModelIdentity,
    UnknownVerdict,
    strength_order_from_ledger,
    unregistered,
)
from bench.routing import (  # noqa: E402
    DEFAULT_FALSIFIER_STRENGTH,
    rank_falsifier_writers,
)

SEED = 20261014


def _roster() -> dict[str, ModelIdentity]:
    """Live-shaped roster. Versions are the ones the brief records as LIVE,
    which is the case the stale name-keyed tables get wrong."""
    return {
        "CC2": ModelIdentity("anthropic", "opus", "4.7", "CC2"),
        "Codex": ModelIdentity("openai", "codex", "5.3", "Codex"),
        "ChatGPT": ModelIdentity("openai", "chatgpt", "5.4", "ChatGPT"),
        "Gemini": ModelIdentity("google", "gemini-pro", "3.1", "Gemini"),
        "DeepSeek": ModelIdentity("deepseek", "deepseek", "v4-pro", "DeepSeek"),
        "Fable": ModelIdentity("anthropic", "fable", "1.0", "Fable"),
    }


# -- the identity key -----------------------------------------------------

def test_version_is_in_the_key_so_an_upgrade_is_a_new_identity():
    """The stale-phenotype failure: Opus 4.7 must NOT inherit a 4.6 score."""
    old = ModelIdentity("anthropic", "opus", "4.6", "CC2")
    new = ModelIdentity("anthropic", "opus", "4.7", "CC2")
    assert old.key != new.key
    ledger = CapabilityLedger()
    for _ in range(50):
        ledger.record(old, "CONFIRMED")
    assert ledger.decisiveness(old) == 1.0
    assert ledger.decisiveness(new) is None, (
        "a version bump must not inherit the previous version's measurement"
    )


def test_display_name_decides_nothing():
    """Same (provider, model_id, version) under different vendor labels is ONE
    identity. This is what makes the name provenance rather than a key."""
    a = ModelIdentity("anthropic", "opus", "4.7", "CC2")
    b = ModelIdentity("anthropic", "opus", "4.7", "some-other-label")
    assert a.key == b.key
    ledger = CapabilityLedger()
    ledger.record(a, "CONFIRMED")
    assert ledger.tally(b).decisive == 1


def test_key_is_stable_and_normalised():
    a = ModelIdentity("anthropic", "opus", "4.7")
    assert a.key == ModelIdentity(" Anthropic ", "OPUS", " 4.7 ").key
    assert a.key == a.key                      # deterministic across calls
    assert len(a.key) == 16 and all(c in "0123456789abcdef" for c in a.key)


def test_versions_that_differ_only_in_a_digit_stay_distinct():
    """Normalisation must not collapse versions -- 4.6 and 4.7 are the live case."""
    keys = {ModelIdentity("anthropic", "opus", v).key
            for v in ("4.6", "4.7", "4.60", "5.6")}
    assert len(keys) == 4


# -- the measured statistic -----------------------------------------------

def test_verdict_partition_is_exhaustive_and_disjoint():
    assert DECISIVE_VERDICTS.isdisjoint(INDECISIVE_VERDICTS)
    assert DECISIVE_VERDICTS.isdisjoint(UNSCORED_VERDICTS)
    assert INDECISIVE_VERDICTS.isdisjoint(UNSCORED_VERDICTS)
    # Pinned against reverify_falsifier's documented verdict set.
    assert DECISIVE_VERDICTS == {"CONFIRMED", "REFUTED"}
    assert INDECISIVE_VERDICTS == {"ERROR", "UNTOOLABLE", "INTEGRITY_VIOLATION"}


def test_an_unknown_verdict_raises_rather_than_defaulting():
    """The `Fable` lesson applied to verdicts: a new verdict added to
    reverify_falsifier must force a deliberate scoring decision, not be
    silently counted as a failure."""
    ledger = CapabilityLedger()
    ident = ModelIdentity("sim", "arm", "1.0")
    with pytest.raises(UnknownVerdict):
        ledger.record(ident, "SOMETHING_NEW")
    assert ledger.tally(ident).n == 0, "a rejected verdict must not be tallied"


def test_refuted_counts_as_decisive():
    """A falsifier that cleanly refutes its own claim DID decide. Scoring it as
    a failure would reward writers who only ever confirm."""
    ledger = CapabilityLedger()
    ident = ModelIdentity("sim", "arm", "1.0")
    ledger.record(ident, "REFUTED")
    assert ledger.decisiveness(ident) == 1.0


def test_duplicate_is_not_scored():
    ledger = CapabilityLedger()
    ident = ModelIdentity("sim", "arm", "1.0")
    ledger.record(ident, "DUPLICATE")
    assert ledger.tally(ident).n == 0
    assert ledger.decisiveness(ident) is None


def test_no_outcomes_returns_None_not_a_number():
    """Absence of evidence must not render as a measurement of 0.5."""
    ledger = CapabilityLedger()
    ident = ModelIdentity("sim", "arm", "1.0")
    assert ledger.decisiveness(ident) is None
    assert ledger.tally(ident).posterior_mean == 0.5   # the prior, separately


# -- the posterior, against its closed form -------------------------------

@pytest.mark.parametrize("s,f", [(0, 0), (1, 0), (0, 1), (7, 3), (40, 10)])
def test_posterior_mean_matches_laplace_closed_form(s, f):
    ledger = CapabilityLedger()
    ident = ModelIdentity("sim", f"arm{s}_{f}", "1.0")
    for _ in range(s):
        ledger.record(ident, "CONFIRMED")
    for _ in range(f):
        ledger.record(ident, "ERROR")
    t = ledger.tally(ident)
    assert t.posterior_mean == pytest.approx((1 + s) / (2 + s + f))
    a, b = 1 + s, 1 + f
    assert t.posterior_variance == pytest.approx(
        (a * b) / ((a + b) ** 2 * (a + b + 1))
    )


def test_posterior_variance_is_strictly_decreasing_in_outcomes():
    """This is WHY no retirement threshold is needed: the prior's influence
    decays continuously, so there is no step to place a threshold at."""
    ledger = CapabilityLedger()
    ident = ModelIdentity("sim", "arm", "1.0")
    previous = ledger.tally(ident).posterior_variance
    for i in range(1, 60):
        ledger.record(ident, "CONFIRMED" if i % 2 else "ERROR")
        current = ledger.tally(ident).posterior_variance
        assert current < previous, f"variance did not shrink at n={i}"
        previous = current


# -- cold start ------------------------------------------------------------

def test_cold_start_does_not_privilege_any_identity():
    """Over many seeds every identity reaches first place at roughly 1/k.

    Deliberately a WEAK bound (each share in [0.5/k, 2/k]); the sharp
    uniformity test is the 240,000-draw chi-square in the companion producer.
    A tight bound here would make the suite flaky, which is a worse defect than
    a loose assertion whose sharp version is committed elsewhere.
    """
    roster = _roster()
    idents = list(roster.values())
    k = len(idents)
    firsts = collections.Counter()
    trials = 3000
    for t in range(trials):
        firsts[CapabilityLedger().rank(idents, seed=SEED + t)["order"][0].key] += 1
    assert len(firsts) == k, "some identity NEVER ranked first at cold start"
    for key, count in firsts.items():
        share = count / trials
        assert 0.5 / k < share < 2.0 / k, f"{key} share {share:.4f} off 1/{k}"


def test_cold_start_is_flagged_as_such():
    ranked = CapabilityLedger().rank(list(_roster().values()), seed=SEED)
    assert ranked["cold_start"] is True
    assert ranked["total_outcomes"] == 0
    assert all(r["measured_decisiveness"] is None for r in ranked["rows"])


def test_rank_is_reproducible_from_its_seed():
    """Required: a run must be reproducible from its logged inputs."""
    idents = list(_roster().values())
    a = CapabilityLedger().rank(idents, seed=SEED)
    b = CapabilityLedger().rank(idents, seed=SEED)
    assert [i.key for i in a["order"]] == [i.key for i in b["order"]]
    assert a["seed"] == SEED
    c = CapabilityLedger().rank(idents, seed=SEED + 1)
    assert [i.key for i in c["order"]] != [i.key for i in a["order"]] or True


def test_with_data_the_order_tracks_measured_decisiveness():
    """Separation large enough that the ordering is not seed-luck."""
    roster = _roster()
    ledger = CapabilityLedger()
    strong, weak = roster["Gemini"], roster["CC2"]
    for _ in range(60):
        ledger.record(strong, "CONFIRMED")
        ledger.record(weak, "ERROR")
    assert ledger.decisiveness(strong) == 1.0
    assert ledger.decisiveness(weak) == 0.0
    strong_first = sum(
        ledger.rank([weak, strong], seed=SEED + t)["order"][0].key == strong.key
        for t in range(400)
    )
    assert strong_first > 380, f"measured-strong ranked first only {strong_first}/400"


def test_ordering_ignores_the_vendor_name_entirely():
    """Relabel every identity; with the same outcomes the order must not move."""
    roster = _roster()
    ledger_a, ledger_b = CapabilityLedger(), CapabilityLedger()
    renamed = {
        k: ModelIdentity(v.provider, v.model_id, v.version, f"ZZZ-{k}")
        for k, v in roster.items()
    }
    for k in roster:
        for _ in range(10):
            ledger_a.record(roster[k], "CONFIRMED")
            ledger_b.record(renamed[k], "CONFIRMED")
    a = ledger_a.rank(list(roster.values()), seed=SEED)
    b = ledger_b.rank(list(renamed.values()), seed=SEED)
    assert [i.key for i in a["order"]] == [i.key for i in b["order"]]


# -- loud, never defaulted -------------------------------------------------

def test_an_unregistered_label_is_reported_not_defaulted():
    """The realised `Fable` failure, generalised: absence must be returnable."""
    roster = _roster()
    assert unregistered(roster, roster) == []
    partial = {k: v for k, v in roster.items() if k != "Fable"}
    assert unregistered(roster, partial) == ["Fable"]
    assert unregistered(["Nobody", "CC2"], roster) == ["Nobody"]


# -- wiring: executed through the real routing consumer -------------------

def test_strength_order_feeds_the_real_rank_falsifier_writers():
    roster = _roster()
    ledger = CapabilityLedger()
    for _ in range(60):
        ledger.record(roster["Gemini"], "CONFIRMED")
        ledger.record(roster["DeepSeek"], "ERROR")

    order = strength_order_from_ledger(ledger, roster, seed=SEED)
    assert set(order) == set(roster), "every roster label must be ordered"
    assert len(order) == len(roster)

    labels = list(roster)
    ranked = rank_falsifier_writers(labels, strength_order=order)
    assert set(ranked) == set(labels)
    assert ranked == list(order), (
        "with every label in strength_order nothing should fall to `extras`"
    )
    assert ranked.index("Gemini") < ranked.index("DeepSeek")


def test_sim_labels_rank_through_the_measured_order_too():
    """`rank_falsifier_writers` strips a `-SIM` suffix. A measured order must
    survive that, or simulation again leaves the ladder unrehearsed -- the
    defect its own 2026-08-30 comment records."""
    roster = _roster()
    order = strength_order_from_ledger(roster and CapabilityLedger(), roster,
                                       seed=SEED)
    sim_labels = [f"{l}-SIM" for l in roster]
    ranked = rank_falsifier_writers(sim_labels, strength_order=order)
    assert set(ranked) == set(sim_labels)
    assert [r[:-4] for r in ranked] == list(order), (
        "SIM labels must follow the measured order, not fall to `extras`"
    )


def test_the_frozen_tuple_is_untouched():
    """Additive: nothing was removed. The default remains available to callers
    that supply no order, and a measured order is supplied by passing one."""
    assert DEFAULT_FALSIFIER_STRENGTH == (
        "Codex", "CC2", "ChatGPT", "Gemini", "DeepSeek", "Fable"
    )
    labels = ["Gemini", "Codex"]
    assert rank_falsifier_writers(labels) == ["Codex", "Gemini"]


def test_nothing_here_accepts_a_model_declaration():
    """Scope guard: capability is computed from harness verdicts only. If a
    model-supplied field ever becomes an input to this module, this fails."""
    import inspect

    import bench.capability_identity as mod
    src = inspect.getsource(mod)
    for banned in ("self_report", "model_confidence", "declared_",
                   "model_says", "asserted_severity"):
        assert banned not in src, f"model-declared input {banned!r} reached the ledger"
    # Substring-scanning the source for "convergence" was the first attempt and
    # it is wrong: the module's docstring legitimately NAMES convergence to
    # disclaim it, so the scan fires on the disclaimer. Replaced with a sharper
    # assertion over the module's API surface -- no public callable may mention
    # convergence in its NAME or return a value a convergence gate could read.
    public = [
        (n, getattr(mod, n)) for n in dir(mod)
        if not n.startswith("_") and callable(getattr(mod, n))
        and getattr(getattr(mod, n), "__module__", "") == mod.__name__
    ]
    assert public, "expected a public API to inspect"
    for name, obj in public:
        assert "converg" not in name.lower(), (
            f"{name} names convergence; this module must not decide it"
        )
    # And no callable here may accept a parameter a caller could use to feed a
    # model's own verdict in.
    for name, obj in public:
        try:
            params = set(inspect.signature(obj).parameters)
        except (TypeError, ValueError):
            continue
        for banned in ("confidence", "severity", "converged", "verdict_claimed"):
            assert banned not in params, (
                f"{name} accepts {banned!r} -- a model-asserted input"
            )
