# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'standards_currency_2026-11-13', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 2f9db4a2fb6c24180d17fdfb00ce895b98b820f8fd00a2fe8de594a256c8b090
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""Panel fixes of 2026-11-13: these tests go RED if the fixes are reverted.

1. `exposure_exact` -- the producer's first draft quoted lam*T/2 as "the
   closed form" and tested its Monte Carlo against it under a 0.12 tolerance,
   absorbing an 8.4% truncation error at (0.5/yr, 180 d) as "noise". The exact
   law is 1 - (1 - e^(-x))/x. Second routes: mpmath here; Wolfram Language
   (local Wolfram Engine) gave 0.020255649821 and T_max 14.708219 on
   2026-11-13.
2. `expected_archive_epochs` -- the first draft printed
   `archive_epochs_at_T30 = 4` by counting CHECK boundaries (days//30 + 1).
   Encoding versions come from REVISIONS: expected 1.278 over 104 days,
   P(>=3) = 0.0029.
3. `VER_ANY` -- the seat-row tag called `openai/gpt-5.5` "alias, no version".
4. `probe_seat` records WHICH model answered when the route reports it, and
   whether it matches the intended identity, without ever benching a seat.
"""
import importlib.util
import math
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))


def _load(relpath, name):
    spec = importlib.util.spec_from_file_location(name, REPO / relpath)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod            # dataclasses resolves string annotations
    spec.loader.exec_module(mod)       # via sys.modules[cls.__module__]
    return mod


def test_exposure_exact_is_the_exact_law_not_its_first_order_term():
    prod = _load("scripts/standards_currency_and_model_staleness_2026-11-13.py", "prod")
    lam, T = 0.5, 30.0
    x = lam * T / 365.25
    expect = 1.0 - (1.0 - math.exp(-x)) / x          # independent in-test route
    got = prod.exposure_exact(lam, T)
    assert abs(got - expect) < 1e-12
    assert abs(got - 0.020255649821076083) < 1e-12   # Wolfram Language figure
    # and it is strictly BELOW the first-order form the first draft used:
    assert got < lam * T / 2 / 365.25
    # at the cell where the first draft hid 8.4% truncation error:
    e180 = prod.exposure_exact(0.5, 180.0)
    assert abs(e180 - 0.11367818) < 1e-6
    assert (0.5 * 180 / 2 / 365.25) / e180 - 1 > 0.08


def test_monte_carlo_agrees_with_exact_not_with_lamT_over_2():
    prod = _load("scripts/standards_currency_and_model_staleness_2026-11-13.py", "prod2")
    sims = [prod.exposure_simulated(0.5, 180, seed=s) for s in (1, 2, 3, 4, 5)]
    mean = sum(sims) / len(sims)
    exact = prod.exposure_exact(0.5, 180.0)
    approx = 0.5 * 180 / 2 / 365.25
    assert abs(mean - exact) / exact < 0.03, "simulation must match the exact law"
    assert abs(mean - approx) / approx > 0.05, "and must REFUTE lam*T/2 at this cell"


def test_archive_epochs_counts_revisions_not_checks():
    prod = _load("scripts/standards_currency_and_model_staleness_2026-11-13.py", "prod3")
    lams = [1 / 9, 1 / 7, 1 / 4.5, 1 / 2]            # from HIST mean gaps
    epochs, p1, p3 = prod.expected_archive_epochs(lams, 104)
    assert abs(epochs - 1.2780) < 1e-3
    assert abs(p3 - 0.002910) < 1e-5
    assert epochs < 2, "the typed figure 4 counted check boundaries, not revisions"


def test_seat_tag_regex_sees_non_claude_versions():
    prod = _load("scripts/standards_currency_and_model_staleness_2026-11-13.py", "prod4")
    for pinned in ("openai/gpt-5.5", "openai/gpt-5.3-codex",
                   "google/gemini-3.1-pro-preview", "deepseek/deepseek-v4-pro",
                   "kimi-k3", "claude-fable-5-1"):
        assert prod.VER_ANY.search(pinned), pinned
    for alias in ("fable", "opus"):
        assert not prod.VER_ANY.search(alias), alias


def test_probe_records_which_model_answered_without_benching():
    al = _load("bench/seat_aliveness_2026-10-06.py", "alive")
    r = al.probe_seat("fable", lambda: ("Ready!", "claude-fable-5-1"),
                      intended_model="fable_5_1")
    assert r.alive and r.model_reported == "claude-fable-5-1"
    assert r.identity_match is True
    r2 = al.probe_seat("fable", lambda: ("Ready!", "claude-fable-5-1"),
                       intended_model="fable_5_2")
    assert r2.alive, "an identity mismatch must NEVER kill aliveness or bench a seat"
    assert r2.identity_match is False
    r3 = al.probe_seat("fable", lambda: "Ready!")     # plain-string caller: today's path
    assert r3.alive and r3.model_reported is None and r3.identity_match is None
    assert al.identity_match("fable", "claude-fable-5-2") is True   # alias pins nothing
    assert al.identity_match(None, "x") is None
