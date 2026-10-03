# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'falsifier_supply_and_integrity_2026-10-02', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 753a2e37be5a07c198fae73d399292a820317ace2181d59ed6c4088f49d598b0
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""FALSIFIER. 'Run 1b halted with BOTH halves of the two-sided gate satisfied'
is contradicted by run 1b's own archived state.

Imports the REAL producer and the REAL runner module; retypes nothing.
Raises AssertionError when the defect is present, exits clean otherwise.
"""
import importlib.util, json, pathlib, sys
ROOT = pathlib.Path('.').resolve(); sys.path.insert(0, str(ROOT))

spec = importlib.util.spec_from_file_location(
    "_iefig", ROOT / "scripts" / "integrity_exclusion_figures_2026-10-02.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
import bench.reference_runner_v3 as rr          # the real gate's own module

d = ROOT / "bench" / "logs" / m.RUN_1B
st = json.loads((d / "runner_state.json").read_text())

claimed = m.run_1b_halt()
print("the producer's own record of run 1b:", claimed)

# THE TWO HALVES, from the gate's own docstring and body:
#   (a) gamma_critical >= gamma_alt_threshold         -- the GAMMA side
#   (b) K consecutive rounds with ZERO new genuine criticals -- the COUNT side
# `gamma_all` is a THIRD number and is not a half of this gate.
src = (ROOT / "bench" / "reference_runner_v3.py").read_text()
i = src.index("def _check_gamma_alt_convergence")
body = src[i:i + 30000]
assert ("zero-new-critical rounds" in body or "zero\n          NEW genuine critical findings" in body), \
    "the gate's COUNT side is not described as I claim; re-read before trusting this"

novel = st.get("novel_critical_history") or []
gates = st.get("gate_history") or []
print("novel_critical_history (new genuine criticals per round):", novel)
print("gate_history (the runner's own record of the gate):      ", gates)

count_side_met = any(n == 0 for n in novel)
gate_ever_true = any(bool(g) for g in gates)

if not count_side_met and not gate_ever_true:
    print("\nFALSIFIED")
    raise AssertionError(
        "BOTH HALVES SATISFIED is false. The COUNT side needs consecutive "
        f"rounds with ZERO new criticals; run 1b recorded {novel} -- never "
        f"zero in any round -- and the runner's own gate_history is {gates}, "
        "False at every round. `gamma_all`=0.432 is not the second half of "
        "the two-sided gate. So run 1b would not have converged at round 2 "
        "whatever the irreducible queue contained, and the halt-bound change "
        "is not demonstrated by this run.")
print("\nclean exit: the gate really was satisfied; the claim stands")
