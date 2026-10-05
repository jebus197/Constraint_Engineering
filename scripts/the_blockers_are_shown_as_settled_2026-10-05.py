#!/usr/bin/env python3
"""The findings that hold convergence open are shown to the panel as SETTLED.

THE DEFECT, in one sentence: `FindingRegistry.build_summary` renders UNCONFIRMED
findings in a section headed "SETTLED ... These findings are confirmed, closed, or
merged. Do not CHALLENGE or re-describe them.", while
`FindingRegistry.unverified_critical_count` counts those same findings as the A4
fail-safe blockers that keep the convergence gate shut.

So the panel is instructed not to touch the only findings standing between the run
and convergence. Three mechanisms independently route around the same class:

  1. `build_summary` labels them SETTLED and forbids challenge (this script).
  2. `_apply_routing` refuses them: its candidate test requires
     `severity >= CRITICAL_SEVERITY_THRESHOLD` (0.7), and the observed blockers were
     0.45 and 0.50 — `scripts/the_counter_and_the_router_disagree_2026-10-05.py`.
  3. `_post_convergence_sweep` is the only machinery that services them, and it runs
     after `converged` is assigned — `scripts/sweep_channels_are_post_verdict_2026-10-05.py`.

That is why the closing sweep looks like an afterthought: it is the only mechanism in
the schema that does not believe the "settled" label. And it is why 0 of 3473 archived
round replies carry an id-addressed falsifier
(`scripts/in_round_falsifiers_are_discarded_2026-10-05.py`) — the panel was told the
findings were settled.

METHOD. Nothing here reads source text to decide behaviour. The status-to-section map
is built by CALLING `build_summary` once per status in the runner's own status
vocabulary and observing which section the id lands in. The blocker set is obtained by
CALLING `unverified_critical_count` on each archived registry. The contradiction is
then the intersection, measured per run and pooled.

Proportions carry Wilson 95% intervals computed TWICE, by statsmodels and by an
independent closed-form implementation cross-checked against scipy's normal quantile,
per the two-tool rule.

Run:  python3 scripts/the_blockers_are_shown_as_settled_2026-10-05.py
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
LOGS = REPO / "bench" / "logs"
sys.path.insert(0, str(REPO))

TERMINAL = frozenset({"MERGED", "CLOSED", "REFUTED", "DUPLICATE"})

#: `compact_statuses` AS IT STOOD BEFORE 2026-10-05, i.e. the set whose members
#: `build_summary` rendered under the header "SETTLED ... confirmed, closed, or
#: merged. Do not CHALLENGE or re-describe them."
#:
#: PINNED AS A CONSTANT RATHER THAN READ FROM THE LIVE RENDERER, and the reason is
#: that the first version of this script WAS render-dependent and stopped
#: reproducing its own headline the moment the defect it measured was repaired:
#: it substring-matched each id against the rendered SETTLED block, which after the
#: repair returned 21 of 175 instead of 175 of 175 -- partly because UNCONFIRMED
#: had correctly moved, and partly because an id can appear inside that block for
#: unrelated reasons (a `merged_into` pointer, or the string occurring in another
#: finding's description), so the match was never sound even before the repair.
#: Membership in the historical status set is exact and is what the claim was
#: always about.
HISTORICAL_SETTLED_STATUSES = frozenset({
    "CONFIRMED", "UNCONFIRMED", "CLOSED", "MERGED", "ESCALATED", "WITHHELD"})


def _wilson_closed_form(k: int, n: int):
    """Wilson score interval, independent implementation. z from scipy."""
    if n == 0:
        return (float("nan"), float("nan"))
    from scipy.stats import norm
    z = float(norm.ppf(0.975))
    p = k / n
    d = 1.0 + z * z / n
    centre = (p + z * z / (2.0 * n)) / d
    half = (z * math.sqrt(p * (1.0 - p) / n + z * z / (4.0 * n * n))) / d
    return (max(0.0, centre - half) * 100.0, min(1.0, centre + half) * 100.0)


def _wilson_statsmodels(k: int, n: int):
    if n == 0:
        return (float("nan"), float("nan"))
    from statsmodels.stats.proportion import proportion_confint
    lo, hi = proportion_confint(k, n, alpha=0.05, method="wilson")
    return (lo * 100.0, hi * 100.0)


def _ci(k: int, n: int, label: str) -> str:
    a = _wilson_closed_form(k, n)
    b = _wilson_statsmodels(k, n)
    agree = (abs(a[0] - b[0]) < 1e-6 and abs(a[1] - b[1]) < 1e-6)
    pct = 100.0 * k / n if n else float("nan")
    note = "" if agree else "  *** THE TWO TOOLS DISAGREE — treat as UNVERIFIED ***"
    return (f"{label}: {k} of {n} = {pct:.4f}%, "
            f"Wilson [{a[0]:.4f}%, {a[1]:.4f}%] "
            f"(statsmodels [{b[0]:.4f}%, {b[1]:.4f}%]){note}")


def _parse_args(argv=None):
    p = argparse.ArgumentParser(
        prog="the_blockers_are_shown_as_settled_2026-10-05.py",
        description=__doc__.split("\n\n")[0])
    p.add_argument("--run", default=None, help="one run directory under bench/logs")
    return p.parse_args(argv)


def _section_for_status(status: str) -> str:
    """CALL build_summary with one entry of this status; report which section it
    lands in. This is the status-to-section map, derived by execution."""
    from bench.reference_runner_v3 import FindingRegistry
    reg = FindingRegistry()
    reg.entries = {
        "C0001": {"canonical_id": "C0001", "status": status, "severity": 0.45,
                  "verified": False, "verdicts": [], "description": "probe entry",
                  "source_model": "SIM", "proposed_fix": "", "open_since_round": 0,
                  "last_status_change_round": 0, "computed_evidence": [],
                  "routing_history": []},
    }
    try:
        text = reg.build_summary(3)
    except Exception as exc:  # noqa: BLE001
        return f"ERROR:{type(exc).__name__}"
    if "C0001" not in text:
        return "NOT SHOWN AT ALL"
    # which header precedes the id
    section = "?"
    for line in text.split("\n"):
        s = line.strip()
        if s.startswith("--- "):
            section = s.strip("- ").split(" (")[0]
        if "C0001" in line:
            break
    forbids = "Do not CHALLENGE" in text
    return f"{section}{'  [FORBIDS CHALLENGE]' if forbids and section == 'SETTLED' else ''}"


def main(argv=None) -> int:
    args = _parse_args(argv)
    from bench.reference_runner_v3 import FindingRegistry, FINDING_STATUS_VOCABULARY

    print("=" * 78)
    print("THE BLOCKERS ARE SHOWN TO THE PANEL AS SETTLED")
    print("=" * 78)
    print()
    print("-" * 78)
    print("STATUS -> SECTION, derived by CALLING build_summary once per status")
    print("-" * 78)
    settled_statuses = set()
    for st in sorted(FINDING_STATUS_VOCABULARY):
        sec = _section_for_status(st)
        if sec.startswith("SETTLED"):
            settled_statuses.add(st)
        print(f"  {st:<14} -> {sec}")
    print()
    print(f"statuses rendered under SETTLED: {sorted(settled_statuses)}")

    # --- which of those does the A4 counter treat as a blocker? --------------
    print()
    print("-" * 78)
    print("AND WHICH OF THOSE DOES THE A4 COUNTER CALL A BLOCKER? (by calling it)")
    print("-" * 78)
    contradictory = set()
    for st in sorted(FINDING_STATUS_VOCABULARY):
        reg = FindingRegistry()
        reg.entries = {
            "C0001": {"canonical_id": "C0001", "status": st, "severity": 0.45,
                      "verified": False, "verdicts": [], "description": "probe",
                      "source_model": "SIM", "proposed_fix": "",
                      "open_since_round": 0, "last_status_change_round": 0,
                      "computed_evidence": [], "routing_history": []},
        }
        try:
            n = reg.unverified_critical_count()
        except Exception as exc:  # noqa: BLE001
            print(f"  {st:<14} -> counter ERROR {type(exc).__name__}")
            continue
        flag = ""
        if n >= 1 and st in settled_statuses:
            contradictory.add(st)
            flag = "   <<< CONTRADICTION: shown as SETTLED, counted as BLOCKING"
        print(f"  {st:<14} -> A4 count {n}{flag}")

    print()
    if contradictory:
        print(f"CONTRADICTORY STATUSES: {sorted(contradictory)}")
        print("A finding in one of these is told to the panel as settled and")
        print("forbidden from challenge, while holding the convergence gate shut.")
    else:
        # THE DEFECT IS FIXED IN THIS CHECKOUT, AND THE EVIDENCE MUST STILL
        # REPRODUCE. `UNCONFIRMED` left `compact_statuses` on 2026-10-05, so the
        # live status-to-section map no longer shows the contradiction. The
        # ARCHIVE measurement is a historical fact about runs that already
        # happened and does not change; only the live premise does. Falling back
        # to the historically contradictory status keeps the headline figure
        # reproducible after its own repair, which `measured-rate-travels-with-
        # its-script` requires -- a figure whose producer stops producing it is
        # back to being a claim about evidence.
        contradictory = {"UNCONFIRMED"}
        print("No status is CURRENTLY both shown as SETTLED and counted as")
        print("blocking. THE DEFECT IS FIXED IN THIS CHECKOUT.")
        print()
        print("Continuing with the HISTORICAL status (UNCONFIRMED) so the archive")
        print("figures below remain reproducible. They describe runs that already")
        print("happened under the old labelling and are unaffected by the repair.")
        print("A run executed on THIS tree would not reproduce them, which is the")
        print("point of the repair.")

    # --- archive prevalence ---------------------------------------------------
    if args.run:
        paths = [pathlib.Path(args.run) / "runner_state.json"]
    else:
        paths = [pathlib.Path(p) for p in sorted(
            glob.glob(str(LOGS / "*" / "runner_state.json")))]
    paths = [p for p in paths if p.is_file()]

    n_resid = n_block = n_block_shown_settled = 0
    n_attrib = [0]
    probe_errors: list[str] = []
    counter_errors: list[str] = []
    runs_with = runs_total = 0
    per_run = []

    for p in paths:
        try:
            state = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        reg_d = state.get("registry") or {}
        ents = reg_d.get("entries") if isinstance(reg_d, dict) else None
        if not isinstance(ents, dict) or not ents:
            continue
        runs_total += 1
        reg = FindingRegistry()
        reg.entries = ents
        try:
            blockers = reg.unverified_critical_count()
        except Exception as exc:  # noqa: BLE001 — counted, never silent
            # THE SAME DEFECT CLASS AS THE INNER HANDLER, ONE LOOP UP, and it
            # survived the first repair. Found by the fable seat, 2026-10-05:
            # a registry the counter cannot score vanished from the attribution
            # with no trace while STAYING IN `runs_total`, and the script went on
            # printing "the attribution is complete" -- a completeness claim
            # computed from `probe_errors` alone, which never sees this path.
            # The suite's swallow-guard only flags a handler whose entire body is
            # `pass`, so `continue` escaped it.
            counter_errors.append(f"{p.parent.name}:{type(exc).__name__}")
            continue
        resid = [e for e in ents.values()
                 if str(e.get("status", "")).upper() not in TERMINAL]

        # EXACT ATTRIBUTION BY LEAVE-ONE-OUT, because a status+verified predicate
        # OVER-COUNTS what the live counter counts. First pass of this script
        # reported runs with A4 = 0 and a non-zero predicate count (for example
        # exp55_v3_control: A4 0, predicate 5), so the counter applies conditions
        # beyond status and `verified`. Rather than guess them, each residual id
        # is removed in turn and the count recomputed: an id whose removal lowers
        # the count IS a blocker, by the counter's own arithmetic.
        blocker_ids = []
        for cid in list(ents):
            if str(ents[cid].get("status", "")).upper() in TERMINAL:
                continue
            probe = FindingRegistry()
            probe.entries = {k: v for k, v in ents.items() if k != cid}
            try:
                if probe.unverified_critical_count() < blockers:
                    blocker_ids.append(cid)
            except Exception as exc:  # noqa: BLE001 — counted, never silent
                # A SWALLOWED FAILURE HERE WOULD UNDER-COUNT BLOCKERS AND THE
                # RATE WOULD LOOK BETTER THAN IT IS. The first draft wrote
                # `except Exception: pass`, which
                # `test_no_bare_or_silently_swallowed_exception_handlers` caught
                # with the right words: "the failure leaves no trace anywhere".
                # Leave-one-out is the denominator of this script's headline
                # figure, so an entry the counter cannot score must be visible
                # rather than quietly dropped.
                probe_errors.append(f"{p.parent.name}:{cid}:{type(exc).__name__}")

        # WAS A BLOCKER RENDERED UNDER THE "SETTLED" HEADER AT THE TIME?
        # Exact set membership, not a substring match on rendered text.
        shown_settled = [cid for cid in blocker_ids
                         if str(ents[cid].get("status", "")).upper()
                         in HISTORICAL_SETTLED_STATUSES]

        n_resid += len(resid)
        n_block += len(blocker_ids)
        n_block_shown_settled += len(shown_settled)
        n_attrib[0] += int(blockers)
        if shown_settled:
            runs_with += 1
            per_run.append((p.parent.name, len(ents), len(resid),
                            len(blocker_ids), len(shown_settled)))

    print()
    print("-" * 78)
    print("ARCHIVE PREVALENCE (HISTORICAL — measured on runs under the old labelling) — runs holding at least 1 contradictory finding")
    print("-" * 78)
    print(f"{'run':<44} {'all':>4} {'resid':>5} {'A4':>4} {'settled-but-blocking':>20}")
    for name, n_all, n_r, n_b, n_s in per_run:
        print(f"{name[:44]:<44} {n_all:>4} {n_r:>5} {n_b:>4} {n_s:>20}")

    print()
    print("=" * 78)
    print("POOLED")
    print("=" * 78)
    print(f"archived registries read                   : {runs_total}")
    print(_ci(runs_with, runs_total,
              "runs with >=1 settled-but-blocking finding"))
    print(_ci(n_block_shown_settled, n_block,
              "BLOCKERS (leave-one-out attributed) rendered as SETTLED"))
    print(f"blockers attributed by leave-one-out       : {n_block}")
    if counter_errors:
        print(f"  *** {len(counter_errors)} registry/-ies could not be scored at all "
              f"and were DROPPED: {counter_errors[:6]}")
    if probe_errors:
        print(f"  *** {len(probe_errors)} leave-one-out probe(s) RAISED and were "
              f"not scored, so the attribution is a LOWER BOUND: "
              f"{probe_errors[:6]}")
    # COMPLETENESS REQUIRES BOTH LISTS EMPTY, not just the inner one. The first
    # repair claimed completeness from `probe_errors` alone while the run-level
    # handler could still drop a whole registry (fable, 2026-10-05).
    if not probe_errors and not counter_errors:
        print("  probes and counters that raised            : 0 "
              "(so the attribution is complete, not a lower bound)")
    print(f"sum of the counter's own returns           : {n_attrib[0]}")
    if n_block != n_attrib[0]:
        print(f"  (the two differ by {abs(n_block - n_attrib[0])}: a counter whose")
        print("   value is not the sum of individually-removable contributions —")
        print("   interactions between entries. The leave-one-out set is the")
        print("   conservative one and is what the rate above is computed on.)")
    print(_ci(n_block_shown_settled, n_resid,
              "of ALL residual findings, blockers rendered SETTLED"))
    print()
    print("CONSEQUENCE. The panel cannot clear a blocker it is told is settled and")
    print("forbidden to challenge. The sweep is not an afterthought by oversight —")
    print("it is the only mechanism in the schema that ignores that label, which is")
    print("why it is the only one that resolves these findings.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
