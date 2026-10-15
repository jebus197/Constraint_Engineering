#!/usr/bin/env python3
"""Haiku's 3 roles, and the 1 guard that is switched off in exactly the wrong domain.

THE FOUNDER'S QUESTION, 2026-10-15, verbatim: *"Is it optimal that the Haiku
classifier should be restricted in all its use cases to considering purely code
based issues? Wouldn't this risk (as you have observed) rendering it redundant in
other STEM focused experiments that have nothing to do with code...? Please
suggest a fix for those areas that Haiku currently deals with within the
harness."* And: *"But you said previously Haiku had 'three roles' in the harness?
Are they not all potentially useful in non-coding/other STEM related topics
too?"*

THE FIRST HALF OF THE ANSWER CORRECTS THE PREMISE, AND THE PREMISE CAME FROM
CC1's OWN EARLIER WORDING. Haiku holds 3 live roles and only 1 of them is
domain-gated at all:

  1. the claim classifier, `bench/immune_agents.py:4967` — GATED. `llm_primary =
     (domain == "software")`. Outside software Haiku is not switched off; it is
     DEMOTED to SEMI-ACTIVE, overriding when confidence >= 0.70 and a guard
     passes. So it is restricted in AUTHORITY, never in SCOPE.
  2. the dedup assessor, `bench/cc2_manager.py:489` — NOT GATED. Runs in every
     domain.
  3. the Ouroboros librarian reader, `bench/ouroboros_cell.py:724` — NOT GATED.
     Runs in every domain.

So the redundancy worry lands on 1 role of 3, and even there Haiku still acts:
run 1 made 22 classifications in a `mathematics` domain.

A DOCUMENTATION DEFECT FOUND ON THE WAY. `bench/cc2_manager.py:15` still lists
"Citation Verifier — Haiku", while line 360 of the same file records that role as
"Upgraded from Haiku" and dispatches Sonnet. The docstring names 3 Haiku roles
where the code runs 2 plus a Sonnet one. Stale documentation, equal standing to
stale code.

THE SECOND HALF IS THE DEFECT, AND IT RUNS THE OPPOSITE WAY TO THE WORRY. Two
guards protect a claim from being moved to a verifier that cannot ground it, and
each is wired to fire in only 1 domain:

    math_guard         = regex is MATHEMATICAL and NOT llm_primary
    code_path_protected = llm_primary and regex is CODE and llm is not CODE

Read together: in SOFTWARE, code claims are protected and mathematical ones are
not. Outside software, mathematical claims are protected and CODE CLAIMS ARE
NOT. The code-path guard carries a careful written rationale -- demoting a true
code claim off the CT (code-verifier) path starves the only cell that can ground
it against the source, and that caused exp41c's C0007, C0015 and C0017 to sit
UNCONFIRMED -- and that rationale is domain-independent, while its wiring is not.

AND THE EXPOSURE IS NOT HYPOTHETICAL. The 2 free runs of 2026-10-15 ran
`domain=mathematics` against a target named `prose_with_computable_listings.md`:
prose carrying real Python. Their round-0 findings include a biased variance
estimator in `round_dispersion` and a missing factor of 2 in `wilson_interval`.
Those are CODE claims arising in a non-software domain -- precisely the
population the code-path guard does not cover.

THIS SCRIPT MEASURES THE FOOTPRINT rather than arguing it, over every archived
classifier log in the live tree (sandbox harvests and worktree harvests
excluded, because a harvested copy is not a run). Every instance is printed
UNFILTERED. It dispatches nothing and costs nothing.
"""
from __future__ import annotations

import collections
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from _cli_help import answer_help                                  # noqa: E402

CODE_TYPES = {"code_behavioral", "code_structural"}
EXCLUDE = ("sandbox_harvest", "panel_worktree", "worktree_harvest")

RE_MODE = re.compile(r"LLM classifier: (PRIMARY|SEMI-ACTIVE) \(CLI Haiku")
RE_OVER = re.compile(
    r"LLM classifier OVERRIDE: (\S+) [—-] regex=(\w+) → llm=(\w+) "
    r"\(conf=([0-9.]+)")
RE_GUARD = re.compile(
    r"LLM classifier: (\S+) [—-] regex=(\w+) llm=(\w+) "
    r"\(conf=([0-9.]+), BLOCKED by ([A-Z-]+) guard")


def wilson(k: int, n: int) -> str:
    if n == 0:
        return "n=0"
    from statsmodels.stats.proportion import proportion_confint
    lo_a, hi_a = proportion_confint(k, n, alpha=0.05, method="wilson")
    import scipy.stats as st
    z = st.norm.ppf(0.975)
    p, d = k / n, 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    assert max(abs(lo_a - (centre - half)), abs(hi_a - (centre + half))) < 1e-9
    return f"{100 * k / n:.4f}%, 95% Wilson [{100 * lo_a:.4f}%, {100 * hi_a:.4f}%]"


def logs() -> list[pathlib.Path]:
    out = []
    for p in (REPO / "bench" / "logs").rglob("*"):
        if not p.is_file():
            continue
        if any(x in str(p) for x in EXCLUDE):
            continue
        try:
            if "LLM classifier" in p.read_text(errors="ignore"):
                out.append(p)
        except (OSError, UnicodeDecodeError):
            continue
    return sorted(out)


def main() -> int:
    files = logs()
    print("=" * 78)
    print("1. THE ARCHIVE")
    print("=" * 78)
    print(f"  {len(files)} log files in the live tree carry classifier lines")

    per_mode = collections.Counter()
    overrides = []          # (mode, file, id, regex_t, llm_t, conf)
    guards = collections.Counter()
    rescue_refusals = []
    # ★ MODE IS TRACKED PER SECTION, NOT PER FILE. A first version keyed the
    # mode off the whole file and dropped every file carrying both headers into
    # a MIXED bucket: that excluded 1,465 of 2,273 override lines, so the
    # measurement rested on 36% of the evidence. The runner prints the mode
    # header before each batch it classifies, so the mode in force for a line
    # is the last header seen ABOVE it. This uses all of the archive.
    for p in files:
        mode = "UNKNOWN"
        for line in p.read_text(errors="ignore").splitlines():
            m = RE_MODE.search(line)
            if m:
                mode = m.group(1)
                per_mode[mode] += 1
                continue
            m = RE_OVER.search(line)
            if m:
                overrides.append((mode, p, m.group(1), m.group(2),
                                  m.group(3), float(m.group(4))))
                continue
            m = RE_GUARD.search(line)
            if m:
                guards[(mode, m.group(5))] += 1
                if (m.group(5).startswith("MATH")
                        and m.group(3) in CODE_TYPES):
                    # ★ THE RUN IS PART OF THE KEY. A first version keyed on
                    # (finding_id, types, confidence) and called the result
                    # "distinct findings". The same finding_id recurs across
                    # many runs at different confidences, so that key counted
                    # OCCASIONS while the label claimed FINDINGS -- the same
                    # denominator error as the withdrawn "282 of 711".
                    run = (p.parent.name if p.parent.name != "logs"
                           else p.stem)
                    rescue_refusals.append(
                        (run, m.group(1), m.group(2), m.group(3)))

    print(f"  mode headers: " + ", ".join(
        f"{k}={v}" for k, v in sorted(per_mode.items())))
    print(f"  override lines parsed: {len(overrides)}")
    unattributed = sum(1 for o in overrides if o[0] == "UNKNOWN")
    print(f"  override lines with no mode header above them: {unattributed}")
    print("  guard blocks by mode:")
    for (mode, guard), n in sorted(guards.items()):
        print(f"    {mode:<12} {guard:<14} {n}")

    print()
    print("=" * 78)
    print("2. THE HOLE — A CODE CLAIM DEMOTED OFF THE CODE PATH, UNGUARDED")
    print("=" * 78)
    semi = [o for o in overrides if o[0] == "SEMI-ACTIVE"]
    prim = [o for o in overrides if o[0] == "PRIMARY"]
    hole = [o for o in semi if o[3] in CODE_TYPES and o[4] not in CODE_TYPES]
    blocked_equiv = [o for o in prim
                     if o[3] in CODE_TYPES and o[4] not in CODE_TYPES]
    print(f"  SEMI-ACTIVE (non-software) overrides: {len(semi)}")
    print(f"  PRIMARY (software) overrides:         {len(prim)}")
    print()
    # ★ DE-DUPLICATED. The same classification is written to both console.log
    # and immune_pipeline.log in a run directory, so a LINE count double-counts
    # a FINDING. Both figures are reported, and the distinct one is the claim.
    distinct_hole = {(o[2], o[3], o[4], o[5]) for o in hole}
    distinct_semi = {(o[2], o[3], o[4], o[5]) for o in semi}
    print(f"  CODE -> non-CODE demotions ALLOWED THROUGH in SEMI-ACTIVE:")
    print(f"    log lines:          {len(hole)} of {len(semi)}")
    print(f"    DISTINCT findings:  {len(distinct_hole)} of "
          f"{len(distinct_semi)}  <-- the claim")
    print(f"    {wilson(len(distinct_hole), len(distinct_semi))}")
    print(f"  the same move in PRIMARY, where the guard DOES fire and would "
          f"have refused it: {len(blocked_equiv)}")
    print(f"  code-path guard blocks recorded: "
          f"{sum(v for (m, g), v in guards.items() if g.startswith('CODE'))}")

    if hole:
        print()
        print("  EVERY UNGUARDED DEMOTION, UNFILTERED:")
        seen = set()
        for mode, p, fid, rt, lt, conf in hole:
            if (fid, rt, lt, conf) in seen:
                print(f"    - {fid:<22} (same finding again in another log of "
                      f"the same run — not counted twice)")
                continue
            seen.add((fid, rt, lt, conf))
            print(f"    - {fid:<22} {rt} -> {lt}  conf={conf:.2f}")
            print(f"      {p.relative_to(REPO)}")
    else:
        print()
        print("  THE HOLE HAS NO ARCHIVED FOOTPRINT. The asymmetry is real in "
              "the code and 0 archived runs exercised it. It is then a latent "
              "defect, not an observed one, and the fix is pre-emptive.")

    print()
    print("=" * 78)
    print("3. WHAT THE MATHEMATICAL GUARD REFUSED, FOR THE FOUNDER'S RULING")
    print("=" * 78)
    mg = sum(v for (m, g), v in guards.items() if g.startswith("MATH"))
    print(f"  mathematical-guard blocks: {mg}")
    print("  These are overrides Haiku proposed and did NOT get. The guard is")
    print("  unconditional on confidence: in a non-software domain a regex")
    print("  `mathematical` label cannot be moved at ANY confidence. Whether to")
    print("  relax it to a confidence test is the founder's call, not CC1's, so")
    print("  this script reports the population and proposes no removal.")

    print()
    print("=" * 78)
    print("4. THE SECOND HOLE — THE EXP 38 RESCUE CANNOT FIRE OUTSIDE SOFTWARE")
    print("=" * 78)
    print("  `math_guard` blocks ANY move away from a regex `mathematical`")
    print("  label outside software, at any confidence — INCLUDING the move to")
    print("  a CODE type. But the CT (code-verifier) cell CAN ground a claim")
    print("  about code, so that destination is the one the guard's own")
    print("  reasoning would permit. The classifier's stated purpose is to")
    print('  "RESCUE code bugs that the regex misroutes to math (non-code ->')
    print('  code, Exp 38)" — and that rescue is reachable in the software')
    print("  domain only. Found by executing the fix, not by reading it: a test")
    print("  written to confirm the rescue survived instead refuted it.")
    print()
    refused = list(rescue_refusals)
    occasions = {(run, fid, rt, lt) for run, fid, rt, lt in refused}
    ids = {fid for _, fid, _, _ in refused}
    runs = {run for run, _, _, _ in refused}
    print(f"  MATHEMATICAL-guard blocks whose destination was a CODE type,")
    print(f"  i.e. a rescue onto the code path refused:")
    print(f"    log lines:                      {len(refused)}")
    print(f"    distinct (run, finding) OCCASIONS: {len(occasions)}  <-- the claim")
    print(f"    distinct finding identifiers:   {len(ids)}")
    print(f"    runs affected:                  {len(runs)}")
    print(f"  of all mathematical-guard block log lines: {mg}")
    print(f"    share of maths-guard blocks that were refused rescues: "
          f"{wilson(len(refused), mg)}")
    if occasions:
        print("  EVERY REFUSED RESCUE OCCASION, UNFILTERED "
              "(run, finding, move):")
        for run, fid, rt, lt in sorted(occasions):
            print(f"    - {fid:<22} {rt} -> {lt:<16} {run}")
    print()
    print("  THE ONE-LINE FIX, NOT APPLIED, AWAITING THE FOUNDER'S RULING:")
    print("    math_guard = (regex is MATHEMATICAL and not llm_primary")
    print("                  and llm_type not in _code_types)")
    print("  It narrows a guard rather than adding one, so under the additive")
    print("  standard it needs his ruling and a named dominated property. The")
    print("  property is whether a code claim can reach the only cell that can")
    print("  ground it: today, outside software, it cannot, ever.")
    return 0


if __name__ == "__main__":
    answer_help(__doc__, __file__)
    raise SystemExit(main())
