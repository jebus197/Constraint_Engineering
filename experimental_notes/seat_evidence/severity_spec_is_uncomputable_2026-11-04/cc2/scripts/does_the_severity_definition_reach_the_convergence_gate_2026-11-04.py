# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'severity_spec_is_uncomputable_2026-11-04', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 3892b9601c4d04945c32d71529d83f23e117c9551c35ce5602d361683f6d5080
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Does a change to the section 7.7 severity definition reach a convergence verdict?

PANEL BRIEF 2026-11-04 asked each seat to "establish by execution whether a
change to the severity definition changes a convergence verdict, or whether the
cut collapses the formula to a threshold test".

THIS SCRIPT ANSWERS A SHARPER QUESTION THAN THE BRIEF ASKED, because the brief's
own dependency chain does not hold in the code. The brief states:

    "_check_gamma_alt_convergence ... reads `gamma_critical`, which depends on
     which findings are CRITICAL, which depends on the severity cut."

Every link is true of the ASSERTED severity. What the brief omits is that
`RunnerConfig.severity_spec_enabled` -- the flag built 2026-10-15 to make
section 7.7 DECIDE -- cannot travel down that chain. `effective_severity` has
exactly 2 consumers in the whole runner, and `_settled_novelty_series` (which
produces the critical series `gamma_critical` is fitted to) is not one of them:
it reads `e.get("severity")` RAW at line 10794.

So there are TWO severity definitions live in the runner at once:

  * the A4 release door reads `effective_severity` (specification-aware);
  * the critical-novelty series, and therefore `gamma_critical` and the whole
    two-sided gate, reads the asserted float (specification-blind).

MEASUREMENTS (all over bench/logs/**/runner_state.json):

  1. `severity_spec_shadow` on real archived entries -- does it return, and does
     anything in the gating path consume it.
  2. crit_s and gamma_critical under asserted vs specification severity, per run.
  3. The REAL `_check_gamma_alt_convergence` called under both, per run, to count
     verdict flips. The gate is never reimplemented here -- the runner's own
     comment at line ~11020 records that a prior reimplementation of this gate
     produced answers about a gate that does not exist, so the real function is
     called or nothing is reported.
  4. Whether the promotion flag can reach the critical series at all.

Run:  python3 scripts/does_the_severity_definition_reach_the_convergence_gate_2026-11-04.py
"""
from __future__ import annotations

import glob
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "bench"))

import reference_runner_v3 as R  # noqa: E402

try:
    from statsmodels.stats.proportion import proportion_confint
except ImportError:  # pragma: no cover
    proportion_confint = None

THR = R.CRITICAL_SEVERITY_THRESHOLD


def ci(k, n):
    if not n or proportion_confint is None:
        return "n/a"
    w = proportion_confint(k, n, method="wilson")
    b = proportion_confint(k, n, method="beta")
    return ("%.4f%% Wilson [%.4f%%, %.4f%%] Clopper-Pearson [%.4f%%, %.4f%%]"
            % (100 * k / n, 100 * w[0], 100 * w[1], 100 * b[0], 100 * b[1]))


class Reg:
    """Minimal duck-typed stand-in exposing only `.entries`.

    `severity_spec_shadow` and `_settled_novelty_series` both reach the registry
    through `.entries` alone (both guard with hasattr), so this is sufficient to
    call the REAL implementations rather than copies of them.
    """

    def __init__(self, entries):
        self.entries = entries


def load_runs():
    out = []
    for f in sorted(glob.glob("bench/logs/**/runner_state.json", recursive=True)):
        try:
            d = json.load(open(f))
        except Exception:
            continue
        e = (d.get("registry") or {}).get("entries") or {}
        if isinstance(e, dict) and e:
            out.append((f, e))
    return out


def spec_entries(entries):
    """Copy with severity replaced by section 7.7's asserted x V."""
    out = {}
    for cid, e in entries.items():
        c = dict(e)
        sev = e.get("severity")
        if isinstance(sev, (int, float)):
            c["severity"] = float(sev) * R.spec_verification_factor(e)
        out[cid] = c
    return out


def main():
    runs = load_runs()
    n_entries = sum(len(e) for _, e in runs)
    print("=" * 78)
    print("ARCHIVE READ: %d runner_state.json files with entries, %d entries total"
          % (len(runs), n_entries))
    print("=" * 78)

    # ---------------- 1. severity_spec_shadow on real entries ----------------
    print("\n[1] severity_spec_shadow on real archived entries")
    tot = {"V_true": 0, "V_none": 0, "V_false": 0, "critical_asserted": 0,
           "critical_spec": 0, "crossed": 0, "keyviol": 0}
    ok = 0
    for f, e in runs:
        try:
            s = R.FindingRegistry.severity_spec_shadow(Reg(e))
        except Exception as ex:
            print("    ERROR on %s: %s" % (f, ex))
            continue
        ok += 1
        for k in ("V_true", "V_none", "V_false", "critical_asserted", "critical_spec"):
            tot[k] += s[k]
        tot["crossed"] += len(s["crossed_downward"])
        tot["keyviol"] += len(s["key_property_violations"])
    scored = tot["V_true"] + tot["V_none"] + tot["V_false"]
    print("    returned a value on %d of %d runs" % (ok, len(runs)))
    print("    V_true=%d  V_none=%d  V_false=%d  (scored=%d)"
          % (tot["V_true"], tot["V_none"], tot["V_false"], scored))
    print("    critical_asserted=%d  critical_spec=%d" % (tot["critical_asserted"], tot["critical_spec"]))
    print("    crossed downward: %s" % ci(tot["crossed"], scored))
    print("    KEY PROPERTY violations: %d of %d disproved -- %s"
          % (tot["keyviol"], tot["V_false"], ci(tot["keyviol"], tot["V_false"])))

    # ---------------- 2/3. gamma_critical and the real gate ----------------
    print("\n[2+3] crit_s / gamma_critical / REAL two-sided gate under both definitions")
    cfg = R.RunnerConfig()
    W = cfg.gamma_alt_consecutive_zero_crit
    theta = cfg.gamma_alt_threshold
    print("    cfg: window=%d theta=%.3f earliest_round=%d"
          % (W, theta, cfg.gamma_alt_earliest_round))

    g_moved = part_moved = verdict_flipped = 0
    comparable = 0
    flips = []
    moves = []
    for f, e in runs:
        rounds = [x.get("open_since_round") for x in e.values()
                  if isinstance(x.get("open_since_round"), int) and x.get("open_since_round") >= 0]
        if not rounds:
            continue
        mx = max(rounds)
        a_all, a_crit = R._settled_novelty_series(Reg(e), mx)
        s_all, s_crit = R._settled_novelty_series(Reg(spec_entries(e)), mx)
        comparable += 1
        ga = R._estimate_gamma(a_crit)
        gs = R._estimate_gamma(s_crit)
        if a_crit != s_crit:
            part_moved += 1
        if abs(ga - gs) > 1e-9:
            g_moved += 1
            moves.append((f, ga, gs))
        # The REAL gate, both definitions. A4 count held at 0 and contested at 0
        # so the ONLY thing varying between the two calls is the severity
        # definition feeding the critical series.
        va, ra = R._check_gamma_alt_convergence(
            round_idx=mx, gamma=ga, novel_critical_history=a_crit, cfg=cfg,
            unresolved_critical=0, contested=0, gamma_critical=ga,
            total_findings=sum(a_all))
        vs, rs = R._check_gamma_alt_convergence(
            round_idx=mx, gamma=gs, novel_critical_history=s_crit, cfg=cfg,
            unresolved_critical=0, contested=0, gamma_critical=gs,
            total_findings=sum(s_all))
        if va != vs:
            verdict_flipped += 1
            flips.append((f, va, vs, ra[:100], rs[:100]))

    print("    runs with a usable round series: %d" % comparable)
    print("    CRITICAL partition moved:  %d of %d -- %s" % (part_moved, comparable, ci(part_moved, comparable)))
    print("    gamma_critical moved:      %d of %d -- %s" % (g_moved, comparable, ci(g_moved, comparable)))
    print("    REAL gate verdict FLIPPED: %d of %d -- %s" % (verdict_flipped, comparable, ci(verdict_flipped, comparable)))
    for f, ga, gs in moves[:10]:
        print("      gamma %.4f -> %.4f  %s" % (ga, gs, os.path.basename(os.path.dirname(f))))
    for f, va, vs, ra, rs in flips[:10]:
        print("      FLIP %s -> %s  %s" % (va, vs, os.path.basename(os.path.dirname(f))))
        print("         asserted: %s" % ra)
        print("         spec    : %s" % rs)

    # ---------------- 4. Can the promotion flag reach any of this? ----------
    print("\n[4] Can RunnerConfig.severity_spec_enabled reach the critical series?")
    probe = {"x": {"severity": 0.9, "falsifier_verdict": "REFUTED",
                   "open_since_round": 0, "status": "OPEN"}}
    R._SEVERITY_SPEC["on"] = False
    off_all, off_crit = R._settled_novelty_series(Reg(probe), 0)
    off_eff = R.effective_severity(probe["x"])
    R._SEVERITY_SPEC["on"] = True
    on_all, on_crit = R._settled_novelty_series(Reg(probe), 0)
    on_eff = R.effective_severity(probe["x"])
    R._SEVERITY_SPEC["on"] = False
    print("    probe entry: severity=0.9, falsifier_verdict=REFUTED (V=0, so Sev=0)")
    print("    flag OFF: effective_severity=%.3f  critical series=%s" % (off_eff, off_crit))
    print("    flag ON : effective_severity=%.3f  critical series=%s" % (on_eff, on_crit))
    reached = (off_crit != on_crit)
    print("    the flag reaches the critical series: %s" % reached)
    if not reached:
        print("    => CONFIRMED: the specification can annihilate this finding at the A4")
        print("       door while the SAME finding still counts as CRITICAL in the series")
        print("       gamma_critical is fitted to. The promotion flag is wired to 1 of the")
        print("       2 severity consumers that decide convergence.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
