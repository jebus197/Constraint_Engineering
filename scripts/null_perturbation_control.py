#!/usr/bin/env python3
"""THE NULL-PERTURBATION CONTROL. Does a falsifier respond to the CLAIM, or to any change?

WHAT THIS TESTS, AND WHY IT IS THE COMPLEMENT OF THE DISCRIMINATION CONTROL
--------------------------------------------------------------------------
The discrimination control asks: repair the claim, does the falsifier go QUIET?
It has never run, because it needs a corrected copy from the panel and nothing
supplies one (`reference_runner_v2.py:593` is a dead flag).

This asks the opposite and needs no panel input at all: change something
SEMANTICALLY IRRELEVANT, does the falsifier STAY PUT? A sound falsifier must.
One that flips is responding to the file changing rather than to the claim - the
access-versus-dependence hole (`reference_runner_v2.py:2972`) promoted one level,
and the failure mode a CC2 review named on 2026-08-22: "change-response without
claim-dependence".

Recommended as the first thing to build by a CC2 review, on three grounds: it runs
offline today; the discrimination control cannot substitute because nothing supplies
a corrected copy; and it is logically PRIOR to a provenance log, because a log that
records which mechanism settled a verdict is worthless if the mechanism does not
discriminate.

THE PERTURBATION IS DELIBERATELY THE WEAKEST POSSIBLE
-----------------------------------------------------
A trailing comment line. It changes the file's bytes and its length and NOTHING
else: no name, no value, no control flow, no import. If a falsifier's verdict moves
under that, nothing about the claim moved with it.

This is the conservative direction. A stronger perturbation would flip more
falsifiers and prove less, because a genuine dependence could legitimately respond.

SAFETY
------
The real target is NEVER written. `_build_discrimination_overlay` builds a symlink
mirror of the repo in a temp dir and replaces exactly one file there. Each overlay
is removed in a `finally`.

    python3 scripts/null_perturbation_control.py --limit 40
    python3 scripts/null_perturbation_control.py            # all eligible findings
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import shutil
import sys
from collections import Counter

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from bench.falsifier_verify import reverify_falsifier  # noqa: E402
from bench.reference_runner_v2 import _build_discrimination_overlay  # noqa: E402

MARKER = "\n# null-perturbation control: semantically inert line, appended by the control\n"

# TWO perturbations, because one of them is too weak on its own.
#
# COMMENT: appends a comment line. Changes bytes and length, nothing else. But 449
# of 465 archived falsifiers IMPORT the target rather than reading it as text, and
# an importer cannot see a comment. So a 0% flip rate here proves only that
# falsifiers are not byte-sensitive - a weak claim, and a control that cannot fail.
#
# UNRELATED_CODE: renames a module-level function the finding does NOT accuse, and
# leaves an alias behind so every existing caller still resolves. Semantically
# equivalent, visible to an importer, and genuinely unrelated to the claim. THIS is
# the one that can fail, and therefore the one that means something.


def _perturb_unrelated_code(src: str, accused: set) -> "tuple[str, str] | None":
    """Rename one module-level def the finding does not accuse; alias it back."""
    import re as _re
    names = _re.findall(r"^def\s+(\w+)\s*\(", src, _re.M)
    victim = next((n for n in names if n not in accused and not n.startswith("_")), None)
    if victim is None:
        victim = next((n for n in names if n not in accused), None)
    if victim is None:
        return None
    new = f"{victim}_nullperturb"
    out = _re.sub(rf"^def\s+{_re.escape(victim)}\s*\(", f"def {new}(", src, count=1, flags=_re.M)
    # alias so behaviour is preserved for every caller
    out += f"\n\n{victim} = {new}  # null-perturbation control: alias preserves behaviour\n"
    return out, victim


def eligible():
    """Findings with a falsifier AND a target that resolves inside the repo."""
    out = []
    for p in sorted((REPO / "bench" / "logs").glob("exp4[2-9]*/*_report.json")):
        if ".errata" in str(p):
            continue
        rep = json.loads(p.read_text(encoding="utf-8"))
        tf = rep.get("target_file")
        if not tf or pathlib.Path(tf).is_absolute() or not (REPO / tf).is_file():
            continue
        run = p.parent.name.split("_")[0]
        for cid, e in (rep.get("registry", {}).get("entries") or {}).items():
            code = (e.get("falsifier_code") or "").strip()
            if code:
                out.append({"run": run, "cid": cid, "target": tf, "code": code,
                            "severity": e.get("severity"), "status": e.get("status"),
                            "description": (e.get("description") or "")[:400]})
    return out


def _run_against(code, content, tf):
    overlay = None
    try:
        overlay = _build_discrimination_overlay(REPO, tf, content)
        return reverify_falsifier(code, repo_root=str(overlay), timeout=30)
    finally:
        if overlay is not None:
            shutil.rmtree(overlay, ignore_errors=True)


def run_one(item):
    """Return (baseline, after-comment, after-unrelated-code-change, victim)."""
    tf = item["target"]
    original = (REPO / tf).read_text(encoding="utf-8")
    base = reverify_falsifier(item["code"], repo_root=str(REPO), timeout=30)
    p_comment = _run_against(item["code"], original + MARKER, tf)
    accused = set(re.findall(r"\b(\w+)\s*\(", item.get("description") or ""))
    made = _perturb_unrelated_code(original, accused)
    if made is None:
        return base, p_comment, "NO_UNRELATED_DEF", None
    src2, victim = made
    return base, p_comment, _run_against(item["code"], src2, tf), victim


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--limit", type=int, default=0, help="cap the number tested")
    ap.add_argument("--out", default="experimental_notes/data/null_perturbation_control.json")
    args = ap.parse_args()

    items = eligible()
    if args.limit:
        items = items[: args.limit]
    print(f"  eligible findings (falsifier + in-repo target): {len(items)}\n")

    rows, pair = [], Counter()
    for n, it in enumerate(items, 1):
        try:
            base, p_com, p_code, victim = run_one(it)
        except Exception as exc:  # noqa: BLE001 — a control must not die on one item
            base, p_com, p_code, victim = "HARNESS_ERROR", f"{type(exc).__name__}", "-", None
        rows.append({**{k: it[k] for k in ("run", "cid", "target", "severity", "status")},
                     "baseline": base, "after_comment": p_com,
                     "after_unrelated_code": p_code, "renamed": victim,
                     "changed_comment": base != p_com,
                     "changed_code": p_code not in (base, "NO_UNRELATED_DEF")})
        pair[(base, p_com, p_code)] += 1
        if n % 40 == 0:
            print(f"    {n}/{len(items)}…", flush=True)

    # A falsifier that never fired on the unmodified target says nothing either way.
    informative = [r for r in rows if r["baseline"] not in ("HARNESS_ERROR",)]
    fired = [r for r in informative if r["baseline"] == "CONFIRMED"]
    flip_com = [r for r in fired if r["changed_comment"]]
    flip_code = [r for r in fired if r["changed_code"]]
    no_def = [r for r in fired if r["after_unrelated_code"] == "NO_UNRELATED_DEF"]

    print(f"\n  tested                              : {len(rows)}")
    print(f"  usable (baseline ran)               : {len(informative)}")
    print(f"  fired on the unmodified target      : {len(fired)}")
    n = len(fired) or 1
    print("  OF THOSE:")
    print(f"    flipped on an appended COMMENT        : {len(flip_com):4d}  ({len(flip_com)/n*100:5.1f}%)")
    print(f"    flipped on an UNRELATED CODE CHANGE   : {len(flip_code):4d}  ({len(flip_code)/n*100:5.1f}%)  <-- the meaningful one")
    print(f"    (no unrelated def available to rename): {len(no_def):4d}")
    print("\n  baseline -> comment -> unrelated-code, most common:")
    for (b, c1, c2), c in pair.most_common(8):
        flag = "   <-- CODE FLIP" if c2 not in (b, "NO_UNRELATED_DEF") else ""
        print(f"    {str(b)[:18]:18s} -> {str(c1)[:18]:18s} -> {str(c2)[:20]:20s} {c:4d}{flag}")

    dest = REPO / args.out
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps({"rows": rows}, indent=2), encoding="utf-8")
    print(f"\n  written: {args.out}")
    print("""
  READING IT. A falsifier that changes verdict when a comment is appended is not
  testing its claim - it is reacting to the file. A low rate means the instrument
  discriminates and the provenance log becomes the binding constraint. A high rate
  means tool-settled verdicts in the archive are worth less than their label says.""")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
