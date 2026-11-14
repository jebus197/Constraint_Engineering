# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'severity_proof_and_weight_2026-11-14', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 44c57bb2f346e0dda9010a2b6df39eca25eacf3b5fb620ae8a017b3f56da69c6
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""Guards from the panel round of 2026-11-14 on severity.

Three things this file pins, each of which was measured before it was written:

1.  R1 -- `severity_is_proven` can be repointed at the number the GATE reads,
    the repoint is CONJUNCTIVE, and the mirror is actually WIRED. Both arms of
    the flag are executed here, because a default-off flag nothing reaches is
    not an addition (this project's own record: 11 confirmed defects were
    additions that did nothing).

2.  F3 -- the critical cut is spelled SIX times outside its canonical constant,
    not four. Five of the six were pinned by nothing. They are pinned here.

3.  R2 -- why a 3rd consequence weight is REFUSED. The product's induced
    ordering on findings is not determined by the consequence ORDERING, so a
    3rd weight repairs the arity of W while leaving the product inadmissible
    under `cdsfl_core_formal.md`'s ordinal criterion. The order flip is
    reproduced here in arithmetic so the refusal is checkable rather than
    asserted.
"""
import inspect

import pytest

from bench import reference_runner_v3 as rr


# ── 1. R1: the repointed proof door ──────────────────────────────────────────

def _entry(sev, rk, status="PASS"):
    return {"severity": sev, "severity_proof": {"status": status,
                                                "recomputed_rk": rk}}


@pytest.fixture(autouse=True)
def _restore_mirror():
    """Leave the module mirror exactly as found, whatever the test does."""
    was = rr._SEVERITY_PROOF_MATCHES_GATED["on"]
    yield
    rr._SEVERITY_PROOF_MATCHES_GATED["on"] = was


def test_default_is_byte_identical_to_the_old_door():
    """OFF must be the tree as it stood: status alone decides."""
    rr._SEVERITY_PROOF_MATCHES_GATED["on"] = False
    assert rr.severity_is_proven(_entry(0.45, 0.95)) is True
    assert rr.severity_is_proven(_entry(0.45, 0.45)) is True
    assert rr.severity_is_proven(_entry(0.45, 0.95, "FAIL")) is False
    assert rr.severity_is_proven({}) is False


def test_on_refuses_a_proof_of_a_different_number():
    """The archive's whole problem in one case: R_k 0.95 releasing a 0.45."""
    rr._SEVERITY_PROOF_MATCHES_GATED["on"] = True
    assert rr.severity_is_proven(_entry(0.45, 0.95)) is False
    assert rr.severity_is_proven(_entry(0.45, 0.45)) is True
    # at the proof's OWN tolerance, so a 3-significant-figure write still passes
    assert rr.severity_is_proven(_entry(0.45, 0.49)) is True
    assert rr.severity_is_proven(_entry(0.45, 0.51)) is False


def test_a_missing_or_nonnumeric_figure_is_not_agreement():
    rr._SEVERITY_PROOF_MATCHES_GATED["on"] = True
    assert rr.severity_is_proven({"severity": 0.5,
                                  "severity_proof": {"status": "PASS"}}) is False
    assert rr.severity_is_proven(_entry(0.5, "0.5")) is False
    assert rr.severity_is_proven(_entry(0.5, True)) is False
    assert rr.severity_is_proven(_entry(0.5, float("nan"))) is False


def test_the_repoint_is_conjunctive_and_therefore_cannot_loosen():
    """THE DIRECTION PROPERTY. Exhaustive over a grid: ON implies OFF, always.

    This is what makes the direction of effect knowable without a round. All
    three live call sites admit MORE when `severity_is_proven` is True, so a
    strictly smaller proven set can only shrink what is released.
    """
    grid = [_entry(s, r, st)
            for s in (0.0, 0.3, 0.45, 0.69, 0.7, 0.95, 1.0)
            for r in (0.0, 0.3, 0.44, 0.45, 0.46, 0.7, 0.95, 1.0)
            for st in ("PASS", "WARN", "FAIL", "SKIP")]
    loosened = 0
    for e in grid:
        rr._SEVERITY_PROOF_MATCHES_GATED["on"] = False
        off = rr.severity_is_proven(e)
        rr._SEVERITY_PROOF_MATCHES_GATED["on"] = True
        on = rr.severity_is_proven(e)
        if on and not off:
            loosened += 1
    assert loosened == 0, f"{loosened}/{len(grid)} entries LOOSEN -- not monotone"


def test_the_mirror_is_wired_to_the_config():
    """An unwired flag is an addition nothing reaches. This executes the wiring."""
    cfg = rr.RunnerConfig()
    assert cfg.severity_proof_must_match_gated is False
    got = rr.wire_module_mirrors(cfg)
    assert got["severity_proof_matches_gated"] is False
    assert rr._SEVERITY_PROOF_MATCHES_GATED["on"] is False

    cfg.severity_proof_must_match_gated = True
    got = rr.wire_module_mirrors(cfg)
    assert got["severity_proof_matches_gated"] is True
    assert rr._SEVERITY_PROOF_MATCHES_GATED["on"] is True


# ── 2. F3: every spelling of the cut, pinned ─────────────────────────────────

def test_every_duplicate_spelling_of_the_critical_cut_matches_the_runner():
    """SIX spellings outside the canonical constant, not four.

    `bench/evidence.py` was already pinned by test_verified_true_ledger.py.
    The other five were pinned by nothing, and four of them live in
    `convergence_location.py` as PARAMETER DEFAULTS, which no text search for
    an assignment finds. Read by import and by `inspect.signature`.
    """
    from bench import audit_closing_window as acw
    from bench import convergence_location as cl
    from bench import evidence

    canonical = rr.CRITICAL_SEVERITY_THRESHOLD
    spellings = {
        "evidence.LEDGER_CRITICAL_SEVERITY": evidence.LEDGER_CRITICAL_SEVERITY,
        "audit_closing_window.CRITICAL_SEVERITY_THRESHOLD":
            acw.CRITICAL_SEVERITY_THRESHOLD,
    }
    for fn in (cl.combined_novelty_series, cl.hierarchical_novelty_series,
               cl.location_only_series, cl.novelty_rule_divergence):
        p = inspect.signature(fn).parameters["critical_threshold"]
        spellings[f"convergence_location.{fn.__name__}(critical_threshold=)"] = p.default

    assert len(spellings) == 6, f"spelling count changed: {sorted(spellings)}"
    bad = {k: v for k, v in spellings.items() if v != canonical}
    assert not bad, f"drifted from runner {canonical}: {bad}"


# ── 3. R2: why a 3rd weight is refused ───────────────────────────────────────

def test_the_product_ordering_is_not_determined_by_the_consequence_ordering():
    """Reproduces, in arithmetic, the z3 `sat` that refuses R2.

    Two findings. A is the lower consequence class with the higher credence; B
    is the higher class with the lower credence. Re-label the two classes by a
    strictly increasing map that PRESERVES their ordering. The ordering of the
    FINDINGS flips. A product of a consequence and a belief is therefore not a
    statement about an ordinal consequence, and adding a 3rd weight does not
    change that -- it adds a third arbitrary numeric label to the same product.
    """
    cA, cB = 0.75, 0.25
    lo, hi = rr.SEV_F_W["SOFT"], rr.SEV_F_W["HARD"]        # 0.5, 1.0 -- live values
    assert lo < hi
    assert lo * cA > hi * cB                               # A outranks B

    relo, rehi = 1.0, 4.0                                  # strictly increasing
    assert relo < rehi                                     # class ordering PRESERVED
    assert relo * cA < rehi * cB                           # finding ordering FLIPPED

    # the ordered pair of R3, compared lexicographically, does not flip:
    # B is in the higher class under BOTH labellings, so B outranks A in both.
    def lex_gt(rank_x, cred_x, rank_y, cred_y):
        return rank_x > rank_y or (rank_x == rank_y and cred_x > cred_y)

    assert lex_gt(hi, cB, lo, cA) is True
    assert lex_gt(rehi, cB, relo, cA) is True


def test_only_one_of_the_six_cells_can_reach_the_critical_cut():
    """F2 at the level of actual return values, from the real function.

    `Sev >= 0.7` is identically `HARD AND CONFIRMED AND confidence >= 0.7`, and
    inside that one surviving cell `Sev == confidence` exactly. Consequence
    magnitude places NO constraint on the magnitude the gate tests.
    """
    reachable = [(c, v)
                 for c in ("HARD", "SOFT")
                 for v in ("CONFIRMED", "REFUTED", "UNTOOLABLE")
                 if rr.compute_sev_f(c, 1.0, v) >= rr.CRITICAL_SEVERITY_THRESHOLD]
    assert reachable == [("HARD", "CONFIRMED")]
    for conf in (0.0, 0.33, 0.7, 0.9, 1.0):
        assert rr.compute_sev_f("HARD", conf, "CONFIRMED") == pytest.approx(conf)
