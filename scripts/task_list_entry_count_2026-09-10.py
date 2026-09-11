#!/usr/bin/env python3
"""Task M1: how many entries does the master task list actually have?

MEASURED, and committed alongside the figures (`measured-rate-travels-with-its-script`).

WHY THIS SCRIPT EXISTS, and it is the entry's own subject turned on itself.
M1 argues that the task list cannot be counted mechanically without an explicit
machine-readable marker. It then quoted "15 of 29, 51.7%" -- a denominator it
described as coming from a narrow regular expression. The arithmetic was right
and the population was wrong: `parse_entries` returns 48 at both `4b697af` and
`cfdc0cb`, so the corrected figure is 15 of 48.

AND THE CORRECTION CARRIED FORWARD A SECOND UNVERIFIED CLAIM, found by this
script on 2026-09-10. The corrected entry still said that "2 different regular
expressions over this file counted 29 entries and 48 entries". **No counter
reads 29 at ANY of the file's revisions.** This script walks every revision of
the file in `git log` and evaluates 4 counters at each: the committed `ENTRY`
regex raw, the same regex with its letter prefix removed, the `<!-- task: -->`
markers, and the shipped `parse_entries` engine. The minimum any of them has
ever returned is 35, at the file's first revision. 29 was never a count of this
file. Correcting a figure while preserving an unverified story about where the
figure came from is the same defect one level up.

THE ENGINE IS CALLED, NOT RE-IMPLEMENTED (`execute-do-not-grep`). A script that
retyped the pattern would assert only that this file and that file describe the
same regex, which is exactly the class of test that cannot detect a producer and
a consumer disagreeing.

Two tools per proportion, as the project requires: statsmodels for the intervals
and an mpmath closed form that shares none of statsmodels' implementation.
"""
from __future__ import annotations

import pathlib
import re
import subprocess
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from _cli_help import answer_help  # noqa: E402

# `--help` MUST NOT ACT. MEASURED 2026-09-11: `--help` on
# `scripts/assemble_panel_record_0819.py` rewrote a 55,814-byte verbatim panel
# record down to 1,334 bytes and exited 0, because the flag fell through to the
# script's ordinary work. 7 tracked scripts both WROTE something and ignored the
# flag -- 5.7377% of 122, Wilson [2.8068%, 11.3709%].
#
# `answer_help` returns immediately when argv is empty, so a plain run reaches
# exactly the code it reached before.
answer_help(__doc__, __file__, sys.argv[1:])

REPO = pathlib.Path(__file__).resolve().parents[1]
REL = "experimental_notes/CDSFL_MASTER_TASK_LIST.md"
LIST = REPO / REL

sys.path.insert(0, str(REPO / "scripts"))
from task_list_markers import ENTRY, parse_entries  # noqa: E402

#: The committed pattern with its optional 1-2 letter prefix removed. This is
#: what "narrow" means concretely: it cannot see `M1`, `P3`, `V5`, `A7` or `Z1`,
#: every lettered section the list has grown. It is NOT a reconstruction of
#: whatever produced 29 -- nothing reproduces that, which is the point.
NARROW = re.compile(r"^\*\*(\d+(?:\.\d+)?[a-z]?)(?:\.\*\*|\*\*|\.|)\s")

TASK_MARKER = re.compile(r"<!--\s*task:")

#: Rule 20 statuses, per the note standard.
STATUSES = ("PROPOSED", "BUILT", "TESTED", "COMMITTED", "ENABLED")
#: THE FORM MATTERS AND THE FIRST VERSION OF THIS SCRIPT GOT IT WRONG. Rule 20
#: statuses were written in PROSE ("Status COMMITTED and ENABLED 2026-09-09.")
#: before the `<!-- task: ... status: ... -->` markers existed; at `4b697af` and
#: `cfdc0cb` there are 0 markers in the whole file. Searching only for the marker
#: form returned "0 of 48", which is not M1's claim and is not true of the file.
#: Both forms are counted, separately, and both are printed.
PROSE_STATUS = re.compile(r"\bStatus\s+(?:is\s+)?(" + "|".join(STATUSES) + r")\b")
MARKER_STATUS = re.compile(r"status:\s*(" + "|".join(STATUSES) + r")\b")


def wilson_mpmath(k: int, n: int, conf: float = 0.95) -> tuple[float, float]:
    """A closed form that shares no code with statsmodels."""
    import mpmath as mp
    from scipy import stats as sps
    mp.mp.dps = 30
    z = mp.mpf(str(sps.norm.ppf(1 - (1 - conf) / 2)))
    p, N = mp.mpf(k) / n, mp.mpf(n)
    centre = (p + z**2 / (2 * N)) / (1 + z**2 / N)
    half = (z / (1 + z**2 / N)) * mp.sqrt(p * (1 - p) / N + z**2 / (4 * N**2))
    return float(centre - half), float(centre + half)


def report(label: str, k: int, n: int) -> None:
    from statsmodels.stats.proportion import proportion_confint
    if n == 0:
        print(f"  {label}\n      no denominator — 0 entries matched")
        return
    lo_w, hi_w = proportion_confint(k, n, method="wilson")
    lo_c, hi_c = proportion_confint(k, n, method="beta")
    lo_m, hi_m = wilson_mpmath(k, n) if 0 < k < n else (lo_w, hi_w)
    agree = abs(lo_w - lo_m) < 1e-9 and abs(hi_w - hi_m) < 1e-9
    print(f"  {label}")
    print(f"      {k} of {n} = {k / n:.4%}")
    print(f"      Wilson 95%          [statsmodels] : [{lo_w:.4%}, {hi_w:.4%}]")
    print(f"      Wilson 95%          [mpmath     ] : [{lo_m:.4%}, {hi_m:.4%}]   agree to 1e-9: {agree}")
    print(f"      Clopper-Pearson 95% [statsmodels] : [{lo_c:.4%}, {hi_c:.4%}]")


def _engine_count(text: str) -> int:
    """Run the SHIPPED parser over a revision's text."""
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False,
                                     encoding="utf-8") as f:
        f.write(text)
        tmp = pathlib.Path(f.name)
    try:
        return len(parse_entries(tmp))
    finally:
        tmp.unlink(missing_ok=True)


def counters(text: str) -> dict[str, int]:
    lines = text.splitlines()
    return {
        "engine": _engine_count(text),
        "ENTRY raw": sum(1 for ln in lines if ENTRY.match(ln)),
        "narrow": sum(1 for ln in lines if NARROW.match(ln)),
        "markers": len(TASK_MARKER.findall(text)),
    }


def with_status(text: str, pattern: re.Pattern, status_re: re.Pattern) -> int:
    """Entries carrying a Rule 20 status within the next 3 lines.

    The window is 3 lines rather than exactly 1 because a heading may be followed
    by prose before its status. Widening a window can only raise a count, so this
    is an UPPER BOUND on coverage -- stated here rather than left for a reader to
    discover. The prose form is matched from the heading line itself, because
    that is where "Status COMMITTED" is written.
    """
    lines = text.splitlines()
    n = 0
    for i, ln in enumerate(lines):
        if not pattern.match(ln):
            continue
        window = "\n".join(lines[i:i + 4] if status_re is PROSE_STATUS
                           else lines[i + 1:i + 4])
        if status_re.search(window):
            n += 1
    return n


def revisions() -> list[tuple[str, str]]:
    out = subprocess.run(["git", "log", "--format=%h %ci", "--", REL],
                         cwd=REPO, capture_output=True, text=True, timeout=120)
    rows = []
    for line in out.stdout.strip().splitlines():
        h, _, when = line.partition(" ")
        rows.append((h, when.strip()))
    return rows


def text_at(rev: str) -> str | None:
    r = subprocess.run(["git", "show", f"{rev}:{REL}"], cwd=REPO,
                       capture_output=True, text=True, timeout=60)
    return r.stdout if r.returncode == 0 else None


def main() -> int:
    print(f"file: {REL}\n")
    revs = revisions()
    print(f"EVERY REVISION OF THE FILE — {len(revs)} of them — under 4 counters:")
    print(f"  {'rev':>8}  {'when':<26} {'engine':>7} {'ENTRYraw':>9} {'narrow':>7} {'markers':>8}")
    seen_29 = []
    floors: dict[str, int] = {}
    for rev, when in revs:
        t = text_at(rev)
        if t is None:
            continue
        c = counters(t)
        if 29 in c.values():
            seen_29.append(rev)
        for name, v in c.items():
            floors[name] = v if name not in floors else min(floors[name], v)
        print(f"  {rev:>8}  {when:<26} {c['engine']:7d} {c['ENTRY raw']:9d} "
              f"{c['narrow']:7d} {c['markers']:8d}")

    print(f"\n  revisions at which ANY counter reads 29: "
          f"{', '.join(seen_29) if seen_29 else 'NONE'}")
    print("  lowest value each counter has ever returned: "
          + ", ".join(f"{k}={v}" for k, v in floors.items()))
    print("     (`markers` reads 0 before 33ce5d6 because the marker comments did "
          "not exist yet;\n      it is the entry COUNTERS that never reach 29.)")
    if not seen_29:
        print("  => the denominator 29 was never a count of this file by any of these 4 "
              "counters.\n     M1's corrected text should not attribute it to a regular "
              "expression over this file.")

    live = LIST.read_text(encoding="utf-8")
    c = counters(live)
    print(f"\nAT HEAD: engine={c['engine']}, ENTRY raw={c['ENTRY raw']}, "
          f"narrow={c['narrow']}, markers={c['markers']}")
    print("  engine and ENTRY raw differ because `_is_entry` drops headings on the "
          "NOT_ENTRIES list.")

    print("\nRULE 20 STATUS COVERAGE at the 2 revisions M1 cites:")
    for rev in ("4b697af", "cfdc0cb"):
        t = text_at(rev)
        if t is None:
            print(f"  {rev}: not present in this clone")
            continue
        n = _engine_count(t)
        k_prose = with_status(t, ENTRY, PROSE_STATUS)
        k_mark = with_status(t, ENTRY, MARKER_STATUS)
        print(f"  --- {rev} --- marker-form statuses at this revision: {k_mark} "
              f"(the marker comments did not exist yet)")
        report("prose-form statuses against the engine denominator:", k_prose, n)

    print("\nWHAT THE NARROW PATTERN CANNOT SEE at HEAD — the lettered identifiers:")
    lettered = sorted({ENTRY.match(ln).group(1) for ln in live.splitlines()
                       if ENTRY.match(ln) and not NARROW.match(ln)})
    print(f"      {len(lettered)} identifiers: {', '.join(lettered)}")
    print("\nThe file cannot be counted mechanically without agreeing which counter is "
          "canonical,\nwhich is the strongest available argument for the explicit "
          "machine-readable marker M1 asks for.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
