#!/usr/bin/env python3
"""What does a collaborative round actually spend waiting on its slowest seat?

HIS QUESTION, `qs:157b6ddc201f`, raised 3 times and ruled on 2026-10-28:
*"Verdict. Do it and study it in the upcoming simulated run."* -- on whether a
collaborative star round needs a COMPLETION barrier and not just a staggered
start.

THE QUESTION CAN BE ANSWERED RETROSPECTIVELY, which is why this exists beside
the prospective instrumentation rather than instead of it. No archived seat
record carries an absolute completion time, so the barrier was thought to be
unmeasurable before the next run. It is not: a seat's reply file is written at
the END of `dispatch`, so its mtime approximates that seat's completion, and
`elapsed_s` gives the duration, which recovers the start. 88 archived panel
rounds answer the question today.

THE ANSWER. A round wastes a median 0.144892 of its available seat-time waiting
at the barrier, bootstrap 95% CI [0.105753, 0.181047] over 20,000 resamples, and
13 of 88 rounds wasted more than 0.30, a share of 0.147727. The median round
loses 255.9 s to the barrier and the archive loses 14.11 hours in all. His
instinct was right: the cost is real,
it is not small, and the 20-second stagger cannot touch it, because the stagger
governs STARTS and this is entirely a property of FINISHES.

WHETHER IT WORSENS WITH SEAT COUNT IS SUGGESTIVE AND NOT ESTABLISHED, and the
2-tool rule is what keeps that distinction. Restricted to rounds where every
seat succeeded: 0.384744 at 4 or more seats (n = 6, CI [0.186245, 0.535009])
against 0.131478 at 2 seats (n = 74, CI [0.093287, 0.170485]). The intervals do
not overlap, Mann-Whitney gives p = 0.005483 and a permutation test on the
median difference gives p = 0.000100 -- BUT Brunner-Munzel, which does not
assume the 2 groups have equal spread, gives p = 0.104133. The spreads differ
markedly and the larger group is 6 rounds, so the direction is consistent across
3 tests while significance is NOT robust to the variance difference. Quoting
only the Mann-Whitney figure would have overstated it.

2 CORRECTIONS THIS SCRIPT RECORDS AGAINST ITS OWN FIRST READING, because both
were produced by this instrument before being caught by it.

  1. A FIRST PASS FOUND THE OPPOSITE RESULT -- 4-or-more-seat rounds appearing to
     waste almost NOTHING, a median idle share of 0.000014 against 0.128978 for
     2-seat rounds, at p = 2.814701e-04. It was an artefact of counting any JSON
     file carrying `model` and `elapsed_s` as a panel seat. Experiment
     directories hold per-round finding files, so one "round" was credited with
     144 seats, and 34 of 60 supposed 4-seat rounds had ZERO seats succeed. A
     panel seat record is now identified by the `route` field, which only
     `dispatch` writes, and by rejecting the `r<digit>_` round-prefixed files
     that experiments produce. The seat-count distribution is then 78 rounds of
     2, 4 of 5 and 6 of 7, which matches a panel of at most 6 seats plus retries.
  2. THE MTIME RECONSTRUCTION IS NOT VALID EVERYWHERE and the first pass did not
     bound it, giving a mean idle of 80,028.9 s and a start spread of
     129,292.6 s -- both impossible. A seat file rewritten days later carries a
     meaningless mtime. The bound applied now is a NECESSARY condition rather
     than a judgement: under any dispatch pattern, serial, staggered or fully
     concurrent, a round's wall clock cannot exceed the sum of its seat durations
     plus what the staggers add, at most 20 s per seat over at most 6 seats. With
     the seat detector of correction 1 in place, 4 of 92 candidate rounds are
     excluded by the bound, 0.043478, counted here rather than silently dropped.
     The figure is small BECAUSE the 2 corrections overlap: identifying seats by
     `route` already removes most directories whose mtimes were meaningless, and
     the bound catches what remains. Quoting the 0.1183 measured under the loose
     detector would misstate this producer's own behaviour.

AN INDEPENDENT CORROBORATION FALLS OUT, and it was not sought. The median saving
against strict serialisation reads 0.436250 by this method against the 0.396900
committed by `scripts/the_contention_evidence_is_cap_confounded_2026-10-07.py`,
which measured it from seat durations alone. 2 instruments on different inputs,
differing by 0.039350.

Run with --help to read this without computing anything.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

import numpy as np

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
from _cli_help import answer_help  # noqa: E402

LOGS = REPO / "bench" / "logs"
NOT_A_SEAT = {"topology.json", "runner_state.json", "seat_proposals.json",
              "completion_barrier.json"}
#: Experiment directories name their per-round seat files `r1_cc2-sim_...json`.
#: Counting those as panel seats is what produced a 144-seat round.
ROUND_PREFIXED = re.compile(r"^r\d+_")
#: 20 s of stagger over at most 6 seats. The bound is a necessary condition on
#: any dispatch pattern, not a tuned tolerance.
MAX_STAGGER_SLACK_S = 120.0
SEED = 20261028
RESAMPLES = 20000


def _seat_records(round_dir: pathlib.Path) -> list[tuple[str, float, float, bool, bool]]:
    """Panel seat replies in one round directory, as (model, mtime, dur, ok).

    `route` is the discriminator: `dispatch` writes it on every seat record and
    nothing else in the tree does. The 5th element says whether the completion
    time is an EXACT stamp or a reconstruction from the file's mtime, so a
    mixed corpus reports which it used rather than blurring the two.
    """
    out = []
    for p in sorted(round_dir.glob("*.json")):
        if (p.name.startswith("_") or ".tools" in p.name
                or p.name in NOT_A_SEAT or ROUND_PREFIXED.match(p.name)):
            continue
        try:
            o = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if (isinstance(o, dict) and "route" in o and "model" in o
                and isinstance(o.get("elapsed_s"), (int, float))):
            # ★ PREFER THE EXACT STAMP OVER THE FILE'S MTIME, 2026-10-28. Both
            # dispatch paths now record `t_end_epoch` at the moment the seat
            # finishes, so a round written after this date needs no
            # reconstruction at all and no exclusion bound applies to it. The
            # mtime route stays for the 88 archived rounds that predate the
            # stamps -- deleting it would throw away the only evidence that
            # answers his question today.
            end = o.get("t_end_epoch")
            out.append((str(o["model"]),
                        float(end) if isinstance(end, (int, float))
                        else p.stat().st_mtime,
                        float(o["elapsed_s"]), bool(o.get("ok")),
                        isinstance(end, (int, float))))
    return out


def simulated_round_barriers(run_dir: pathlib.Path) -> list[dict]:
    """★ THE BARRIER FOR A SIMULATED RUN, per ROUND. His ruling of 2026-10-28:
    *"Verdict. Do it and study it in the upcoming simulated run."*

    WHY THIS IS A SEPARATE READER AND NOT THE ONE ABOVE. 2 facts that look like
    an oversight and are not. First, `confer_maths_panel` writes
    `completion_barrier.json` at the end of its round; `reference_runner_v3` has
    its OWN dispatch path and calls nothing of the kind, so a simulated run
    stamps its seats and derives nothing. Second, the reader above DELIBERATELY
    rejects `r<digit>_` files -- that rejection is the fix for a loose detector
    that credited one "round" with 144 seats and reported the seat-count effect
    BACKWARDS. So the files that now carry the stamps are exactly the files that
    reader must keep ignoring.

    AND THE UNIT IS BETTER HERE. A simulated run writes one file per seat PER
    ROUND, so each round is its own barrier rather than one barrier for a whole
    directory. That is a finer measurement than the panel's, and it is the one
    his ruling asked for: the idle a round spends waiting on its slowest seat,
    round by round, from EXACT stamps with no reconstruction and no exclusion
    bound.
    """
    import re as _re
    import importlib.util as _il
    spec = _il.spec_from_file_location(
        "cdsfl_star_for_barrier", REPO / "bench" / "star_topology_2026-10-06.py")
    star = _il.module_from_spec(spec)
    spec.loader.exec_module(star)

    by_round: dict[str, list[dict]] = {}
    for f in sorted(run_dir.glob("r*_*.json")):
        m = _re.match(r"^(r\d+)_", f.name)
        if not m:
            continue
        try:
            o = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        meta = o.get("metadata") if isinstance(o.get("metadata"), dict) else o
        if not (isinstance(meta.get("t_start_epoch"), (int, float))
                and isinstance(meta.get("t_end_epoch"), (int, float))):
            continue
        # `completion_barrier` reads `model`, `ok`, and both stamps.
        by_round.setdefault(m.group(1), []).append({
            "model": o.get("model") or f.name.split("_", 1)[1].split("_")[0],
            "ok": True,
            "elapsed_s": float(meta.get("elapsed", 0.0) or 0.0),
            "t_start_epoch": float(meta["t_start_epoch"]),
            "t_end_epoch": float(meta["t_end_epoch"]),
        })
    out = []
    for rnd in sorted(by_round, key=lambda r: int(r[1:])):
        rec = star.completion_barrier(by_round[rnd], 0.0)
        rec["round"] = rnd
        out.append(rec)
    return out


def reconstruct() -> tuple[list[dict], list[dict]]:
    """Every plausible round, and every round the bound excludes, with reasons."""
    kept, dropped = [], []
    for d in sorted(p for p in LOGS.iterdir() if p.is_dir()):
        recs = _seat_records(d)
        if len(recs) < 2:
            continue
        starts = [m - dur for _n, m, dur, _ok, _x in recs]
        ends = [m for _n, m, _d, _ok, _x in recs]
        durs = [dur for _n, _m, dur, _ok, _x in recs]
        r0, r1 = min(starts), max(ends)
        wall, serial = r1 - r0, sum(durs)
        if wall <= 0:
            dropped.append({"round": d.name, "why": "non-positive wall clock",
                            "wall": wall, "serial": serial})
            continue
        if wall > serial + MAX_STAGGER_SLACK_S:
            dropped.append({"round": d.name, "wall": wall, "serial": serial,
                            "why": "wall exceeds the sum of seat durations, so a "
                                   "seat file was written long after its round"})
            continue
        idle = sum(r1 - e for e in ends)
        kept.append({"round": d.name, "n": len(recs), "wall_s": wall,
                     "exact_stamps": sum(1 for *_x, ex in recs if ex),
                     "idle_s": idle, "idle_share": idle / (len(recs) * wall),
                     "serial_s": serial, "saving_vs_serial": 1 - wall / serial,
                     "n_ok": sum(1 for _n, _m, _d, ok, _s in recs if ok),
                     "duration_spread_s": max(durs) - min(durs)})
    return kept, dropped


def _median_ci(a: np.ndarray, rng) -> tuple[float, float]:
    bs = np.array([np.median(rng.choice(a, len(a))) for _ in range(RESAMPLES)])
    return float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))


def measure() -> dict:
    from scipy import stats

    all_kept, dropped = reconstruct()
    # ★ THE HEADLINE IS THE ARCHIVAL CORPUS, AND IT IS FIXED. 2026-10-28.
    # Both dispatch paths now stamp `t_end_epoch`, so every round run from here
    # adds a STAMPED row -- and the first such round moved the median from
    # 0.144892 to 0.136904 within minutes of the stamps landing. Pinning a
    # figure that every future round moves is a FLAKY guard, which this project
    # has measured as worse than a red one. So the headline is computed over the
    # RECONSTRUCTED rounds, a closed set that cannot grow, and the stamped
    # rounds are reported beside it as their own figure. Nothing is discarded;
    # the 2 provenances are simply not averaged together.
    kept = [r for r in all_kept if r["exact_stamps"] == 0]
    stamped = [r for r in all_kept if r["exact_stamps"] == r["n"]]
    rng = np.random.default_rng(SEED)
    sh = np.array([r["idle_share"] for r in kept])
    idl = np.array([r["idle_s"] for r in kept])
    sv = np.array([r["saving_vs_serial"] for r in kept])
    lo, hi = _median_ci(sh, rng)
    r = {
        "n_candidate": len(kept) + len(dropped),
        "n_kept": len(kept),
        "n_dropped": len(dropped),
        "dropped_share": len(dropped) / max(len(kept) + len(dropped), 1),
        "dropped_examples": sorted(dropped, key=lambda x: -x["wall"])[:3],
        "n_all_kept": len(all_kept),
        "rounds_with_exact_stamps": len(stamped),
        "rounds_reconstructed": len(kept),
        # Reported, never pinned: this set grows with every round that runs.
        "stamped_idle_share_median": (float(np.median([x["idle_share"] for x in stamped]))
                                      if stamped else float("nan")),
        "stamped_rounds": [x["round"] for x in stamped][:6],
        "seat_counts": {int(k): int(v) for k, v in
                        zip(*np.unique([r_["n"] for r_ in kept], return_counts=True))},
        "idle_share_mean": float(sh.mean()),
        "idle_share_median": float(np.median(sh)),
        "idle_share_ci": (lo, hi),
        "idle_share_quartiles": [float(x) for x in np.quantile(sh, [0.25, 0.75])],
        "idle_share_max": float(sh.max()),
        "idle_s_median": float(np.median(idl)),
        "idle_hours_total": float(idl.sum() / 3600.0),
        "rounds_over_30pc": int((sh > 0.30).sum()),
        "rounds_over_30pc_share": float((sh > 0.30).mean()),
        "saving_vs_serial_median": float(np.median(sv)),
        "committed_saving_2026_10_07": 0.3969,
    }
    r["saving_agreement_gap"] = abs(r["saving_vs_serial_median"]
                                   - r["committed_saving_2026_10_07"])

    # THE SEAT-COUNT QUESTION, on rounds where every seat succeeded, because a
    # failed seat's duration is set by a cap rather than by its work.
    clean = [x for x in kept if x["n_ok"] == x["n"]]
    two = np.array([x["idle_share"] for x in clean if x["n"] == 2])
    many = np.array([x["idle_share"] for x in clean if x["n"] >= 4])
    r["n_clean"] = len(clean)
    r["two_seat_n"], r["many_seat_n"] = len(two), len(many)
    r["two_seat_median"] = float(np.median(two)) if len(two) else float("nan")
    r["many_seat_median"] = float(np.median(many)) if len(many) else float("nan")
    r["two_seat_ci"] = _median_ci(two, rng) if len(two) > 1 else (float("nan"),) * 2
    r["many_seat_ci"] = _median_ci(many, rng) if len(many) > 1 else (float("nan"),) * 2
    if len(two) > 2 and len(many) > 2:
        u, p_mw = stats.mannwhitneyu(two, many, alternative="two-sided")
        r["mannwhitney_u"], r["mannwhitney_p"] = float(u), float(p_mw)
        r["rank_biserial"] = float(1 - 2 * u / (len(two) * len(many)))
        bm = stats.brunnermunzel(two, many)
        r["brunnermunzel_p"] = float(bm.pvalue)
        perm = stats.permutation_test(
            (two, many), lambda a, b: np.median(a) - np.median(b),
            n_resamples=RESAMPLES, alternative="two-sided", random_state=SEED)
        r["permutation_p"] = float(perm.pvalue)
        # 3 TESTS, AND THEY DISAGREE. That disagreement IS the finding about how
        # far the seat-count result can be pushed.
        r["seat_count_robust"] = bool(r["brunnermunzel_p"] < 0.05)
        r["intervals_disjoint"] = bool(r["two_seat_ci"][1] < r["many_seat_ci"][0])
    return r


def latest_stamped_run() -> pathlib.Path | None:
    """The newest run directory whose per-round seat files carry both stamps."""
    for d in sorted((q for q in LOGS.iterdir() if q.is_dir()),
                    key=lambda q: q.stat().st_mtime, reverse=True):
        for f in d.glob("r*_*.json"):
            try:
                o = json.loads(f.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            meta = o.get("metadata") if isinstance(o.get("metadata"), dict) else o
            if isinstance(meta.get("t_end_epoch"), (int, float)):
                return d
    return None


def _simulated_report(which: str) -> list[dict]:
    """Print one simulated run's PER-ROUND barrier. Returns the rows.

    ★ THIS IS WHAT MAKES `simulated_round_barriers` REACHABLE. That function was
    added and then reached by NOTHING -- no test, not even this script's own
    `main` -- which is the unwired-addition half of the additive standard,
    committed within an hour of a memory file being written about exactly that
    failure. The FFAFP stop gate asked for the FOLLOW that found it.
    """
    import numpy as np
    run = latest_stamped_run() if which == "latest" else (LOGS / which)
    if run is None or not run.is_dir():
        print(f"  no such run directory: {which!r}")
        return []
    rows = simulated_round_barriers(run)
    if not rows:
        print(f"  {run.name}: no per-round seat file carries both stamps. A run "
              f"from before 2026-10-28 cannot be measured this way, and the "
              f"archive reconstruction is what covers those.")
        return []
    print("=" * 78)
    print(f"PER-ROUND COMPLETION BARRIER -- {run.name}")
    print("=" * 78)
    print("\n  from EXACT stamps: no reconstruction, no exclusion bound\n")
    print(f"  {'round':>6} {'seats':>5} {'wall s':>9} {'idle s':>9} "
          f"{'idle share':>11}  slowest")
    for r in rows:
        print(f"  {r['round']:>6} {r['n_timed']:>5} {r['round_wall_s']:>9.1f} "
              f"{r['total_idle_s']:>9.1f} {r['idle_share']:>11.6f}  "
              f"{r['slowest_seat']}")
    sh = np.array([r["idle_share"] for r in rows])
    idle = sum(r["total_idle_s"] for r in rows)
    print(f"\n  median idle share {np.median(sh):.6f}, mean {sh.mean():.6f}, "
          f"max {sh.max():.6f}")
    print(f"  total idle {idle / 60:.1f} minutes across {len(rows)} round(s)")
    slow = [r["slowest_seat"] for r in rows]
    top = max(set(slow), key=slow.count)
    k = slow.count(top)
    if len(rows) > 1 and k == len(rows):
        from scipy import stats
        seats = max(r["n_timed"] for r in rows)
        pv = float(stats.binomtest(k, len(rows), 1.0 / seats,
                                   alternative="greater").pvalue)
        print(f"  ★ ONE SEAT IS THE CRITICAL PATH IN {k} OF {len(rows)} "
              f"ROUNDS: {top}")
        print(f"    exact binomial against a 1-in-{seats} null: p = {pv:.9f}")
    return rows


def main() -> int:
    # `takes_no_arguments=False` IS REQUIRED HERE, and its absence made every
    # flag below unreachable. `answer_help` defaults to refusing ANY argument
    # before the caller's own parser runs, so `--json` and `--trials` exited 2
    # with "this script takes no arguments" -- an unwired addition of exactly
    # the kind the additive standard forbids, and invisible to the guards
    # because they call `measure()` directly rather than the command line.
    answer_help(__doc__, __file__, takes_no_arguments=False)
    ap = argparse.ArgumentParser(
        description="Measure the completion-barrier cost over archived rounds.")
    ap.add_argument("--json", action="store_true", help="emit figures as JSON")
    ap.add_argument("--simulated-run", metavar="DIR", default=None,
                    help="a simulated run directory under bench/logs/: report "
                         "its PER-ROUND barrier from the exact stamps instead "
                         "of the archive reconstruction. Pass 'latest' for the "
                         "newest run carrying stamped seat files.")
    args = ap.parse_args()
    if args.simulated_run:
        rows = _simulated_report(args.simulated_run)
        if args.json:
            print(json.dumps(rows, indent=2, default=str))
        return 0 if rows else 1
    r = measure()
    if args.json:
        print(json.dumps(r, indent=2, default=str))
        return 0

    print("=" * 78)
    print("WHAT A ROUND SPENDS WAITING ON ITS SLOWEST SEAT")
    print("=" * 78)
    print(f"\n1. THE CORPUS, with its exclusions counted")
    print(f"   candidate rounds {r['n_candidate']}; plausible {r['n_all_kept']}; "
          f"excluded {r['n_dropped']} ({r['dropped_share']:.6f})")
    print(f"   HEADLINE CORPUS: the {r['n_kept']} RECONSTRUCTED rounds, a closed "
          f"set that cannot grow")
    shown = len(r["dropped_examples"])
    print(f"   the {shown} largest exclusions"
          + (f", of {r['n_dropped']} in all" if r["n_dropped"] > shown else "")
          + ":")
    for d in r["dropped_examples"]:
        print(f"     {d['round'][:44]:44s} wall {d['wall']:.0f}s vs serial "
              f"{d['serial']:.0f}s")
    if r["n_dropped"] > shown:
        print(f"     ... and {r['n_dropped'] - shown} more not shown; every one "
              f"is counted in the figure above")
    print(f"   seat counts: {r['seat_counts']}")
    print(f"   completion times: {r['rounds_with_exact_stamps']} round(s) from EXACT "
          f"stamps, {r['rounds_reconstructed']} reconstructed from mtimes")
    if r["rounds_with_exact_stamps"]:
        print(f"   STAMPED rounds, reported and NOT pinned because the set grows: "
              f"median idle share {r['stamped_idle_share_median']:.6f} over "
              f"{r['rounds_with_exact_stamps']}  {r['stamped_rounds']}")

    print(f"\n2. THE BARRIER COST")
    print(f"   idle share of available seat-time: median "
          f"{r['idle_share_median']:.6f}, 95% CI "
          f"[{r['idle_share_ci'][0]:.6f}, {r['idle_share_ci'][1]:.6f}]")
    print(f"   mean {r['idle_share_mean']:.6f}, quartiles "
          f"{[round(x, 6) for x in r['idle_share_quartiles']]}, max "
          f"{r['idle_share_max']:.6f}")
    print(f"   median {r['idle_s_median']:.1f}s per round; "
          f"{r['idle_hours_total']:.2f} hours across the archive")
    print(f"   rounds wasting over 0.30: {r['rounds_over_30pc']} of {r['n_kept']} "
          f"({r['rounds_over_30pc_share']:.6f})")

    print(f"\n3. DOES IT WORSEN WITH SEAT COUNT? SUGGESTIVE, NOT ESTABLISHED")
    print(f"   2 seats : n={r['two_seat_n']:3d} median {r['two_seat_median']:.6f} "
          f"CI [{r['two_seat_ci'][0]:.6f}, {r['two_seat_ci'][1]:.6f}]")
    print(f"   4+ seats: n={r['many_seat_n']:3d} median {r['many_seat_median']:.6f} "
          f"CI [{r['many_seat_ci'][0]:.6f}, {r['many_seat_ci'][1]:.6f}]")
    if "mannwhitney_p" in r:
        print(f"   Mann-Whitney p {r['mannwhitney_p']:.6f} (rank-biserial "
              f"{r['rank_biserial']:+.6f})")
        print(f"   permutation on the median difference p {r['permutation_p']:.6f}")
        print(f"   Brunner-Munzel p {r['brunnermunzel_p']:.6f}  <- does NOT assume "
              f"equal spread")
        print(f"   intervals disjoint: {r['intervals_disjoint']};  robust across "
              f"all 3 tests: {r['seat_count_robust']}")

    print(f"\n4. AN INDEPENDENT CORROBORATION, NOT SOUGHT")
    print(f"   saving against strict serialisation, this method: "
          f"{r['saving_vs_serial_median']:.6f}")
    print(f"   committed 2026-10-07 figure from seat durations alone: "
          f"{r['committed_saving_2026_10_07']:.6f}")
    print(f"   difference {r['saving_agreement_gap']:.6f}")

    print("\n" + "=" * 78)
    print("VERDICT")
    print("=" * 78)
    print("""
  1. YES, a collaborative round pays a real completion-barrier cost. The
     stagger cannot address it: a stagger governs STARTS, and this is wholly a
     property of FINISHES.
  2. The seat-count effect points the way his question anticipated, and 3 tests
     do not agree on its significance. It must be quoted with its n of 6 and
     with the Brunner-Munzel result beside it.
  3. The prospective instrumentation is what settles it:
     `completion_barrier` in `bench/star_topology_2026-10-06.py` records the
     figures per round from absolute timestamps rather than from file mtimes,
     and no exclusion bound is then needed.
""")
    return 0


if __name__ == "__main__":
    sys.exit(main())
