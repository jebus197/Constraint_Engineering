#!/usr/bin/env python3
"""Does the discrimination control already test DEPENDENCE, not merely ACCESS?

The 2026-08-12 panel refuted `discrimination_control_blocks` on three grounds:
satisfied by ACCESS rather than DEPENDENCE, defeated by `open(TARGET).read()`
with the contents discarded, and it fails green.  The 2026-09-15 founder ruling
says arm it and test it live.  This falsifier decides which governs, by running
the SHIPPED control's own interception probe against both falsifier shapes.

Run against the real `bench/reference_runner_v3` — nothing is retyped.

    python3 scripts/discrimination_dependence_check_cc_seat_2026-09-21.py
    python3 scripts/discrimination_dependence_check_cc_seat_2026-09-21.py --help
"""
from __future__ import annotations

import argparse
import pathlib
import shutil
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "bench"))
import reference_runner_v3 as RR
from falsifier_verify import execute_python

FAIL: list[str] = []


def head(n): print("\n" + "=" * 74 + f"\n{n}\n" + "=" * 74)


# ------------------------------------------------------------------ B1
def b1_flag_gates_only_the_reversal():
    """The flag gates the REVERSAL. The measurement has no flag at all."""
    head("B1  WHAT THE FLAG ACTUALLY GATES")
    src = (ROOT / "bench/reference_runner_v3.py").read_text().splitlines()
    sites = [(i + 1, l.strip()) for i, l in enumerate(src)
             if "discrimination_control_blocks" in l and "getattr" in l]
    for ln, txt in sites:
        print(f"   line {ln}: {txt[:100]}")
    assert len(sites) == 2, f"expected 2 runtime read sites, found {len(sites)}"

    # Both sites guard a resolve/un-confirm, never the measurement.
    for ln, _ in sites:
        # The two blocking shapes: un-confirm outright, or withhold the
        # CONFIRMED close and divert to HIL. Both are the REVERSAL, not the
        # measurement.
        window = "\n".join(src[ln - 1: ln + 20])
        assert any(t in window for t in ("UNCONFIRMED", 'resolve(', 'tally["HIL"]')), (
            f"FALSIFIED: site at line {ln} gates something other than the "
            f"verdict reversal")
    print("   -> both runtime reads guard the verdict REVERSAL.")

    # The measurement itself is presence-gated: it runs iff a corrected copy
    # exists. `discrimination_control_ask` supplies that copy and is ON.
    cfg = RR.RunnerConfig()
    print(f"   RunnerConfig().discrimination_control_blocks = "
          f"{cfg.discrimination_control_blocks}")
    print(f"   RunnerConfig().discrimination_control_ask    = "
          f"{getattr(cfg, 'discrimination_control_ask', 'ABSENT')}")
    assert cfg.discrimination_control_blocks is False
    sim = (ROOT / "bench/tools/run_simulated_experiment.py").read_text()
    assert "discrimination_control_ask=True" in sim, (
        "FALSIFIED: the simulated run does not ask for a corrected copy")
    print("   -> the study run ALREADY runs and records the control.")
    print("      'Armed and tested live' and 'the blocking design is refuted'")
    print("      are satisfied SIMULTANEOUSLY by the shipped defaults.")


# ------------------------------------------------------------------ B2
def b2_tripwire_is_a_dependence_test():
    """Run the SHIPPED interception probe on access-only vs dependent code."""
    head("B2  THE INTERCEPTION PROBE — access or dependence?")
    repo = pathlib.Path(tempfile.mkdtemp(prefix="cdsfl_b2_"))
    try:
        (repo / "pkg").mkdir()
        tgt = "pkg/target.py"
        (repo / tgt).write_text("VALUE = 41\n")

        real = RR._build_discrimination_overlay(repo, tgt, "VALUE = 41\n")
        trip = RR._build_discrimination_overlay(repo, tgt, RR.DISC_TRIPWIRE_BODY)

        # (a) ACCESS ONLY — opens the target and throws the contents away.
        access = ("import pathlib\n"
                  "pathlib.Path('pkg/target.py').read_text()\n"
                  "print('FALSIFIED')\n")
        # (b) DEPENDENT — its output is a function of the target's contents.
        depend = ("import sys; sys.path.insert(0, '.')\n"
                  "from pkg.target import VALUE\n"
                  "assert VALUE == 42, 'FALSIFIED'\n")

        out = {}
        for name, code in (("access-only", access), ("dependent", depend)):
            a, _ = RR._retarget_falsifier(code, repo, real)
            b, _ = RR._retarget_falsifier(code, repo, trip)
            pa = execute_python(a, repo_root=str(real), cwd=str(real))
            pb = execute_python(b, repo_root=str(trip), cwd=str(trip))
            na = RR._normalise_probe_output(
                pa[0] if isinstance(pa, tuple) else pa, (real, repo))
            nb = RR._normalise_probe_output(
                pb[0] if isinstance(pb, tuple) else pb, (trip, repo))
            intercepted = (nb != na)
            out[name] = intercepted
            verdict = "proceeds to the control" if intercepted else \
                      RR.DISC_NOT_INTERCEPTED
            print(f"   {name:12s}: intercepted={intercepted!s:5s} -> {verdict}")

        assert out["access-only"] is False, (
            "FALSIFIED: an access-only falsifier passes the interception probe, "
            "so the control tests ACCESS and the 2026-08-12 refutation stands")
        assert out["dependent"] is True, (
            "FALSIFIED: a genuinely dependent falsifier is rejected as "
            "not-intercepted, so the probe is unusable")
        assert RR.DISC_NOT_INTERCEPTED in RR.DISC_INDETERMINATE, (
            "FALSIFIED: not-intercepted is not an INDETERMINATE outcome — "
            "the control would fail green")
        print(f"   DISC_NOT_INTERCEPTED in DISC_INDETERMINATE : "
              f"{RR.DISC_NOT_INTERCEPTED in RR.DISC_INDETERMINATE}")
        print("   -> the probe is a DEPENDENCE test and it fails INDETERMINATE,")
        print("      not green. The dependence-based check the panel asked for")
        print("      already exists, inside the control it refuted.")
    finally:
        shutil.rmtree(repo, ignore_errors=True)
        for p in pathlib.Path(tempfile.gettempdir()).glob("cdsfl_disc_*"):
            shutil.rmtree(p, ignore_errors=True)


def main() -> int:
    argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter).parse_args()
    for fn in (b1_flag_gates_only_the_reversal, b2_tripwire_is_a_dependence_test):
        try:
            fn()
        except AssertionError as exc:
            print(f"   FALSIFIED  {fn.__name__}: {exc}")
            FAIL.append(fn.__name__)
        except Exception as exc:  # apparatus failure is NOT a verdict
            print(f"   UNCHECKED  {fn.__name__}: {type(exc).__name__}: {exc}")
            FAIL.append(fn.__name__ + " (UNCHECKED)")
    head("SUMMARY")
    print(f"   FALSIFIED/UNCHECKED: {len(FAIL)}  {FAIL}")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
