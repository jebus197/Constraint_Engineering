# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'dynamic_roster_and_derived_ladder_2026-10-07', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 575b1e249e97fa88be05060102128006d1c306ed3bbdb103992ff40c9879ff79
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""FALSIFIER for finding F1: no mid-run re-probe, so a transient fault is benching.

CLAIM: in the repository as it stands, a seat whose route fails transiently can
never rejoin a run. The aliveness probe runs once, before round 1; a single dead
seat refuses the WHOLE run; and no readmission path exists.

Prints FALSIFIED iff the defect is genuinely present. Exits cleanly if it is not.
Imports the REAL modules; defines no copy of anything under test.
"""
import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BENCH = ROOT / "bench"


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


AL = load(BENCH / "seat_aliveness_2026-10-06.py", "real_seat_aliveness")
runner_src = (BENCH / "reference_runner_v3.py").read_text()

defects = []

# (1) One transient dead seat refuses the whole run.
alive = AL.AliveResult("ok_seat", True, 1, 0.1, "answered", [])
dead = AL.AliveResult("flaky_seat", False, 3, 0.2, "no reply", [])
refusal = AL.refusal_for({"ok_seat": alive, "flaky_seat": dead})
if refusal is not None and "REFUS" in refusal.upper():
    defects.append("refusal_for refuses the run for 1 of 2 seats dead "
                   "(5 of 6 live seats cannot proceed)")

# (2) refusal_for cannot express a filtered roster at all: its only outputs are
#     None or a refusal string, so there is no third state.
outs = {type(AL.refusal_for({"s": alive})).__name__,
        type(AL.refusal_for({"s": dead})).__name__}
if outs == {"NoneType", "str"}:
    defects.append("refusal_for's codomain is {None, refusal str} -- no third "
                   "state between available and refused exists")

# (3) The probe is invoked exactly once in the runner, before round 1.
calls = len(re.findall(r"_refuse_if_a_route_is_dead\(", runner_src))
if calls <= 2:  # 1 def + 1 call site
    defects.append(f"_refuse_if_a_route_is_dead appears {calls}x "
                   f"(definition + single call site) -- probed once, never re-probed")

# (4) No SEAT readmission path in the active runner.
#     Scoped to SEAT readmission on purpose. `_reprobed` (line 18407) DOES occur,
#     but it counts fix-efficacy probes on FINDINGS in the post-sweep
#     reconciliation and has nothing to do with seat liveness. A token search that
#     accepted it would pass for the wrong reason, which is the exact failure class
#     this project audits for, so the match must mention a seat or the probe module.
seat_readmit = [m.group(0) for m in re.finditer(
    r"(?:readmit|re[_-]?admit|half[_-]?open|HALF_OPEN)[A-Za-z_]*", runner_src)]
seat_reprobe = [ln for ln in runner_src.splitlines()
                if re.search(r"re[_-]?prob", ln, re.I)
                and re.search(r"seat|alive|roster|route", ln, re.I)]
if not seat_readmit and not seat_reprobe:
    defects.append("no SEAT readmission path in reference_runner_v3.py: 0 "
                   "readmit/half-open tokens, and every re-probe mention is "
                   "about findings (fix-efficacy), not seats")

if defects:
    print("FALSIFIED -- the defect is present:")
    for d in defects:
        print("  *", d)
else:
    print("defect NOT demonstrated; claim is false")
    sys.exit(0)

# ---- the fix cures it. Raises if the fix is broken. ----
CB = load(BENCH / "seat_circuit_breaker_2026-10-07.py", "real_seat_circuit_breaker")
bs = {s: CB.SeatBreaker(s) for s in ("cx", "cgpt", "ge", "ds", "cc2", "fable")}
t = 1000.0

# a transient fault opens one breaker; the other 5 keep running
CB.open_breaker(bs["cc2"], t, "network dropped mid-round")
assert CB.live_roster(bs, t) == ["cx", "cgpt", "ge", "ds", "fable"], "roster wrong"
assert CB.should_refuse_run(bs, t, floor=2) is None, \
    "requirement 8 violated: 5 live seats must not block the run"

# it is NOT benched: a deadline exists and readmission fires without an operator
assert bs["cc2"].is_benched() is False
assert bs["cc2"].reprobe_at == t + CB.DEFAULT_BACKOFF_S, "no re-probe deadline"
assert not bs["cc2"].probe_due(t + 1), "probed before its deadline"
later = t + CB.DEFAULT_BACKOFF_S + 1
moved = CB.reprobe_and_readmit(bs, later, probe_fn=lambda s: True)
assert moved == {"cc2": CB.CLOSED}, f"readmission failed: {moved}"
assert "cc2" in CB.live_roster(bs, later), "recovered seat did not rejoin"

# a still-dead seat re-opens with a LONGER but FINITE backoff
CB.open_breaker(bs["ge"], later, "still down")
b4 = bs["ge"].backoff_s
CB.reprobe_and_readmit(bs, later + b4 + 1, probe_fn=lambda s: False)
assert bs["ge"].backoff_s == min(CB.MAX_BACKOFF_S, b4 * 2), "backoff did not grow"
for _ in range(20):
    CB.open_breaker(bs["ge"], later, "still down")
assert bs["ge"].backoff_s <= CB.MAX_BACKOFF_S, "backoff unbounded == benching"
assert bs["ge"].reprobe_at is not None, "a state with no deadline is benching"

# benching is structurally unrepresentable
try:
    CB.SeatBreaker("x", state=CB.OPEN, reprobe_at=None)
    raise SystemExit("FAIL: a deadline-free OPEN state was constructible == benching")
except ValueError:
    pass

# the floor still refuses when there is no panel left
for s in bs:
    if bs[s].state == CB.CLOSED:
        CB.open_breaker(bs[s], later, "all down")
assert CB.should_refuse_run(bs, later, floor=1) is not None, "empty roster must refuse"

print("FIX VERIFIED: transient fault keeps 5 of 6 seats running, the dead seat is "
      "re-probed and readmitted mid-run, backoff is finite, and a deadline-free "
      "non-CLOSED state cannot be constructed.")
