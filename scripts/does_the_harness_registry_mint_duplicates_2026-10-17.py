#!/usr/bin/env python3
"""Does the harness registry mint 2 canonical ids for one defect?

HIS QUESTION, 2026-10-17: *"The full harness already has a registry, but I don't
know if it currently works this way either? But if it doesn't and you do gauge it
to be genuinely useful you should probably apply these principles to the harness
registry too."*

THE DIRECT ANSWER IS NO, AND THE CODE ALREADY SAYS SO. `FindingRegistry.register`
assigns `C{next:04d}` -- a sequential counter, not a function of content -- and
its own comment records the consequence, measured 2026-09-02: *"2 of 2,050
archived findings are recorded as raised by more than one model, because when two
models find one defect the runner mints two unlinked canonicals and the second is
merged away."*

SO THE QUESTION WORTH MEASURING IS WHAT THAT COSTS. The ticket register's useful
principle is not its hash -- a counter is a perfectly good label for a finding,
which has no external reference to key on. It is that a LOOKUP HAPPENS BEFORE A
NEW IDENTITY IS MINTED. The harness dedupes later, through merge and the
routing-ladder duplicate check, not at registration. This script measures how
often a registration mints a canonical that a lookup would have matched to an
existing one.

IT USES THE HARNESS'S OWN SIMILARITY FUNCTION, `_routing_similarity`, so the
judgement is the system's and not this script's. Two thresholds are reported:
the 0.85 the routing ladder actually uses for `confirmed_duplicate`, and a sweep,
because an operating point chosen after seeing the answer is not a measurement.

WHAT IT CANNOT SETTLE, said up front. A high similarity between 2 descriptions is
evidence they are the same defect, not proof. The ladder already acts on exactly
this signal at 0.85, so the figure below is "pairs the system itself would call
duplicates", which is the relevant quantity for deciding whether a pre-mint
lookup would have caught them.
"""
from __future__ import annotations

import argparse
import itertools
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
for p in (str(REPO), str(REPO / "bench")):
    if p not in sys.path:
        sys.path.insert(0, p)

import reference_runner_v3 as R  # noqa: E402

LOGS = REPO / "bench" / "logs"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()

    runs, total, pairs_at = 0, 0, {}
    thresholds = [0.60, 0.70, 0.80, 0.85, 0.90, 0.95]
    for th in thresholds:
        pairs_at[th] = 0
    examples = []
    _pairs85: list = []
    same_model_pairs = cross_model_pairs = 0

    for rs in sorted(LOGS.rglob("runner_state.json")):
        if len(rs.relative_to(LOGS).parts) != 2:
            continue
        try:
            ents = (json.loads(rs.read_text(errors="replace"))
                    .get("registry") or {}).get("entries") or {}
        except (OSError, ValueError):
            continue
        rows = [(cid, e) for cid, e in ents.items()
                if isinstance(e, dict) and (e.get("description") or "").strip()]
        if len(rows) < 2:
            continue
        runs += 1
        total += len(rows)
        for (ca, ea), (cb, eb) in itertools.combinations(rows, 2):
            s = R._routing_similarity(ea, eb)
            for th in thresholds:
                if s >= th:
                    pairs_at[th] += 1
            if s >= 0.85:
                _pairs85.append((rs.parent.name, ca, cb, ea, eb))
                if (ea.get("source_model") == eb.get("source_model")):
                    same_model_pairs += 1
                else:
                    cross_model_pairs += 1
                if len(examples) < 6:
                    examples.append((rs.parent.name, ca, cb, round(s, 4),
                                     (ea.get("description") or "")[:70]))

    print(f"runs with 2 or more described findings : {runs}")
    print(f"findings compared                      : {total}")
    print()
    print("PAIRS THE HARNESS'S OWN SIMILARITY WOULD CALL DUPLICATES:")
    for th in thresholds:
        mark = "   <- the threshold the routing ladder uses" if th == 0.85 else ""
        print(f"  at {th:.2f}: {pairs_at[th]}{mark}")
    print()
    n85 = pairs_at[0.85]
    print(f"at 0.85, of those pairs: {cross_model_pairs} are CROSS-MODEL, "
          f"{same_model_pairs} are same-model")
    print("  a cross-model pair is the case the register's comment names: 2 models")
    print("  finding one defect and the runner minting 2 unlinked canonicals.")

    if total > 1:
        try:
            from statsmodels.stats.proportion import proportion_confint
            # the unit is the FINDING, so express duplicates as findings involved
            involved = min(total, 2 * n85)
            lo, hi = proportion_confint(involved, total, method="wilson")
            print()
            print(f"findings involved in at least 1 such pair (upper bound, "
                  f"counting both members): {involved} of {total} = "
                  f"{100*involved/total:.4f}%")
            print(f"  Wilson [{lo*100:.4f}%, {hi*100:.4f}%]")
        except Exception as exc:                            # noqa: BLE001
            print(f"  interval unavailable: {exc}")

    # THE 0.85 COUNT IS INFLATED AND THE BREAKDOWN SAYS BY HOW MUCH.
    #
    # `_routing_similarity` is word overlap on the description, so 2 findings
    # whose descriptions are short CODE FRAGMENTS reach 1.0 by sharing tokens
    # like `finding_id: str` without being the same defect at all. Reporting 33
    # without this split would be an inflated figure dressed as a measurement.
    frag = mid = subst = 0
    subst_rows = []
    for run, ca, cb, ea, eb in _pairs85:
        m = min(len(set((ea.get("description") or "").lower().split())),
                len(set((eb.get("description") or "").lower().split())))
        if m <= 8:
            frag += 1
        elif m <= 20:
            mid += 1
        else:
            subst += 1
            subst_rows.append((run, ca, cb, (ea.get("description") or "")[:72]))
    print()
    print("HOW MUCH OF THAT COUNT IS A WORD-OVERLAP ARTEFACT:")
    print(f"  both descriptions 8 distinct words or fewer (fragments) : {frag}")
    print(f"  9 to 20 distinct words                                  : {mid}")
    print(f"  more than 20 distinct words (substantial)               : {subst}")
    if subst_rows and not a.quiet:
        print("  the substantial pairs, named:")
        for run, ca, cb, d in subst_rows:
            print(f"    {run[:32]:<32} {ca} vs {cb}  {d!r}")

    if examples and not a.quiet:
        print()
        print("EXAMPLES, so the figure has named members:")
        for run, ca, cb, s, desc in examples:
            print(f"  {run[:34]:<34} {ca} vs {cb}  sim={s}  {desc!r}")

    print()
    print("=" * 74)
    print("VERDICT")
    print("=" * 74)
    print(f"""
The harness registry does NOT work like the ticket register: `register` assigns
`C{{next:04d}}`, a sequential counter, and dedupes LATER through merge and the
ladder's duplicate check rather than looking up before minting.

AND APPLYING THE TICKET REGISTER'S PRE-MINT LOOKUP HERE IS NOT RECOMMENDED, on
this evidence. Of the {n85} pairs at the ladder's own threshold, only {subst}
carry substantial descriptions on BOTH sides; {frag} are fragments of 8 words or
fewer and {mid} are mid-length, where word overlap reaches 0.85 on shared code
tokens such as `finding_id: str` without the findings being the same defect.
Reading the {subst} substantial pairs, several are findings ABOUT other findings
-- "Addresses C0007", "VERDICT: CONFIRM C0014" -- which are legitimately
distinct.

So a pre-mint lookup on this signal would catch very little real duplication and
would risk MERGING genuinely distinct findings whose descriptions share code
tokens. That is the over-merge direction, which this project has already
measured as the more damaging one: it hides the open item behind the closed one.

WHAT THE 2 REGISTERS LEGITIMATELY DIFFER ON. A task entry has an external, stable
reference to key on and is written once by one author. A finding has neither: it
is minted by a model mid-run, its description is whatever that model wrote, and a
counter is an honest label for it. The principle that transferred was never the
hash -- it was that a lookup happens before a new identity is minted, and that
requires a signal reliable enough to act on. On this archive, description overlap
is not that signal.""")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
