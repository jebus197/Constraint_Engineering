#!/usr/bin/env python3
# PROVENANCE: written by panel seat cc2 inside its own sandbox during the
# falsifier-root-cause design review of 2026-09-30, NOT by the orchestrating
# session. Rescued verbatim to scripts/ on 2026-09-30T10:47:16+01:00 because
# .gitignore:48 `bench/logs/**` excluded the harvest that held it, leaving the
# evidence behind this review's published figures unversioned and one reboot
# from unrecoverable. Body is byte-identical to the seat's output below this
# header; the seat's original sha256 is 154507f878ea4f535b43b27bfa4568fb616635f19984f386006f98c14658d4c4
# (recorded in scripts/seat_evidence_manifest_2026-09-30.json). It is EVIDENCE,
# not an applied fix: no seat proposal is adopted by this rescue.
"""FALSIFIER: arm4's `test_cmd=None` does NOT exclude e2_regression -- it
inherits an unrelated default suite, so the gate is FAKED, not excluded.

THE CLAIM UNDER TEST. `bench/tools/commissioning_arms_2026-09-21.py` builds arm4
(the prose arm) with `test_cmd=None`, and its own comment states

    "e2_regression is UNAVAILABLE on prose by construction, so no test command
     is passed and the gate is excluded rather than faked"

with the dataclass field documented
    #: None where the gate is unavailable by construction rather than by choice.

BOTH ARE FALSE. `Arm.argv()` guards the flag with a TRUTHINESS test
(`if self.test_cmd:`), so `None` emits no `--test-cmd`. Control falls to the
argparse DEFAULT in `bench/tools/run_simulated_experiment.py`: the immune-memory
suite tied to `bench/dm/_memory.py`, unrelated to any prose target. The gate
RUNS, against the wrong artefact, and returns a CONSTANT 52/55 =
0.9454545454545454 on every scored fix. A gate whose output does not vary with
its input decides nothing.

Imports the REAL modules; retypes neither. Raises AssertionError iff the defect
stands. Prints NOT FALSIFIED and exits 0 once `None` means "explicitly disabled"
end to end.

Run:  python3 scripts/falsify_e2_inherits_default_2026-09-30.py
"""
import argparse
import importlib.util
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


def _load(rel, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


arms = _load("bench/tools/commissioning_arms_2026-09-21.py", "_arms_2026_09_30")
arm4 = next(a for a in arms.ARMS if a.key == "arm4")
argv = arm4.argv()
print("arm4.test_cmd      = %r" % (arm4.test_cmd,))
print("arm4.argv()        = %s" % (argv,))
flag_emitted = "--test-cmd" in argv
print("--test-cmd emitted = %s" % flag_emitted)

runner_src = (ROOT / "bench/tools/run_simulated_experiment.py").read_text(encoding="utf-8")
start = runner_src.index('ap.add_argument("--test-cmd"')
end = runner_src.index("help=", start)
end = runner_src.index(")", runner_src.index('"', end + 6) + 1) + 1
snippet = runner_src[start:end]
ap = argparse.ArgumentParser()
exec(snippet, {"ap": ap})  # executing the project's OWN declaration, not a copy
inherited = ap.parse_args([]).test_cmd
print("inherited default  = %r" % (inherited,))

names_memory_suite = ("_memory" in (inherited or "")) or ("immune_memory" in (inherited or ""))
print("names immune-memory suite = %s" % names_memory_suite)

CONSTANT = 52 / 55
print("\nthe constant e2 reported across all 4 scored fixes = %r" % CONSTANT)

if not flag_emitted and names_memory_suite:
    raise AssertionError(
        "e2_regression is FAKED on the prose arm, not excluded. arm4 sets "
        "test_cmd=%r and Arm.argv() drops it via a truthiness guard "
        "(`if self.test_cmd:`), so no --test-cmd reaches the runner and argparse "
        "substitutes its own default:\n    %s\n"
        "That is the immune-memory suite tied to bench/dm/_memory.py, unrelated "
        "to a prose target. The gate runs against the wrong artefact and returns "
        "the constant %r (52/55) for every fix, so its output does not vary with "
        "its input and it decides nothing. `None` cannot express 'explicitly "
        "disabled' through a falsy guard: None and '' are indistinguishable from "
        "'unset'." % (arm4.test_cmd, inherited, CONSTANT)
    )

print("\nNOT FALSIFIED: `None` now propagates as an explicit disable.")
raise SystemExit(0)
