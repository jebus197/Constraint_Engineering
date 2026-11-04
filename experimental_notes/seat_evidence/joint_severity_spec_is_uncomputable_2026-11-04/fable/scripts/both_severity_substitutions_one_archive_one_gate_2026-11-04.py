# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'joint_severity_spec_is_uncomputable_2026-11-04', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 8813c4678152e637ab08b6c049fd2a6f3c92f314e79751123d2d35206dcb60a4
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Item 1 of the 2026-11-04 joint round: are the two seats' flip results
compatible facts about two DIFFERENT substitutions, or does one refute the other?

Protocol: SAME archive (every bench/logs/**/runner_state.json, deduplicated by
file content hash), SAME gate (the REAL `_check_gamma_alt_convergence`), SAME
series reader (the REAL `_settled_novelty_series`), SAME estimator
(`_estimate_gamma`). Severity is varied ONLY by rewriting entry["severity"] on a
deep copy before the real readers run -- no reader is reimplemented.

Definitions measured, each against the raw-asserted baseline:
  cc2_full        asserted * V            (cc2's round-1 substitution; V(None)=0.5)
  fable_op        compute_sev_f(class, confidence, verdict)  (fable's round-1 substitution)
  fable_WV        W(class) * V            (fable's round-1 proposed fix, confidence dropped)
  cc2_restricted  0 if verdict REFUTED else asserted         (cc2's round-1 fix)

Two replay protocols per definition:
  A  unresolved_critical=0, contested=0 (both seats' round-1 protocol)
  B  faithful: unverified_critical_count()/contested_count() recomputed from the
     REAL FindingRegistry on the archived entries. Both counters are
     severity-independent (status-only; the contested severity branch is opt-in
     and off here), so they are computed ONCE per run and apply to every
     definition identically.

Also measured, because the fix decision depends on them:
  * entries where fable_WV != fable_op (non-defaulted confidence in the archive)
  * the population any annihilator touches: falsifier_verdict REFUTED with a
    status NOT in _NON_NOVEL_TERMINAL_STATUSES, at raw severity >= 0.7
  * status_log transitions OUT of REFUTED (is REFUTED terminal in practice?)
"""
from __future__ import annotations

import copy
import hashlib
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "bench"))
import reference_runner_v3 as R  # noqa: E402


def sev_base(e):
    return float(e.get("severity") or 0.0)


def sev_cc2_full(e):
    return sev_base(e) * R.spec_verification_factor(e)


def sev_fable_op(e):
    return R.compute_sev_f(e.get("constraint_class"), e.get("confidence"),
                           e.get("falsifier_verdict"))


def sev_fable_WV(e):
    w = R.SEV_F_W.get(str(e.get("constraint_class") or "").strip().upper(),
                      R.SEV_F_W["HARD"])
    return w * R.spec_verification_factor(e)


def sev_cc2_restricted(e):
    v = str(e.get("falsifier_verdict") or "").strip().upper()
    return 0.0 if v == "REFUTED" else sev_base(e)


DEFS = [("cc2_full", sev_cc2_full), ("fable_op", sev_fable_op),
        ("fable_WV", sev_fable_WV), ("cc2_restricted", sev_cc2_restricted)]


def gate(reg, max_round, cfg, unresolved, contested):
    all_s, crit_s = R._settled_novelty_series(reg, max_round)
    g_all = R._estimate_gamma(all_s)
    g_crit = R._estimate_gamma(crit_s)
    ok, reason = R._check_gamma_alt_convergence(
        round_idx=max_round, gamma=g_all, novel_critical_history=crit_s,
        cfg=cfg, unresolved_critical=unresolved, contested=contested,
        gamma_critical=g_crit, total_findings=sum(all_s))
    return ok, reason, crit_s, g_crit


def reg_with(entries, sev_fn):
    ents = copy.deepcopy(entries)
    for e in ents.values():
        if isinstance(e, dict):
            e["severity"] = sev_fn(e)
    return R.FindingRegistry.from_dict({"entries": ents})


def main():
    files = sorted(REPO.glob("bench/logs/**/runner_state.json"))
    seen, runs = set(), []
    for f in files:
        h = hashlib.sha256(f.read_bytes()).hexdigest()
        if h in seen:
            continue
        seen.add(h)
        runs.append(f)
    print(f"[scope] {len(files)} runner_state.json files, "
          f"{len(runs)} distinct by content hash, "
          f"{len(files) - len(runs)} duplicate copies skipped")

    cfg = R.RunnerConfig()
    tot_entries = 0
    conf_divergence = 0
    refuted_nonterminal_crit = 0
    refuted_status_exits = []
    flips = {name: {"A": [], "B": []} for name, _ in DEFS}
    part_moves = {name: 0 for name, _ in DEFS}

    for f in runs:
        state = json.loads(f.read_text())
        regd = state.get("registry") or {}
        entries = regd.get("entries") or {}
        if not entries:
            continue
        tot_entries += len(entries)
        nch = state.get("novel_critical_history") or []
        max_round = (len(nch) - 1 if nch else
                     max((e.get("open_since_round") or 0)
                         for e in entries.values()))
        base_reg = R.FindingRegistry.from_dict(
            {"entries": copy.deepcopy(entries)})
        unresolved = base_reg.unverified_critical_count(max_round)
        contested = base_reg.contested_count(max_round)

        for e in entries.values():
            if not isinstance(e, dict):
                continue
            if abs(sev_fable_WV(e) - sev_fable_op(e)) > 1e-12:
                conf_divergence += 1
            v = str(e.get("falsifier_verdict") or "").strip().upper()
            if (v == "REFUTED"
                    and e.get("status") not in R._NON_NOVEL_TERMINAL_STATUSES
                    and sev_base(e) >= R.CRITICAL_SEVERITY_THRESHOLD):
                refuted_nonterminal_crit += 1
            for t in e.get("status_log") or []:
                if isinstance(t, dict) and t.get("from") == "REFUTED":
                    refuted_status_exits.append(
                        (f.parent.name, e.get("canonical_id"),
                         t.get("to"), t.get("round")))

        baseA = gate(base_reg, max_round, cfg, 0, 0)
        baseB = gate(base_reg, max_round, cfg, unresolved, contested)
        for name, fn in DEFS:
            sub = reg_with(entries, fn)
            for proto, base, (u, c) in (("A", baseA, (0, 0)),
                                        ("B", baseB, (unresolved, contested))):
                got = gate(sub, max_round, cfg, u, c)
                if got[0] != base[0]:
                    flips[name][proto].append(
                        (f.parent.name, base[0], got[0],
                         "VACUOUS" in got[1] or "VACUOUS" in base[1]))
            moved = sum(
                1 for e in entries.values() if isinstance(e, dict)
                and ((sev_base(e) >= R.CRITICAL_SEVERITY_THRESHOLD)
                     != (fn(e) >= R.CRITICAL_SEVERITY_THRESHOLD)))
            part_moves[name] += moved

    print(f"[scope] {tot_entries} entries across distinct runs")
    print(f"[conf]  entries where W*V != compute_sev_f (live confidence): "
          f"{conf_divergence}")
    print(f"[pop]   verdict-REFUTED, status non-terminal, raw sev>=0.7 "
          f"(the population any annihilator can move): "
          f"{refuted_nonterminal_crit}")
    print(f"[refuted-exits] status_log transitions OUT of REFUTED: "
          f"{len(refuted_status_exits)}")
    for row in refuted_status_exits:
        print("   ", row)
    for name, _ in DEFS:
        print(f"\n== {name} ==  critical-partition entry moves: "
              f"{part_moves[name]}")
        for proto in ("A", "B"):
            fl = flips[name][proto]
            f2t = sum(1 for _, b, g, _ in fl if not b and g)
            t2f = sum(1 for _, b, g, _ in fl if b and not g)
            vac = sum(1 for *_x, v in fl if v)
            print(f"  protocol {proto}: {len(fl)} gate flips "
                  f"(False->True {f2t}, True->False {t2f}, "
                  f"via vacuous branch {vac})")
            for run, b, g, v in fl:
                print(f"    {run}: {b} -> {g}{'  [vacuous]' if v else ''}")


if __name__ == "__main__":
    main()
