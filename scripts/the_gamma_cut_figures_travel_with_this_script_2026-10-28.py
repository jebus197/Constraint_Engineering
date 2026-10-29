# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'joint_the_nine_changes_2026-10-28', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 1ddbfcdf11c4463cdab99c3e0f4eb9de00b376a7da86e83d8fb09791bb40ed60
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""The 0.41 ruling's figures, emitted by a committed producer.

THE DEFECT THIS REPAIRS: the figures justifying gamma_alt_threshold = 0.41 --
minimum premature gamma 0.3173, premature blocked 0 of 8 at 0.30 rising to
4 of 8 at 0.41, sound blocked 2 of 22 at both, Fisher p = 0.029355, and the
leave-one-out fold optima 0.4140 / 0.4585 -- existed only as comments in
`bench/reference_runner_v3.py` and `bench/tests/test_gamma_does_not_cover_the_
quiet_arm_2026-10-08.py`. The nearest committed producer,
`claim_gamma_does_not_cut_the_joint_rate`, measures a DIFFERENT population
(23 premature windows, not the 8 once-per-run gate-fire points) and emits none
of them. Under `measured-rate-travels-with-its-script` that is the defect the
standard exists to catch. Found by the fix-review panel of 2026-10-28 (cc2's
blind condition 1; confirmed in the joint round).

WHAT IT ADDS BEYOND THE CITED FIGURES: a permutation null over the threshold
sweep. The cut was selected by searching a continuum against 8 positives, so
the Fisher p at the chosen cut is not selection-corrected. The statistic here
is the MINIMUM one-sided Fisher p over every achievable cut; its null
distribution comes from shuffling the premature labels. That number, not the
raw 0.029355, is the honest strength of the 0.41 evidence.

Fire-point extraction is IMPORTED from the committed signal producer rather
than re-implemented, so the two scripts cannot drift apart silently.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import pathlib
import sys

import numpy as np
from scipy.stats import fisher_exact

REPO = pathlib.Path(__file__).resolve().parents[1]
SEED = 20261028
N_PERM = 20000

_spec = importlib.util.spec_from_file_location(
    "can_any_signal", REPO / "bench" / "can_any_signal_see_a_premature_close_2026-10-27.py")
_sig = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_sig)


def blocked_counts(prem, sound, theta):
    """The arm blocks a close whose gamma sits BELOW the cut."""
    bp = sum(1 for g in prem if g < theta)
    bs = sum(1 for g in sound if g < theta)
    p = fisher_exact([[bp, len(prem) - bp], [bs, len(sound) - bs]],
                     alternative="greater")[1]
    return bp, bs, p


def sweep_best(prem, sound):
    """Minimum one-sided Fisher p over every achievable cut.

    Returns (best_p, lo, hi): every cut in (lo, hi] blocks the same two sets,
    so the "optimal threshold" is an INTERVAL, and any single number quoted
    from it (0.3927, 0.4140, 0.41) is a representative, not a finding.
    """
    vals = np.unique(np.concatenate([prem, sound]))
    best_p, best_i = float("inf"), None
    for i, c in enumerate(vals):
        t = float(np.nextafter(c, np.inf))      # cut just above an observed value
        _, _, p = blocked_counts(list(prem), list(sound), t)
        if p < best_p:
            best_p, best_i = p, i
    lo = float(vals[best_i])
    hi = float(vals[best_i + 1]) if best_i + 1 < len(vals) else float("inf")
    return best_p, lo, hi


def main() -> int:
    # ★ THE HAND-ROLLED HELP CHECK IS REPLACED BY A REAL PARSER, 2026-10-29.
    # It read `if "--help" in sys.argv or "-h" in sys.argv: print(__doc__)`,
    # which answered help and let EVERY OTHER argument through silently -- so a
    # mistyped flag ran the script's ordinary work, and this script WRITES a
    # file. Measured before the change: `--no-such-flag` exited 0 and did the
    # work. 2 guards caught it: `test_every_script_that_writes_answers_help`,
    # because a writer must not act on an unrecognised flag, and
    # `test_an_unknown_flag_is_rejected_loudly`, because a silently ignored flag
    # is how a retired option becomes a no-op nobody notices.
    #
    # A PARSER RATHER THAN THE `answer_help` HELPER, and that is deliberate:
    # this file has no `sys.path` bootstrap, so the helper is not importable by
    # name without adding one, and `test_no_script_uses_both` forbids carrying
    # both mechanisms anyway. argparse answers help, prints the usage text and
    # exits 2 on anything it does not recognise, which is the whole requirement.
    # The parser takes no arguments because the script takes none.
    argparse.ArgumentParser(
        description="The gamma-cut figures, re-derived so they travel with "
                    "this script rather than as prose.").parse_args()
    reps = _sig.collect()
    rows = _sig.fire_points(reps, 3)
    out = {"fire_points": len(rows)}
    for series in ("gamma", "gamma_critical"):
        prem = [r["signals"][series] for r in rows
                if r["premature"] and r["signals"].get(series) is not None]
        sound = [r["signals"][series] for r in rows
                 if not r["premature"] and r["signals"].get(series) is not None]
        print(f"\n== series `{series}`  (premature n={len(prem)}, sound n={len(sound)}) ==")
        if not prem or not sound:
            print("   not recorded at enough fire points; no figure is derivable")
            out[series] = {"n_premature": len(prem), "n_sound": len(sound)}
            continue
        mn = min(prem)
        print(f"   minimum premature {series} at fire = {mn:.4f}")
        row = {"n_premature": len(prem), "n_sound": len(sound),
               "min_premature": mn, "thresholds": {}}
        for theta in (0.30, 0.41):
            bp, bs, p = blocked_counts(prem, sound, theta)
            print(f"   theta={theta:.2f}: premature blocked {bp} of {len(prem)}, "
                  f"sound blocked {bs} of {len(sound)}, Fisher one-sided p = {p:.6f}")
            row["thresholds"][str(theta)] = {"premature_blocked": bp,
                                             "sound_blocked": bs, "fisher_p": p}
        ap, sp = np.array(prem), np.array(sound)
        best_p, blo, bhi = sweep_best(ap, sp)
        print(f"   sweep: every cut in ({blo:.4f}, {bhi:.4f}] gives the minimum "
              f"Fisher p = {best_p:.6f}; 0.41 is inside = {blo < 0.41 <= bhi}")
        rng = np.random.default_rng(SEED)
        pooled = np.concatenate([ap, sp])
        k = len(ap)
        hits = 0
        for _ in range(N_PERM):
            idx = rng.permutation(len(pooled))
            pb, _, _ = sweep_best(pooled[idx[:k]], pooled[idx[k:]])
            hits += pb <= best_p
        perm_p = (hits + 1) / (N_PERM + 1)
        print(f"   permutation null over the sweep ({N_PERM} shuffles, seed {SEED}): "
              f"selection-corrected p = {perm_p:.6f}")
        row["sweep"] = {"best_p": best_p, "best_cut_interval": [blo, bhi],
                        "permutation_corrected_p": perm_p, "n_perm": N_PERM}
        folds = []
        for i in range(len(ap)):
            fp, flo, fhi = sweep_best(np.delete(ap, i), sp)
            folds.append((round(flo, 4), round(fhi, 4)))
        print(f"   leave-one-out fold optimal-cut intervals: {sorted(set(folds))}"
              f"  over {len(folds)} folds; 0.41 inside all = "
              f"{all(lo < 0.41 <= hi for lo, hi in folds)}")
        row["loo_fold_optima"] = folds
        out[series] = row
    dst = REPO / "experimental_notes" / "data" / "gamma_cut_figures_2026-10-28.json"
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(json.dumps(out, indent=1))
    print(f"\nwrote {dst}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
