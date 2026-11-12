#!/usr/bin/env python3
"""Each mutation of the roster-aware window must turn its guard RED.

Mutates `bench/reference_runner_v3.py` in place, runs
`bench/tests/test_both_convergence_arms_are_roster_aware_2026-11-12.py`, and
RESTORES THE BYTES IT FOUND -- not the bytes it expected, because a restore that
writes an assumed original is itself a mutation.

THE MUTATIONS ARE CHOSEN TO BREAK THE PROPERTIES, NOT THE SYNTAX. A harness that
only proves a file can be made to fail to import proves nothing about the guard.
"""
from __future__ import annotations

import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
SUBJECT = REPO / "bench" / "reference_runner_v3.py"
GUARD = (REPO / "bench" / "tests"
         / "test_both_convergence_arms_are_roster_aware_2026-11-12.py")

MUTATIONS = [
    ("M1 the window stops rising when seats drop (floor instead of ceiling)",
     "    return -((-k_i * dec) // live)", "    return (k_i * dec) // live"),
    #: ★ M2 IS A 2-SITE MUTATION AND THE REASON IS WORTH RECORDING. The first
    #: version removed only the `if n_live is None:` branch and the guard stayed
    #: GREEN -- correctly, because `int(None)` raises and the `except` below
    #: returns K anyway. The None contract is protected TWICE, which is defence
    #: in depth and good code, so NO SINGLE-SITE MUTATION CAN BREAK IT. A
    #: harness that mutates one of 2 redundant protections proves nothing about
    #: the guard; it measures the redundancy. Both protections are therefore
    #: removed together, which is the only edit that genuinely loses the
    #: property.
    ("M2 BOTH protections for an absent counter are removed, so None stops "
     "returning K and every existing caller demands K * n_declared quiet rounds",
     "    if n_live is None:\n        try:\n            return max(1, int(k))\n"
     "        except (TypeError, ValueError):\n            return 1\n",
     "    if n_live is None:\n        n_live = 0\n"),
    ("M3 a measured 0 live seats becomes the CHEAPEST path rather than the strictest",
     "        return k_i * max(1, dec)", "        return k_i"),
    ("M4 the roster is ignored entirely, so the gate goes back to roster-blind",
     "    if dec < 1 or live >= dec:\n        return k_i",
     "    if True:\n        return k_i"),
    ("M5 the hardened arm -- the one that RUNS -- stops reading the helper",
     '    W = required_quiet_run(\n        cfg.gamma_alt_consecutive_zero_crit, '
     'len(getattr(cfg, "models", []) or []), n_live)',
     "    W = cfg.gamma_alt_consecutive_zero_crit"),
    ("M6 the legacy arm stops reading the helper",
     '    window = required_quiet_run(\n        cfg.gamma_alt_consecutive_zero_crit, '
     'len(getattr(cfg, "models", []) or []), n_live)',
     "    window = cfg.gamma_alt_consecutive_zero_crit"),
]


def main() -> int:
    found = SUBJECT.read_bytes()
    src = found.decode("utf-8")
    red = 0
    try:
        print(f"{len(MUTATIONS)} mutations; each must turn its guard red\n")
        for label, a, b in MUTATIONS:
            n = src.count(a)
            if n != 1:
                raise SystemExit(
                    f"ANCHOR NOT UNIQUE for {label}: {n} occurrence(s). The "
                    f"subject moved; fix this harness rather than the count.")
            SUBJECT.write_text(src.replace(a, b, 1), encoding="utf-8")
            r = subprocess.run([sys.executable, "-m", "pytest", str(GUARD), "-q",
                                "-p", "no:cacheprovider"],
                               cwd=REPO, capture_output=True, text=True, timeout=600)
            if r.returncode != 0:
                red += 1
                fails = [l for l in r.stdout.splitlines() if l.startswith("FAILED")]
                print(f"  RED    {label}")
                for f in fails[:3]:
                    print(f"           -> {f.split('::')[-1]}")
            else:
                print(f"  GREEN  {label}   <<< THE GUARD MISSED IT")
    finally:
        SUBJECT.write_bytes(found)
        print(f"\nsubject restored byte-identical: "
              f"{SUBJECT.read_bytes() == found} ({len(found)} bytes)")
    print(f"\n{red} of {len(MUTATIONS)} mutations red")
    return 0 if red == len(MUTATIONS) else 1


if __name__ == "__main__":
    sys.exit(main())
