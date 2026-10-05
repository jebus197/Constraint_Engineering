# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'fingerprint_ladder_review_2026-10-05', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: cdb8ab28d1f5b5fda0ce0794631c51902d4a5dfc82a343dffa88bab487cae43f
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Which config facilities are ARMED in a real experiment config but INERT in
the simulated path (`bench/tools/run_simulated_experiment.py`)?

READ-ONLY. Writes nothing to disk; prints a table.

THE QUESTION HAS A TRAP IN ITS WORDING, and this script is built to expose it
rather than answer past it.

  1. THERE ARE NO EXPERIMENT CONFIGS UNDER `configs/`. That directory holds
     DOMAIN-EXPERT PROMPT configs -- markdown files and a README, 0 JSON. The
     real experiment configs are `bench/exp*_configs/*.json`. This script
     globs BOTH and prints what it found in each, so the count stands on
     execution rather than on the premise.

  2. THE SIMULATED RUNNER DOES NOT LOAD A CONFIG FILE AT ALL. It has no
     `--config`; it CONSTRUCTS `R.RunnerConfig(...)` as an inline literal and
     hands it to `R.run_experiment` -- the SAME `reference_runner_v3` the paid
     runs use. So "read by the simulated runner" splits in two, and conflating
     them is how a false gap gets reported:

       SET   -- does the sim harness's inline literal pass the key?
       READ  -- does the code the sim run EXECUTES consult the key?

     READ is the same answer as for the real runner, always, because it is the
     same module. The real gap is a key that is truthy in a shipped config,
     READ by the shared runner, but NOT SET by the sim literal -- it then
     silently takes its `RunnerConfig` dataclass default, which for the flags
     in question is False. Armed on paid runs, dark in rehearsal.

So the reported class is the CONJUNCTION:
     truthy in >=1 shipped config
  AND read by reference_runner_v3 (in any of the 4 forms the language offers)
  AND not set by the sim harness literal
  AND its dataclass default is falsy

Readers are resolved in ALL FOUR FORMS, because a scanner that resolves one
reports a false zero for the rest -- the lesson already paid for in
`scripts/config_fields_are_read_2026-09-11.py`:
    cfg.key            attribute load
    getattr(c, "key")  the same read, written as a string
    d["key"]           subscript, which is how nested blocks are consulted
    d.get("key")
"""
from __future__ import annotations

import argparse
import ast
import json
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]

SIM = REPO / "bench" / "tools" / "run_simulated_experiment.py"
REAL = REPO / "bench" / "reference_runner_v3.py"
LAUNCHER = REPO / "bench" / "launcher_core.py"

#: Copies of the tree that are not the tree. `bench/logs/*/sandbox_harvest/`
#: holds verbatim snapshots of runner files taken during review runs, and
#: `.claude/worktrees/` holds agent checkouts -- counting either would report a
#: reader that is a photograph of a reader.
EXCLUDE_PARTS = {
    ".claude", ".scratch", ".mutants", ".mypy_cache", ".pytest_cache",
    ".ruff_cache", "logs", "experimental_notes", "node_modules", "tests",
}


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """The argument surface, built and parsed FIRST in main()."""
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--min-truthy", type=int, default=1,
                    help="only report keys truthy in at least N configs "
                         "(default: 1)")
    ap.add_argument("--key", action="append", default=[],
                    help="audit a specific key in full detail; repeatable. "
                         "Used to CONFIRM or REFUTE a prior count.")
    ap.add_argument("--all-keys", action="store_true",
                    help="print the full per-key table, not just the gap class")
    return ap.parse_args(argv)


# ---------------------------------------------------------------- config side

def config_files() -> dict[str, list[pathlib.Path]]:
    """Every candidate config, grouped by the directory the question named."""
    return {
        "configs/ (the directory the task named)":
            sorted(p for p in (REPO / "configs").rglob("*")
                   if p.is_file() and p.suffix in (".json", ".toml", ".yaml",
                                                   ".yml", ".md")),
        "bench/exp*_configs/*.json (the real experiment configs)":
            sorted(REPO.glob("bench/exp*_configs/*.json")),
    }


def flatten(obj, prefix: str = ""):
    """Yield (dotted_key, leaf_key, value) for every scalar leaf."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            dotted = f"{prefix}.{k}" if prefix else k
            if isinstance(v, (dict, list)):
                yield from flatten(v, dotted)
            else:
                yield dotted, k, v
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from flatten(v, f"{prefix}[{i}]")


def census(paths: list[pathlib.Path]):
    """key -> {"truthy": n, "falsy": n, "values": {...}, "files": [...]}"""
    out: dict[str, dict] = {}
    for p in paths:
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        for dotted, leaf, val in flatten(data):
            # ANY `_`-prefixed component, not just the leaf. Measured: exp50/51
            # carry `_redesign_2026_09_10.deliberately_unchanged.
            # immune_memory_enabled`, whose VALUE IS A PARAGRAPH OF PROSE
            # explaining why the real flag is left True. A leaf-only filter
            # counted those 2 paragraphs as 2 more configs arming the facility
            # and inflated the count from 13 to 15.
            if any(part.startswith("_") for part in dotted.split(".")):
                continue  # `_comment`, `_note`, `_redesign_*` -- prose
            if not isinstance(val, (bool, str)):
                continue
            rec = out.setdefault(leaf, {"truthy": 0, "falsy": 0,
                                        "values": {}, "files": []})
            rec["values"][str(val)] = rec["values"].get(str(val), 0) + 1
            if val is True or (isinstance(val, str) and val != ""):
                rec["truthy"] += 1
                rec["files"].append(p.name)
            else:
                rec["falsy"] += 1
    return out


# ---------------------------------------------------------------- reader side

def production_sources():
    for base in ("bench", "scripts", "hooks", "explorer"):
        root = REPO / base
        if not root.is_dir():
            continue
        for p in sorted(root.rglob("*.py")):
            if EXCLUDE_PARTS & set(p.relative_to(REPO).parts):
                continue
            yield p


def reader_patterns(key: str) -> re.Pattern:
    k = re.escape(key)
    return re.compile(
        rf"(?:\.{k}\b)"                             # cfg.key
        rf"|(?:getattr\s*\([^()]*?[\"']{k}[\"'])"   # getattr(cfg, "key")
        rf"|(?:\[\s*[\"']{k}[\"']\s*\])"            # d["key"]
        rf"|(?:\.get\s*\(\s*[\"']{k}[\"'])"         # d.get("key")
    )


def readers_of(key: str, sources: list[pathlib.Path]) -> list[str]:
    pat = reader_patterns(key)
    hits = []
    for p in sources:
        try:
            txt = p.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        for i, line in enumerate(txt.splitlines(), 1):
            s = line.strip()
            if s.startswith("#"):
                continue  # a comment naming a key is not a read
            if pat.search(line):
                hits.append(f"{p.relative_to(REPO)}:{i}")
    return hits


# ------------------------------------------------- what the sim literal SETS

def sim_set_keys() -> dict[str, str]:
    """Keywords passed to `R.RunnerConfig(...)` inside the sim harness.

    AST, not grep: the call spans ~130 lines of interleaved commentary, and a
    line-based scan cannot tell a keyword argument from a key NAMED in the
    prose beside it. This file's comments mention more flags than it sets.
    """
    tree = ast.parse(SIM.read_text(encoding="utf-8"))
    found: dict[str, str] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        f = node.func
        name = (f.attr if isinstance(f, ast.Attribute)
                else getattr(f, "id", ""))
        if name not in ("RunnerConfig", "ExperimentConfig", "ModelConfig"):
            continue
        for kw in node.keywords:
            if kw.arg:
                found[kw.arg] = ast.unparse(kw.value)
    return found


def runner_config_defaults() -> dict[str, str]:
    """`RunnerConfig` field defaults, by AST, so nothing is imported."""
    tree = ast.parse(REAL.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "RunnerConfig":
            out = {}
            for stmt in node.body:
                if isinstance(stmt, ast.AnnAssign) and isinstance(
                        stmt.target, ast.Name):
                    out[stmt.target.id] = (ast.unparse(stmt.value)
                                           if stmt.value else "<required>")
            return out
    return {}


def main() -> int:
    args = _parse_args()

    groups = config_files()
    print("=" * 78)
    print("STEP 0 -- WHERE THE CONFIGS ACTUALLY ARE")
    print("=" * 78)
    real_configs: list[pathlib.Path] = []
    for label, paths in groups.items():
        njson = [p for p in paths if p.suffix == ".json"]
        print(f"  {label}")
        print(f"      {len(paths)} file(s), of which {len(njson)} are .json")
        if paths and not njson:
            for p in paths:
                print(f"        - {p.relative_to(REPO)}  (not a config schema)")
        real_configs.extend(njson)
    print(f"\n  TOTAL experiment config JSONs audited: {len(real_configs)}")

    keys = census(real_configs)
    sources = list(production_sources())
    sets = sim_set_keys()
    defaults = runner_config_defaults()
    print(f"  bool/str keys found across them: {len(keys)}")
    print(f"  production .py files scanned for readers: {len(sources)}")
    print(f"  keys SET by the sim harness literal (AST): {len(sets)}")

    rows = []
    for key, rec in sorted(keys.items()):
        if rec["truthy"] < args.min_truthy:
            continue
        r_real = readers_of(key, [REAL, LAUNCHER])
        r_any = readers_of(key, sources)
        r_sim = readers_of(key, [SIM])
        rows.append({
            "key": key, "truthy": rec["truthy"], "falsy": rec["falsy"],
            "real": r_real, "any": r_any, "sim_reads": r_sim,
            "sim_sets": sets.get(key), "default": defaults.get(key, "-"),
            "values": rec["values"],
        })

    def falsy_default(d):
        return d in ("False", "''", '""', "0", "None", "0.0")

    gaps = [r for r in rows
            if r["real"] and r["sim_sets"] is None
            and falsy_default(r["default"])]

    print()
    print("=" * 78)
    print("STEP 1 -- THE GAP CLASS: truthy in a shipped config, READ by the")
    print("          shared runner, NOT SET by the sim literal, falsy default")
    print("=" * 78)
    print(f"{'key':<40} {'T':>3} {'F':>3} {'default':>9}  first real reader")
    print("-" * 78)
    for r in sorted(gaps, key=lambda x: -x["truthy"]):
        print(f"{r['key']:<40} {r['truthy']:>3} {r['falsy']:>3} "
              f"{r['default']:>9}  {r['real'][0]}")
    print(f"\n  {len(gaps)} key(s) in the gap class.")

    print()
    print("=" * 78)
    print("STEP 2 -- burst_mode")
    print("=" * 78)
    bm = keys.get("burst_mode")
    print(f"  sim harness sets burst_mode = {sets.get('burst_mode')} "
          f"(AST of the RunnerConfig literal)")
    print(f"  RunnerConfig default        = {defaults.get('burst_mode')}")
    if bm:
        print(f"  shipped configs setting it  = "
              f"{bm['truthy'] + bm['falsy']} of {len(real_configs)}")
        for v, n in sorted(bm["values"].items(), key=lambda x: -x[1]):
            print(f"        {v!r:<12} in {n} config(s)")
    else:
        print(f"  shipped configs setting it  = 0 of {len(real_configs)}")

    for key in args.key:
        print()
        print("=" * 78)
        print(f"STEP 3 -- AUDIT: {key}")
        print("=" * 78)
        rec = keys.get(key)
        if rec is None:
            print(f"  NOT PRESENT in any of the {len(real_configs)} configs.")
            continue
        total = rec["truthy"] + rec["falsy"]
        print(f"  truthy in {rec['truthy']} of {len(real_configs)} configs "
              f"({total} set it at all, {rec['falsy']} set it falsy)")
        print(f"  values: {rec['values']}")
        print(f"  RunnerConfig default: {defaults.get(key, '-')}")
        print(f"  SET by sim literal:   {sets.get(key)}")
        rr = readers_of(key, [REAL, LAUNCHER])
        print(f"  READ by reference_runner_v3/launcher_core "
              f"({len(rr)} site(s)):")
        for h in rr[:6]:
            print(f"        {h}")
        print(f"  READ textually in run_simulated_experiment.py: "
              f"{readers_of(key, [SIM]) or 'none'}")
        print(f"  configs arming it: {sorted(set(rec['files']))}")

    if args.all_keys:
        print()
        print("=" * 78)
        print("STEP 4 -- FULL TABLE")
        print("=" * 78)
        print(f"{'key':<38} {'T':>3} {'real?':>6} {'simset?':>8} {'default':>9}")
        print("-" * 78)
        for r in sorted(rows, key=lambda x: (-x["truthy"], x["key"])):
            print(f"{r['key']:<38} {r['truthy']:>3} "
                  f"{('YES' if r['real'] else 'no'):>6} "
                  f"{('YES' if r['sim_sets'] is not None else 'no'):>8} "
                  f"{r['default']:>9}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
