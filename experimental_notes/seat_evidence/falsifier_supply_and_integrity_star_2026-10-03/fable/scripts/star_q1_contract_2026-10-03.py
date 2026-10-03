# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'falsifier_supply_and_integrity_star_2026-10-03', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 350bb13a8daafe1acbc0e77f36bbb640887d6860ae6eb9d464385e452b9d8b89
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Q1, measured independently for the 2026-10-03 STAR round.

POPULATION: every entry in every runner-authored `runner_state.json`
registry under bench/logs and logs, severity >= 0.7, deduplicated on
(run, cid). Cuts reported separately: post-exp42 feature cut, post-
2026-06-06 date cut, and their intersection.

PREDICATE: "accepted" = status in {CONFIRMED, CLOSED, CORROBORATED}.
"tool-adjudicated" at 2 strictness levels:
  loose : ANY tool execution record -- falsifier_verdict, the unreconciled
          ladder residual, or routing_history[-1].verdict, any value
  strict: an ADJUDICATING verdict (CONFIRMED / REFUTED) in any of those
          fields. ERROR / UNTOOLABLE are equipment failures by the
          runner's own EQUIPMENT_FAILURE_VERDICTS definition ("the
          instrument produced NO reading"), so they are execution records
          but not adjudications.
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

ADJ = {"CONFIRMED", "REFUTED"}
ACCEPT = {"CONFIRMED", "CLOSED", "CORROBORATED"}


def wilson(k, n):
    if not n:
        return (float("nan"), float("nan"))
    from statsmodels.stats.proportion import proportion_confint
    lo, hi = proportion_confint(k, n, method="wilson")
    return lo, hi


def tool_verdicts(e):
    out = []
    for f in ("falsifier_verdict", "routing_verdict_unreconciled"):
        v = (e.get(f) or "").strip().upper()
        if v:
            out.append(v)
    rh = e.get("routing_history") or []
    if rh and isinstance(rh[-1], dict):
        v = (rh[-1].get("verdict") or "").strip().upper()
        if v:
            out.append(v)
    return out


def run_meta(d):
    name = d.name
    m = re.match(r"exp(\d+)", name)
    expno = int(m.group(1)) if m else None
    m2 = re.search(r"(\d{8})T\d+Z", name) or re.search(r"(\d{4}-\d{2}-\d{2})", name)
    date = None
    if m2:
        raw = m2.group(1).replace("-", "")
        date = raw
    return expno, date


rows = []
seen = set()
for base in (ROOT / "bench" / "logs", ROOT / "logs"):
    if not base.is_dir():
        continue
    for st in sorted(base.rglob("runner_state.json")):
        run = st.parent
        key = run.name
        if key in seen:
            continue
        seen.add(key)
        try:
            obj = json.loads(st.read_text(errors="replace"))
        except Exception:
            continue
        entries = obj.get("entries") or (obj.get("registry") or {}).get("entries") or {}
        if not isinstance(entries, dict):
            continue
        expno, date = run_meta(run)
        for cid, e in entries.items():
            if not isinstance(e, dict):
                continue
            if (e.get("severity") or 0.0) < 0.7:
                continue
            rows.append((key, expno, date, cid, e))

print(f"registries read: {len(seen)}, criticals (sev>=0.7, dedup run x cid): {len(rows)}")


def cut(label, pred):
    sel = [r for r in rows if pred(r)]
    acc = [(k, c, e) for k, x, d, c, e in sel if (e.get("status") or "").upper() in ACCEPT]
    verd = [(k, c, e, tool_verdicts(e)) for k, c, e in acc]
    no_tool = [(k, c, e) for k, c, e, v in verd if not v]
    no_adj = [(k, c, e, v) for k, c, e, v in verd if not (set(v) & ADJ)]
    n = len(acc)
    print(f"\n[{label}] criticals={len(sel)}  accepted={n}")
    if n:
        k1 = n - len(no_tool)
        k2 = n - len(no_adj)
        lo, hi = wilson(k1, n)
        print(f"  accepted w/ ANY tool record : {k1}/{n} = {100*k1/n:.4f}%  Wilson [{100*lo:.4f}%, {100*hi:.4f}%]")
        lo, hi = wilson(k2, n)
        print(f"  accepted w/ ADJUDICATION    : {k2}/{n} = {100*k2/n:.4f}%  Wilson [{100*lo:.4f}%, {100*hi:.4f}%]")
        for k, c, e in no_tool[:6]:
            print(f"    NO TOOL RECORD: {k}/{c} status={e.get('status')}")
        for k, c, e, v in no_adj[:8]:
            if (k, c) not in {(a, b) for a, b, _ in no_tool}:
                print(f"    NO ADJUDICATION: {k}/{c} status={e.get('status')} verdicts={sorted(set(v))}")


cut("feature cut: expno>=42 or non-exp",
    lambda r: r[1] is None or r[1] >= 42)
cut("date cut: >= 20260606",
    lambda r: r[2] is not None and r[2] >= "20260606")
cut("intersection",
    lambda r: (r[1] is None or r[1] >= 42) and (r[2] is None or r[2] >= "20260606"))
