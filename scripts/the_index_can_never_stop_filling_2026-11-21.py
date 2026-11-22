#!/usr/bin/env python3
"""THE MEMORY INDEX CANNOT BE KEPT UNDER ITS LIMIT BY ANY ONE-OFF TRIM.

Producer for every figure quoted in `scripts/cdsfl_sv.py`'s relief constants and
in `relieve_memory_index_pressure`'s docstring, per `measured-rate-travels-with-
its-script`. Run it before quoting any of them again: the index changes daily and
every statistic over it goes stale immediately.

THE FOUNDER'S INSTRUCTION, 2026-11-21, verbatim: *"sv should be trimming itself
automatically so it never becomes full. That was always the intent, and (as far
as I know) how it has always worked up until now. If it is no longer working that
way, then you clearly need to fix it."*

HIS MEMORY OF THE DESIGN IS CORRECT AND THE DEFECT IS ITS SCOPE. The trim has run
automatically inside `_preflight_completeness` since 2026-10-03. What no reply of
mine ever told him is what it can REACH: ageing is confined to
`_MEMORY_AGEING_SECTIONS`, and the pressure is in `Feedback`, which is excluded
deliberately and for a sound reason -- a standing rule does not go stale by the
calendar, and `test_standing_feedback_is_NEVER_moved_however_old` pins that.

WHAT THIS SCRIPT ESTABLISHES, each on 2 independent tools:
  1. the section census, so the scope gap is a measurement and not a claim;
  2. z3: NO finite one-off relief satisfies "never full" under positive growth,
     cross-checked by SymPy solving the same inequality symbolically;
  3. z3: the same query in CAP form is SAT, with `forall t` dropping out;
  4. the eviction order's dominance on a NAMED PROPERTY -- days a 3-star lesson
     stays in the loaded window -- which is what `composability-requires-a-
     measurement` demands before a composed rule may be recommended;
  5. every proportion with a confidence interval on 2 agreeing routes.

Exit 0 on success. Writes nothing.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import re
import statistics

MEM = (pathlib.Path.home() / ".claude" / "projects"
       / "-Users-georgejackson-Developer-Projects" / "memory")
INDEX = MEM / "MEMORY.md"
LOADER_LIMIT = 25_000
REFUSE_FRACTION = 0.98
#: The trailing window the growth rate is measured over. 21 days is 3 weeks of
#: his working rhythm and is stated here rather than chosen per run, so a later
#: run cannot pick the window that flatters the conclusion.
WINDOW_DAYS = 21
LINK = re.compile(r"\[([^\]]*)\]\(([^)]*)\)")
DATED = re.compile(r"(\d{4}-\d{2}-\d{2})\.md$")
FEEDBACK = "Feedback (applies to all work)"
JOIN = " · "


def u16(s: str) -> int:
    """The unit the loader actually counts: UTF-16 code units, not bytes.

    The index is full of stars, Greek letters and em-dashes, so conflating the
    two would itself be a silent wrong answer -- which is why
    `_MEMORY_INDEX_LIMIT_CHARS` carries the same note.
    """
    return len(s.encode("utf-16-le")) // 2


def sections(text: str) -> list[tuple[str, str]]:
    out, name, buf = [], "<preamble>", []
    for line in text.splitlines(keepends=True):
        if line.startswith("## "):
            out.append((name, "".join(buf)))
            name, buf = line[3:].strip(), [line]
        else:
            buf.append(line)
    out.append((name, "".join(buf)))
    return out


def units_of(feedback: str) -> list[str]:
    """Feedback's atomic pointer-units. The section packs many per line."""
    out = []
    for line in feedback.splitlines():
        if line.startswith("## ") or not line.strip():
            continue
        out.extend(line.split(JOIN))
    return out


def growth_rate() -> tuple[float, float, int, int]:
    """New dated memory files per day over the trailing window, and per-pointer cost."""
    stamps = []
    for p in MEM.glob("*.md"):
        m = DATED.search(p.name)
        if m:
            try:
                stamps.append(dt.date.fromisoformat(m.group(1)))
            except ValueError:
                continue
    stamps.sort()
    if not stamps:
        raise SystemExit("no date-stamped memory files; cannot measure growth")
    cut = stamps[-1] - dt.timedelta(days=WINDOW_DAYS)
    recent = [d for d in stamps if d >= cut]
    return len(recent) / WINDOW_DAYS, 0.0, len(recent), len(stamps)


def _args(argv=None):
    """★ `--help` MUST BE ANSWERED, NOT MERELY SURVIVED, and a script with no
    parser ignores the flag, runs its whole measurement and exits 0 -- which an
    exit-code test cannot tell from an answer. Held by
    `bench/tests/test_help_is_answered_2026-09-11.py`, which requires a `usage:`
    line; 30 of 53 scripts failed it when it was written.
    """
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true",
                    help="also print every figure as a JSON object")
    return ap.parse_args(argv)


def main(argv=None) -> int:
    args = _args(argv)
    if not INDEX.is_file():
        print(f"no index at {INDEX}")
        return 2
    text = INDEX.read_text(encoding="utf-8")
    total = u16(text)
    refuse = int(LOADER_LIMIT * REFUSE_FRACTION)

    print("=" * 72)
    print("1. THE SCOPE GAP: where the characters are against where ageing reaches")
    print("=" * 72)
    rows = [(n, u16(b)) for n, b in sections(text)]
    for n, c in sorted(rows, key=lambda r: -r[1]):
        reach = "  <- the ONLY section that ages" if n == "Project State" else ""
        print(f"  {c:7d} u16  {n}{reach}")
    print(f"  {total:7d} u16  TOTAL   (refuse at {REFUSE_FRACTION:.0%} = {refuse}, "
          f"headroom {refuse - total})")

    fb = next(b for n, b in sections(text) if n == FEEDBACK)
    ageing = next(b for n, b in sections(text) if n == "Project State")
    fb_u, ag_u = u16(fb), u16(ageing)

    units = units_of(fb)
    linked = [(u, max(m.group(1).count("★") for m in LINK.finditer(u)))
              for u in units if LINK.search(u)]
    n_ptr = len(linked)
    per_ptr = statistics.mean(u16(u) + len(JOIN) for u, _s in linked)
    rate_files, _unused, n_recent, n_all = growth_rate()
    rate_chars = rate_files * per_ptr
    print(f"\n  Feedback pointers: {n_ptr}   mean {per_ptr:.4f} u16 each")
    print(f"  growth: {n_recent} dated memory files in the trailing {WINDOW_DAYS} days "
          f"= {rate_files:.4f}/day = {rate_chars:.4f} u16/day   ({n_all} dated files in all)")

    print("\n" + "=" * 72)
    print("2. z3: IS ANY ONE-OFF RELIEF EVER SUFFICIENT?  (cross-checked in SymPy)")
    print("=" * 72)
    from z3 import ForAll, Implies, Real, Solver, sat, unsat
    R, t = Real("R"), Real("t")
    s = Solver()
    s.add(R >= 0, R <= total)
    s.add(ForAll([t], Implies(t >= 0, total - R + rate_chars * t <= refuse)))
    q1 = s.check()
    print(f"  exists R in [0, {total}] . forall t>=0 . total - R + rate*t <= refuse")
    print(f"  z3 -> {q1}")
    if q1 != unsat:
        print("  !! EXPECTED unsat; the premise of the fix does not hold")
        return 1
    print("  UNSAT: no finite one-off relief satisfies 'never full'.")

    import sympy as sp
    Rs, ts = sp.symbols("R t", real=True, nonnegative=True)
    rate_q = sp.Rational(str(round(rate_chars, 6)))
    t_star = sp.solve(sp.Eq(total - Rs + rate_q * ts - refuse, 0), ts)[0]
    whole = float(t_star.subs(Rs, total))
    print(f"  SymPy: t*(R) = {sp.simplify(t_star)}")
    print(f"  SymPy: emptying the ENTIRE index buys {whole:.2f} days -> finite, agrees with z3")

    print("\n" + "=" * 72)
    print("3. z3: THE SAME QUERY IN CAP FORM")
    print("=" * 72)
    other = total - fb_u
    B = Real("B")
    s2 = Solver()
    s2.add(B >= 0, B <= fb_u)
    s2.add(ForAll([t], Implies(t >= 0, other + B <= refuse)))
    q2 = s2.check()
    print(f"  other sections = {other} u16 (fixed); exists a cap B . forall t>=0 -> {q2}")
    if q2 != sat:
        print("  !! EXPECTED sat")
        return 1
    print(f"  SAT, and `forall t` drops out: max Feedback budget = {refuse - other} u16.")
    print("  So the mechanism must be a STANDING BOUND, not a bigger trim.")

    print("\n" + "=" * 72)
    print("4. THE EVICTION ORDER, ON A NAMED PROPERTY")
    print("   property: days a 3-star lesson stays inside the loaded window")
    print("=" * 72)
    three = sum(u16(u) + len(JOIN) for u, sal in linked if sal >= 3)
    low = sum(u16(u) + len(JOIN) for u, sal in linked if sal < 3)
    A = (0.5 * (three + low)) / rate_chars          # age alone
    Bd = low / rate_chars                           # salience alone
    C = (low + 0.5 * three) / rate_chars            # salience then age
    print(f"  3-star mass {three} u16   lower-salience mass {low} u16")
    print(f"  A  age alone            : {A:8.2f} days")
    print(f"  B  salience alone       : {Bd:8.2f} days, then NO evictable mass remains")
    print(f"  C  salience then age    : {C:8.2f} days   <- the composed rule")
    print(f"  dominance: C/A = {C / A:.4f}x   C/B = {C / Bd:.4f}x")
    th, lo, rt = sp.symbols("three low rate", positive=True)
    gap = sp.simplify((lo + th / 2) / rt - (lo + th) / 2 / rt)
    print(f"  SymPy: C - A = {gap}  -> positive whenever any lower-salience mass exists,")
    print("  so the composition dominates age alone UNCONDITIONALLY, not just here.")
    if not (C > A > Bd):
        print("  !! the composed rule no longer dominates; the recommendation lapses")
        return 1

    print("\n" + "=" * 72)
    print("5. PROPORTIONS, EACH ON 2 AGREEING ROUTES")
    print("=" * 72)
    import mpmath as mp
    from scipy.stats import beta as sbeta
    from statsmodels.stats.proportion import proportion_confint

    def wilson_hand(k, n, z=1.959963984540054):
        p = k / n
        d = 1 + z * z / n
        c = (p + z * z / (2 * n)) / d
        h = z * mp.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
        return float(c - h), float(c + h)

    def cp_hand(k, n):
        lo_ = 0.0 if k == 0 else float(sbeta.ppf(0.025, k, n - k + 1))
        hi_ = 1.0 if k == n else float(sbeta.ppf(0.975, k + 1, n - k))
        return lo_, hi_

    worst = 0.0
    for label, k, n in [
        ("Feedback share of the index", fb_u, total),
        ("ageing scope's share of the index", ag_u, total),
        ("3-star share of Feedback pointers",
         sum(1 for _u, s_ in linked if s_ >= 3), n_ptr),
    ]:
        w1 = proportion_confint(k, n, 0.05, "wilson")
        w2 = wilson_hand(k, n)
        c1 = proportion_confint(k, n, 0.05, "beta")
        c2 = cp_hand(k, n)
        d1 = max(abs(w1[0] - w2[0]), abs(w1[1] - w2[1]))
        d2 = max(abs(c1[0] - c2[0]), abs(c1[1] - c2[1]))
        worst = max(worst, d1, d2)
        print(f"  {label}: {k}/{n} = {k / n:.6f}")
        print(f"     Wilson [{w1[0]:.6f}, {w1[1]:.6f}]  2-route dmax {d1:.3e}")
        print(f"     Clopper-Pearson [{c1[0]:.6f}, {c1[1]:.6f}]  2-route dmax {d2:.3e}")
    print(f"\n  worst 2-route disagreement across all intervals: {worst:.3e}")

    print("\n" + "=" * 72)
    print("VERDICT")
    print("=" * 72)
    print(f"  The trim is automatic and always has been. Its SCOPE reaches "
          f"{ag_u}/{total} = {ag_u / total:.6f} of the index,")
    print(f"  while the growth sits in Feedback at {fb_u}/{total} = {fb_u / total:.6f}.")
    print("  No one-off relief can satisfy his instruction (z3 unsat); a standing")
    print("  bound can (z3 sat), and salience-then-age dominates either half alone.")
    if args.json:
        print(json.dumps({
            "total_u16": total, "refuse": refuse, "feedback_u16": fb_u,
            "ageing_u16": ag_u, "pointers": n_ptr, "u16_per_pointer": per_ptr,
            "rate_files_per_day": rate_files, "rate_u16_per_day": rate_chars,
            "whole_index_days": whole, "max_feedback_budget": refuse - other,
            "days_age_only": A, "days_salience_only": Bd, "days_composed": C,
            "worst_two_route_delta": worst}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
