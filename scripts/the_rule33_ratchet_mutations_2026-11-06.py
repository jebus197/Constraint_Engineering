#!/usr/bin/env python3
"""Mutation harness for the Rule 33 ratchet, 2026-11-06.

A ratchet that has never been seen to fail is a ratchet that asserts nothing.
This strips a recommendation and a named standard out of the DATA -- the real
subject, since the ratchet reads the decisions record and not any code -- and
requires the NAMED test to go red. The subject is restored from the bytes this
script read, never from git.

WHY THE DATA AND NOT THE GUARD. Mutating the guard would show only that the
guard can fail. What has to be shown is that the guard notices the record
losing a recommendation, because that is the thing that actually happens: a
decision gets reworded and its argument quietly goes with it.
"""
from __future__ import annotations
import collections, json, pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "experimental_notes" / "data" / "morning_report_decisions.json"
PROD = ROOT / "scripts" / "does_every_decision_name_a_standard_2026-11-06.py"
TEST = ROOT / "bench" / "tests" / "test_every_decision_names_a_standard_2026-11-06.py"

STANDARD = re.compile(r"additive|simplest sufficient|composab", re.I)
RECOMMENDS = re.compile(r"this is the recommendation|\brecommend", re.I)


def _a_live_decision_with_both(data: dict) -> str:
    """DERIVED: pick a key the ratchet actually reads and that carries both."""
    for k, v in data.items():
        if not (k.startswith("task:") and isinstance(v, dict)):
            continue
        if v.get("ruled") or v.get("no_ruling_needed"):
            continue          # not live, so the ratchet would not read it
        blob = json.dumps(v)
        if STANDARD.search(blob) and RECOMMENDS.search(blob):
            return k
    raise SystemExit("ANCHOR NOT FOUND -- no live decision carries both; "
                     "the harness is stale, not the guard")


def main() -> int:
    found = DATA.read_bytes()
    prod_found = PROD.read_bytes()
    data = json.loads(found.decode(), object_pairs_hook=collections.OrderedDict)
    victim = _a_live_decision_with_both(data)
    print(f"subject: {DATA.relative_to(ROOT)}")
    print(f"guard:   {TEST.relative_to(ROOT)}")
    print(f"victim (derived): {victim}\n")

    def strip(obj, pattern, repl):
        s = json.dumps(obj)
        return json.loads(re.sub(pattern, repl, s, flags=re.I))

    muts = []

    d1 = json.loads(found.decode(), object_pairs_hook=collections.OrderedDict)
    d1[victim] = strip(d1[victim], r"additive|simplest sufficient|composab\w*", "XX")
    muts.append(("M1 a live decision loses every named standard", DATA, d1,
                 "test_every_live_decision_names_one_of_the_three_standards"))

    d2 = json.loads(found.decode(), object_pairs_hook=collections.OrderedDict)
    d2[victim] = strip(d2[victim], r"this is the recommendation|recommend\w*", "XX")
    muts.append(("M2 a live decision loses its recommendation", DATA, d2,
                 "test_every_live_decision_carries_a_recommendation"))

    d3 = json.loads(found.decode(), object_pairs_hook=collections.OrderedDict)
    for k, v in list(d3.items()):
        if k.startswith("task:") and isinstance(v, dict):
            v["no_ruling_needed"] = True        # empties the live queue
    muts.append(("M3 the live queue is emptied (both tests pass on nothing)",
                 DATA, d3, "test_the_ratchet_is_not_vacuous"))

    red = 0
    try:
        for label, path, payload, node in muts:
            path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
            r = subprocess.run([sys.executable, "-m", "pytest", str(TEST), "-q",
                                "--no-header", "-k", node.replace("test_", "")[:40]],
                               cwd=ROOT, capture_output=True, text=True, timeout=900)
            if r.returncode != 0:
                red += 1
                print(f"  RED    {label}\n           -> {node}")
            else:
                print(f"  GREEN  {label}  <- THE RATCHET DID NOT CATCH THIS")
            path.write_bytes(found)

        # M4 mutates the PRODUCER, so the --help guarantee is also exercised
        src = prod_found.decode()
        a = re.search(r'^    if "--help" in sys\.argv or "-h" in sys\.argv:$', src, re.M)
        if not a:
            print("  INERT  M4: the --help guard moved; harness is stale")
        else:
            PROD.write_text(src.replace(a.group(0), "    if False:"))
            r = subprocess.run([sys.executable, "-m", "pytest", str(TEST), "-q",
                                "--no-header", "-k", "help_costs_nothing"],
                               cwd=ROOT, capture_output=True, text=True, timeout=900)
            if r.returncode != 0:
                red += 1
                print(f"  RED    M4 --help runs the measurement\n"
                      f"           -> test_help_costs_nothing")
            else:
                print("  GREEN  M4 --help runs the measurement  <- NOT CAUGHT")
            PROD.write_bytes(prod_found)
    finally:
        DATA.write_bytes(found)
        PROD.write_bytes(prod_found)
        assert DATA.read_bytes() == found, "RESTORE FAILED -- the data is damaged"
        assert PROD.read_bytes() == prod_found, "RESTORE FAILED -- the producer is damaged"
        print(f"\nboth subjects restored byte-identical "
              f"({len(found)} + {len(prod_found)} bytes)")

    total = len(muts) + 1
    print(f"\n{red} of {total} mutations red")
    return 0 if red == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
