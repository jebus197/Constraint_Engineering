#!/usr/bin/env python3
"""Task A3: guard the CONTENT of a cited line, not merely the file.

MEASURED, and committed alongside the figures (`measured-rate-travels-with-its-script`).

THE DEFECT. A hand-written `path:LINE` citation breaks the moment anything is
inserted above it, and the existing citation guard checks only that the FILE
exists -- `cdsfl_utils.SUPPRESS_LINE` says so in as many words: "the FILE exists;
line numbers NOT checked". The run ledger self-heals because it has a generator.
Hand-written citations do not. This project moved the same citation 3 times in
one day on 2026-09-10, and the runner grew by roughly 90 lines that evening.

THE CHECK, AND WHY IT IS BY AST RATHER THAN BY TEXT. A citation is usually
preceded by the symbol it is about, in backticks. If that symbol is a function or
class, its true span is known exactly, and the question "does this citation point
inside the thing it names" is decidable. A text search would be defeated by the
symbol appearing in a comment 400 lines away; an AST span is not.

WHAT IT CANNOT CHECK, STATED RATHER THAN HIDDEN. A citation with no backticked
symbol before it, or one naming something that is not a def or a class, is
reported as UNCHECKABLE and counted separately. Folding those into the pass count
would be the "a guard that cannot fail" defect, and folding them into the fail
count would invent findings.
"""
from __future__ import annotations

import argparse  # noqa: F401  (imported in main; kept for discoverability)
import ast
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]

#: Files whose line citations are worth guarding. Extend deliberately.
CITED = ("bench/reference_runner_v3.py",)

#: Where citations are written.
SEARCH = ("experimental_notes/**/*.md", "bench/tests/*.py", "scripts/*.py",
          "resources/*.md", ".claude/*.md")

IDENT = re.compile(r"`([A-Za-z_][A-Za-z0-9_]*)`")


def spans(path: str) -> dict:
    tree = ast.parse((REPO / path).read_text(encoding="utf-8"))
    return {n.name: (n.lineno, getattr(n, "end_lineno", n.lineno))
            for n in ast.walk(tree)
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))}


def read_citing(path: pathlib.Path) -> tuple[bytes, str]:
    """The ONE way a citing file is read. Returns (raw bytes, decoded text).

    THREE DEFECTS CLOSED BY HAVING 1 READER, all found 2026-09-11 by both panel
    seats independently.

    1. `check()` read with `errors="replace"` and `repair()` with the strict
       default. One bad byte in one note therefore raised inside `repair()`, the
       hook's `|| true` swallowed it, and NO citation was repaired in that pass
       -- the "repair lags a commit behind" defect re-entering through the
       repair that exists to close it.

    2. `read_text` translates CRLF to LF on the way in and `write_text` writes
       LF on the way out, so repairing 1 line number silently rewrote EVERY line
       ending in the file. The offset guard cannot see that: the offsets agree;
       the damage is in the write.

    3. Worse, translation makes `check()`'s offsets index a DIFFERENT string
       from the bytes on disk, so a positional splice would land in the wrong
       place on any CRLF file. `decode` does no translation, so both agree by
       construction.

    Reachability today is 0 -- 862 citing files, 0 invalid UTF-8, 0 CRLF -- which
    is exactly why it needs a mechanism rather than a note. Nothing enforces LF
    or UTF-8 on these paths: there is no `.gitattributes` and no encoding check.
    """
    raw = path.read_bytes()
    return raw, raw.decode("utf-8", errors="replace")


def citing_files():
    seen = set()
    for pat in SEARCH:
        for p in REPO.glob(pat):
            if p.is_file() and p not in seen:
                seen.add(p)
                yield p


def check(target: str):
    sp = spans(target)
    rx = re.compile(re.escape(target) + r":(\d+)")
    n_lines = len((REPO / target).read_text(encoding="utf-8").splitlines())
    good, bad, unchecked, past_end = [], [], 0, []
    for p in citing_files():
        _raw, txt = read_citing(p)
        for m in rx.finditer(txt):
            line = int(m.group(1))
            if line > n_lines:
                past_end.append((p, line))
            ids = IDENT.findall(txt[max(0, m.start() - 220):m.start()])
            anchor = next((i for i in reversed(ids) if i in sp), None)
            if anchor is None:
                unchecked += 1
                continue
            lo, hi = sp[anchor]
            # The number's exact offsets travel with the finding, because
            # `repair` must splice AT THIS POSITION rather than search for the
            # digits again. See the corruption recorded in `repair`.
            (good if lo <= line <= hi else bad).append(
                (p, line, anchor, lo, hi, m.start(1), m.end(1)))
    return good, bad, unchecked, past_end, n_lines


def repair(target: str) -> int:
    """Re-point every stale anchored citation at its symbol's definition line.

    ADDED THE SAME EVENING THE GUARD WAS, and the reason is the guard's own
    output. The 6 citations were repaired at 21:20; adding a report block to the
    runner at 21:35 moved every one of them by exactly +102 and the guard went
    red inside the hour. Repairing by hand each time is a treadmill, and a
    treadmill is how the figure got wrong in the first place. The guard already
    computes the correct line, so it can write it.

        IT CORRUPTED 3 CITATIONS ON 2026-09-11 AND THE FIX IS POSITIONAL.

    The first version wrote `txt.replace(f"{target}:{line}", f"{target}:{lo}")`.
    That is an unbounded substring replace with no digit boundary, so a SHORT
    stale line number rewrites the PREFIX of every longer one. Reproduced by
    deliberately staling 1 citation to `:1` and committing, which turned
    `reference_runner_v3.py:1` into `:11456` and, in the same pass:

        in reference_runner_v3.py, line number before -> after:
            10934  ->  114560934
            12638  ->  114562638
            14984  ->  114564984

    (The numbers are written bare, not as `path:number` tokens, because a
    scanner cannot tell a warning about a corrupted citation from a corrupted
    citation -- and the guard added below duly flagged this very paragraph.)

    3 correct citations destroyed while repairing 1. The probe used `:1`, but
    nothing about the fault needs a contrived value: any stale number that is a
    prefix of another citation's number in the same file does it, and 4-digit
    and 5-digit line numbers into an 11,000-line file collide constantly --
    `:1135` would eat `:11354`.

    The SECOND fault in the same line is that `str.replace` is GLOBAL. Two
    citations sharing a line number, 1 stale and 1 correct, were both rewritten,
    so a citation that pointed inside its own symbol could be moved out of it.

    Both faults come from searching for the text again when the position was
    already known. `check` now carries the number's offsets and this splices at
    them, right to left so earlier offsets stay valid. If the bytes at an offset
    are not the digits expected, the edit is REFUSED and reported rather than
    applied to whatever is there.
    """
    _good, bad, _u, _p, _n = check(target)
    by_path: dict = {}
    for path, line, anchor, lo, _hi, start, end in bad:
        by_path.setdefault(path, []).append((start, end, line, lo, anchor))
    applied = 0
    for path, edits in by_path.items():
        raw, txt = read_citing(path)
        # REFUSE A FILE WHOSE BYTES DO NOT SURVIVE THE ROUND TRIP, and carry on
        # with the rest. `errors="replace"` would otherwise write U+FFFD over
        # real bytes. Refusing 1 file is a repair that did not happen; raising
        # is a pass that did not happen, for every file.
        if txt.encode("utf-8") != raw:
            print(f"  REFUSED {path.relative_to(REPO)}: its bytes are not valid "
                  f"UTF-8, so repairing it would overwrite them; nothing "
                  f"written", file=sys.stderr)
            continue
        messages = []
        for start, end, line, lo, anchor in sorted(edits, reverse=True):
            if txt[start:end] != str(line):
                print(f"  REFUSED {path.relative_to(REPO)}: offset {start} holds "
                      f"{txt[start:end]!r}, not {line}; nothing written",
                      file=sys.stderr)
                continue
            txt = txt[:start] + str(lo) + txt[end:]
            messages.append((start, f"  {path.relative_to(REPO)}: {line} -> {lo}"
                                    f"  (`{anchor}`)"))
            applied += 1
        if messages:
            # write_bytes, not write_text: write_text re-translates newlines, so
            # repairing 1 number in a CRLF file would rewrite every line ending.
            path.write_bytes(txt.encode("utf-8"))
            for _s, msg in sorted(messages):
                print(msg)
    return applied


def main() -> int:
    # A REAL PARSER, NOT `"--fix" in sys.argv`. The first version read argv
    # directly, so `--this-flag-does-not-exist` was accepted and exited 0 --
    # an unrecognised argument that reads as success, which is the defect class
    # this project spent 118 days on. Caught by
    # test_operational_scripts.py::test_an_unknown_flag_is_rejected_loudly.
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--fix", action="store_true",
                    help="re-point stale anchored citations at their symbol")
    args = ap.parse_args()
    if args.fix:
        total = sum(repair(t) for t in CITED)
        print(f"repaired {total} citation(s)")
        return 0
    rc = 0
    for target in CITED:
        good, bad, unchecked, past_end, n_lines = check(target)
        total = len(good) + len(bad) + unchecked
        print(f"--- {target} ({n_lines:,} lines) ---")
        print(f"  citations found        : {total}")
        print(f"  checkable (anchored)   : {len(good) + len(bad)}")
        print(f"  UNCHECKABLE (no symbol): {unchecked}")
        print(f"  pointing past the end  : {len(past_end)}")
        print(f"  inside the named symbol: {len(good)}")
        print(f"  OUTSIDE it             : {len(bad)}")
        if good or bad:
            from statsmodels.stats.proportion import proportion_confint
            k, n = len(bad), len(good) + len(bad)
            lo, hi = proportion_confint(k, n, method="wilson")
            lo_c, hi_c = proportion_confint(k, n, method="beta")
            print(f"  {k}/{n} = {k / n:.4%}  Wilson [{lo:.4%}, {hi:.4%}]  "
                  f"Clopper-Pearson [{lo_c:.4%}, {hi_c:.4%}]")
        for p, line, anchor, lo, hi, _s, _e in bad:
            rel = p.relative_to(REPO)
            print(f"    {rel}:{line} names `{anchor}`, which spans {lo}-{hi} "
                  f"(off by {lo - line:+d})")
            rc = 1
    if rc:
        print("\n  A citation that names a symbol must point inside it. Repair the")
        print("  line number, or cite the symbol and drop the number.")
    return rc


if __name__ == "__main__":
    sys.exit(main())
