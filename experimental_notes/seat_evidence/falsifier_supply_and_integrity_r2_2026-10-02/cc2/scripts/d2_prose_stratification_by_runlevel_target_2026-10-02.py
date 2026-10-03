# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'falsifier_supply_and_integrity_r2_2026-10-02', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 2c8dac1a8a26a8cb36ca515da07e8e50048263d1bc67555e34ca0a3ac8c5b049
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""CAUSE 3, re-measured after JOINING the RUN-LEVEL target onto the findings.

WHY THIS FILE EXISTS. `scripts/repro_supply_causes_2026-10-02.py` reports
"CAUSE 3 prose vs code targets: NOT MEASURABLE". It reads `target_file` off the
same artefact it took the FINDING from, and its dedup rule prefers whichever
artefact carries a falsifier BODY. Measured here: `runner_state.json` carries a
registry but NO run-level `target_file`, while `*_report.json` carries the
target -- so whenever the body-bearing record was the runner_state, the target
was silently dropped to "". That is why only 52 of 624 post-feature criticals
had a target and why NONE of them were prose: the prose runs are exactly the
ones whose chosen records came from runner_state.json.

PROSE TARGET PROVENANCE EXISTS. The run-level report for
`prose_convergence_run1b_2026-10-02_20261002T044234Z` records
  target_file: 'bench/BUILD_BOT_TEST_BENCH_FIX_SPEC.md'
  target_kind: {'kind': 'prose', 'reason': 'suffix .md', ...}
It is simply never copied onto the FINDING entries. So the fix is a JOIN, not a
new measurement: resolve the target ONCE PER RUN DIRECTORY, from the
runner-authored artefacts, and attach it to every critical of that run.

WHAT IS REUSED, AND FROM WHERE (imported by path -- the filenames are not legal
module names, so importlib is used rather than a copy):
  scripts/falsifier_supply_decomposition_2026-10-02.py -> `_body`, `classify`,
      `wilson` (the 5-state decomposition and the dual Wilson interval)
  scripts/repro_supply_causes_2026-10-02.py            -> `expno`, `fisher`
      (the post-feature population cut and the dual Fisher exact test)
The finding population is harvested with the SAME glob, SAME severity floor and
SAME (run_dir, cid) dedup as `repro_supply_causes`, so the denominator is the
SAME 624 and the result is comparable. The ONLY change is where the target
comes from.

FOUR OUTCOMES ARE REPORTED, NOT ONE, because "no falsifier body at all" is
ambiguous and the ambiguity decides the answer:
  STRICT      nothing written AND nothing recorded (classify's "NOTHING
              WRITTEN AND NOTHING RECORDED") -- a declination is NOT in it
  LOOSE       no body retained on the record, whatever verdict it carries
  ERROR       written, and it broke
  UNTOOLABLE  the ladder was asked and declined
A rate with zero events in both arms is reported as UNDECIDABLE with its exact
denominator rather than dressed up as a null result.

Every odds ratio and p-value is computed by scipy AND by an independent mpmath
hypergeometric sum; every proportion carries a Wilson 95% interval from
statsmodels AND from an independent mpmath closed form. Disagreement is printed.
No Wolfram result is used.
"""
from __future__ import annotations

import collections
import importlib.util
import json
import pathlib
import sys

# `_cli_help` lives in scripts/. Locate it rather than assume a depth.
for _cand in (pathlib.Path(__file__).resolve().parent,
              *pathlib.Path(__file__).resolve().parents):
    if (_cand / "_cli_help.py").is_file():
        sys.path.insert(0, str(_cand))
        break
from _cli_help import answer_help  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
LOGS = ROOT / "bench" / "logs"
CRITICAL = 0.7

#: Runner-authored artefacts, in the order they are TRUSTED for the run-level
#: target. The report is the runner's final word; the other two are fallbacks.
ARTEFACT_ORDER = ("report", "runner_state.json", "checkpoint.json")

PROSE_SUFFIXES = {".md", ".txt", ".rst"}
CODE_SUFFIXES = {".py"}


def _load(path: pathlib.Path, name: str):
    """Import a script whose filename is not a legal module name."""
    spec = importlib.util.spec_from_file_location(name, str(path))
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


DEC = _load(SCRIPTS / "falsifier_supply_decomposition_2026-10-02.py",
            "_d2_decomposition")
REP = _load(SCRIPTS / "repro_supply_causes_2026-10-02.py", "_d2_repro")

_body = DEC._body
classify = DEC.classify
wilson = DEC.wilson
expno = REP.expno
fisher = REP.fisher


# ---------------------------------------------------------------------------
# 1. RUN-LEVEL TARGET PROVENANCE
# ---------------------------------------------------------------------------
def _artefact_kind(name: str):
    if name in ("runner_state.json", "checkpoint.json"):
        return name
    if name.endswith("_report.json"):
        return "report"
    return None


def _run_level_target(data: dict):
    """The target the RUNNER recorded for the whole run, and its declared kind.

    Only run-level fields are read. `checkpoint.json` also carries a
    `target_file` on INDIVIDUAL findings inside `all_findings`; that is a claim
    about one finding, not run provenance, and is deliberately NOT used here.
    """
    cfg = data.get("config") if isinstance(data.get("config"), dict) else {}
    target = str((cfg or {}).get("target_file") or data.get("target_file") or "")
    tk = data.get("target_kind")
    if isinstance(tk, dict):
        kind = tk.get("kind")
    elif isinstance(tk, str):
        kind = tk
    else:
        kind = None
    return target, (str(kind) if kind else None)


def walk_run_dirs():
    """Every directory under bench/logs/ holding a runner-authored artefact.

    Recursive: archived sandbox harvests nest whole copies of bench/logs
    several levels down, and a run directory is a run directory wherever it
    sits. Keyed by the path RELATIVE to bench/logs so a nested copy is a
    distinct run directory rather than silently shadowing the original.
    """
    per_dir = {}
    unreadable = 0
    artefacts = 0
    for f in sorted(LOGS.rglob("*.json")):
        kind = _artefact_kind(f.name)
        if kind is None:
            continue
        artefacts += 1
        try:
            data = json.loads(f.read_text(encoding="utf-8", errors="replace"))
        except (ValueError, OSError):
            unreadable += 1
            continue
        if not isinstance(data, dict):
            continue
        rel = str(f.parent.relative_to(LOGS))
        slot = per_dir.setdefault(rel, {"artefacts": {}, "name": f.parent.name})
        target, tkind = _run_level_target(data)
        slot["artefacts"][kind] = {"target": target, "kind": tkind}
    for slot in per_dir.values():
        slot["target"] = ""
        slot["target_kind"] = None
        slot["source"] = None
        for want in ARTEFACT_ORDER:
            a = slot["artefacts"].get(want)
            if a and a["target"]:
                slot["target"] = a["target"]
                slot["target_kind"] = a["kind"]
                slot["source"] = want
                break
    return per_dir, unreadable, artefacts


def arm_of(target: str) -> str:
    suf = pathlib.PurePosixPath(target.replace("\\", "/")).suffix.lower()
    if suf in PROSE_SUFFIXES:
        return "prose"
    if suf in CODE_SUFFIXES:
        return "code"
    return "other"


# ---------------------------------------------------------------------------
# 2. FINDING POPULATION -- identical harvest to repro_supply_causes
# ---------------------------------------------------------------------------
def harvest_criticals():
    """(run_dir_name, cid) -> entry, with repro_supply_causes' exact rule.

    Same glob (`bench/logs/*/runner_state.json`, `bench/logs/*/*_report.json`),
    same severity floor, same body-preferring dedup. The target is NOT taken
    here; that is the whole point of this file.
    """
    rows = {}
    provenance = {}
    for name in ("runner_state.json", "*_report.json"):
        for f in sorted(LOGS.glob(f"*/{name}")):
            try:
                data = json.loads(f.read_text(encoding="utf-8", errors="replace"))
            except (ValueError, OSError):
                continue
            reg = (data.get("registry") or {}).get("entries") or {}
            for cid, e in reg.items():
                if not isinstance(e, dict):
                    continue
                if (e.get("severity") or 0.0) < CRITICAL:
                    continue
                key = (f.parent.name, cid)
                prev = rows.get(key)
                if prev is None or (not _body(prev) and _body(e)):
                    rows[key] = e
                    provenance[key] = f.name
    return rows, provenance


# ---------------------------------------------------------------------------
# 3. REPORTING HELPERS
# ---------------------------------------------------------------------------
def pctline(k: int, n: int, label: str, indent: str = "    ") -> None:
    if not n:
        print(f"{indent}{label:32s} {k:5d} / {n:5d}  (NO DENOMINATOR)")
        return
    lo_sm, hi_sm, lo_mp, hi_mp, agree = wilson(k, n)
    print(f"{indent}{label:32s} {k:5d} / {n:5d} = {100*k/n:8.4f}%")
    print(f"{indent}{'':32s}   Wilson95 statsmodels [{100*lo_sm:8.4f}%, "
          f"{100*hi_sm:8.4f}%]")
    print(f"{indent}{'':32s}   Wilson95 mpmath      [{100*lo_mp:8.4f}%, "
          f"{100*hi_mp:8.4f}%]  agree(1e-9)={agree}")


def two_by_two(title: str, a: int, b: int, c: int, d: int) -> None:
    """a=prose&outcome, b=prose&other, c=code&outcome, d=code&other."""
    print(f"\n  {title}")
    print(f"    {'':12s} {'outcome':>9s} {'other':>9s} {'n':>9s}")
    print(f"    {'PROSE':12s} {a:9d} {b:9d} {a+b:9d}")
    print(f"    {'CODE':12s} {c:9d} {d:9d} {c+d:9d}")
    if not (a + b) or not (c + d):
        print("    UNDECIDABLE: an arm has no denominator.")
        return
    pctline(a, a + b, "prose rate", indent="    ")
    pctline(c, c + d, "code  rate", indent="    ")
    if a + c == 0:
        print(f"    ZERO EVENTS IN BOTH ARMS ({a}/{a+b} prose, {c}/{c+d} code).")
        print("    UNDECIDABLE BY CONSTRUCTION: no contrast exists to test.")
        print("    Reporting this as a null effect would be a manufactured")
        print("    result, so no odds ratio is printed.")
        return
    odds, p, pm = fisher(a, b, c, d)
    print(f"    Fisher exact OR  = {odds!r}")
    print(f"    scipy  p         = {p:.12e}")
    print(f"    mpmath p         = {pm:.12e}")
    print(f"    agree(1e-9)      = {abs(p - pm) < 1e-9}   |delta| = "
          f"{abs(p - pm):.3e}")
    if c:
        print(f"    risk ratio prose/code = {(a/(a+b))/(c/(c+d)):.4f}")
    print(f"    absolute excess       = {100*(a/(a+b) - c/(c+d)):+.4f} "
          f"percentage points")


def main() -> int:
    print("=" * 78)
    print("D2  CAUSE 3 AFTER A RUN-LEVEL TARGET JOIN")
    print("=" * 78)

    # -- 1. target provenance census ---------------------------------------
    per_dir, unreadable, artefacts = walk_run_dirs()
    print("\n1. RUN-LEVEL TARGET PROVENANCE (recursive walk of bench/logs/)")
    print(f"   runner-authored artefacts read     : {artefacts}")
    print(f"   unreadable (reported, not dropped) : {unreadable}")
    print(f"   run directories found              : {len(per_dir)}")
    with_t = {r: s for r, s in per_dir.items() if s["target"]}
    print(f"   run directories WITH a target_file : {len(with_t)}")
    print(f"   run directories WITHOUT one        : "
          f"{len(per_dir) - len(with_t)}")

    print("\n   which artefact supplied the target:")
    src = collections.Counter(s["source"] for s in with_t.values())
    for k in ARTEFACT_ORDER:
        print(f"     {k:20s} {src.get(k, 0):5d}")

    print("\n   per-artefact availability of a RUN-LEVEL target_file:")
    avail = collections.defaultdict(lambda: [0, 0])
    for s in per_dir.values():
        for k, a in s["artefacts"].items():
            avail[k][0] += 1
            if a["target"]:
                avail[k][1] += 1
    for k in ARTEFACT_ORDER:
        n, y = avail[k]
        print(f"     {k:20s} {y:4d} of {n:4d} carry one")
    print("     (checkpoint.json carries target_file only on INDIVIDUAL")
    print("      findings inside all_findings; that is finding-level, not run")
    print("      provenance, and is deliberately not read as a run target.)")

    print("\n   breakdown of the run directories that yield a target:")
    arms = collections.Counter(arm_of(s["target"]) for s in with_t.values())
    for a in ("prose", "code", "other"):
        print(f"     {a:20s} {arms.get(a, 0):5d}")
    sufs = collections.Counter(
        pathlib.PurePosixPath(s["target"].replace("\\", "/")).suffix.lower()
        for s in with_t.values())
    print("   by suffix: " + ", ".join(f"{k or '(none)'}={v}"
                                       for k, v in sorted(sufs.items())))

    print("\n   declared target_kind.kind, where the runner recorded one:")
    kinds = collections.Counter(s["target_kind"] or "(absent)"
                                for s in with_t.values())
    for k, v in sorted(kinds.items()):
        print(f"     {k:20s} {v:5d}")
    mism = [(r, s["target"], s["target_kind"]) for r, s in with_t.items()
            if s["target_kind"] and
            ((s["target_kind"] == "prose") != (arm_of(s["target"]) == "prose"))]
    print(f"   suffix/declared-kind disagreements  : {len(mism)}")
    for r, t, k in sorted(mism):
        print(f"     {r}  {t}  declared={k}")

    print("\n   the prose run directories, named:")
    for r, s in sorted(with_t.items()):
        if arm_of(s["target"]) == "prose":
            print(f"     {r}")
            print(f"       target={s['target']}  kind={s['target_kind']}  "
                  f"from={s['source']}")

    # -- 2. the join -------------------------------------------------------
    rows, prov = harvest_criticals()
    post = {k: v for k, v in rows.items()
            if expno(k[0]) is None or expno(k[0]) >= 42}
    print("\n2. FINDING POPULATION AND JOIN")
    print(f"   critical entries, deduplicated     : {len(rows)}")
    print(f"   POST-FEATURE CUT (expno>=42 or n/a): {len(post)}")
    print(f"   matches repro_supply_causes' 624   : {len(post) == 624}")

    # Resolve run-dir NAME -> target. Nested copies share the name and the
    # target, so collisions are harmless; the first in sorted order wins.
    by_dir_name = {}
    for rel in sorted(with_t):
        by_dir_name.setdefault(with_t[rel]["name"], with_t[rel])

    old_style = sum(1 for k in post
                    if prov[k].endswith("_report.json") and k[0] in by_dir_name)
    dropped = sum(1 for k in post
                  if not prov[k].endswith("_report.json")
                  and k[0] in by_dir_name)
    print("\n   WHY repro_supply_causes saw only 52: it read the target off the")
    print("   SAME artefact it took the body from.")
    print(f"     criticals whose chosen record was a *_report.json : {old_style}")
    print(f"     criticals whose chosen record was runner_state    : {dropped}")
    print(f"     -> {dropped} targets were discarded by the dedup, including")
    print("        every prose run, because runner_state.json never records a")
    print("        run-level target_file.")

    joined = {}
    unjoined = {}
    for k, e in post.items():
        s = by_dir_name.get(k[0])
        if s is None:
            unjoined[k] = e
        else:
            joined[k] = (s["target"], arm_of(s["target"]), e)
    print(f"\n   criticals JOINED to a run-level target : {len(joined)}")
    print(f"   criticals with NO run target (dropped) : {len(unjoined)}")
    print(f"   coverage of the 624                    : "
          f"{100*len(joined)/len(post):.4f}%")

    arm_counts = collections.Counter(v[1] for v in joined.values())
    for a in ("prose", "code", "other"):
        print(f"     {a:8s} criticals {arm_counts.get(a, 0):5d}")
    run_arm = {run: a for (run, _cid), (_t, a, _e) in joined.items()}
    runs_in = collections.Counter(run_arm.values())
    print("   contributing run directories: "
          + ", ".join(f"{a}={runs_in.get(a, 0)}"
                      for a in ("prose", "code", "other")))

    print("\n   runs in the 624 with NO run-level target (and their criticals):")
    for r, n in sorted(collections.Counter(k[0] for k in unjoined).items()):
        print(f"     {r:55s} {n:4d}")

    print("\n   per prose run, criticals carried:")
    pr = collections.Counter(k[0] for k, v in joined.items() if v[1] == "prose")
    for r, n in sorted(pr.items()):
        print(f"     {r:55s} {n:4d}")

    # -- 3. state decomposition per arm ------------------------------------
    states = {"prose": collections.Counter(), "code": collections.Counter()}
    ents = {"prose": [], "code": []}
    for (run, cid), (t, a, e) in sorted(joined.items()):
        if a not in states:
            continue
        states[a][classify(e)] += 1
        ents[a].append(e)
    print("\n3. FALSIFIER END-STATE, STRATIFIED BY RUN-LEVEL TARGET KIND")
    for a in ("prose", "code"):
        n = len(ents[a])
        print(f"\n   {a.upper()}  n = {n}")
        for lbl in sorted(states[a], key=lambda k: (-states[a][k], k)):
            pctline(states[a][lbl], n, lbl[:32], indent="      ")

    def table(pred, title):
        a = sum(1 for e in ents["prose"] if pred(e))
        b = len(ents["prose"]) - a
        c = sum(1 for e in ents["code"] if pred(e))
        d = len(ents["code"]) - c
        two_by_two(title, a, b, c, d)
        return a, b, c, d

    print("\n4. CAUSE 3 RECOMPUTED: 2x2 TABLES, PROSE vs CODE")
    strict = table(
        lambda e: classify(e) == "NOTHING WRITTEN AND NOTHING RECORDED",
        "CAUSE 3 (STRICT): no body AND no verdict -- 'no falsifier body at all'")
    loose = table(lambda e: not _body(e),
                  "CAUSE 3 (LOOSE): no body RETAINED, whatever the verdict")
    err = table(lambda e: classify(e) == "WRITTEN, THEN ERRORED",
                "ERROR-rate: a falsifier existed and it broke")
    unt = table(lambda e: classify(e) == "ASSESSED AND DECLINED (UNTOOLABLE)",
                "UNTOOLABLE-rate: the ladder was asked and declined")

    # -- 5. the plain statement --------------------------------------------
    np_, nc = len(ents["prose"]), len(ents["code"])
    print("\n5. PLAIN STATEMENT")
    print(f"   PROSE denominator after the join: {np_} criticals from "
          f"{runs_in.get('prose', 0)} run directories.")
    print(f"   CODE  denominator after the join: {nc} criticals from "
          f"{runs_in.get('code', 0)} run directories.")
    if np_ == 0:
        print("   CAUSE 3 IS STILL NOT MEASURABLE: the prose stratum is EMPTY.")
        return 0
    if strict[0] + strict[2] == 0:
        print(f"   STRICT 'no body at all' is UNDECIDABLE: {strict[0]}/{np_} "
              f"prose and {strict[2]}/{nc} code -- zero events in BOTH arms.")
        print("   CAUSE 3 AS LITERALLY WORDED HAS NO EVENTS TO EXPLAIN. Every")
        print("   starved critical in this population carries a VERDICT, so it")
        print("   is an ERROR or an UNTOOLABLE declination, not a silent void.")
    for lbl, (a, b, c, d) in (("NO BODY RETAINED", loose),
                              ("ERROR", err),
                              ("UNTOOLABLE", unt)):
        if a + c == 0:
            print(f"   {lbl}: zero events in both arms -- undecidable.")
            continue
        wp, wc = wilson(a, a + b), wilson(c, c + d)
        odds, p, pm = fisher(a, b, c, d)
        print(f"   {lbl:17s} prose {100*a/(a+b):7.4f}% "
              f"[{100*wp[0]:.4f}, {100*wp[1]:.4f}]  vs  code "
              f"{100*c/(c+d):7.4f}% [{100*wc[0]:.4f}, {100*wc[1]:.4f}]  "
              f"OR={odds:.4f}  p={p:.3e}  (mpmath p={pm:.3e}, "
              f"agree={abs(p-pm) < 1e-9})")
    return 0


if __name__ == "__main__":
    # A `--help` MUST NEVER COST ANYTHING (founder ruling). This call precedes
    # every archive read below it.
    answer_help(__doc__, __file__)
    raise SystemExit(main())
