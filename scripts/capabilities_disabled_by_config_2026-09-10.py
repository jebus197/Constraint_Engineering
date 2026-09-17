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


def _getattr_string_read(n: ast.Call) -> str | None:
    """`getattr(obj, "field", ...)`: an attribute read WRITTEN AS A STRING.

    ADDED 2026-09-17 (task 3.3, panel round 16). Until then this scanner resolved
    `cfg.field`, `d["field"]` and `d.get("field")` but not this form, so it
    reported `merge_arbitration_enabled` and `immune_memory_enabled` as read by
    nothing while `bench/reference_runner_v3.py` reads both through `getattr`.
    Task A18's `readers_of()` in `scripts/config_fields_are_read_2026-09-11.py`
    had already resolved both forms; its test compares the 2 instruments.
    """
    if isinstance(n.func, ast.Name) and n.func.id == "getattr" \
            and len(n.args) >= 2 and isinstance(n.args[1], ast.Constant) \
            and isinstance(n.args[1].value, str):
        return n.args[1].value
    return None


def read_fields(src: str) -> set[str]:
    """Field names the runner actually reads, by AST rather than by grep.

    A grep for the name matches its own definition, a comment, and a docstring.
    Only a subscript, an attribute access, a `.get("field")` or a
    `getattr(obj, "field")` is a READ.
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
        elif isinstance(n, ast.Call):
            s = _getattr_string_read(n)
            if s:
                names.add(s)
    return names


def explanation(data: dict, leaf: str, path: str | None = None) -> str:
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

    NESTED PATHS, ADDED 2026-09-17 (task 3.3, panel round 16), AND IT IS THE SAME
    DEFECT A SECOND TIME. This looked only at top-level `_<field>_note` keys, so
    `_ouroboros.max_papers_per_round = 0` read as unexplained in every arm while
    its own block carried `_note`: "External literature retrieval OFF". Given the
    full `path`, each enclosing block is now searched too, innermost first: its
    sibling `_<field>_note` keys, then the block's own `_note`.
    """
    base = leaf.rstrip("_")
    keys = (f"_{base}_note", f"_{base.replace('_enabled','')}_note",
            f"_{base.split('_')[0]}_note")
    blocks = list(reversed(_enclosing_blocks(data, path))) if path else []
    for block in [data] + blocks:
        for key in keys:
            v = block.get(key)
            if isinstance(v, str) and v.strip():
                return v.strip()
    for block in blocks:
        v = block.get("_note")
        if isinstance(v, str) and v.strip():
            return v.strip()
    return ""


def _enclosing_blocks(data: dict, path: str) -> list[dict]:
    """The dicts that contain the leaf at `path`, outermost first, excluding `data`."""
    tokens = [t for t in re.split(r"\.|\[(\d+)\]", path) if t]
    out, node = [], data
    for tok in tokens[:-1]:
        try:
            node = node[int(tok)] if isinstance(node, list) else node[tok]
        except (KeyError, IndexError, ValueError, TypeError):
            return out
        if isinstance(node, dict):
            out.append(node)
    return out


def cited_record(data: dict, leaf: str, val) -> str:
    """A string elsewhere in the same file that names `leaf=value`, if any.

    ADDED 2026-09-17 (task 3.3, panel round 16). `hardened_gate_enabled = false`
    has no `_note` of its own in any exp56 arm, but each arm's
    `_convergence_criteria.description` reads "TWO-SIDED GATE (founder ruling
    2026-06-10; hardened_gate_enabled=false)". That RECORDS the setting and names
    the ruling it belongs to without stating a reason, so it is reported as
    CITED, distinct from a note that explains the setting.
    """
    if val is False:
        value = r"false"
    elif isinstance(val, (int, float)) and not isinstance(val, bool):
        value = re.escape(json.dumps(val)) + r"(?![\d.])"
    else:
        return ""
    pat = re.compile(rf"(?<![A-Za-z0-9_]){re.escape(leaf)}\s*[=:]\s*{value}", re.I)
    for path, s in walk(data):
        if isinstance(s, str):
            m = pat.search(s)
            if m:
                return f"{path}: {m.group(0)}"
    return ""


def classify(data: dict, rel: str, read: set[str]) -> list[dict]:
    """Every off-switch in a config, with whether it is read and what records it.

    `status` is DOCUMENTED (a note states a reason), CITED (a string names the
    setting without stating a reason) or UNEXPLAINED (neither).
    """
    rows = []
    for path, val in walk(data):
        leaf = path.split(".")[-1].split("[")[0]
        off = (val is False and ENABLEMENT.search(leaf)) or \
              (isinstance(val, int) and not isinstance(val, bool)
               and val == 0 and ALLOWANCE.search(leaf))
        if not off:
            continue
        why = explanation(data, leaf, path)
        cite = "" if why else cited_record(data, leaf, val)
        rows.append({"file": rel, "path": path, "leaf": leaf, "value": val,
                     "read": leaf in read, "why": why, "cited": cite,
                     "status": "DOCUMENTED" if why else
                               "CITED" if cite else "UNEXPLAINED"})
    return rows


def walk(obj, prefix=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from walk(v, f"{prefix}.{k}" if prefix else k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from walk(v, f"{prefix}[{i}]")
    else:
        yield prefix, obj


def survey() -> dict:
    """Read every runner module and every config; classify every off-switch."""
    srcs = runner_sources()
    read = set()
    for f in srcs:
        try:
            read |= read_fields(f.read_text(encoding="utf-8", errors="replace"))
        except OSError:
            continue
    files = config_files()
    rows = []
    for f in files:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        rows.extend(classify(data, str(f.relative_to(REPO)), read))
    return {"sources": srcs, "read": read, "files": files, "rows": rows}


def main() -> int:
    s = survey()
    srcs, read, files, rows = s["sources"], s["read"], s["files"], s["rows"]
    disabled = [r for r in rows if r["read"]]
    unread = [r for r in rows if not r["read"]]

    print(f"config files scanned: {len(files)}")
    print(f"runner modules scanned: {len(srcs)}")
    print(f"fields those modules READ, by AST: {len(read)}\n")

    _SHOW = 40
    _TAG = {"DOCUMENTED": "DOCUMENTED", "CITED": "CITED, NO REASON STATED",
            "UNEXPLAINED": "*** UNEXPLAINED ***"}

    def show(r):
        print(f"    {r['file']}\n        {r['path']} = {r['value']!r}   "
              f"[{_TAG[r['status']]}]")
        if r["why"]:
            print(f"          reason on file: {r['why'][:150]}")
        elif r["cited"]:
            print(f"          cited on file : {r['cited'][:150]}")

    print(f"CAPABILITIES SWITCHED OFF IN CONFIG THAT THE RUNNER READS "
          f"({len(disabled)}):")
    for r in disabled[:_SHOW]:
        show(r)
    if len(disabled) > _SHOW:
        print(f"    ... {len(disabled) - _SHOW} more not shown")
    if not disabled:
        print("    none")

    print(f"\nSET TO OFF BUT THE RUNNER NEVER READS THE FIELD ({len(unread)}) — "
          f"a DIFFERENT defect, an unwired addition, not this task's:")
    for r in unread[:_SHOW]:
        show(r)
    if len(unread) > _SHOW:
        print(f"    ... {len(unread) - _SHOW} more not shown")
    if not unread:
        print("    none")

    documented = [r for r in rows if r["status"] == "DOCUMENTED"]
    cited = [r for r in rows if r["status"] == "CITED"]
    unexplained = [r for r in rows if r["status"] == "UNEXPLAINED"]
    print(f"\n  off-switches whose own file STATES A REASON (a sibling or "
          f"enclosing-block note): {len(documented)} of {len(rows)}")
    print(f"  off-switches whose own file only CITES the setting, stating no "
          f"reason: {len(cited)} of {len(rows)}")
    for r in cited[:_SHOW]:
        print(f"      {r['file']}: {r['path']} = {r['value']!r}")
    print(f"\n  THE FIGURE THAT MATTERS: off-switches with NEITHER a note NOR a "
          f"cited record in their own file: {len(unexplained)} of {len(rows)}")
    for r in unexplained[:_SHOW]:
        print(f"      {r['file']}: {r['path']} = {r['value']!r}")
    if not unexplained:
        print("      none — every off-switch found has a note or a cited record "
              "in its own file")
    n = len(rows)
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
