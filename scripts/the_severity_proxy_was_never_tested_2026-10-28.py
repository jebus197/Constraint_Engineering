#!/usr/bin/env python3
"""Was the 0.7 severity proxy ever actually TESTED against its pre-registered rubric?

HIS INSTRUCTION, 2026-10-28, verbatim from his annotation on the overnight
report: *"Then do the measurement first."* He promoted this measurement ahead of
the convergence condition his earlier ruling had made it conditional on.

THE QUESTION AS REGISTERED, `qs:c2e25a1e79c1`: "Re-measure the 0.7 proxy against
its pre-registered rubric, kappa last read as chance."

THE ANSWER IS NO, AND THAT IS THE FINDING. The measurement that exists was run
on a BOUNDARY BAND, and a boundary band cannot answer the question that was
asked of it. Every figure below is recomputed here from the stored audit and
from the archive; none is carried over as prose.

WHAT WAS ALREADY ON THE RECORD, AND IS REPRODUCED EXACTLY HERE. The consequence
rubric frozen at `bench/exp40_baseline/CRITICAL_DEFINITION_PREREG_2026-05-18.md`
was scored blind against 286 archived findings on 2026-09-02, and its agreement
with the `severity >= 0.7` proxy read kappa = -0.022688 with Fisher p = 0.778818
over the 259 judgeable items. `.claude/CLAUDE.md` cites that pair as the reason
a proposal to REPLACE the model-derived severity with the rubric was wrong: "a
rubric it had already measured as agreeing no better than chance".

WHY THAT CITATION OVERSTATES WHAT THE NUMBER CAN CARRY. The audited corpus holds
severities in [0.65, 0.74] ONLY -- a window 0.09 wide, standard deviation
0.026915, against 0.224319 across the 3,237 registry entries in the archive,
whose severities span the full [0.0, 1.0]. The band holds 0.132839 of archive
severities. Restricting the predictor to a window that narrow inflates the
standard error of any slope fitted across it by the ratio of the deviations,
8.3344-fold here, and the consequence is measured below rather than asserted:

  * power against a STRONG full-range effect -- one moving P(CRITICAL) from
    0.10 at severity 0 to 0.90 at severity 1, a slope of 2*ln(9) = 4.394449 --
    is 0.1460. The design would MISS such an effect in about 85 runs in 100.
  * that strong effect PREDICTS an in-band odds ratio of 1.256464 -- the EXACT
    expected marginal figure; the first-order exp(beta . delta-mean) step gives
    1.256682, a relative error of 0.0174%, so nothing here rests on the
    approximation. The measured interval is [0.516836, 1.569980] and the
    prediction sits inside it. Stronger still: 0.792050 of simulated draws under
    that hypothesis produce a point estimate inside the SAME interval, so the
    observation is the modal outcome under the hypothesis this project's
    directive treats as excluded.

So this corpus cannot separate "no relationship" from "a strong relationship":
both predict an in-band odds ratio the interval covers. kappa = -0.022688 is
therefore UNINFORMATIVE about the proxy, not negative about it. The founder's
catch of the replacement proposal stands -- the replacement would change
behaviour precisely at the cut, which is where the band measured chance -- but
the general claim his directive currently states is not supported by it.

THE BAND DOES NOT EXPLAIN IT AWAY EITHER, AND THIS IS THE FALSIFICATION THE
FINDING SURVIVED. If range restriction were a blanket excuse, the rubric's own
readers would look unreliable in the band too. They do not: the 2 blind readers
agree with EACH OTHER at kappa 0.836883 on the 93 shared judgeable items, raw
agreement 0.924731, Fisher p = 6.230872e-17, while agreeing with the proxy at
kappa +0.016913 and +0.157562 on those same items. Restriction bites on the
CONTINUOUS predictor, not on the binary construct both readers judge, so the
labels are sound and only the proxy comparison is crippled. The 2 results are
consistent, and together they say the rubric is a reliable instrument whose
relationship to the number has never been measured where it varies.

DICHOTOMISATION IS NOT THE CAUSE, which had to be ruled out before range
restriction could be blamed. Continuous severity does not predict the rubric
verdict inside the band either: logistic slope -4.199407, p = 0.387828;
Mann-Whitney p = 0.308546; and the mean severity is marginally HIGHER for
NON_CRITICAL (0.695426) than for CRITICAL (0.692424). Throwing away the 10
distinct severity values by cutting at 0.7 is not what produced the null.

THE COSTED ASK, BY SIMULATION RATHER THAN BY CLOSED FORM. A full-range
adjudication sample reaches 80% power against the strong effect at about 48
items; 50 gives 0.8397 and 63 gives 0.9207. The 63 the project already costed
from an exact power calculation on the measured discordance is therefore
sufficient, and conservative. THE CLOSED FORM MUST NOT BE QUOTED: it says 35,
and simulation at 35 gives 0.6472, so the analytic figure is optimistic by a
wide margin. That disagreement is why the 2-tool rule exists.

WHAT THIS SCRIPT CANNOT DO. The audit's method line records that severity was
"withheld and redacted from 80 of 286 texts", but NO PER-ITEM REDACTION FLAG IS
STORED, so the 80 blinded items cannot be located. The clean arm of the existing
instrument is unrecoverable, and 206 of the 259 verdicts may have been formed
with the number in view. That is a second, independent reason the stored kappa
cannot settle the question, and it cannot be repaired by analysis -- only by a
fresh adjudication that records its own blinding per item.

Run with --help to read this without computing anything.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

import numpy as np

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
from _cli_help import answer_help  # noqa: E402

AUDIT = (REPO / "experimental_notes" / "adversarial_records"
         / "rubric_adherence_audit_0C8_2026-09-02.json")
LOGS = REPO / "bench" / "logs"
CUT = 0.7
SEED = 20261028
# The strong full-range effect this design is tested against: P(CRITICAL)
# running 0.10 at severity 0 to 0.90 at severity 1. Stated as a hypothesis to
# be powered against, NOT as a claim that the effect exists.
STRONG_SLOPE_LOG9 = 2.0
#: Draws for the compatibility share. FIXED, so the figure cannot drift
#: when an unrelated knob moves; 20,000 is where it is stable to 4 decimals.
COMPATIBILITY_DRAWS = 20000


def _audit_rows() -> tuple[np.ndarray, np.ndarray, dict]:
    """Judgeable items only, as (severity, rubric_is_critical) plus the raw doc."""
    doc = json.loads(AUDIT.read_text(encoding="utf-8"))
    gt = doc["ground_truth"]
    first = {x["item"]: x["verdict"] for x in doc["first_pass"]}
    keep = [i for i in sorted(first) if first[i] != "UNJUDGEABLE"]
    sev = np.array([gt[str(i)][0] for i in keep], dtype=float)
    crit = np.array([1 if first[i] == "CRITICAL" else 0 for i in keep], dtype=int)
    return sev, crit, doc


def _archive_severities() -> np.ndarray:
    """Every registry severity in the archive -- the real sampling frame."""
    out: list[float] = []
    for p in sorted(LOGS.glob("*/runner_state.json")):
        try:
            entries = json.loads(p.read_text(encoding="utf-8")) \
                          .get("registry", {}).get("entries", {})
        except (OSError, ValueError):
            continue          # an unreadable run must not silence the rest
        for e in entries.values():
            if isinstance(e, dict) and isinstance(e.get("severity"), (int, float)):
                out.append(float(e["severity"]))
    return np.array(out, dtype=float)


def _kappa(x: np.ndarray, y: np.ndarray) -> tuple[float, float, float]:
    """Cohen kappa by hand, so it is cross-checkable against sklearn."""
    n = len(x)
    po = float((x == y).mean())
    pe = float(x.mean() * y.mean() + (1 - x.mean()) * (1 - y.mean()))
    return (po - pe) / (1 - pe), po, pe


def _table(x: np.ndarray, y: np.ndarray) -> list[list[int]]:
    return [[int(((x == 1) & (y == 1)).sum()), int(((x == 1) & (y == 0)).sum())],
            [int(((x == 0) & (y == 1)).sum()), int(((x == 0) & (y == 0)).sum())]]


def _power(sev_frame: np.ndarray, n: int, slope: float, trials: int,
           base_p: float, rng: np.random.Generator) -> float:
    """Share of simulated draws in which the slope is detected at alpha 0.05."""
    import statsmodels.api as sm
    hits = usable = 0
    centre = float(sev_frame.mean())
    for _ in range(trials):
        x = rng.choice(sev_frame, size=n, replace=n > len(sev_frame))
        eta = np.log(base_p / (1 - base_p)) + slope * (x - centre)
        y = (rng.random(n) < 1.0 / (1.0 + np.exp(-eta))).astype(int)
        if y.sum() in (0, n):
            continue          # a degenerate draw cannot be fitted
        try:
            fit = sm.Logit(y, sm.add_constant(x)).fit(disp=0)
        except Exception:
            continue
        usable += 1
        if fit.pvalues[1] < 0.05:
            hits += 1
    return hits / usable if usable else float("nan")


def measure(trials: int = 4000) -> dict:
    """Every figure in the docstring, recomputed. Returns them for the guard."""
    import statsmodels.api as sm
    from scipy import stats
    from sklearn.metrics import cohen_kappa_score
    from statsmodels.stats.contingency_tables import Table2x2
    import mpmath as mp

    sev, crit, doc = _audit_rows()
    proxy = (sev >= CUT).astype(int)
    r = {"n_judgeable": len(sev), "n_audited": len(doc["first_pass"])}

    # --- 1. the stored result, reproduced, 2 tools -------------------------
    r["table"] = _table(proxy, crit)
    k_manual, po, pe = _kappa(proxy, crit)
    r["kappa"] = float(cohen_kappa_score(proxy, crit))
    r["kappa_manual"] = k_manual
    r["p_observed"], r["p_expected"] = po, pe
    t2 = Table2x2(r["table"])
    r["odds_ratio"] = float(t2.oddsratio)
    lo, hi = t2.oddsratio_confint()
    r["or_ci"] = (float(lo), float(hi))
    r["fisher_p"] = float(stats.fisher_exact(r["table"])[1])

    # --- 2. dichotomisation is not the cause ------------------------------
    fit = sm.Logit(crit, sm.add_constant(sev)).fit(disp=0)
    r["logit_slope"] = float(fit.params[1])
    r["logit_se"] = float(fit.bse[1])
    r["logit_p"] = float(fit.pvalues[1])
    r["mw_p"] = float(stats.mannwhitneyu(sev[crit == 1], sev[crit == 0],
                                         alternative="two-sided")[1])
    r["mean_sev_critical"] = float(sev[crit == 1].mean())
    r["mean_sev_noncritical"] = float(sev[crit == 0].mean())

    # --- 3. the band, against the real sampling frame ---------------------
    frame = _archive_severities()
    r["archive_n"] = len(frame)
    r["archive_sd"] = float(frame.std(ddof=1))
    r["band_sd"] = float(sev.std(ddof=1))
    r["sd_ratio"] = r["archive_sd"] / r["band_sd"]
    r["archive_range"] = (float(frame.min()), float(frame.max()))
    r["share_in_band"] = float(((frame >= sev.min()) & (frame <= sev.max())).mean())

    # --- 4. power, analytic AND simulated ---------------------------------
    base_p = float(crit.mean())
    r["base_p"] = base_p
    strong = STRONG_SLOPE_LOG9 * float(np.log(9))
    r["strong_slope"] = strong
    r["strong_slope_mpmath"] = float(STRONG_SLOPE_LOG9 * mp.log(9))
    se_analytic = 1.0 / (r["band_sd"] * np.sqrt(len(sev) * base_p * (1 - base_p)))
    r["se_analytic"] = float(se_analytic)
    r["se_observed"] = r["logit_se"]
    z_a, z_b = stats.norm.ppf(0.975), stats.norm.ppf(0.80)
    r["min_detectable_slope"] = float((z_a + z_b) * se_analytic)
    rng = np.random.default_rng(SEED)
    r["power_at_min_detectable"] = _power(sev, len(sev), r["min_detectable_slope"],
                                          trials, base_p, rng)
    r["power_vs_strong_in_band"] = _power(sev, len(sev), strong, trials, base_p, rng)

    # --- 5. the decisive prediction ---------------------------------------
    # 3 FIGURES, NOT 1, BECAUSE THE FIRST IS AN APPROXIMATION. Translating a
    # continuous slope into a DICHOTOMISED odds ratio by exp(beta * delta-mean)
    # is first-order only; the exact expected marginal odds ratio integrates the
    # per-item probabilities over each side of the cut. They agree to 0.0174%
    # here, so the finding does not rest on the approximation -- but the exact
    # figure is the one to quote, and the check is the reason we know.
    dmu = float(sev[proxy == 1].mean() - sev[proxy == 0].mean())
    r["dichotomy_separation"] = dmu
    r["or_predicted_first_order"] = float(np.exp(strong * dmu))
    r["or_predicted_mpmath"] = float(mp.e ** (mp.mpf(strong) * mp.mpf(dmu)))
    alpha = float(np.log(base_p / (1 - base_p)))
    probs = 1.0 / (1.0 + np.exp(-(alpha + strong * (sev - sev.mean()))))
    hi_1, hi_0 = probs[proxy == 1].sum(), (1 - probs[proxy == 1]).sum()
    lo_1, lo_0 = probs[proxy == 0].sum(), (1 - probs[proxy == 0]).sum()
    r["or_predicted_by_strong"] = float((hi_1 / hi_0) / (lo_1 / lo_0))
    r["or_first_order_relative_error"] = abs(
        r["or_predicted_by_strong"] - r["or_predicted_first_order"]) \
        / r["or_predicted_by_strong"]
    r["strong_prediction_inside_ci"] = bool(
        r["or_ci"][0] <= r["or_predicted_by_strong"] <= r["or_ci"][1])
    # AND THE STRONGER STATEMENT. "Inside the interval" only says the
    # observation is not ruled out. This asks how OFTEN the strong hypothesis
    # would produce a point estimate inside the interval actually measured, so a
    # high share means the observation is the MODAL outcome under the hypothesis
    # the project's directive treats as excluded.
    # ITS OWN GENERATOR AND ITS OWN FIXED DRAW COUNT. Sharing the power
    # simulations' generator made this figure move when `--trials` moved, which
    # is how a quotable number silently stops matching the prose that quotes it.
    rng_c = np.random.default_rng(SEED + 1)
    ors = []
    for _ in range(COMPATIBILITY_DRAWS):
        y = rng_c.random(len(sev)) < probs
        a = int((y & (proxy == 1)).sum()); b = int((~y & (proxy == 1)).sum())
        c = int((y & (proxy == 0)).sum()); dd = int((~y & (proxy == 0)).sum())
        if 0 in (a, b, c, dd):
            continue          # an undefined odds ratio is not a small one
        ors.append((a / b) / (c / dd))
    ors_a = np.array(ors)
    r["strong_draws_usable"] = len(ors)
    r["strong_median_or"] = float(np.median(ors_a)) if len(ors_a) else float("nan")
    r["strong_share_inside_measured_ci"] = float(
        ((ors_a >= r["or_ci"][0]) & (ors_a <= r["or_ci"][1])).mean()
    ) if len(ors_a) else float("nan")

    # --- 6. the instrument's own reliability ------------------------------
    first = {x["item"]: x["verdict"] for x in doc["first_pass"]}
    second = {x["item"]: x["verdict"] for x in doc["second_pass"]}
    shared = [i for i in sorted(second)
              if first.get(i) != "UNJUDGEABLE" and second[i] != "UNJUDGEABLE"]
    r1 = np.array([1 if first[i] == "CRITICAL" else 0 for i in shared])
    r2 = np.array([1 if second[i] == "CRITICAL" else 0 for i in shared])
    r["n_shared"] = len(shared)
    r["reader_kappa"] = float(cohen_kappa_score(r1, r2))
    r["reader_agreement"] = float((r1 == r2).mean())
    r["reader_fisher_p"] = float(stats.fisher_exact(_table(r1, r2))[1])
    px = (np.array([doc["ground_truth"][str(i)][0] for i in shared]) >= CUT).astype(int)
    r["reader1_vs_proxy_kappa"] = float(cohen_kappa_score(px, r1))
    r["reader2_vs_proxy_kappa"] = float(cohen_kappa_score(px, r2))
    r["reader1_vs_proxy_p"] = float(stats.fisher_exact(_table(px, r1))[1])
    r["reader2_vs_proxy_p"] = float(stats.fisher_exact(_table(px, r2))[1])

    # --- 7. what a full-range design would cost ---------------------------
    rng = np.random.default_rng(SEED)
    r["full_range_power"] = {n: _power(frame, n, strong, trials, base_p, rng)
                             for n in (35, 50, 63)}
    r["n_analytic_closed_form"] = float(
        ((z_a + z_b) / (strong * r["archive_sd"])) ** 2 / (base_p * (1 - base_p)))

    # --- 7b. THE OBJECTION THAT THE BAND IS ALL THAT MATTERS, ANSWERED ----
    # "The gate only ever acts AT the cut, so in-band agreement is the only
    # agreement that matters operationally." It is the strongest objection to
    # this finding and it is FALSE, measurably: the gate's critical calls are
    # overwhelmingly made FAR above the cut, where nothing is known.
    band_lo, band_hi = float(sev.min()), float(sev.max())
    above = frame > band_hi
    below = frame < band_lo
    crit_all = frame >= CUT
    r["band_bounds"] = (band_lo, band_hi)
    r["archive_above_band"] = int(above.sum())
    r["archive_below_band"] = int(below.sum())
    r["archive_outside_band"] = int((above | below).sum())
    r["archive_outside_share"] = float((above | below).mean())
    r["archive_critical"] = int(crit_all.sum())
    r["critical_above_band"] = int(above.sum())
    # Every entry above the band's top is above the cut, so this is the share of
    # the gate's CRITICAL calls made at a severity the audit never examined.
    r["critical_calls_unexamined_share"] = (
        float(above.sum() / crit_all.sum()) if crit_all.sum() else float("nan"))
    r["outside_share_cp"] = tuple(
        float(x) for x in stats.binomtest(r["archive_outside_band"],
                                          len(frame)).proportion_ci(method="exact"))

    # --- 8. the limit that analysis cannot repair -------------------------
    blob = json.dumps(doc)
    r["per_item_redaction_flag_present"] = ("redacted_items" in blob
                                            or "is_redacted" in blob)
    r["method_line"] = doc["method"]
    return r


def main() -> int:
    answer_help(__doc__, __file__)
    ap = argparse.ArgumentParser(description="Re-measure the 0.7 severity proxy "
                                             "against its pre-registered rubric.")
    ap.add_argument("--trials", type=int, default=4000,
                    help="simulation draws per power figure (default 4000)")
    ap.add_argument("--json", action="store_true",
                    help="emit the figures as JSON instead of prose")
    args = ap.parse_args()

    r = measure(trials=args.trials)
    if args.json:
        print(json.dumps(r, indent=2, default=str))
        return 0

    w = 78
    print("=" * w)
    print("WAS THE 0.7 SEVERITY PROXY EVER TESTED AGAINST ITS RUBRIC?")
    print("=" * w)
    print(f"\n1. THE STORED RESULT, REPRODUCED ({r['n_judgeable']} judgeable "
          f"of {r['n_audited']} audited)")
    print(f"   2x2 [[CRIT+, NON+], [CRIT-, NON-]] = {r['table']}")
    print(f"   agreement observed {r['p_observed']:.6f} against expected "
          f"{r['p_expected']:.6f}")
    print(f"   kappa sklearn {r['kappa']:+.6f};  by hand {r['kappa_manual']:+.6f}"
          f"  (differ by {abs(r['kappa'] - r['kappa_manual']):.2e})")
    print(f"   odds ratio {r['odds_ratio']:.6f}, 95% CI "
          f"[{r['or_ci'][0]:.6f}, {r['or_ci'][1]:.6f}], Fisher p {r['fisher_p']:.6f}")

    print("\n2. DICHOTOMISATION IS NOT THE CAUSE")
    print(f"   continuous severity as predictor: slope {r['logit_slope']:+.6f}, "
          f"SE {r['logit_se']:.6f}, p {r['logit_p']:.6f}")
    print(f"   Mann-Whitney p {r['mw_p']:.6f}")
    print(f"   mean severity CRITICAL {r['mean_sev_critical']:.6f} against "
          f"NON_CRITICAL {r['mean_sev_noncritical']:.6f}")

    print("\n3. THE CORPUS IS A BOUNDARY BAND")
    print(f"   band SD {r['band_sd']:.6f} against archive SD {r['archive_sd']:.6f} "
          f"over {r['archive_n']} entries")
    print(f"   archive range [{r['archive_range'][0]:.4f}, "
          f"{r['archive_range'][1]:.4f}];  share inside the band "
          f"{r['share_in_band']:.6f}")
    print(f"   standard-error inflation from the restriction: "
          f"{r['sd_ratio']:.4f}-fold")

    print("\n4. WHAT THE DESIGN COULD DETECT")
    print(f"   analytic SE {r['se_analytic']:.6f} against the fit's own "
          f"{r['se_observed']:.6f}  -- the power model is validated on the real fit")
    print(f"   minimum detectable slope {r['min_detectable_slope']:.6f}; "
          f"simulated power there {r['power_at_min_detectable']:.4f} (target 0.80)")
    print(f"   power against the strong effect (slope {r['strong_slope']:.6f}): "
          f"{r['power_vs_strong_in_band']:.4f}")

    print("\n5. THE DECISIVE TEST")
    print(f"   separation the 0.7 cut achieves inside the band: "
          f"{r['dichotomy_separation']:.6f}")
    print(f"   strong effect predicts an in-band odds ratio of "
          f"{r['or_predicted_by_strong']:.6f} (EXACT marginal)")
    print(f"   first-order exp(beta . delta-mean) "
          f"{r['or_predicted_first_order']:.6f}, mpmath "
          f"{r['or_predicted_mpmath']:.6f}, relative error "
          f"{r['or_first_order_relative_error']:.6%}")
    print(f"   inside the measured interval: {r['strong_prediction_inside_ci']}")
    print(f"   and the stronger statement: {r['strong_share_inside_measured_ci']:.4f} "
          f"of draws under the strong hypothesis land INSIDE that interval")
    print(f"   (median simulated odds ratio {r['strong_median_or']:.6f}, "
          f"{r['strong_draws_usable']} usable draws)")

    print("\n6. THE RUBRIC INSTRUMENT ITSELF IS RELIABLE")
    print(f"   {r['n_shared']} shared judgeable items; the 2 blind readers agree "
          f"at kappa {r['reader_kappa']:.6f}")
    print(f"   raw agreement {r['reader_agreement']:.6f}, Fisher p "
          f"{r['reader_fisher_p']:.6e}")
    print(f"   same items against the proxy: reader 1 kappa "
          f"{r['reader1_vs_proxy_kappa']:+.6f} (p {r['reader1_vs_proxy_p']:.6f}), "
          f"reader 2 {r['reader2_vs_proxy_kappa']:+.6f} "
          f"(p {r['reader2_vs_proxy_p']:.6f})")

    print("\n7. THE COSTED ASK")
    for n, pw in sorted(r["full_range_power"].items()):
        print(f"   full-range n = {n:>3}: simulated power {pw:.4f}")
    print(f"   closed form says n = {r['n_analytic_closed_form']:.4f} and is "
          f"OPTIMISTIC; do not quote it")

    print("\n7b. 'ONLY THE BAND MATTERS' IS FALSE, MEASURABLY")
    print(f"   of {r['archive_n']} archive entries, {r['archive_outside_band']} "
          f"({r['archive_outside_share']:.6f}, Clopper-Pearson "
          f"[{r['outside_share_cp'][0]:.6f}, {r['outside_share_cp'][1]:.6f}]) were")
    print(f"   classified at a severity the audit never examined: "
          f"{r['archive_above_band']} above {r['band_bounds'][1]} and "
          f"{r['archive_below_band']} below {r['band_bounds'][0]}")
    print(f"   and {r['critical_calls_unexamined_share']:.6f} of the "
          f"{r['archive_critical']} CRITICAL calls the gate has ever made sit")
    print(f"   ABOVE the band -- confident classifications, where a disagreement "
          f"is MORE")
    print(f"   consequential than one at the cut, because nothing would prompt a "
          f"second look")

    print("\n8. THE LIMIT ANALYSIS CANNOT REPAIR")
    print(f"   per-item redaction flag stored: "
          f"{r['per_item_redaction_flag_present']}")
    print(f"   method line: {r['method_line']}")

    print("\n" + "=" * w)
    print("VERDICT")
    print("=" * w)
    print("""
  1. The 0.7 proxy has NEVER been tested against the rubric where severity
     varies. The one measurement that exists covers a 0.09-wide band at the cut.
  2. kappa = -0.022688 is UNINFORMATIVE about the proxy, not negative about it:
     the strong hypothesis predicts an in-band odds ratio of 1.256464 which the
     measured interval contains, 0.792050 of draws under that hypothesis land
     inside the same interval, and power against it is 0.1460. The observation
     is the MODAL outcome under the hypothesis the directive treats as excluded.
  3. The rubric's labels are sound -- 2 blind readers at kappa 0.836883 on the
     same items -- so the fault is the corpus, not the instrument.
  4. His catch of the replacement proposal STANDS, because the replacement acts
     at the cut and the band measured chance there. The GENERAL claim in
     `.claude/CLAUDE.md`, that the rubric agrees with the number no better than
     chance, needs the band qualifier it currently lacks.
  5. "ONLY THE BAND MATTERS" IS FALSE. 0.794744 of every CRITICAL call the gate
     has ever made sits ABOVE the audited band, and 0.867161 of all entries were
     classified at a severity the audit never examined. The gate's confident
     calls are exactly the ones nothing is known about.
  6. The 63-item adjudication already costed reaches power 0.9207 full-range.
     It is a founder task; no model can supply the labels.
""")
    return 0


if __name__ == "__main__":
    sys.exit(main())
