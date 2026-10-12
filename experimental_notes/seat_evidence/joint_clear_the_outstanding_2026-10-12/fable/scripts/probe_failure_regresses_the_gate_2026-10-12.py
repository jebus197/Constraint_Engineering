# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'joint_clear_the_outstanding_2026-10-12', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 719232c5534eab18864c2a3fe502fb4011353bb3aa7d454b79a65af843af1712
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Does a probe failure put the integrity gate back to refusing correct falsifiers?

JOINT ROUND J2, 2026-10-12. The 1b composition made the interpreter carve-out
probe-based: each discoverable interpreter reports its own installation roots.
The probe fails CLOSED -- a candidate that does not answer contributes nothing
-- and the result is cached per process. MEASURED HERE on the unfixed tree:

    normal probe                         22 roots
    every probe times out (loaded box)    0 roots
    after the load clears, same process   0 roots  <- POISONED FOR PROCESS LIFE
    stripped PATH                        22 roots  (static candidates cover it)

So one 10-second load spike at the first falsifier of a run disabled the
carve-out for EVERY falsifier of that run: the false-refusal class the fix
exists to remove (a spawned /usr/bin/python3's import bootstrap recorded as
denials, any denial becoming INTEGRITY_VIOLATION) RETURNED, run-wide.

THE REPAIR MEASURED BY THIS SCRIPT'S SECOND HALF: a declared fallback per
failed candidate -- roots derived from the candidate's path without executing
it (structural lib/python3.* trees; the fixed CommandLineTools and
/Library/Python locations for the /usr/bin/python3 shim), existence-filtered,
consulted ONLY on probe failure. With every probe timing out, the import-
bootstrap-class trees (stdlib, lib-dynload, site-packages, user-site) of every
candidate remain covered in at least one spelling, and the observer realpaths
both the read target and the allow set, so symlink spellings collapse. When
the probe answers, behaviour is byte-identical: the fallback is unreached.

Usage: python3 scripts/probe_failure_regresses_the_gate_2026-10-12.py
"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))

from _cli_help import answer_help  # noqa: E402

answer_help(__doc__)

import bench.falsifier_verify as fv  # noqa: E402


def roots_under(patch=None):
    fv._SECONDARY_ROOTS_CACHE = None
    if patch is None:
        return set(fv._secondary_interpreter_roots())
    real = subprocess.run
    subprocess.run = patch
    try:
        return set(fv._secondary_interpreter_roots())
    finally:
        subprocess.run = real


def main() -> int:
    def timeout(*a, **k):
        raise subprocess.TimeoutExpired(cmd=a[0], timeout=k.get("timeout", 10))

    normal = roots_under()
    loaded = roots_under(timeout)
    healed = set(fv._secondary_interpreter_roots())  # cache from the loaded pass
    print(f"normal probe: {len(normal)} roots")
    print(f"every probe times out: {len(loaded)} roots")
    print(f"same process after load clears (cached): {len(healed)} roots")
    missing = sorted(normal - loaded)
    # THE OBSERVER REALPATHS BOTH SIDES (fv._resolve on the read target,
    # fv._realpaths on the allow set), so a spelling is a gap only if its
    # REALPATH is outside the realpathed fallback set.
    loaded_real = {os.path.realpath(r) for r in loaded}
    boot_missing = [m for m in missing
                    if ("/lib/python3" in m or m.rstrip("/").endswith(
                        ("site-packages", "lib-dynload")))
                    and os.path.realpath(m) not in loaded_real]
    print(f"missing vs normal: {len(missing)} "
          f"(import-bootstrap-class among them: {len(boot_missing)})")
    for m in boot_missing:
        print("  BOOTSTRAP-CLASS GAP:", m)
    if not loaded:
        print("-> REGRESSED: a load spike returns the gate to refusing every "
              "spawned-interpreter falsifier for the life of the process.")
    elif boot_missing:
        print("-> PARTIAL: fallback present but a bootstrap-class tree is "
              "uncovered in every spelling; check whether realpath collapses it.")
    else:
        print("-> COVERED: under total probe failure every import-bootstrap-"
              "class tree stays allowed in at least one spelling; normal "
              "operation is byte-identical (fallback unreached).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
