#!/usr/bin/env python3
"""Task 7.2: how many notes did the linter's only real-note test actually reach?

MEASURED, and committed alongside the figure (`measured-rate-travels-with-its-script`).

THE CLAIM. Entry 7.2 states that before the pre-commit guard existed, the only
test that linted real notes selected those declaring a v1.7 foot-line -- "29 of
379 files, 7.65%, Wilson [5.4%, 10.8%]" -- so a new note that simply omitted the
foot-line was exempt by omission. The checker existed and the note never met it.
That figure was quoted with no script. This is the script.

THE SELECTOR IS IMPORTED, NOT RETYPED (`execute-do-not-grep`). `_v17_notes` in
`bench/tests/test_note_standard_v17_enforced_2026-08-26.py` is the live selector;
this script calls it. A retyped copy of the glob and the regex would assert only
that 2 files describe the same rule, which cannot detect them disagreeing.

TWO POPULATIONS ARE REPORTED, not one, because the denominator is the contested
half. `experimental_notes/*.md` at the top level and `experimental_notes/**/*.md`
recursively are different files, and the selector was itself non-recursive until
2026-09-08. Both are printed so a reader can see which 379 means.

Two tools per proportion: statsmodels for the intervals, and an mpmath closed
form that shares none of statsmodels' implementation.
"""
from __future__ import annotations

import functools
import importlib.util
import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
NOTES = REPO / "experimental_notes"
GUARD = REPO / "bench" / "tests" / "test_note_standard_v17_enforced_2026-08-26.py"


def _selector():
    """Import the LIVE selector from the enforcement test."""
    sys.path.insert(0, str(REPO))
    spec = importlib.util.spec_from_file_location("v17_guard", GUARD)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def wilson_mpmath(k: int, n: int, conf: float = 0.95) -> tuple[float, float]:
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
    lo_w, hi_w = proportion_confint(k, n, method="wilson")
    lo_c, hi_c = proportion_confint(k, n, method="beta")
    lo_m, hi_m = wilson_mpmath(k, n)
    agree = abs(lo_w - lo_m) < 1e-9 and abs(hi_w - hi_m) < 1e-9
    print(f"  {label}")
    print(f"      {k} of {n} = {k / n:.4%}")
    print(f"      Wilson 95%          [statsmodels] : [{lo_w:.4%}, {hi_w:.4%}]")
    print(f"      Wilson 95%          [mpmath     ] : [{lo_m:.4%}, {hi_m:.4%}]   agree to 1e-9: {agree}")
    print(f"      Clopper-Pearson 95% [statsmodels] : [{lo_c:.4%}, {hi_c:.4%}]")


def populations() -> dict[str, list[pathlib.Path]]:
    return {
        "experimental_notes/*.md (top level only)": sorted(NOTES.glob("*.md")),
        "experimental_notes/**/*.md (recursive)": sorted(NOTES.rglob("*.md")),
    }


def declaring(paths: list[pathlib.Path], footline: re.Pattern) -> list[pathlib.Path]:
    """Notes whose foot-line declares v1.7 or later — the selector's own rule."""
    out = []
    for p in paths:
        m = footline.search(p.read_text(encoding="utf-8", errors="replace"))
        if m and (int(m.group(1)), int(m.group(2))) >= (1, 7):
            out.append(p)
    return out


@functools.lru_cache(maxsize=None)
def _revision_footlines(rev: str) -> tuple[tuple[str, int, int], ...]:
    """(path, major, minor) for every note at `rev` that declares a foot-line.

    ONE `git grep` FOR THE WHOLE REVISION. The first version ran `git show` per
    file -- 380 subprocesses per call, and several tests call it, which pushed
    the full suite's runtime up measurably for a measurement that has not
    changed. The blast radius of a slow instrument is that nobody runs it, which
    is how the 6.2 script came to sit broken for a day.
    """
    r = subprocess.run(
        ["git", "grep", "-I", "-h", "-e", "CDSFL note standard v", rev, "--",
         "experimental_notes/"],
        cwd=REPO, capture_output=True, text=True, timeout=300)
    # `git grep` exits 1 when nothing matches, which is not an error here.
    if r.returncode not in (0, 1):
        raise SystemExit(f"git grep failed at {rev}: {r.stderr[-400:]}")
    out = []
    for line in r.stdout.splitlines():
        m = re.search(r"CDSFL note standard v(\d+)\.(\d+)", line)
        if m:
            out.append(("", int(m.group(1)), int(m.group(2))))
    return tuple(out)


@functools.lru_cache(maxsize=None)
def _revision_declaring(rev: str) -> frozenset[str]:
    """The set of note paths at `rev` whose foot-line declares v1.7 or later."""
    r = subprocess.run(
        ["git", "grep", "-I", "-e", "CDSFL note standard v", rev, "--",
         "experimental_notes/"],
        cwd=REPO, capture_output=True, text=True, timeout=300)
    if r.returncode not in (0, 1):
        raise SystemExit(f"git grep failed at {rev}: {r.stderr[-400:]}")
    hits: set[str] = set()
    for line in r.stdout.splitlines():
        # `<rev>:<path>:<matched line>`
        parts = line.split(":", 2)
        if len(parts) < 3:
            continue
        path, text = parts[1], parts[2]
        # `.md` ONLY, MATCHING THE LIVE SELECTOR. `_v17_notes()` globs
        # `NOTES.rglob("*.md")`; this half asked git grep for the foot-line
        # across `experimental_notes/` with NO extension filter, so any file
        # CONTAINING the string counted as a note.
        #
        # It became live on 2026-09-11, when the panel record mirror committed
        # 364 files under `experimental_notes/evidence/`. Two of them are
        # `seat_proposals.diff` -- a seat's proposed patch that happens to
        # include a note's foot-line in its diff body -- so HEAD declared 52
        # notes where the working tree declared 50, and the comparison failed in
        # a fresh clone. The 2 extra were diffs, not notes.
        #
        # This file's own docstring says "THE SELECTOR IS IMPORTED, NOT RETYPED
        # (`execute-do-not-grep`)", and it is, for the live half. The HEAD half
        # retyped the POPULATION instead of the pattern, which is the same
        # defect one level out: 2 expressions of "which files are notes", and
        # only 1 of them was the imported one.
        if not path.endswith(".md"):
            continue
        m = re.search(r"CDSFL note standard v(\d+)\.(\d+)", text)
        if m and (int(m.group(1)), int(m.group(2))) >= (1, 7):
            hits.add(path)
    return frozenset(hits)


@functools.lru_cache(maxsize=None)
def _revision_notes(rev: str) -> tuple[str, ...]:
    names = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", rev, "experimental_notes/"],
        cwd=REPO, capture_output=True, text=True, timeout=120).stdout.split()
    return tuple(n for n in names if n.endswith(".md"))


def at_revision(rev: str, recursive: bool, footline: re.Pattern) -> tuple[int, int]:
    """The same measurement against a git revision, so a past figure is checkable.

    THE FIGURE 7.2 QUOTES IS HISTORICAL. It was written at `b593500` on
    2026-09-09 22:10 and the notes tree has grown since, so running only against
    the working tree can neither confirm nor refute it. A script that cannot
    reach the revision a figure was taken at cannot back that figure.

    `footline` is accepted and its PATTERN is honoured, so a caller substituting
    the selector still steers this function -- the selector must remain the live
    one rather than a copy.
    """
    md = list(_revision_notes(rev))
    if not recursive:
        md = [n for n in md if n.count("/") == 1]
    declaring = _revision_declaring(rev)
    if footline.pattern != r"CDSFL note standard v(\d+)\.(\d+)":
        # A substituted selector cannot use the cached fast path, because the
        # cache was built with the live pattern. Fall back to reading each file.
        k = 0
        for n in md:
            t = subprocess.run(["git", "show", f"{rev}:{n}"], cwd=REPO,
                               capture_output=True, text=True, timeout=60).stdout
            m = footline.search(t)
            if m and (int(m.group(1)), int(m.group(2))) >= (1, 7):
                k += 1
        return k, len(md)
    return sum(1 for n in md if n in declaring), len(md)


def main() -> int:
    guard = _selector()
    live = list(guard._v17_notes())
    print(f"the LIVE selector `_v17_notes` returns {len(live)} note(s)\n")

    pops = populations()
    for name, paths in pops.items():
        k = len(declaring(paths, guard.FOOTLINE))
        print(f"POPULATION: {name}")
        report("notes reached by the foot-line selector:", k, len(paths))
        print(f"      exempt by omission: {len(paths) - k}\n")

    rec = pops["experimental_notes/**/*.md (recursive)"]
    top = pops["experimental_notes/*.md (top level only)"]
    print(f"THE 2 POPULATIONS DIFFER BY {len(rec) - len(top)} FILE(S) IN SUBDIRECTORIES.")
    print("The selector was non-recursive until 2026-09-08, so those files could not "
          "fail\nthe enforcement at all — the same shape as the exemption this entry "
          "is about,\none directory level up.")

    # The reach the guard achieves is not the same question as the reach the
    # PRE-COMMIT hook achieves, and conflating them is how 7.2 was overstated
    # once already. The hook lints STAGED notes, which is a different population
    # entirely and is not measurable from a clean tree.
    print("\nSCOPE NOTE, stated rather than left implicit: this measures the reach of the "
          "SUITE-TIME\nselector only. The pre-commit guard added in 7.2 lints STAGED notes, "
          "a different\npopulation that a clean working tree cannot exhibit.")

    print("\nTHE FIGURE 7.2 QUOTES, AT THE REVISION IT WAS TAKEN:")
    for rev in ("b593500", "HEAD"):
        for recursive in (True, False):
            k, n = at_revision(rev, recursive, guard.FOOTLINE)
            which = "recursive" if recursive else "top level"
            report(f"{rev} ({which}):", k, n)
    # THE CLOSING SENTENCE IS COMPUTED, NOT TYPED. It said "is 27 of 368" as a
    # string literal, and a mutation test caught it on 2026-09-10: disabling the
    # recursive flag changed every computed figure while the literal stayed put,
    # so an assertion on that text passed against a broken script. A number typed
    # into the prose of a measurement script is the very defect the script exists
    # to prevent, one level down.
    k_rec, n_rec = at_revision("b593500", True, guard.FOOTLINE)
    k_top, n_top = at_revision("b593500", False, guard.FOOTLINE)
    print(f"  7.2 quotes 29 of 379, 7.65%, Wilson [5.4%, 10.8%]. At b593500 the RECURSIVE "
          f"population\n  is {k_rec} of {n_rec} and the top-level population is {k_top} of "
          f"{n_top}.")
    if (k_rec, n_rec) == (29, 379):
        print("  The entry's figure reproduces exactly, and its population was the recursive one.")
    else:
        print("  *** THE ENTRY'S FIGURE DOES NOT REPRODUCE — it must be revisited. ***")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
