#!/usr/bin/env python3
"""Recompute every figure cited in the 2026-10-02 integrity-guard analysis.

WHY THIS EXISTS. `measured-rate-travels-with-its-script` (founder ruling
2026-09-04): a measured rate, proportion or count may be cited only if the
script that produced it is committed alongside it. A number that exists solely
as prose in a note is a claim about evidence, not evidence.

The specific hazard this guards was demonstrated earlier the same day: Wilson
bounds were typed into a code comment from recall as [9.1823%, 19.8622%] when
the measured values were [9.2001%, 19.8226%]. Every figure below is therefore
recomputed from the archive on each run, and every proportion carries a Wilson
interval computed by 2 independent tools plus a Clopper-Pearson interval from a
third, so a disagreement between them shows up as a disagreement rather than as
a number.

THE CENTRAL FINDING IT PRODUCES. `bench/tests/test_falsifier_cannot_read_the_key.py`
holds the integrity guard's false-positive rate at 0 over what its docstring
calls "every falsifier this project has ever run". It reads
`registry.entries.<cid>.falsifier_code`. The runner writes that field back only
on `result.resolved` (`bench/reference_runner_v3.py`, `_apply_routing`), so a
REFUSED falsifier's body never reaches the field the test reads. The corpus that
measures refusals excludes refusals by construction.

Usage:  python3 scripts/guard_false_positive_blind_spot_2026-10-02.py
"""
from __future__ import annotations

import json
import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from bench.falsifier_verify import scan_falsifier_source  # noqa: E402

LOGS = REPO / "bench" / "logs"
RUN1B = LOGS / "prose_convergence_run1b_2026-10-02_20261002T044234Z"
TARGET_SPEC = REPO / "bench" / "BUILD_BOT_TEST_BENCH_FIX_SPEC.md"
PRODUCTION = ["bench/run_benchmark.py", "bench/run_phase2.py",
              "bench/run_round_robin.py", "bench/evaluate.py",
              "bench/run_experiment.py"]
ACCESS = re.compile(r"""\[\s*['"]seeded_faults?['"]\s*\]"""
                    r"""|\.get\(\s*['"]seeded_faults?['"]""")


def interval(k: int, n: int):
    """Wilson by 2 tools plus Clopper-Pearson by a third. Returns a dict."""
    from statsmodels.stats.proportion import proportion_confint
    from scipy.stats import beta as sbeta
    import mpmath as mp
    if n == 0:
        return {"k": k, "n": n, "pct": None}
    lo_sm, hi_sm = proportion_confint(k, n, method="wilson")
    z = mp.mpf("1.959963984540054")
    p = mp.mpf(k) / n
    d = 1 + z ** 2 / n
    c = (p + z ** 2 / (2 * n)) / d
    h = z * mp.sqrt(p * (1 - p) / n + z ** 2 / (4 * n ** 2)) / d
    lo_mp, hi_mp = float(c - h), float(c + h)
    cp_lo = 0.0 if k == 0 else float(sbeta.ppf(0.025, k, n - k + 1))
    cp_hi = 1.0 if k == n else float(sbeta.ppf(0.975, k + 1, n - k))
    return {"k": k, "n": n, "pct": 100.0 * k / n,
            "wilson_statsmodels": (100 * lo_sm, 100 * hi_sm),
            "wilson_mpmath": (100 * lo_mp, 100 * hi_mp),
            "tools_agree": abs(lo_sm - lo_mp) < 1e-9 and abs(hi_sm - hi_mp) < 1e-9,
            "clopper_pearson": (100 * cp_lo, 100 * cp_hi)}


def show(label: str, r: dict) -> None:
    if r.get("pct") is None:
        print(f"{label}: empty corpus")
        return
    print(f"{label}: {r['k']}/{r['n']} = {r['pct']:.4f}%")
    print(f"    Wilson  [{r['wilson_statsmodels'][0]:.4f}%, "
          f"{r['wilson_statsmodels'][1]:.4f}%]   statsmodels==mpmath: "
          f"{r['tools_agree']}")
    print(f"    Clopper-Pearson [{r['clopper_pearson'][0]:.4f}%, "
          f"{r['clopper_pearson'][1]:.4f}%]")


def corpora():
    """The 2 falsifier corpora: what the test reads, and what it cannot read."""
    accepted: dict[str, tuple[str, str]] = {}
    attempted: dict[str, tuple[str, str]] = {}
    for report in sorted(LOGS.rglob("*_report.json")):
        try:
            data = json.loads(report.read_text(encoding="utf-8", errors="replace"))
        except (ValueError, OSError):
            continue
        entries = (data.get("registry") or {}).get("entries") or {}
        for cid, e in entries.items():
            e = e or {}
            a = (e.get("falsifier_code") or "").strip()
            if a:
                accepted.setdefault(a, (report.parent.name, cid))
            for h in (e.get("routing_history") or []):
                b = (h.get("last_falsifier_code") or "").strip()
                if b and b not in accepted:
                    attempted.setdefault(b, (report.parent.name, cid))
    return accepted, attempted


def refused(corpus):
    return {k: v for k, v in corpus.items() if scan_falsifier_source(k)}


def main() -> int:
    print("=" * 72)
    print("1. THE GUARD'S FALSE-POSITIVE RATE, OVER BOTH CORPORA")
    print("=" * 72)
    accepted, attempted = corpora()
    acc_rej, att_rej = refused(accepted), refused(attempted)
    show("  corpus the test READS (falsifier_code)", interval(len(acc_rej), len(accepted)))
    show("  corpus it CANNOT read (last_falsifier_code)",
         interval(len(att_rej), len(attempted)))
    tok: dict[str, int] = {}
    for body in att_rej:
        for _rule, t in scan_falsifier_source(body):
            tok[t] = tok.get(t, 0) + 1
    print(f"    tokens responsible in the unseen corpus: {tok}")

    print()
    print("=" * 72)
    print("2. REFUSAL EVENTS IN THE LOGS, BY MATCHED TOKEN")
    print("=" * 72)
    counts: dict[str, int] = {}
    run1b_counts: dict[str, int] = {}
    # DEDUPED. `*/run.log` is ALSO matched by `*/*.log`, so the union
    # double-counted every event in a run.log and reported 20 refusal
    # events where there are 10. Caught by this script disagreeing with a
    # direct `grep -c` of the same file.
    seen_logs = sorted({p.resolve() for p in LOGS.glob("*/*.log")})
    for lg in seen_logs:
        try:
            text = lg.read_text(errors="ignore")
        except OSError:
            continue
        for m in re.findall(r"matched: '([^']+)'", text):
            counts[m] = counts.get(m, 0) + 1
            if "prose_convergence_run1b" in str(lg):
                run1b_counts[m] = run1b_counts.get(m, 0) + 1
    total = sum(counts.values())
    seeded = counts.get("seeded_fault", 0)
    print(f"  archive-wide refusal events: {total}")
    for t, n in sorted(counts.items(), key=lambda kv: -kv[1]):
        print(f"      {n:3d}  {t[:60]}")
    show("  share attributable to the seeded_fault token", interval(seeded, total))
    print(f"  run 1b refusal events by token: {run1b_counts}")

    print()
    print("=" * 72)
    print("3. MENTION VERSUS ACCESS: DID ANY FALSIFIER READ THE FIELD?")
    print("=" * 72)
    blob = "\n".join(f.read_text(encoding="utf-8", errors="ignore")
                     for f in RUN1B.glob("*.json")) if RUN1B.is_dir() else ""
    frags = re.findall(r".{0,400}seeded_fault.{0,400}", blob)
    acc = [f for f in frags if ACCESS.search(f)]
    show("  fragments that subscript or .get the field", interval(len(acc), len(frags)))

    print()
    print("=" * 72)
    print("4. WHERE THE TOKEN LIVES, AND THE COST OF RENAMING IT")
    print("=" * 72)
    spec_n = (TARGET_SPEC.read_text(encoding="utf-8", errors="ignore")
              .count("seeded_fault") if TARGET_SPEC.is_file() else None)
    print(f"  occurrences in the target spec {TARGET_SPEC.name}: {spec_n}")
    prod = 0
    for rel in PRODUCTION:
        p = REPO / rel
        txt = p.read_text(encoding="utf-8", errors="ignore") if p.is_file() else ""
        n = txt.count("seeded_fault")
        lines = sum(1 for ln in txt.splitlines() if "seeded_fault" in ln)
        prod += n
        print(f"      {rel}: {n} occurrence(s) on {lines} line(s)")
    print(f"  production total: {prod} occurrence(s)")
    # TWO CORRECTIONS, BOTH MEASURED, BOTH MINE.
    #
    # 1. UNITS. The first version of this block summed `git grep -c`, which
    #    counts LINES CONTAINING a match, and printed the total as
    #    "occurrences". On this tree the 2 differ: 133 lines against 136
    #    occurrences of the substring. The same line/occurrence confusion was
    #    caught once already the same day in a per-file figure, and reappeared
    #    here in the repo-wide one.
    #
    # 2. THE MEASURING DOCUMENT IS INSIDE THE MEASURED POPULATION. This script,
    #    its test, and the note they support all discuss `seeded_faults`, so
    #    committing them RAISED the count they report, from 111 to 124
    #    occurrences. A census of a token cannot include the documents written
    #    about that token, or it grows every time the analysis is revised. The
    #    3 artefacts are excluded by prefix and the exclusion is printed, so
    #    the population is stated rather than assumed.
    #
    # The plural is counted, not the substring: `seeded_faults` is the real
    # field name, and the guard's rule looks for the singular `seeded_fault`,
    # which matches inside the plural because it carries no end-of-word
    # boundary. That substring relationship IS the defect, so the 2 forms are
    # reported separately.
    SELF = ("experimental_notes/Integrity_Guard_False_Positive",
            "scripts/guard_false_positive_blind_spot",
            "bench/tests/test_guard_false_positive_figures")
    tracked = subprocess.run(["git", "ls-files"], cwd=REPO,
                             capture_output=True, text=True).stdout.split()
    def census(pred):
        occ = files_n = 0
        for rel in tracked:
            if not pred(rel):
                continue
            try:
                t = (REPO / rel).read_text(encoding="utf-8", errors="ignore")
            except (OSError, UnicodeDecodeError):
                continue
            n = len(re.findall(r"seeded_faults", t))
            if n:
                occ += n
                files_n += 1
        return occ, files_n
    all_occ, all_files = census(lambda r: True)
    pop_occ, pop_files = census(lambda r: not r.startswith(SELF))
    task_occ, task_files = census(lambda r: r.startswith("bench/tasks/"))
    sing = 0
    for rel in tracked:
        if rel.startswith(SELF):
            continue
        try:
            t = (REPO / rel).read_text(encoding="utf-8", errors="ignore")
        except (OSError, UnicodeDecodeError):
            continue
        sing += len(re.findall(r"seeded_fault(?!s)", t))
    try:
        import numpy as np
        cross = f"NumPy agrees: {int(np.array([pop_occ]).sum())}"
    except ImportError:
        cross = "NumPy unavailable"
    print(f"  plural occurrences, ALL tracked files: {all_occ} across {all_files}"
          f" files   <-- includes the 3 artefacts written ABOUT the token")
    print(f"  plural occurrences, POPULATION (those 3 excluded): {pop_occ} across"
          f" {pop_files} files   ({cross})")
    print(f"      of which task data carrying planted faults: {task_occ} across"
          f" {task_files} files")
    print(f"  bare singular `seeded_fault` in the population: {sing}"
          f"   (the guard's rule looks for this and matches inside the plural)")

    print()
    print("=" * 72)
    print("5. HAS THE GUARD EVER FIRED IN A LIVE RUN?")
    print("=" * 72)
    live = [d for d in LOGS.iterdir() if d.is_dir() and "_live_" in d.name]
    tripped = []
    for d in live:
        for lg in sorted({q.resolve() for q in d.glob("*.log")}):
            if "INTEGRITY VIOLATION" in lg.read_text(errors="ignore"):
                tripped.append(d.name)
                break
    show(f"  live run directories ({len(live)}) that tripped it",
         interval(len(tripped), len(live)))
    sim_mods = len(re.findall(r"simulat|sim_mode|is_sim",
                              (REPO / "bench" / "falsifier_verify.py")
                              .read_text(encoding="utf-8"), re.I))
    print(f"  sim-related mentions in bench/falsifier_verify.py: {sim_mods}"
          f"   (a sim/live branch would need at least one)")

    print()
    print("=" * 72)
    print("6. RUN 1B's HALT, AND THE 3 QUEUED CRITICALS")
    print("=" * 72)
    sig = RUN1B / "completion_signal.json"
    if sig.is_file():
        s = json.loads(sig.read_text())
        print(f"  status={s['status']} reason={s['reason']} rounds={s['total_rounds']}")
        print(f"  findings={s['total_findings']} per_round={s['per_round_counts']} "
              f"kappa={s['final_kappa']:.4f}")
    chain = RUN1B / "experiment_chain.json"
    if chain.is_file():
        recs = json.loads(chain.read_text())["records"]
        for r in recs:
            al = ((r.get("sealed_body") or {}).get("payload") or {}).get(
                "irreducible_queue_alarm")
            if not al:
                continue
            print(f"  alarm: round={al['round']} count={al['count']} "
                  f"bound={al['bound']} "
                  f"items_without_falsifier={al['items_without_falsifier']} "
                  f"sk_states={al['sk_states_in_queue']}")
            for x in al["evidence"]:
                h = (x.get("routing_history") or [{}])[0]
                body = (h.get("last_falsifier_code") or "").strip()
                # THE ENTRY LABEL IS STALE BY DESIGN AND I READ IT ANYWAY.
                # `reconcile_routing_verdict`'s docstring states it outright:
                # "_apply_routing writes falsifier_code/falsifier_verdict back
                # only on result.resolved ... the entry keeps the stale
                # UNTOOLABLE and the ladder's real verdict survives only in
                # routing_history[-1]['verdict'], beside a body truncated to
                # 600 chars." This loop already bound `h` to that history and
                # read `rungs_tried` from it, then printed the ENTRY's
                # `falsifier_verdict` one key away. C0029 therefore read
                # UNTOOLABLE, "no falsifier was written", when the ladder had
                # written one and the guard had REFUSED it.
                #
                # `scan=` is likewise reported against the 600-char PREFIX, not
                # against what the guard read: archive-wide 183 of 221 retained
                # bodies sit at the cap, so a clean scan is evidence of nothing.
                # The run's OWN recorded verdict is authoritative and is printed
                # first.
                print(f"      {x['canonical_id']}: ladder_verdict={h.get('verdict')} "
                      f"(entry label: {x['falsifier_verdict']}, stale unless "
                      f"resolved) born={x['open_since_round']} "
                      f"rungs_tried={h.get('rungs_tried')}/"
                      f"{h.get('rungs_available')} "
                      f"prefix_scan={'REFUSED' if (body and scan_falsifier_source(body)) else 'clean'}"
                      f" (over {len(body)} of up to 600 retained chars)")
            break
    log = LOGS / "prose_convergence_run1b_2026-10-02" / "run.log"
    if log.is_file():
        text = log.read_text(errors="ignore")
        sk = re.findall(r"S_k \[C\d+\]: ([A-Z_]+)", text)
        tally: dict[str, int] = {}
        for v in sk:
            tally[v] = tally.get(v, 0) + 1
        print(f"  S_k outcomes: {tally}  (total {len(sk)})")
        for m in re.findall(r"gamma_(all|critical): ([0-9.]+)", text)[-2:]:
            print(f"  gamma_{m[0]} at the final gate: {m[1]}")
        settled = re.findall(r"post-sweep reconciliation: (\d+) re-probed, \[([^\]]*)\]", text)
        if settled:
            n, ids = settled[-1]
            held = [c.strip().strip("'") for c in ids.split(",")]
            queued = {"C0029", "C0032", "C0035"}
            print(f"  post-sweep reconciliation re-probed {n}; "
                  f"of the 3 queued criticals, "
                  f"{len(queued & set(held))} were settled afterwards")

    print()
    print("=" * 72)
    print("7. WHICH RUNS CONVERGED, AND ON WHAT KIND OF TARGET")
    print("=" * 72)
    for d in sorted(LOGS.iterdir()):
        sg = d / "completion_signal.json" if d.is_dir() else None
        if not sg or not sg.is_file():
            continue
        try:
            s = json.loads(sg.read_text())
        except (ValueError, OSError):
            continue
        if s.get("status") != "COMPLETE" and "CONVERG" not in str(s.get("reason", "")).upper():
            continue
        tgt = None
        for f in d.glob("*.json"):
            m = re.search(r'"(?:test_article|target_file)"\s*:\s*"([^"]{1,120})"',
                          f.read_text(encoding="utf-8", errors="ignore"))
            if m:
                tgt = m.group(1)
                break
        kind = "prose" if (tgt or "").endswith(".md") else (
            "python" if (tgt or "").endswith(".py") else "unknown")
        print(f"  {d.name[:52]:54s} rounds={s.get('total_rounds')} "
              f"seats={len(s.get('active_models') or [])} target_kind={kind}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
