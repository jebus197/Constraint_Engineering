# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'severity_spec_is_uncomputable_2026-11-04', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: d63f19fdf9476bbf1cf22638d9c960df66830e5a1b65be3f86d009f720087731
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Does recomputing severity as Sev_op(f) = W(class) . V(verification) move
the two-sided convergence gate on the archive?

Panel 2026-11-04 (severity_spec_is_uncomputable). docs/MATHEMATICAL_APPENDIX.md
section 7.7 specifies Sev(f) = W(class) . confidence . V(verification);
`confidence` is inadmissible under cdsfl_operational.md section 15 (d_tool)
and the HARD/SOFT class is uncollected (0 of 3,170 distinct archived entries
carry either), so the operational form is the two harness-ownable factors,
exactly what `compute_sev_f` returns on every archived entry (its confidence
input is identically absent and defaults to 1).

THE MEASUREMENT. Over every DISTINCT archived registry (content-hash
deduplicated -- sandbox_harvest copies and *_latest mirrors counted once),
rebuild the settled critical-novelty series twice: once with the
model-asserted severity float at the 0.7 cut (production), once with
Sev_op >= 0.7 (which, by the z3-checked collapse in section 7.7 caution 1,
is `falsifier_verdict == CONFIRMED` while class defaults HARD). Then call
`_check_gamma_alt_convergence` with each series and its own gamma_critical.
The all-severity series and gamma_all are UNCHANGED BY CONSTRUCTION -- the
severity cut does not enter them -- which is the novelty-separability half
of the answer.

Measured 2026-11-04: 67 distinct registries, 3,170 entries; 46 runs carry
falsifier verdicts; the critical partition moves on 588 entries and the
convergence verdict flips True -> False in 12 runs. GATES NOTHING -- this is
the non-distortion evidence the founder's promotion decision needs.

Usage: python3 scripts/the_severity_definition_moves_the_convergence_verdict_2026-11-04.py
"""
import glob
import hashlib
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from bench import reference_runner_v3 as rr  # noqa: E402


def main() -> int:
    files = sorted(glob.glob(str(REPO / "bench/logs/**/runner_state.json"),
                             recursive=True))
    seen, regs = set(), []
    for fp in files:
        try:
            d = json.loads(pathlib.Path(fp).read_text(errors="ignore"))
        except Exception:                                 # noqa: BLE001
            continue
        ents = ((d or {}).get("registry") or {}).get("entries") or {}
        if not ents:
            continue
        h = hashlib.sha256(json.dumps(ents, sort_keys=True,
                                      default=str).encode()).hexdigest()
        if h in seen:
            continue
        seen.add(h)
        regs.append((fp, ents))
    cfg = rr.RunnerConfig()
    thr = rr.CRITICAL_SEVERITY_THRESHOLD
    runs_verdict = flips_total = 0
    conv_flips = []
    for fp, ents in regs:
        if not any(isinstance(e, dict) and e.get("falsifier_verdict")
                   for e in ents.values()):
            continue
        runs_verdict += 1
        reg = rr.FindingRegistry()
        reg.entries = ents
        rounds = [e.get("open_since_round") for e in ents.values()
                  if isinstance(e, dict)
                  and e.get("open_since_round") is not None]
        if not rounds:
            continue
        mx = max(rounds)
        all_s, crit_base = rr._settled_novelty_series(reg, mx)
        crit_op = [0] * (mx + 1)
        flips = 0
        for e in ents.values():
            if not isinstance(e, dict):
                continue
            r = e.get("open_since_round")
            if r is None or r < 0 or r > mx:
                continue
            if e.get("status") in rr._NON_NOVEL_TERMINAL_STATUSES:
                continue
            sev_op = rr.compute_sev_f(e.get("constraint_class"),
                                      e.get("confidence"),
                                      e.get("falsifier_verdict"))
            if sev_op >= thr:
                crit_op[r] += 1
            if ((e.get("severity") or 0.0) >= thr) != (sev_op >= thr):
                flips += 1
        flips_total += flips
        g_all = rr._estimate_gamma(all_s)
        conv_base, _ = rr._check_gamma_alt_convergence(
            mx, g_all, crit_base, cfg, unresolved_critical=0, contested=0,
            gamma_critical=rr._estimate_gamma(crit_base),
            total_findings=sum(all_s))
        conv_op, _ = rr._check_gamma_alt_convergence(
            mx, g_all, crit_op, cfg, unresolved_critical=0, contested=0,
            gamma_critical=rr._estimate_gamma(crit_op),
            total_findings=sum(all_s))
        if conv_base != conv_op:
            conv_flips.append((fp, conv_base, conv_op))
    print(f"distinct registries: {len(regs)}  "
          f"entries: {sum(len(e) for _, e in regs)}")
    print(f"runs with falsifier verdicts: {runs_verdict}")
    print(f"critical-partition flips (asserted float vs Sev_op): {flips_total}")
    print(f"convergence-verdict flips at _check_gamma_alt_convergence: "
          f"{len(conv_flips)}")
    for fp, a, b in conv_flips:
        print(f"  {pathlib.Path(fp).parent.name}: {a} -> {b}")
    print("\ngamma_all / all-severity novelty: unchanged by construction "
          "(the severity cut does not enter the all-severity series).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
