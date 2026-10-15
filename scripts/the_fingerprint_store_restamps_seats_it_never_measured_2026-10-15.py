#!/usr/bin/env python3
"""A simulated run restamps the REAL paid seats' fingerprints. Measured.

OBSERVED 2026-10-15 08:19 BST, while free run 1 was in its post-convergence
sweep: all 11 files in `bench/fingerprints/` were written at 08:17:00, the
convergence moment, and 5 of them are the REAL paid seats -- CC2, ChatGPT,
Codex, DeepSeek, Gemini -- which were never dispatched in a simulated run.
`bench/fingerprints/CC2.json` now carries
`"experiment": "free_run1_directive_whole_20261015T061123Z"`.

THIS IS NOT A NEW FINDING AND THE CREDIT IS NOT CC1's. The `fable` seat found
it on 2026-10-05 during the fingerprint ladder review and named the mechanism
exactly, in section 3 of a script titled "THE FINGERPRINT STORE ERASES RUN
PROVENANCE ON EVERY SAVE":

    "`_load_fingerprints` loads ALL files and `_save_fingerprints` writes back
     every model in the loaded dict, so the last run to save re-attributes
     profiles it did not measure -- real and -SIM alike. Any per-model
     falsification rate persisted here inherits this."

When this was written that script existed ONLY inside the 2026-10-05 fingerprint
ladder review's sandbox harvest -- absent from `scripts/`, and `grep -i
fingerprint` over the master task list returned 4 hits, none of them this. It
has since been PROMOTED to
`scripts/the_provenance_gate_reads_text_not_behaviour_2026-10-05.py`, 7,214
bytes unchanged beneath a header naming the fable seat as its author, which is
the reachable copy a reader should open. The harvest location is described
rather than cited because `bench/logs/` is gitignored. SO THE SECOND FINDING HERE IS THE PROCESS
ONE: a seat found a real defect, wrote the producer, and it never left the
sandbox. Same shape as the 41 of 220 harvested seat files that existed nowhere
else (`feedback_never_delete_bulk_resources`).

THE CAUSE, in `bench/reference_runner_v3.py:11324-11350`:
  * `_load_fingerprints()` globs EVERY `*.json` in the directory into one dict
    keyed by `model_id`, discarding `experiment` and `timestamp`.
  * `_save_fingerprints(observed, experiment_name)` iterates EVERY key of that
    dict and rewrites each file with THIS run's name and a fresh timestamp.
So any run restamps every seat that has ever had a fingerprint file.

WHAT MAKES IT RECORD-ONLY TODAY, AND WHAT WOULD MAKE IT DATA-BEARING. The
`observed` payload is not inert: it carries `total_findings`, 400 for CC2,
`rounds_participated` 274, `avg_findings_per_round`, `quality_at_capacity`,
`D_decay`, and the 3 fields that FEED LIVE DECISIONS --
`compression_threshold`, `decomposition_recommended` and
`max_successful_prompt_chars`. The real seats' values did NOT move in run 1,
because those seats were never dispatched and so nothing was appended. The
separation holds for exactly one reason: the mandatory `-SIM` suffix makes
`CC2-SIM` a DIFFERENT dict key from `CC2`. That naming rule, recorded in the
project CLAUDE.md as a provenance rule about labels, is therefore also the
only thing standing between a simulated run and the real seats' accumulated
counters. Drop the suffix and this becomes data corruption rather than a
mislabelled record.

NOT FIXED HERE. Run 1 is in flight and a fix to the save path is a change to
live run machinery; `fixes are SUGGESTED to HIL, never auto-applied`. The
operational step taken instead is to RESTORE the 5 real-seat files to HEAD and
commit only the 6 `-SIM` files, so the committed record carries true
provenance.
"""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys

# `_cli_help` lives in scripts/. Locate it rather than assume a depth.
for _cand in (pathlib.Path(__file__).resolve().parent,
              *pathlib.Path(__file__).resolve().parents):
    if (_cand / "_cli_help.py").is_file():
        sys.path.insert(0, str(_cand))
        break
from _cli_help import answer_help  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[1]
FP = REPO / "bench/fingerprints"
REAL = ["CC2", "ChatGPT", "Codex", "DeepSeek", "Gemini"]
SIM = ["CC2-SIM", "ChatGPT-SIM", "Codex-SIM", "DeepSeek-SIM", "Fable-SIM", "Gemini-SIM"]
DECISION_FIELDS = [
    "compression_threshold",
    "decomposition_recommended",
    "max_successful_prompt_chars",
]


def _head(rel: str) -> dict | None:
    r = subprocess.run(["git", "show", f"HEAD:{rel}"],
                       capture_output=True, text=True, cwd=REPO)
    if r.returncode != 0:
        return None
    return json.loads(r.stdout)


def main() -> int:
    from statsmodels.stats.proportion import proportion_confint
    from scipy import stats as sstats

    print("=" * 74)
    print("1. WHICH SEATS DID THE SIMULATED RUN RESTAMP?")
    print("=" * 74)
    restamped, values_moved = [], []
    for seat in REAL:
        rel = f"bench/fingerprints/{seat}.json"
        old, new = _head(rel), json.loads((FP / f"{seat}.json").read_text())
        if old is None:
            continue
        stamp = old.get("experiment") != new.get("experiment")
        o = {k: v for k, v in old.items() if k not in ("experiment", "timestamp")}
        n = {k: v for k, v in new.items() if k not in ("experiment", "timestamp")}
        if stamp:
            restamped.append(seat)
        if o != n:
            values_moved.append(seat)
        print(f"  {seat:<10} restamped={stamp!s:<5} values_moved={o != n!s:<5} "
              f"{old.get('experiment')} -> {new.get('experiment')}")

    k, n_real = len(restamped), len(REAL)
    lo, hi = proportion_confint(k, n_real, method="beta")
    lo_w, hi_w = proportion_confint(k, n_real, method="wilson")
    print(f"\n  restamped: {k} of {n_real}")
    print(f"    Clopper-Pearson 95% [{lo*100:.4f}%, {hi*100:.4f}%]")
    print(f"    Wilson          95% [{lo_w*100:.4f}%, {hi_w*100:.4f}%]")
    print(f"  observed values altered: {len(values_moved)} of {n_real}")
    lo2, hi2 = proportion_confint(len(values_moved), n_real, method="beta")
    print(f"    Clopper-Pearson 95% [{lo2*100:.4f}%, {hi2*100:.4f}%]")

    print()
    print("=" * 74)
    print("2. IS THERE A MERGE PATH FROM A -SIM SEAT INTO A REAL SEAT?")
    print("=" * 74)
    # If CC2-SIM's observations had merged into CC2, the decision fields would
    # match. Disjoint values are the evidence that the -SIM suffix separates them.
    collisions = 0
    for sim in SIM:
        base = sim[:-4]
        if base not in REAL:
            print(f"  {sim:<14} -> no real counterpart named {base}")
            continue
        sp = FP / f"{sim}.json"
        rp = FP / f"{base}.json"
        if not sp.exists() or not rp.exists():
            continue
        so = json.loads(sp.read_text())["observed"]
        ro = json.loads(rp.read_text())["observed"]
        same = {f: (so.get(f), ro.get(f)) for f in DECISION_FIELDS
                if so.get(f) == ro.get(f)}
        identical = len(same) == len(DECISION_FIELDS)
        if identical:
            collisions += 1
        print(f"  {sim:<14} vs {base:<10} decision fields identical={identical}")
        for f in DECISION_FIELDS:
            print(f"      {f:<30} SIM={json.dumps(so.get(f))[:22]:<24} REAL={json.dumps(ro.get(f))[:22]}")

    print(f"\n  seats where SIM and REAL carry identical decision fields: {collisions}")
    print("  (0 means the -SIM suffix is what keeps the records separate)")

    print()
    print("=" * 74)
    print("3. WAS THE 2026-10-05 FINDING EVER PROMOTED OUT OF THE SANDBOX?")
    print("=" * 74)
    harvested = (REPO / "bench/logs/fingerprint_ladder_review_2026-10-05/"
                 "sandbox_harvest/fable/attempt-1/files/scripts/"
                 "the_provenance_gate_reads_text_not_behaviour_2026-10-05.py")
    live = REPO / "scripts/the_provenance_gate_reads_text_not_behaviour_2026-10-05.py"
    tasks = (REPO / "experimental_notes/CDSFL_MASTER_TASK_LIST.md").read_text()
    fp_hits = tasks.lower().count("fingerprint")
    names_this = "erases run provenance" in tasks.lower() or "restamp" in tasks.lower()
    print(f"  fable's producer exists in the harvest : {harvested.exists()}")
    print(f"  the same producer exists in scripts/   : {live.exists()}")
    print(f"  'fingerprint' hits in master task list : {fp_hits}")
    print(f"  task list names THIS defect            : {names_this}")
    promoted = live.exists() or names_this
    print(f"  PROMOTED OUT OF THE SANDBOX            : {promoted}")

    print()
    print("=" * 74)
    print("VERDICT")
    print("=" * 74)
    print(f"  {k} of {n_real} real paid seats restamped by a simulated run")
    print(f"  {len(values_moved)} of {n_real} had any observed value altered -> RECORD-ONLY today")
    print(f"  {collisions} SIM/REAL decision-field collisions -> the -SIM suffix is load-bearing")
    print(f"  fable found this on 2026-10-05 and it was NOT promoted: {not promoted}")

    ok = (k == n_real and len(values_moved) == 0 and collisions == 0 and not promoted)
    out = {
        "observed_at": "2026-10-15T08:19+01:00",
        "restamped": restamped,
        "restamped_of_real": [k, n_real],
        "restamped_clopper_pearson": [lo, hi],
        "restamped_wilson": [lo_w, hi_w],
        "observed_values_altered": values_moved,
        "values_altered_clopper_pearson": [lo2, hi2],
        "sim_real_decision_field_collisions": collisions,
        "decision_fields_checked": DECISION_FIELDS,
        "prior_finding": {
            "by": "fable seat",
            "date": "2026-10-05",
            "producer": str(harvested.relative_to(REPO)),
            "promoted_to_scripts": live.exists(),
            "named_in_master_task_list": names_this,
        },
        "severity": "RECORD-ONLY today; DATA-BEARING if the -SIM suffix is ever dropped",
        "cause": "bench/reference_runner_v3.py:11324-11350 load-globs-all / save-writes-all",
        "all_assertions_hold": ok,
    }
    dest = REPO / "experimental_notes/evidence/fingerprint_restamp_2026-10-15.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, indent=2) + "\n")
    print(f"  evidence -> {dest.relative_to(REPO)}")
    return 0 if ok else 1


if __name__ == "__main__":
    answer_help(__doc__, __file__)
    sys.exit(main())
