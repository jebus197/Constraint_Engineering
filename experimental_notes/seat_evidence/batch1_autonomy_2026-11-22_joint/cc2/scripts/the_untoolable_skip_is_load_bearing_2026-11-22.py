# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'batch1_autonomy_2026-11-22_joint', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 9afc18c63a956213a0941217873a33e3082b5ef69c560b4af26076ab2bbf51c3
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Is the UNTOOLABLE skip conditioned on a MEASURED probe, or a blanket disable?

WHY THIS SCRIPT EXISTS. The 2026-11-22 joint round put `skipif` markers on the
3 arms of `test_the_board_detector_fails_toward_writing_2026-11-22.py` whose
precondition -- an EXECUTABLE `/bin/ps` -- is unmeetable under panel seat
confinement. The project forbids marking a case skip to make it pass, and the
only thing separating an honest UNTOOLABLE from that prohibition is WHAT THE
SKIP IS CONDITIONED ON. A claim about that is a claim, so it is measured here.

METHOD, 2 ARMS DIFFERING IN ONE VARIABLE -- the probe's value, nothing else.
The guard file is copied to a scratch path with `_PS_USABLE` forced, and the
copy is run. Forcing the probe TRUE on a machine where `ps` is genuinely denied
must make those 3 arms RUN and go RED. If they stay green or stay skipped, the
marker is not load-bearing and the skip is a blanket disable.

  arm 1  probe as measured  -> the 3 ps-DENIED arms PASS, the 3 ps-REQUIRING
                               arms SKIP
  arm 2  probe forced True  -> the 3 ps-REQUIRING arms RUN and FAIL

ALSO ASSERTED: the 3 arms that pin the B205(c) repair carry NO marker and run
in BOTH arms. A repair measured only where it cannot be contradicted is not
measured.

Reads nothing outside the artefact under review: the guard file, and pytest.
"""
from __future__ import annotations

import pathlib
import re
import subprocess
import sys
import tempfile

for _c in (pathlib.Path(__file__).resolve().parent,
           *pathlib.Path(__file__).resolve().parents):
    if (_c / "_cli_help.py").is_file():
        sys.path.insert(0, str(_c))
        break
from _cli_help import answer_help  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[1]
GUARD = REPO / "bench" / "tests" / \
    "test_the_board_detector_fails_toward_writing_2026-11-22.py"

#: The arms whose precondition is an executable /bin/ps.
NEEDS_PS = ("test_ps_can_answer_is_true_on_a_working_machine",
            "test_the_triage_still_detects_a_real_board_when_ps_works",
            "test_a_shell_is_not_a_board_when_ps_can_identify_it")
#: The arms that PIN the repair. These must never be conditional.
PINS_REPAIR = ("test_ps_can_answer_is_false_when_ps_is_denied",
               "test_the_triage_returns_empty_when_ps_cannot_answer",
               "test_the_monitor_gate_still_detects_when_ps_cannot_answer")


def run(path: pathlib.Path, force_probe: bool) -> dict:
    """Run `path` (a copy of the guard) and return {test_name: PASS/FAIL/SKIP}."""
    src = path.read_text()
    if force_probe:
        src = src.replace("_PS_USABLE = _ps_is_usable()", "_PS_USABLE = True")
        assert "_PS_USABLE = True" in src, "the probe assignment has moved"
    #: ★ THE COPY MUST LIVE IN THE GUARD'S OWN DIRECTORY, AND THE FIRST VERSION
    #: OF THIS SCRIPT PUT IT IN `tempfile.TemporaryDirectory()`. The guard
    #: computes `REPO = pathlib.Path(__file__).resolve().parents[2]`, so a copy
    #: at a scratch path resolved REPO to the scratch parent, every path to the
    #: subject broke, and arm 1 read `4 failed, 3 skipped` instead of the
    #: `3 passed, 4 skipped` the same file gives in place. This script's own
    #: assertions caught it: all 6 repair-pinning checks reported FALSIFIED in
    #: BOTH arms, which is the signature of a broken probe rather than of a
    #: broken subject -- a defect cannot be present and absent at once.
    #: A SIBLING COPY, not a scratch one. The name does not match `test_*.py`
    #: so no board collects it by glob, and pytest collects an explicitly named
    #: path regardless -- checked by execution before relying on it. Removed in
    #: `finally` so a crash cannot leave it behind.
    copy = path.parent / f"_scratch_untoolable_probe_{'forced' if force_probe else 'measured'}.py"
    copy.write_text(src)
    try:
        out = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
             "-rsf", "--no-header", "-o", "addopts=", str(copy)],
            cwd=REPO, capture_output=True, text=True, timeout=600)
    finally:
        copy.unlink(missing_ok=True)
    txt = out.stdout + out.stderr
    res = {}
    for name in NEEDS_PS + PINS_REPAIR:
        if re.search(rf"^FAILED .*::{name}\b", txt, re.M):
            res[name] = "FAIL"
        elif re.search(rf"^SKIPPED .*{name}", txt, re.M) or \
                re.search(rf"{name}.*\n?.*SKIPPED", txt):
            res[name] = "SKIP"
        else:
            res[name] = "PASS"
    # SKIPPED lines carry the file:line, not the test name, so fall back to counts
    n_skip = txt.count("SKIPPED [")
    return {"res": res, "n_skip": n_skip, "raw": txt}


def main() -> int:
    print(f"subject: {GUARD}\n")
    a = run(GUARD, force_probe=False)
    b = run(GUARD, force_probe=True)

    print("arm 1, probe AS MEASURED on this machine")
    print(f"  SKIPPED lines: {a['n_skip']}")
    print("  " + a["raw"].strip().splitlines()[-1])
    print("\narm 2, probe FORCED True (the only variable changed)")
    print(f"  SKIPPED lines: {b['n_skip']}")
    print("  " + b["raw"].strip().splitlines()[-1])
    print()

    bad = []
    # The repair-pinning arms must PASS in BOTH arms, unconditionally.
    for n in PINS_REPAIR:
        if a["res"][n] != "PASS":
            bad.append(f"arm 1: {n} did not pass -- it pins the repair and must")
        if b["res"][n] != "PASS":
            bad.append(f"arm 2: {n} did not pass -- it pins the repair and must")
    # Forcing the probe True must make the ps-requiring arms RUN and FAIL here,
    # because /bin/ps really is denied. That is what makes the marker
    # load-bearing rather than a blanket disable.
    ran_red = [n for n in NEEDS_PS if b["res"][n] == "FAIL"]
    if not ran_red:
        bad.append("arm 2: forcing the probe True changed nothing -- the skipif "
                   "marker is NOT load-bearing and the skip is a blanket disable")
    if a["n_skip"] <= b["n_skip"]:
        bad.append(f"the probe does not drive the skips: {a['n_skip']} skipped "
                   f"as measured vs {b['n_skip']} skipped when forced True")

    print(f"  repair-pinning arms passing, probe as measured : "
          f"{sum(a['res'][n] == 'PASS' for n in PINS_REPAIR)} of {len(PINS_REPAIR)}")
    print(f"  repair-pinning arms passing, probe forced True : "
          f"{sum(b['res'][n] == 'PASS' for n in PINS_REPAIR)} of {len(PINS_REPAIR)}")
    print(f"  ps-requiring arms that RUN AND GO RED when forced: "
          f"{len(ran_red)} of {len(NEEDS_PS)}  {ran_red}")
    print()
    if bad:
        for line in bad:
            print(f"FALSIFIED — {line}")
        return 1
    print("The skip is conditioned on the MEASURED probe and nothing else: "
          "forcing it True makes the unmeetable arms run and go red, while the "
          "3 arms that pin the B205(c) repair pass unconditionally in both arms.")
    return 0


if __name__ == "__main__":
    answer_help(__doc__, __file__)
    sys.exit(main())
