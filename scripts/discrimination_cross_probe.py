#!/usr/bin/env python3
"""Separate "the falsifier does not discriminate" from "the proposed fix was bad".

THE PROBLEM THIS EXISTS TO SOLVE
--------------------------------
The discrimination control returned 132 of 263 falsifiers going quiet when their
own accused defect was repaired (50.2%). Against a pre-registered threshold of
95% that is a bad number -- but only if the 131 that still fired did so because
they do not discriminate. There is a competing explanation with equal standing:
these are MODEL-PROPOSED fixes that in most cases were never applied or reviewed,
so a fix that applies cleanly may simply not repair the defect. A perfect
falsifier facing a bad fix is RIGHT to keep firing.

Nothing measured so far separates those two, and reporting 50.2% without
separating them would be a conclusion resting on an unresolved confound.

THE SEPARATION
--------------
For each falsifier that never went quiet, run it against patched versions of its
own target produced by OTHER findings' fixes -- specifically the ones that were
observed to SILENCE some other falsifier, so they are known to be substantive
changes to that file rather than cosmetic ones.

  * quiet on at least one  -> the falsifier IS sensitive to substantive change in
                              its target. Its own fix was the thing that failed.
  * quiet on none of them  -> across its own fix, N other substantive changes, and
                              the null-perturbation control, this falsifier has
                              never once been observed to change its answer.

The second group is the one that matters. It is not proof of a worthless
falsifier -- the other changes may not touch the accused defect -- but it is the
population for which no evidence of discrimination exists anywhere.

Nothing is written to the real tree; every run is a throwaway symlink overlay.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import pathlib
import re
import shutil
import subprocess
import sys
import time

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
import bench.reference_runner_v2 as RR                      # noqa: E402
from bench.falsifier_verify import reverify_falsifier       # noqa: E402

RECORD = REPO / "experimental_notes/data/discrimination_control_archive.json"
OUT_BASE = REPO / "experimental_notes/data/discrimination_cross_probe"
BLK = re.compile(r"<<<<\s*SEARCH[^\n]*\n(.*?)\n====\s*REPLACE[^\n]*\n(.*?)\n>>>>", re.S)
TIMEOUT = 25
_cache: dict = {}


def _sha(t: str) -> str:
    return hashlib.sha256((t or "").encode("utf-8", "replace")).hexdigest()[:16]


def _verdict(fcode: str, rel: str, content: str) -> str:
    key = (_sha(content), _sha(fcode), rel)
    if key in _cache:
        return _cache[key]
    root = None
    try:
        root = RR._build_discrimination_overlay(REPO, rel, content)
        code, _ = RR._retarget_falsifier(fcode, REPO, root)
        v = reverify_falsifier(code, repo_root=str(root), timeout=TIMEOUT)
    except Exception as exc:                       # noqa: BLE001
        v = f"ERROR:{type(exc).__name__}"
    finally:
        if root is not None:
            shutil.rmtree(root, ignore_errors=True)
    _cache[key] = v
    return v


def _apply(src: str, fix: str):
    blocks = BLK.findall(fix or "")
    if not blocks:
        return None
    out, n = src, 0
    for s_, r_ in blocks:
        if s_ and s_ in out:
            out = out.replace(s_, r_, 1); n += 1
    return out if n == len(blocks) else None       # ALL blocks or nothing


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--variants", type=int, default=8,
                    help="how many other-finding patches to try per falsifier")
    ap.add_argument("--subjects", default="never_quiet",
                    choices=["never_quiet", "discriminating"],
                    help="never_quiet: does a still-firing falsifier respond to ANY "
                         "change (is its own fix to blame)? discriminating: does a "
                         "falsifier that DID go quiet stay firing on other findings' "
                         "fixes, i.e. is it SPECIFIC rather than merely fragile?")
    args = ap.parse_args()

    rec = json.loads(RECORD.read_text())["rows"]
    idx = {(r["run"], r["cid"]): r for r in rec}
    ents: dict = {}
    for rp in sorted(p for p in (REPO / "bench/logs").glob("*/*_report.json")
                     if ".errata" not in str(p)):
        nm = rp.parent.name
        if nm.endswith("_latest"):
            continue
        d = json.loads(rp.read_text(encoding="utf-8", errors="replace"))
        for cid, e in ((d.get("registry") or {}).get("entries") or {}).items():
            if (nm, cid) in idx:
                ents[(nm, cid)] = e

    # Known-substantive patches per target: the ones that silenced SOME falsifier.
    donors: dict = collections.defaultdict(list)
    for k, r in idx.items():
        if r["route_a"] != "DISCRIMINATES":
            continue
        e = ents.get(k)
        if not e:
            continue
        base = subprocess.run(["git", "show", f"{r['baseline_sha']}:{r['target']}"],
                              capture_output=True, text=True, cwd=str(REPO)).stdout
        patched = _apply(base, e.get("proposed_fix") or "")
        if patched and patched != base:
            donors[r["target"]].append((k[1], patched))

    if args.subjects == "never_quiet":
        subjects = [(k, r) for k, r in idx.items()
                    if r["route_a"] == "NO_DISCRIMINATION_OR_INEFFECTIVE_FIX"
                    and r["route_b"] == "ALWAYS_FIRES_NEVER_QUIET"]
        label = "never-quiet"
    else:
        subjects = [(k, r) for k, r in idx.items() if r["route_a"] == "DISCRIMINATES"]
        label = "discriminating"
    print(f"=== cross-probe [{args.subjects}]: {len(subjects)} {label} falsifiers, "
          f"up to {args.variants} substantive variants each ===")
    for t, v in sorted(donors.items()):
        print(f"    {len(v):>4} donor patches available for {t}")
    print(flush=True)

    rows, tally = [], collections.Counter()
    t0 = time.time()
    for i, (k, r) in enumerate(subjects, 1):
        fcode = (ents[k].get("falsifier_code") or "")
        rel = r["target"]
        pool = [(c, p) for c, p in donors.get(rel, []) if c != k[1]][:args.variants]
        quiet_on, errs = [], 0
        for cid_d, patched in pool:
            v = _verdict(fcode, rel, patched)
            if v.startswith("ERROR"):
                errs += 1
            elif v != "CONFIRMED":
                quiet_on.append(cid_d)
        row = {"run": k[0], "cid": k[1], "target": rel, "variants_tried": len(pool),
               "quiet_on": quiet_on, "errors": errs}
        if not pool:
            row["verdict"] = "NO_VARIANTS_AVAILABLE"; tally["no_variants"] += 1
        elif args.subjects == "never_quiet":
            if quiet_on:
                row["verdict"] = "SENSITIVE_ITS_OWN_FIX_FAILED"; tally["sensitive"] += 1
            else:
                row["verdict"] = "NEVER_QUIET_ON_ANY_CHANGE"; tally["never_quiet"] += 1
        else:
            # A falsifier that goes quiet on SOMEBODY ELSE'S fix is not specific to
            # its own claim -- it is merely fragile, and its route-A pass is hollow.
            if quiet_on:
                row["verdict"] = "NOT_SPECIFIC_QUIET_ON_OTHERS_TOO"; tally["not_specific"] += 1
            else:
                row["verdict"] = "SPECIFIC_QUIET_ONLY_ON_ITS_OWN_FIX"; tally["specific"] += 1
        rows.append(row)
        if i % 20 == 0 or i == len(subjects):
            print(f"  [{i:>4}/{len(subjects)}] {time.time()-t0:6.0f}s  "
                  + "  ".join(f"{a}={b}" for a, b in sorted(tally.items())), flush=True)

    OUT = pathlib.Path(f"{OUT_BASE}_{args.subjects}.json")
    OUT.write_text(json.dumps({"n": len(rows), "tally": dict(tally), "rows": rows}, indent=1))
    print(f"\n  written: {OUT}\n")
    if args.subjects == "never_quiet":
        n = tally["sensitive"] + tally["never_quiet"]
        print(f"  of {n} never-quiet falsifiers with variants available:")
        print(f"    SENSITIVE to substantive change (own fix failed) : {tally['sensitive']:>4}"
              f"  ({tally['sensitive']/max(n,1)*100:.1f}%)")
        print(f"    NEVER quiet on any change tested                 : {tally['never_quiet']:>4}"
              f"  ({tally['never_quiet']/max(n,1)*100:.1f}%)")
    else:
        n = tally["specific"] + tally["not_specific"]
        print(f"  of {n} DISCRIMINATING falsifiers with variants available:")
        print(f"    SPECIFIC  -- quiet on its own fix, fires on all others : {tally['specific']:>4}"
              f"  ({tally['specific']/max(n,1)*100:.1f}%)")
        print(f"    NOT specific -- also quiet on other findings' fixes    : {tally['not_specific']:>4}"
              f"  ({tally['not_specific']/max(n,1)*100:.1f}%)")
    print(f"    no donor patches available for the target        : {tally['no_variants']:>4}")
    print("\n  A 'sensitive' falsifier answers the confound in the instrument's favour:")
    print("  it responds to substantive change, so its own fix is what failed.")
    print("  'Never quiet on any change' is not proof the falsifier is worthless -- the")
    print("  donor patches may not touch its accused defect -- but it is the population")
    print("  for which no evidence of discrimination exists anywhere.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
