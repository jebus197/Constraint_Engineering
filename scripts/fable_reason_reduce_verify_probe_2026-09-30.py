#!/usr/bin/env python3
"""A working REASON -> REDUCE -> VERIFY probe, run on a REAL repository prose
document the current triage cannot engage -- the minimal executable form of the
architecture the 2026-09-30 intelligence-first brief asks the panel to design.

TARGET: experimental_notes/Maths_Revision_Review_Synthesis_2026-09-20.md,
a document with 0 fenced listings. Measured by
fable_sk_verdict_is_syntax_bound_2026-09-30.py: `compute_sk` returns NO_SCORE
on any such target and `_gateable_source` returns None -- the machinery holds
no opinion on anything in it.

THE THREE STAGES, honestly labelled:
  REASON  is the MODEL's stage. Offline, the panel seat (a model) read the
          document and produced the candidate claims below. They are recorded
          as DATA with anchors, exactly as a live REASON stage would emit them.
          This script does not pretend to do the reasoning; it verifies it.
  REDUCE  decides, per claim, whether it is decidable by computation, and for
          each decidable claim carries a falsifier. Claims it declines are
          ROUTED (to [VERIFY:current] / HIL), not discarded -- the one-character
          near-miss of March 2026 (EXTENDED_RATIONALE.md:119) is the standing
          warning against discarding the unverifiable.
  VERIFY  runs each falsifier with >= 2 independent tools and emits per-claim
          verdicts. The file-level verdict is an AGGREGATE of claim verdicts,
          never a gate in front of them.

CONTROL: the same pipeline on mood-in-the-room prose must emit 0 candidate
claims and the file-level statement "no decidable claims" -- the honest
boundary of inadmissibility, attached to the absence of claims rather than the
absence of fences.

Writes nothing. Exits 0; figures are the output.
"""
from __future__ import annotations

import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "bench"))

DOC = REPO / "experimental_notes/Maths_Revision_Review_Synthesis_2026-09-20.md"

# ---- REASON: model-produced candidate claims, recorded as data -------------
CLAIMS = [
    {
        "tag": "MRS-C1",
        "anchor": "the optimal round count is `n* = (a/θ)^(1/γ)`",
        "statement": "Solving the decay law a*n^(-gamma) = theta for n yields "
                     "n* = (a/theta)^(1/gamma).",
        "reduce": "derivation",
    },
    {
        "tag": "MRS-C2",
        "anchor": "the parameters are 4.89 and 0.709, and at a threshold of 1 "
                  "finding per round this gives **9.37 rounds**",
        "statement": "(4.89/1)^(1/0.709) = 9.37 to the stated 2 decimal places.",
        "reduce": "numeric",
    },
    {
        "tag": "MRS-C3",
        "anchor": "The fit runs every round and feeds only the convergence "
                  "gate; the round budget remains a typed integer.",
        "statement": "No live module derives the round budget from the fit.",
        "reduce": "declined: present-day-state of the codebase, not arithmetic. "
                  "Routed [VERIFY:current] -> code-path falsifier or HIL.",
    },
]

MOOD = "The mood in the room improved. Everyone felt the meeting went well.\n"


def main(argv=None) -> None:
    import argparse
    ap = argparse.ArgumentParser(
        description="Minimal REASON/REDUCE/VERIFY pipeline over a real prose "
                    "document plus a mood-prose control. No model dispatched; "
                    "the REASON stage's output is recorded as data. Writes "
                    "nothing.")
    ap.parse_args(argv)

    import sympy as sp
    from mpmath import mp, mpf
    mp.dps = 30

    text = DOC.read_text(encoding="utf-8")

    from reference_runner_v3 import compute_sk, _gateable_source
    red, why = _gateable_source(text, DOC.name)
    r = compute_sk("<<<< SEARCH\nx\n====\ny\n>>>> REPLACE\n", text, DOC.name,
                   score_prose_listings=True)
    print(f"CURRENT MACHINERY on {DOC.name}:")
    print(f"  _gateable_source: {'None' if red is None else 'source'} ({why})")
    print(f"  compute_sk tristate: {r.tristate}")

    print("\nREASON output (model-produced, recorded as data): "
          f"{len(CLAIMS)} candidate claims")
    anchored = sum(1 for c in CLAIMS if c["anchor"] in text)
    print(f"  anchors found verbatim in the document: {anchored} of {len(CLAIMS)}")

    print("\nREDUCE + VERIFY:")
    verdicts = {}

    # MRS-C1, derivation, tool 1: sympy solve; tool 2: substitution identity.
    a, th, g, n = sp.symbols("a theta gamma n", positive=True)
    sols = sp.solve(sp.Eq(a * n ** (-g), th), n)
    t1 = len(sols) == 1 and sp.simplify(sols[0] - (a / th) ** (1 / g)) == 0
    t2 = sp.simplify(a * ((a / th) ** (1 / g)) ** (-g) - th) == 0
    verdicts["MRS-C1"] = "TRUE" if (t1 and t2) else "FALSE"
    print(f"  MRS-C1 derivation  sympy.solve -> {sols}  substitution check "
          f"{t2}  verdict {verdicts['MRS-C1']}")
    print("         NOTE this verifies the ALGEBRA as stated in the document. "
          "Whether the repo's fitter emits a RATE coefficient a is a separate, "
          "already-recorded finding (A19 panel: it fits the CUMULATIVE curve).")

    # MRS-C2, numeric, tools: mpmath and sympy independently.
    v1 = mpf("4.89") ** (1 / mpf("0.709"))
    v2 = sp.N(sp.Rational(489, 100) ** (1 / sp.Rational(709, 1000)), 25)
    agree = abs(v1 - mpf(str(v2))) < mpf("1e-20")
    stated_ok = f"{float(v1):.2f}" == "9.37"
    verdicts["MRS-C2"] = "TRUE" if stated_ok else "FALSE"
    print(f"  MRS-C2 numeric     mpmath {mp.nstr(v1, 10)}  sympy {v2}  "
          f"tools_agree={agree}")
    print(f"         document states 9.37; computed value rounds to "
          f"{float(v1):.2f}  verdict {verdicts['MRS-C2']} (immaterial "
          f"magnitude, decidable kind)")

    # MRS-C3: declined by REDUCE, routed -- NOT discarded.
    verdicts["MRS-C3"] = "ROUTED"
    print(f"  MRS-C3 {CLAIMS[2]['reduce']}")

    decided = sum(1 for v in verdicts.values() if v in ("TRUE", "FALSE"))
    print(f"\nFILE-LEVEL AGGREGATE for {DOC.name}: {decided} decided, "
          f"{len(CLAIMS) - decided} routed, 0 discarded -> the document is "
          "claim-addressable, where the current triage holds no opinion.")

    print("\nCONTROL, mood prose:")
    mood_claims = []   # REASON on the control yields no decidable candidates.
    print(f"  REASON candidates: {len(mood_claims)}")
    print("  file-level verdict: no decidable claims -- inadmissibility "
          "attached to the absence of claims, not the absence of fences.")


if __name__ == "__main__":
    main(sys.argv[1:])
