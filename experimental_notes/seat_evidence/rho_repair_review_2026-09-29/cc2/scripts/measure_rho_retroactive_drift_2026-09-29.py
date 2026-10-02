# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'rho_repair_review_2026-09-29', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: c188cfd64affe5ca793f03cb93edf5a5f1922ec1b82953f20ab13297da578d1f
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Q2, MEASURED: how stale is `rho_history` when only `novelty_counts[-1]` is
overwritten, now that option 3 makes the numerator RETROACTIVE?

The runner overwrites `novelty_counts[-1]` each round, so round r keeps the
value known at round r. Before option 3 that value could only move when an
entry's STATUS later changed. Under option 3 it also moves when a codiscovery
arrives in ANY later round, because a discount is keyed on `open_since_round`,
not on the round the occasion was recorded. This script replays each archived
run round by round -- restricting the registry to what was visible at round K --
and compares the live "overwrite [-1] only" series against a full resettle.

Reads only bench/logs/**/runner_state.json. Writes nothing. No arguments.
"""
from __future__ import annotations
import argparse, json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class _Reg:
    def __init__(self, e): self.entries = e


def _reconstruct(entries, alias_map):
    for cid, e in entries.items():
        if not isinstance(e, dict):
            continue
        for cd in e.get("codiscovery") or []:
            model, fid = cd.get("model") or "", cd.get("finding_id") or ""
            e.setdefault("occasions", []).append({
                "model": model, "round": e.get("open_since_round", 0),
                "alias": fid,
                "from_canonical": alias_map.get(f"{model}:{fid}", cid),
                "via": "codiscovery", "similarity": cd.get("similarity", 0.0)})


def _visible_at(entries, k):
    """The registry as it stood at the END of round k: entries opened by then,
    occasions recorded by then."""
    out = {}
    for cid, e in entries.items():
        if not isinstance(e, dict):
            continue
        r = e.get("open_since_round")
        if r is None or r > k:
            continue
        c = dict(e)
        c["occasions"] = [o for o in (e.get("occasions") or [])
                          if not isinstance(o, dict)
                          or o.get("via") != "codiscovery"
                          or (o.get("round") is not None and o["round"] <= k)]
        out[cid] = c
    return out


def main() -> int:
    argparse.ArgumentParser(description=__doc__.splitlines()[0],
                            epilog="No arguments. Exit 0.").parse_args()
    import bench.reference_runner_v3 as R
    cfg = R.RunnerConfig()
    tot_rounds = tot_stale = 0
    affected = []
    for fp in sorted((ROOT / "bench" / "logs").glob("**/runner_state.json")):
        try:
            st = json.loads(fp.read_text(encoding="utf-8", errors="ignore"))
        except Exception:                                    # noqa: BLE001
            continue
        rg = st.get("registry") or {}
        ents = rg.get("entries")
        if not isinstance(ents, dict) or not ents:
            continue
        ents = json.loads(json.dumps(ents))
        _reconstruct(ents, rg.get("alias_map") or {})
        maxr = max((e.get("open_since_round") or 0) for e in ents.values()
                   if isinstance(e, dict))
        raw = st.get("raw_counts") or []
        if len(raw) <= maxr:
            continue
        live = []                       # what the runner keeps: value at the time
        for k in range(maxr + 1):
            a, _ = R._corroborated_novelty_series(_Reg(_visible_at(ents, k)), k)
            live.append(a[k])
        final, _ = R._corroborated_novelty_series(_Reg(ents), maxr)
        stale = [k for k in range(maxr + 1) if live[k] != final[k]]
        tot_rounds += maxr + 1
        tot_stale += len(stale)
        if stale:
            rl = [round(live[k] / raw[k], 4) if raw[k] else 0.0 for k in range(maxr + 1)]
            rf = [round(final[k] / raw[k], 4) if raw[k] else 0.0 for k in range(maxr + 1)]
            affected.append((fp.parent.name, stale, live, final, rl, rf))
    print("=" * 78)
    print("Q2: RETROACTIVITY OF THE OPTION-3 NUMERATOR")
    print("=" * 78)
    for name, stale, live, final, rl, rf in affected:
        print(f"\n--- {name}  ({len(stale)} of {len(live)} rounds stale) ---")
        print(f"  novelty as-known-then : {live}")
        print(f"  novelty fully resettled: {final}")
        print(f"  rho    as-known-then  : {rl}")
        print(f"  rho    fully resettled: {rf}")
    from statsmodels.stats.proportion import proportion_confint
    lo, hi = proportion_confint(tot_stale, tot_rounds, 0.05, method="wilson")
    print(f"\nARCHIVE REPLAY: {tot_stale}/{tot_rounds} rounds stale "
          f"= {100*tot_stale/tot_rounds:.4f}%  Wilson [{100*lo:.4f}%, "
          f"{100*hi:.4f}%], runs affected {len(affected)}")
    print("""
    THIS ZERO IS AN ARTEFACT AND MUST NOT BE READ AS EVIDENCE OF SOUNDNESS.
    The archived `codiscovery` records carry model / finding_id / similarity and
    NO ROUND, so the replay has to stamp each reconstructed occasion with the
    target's own `open_since_round`. Every occasion is therefore visible in the
    same round its target opened, and the round-by-round replay cannot express
    a LATE corroboration at all. The archive is structurally incapable of
    answering Q2; a scan over it returns 0 by construction. Recorded as
    UNMEASURABLE-FROM-ARCHIVE, not as measured-clean.

    The live path is different, and that difference is the whole question:
    `_backfill_occasion` writes `"round": int(round_idx)` -- the round the
    corroboration ARRIVED -- while `_corroborated_novelty_series` buckets the
    discount by the discounted entry's `open_since_round`. The two are not the
    same round, which is exactly what makes the numerator retroactive.
    Demonstrated by construction below.""")

    print("\n" + "=" * 78)
    print("CONSTRUCTED DEMONSTRATION: a round-3 corroboration rewrites round 1")
    print("=" * 78)
    print("""  The discount always lands on the LATER-opened of the two canonicals,
  so it reaches back only when BOTH opened before the round the occasion is
  recorded. That is not a corner case: it is the RESUME BACKFILL path added on
  2026-09-29. `record_codiscovery` returns early when the alias is already in
  `source_aliases`, and now calls `_backfill_occasion` with the CURRENT
  round_idx on an alias first recorded rounds earlier. `from_canonical` then
  resolves through `_alias_map` to that older canonical.""")

    def _f(fid, model, rnd):
        return R.Finding(finding_id=fid, model_id=model, round_idx=rnd,
                         flaw_class="logic", severity=0.9,
                         abstraction_index=0.5, description="d",
                         proposed_fix="f", target_file="t.py")

    reg = R.FindingRegistry()
    t = reg.register(_f("FT", "A", 0), "A")          # target, round 0
    reg.register(_f("FD", "B", 1), "B")              # duplicate, round 1
    reg.entries[t].setdefault("source_aliases", []).append("FD")   # alias known
    raw = [2, 2, 1, 2]
    before, _ = R._corroborated_novelty_series(reg, 3)
    rho_before = [round(before[k] / raw[k], 4) for k in range(4)]
    # Round 3: resume backfill writes the occasion for an alias from round 1.
    reg.record_codiscovery(t, "B", "FD", 0.9, round_idx=3)
    after, _ = R._corroborated_novelty_series(reg, 3)
    rho_after = [round(after[k] / raw[k], 4) for k in range(4)]
    print(f"\n  raw_counts                          : {raw}")
    print(f"  novelty BEFORE the round-3 occasion : {before}   rho {rho_before}")
    print(f"  novelty AFTER  the round-3 occasion : {after}   rho {rho_after}")
    moved = [k for k in range(4) if before[k] != after[k]]
    print(f"  rounds whose novelty MOVED          : {moved}")
    stale = [k for k in moved if k != 3]
    print(f"  the runner overwrites only index [-1]=3, so round(s) {stale} keep")
    print(f"  a value the registry no longer supports.")
    cfg_w = cfg.rho_rolling_window
    print(f"\n  AND IT PROPAGATES. rho_rolling_window={cfg_w}, and `_compute_rho`")
    print(f"  reads the STORED novelty_counts[i] over that window, so a stale")
    print(f"  index inside it moves rho_avg -- the quantity the churn flag tests.")
    live_avg = sum(before[k] / raw[k] for k in range(1, 4)) / 3
    true_avg = sum(after[k] / raw[k] for k in range(1, 4)) / 3
    print(f"  rho_avg over rounds 1-3, as stored    : {live_avg:.4f}")
    print(f"  rho_avg over rounds 1-3, resettled    : {true_avg:.4f}")
    print(f"  difference                            : {live_avg - true_avg:+.4f}"
          f"  (threshold {cfg.rho_threshold})")
    assert stale, "retroactivity not demonstrated -- re-examine before trusting this"
    assert abs(live_avg - true_avg) > 1e-9, "no propagation into rho_avg"
    print("\n  VERDICT: the option-3 numerator IS retroactive, the [-1]-only")
    print("  overwrite cannot reach the round it rewrites, and the error lands")
    print("  inside rho's rolling window.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
