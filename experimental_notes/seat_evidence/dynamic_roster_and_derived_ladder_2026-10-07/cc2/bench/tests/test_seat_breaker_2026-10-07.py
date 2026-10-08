# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'dynamic_roster_and_derived_ladder_2026-10-07', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 3d42c5aef8684dbb64ec0e088f3ce552d10bc51fe469267b654c5b58615d9fa9
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""FALSIFIER for bench/seat_breaker_2026-10-07.py. Imports the REAL modules."""
from __future__ import annotations

import importlib.util as iu
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))


def _load(name, filename):
    spec = iu.spec_from_file_location(name, HERE / filename)
    m = iu.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


SB = _load("cdsfl_seat_breaker", "seat_breaker_2026-10-07.py")
AL = _load("cdsfl_aliveness_f", "seat_aliveness_2026-10-06.py")
DC = _load("cdsfl_dc_f", "degraded_convergence_2026-10-07.py")
fails = []

# ── 1. THE DEFECT: the probe runs ONCE and there is no re-probe anywhere. ───
runner = (HERE / "reference_runner_v3.py").read_text()
n_calls = runner.count("_refuse_if_a_route_is_dead(")   # 1 def + 1 call
n_probe = runner.count("probe_models(") + runner.count("probe_seat(")
print(f"[1] _refuse_if_a_route_is_dead occurrences in the runner: {n_calls} "
      f"(1 definition + 1 call site)")
print(f"    probe_models/probe_seat call sites in the runner: {n_probe}")
if n_calls > 2 or n_probe > 1:
    fails.append(f"the runner DOES re-probe ({n_calls=}, {n_probe=}) -- defect absent")
# and the conflation, quoted from the source
al_src = " ".join((HERE / "seat_aliveness_2026-10-06.py").read_text().split())
if "dropping a seat is benching it" not in al_src:
    fails.append("refusal_for no longer conflates a transient fault with benching")
print("    refusal_for still says 'dropping a seat is benching it': True")

# ── 2. THE THIRD STATE EXISTS AND IS TRANSIENT BY CONSTRUCTION. ────────────
print("\n[2] three states, and no fourth")
board = SB.BreakerBoard(["CC2", "Codex", "ChatGPT", "Gemini", "DeepSeek", "Fable"])
if board.states()["Codex"] != SB.CLOSED:
    fails.append("a fresh seat did not start CLOSED")
board.breakers["Codex"].record_failure(2, "network dropped mid-round")
board.breakers["Gemini"].record_failure(2, "HTTP 402")
st = board.states()
print(f"    after round 2 failures: {st}")
if st["Codex"] != SB.OPEN or st["Gemini"] != SB.OPEN:
    fails.append("a failed seat did not enter OPEN")
# THE INVARIANT: benching is unreachable.
if not board.never_benched():
    fails.append("a seat left the declared roster -- that IS benching")
if len(board.declared) != 6:
    fails.append(f"declared roster shrank to {len(board.declared)} -- benching")
# Exact names, because `never_benched` legitimately CONTAINS "bench" -- a
# substring test here fails on the very invariant that proves the point.
_mutators = {m for m in dir(board) if not m.startswith("_")
             and callable(getattr(board, m))}
_benching = _mutators & {"bench", "remove", "remove_seat", "drop", "drop_seat",
                         "retire", "exclude", "deactivate", "disable", "pop",
                         "discard", "delete"}
if _benching:
    fails.append(f"BreakerBoard exposes {sorted(_benching)} -- benching is "
                 f"representable after all")
# And `declared` must not be mutable through any public method: run every
# 0-arg/1-arg public method and assert the roster is unchanged.
_before = list(board.declared)
for _m in sorted(_mutators):
    try:
        getattr(board, _m)(2)
    except TypeError:
        try:
            getattr(board, _m)()
        except TypeError:
            pass
    except Exception:
        pass
if list(board.declared) != _before:
    fails.append(f"a public method mutated the declared roster: {_before} -> "
                 f"{board.declared}")
print(f"    declared roster still names all 6 after 2 failures: {board.never_benched()}")
print(f"    public methods {sorted(_mutators)} contain no benching verb, and none "
      f"mutated `declared`: True")
# The run is NOT blocked (requirement 8): 4 seats still dispatch.
live = board.live(2)
print(f"    live at round 2: {live} -> the round proceeds with {len(live)} seat(s) "
      f"(requirement 8): {len(live) == 4}")
if len(live) != 4:
    fails.append(f"live roster was {live}, expected the 4 healthy seats")

# ── 3. READMISSION, and it is not benching by another name. ────────────────
print("\n[3] readmission mid-run")
# Codex's network comes back; Gemini's does not.
recovered = {"Codex"}
calls = []


def probe(seat):
    calls.append(seat)
    return seat in recovered


r = board.readmit_due(3, probe)
print(f"    round 3 probed {calls}, readmitted {r}")
if r != ["Codex"]:
    fails.append(f"readmission returned {r}, expected ['Codex']")
if board.states()["Codex"] != SB.CLOSED:
    fails.append("a recovered seat was not readmitted to CLOSED")
if board.states()["Gemini"] != SB.OPEN:
    fails.append("a still-dead seat was readmitted anyway")
print(f"    states now: {board.states()}")
# The still-OPEN seat must ALWAYS eventually be due again -- otherwise the
# backoff silently becomes a permanent exclusion, i.e. benching by arithmetic.
g = board.breakers["Gemini"]
due_rounds = [rd for rd in range(3, 60) if g.due_for_probe(rd)]
print(f"    Gemini still OPEN; next 5 rounds it is due for a probe: {due_rounds[:5]}")
if not due_rounds:
    fails.append("an OPEN seat is never due for a probe again -- benching by backoff")
if g.backoff > g.max_backoff:
    fails.append(f"backoff {g.backoff} exceeded its bound {g.max_backoff} -- the next "
                 f"probe can be pushed past the end of the run")
# Exhaust the backoff: it must stay bounded however long the outage runs.
for rd in range(4, 40):
    if g.due_for_probe(rd):
        g.record_failure(rd, "still down")
print(f"    after a 36-round outage, backoff={g.backoff} <= max={g.max_backoff}: "
      f"{g.backoff <= g.max_backoff}; consecutive_failures={g.consecutive_failures}")
if g.state != SB.OPEN:
    fails.append(f"a long outage changed the state to {g.state} -- there should be "
                 f"no terminal state")
if "Gemini" not in board.declared:
    fails.append("a long outage removed the seat from the roster -- benching")

# A raising route is a dead route, not a crash.
board.breakers["DeepSeek"].record_failure(5, "init")


def raiser(seat):
    raise RuntimeError("connection reset")


r2 = board.readmit_due(6, raiser)
if r2 != []:
    fails.append("a raising probe readmitted a seat")
if board.states()["DeepSeek"] != SB.OPEN:
    fails.append("a raising probe left the seat in a state other than OPEN")
print(f"    a probe that RAISES leaves the seat OPEN, not crashed: "
      f"{board.states()['DeepSeek'] == SB.OPEN}")

# ── 4. IT COMPOSES WITH THE CONVERGENCE RECORD -- the demonstrated advantage. ─
# Composability is only justified on a MEASURED advantage over either fix alone.
# Here it is: the breaker supplies the live roster, and WITHOUT it the gate has
# no live roster to compare against, so the degraded case is invisible. With the
# breaker alone, the run adapts but still converges on the short window.
print("\n[4] the two fixes compose, and each alone is insufficient")
hist = [2, 0, 0, 0]
full = ["CC2", "Codex", "ChatGPT", "Gemini", "DeepSeek", "Fable"]
b2 = SB.BreakerBoard(full)
b2.breakers["Gemini"].record_failure(2)
b2.breakers["DeepSeek"].record_failure(2)
live_rounds = [b2.live(rd) for rd in (2, 3, 4)]
rec = DC.assess_roster(full, live_rounds, hist, 3,
                       breaker_states=b2.states())
print(f"    breaker-supplied live roster: {[len(x) for x in live_rounds]} seats/round")
print(f"    record: integrity={rec.integrity} n_live={rec.n_live_binding} "
      f"K_req={rec.k_required} met={DC.count_side_is_met(rec)}")
print(f"    breaker states carried into the convergence record: {rec.breaker_states}")
if rec.integrity != DC.DEGRADED:
    fails.append("the composed path did not mark the run DEGRADED")
if not rec.breaker_states:
    fails.append("the convergence record carries no breaker state -- a reader cannot "
                 "tell WHY a seat was absent")
# Breaker alone: the run adapts, but a 4-seat panel converges on K=3 unchanged.
if DC.required_quiet_window(6, 4, 3) <= 3:
    fails.append("the window did not tighten for a 4-seat panel")
print(f"    breaker ALONE would converge at K=3 on 4 seats; composed requires "
      f"K={DC.required_quiet_window(6, 4, 3)}: advantage is measured, not judged")

print("\n" + "=" * 62)
if fails:
    print("FALSIFIED")
    for f in fails:
        print("  -", f)
    raise AssertionError(f"{len(fails)} claim(s) falsified")
print("NOT FALSIFIED: the third state is transient by construction and benching "
      "is unreachable.")
