# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'check_my_fixes_2026-11-10', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 264ce493f6d81c0b2f57e6eb40c189ac90b7ecee888303059197bc0f63cba96a
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Which B-Cell tools return a DEFINITIVE FOR to a claim and to its corrupted twin?

WHY THIS EXISTS. `bench/domain_immune.domain_verification_set` sets
``admits = bool(definitive_for) and not definitive_against``. So ONE tool
returning CONFIRMED / VERIFIED / SUPPORTED admits a fix on its own. That is
only sound for a tool whose definitive FOR DISCRIMINATES -- one that answers
differently for a true claim and for a false one. A tool that answers CONFIRMED
to both carries no information, and its admission is not evidence-backed.

WHAT IT MEASURES. A paired discrimination control. For each claim pair
(true, corrupted) and each manifest tool that can run without a file, it
records the verdict on both halves and classifies the tool on that pair:

  DISCRIMINATES   definitive FOR on the true half, not on the false half
  NON_DISCRIM     definitive FOR on BOTH halves          <- the false-admit route
  INVERTED        definitive FOR on the false half only
  SILENT          no definitive FOR on either half

Only NON_DISCRIM and INVERTED are faults. SILENT is the correct behaviour of a
tool outside its competence and is NOT counted against it -- the B88 ruling's
operative words are "available/reducible to them".

SCOPE, STATED RATHER THAN IMPLIED. This is a sample, not a proof of the tools'
general behaviour. A tool classed SILENT here may discriminate on claims this
battery does not contain, so this script can establish that a tool DOES fail to
discriminate and cannot establish that one never will. The reported proportion
is over the pairs actually run, and each interval belongs to its own
denominator only.

Every proportion carries a 95% interval computed on 2 independent routes
(`_iv`), as the project's stated-interval rule requires.
"""
from __future__ import annotations

import argparse
import math
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]

#: Verdict strings `domain_verification_set` counts as a definitive FOR.
DEFINITIVE_FOR = ("CONFIRMED", "VERIFIED", "SUPPORTED")
#: ... and as a definitive AGAINST.
DEFINITIVE_AGAINST = ("REFUTED", "REJECTED", "CONTRADICTED")

#: (label, domain, true_claim, corrupted_claim). The corruption always makes
#: the claim FALSE while leaving its SHAPE intact, so a tool that matches shape
#: rather than checking the result is exposed.
PAIRS = [
    ("c_in_m_per_s", "physics",
     "the speed of light is 299792458 m/s",
     "the speed of light is 299792458 km/s"),
    ("earth_radius", "astronomy",
     "the radius of the Earth is 6371 km",
     "the radius of the Earth is 6371 m"),
    ("au_distance", "astronomy",
     "1 astronomical unit is 149597870700 m",
     "1 astronomical unit is 149597870700 km"),
    ("water_formula", "chemistry",
     "the molecular formula of water is H2O",
     "the molecular formula of water is H3O"),
    ("methane_formula", "chemistry",
     "the molecular formula of methane is CH4",
     "the molecular formula of methane is CH5"),
    ("arith_identity", "mathematics",
     "Eq(2 + 2, 4)",
     "Eq(2 + 2, 5)"),
    ("newton_second_law", "physics",
     "Eq(force, mass * acceleration)",
     "Eq(force, mass * velocity)"),
    ("dna_complement", "biology",
     "the complement of the DNA sequence ATGC is TACG",
     "the complement of the DNA sequence ATGC is TAGC"),
]


def _iv(k: int, n: int):
    """Wilson and Clopper-Pearson, each on 2 INDEPENDENT routes."""
    from scipy import stats
    from statsmodels.stats.proportion import proportion_confint
    import mpmath
    mpmath.mp.dps = 40
    if n == 0:
        return (0.0, 1.0), (0.0, 1.0), 0.0
    wl, wh = proportion_confint(k, n, alpha=0.05, method="wilson")
    z = stats.norm.ppf(0.975)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    hw = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    wdiff = max(abs(wl - (c - hw)), abs(wh - (c + hw)))
    cl = 0.0 if k == 0 else float(stats.beta.ppf(0.025, k, n - k + 1))
    ch = 1.0 if k == n else float(stats.beta.ppf(0.975, k + 1, n - k))

    def bi(a, b, y):
        lo, hi = mpmath.mpf(0), mpmath.mpf(1)
        for _ in range(200):
            mid = (lo + hi) / 2
            try:
                v = mpmath.betainc(a, b, 0, mid, regularized=True)
            except Exception:                                 # noqa: BLE001
                return None
            if v < y:
                lo = mid
            else:
                hi = mid
        return float((lo + hi) / 2)

    m_lo = 0.0 if k == 0 else bi(k, n - k + 1, mpmath.mpf("0.025"))
    m_hi = 1.0 if k == n else bi(k + 1, n - k, mpmath.mpf("0.975"))
    cdiff = 0.0
    for a, b in ((cl, m_lo), (ch, m_hi)):
        if b is not None:
            cdiff = max(cdiff, abs(a - b))
    return (wl, wh), (cl, ch), max(wdiff, cdiff)


def _load():
    sys.path.insert(0, str(REPO))
    sys.path.insert(0, str(REPO / "bench"))
    import immune_agents as ia
    return ia


def _verdict(ia, entry, claim: str):
    fn = entry.get("verifier")
    f = fn if callable(fn) else getattr(ia, str(fn), None)
    if not callable(f):
        return "UNRESOLVED"
    try:
        v = f(claim)
    except Exception as exc:                                  # noqa: BLE001
        return f"RAISED_{type(exc).__name__}"
    return getattr(v, "verdict", None)


def classify(v_true, v_false) -> str:
    for_t = v_true in DEFINITIVE_FOR
    for_f = v_false in DEFINITIVE_FOR
    if for_t and for_f:
        return "NON_DISCRIM"
    if for_f and not for_t:
        return "INVERTED"
    if for_t and not for_f:
        return "DISCRIMINATES"
    return "SILENT"


def main() -> int:
    ap = argparse.ArgumentParser(
        description=("Which B-Cell tools give the SAME definitive FOR to a "
                     "claim and to its corrupted twin?"))
    ap.parse_args()

    ia = _load()
    manifest = ia._load_tool_manifest()
    # NOT RUN, AND SAID RATHER THAN SILENTLY DROPPED. A first run of this
    # script hung past 120 s because some verifiers leave the process: the
    # `model` class calls a remote API, the `execute` class runs a test
    # command, and `wolfram` shells out to a kernel queued against 1 licence.
    # None can be timed inside a paired control that must finish, so they are
    # EXCLUDED and named in the output. Their discrimination is UNMEASURED
    # here -- which is not the same as measured-and-clean.
    skipped = {n: e for n, e in manifest.items()
               if e.get("needs_file")
               or e.get("independence_class") in ("model", "execute")
               or n == "wolfram"}
    runnable = {n: e for n, e in manifest.items() if n not in skipped}

    print("=" * 78)
    print("WHICH TOOLS CAN ADMIT A FALSE CLAIM ALONE -- paired discrimination")
    print("=" * 78)
    print(f"\n  manifest tools: {len(manifest)}   measured here: {len(runnable)}"
          f"   claim pairs: {len(PAIRS)}\n")
    print(f"  EXCLUDED and therefore UNMEASURED ({len(skipped)}): "
          f"{', '.join(sorted(skipped))}")
    print("    needs_file, or leaves the process (model API / test run / "
          "wolfram kernel).\n")

    rows = []
    for label, _domain, t_claim, f_claim in PAIRS:
        for name, entry in sorted(runnable.items()):
            vt = _verdict(ia, entry, t_claim)
            vf = _verdict(ia, entry, f_claim)
            rows.append((label, name, vt, vf, classify(vt, vf)))

    faults = [r for r in rows if r[4] in ("NON_DISCRIM", "INVERTED")]
    print(f"  {'pair':18} {'tool':22} {'true':11} {'false':11} class")
    print("  " + "-" * 72)
    for label, name, vt, vf, cls in rows:
        if cls == "SILENT":
            continue
        print(f"  {label:18} {name:22} {str(vt):11} {str(vf):11} {cls}")

    tools_seen = sorted(runnable)
    bad_tools = sorted({r[1] for r in faults})
    definitive_tools = sorted({r[1] for r in rows if r[4] != "SILENT"})

    print(f"\n  tools that produced ANY definitive FOR: "
          f"{len(definitive_tools)} of {len(tools_seen)}")
    print(f"    {', '.join(definitive_tools) or '-'}")
    print(f"\n  tools that FAILED to discriminate on >=1 pair: "
          f"{len(bad_tools)} of {len(definitive_tools)}")
    print(f"    {', '.join(bad_tools) or '-'}")

    k, n = len(bad_tools), len(definitive_tools)
    (wl, wh), (cl, ch), xd = _iv(k, n)
    print(f"\n  proportion {k}/{n} = {0.0 if n == 0 else k / n:.6f}")
    print(f"    wilson           [{wl:.6f}, {wh:.6f}]")
    print(f"    clopper-pearson  [{cl:.6f}, {ch:.6f}]")
    print(f"    2-route max gap  {xd:.3e}")

    kp, np_ = len(faults), len(rows)
    (wl2, wh2), (cl2, ch2), xd2 = _iv(kp, np_)
    print(f"\n  (tool, pair) cells failing to discriminate {kp}/{np_} = "
          f"{kp / np_:.6f}")
    print(f"    wilson           [{wl2:.6f}, {wh2:.6f}]")
    print(f"    clopper-pearson  [{cl2:.6f}, {ch2:.6f}]")
    print(f"    2-route max gap  {xd2:.3e}")

    print("\n  SCOPE. This establishes that the tools named above DO fail to "
          "discriminate\n  on the pairs run. It does NOT establish that a "
          "SILENT tool never will.")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
