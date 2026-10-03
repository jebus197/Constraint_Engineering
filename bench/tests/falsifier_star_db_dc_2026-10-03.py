"""STAR-round falsifier for D-B and D-C, 2026-10-03.

FALSIFIER: imports the REAL bench.reference_runner_v3 and bench.routing,
drives the REAL _apply_routing (route monkeypatched to return an unresolved
INTEGRITY_VIOLATION; dispatch stubbed so the transport-dead guard is not
tripped), then reads the REAL counters.

D-B claim: a SUB-critical UNCONFIRMED entry carrying an integrity refusal is
drained from the A4 blocker (unverified_critical_count has had no severity
gate since 2026-09-06) while integrity_refused_criticals gates severity>=0.7,
so the drain appears in NO report.

D-C claim: _apply_routing routes an integrity_unobserved entry into the
`else` branch (branch condition requires `not integrity_unobserved`),
stamping irreducible_escalation=True; unverified_critical_count skips that
flag BEFORE consulting _integrity_violation_excluded, so the carve-out never
reaches the A4 consumer, and with <= max_irreducible_queue such entries the
run CONVERGES with zero verified criticals.

Prints FALSIFIED (defect present) per claim; exits clean if the claims are
false.
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from bench import reference_runner_v3 as rv  # noqa: E402
import bench.routing as routing  # noqa: E402

defects = []

# ---------------------------------------------------------------- D-B -----
reg = rv.FindingRegistry()
reg.entries["C0001"] = {"status": "UNCONFIRMED", "severity": 0.5,
                        "description": "sub-critical, no falsifier"}
a4_before = reg.unverified_critical_count()
reg.entries["C0001"]["integrity_refused"] = True
a4_after = reg.unverified_critical_count()
reported = reg.integrity_refused_criticals()
# The defect predicate is "drained AND named in NO report". Any reader the
# runner's round loop actually logs counts as a report; absent on the
# pre-fix tree, so getattr-guarded.
reported_sub = getattr(reg, "integrity_refused_subcriticals", lambda: [])()
print(f"D-B  sub-critical (0.5) UNCONFIRMED: A4 before refusal = {a4_before}"
      f"  (severity gate absent: {'yes' if a4_before == 1 else 'NO'})")
print(f"D-B  same entry + integrity_refused : A4 after = {a4_after},"
      f" integrity_refused_criticals() = {reported!r},"
      f" integrity_refused_subcriticals() = {reported_sub!r}")
assert a4_before == 1, "A4 counter DOES gate severity -- D-B premise false"
if a4_after == 0 and reported == [] and reported_sub == []:
    defects.append("D-B")
    print("D-B  FALSIFIED: drained from the A4 blocker, named in NO report\n")
else:
    print("D-B  not demonstrated: either not drained or reported\n")

# ---------------------------------------------------------------- D-C -----
# Drive the REAL _apply_routing. route() is monkeypatched to an unresolved
# INTEGRITY_VIOLATION result; dispatch stubbed so resolve_fn records a
# reached model (otherwise the transport-dead guard continues first and the
# test would measure the wrong branch).
class _MC:
    def __init__(self, label):
        self.label = label
        self.model_id = label


class _Exp:
    models = [_MC("SIM-A"), _MC("SIM-B")]


cfg = rv.RunnerConfig(routing_enabled=True)

_real_route = routing.route
_real_dispatch = rv.dispatch_to_model


def _fake_dispatch(mc, prompt, system, enable_tools=False, **kw):
    return "no falsifier was produced", None


def _fake_route(finding, models, confirmed, resolve_fn, reverify, sim, **kw):
    # Reach one model for real so _routing_attempts grows (resolve_fn appends)
    resolve_fn("SIM-B", finding)
    return routing.RoutingResult(
        finding_id=str(finding.get("id")), verdict="INTEGRITY_VIOLATION",
        resolved=False, model_used="SIM-B", falsifier_code="", rungs_tried=1)


def _unobserved_entry():
    return {"status": "UNCONFIRMED", "severity": 0.9, "escalated": True,
            "falsifier_verdict": "INTEGRITY_VIOLATION",
            "integrity_unobserved": True, "falsifier_code": "assert True",
            "description": "critical under machine-wide observer failure"}


routing.route = _fake_route
rv.dispatch_to_model = _fake_dispatch
try:
    reg2 = rv.FindingRegistry()
    reg2.entries["C0001"] = _unobserved_entry()
    reg2.entries["C0002"] = _unobserved_entry()
    # control arm: identical refusal WITHOUT the unobserved flag
    ctl = _unobserved_entry()
    del ctl["integrity_unobserved"]
    reg2.entries["C0003"] = ctl
    rv._apply_routing(reg2, 1, _Exp(), cfg=cfg, repo_root=str(ROOT))
finally:
    routing.route = _real_route
    rv.dispatch_to_model = _real_dispatch

e1 = reg2.entries["C0001"]
e3 = reg2.entries["C0003"]
print(f"D-C  unobserved entry after REAL _apply_routing: "
      f"irreducible_escalation={e1.get('irreducible_escalation')} "
      f"integrity_refused={e1.get('integrity_refused')}")
print(f"D-C  control (refused, NOT unobserved):           "
      f"irreducible_escalation={e3.get('irreducible_escalation')} "
      f"integrity_refused={e3.get('integrity_refused')}")
print(f"D-C  carve-out predicate on the unobserved entry: "
      f"_integrity_violation_excluded = "
      f"{rv._integrity_violation_excluded(e1)}  (False = must keep blocking)")

# Remove the control so the convergence arm holds exactly 2 unobserved
# criticals (the <= bound case; the bound default is 2).
del reg2.entries["C0003"]
a4 = reg2.unverified_critical_count()
q = reg2.irreducible_queue_count()
alarm = rv.build_irreducible_queue_alarm(reg2, cfg, 5)
converged, reason = rv._check_gamma_alt_convergence(
    5, 0.0, [0, 0, 0, 0, 0], cfg,
    unresolved_critical=a4, contested=0, rho_churn=False,
    irreducible_queue=q, gamma_critical=0.0, total_findings=2)
print(f"D-C  A4 blocker over 2 unobserved criticals = {a4} "
      f"(docstring: 'integrity_unobserved entries keep blocking')")
print(f"D-C  irreducible queue = {q}, bound = {cfg.max_irreducible_queue}, "
      f"halt alarm = {alarm!r}")
print(f"D-C  _check_gamma_alt_convergence -> converged={converged}")
print(f"     reason: {reason[:180]}...")

if (e1.get("irreducible_escalation") and a4 == 0 and alarm is None
        and converged):
    defects.append("D-C")
    print("\nD-C  FALSIFIED: machine-wide observer failure, 2 criticals, "
          "ZERO verified -- and the run CONVERGED. The carve-out's False "
          "return was never consulted by the A4 consumer.")
else:
    print("\nD-C  not demonstrated")

if defects:
    print(f"\nFALSIFIED: {defects}")
    raise AssertionError(f"defects demonstrated: {defects}")
print("CLEAN EXIT: neither claim demonstrated")
