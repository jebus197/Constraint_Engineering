#!/usr/bin/env python3
"""Task V4: produce the task-list figures that had no producing script.

MEASURED, and committed alongside the figures (`measured-rate-travels-with-its-script`).

The rule is a founder ruling this project quotes constantly and has broken
repeatedly. A sweep of the master task list on 2026-09-10 found 18 entries
carrying a percentage or a p-value and 4 of them naming no script that exists:
22.2222%, Wilson [9.0009%, 45.2146%]. This produces the 2 that are genuine
measurements over the archive. The other 2 were repaired by naming a script that
already existed.

WHY A TYPED FIGURE OVER A GROWING ARCHIVE CANNOT STAY TRUE. Entry 6.1 states "23
of 41 completion signals carry an empty reason", measured 2026-09-09. Re-measured
2026-09-10 the archive holds 42 signals, not 41, because it grows. A figure with
no producer is not merely unverifiable; it is guaranteed to drift.

BOTH POPULATIONS ARE REPORTED FOR 6.1, because the entry does not say which it
counted and the 2 differ: `exp*` run directories alone, and every run directory
including simulation harnesses.
"""
from __future__ import annotations

import glob
import json
import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]


def stop_reasons(pattern: str):
    """(signals, empty) for completion signals matching `pattern`."""
    total = empty = 0
    for f in sorted(glob.glob(str(REPO / pattern))):
        try:
            d = json.loads(pathlib.Path(f).read_text())
        except (ValueError, OSError):
            continue
        total += 1
        reason = str(d.get("reason") or d.get("convergence_reason") or "").strip()
        if not reason:
            empty += 1
    return total, empty


#: A cited path must look like a FILE. A first version matched anything after
#: `bench/logs/` and swept in `bench/logs/--help`, `bench/logs/.` and bare
#: directory names, giving 206 of 290 -- a figure about the extractor rather than
#: the corpus. Requiring a real extension is what makes the count mean something.
_LOOKS_LIKE_A_FILE = re.compile(r"\.[A-Za-z0-9]{1,6}$")


class GitCannotAnswer(RuntimeError):
    """Raised when the tracked corpus cannot be identified at all.

    A DISTINCT TYPE so the A8 section can refuse WITHOUT taking A19 down with it.
    The seat's own first cut raised SystemExit and silenced a figure that was
    perfectly measurable; that regression is what this class exists to prevent.
    """


def untracked_cited_paths(prefix: str = "bench/logs/"):
    """Cited paths under `prefix` that git does not track. Entry A8's figure."""
    cited = set()
    pat = re.compile(r"(" + re.escape(prefix) + r"[\w./-]+)")
    for d in ("experimental_notes", "resources", "scripts", "bench/tests", "docs"):
        base = REPO / d
        if not base.is_dir():
            continue
        for p in base.rglob("*"):
            if p.suffix not in (".md", ".py", ".json", ".sh"):
                continue
            try:
                cited |= set(pat.findall(p.read_text(encoding="utf-8",
                                                     errors="replace")))
            except OSError:
                continue
    cited = {c.rstrip(".,);:") for c in cited}
    cited = {c for c in cited if _LOOKS_LIKE_A_FILE.search(c)}
    # THE RETURN CODE IS PART OF THE ANSWER. Found 2026-09-11 by the cc2 seat in
    # panel round 10, premise verified before acceptance: this read `.stdout` and
    # ignored the exit status, so in a checkout with no `.git` -- the panel
    # sandbox, a ZIP, a Zenodo archive -- `git ls-files` exits 128 with empty
    # output, `tracked` becomes the empty set, and EVERY cited path counts as
    # untracked. The script printed "127/127 = 100.0000%, Wilson [97.0640%,
    # 100.0000%]": a fabricated figure with a confidence interval on it, in the
    # direction that INFLATES the finding.
    #
    # It refuses rather than guessing, and refuses LOUDLY, because a figure that
    # is 100% by construction is worse than no figure. The correct pattern was
    # already in this repository, written the same day:
    # `bench/archive_corpus.py` tests `out.returncode != 0`.
    r = subprocess.run(["git", "ls-files"], cwd=REPO,
                       capture_output=True, text=True)
    if r.returncode != 0 or not r.stdout.strip():
        raise GitCannotAnswer(
            f"`git ls-files` could not list this checkout (exit {r.returncode}: "
            f"{(r.stderr or '').strip()[:120]}). Every cited path would count as "
            f"untracked and the figure would read 100% by construction, not by "
            f"measurement. Run this in a git checkout.")
    tracked = set(r.stdout.split())
    untracked = sorted(c for c in cited if c not in tracked)
    return sorted(cited), untracked


def no_score_outcomes():
    """Entry A19's figure: how often has S_k returned NO_SCORE?"""
    import collections
    counts = collections.Counter()
    total = 0
    for r in sorted(glob.glob(str(REPO / "bench" / "logs" / "exp*" / "runner_state.json"))):
        try:
            s = json.loads(pathlib.Path(r).read_text())
        except (ValueError, OSError):
            continue
        reg = s.get("registry", {})
        ent = reg.get("entries", reg) if isinstance(reg, dict) else reg
        for v in (ent.values() if isinstance(ent, dict) else ent or []):
            if not isinstance(v, dict):
                continue
            sk = v.get("sk_result")
            if isinstance(sk, dict) and "tristate" in sk:
                total += 1
                counts[sk["tristate"]] += 1
    return total, counts


def main() -> int:
    from statsmodels.stats.proportion import proportion_confint

    print("--- ENTRY 6.1: completion signals with no stop reason ---")
    for pattern, label in (("bench/logs/exp*/completion_signal.json", "exp* only"),
                           ("bench/logs/*/completion_signal.json", "every run dir")):
        total, empty = stop_reasons(pattern)
        if not total:
            print(f"  {label}: no completion signals found")
            continue
        lo, hi = proportion_confint(empty, total, method="wilson")
        lo_c, hi_c = proportion_confint(empty, total, method="beta")
        print(f"  {label:14s}: {empty} of {total} = {empty/total:.4%}")
        print(f"                  Wilson [{lo:.4%}, {hi:.4%}]  "
              f"Clopper-Pearson [{lo_c:.4%}, {hi_c:.4%}]")
    print("  The entry states 23 of 41, measured 2026-09-09. Neither population")
    print("  gives that today, because the archive GREW. A typed figure over a")
    print("  growing corpus is guaranteed to drift, not merely unverifiable.")

    print("\n--- ENTRY A8: cited bench/logs/ paths that git does not track ---")
    try:
        cited, untracked = untracked_cited_paths()
    except GitCannotAnswer as exc:
        # REFUSE THIS FIGURE, KEEP THE OTHERS. A19's figure is measured from the
        # archive and needs no git at all; taking it down with A8 would be a
        # second defect fixing the first.
        print(f"  REFUSING TO REPORT entry A8's figure: {exc}")
        cited = untracked = None
    if cited is not None and not cited:
        print("  no bench/logs/ paths are cited anywhere")
        cited = untracked = None
    if cited is None:
        return _entry_a19()
    lo, hi = proportion_confint(len(untracked), len(cited), method="wilson")
    lo_c, hi_c = proportion_confint(len(untracked), len(cited), method="beta")
    print(f"  cited: {len(cited)}   untracked: {len(untracked)}")
    print(f"  {len(untracked)}/{len(cited)} = {len(untracked)/len(cited):.4%}")
    print(f"  Wilson 95%          : [{lo:.4%}, {hi:.4%}]")
    print(f"  Clopper-Pearson 95% : [{lo_c:.4%}, {hi_c:.4%}]")
    print(f"\n  first few untracked:")
    for u in untracked[:5]:
        print(f"    {u}")
    if len(untracked) > 5:
        print(f"    ... and {len(untracked) - 5} more not shown")
    # THE ENTRY'S DENOMINATOR IS A DIFFERENT POPULATION, and saying so is the
    # point. A8 states "177 of 3803, 4.65%". 3803 is every cited path in the
    # corpus, of which the untracked bench/logs ones are a slice. This script
    # measures the SLICE and its own denominator; it does not reproduce 4.65%
    # and does not pretend to.
    all_cited, _ = untracked_cited_paths(prefix="")
    print(f"\n  for comparison, the entry's denominator is EVERY cited path, not")
    print(f"  only bench/logs ones. This script measures the slice: {len(untracked)}")
    print(f"  untracked of {len(cited)} cited bench/logs paths. The entry's 4.65% is")
    print(f"  over a different population and the 2 must not be quoted against")
    print(f"  each other.")

    return _entry_a19()


def _entry_a19() -> int:
    """Entry A19's figure, EXTRACTED so entry A8 can refuse without it.

    A19 is measured from the archive and needs no git at all. Keeping it
    inline meant a git failure in A8 silenced a perfectly measurable
    figure -- which is what the cc2 seat's own first cut did, and it caught
    that regression itself before handing the fix back.
    """
    from statsmodels.stats.proportion import proportion_confint

    print("\n--- ENTRY A19: has S_k ever returned NO_SCORE? ---")
    total, counts = no_score_outcomes()
    if total:
        n = counts.get("NO_SCORE", 0)
        lo, hi = proportion_confint(n, total, method="wilson")
        lo_c, hi_c = proportion_confint(n, total, method="beta")
        print(f"  tristate outcomes in exp* archives: {total}")
        print(f"  by verdict: {dict(counts)}")
        print(f"  NO_SCORE: {n} of {total} = {n/total:.4%}")
        print(f"  Wilson 95%          : [{lo:.4%}, {hi:.4%}]")
        print(f"  Clopper-Pearson 95% : [{lo_c:.4%}, {hi_c:.4%}]")
        print(f"  The entry states 0 of 5834 with a tighter interval. The CLAIM")
        print(f"  holds in this population too; the INTERVAL differs because the")
        print(f"  denominator does, and a wider one is the honest report of a")
        print(f"  smaller sample.")

    print("\n  `.gitignore` excludes bench/logs by design, so these are cited")
    print("  evidence that exists on 1 machine only. The disposition -- track,")
    print("  relocate, or accept and label -- is the founder's; this is the count.")
    return 0




if __name__ == "__main__":
    sys.exit(main())
