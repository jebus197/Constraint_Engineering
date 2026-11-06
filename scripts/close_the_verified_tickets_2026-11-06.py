#!/usr/bin/env python3
"""Close the open tickets whose closure can be VERIFIED, not asserted.

DRY RUN BY DEFAULT. `--apply` writes; without it nothing is touched, so this can
be read and re-read while a board is running.

THE VERIFICATION, and why it is not a vote. `ticket_store.close()` demands "a
test name, a producer, or an execution result" and refuses an assertion. For each
ticket closed here the verification names: the task entry recorded DONE or
WITHDRAWN, the evidence test file that exists on disk, and THE TICKET'S OWN
SUBJECT SYMBOL found in an EXECUTABLE position in that file -- an import, a call,
an attribute, a definition or a string argument, collected by AST so a docstring
mention cannot qualify. A source-text match would have admitted 60 more tickets,
0.319149 of 188, Wilson [0.256708, 0.388833]; every one of those was a comment or
docstring. That is the difference between a test that exercises the subject and a
file that merely mentions it.

WHAT IT REFUSES TO DO. It does not close a ticket with no subjects, nor one whose
subject is absent from its entry's evidence. Those stay open and are listed, 
because the honest statement is that nothing verifies them yet.
"""
from __future__ import annotations
import argparse, ast, json, re, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1] if (Path(__file__).resolve().parents[1]/"bench").is_dir() \
       else Path("/Users/georgejackson/Developer_Projects/Constraint_Engineering")

def markers() -> dict:
    tl = (REPO/"experimental_notes"/"CDSFL_MASTER_TASK_LIST.md").read_text(encoding="utf-8")
    out = {}
    for m in re.finditer(r"<!--\s*task:\s*([A-Za-z0-9.]+)\s*\|([^>]*)-->", tl):
        f = dict(re.findall(r"(\w+):\s*([^|]+)", m.group(2)))
        out[m.group(1)] = {k: v.strip() for k, v in f.items()}
    return out

_cache: dict = {}
def exec_symbols(rel: str) -> set:
    if rel in _cache: return _cache[rel]
    out: set = set()
    try: tree = ast.parse((REPO/rel).read_text(encoding="utf-8", errors="replace"))
    except Exception: _cache[rel] = out; return out
    for n in ast.walk(tree):
        if isinstance(n, ast.Name): out.add(n.id)
        elif isinstance(n, ast.Attribute): out.add(n.attr)
        elif isinstance(n, ast.Import):
            for a in n.names: out.add((a.asname or a.name).split(".")[-1])
        elif isinstance(n, ast.ImportFrom):
            for a in n.names: out.add(a.asname or a.name)
            if n.module: out.add(n.module.split(".")[-1])
        elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            out.add(n.name)
        elif isinstance(n, ast.Call):
            for a in list(n.args) + [k.value for k in n.keywords]:
                if isinstance(a, ast.Constant) and isinstance(a.value, str): out.add(a.value)
        elif isinstance(n, ast.Subscript) and isinstance(n.slice, ast.Constant) \
                and isinstance(n.slice.value, str):
            out.add(n.slice.value)
    _cache[rel] = out
    return out

TERM = {"DONE", "WITHDRAWN"}

def plan() -> tuple[list, list]:
    mk = markers()
    rows = [json.loads(l) for l in (REPO/"bench"/"tickets"/"tickets.jsonl")
            .read_text(encoding="utf-8").splitlines() if l.strip()]
    #: ★ EFFECTIVE STATE, NOT ROW STATE. Corrected 2026-11-06 after this pass
    #: closed 97 tickets of which only 2 were genuinely open: 37 were MERGED
    #: redirects and 58 were already CLOSED. The store is APPEND-ONLY, so a
    #: ticket's state is its LAST row; filtering `status == "OPEN"` over every
    #: row matches any ticket that was EVER open, however it ended. Closing a
    #: MERGED redirect is the real harm: following a superseded identifier then
    #: reaches a dead end instead of the live ticket. All 95 were restored by
    #: replaying their prior rows, and this is the repair that stops it
    #: recurring. The same append-only trap caught 3 measurements tonight.
    effective = {}
    for r in rows:
        if r.get("tid"):
            effective[r["tid"]] = r
    go, skip = [], []
    for r in effective.values():
        if (r.get("status") or "").upper() != "OPEN": continue
        ref = (r.get("task_ref") or "").split(":")[-1].strip()
        e = mk.get(ref)
        if not e or (e.get("state") or "").upper() not in TERM:
            continue
        ev = [x.strip() for x in (e.get("evidence") or "").split(",") if x.strip()]
        ev = [x for x in ev if (REPO/x).is_file()]
        subs = [s for s in (r.get("subjects") or []) if isinstance(s, str) and s.strip()]
        if not ev or not subs:
            skip.append((r.get("tid"), ref, "no evidence file" if not ev else "no subjects"))
            continue
        proof = []
        for s in subs:
            sym = s.split(".")[-1].strip()
            if len(sym) < 4: continue
            for f in ev:
                if sym in exec_symbols(f):
                    proof.append((sym, f)); break
        if not proof:
            skip.append((r.get("tid"), ref, "subject absent from the evidence tests"))
            continue
        sym, f = proof[0]
        verification = (f"entry {ref} recorded {(e.get('state') or '').upper()}; "
                        f"its evidence {f} names `{sym}` in an executable position "
                        f"(AST, not source text); {len(proof)} of {len(subs)} subjects matched")
        go.append((r.get("tid"), ref, verification))
    return go, skip

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--apply", action="store_true", help="write the closures")
    a = ap.parse_args()
    go, skip = plan()
    print(f"VERIFIABLE CLOSURES : {len(go)}")
    print(f"LEFT OPEN, LISTED   : {len(skip)}")
    from collections import Counter
    print(f"  reasons left open : {dict(Counter(r for *_x, r in skip))}")
    bad = [t for t, _r, v in go if not str(v).strip()]
    print(f"  closures with an EMPTY verification (close() would refuse): {len(bad)}")
    assert not bad, "a closure without a verification must never be attempted"
    for tid, ref, v in go[:5]:
        print(f"\n  {tid}  {ref}\n    {v}")
    if not a.apply:
        print(f"\nDRY RUN -- nothing written. Re-run with --apply on a green board.")
        return 0
    sys.path.insert(0, str(REPO))
    from bench.ticket_store import TicketStore            # noqa: E402
    st = TicketStore()
    n = 0
    for tid, ref, v in go:
        st.close(tid, resolution=f"closed by the verified-closure pass; entry {ref} is terminal", verification=v)
        n += 1
    print(f"\nCLOSED {n} tickets, each with a verification.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
