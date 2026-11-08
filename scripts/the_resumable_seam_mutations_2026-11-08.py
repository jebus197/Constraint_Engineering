#!/usr/bin/env python3
"""Reverse each part of B20's resumable seam and prove the guard reds.

The seam spans 2 files -- the lifted installer and the wrapper that drives the
runner -- so the mutations cross both. Each subject is restored from bytes held
here and verified by sha256
(`feedback_a_harness_must_restore_what_it_found_2026-11-01`), and every anchor is
asserted present before any edit
(`feedback_a_mutation_harness_must_derive_its_anchors_2026-11-04`).

WHY EACH REVERSION IS THE RIGHT ONE TO TRY. The 2 properties B20's entry names
are that the wrapper REFUSES a paid host and PROPAGATES exit 42. The 6 below
attack those 2 from the directions that would actually occur: swallowing the
pause, over-mapping every failure TO the pause, dropping the flag that creates
the pause, leaving the patched resolver installed, chaining 2 patches, and
removing the call that installs it at all.
"""
from __future__ import annotations

import argparse
import hashlib
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
WRAPPER = REPO / "bench/tools/run_simulated_resumable_2026-11-08.py"
RSE = REPO / "bench/tools/run_simulated_experiment.py"
GUARD = REPO / "bench/tests/test_a_simulated_run_can_be_resumed_2026-11-08.py"

MUTATIONS = [
    (WRAPPER, "the pause is swallowed (42 reported as success)",
     "        rc = 0 if rc is None else int(rc)",
     "        rc = 0",
     "a_returned_42_is_propagated"),
    (WRAPPER, "every failure is mapped TO the pause",
     "        rc = 0 if rc is None else int(rc)",
     "        rc = 42 if rc else 0",
     "a_failure_is_not_turned_into_a_pause"),
    (WRAPPER, "the flag that CREATES the pause is dropped",
     "    if hil_review:\n        argv.append(\"--hil-review\")",
     "    if False:\n        argv.append(\"--hil-review\")",
     "the_pause_flag_is_on_by_default"),
    (WRAPPER, "resume is appended unconditionally",
     "    if resume:\n        argv.append(\"--resume\")",
     "    argv.append(\"--resume\")",
     "resume_is_appended_only_when_asked"),
    (WRAPPER, "the patched resolver is left installed",
     "        import socket as _sock                                 # noqa: PLC0415\n"
     "        _sock.getaddrinfo = original",
     "        pass",
     "the_resolver_is_restored_afterwards"),
    (RSE, "the installer chains instead of being idempotent",
     "    if getattr(_sock.getaddrinfo, \"_cdsfl_paid_tripwire\", False):\n"
     "        return getattr(_sock.getaddrinfo, \"_cdsfl_original\")",
     "    pass",
     "the_installer_is_idempotent_and_returns_the_original"),
]


def main() -> int:
    argparse.ArgumentParser(description=__doc__.splitlines()[0]).parse_args()
    good = {p: p.read_bytes() for p in (WRAPPER, RSE)}
    shas = {p: hashlib.sha256(b).hexdigest() for p, b in good.items()}
    for p, h in shas.items():
        print(f"subject : {p.relative_to(REPO)}  sha256 {h[:16]}")
    base = subprocess.run([sys.executable, "-m", "pytest", str(GUARD), "-q"],
                          capture_output=True, text=True, cwd=REPO)
    print(f"baseline: {'GREEN' if base.returncode == 0 else 'RED'}")
    if base.returncode != 0:
        print(base.stdout[-1800:])
        return 1

    failures: list[str] = []
    try:
        for subject, name, anchor, repl, expect in MUTATIONS:
            txt = good[subject].decode("utf-8")
            if txt.count(anchor) != 1:
                failures.append(f"{name}: anchor appears {txt.count(anchor)} "
                                f"times, not 1 -- the probe is wrong")
                print(f"\n[{name}] ANCHOR COUNT WRONG; skipped")
                continue
            subject.write_text(txt.replace(anchor, repl, 1), encoding="utf-8")
            r = subprocess.run([sys.executable, "-m", "pytest", str(GUARD), "-q"],
                               capture_output=True, text=True, cwd=REPO)
            red, named = r.returncode != 0, expect in r.stdout
            tail = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
            print(f"\n[{name}]\n  subject: {subject.name}")
            print(f"  guard  : {'RED' if red else 'GREEN'}   {tail}")
            print(f"  the expected test is named: {named}")
            if not red:
                failures.append(f"{name}: guard stayed GREEN")
            elif not named:
                failures.append(f"{name}: red, but {expect!r} is not the failure")
            subject.write_bytes(good[subject])
    finally:
        ok = True
        for p, b in good.items():
            p.write_bytes(b)
            back = hashlib.sha256(p.read_bytes()).hexdigest()
            ok &= back == shas[p]
            print(f"restored: {p.name} sha256 matches = {back == shas[p]}")
        if not ok:
            print("★ A SUBJECT MAY BE MUTATED. Restore it by hand.")
            return 1

    print("\n" + "=" * 70)
    if failures:
        for f in failures:
            print("FAILURE:", f)
        return 1
    print(f"all {len(MUTATIONS)} reversions turn the guard red")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
