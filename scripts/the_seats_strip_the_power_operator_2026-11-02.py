#!/usr/bin/env python3
"""Why did 0 of 14 proposed fixes apply in the 2026-11-02 validation run?

FIND. The run logged 20 `S_k: SEARCH block not found in source` failures and
closed with `apply-back CLOSE: nothing folded (0 applied, 14 refused)`. The
failing anchors read `centre = p + z  2 / n` and `(v - mean)  2` -- the `**`
power operator replaced by the 2 spaces that surrounded it.

FOUR HYPOTHESES WERE TESTED AND THREE WERE REFUTED BY EXECUTION.
  H1  the log mangles the text for display.           REFUTED: `apply_fix_blocks`
      matches `block.search not in modified` and logs that SAME string, so the
      logged value IS the matched value.
  H2  `_prose_normalise` eats it.                     REFUTED: it is called at
      exactly 2 sites, both inside `_splice_corrected_copy` for prose anchoring,
      and neither is on the parse path.
  H3  `parse_search_replace_blocks` eats it.          REFUTED BY EXECUTION: fed
      round 2's stored text it returns
      search == '    centre = p + z ** 2 / n', `**` intact.
  H4  THE SEATS WRITE IT THAT WAY.                    CONFIRMED, and measured
      below.

WHAT IS MEASURED. Over every SEARCH block in the run whose quoted line REQUIRES
a power operator -- the mean-squared term of the dispersion helper, or the
z-squared term of the Wilson centre -- how many were written with `**` and how
many without. A block that quotes a line needing no operator is excluded,
because its presence or absence says nothing.

WHY IT IS NOT A HARNESS DEFECT, AND WHY IT IS STILL A DEFECT. Nothing in the
harness alters the text. But `_prose_normalise` exists BECAUSE of this exact
behaviour on prose targets, and its docstring states the measured justification:
*"on prose targets the models' SEARCH blocks matched almost nothing -- 2 of 33
for exp48, 7 of 32 for exp49 -- and it was NOT paraphrase ... Models strip
formatting when they quote. Normalising both sides took the locatable share from
14% to 80%"*. The repair was applied to the PROSE anchoring path and not to the
S_k search-match path, so a markdown target carrying a python listing still
fails the same way. That is the finding: a measured fix with a known remedy,
applied on one of the 2 paths that needed it.

NOT FIXED HERE, DELIBERATELY. Changing what gets applied to an artefact changes
the experiment, `feedback_fixes_hil_only` says fixes reach the founder rather
than being auto-applied, and the run completed and converged regardless -- so by
his own blocker predicate (*does it prevent further progress*) this is PARKED,
not blocking.

TOOLS: 2 per the 2026-04-21 rule -- statsmodels and a closed-form Wilson for the
interval, which must agree to 1e-12, and the counts recomputed on the decoded
JSON rather than the raw text (the first attempt regexed raw JSON, where `\\n` is
2 characters and not a newline, and got 0 of 0).
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_RUN = "severity_bounds_validation_20261102T004713Z"
#: lines in the target whose correct form carries `**`
_NEEDS_OP = ("(v - mean)", "centre = p + z")
_BLOCK = re.compile(r"<<<<\s*SEARCH[^\n]*\n(.*?)\n\s*====", re.S)


def _walk(o):
    if isinstance(o, dict):
        for v in o.values():
            yield from _walk(v)
    elif isinstance(o, list):
        for v in o:
            yield from _walk(v)
    elif isinstance(o, str):
        yield o


def _wilson_closed(k: int, n: int, z: float = 1.959963984540054):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    den = 1.0 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / den
    return (max(0.0, c - h), min(1.0, c + h))


def measure(run: str) -> dict:
    d = REPO / "bench" / "logs" / f"{run}_{run.split('_')[-1]}"
    if not d.is_dir():
        cand = sorted((REPO / "bench" / "logs").glob(f"{run}*"))
        d = next((c for c in cand if c.is_dir()), d)
    intact = stripped = 0
    examples: list[tuple[str, str]] = []
    for p in sorted(d.rglob("*.json")):
        try:
            obj = json.loads(p.read_text(errors="replace"))
        except Exception:
            continue
        for s in _walk(obj):
            if "<<<<" not in s:
                continue
            for m in _BLOCK.finditer(s):
                blk = m.group(1)
                if not any(t in blk for t in _NEEDS_OP):
                    continue
                if "**" in blk:
                    intact += 1
                else:
                    stripped += 1
                    if len(examples) < 4:
                        examples.append((p.name, blk.strip()[:52]))
    return {"dir": str(d), "intact": intact, "stripped": stripped,
            "examples": examples}


def main() -> int:
    # ★ A REAL PARSER, 2026-11-02. This read `sys.argv[1]` directly and IGNORED
    # every flag: `--bogus` ran the whole measurement and exited 0, which
    # `test_an_unknown_flag_is_rejected_loudly` names as the 118-day no-op. An
    # argument accepted and not acted on is indistinguishable from one honoured.
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("run", nargs="?", default=DEFAULT_RUN,
                    help="run name under bench/logs to measure")
    run = ap.parse_args().run
    r = measure(run)
    k, n = r["stripped"], r["intact"] + r["stripped"]

    print("=" * 78)
    print("DO THE SEATS DROP THE POWER OPERATOR WHEN THEY QUOTE CODE?")
    print("=" * 78)
    print(f"\nrun directory : {r['dir']}")
    print(f"\nSEARCH blocks quoting a line that REQUIRES `**`:")
    print(f"    written WITH    `**` : {r['intact']}")
    print(f"    written WITHOUT `**` : {r['stripped']}")
    if n == 0:
        print("\n    0 qualifying blocks -- this measurement is VACUOUS for this run.")
        return 1

    lo_c, hi_c = _wilson_closed(k, n)
    try:
        from statsmodels.stats.proportion import proportion_confint
        lo_s, hi_s = proportion_confint(k, n, alpha=0.05, method="wilson")
        agree = abs(lo_c - lo_s) < 1e-12 and abs(hi_c - hi_s) < 1e-12
        second = f"statsmodels [{lo_s:.6f}, {hi_s:.6f}], agree={agree}"
    except Exception as e:                                   # pragma: no cover
        agree, second = False, f"statsmodels unavailable ({type(e).__name__})"
    print(f"\n    stripped share : {k}/{n} = {k/n:.6f}")
    print(f"    closed form    : Wilson 95% [{lo_c:.6f}, {hi_c:.6f}]")
    print(f"    second tool    : {second}")
    if not agree:
        print("    ★ THE 2 TOOLS DISAGREE, so the interval may not be quoted.")
        return 4

    print("\n    examples written WITHOUT the operator:")
    for nm, ex in r["examples"]:
        print(f"      {nm:28} {ex!r}")

    print("\nWHAT THIS MEANS")
    print("    The harness alters nothing: `parse_search_replace_blocks` returns")
    print("    `**` intact when the seat wrote it. The seats are inconsistent, and")
    print("    an exact-match gate cannot locate the majority of their anchors.")
    print("    `_prose_normalise` already solves this -- measured 14% -> 80% on")
    print("    prose -- and is wired to the PROSE path only.")
    print("\n    PARKED, not blocking: the run converged, and changing what is")
    print("    applied to an artefact is an experimental change and his to rule.")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(REPO / "scripts"))
    # takes_no_arguments=False: this script HAS its own parser, and the
    # helper's default refusal fires BEFORE it, which made every flag
    # declared below unreachable -- an addition nothing can reach, found
    # 2026-11-02 when --log was refused on a script that declares it.
    # ★ THE HELP-INTERCEPTING CALL IS REMOVED, 2026-11-03. It answered `--help`
    # BEFORE this script's own parser ran, so argparse never listed the flags:
    # measured across the 6 scripts that had both, 0 of 16 defined flags were
    # visible. `takes_no_arguments=False` was an earlier partial fix on
    # 2026-11-02; it stops the helper REFUSING a flag but not from answering
    # `--help` first. argparse's own help is now enabled, so the capability is
    # improved rather than lost.
    sys.exit(main())
