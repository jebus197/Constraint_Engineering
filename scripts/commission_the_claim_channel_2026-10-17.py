#!/usr/bin/env python3
"""Task C1: measure the claim channel's error, which its promotion waits on.

HIS INSTRUCTION, 2026-10-02: *"Also implement this and test it on the upcoming
simulated runs."* His reply to the position that *"the claim channel's
promotion into the scoring equations waits on a commissioning run measuring how
often it is wrong against known ground truth"*.

THE TEST HALF WAS DONE AND THE MEASURE HALF WAS NOT. `bench/claim_ledger.py`
still carries `informative_only = True` at line 184, and its header still says
the ledger is promoted "only after a commissioning run measures its error". The
channel DID run in both free runs of 2026-10-15 -- 22 claims, 19 decidable,
3 routed -- so it was exercised. No measurement of its error was ever produced.

WHAT THE CHANNEL ACTUALLY IS, which decides what "its error" can mean.
`claim_from_entry` does NOT judge whether a claim is true. It reads a registry
entry and TRANSCRIBES the falsifier path: `decidable` is whether a falsifier
exists, `verdict` is the falsifier's own verdict when that verdict is one of
the decided five, and `routed_to` records where an undecidable claim went. So
the channel's own error is TRANSCRIPTION ERROR, and the end-to-end accuracy it
inherits belongs to the falsifier path, not to it. Reporting one as the other
would credit or blame the wrong mechanism, so both are measured separately and
the boundary is stated.

  PART 1, THE FALSIFIER PATH'S DISCRIMINATION, against the 29 ground-truth
  claims in `bench/tests/fixtures/stem/`. Each of the 5 documents carries a
  runnable falsifier and a known correct fix. A template must CONFIRM on the
  pristine document, where the planted false claim is present, and REFUTE on
  the corrected one. That is bidirectional: a template that always confirms
  would pass half of it and fail the other half.

  PART 2, THE CHANNEL'S TRANSCRIPTION FIDELITY. Each verdict Part 1 produced is
  fed through `claim_from_entry` as a registry entry and the Claim's verdict is
  compared to the verdict that went in. This is the figure the promotion gate
  actually asked for.

  PART 3, THE ROUTING DECISION, which is the channel's only judgement of its
  own: an entry with no falsifier must be ROUTED and not decided, and a `state`
  claim must route to [VERIFY:current] rather than to a human.

  PART 4, NON-DISTORTION, required by this project's own shadow-promotion rule:
  a channel may be promoted only with evidence that promoting it does not
  distort what is already scored. Since the channel is not wired into sigma,
  S_k or R_k, this part reports WHAT WOULD HAVE TO BE SPECIFIED rather than
  pretending to measure a wiring that does not exist.

Costs nothing: runs local falsifiers under the project's own decider and
dispatches to no model.

Usage: python3 scripts/commission_the_claim_channel_2026-10-17.py
"""
from __future__ import annotations

import argparse
import pathlib
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "bench" / "tests" / "fixtures" / "stem"))


def _proportion(k, n):
    from statsmodels.stats.proportion import proportion_confint
    import scipy.stats as st
    if n == 0:
        return None
    w = proportion_confint(k, n, method="wilson")
    b = proportion_confint(k, n, method="beta")
    cp_hi = 1.0 if k == n else float(st.beta.ppf(0.975, k + 1, n - k))
    return {"k": k, "n": n, "pct": 100.0 * k / n,
            "wilson": (w[0] * 100, w[1] * 100),
            "cp": (b[0] * 100, b[1] * 100),
            "agrees": abs(b[1] - cp_hi) < 1e-9}


def _say(label, p):
    if p is None:
        print(f"  {label}: no denominator, so no figure")
        return
    print(f"  {label}: {p['k']} of {p['n']} = {p['pct']:.4f}%")
    print(f"      Wilson [{p['wilson'][0]:.4f}%, {p['wilson'][1]:.4f}%]  "
          f"Clopper-Pearson [{p['cp'][0]:.4f}%, {p['cp'][1]:.4f}%]  "
          f"scipy agrees {p['agrees']}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog=pathlib.Path(__file__).name,
        description=__doc__.splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__)
    parser.parse_args(argv)

    import stem_fixtures as SF
    from bench.claim_ledger import (ClaimLedger, claim_from_entry, UNVERIFIED,
                                    ROUTE_HIL, ROUTE_VERIFY_CURRENT)
    from bench.falsifier_verify import reverify_falsifier

    claims_total = sum(len(f.claims) for f in SF.FIXTURES)
    print("THE GROUND TRUTH")
    print(f"  documents          : {len(SF.FIXTURES)}")
    print(f"  tagged claims      : {claims_total}")
    for f in SF.FIXTURES:
        print(f"    {f.key:<11} {f.domain:<32} {len(f.claims)} claims")

    print("\nPART 1: THE FALSIFIER PATH'S DISCRIMINATION (bidirectional)")
    pairs, bidirectional = [], 0
    with tempfile.TemporaryDirectory() as td:
        tmp = pathlib.Path(td)
        for f in SF.FIXTURES:
            v_pristine = reverify_falsifier(f.falsifier(), repo_root=str(ROOT))
            corrected = tmp / f.doc_name
            corrected.write_text(f.apply(f.correct_fix), encoding="utf-8")
            v_fixed = reverify_falsifier(f.falsifier(corrected),
                                         repo_root=str(ROOT))
            ok = (v_pristine == "CONFIRMED" and v_fixed == "REFUTED")
            bidirectional += ok
            pairs.append((f, v_pristine, v_fixed))
            print(f"  {f.key:<11} pristine={v_pristine:<11} "
                  f"corrected={v_fixed:<10} {'OK' if ok else 'MISBEHAVED'}")
    _say("templates discriminating in BOTH directions",
         _proportion(bidirectional, len(SF.FIXTURES)))
    print("  THIS IS THE FALSIFIER PATH'S FIGURE, NOT THE CHANNEL'S. A channel")
    print("  that transcribes perfectly still inherits whatever this is.")

    print("\nPART 2: THE CHANNEL'S TRANSCRIPTION FIDELITY")
    print("  Every verdict above is fed back through `claim_from_entry` as a")
    print("  registry entry, and the Claim's verdict is compared to the one")
    print("  that went in. This is the figure the promotion gate asked for.")
    #: EVERY TAGGED CLAIM, not one per document. The first version used
    #: `claims[0]` of each of the 5 fixtures, giving n=10 and a Wilson lower
    #: bound of 72.2467% -- which bounds the transcription error only below
    #: about 28%, and that is not a figure worth gating a promotion on. All 29
    #: tagged claims against both verdicts gives n=58 and a far tighter bound,
    #: for no extra falsifier runs: the verdicts are already in hand.
    faithful, checked, wrong = 0, 0, []
    for f, v_pristine, v_fixed in pairs:
        for which, verdict in (("pristine", v_pristine),
                               ("corrected", v_fixed)):
            for claim in f.claims:
                entry = {"canonical_id": f"{f.key}-{claim.tag}-{which}",
                         "description": claim.summary,
                         "source_ref": claim.anchor,
                         "falsifier_code": f.falsifier(),
                         "falsifier_verdict": verdict,
                         "finding_category": "computation",
                         "severity": 0.5,
                         "source_model": "fixture"}
                c = claim_from_entry(entry["canonical_id"], entry)
                checked += 1
                if c.verdict == verdict:
                    faithful += 1
                else:
                    wrong.append((entry["canonical_id"], verdict, c.verdict))
    _say("verdicts transcribed exactly", _proportion(faithful, checked))
    for cid, went_in, came_out in wrong:
        print(f"      {cid}: in={went_in!r} out={came_out!r}")

    print("\nPART 3: THE ROUTING DECISION, the channel's only own judgement")
    no_falsifier = {"canonical_id": "R-1", "description": "a claim",
                    "source_ref": "x", "falsifier_code": "",
                    "falsifier_verdict": "", "finding_category": "logic"}
    c1 = claim_from_entry("R-1", no_falsifier)
    state_claim = dict(no_falsifier, canonical_id="R-2",
                       finding_category="state")
    c2 = claim_from_entry("R-2", state_claim)
    checks = {
        "a claim with no falsifier is NOT decidable": c1.decidable is False,
        "and its verdict is UNVERIFIED, not a decision": c1.verdict == UNVERIFIED,
        "and it is routed to a human": c1.routed_to == ROUTE_HIL,
        "a `state` claim routes to [VERIFY:current] instead":
            c2.routed_to == ROUTE_VERIFY_CURRENT,
    }
    for label, ok in checks.items():
        print(f"  {'PASS' if ok else 'FAIL'}  {label}")
    _say("routing properties holding",
         _proportion(sum(checks.values()), len(checks)))

    print("\nPART 4: NON-DISTORTION, AND WHAT IS STILL UNSPECIFIED")
    led = ClaimLedger(target="commissioning")
    for f, v_pristine, _ in pairs:
        led.add(claim_from_entry(f.key, {
            "canonical_id": f.key, "description": f.claims[0].summary,
            "source_ref": f.claims[0].anchor, "falsifier_code": f.falsifier(),
            "falsifier_verdict": v_pristine,
            "finding_category": "computation", "severity": 0.5,
            "source_model": "fixture"}))
    print(f"  ledger aggregate on the corpus : {led.aggregate()}")
    print(f"  decidable / routed / decided   : {len(led.decidable())} / "
          f"{len(led.routed())} / {len(led.decided())}")
    print(f"  informative_only still set     : {ClaimLedger.informative_only}")
    print("  WHAT PROMOTION WOULD REQUIRE, AND WHY THIS SCRIPT DOES NOT DO IT:")
    print("  the channel is not wired into sigma, S_k or R_k, and no document")
    print("  specifies HOW it would enter them -- as a weight, a multiplier, a")
    print("  gate, or a term. Removing `informative_only` without that form")
    print("  specified would not promote the channel; it would invent a model")
    print("  term, which belongs to the mathematical appendix and to him. The")
    print("  measurement above is what his gate asked for; the FORM is the")
    print("  decision that remains.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
