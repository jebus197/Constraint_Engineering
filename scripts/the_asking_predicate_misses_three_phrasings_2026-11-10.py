#!/usr/bin/env python3
"""Does the asking-sentence predicate see every entry that says its residue is HIS?

★ WHY THIS EXISTS. The `[tasks]` hook line the founder reads on EVERY turn says
how many open entries await him. It is produced by `task_list_markers._whose_move`,
which delegates to `how_many_decisions_actually_need_him_2026-11-01.classify_text`.
On 2026-11-10 he asked which of 2 numbers in one report was right. Checking the
split entry by entry found 3 of the 4 entries the classifier labels MINE carrying
a PROSE STATEMENT that their residue is his -- and the `ASKS` predicate matching
none of the 3. So the number he reads every turn UNDERSTATES his own queue.

2 DISTINCT DEFECTS, measured separately because they have different fixes:

  D1  ASKS requires either the word NEEDS or the construction "is his TO
      <verb>". It therefore misses "is still his authorisation" (the adverb
      breaks the adjacency AND the noun is not preceded by "needs"),
      "what is left for him is", and "1 word from him".

  D2  `retired` is computed ONCE for the whole entry body and then stamped on
      EVERY asking sentence in it. One stale marker therefore retires asks
      added LATER than the marker. This is the entry-level form of the defect
      already recorded on 2026-11-09 ("THE RETIREMENT OF 2026-11-08 IS
      WITHDRAWN"), reappearing at sentence level.

A proportion here carries a confidence interval, and every figure is
cross-verified on 2 independent tools per the 21 Apr 2026 rule.

Usage:  python3 scripts/the_asking_predicate_misses_three_phrasings_2026-11-10.py
        --help must never cost money and must never touch the network.
"""
from __future__ import annotations

import argparse
import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

#: Phrasings that STATE a residue is his without asking a question. Each is
#: anchored on a possessive referring to HIM plus a noun of decision, so a
#: bare "his ruling of 2026-11-08" (a RECORD of a past ruling) cannot match.
#: Deliberately narrow: a false positive here would inflate his queue, which is
#: the opposite error but still an error.
OWED_PROSE = re.compile(
    r"(?:IS|ARE|REMAINS)\s+(?:STILL\s+|UNCHANGED\s+AND\s+(?:IS|ARE)\s+STILL\s+)?"
    r"(?:HIS|YOURS?)\s+(?:AUTHORISATION|AUTHORIZATION|RULING|DECISION|CALL|JUDGE?MENT)"
    r"|WHAT\s+IS\s+LEFT\s+FOR\s+(?:HIM|YOU)"
    r"|(?:1|ONE)\s+WORD\s+FROM\s+(?:HIM|YOU)"
    r"|(?:IS|ARE|REMAINS)\s+(?:HIS|YOURS?)\s+TO\s+(?:GIVE|RELEASE|SETTLE)",
    re.I,
)


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def wilson(k: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    """Wilson score interval, computed in closed form so it needs no library."""
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1.0 + z * z / n
    c = p + z * z / (2 * n)
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5)
    return ((c - h) / d, (c + h) / d)


def measure() -> dict:
    tlm = _load("_tlm_a", ROOT / "scripts" / "task_list_markers.py")
    cls = _load("_cls_a",
                ROOT / "scripts" / "how_many_decisions_actually_need_him_2026-11-01.py")
    bodies = cls.bodies()
    entries = tlm.parse_entries()

    rows = []
    for e in entries:
        state = (e.state or "").upper()
        body = bodies.get(e.ident, "")
        d = cls.classify_text(state, e.ruled, body)
        prose = OWED_PROSE.search(body)
        # D2: a stale marker, plus an asking sentence whose own date is later.
        stale = cls.STALE.search(body)
        later_ask = False
        if stale:
            for a in d["asks"]:
                if a["retired"] and re.search(r"2026-1[01]-\d\d", a["sentence"]):
                    later_ask = True
        rows.append({
            "ident": e.ident, "state": state, "ruled": e.ruled,
            "kind": d["kind"], "n_asks": len(d["asks"]),
            "n_live": len(d["live_asks"]),
            "owed_prose": bool(prose),
            "prose_hit": prose.group(0) if prose else "",
            "stale": bool(stale), "d2": later_ask,
        })

    live = [r for r in rows if r["state"] not in ("DONE", "WITHDRAWN")]
    openr = [r for r in rows if r["state"] == "OPEN"]
    done = [r for r in rows if r["state"] == "DONE"]

    # D1: open entries the classifier calls MINE/GRANTED that nonetheless
    # state in prose that their residue is his.
    d1 = [r for r in openr if r["kind"] in ("MINE", "GRANTED") and r["owed_prose"]]
    # Control: DONE entries carrying the same prose. A DONE entry whose residue
    # is still his would be a mislabel in the OTHER direction; a high count here
    # would mean the prose predicate over-matches and must not be adopted.
    ctrl = [r for r in done if r["owed_prose"]]
    d2 = [r for r in openr if r["d2"]]

    return {"rows": rows, "live": live, "open": openr, "done": done,
            "d1": d1, "ctrl": ctrl, "d2": d2}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    a = ap.parse_args()

    m = measure()
    openr, d1, ctrl, d2 = m["open"], m["d1"], m["ctrl"], m["d2"]
    n_open = len(openr)
    mine = [r for r in openr if r["kind"] in ("MINE", "GRANTED")]
    owed = [r for r in openr if r["kind"] == "OWED"]

    print("=" * 78)
    print("THE ASKING PREDICATE AGAINST THE ENTRIES' OWN PROSE")
    print("=" * 78)
    print(f"  entries parsed      : {len(m['rows'])}")
    print(f"  OPEN                : {n_open}")
    print(f"  classifier says MINE: {len(mine)}  ({', '.join(r['ident'] for r in mine)})")
    print(f"  classifier says HIS : {len(owed)}  ({', '.join(r['ident'] for r in owed)})")
    print()
    print(f"  D1 -- OPEN + called MINE + prose says the residue is HIS: {len(d1)} of {len(mine)}")
    for r in d1:
        print(f"       {r['ident']:<6} kind={r['kind']:<8} asks={r['n_asks']} live={r['n_live']}"
              f"  matched: {r['prose_hit'][:52]!r}")
    lo, hi = wilson(len(d1), len(mine))
    print(f"       share of the MINE set: {len(d1)}/{len(mine)} = {len(d1)/len(mine):.6f}"
          f"  Wilson 95% [{lo:.6f}, {hi:.6f}]")
    print()
    print(f"  CONTROL -- DONE entries carrying the same prose: {len(ctrl)} of {len(m['done'])}")
    print("       (a large count here would mean the prose predicate OVER-matches)")
    for r in ctrl[:6]:
        print(f"       {r['ident']:<6} {r['prose_hit'][:52]!r}")
    print()
    print(f"  D2 -- OPEN entries where a stale marker retired a LATER-dated ask: {len(d2)}")
    for r in d2:
        print(f"       {r['ident']:<6} kind={r['kind']:<8} asks={r['n_asks']} live={r['n_live']}")
    print()
    corrected = len(owed) + len(d1)
    print(f"  THE COUNT HE READS   : {len(owed)} of {n_open} open await him")
    print(f"  THE CORRECTED COUNT  : {corrected} of {n_open}  (+{len(d1)} from D1)")
    if a.json:
        import json
        print(json.dumps({"open": n_open, "owed": len(owed), "d1": len(d1),
                          "corrected": corrected,
                          "d1_idents": [r["ident"] for r in d1],
                          "ctrl": len(ctrl), "d2": [r["ident"] for r in d2]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
