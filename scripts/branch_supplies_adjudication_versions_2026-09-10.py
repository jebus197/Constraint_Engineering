#!/usr/bin/env python3
"""Task 8.3: rebuild the figure that justifies keeping `exp39-experimental`.

MEASURED, and committed alongside the figures (`measured-rate-travels-with-its-script`).

THE FIGURE AS IT STOOD. "20 of 21 falsifiers reproduce against an earlier stored
version" exists only as prose and as a code comment at
`scripts/adjudicate_by_repair.py:270`. The rule covering this names code comments
explicitly, so a comment is not an exemption.

IT DOES NOT REPRODUCE FROM THE COMMITTED OUTPUT, and the reason is structural
rather than a lost file. `experimental_notes/data/adjudication_by_repair.json`
records PAIR verdicts -- 133 rows, 7 NO_BASELINE, 15 adjudicated at a non-HEAD
version -- while the claim is about FINDINGS. Counted as findings the committed
data gives 9, 16 and 25 for the nearest available quantities, and none of them is
21. The per-finding search the comment describes was never stored.

RE-DERIVING IT WOULD MEAN RE-RUNNING THE ADJUDICATOR, and that routine WRITES TO
THE TARGET FILE -- `target.write_text(txt)` inside a version loop, restored in a
`finally`. Running it to reconstruct a figure is not worth writing to real
targets, so it is not done here and the reason is recorded rather than the
attempt.

WHAT IS REBUILT INSTEAD IS THE ACTUAL QUESTION. The comment's own justification
for the branch is not the 20 of 21. It is `_versions`, whose docstring says
"`--all` is load-bearing ... the branch `exp39-experimental` holds 107 commits
main does not". That IS the figure that justifies keeping the branch, it is
answerable read-only, and it is answered below.

REVISED 2026-09-17 (task 8.3 correction, panel round 16). 4 defects found by
execution, each repaired here:

  1. THE ATTRIBUTION SENTENCE WAS A CONSTANT. It printed "1 came from local main
     ... 40%" on every run, while the measurement that day gave 0 from local
     main and 20%. It is now computed from the ref sets the run measures.
  2. THE BRANCH WAS LOOKED UP BY 1 NAME ONLY. A local-path clone carries the
     history under `refs/remotes/origin/exp39-experimental` and the pin tag, and
     the script still reported it UNAVAILABLE and exited 0. The branch now
     resolves from `refs/heads/`, then any `refs/remotes/<remote>/`, then the tag
     `exp39-experimental-pinned-2026-09-10`, and the run names which one it used.
  3. AN UNAVAILABLE MEASUREMENT EXITED 0. When nothing resolves, the run prints
     UNAVAILABLE with no attribution numbers and exits 4.
  4. "SUPPLIED BY THE BRANCH" WAS NOT "SUPPLIED ONLY BY THE BRANCH". The pin tag
     peels to the branch tip, so every version the branch supplies is also
     reachable from the tag. Each off-main version is now printed with every ref
     that reaches it, and the versions reached by the branch ref and nothing else
     are counted separately.

THE PIN. `python3 scripts/branch_supplies_adjudication_versions_2026-09-10.py
--write-sidecar` writes `experimental_notes/data/branch_supplies_versions.json`:
the ref tips measured, the counts, and every off-main version with its ref set.
`bench/tests/test_branch_supplies_versions_2026-09-10.py` recomputes the figure
from those recorded tips, so the dated figure is held exactly, and a later commit
to a target file does not silently change what the task entry quotes.
"""
from __future__ import annotations

import argparse
import datetime
import json
import pathlib
import subprocess
import sys

# `--help` MUST NOT ACT, AND ON A SIBLING OF THIS SCRIPT IT DESTROYED 54,480
# BYTES. Measured 2026-09-11: `--help` on `scripts/assemble_panel_record_0819.py`
# rewrote a 55,814-byte verbatim panel record down to 1,334 and exited 0, because
# the flag fell through to the script's ordinary work.
#
# THIS SCRIPT NOW TAKES A FLAG, `--write-sidecar`, so it parses with argparse at
# the top of `main()`, before any git call or write. argparse answers `--help`
# and refuses an unknown argument with exit 2 before any work. The earlier
# `_cli_help.answer_help` call is removed rather than kept alongside, because
# `answer_help` refuses every argument and would refuse `--write-sidecar` too.

REPO = pathlib.Path(__file__).resolve().parents[1]
BRANCH = "exp39-experimental"
PIN_TAG = "exp39-experimental-pinned-2026-09-10"
MAIN_REF = "refs/remotes/origin/main"
SIDECAR = REPO / "experimental_notes" / "data" / "branch_supplies_versions.json"
EXIT_UNAVAILABLE = 4


def _shown(p: pathlib.Path) -> str:
    """A path relative to the repository where it lies inside it, else in full."""
    try:
        return str(p.relative_to(REPO))
    except ValueError:
        return str(p)


def _git(*args: str) -> str:
    r = subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} exited {r.returncode}: "
                           f"{r.stderr.strip()[:300]}")
    return r.stdout


def shas(revs, path: str) -> set:
    """Full hashes of the commits touching `path` reachable from `revs`.

    A failed `git log` RAISES. Returning an empty set there would read as "this
    ref supplies nothing", which is a measurement, not a failure.
    """
    revs = [revs] if isinstance(revs, str) else list(revs)
    return set(_git("log", *revs, "--format=%H", "--", path).split())


def in_repo_targets() -> list:
    out = set()
    for r in sorted((REPO / "bench" / "logs").glob("exp*/exp*_report.json")):
        try:
            d = json.loads(r.read_text())
        except (ValueError, OSError):
            continue
        t = d.get("target_file", "")
        if t and not t.startswith("/"):
            out.add(t)
    return sorted(out)


def live_tips() -> dict:
    """Every ref `git log --all` walks, as {refname: object id}, plus HEAD."""
    tips = {}
    for line in _git("for-each-ref", "--format=%(refname) %(objectname)").splitlines():
        name, oid = line.split()
        if name.endswith("/HEAD"):
            continue            # symbolic; its target is listed under its own name
        tips[name] = oid
    tips["HEAD"] = _git("rev-parse", "HEAD").strip()
    return tips


def resolve_branch(tips: dict) -> str | None:
    """The ref the branch is measured through, in a fixed order of preference."""
    if f"refs/heads/{BRANCH}" in tips:
        return f"refs/heads/{BRANCH}"
    remotes = sorted(r for r in tips
                     if r.startswith("refs/remotes/") and len(r.split("/")) == 4
                     and r.split("/")[3] == BRANCH)
    if remotes:
        return remotes[0]
    if f"refs/tags/{PIN_TAG}" in tips:
        return f"refs/tags/{PIN_TAG}"
    return None


def measure(tips: dict | None = None, targets: list | None = None) -> dict:
    """The measurement. `tips=None` measures the live refs; a dict replays a pin."""
    tips = live_tips() if tips is None else dict(tips)
    targets = in_repo_targets() if targets is None else list(targets)
    branch_ref = resolve_branch(tips)
    if branch_ref is None or MAIN_REF not in tips:
        return {"available": False, "branch_ref": branch_ref,
                "main_ref_present": MAIN_REF in tips}

    all_tips = sorted(set(tips.values()))
    main_tip = tips[MAIN_REF]
    reach: dict = {}

    def reaches(ref: str, t: str) -> set:
        if (ref, t) not in reach:
            reach[(ref, t)] = shas(tips[ref], t)
        return reach[(ref, t)]

    total = 0
    versions = []
    for t in targets:
        every = shas(all_tips, t)
        total += len(every)
        for s in sorted(every - shas(main_tip, t)):
            who = sorted(r for r in tips if s in reaches(r, t))
            versions.append({"target": t, "sha": s, "refs": who,
                             "from_branch": branch_ref in who,
                             "branch_only": who == [branch_ref]})
    from_branch = sum(v["from_branch"] for v in versions)
    return {
        "available": True,
        "branch_ref": branch_ref,
        "branch_tip": tips[branch_ref],
        "main_ref": MAIN_REF,
        "main_tip": main_tip,
        "targets": targets,
        "n_targets": len(targets),
        "total": total,
        "off_main": len(versions),
        "from_branch": from_branch,
        "branch_only": sum(v["branch_only"] for v in versions),
        "not_from_branch": len(versions) - from_branch,
        "versions": versions,
    }


def attribution(m: dict) -> str:
    """The attribution sentence, computed from the measured ref sets.

    It replaces a constant that printed "1 from local main ... 40%" on every run.
    """
    off, b = m["off_main"], m["from_branch"]
    groups: dict = {}
    for v in m["versions"]:
        if not v["from_branch"]:
            key = ", ".join(v["refs"]) or "(no named ref)"
            groups[key] = groups.get(key, 0) + 1
    parts = [f"ATTRIBUTION MATTERS AND IS NOT ASSUMED. {off} stored version(s) are "
             f"off {m['main_ref']}, and {b} are reachable from {m['branch_ref']}."]
    if groups:
        parts.append(f"The other {off - b}, by the refs that reach them:")
        for key, n in sorted(groups.items()):
            parts.append(f"{n} reachable only from [{key}].")
    else:
        parts.append("None comes from any other ref.")
    if b:
        parts.append(f"Crediting the branch with all {off} would overstate its "
                     f"contribution by {(off - b) / b:.4%}.")
    else:
        parts.append("The branch supplies none, so no overstatement ratio exists.")
    parts.append(f"{m['branch_only']} of the {b} are reached by {m['branch_ref']} "
                 f"and by no other ref.")
    return " ".join(parts)


def intervals(k: int, n: int) -> dict:
    from statsmodels.stats.proportion import proportion_confint
    from scipy.stats import beta as sbeta
    lo, hi = proportion_confint(k, n, method="wilson")
    lo_c, hi_c = proportion_confint(k, n, method="beta")
    slo = sbeta.ppf(0.025, k, n - k + 1) if k else 0.0
    return {"wilson": [lo, hi], "clopper_pearson": [lo_c, hi_c],
            "clopper_pearson_lo_scipy": slo}


def _print_negative_half() -> None:
    print("--- the 20 of 21, checked against the committed output ---")
    p = REPO / "experimental_notes" / "data" / "adjudication_by_repair.json"
    if not p.is_file():
        print("  no committed adjudication output in this clone")
        return
    rows = json.loads(p.read_text())["rows"]
    nb = [r for r in rows if r["verdict"] == "NO_BASELINE"]
    ver = [r for r in rows if r.get("baseline") not in (None, "HEAD")]
    f_nb, f_ver = set(), set()
    for r in nb:
        f_nb |= {(r["run"], r["a"]), (r["run"], r["b"])}
    for r in ver:
        f_ver |= {(r["run"], r["a"]), (r["run"], r["b"])}
    print(f"  pair rows: {len(rows)}   NO_BASELINE: {len(nb)}   "
          f"adjudicated at a non-HEAD version: {len(ver)}")
    print(f"  distinct FINDINGS: {len(f_nb)} in NO_BASELINE pairs, "
          f"{len(f_ver)} adjudicated at a version, {len(f_nb | f_ver)} in union")
    print("  NONE of these is 21. The output records PAIRS; the claim is about")
    print("  FINDINGS, and the per-finding search was never stored.")


def main(argv: list | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--write-sidecar", action="store_true",
                    help=f"also write the measurement to {_shown(SIDECAR)}")
    args = ap.parse_args(argv)

    _print_negative_half()

    print(f"\n--- what {BRANCH} supplies to the version search ---")
    tips = live_tips()
    m = measure(tips)
    if not m["available"]:
        print(f"  UNAVAILABLE. Looked for refs/heads/{BRANCH}, "
              f"refs/remotes/<remote>/{BRANCH} and refs/tags/{PIN_TAG}: "
              f"{'found ' + m['branch_ref'] if m['branch_ref'] else 'none resolves'}. "
              f"{MAIN_REF} {'resolves' if m['main_ref_present'] else 'does not resolve'}.")
        print("  Nothing is measured here, so no count and no attribution is printed.")
        if args.write_sidecar:
            print(f"  --write-sidecar refused: {_shown(SIDECAR)} left unchanged.")
        return EXIT_UNAVAILABLE

    print(f"  branch measured through           : {m['branch_ref']} ({m['branch_tip'][:7]})")
    print(f"  off-main measured against         : {m['main_ref']} ({m['main_tip'][:7]})")
    print(f"  in-repo targets across archived runs: {m['n_targets']}")
    print(f"  stored versions reachable with --all: {m['total']}")
    print(f"  reachable from no ref on origin/main: {m['off_main']}")
    print(f"  of those, supplied by {BRANCH}      : {m['from_branch']}")
    print(f"  of those, supplied by it and no other ref: {m['branch_only']}")
    print("  every off-main version, and every ref that reaches it:")
    for v in m["versions"]:
        mark = "B" if v["from_branch"] else "-"
        print(f"   {mark} {v['sha'][:7]}  {v['target']}")
        print(f"       refs: {', '.join(v['refs'])}")

    ci = intervals(m["from_branch"], m["total"])
    lo, hi = ci["wilson"]
    lo_c, hi_c = ci["clopper_pearson"]
    print(f"\n  {m['from_branch']}/{m['total']} = {m['from_branch'] / m['total']:.4%}")
    print(f"  Wilson 95%          : [{lo:.4%}, {hi:.4%}]  (statsmodels)")
    print(f"  Clopper-Pearson 95% : [{lo_c:.4%}, {hi_c:.4%}]")
    print(f"  Clopper-Pearson 95% : [{ci['clopper_pearson_lo_scipy']:.4%}, ...]  "
          f"(scipy; agrees to {abs(ci['clopper_pearson_lo_scipy'] - lo_c):.1e})")

    print("\n  " + attribution(m))

    if SIDECAR.is_file():
        pin = json.loads(SIDECAR.read_text())
        keys = ("n_targets", "total", "off_main", "from_branch", "branch_only")
        drift = {k: (pin[k], m[k]) for k in keys if pin[k] != m[k]}
        print(f"\n  pinned in {_shown(SIDECAR)} at {pin['head'][:7]} "
              f"({pin['measured_at_utc']}): "
              + ", ".join(f"{k} {pin[k]}" for k in keys))
        print("  live refs differ from the pin: " + (
            ", ".join(f"{k} {a} -> {b}" for k, (a, b) in drift.items())
            if drift else "no"))

    if args.write_sidecar:
        record = {
            "measured_at_utc": datetime.datetime.now(datetime.timezone.utc)
                               .isoformat(timespec="seconds"),
            "head": tips["HEAD"],
            "producer": "scripts/branch_supplies_adjudication_versions_2026-09-10.py "
                        "--write-sidecar",
            "tips": tips,
            **{k: v for k, v in m.items() if k != "available"},
            "intervals": ci,
        }
        SIDECAR.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
        print(f"\n  wrote {_shown(SIDECAR)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
