#!/usr/bin/env python3
"""Does the serial gate a seat actually reaches queue 2 concurrent calls? Measured.

WHY THIS EXISTS AS A SCRIPT RATHER THAN A TEST. The test suite may not start the
licensed kernel -- its network guard denies any spawn named `wolframscript`, and
the Engine is single-kernel, so a suite that started one would contend with the
founder's own session. `bench/tests/test_wolfram_secondary_source_2026-09-17.py`
therefore drives the gate's ENTRY POINT against a fake kernel. This script closes
the remaining gap: it runs the 2-line shim a seat really reaches, against the
REAL Engine, and reports what came back.

WHAT IT MEASURES, in 1 run: 2 calls started at the same moment through the shim,
each classified by the Wolfram standard's own `classify`, and the 2 KERNEL
windows compared. Serialisation holds when those windows do not overlap and both
results are evidence. Without the queue, 3 concurrent calls measured on
2026-08-02 gave 1 result and 2 "Connection closed by WolframKernel".

THE FIRST VERSION OF THIS SCRIPT MEASURED THE WRONG INTERVAL AND REPORTED
"OVERLAPPED" AGAINST A GATE THAT WAS QUEUING CORRECTLY. It compared PROCESS
lifetimes, and the second process spends its wait inside its own lifetime, so
the 2 always overlap by construction. The kernel window is
`start + queued .. start + queued + ran`, and the gate records `queued` and `ran`
for every call it makes, so the measurement is taken from the gate's own log
rather than from the wall clock outside it.

FOUNDER, 2026-09-17: *"fully enable it ... Wolfram ... should remain the
secondary/verification source (a second falsifier)"*. Enabling it is only safe
because of the queue, so the queue is the thing to measure.

Read-only unless `--run` is given: it starts no kernel without it. Costs no
money on any flag -- the local Engine is licensed, not metered.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "bench"))

import wolfram_standard as W  # noqa: E402

GATE = W.SERIAL_GATE / "wolframscript"
PROBES = ("Sum[i, {i, 1, 10}]", "Prime[100]")
EXPECTED = ("55", "541")


def one(code: str, seat: str, timeout: int, log: pathlib.Path) -> dict:
    started = time.monotonic()
    env = {**__import__("os").environ, "CDSFL_SEAT": seat, W.CALL_LOG_ENV: str(log)}
    r = subprocess.run([str(GATE), "-code", code], capture_output=True, text=True,
                       timeout=timeout, env=env, stdin=subprocess.DEVNULL)
    ended = time.monotonic()
    body = ((r.stdout or "") + "\n" + (r.stderr or "")).strip()
    ok, why = W.classify("local", body, r.returncode)
    return {"seat": seat, "code": code, "start": started, "end": ended,
            "seconds": round(ended - started, 2), "returncode": r.returncode,
            "stdout": (r.stdout or "").strip(), "evidence": ok, "reason": why,
            "attributed": W.attribution("local") in (r.stderr or "")}


def kernel_window(call: dict, log: pathlib.Path) -> tuple[float, float] | None:
    """(kernel start, kernel end) for `call`, from the gate's own record of it.

    None when the record cannot be read, and the caller must NOT treat that as a
    pass. THE SECOND VERSION OF THIS SCRIPT DID: it matched the seat against the
    wrong field, found nothing, defaulted both numbers to 0, and reported 2
    zero-length windows as "not overlapping". A check that passes because it
    measured nothing is the failure shape this project keeps finding, so the
    absent case is now loud.
    """
    queued = ran = None
    for line in log.read_text(encoding="utf-8").splitlines():
        fields = line.split("\t")
        # The gate writes `<timestamp> <seat>\t<verdict>\t...`, so the seat is
        # the last token of field 0, not a field of its own.
        if not fields or fields[0].split(" ")[-1] != call["seat"]:
            continue
        for field in fields:
            if field.startswith("queued "):
                queued = float(field.split()[1].rstrip("s"))
            elif field.startswith("ran "):
                ran = float(field.split()[1].rstrip("s"))
    if queued is None or ran is None:
        return None
    return call["start"] + queued, call["start"] + queued + ran


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--run", action="store_true", help="actually call the local Engine twice")
    ap.add_argument("--timeout", type=int, default=300)
    ap.add_argument("--json", type=pathlib.Path, help="write the measurement here")
    ap.add_argument("--log", help="the gate's call log to read the kernel windows from")
    a = ap.parse_args(argv)

    if not a.run:
        print(f"read-only. The gate is {GATE}, policy {W.policy()!r}, lock {W.lock_path()}.\n"
              "Pass --run to start 2 concurrent calls on the local Engine.")
        return 0

    if W.real_wolframscript() is None:
        print("wolframscript is not installed: nothing to measure, and nothing is broken. "
              "Wolfram is the second falsifier here, never a dependency.")
        return 0

    log = pathlib.Path(a.log or (REPO / "experimental_notes" / "evidence" /
                                 "wolfram_serial_gate_calls_2026-09-17.log"))
    log.parent.mkdir(parents=True, exist_ok=True)
    log.write_text("", encoding="utf-8")
    with ThreadPoolExecutor(max_workers=2) as pool:
        got = list(pool.map(lambda p: one(p[0], p[1], a.timeout, log),
                            zip(PROBES, ("probe-A", "probe-B"))))
    windows = {g["seat"]: kernel_window(g, log) for g in got}
    if any(w is None for w in windows.values()):
        print(json.dumps({"measured": False, "why": "the gate's call log carried no queued/ran "
                          "record for 1 or both probes; nothing here is evidence",
                          "log": str(log)}, indent=2))
        return 3
    got.sort(key=lambda g: windows[g["seat"]][0])
    first, second = got
    overlap = windows[second["seat"]][0] < windows[first["seat"]][1]
    waited = round(windows[second["seat"]][0] - second["start"], 2)
    for g in got:
        g["kernel_seconds"] = round(windows[g["seat"]][1] - windows[g["seat"]][0], 2)
    answers = {g["stdout"] for g in got}
    out = {
        "when": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "gate": str(GATE), "policy": W.policy(), "lock": W.lock_path(),
        "calls": [{k: v for k, v in g.items() if k not in ("start", "end")} for g in got],
        "serialised": not overlap,
        "second_call_waited_seconds": waited,
        "kernel_windows_disjoint": not overlap,
        "both_evidence": all(g["evidence"] for g in got),
        "both_attributed": all(g["attributed"] for g in got),
        "answers_correct": answers == set(EXPECTED),
    }
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2))
    print(f"\n{'SERIALISED' if out['serialised'] else 'OVERLAPPED'}: the second call waited "
          f"{waited}s in the queue while the first held the kernel for "
          f"{first['kernel_seconds']}s. "
          f"Both evidence: {out['both_evidence']}. Answers correct: {out['answers_correct']}.")
    return 0 if (out["serialised"] and out["both_evidence"] and out["answers_correct"]) else 3


if __name__ == "__main__":
    raise SystemExit(main())
