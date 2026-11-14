# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'asking_predicate_and_fourth_standard_2026-11-14', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 67e4102f9fd7b9760cbef39861f8a9bd0088768fef7f667c161d6ba806af9092
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Whether an ask outlives a ruling, decided by a RECORDED fact, never by a date proxy.

* PROPOSED, NOT INSTALLED -- AWAITS THE FOUNDER'S RULING. Nothing imports this
file; the live banner still routes through `classify_text` unchanged. Panel
deliverable of 2026-11-14 for the brief "the predicate that decides what the
founder is told he owes".

THE DEFECT THIS REPLACES, DEMONSTRATED NOT ASSERTED. `classify_text`'s `_later`
test -- any date in the body later than the `ruled:` date -- is a proxy for "a
question was raised after the ruling". A falsifier executed 2026-11-14 against
the real module showed it fires on a dated progress note that asks nothing
(AssertionError raised; controls GRANTED/OWED both correct). On live data it
holds B94 at OWED although every post-ruling date there is a progress note
("HIS QUESTION ANSWERED 2026-11-09", "SETTLED BY MEASUREMENT", "NOT BUILT")
and the only live ask was added 2026-11-03, five days BEFORE the ruling.

WHY NO 4TH TEXT PREDICATE IS WRITTEN. The 3 siblings (A: any later date;
B: later date inside the ask; C: ask positioned after the first later date)
form a provable implication lattice -- B implies A and C implies A, machine-
checked over all 10 ruled OPEN entries on 2026-11-14 with 0 violations -- so
B and C can only SHRINK the owed set relative to A, which is the suppression
direction withdrawn on 2026-11-09. The fact "when was this question raised"
is a POINT EVENT the body text does not carry; no text predicate recovers it.

THE RECORDED FORM. An asking sentence may carry an inline stamp
`raised:YYYY-MM-DD`, written at the moment the question is raised. Then:

  - any live ask stamped LATER than the ruling      -> OWED,    basis RECORDED
  - every live ask stamped, none later              -> GRANTED, basis RECORDED
  - any live ask UNSTAMPED                          -> the classifier's own
    verdict stands (the A proxy), basis PROXY -- and the caller is told the
    entry is UNDECIDED BY RECORD rather than handed a silent verdict.

MONOTONE-SAFE BY CONSTRUCTION: this never removes an entry from OWED relative
to `classify_text` except on a recorded stamp -- the direction the founder's
precedent requires. `bench/tests/
test_the_later_proxy_only_overreports_2026-11-14.py` asserts it.

WHAT IT COSTS AT THE RAISE SURFACES. One 17-character token per new ask,
written where the ask is written. A lint in `task_list_markers.check()` COULD
warn on a new unstamped ask -- proposed only, not installed, because `check()`
gates his file and widening a gate is his to rule. Legacy asks need no
backfill: they fall through to today's behaviour, and the undecided residue
(5 entries on 2026-11-14) SHRINKS as he rules on them, instead of growing by
1 each time a ruling is recorded on an asking entry -- which is how B142
joined the set on 2026-11-14.
"""
from __future__ import annotations

import importlib.util
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
LIST = REPO / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md"

#: The recorded fact: `raised:` plus the date, inside the asking sentence.
RAISED = re.compile(r"\braised:(\d{4}-\d{2}-\d{2})")


def _clf():
    spec = importlib.util.spec_from_file_location(
        "_aor_clf",
        REPO / "scripts" / "how_many_decisions_actually_need_him_2026-11-01.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules.setdefault("_aor_clf", m)
    spec.loader.exec_module(m)
    return m


def entry_verdict(state: str, ruled: str | None, body: str, clf=None) -> dict:
    """classify_text's verdict, upgraded to RECORDED where a stamp decides it.

    Returns {kind, basis, stamps} where basis is one of:
      "recorded"  -- every live ask's raise date is on record and decided it
      "proxy"     -- at least one live ask is unstamped; the classifier's own
                     verdict stands and the entry is UNDECIDED BY RECORD
      "no-ruling" -- no ruling to outlive; the stamp question does not arise
    """
    clf = clf or _clf()
    d = clf.classify_text(state, ruled, body)
    if not ruled or d["kind"] != "OWED" or not d["live_asks"]:
        return {**d, "basis": "no-ruling" if not ruled else "recorded",
                "stamps": []}
    stamps = [(s, RAISED.search(s)) for s in d["live_asks"]]
    dated = [(s, m.group(1)) for s, m in stamps if m]
    if any(dt > ruled for _, dt in dated):
        return {**d, "kind": "OWED", "basis": "recorded", "stamps": dated}
    if len(dated) == len(d["live_asks"]):
        # every live ask on record, none later than the ruling: it answered them
        return {**d, "kind": "GRANTED", "basis": "recorded", "stamps": dated}
    # an unstamped ask: NEVER silently dropped -- the proxy verdict stands, named
    return {**d, "kind": d["kind"], "basis": "proxy", "stamps": dated}


def main() -> int:
    sys.path.insert(0, str(REPO / "scripts"))
    import task_list_markers as tlm                          # type: ignore
    clf = _clf()
    bodies = clf.bodies()
    opens = [e for e in tlm.parse_entries(LIST)
             if (e.state or "").upper() == "OPEN"]
    recorded, proxy, unruled_owed = [], [], []
    for e in opens:
        v = entry_verdict(e.state, e.ruled, bodies.get(e.ident, ""), clf)
        if v["kind"] != "OWED":
            continue
        if v["basis"] == "no-ruling":
            unruled_owed.append(e.ident)
        elif v["basis"] == "recorded":
            recorded.append(e.ident)
        else:
            proxy.append(e.ident)
    owed = len(recorded) + len(proxy) + len(unruled_owed)
    print(f"OPEN {len(opens)}: {owed} await him -- "
          f"{len(unruled_owed)} never ruled, {len(recorded)} by RECORD, "
          f"{len(proxy)} by the date PROXY ONLY (undecided by record)")
    if proxy:
        print(f"  undecided by record: {', '.join(proxy)}")
    # the composed half of the fix: the residue is SHOWN, never silently resolved
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
