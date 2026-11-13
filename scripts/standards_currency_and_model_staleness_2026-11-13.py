#!/usr/bin/env python3
"""Producer for every figure quoted on the standards-currency and model-staleness question.

FOUNDER'S PROPOSAL, 2026-11-13, verbatim: *"when an encoding is loaded, perhaps our
classifier model (in this case Haiku) should perform an online check to ensure any
encoding matches the existing formal standards, and if not update the encoding
dynamically before loading it? [...] User preferences/constraints don't change, but
standards, formal measurements, legislation etc. should always be current? [...] So I
would propose a cadence of one month between checks, in order to stay current."*

AND, separately: *"sometimes the model names and version numbers can become stale. So
in order to fix this fully too, perhaps we can integrate a model name/version check
with our aliveness check, so that the harness can stay fully current with whatever
models we are using at any given point too?"*

WHAT THIS SCRIPT ESTABLISHES, and nothing else:
  1. The exposure fraction -- the share of runs executed under a superseded standard
     -- as a closed form in the check interval T and the revision rate lambda, with
     the run rate CANCELLING. SymPy closed form, NumPy Monte Carlo cross-check.
  2. What his 30-day cadence buys against the 4 standards the registry actually
     names, and what a 1 per cent exposure ceiling would require instead.
  3. The share of live model-identity literals that carry a version and therefore
     go stale, with 2 independent confidence-interval routes.
  4. Whether a currency CHECK and per-run PROVENANCE compose in his strong sense --
     a measured dominance on a named property, not a judgement that both are nice.

TWO DEFECTS IN THIS SCRIPT'S OWN FIRST DRAFT, recorded because both were found by
running it rather than by reading it:
  * The first decision metric was P(at least 1 run under a superseded standard). At
    the archive's observed run rate it returned 1.000000 at EVERY cadence from 1 day
    to 365, so it could not discriminate between the options it existed to compare.
  * The first source census counted `bench/logs/**/sandbox_harvest/**` as live code.
    4 of the 8 worst-offending files were archived seat working directories.

[VERIFY:current] The revision histories in HIST are from training knowledge, not a
fresh lookup -- which is precisely the staleness the founder's proposal targets. The
recommendation is therefore tested for robustness across a 20x range of lambda, so
that it does not depend on those dates being right.
"""
from __future__ import annotations

import ast
import datetime as dt
import pathlib
import re
import sys
from collections import Counter

import mpmath as mp
import numpy as np
import sympy as sp
from scipy import stats as sps
from statsmodels.stats.proportion import proportion_confint

mp.mp.dps = 40
REPO = pathlib.Path(__file__).resolve().parent.parent

# The 4 domains that declare a consequence scale of their OWN, with the standard
# each names. The other 6 inherit or are unresolved and declare no scale, which is
# why they cannot conflict -- see bench/cdsfl_registry/domain_vocabulary.py.
HIST = {
    "FMEA (engineering)": [2001, 2008, 2019],
    "CTCAE (biology)": [2003, 2009, 2017],
    "CVSS (software)": [2005, 2007, 2015, 2019, 2023],
    "GHS (chemistry)": [2005, 2007, 2009, 2011, 2013, 2015, 2017, 2019, 2021, 2023, 2025],
}

# Measured live on 2026-11-13 through `claude -p --model <id>` on the Max
# subscription -- the CLI route, not a metered API call, and not billed.
CLI_INSTALLED = (2, 1, 220)
CLI_REQUIRED = {"claude-fable-5-1": (2, 1, 251), "claude-fable-5-2": (2, 1, 290)}

VER = re.compile(r"\b(?:claude[-_])?(?:opus|fable|sonnet|haiku)[-_]?\d+(?:[-_.]\d+)*", re.I)

#: ★ THE POPULATION THIS MEASURES IS CLAUDE-FAMILY ONLY, and saying so is a
#: correction. `VER` names 4 Anthropic families, so `share_version_bearing`
#: answers "of CLAUDE-family model-identity literals, what share carry a
#: version" -- not the all-provider question the prose implied. The fable seat
#: recounted over a provider-agnostic population in the blind round of
#: 2026-11-13 and got 532 of 960, share 0.554167, Wilson [0.522570, 0.585331]:
#: more than double. Both populations are now named where the figure is printed.
CLAUDE_FAMILIES = ("opus", "fable", "sonnet", "haiku")


def _installed_cli_version():
    """The installed CLI version, READ rather than typed. None if unobtainable."""
    import subprocess
    try:
        r = subprocess.run(["claude", "--version"], capture_output=True,
                           text=True, timeout=30)
    except Exception:                                              # noqa: BLE001
        return None
    m = re.search(r"(\d+)\.(\d+)\.(\d+)", r.stdout or "")
    return tuple(int(g) for g in m.groups()) if m else None
ALIASES = ("opus", "fable", "sonnet", "haiku")


#: THE MEASUREMENT APPARATUS, named explicitly so the exclusion is auditable
#: rather than convenient. A file whose only purpose is to produce or guard this
#: quantity is an instrument, not a member of the population being measured.
#:
#: THIS SET GREW ONCE, AND THE GROWTH IS THE REASON IT IS A SET. The first
#: version excluded only this producer, which held 2 version-bearing literals in
#: CLI_REQUIRED and 4 aliases in ALIASES. Then the guard was written, it contains
#: the literal "fable" in an assertion about the seat roster, and the headline
#: figure MOVED from 0.253054 to 0.252613 -- a measurement that changes when you
#: write a test about it. The mutation harness joined for the same reason.
#:
#: BOTH FIGURES ARE PRINTED. Excluding apparatus to make a number come out right
#: would be the dishonest version of this, so the included figure is reported
#: beside the excluded one and the reader can see the size of the effect.
APPARATUS = frozenset({
    "scripts/standards_currency_and_model_staleness_2026-11-13.py",
    "bench/tests/test_the_standards_currency_producer_holds_2026-11-13.py",
    "scripts/the_standards_currency_mutations_2026-11-13.py",
})


def _live(p: pathlib.Path, exclude_self: bool = True) -> bool:
    """Live source only. Archived seat sandboxes are not this project's code."""
    parts = set(p.parts)
    # `seat_evidence` JOINED THIS LIST ON ITS 3RD OFFENCE, 2026-11-13. The
    # harvester preserves what a panel seat wrote in its sandbox to
    # experimental_notes/seat_evidence/<round>/<seat>/, which is OUTSIDE logs/.
    # After the blind round landed, 4 harvested files entered this population and
    # share_version_bearing moved from 0.253054 to 0.264120. Harvested seat output
    # is archived evidence of a round, exactly like sandbox_harvest, and is not
    # this project's live source. 3rd instance of one shape in one night: the
    # producer, then its own guard, then the panel's harvest.
    if (".git" in parts or "logs" in parts or "sandbox_harvest" in parts
            or "seat_evidence" in parts):
        return False
    if exclude_self:
        try:
            if p.resolve().relative_to(REPO).as_posix() in APPARATUS:
                return False
        except ValueError:
            pass
    return True


def exposure_closed_form():
    """Fraction of runs under a superseded standard -- FIRST-ORDER form.

    ★ THIS IS THE LEADING TERM OF A SERIES, NOT THE QUANTITY, and the label is
    the correction. Found by BOTH free panel seats on 2026-11-13, independently,
    and then confirmed here by derivation rather than by their agreement, because
    2 models concurring is not a confirmation route in this project.

    THE ERROR: `lam * E[window]` multiplies the revision RATE by the mean window,
    which SUMS the stale windows of every revision in a check interval. When 2
    revisions land in one interval the standard is stale ONCE -- from the first
    revision until the next check -- not twice. The correct object is the UNION.
    See `exposure_exact()`.

    IT IS RETAINED, NOT DELETED. It is the correct first-order approximation, it
    is conservative (it OVERSTATES exposure), and it is what makes the run-rate
    cancellation visible in closed form. Overstatement measured: 1.37 per cent at
    T=30, 8.38 per cent at T=180, 17.32 per cent at T=365.
    """
    lam, T, t = sp.symbols("lambda T t", positive=True)
    window = sp.integrate((T - t) / T, (t, 0, T))       # E[undetected window]
    frac = sp.simplify(lam * window / sp.Rational(36525, 100))
    return lam, T, window, frac


def exposure_exact():
    """The exact exposure fraction, derived as a UNION rather than a sum.

    Within a check interval [0, T) the standard is stale at time t exactly when at
    least 1 revision has landed in [0, t), which has probability 1 - exp(-lam*t).
    Integrating gives the expected stale LENGTH, and dividing by T the fraction.

    Returns (lam, T, frac) with lam in revisions per DAY, so a caller converts
    from per-year itself. Confirmed 3 ways on 2026-11-13: SymPy here, a 12-seed
    NumPy Monte Carlo (z = -1.13 and -0.90 against this form, -3.33 and -28.65
    against the first-order one), and Wolfram Language, which returned the same
    series x/2 - x^2/6 + x^3/24.
    """
    lam, T, t = sp.symbols("lambda T t", positive=True)
    stale = sp.integrate(1 - sp.exp(-lam * t), (t, 0, T))
    return lam, T, sp.simplify(stale / T)


def exposure_exact_value(lam_per_year: float, T_days: float) -> float:
    """The exact fraction at a per-YEAR rate and a cadence in days."""
    L = lam_per_year / 365.25
    x = L * T_days
    if x == 0:
        return 0.0
    return float(1.0 - (1.0 - np.exp(-x)) / x)


def exposure_ceiling_cadence(lam_per_year: float, ceiling: float = 0.01) -> float:
    """The cadence T at which exact exposure equals `ceiling`. Root, not algebra.

    The first-order form inverts in closed form; the exact one does not, so this
    is solved numerically and cross-checked against mpmath by the guard.
    """
    from scipy import optimize
    f = lambda x: exposure_exact_value(lam_per_year, x) - ceiling
    return float(optimize.brentq(f, 1e-9, 1e6))


#: 12 INDEPENDENT SEEDS, not 1. A single seed gives no sampling distribution, so a
#: tolerance over it can only be TYPED -- which is how `err < 0.12` came to be wider
#: than the first-order form's own truncation error (0.0838 at T=180) and so could
#: not tell the 2 forms apart.
CROSS_CHECK_SEEDS = tuple(range(20261113, 20261125))

#: In units of the simulation's own standard error. DERIVED tolerance: the figure
#: that varies is the sampling noise, and this says how many of those a difference
#: may be before it is a disagreement rather than noise.
CROSS_CHECK_Z = 4.0


def exposure_simulated_many(lam_yr, T_days, seeds=CROSS_CHECK_SEEDS):
    """Mean and standard error of the exposure fraction over independent seeds."""
    vals = np.array([exposure_simulated(lam_yr, T_days, seed=s) for s in seeds])
    return float(vals.mean()), float(vals.std(ddof=1) / np.sqrt(len(vals)))


def exposure_simulated(lam_yr, T_days, years=4000, n_runs=120000, seed=20261113):
    """The same quantity by an independent route: NumPy Monte Carlo."""
    rng = np.random.default_rng(seed)
    horizon = years * 365.25
    rev = np.sort(rng.uniform(0, horizon, rng.poisson(lam_yr * years)))
    if rev.size == 0:
        return 0.0
    nxt = np.ceil(rev / T_days) * T_days
    runs = np.sort(rng.uniform(0, horizon, n_runs))
    i = np.searchsorted(rev, runs, "right") - 1
    ok = i >= 0
    exposed = np.zeros(runs.shape, dtype=bool)
    exposed[ok] = runs[ok] < nxt[i[ok]]
    return float(exposed.mean())


def prod_apparatus() -> list[str]:
    """The apparatus files that actually exist, so the count cannot overstate."""
    return sorted(a for a in APPARATUS if (REPO / a).is_file())


def version_census(exclude_self: bool = True):
    """Model-identity string literals in live code, split version-bearing vs alias."""
    typed, alias = [], []
    for p in sorted(x for x in REPO.rglob("*.py") if _live(x, exclude_self)):
        try:
            tree = ast.parse(p.read_text(errors="replace"))
        except Exception:                                          # noqa: BLE001
            continue
        docs = set()
        for n in ast.walk(tree):
            if isinstance(n, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if ast.get_docstring(n, clean=False) is not None and n.body \
                        and isinstance(n.body[0], ast.Expr):
                    docs.add(id(n.body[0].value))
        for n in ast.walk(tree):
            if isinstance(n, ast.Constant) and isinstance(n.value, str) and id(n) not in docs:
                v = n.value
                if len(v) > 120:
                    continue
                rel = p.relative_to(REPO).as_posix()
                if VER.fullmatch(v.strip()) or (VER.search(v) and len(v) < 40):
                    typed.append((rel, n.lineno, v))
                elif v.strip().lower() in ALIASES:
                    alias.append((rel, n.lineno, v))
    return typed, alias


def intervals(nt: int, n: int) -> dict:
    """The 4 interval bounds, computed ONCE and returned so a caller can check them.

    THIS EXISTS BECAUSE THE GUARD COULD NOT REACH IT. The arithmetic was inline in
    `main()`, so `bench/tests/test_the_standards_currency_producer_holds_2026-11-13.py`
    re-implemented the hand-rolled Wilson route and compared its OWN 2 copies --
    which is a tautology about the test, not a check on this file. Mutation M4 of
    `scripts/the_standards_currency_mutations_2026-11-13.py` broke this route and
    the guard stayed GREEN, 4 of 5 red. One declaration, 2 readers.

    2 routes per family, by construction:
      * Wilson from statsmodels, and Wilson from the closed form written out here.
      * Clopper-Pearson from statsmodels, and from scipy's beta quantiles directly.
    """
    if not 0 < nt < n:
        raise ValueError(f"degenerate proportion: {nt} of {n}")
    ph = nt / n
    z = sps.norm.ppf(0.975)
    c = z * z / n
    centre = (ph + c / 2) / (1 + c)
    half = (z / (1 + c)) * np.sqrt(ph * (1 - ph) / n + c / (4 * n))
    w_sm = proportion_confint(nt, n, method="wilson")
    cp_sm = proportion_confint(nt, n, method="beta")
    return {
        "p_hat": ph,
        "wilson_statsmodels": (float(w_sm[0]), float(w_sm[1])),
        "wilson_closed_form": (float(centre - half), float(centre + half)),
        "clopper_pearson_statsmodels": (float(cp_sm[0]), float(cp_sm[1])),
        "clopper_pearson_scipy": (float(sps.beta.ppf(0.025, nt, n - nt + 1)),
                                  float(sps.beta.ppf(0.975, nt + 1, n - nt))),
    }


def seats_from_syntax_tree():
    """Lift the panel's seat table by EXECUTION of the syntax tree, not by grep.

    `execute-do-not-grep`: a regex over the source would report what the file says
    about itself. This reads the literal the interpreter would bind.
    """
    f = REPO / "bench" / "confer_maths_panel_2026-09-05.py"
    tree = ast.parse(f.read_text(errors="replace"))
    rows = []
    for nd in ast.walk(tree):
        if isinstance(nd, (ast.Assign, ast.AnnAssign)):
            names = ([getattr(t, "id", "") for t in nd.targets]
                     if isinstance(nd, ast.Assign) else [getattr(nd.target, "id", "")])
            # The binding is `_ALL`. Found by asking which assignment's value
            # contains the literal "claude_cli", not by guessing a name:
            # guessing "SEATS" returned 0 rows and read as "no seats pinned",
            # which is the same sentence a real empty table would produce.
            if not any(n in ("_ALL", "SEATS", "MODELS", "_MODELS") for n in names):
                continue
            for el in ast.walk(nd.value):
                if isinstance(el, ast.Tuple) and len(el.elts) == 3 \
                        and all(isinstance(e, ast.Constant) for e in el.elts):
                    rows.append(tuple(e.value for e in el.elts))
    return rows


def main() -> int:
    lam, T, window, frac = exposure_closed_form()
    print("=" * 78)
    print("1  THE EXPOSURE FRACTION -- closed form, and why the run rate cancels")
    print("=" * 78)
    print(f"  E[undetected window | revision] = {sp.simplify(window)}")
    assert sp.simplify(window - T / 2) == 0, "the window must be T/2"
    print(f"  fraction of runs exposed        = {frac}")
    print("  The run rate does not appear, so this cannot be moved by running more")
    print("  or fewer experiments. It is a property of the cadence alone.")
    print()

    lams = {}
    print("  Revision rate from each standard's OWN history:")
    for name, yrs in HIST.items():
        gaps = np.diff(np.array(yrs, dtype=float))
        lams[name] = 1.0 / gaps.mean()
        print(f"    {name:22s} revisions={len(gaps):2d}  mean gap={gaps.mean():6.3f} yr"
              f"  lambda={lams[name]:.6f}/yr")
    worst = max(lams, key=lams.get)
    lam_worst = lams[worst]
    print(f"  worst case is {worst} at lambda={lam_worst:.6f}/yr")
    print()

    print("  Exposure fraction by cadence (his proposal is T = 30):")
    print(f"    {'T (days)':>9} " + " ".join(f"{k.split()[0]:>12}" for k in lams)
          + f" {'worst':>10} {'checks/yr':>10}")
    for td in (1, 7, 14, 30, 60, 90, 180, 365):
        vals = [L * td / 2 / 365.25 for L in lams.values()]
        print(f"    {td:>9} " + " ".join(f"{v:>12.6f}" for v in vals)
              + f" {max(vals):>10.6f} {365.25 / td:>10.1f}")
    e30 = float(lam_worst * 30 / 2 / 365.25)
    print()
    print(f"  exposure_T30_GHS = {e30:.6f}")
    print()

    print("  CROSS-CHECK -- ANCHORED TO THE EXACT LAW, tolerance DERIVED from the")
    print("  simulation's own standard error over "
          f"{len(CROSS_CHECK_SEEDS)} independent seeds.")
    print("  ★ WHAT STOOD HERE WAS REFUTED by BOTH free panel seats, independently,")
    print("  in the joint round of 2026-11-13: it compared a SINGLE seed against the")
    print("  FIRST-ORDER form at a typed tolerance of 0.12 -- wider than that form's")
    print("  own truncation error of 0.0838 at T=180 -- and printed `agree on 4 of 4`.")
    print("  A cross-check that cannot distinguish its own answer from one 8 per cent")
    print("  away is not a second route. The repair had been WRITTEN IN A DOCSTRING")
    print("  WITH NO CALLER, which is this project's most frequent defect occurring")
    print("  inside the instrument built to study it.")
    print()
    print(f"    {'lambda':>9} {'T':>5} {'MC mean':>10} {'MC s.e.':>10} {'exact':>10}"
          f" {'z_exact':>9} {'1st-order':>10} {'z_1st':>8}")
    worst_z = 0.0
    biggest_lamT = (None, 0.0)
    for L in (min(lams.values()), lam_worst):
        for td in (30, 180):
            mc, se = exposure_simulated_many(L, td)
            ex = exposure_exact_value(L, td)
            fo = L * td / 2 / 365.25
            z_ex = (mc - ex) / se
            z_fo = (mc - fo) / se
            worst_z = max(worst_z, abs(z_ex))
            if L * td > biggest_lamT[1]:
                biggest_lamT = ((abs(z_ex), abs(z_fo)), L * td)
            print(f"    {L:>9.6f} {td:>5} {mc:>10.6f} {se:>10.6f} {ex:>10.6f}"
                  f" {z_ex:>9.2f} {fo:>10.6f} {z_fo:>8.2f}")
            assert abs(z_ex) < CROSS_CHECK_Z, (
                f"the simulation rejects the EXACT law at lambda={L}, T={td}: "
                f"z={z_ex:.2f} beyond {CROSS_CHECK_Z} standard errors")
    print(f"    worst |z| against the exact law = {worst_z:.2f}, "
          f"tolerance {CROSS_CHECK_Z} standard errors")
    # THE VACUITY GUARD. Where the 2 forms differ most, the simulation must PREFER
    # the exact one. A tolerance that cannot express that preference is a tolerance
    # absorbing the truncation error, which is what the typed 0.12 did.
    z_ex_big, z_fo_big = biggest_lamT[0]
    print(f"    at the largest lambda*T: |z| exact {z_ex_big:.2f} vs first-order "
          f"{z_fo_big:.2f} -> the simulation PREFERS the exact law: "
          f"{z_fo_big > z_ex_big}")
    assert z_fo_big > z_ex_big, (
        "the cross-check cannot distinguish the exact law from its own first-order "
        "term, so it is not a second route")
    m = mp.mpf(lam_worst) * 30 / 2 / mp.mpf("365.25")
    print(f"    mpmath 40 dps first-order at T=30 = {mp.nstr(m, 12)}   "
          f"NumPy = {e30:.12f}")
    assert abs(float(m) - e30) < 1e-15, "mpmath and NumPy must agree"
    print()

    print("  What a 1 per cent exposure ceiling requires:")
    t_max = sp.solve(sp.Eq(frac, sp.Rational(1, 100)), T)[0]
    tmax_worst = float(t_max.subs(lam, lam_worst))
    print(f"    {'standard':22s} {'first-order':>12} {'EXACT':>10} {'delta d':>9}")
    for name, L in lams.items():
        fo = float(t_max.subs(lam, L))
        ex = exposure_ceiling_cadence(L, 0.01)        # <- its FIRST caller here
        print(f"    {name:22s} {fo:>12.4f} {ex:>10.4f} {ex - fo:>9.4f}")
    tmax_worst_exact = exposure_ceiling_cadence(lam_worst, 0.01)
    print(f"  T_max_worst_days = {tmax_worst:.2f}          (first-order, retained "
          f"and declared)")
    print(f"  T_max_worst_days_exact = {tmax_worst_exact:.4f}")
    print("  ★ THE EXACT CEILING IS LOOSER THAN THE FIRST-ORDER ONE, because the")
    print("  first-order form OVERSTATES exposure. `exposure_ceiling_cadence` had")
    print("  NO CALLER in this producer until the joint round of 2026-11-13; both")
    print("  seats found it. An addition nothing reaches is not a repair.")
    assert tmax_worst_exact > tmax_worst, (
        "the exact ceiling must exceed the first-order one")
    print(f"  His 30 days clears the ceiling for 3 of 4 and misses it for {worst}.")
    print()
    print("  UPPER BOUND, NOT AN ESTIMATE: every stale run counts as exposed even")
    print("  when the revision did not touch the clause in use. True harm is")
    print("  exposure x P(revision is material), and P(material) is measured")
    print("  nowhere in this project.")
    print()
    print("  ROBUSTNESS across a 20x range of lambda, so the recommendation does")
    print("  not rest on recalled revision dates:")
    for L in (0.05, 0.09, 0.2, 0.5, 1.0):
        print(f"    lambda={L:4.2f}/yr -> exposure at T=30 is {L * 30 / 2 / 365.25:.6f}"
              f", 1 per cent ceiling at T={float(t_max.subs(lam, L)):7.2f} days")
    print()

    print("=" * 78)
    print("2  IS A TYPED MODEL VERSION THE DEFECT?  Census of live source")
    print("=" * 78)
    typed, alias = version_census(exclude_self=True)
    t_in, a_in = version_census(exclude_self=False)
    nt, na = len(typed), len(alias)
    n = nt + na
    print(f"  model-identity literals in live code (docstrings and harvests excluded) = {n}")
    print(f"    apparatus check: including the {len(prod_apparatus())} apparatus "
          f"file(s) the figures are {len(t_in)} of {len(t_in) + len(a_in)}; they are "
          f"EXCLUDED below because an instrument is not a member of its own population")
    print(f"    version-bearing, goes stale = {nt}")
    print(f"    bare alias, does not        = {na}")
    iv = intervals(nt, n)
    ph = iv["p_hat"]
    wl, wh = iv["wilson_statsmodels"]
    centre_lo, centre_hi = iv["wilson_closed_form"]
    cl, ch = iv["clopper_pearson_statsmodels"]
    c2l, c2h = iv["clopper_pearson_scipy"]
    print("  ★ SUPERSEDED: `share_version_bearing = 0.253054` -> the value below.")
    print("  The figure did not change because the code changed; the POPULATION was")
    print("  wrong in 2 ways. The fable seat found the 1st in the blind round of")
    print("  2026-11-13: it counts Claude-family literals only, not all providers.")
    print("  The 2nd is larger and was found after that round: "
          "experimental_notes/seat_evidence/")
    print("  holds archived Python files from earlier panel rounds, and every one")
    print("  of them was inside the population -- so the figure was counting other")
    print("  models' sandbox output as this project's live source.")
    print(f"  share_version_bearing = {ph:.6f}")
    print(f"    POPULATION: Claude-family identity literals only "
          f"({', '.join(CLAUDE_FAMILIES)}). A provider-agnostic recount is a "
          f"different and larger population; see CLAUDE_FAMILIES.")
    print(f"    Wilson statsmodels  [{wl:.6f}, {wh:.6f}]")
    print(f"    Wilson closed form  [{centre_lo:.6f}, {centre_hi:.6f}]")
    print(f"    Clopper-Pearson sm  [{cl:.6f}, {ch:.6f}]")
    print(f"    Clopper-Pearson sps [{c2l:.6f}, {c2h:.6f}]")
    d1 = max(abs(wl - centre_lo), abs(wh - centre_hi))
    d2 = max(abs(cl - c2l), abs(ch - c2h))
    print(f"    2 Wilson routes agree to {d1:.3e}; 2 Clopper-Pearson routes to {d2:.3e}")
    assert d1 < 1e-9 and d2 < 1e-9, "the 2 interval routes must agree"
    groups = Counter()
    for f, _, _ in typed:
        if "/tests/" in f or f.startswith("bench/tests"):
            groups["tests"] += 1
        elif "cdsfl_registry/" in f:
            groups["cdsfl_registry"] += 1
        elif f.startswith("scripts/"):
            groups["scripts"] += 1
        else:
            groups["other live"] += 1
    print("  by role, because a pin in a test is not a pin in a route:")
    for k, v in groups.most_common():
        print(f"    {v:>4}  {k}")
    print()
    print("  THE ROUTE ITSELF, lifted from the panel's syntax tree:")
    rows = seats_from_syntax_tree()
    free = [r for r in rows if r[2] == "claude_cli"]
    for r in rows:
        tag = "VERSION-PINNED" if VER.search(str(r[1])) else "alias, no version"
        paid = "free, Max" if r[2] == "claude_cli" else "PAID"
        print(f"    {r[0]:<8} model={str(r[1]):<22} api={str(r[2]):<12} {paid:<10} {tag}")
    print(f"  seat_rows_lifted = {len(rows)}; free_claude_cli_seats = {len(free)}")
    assert rows, ("the seat table lifted as EMPTY. A guess at the binding name "
                  "returns 0 rows and reads exactly like a real empty table, so "
                  "this refuses rather than reporting 'no versions pinned'.")
    assert len(free) == 2, f"expected 2 free claude_cli seats, lifted {len(free)}"
    pinned_free = [r for r in free if VER.search(str(r[1]))]
    print(f"  free_seats_pinning_a_version = {len(pinned_free)}")
    print("  So the panel dispatch pins NO version for the free seats: it names an")
    print("  alias, and the alias resolves to whatever the installed CLI serves.")
    print()

    print("=" * 78)
    print("3  THE CLI VERSION GATE -- 1 side DERIVED, 1 side a DATED OBSERVATION")
    print("=" * 78)
    print("  ★ THE HEADING HERE USED TO READ 'measured live on the Max")
    print("  subscription' while both figures were typed constants. The fable")
    print("  seat named that as its strongest disagreement in the blind round of")
    print("  2026-11-13 and it was right: a brief whose thesis is DERIVED-NOT-TYPED")
    print("  shipped its own model-staleness evidence as a typed constant.")
    live = _installed_cli_version()
    print(f"    installed CLI, DERIVED by running `claude --version` now = "
          f"{'.'.join(map(str, live)) if live else 'NOT DETERMINED'}")
    print(f"    typed constant for comparison = {'.'.join(map(str, CLI_INSTALLED))}")
    if live and live != CLI_INSTALLED:
        print(f"    ★ THE TYPED CONSTANT IS NOW STALE -- this is the defect, live.")
    print("    the REQUIRED versions below are a DATED OBSERVATION of 2026-11-13,")
    print("    read from the upstream refusal itself, not re-executed here: a probe")
    print("    costs a dispatch, and the observation is recorded with its date")
    print("    rather than relabelled as a measurement.")
    for mid, need in CLI_REQUIRED.items():
        print(f"  {mid:20s} needs {'.'.join(map(str, need))}"
              f"  installed {'.'.join(map(str, CLI_INSTALLED))}"
              f"  gap = {need[2] - CLI_INSTALLED[2]:>3} patch releases")
    gap = CLI_REQUIRED["claude-fable-5-2"][2] - CLI_INSTALLED[2]
    print(f"  cli_patch_gap_fable_5_2 = {gap}")
    print("  The newest Fable is REAL -- the upstream response names its own minimum")
    print("  CLI version -- and it is UNREACHABLE from this machine. Nothing in the")
    print("  repository could have reported that, because the aliveness probe asks")
    print("  whether a route answers and never which model answered.")
    print()

    print("=" * 78)
    print("4  DO A CURRENCY CHECK AND PER-RUN PROVENANCE COMPOSE, IN HIS SENSE?")
    print("=" * 78)
    print("  ★ THE COUNT THAT STOOD HERE IS REFUTED: `composed_covers = 5 of 5`")
    print("  WAS NOT A DOMINANCE MEASUREMENT, and both")
    print("  free panel seats killed it independently in the blind round of")
    print("  2026-11-13 by different arguments. Both are kept because both bite.")
    print()
    print("  fable's argument, which is the decisive one: coverage of a composition")
    print("  is the UNION of the parts' coverage, so |composed| >= max(|part|)")
    print("  ALWAYS. The table could never come out against composing. An")
    print("  instrument that cannot return the answer it was built to test is not")
    print("  a measurement -- it is a rubric wearing a number.")
    print()
    print("  cc2's argument: a count is a sum of indicators over an AUTHOR-CHOSEN")
    print("  partition, and re-partitioning the SAME coverage reverses the ranking.")
    modes = {
        "F1 encoding silently falls behind a revised standard": (True, False),
        "F2 a past severity cannot be attributed to the standard it used": (False, True),
        "F3 a past run cannot be reproduced after a revision": (False, True),
        "F4 an update partitions the archive with no epoch recorded": (False, True),
        "F5 a revision occurs that the check fails to detect": (False, True),
    }
    partitions = {
        "as first enumerated": modes,
        "F1 split per standard feed (4 standards)": {
            **{f"F1.{i} revision of {k.split()[0]} undetected": (True, False)
               for i, k in enumerate(HIST, 1)},
            **{k: v for k, v in modes.items() if not k.startswith("F1")},
        },
        "F2-F4 merged into 1 archive consequence": {
            "F1 encoding silently falls behind a revised standard": (True, False),
            "F2-F4 the archive cannot be attributed, reproduced or partitioned": (False, True),
            "F5 a revision occurs that the check fails to detect": (False, True),
        },
    }
    print(f"    {'partition':<42}{'check':>6}{'prov':>6}{'both':>6}  winner alone")
    winners = set()
    for name, mm in partitions.items():
        nc = sum(1 for c, _ in mm.values() if c)
        npv = sum(1 for _, pv in mm.values() if pv)
        nb = sum(1 for c, pv in mm.values() if c or pv)
        w = "check" if nc > npv else ("provenance" if npv > nc else "TIE")
        winners.add(w)
        print(f"    {name:<42}{nc:>6}{npv:>6}{nb:>6}  {w}")
    print(f"  the count's winner changes under re-partition = {len(winners) > 1}")
    print()
    print("  WHAT SURVIVES, PARTITION-INVARIANT: strict SET INCLUSION. F1 is in")
    print("  check-minus-provenance in every partition above, so")
    print("  covered(composition) STRICTLY contains covered(provenance). That is a")
    print("  set fact, carries no weights, and needs no partition.")
    inclusion_holds = all(
        any(c and not pv for c, pv in mm.values()) for mm in partitions.values())
    print(f"  F1 in check \\ provenance in ALL partitions = {inclusion_holds}")
    print()
    print("  AND THE MEASUREMENT THE FOUNDER'S STANDARD ACTUALLY ASKS FOR, which is")
    print("  fable's and is on a ratio scale: provenance ALONE leaves the detection")
    print("  LATENCY of a superseded standard unbounded -- a human notices")
    print("  eventually, at a rate measured nowhere. Adding the detect-only check")
    print("  BOUNDS that latency at an expected T/2. That is a named property with")
    print("  a derivable advantage over the better single repair.")
    lam_worst2 = max(1.0 / np.diff(np.array(y, dtype=float)).mean()
                     for y in HIST.values())
    for Td in (30, 90, 180):
        print(f"    T={Td:>4}d -> expected detection latency {Td / 2:6.1f} d, "
              f"exact exposure {exposure_exact_value(lam_worst2, Td):.6f} "
              f"(first-order {lam_worst2 * Td / 2 / 365.25:.6f})")
    print("    provenance alone -> latency UNBOUNDED, exposure not reduced at all")
    assert inclusion_holds, "if set inclusion fails, prefer the single repair"
    print()
    print("=" * 78)
    print("5  WHAT HIS CADENCE WOULD ALREADY HAVE DONE TO THE EXISTING ARCHIVE")
    print("=" * 78)
    start, today = dt.date(2026, 8, 1), dt.date(2026, 11, 13)
    days = (today - start).days
    print(f"  project record 2026-08-01 to 2026-11-13 = {days} days")
    print()
    print("  ★ THE FIGURE THAT STOOD HERE IS REFUTED: `archive_epochs_at_T30 = 4`.")
    print("  REFUTED, continued: it read `archive_epochs_at_T30 = 4 encoding")
    print("  versions after 3 checks`,")
    print("  computed as days//30 + 1. That counts CHECK BOUNDARIES. An encoding")
    print("  version is created by a REVISION, and a check that finds nothing")
    print("  creates nothing. Found by the fable seat in the blind round of")
    print("  2026-11-13 and confirmed here.")
    boundaries = days // 30 + 1
    lam_sum = sum(1.0 / np.diff(np.array(y, dtype=float)).mean() for y in HIST.values())
    m = lam_sum * days / 365.25
    p_ge3 = float(1.0 - sps.poisson.cdf(2, m))
    p_ge1 = float(1.0 - sps.poisson.cdf(0, m))
    print(f"    check boundaries at T=30 over {days} days = {boundaries}")
    print(f"    combined revision rate across the 4 standards = {lam_sum:.6f}/yr")
    print(f"    expected_revisions_in_window = {m:.6f}")
    print(f"    P(at least 1 revision)  = {p_ge1:.6f}")
    print(f"    P(at least 3 revisions) = {p_ge3:.6f}   <- what 4 epochs required")
    print(f"    expected_epochs = {1 + m:.6f}")
    print("  So 4 epochs was a sub-1-per-cent event reported as what would already")
    print("  hold. THE QUALITATIVE CLAIM SURVIVES at any epoch count above 1,")
    print("  because 0 archived severities carry a scale or version key, so any")
    print("  partition at all would be invisible.")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
