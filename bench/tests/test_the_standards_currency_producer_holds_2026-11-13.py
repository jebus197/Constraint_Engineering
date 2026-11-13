"""The standards-currency producer's contracts, EXECUTED rather than read.

WHY THIS GUARD EXISTS. `scripts/standards_currency_and_model_staleness_2026-11-13.py`
produces every figure quoted to the founder on the standards-currency and
model-staleness question, and `measured-rate-travels-with-its-script` makes the
script the evidence. A producer with no guard is a measurement that can silently
change meaning, which is the defect this project has found repeatedly.

WHAT IT DOES NOT DO, deliberately. It does not re-assert the decimal figures.
`scripts/panel_brief_validate.py:check_declared_figures` already re-executes every
figure the brief declares, so pinning the same decimals here would duplicate a
working check and add a second place to re-rule when a count grows -- and 0.654350
of this suite's numeric assertions are already exact-equality pins, Wilson
[0.640566, 0.667880]. This guard pins the producer's CONTRACTS instead, each
derived from the subject rather than typed, per
`feedback_a_mutation_harness_must_derive_its_anchors_2026-11-04`.

THE 5 CONTRACTS, and what breaks each:
  C1 the exposure fraction is 2*lambda*T/1461 symbolically, so the run rate cancels.
     Independently confirmed in Wolfram on 2026-11-13: `frac_form = (2*lam*T)/1461`.
  C2 the self-exclusion is REACHABLE and CHANGES the answer. The producer holds
     version-bearing literals of its own, so an instrument left inside its own
     population inflates what it measures. A decorative flag would pass a test
     that only called it one way.
  C3 the seat table lifts NON-EMPTY. A guessed binding name returns 0 rows and
     reads exactly like a real empty table -- the first draft guessed "SEATS",
     got 0 rows, and printed "the dispatch pins NO version", which was the
     right sentence reached by a broken route.
  C4 the Monte Carlo agrees with the closed form, so neither alone is trusted.
  C5 both confidence-interval routes agree, on both interval families.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

sympy = pytest.importorskip("sympy")

REPO = pathlib.Path(__file__).resolve().parent.parent.parent
PRODUCER = REPO / "scripts" / "standards_currency_and_model_staleness_2026-11-13.py"


def _load():
    """Import the producer by path: its filename carries a date and hyphens.

    EXECUTED, not grepped. A regex over the source would confirm the file
    describes itself consistently and could not detect a producer and a consumer
    that disagree.
    """
    assert PRODUCER.is_file(), f"the producer is missing: {PRODUCER}"
    spec = importlib.util.spec_from_file_location("cdsfl_standards_currency", PRODUCER)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["cdsfl_standards_currency"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def prod():
    return _load()


def test_c1_the_run_rate_cancels_out_of_the_exposure_fraction(prod):
    """C1. The anchor is DERIVED by symbolic comparison, not typed as a decimal."""
    lam, T, window, frac = prod.exposure_closed_form()
    assert sympy.simplify(window - T / 2) == 0, (
        "the undetected window must be T/2; a revision is uniform in the interval")
    expected = 2 * lam * T / 1461
    assert sympy.simplify(frac - expected) == 0, (
        f"the exposure fraction must be 2*lambda*T/1461, got {frac}. Wolfram "
        f"independently returns (2*lam*T)/1461 for this integral.")
    # And the thing that makes it a usable decision rule: no run-rate symbol.
    assert {s.name for s in frac.free_symbols} == {"lambda", "T"}, (
        f"the fraction must depend on lambda and T ONLY, found "
        f"{sorted(s.name for s in frac.free_symbols)}. If a run-rate symbol "
        f"appears, the cadence could be gamed by running more experiments.")


def test_c2_the_self_exclusion_is_reachable_and_moves_the_count(prod):
    """C2. Call it BOTH ways. A flag tested one way is a flag that may do nothing."""
    t_out, a_out = prod.version_census(exclude_self=True)
    t_in, a_in = prod.version_census(exclude_self=False)
    assert len(t_in) > len(t_out), (
        f"including the producer must raise the version-bearing count: "
        f"{len(t_in)} including vs {len(t_out)} excluding. Equal counts mean the "
        f"exclusion is decorative and the instrument is inside its own population.")
    assert len(a_in) > len(a_out), (
        f"including the producer must also raise the alias count: {len(a_in)} vs "
        f"{len(a_out)}; the producer holds an ALIASES tuple.")
    # The excluded population must still be the large one -- an exclusion that
    # removed most of the corpus would be a different defect.
    assert len(t_out) + len(a_out) > 100, (
        f"the excluded population collapsed to {len(t_out) + len(a_out)} literals; "
        f"_live() is over-filtering")

    # ARCHIVED SEAT EVIDENCE MUST BE OUT, and this is tested on `_live` DIRECTLY
    # rather than through the exclude_self toggle. The first version of this
    # contract went through the toggle and was VACUOUS -- seat_evidence sits in
    # the UNCONDITIONAL exclusion, so no value of the flag can include it, and
    # the census could never show a difference. The vacuity probe written beside
    # it caught that on the first run, which is the only reason it is not still
    # sitting here passing for the wrong reason.
    harvested = [f for f, _, _ in (t_out + a_out) if "seat_evidence" in f]
    assert not harvested, (
        f"{len(harvested)} archived seat-evidence file(s) are in the population, "
        f"e.g. {harvested[:2]}. Harvested seat output records a round; it is not "
        f"this project's source.")
    # NON-VACUOUS BY CONSTRUCTION: such files must actually exist on disk, or the
    # assertion above would pass against an empty directory.
    harvest_dir = REPO / "experimental_notes" / "seat_evidence"
    real = sorted(harvest_dir.rglob("*.py")) if harvest_dir.is_dir() else []
    assert len(real) > 50, (
        f"only {len(real)} harvested .py file(s) found under {harvest_dir}; this "
        f"contract would be vacuous. 359 were present on 2026-11-13 across 63 "
        f"rounds, and every one had been inside the measured population.")
    for f in real[:5]:
        assert prod._live(f) is False, (
            f"_live() admits an archived seat-evidence file: {f}")
        assert prod._live(f, exclude_self=False) is False, (
            f"_live() admits {f} when exclude_self is off. Archived evidence is "
            f"excluded UNCONDITIONALLY -- it is not apparatus, and the 2 reasons "
            f"must not be conflated.")


def test_c3_the_seat_table_lifts_non_empty(prod):
    """C3. An empty lift and a real empty table print the same sentence."""
    rows = prod.seats_from_syntax_tree()
    assert rows, (
        "the seat table lifted as EMPTY. A guessed binding name returns 0 rows "
        "and is indistinguishable from a dispatcher with no seats, which is how "
        "the first draft reached a true-sounding conclusion by a broken route.")
    free = [r for r in rows if r[2] == "claude_cli"]
    assert len(free) == 2, (
        f"expected 2 free claude_cli seats (cc2 and fable, both Max "
        f"subscription), lifted {len(free)}: {[r[0] for r in free]}")
    names = {r[0] for r in free}
    assert names == {"cc2", "fable"}, f"free seats should be cc2 and fable, got {names}"
    pinned = [r for r in free if prod.VER.search(str(r[1]))]
    assert not pinned, (
        f"a free seat now pins a model version: {pinned}. The claim made to the "
        f"founder is that the dispatch names an ALIAS, so there is no version "
        f"there to update. If this fails, that claim has stopped being true.")


def test_c4_the_simulation_agrees_with_the_closed_form(prod):
    """C4. Two independent routes to one number; neither is trusted alone."""
    lam, T, _w, frac = prod.exposure_closed_form()
    for lam_v, T_v in ((0.5, 30), (1.0 / 9.0, 60)):
        closed = float(frac.subs({lam: lam_v, T: T_v}))
        sim = prod.exposure_simulated(lam_v, T_v, years=3000, n_runs=60000)
        rel = abs(sim - closed) / closed
        assert rel < 0.15, (
            f"closed form {closed:.6f} and simulation {sim:.6f} disagree by "
            f"{rel:.4f} at lambda={lam_v}, T={T_v}")


def test_c5_both_interval_routes_agree_on_both_families(prod):
    """C5. CALL the producer's intervals; do not re-implement them here.

    THE FIRST VERSION OF THIS TEST WAS VACUOUS and the mutation harness proved it.
    It computed the hand-rolled Wilson route in its own body and asserted that its
    2 copies agreed -- a tautology about the test. Mutation M4 broke the producer's
    route and this test stayed GREEN: 4 of 5 red, which is how the blind spot was
    found rather than argued about. Now the producer's `intervals()` is the subject
    and statsmodels, computed fresh here, is the independent check.
    """
    from statsmodels.stats.proportion import proportion_confint

    typed, alias = prod.version_census(exclude_self=True)
    nt = len(typed)
    n = nt + len(alias)
    assert 0 < nt < n, f"degenerate census: {nt} of {n}"

    iv = prod.intervals(nt, n)

    # INDEPENDENT of the producer: statsmodels called here, in this file.
    ref_w = proportion_confint(nt, n, method="wilson")
    ref_cp = proportion_confint(nt, n, method="beta")

    got_w = iv["wilson_closed_form"]
    assert max(abs(got_w[0] - ref_w[0]), abs(got_w[1] - ref_w[1])) < 1e-9, (
        f"the producer's closed-form Wilson {got_w} disagrees with statsmodels "
        f"{tuple(float(x) for x in ref_w)}. A proportion reported to the founder "
        f"needs 2 routes that AGREE; this is the route that can drift.")
    got_cp = iv["clopper_pearson_scipy"]
    assert max(abs(got_cp[0] - ref_cp[0]), abs(got_cp[1] - ref_cp[1])) < 1e-9, (
        f"the producer's scipy Clopper-Pearson {got_cp} disagrees with statsmodels "
        f"{tuple(float(x) for x in ref_cp)}")
    assert got_w[0] < iv["p_hat"] < got_w[1], (
        "the point estimate must lie inside its own interval")
    # And the helper must REFUSE a degenerate proportion rather than returning one.
    import pytest as _pt
    for bad in ((0, 10), (10, 10), (5, 0)):
        with _pt.raises(ValueError):
            prod.intervals(*bad)


def test_c7_the_exact_law_and_the_first_order_form_agree_in_the_limit(prod):
    """C7. The 2 exposure forms must relate as a series and its leading term.

    ADDED AFTER BOTH PANEL SEATS REFUTED THE FIRST-ORDER FORM as the quantity.
    `lam * E[window]` SUMS the stale windows of every revision in a check
    interval; 2 revisions in 1 interval leave the standard stale ONCE. The exact
    object is the union. This contract pins the RELATION, not a decimal: the
    ratio of the 2 forms must tend to 1 as lambda tends to 0, and the first-order
    form must OVERSTATE at every positive rate, because overstating is the safe
    direction and a sign flip would be a silent downgrade of a safety margin.
    """
    import sympy as sp
    lam_e, T_e, exact = prod.exposure_exact()
    lam_f, T_f, _w, first = prod.exposure_closed_form()

    # The exact form in per-DAY units against the first-order form in per-YEAR.
    ratio = sp.simplify((first.subs({lam_f: lam_e * sp.Rational(36525, 100), T_f: T_e}))
                        / exact)
    assert sp.limit(ratio, lam_e, 0) == 1, (
        f"the first-order form must be the leading term of the exact one; the "
        f"ratio tends to {sp.limit(ratio, lam_e, 0)}")

    # And it must overstate, never understate, at every rate we care about.
    for lam_yr in (0.05, 0.1111111111, 0.2222222222, 0.5, 1.0):
        for Td in (7, 30, 90, 180, 365):
            ex = prod.exposure_exact_value(lam_yr, Td)
            fo = lam_yr * Td / 2 / 365.25
            assert fo >= ex, (
                f"the first-order form UNDERSTATES at lambda={lam_yr}, T={Td}: "
                f"{fo:.8f} < {ex:.8f}. Understating exposure is the unsafe "
                f"direction.")
    # The overstatement must be material at long cadences, or the correction the
    # panel forced would have been cosmetic and this contract would be theatre.
    ex180 = prod.exposure_exact_value(0.5, 180)
    fo180 = 0.5 * 180 / 2 / 365.25
    assert fo180 / ex180 - 1 > 0.05, (
        f"the overstatement at T=180 is only {fo180 / ex180 - 1:.4%}; if it were "
        f"this small the correction would not have mattered")


def test_c8_the_exposure_ceiling_root_is_cross_checked(prod):
    """C8. The cadence for a 1 per cent ceiling, scipy root against mpmath root.

    The first-order form inverts algebraically; the exact one does not, so the
    answer comes from a numerical root and a single root-finder is a single route.
    """
    import mpmath as mp
    mp.mp.dps = 30
    for lam_yr in (0.1111111111, 0.1428571429, 0.2222222222, 0.5):
        got = prod.exposure_ceiling_cadence(lam_yr, 0.01)
        # Independent route: mpmath's own root finder on the same function.
        f = lambda x: (1 - (1 - mp.e ** (-(mp.mpf(lam_yr) / mp.mpf("365.25")) * x))
                       / ((mp.mpf(lam_yr) / mp.mpf("365.25")) * x)) - mp.mpf("0.01")
        ref = float(mp.findroot(f, mp.mpf(got)))
        assert abs(got - ref) < 1e-6, (
            f"scipy root {got} and mpmath root {ref} disagree at lambda={lam_yr}")
        # And the exact ceiling must be LOOSER than the first-order one, because
        # the first-order form overstates exposure.
        first_order = 0.01 * 2 * 365.25 / lam_yr
        assert got > first_order, (
            f"the exact ceiling {got:.4f} must exceed the first-order "
            f"{first_order:.4f} at lambda={lam_yr}")


def test_the_producer_runs_clean_end_to_end():
    """It must EXIT 0, because the brief validator re-executes it per figure."""
    import subprocess
    r = subprocess.run([sys.executable, str(PRODUCER)], cwd=REPO,
                       capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"the producer exited {r.returncode}; the panel brief declares 7 figures "
        f"against it and a cited script that does not run is worthless as "
        f"evidence.\nstderr tail:\n{r.stderr[-1500:]}")
    out = r.stdout
    # THE LABELS THE CURRENT BRIEF DECLARES MUST STILL PRINT, read from the
    # NEWEST brief rather than the first.
    #
    # WHY NEWEST AND NOT ALL: the blind round's BRIEF.md is a HISTORICAL RECORD of
    # what 2 seats were actually sent. It declared `composed_covers = 5 of 5`, both
    # seats refuted that figure as a dominance measurement, and the producer now
    # prints the refutation where the count was. Editing the dispatched brief to
    # match would falsify the record of what the seats received, so the brief
    # stands and the guard follows the current one.
    #
    # AND A RETIREMENT MUST BE RECORDED, NOT SILENT: the producer must still say
    # REFUTED where a figure was withdrawn, so a figure cannot simply disappear.
    import re
    briefs = sorted((REPO / "bench" / "logs").glob("standards_currency*/BRIEF.md"),
                    key=lambda q: q.stat().st_mtime)
    assert briefs, "no standards_currency brief found; this contract is vacuous"
    current = briefs[-1]
    declared = re.findall(r"<!--\s*figure:[^|]+\|[^|]+\|\s*([^>]+?)\s*-->",
                          current.read_text(errors="replace"))
    assert len(declared) >= 5, (
        f"the current brief {current.name} declares only {len(declared)} figure(s)")
    missing = [d for d in declared if d.split("=")[0].strip() not in out]
    assert not missing, (
        f"the producer no longer prints label(s) the CURRENT brief "
        f"({current.parent.name}) declares: {missing}")

    # ★ A THREE-WAY CONTRACT, replacing a count. Both free panel seats proposed
    # this independently in the joint round of 2026-11-13, and the count it
    # replaces had just been shown to degrade: adding unrelated REFUTED prose
    # elsewhere made `count("REFUTED") >= 2` satisfiable without the specific
    # retirement, and mutation M9 went GREEN. A count can be satisfied by
    # content that has nothing to do with what it was built to check.
    #
    # EVERY figure EVERY brief in this family declared must be in exactly 1 of:
    #   CURRENT    -- its value prints verbatim
    #   SUPERSEDED -- its label appears on a line carrying SUPERSEDED, naming it
    #   WITHDRAWN  -- its label appears on a line that also carries REFUTED
    # Anything else is a figure that vanished silently, which is the case that
    # lets a withdrawn number keep being cited.
    lines = out.splitlines()
    all_declared = {}
    for b in briefs:
        for d in re.findall(r"<!--\s*figure:[^|]+\|[^|]+\|\s*([^>]+?)\s*-->",
                            b.read_text(errors="replace")):
            all_declared[d] = b.parent.name
    assert len(all_declared) >= 7, (
        f"only {len(all_declared)} figure(s) declared across {len(briefs)} brief(s); "
        f"this contract would be weak")
    # ★ ORDER IS LOAD-BEARING, and getting it wrong reproduced entry B174 inside
    # this very guard. A retraction line QUOTES the figure it retracts, so testing
    # `decl in out` FIRST classifies a withdrawn figure as CURRENT and the
    # retirement branch is never reached. Retraction lines are excluded from the
    # verbatim test, not checked after it.
    RETIRED_MARKERS = ("REFUTED", "SUPERSEDED")
    plain = [ln for ln in lines if not any(m in ln for m in RETIRED_MARKERS)]
    plain_text = "\n".join(plain)

    def state_of(decl):
        label = decl.split("=")[0].strip()
        for marker in RETIRED_MARKERS:
            if any(label in ln and marker in ln for ln in lines):
                return marker
        return "CURRENT" if decl in plain_text else "SILENT"

    states = {d: state_of(d) for d in all_declared}
    silent = [f"{d!r} (declared by {all_declared[d]})"
              for d, st in sorted(states.items()) if st == "SILENT"]
    assert not silent, (
        "figure(s) neither printed verbatim on a non-retraction line nor recorded "
        "as REFUTED or SUPERSEDED, so they vanished silently and a reader cannot "
        "tell a correction from a regression:\n  " + "\n  ".join(silent))
    retired = {m: [d for d, st in states.items() if st == m] for m in RETIRED_MARKERS}
    assert retired["REFUTED"], (
        "no declared figure is WITHDRAWN, so that branch is never exercised")
    assert retired["SUPERSEDED"], (
        "no declared figure is SUPERSEDED, so that branch is never exercised. "
        "A figure whose value moved must say so where it is produced, or a "
        "reader cannot tell a correction from a regression.")
