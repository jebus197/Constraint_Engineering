#!/usr/bin/env python3
"""Which of the memory index's 2 truncation budgets binds, and by how much.

The loader truncates the index on EITHER too many characters (PRe=25000) or
too many lines (fie=200), read out of the installed binary rather than
assumed. `_MemoryIndexAudit.entries_left` reported the CHARACTER answer alone
until 2026-10-29, so it told the reader 34 entries of runway remained while
the binding LINE budget allowed 11 and `sv` itself would refuse after 1.

This script produces every figure quoted for that correction, and would
contradict them just as readily: it recomputes from the live index and from
every archived snapshot beside it, and proves the repaired bound safe with z3
instead of asserting it.

READ-ONLY. It never writes under the memory directory.
"""
from __future__ import annotations
import argparse, importlib.util, pathlib, re, statistics, sys

REPO = pathlib.Path(__file__).resolve().parents[1]
DATE_LINE = re.compile(r'^- \*\*(\d{1,2} \w+(?: [AP]M)?)\*\* — (.*)$')


def load_sv():
    spec = importlib.util.spec_from_file_location(
        "cdsfl_sv", REPO / "scripts" / "cdsfl_sv.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["cdsfl_sv"] = mod          # dataclass needs it registered
    spec.loader.exec_module(mod)
    return mod


def loader_units(text: str) -> tuple[int, int]:
    """Characters and lines exactly as the loader's EDt counts them.

    It trims first, then takes the JavaScript UTF-16 length and
    ``count('\\n') + 1``. Code points and UTF-8 bytes both differ from
    UTF-16 on this file, so the unit is not incidental.
    """
    t = text.strip()
    if not t:
        return 0, 0
    return sum(2 if ord(c) > 0xFFFF else 1 for c in t), t.count("\n") + 1


def median_pointer_len(sv, text: str) -> int:
    lens = [n for ln in text.splitlines()
            for _title, _t, n in sv._memory_index_pointers(ln)]
    return int(statistics.median(lens)) if lens else 0


def group_same_date(text: str) -> str:
    """Merge same-date entry lines WITHIN one section. Loses no pointer.

    Section-aware deliberately: a global merge would move an entry across a
    section boundary if 2 sections ever shared a date. On the 2026-10-29 index
    0 of 18 dates span more than 1 section, so the 2 forms agree there -- but
    the risk is a property of the mechanism, not of today's file.
    """
    out: list[str] = []
    seen: dict[tuple[str | None, str], int] = {}
    section: str | None = None
    for line in text.split("\n"):
        if line.startswith("## "):
            section = line[3:].strip()
        m = DATE_LINE.match(line)
        if not m:
            out.append(line)
            continue
        key = (section, m.group(1))
        if key in seen:
            out[seen[key]] = out[seen[key]].rstrip() + "; " + m.group(2)
        else:
            seen[key] = len(out)
            out.append(line)
    return "\n".join(out)


def budgets(sv, text: str) -> dict:
    chars, lines = loader_units(text)
    med = median_pointer_len(sv, text)
    cl, ll, frac = (sv._MEMORY_INDEX_LIMIT_CHARS, sv._MEMORY_INDEX_LIMIT_LINES,
                    sv._MEMORY_INDEX_REFUSE_FRACTION)
    by_chars = (cl - chars) // (med + 1) if med else -1
    by_lines = ll - lines
    return {
        "chars": chars, "lines": lines, "median": med,
        "by_chars": by_chars, "by_lines": by_lines,
        "binding": "LINES" if by_lines < by_chars else "CHARS",
        "true_left": min(by_chars, by_lines) if med else -1,
        "refuse_chars": (int(cl * frac) - chars) // (med + 1) if med else -1,
        "refuse_lines": int(ll * frac) - lines,
    }


def prove_min_is_safe() -> str:
    """z3: can min(by_chars, by_lines) overrun either budget? Expect unsat."""
    try:
        import z3
    except ImportError:                     # pragma: no cover
        return "z3 absent — not proven here"
    h, lh, m = z3.Ints("h lh m")
    fixed = z3.If(h / (m + 1) < lh, h / (m + 1), lh)
    s = z3.Solver()
    s.add(h >= 0, lh >= 0, m >= 1)
    s.add(z3.Or(fixed * (m + 1) > h, fixed > lh))
    return str(s.check())


def crossover(b: dict) -> str:
    """The median entry length at which the 2 budgets swap, from SymPy."""
    try:
        import sympy as sp
    except ImportError:                     # pragma: no cover
        return "sympy absent"
    if b["by_lines"] <= 0:
        return "no line headroom — crossover undefined"
    x = sp.Symbol("x", positive=True)
    sol = sp.solve(sp.Eq((25000 - b["chars"]) / (x + 1), b["by_lines"]), x)
    return ", ".join(f"{sp.nsimplify(s)} = {float(s):.4f}" for s in sol)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--index", default=None,
                    help="index to measure (default: the live MEMORY.md)")
    ap.add_argument("--snapshots", action="store_true",
                    help="also measure every MEMORY*.md snapshot beside it")
    args = ap.parse_args()      # exits on --help BEFORE any measurement runs
    sv = load_sv()
    mem = sv._MEMORY_DIR
    index = pathlib.Path(args.index) if args.index else mem / sv._MEMORY_INDEX_NAME
    text = index.read_text(encoding="utf-8")

    b = budgets(sv, text)
    audit = sv._audit_memory_index(index.parent)
    print(f"INDEX {index}")
    print(f"  chars {b['chars']} of {sv._MEMORY_INDEX_LIMIT_CHARS}   "
          f"lines {b['lines']} of {sv._MEMORY_INDEX_LIMIT_LINES}   "
          f"median pointer {b['median']} chars")
    print(f"  to the LOADER limit: {b['by_chars']} entries by chars, "
          f"{b['by_lines']} by lines -> BINDING {b['binding']} = {b['true_left']}")
    print(f"  to SV'S REFUSE line: {b['refuse_chars']} by chars, "
          f"{b['refuse_lines']} by lines")
    print(f"  sv reports entries_left = {audit.entries_left}"
          f"   (overstates by {audit.entries_left - b['true_left']})")
    print(f"  budgets cross at median entry = {crossover(b)} chars")
    print(f"  z3, can min() overrun either budget? {prove_min_is_safe()} "
          f"(unsat = proven safe)")

    trim = sv.archive_stale_memory_entries(mem, dry_run=True)
    print(f"\nTHE EXISTING TRIM, dry run: would move {trim['moved']}, "
          f"freeing {trim['freed_chars']} chars — {trim['reason'] or 'ok'}")

    g = group_same_date(text)
    gb = budgets(sv, g)
    # sv's OWN parser, not a second regex, so there is 1 source of truth about
    # what a pointer is. The question here is whether grouping LOSES a pointer,
    # which is a question about the set of targets, so the counts below are
    # DISTINCT targets: 185, against the audit's 187 entries. The 2 forms do NOT
    # disagree -- `feedback_measured_capability_not_model_names_2026-10-07.md`
    # and `rg_command.md` are each linked twice, so 187 entries carry 185
    # distinct targets. Comparing the 2 numbers as though they measured the same
    # thing was an error made while writing this script and caught by running it.
    def _ptrs(t: str) -> set[str]:
        return {tgt for ln in t.splitlines()
                for _ti, tgt, _n in sv._memory_index_pointers(ln)
                if tgt.endswith(".md")}
    before, after = _ptrs(text), _ptrs(g)
    print(f"SECTION-AWARE SAME-DATE GROUPING: lines {b['lines']} -> {gb['lines']} "
          f"({gb['lines'] - b['lines']:+d}), chars {b['chars']} -> {gb['chars']} "
          f"({gb['chars'] - b['chars']:+d})")
    print(f"  pointers {len(before)} -> {len(after)}; lost: "
          f"{sorted(before - after) or 'none'}")
    print(f"  refuse headroom in lines: {b['refuse_lines']} -> {gb['refuse_lines']}")

    if args.snapshots:
        print("\nWHICH BUDGET BOUND, PER SNAPSHOT")
        rows = []
        for p in sorted(mem.glob("MEMORY*.md")):
            sb = budgets(sv, p.read_text(encoding="utf-8", errors="replace"))
            rows.append((p.name, sb))
            print(f"  {p.name:<34} chars {sb['chars']:6d} lines {sb['lines']:4d} "
                  f"-> {sb['binding']}")
        n = sum(1 for _n, s in rows if s["binding"] == "LINES")
        print(f"  LINE budget bound in {n} of {len(rows)} snapshots")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
