#!/usr/bin/env python3
"""THE COMPLEMENTARY CONTROL, run offline against the archive. Both routes.

WHAT IT ASKS
------------
The null-perturbation control (2026-08-21) asked: change something the finding
does NOT accuse, and does the falsifier stay put? 0 of 360 moved.

That closes one half. This is the other half, and it is the one that matters:
REPAIR THE ACCUSED DEFECT, AND THE FALSIFIER MUST GO QUIET. A falsifier that
still fires after its own accused defect is repaired was never testing that
defect, and CC2 demonstrated on 2026-08-22 that the gate cannot tell the
difference -- `reverify_falsifier("assert False, 'FALSIFIED'")` returns
CONFIRMED.

Four of five panellists named this as the next step. 0 of 2,030 archived entries
carry a discrimination record; the control has never run once in the project's
life.

TWO ROUTES, AND THEY MUST BOTH RUN
----------------------------------
Each has a confound the other does not, so agreement between them is worth more
than either alone.

  ROUTE A -- THE PROPOSED FIX. Apply the finding's own archived `proposed_fix`
  to the baseline text and re-run. Confound: "still fires" cannot distinguish
  "the falsifier does not discriminate" from "the proposed fix did not work".

  ROUTE B -- THE REPAIR HISTORY (CC2's route). Take the target as it stands at
  HEAD and re-run. If the defect was genuinely repaired in the repo since, a
  discriminating falsifier must be quiet. Confound: "still fires" cannot
  distinguish "does not discriminate" from "was never repaired". Needs no fix
  and makes no assumption that a proposed fix is a correct fix.

THE BASELINE REQUIREMENT, WHICH IS THE WHOLE GAME
-------------------------------------------------
A falsifier that does not fire in the first place will trivially "go quiet"
after any repair, and would be scored as a pass. So nothing is scored until the
falsifier has been shown to FIRE against a real historical state of its target.
`--all` version search finds that state; if no version reproduces it, the
finding is EXCLUDED, not passed.

Three further self-checks come from the runner's own apparatus and are not
re-implemented here: the tripwire probe (did the falsifier actually read the
target through the overlay, or is it ignoring the file entirely), the repeat
probe (is it deterministic), and the runner's own baseline check. Any of them
failing yields an INDETERMINATE_* outcome and NO verdict.

NOTHING IS WRITTEN TO THE REAL TREE. Every execution happens inside a throwaway
symlink overlay built by `reference_runner_v2._build_discrimination_overlay`.
The one earlier tool that adjudicated by repair wrote to the target file and
restored it in a `finally`; this does not, deliberately.

SCOPE. exp42-exp47, the code targets. exp48/exp49 are excluded: their target
documents are deleted from disk, so their 68 falsifiers cannot be re-executed at
all, and 100% of the archive's detached falsifiers live there.

    python3 scripts/discrimination_control_archive.py [--limit N] [--runs exp44,exp45]
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

import bench.reference_runner_v2 as RR                       # noqa: E402
from bench.falsifier_verify import reverify_falsifier        # noqa: E402

RUNS = {
    "exp42": "bench/cdsfl_registry/composer.py",
    "exp43": "bench/macrophage_cell.py",
    "exp44": "bench/evidence.py",
    "exp45": "bench/dm/_memory.py",
    "exp46": "bench/dm/_shadow_stage6.py",
    "exp47": "bench/dm/_divergence.py",
}
OUT = REPO / "experimental_notes/data/discrimination_control_archive.json"
TIMEOUT = 25

_verdict_cache: dict = {}
_version_cache: dict = {}


def _target_for(entry: dict, nominal: str) -> str:
    """The file this finding actually accuses.

    The fix emitter writes `<<<< SEARCH <path>` and that path is the finding's
    own statement of what it is about. It agrees with the run's nominal target
    for 290 of the 311 findings that carry a header, but the exceptions are real
    -- exp44 raised findings against `bench/cdsfl_registry/registry.py` -- and
    overlaying the wrong file makes the tripwire report NOT_INTERCEPTED for a
    perfectly sound falsifier. Falls back to the nominal target when the header
    is malformed, which happens when a model puts code on the SEARCH line.
    """
    m = re.search(r"<<<<\s*SEARCH\s+([^\n]+)", entry.get("proposed_fix") or "")
    if m:
        cand = m.group(1).strip()
        if cand and not cand.startswith(("#", "def ", "return ", "if ", "- ")) \
                and (REPO / cand).is_file():
            return cand
    return nominal


def _sha(t: str) -> str:
    return hashlib.sha256((t or "").encode("utf-8", "replace")).hexdigest()[:16]


def _versions(target_rel: str) -> list:
    """Every stored version of the target, newest first, ACROSS ALL REFS.

    `--all` is load-bearing: the milestone merge squashed 107 commits that only
    exist on `exp39-experimental`, and several findings' run-time states live
    only there.
    """
    if target_rel in _version_cache:
        return _version_cache[target_rel]
    shas = subprocess.run(["git", "log", "--all", "--format=%h", "--", target_rel],
                          capture_output=True, text=True, cwd=str(REPO)).stdout.split()
    vers = []
    for sha in shas:
        txt = subprocess.run(["git", "show", f"{sha}:{target_rel}"],
                             capture_output=True, text=True, cwd=str(REPO)).stdout
        if txt:
            vers.append((sha, txt))
    _version_cache[target_rel] = vers
    return vers


def _verdict_against(fcode: str, target_rel: str, content: str) -> str:
    """Run a falsifier with `content` standing in for the target. Never touches
    the real tree: the substitution is a throwaway symlink overlay."""
    key = (_sha(content), _sha(fcode), target_rel)
    if key in _verdict_cache:
        return _verdict_cache[key]
    root = None
    try:
        root = RR._build_discrimination_overlay(REPO, target_rel, content)
        code, _ = RR._retarget_falsifier(fcode, REPO, root)
        v = reverify_falsifier(code, repo_root=str(root), timeout=TIMEOUT)
    except Exception as exc:                        # noqa: BLE001 — recorded, not swallowed
        v = f"ERROR:{type(exc).__name__}"
    finally:
        if root is not None:
            shutil.rmtree(root, ignore_errors=True)
    _verdict_cache[key] = v
    return v


def _intercepts(fcode: str, target_rel: str) -> bool:
    """THE TRIPWIRE. Replace the target with a file that raises on import. A
    falsifier that still returns a normal verdict never read the target, so
    nothing downstream of it means anything."""
    v = _verdict_against(fcode, target_rel, RR.DISC_TRIPWIRE_BODY)
    return v.startswith("ERROR") or v in ("ERROR", "INDETERMINATE")


def _find_baseline(fcode: str, target_rel: str, versions: list, fix: str = ""):
    """A stored version where this falsifier FIRES. Without one, nothing is
    scored: a falsifier that never fires goes quiet on every repair.

    Where a proposed fix exists, PREFER a firing version the fix also applies to.
    A fix whose SEARCH block does not match the baseline is not evidence about
    the falsifier, and taking the newest firing version regardless produced a
    50% no-apply rate on the first smoke test.
    """
    firing = []
    for sha, txt in versions:
        if _verdict_against(fcode, target_rel, txt) == "CONFIRMED":
            firing.append((sha, txt))
            if fix and _apply_fix(txt, fix):
                return sha, txt
            if not fix:
                return sha, txt
    return firing[0] if firing else (None, None)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--limit", type=int, default=0, help="stop after N findings")
    ap.add_argument("--runs", default="", help="comma-separated run prefixes")
    ap.add_argument("--out", default=str(OUT), help="where to write the record")
    args = ap.parse_args()
    want = {r.strip() for r in args.runs.split(",") if r.strip()} or set(RUNS)

    findings = []
    for rp in sorted(p for p in (REPO / "bench/logs").glob("*/*_report.json")
                     if ".errata" not in str(p)):
        nm = rp.parent.name
        if nm.endswith("_latest"):
            continue
        m = re.match(r"(exp\d+)", nm)
        if not m or m.group(1) not in RUNS or m.group(1) not in want:
            continue
        rel = RUNS[m.group(1)]
        d = json.loads(rp.read_text(encoding="utf-8", errors="replace"))
        for cid, e in ((d.get("registry") or {}).get("entries") or {}).items():
            if (e.get("falsifier_verdict") or "").upper() != "CONFIRMED":
                continue
            if not (e.get("falsifier_code") or "").strip():
                continue
            findings.append((nm, m.group(1), _target_for(e, rel), cid, e))
    if args.limit:
        findings = findings[:args.limit]

    print(f"=== discrimination control, both routes: {len(findings)} CONFIRMED "
          f"falsifiers over {len(want)} runs ===", flush=True)
    print("  nothing is written to the real tree; every run is a throwaway overlay\n",
          flush=True)

    rows, tally = [], collections.Counter()
    t0 = time.time()
    for i, (nm, run, rel, cid, e) in enumerate(findings, 1):
        fcode = e["falsifier_code"]
        row = {"run": nm, "exp": run, "cid": cid, "target": rel,
               "severity": e.get("severity"), "status": e.get("status"),
               "route_a": "", "route_b": "", "baseline_sha": "",
               "detail": ""}

        if not _intercepts(fcode, rel):
            row["route_a"] = row["route_b"] = "INDETERMINATE_NOT_INTERCEPTED"
            row["detail"] = ("the falsifier returned a normal verdict against a target "
                             "replaced by a file that raises on import, so it never "
                             "read the target and nothing about it can be scored")
            tally["NOT_INTERCEPTED"] += 1
            rows.append(row); _progress(i, len(findings), t0, tally); continue

        bsha, btext = _find_baseline(fcode, rel, _versions(rel),
                                     (e.get('proposed_fix') or '').strip())
        if btext is None:
            row["route_a"] = row["route_b"] = "EXCLUDED_NO_BASELINE"
            row["detail"] = ("no stored version of the target makes this falsifier fire, "
                             "so there is no state in which it demonstrates the defect "
                             "and a 'went quiet' result would be vacuous")
            tally["NO_BASELINE"] += 1
            rows.append(row); _progress(i, len(findings), t0, tally); continue
        row["baseline_sha"] = bsha

        # Determinism: the same falsifier against the same bytes must agree.
        _verdict_cache.pop((_sha(btext), _sha(fcode), rel), None)
        if _verdict_against(fcode, rel, btext) != "CONFIRMED":
            row["route_a"] = row["route_b"] = "INDETERMINATE_NONDETERMINISTIC"
            row["detail"] = "the falsifier gave two different answers to identical input"
            tally["NONDETERMINISTIC"] += 1
            rows.append(row); _progress(i, len(findings), t0, tally); continue

        # ---- ROUTE A: the finding's own proposed fix ------------------------
        fix = (e.get("proposed_fix") or "").strip()
        patched = _apply_fix(btext, fix) if fix else None
        if not patched or patched == btext:
            row["route_a"] = "NO_APPLICABLE_FIX"
            tally["A:no_fix"] += 1
        else:
            v = _verdict_against(fcode, rel, patched)
            if v == "CONFIRMED":
                row["route_a"] = "NO_DISCRIMINATION_OR_INEFFECTIVE_FIX"
                tally["A:still_fires"] += 1
            elif v.startswith("ERROR"):
                row["route_a"] = "INDETERMINATE_ERROR"
                tally["A:error"] += 1
            else:
                row["route_a"] = "DISCRIMINATES"
                tally["A:quiet"] += 1

        # ---- ROUTE B: the repair history, in its strong form ----------------
        # CC2's route. NOT "baseline versus HEAD": that is vacuous whenever the
        # baseline search lands on the newest version, which it does for every
        # defect nobody ever repaired -- and this runner suggests fixes to a human
        # rather than committing them, so most were never repaired in the repo.
        #
        # The answerable question, needing no repair and no proposed fix: across
        # every stored version of the file it accuses, does this falsifier EVER go
        # quiet? A falsifier that fires on all N versions -- months of real edits
        # to that file -- is not responding to its contents. One that is quiet on
        # some and fires on others demonstrably is. That does not prove it tracks
        # the ACCUSED claim, which only route A approaches; it separates access
        # from dependence, which is the hole the null-perturbation control left.
        vers = _versions(rel)                        # newest first
        idx = {sha: k for k, (sha, _t) in enumerate(vers)}
        quiet, fired, errs = [], [], 0
        for sha, txt in vers:
            v = _verdict_against(fcode, rel, txt)
            if v.startswith("ERROR"):
                errs += 1
            elif v == "CONFIRMED":
                fired.append(sha)
            else:
                quiet.append(sha)
        row["versions_total"] = len(vers)
        row["versions_fired"] = len(fired)
        row["versions_quiet"] = len(quiet)
        b = idx.get(bsha, 10 ** 6)
        row["quiet_after_baseline"] = any(idx.get(q, 10 ** 6) < b for q in quiet)
        if len(vers) < 2:
            row["route_b"] = "UNINFORMATIVE_ONE_VERSION_ONLY"
            tally["B:one_version"] += 1
        elif quiet:
            row["route_b"] = "DISCRIMINATES"
            tally["B:quiet"] += 1
            if row["quiet_after_baseline"]:
                tally["B:tracked_a_repair"] += 1
        elif errs and not fired:
            row["route_b"] = "INDETERMINATE_ERROR"
            tally["B:error"] += 1
        else:
            row["route_b"] = "ALWAYS_FIRES_NEVER_QUIET"
            tally["B:always_fires"] += 1

        rows.append(row)
        _progress(i, len(findings), t0, tally)

    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"generated_utc_epoch": int(time.time()), "n": len(rows),
                               "tally": dict(tally), "rows": rows}, indent=1))
    _report(rows, tally, out)
    return 0


def _apply_fix(src: str, fix: str):
    """Apply a `<<<< SEARCH <path>` / `==== REPLACE` / `>>>>` block."""
    blocks = re.findall(r"<<<<\s*SEARCH[^\n]*\n(.*?)\n====\s*REPLACE[^\n]*\n(.*?)\n>>>>",
                        fix, re.S)
    if not blocks:
        return None
    out = src
    applied = 0
    for search, replace in blocks:
        if search and search in out:
            out = out.replace(search, replace, 1)
            applied += 1
    return out if applied else None


def _progress(i, n, t0, tally):
    if i % 20 == 0 or i == n:
        el = time.time() - t0
        print(f"  [{i:>4}/{n}] {el:6.0f}s  "
              + "  ".join(f"{k}={v}" for k, v in sorted(tally.items())), flush=True)


def _report(rows, tally, out):
    print(f"\n  written: {out}\n")
    for route, label in (("route_a", "ROUTE A — the finding's own proposed fix"),
                         ("route_b", "ROUTE B — does it EVER respond to the file it accuses?")):
        c = collections.Counter(r[route] for r in rows)
        scored = (c["DISCRIMINATES"] + c["NO_DISCRIMINATION_OR_INEFFECTIVE_FIX"]
                  + c["ALWAYS_FIRES_NEVER_QUIET"])
        print(f"  {label}")
        for k, v in c.most_common():
            print(f"    {k:<42}{v:>5}")
        if scored:
            q = c["DISCRIMINATES"]
            print(f"    -> of {scored} SCORED findings, {q} went quiet "
                  f"({q/scored*100:.1f}%)")
        print()
    both = [r for r in rows if r["route_a"] in ("DISCRIMINATES", "NO_DISCRIMINATION_OR_INEFFECTIVE_FIX")
            and r["route_b"] in ("DISCRIMINATES", "ALWAYS_FIRES_NEVER_QUIET")]
    if both:
        agree = sum(1 for r in both if (r["route_a"] == "DISCRIMINATES")
                    == (r["route_b"] == "DISCRIMINATES"))
        print(f"  BOTH ROUTES SCORED: {len(both)} findings; they agree on "
              f"{agree} ({agree/len(both)*100:.1f}%).")
        print("  The routes' confounds are disjoint, so agreement is worth more than")
        print("  either route alone and disagreement localises which confound bit.")


if __name__ == "__main__":
    raise SystemExit(main())
