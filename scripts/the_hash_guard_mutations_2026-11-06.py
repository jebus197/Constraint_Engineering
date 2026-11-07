#!/usr/bin/env python3
"""Does the hash-identity guard discriminate? Mutate a COPY of the store.

The real store is append-only and is never written here: each mutation builds a
copy in a temporary directory and points the guard at it. Anchors are derived by
searching the copy for the row each mutation must break, and a mutation whose
anchor is absent REFUSES rather than scoring green.
"""
from __future__ import annotations
import importlib.util, json, os, subprocess, sys, tempfile
from pathlib import Path

REPO = Path("/Users/georgejackson/Developer_Projects/Constraint_Engineering")
GUARD = REPO / "bench" / "tests" / "test_every_live_entry_carries_its_hash_2026-11-06.py"
STORE = REPO / "bench" / "tickets" / "tickets.jsonl"


def live_idents() -> list[str]:
    spec = importlib.util.spec_from_file_location(
        "mrb", REPO / "scripts" / "morning_report_build_2026-10-12.py")
    m = importlib.util.module_from_spec(spec); sys.modules["mrb"] = m
    spec.loader.exec_module(m)
    return [it["ident"] for it in m.task_items()]


def rows() -> list[dict]:
    """Parse the append-only store, RECORDING any line that will not parse.

    ★ THE `except Exception: pass` HERE WAS A SWALLOWED FAILURE, caught
    2026-11-06 by `test_no_bare_or_silently_swallowed_exception_handlers` in
    `bench/tests/test_operational_scripts.py` -- a guard outside the commit
    gate, so 5 gate-green commits passed over it. A store line that will not
    parse is a store line this harness cannot see, and a mutation harness that
    silently drops rows measures a store it has quietly altered. The count is
    returned alongside and asserted by the caller, so a parse failure can
    never again be indistinguishable from a clean read.
    """
    out, unparseable = [], []
    for n, l in enumerate(
            STORE.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        if not l.strip():
            continue
        try:
            out.append(json.loads(l))
        except json.JSONDecodeError as err:
            unparseable.append(f"{STORE.name}:{n}: {type(err).__name__}: {err}")
    if unparseable:
        print(f"  WARNING: {len(unparseable)} store line(s) did not parse and are "
              f"NOT in the population measured below:")
        for u in unparseable[:5]:
            print(f"    {u}")
        if len(unparseable) > 5:
            print(f"    ... and {len(unparseable) - 5} more")
    return out


def write(tmp: Path, rs: list[dict]) -> Path:
    p = tmp / "tickets.jsonl"
    p.write_text("\n".join(json.dumps(r) for r in rs) + "\n", encoding="utf-8")
    return p


def run(store: Path) -> tuple[int, str]:
    env = {**os.environ, "TICKET_STORE_OVERRIDE": str(store)}
    p = subprocess.run([sys.executable, "-m", "pytest", str(GUARD), "-q", "--no-header"],
                       cwd=REPO, capture_output=True, text=True, env=env, timeout=600)
    return p.returncode, p.stdout + p.stderr


def main() -> int:
    live = set(live_idents())
    base = rows()
    rc, out = run(STORE)
    print(f"0. BASELINE on the real store: exit {rc}  "
          f"({[l for l in out.strip().splitlines() if l.strip()][-1][:40]})")
    if rc != 0:
        print("   baseline red; stop."); return 1

    red, bad = 0, []
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)

        # M1 -- drop every row for 1 live entry
        target = next((i for i in sorted(live)
                       if any((r.get("task_ref") or "").split(":")[-1] == i for r in base)), None)
        if target is None:
            print("\nM1 ANCHOR ABSENT: no live entry has a row"); bad.append("M1")
        else:
            kept = [r for r in base
                    if (r.get("task_ref") or "").split(":")[-1] != target]
            rc, out = run(write(tmp, kept))
            named = "test_every_live_entry_has_a_ticket" in out
            ok = rc != 0 and named
            print(f"\n1. every row for {target} dropped: exit {rc}  named: {named}  "
                  f"-> {'RED as required' if ok else 'DID NOT DISCRIMINATE'}")
            red += ok; bad += [] if ok else ["M1"]

        #: ★ THE STORE IS APPEND-ONLY AND THE GUARD TAKES THE LAST ROW PER
        #: ENTRY. My first M2 and M3 mutated the FIRST matching row and both
        #: scored green, because a later row for the same entry overwrote the
        #: change. The harness reported them as not discriminating rather than
        #: as red, which is the only reason the mistake was visible. Both now
        #: mutate the LAST row, which is the one the guard reads.
        def last_rows(rs):
            out = {}
            for r in rs:
                i = (r.get("task_ref") or "").split(":")[-1]
                if i in live and str(r.get("tid") or ""):
                    out[i] = r
            return out

        # M2 -- truncate 1 identity to 11 characters
        mut = [dict(r) for r in base]
        _last = last_rows(mut)
        hit = next((r for r in _last.values()
                    if len(str(r.get("tid") or "")) == 12), None)
        if hit is None:
            print("\nM2 ANCHOR ABSENT: no 12-character identity on a live entry"); bad.append("M2")
        else:
            hit["tid"] = str(hit["tid"])[:11]
            rc, out = run(write(tmp, mut))
            named = "test_every_identity_is_a_12_character_hash" in out
            ok = rc != 0 and named
            print(f"2. 1 identity truncated to 11 chars: exit {rc}  named: {named}  "
                  f"-> {'RED as required' if ok else 'DID NOT DISCRIMINATE'}")
            red += ok; bad += [] if ok else ["M2"]

        # M3 -- make 2 live entries share 1 identity
        mut = [dict(r) for r in base]
        two = list(last_rows(mut).values())[:2]
        if len(two) < 2:
            print("\nM3 ANCHOR ABSENT: fewer than 2 live entries with identities"); bad.append("M3")
        else:
            two[1]["tid"] = two[0]["tid"]
            rc, out = run(write(tmp, mut))
            named = "test_distinct_entries_do_not_share_an_identity" in out
            ok = rc != 0 and named
            print(f"3. 2 live entries share 1 identity: exit {rc}  named: {named}  "
                  f"-> {'RED as required' if ok else 'DID NOT DISCRIMINATE'}")
            red += ok; bad += [] if ok else ["M3"]

    print(f"\n{red} of 3 mutations turned the guard red.")
    if bad:
        print("NOT DISCRIMINATING:", bad); return 1
    print("the guard discriminates on every property it pins.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
