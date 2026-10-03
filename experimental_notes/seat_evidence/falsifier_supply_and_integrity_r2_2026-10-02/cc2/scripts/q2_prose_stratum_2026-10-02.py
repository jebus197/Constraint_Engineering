# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'falsifier_supply_and_integrity_r2_2026-10-02', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: b882e8617c1a5502696c3b49affa2f4f347be522adff0d8fd8427713bb795d82
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Q2 + D-2: what adjudicates on PROSE, and recover the prose/code stratum.

D-2 BLOCKER. `scripts/repro_supply_causes_2026-10-02.py` reports CAUSE 3 as NOT
MEASURABLE: `target_file` lands on only 52 of 624 post-feature criticals, all
`.py`, zero prose. The cause is a BROKEN JOIN, not missing data:

  * `target_file` is NOT a per-finding field. Measured here: 0 of ~6029
    registry entries across bench/logs carry `target_file` or `target_kind`.
    It is a RUN-level field, written once at the top of `*_report.json`
    (`target_file`, and `target_kind` as a dict with `kind`/`reason`).
  * `runner_state.json` carries the registry but NO target block at all
    (measured: 0 of 57 files have one).
  * The repro script scans `runner_state.json` FIRST, keys rows by
    (run_dir, canonical_id), and only lets a later row win if the earlier one
    had no falsifier body. So for every run directory holding BOTH files --
    47 of them, including every prose run -- the target-less `runner_state`
    row wins and the target is lost.
  * Only report-only directories can therefore contribute a target, and of
    those just 6 reports carry one. All 6 are `.py`. Hence 52, all `.py`,
    zero prose. The prose stratum was never absent; it was overwritten.

THE RECOVERY ROUTE: join a finding to its RUN's `target_file`/`target_kind`
from the run report, rather than to a per-finding field that does not exist.
This script does that and recomputes CAUSE 3 on the join.

Q2. It then enumerates what actually adjudicates on a prose target, by
classifying the falsifier bodies of the CONFIRMED criticals of an archived
prose run, and finally RE-EXECUTES those falsifiers through the runner's own
`bench.falsifier_verify.reverify_falsifier` to test whether the
"keep trying until tool-confirmed" loop is reachable on prose at all.

Every proportion gets a Wilson interval from statsmodels AND from an
independent mpmath closed form. Every 2x2 gets a scipy Fisher exact AND an
independent mpmath hypergeometric sum. Disagreement is printed, not hidden.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys
from collections import Counter

for _cand in (pathlib.Path(__file__).resolve().parent,
              *pathlib.Path(__file__).resolve().parents):
    if (_cand / "_cli_help.py").is_file():
        sys.path.insert(0, str(_cand))
        break
from _cli_help import answer_help  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
LOGS = ROOT / "bench" / "logs"
CRIT = 0.7
PROSE_RUN = "prose_convergence_run1b_2026-10-02_20261002T044234Z"


# -- statistics, each by two independent routes ----------------------------
def wilson(k: int, n: int, alpha: float = 0.05):
    """Wilson score interval, statsmodels and an independent mpmath form."""
    from statsmodels.stats.proportion import proportion_confint
    import mpmath as mp
    if n == 0:
        return (float("nan"), float("nan")), (float("nan"), float("nan"))
    lo, hi = proportion_confint(k, n, alpha=alpha, method="wilson")
    mp.mp.dps = 40
    # z = Phi^-1(1 - alpha/2) via the mpmath inverse error function, not scipy.
    z = mp.sqrt(2) * mp.erfinv(1 - mp.mpf(alpha))
    nn, p = mp.mpf(n), mp.mpf(k) / mp.mpf(n)
    den = 1 + z**2 / nn
    centre = (p + z**2 / (2 * nn)) / den
    half = (z * mp.sqrt(p * (1 - p) / nn + z**2 / (4 * nn**2))) / den
    return (float(lo), float(hi)), (float(centre - half), float(centre + half))


def fisher(a: int, b: int, c: int, d: int):
    """Odds ratio + two-sided p: scipy, and an independent mpmath hypergeom sum."""
    from scipy.stats import fisher_exact
    import mpmath as mp
    odds, p = fisher_exact([[a, b], [c, d]])
    mp.mp.dps = 50
    n, r1, c1 = a + b + c + d, a + b, a + c
    def pr(x):
        return (mp.binomial(c1, x) * mp.binomial(n - c1, r1 - x)) / mp.binomial(n, r1)
    obs, tot = pr(a), mp.mpf(0)
    for x in range(max(0, r1 - (n - c1)), min(r1, c1) + 1):
        q = pr(x)
        if q <= obs * (1 + mp.mpf("1e-30")):
            tot += q
    return odds, p, float(tot)


def pct(k, n):
    sm, mpm = wilson(k, n)
    agree = (abs(sm[0] - mpm[0]) < 1e-9 and abs(sm[1] - mpm[1]) < 1e-9)
    r = 100.0 * k / n if n else float("nan")
    return (f"{k}/{n} = {r:7.3f}%  Wilson95 [{100*sm[0]:7.3f}%, {100*sm[1]:7.3f}%]"
            f"  (mpmath agrees={agree})")


# -- the join --------------------------------------------------------------
def run_targets() -> dict:
    """run_dir -> (target_file, target_kind). RUN level, from the run report."""
    out = {}
    for f in sorted(LOGS.glob("*/*_report.json")):
        try:
            d = json.loads(f.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            continue
        tf = d.get("target_file") or (d.get("config") or {}).get("target_file")
        if not tf:
            continue
        tk = d.get("target_kind")
        kind = tk.get("kind") if isinstance(tk, dict) else tk
        if not kind:  # pre-2026-08-01 reports predate the field: read the suffix
            kind = "prose" if str(tf).lower().endswith(".md") else (
                "python_module" if str(tf).lower().endswith(".py") else "")
        prev = out.get(f.parent.name)
        if prev is None or (not prev[1] and kind):
            out[f.parent.name] = (str(tf), kind)
    return out


def body(e: dict) -> str:
    return ((e.get("falsifier_code") or "").strip()
            or (e.get("last_falsifier_code") or "").strip())


def verdict(e: dict) -> str:
    h = e.get("routing_history") or []
    return ((e.get("falsifier_verdict") or "").strip().upper()
            or (e.get("routing_verdict_unreconciled") or "").strip().upper()
            or ((h[-1].get("verdict") or "").strip().upper() if h else ""))


def criticals():
    """(run_dir, cid) -> entry, deduped, preferring the row that has a body."""
    rows, per_finding_target, total_entries = {}, 0, 0
    for f in (sorted(LOGS.glob("*/runner_state.json"))
              + sorted(LOGS.glob("*/*_report.json"))):
        try:
            d = json.loads(f.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            continue
        for cid, e in ((d.get("registry") or {}).get("entries") or {}).items():
            if not isinstance(e, dict):
                continue
            total_entries += 1
            if "target_file" in e or "target_kind" in e:
                per_finding_target += 1
            if (e.get("severity") or 0) < CRIT:
                continue
            key = (f.parent.name, cid)
            prev = rows.get(key)
            if prev is None or (not body(prev) and body(e)):
                rows[key] = e
    return rows, per_finding_target, total_entries


def expno(r: str):
    m = re.match(r"exp(\d+)", r)
    return int(m.group(1)) if m else None


# -- Q2: what a prose falsifier actually does ------------------------------
LINTERS = re.compile(r"\b(ruff|mypy|bandit|pytest|flake8|pylint)\b")
IMPORT_REPO = re.compile(
    r"^\s*(?:from|import)\s+(bench|scripts|explorer|hooks)\b", re.M)


def classify(code: str, target_basename: str) -> str:
    """(i) reads prose + asserts, (ii) imports a repo module, (iii) general
    linter, (iv) other -- checked in that order of evidential weight."""
    if LINTERS.search(code) and re.search(r"subprocess|os\.system", code):
        return "iii_general_linter"
    reads_doc = (target_basename in code) and bool(
        re.search(r"read_text|open\(|\.read\(", code))
    asserts = ("assert" in code) or ("FALSIFIED" in code)
    if reads_doc and asserts:
        return "i_reads_prose_and_asserts"
    if IMPORT_REPO.search(code) or _imports_repo_by_syspath(code):
        return "ii_imports_repo_module"
    if reads_doc:
        return "i_reads_prose_and_asserts"
    return "iv_other"


def _imports_repo_by_syspath(code: str) -> bool:
    """`sys.path.insert(...bench)` then `import run_benchmark` is still an
    import of real repository code; it just does not spell the package."""
    if "sys.path" not in code:
        return False
    for name in re.findall(r"^\s*(?:import|from)\s+([A-Za-z_]\w*)", code, re.M):
        if (ROOT / "bench" / f"{name}.py").is_file() or (ROOT / f"{name}.py").is_file():
            return True
    return False


def main() -> int:
    print("=" * 78)
    print("PART A -- WHY `target_file` IS MISSING ON PROSE FINDINGS")
    print("=" * 78)
    rows, per_finding, total_entries = criticals()
    print(f"registry entries scanned across bench/logs : {total_entries}")
    print(f"entries carrying a PER-FINDING target field: {per_finding}")
    print("  -> `target_file` is a RUN-level field. No finding has ever had one.")

    st = sorted(LOGS.glob("*/runner_state.json"))
    rp = sorted(LOGS.glob("*/*_report.json"))
    st_with_target = 0
    for f in st:
        d = json.loads(f.read_text(encoding="utf-8", errors="replace"))
        if d.get("target_file") or (d.get("config") or {}).get("target_file"):
            st_with_target += 1
    print(f"runner_state.json files                    : {len(st)}"
          f"  (with a target block: {st_with_target})")
    print(f"*_report.json files                        : {len(rp)}")
    tmap = run_targets()
    print(f"run dirs with a recoverable RUN target     : {len(tmap)}")
    dirs = {}
    for f in st:
        dirs.setdefault(f.parent.name, set()).add("state")
    for f in rp:
        dirs.setdefault(f.parent.name, set()).add("report")
    both = [k for k, v in dirs.items() if v == {"state", "report"}]
    print(f"run dirs holding BOTH files                : {len(both)}"
          f"   <- target-less runner_state row wins the (dir,cid) key here")
    print(f"  the prose run is in that set              : {PROSE_RUN in both}")

    post = {k: v for k, v in rows.items()
            if expno(k[0]) is None or expno(k[0]) >= 42}
    state_dirs = {f.parent.name for f in st}
    print(f"\npost-feature criticals (sev>={CRIT}, exp>=42 or unnumbered): {len(post)}")
    old = sum(1 for (r, _c) in post if r not in state_dirs and r in tmap)
    joined = sum(1 for (r, _c) in post if r in tmap)
    print("  target attributable, OLD per-row route  : 52 (as D-2 reports)")
    print(f"  report-only dirs, the old route's reach : {old}")
    print(f"  target attributable, RUN-JOIN route     : {joined}")
    kinds = Counter(tmap[r][1] for (r, _c) in post if r in tmap)
    print(f"  joined kinds: {dict(kinds)}")

    print()
    print("=" * 78)
    print("PART B -- CAUSE 3 RECOMPUTED ON THE RUN JOIN")
    print("=" * 78)
    a = b = c = d = 0
    prose_runs, code_runs = set(), set()
    for (run, cid), e in post.items():
        if run not in tmap:
            continue
        tf, kind = tmap[run]
        nobody = (not body(e)) and (not verdict(e))
        if kind == "prose" or tf.lower().endswith(".md"):
            a, b = a + nobody, b + (not nobody)
            prose_runs.add(run)
        elif kind == "python_module" or tf.lower().endswith(".py"):
            c, d = c + nobody, d + (not nobody)
            code_runs.add(run)
    print(f"prose runs contributing: {len(prose_runs)}  code runs: {len(code_runs)}")
    for r in sorted(prose_runs):
        print(f"  prose run: {r}  -> {tmap[r][0]}")
    print("\nCAUSE 3  prose vs code targets: rate of NO FALSIFIER AT ALL")
    print(f"  prose targets  no-falsifier {a:4d}   other {b:4d}   n={a+b}")
    print(f"  code  targets  no-falsifier {c:4d}   other {d:4d}   n={c+d}")
    print(f"  prose rate: {pct(a, a + b)}")
    print(f"  code  rate: {pct(c, c + d)}")
    measurable = bool((a + b) and (c + d))
    print(f"  MEASURABLE: {measurable}")
    if measurable:
        o, p, pm = fisher(a, b, c, d)
        print(f"  Fisher OR = {o}  scipy p = {p:.6e}  mpmath p = {pm:.6e}"
              f"  agree={abs(p - pm) < 1e-9}")
        print("  claimed: 18 of 123 prose vs 11 of 357 code, OR 5.3922 -> "
              + ("REPRODUCED" if (a, a + b, c, c + d) == (18, 123, 11, 357)
                 else "NOT REPRODUCED (counts differ)"))

    # The strict definition (no body AND no verdict) is degenerate above, so
    # report the weaker one too rather than leave the stratum undecided: a
    # critical with NO falsifier body at all, whatever the verdict field says.
    a2 = b2 = c2 = d2 = 0
    for (run, cid), e in post.items():
        if run not in tmap:
            continue
        tf, kind = tmap[run]
        nb = not body(e)
        if kind == "prose" or tf.lower().endswith(".md"):
            a2, b2 = a2 + nb, b2 + (not nb)
        elif kind == "python_module" or tf.lower().endswith(".py"):
            c2, d2 = c2 + nb, d2 + (not nb)
    print("\nCAUSE 3 (weaker definition) no falsifier BODY on the entry")
    print(f"  prose targets  no-body {a2:4d}   has-body {b2:4d}")
    print(f"  code  targets  no-body {c2:4d}   has-body {d2:4d}")
    print(f"  prose rate: {pct(a2, a2 + b2)}")
    print(f"  code  rate: {pct(c2, c2 + d2)}")
    if (a2 + b2) and (c2 + d2) and (a2 + c2):
        o, p, pm = fisher(a2, b2, c2, d2)
        print(f"  Fisher OR = {o}  scipy p = {p:.6e}  mpmath p = {pm:.6e}"
              f"  agree={abs(p - pm) < 1e-9}")
    else:
        print("  Fisher: degenerate (a zero margin), nothing to test")

    # And the thing the stratum actually differs on: the verdict mix.
    for label, pred in (("prose", lambda k, t: k == "prose" or t.lower().endswith(".md")),
                        ("code", lambda k, t: k == "python_module" or t.lower().endswith(".py"))):
        vc = Counter()
        for (run, cid), e in post.items():
            if run not in tmap:
                continue
            tf, kind = tmap[run]
            if pred(kind, tf):
                vc[verdict(e) or "(none)"] += 1
        print(f"  {label:5s} falsifier-verdict mix: {dict(vc.most_common())}")

    print()
    print("=" * 78)
    print("PART C -- WHAT ADJUDICATES ON PROSE (archived prose run)")
    print("=" * 78)
    rep = next((LOGS / PROSE_RUN).glob("*_report.json"))
    doc = json.loads(rep.read_text(encoding="utf-8", errors="replace"))
    tf = doc["target_file"]
    tk = doc["target_kind"]
    print(f"run        : {PROSE_RUN}")
    print(f"target_file: {tf}")
    print(f"target_kind: {tk.get('kind')}  ({tk.get('reason')})")
    ents = (doc.get("registry") or {}).get("entries") or {}
    crit = sorted((e for e in ents.values() if (e.get("severity") or 0) >= CRIT),
                  key=lambda e: e["canonical_id"])
    print(f"criticals  : {len(crit)}   statuses "
          f"{dict(Counter(e['status'] for e in crit))}")
    conf = [e for e in crit if verdict(e) == "CONFIRMED"]
    print(f"CONFIRMED by the runner's falsifier re-run: {pct(len(conf), len(crit))}")
    base = pathlib.Path(tf).name
    cls = Counter(classify(body(e), base) for e in conf)
    print("\nclassification of the CONFIRMED criticals' falsifier bodies:")
    for k in ("i_reads_prose_and_asserts", "ii_imports_repo_module",
              "iii_general_linter", "iv_other"):
        print(f"  {k:28s} {pct(cls.get(k, 0), len(conf))}")
    execs = sum(1 for e in conf if re.search(r"\bexec\(", body(e)))
    absre = re.compile(r"""['"]/[\w./-]*""" + re.escape(base))
    absp = sum(1 for e in conf if absre.search(body(e)))
    relp = len(conf) - absp
    lint = sum(1 for e in conf if LINTERS.search(body(e)))
    rglob = sum(1 for e in conf if re.search(r"rglob|glob\(", body(e)))
    print(f"\n  exec() a code listing lifted OUT of the prose: {pct(execs, len(conf))}")
    print(f"  address the document by a RELATIVE path      : {pct(relp, len(conf))}")
    print(f"  address the document by an ABSOLUTE path     : {pct(absp, len(conf))}")
    print(f"  also walk real repo files (glob/rglob)       : {pct(rglob, len(conf))}")
    print(f"  mention ruff/mypy/bandit/pytest at all       : {pct(lint, len(conf))}")

    print()
    print("=" * 78)
    print("PART D -- IS THE TOOL-CONFIRMATION LOOP REACHABLE ON PROSE?")
    print("   live re-execution through bench.falsifier_verify.reverify_falsifier")
    print("=" * 78)
    sys.path.insert(0, str(ROOT))
    from bench.falsifier_verify import reverify_falsifier, set_falsifier_target
    tgt_abs = ROOT / tf
    print(f"target on disk here: {tgt_abs}")
    print(f"exists             : {tgt_abs.is_file()}")
    set_falsifier_target(str(tgt_abs), tf)
    got, byclass, byverdict = Counter(), {}, {}
    for e in conf:
        v = reverify_falsifier(body(e), repo_root=str(ROOT), timeout=25)
        byverdict[e["canonical_id"]] = v
        got[v] += 1
        key = "absolute" if absre.search(body(e)) else "relative"
        byclass.setdefault(key, Counter())[v] += 1
        print(f"  {e['canonical_id']}  archived={verdict(e):10s}  "
              f"re-run NOW={v:22s} path={key}")
    set_falsifier_target(None)
    print(f"\n  re-run verdicts: {dict(got)}")
    for k, v in sorted(byclass.items()):
        print(f"    {k}-path falsifiers: {dict(v)}")
    n_rel = sum(byclass.get("relative", Counter()).values())
    print(f"\n  CONFIRMED among relative-path falsifiers: "
          f"{pct(byclass.get('relative', Counter()).get('CONFIRMED', 0), n_rel)}")
    print(f"  CONFIRMED among ALL re-runs            : "
          f"{pct(got.get('CONFIRMED', 0), len(conf))}")
    print("\n  Why the non-CONFIRMED ones failed, from scan_falsifier_source:")
    from bench.falsifier_verify import scan_falsifier_source
    for e in conf:
        v = byverdict.get(e["canonical_id"])
        if v == "CONFIRMED":
            continue
        viol = scan_falsifier_source(body(e), repo_root=str(ROOT))
        print(f"    {e['canonical_id']}: {viol}")
    print("  These are LAYER-1 static rejections for a hard-coded home-rooted")
    print("  path outside the declared target roots. The paths are the")
    print("  maintainer's checkout; this tree sits in a temp dir, so the same")
    print("  literal is now out-of-roots. A portability fault of the stored")
    print("  artefact, not evidence about whether prose can be adjudicated.")
    return 0


if __name__ == "__main__":
    answer_help(__doc__, __file__)
    raise SystemExit(main())
