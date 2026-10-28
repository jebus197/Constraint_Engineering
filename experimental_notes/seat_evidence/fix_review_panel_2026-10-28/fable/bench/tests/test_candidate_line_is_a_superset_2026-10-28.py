# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'fix_review_panel_2026-10-28', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 6cc0de66b09c16d02a8a838515193f00ab311f002f03a0c43518580da5e01075
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""CANDIDATE_LINE must never reject a raw JSON line whose decoded text the
decision (raises_a_marker on whitespace-normalised text) accepts.

Panel falsifier, 2026-10-28. Before the fix, markers preceded by an escaped
newline/tab/\\u00a0 were invisible: the escape ends in a word character,
destroying the left word boundary the old prefilter required.
"""
import importlib.util, json
from pathlib import Path

_p = Path(__file__).resolve().parents[2] / "scripts" / "harvest_tickets_2026-10-17.py"
_spec = importlib.util.spec_from_file_location("harvest_tickets", _p)
h = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(h)

CASES = [
    "plan for tonight:\npf: raise the gamma threshold to 0.41 as ruled",
    "items follow\tqs: does the star round need a completion barrier at all",
    "list: wr: finish the adjudication of the sixty-three items",
    "pf: a marker at the very start of the message",
    "trailing bare marker case ends here pf",
]

def test_prefilter_is_a_superset_of_the_decision():
    missed = []
    for decoded in CASES:
        raw = json.dumps({"timestamp": "2026-10-28T00:00:00",
                          "message": {"role": "user", "content": decoded}})
        normalised = " ".join(decoded.split())
        if h.raises_a_marker(normalised) and not h.CANDIDATE_LINE.search(raw):
            missed.append(decoded)
    assert not missed, f"prefilter rejected decision-accepted lines: {missed!r}"

def test_prefilter_randomised_against_decision():
    # Fixed seed: every decoded text whose normalised form the decision accepts
    # must be admitted from its raw JSON encoding.
    import random
    rng = random.Random(20261028)
    seps = [" ", "\n", "\t", " ", "(", "["]
    tails = [": fix the gate now please", "] noted for the record",
             " - work remaining on the ladder", ""]
    missed = 0
    for _ in range(500):
        t = (f"{'x' * rng.randint(0, 6)}{rng.choice(seps)}"
             f"{rng.choice(['fr','pf','qs','wr'])}{rng.choice(tails)}"
             " padding so the length gate is irrelevant")
        raw = json.dumps({"message": {"content": t}})
        if h.raises_a_marker(" ".join(t.split())) and not h.CANDIDATE_LINE.search(raw):
            missed += 1
    assert missed == 0, f"{missed} of 500 randomised cases rejected"
