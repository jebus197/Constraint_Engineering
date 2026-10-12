#!/usr/bin/env python3
"""Which interpreters does the falsifier integrity allowlist actually cover?

THE NAMED PROPERTY THIS MEASURES. For every `python3` interpreter discoverable
on this machine, are the installation roots that interpreter reports for ITSELF
inside the allow set returned by `bench.falsifier_verify._interpreter_roots()`?
An uncovered root that EXISTS on disk is a false INTEGRITY_VIOLATION waiting to
happen: any falsifier spawning that interpreter trips the gate on its ordinary
import bootstrap, so the gate refuses the CORRECT falsifier.

WHY A SCRIPT AND NOT A PROSE CLAIM. Two seats of the free panel of 2026-10-12
each fixed this class, by different mechanisms, and the argument for each was
stated in prose: a declared list of roots (cc2) versus probing each interpreter
for its own roots (fable), the latter argued as "more robust". Measured on this
machine, the prose argument was BACKWARDS -- the probe covered FEWER
interpreters than the declared list, because it probed only 2 of the 4 present:

    baseline (no fix)                         1 of 4
    cc2, declared roots                       2 of 4
    fable, probe of 2 interpreters            1 of 4
    composed: probe + full discovery + sysconfig   4 of 4

THE INSTRUMENT'S OWN DEFECT, CORRECTED HERE. The first version of this script
counted a root as a coverage gap whether or not it existed. Three of the gaps
it reported were paths that DO NOT EXIST on disk
(`/Library/Python/3.9/site-packages` and two per-user site directories), and a
directory that does not exist can never produce a filesystem read, so excluding
it from an allowlist cannot cause a refusal. Counting them made the composed fix
read as 1 of 4 when it is 4 of 4. Only roots that exist are counted.

Usage: python3 scripts/interpreter_allowlist_coverage_2026-10-12.py
"""
import json
import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from _cli_help import answer_help  # noqa: E402

PROBE = (
    "import json,sys,sysconfig,site;"
    "p=sysconfig.get_paths();"
    "print(json.dumps({'v':sys.version.split()[0],"
    "'stdlib':p.get('stdlib'),'purelib':p.get('purelib'),"
    "'platlib':p.get('platlib'),'prefix':sys.prefix,"
    "'usersite':site.getusersitepackages()"
    " if hasattr(site,'getusersitepackages') else None}))"
)

CANDIDATES = (
    "/usr/bin/python3",
    "/opt/homebrew/bin/python3",
    "/usr/local/bin/python3",
    "/Library/Frameworks/Python.framework/Versions/3.13/bin/python3",
    "/Library/Frameworks/Python.framework/Versions/3.12/bin/python3",
    "/Library/Frameworks/Python.framework/Versions/3.11/bin/python3",
)

ROOT_KEYS = ("stdlib", "purelib", "platlib", "prefix", "usersite")


def discover() -> list[tuple[str, dict]]:
    """Every distinct interpreter that answers the probe, realpath-deduplicated."""
    seen: set[str] = set()
    out: list[tuple[str, dict]] = []
    for cand in list(CANDIDATES) + [shutil.which("python3"), sys.executable]:
        if not cand or not os.path.exists(cand):
            continue
        real = os.path.realpath(cand)
        if real in seen:
            continue
        seen.add(real)
        try:
            proc = subprocess.run([cand, "-c", PROBE],
                                  capture_output=True, text=True, timeout=20)
        except Exception:
            continue
        if proc.returncode == 0 and proc.stdout.strip():
            out.append((cand, json.loads(proc.stdout.strip().splitlines()[-1])))
    return out


def covered(path: str | None, roots: list[str]) -> bool:
    """Is `path` inside any allowed root?

    A path that does not EXIST is reported covered, because a directory that is
    not on disk can never be read and so can never be denied. That correction
    is the difference between reading the composed fix as 1 of 4 and as 4 of 4.
    """
    if not path or not os.path.exists(path):
        return True
    real = os.path.realpath(path)
    return any(real == r or real.startswith(r.rstrip(os.sep) + os.sep)
               for r in roots)


def main() -> int:
    answer_help(__doc__, __file__)
    import bench.falsifier_verify as fv
    roots = [os.path.realpath(r) for r in fv._interpreter_roots()]
    interps = discover()
    print(f"allow roots: {len(roots)}   interpreters discovered: {len(interps)}")
    full = 0
    for exe, info in interps:
        gaps = [k for k in ROOT_KEYS if not covered(info.get(k), roots)]
        if not gaps:
            full += 1
        print(f"  {exe}  ({info['v']})  "
              f"{'COVERED' if not gaps else 'UNCOVERED: ' + ','.join(gaps)}")
        for g in gaps:
            print(f"      {g} = {info.get(g)}")
    print(f"\ninterpreters fully covered (existing roots only): "
          f"{full} of {len(interps)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
