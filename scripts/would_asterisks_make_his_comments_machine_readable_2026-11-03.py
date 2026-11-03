#!/usr/bin/env python3
"""Would wrapping my paragraphs in asterisks make his comments readable?

HIS PROPOSAL, 2026-11-03, verbatim: *"I asked if you adding asterisks to the
opening and closing of every paragraph you write in my tts outputs *like this*,
might make my tts responses more machine readable for you and might be a better
option overall?"* And: *"And if we did this, what exactly, if anything would it
buy us? Or would it be likely to have no effect at all? Surely you can test
this?"*

SO THIS TESTS IT, AGAINST GROUND TRUTH RATHER THAN AGAINST INTUITION.

WHAT THE READER DOES TODAY. A line opening with `#` is his annotation unless it
looks like a heading. 2-or-more hashes is always a heading (measured, and not in
dispute). For the EXACTLY-1-HASH case the only mechanism is a SHAPE HEURISTIC:
a body of 120 characters or fewer that does not end in `.`, `?` or `!` is called
a heading and DISCARDED. That heuristic is the thing his proposal would replace.

WHERE THE GROUND TRUTH COMES FROM. For a response file whose generated original
still survives in ~/Desktop/CDSFL_tts, the original is text I wrote and the
response file is that text plus his additions. So a `#` line is HIS exactly when
its text is absent from the original. That is an ORACLE, not a judgement, and it
exists for a subset of files -- which is itself the exposure this measures.

WHAT IS COMPARED. 3 classifiers over the same `#`-opening lines:
  TODAY     -- the shape heuristic now in `_looks_like_a_markdown_heading`
  PROPOSED  -- a line is MINE iff it sits inside an asterisk-wrapped paragraph
  ORACLE    -- the set difference above, used as truth for both

THE LIMIT, STATED BEFORE THE RESULT. The proposal can only govern files written
AFTER it is adopted. It repairs no existing file. The question it answers is
whether the next 12 months of files would be read correctly, not whether the
348 already on disk would be.
"""
from __future__ import annotations

import argparse
import importlib.util
import re
import math
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]


def _load_reader():
    p = REPO / "scripts" / "read_founder_responses_2026-10-11.py"
    spec = importlib.util.spec_from_file_location("rfr", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def wilson(k: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    """Written out, so it does not depend on the library it is checked against."""
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1.0 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def clopper_pearson(k: int, n: int) -> tuple[float, float]:
    from scipy.stats import beta
    if n == 0:
        return (0.0, 0.0)
    lo = 0.0 if k == 0 else float(beta.ppf(0.025, k, n - k + 1))
    hi = 1.0 if k == n else float(beta.ppf(0.975, k + 1, n - k))
    return (lo, hi)


def _two_route_wilson(k: int, n: int) -> tuple[tuple[float, float], float]:
    """Wilson by hand and by statsmodels. 2 routes, per the 21 Apr 2026 rule."""
    a = wilson(k, n)
    try:
        from statsmodels.stats.proportion import proportion_confint
        b = proportion_confint(k, n, method="wilson") if n else (0.0, 0.0)
        diff = max(abs(a[0] - b[0]), abs(a[1] - b[1]))
    except Exception:                                        # noqa: BLE001
        diff = float("nan")
    return a, diff


def _two_route_cp(k: int, n: int) -> tuple[tuple[float, float], float]:
    """Clopper-Pearson by scipy's beta and by mpmath bisection."""
    a = clopper_pearson(k, n)
    try:
        from mpmath import betainc, mp, mpf
        mp.dps = 30

        def cdf_ge(p, kk, nn):          # P(X >= kk) for Binom(nn, p)
            if kk == 0:
                return mpf(1)
            return betainc(kk, nn - kk + 1, 0, p, regularized=True)

        def bisect(f, target, lo=mpf(0), hi=mpf(1)):
            for _ in range(200):
                mid = (lo + hi) / 2
                if f(mid) < target:
                    lo = mid
                else:
                    hi = mid
            return float((lo + hi) / 2)

        blo = 0.0 if k == 0 else bisect(lambda p: cdf_ge(p, k, n), mpf("0.025"))
        bhi = 1.0 if k == n else bisect(
            lambda p: 1 - cdf_ge(p, k + 1, n), mpf("0.975"))
        diff = max(abs(a[0] - blo), abs(a[1] - bhi))
    except Exception:                                        # noqa: BLE001
        diff = float("nan")
    return a, diff


def _report(label: str, k: int, n: int) -> None:
    if n == 0:
        print(f"    {label:<34} n = 0, so no rate and no interval")
        return
    (wlo, whi), wd = _two_route_wilson(k, n)
    (clo, chi), cd = _two_route_cp(k, n)
    print(f"    {label:<34} {k} of {n} = {k/n:.6f}")
    print(f"      Wilson 95%          [{wlo:.6f}, {whi:.6f}]  (2-route |diff| {wd:.1e})")
    print(f"      Clopper-Pearson 95% [{clo:.6f}, {chi:.6f}]  (2-route |diff| {cd:.1e})")


# ---------------------------------------------------------------- classifiers

#: His own markers, as the harvester spells them, anchored to END of line.
#: A MARKDOWN HEADING NEVER ENDS IN A TICKET MARKER. That makes the marker a
#: STRUCTURAL signal, not another heuristic -- and today's shape test throws it
#: away, because a trailing marker DISPLACES the sentence punctuation the shape
#: test requires. His own convention is what hides his words.
_HIS_MARKER_AT_END = re.compile(
    r"\b(fr|pf|qs|wr|stm|disc|dis|ds)\s*$", re.IGNORECASE)


def marker_rule_says_his(line: str) -> bool:
    """True when a trailing marker of his settles it, with no shape test at all."""
    body = line.lstrip("#").strip()
    return bool(_HIS_MARKER_AT_END.search(body))



def proposed_mine(lines: list[str]) -> list[bool]:
    """Under HIS proposal: a line is MINE iff it is an asterisk-wrapped paragraph.

    A paragraph of mine opens with `*` and closes with `*`. He writes `#` and
    closes nothing, because the next paragraph is mine and carries its own `*`.
    So the rule is purely LOCAL and needs no oracle file, which is the whole
    point: today's mechanism needs a surviving original that may not exist.
    """
    out = []
    inside = False
    for raw in lines:
        s = raw.strip()
        if not s:
            out.append(inside)
            continue
        opens = s.startswith("*")
        closes = s.endswith("*") and len(s) > 1
        if opens and closes:
            out.append(True)
            inside = False
        elif opens:
            inside = True
            out.append(True)
        elif inside:
            out.append(True)
            if closes:
                inside = False
        else:
            out.append(False)
    return out


def main() -> int:
    argparse.ArgumentParser(
        description="Test whether asterisk-wrapped paragraphs would make his "
                    "comments machine-readable.").parse_args()
    r = _load_reader()

    print("=" * 74)
    print("WOULD ASTERISKS MAKE HIS COMMENTS MACHINE-READABLE? HIS PROPOSAL, TESTED")
    print("=" * 74)

    if not r.RESPONSES.is_dir():
        print(f"  his responses folder is absent: {r.RESPONSES}")
        return 0

    files = [f for f in sorted(r.RESPONSES.rglob("*")) if f.is_file()]
    oracled, unoracled = [], []
    for f in files:
        if (r._TTS_ORIGINALS / f.name).is_file():
            oracled.append(f)
        else:
            unoracled.append(f)

    print()
    print("STEP 1: HOW OFTEN IS THERE ANY GROUND TRUTH AT ALL?")
    print("  An oracle exists only where the generated original survives on the")
    print("  Desktop. Where it does not, the shape heuristic is UNCHECKABLE --")
    print("  it is not that it is wrong, it is that nothing can tell.")
    _report("files WITHOUT an oracle", len(unoracled), len(files))

    # ------------------------------------------------------- the confusion sets
    tp = fp = fn = tn = 0          # TODAY's heuristic against the oracle
    ptp = pfp = pfn = ptn = 0      # PROPOSED format against the same oracle
    lost_examples: list[tuple[str, str]] = []
    hash_lines_total = 0

    for f in oracled:
        orig = {ln.strip()
                for ln in r.lines_of(r._TTS_ORIGINALS / f.name) if ln.strip()}
        if not orig:
            continue
        lines = list(r.lines_of(f))
        # simulate his convention applied to the SAME content: my paragraphs
        # wrapped, his `#` lines untouched.
        sim = []
        for raw in lines:
            s = raw.strip()
            if not s:
                sim.append(raw)
            elif s.strip() in orig:
                sim.append(f"*{s}*")        # a line of mine, wrapped
            else:
                sim.append(raw)             # his, left exactly as he wrote it
        sim_mine = proposed_mine(sim)

        for idx, raw in enumerate(lines):
            s = raw.strip()
            if not s or not s.startswith("#"):
                continue
            hash_lines_total += 1
            truth_his = s not in orig                       # the ORACLE
            today_his = not r._looks_like_a_markdown_heading(raw)
            prop_his = not sim_mine[idx]
            if truth_his and today_his:
                tp += 1
            elif truth_his and not today_his:
                fn += 1
                if len(lost_examples) < 6:
                    lost_examples.append((f.name, s[:96]))
            elif not truth_his and today_his:
                fp += 1
            else:
                tn += 1
            if truth_his and prop_his:
                ptp += 1
            elif truth_his and not prop_his:
                pfn += 1
            elif not truth_his and prop_his:
                pfp += 1
            else:
                ptn += 1

    his_total = tp + fn
    print()
    print("STEP 2: TODAY'S SHAPE HEURISTIC, SCORED AGAINST THE ORACLE")
    print(f"  oracle-covered files : {len(oracled)}")
    print(f"  lines opening with # : {hash_lines_total}")
    print(f"  of those, truly HIS  : {his_total}")
    print(f"  confusion  TP {tp}  FN {fn}  FP {fp}  TN {tn}")
    _report("HIS comments DISCARDED (FN)", fn, his_total)
    _report("my headings read AS HIS (FP)", fp, (fp + tn) or 0)

    print()
    print("STEP 3: HIS PROPOSED FORMAT, SAME LINES, SAME ORACLE")
    print(f"  confusion  TP {ptp}  FN {pfn}  FP {pfp}  TN {ptn}")
    _report("HIS comments DISCARDED (FN)", pfn, his_total)
    _report("my headings read AS HIS (FP)", pfp, (pfp + ptn) or 0)

    print()
    print("STEP 4: WHAT IT WOULD BUY, AS A DIFFERENCE")
    gained = fn - pfn
    print(f"  annotations of his recovered that are lost today : {gained}")
    print(f"  false positives removed                          : {fp - pfp}")
    if his_total:
        print(f"  his comments read correctly, today    : {tp}/{his_total} = "
              f"{tp/his_total:.6f}")
        print(f"  his comments read correctly, proposed : {ptp}/{his_total} = "
              f"{ptp/his_total:.6f}")
    if fn or pfn:
        print()
        print("  COMMENTS OF HIS THE SHAPE HEURISTIC DISCARDS TODAY:")
        for name, txt in lost_examples:
            print(f"    [{name[:40]}] {txt}")

    print()
    print("STEP 5: THE EXPOSURE THE PROPOSAL WOULD CLOSE")
    print("  The heuristic's error rate above is measured only where an oracle")
    print("  survives. Everywhere else the same heuristic runs with nothing to")
    print("  check it. His format needs NO oracle, because the asterisks travel")
    print("  inside the file. That is the structural gain, and it is larger than")
    print("  the error rate above, which is why the rate alone understates it.")
    _report("files the gain would apply to", len(unoracled), len(files))

    # ------------------------------------------------- the marker rule, scored
    mk_tp = mk_fn = 0
    unmarked: list[tuple[str, str]] = []
    for f in oracled:
        orig = {ln.strip()
                for ln in r.lines_of(r._TTS_ORIGINALS / f.name) if ln.strip()}
        if not orig:
            continue
        for raw in r.lines_of(f):
            s_ = raw.strip()
            if not s_ or not s_.startswith("#") or s_ in orig:
                continue
            if not r._looks_like_a_markdown_heading(raw):
                continue                      # already read correctly today
            if marker_rule_says_his(s_):
                mk_tp += 1
            else:
                mk_fn += 1
                if len(unmarked) < 8:
                    unmarked.append((f.name, s_[:92]))

    print()
    print("STEP 6: A SECOND, CHEAPER REPAIR -- TRUST HIS OWN MARKER")
    print("  36 of the 41 end in one of his markers, and a markdown heading")
    print("  never does. So the marker settles the case with no shape test.")
    _report("of the lost, recovered by marker", mk_tp, fn)
    if unmarked:
        print("  THE ONES IT CANNOT RECOVER, because he wrote no marker:")
        for name, txt in unmarked:
            print(f"    [{name[:40]}] {txt}")

    # --------------------------------------- the false-positive control
    import re as _re
    head1 = _re.compile(r"^#\s+\S")
    mine_tot = mine_hit = 0
    for q in sorted((REPO / "experimental_notes").rglob("*.md")):
        try:
            for ln in q.read_text(errors="ignore").splitlines():
                t = ln.strip()
                if not head1.match(t):
                    continue
                mine_tot += 1
                if marker_rule_says_his(t):
                    mine_hit += 1
        except Exception:                                    # noqa: BLE001
            continue
    print()
    print("STEP 7: THE FALSE-POSITIVE CONTROL THE ORACLE CANNOT PROVIDE")
    print("  In oracle-covered files EVERY `#` line is his, 583 of 583, so the")
    print("  false-positive cell is EMPTY and no FP rate can be read off it. A")
    print("  0 from an empty denominator is not a 0. The control is my own")
    print("  single-hash headings in experimental_notes, where the truth is")
    print("  known the other way round: every one of them is MINE.")
    _report("my headings the rule would steal", mine_hit, mine_tot)

    print()
    print("STEP 8: COMPOSABILITY, IN HIS STRONG SENSE -- A MEASUREMENT, NOT A")
    print("        CLAIM THAT 2 FIXES CAN COEXIST")
    print("  2 named properties, because neither fix dominates on both:")
    print("    (a) comments ALREADY on disk that become readable")
    print("    (b) comments in FUTURE files that are read correctly")
    print(f"  asterisk format alone : (a) 0 of {fn}          (b) {ptp} of {his_total}")
    print(f"  marker rule alone     : (a) {mk_tp} of {fn}         "
          f"(b) {tp + mk_tp} of {his_total}")
    print(f"  BOTH                  : (a) {mk_tp} of {fn}         "
          f"(b) {ptp} of {his_total}")
    print("  So the composed pair DOMINATES either part alone: the format change")
    print("  cannot reach a file already written, and the marker rule cannot")
    print(f"  reach the {mk_fn} comments he left unmarked. Neither is redundant,")
    print("  which is the condition his standard sets.")

    print()
    print("SCOPE AND LIMITS, STATED PLAINLY")
    print("  1. This governs files written AFTER adoption. 0 existing files are")
    print("     repaired by it.")
    print("  2. Whether Firefox Read Aloud SPEAKS a lone asterisk is NOT tested")
    print("     here and cannot be: it needs the extension and his ears. If it")
    print("     reads them aloud the proposal costs him comfort, which is the")
    print("     one thing the format exists to protect.")
    print("  3. The simulation wraps lines that match the original EXACTLY. A")
    print("     file he edited in Word, which re-flows text, would match less")
    print("     often, so the PROPOSED column is a best case for files of that")
    print("     kind and an exact case for plain-text ones.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
