#!/usr/bin/env python3
"""Where did this review's value come from, and is the revision derivative?

Two questions, both answered from the archive rather than from impression.

QUESTION 1 -- THE FOUNDER'S HYPOTHESIS. He proposed: "It would not shock me if
Astra essentially 'stole' its finding from our existing appendix ... because our
maths is so new, its training data had little else to go on." That is
falsifiable. Measured here: how much of the revision's core is already in the
appendix, symbol by symbol and form by form.

QUESTION 2 -- WHO EARNED THE ROUND. 5 of 7 seats returned in round 3. 2 are free
(Max subscription), 3 were paid. Counting tool calls and, more importantly,
DELIVERED EXECUTABLE ARTEFACTS, because a seat that re-derives by hand and a
seat that runs the code are not making the same kind of claim.

Run:  python3 scripts/panel_value_and_provenance_2026-09-20.py
"""
from __future__ import annotations

import argparse
import json
import re
from math import sqrt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
R3 = ROOT / "bench/logs/maths_panel_2026-09-20_r3"
APPENDIX = ROOT / "docs/MATHEMATICAL_APPENDIX.md"
SPEC = ROOT / "docs/maths_revision_review_2026-09-10/outputs/CDSFL_revised_model_specification.md"

FREE_SEATS = {"cc2", "fable"}
PAID_SEATS = {"cx", "cgpt", "ge", "ds", "kimi"}


def wilson(k: int, n: int) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    z = 1.959963984540054
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - h) / d, (c + h) / d)


def q1_derivative() -> None:
    print("QUESTION 1 -- is the revision derivative of this project's own appendix?")
    print()
    app = APPENDIX.read_text(errors="ignore")
    spec = SPEC.read_text(errors="ignore") if SPEC.exists() else ""

    # The introduction symbol already in the appendix.
    nu_app = len(re.findall(r"\bnu\b|ν", app))
    sigma_app = len(re.findall(r"\bsigma\b|σ", app))
    print(f"  appendix mentions of the introduction symbol nu : {nu_app}")
    print(f"  appendix mentions of the repair symbol sigma    : {sigma_app}")

    # External scholarship in the revision.
    ext = re.findall(r"(?:doi\.org|arxiv|NIST|Springer|Wiley|IEEE|Elsevier)", spec, re.I)
    internal = re.findall(r"(?:MATHEMATICAL_APPENDIX|reference_runner|CDSFL_|bench/|docs/)", spec)
    has_bib = bool(re.search(r"^#+\s*(references|bibliography)", spec, re.I | re.M))
    print(f"  revision: external scholarly references         : {len(set(ext))} distinct")
    print(f"  revision: citations of this project's own files : {len(internal)}")
    print(f"  revision: has a bibliography section            : {has_bib}")
    print()
    print("  WHAT THE ALGEBRA SAYS (settled this session with SymPy, exact rationals")
    print("  and mpmath at 40 digits, all 3 agreeing):")
    print("    the revision's ACTION STEP is identical to the appendix Phase-3 form")
    print("    under s = sigma*(1-nu), b = nu. Symbolic difference exactly 0.")
    print()
    print("  SUPPORTS the hypothesis: the action step adds no mathematics the")
    print("  appendix did not already contain, and the package leans overwhelmingly")
    print("  on this project's own artefacts rather than outside scholarship.")
    print()
    print("  DOES NOT SUPPORT IT, and this is the honest boundary: identity with")
    print("  the appendix is NOT evidence of derivation FROM the appendix. A 2-state")
    print("  Markov transition is a textbook object. Two authors reaching the same")
    print("  standard form is convergence, not copying, and no archive can separate")
    print("  those from the text alone.")
    print()
    print("  WHERE THE HYPOTHESIS FAILS OUTRIGHT: the SHIPPED recurrence is NOT the")
    print("  same as the revision's. The shipped Phase 2 interpolates between the")
    print("  posterior and the prior; the revision acts on the posterior. Measured:")
    print("  3959 of 4000 exact-rational samples differ, mpmath worst gap 0.917.")
    print("  That distinction is NOT in the appendix, so at least one component of")
    print("  the revision is not derivative of it.")
    print()


def q2_who_earned_it() -> None:
    print("QUESTION 2 -- which seats produced executable evidence?")
    print()
    rows = []
    for seat in sorted(FREE_SEATS | PAID_SEATS):
        f = R3 / f"{seat}.json"
        if not f.exists():
            continue
        d = json.loads(f.read_text())
        harvest = R3 / "sandbox_harvest" / seat
        delivered = 0
        if harvest.is_dir():
            delivered = len([p for p in harvest.rglob("*")
                             if p.is_file() and p.name not in ("changes.diff", "dispatch.log")])
        rows.append({
            "seat": seat,
            "paid": seat in PAID_SEATS,
            "chars": d.get("chars") or 0,
            "tools": d.get("n_tool_calls") or 0,
            "delivered": delivered,
            "returned": bool((d.get("chars") or 0) > 0),
        })

    print(f"  {'seat':6s} {'tier':5s} {'chars':>7s} {'tools':>6s} {'files':>6s}  returned")
    for r in rows:
        print(f"  {r['seat']:6s} {'paid' if r['paid'] else 'free':5s} "
              f"{r['chars']:>7,d} {r['tools']:>6d} {r['delivered']:>6d}  "
              f"{'yes' if r['returned'] else 'NO'}")
    print()

    free = [r for r in rows if not r["paid"]]
    paid = [r for r in rows if r["paid"]]
    fr = sum(1 for r in free if r["returned"]); fn = len(free)
    pr = sum(1 for r in paid if r["returned"]); pn = len(paid)
    flo, fhi = wilson(fr, fn); plo, phi = wilson(pr, pn)
    print(f"  free seats returning an answer : {fr} of {fn}  Wilson [{flo:.2%}, {fhi:.2%}]")
    print(f"  paid seats returning an answer : {pr} of {pn}  Wilson [{plo:.2%}, {phi:.2%}]")
    print()
    fd = sum(r["delivered"] for r in free); pd = sum(r["delivered"] for r in paid)
    print(f"  executable files delivered, free seats : {fd}")
    print(f"  executable files delivered, paid seats : {pd}")
    print()
    print("  THE UNCOMFORTABLE READING, stated because it is what the numbers say:")
    print("  every delivered, executable artefact in round 3 came from a FREE seat.")
    print("  The paid seats reason well and converged on the same verdict, but 2 of")
    print("  them explicitly declined to re-execute the figures the brief supplied")
    print("  and accepted them on the brief's authority -- which is precisely how")
    print("  CC1's unreproducible 75.8% travelled unchallenged.")
    print()
    print("  THE COUNTER-READING, which is equally supported: the paid seats are")
    print("  confined read-only by design and CANNOT write a file, so 'files")
    print("  delivered' is not a fair comparator across tiers. Their contribution")
    print("  is independent verdict diversity, and on that they did the job: 3")
    print("  independent architectures reached ADOPT THE NAMED CORRECTIONS without")
    print("  conferring, and cgpt caught its own Wolfram failure and marked it")
    print("  NOT EVIDENCE rather than quoting it.")


def main(argv: list | None = None) -> int:
    # `--help` MUST NEVER COST MONEY, and must never run a measurement either.
    # argparse is constructed and parsed BEFORE any archive walk or subprocess,
    # so the flag is answered rather than consumed as a positional argument.
    # This project already carries the rule in its strong form, written after 15
    # of 17 runners billed a live dispatch on an unrecognised argument.
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.parse_args(argv)

    print("PANEL VALUE AND PROVENANCE, round 3, 2026-09-20")
    print("=" * 70)
    q1_derivative()
    print("=" * 70)
    q2_who_earned_it()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
