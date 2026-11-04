# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'joint_severity_spec_is_uncomputable_2026-11-04', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: c0d80ae74075023b81d83a4a2ac4a7d6526ee909914b868e3106e18063f5348e
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""PRODUCER: the two seats' opposite flip directions, on ONE archive and ONE gate.

Round 1 of `severity_spec_is_uncomputable_2026-11-04` was blind, and the two
seats returned flip results of OPPOSITE SIGN for "drop `confidence`":

  * `cc2`  substituted `asserted * V`                          -> 11 flips, all False -> True
  * `fable` substituted `compute_sev_f(class, confidence, V)`  -> 12 flips, all True  -> False

The joint brief asks whether those are a contradiction or two compatible
results about two different substitutions. They are two different functions,
so the question is answerable only by running BOTH on the SAME archive through
the SAME gate, which is what this does.

WHAT IS HELD FIXED, so that the substitution is the only moving part:
  * one archive -- every `bench/logs/**/runner_state.json`, content-hash
    deduplicated (the `fable` correction adopted in the appendix 2026-11-04:
    77 files, 10 under `sandbox_harvest/`, 67 distinct);
  * one gate -- the REAL `_check_gamma_alt_convergence`, imported, never
    re-typed;
  * one series reader -- the REAL `_settled_novelty_series`, which is the
    reader the live round loop feeds to that gate (reference_runner_v3.py
    line 20552 assigns `_settled_all, _settled_crit` from it, 20567 writes
    `novel_critical_history[-1] = _settled_crit[round_idx]`, and 20788
    computes `gamma_critical` from `_settled_crit`);
  * one config -- `RunnerConfig()` defaults.

HOW A SEVERITY DEFINITION IS SUBSTITUTED. Both readers test
`(e.get("severity") or 0.0) >= _thr`, so substituting the definition means
replacing the number the reader reads. This script deep-copies the archived
entries, writes the substituted value onto `severity` IN MEMORY, and calls the
real functions. Nothing is written back: the archive is read-only here, per the
founder's 2026-11-01 ruling that no revision be applied to the historical
record.

TWO A4 VARIANTS, because the round-1 replays differed there too and it is not
a detail. `unresolved_critical` is the A4 fail-safe input, and the live run
takes it from `registry.unverified_critical_count(round_idx)`, which ITSELF
reads severity. Variant FORCED pins it to 0 (severity is then the only varying
input -- the `cc2` round-1 setup); variant LIVE recomputes it, and both
`contested` and the irreducible queue, under the substituted severity from the
same registry object, which is what a live run would actually do.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from statsmodels.stats.proportion import proportion_confint  # noqa: E402

from bench.reference_runner_v3 import (  # noqa: E402
    CRITICAL_SEVERITY_THRESHOLD, FindingRegistry, RunnerConfig,
    _check_gamma_alt_convergence, _corroborated_novelty_series,
    _estimate_gamma, _settled_novelty_series, compute_sev_f,
    spec_critical_severity, spec_verification_factor,
)
import bench.reference_runner_v3 as _rr  # noqa: E402

# THE READERS' OWN SEVERITY HOOK IS NEUTRALISED FOR THE DURATION OF THIS
# MEASUREMENT, DELIBERATELY AND IN ONE PLACE. `_settled_novelty_series` and
# `_corroborated_novelty_series` now call `spec_critical_severity(e)` rather
# than reading `e["severity"]` raw. This producer's whole method is to put the
# substituted value ON `severity` and let the real reader read it, so leaving
# the hook in place would apply the shipped fix on top of every substitution
# and the baseline would no longer be the pre-fix gate. The hook is replaced
# with the raw read the readers performed before 2026-11-04, so "baseline"
# means what the gate actually did, and the shipped fix is measured as one of
# the severity maps below -- through the REAL imported `spec_critical_severity`,
# never a copy of it.
_rr.spec_critical_severity = lambda e: float(e.get("severity") or 0.0)

TERMINAL_STATUS = {"MERGED", "CLOSED", "REFUTED", "DUPLICATE"}


# ---------------------------------------------------------------- substitutions
def sev_asserted(e: dict) -> float:
    """BASELINE: what the gate reads today -- the model-asserted float."""
    return float(e.get("severity") or 0.0)


def sev_cc2_asserted_times_v(e: dict) -> float:
    """`cc2` round 1, and `effective_severity` with `_SEVERITY_SPEC['on']`.

    `asserted * V`: monotone non-increasing in the asserted number.
    """
    return sev_asserted(e) * spec_verification_factor(e)


def sev_fable_sev_f(e: dict) -> float:
    """`fable` round 1: the REAL `compute_sev_f`, appendix section 7.7 as written."""
    return compute_sev_f(e.get("constraint_class"), e.get("confidence"),
                         e.get("falsifier_verdict"))


def sev_fable_w_times_v(e: dict) -> float:
    """`fable`'s PROPOSED form, `W(class) * V(verification)` -- confidence dropped.

    Expressed through the real `compute_sev_f` with confidence pinned to 1, so
    the W and V tables are the harness's, not a copy.
    """
    return compute_sev_f(e.get("constraint_class"), 1.0,
                         e.get("falsifier_verdict"))


def sev_annihilator_plain(e: dict) -> float:
    """`cc2`'s round-1 PROPOSED form: the KEY PROPERTY and nothing else.

    V == 0 annihilates; every other value passes the asserted number through
    untouched. This is the appendix section 7.7 key property ("disproved
    findings always receive zero severity") without the V(None) halving and
    without the status carve-out the shipped form below carries.
    """
    asserted = sev_asserted(e)
    return 0.0 if spec_verification_factor(e) == 0.0 else asserted


def sev_shipped(e: dict) -> float:
    """THE SHIPPED FIX: the REAL `spec_critical_severity`, imported.

    Annihilator only, plus the measured carve-out for an entry whose
    tool-owned status is CONFIRMED while a stale `falsifier_verdict` still
    reads REFUTED.
    """
    return spec_critical_severity(e)


SUBSTITUTIONS = [
    ("asserted (baseline)", sev_asserted),
    ("cc2: asserted * V", sev_cc2_asserted_times_v),
    ("fable: compute_sev_f(class, confidence, V)", sev_fable_sev_f),
    ("fable fix: W(class) * V", sev_fable_w_times_v),
    ("cc2 round-1 fix: annihilator only (no status carve-out)",
     sev_annihilator_plain),
    ("SHIPPED fix: spec_critical_severity (annihilator + status carve-out)",
     sev_shipped),
]


# ---------------------------------------------------------------------- helpers
def wilson(k: int, n: int) -> str:
    if n == 0:
        return "n=0"
    lo, hi = proportion_confint(k, n, alpha=0.05, method="wilson")
    return f"{100.0 * k / n:.4f}% Wilson [{100 * lo:.4f}%, {100 * hi:.4f}%]"


def distinct_registries(root: pathlib.Path):
    """Every archived runner_state.json, deduplicated by content hash."""
    seen, out, skipped = set(), [], 0
    for p in sorted(root.rglob("runner_state.json")):
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        if h in seen:
            skipped += 1
            continue
        seen.add(h)
        try:
            d = json.loads(p.read_text())
        except Exception:                        # noqa: BLE001
            skipped += 1
            continue
        entries = (d.get("registry") or {}).get("entries") or {}
        if isinstance(entries, dict) and entries:
            out.append((p, d))
    return out, skipped


def replay(entries: dict, alias_map: dict, severity_fn, cfg, live_a4: bool):
    """Call the REAL series reader and the REAL gate under one severity map."""
    ents = copy.deepcopy(entries)
    for e in ents.values():
        if isinstance(e, dict):
            e["severity"] = severity_fn(e)
    reg = FindingRegistry()
    reg.entries = ents
    try:
        reg.alias_map = dict(alias_map or {})
    except Exception:                            # noqa: BLE001
        pass
    rounds = [e.get("open_since_round") for e in ents.values()
              if isinstance(e, dict) and isinstance(e.get("open_since_round"), int)]
    max_round = max(rounds) if rounds else 0
    all_s, crit_s = _settled_novelty_series(reg, max_round)
    _, corr_crit = _corroborated_novelty_series(reg, max_round)
    gamma_all = _estimate_gamma(all_s, cfg.min_rounds_for_gamma)
    gamma_crit = _estimate_gamma(crit_s, cfg.min_rounds_for_gamma)
    if live_a4:
        unresolved = int(reg.unverified_critical_count(max_round))
        contested = int(reg.contested_count(max_round))
        irq = int(reg.irreducible_queue_count())
    else:
        unresolved = contested = irq = 0
    converged, reason = _check_gamma_alt_convergence(
        max_round, gamma_all, list(crit_s), cfg,
        unresolved_critical=unresolved, contested=contested, rho_churn=False,
        irreducible_queue=irq, gamma_critical=gamma_crit,
        total_findings=len(ents),
    )
    crit_ids = {cid for cid, e in ents.items()
                if isinstance(e, dict)
                and float(e.get("severity") or 0.0) >= CRITICAL_SEVERITY_THRESHOLD}
    return dict(max_round=max_round, all_s=all_s, crit_s=crit_s,
                corr_crit=corr_crit, gamma_all=gamma_all,
                gamma_crit=gamma_crit, converged=converged, reason=reason,
                crit_ids=crit_ids, unresolved=unresolved, contested=contested)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--logs", default=str(REPO / "bench" / "logs"))
    args = ap.parse_args(argv)

    cfg = RunnerConfig()
    regs, skipped = distinct_registries(pathlib.Path(args.logs))
    n_entries = sum(len((d.get("registry") or {}).get("entries") or {})
                    for _p, d in regs)
    print(f"[scope] distinct registries : {len(regs)} "
          f"(skipped {skipped} duplicate/unreadable)")
    print(f"[scope] archived entries    : {n_entries}")
    print(f"[scope] gate                : _check_gamma_alt_convergence "
          f"(theta={cfg.gamma_alt_threshold}, "
          f"window={cfg.gamma_alt_consecutive_zero_crit}, "
          f"earliest={cfg.gamma_alt_earliest_round})")

    # --- the two `fable` forms are the SAME function on this archive --------
    diff = both = 0
    conf_present = class_present = 0
    for _p, d in regs:
        for e in ((d.get("registry") or {}).get("entries") or {}).values():
            if not isinstance(e, dict):
                continue
            both += 1
            conf_present += int("confidence" in e)
            class_present += int("constraint_class" in e)
            if abs(sev_fable_sev_f(e) - sev_fable_w_times_v(e)) > 1e-12:
                diff += 1
    print(f"\n[identity] entries carrying `confidence`       : {conf_present} "
          f"of {both}")
    print(f"[identity] entries carrying `constraint_class` : {class_present} "
          f"of {both}")
    print(f"[identity] compute_sev_f(.,conf,.) != W*V on    : {diff} of {both} "
          "entries -- so on THIS archive the two `fable` forms are one function")
    ab = 0
    for _p, d in regs:
        for e in ((d.get("registry") or {}).get("entries") or {}).values():
            if isinstance(e, dict) and abs(
                    sev_annihilator_plain(e) - sev_shipped(e)) > 1e-12:
                ab += 1
    print(f"[A/B]      plain annihilator != shipped form on    : {ab} of {both} "
          "entries (the status==CONFIRMED carve-out's whole reach)")

    for live_a4 in (False, True):
        tag = "LIVE A4 (unresolved/contested/queue recomputed)" if live_a4 \
            else "FORCED A4 (unresolved=contested=queue=0)"
        print(f"\n================ {tag} ================")
        base = {}
        for p, d in regs:
            reg = d.get("registry") or {}
            base[p] = replay(reg.get("entries") or {}, reg.get("alias_map"),
                             sev_asserted, cfg, live_a4)
        n = len(regs)
        print(f"baseline converged: {sum(r['converged'] for r in base.values())} "
              f"of {n}")
        for label, fn in SUBSTITUTIONS[1:]:
            f2t, t2f, moved, gmoved, vac, corr_moved = [], [], 0, 0, 0, 0
            for p, d in regs:
                reg = d.get("registry") or {}
                r = replay(reg.get("entries") or {}, reg.get("alias_map"),
                           fn, cfg, live_a4)
                b = base[p]
                if r["crit_ids"] != b["crit_ids"]:
                    moved += 1
                if r["corr_crit"] != b["corr_crit"]:
                    corr_moved += 1
                if abs(r["gamma_crit"] - b["gamma_crit"]) > 1e-9:
                    gmoved += 1
                if r["converged"] != b["converged"]:
                    rec = (p.parent.name, b["gamma_crit"], r["gamma_crit"],
                           b["crit_s"], r["crit_s"],
                           "VACUOUS" if "VACUOUS" in r["reason"] else "two-sided")
                    if r["converged"]:
                        f2t.append(rec)
                        vac += int("VACUOUS" in r["reason"])
                    else:
                        t2f.append(rec)
            print(f"\n--- {label}")
            print(f"    critical partition moved (runs) : {moved} of {n}")
            print(f"    corroborated series moved (runs) : {corr_moved} of {n}")
            print(f"    gamma_critical moved (runs)     : {gmoved} of {n}")
            print(f"    GATE FLIPS                      : "
                  f"{len(f2t) + len(t2f)} of {n}  "
                  f"[{wilson(len(f2t) + len(t2f), n)}]")
            print(f"      False -> True (manufactured)  : {len(f2t)}  "
                  f"(of which via VACUOUS CURVE: {vac})")
            print(f"      True -> False (prevented)     : {len(t2f)}")
            for direction, recs in (("F->T", f2t), ("T->F", t2f)):
                for run, gb, gr, cb, cr, branch in recs:
                    print(f"      {direction} {run}: gamma_crit "
                          f"{gb:.3f}->{gr:.3f}  crit {cb}->{cr}  [{branch}]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
