# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'joint_severity_gates_convergence_2026-10-31', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: b1c5498cc3cea743d11e3807d9f695ea6ce19950a27fd31117e5f162d1f28d79
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""JOINT ROUND, third seat. What an R_k convergence gate would actually measure
if it were wired TODAY, and what sets its boundaries.

Everything here is computed. No figure quoted from either prior seat's reply is
taken as given; each is re-executed and either reproduced or corrected.

SECTIONS
  A  AST census: writers and readers of ``entry["model_params"]`` in the LIVE
     production tree (bench/logs/** and seat_evidence/** excluded: those are
     harvested copies of the runner, not the runner).
  B  Fixed points of the real three-phase recursion, SymPy + z3 + mpmath +
     iteration of the SHIPPED ``compute_rk`` (not a retyped copy).
  C  The pi confinement: whether [0.4, 0.6] is arithmetic (first seat's claim)
     or a property of the DEFAULT ``immune_memory_rho`` only.
  D  Archive: R_old / R_new distributions and the Spearman/Kendall association
     between R_new and asserted ``severity``.
  E  THE DECISIVE ONE. With ``sk_carry_rk_across_rounds`` on (default True since
     2026-10-31) R_k now accumulates across rounds. So a bound on R_k is
     reachable today -- and that is the problem, not the solution: with q pinned
     the trajectory is a function of ROUND COUNT and fix quality alone, so the
     founder's easy question and his hard question produce the IDENTICAL curve.
     A gate on it would read as a confidence gate and behave as a round counter.
  F  Gate-reader census: does any convergence predicate read R_new today.
"""
from __future__ import annotations

import ast
import collections
import json
import pathlib
import sys

import mpmath
import numpy as np
import sympy as sp
import z3
from scipy import stats

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from bench import reference_runner_v3 as rr  # noqa: E402

LOGS = REPO / "bench" / "logs"
FAILURES: list[str] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}" + (f" -- {detail}" if detail else ""))
    if not ok:
        FAILURES.append(label)


# --------------------------- A. model_params census ---------------------------
def _is_live(p: pathlib.Path) -> bool:
    parts = set(p.parts)
    return not ({"logs", ".git", "seat_evidence", "sandbox_harvest"} & parts)


def section_a() -> dict:
    print("\nA. AST census of entry['model_params'] in the LIVE tree")
    writers, readers = [], []
    for p in sorted(REPO.rglob("*.py")):
        if not _is_live(p):
            continue
        try:
            tree = ast.parse(p.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:
            continue
        rel = p.relative_to(REPO)
        for node in ast.walk(tree):
            if isinstance(node, (ast.Assign, ast.AugAssign, ast.AnnAssign)):
                tgts = node.targets if isinstance(node, ast.Assign) else [node.target]
                for t in tgts:
                    for sub in ast.walk(t):
                        if (isinstance(sub, ast.Subscript)
                                and isinstance(sub.slice, ast.Constant)
                                and sub.slice.value == "model_params"):
                            writers.append((str(rel), node.lineno, "subscript-store"))
            if isinstance(node, ast.Dict):
                for k in node.keys:
                    if isinstance(k, ast.Constant) and k.value == "model_params":
                        writers.append((str(rel), node.lineno, "dict-literal"))
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                for a in node.args:
                    if isinstance(a, ast.Constant) and a.value == "model_params":
                        slot = (writers if node.func.attr in ("setdefault", "update")
                                else readers if node.func.attr in ("get", "pop")
                                else None)
                        if slot is not None:
                            slot.append((str(rel), node.lineno, node.func.attr))
            if (isinstance(node, ast.Subscript)
                    and isinstance(node.slice, ast.Constant)
                    and node.slice.value == "model_params"
                    and isinstance(node.ctx, ast.Load)):
                readers.append((str(rel), node.lineno, "subscript-load"))

    for w in writers:
        print(f"      WRITE {w}")
    for r in readers:
        print(f"      READ  {r}")
    check("model_params has 0 writers in the live tree", not writers,
          f"{len(writers)} found")
    check("model_params has at least 1 reader", bool(readers),
          f"{len(readers)} found: {readers}")
    return {"writers": writers, "readers": readers}


# ----------------------- B. fixed points of the recursion ---------------------
def section_b() -> dict:
    print("\nB. Fixed points of the shipped three-phase recursion")
    R, q, s, nb, nf = sp.symbols("R q s nu_b nu_f", positive=True)

    R_det = R * (1 - q) / (1 - q * R)
    R_base = s * R_det + (1 - s) * R
    nu_eff = 1 - (1 - nb) * (1 - (1 - s) * nf)
    R_next = sp.simplify(R_base * (1 - nu_eff) + nu_eff)

    roots_general = sp.solve(sp.Eq(R_next, R), R)
    print(f"      general fixed points: {len(roots_general)}")
    for r in roots_general:
        print(f"        {sp.simplify(r)}")

    perfect = sp.simplify(R_next.subs(s, 1))
    roots_perf = sorted(sp.solve(sp.Eq(perfect, R), R), key=str)
    roots_perf_s = [sp.simplify(r) for r in roots_perf]
    print(f"      at s=1 (perfect fix): {roots_perf_s}")
    has_one = any(sp.simplify(r - 1) == 0 for r in roots_perf_s)
    has_nbq = any(sp.simplify(r - nb / q) == 0 for r in roots_perf_s)
    check("s=1 fixed points are exactly {1, nu_b/q}  (SymPy)",
          len(roots_perf_s) == 2 and has_one and has_nbq, str(roots_perf_s))

    zr, zq, znb = z3.Reals("zr zq znb")
    sol = z3.Solver()
    sol.add(zq == 0.5, znb == 0.05, zr > 0, zr < 1)
    sol.add(zq * zr * zr - (zq + znb) * zr + znb == 0)
    z3_ok = sol.check() == z3.sat
    z3_val = float(sol.model()[zr].as_fraction()) if z3_ok else None
    check("z3 finds the interior root at q=0.5, nu_b=0.05",
          bool(z3_ok) and abs((z3_val or 9) - 0.1) < 1e-12, f"z3 root = {z3_val}")

    print("      iterating the SHIPPED compute_rk (s=1, nu_b=0.05, 4000 steps):")
    table = {}
    for qv in (0.95, 0.50, 0.30, 0.05):
        x = 0.5
        for _ in range(4000):
            x = rr.compute_rk(x, qv, 1.0, nu_b=0.05, nu_f=0.20)
        predicted = min(1.0, 0.05 / qv)
        table[qv] = (x, predicted)
        print(f"        q={qv:<5} iterated R*={x:.10f}   nu_b/q={predicted:.10f}")
        check(f"iteration of shipped compute_rk matches nu_b/q at q={qv}",
              abs(x - predicted) < 1e-9, f"{x} vs {predicted}")

    mpmath.mp.dps = 40
    x = mpmath.mpf("0.5")
    half = mpmath.mpf("0.5")
    for _ in range(2000):
        x = x * (1 - half) / (1 - half * x) * mpmath.mpf("0.95") + mpmath.mpf("0.05")
    check("mpmath (40 dps) agrees with nu_b/q at q=0.5", abs(float(x) - 0.1) < 1e-12,
          f"{x}")

    absorbing = all(rr.compute_rk(1.0, qv, sv) == 1.0
                    for qv in np.linspace(0.0, 1.0, 21)
                    for sv in np.linspace(0.0, 1.0, 21))
    check("R=1 is absorbing for every (q,s) on a 21x21 grid", absorbing)
    return table


# ------------------------------ C. pi confinement -----------------------------
def section_c() -> dict:
    print("\nC. Is pi confined to [0.4, 0.6], or is that the DEFAULT rho only?")
    base = rr.RK0_PI_BASE
    rows = {}
    for rho in (0.0, 0.2, 0.5, 0.6024, 1.0):
        lo = (1 - rho) * base + rho * 0.0
        hi = (1 - rho) * base + rho * 1.0
        rows[rho] = (lo, hi)
        print(f"      rho={rho:<7} reachable pi = [{lo:.4f}, {hi:.4f}]  width {hi-lo:.4f}")
    check("at the DEFAULT rho=0.2 the window is [0.4, 0.6]",
          abs(rows[0.2][0] - 0.4) < 1e-12 and abs(rows[0.2][1] - 0.6) < 1e-12)
    check("at rho=1.0 the window is the FULL unit interval -- the confinement "
          "is a DEFAULT, not arithmetic",
          abs(rows[1.0][0]) < 1e-12 and abs(rows[1.0][1] - 1.0) < 1e-12)
    src = (REPO / "bench" / "reference_runner_v3.py").read_text()
    check("immune_memory_rho is a plain config float with default 0.2",
          "immune_memory_rho: float = 0.2" in src)
    frac = (rows[0.2][1] - rows[0.2][0]) / (0.90 - 0.02)
    print(f"      default window covers {frac*100:.1f}% of his worked [0.02, 0.90]")
    return rows


# --------------------------------- D. archive ---------------------------------
def _walk(obj, key):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == key:
                yield v
            yield from _walk(v, key)
    elif isinstance(obj, list):
        for it in obj:
            yield from _walk(it, key)


def section_d() -> dict:
    print("\nD. Archive: R_old, R_new, and association with asserted severity")
    R_old, R_new, pairs = collections.Counter(), collections.Counter(), []
    n_files = 0
    for path in LOGS.rglob("*.json"):
        try:
            doc = json.loads(path.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            continue
        n_files += 1
        for sk in _walk(doc, "sk_result"):
            if not isinstance(sk, dict):
                continue
            if isinstance(sk.get("R_old"), (int, float)):
                R_old[round(float(sk["R_old"]), 9)] += 1
            if isinstance(sk.get("R_new"), (int, float)):
                R_new[round(float(sk["R_new"]), 9)] += 1
        for entries in _walk(doc, "entries"):
            if not isinstance(entries, dict):
                continue
            for _cid, e in entries.items():
                if not isinstance(e, dict):
                    continue
                sk = e.get("sk_result")
                sev = e.get("severity")
                if isinstance(sk, dict) and isinstance(sk.get("R_new"), (int, float)) \
                        and isinstance(sev, (int, float)):
                    pairs.append((float(sk["R_new"]), float(sev)))

    n_old, n_new = sum(R_old.values()), sum(R_new.values())
    print(f"      json files scanned: {n_files}")
    print(f"      R_old: n={n_old} distinct={len(R_old)} -> {dict(R_old.most_common(6))}")
    if R_new:
        print(f"      R_new: n={n_new} distinct={len(R_new)} "
              f"range=[{min(R_new):.6f}, {max(R_new):.6f}]")
        print(f"      R_new top: {dict(R_new.most_common(5))}")
    out = {"n_old": n_old, "n_new": n_new, "distinct_old": len(R_old),
           "distinct_new": len(R_new), "pairs": len(pairs)}
    if len(pairs) >= 30:
        a = np.array([p[0] for p in pairs]); b = np.array([p[1] for p in pairs])
        sp_r, sp_p = stats.spearmanr(a, b)
        kd_r, kd_p = stats.kendalltau(a, b)
        print(f"      paired entries: {len(pairs)}")
        print(f"      Spearman(R_new, severity) = {sp_r:.4f}  p={sp_p:.3g}")
        print(f"      Kendall (R_new, severity) = {kd_r:.4f}  p={kd_p:.3g}")
        out.update(spearman=float(sp_r), spearman_p=float(sp_p),
                   kendall=float(kd_r), kendall_p=float(kd_p))
        check("R_new and asserted severity are NOT the same quantity",
              abs(sp_r) < 0.5, f"Spearman {sp_r:.4f}")
    else:
        print(f"      paired entries: {len(pairs)} -- too few to associate")
    return out


# ------------- E. the decisive measurement: round count vs difficulty --------
def section_e() -> dict:
    print("\nE. Would an R_k gate measure difficulty, or round count?")
    EASY = {"name": "4+4-like     (pi=0.02, q=0.95)", "pi": 0.02, "q": 0.95}
    HARD = {"name": "Riemann-like (pi=0.90, q=0.05)", "pi": 0.90, "q": 0.05}
    SK = 0.92

    def trajectory(pi, q, rounds=12, sk=SK):
        xs, x = [], pi
        for _ in range(rounds):
            x = rr.compute_rk(x, q, sk)
            xs.append(x)
        return xs

    print("    (i) WHAT THE MODEL CAN EXPRESS, if pi and q were per-question:")
    t_easy = trajectory(EASY["pi"], EASY["q"])
    t_hard = trajectory(HARD["pi"], HARD["q"])
    for nm, t in ((EASY["name"], t_easy), (HARD["name"], t_hard)):
        print(f"        {nm}: R_1={t[0]:.6f}  R_6={t[5]:.6f}  R_12={t[11]:.6f}")
    sep_possible = abs(t_easy[5] - t_hard[5])
    print(f"        separation at round 6: {sep_possible:.6f}")
    check("with per-question (pi,q) the model DOES separate his two questions",
          sep_possible > 0.2, f"gap {sep_possible:.6f}")

    print("    (ii) WHAT THE HARNESS ACTUALLY COMPUTES TODAY: q pinned to the")
    print("         model_params fallback 0.5 and pi to RK0_PI_BASE 0.5, for BOTH:")
    q_live, pi_live = 0.5, rr.RK0_PI_BASE
    t_easy_live = trajectory(pi_live, q_live)
    t_hard_live = trajectory(pi_live, q_live)
    for nm, t in ((EASY["name"], t_easy_live), (HARD["name"], t_hard_live)):
        print(f"        {nm}: R_1={t[0]:.6f}  R_6={t[5]:.6f}  R_12={t[11]:.6f}")
    sep_live = max(abs(a - b) for a, b in zip(t_easy_live, t_hard_live))
    print(f"        max separation over 12 rounds: {sep_live:.6e}")
    check("TODAY the two questions produce the IDENTICAL R_k trajectory",
          sep_live == 0.0, f"max gap {sep_live:.6e}")

    print("    (iii) so what WOULD a fixed R_k bound be measuring? round count.")
    traj = t_easy_live
    crossings = {}
    for theta in (0.40, 0.30, 0.25, 0.20, 0.15, 0.10):
        hit = next((i + 1 for i, v in enumerate(traj) if v <= theta), None)
        crossings[theta] = hit
        print(f"        bound R_k <= {theta:.2f}  first satisfied at round "
              f"{hit if hit else '>12 (not within 12)'}")
    mono = all(traj[i + 1] <= traj[i] + 1e-15 for i in range(len(traj) - 1))
    check("the live trajectory is monotone non-increasing in the round index",
          mono)
    reachable = [t for t, h in crossings.items() if h is not None]
    check("at least one candidate bound IS reachable today, so the gate would "
          "fire -- on round count, not on difficulty", bool(reachable),
          f"reachable: {sorted(reachable, reverse=True)}")
    x = 0.5
    for _ in range(4000):
        x = rr.compute_rk(x, q_live, SK)
    print(f"        live attractor at (q=0.5, S_k={SK}): R* = {x:.6f}")
    print(f"        no bound below R* = {x:.6f} is satisfiable at this S_k")
    return {"sep_possible": sep_possible, "sep_live": sep_live,
            "crossings": crossings, "live_attractor": x}


# ----------------------- F. does any gate read R_new -------------------------
GATE_FNS = ("_check_gamma_alt_convergence", "_check_hardened_convergence",
            "_check_stall_convergence", "_check_state_convergence")


def section_f() -> dict:
    print("\nF. Does any convergence predicate read R_new / R_old today?")
    src = (REPO / "bench" / "reference_runner_v3.py").read_text()
    tree = ast.parse(src)
    found = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name in GATE_FNS:
            names = set()
            for sub in ast.walk(node):
                if isinstance(sub, ast.Constant) and isinstance(sub.value, str) \
                        and sub.value in ("R_new", "R_old", "sk_result"):
                    names.add(sub.value)
                if isinstance(sub, ast.Name) and sub.id in ("R_new", "R_old"):
                    names.add(sub.id)
                if isinstance(sub, ast.Attribute) and sub.attr in ("R_new", "R_old"):
                    names.add(sub.attr)
            found[node.name] = sorted(names)
            print(f"      {node.name}: risk references = {sorted(names) or 'NONE'}")
    check("no convergence predicate reads R_new or R_old -- the quantity is "
          "RECORDED, not gating",
          all(not v for v in found.values()), str(found))
    return found


if __name__ == "__main__":
    section_a(); section_b(); section_c(); section_d(); section_e(); section_f()
    print("\n" + "=" * 72)
    if FAILURES:
        print(f"FALSIFIED on {len(FAILURES)} check(s):")
        for x in FAILURES:
            print(f"  - {x}")
        sys.exit(1)
    print("ALL CHECKS PASSED -- every claim in the reply is reproduced above.")
