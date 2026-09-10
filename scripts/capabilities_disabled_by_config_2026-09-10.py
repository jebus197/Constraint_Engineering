#!/usr/bin/env python3
"""Task 3.3: what else is switched OFF by configuration rather than by code?

MEASURED, and committed alongside the figures (`measured-rate-travels-with-its-script`).

WHY. The exp56 case -- `routing_enabled: false` and
`post_convergence_sweep_rounds: 0` -- was found by accident, and nothing had ever
looked for siblings. A capability that exists, is tested, and is switched off in a
config file is invisible to the test suite: every test passes and the feature
never runs. That is the additive standard's own failure mode, hiding in data
rather than in code.

WHAT COUNTS AS DISABLED, and the definition is deliberately narrow so the output
is actionable rather than a list of every false in the tree:

  * a boolean field set to `false` whose name reads as an ENABLEMENT
    (`*_enabled`, `enable_*`, `use_*`, `*_on`), or
  * a numeric field set to 0 whose name reads as an ALLOWANCE
    (`*_rounds`, `*_attempts`, `*_retries`, `max_*`, `*_limit`)

and, in both cases, ONLY where the runner actually READS that field. A field
nothing reads is a different defect -- an unwired addition -- and is reported
separately rather than conflated with this one.
"""
from __future__ import annotations

import ast
import json
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
#: EVERY module a run passes through, not just the main runner. The first version
#: of this script read only `reference_runner_v3.py` and would have reported 12
#: fields as unread when they may be read by the orchestrator or by runner_core.
#: A claim that nothing reads a field is exactly the kind that must be checked
#: against the whole surface before it is believed.
def runner_sources() -> list[pathlib.Path]:
    out = []
    for p in sorted((REPO / "bench").rglob("*.py")):
        if "logs" in p.parts or "__pycache__" in p.parts or "tests" in p.parts:
            continue
        out.append(p)
    return out

# THE `$` ANCHORED THE WHOLE ALTERNATION, which made `^enable_` mean "the field
# is literally the string 'enable_'". So the first version of this sweep was
# blind to every `enable_*` and `use_*` field, and to every `max_*` allowance --
# exactly the fields most likely to name a capability. Caught by this script's
# own test asserting `enable_tools` matches, before any figure was believed.
# Suffixes and prefixes are now separate patterns rather than one alternation
# wearing a single anchor.
ENABLEMENT = re.compile(r"(_enabled$|_on$|^enable_|^use_|^with_)", re.I)
ALLOWANCE = re.compile(r"(_rounds$|_attempts$|_retries$|_limit$|_threshold$|^max_)", re.I)


def config_files() -> list[pathlib.Path]:
    out = []
    for d in ("bench/exp56_configs", "bench/configs", "bench/cdsfl_registry"):
        p = REPO / d
        if p.is_dir():
            out.extend(sorted(p.rglob("*.json")))
    return out


def read_fields(src: str) -> set[str]:
    """Field names the runner actually reads, by AST rather than by grep.

    A grep for the name matches its own definition, a comment, and a docstring.
    Only a subscript or an attribute access is a READ.
    """
    names: set[str] = set()
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return names
    for n in ast.walk(tree):
        if isinstance(n, ast.Subscript) and isinstance(n.slice, ast.Constant) \
                and isinstance(n.slice.value, str):
            names.add(n.slice.value)
        elif isinstance(n, ast.Attribute):
            names.add(n.attr)
        elif isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) \
                and n.func.attr == "get" and n.args \
                and isinstance(n.args[0], ast.Constant) \
                and isinstance(n.args[0].value, str):
            names.add(n.args[0].value)
    return names


def explanation(data: dict, leaf: str) -> str:
    """The sibling `_<field>_note` that explains an off-switch, if one exists.

    ADDED 2026-09-10 17:35 BST, AFTER THIS SWEEP REPORTED 9 FINDINGS THAT WERE
    ALL DOCUMENTED DECISIONS. Every exp56 arm carries a `_sk_note`,
    `_merge_arbitration_note`, `_immune_memory_note` and `_apply_fixes_back_note`
    IN THE SAME FILE, each giving a measured reason. The first version read the
    values and not the notes beside them, and reported deliberate experimental
    controls as undiscovered off-switches -- including `sk_enabled`, whose note
    records that the gate "has never rejected anything -- 0 of 3816, Wilson
    [0.0000, 0.0010]".

    That is `feedback_check_the_record_before_declaring_a_gap` violated by an
    instrument built to find gaps: the record was not merely in the repository,
    it was 3 lines away in the file being read.
    """
    base = leaf.rstrip("_")
    for key in (f"_{base}_note", f"_{base.replace('_enabled','')}_note",
                f"_{base.split('_')[0]}_note"):
        v = data.get(key)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return ""


def walk(obj, prefix=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from walk(v, f"{prefix}.{k}" if prefix else k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from walk(v, f"{prefix}[{i}]")
    else:
        yield prefix, obj


def main() -> int:
    srcs = runner_sources()
    read = set()
    for f in srcs:
        try:
            read |= read_fields(f.read_text(encoding="utf-8", errors="replace"))
        except OSError:
            continue
    disabled, unread = [], []
    files = config_files()
    for f in files:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        for path, val in walk(data):
            leaf = path.split(".")[-1].split("[")[0]
            off = (val is False and ENABLEMENT.search(leaf)) or \
                  (isinstance(val, int) and not isinstance(val, bool)
                   and val == 0 and ALLOWANCE.search(leaf))
            if not off:
                continue
            rel = str(f.relative_to(REPO))
            why = explanation(data, leaf)
            (disabled if leaf in read else unread).append((rel, path, val, why))

    print(f"config files scanned: {len(files)}")
    print(f"runner modules scanned: {len(srcs)}")
    print(f"fields those modules READ, by AST: {len(read)}\n")

    _SHOW = 40
    print(f"CAPABILITIES SWITCHED OFF IN CONFIG THAT THE RUNNER READS "
          f"({len(disabled)}):")
    for rel, path, val, why in disabled[:_SHOW]:
        tag = "DOCUMENTED" if why else "*** UNEXPLAINED ***"
        print(f"    {rel}\n        {path} = {val!r}   [{tag}]")
        if why:
            print(f"          reason on file: {why[:150]}")
    if len(disabled) > _SHOW:
        print(f"    ... {len(disabled) - _SHOW} more not shown")
    if not disabled:
        print("    none")

    print(f"\nSET TO OFF BUT THE RUNNER NEVER READS THE FIELD ({len(unread)}) — "
          f"a DIFFERENT defect, an unwired addition, not this task's:")
    for rel, path, val, why in unread[:_SHOW]:
        tag = "DOCUMENTED" if why else "*** UNEXPLAINED ***"
        print(f"    {rel}\n        {path} = {val!r}   [{tag}]")
    if len(unread) > _SHOW:
        print(f"    ... {len(unread) - _SHOW} more not shown")
    if not unread:
        print("    none")

    allsw = disabled + unread
    unexplained = [x for x in allsw if not x[3]]
    print(f"\n  THE FIGURE THAT MATTERS: off-switches with NO recorded reason in "
          f"their own file: {len(unexplained)} of {len(allsw)}")
    for rel, path, val, _ in unexplained[:_SHOW]:
        print(f"      {rel}: {path} = {val!r}")
    if not unexplained:
        print("      none — every off-switch found carries a sibling _<field>_note "
              "giving a measured reason")
    n = len(disabled) + len(unread)
    if n:
        from statsmodels.stats.proportion import proportion_confint
        from scipy import stats as sps
        import mpmath as mp
        k = len(disabled)
        w = proportion_confint(k, n, method="wilson")
        c = proportion_confint(k, n, method="beta")
        mp.mp.dps = 30
        z = mp.mpf(str(sps.norm.ppf(0.975)))
        p, N = mp.mpf(k) / n, mp.mpf(n)
        cc = (p + z**2 / (2 * N)) / (1 + z**2 / N)
        h = (z / (1 + z**2 / N)) * mp.sqrt(p * (1 - p) / N + z**2 / (4 * N**2))
        print(f"\n  of {n} off-switches found, {k} are READ by the runner = {k / n:.4%}")
        print(f"      Wilson [{w[0]:.4%}, {w[1]:.4%}] statsmodels | "
              f"[{float(cc - h):.4%}, {float(cc + h):.4%}] mpmath | "
              f"agree to 1e-9: {abs(w[0] - float(cc - h)) < 1e-9}")
        print(f"      Clopper-Pearson [{c[0]:.4%}, {c[1]:.4%}]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
