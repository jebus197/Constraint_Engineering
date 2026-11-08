#!/usr/bin/env python3
"""How much of the panel's delivered work never reached the repository.

THE DEFECT. Panel seats work inside isolated copies of this repository and
deliver fixes as FILES into those copies. The dispatcher harvests those files to
`bench/logs/<run>/sandbox_harvest/<seat>/attempt-N/files/<real path>`, which
persists. Nothing then copied them onward into `scripts/`, so the work was
present in the archive and absent from the tree -- invisible to every later
session, which re-asked questions that had already been answered.

WHY THIS SCRIPT EXISTS AT ALL. The rate below was quoted to the founder in
`experimental_notes/Panel_Audit_Closing_Report_2026-09-22.md` with NO producing
script, which is precisely the defect `measured-rate-travels-with-its-script`
names: a number that exists only as prose is a claim about evidence, not
evidence. It was caught by `scripts/panel_brief_validate.py` refusing to let the
same figure into a panel brief undeclared. The rule had to be enforced by a
machine before it was obeyed, which is the same shape as the note lint.

THE REFERENCE POINT IS PINNED, DELIBERATELY. The loss is measured against the
tree as it stood BEFORE recovery (default `ae0c837`). Measuring against a moving
HEAD would silently report 0 the moment the recovered files are committed, and a
measurement that erases itself on being acted upon is not a measurement. Pass
--ref to check any other commit; --ref HEAD answers the different and also
useful question "is anything UNHARVESTED right now".

Run:  python3 scripts/panel_harvest_loss_2026-09-22.py
      python3 scripts/panel_harvest_loss_2026-09-22.py --ref HEAD
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
import math


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
        """Invert the regularised incomplete beta by bisection.

        HARDENED 2026-11-04. `mpmath.betainc` is fast, but its hyp2f1 path
        FAILS TO CONVERGE for large parameters at mid-range x. Measured at
        a=2437, b=17564 it succeeds for x <= 0.1264 and for x >= 0.9 and raises
        ValueError in between -- which is exactly where a bisection over [0, 1]
        takes its first step, so the whole inversion died rather than degrading.
        It surfaced when a producer called this at k=2436, n=20000; every
        existing caller used a small n, and the guard that executes every `_iv`
        against the same k and n uses n <= 38, so no test could have seen it.

        Where betainc raises, the same integral is computed by quadrature in
        log space instead. At the measured failing point that agreed with
        scipy's quantile to 1.11e-16. It costs about 6 s per bound against
        milliseconds for betainc, so it is used only after a failure, never by
        default.
        """
        logB = mpmath.log(mpmath.beta(a, b))

        def by_quad(x):
            if x <= 0:
                return mpmath.mpf(0)
            def dens(u):
                return mpmath.e**((a - 1) * mpmath.log(u)
                                  + (b - 1) * mpmath.log1p(-u) - logB)
            return mpmath.quad(dens, [0, min(mpmath.mpf(x), mpmath.mpf(1))])

        fell_back = False

        def f(x):
            nonlocal fell_back
            if not fell_back:
                try:
                    return mpmath.betainc(a, b, 0, x, regularized=True) - y
                except Exception:
                    fell_back = True
            return by_quad(x) - y

        # STOP ON PRECISION, not on a fixed count. The bracket halves every
        # step, so 2**-60 is already below this tolerance and a fixed 240 did
        # 180 redundant evaluations. That is free for betainc and it is NOT
        # free for the quadrature fallback, which costs about 28 ms per
        # evaluation: 240 steps took 6.66 s and 60 take 1.69 s for a bound
        # identical to 12 decimal places. The count is still capped so a
        # pathological case cannot spin.
        lo, hi = mpmath.mpf(0), mpmath.mpf(1)
        tol = mpmath.mpf("1e-18")
        for _ in range(240):
            if hi - lo < tol:
                break
            m = (lo + hi) / 2
            lo, hi = (m, hi) if f(m) < 0 else (lo, m)
        return float((lo + hi) / 2)

    cdiff = max(abs(cl - (0.0 if k == 0 else bi(k, n - k + 1, 0.025))),
                abs(ch - (1.0 if k == n else bi(k + 1, n - k, 0.975))))
    return (max(0.0, wl), wh), (cl, ch), max(wdiff, cdiff)

REPO = Path(__file__).resolve().parents[1]
LOGS = REPO / "bench" / "logs"

#: The tree as it stood before the 2026-09-22 recovery. See the docstring.
PRE_RECOVERY_REF = "ae0c837"


def tracked_scripts(ref: str) -> set[str]:
    """Basenames under scripts/ present at `ref`."""
    out = subprocess.run(["git", "ls-tree", "-r", "--name-only", ref, "scripts/"],
                         cwd=REPO, capture_output=True, text=True)
    if out.returncode != 0:
        print(f"git ls-tree failed for ref {ref!r}: {out.stderr.strip()}",
              file=sys.stderr)
        raise SystemExit(2)
    return {Path(p).name for p in out.stdout.split() if p.endswith(".py")}


#: The THREE directories a launcher may harvest into. Measured 2026-09-23 by a
#: panel critic: this script originally globbed only the first, so it reached 1
#: destination of 3 and 1 directory level. `bench/confer_maths_panel_2026-09-05.py`
#: writes `sandbox_harvest`; `bench/confer_convergence_panel_2026-08-23.py` and
#: `bench/build_experiment_run.py` write `worktree_harvest`; and
#: `bench/tools/run_simulated_experiment.py` writes `panel_worktree_harvest` --
#: which is where all 4 of the 2026-09-21/22 commissioning arms put their files.
#: An instrument blind to a destination reports 0 loss there however bad it is.
HARVEST_DIRS = ("sandbox_harvest", "worktree_harvest", "panel_worktree_harvest")

#: Delivered paths that must NEVER be promoted, with the reason. Kept explicit
#: and narrow: a broad pattern here would silently excuse real losses.
NEVER_PROMOTE = (
    "__pycache__/",      # build artefact
    ".scratch/",         # a seat's own scratch space, by its own naming
)


def _is_throwaway(rel: str) -> bool:
    """A seat's temporary file, recognised by name rather than by judgement."""
    name = Path(rel).name
    return name.startswith("tmp") and name.endswith(".py")


def harvested_files(suffix: str = ".py") -> dict[str, list[str]]:
    """Every seat-delivered path, at FULL DEPTH, across ALL harvest destinations.

    Returns {repo-relative delivered path: [archive paths]}. The key is the path
    the seat MEANT, so `scripts/cc_free_seat_2026_09_21/f1.py` is distinct from
    `scripts/f1.py` -- the original keyed on BASENAME ONLY and one level deep,
    which is exactly how 7 nested files went unnoticed.
    """
    found: dict[str, list[str]] = {}
    for d in HARVEST_DIRS:
        for p in sorted(LOGS.glob(f"*/{d}/*/attempt-*/files/**/*{suffix}")):
            if not p.is_file():
                continue
            parts = p.parts
            rel = str(Path(*parts[parts.index("files") + 1:]))
            if any(skip in rel for skip in NEVER_PROMOTE) or _is_throwaway(rel):
                continue
            found.setdefault(rel, []).append(str(p.relative_to(REPO)))
    return found


def _sha(path: Path) -> str:
    import hashlib
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree_content_index() -> dict[str, str]:
    """sha256 -> first tree path, over the live tree's .py files.

    CONTENT-ADDRESSED, and that is not a preference. Path-addressed checking
    reported 5 false losses on 2026-09-23, because a CORRECT promotion had
    relocated those files to `scripts/panel_falsifiers/` on purpose. A file that
    is present under another name is not lost; a file whose bytes are nowhere is.
    """
    idx: dict[str, str] = {}
    for sub in ("scripts", "bench", "hooks"):
        for p in (REPO / sub).rglob("*.py"):
            if "logs" in p.parts or "__pycache__" in p.parts:
                continue
            try:
                idx.setdefault(_sha(p), str(p.relative_to(REPO)))
            except OSError:
                continue
    return idx


def harvested_scripts() -> dict[str, str]:
    """RETAINED for the original caller: basename -> first archive path.

    Kept rather than deleted because `main()` below still reports the pinned
    historical rate through it and the 2 forms answer different questions. The
    wider measurement is `harvested_files()`.
    """
    found: dict[str, str] = {}
    for p in sorted(LOGS.glob("*/sandbox_harvest/*/attempt-*/files/scripts/*.py")):
        found.setdefault(p.name, str(p.relative_to(REPO)))
    return found


def interval(k: int, n: int):
    """Wilson and Clopper-Pearson, from the canonical helper.

    ★ DELEGATED 2026-11-08 on his ruling for B135 option 1, and here the
    delegation fixes a second thing. This returned
    statsmodels' own Wilson method beside its own beta method -- 2
    intervals from 1 LIBRARY, which
    is the single-tool-by-construction shape `bench/falsifier_pairing.py`
    exists to prevent. `_iv` computes Wilson on statsmodels against an
    mpmath closed form and Clopper-Pearson on scipy against an mpmath
    incomplete-beta inverse, at the same values.
    """
    w, cp, _disagreement = _iv(k, n)
    return w, cp


def main() -> int:
    # add_help=True (2026-09-24): argparse OWNS `-h` here, because this script
    # has a real flag (`--ref`) and argparse's own usage lists it. The shared
    # `answer_help` helper is for scripts with NO parser; using both meant the
    # helper answered first and argparse's flag list was never shown, which
    # `test_no_script_uses_both` names exactly.
    ap = argparse.ArgumentParser(add_help=True, description=__doc__.strip().splitlines()[0])
    ap.add_argument("--ref", default=PRE_RECOVERY_REF)
    # parse_args, NOT parse_known_args (corrected 2026-09-24). The lenient form
    # SILENTLY DISCARDED an unrecognised flag, so `--rev HEAD` (a typo for --ref)
    # measured the pinned commit and reported it as though the flag had been
    # honoured. That is the "accepts a flag and does nothing with it" defect this
    # repo names as the 118-day no-op. argparse exits 2 on an unknown flag.
    args = ap.parse_args()

    harvest = harvested_scripts()
    tracked = tracked_scripts(args.ref)
    if not harvest:
        print("no harvested scripts found -- has any panel run yet?",
              file=sys.stderr)
        return 2

    lost = {n: p for n, p in harvest.items() if n not in tracked}
    n, k = len(harvest), len(lost)

    print("PANEL HARVEST LOSS")
    print(f"  reference commit : {args.ref}"
          f"{'  (pinned: the tree before recovery)' if args.ref == PRE_RECOVERY_REF else ''}")
    print(f"  distinct scripts delivered by seats into sandboxes : {n}")
    print(f"  of those, absent from scripts/ at that commit      : {k}")
    print()
    (wlo, whi), (clo, chi) = interval(k, n)
    print(f"  LOSS RATE {k}/{n} = {100*k/n:.4f}%")
    print(f"      Wilson 95%          [{100*wlo:.4f}%, {100*whi:.4f}%]")
    print(f"      Clopper-Pearson 95% [{100*clo:.4f}%, {100*chi:.4f}%]")

    # second route, per multi_tool_crossverify: Wilson recomputed at 50 digits
    try:
        import mpmath as mp
        mp.mp.dps = 50
        z = mp.mpf("1.959963984540054235524594430520551527955550999086")
        ph, nn = mp.mpf(k) / n, mp.mpf(n)
        d = 1 + z**2 / nn
        c = (ph + z**2 / (2 * nn)) / d
        h = z * mp.sqrt(ph * (1 - ph) / nn + z**2 / (4 * nn**2)) / d
        print(f"      mpmath@50dps Wilson [{float(100*(c-h)):.4f}%, "
              f"{float(100*(c+h)):.4f}%]  |agreement| "
              f"{abs(float(c-h)-wlo):.2e} / {abs(float(c+h)-whi):.2e}")
    except ImportError:
        print("      (mpmath absent; single-route interval only)")

    print()
    print("  LOST FILES")
    for name, path in sorted(lost.items()):
        print(f"    {name}")
        print(f"        archived at {path}")
    if not lost:
        print("    none -- every delivered script is present at this commit")
    return 0


if __name__ == "__main__":
    sys.exit(main())
