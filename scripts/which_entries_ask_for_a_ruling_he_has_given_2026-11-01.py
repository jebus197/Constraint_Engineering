#!/usr/bin/env python3
"""PRODUCER: task entries that ASK for a ruling the record shows he GAVE.

THE ROOT OF HIS `pf` OF 2026-11-01. He wrote: *"The vast majority of these have
already been discussed and ruled on."* The parked file was 1 symptom and the
presentation was another, but the underlying fault is narrower and nastier: an
ENTRY can carry a sentence asking for a ruling while a LATER paragraph of the
same entry records him giving it. The stale half is the one a report reads.

3 INSTANCES WERE FOUND BY HAND ON THE NIGHT OF 2026-11-01, which is what
motivated writing this:

  * B41 says `THIS ENTRY STILL NEEDS HIS GO-AHEAD` and a LATER paragraph of the
    SAME entry quotes him: *"I accept your recommendation. But also run the
    panel briefs in sequence as suggested above. fr"*
  * B22 says `STILL NEEDS HIS GO-AHEAD` for a FREE panel dispatch, against his
    standing rule that a free panel needs no permission beyond the instruction
    to run it.
  * C1 says `STILL NEEDS HIS RULING, on 1 channel` -- and he ruled it on
    2026-10-29, annotation at line 106 of
    `Responses/Decisions_Awaiting_You_2026-10-29.txt`, accepting the
    recommendation that the channel enter as a multiplier on R_k. The code in
    `bench/claim_ledger.py` records the ruling correctly; only the task entry
    is stale. A panel brief was written for that question on 2026-10-20 and
    would have been dispatched tonight had this not been checked.

WHAT THIS SCRIPT DOES, AND WHAT IT CANNOT DO. It flags an entry that BOTH asks
for a ruling AND carries a `ruled:` marker date, which is a mechanical
contradiction worth a human's eye. It cannot decide whether the ruling it
carries ANSWERS the question it asks -- those can legitimately differ, and
B41's case proves it, since his 2026-10-30 ruling and the go-ahead request are
about the same dispatch while a different entry might ask about something new.
So the output is a QUEUE FOR READING, not a verdict, and it is deliberately
reported that way.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))

import mpmath as mp  # noqa: E402
from statsmodels.stats.proportion import proportion_confint  # noqa: E402

import task_list_markers as tlm  # noqa: E402

FAILURES: list[str] = []

#: A sentence asking him for a decision.
ASKS = re.compile(
    r"(STILL\s+NEEDS\s+(?:HIS|YOUR)|NEEDS\s+(?:HIS|YOUR)\s+"
    r"(?:RULING|GO-?AHEAD|VERDICT|AUTHORISATION|DECISION)|AWAITS?\s+"
    r"(?:HIS|YOUR)\s+(?:RULING|GO-?AHEAD|VERDICT|YES))", re.I)

#: A sentence recording that he decided.
GAVE = re.compile(
    r"(HIS\s+RULING|HE\s+RULED|YOU\s+RULED|I\s+accept\s+your\s+recommendation|"
    r"ON\s+HIS\s+(?:RULING|INSTRUCTION)|HIS\s+INSTRUCTION)", re.I)


def gave_outside_the_ask(text: str):
    """The first `GAVE` match that is NOT inside a sentence asking him to rule.

    ★ THE DETECTOR SPELLED ITS OWN PATTERN, found 2026-11-02. `ASKS` matches
    `NEEDS HIS RULING` and `GAVE` matches `HIS RULING`, which is a SUBSTRING of
    it -- so the asking phrase satisfied the giving pattern on its own and every
    entry using those 3 words was reported as ALSO recording a ruling it does
    not record.

    MEASURED BEFORE THE REPAIR: of 35 entries matching `ASKS`, 31 matched `GAVE`
    somewhere and **6 matched it ONLY inside the asking phrase -- 6 of 31,
    0.193548, Wilson 95% [0.091870, 0.362803], Clopper-Pearson [0.074520,
    0.374732]**. The 6 are B13, B17, B37, B82, B83 and B87, and 3 of them (B82,
    B83, B87) are entries genuinely awaiting his decision, which is the
    direction that misleads: a reader is told he has ruled where he has not.
    `feedback_already_ruled_and_misread_rates` records that failure reaching him
    4 times already, and
    `feedback_a_detector_must_not_spell_out_its_own_pattern_2026-11-02` records
    this exact shape twice before today.

    WHY MASKING AND NOT A NARROWER `GAVE`. Narrowing `GAVE` to exclude a
    preceding `NEEDS` would have to anticipate every phrasing; masking is stated
    over the OTHER pattern's own matches, so the 2 cannot drift apart. Only the
    matched asking phrase is masked, about 16 characters, so a genuine ruling
    recorded in the same sentence is still found.
    """
    spans = [m.span() for m in ASKS.finditer(text)]
    for g in GAVE.finditer(text):
        if not any(s <= g.start() < e for s, e in spans):
            return g
    return None


def _check(label: str, cond: bool, detail: str = "") -> None:
    if not cond:
        FAILURES.append(f"{label}: {detail}")


def wilson(k: int, n: int) -> tuple[float, float]:
    lo_sm, hi_sm = proportion_confint(k, n, alpha=0.05, method="wilson")
    z = mp.mpf("1.959963984540054")
    p = mp.mpf(k) / n
    d = 1 + z**2 / n
    c = p + z**2 / (2 * n)
    h = z * mp.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))
    _check("wilson cross-check",
           abs(float((c - h) / d) - lo_sm) < 1e-9 and abs(float((c + h) / d) - hi_sm) < 1e-9,
           "statsmodels and mpmath disagree")
    return float(lo_sm), float(hi_sm)


def main(argv=None) -> int:
    # ★ A `--help` MUST NEVER COST ANYTHING — his standing rule, and the
    # pre-commit gate enforces it. Without this, `--help` fell through to the
    # measurement and ran the whole thing: 8 producers were refused the commit
    # on exactly this. argparse answers and exits before any body runs.
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.parse_args(argv)

    entries = tlm.parse_entries()
    live = [e for e in entries if (e.state or "").upper() not in ("DONE", "WITHDRAWN")]

    print("=" * 72)
    print("M1. ENTRIES THAT ASK FOR A RULING AND ALSO RECORD ONE")
    print("=" * 72)
    asking = [e for e in live if ASKS.search(e.text)]
    both = [e for e in asking if gave_outside_the_ask(e.text)]
    print(f"live entries                         : {len(live)}")
    print(f"  asking him for a decision          : {len(asking)}")
    print(f"  ALSO recording a ruling of his     : {len(both)}")
    if asking:
        lo, hi = wilson(len(both), len(asking))
        print(f"  contradicting share Wilson 95% [{lo:.6f}, {hi:.6f}]")
    print()
    for e in both:
        ask = ASKS.search(e.text)
        print(f"  {e.ident}  state={e.state} status={e.status} "
              f"marker-ruled={getattr(e, 'ruled', None)}")
        a0 = max(0, ask.start() - 90)
        print(f"      ASKS: ...{e.text[a0:ask.end() + 110].strip()[:190]}")
        g = gave_outside_the_ask(e.text)
        if g:
            g0 = max(0, g.start() - 60)
            print(f"      GAVE: ...{e.text[g0:g.end() + 150].strip()[:190]}")
        print()
    _check("the contradiction class is non-empty", len(both) >= 1,
           "no entry both asks and records -- the finding would be withdrawn")

    print("=" * 72)
    print("M2. ENTRIES ASKING FOR A FREE-PANEL GO-AHEAD, WHICH NEEDS NONE")
    print("=" * 72)
    FREE = re.compile(r"free[- ]?(panel|seat)", re.I)
    free_ask = [e for e in asking if FREE.search(e.text)]
    print(f"entries asking a go-ahead that mention a FREE panel: {len(free_ask)}")
    for e in free_ask:
        print(f"   {e.ident}")
    print()
    print("HIS STANDING RULE MAKES THESE UNNECESSARY, and it is a rule rather")
    print("than an inference: a free panel or a simulated experiment has never")
    print("needed any permission beyond the instruction to run it. So an entry")
    print("asking for one is asking for something already granted, and the")
    print("correct action is to RUN it, not to raise it.")

    print("=" * 72)
    print("M3. THE MARKER AND THE PROSE, COMPARED")
    print("=" * 72)
    # A `ruled:` marker with an asking sentence is the sharpest form, because
    # the marker is the machine-readable half that a report trusts.
    marked_and_asking = [e for e in asking if getattr(e, "ruled", None)]
    print(f"entries carrying a `ruled:` date AND an asking sentence: "
          f"{len(marked_and_asking)}")
    for e in marked_and_asking:
        print(f"   {e.ident}: marker says ruled {e.ruled}, prose still asks")
    if live:
        lo, hi = wilson(len(marked_and_asking), len(live))
        print(f"   share of live entries Wilson 95% [{lo:.6f}, {hi:.6f}]")
    print()
    print("THIS IS A QUEUE FOR READING AND NOT A VERDICT. An entry may")
    print("legitimately carry an old ruling and a NEW question; B41 is the")
    print("case that proves the distinction matters, because there his ruling")
    print("and the request concern the same dispatch. Each row needs a human")
    print("or a reader to compare the 2 sentences, which is cheap once the")
    print("rows are named and impossible when they are not.")

    print()
    print("=" * 72)
    if FAILURES:
        print(f"CONSISTENCY CHECKS FAILED: {len(FAILURES)}")
        for f in FAILURES:
            print("   " + f)
        return 1
    print("ALL CONSISTENCY CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
