#!/usr/bin/env python3
"""Only 1 channel awaits his ruling, not 3 -- and 2 of them he already ruled.

WHY THIS EXISTS. Entry C1 of the master task list asks him a narrow question:
into which of sigma, S_k or R_k should a claim-level verdict enter, and as a
multiplier or as an additive channel of its own. That question is genuinely his
and this script does not touch it.

What this script tests are the 2 SUPPORTING ARGUMENTS the entry built around it,
both asserted from a 2026-10-18 search and neither re-executed since:

  (a) *"`target_complexity` appears with `informative_only` NOWHERE in the
      code"*, used to argue that the claim ledger's own header names a precedent
      that does not exist, so there is no worked example to copy.

  (b) *"3 channels carry `informative_only = True` ... and 0 of the 3 have ever
      been promoted"*, with the conclusion that *"it is worth asking about all 3
      at once, since the same question governs the 2 runner channels, and
      answering it once would retire a class rather than an item."*

BOTH ARE FALSE, and the second one matters most, because acting on it would ask
him to re-decide 2 things he has already decided -- the `already ruled` failure
this project's record names twice.

HOW IT IS MEASURED. By AST, not by grep, because the 2026-10-18 search most
likely failed on a SAME-LINE predicate: `result["target_complexity"]` and
`"informative_only"` sit 4 lines apart in the same dict literal, so any pattern
requiring them on one line reports absence truthfully and uselessly. This walks
every dict literal and every class-body assignment, so proximity is irrelevant.

WHAT IT FINDS. The `why` field beside an `informative_only` flag is the live
evidence of a ruling: 2 of the channels carry one naming his own date and words,
and a channel he has ruled informative-only BY DESIGN is not a channel awaiting
promotion.
"""
from __future__ import annotations

import argparse
import ast
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

#: Live code only. `bench/logs/` holds harvested sandbox copies of the runner,
#: which are evidence of past runs and not code anything executes.
SEARCH = [REPO / "bench", REPO / "scripts"]
EXCLUDE_PARTS = {"logs", "tests", "__pycache__", ".git"}


def _py_files() -> list[Path]:
    out: list[Path] = []
    for root in SEARCH:
        for p in sorted(root.rglob("*.py")):
            if EXCLUDE_PARTS & set(p.relative_to(REPO).parts):
                continue
            out.append(p)
    return out


def _scope_map(tree: ast.AST) -> list[tuple[int, int, str, bool]]:
    """(start, end, name, is_class) for every function and class.

    Sorted smallest-span first, so a scan finds the INNERMOST scope first.
    """
    spans = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            end = getattr(node, "end_lineno", node.lineno)
            spans.append((node.lineno, end, node.name,
                          isinstance(node, ast.ClassDef)))
    return sorted(spans, key=lambda t: (t[1] - t[0]))


def _scope_of(spans, line: int) -> str:
    """The CLASS if the line is inside one, else the innermost function.

    ★ A CLASS BEATS ITS OWN METHOD, corrected mid-measurement. The first
    version returned the innermost scope, which split `ClaimLedger` into 2
    channels: the class body sets `informative_only = True` at line 299 and the
    `report` method serialises it at 346. Those are 1 channel -- a flag and its
    own serialisation -- and counting them as 2 inflates what is owed him,
    which is the exact error this script exists to correct in entry C1.
    """
    enclosing_class = None
    innermost_fn = None
    for start, end, name, is_class in spans:
        if not (start <= line <= end):
            continue
        if is_class and enclosing_class is None:
            enclosing_class = name
        if not is_class and innermost_fn is None:
            innermost_fn = name
    return enclosing_class or innermost_fn or "<module>"


def _dict_sites(tree: ast.AST, path: Path) -> list[dict]:
    """Every dict literal carrying an `informative_only` key, with its siblings."""
    found = []
    _spans = _scope_map(tree)
    for node in ast.walk(tree):
        if not isinstance(node, ast.Dict):
            continue
        keys = [k.value for k in node.keys
                if isinstance(k, ast.Constant) and isinstance(k.value, str)]
        if "informative_only" not in keys:
            continue
        why = None
        for k, v in zip(node.keys, node.values):
            if isinstance(k, ast.Constant) and k.value == "why":
                try:
                    why = ast.literal_eval(v)
                except Exception:
                    why = ast.unparse(v)[:300]
        found.append({"file": str(path.relative_to(REPO)),
                      "line": node.lineno, "kind": "dict-literal",
                      "scope": _scope_of(_spans, node.lineno),
                      "sibling_keys": sorted(keys), "why": why})
    return found


def _attr_sites(tree: ast.AST, path: Path) -> list[dict]:
    """Class-body `informative_only = ...` assignments, which are state flags."""
    found = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        for stmt in node.body:
            if isinstance(stmt, ast.Assign):
                for t in stmt.targets:
                    if isinstance(t, ast.Name) and t.id == "informative_only":
                        found.append({"file": str(path.relative_to(REPO)),
                                      "line": stmt.lineno,
                                      "kind": f"class-attr:{node.name}",
                                      "scope": node.name,
                                      "sibling_keys": [], "why": None})
    return found


def sites() -> list[dict]:
    out: list[dict] = []
    for p in _py_files():
        try:
            tree = ast.parse(p.read_text(errors="ignore"))
        except SyntaxError:
            continue
        out.extend(_dict_sites(tree, p))
        out.extend(_attr_sites(tree, p))
    return sorted(out, key=lambda d: (d["file"], d["line"]))


def target_complexity_cooccurs() -> list[dict]:
    """CLAIM (a): does `target_complexity` ever appear WITH `informative_only`?

    Answered structurally: an assignment whose target subscripts the string
    `target_complexity` and whose value is a dict carrying the flag.
    """
    hits = []
    for p in _py_files():
        try:
            tree = ast.parse(p.read_text(errors="ignore"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Assign):
                continue
            for t in node.targets:
                if not (isinstance(t, ast.Subscript)
                        and isinstance(t.slice, ast.Constant)
                        and t.slice.value == "target_complexity"):
                    continue
                if isinstance(node.value, ast.Dict):
                    keys = [k.value for k in node.value.keys
                            if isinstance(k, ast.Constant)]
                    if "informative_only" in keys:
                        hits.append({"file": str(p.relative_to(REPO)),
                                     "line": node.lineno,
                                     "keys": sorted(str(k) for k in keys)})
    return hits


def first_commit_touching(path: str, line: int) -> dict:
    """WHEN a line was written, so a stale claim is not called a false one."""
    r = subprocess.run(["git", "blame", "-L", f"{line},{line}",
                        "--date=short", "--", path],
                       capture_output=True, text=True, cwd=str(REPO))
    if r.returncode != 0 or not r.stdout.strip():
        return {"sha": None, "date": None}
    head = r.stdout.split("\n")[0]
    parts = head.split()
    return {"sha": parts[0].lstrip("^"),
            "date": next((p for p in parts if p.count("-") == 2), None)}


def wilson(k: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1.0 + z * z / n
    c = p + z * z / (2 * n)
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5)
    return ((c - h) / d, (c + h) / d)


def classify() -> dict:
    """Group sites into CHANNELS, then ask which channels await a decision.

    ★ THE UNIT IS THE CHANNEL, NOT THE SITE, and getting that wrong is the
    mistake entry C1 made. `bench/reference_runner_v3.py:19809` is the ERROR
    path of the very channel ruled 4 lines of output above it, and
    `bench/claim_ledger.py:346` merely serialises the flag set at `:299`. A
    first version of this script counted 6 sites and reported 4 "awaiting a
    decision", which over-counts by exactly the sibling sites a ruling already
    covers. Channels are keyed by (file, enclosing scope) and a `why` naming a
    founder ruling PROPAGATES to every site of its channel.
    """
    all_sites = sites()
    channels: dict[tuple[str, str], dict] = {}
    for s_ in all_sites:
        key = (s_["file"], s_.get("scope", "<module>"))
        ch = channels.setdefault(key, {"file": s_["file"],
                                       "scope": s_.get("scope", "<module>"),
                                       "sites": [], "why": None})
        ch["sites"].append(s_)
        if s_["why"] and "founder ruling" in str(s_["why"]).lower():
            ch["why"] = s_["why"]

    ruled = [c for c in channels.values() if c["why"]]
    unruled = [c for c in channels.values() if not c["why"]]
    return {"sites": all_sites, "n_sites": len(all_sites),
            "channels": list(channels.values()), "n_channels": len(channels),
            "ruled": ruled, "unruled": unruled}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    c = classify()
    tc = target_complexity_cooccurs()
    prov = [dict(h, **first_commit_touching(h["file"], h["line"])) for h in tc]

    n, k = c["n_channels"], len(c["ruled"])
    lo, hi = wilson(k, max(n, 1))
    try:
        from statsmodels.stats.proportion import proportion_confint
        slo, shi = proportion_confint(k, max(n, 1), method="wilson")
        agree = abs(slo - lo) < 1e-12 and abs(shi - hi) < 1e-12
    except Exception:                                          # pragma: no cover
        slo = shi = float("nan"); agree = False

    res = {"classification": c, "target_complexity_cooccurrences": prov,
           "ruled_rate": {"k": k, "n": n, "wilson_closed_form": [lo, hi],
                          "wilson_statsmodels": [slo, shi],
                          "two_tools_agree": agree}}
    if args.json:
        print(json.dumps(res, indent=2, default=str))
        return 0

    print(__doc__)
    print("=" * 78)
    print(f"LIVE `informative_only` SITES (AST, logs/tests excluded): "
          f"{c['n_sites']}  ->  DISTINCT CHANNELS: {n}")
    for ch in sorted(c["channels"], key=lambda d: (d["file"], d["scope"])):
        mark = "RULED   " if ch["why"] else "AWAITING"
        locs = ", ".join(str(x["line"]) for x in ch["sites"])
        print(f"  {mark} {ch['file']}  scope={ch['scope']}  line(s) {locs}")
        if ch["why"]:
            print(f"           why: {str(ch['why'])[:150]}")
    print()
    print(f"ALREADY RULED informative-only BY DESIGN: {k} of {n}")
    print(f"    Wilson 95% (closed form) [{lo:.6f}, {hi:.6f}]")
    print(f"    Wilson 95% (statsmodels) [{slo:.6f}, {shi:.6f}]  agree={agree}")
    print(f"AWAITING A DECISION: {len(c['unruled'])} channel(s)")
    for ch in c["unruled"]:
        print(f"    {ch['file']}  scope={ch['scope']}  "
              f"line(s) {', '.join(str(x['line']) for x in ch['sites'])}")
    print()
    print("CLAIM (a): `target_complexity` with `informative_only`, co-occurring")
    if not prov:
        print("    0 sites. The entry's statement STANDS.")
    else:
        print(f"    {len(prov)} site(s) -- the entry's statement is REFUTED:")
        for h in prov:
            print(f"      {h['file']}:{h['line']}  written {h['date']} "
                  f"in {h['sha']}")
        print("    The entry's search was dated 2026-10-18. Any site written")
        print("    BEFORE that date was present when the search reported it")
        print("    absent, so the search missed it rather than the tree moving.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
