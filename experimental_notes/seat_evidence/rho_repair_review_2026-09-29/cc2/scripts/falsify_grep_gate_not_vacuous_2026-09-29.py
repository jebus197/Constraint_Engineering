# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'rho_repair_review_2026-09-29', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: cf2518eea0cb88e4b4dc0c3c706851ade67945e5813cca60f4a09698b453e982
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""FALSIFIER: does gating the grep divergence test on wrapper presence destroy
the detection it exists for?

CLAIM UNDER TEST. Skipping when no wrapper is loaded silently converts a real
regression -- a wrapper that loads and yet hides nothing -- into a green run.

FAILS (AssertionError) IFF THE GATE IS VACUOUS: i.e. if, with `_wrapper_state`
forced to report a LOADED wrapper and `counts` forced to report equal counts,
`test_the_session_grep_sees_fewer_files_than_usr_bin_grep` does not FAIL.
Exits cleanly when the detection survives the gate.

Imports the REAL test module and the REAL probe script; nothing is retyped.
Reads only those two files, writes nothing.
"""
from __future__ import annotations
import argparse, importlib.util, pathlib, sys, types

ROOT = pathlib.Path(__file__).resolve().parents[1]
TEST = ROOT / "bench" / "tests" / "test_shell_grep_blind_spot_2026-09-28.py"


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


def main() -> int:
    argparse.ArgumentParser(description=__doc__.splitlines()[0],
                            epilog="No arguments. 0 = gate sound, 1 = vacuous."
                            ).parse_args()
    t = _load(TEST, "grep_blind_spot_test")
    case = t.TestTheDivergenceIsReal()
    fake_mod = types.SimpleNamespace(counts=lambda p: (397, 397))

    # 1. Wrapper LOADED + zero divergence  -> the test MUST fail.
    t._wrapper_state = lambda: (True, "grep is a shell function")
    try:
        case.test_the_session_grep_sees_fewer_files_than_usr_bin_grep(fake_mod)
    except AssertionError as exc:
        print(f"[1] wrapper loaded, 397 == 397 -> test FAILED as required\n"
              f"    {str(exc).splitlines()[0][:120]}")
    except BaseException as exc:            # Skipped, or anything else
        print("FALSIFIED[1]: with the wrapper LOADED and zero divergence the "
              f"test did not fail — it raised {type(exc).__name__}: {exc}")
        raise AssertionError("gate is vacuous: real regression not detected")
    else:
        print("FALSIFIED[1]: with the wrapper LOADED and zero divergence the "
              "test PASSED.")
        raise AssertionError("gate is vacuous: real regression not detected")

    # 2. Wrapper ABSENT + zero divergence -> the test must SKIP, not fail.
    import pytest
    t._wrapper_state = lambda: (False, "grep is /usr/bin/grep")
    try:
        case.test_the_session_grep_sees_fewer_files_than_usr_bin_grep(fake_mod)
    except BaseException as exc:
        ok = isinstance(exc, getattr(pytest, "skip").Exception)
        print(f"[2] wrapper absent -> {type(exc).__name__} "
              f"({'skip, correct' if ok else 'NOT a skip'})")
        if not ok:
            raise AssertionError("absent wrapper should skip, not fail")
    else:
        raise AssertionError("FALSIFIED[2]: absent wrapper neither skipped nor failed")

    # 3. The unconditional invariant still bites in the impossible direction.
    try:
        case.test_the_session_grep_never_sees_MORE_than_usr_bin_grep(
            types.SimpleNamespace(counts=lambda p: (500, 397)))
    except AssertionError as exc:
        print(f"[3] seen=500 > real=397 -> invariant FAILED as required\n"
              f"    {str(exc).splitlines()[0][:120]}")
    else:
        raise AssertionError("FALSIFIED[3]: seen > real did not trip the invariant")

    print("REFUTED: the gate preserves the detection — a loaded wrapper with "
          "no divergence still fails, an absent wrapper skips, and the "
          "impossible direction is caught unconditionally.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
