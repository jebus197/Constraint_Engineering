# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'falsifier_supply_and_integrity_r2_2026-10-02', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: a17e73e0ec480979a2588195fdb1c40730a2cb99f79599fc7a53958c632666ab
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""ADJUDICATES CAUSE 1, and the population dispute, on the same corpus.

THE QUESTION THE FOUNDER ASKED was whether falsifiers are "too specific, rather
than general". `repro_supply_causes_2026-10-02.py` answered with CAUSE 1: a body
naming a concrete file ERRORs at OR 4.3063 (scipy p = 2.43e-04). That reproduced,
and it is the only cause of the three that survived an attempt to kill it.

BUT "NAMES A CONCRETE FILE" CONFLATES TWO DIFFERENT DEFECTS, and the distinction
decides what the fix is:

  OVER-SPECIFIC LOGIC   the body reasons about one artefact in a way that cannot
                        transfer -- a generality problem, fixed by a template.
  NON-PORTABLE PATH     the body is fine but hard-codes an ABSOLUTE path that
                        only exists on the authoring machine -- a portability
                        problem, fixed by resolving the target at run time.

They demand opposite remedies, and `FILE_RE` in the reproduction scores them
identically, because `[\\w./-]+\\.py` matches `bench/report.py` and
`/Users/<op>/.../bench/report.py` alike. So this script splits the "named"
column three ways -- ABSOLUTE path / RELATIVE path only / no file named -- and
asks which cell carries the ERROR excess.

WHY THIS WAS WORTH SPLITTING. Two independent observations in this panel's own
round point the same way. On the archived prose run, 7 of 7 falsifiers carrying an
ABSOLUTE path were refused by `falsifier_verify` layer 1 as "a path outside the
declared target", while 13 of 14 carrying a RELATIVE path re-ran and CONFIRMED in
this checkout today. And `key_access_forensics.scan_run` flagged 107 of 114
CONFIRMED hits on that same run purely because the archived bodies spell the
repository with the prefix the run EXECUTED under. Both are the same fault:
absolute paths do not survive leaving the machine that wrote them.

THE POPULATION DISPUTE, settled in the same pass. The brief carries two
incompatible cuts of "criticals with neither a falsifier nor a verdict":
0 of 558 post-2026-06-06, and 14 of 624 cut at exp42. Both are computed here, on
one loader, and the 14 are attributed run by run so the disagreement is explained
rather than averaged.

Every proportion carries a Wilson interval from statsmodels against an
independent mpmath closed form; every odds ratio carries a scipy Fisher exact
test against an independent mpmath hypergeometric sum. No Wolfram result is used.

Run:  python3 scripts/supply_cause1_is_path_portability_2026-10-02.py
"""
from __future__ import annotations

import json
import pathlib
import re
import sys
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parents[1]
CRIT = 0.7

# Reused VERBATIM from repro_supply_causes_2026-10-02.py so the population is the
# same one the declared figures were computed on. Any divergence here would make
# the comparison meaningless.
FILE_RE = re.compile(r"[\w./-]+\.(?:py|md|json|toml|txt|csv|yaml|yml)\b")
# An absolute POSIX path, or a $HOME/~ lead that resolves to one.
ABS_RE = re.compile(r"(?:(?<![\w.])/[\w.-]+/|~/|\$HOME/|\$\{HOME\}/)")


def wilson(k, n):
    from statsmodels.stats.proportion import proportion_confint
    import mpmath as mp
    if not n:
        return float("nan"), float("nan"), True
    lo, hi = proportion_confint(k, n, method="wilson")
    mp.mp.dps = 40
    z = mp.mpf("1.959963984540054235524594430520551527955")
    p, d = mp.mpf(k) / n, 1 + z ** 2 / n
    c = p + z ** 2 / (2 * n)
    h = z * mp.sqrt(p * (1 - p) / n + z ** 2 / (4 * n ** 2))
    mlo, mhi = float((c - h) / d), float((c + h) / d)
    return float(lo), float(hi), abs(lo - mlo) < 1e-9 and abs(hi - mhi) < 1e-9


def show(label, k, n, pad=38):
    lo, hi, agree = wilson(k, n)
    if not n:
        print(f"  {label:<{pad}} n=0  NOT MEASURABLE")
        return
    print(f"  {label:<{pad}} {k:4d}/{n:4d} = {100*k/n:7.3f}%  "
          f"Wilson [{100*lo:6.3f}%, {100*hi:6.3f}%]  agree={agree}")


def fisher(a, b, c, d):
    from scipy.stats import fisher_exact
    import mpmath as mp
    odds, p = fisher_exact([[a, b], [c, d]])
    mp.mp.dps = 50
    n = a + b + c + d
    r1, c1 = a + b, a + c
    if not n or not r1 or not c1:
        return odds, p, float("nan")

    def pr(x):
        return (mp.binomial(c1, x) * mp.binomial(n - c1, r1 - x)) / mp.binomial(n, r1)

    obs, tot = pr(a), mp.mpf(0)
    for x in range(max(0, r1 - (n - c1)), min(r1, c1) + 1):
        q = pr(x)
        if q <= obs * (1 + mp.mpf("1e-30")):
            tot += q
    return odds, p, float(tot)


def ftest(label, a, b, c, d):
    print(f"  table [[{a},{b}],[{c},{d}]]")
    if not (a + b) or not (c + d):
        print(f"  {label}: NOT MEASURABLE (an empty margin)")
        return
    o, p, pm = fisher(a, b, c, d)
    print(f"  {label}: Fisher OR = {o:.4f}  scipy p = {p:.6e}  "
          f"mpmath p = {pm:.6e}  agree={abs(p - pm) < 1e-9}")


def entries():
    """The reproduction's loader, with ONE defect repaired and nothing else.

    D-2, measured: the original iterates ("runner_state.json", "*_report.json")
    and keys on (run_dir, cid), letting a later row win only when the earlier
    carried no falsifier body. `runner_state.json` records NO target block in any
    of 57 files; `*_report.json` records `target_file` in 71. So in every run dir
    holding both, the target-LESS row won and `target_file` survived on 52 of 624
    criticals, all `.py`, none prose -- which is why CAUSE 3 reported NOT
    MEASURABLE. The target is a RUN-level fact, so it is taken per run dir from
    whichever artefact carries it, and the per-finding tie-break is left alone.
    """
    run_target: dict[str, str] = {}
    rows: dict[tuple[str, str], tuple] = {}
    for name in ("runner_state.json", "*_report.json"):
        for f in sorted((ROOT / "bench" / "logs").glob(f"*/{name}")):
            try:
                data = json.loads(f.read_text(encoding="utf-8", errors="replace"))
            except Exception:  # noqa: BLE001
                continue
            cfg = data.get("config") or {}
            tgt = str(cfg.get("target_file") or data.get("target_file") or "")
            if tgt and not run_target.get(f.parent.name):
                run_target[f.parent.name] = tgt
            for cid, e in ((data.get("registry") or {}).get("entries") or {}).items():
                if not isinstance(e, dict) or (e.get("severity") or 0) < CRIT:
                    continue
                key = (f.parent.name, cid)
                body = ((e.get("falsifier_code") or "").strip()
                        or (e.get("last_falsifier_code") or "").strip())
                prev = rows.get(key)
                if prev is None or (not prev[2] and body):
                    rows[key] = (f.parent.name, tgt, body, e)
    return {k: (r, run_target.get(r, t), b, e) for k, (r, t, b, e) in rows.items()}


def expno(r):
    m = re.match(r"exp(\d+)", r)
    return int(m.group(1)) if m else None


def verdict(e):
    h = e.get("routing_history") or []
    return ((e.get("falsifier_verdict") or "").strip().upper()
            or (e.get("routing_verdict_unreconciled") or "").strip().upper()
            or ((h[-1].get("verdict") or "").strip().upper() if h else ""))


def main() -> int:
    rows = entries()
    post = {k: v for k, v in rows.items()
            if expno(k[0]) is None or expno(k[0]) >= 42}
    print(f"criticals (severity >= {CRIT}) : {len(rows)} total, "
          f"{len(post)} post-feature (exp42 cut)")
    print(f"run dirs with a recovered target: "
          f"{len({r for r, t, _, _ in post.values() if t})}")

    # ── CAUSE 1 SPLIT THREE WAYS ────────────────────────────────────────────
    print("\n== CAUSE 1 SPLIT: is the ERROR excess in the PATH or in the LOGIC? ==")
    cell = Counter()
    for (run, cid), (r, tgt, body, e) in post.items():
        v = verdict(e)
        if v not in ("ERROR", "CONFIRMED") or not body:
            continue
        if ABS_RE.search(body):
            kind = "absolute"
        elif FILE_RE.search(body):
            kind = "relative"
        else:
            kind = "none"
        cell[(kind, v)] += 1
    for kind in ("absolute", "relative", "none"):
        err, con = cell[(kind, "ERROR")], cell[(kind, "CONFIRMED")]
        show(f"ERROR rate | names an {kind:8s} path", err, err + con)

    A_e, A_c = cell[("absolute", "ERROR")], cell[("absolute", "CONFIRMED")]
    R_e, R_c = cell[("relative", "ERROR")], cell[("relative", "CONFIRMED")]
    N_e, N_c = cell[("none", "ERROR")], cell[("none", "CONFIRMED")]

    print("\n  (1) ABSOLUTE path vs everything else -- the PORTABILITY hypothesis")
    ftest("absolute vs rest", A_e, A_c, R_e + N_e, R_c + N_c)
    print("\n  (2) RELATIVE-only naming vs naming NOTHING -- the GENERALITY hypothesis")
    print("      If over-specific LOGIC were the mechanism, a body bound to a")
    print("      named file should error more even when the path is portable.")
    ftest("relative vs unnamed", R_e, R_c, N_e, N_c)
    print("\n  (3) the undivided claim, for comparison with the declared 4.3063")
    ftest("named (abs+rel) vs unnamed", A_e + R_e, A_c + R_c, N_e, N_c)

    # ── POPULATION DISPUTE ──────────────────────────────────────────────────
    print("\n== THE POPULATION DISPUTE: 14/624 (exp42 cut) vs 0/558 (date cut) ==")
    neither = {k: v for k, v in post.items()
               if not v[2] and not verdict(v[3])}
    show("neither falsifier nor verdict, exp42 cut", len(neither), len(post))
    by_run = Counter(k[0] for k in neither)
    for run, n in by_run.most_common():
        print(f"      {n:3d}  {run}")

    # The date cut, taken from each run's own recorded timestamp rather than from
    # its name, so a run whose name carries no date still lands somewhere.
    CUT = "2026-06-06"
    dated, undated = {}, {}
    for k, v in post.items():
        m = re.search(r"(20\d{2})(\d{2})(\d{2})T", k[0])
        iso = f"{m.group(1)}-{m.group(2)}-{m.group(3)}" if m else None
        (dated if iso else undated)[k] = (iso, v)
    after = {k: v for k, (iso, v) in dated.items() if iso >= CUT}
    show(f"... restricted to dirs dated >= {CUT}",
         sum(1 for k, v in after.items() if not v[2] and not verdict(v[3])),
         len(after))
    show("... in dirs carrying NO date in the name",
         sum(1 for k, (iso, v) in undated.items()
             if not v[2] and not verdict(v[3])), len(undated))
    print("  So the two cuts do not disagree about the corpus; they disagree about")
    print("  MEMBERSHIP. The exp42 cut admits run dirs with no parseable date, and")
    print("  that is where the residual sits. Report the cut with the figure.")
    return 0


if __name__ == "__main__":
    import argparse
    argparse.ArgumentParser(
        description=(__doc__ or "").strip().split("\n")[0] or None).parse_args()
    raise SystemExit(main())
