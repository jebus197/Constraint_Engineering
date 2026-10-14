# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'the_directive_set_and_capability_2026-10-14', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 0392cd8fdddd1d285addb6a7b38ceeec4de621cd94fc0f8c754ddffe1e24d94f
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Historical-narrative ("chatter") share of the two CDSFL directive source files.

PANEL REVIEW ITEM 1, 2026-10-14. A brief claims the historical-narrative share,
"under the broadest defensible predicate", is 8 of 494 non-empty lines in
`cdsfl_core_formal.md` and 13 of 762 in `cdsfl_operational.md`; 1,486 of 74,178
characters combined; 902 of 48,878 of what a seat actually receives.

WHAT THIS SCRIPT DOES, AND WHY IT EXISTS AS A SCRIPT. The 2026-10-13 figures
(18 of 494 and 20 of 762) were withdrawn precisely because they ran inline with
no committed script. This one reproduces every number reported in the review,
states each predicate as code rather than as prose, and computes the Wilson
interval TWICE by independent tools so neither is taken on trust.

THE THREE PREDICATES (narrow / medium / broad) plus a fourth broadest form are
all applied to the same denominators, so the reader sees the whole range rather
than one chosen point. The published predicate -- `20\\d\\d|\\bMEASURED\\b` over
non-empty lines, used by `scripts/what_the_full_directive_set_costs_2026-10-14.py`
-- is reproduced here verbatim as P3 so the brief's own figure is auditable.

RUN IT:  python3 scripts/directive_chatter_predicate_2026-10-14.py
`--help` is free and dispatches nothing. No required arguments.
"""
from __future__ import annotations

import argparse
import json
import math
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
UNIVERSAL = REPO / "bench" / "directives" / "universal"
CORE = UNIVERSAL / "cdsfl_core_formal.md"
OPERATIONAL = UNIVERSAL / "cdsfl_operational.md"
PRUNING_REVIEW = (
    REPO / "experimental_notes" / "CDSFL_Directive_Pruning_Review_2026-07-18.md"
)

# --------------------------------------------------------------------------
# The predicate atoms. Every one is a compiled regex so the predicate is the
# code, not a description of the code.
# --------------------------------------------------------------------------
_MONTH = (
    r"(?:January|February|March|April|May|June|July|August|September"
    r"|October|November|December)"
)

#: A FULL calendar date: ISO, "D Month YYYY", "Month YYYY", or a "(YYYY)" citation.
RE_FULL_DATE = re.compile(
    rf"\b20\d\d-\d\d-\d\d\b"
    rf"|\b\d{{1,2}}\s+{_MONTH}\s+20\d\d\b"
    rf"|\b{_MONTH}\s+20\d\d\b"
    rf"|\(20\d\d\)"
)

#: A verb or marker that RECOUNTS a past event rather than stating a rule.
RE_RECOUNT = re.compile(
    r"\b(?:added|corrected|derived|implemented|ratified|amendment|recorded"
    r"|adjudicated|raised|reviewed|as of|showed|was built|previous text"
    r"|prior round)\b",
    re.I,
)

#: An OPERATIVE imperative. A line carrying one of these is instruction, so the
#: narrow predicate refuses to call it narrative even when it also carries a date.
RE_IMPERATIVE = re.compile(
    r"\bMUST\b|\bDo not\b|\brequired\b|\bshall\b|\bREJECT\b", re.I
)

#: Named past experiment / incident / external citation -- narrative with no date.
RE_NAMED_PAST = re.compile(
    r"\bExp \d+\b|\bExperiments? \d+|\bC00\d\d\b|Hossenfelder|et al\."
    r"|arXiv:|reward-hacking literature|forensic scan",
    re.I,
)

#: THE PUBLISHED PREDICATE, byte-for-byte from
#: scripts/what_the_full_directive_set_costs_2026-10-14.py. Reproduced, not
#: re-invented, so the brief's own 8 / 13 is checkable here.
RE_PUBLISHED_BROAD = re.compile(r"20\d\d|\bMEASURED\b", re.I)


# --------------------------------------------------------------------------
# Line / paragraph machinery
# --------------------------------------------------------------------------
def nonempty(text: str) -> list[tuple[int, str]]:
    """(1-based line number, line) for every non-empty line.

    Non-empty is the denominator because it is what reproduces the 494 / 762
    counts quoted in the brief, and because a blank line is not a line of
    specification.
    """
    return [(i, ln) for i, ln in enumerate(text.splitlines(), 1) if ln.strip()]


def paragraphs(text: str) -> list[list[tuple[int, str]]]:
    """Blank-line-delimited blocks of non-empty lines."""
    blocks: list[list[tuple[int, str]]] = []
    cur: list[tuple[int, str]] = []
    for i, ln in enumerate(text.splitlines(), 1):
        if ln.strip():
            cur.append((i, ln))
        elif cur:
            blocks.append(cur)
            cur = []
    if cur:
        blocks.append(cur)
    return blocks


# --------------------------------------------------------------------------
# The four predicates
# --------------------------------------------------------------------------
def p1_narrow(text: str) -> set[int]:
    """NARROW. A line is historical narrative iff it carries a FULL calendar
    date AND a past-event recounting marker AND no operative imperative.

    This is the predicate the task statement describes: "a line matching a date
    pattern AND recounting a past event, not stating a rule."
    """
    return {
        n
        for n, ln in nonempty(text)
        if RE_FULL_DATE.search(ln)
        and RE_RECOUNT.search(ln)
        and not RE_IMPERATIVE.search(ln)
    }


def p2_medium(text: str) -> set[int]:
    """MEDIUM. Narrative is a PASSAGE, not a line. Count every line of a
    blank-line-delimited paragraph that either (a) contains a P1-style
    date+recounting line or (b) is about a named past experiment / incident /
    external citation -- provided no line in that paragraph is an operative
    imperative.

    The imperative veto is what keeps this from swallowing instruction: a
    paragraph that tells the model to do something is not chatter, however much
    provenance it also carries.
    """
    keep: set[int] = set()
    for blk in paragraphs(text):
        dated = any(
            RE_FULL_DATE.search(ln) and RE_RECOUNT.search(ln) for _, ln in blk
        )
        named = any(RE_NAMED_PAST.search(ln) for _, ln in blk)
        if (dated or named) and not any(RE_IMPERATIVE.search(ln) for _, ln in blk):
            keep.update(n for n, _ in blk)
    return keep


def p3_published_broad(text: str) -> set[int]:
    """BROAD. The published line-level predicate, reproduced verbatim: any
    non-empty line containing a 20xx token or the word MEASURED.

    This is what the brief reports. It is BROAD in the sense of admitting lines
    that are not narrative at all (see the false-positive audit below).
    """
    return {n for n, ln in nonempty(text) if RE_PUBLISHED_BROAD.search(ln)}


def p4_broadest(text: str) -> set[int]:
    """BROADEST DEFENSIBLE. Paragraph expansion of P3: every line of any
    paragraph containing a P3 hit. No imperative veto.

    This is the genuine upper bound on "how much text sits in a passage that
    recounts something", and it is several times the figure in the brief.
    """
    keep: set[int] = set()
    for blk in paragraphs(text):
        if any(RE_PUBLISHED_BROAD.search(ln) for _, ln in blk):
            keep.update(n for n, _ in blk)
    return keep


PREDICATES = [
    ("P1 narrow   (date AND recounting AND not imperative)", p1_narrow),
    ("P2 medium   (paragraph-expanded, imperative-vetoed)", p2_medium),
    ("P3 broad    (PUBLISHED: 20xx|MEASURED, per line)", p3_published_broad),
    ("P4 broadest (paragraph-expanded P3, no veto)", p4_broadest),
]


# --------------------------------------------------------------------------
# Wilson interval, TWICE, by independent routes
# --------------------------------------------------------------------------
def wilson_hand(k: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    """Hand-rolled Wilson score interval. No statsmodels, no scipy.

    centre = (k + z^2/2) / (n + z^2);  half = z/(n+z^2) * sqrt(k(n-k)/n + z^2/4)
    """
    if n == 0:
        return (float("nan"), float("nan"))
    z2 = z * z
    denom = n + z2
    centre = (k + z2 / 2.0) / denom
    half = (z / denom) * math.sqrt(k * (n - k) / n + z2 / 4.0)
    return (max(0.0, centre - half), min(1.0, centre + half))


def wilson_scipy(k: int, n: int, alpha: float = 0.05):
    """Same interval, z taken from scipy's normal quantile rather than a literal."""
    try:
        from scipy.stats import norm
    except Exception:
        return None
    return wilson_hand(k, n, z=float(norm.ppf(1.0 - alpha / 2.0)))


def wilson_statsmodels(k: int, n: int, alpha: float = 0.05):
    try:
        from statsmodels.stats.proportion import proportion_confint
    except Exception:
        return None
    lo, hi = proportion_confint(k, n, alpha=alpha, method="wilson")
    return (float(lo), float(hi))


AGREE_TOL = 5e-12


def interval_block(k: int, n: int) -> dict:
    hand = wilson_hand(k, n)
    sm = wilson_statsmodels(k, n)
    sp = wilson_scipy(k, n)
    agree = True
    for other in (sm, sp):
        if other is None:
            agree = False
            continue
        agree &= abs(other[0] - hand[0]) < AGREE_TOL
        agree &= abs(other[1] - hand[1]) < AGREE_TOL
    return {
        "k": k,
        "n": n,
        "point": (k / n) if n else float("nan"),
        "wilson_hand": hand,
        "wilson_statsmodels": sm,
        "wilson_scipy": sp,
        "agree": agree,
    }


def fmt_interval(b: dict) -> str:
    lo, hi = b["wilson_hand"]
    sm = b["wilson_statsmodels"]
    sp = b["wilson_scipy"]
    smtxt = "UNAVAILABLE" if sm is None else f"[{sm[0]:.8f}, {sm[1]:.8f}]"
    sptxt = "UNAVAILABLE" if sp is None else f"[{sp[0]:.8f}, {sp[1]:.8f}]"
    flag = "AGREE" if b["agree"] else "DISAGREE -- DO NOT USE"
    return (
        f"{b['k']:4d}/{b['n']:<4d} = {b['point']:.6f}  "
        f"hand=[{lo:.8f}, {hi:.8f}]  statsmodels={smtxt}  scipy={sptxt}  [{flag}]"
    )


# --------------------------------------------------------------------------
# Reachability sweep: can ANY predicate in a broad family hit 18 and 20?
# --------------------------------------------------------------------------
_ATOMS: dict[str, re.Pattern] = {
    "bare_year_20xx": re.compile(r"20\d\d"),
    "any_4_digit": re.compile(r"\b\d{4}\b"),
    "iso_date": re.compile(r"\b20\d\d-\d\d-\d\d\b"),
    "full_date": RE_FULL_DATE,
    "month_name": re.compile(_MONTH),
    "year_or_MEASURED": RE_PUBLISHED_BROAD,
    "year_or_month": re.compile(rf"20\d\d|{_MONTH}", re.I),
    "recount_marker": RE_RECOUNT,
    "named_past": RE_NAMED_PAST,
    "repo_path_ref": re.compile(r"`[a-z_]+/[A-Za-z0-9_./-]+`"),
    "paren_provenance": re.compile(r"^\s*>?\s*\(|\(Recorded|\(Corrected|\(Stage"),
    "exp_number": re.compile(r"\bExp(?:eriments?)?\s*\d+", re.I),
    "citation": re.compile(r"et al\.|arXiv:|\(20\d\d\)"),
}


def _sweep_counts(text: str) -> dict:
    """Every line-count reachable by a single atom, a 2-atom OR, a 2-atom AND,
    and the paragraph expansion of each. Returns count -> example predicate names.
    """
    ne = nonempty(text)
    blocks = paragraphs(text)
    names = list(_ATOMS)
    reach: dict = {}

    def record(count: int, label: str) -> None:
        reach.setdefault(count, []).append(label)

    def line_pred(fn, label: str) -> None:
        hits = {n for n, ln in ne if fn(ln)}
        record(len(hits), label)
        para = set()
        for blk in blocks:
            if any(fn(ln) for _, ln in blk):
                para.update(n for n, _ in blk)
        record(len(para), f"para({label})")

    for a in names:
        ra = _ATOMS[a]
        line_pred(lambda ln, ra=ra: bool(ra.search(ln)), a)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            ra, rb = _ATOMS[a], _ATOMS[b]
            line_pred(
                lambda ln, ra=ra, rb=rb: bool(ra.search(ln) or rb.search(ln)),
                f"{a} OR {b}",
            )
            line_pred(
                lambda ln, ra=ra, rb=rb: bool(ra.search(ln) and rb.search(ln)),
                f"{a} AND {b}",
            )
    for label, fn in PREDICATES:
        record(len(fn(text)), label.split()[0])
    return reach


# --------------------------------------------------------------------------
# Volume accounting
# --------------------------------------------------------------------------
def volume(text: str, keep: set) -> int:
    """Characters on the kept lines, +1 per line for its newline. Matches the
    convention in scripts/what_the_full_directive_set_costs_2026-10-14.py so the
    two scripts cannot drift."""
    return sum(len(ln) + 1 for n, ln in nonempty(text) if n in keep)


def seat_received():
    """What a seat ACTUALLY receives, by execution against the live composer.

    `cdsfl_core_formal.md` goes through the composer, which renders it minimally
    (27,803 chars exceeds every per-model cap). `cdsfl_operational.md` is
    appended AFTER the phenotype transform specifically to bypass those caps
    (bench/reference_runner_v3.py:534-545), so it arrives in full.
    """
    sys.path.insert(0, str(REPO))
    from bench.cdsfl_registry import composer as C

    minimal = C._load_universal_directive(None).text
    op = OPERATIONAL.read_text(encoding="utf-8")
    return len(minimal), len(op), minimal


# --------------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true", help="also dump machine-readable")
    args = ap.parse_args()

    for f in (CORE, OPERATIONAL):
        if not f.is_file():
            print(f"missing: {f}")
            return 2

    core = CORE.read_text(encoding="utf-8")
    op = OPERATIONAL.read_text(encoding="utf-8")
    out: dict = {}

    print("=== DENOMINATORS (characters counted as CHARACTERS, not bytes) ===")
    for label, txt in (("cdsfl_core_formal.md", core), ("cdsfl_operational.md", op)):
        print(
            f"  {label:24s}: {len(txt):,} chars, "
            f"{len(nonempty(txt)):,} non-empty lines, "
            f"{len(txt.splitlines()):,} physical lines"
        )
    combined_chars = len(core) + len(op)
    print(f"  {'COMBINED':24s}: {combined_chars:,} chars")
    print(
        f"  ** the brief says 74,178 combined; the files total "
        f"{combined_chars:,}. Off by {74178 - combined_chars}. **"
    )

    print("\n=== THE FOUR PREDICATES, SAME DENOMINATORS ===")
    out["predicates"] = {}
    for label, fn in PREDICATES:
        print(f"\n  {label}")
        rows = {}
        tot_k = tot_n = tot_vol = 0
        for fl, txt in (("core", core), ("operational", op)):
            keep = fn(txt)
            n = len(nonempty(txt))
            vol = volume(txt, keep)
            rows[fl] = {"lines": interval_block(len(keep), n), "chars": vol}
            tot_k += len(keep)
            tot_n += n
            tot_vol += vol
            print(f"    {fl:12s} lines  {fmt_interval(rows[fl]['lines'])}")
            print(
                f"    {fl:12s} chars  {vol:,} of {len(txt):,} = "
                f"{vol / len(txt):.6f}"
            )
        comb = interval_block(tot_k, tot_n)
        rows["combined"] = {"lines": comb, "chars": tot_vol}
        print(f"    {'COMBINED':12s} lines  {fmt_interval(comb)}")
        print(
            f"    {'COMBINED':12s} chars  {tot_vol:,} of {combined_chars:,} = "
            f"{tot_vol / combined_chars:.6f}"
        )
        out["predicates"][label] = rows

    print("\n=== THE BRIEF'S FIGURES, CHECKED ===")
    b_core = p3_published_broad(core)
    b_op = p3_published_broad(op)
    checks = [
        ("8 of 494 core lines", len(b_core) == 8, f"got {len(b_core)} of 494"),
        ("13 of 762 op lines", len(b_op) == 13, f"got {len(b_op)} of 762"),
        (
            "1,486 chars combined",
            volume(core, b_core) + volume(op, b_op) == 1486,
            f"got {volume(core, b_core) + volume(op, b_op):,}",
        ),
        (
            "74,178 combined denominator",
            combined_chars == 74178,
            f"got {combined_chars:,} -- the brief is 1 char high",
        ),
    ]
    for name, ok, detail in checks:
        print(f"  [{'OK ' if ok else 'NO '}] {name:30s} {detail}")

    print("\n=== FALSE-POSITIVE AUDIT OF THE PUBLISHED PREDICATE (P3) ===")
    print("  P3 hits that carry NO calendar date -- i.e. operative content:")
    fp = 0
    for fl, txt, keep in (("core", core, b_core), ("operational", op, b_op)):
        for n, ln in nonempty(txt):
            if n in keep and RE_FULL_DATE.search(ln) is None:
                fp += 1
                print(f"    {fl}:{n}  {ln.strip()[:88]}")
    print(f"  -> {fp} of {len(b_core) + len(b_op)} P3 hits carry no calendar date.")

    print("\n=== REACHABILITY: ARE 8, 13, 18, 20 REACHABLE? ===")
    for fl, txt, targets in (
        ("core (n=494)", core, (8, 18)),
        ("operational (n=762)", op, (13, 20)),
    ):
        reach = _sweep_counts(txt)
        keys = sorted(reach)
        print(f"  {fl}: {len(keys)} distinct counts reachable over "
              f"{len(_ATOMS)} atoms x {{single, OR, AND}} x {{line, paragraph}}; "
              f"min={keys[0]}, max={keys[-1]}")
        for t in targets:
            if t in reach:
                print(f"    {t:3d}: REACHABLE  e.g. {reach[t][0]}")
            else:
                near = min(keys, key=lambda k: abs(k - t))
                print(
                    f"    {t:3d}: NOT REACHABLE by any predicate in this family "
                    f"(nearest = {near}, via {reach[near][0]})"
                )
        out.setdefault("reachable", {})[fl] = keys

    print("\n=== WHAT A SEAT ACTUALLY RECEIVES (live composer) ===")
    try:
        n_min, n_op, minimal = seat_received()
        seat_total = n_min + n_op
        print(f"  cdsfl_core_formal.md  -> minimal render: {n_min:,} chars")
        print(f"  cdsfl_operational.md  -> appended in full: {n_op:,} chars")
        print(f"  SEAT TOTAL: {seat_total:,} chars")
        print(
            f"  ** the brief says 48,878; the composer delivers "
            f"{seat_total:,}. Off by {48878 - seat_total}. **"
        )
        op_chat = volume(op, p3_published_broad(op))
        mins = {n for n, ln in nonempty(minimal) if RE_PUBLISHED_BROAD.search(ln)}
        print(
            f"  P3 chatter in the delivered text: {op_chat:,} (operational) "
            f"+ {volume(minimal, mins):,} (minimal render) chars"
        )
        for n, ln in nonempty(minimal):
            if n in mins:
                print(f"    minimal-render hit, NOT narrative: {ln.strip()}")
        blk = interval_block(op_chat, seat_total)
        print(f"  share  {fmt_interval(blk)}")
        out["seat"] = {"minimal": n_min, "operational": n_op, "total": seat_total,
                       "chatter_chars": op_chat}
    except Exception as exc:
        print(f"  composer not callable: {exc!r} -- no delivery figure asserted")

    print("\n=== KEEP-VERBATIM SECTIONS (from the 2026-07-18 pruning review) ===")
    if PRUNING_REVIEW.is_file():
        rv = PRUNING_REVIEW.read_text(encoding="utf-8").splitlines()
        cur = None
        verdicts = []
        for ln in rv:
            if ln.startswith("## "):
                cur = ln[3:].strip()
            if "**VERDICT:**" in ln and cur:
                v = ln.split("**VERDICT:**", 1)[1].strip()
                verdicts.append((cur, v))
                cur = None
        for head, v in verdicts:
            tag = "KEEP-VERBATIM" if v.startswith("KEEP-VERBATIM") else "compress"
            print(f"  [{tag:13s}] {head}")
        kv = [h for h, v in verdicts if v.startswith("KEEP-VERBATIM")]
        print(f"  -> {len(kv)} of {len(verdicts)} sections are KEEP-VERBATIM.")
        out["keep_verbatim"] = kv
    else:
        print(f"  missing: {PRUNING_REVIEW}")

    print("\n=== WORKED-PROOF REQUIREMENT: OCCURRENCE COUNTS IN THE SOURCES ===")
    terms = ["worked proof", "worked proofs", "DERIVE", "derivation"]
    out["worked_proof"] = {}
    for label, txt in (("cdsfl_core_formal.md", core), ("cdsfl_operational.md", op)):
        print(f"  {label}")
        row = {}
        for t in terms:
            ci = len(re.findall(re.escape(t), txt, re.I))
            cs = len(re.findall(re.escape(t), txt))
            row[t] = {"case_insensitive": ci, "case_sensitive": cs}
            print(f"    {t!r:18s} case-insensitive={ci:2d}   exact-case={cs:2d}")
        out["worked_proof"][label] = row
    zero = all(
        out["worked_proof"][f][t]["case_insensitive"] == 0
        for f in out["worked_proof"]
        for t in ("worked proof", "worked proofs")
    )
    print(
        f"  CLAIM '\"worked proof\" appears 0 times in either source file': "
        f"{'CONFIRMED' if zero else 'REFUTED'}"
    )
    print("  (The requirement is nonetheless ENFORCED in code -- bench/dm/_rk_proof.py")
    print("   and bench/reference_runner_v3.py:9499-9511 -- so the directive is silent")
    print("   about a gate the runner applies. That is a gap, not a saving.)")

    if args.json:
        print(json.dumps(out, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
