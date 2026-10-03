# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'falsifier_supply_and_integrity_star_2026-10-03', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: fabc572f36c089a9c4f6bbcb070daeb0c36aeac7792098f4126d202cf6661c26
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""FALSIFIER (D-C): the `integrity_unobserved` carve-out does not keep A4 blocking.

`_integrity_violation_excluded` returns False for `integrity_unobserved`, and its
docstring states the safety property that depends on it:

    "a broken sitecustomize would make EVERY falsifier return INTEGRITY_VIOLATION,
     and if this predicate swallowed them all a run could CONVERGE with zero
     verified criticals ... so `integrity_unobserved` entries keep blocking."

They do not keep the A4 blocker blocking. `_apply_routing`'s branch chain is

    elif verdict == INTEGRITY_VIOLATION and not e.get("integrity_unobserved"):
        e["integrity_refused"] = True          # reporting event
    else:
        e["irreducible_escalation"] = True     # "a machine tried and failed"

INTEGRITY_VIOLATION is in neither EQUIPMENT_FAILURE_VERDICTS nor
ROUTABLE_INSTRUMENT_FAULTS, so an UNOBSERVED refusal takes the `else` and is
stamped `irreducible_escalation`.  `unverified_critical_count` skips
`irreducible_escalation` BEFORE it calls the predicate, so the carve-out never
executes for that reader.

Run:  PYTHONPATH=. python3 bench/tests/falsifier_carveout_drains_a4_2026-10-03.py
Fails (AssertionError + "FALSIFIED") iff the defect is present.
"""
from __future__ import annotations

import pathlib
import sys
from types import SimpleNamespace

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

import bench.routing as _routing                      # noqa: E402
from bench import reference_runner_v3 as rr           # noqa: E402


def _drive_routing(unobserved: bool) -> dict:
    """Run the REAL `_apply_routing` over one UNCONFIRMED critical."""
    class _Res:
        verdict = "ERROR"
        resolved = False
        model_used = "Codex"
        duplicate_of = None
        falsifier_code = ""
        rungs_tried = 1

    def fake_route(finding, models, confirmed, resolve_fn, reverify, sim, **kw):
        # Reach a model, as a live ladder does, so the transport-dead guard does
        # not short-circuit the branch chain under test.
        for m in models:
            resolve_fn(m, finding)
        return _Res()

    e = {"status": "UNCONFIRMED", "severity": 0.9, "escalated": True,
         "description": "a claim", "source_model": "CC2",
         "falsifier_code": "assert False", "falsifier_verdict": "INTEGRITY_VIOLATION"}
    if unobserved:
        e["integrity_unobserved"] = True
    reg = rr.FindingRegistry()
    reg.entries["C0001"] = e

    cfg = rr.RunnerConfig(routing_enabled=True)
    cfg.models = ["CC2", "Codex"]
    exp_config = SimpleNamespace(
        models=[SimpleNamespace(label="CC2"), SimpleNamespace(label="Codex")])

    _o_route, _o_disp = _routing.route, rr.dispatch_to_model
    _routing.route = fake_route
    rr.dispatch_to_model = lambda mc, p, s, enable_tools=False: ("", {})
    try:
        rr._apply_routing(reg, 4, exp_config, cfg=cfg, repo_root=str(rr.REPO_ROOT))
    finally:
        _routing.route, rr.dispatch_to_model = _o_route, _o_disp
    return e


def main() -> int:
    print("INTEGRITY_VIOLATION in EQUIPMENT_FAILURE_VERDICTS :",
          rr.INTEGRITY_REFUSED_VERDICT in rr.EQUIPMENT_FAILURE_VERDICTS)
    print("INTEGRITY_VIOLATION in ROUTABLE_INSTRUMENT_FAULTS :",
          rr.INTEGRITY_REFUSED_VERDICT in rr.ROUTABLE_INSTRUMENT_FAULTS)

    unobs = _drive_routing(unobserved=True)
    keyac = _drive_routing(unobserved=False)
    print("\nAFTER THE REAL _apply_routing (differential):")
    for name, e in (("observer never installed", unobs), ("key-access refusal", keyac)):
        print(f"  {name:26} irreducible_escalation={e.get('irreducible_escalation')!s:5} "
              f"integrity_refused={e.get('integrity_refused')!s:5}")

    # ANTI-VACUITY: the control arm must take the OTHER branch, or this
    # falsifier is measuring a dead routing loop rather than the branch chain.
    assert keyac.get("integrity_refused") is True and not keyac.get("irreducible_escalation"), (
        "ANTI-VACUITY FAILURE: the key-access control did not reach the reporting "
        f"branch either, so the routing loop never ran. entry={keyac}")

    bound = rr.RunnerConfig().max_irreducible_queue
    reg = rr.FindingRegistry()
    for i in range(bound):                      # a queue AT the bound, not over it
        reg.entries[f"C{i:04d}"] = dict(unobs)
    a4 = reg.unverified_critical_count()
    queue = reg.irreducible_queue_count()
    report = reg.integrity_refused_criticals()
    print(f"\nMACHINE-WIDE OBSERVER FAILURE — {bound} criticals, alarm bound {bound}")
    print(f"  unverified_critical_count (A4 blocker) : {a4}")
    print(f"  irreducible_queue_count                : {queue}  alarm fires={queue > bound}")
    print(f"  integrity_refused_criticals (report)   : {report}")
    print( "  criticals verified by a tool           : 0")
    print(f"  _integrity_violation_excluded()        : "
          f"{rr._integrity_violation_excluded(unobs)}  <- the carve-out, never consulted by A4")

    if unobs.get("irreducible_escalation") and a4 == 0 and queue <= bound:
        print("FALSIFIED")
        raise AssertionError(
            "D-C CONFIRMED. An UNOBSERVED integrity refusal is stamped "
            "`irreducible_escalation` by `_apply_routing`'s else-branch; "
            "`unverified_critical_count` skips that flag BEFORE consulting "
            "`_integrity_violation_excluded`, so the carve-out never runs for the A4 "
            f"blocker. With {bound} criticals and bound {bound} the irreducible-queue "
            "alarm does not fire either, so the run can converge with ZERO verified "
            "criticals — the exact outcome the carve-out's docstring claims to prevent.")
    print("CLEAN EXIT: the carve-out keeps A4 blocking")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
