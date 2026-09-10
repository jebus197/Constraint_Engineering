#!/usr/bin/env python3
"""Task R5a: does the materiality population 11 / 6 / 2 reproduce from the runs?

MEASURED, and committed alongside the figures (`measured-rate-travels-with-its-script`).

THE CLAIM. `experimental_notes/DECISIONS_AWAITING_YOU_2026-09-06.md:129`, decision
32, states the population of the unstarted materiality review as
"11 Exp 49, 6 Exp 48, 2 Exp 47 HIL residuals". `CLOSING_2026-09-06.md:39` records
that this does not reproduce, that the figures appear in exactly 2 places with no
post mortem, artefact or script behind them, and that they should not be quoted
until something reproduces them. This script is that something. It either
reproduces the triple or establishes that nothing in the archives does.

WHY A SEARCH RATHER THAN A CHECK. Checking 1 definition and reporting a mismatch
would only show that the definition I happened to pick disagrees. That is the
error this project keeps making -- a universal asserted after checking 1 member.
So every field in the registry is enumerated and every value it takes is counted,
together with the round series and severity bands. A triple that no candidate in
that space reproduces is a fact about the archives; a triple that 1 reproduces
tells us what the number actually counted.

THE ARCHIVES ARE THE TRUTH SOURCE. Each run's `runner_state.json` is what the
run actually wrote. Nothing here reads a note, a tracker or a decisions file,
because those are the documents under suspicion.
"""
from __future__ import annotations

import collections
import glob
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]

#: experiment number -> the count decision 32 attributes to it.
CLAIMED = {49: 11, 48: 6, 47: 2}

#: The claim's own words, so the label being tested is never paraphrased.
CLAIM_TEXT = "11 Exp 49, 6 Exp 48, 2 Exp 47 HIL residuals"

SEVERITY_BANDS = (0.5, 0.6, 0.7, 0.8, 0.9)


def _entries(state: dict) -> list[dict]:
    reg = state["registry"]
    ent = reg.get("entries", reg) if isinstance(reg, dict) else reg
    vals = list(ent.values()) if isinstance(ent, dict) else list(ent)
    return [v for v in vals if isinstance(v, dict)]


def load(exp: int):
    """(path, state) for an experiment, or (None, None) if it has no archive."""
    hits = sorted(glob.glob(str(REPO / "bench" / "logs" / f"exp{exp}_*" / "runner_state.json")))
    if not hits:
        return None, None
    p = pathlib.Path(hits[0])
    return p, json.loads(p.read_text())


def candidates(state: dict) -> dict[str, int]:
    """Every count this archive can produce, as {definition: value}.

    Deliberately over-generated. A definition nobody would choose still costs
    nothing to count, and its presence is what makes a null result meaningful.
    """
    out: dict[str, int] = {}
    rows = _entries(state)
    out["registry entries, total"] = len(rows)

    # Every field, every value it takes. This is the part that makes the search
    # exhaustive over the archive rather than over my imagination.
    fields = sorted({k for r in rows for k in r})
    for f in fields:
        counts = collections.Counter(
            json.dumps(r.get(f), sort_keys=True, default=str) for r in rows)
        for value, n in counts.items():
            if len(value) > 60:      # sk_result and similar carry whole blobs
                continue
            out[f"{f} == {value}"] = n
        present = sum(1 for r in rows if r.get(f) is not None)
        out[f"{f} is present"] = present

    sev = [r.get("severity") for r in rows if isinstance(r.get("severity"), (int, float))]
    for band in SEVERITY_BANDS:
        out[f"severity >= {band}"] = sum(1 for s in sev if s >= band)

    for key in ("novel_critical_history", "raw_counts", "novelty_counts"):
        series = state.get(key)
        if isinstance(series, list) and series and all(
                isinstance(x, (int, float)) for x in series):
            out[f"{key}[0], the first round"] = int(series[0])
            out[f"{key}, sum over rounds"] = int(sum(series))
            out[f"{key}, number of rounds"] = len(series)

    flags = state.get("itc_hil_flags")
    if isinstance(flags, list):
        out["itc_hil_flags, entries"] = len(flags)
        out["itc_hil_flags, distinct models"] = len(
            {f.get("model") for f in flags if isinstance(f, dict)})

    # ROUND 8 EXTENSION (panel, 2026-09-10). The space above enumerates only
    # SINGLE-FIELD EQUALITY, presence, bands and series -- it cannot express
    # NEGATION ("status != CLOSED") or CONJUNCTION ("escalated AND
    # unresolved"). That gap is not academic: the claim's own label, "HIL
    # residual", most naturally denotes a conjunction -- a finding ROUTED to
    # human review AND still UNRESOLVED -- which no definition above can
    # state. A null result from a search that cannot state the claim's most
    # natural meaning is weaker than it reads. So: every negation of a
    # small-cardinality field, and every conjunction of a HIL-ish base
    # condition with a small-field condition (affirmed and negated), is
    # counted too. Bounded by construction: fields with <= 12 distinct short
    # values only, bases drawn from fields naming escalation/HIL plus the
    # UNTOOLABLE verdict.
    def _dump(r, f):
        return json.dumps(r.get(f), sort_keys=True, default=str)

    small = {}
    for f in fields:
        vals = collections.Counter(_dump(r, f) for r in rows)
        if len(vals) <= 12 and all(len(v) <= 40 for v in vals):
            small[f] = list(vals)

    for f, vals in small.items():
        for v in vals:
            out[f"{f} != {v}"] = sum(1 for r in rows if _dump(r, f) != v)

    bases = []
    for f in sorted(small):
        if "escalat" in f.lower() or "hil" in f.lower():
            for v in small[f]:
                if v == "true":
                    bases.append((f"{f} == true",
                                  lambda r, f=f: _dump(r, f) == "true"))
        if "verdict" in f.lower():
            for v in small[f]:
                if "UNTOOLABLE" in v:
                    bases.append((f"{f} == {v}",
                                  lambda r, f=f, v=v: _dump(r, f) == v))
    for blabel, bpred in bases:
        for f, vals in small.items():
            if blabel.startswith(f + " "):
                continue          # a condition conjoined with itself is noise
            for v in vals:
                hit = [r for r in rows if bpred(r)]
                out[f"{blabel} AND {f} == {v}"] = sum(
                    1 for r in hit if _dump(r, f) == v)
                out[f"{blabel} AND {f} != {v}"] = sum(
                    1 for r in hit if _dump(r, f) != v)
    return out


def main() -> int:
    print(f"THE CLAIM (decision 32): {CLAIM_TEXT}\n")

    per_exp, missing = {}, []
    for exp in sorted(CLAIMED, reverse=True):
        path, state = load(exp)
        if state is None:
            missing.append(exp)
            print(f"exp{exp}: NO ARCHIVE. The claim cannot be tested for this run.")
            continue
        per_exp[exp] = candidates(state)
        print(f"exp{exp}: {path.relative_to(REPO)}  "
              f"({len(_entries(state))} registry entries, "
              f"{len(per_exp[exp])} candidate definitions)")
    if missing:
        print(f"\n{len(missing)} of {len(CLAIMED)} runs have no archive; a null "
              f"result below is partly an absence of evidence.\n")

    # WHICH DEFINITIONS HIT THE CLAIMED VALUE, PER RUN.
    print("\n--- definitions that yield the claimed value, per run ---")
    hits_by_exp = {}
    for exp, cands in per_exp.items():
        want = CLAIMED[exp]
        hits = sorted(k for k, v in cands.items() if v == want)
        hits_by_exp[exp] = set(hits)
        print(f"\nexp{exp}, claimed {want}: {len(hits)} definition(s) yield it")
        for h in hits:
            print(f"    {h}")

    # THE DECISIVE TEST: one definition that reproduces ALL of them.
    print("\n--- definitions that reproduce the WHOLE triple ---")
    if len(hits_by_exp) < len(CLAIMED):
        print("  not testable: at least 1 run has no archive")
        return 2
    common = set.intersection(*hits_by_exp.values())
    # A definition present in 1 archive and absent from another cannot be the
    # shared meaning of the triple, so absence is treated as failure, not skipped.
    if common:
        for c in sorted(common):
            print(f"  REPRODUCES: {c}")
        print(f"\n  {len(common)} definition(s) reproduce all of "
              f"{', '.join(f'exp{e}={v}' for e, v in sorted(CLAIMED.items()))}.")
        return 0

    print("  NONE.")
    print("\n  No single definition available in the archives yields "
          + ", ".join(f"{v} for exp{e}" for e, v in sorted(CLAIMED.items(), reverse=True))
          + ".")
    print("  Each number is individually reachable or not; as a TRIPLE, which is "
          "how decision 32\n  states it, it corresponds to no measure the runs "
          "recorded.")

    # THE INNOCENT READING, TESTED RATHER THAN ACCEPTED.
    #
    # CLOSING_2026-09-06.md:39 offers one and calls it "probably the right one":
    # for an EXAM target, whether a finding accused a true claim is decided
    # against the answer key rather than against a status field, so the number
    # "may be real and simply uncheckable from what is readable today".
    #
    # That reading has a boundary, and the boundary is decisive. It can only
    # cover targets whose adjudication needs the held answer keys. Each run's own
    # report names its target, so the boundary is read from the archives, not
    # assumed.
    print("\n--- the innocent reading (answer-key adjudication), tested ---")
    code_runs = []
    for exp in sorted(per_exp, reverse=True):
        path, state = load(exp)
        rep = sorted(path.parent.glob("exp*_report.json"))
        if not rep:
            print(f"  exp{exp}: no report; target kind unknown")
            continue
        r = json.loads(rep[0].read_text())
        target = r.get("target_file", "")
        kind = "CODE" if target.endswith(".py") else "EXAM/PROSE"
        print(f"  exp{exp}: {kind:10s} target={target}  domain={r.get('domain')}")
        if kind == "CODE":
            code_runs.append(exp)
    if code_runs:
        print(f"\n  {len(code_runs)} of {len(per_exp)} runs take a CODE target, whose "
              f"adjudication needs no answer key\n  and is fully readable today: "
              + ", ".join(f"exp{e}" for e in code_runs) + ".")
        print("  For those runs the innocent reading does not apply, so the "
              "claimed value must be\n  reproducible from the archive alone. "
              "Below it is not.")
        print("\n  THE INNOCENT READING THEREFORE CANNOT RESCUE THE TRIPLE. It can "
              "at most excuse the\n  exam runs; it cannot excuse a code run whose "
              "numbers are readable and disagree.")
    else:
        print("\n  every run takes an exam target, so the innocent reading is "
              "not excluded here")

    # WHAT THE ARCHIVES DO SAY ABOUT HIL, since that is the claim's own label.
    print("\n--- what 'HIL residual' actually measures in these archives ---")
    for exp in sorted(per_exp, reverse=True):
        c = per_exp[exp]
        parts = []
        for label, key in (("escalated", "escalated == true"),
                           ("hil_escalated", "hil_escalated == true"),
                           ("irreducible", "irreducible_escalation == true"),
                           ("itc HIL flags", "itc_hil_flags, entries")):
            parts.append(f"{label}={c.get(key, 0)}")
        print(f"  exp{exp}: " + ", ".join(parts)
              + f"   (claimed {CLAIMED[exp]})")

    # THE SHARPEST FORM OF THE RESULT, computed rather than read off by eye.
    # The claim is not merely "a triple no single measure produces" -- it is a
    # triple in which NO HIL-labelled measure produces even the value for its own
    # run. That is a stronger statement than a mismatched total and it is the one
    # that decides whether the label can stand.
    HIL_KEYS = ("escalated == true", "hil_escalated == true",
                "irreducible_escalation == true", "itc_hil_flags, entries",
                "itc_hil_flags, distinct models")
    any_hil_match = []
    for exp, c in per_exp.items():
        for k in HIL_KEYS:
            if c.get(k, 0) == CLAIMED[exp]:
                any_hil_match.append((exp, k))
    print("\n--- can ANY HIL-labelled measure produce its own run's claimed value? ---")
    if any_hil_match:
        # WRITTEN AFTER THIS BRANCH FIRED AND REFUTED THE SHARPER CLAIM.
        # The draft conclusion was "no HIL-labelled measure yields ANY of the 3",
        # which is false: exp47's 2 is the number of DISTINCT MODELS flagged for
        # HIL review. It is reported as a match because it is one, and then
        # qualified, because a count of models is not a population of findings
        # and a materiality review reviews findings.
        for exp, k in any_hil_match:
            print(f"  exp{exp}: yes, via {k}")
        unmatched = [e for e in sorted(per_exp, reverse=True)
                     if e not in {x for x, _ in any_hil_match}]
        print(f"  and NO for exp" + ", exp".join(str(e) for e in unmatched)
              + f" -- {len(unmatched)} of {len(per_exp)}.")
        if any(k.startswith("itc_hil_flags") for _, k in any_hil_match):
            print("  NOTE: itc_hil_flags counts MODELS flagged for review, not "
                  "findings. Decision 32\n  states its 3 numbers as a population "
                  "of findings to adjudicate, so a model count\n  cannot be the "
                  "shared meaning even where the arithmetic coincides.")
    else:
        print(f"  NO. Across {len(per_exp)} runs and {len(HIL_KEYS)} HIL-labelled "
              f"measures, {len(per_exp) * len(HIL_KEYS)} combinations,\n  not one "
              f"yields the value decision 32 attributes to its run.")
        print("  The label 'HIL residuals' is not supported for ANY of the 3 "
              "figures, independently\n  of whether they agree with each other.")

    # WHERE THE VALUES ARE REACHABLE AT ALL, they are reachable only by
    # definitions that have nothing to do with HIL -- which is what makes the
    # triple 3 unrelated measurements rather than 1 measurement of 3 runs.
    print("\n--- if not HIL, then what? the reachable definitions, per run ---")
    for exp in sorted(hits_by_exp, reverse=True):
        hits = sorted(hits_by_exp[exp])
        hil_hits = [h for h in hits if h in HIL_KEYS]
        print(f"  exp{exp} (claimed {CLAIMED[exp]}): {len(hits)} reachable, "
              f"{len(hil_hits)} of them HIL-labelled")
    return 1


if __name__ == "__main__":
    sys.exit(main())
