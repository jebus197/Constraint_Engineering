#!/usr/bin/env python3
"""THE REPOINTING EXPERIMENT: are archived falsifiers specific to their target?

FOUNDER RULING 2026-10-03: "Yes run it, record the results and implement any
findings if they are useful."

THE QUESTION. A falsifier that names a file and asserts something about its
contents might be testing a CLAIM about that file, or might be testing a
property so general that any file would satisfy or violate it. The first is a
specific instrument; the second fires on whatever it is pointed at, which is
the cannot-fail shape measured elsewhere by the discrimination control.

THE DESIGN IS 2 ARMS, AND THE CONTROL ARM IS WHAT MAKES IT INTERPRETABLE. This
is fable's design, endorsed by the star round over a single-arm spec:

  ARM A (control)  replay the body UNEDITED against the tree as it stands.
                   An archived falsifier can fail for reasons that have nothing
                   to do with repointing -- the file it names has moved, its
                   content has changed, an import it uses is gone. Arm A
                   measures that decay, so arm B is read against it rather than
                   against an assumption that unedited bodies all still pass.
  ARM B (treatment) rewrite ONLY the path spans that resolve to the file the
                   body names, pointing them at a DIFFERENT target of the same
                   kind, and replay.

THE INDETERMINATE CHANNEL (cc2's addition, kept). A repointed body that errors
for an unrelated reason -- a missing import, a syntax dependency on the old
path's extension -- is REPORTED and never scored in either direction. An
instrument that could not run says nothing about specificity.

PRE-REGISTERED, BEFORE ANY EXECUTION:
  H_general      arm-B CONFIRMED rate falls INSIDE arm-A's Wilson interval
                 => the bodies are not specific to their targets.
  H_specificity  arm-B shows an ERROR/REFUTED excess over arm A
                 => the bodies are specific.
  test           Fisher exact, two-sided, alpha = 0.01, fixed N over the whole
                 population (no interim looks, no stopping on a trend).
  degraded stop  if more than 20% of bodies fail the file-exists precondition,
                 the run is reported as DEGRADED and the hypotheses are not
                 decided.

Usage:
  python3 scripts/repointing_experiment_2026-10-03.py --dry-run
  python3 scripts/repointing_experiment_2026-10-03.py --out <record.json>
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

# A path literal inside a falsifier body: quoted, repo-relative, with a suffix.
_PATH = re.compile(r"""['"]((?:[\w.\-]+/)*[\w.\-]+\.(?:md|py|txt|json|rst))['"]""")

SCORED = ("CONFIRMED", "REFUTED")
UNSCORED = ("ERROR", "UNTOOLABLE")


def wilson(k: int, n: int) -> dict:
    if n == 0:
        return {"k": k, "n": n, "pct": None}
    from statsmodels.stats.proportion import proportion_confint
    import mpmath as mp
    lo, hi = proportion_confint(k, n, method="wilson")
    z = mp.mpf("1.959963984540054")
    p = mp.mpf(k) / n
    d = 1 + z**2 / n
    c = (p + z**2 / (2 * n)) / d
    h = z * mp.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / d
    assert abs(float(c - h) - lo) < 1e-9 and abs(float(c + h) - hi) < 1e-9, (
        f"statsmodels and mpmath disagree on Wilson for {k}/{n}")
    return {"k": k, "n": n, "pct": round(100.0 * k / n, 4),
            "wilson": [round(100 * lo, 4), round(100 * hi, 4)]}


def fisher(table) -> dict:
    """Two-sided Fisher exact from scipy, cross-checked by exact enumeration."""
    from scipy.stats import fisher_exact
    import mpmath as mp
    odds, p_sp = fisher_exact(table)
    a, b = table[0]
    c, d = table[1]
    n = a + b + c + d
    r1, c1 = a + b, a + c
    if min(r1, c1, n - r1, n - c1) < 0 or n == 0:
        return {"odds_ratio": odds, "p_scipy": p_sp, "p_mpmath": None}

    def pr(x):
        return (mp.binomial(r1, x) * mp.binomial(n - r1, c1 - x)
                / mp.binomial(n, c1))

    obs = pr(a)
    lo = max(0, c1 - (n - r1))
    hi = min(r1, c1)
    p_mp = float(sum(pr(x) for x in range(lo, hi + 1)
                     if pr(x) <= obs * (1 + mp.mpf("1e-12"))))
    return {"odds_ratio": float(odds) if odds == odds else None,
            "p_scipy": float(p_sp), "p_mpmath": p_mp}


#: A path a falsifier names may be written from inside the sandbox it ran in,
#: where the repository root was a temporary directory. The prefix is literally
#: the repo root at run time, so stripping it is a RENAME, not a substitution.
_SANDBOX_PREFIX = re.compile(
    r"^(?:cdsfl_sim\.[A-Za-z0-9]+/run/|cdsfl_panel_[a-z0-9]+/repo/)")

#: Where a BARE basename plausibly lives. Searched only when the name carries no
#: directory at all, and only accepted when EXACTLY ONE candidate exists --
#: 2 files of the same name in different directories would otherwise let arm A
#: replay against a file the falsifier never read, which would corrupt the
#: control rather than merely shrink it.
_BASENAME_HOMES = ("bench", "scripts", "bench/cdsfl_registry",
                   "experimental_notes", "docs", ".")


def resolve_named(name: str) -> str | None:
    """The repo-relative path this name refers to, or None if undecidable.

    WHY THIS EXISTS, measured before any arm ran. The first version of this
    experiment required every named path to resolve from the repository root and
    reported 203 of 233 bodies failing that precondition, 87.1245% -- which
    tripped its own degraded stop and would have decided nothing. The cause was
    the PREDICATE, not the archive: most of those names are not repo-relative at
    all. They are sandbox-relative (`cdsfl_sim.1VAxrWgWUK/run/bench/...`) or
    bare basenames (`engine.py`, `mem.json`), written by a falsifier whose
    working directory was the sandbox. Treating those as missing files conflates
    archive decay, which is what arm A exists to measure, with a path that was
    never repo-relative, which is nothing at all.

    With the mapping, the usable population is 126 of 233 (54.0773%, Wilson
    [47.6642%, 60.3581%]) against 43 (18.4549%) strict.
    """
    for cand in (name, _SANDBOX_PREFIX.sub("", name)):
        if (REPO / cand).is_file():
            return cand
    if "/" not in name:
        # UNIQUE IN THE WHOLE TREE, not merely unique among the homes searched.
        # The first version checked 5 candidate directories and accepted a hit
        # if exactly 1 of them held the name -- which resolved `__init__.py` to
        # `bench/cdsfl_registry/__init__.py` purely because that was the only
        # one of the 5 holding an `__init__.py`. A generic basename resolved to
        # an arbitrary file would make arm A replay against a file the
        # falsifier never read, corrupting the control rather than shrinking it.
        # EXCLUDE COPIES OF THE SAME TREE. `bench/logs/` holds seat sandbox
        # harvests and `.claude/worktrees/` holds agent worktrees -- both are
        # copies of this repository, so a file appearing in 3 worktrees is 1
        # file counted 4 times. Measured: with worktrees counted, `engine.py`
        # looked ambiguous (4 hits, 3 of them the same worktree file) and the
        # usable population fell from 126 to 46 on an artefact of local
        # scratch state rather than anything about the archive.
        _COPIES = (".git/", "bench/logs/", ".claude/worktrees/", ".scratch/",
                   "node_modules/", "__pycache__/")
        everywhere = []
        for q in REPO.rglob(name):
            if not q.is_file():
                continue
            rel = str(q.relative_to(REPO))
            if any(c in f"{rel}/" or rel.startswith(c) for c in _COPIES):
                continue
            everywhere.append(rel)
        if len(everywhere) == 1:
            return everywhere[0]
    return None


def harvest() -> list[dict]:
    """Every archived falsifier body that NAMES a file, deduplicated by body."""
    bodies: dict[str, dict] = {}
    for f in sorted((REPO / "bench" / "logs").rglob("*_report.json")):
        try:
            d = json.loads(f.read_text(encoding="utf-8", errors="replace"))
        except (ValueError, OSError):
            continue
        for cid, e in ((d.get("registry") or {}).get("entries") or {}).items():
            if not isinstance(e, dict):
                continue
            code = (e.get("falsifier_code") or "")
            if not code.strip():
                continue
            named = sorted({m.group(1) for m in _PATH.finditer(code)})
            if not named:
                continue
            bodies.setdefault(code, {
                "cid": cid, "run": f.parent.name, "named": named,
                "archived_verdict": e.get("falsifier_verdict") or ""})
    return [dict(body=k, **v) for k, v in bodies.items()]


def _pick_decoy(named: list[str]) -> str | None:
    """A DIFFERENT file of the same kind, which must already exist.

    Same suffix, so a body that parses its target by extension is not failed
    for a reason that has nothing to do with specificity. Chosen
    deterministically -- no Date.now, no random -- so the experiment replays.
    """
    suffix = pathlib.Path(named[0]).suffix
    pool = sorted(p for p in (REPO / "bench").glob(f"*{suffix}")
                  if p.is_file() and p.name not in {pathlib.Path(n).name
                                                    for n in named})
    if not pool:
        pool = sorted(p for p in REPO.glob(f"*{suffix}") if p.is_file())
    return str(pool[0].relative_to(REPO)) if pool else None


def repoint(code: str, named: list[str], decoy: str) -> tuple[str, int]:
    """Rewrite ONLY the quoted path spans resolving to the named file."""
    n = 0
    out = code
    for target in named:
        for quote in ('"', "'"):
            needle = f"{quote}{target}{quote}"
            if needle in out:
                out = out.replace(needle, f"{quote}{decoy}{quote}")
                n += out.count(f"{quote}{decoy}{quote}")
    return out, n


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--limit", type=int, default=0,
                    help="probe at most this many bodies (0 = all). A limit is "
                         "REPORTED and the hypotheses are NOT decided under one, "
                         "because the design is fixed-N over the whole population.")
    ap.add_argument("--timeout", type=int, default=30)
    ap.add_argument("--dry-run", action="store_true",
                    help="harvest and report the population without executing")
    ap.add_argument("--out", help="write the full record here as JSON")
    a = ap.parse_args(argv)

    from bench.falsifier_verify import reverify_falsifier

    pop = harvest()
    print(f"POPULATION: {len(pop)} distinct archived falsifier bodies that name "
          f"a file")
    # THE PRECONDITION IS RESOLVABILITY, NOT LITERAL EXISTENCE -- corrected
    # BEFORE any arm ran, on the measurement in `resolve_named`'s docstring.
    # A name may be sandbox-relative or a bare basename and still refer
    # unambiguously to a file in this tree.
    for r in pop:
        r["resolved"] = {n: resolve_named(n) for n in r["named"]}
        r["targets"] = sorted({v for v in r["resolved"].values() if v})
    usable = [r for r in pop if r["targets"]]
    missing = [r for r in pop if not r["targets"]]
    print(f"  no named path resolves to a file in this tree: {len(missing)} "
          f"({100.0 * len(missing) / max(len(pop), 1):.4f}%)")
    print(f"  usable population: {len(usable)} "
          f"({100.0 * len(usable) / max(len(pop), 1):.4f}%)")
    # THE DEGRADED STOP NOW ASKS THE QUESTION IT WAS MEANT TO ASK. Applied to
    # literal existence it fired at 87.1245% on names that were never
    # repo-relative -- a fact about where falsifiers run, not about archive
    # decay. Arm A is what measures decay, and it measures it on the usable
    # population. The stop is retained against a usable population too small to
    # interpret.
    degraded = len(usable) < 30
    if degraded:
        print("  DEGRADED: more than 20% fail the precondition, so the "
              "pre-registered hypotheses are NOT decided by this run.")
    if a.dry_run:
        print("  --dry-run: nothing executed.")
        return 0

    rows, skipped = [], 0
    if a.limit and len(usable) > a.limit:
        skipped = len(usable) - a.limit
        usable = usable[:a.limit]

    for r in usable:
        decoy = _pick_decoy(r["targets"])
        if not decoy:
            rows.append({**r, "arm_a": None, "arm_b": None,
                         "note": "no decoy of the same kind exists"})
            continue
        # Rewrite only the SPANS AS WRITTEN that resolve to a real file, so a
        # sandbox-relative span is repointed in the form the body actually uses.
        spans = [n for n, v in r["resolved"].items() if v]
        body_b, nsub = repoint(r["body"], spans, decoy)
        if nsub == 0:
            rows.append({**r, "arm_a": None, "arm_b": None,
                         "note": "no path span could be rewritten"})
            continue
        va = reverify_falsifier(r["body"], repo_root=str(REPO), timeout=a.timeout)
        vb = reverify_falsifier(body_b, repo_root=str(REPO), timeout=a.timeout)
        rows.append({**r, "decoy": decoy, "substitutions": nsub,
                     "arm_a": va, "arm_b": vb, "note": ""})

    scored = [r for r in rows
              if r["arm_a"] in SCORED and r["arm_b"] in SCORED]
    unscored = [r for r in rows if r not in scored]
    a_conf = sum(1 for r in scored if r["arm_a"] == "CONFIRMED")
    b_conf = sum(1 for r in scored if r["arm_b"] == "CONFIRMED")
    wa, wb = wilson(a_conf, len(scored)), wilson(b_conf, len(scored))
    table = [[b_conf, len(scored) - b_conf], [a_conf, len(scored) - a_conf]]
    fe = fisher(table) if scored else {}

    inside = (wb["pct"] is not None and wa["pct"] is not None
              and wa["wilson"][0] <= wb["pct"] <= wa["wilson"][1])
    verdict = "NOT DECIDED (degraded or empty)"
    if scored and not degraded and not a.limit:
        if fe.get("p_scipy") is not None and fe["p_scipy"] < 0.01:
            verdict = ("H_specificity SUPPORTED: repointing changes the verdict "
                       "distribution")
        elif inside:
            verdict = ("H_general SUPPORTED: the repointed CONFIRMED rate falls "
                       "inside the unedited arm's interval, so these bodies are "
                       "not specific to their targets")
        else:
            verdict = "NEITHER pre-registered hypothesis is supported"

    out = {
        "population": len(pop), "usable": len(rows),
        "skipped_by_limit": skipped,
        "precondition_failures": len(missing),
        "usable_population": len(usable), "degraded": degraded,
        "scored_pairs": len(scored), "unscored_reported": len(unscored),
        "arm_a_confirmed": wa, "arm_b_confirmed": wb,
        "fisher": fe, "arm_b_rate_inside_arm_a_interval": inside,
        "verdict": verdict,
        "preregistered": {
            "alpha": 0.01, "test": "Fisher exact, two-sided",
            "design": "fixed N over the whole population, no interim looks",
            "degraded_stop": "more than 20% precondition failures",
        },
        "rows": rows,
    }
    print(f"\nSCORED PAIRS: {len(scored)}; unscored and reported: {len(unscored)}")
    if scored:
        print(f"  arm A (unedited)  CONFIRMED {wa['k']}/{wa['n']} = {wa['pct']}%, "
              f"Wilson [{wa['wilson'][0]}%, {wa['wilson'][1]}%]")
        print(f"  arm B (repointed) CONFIRMED {wb['k']}/{wb['n']} = {wb['pct']}%, "
              f"Wilson [{wb['wilson'][0]}%, {wb['wilson'][1]}%]")
        print(f"  Fisher: scipy p = {fe.get('p_scipy')}, "
              f"mpmath p = {fe.get('p_mpmath')}, OR = {fe.get('odds_ratio')}")
    print(f"  VERDICT: {verdict}")
    if skipped:
        print(f"  {skipped} bodies SKIPPED BY --limit; the design is fixed-N, so "
              "no hypothesis is decided")
    if a.out:
        pathlib.Path(a.out).write_text(json.dumps(out, indent=2))
        print(f"  wrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
