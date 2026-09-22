#!/usr/bin/env python3
"""FALSIFIER: the R_k one-directional "self-report bias" is a parser artefact.

THE CLAIM UNDER TEST. Morning report 2026-09-22 SS6: seats understate their own
R_k, 18 of 19 one-directional, p = 7.63e-05; parsing named as an untested
"leading candidate" cause. This script tests it against the SHIPPED extractor.

THE MECHANISM. `_RK_RE_CLIP` bounds a parameter statement at commas,
comparisons and sentence ends, but not (before 2026-09-22) at an arrow. Seats
write inline derivations:

    R_old=0.50, eta=0.90, d=0.85, p=0.80 -> q = 0.90x0.85x0.80 = **0.612**

The statement for `p` runs through the arrow into the q-derivation, and the
last-'=' rule returns 0.612 -- q's value -- as p. The q-line regex requires q
at line START, so q falls back to eta*d*p with the poisoned p:
q_extracted = eta*d*q_true < q_true whenever eta*d < 1. A smaller q gives a
larger R_det, so the recomputed R_k is biased UPWARD in every affected
section. The one-directional delta is the parser's direction, not the seats'.

EXIT BEHAVIOUR. AssertionError (exit 1) while the defect is present in the
shipped `_RK_RE_CLIP`; exit 0 once the arrow boundary is added. Prints a
census over all archived raw responses so reach is measured, not asserted.

Run:  python3 scripts/rk_parser_arrow_boundary_falsifier_2026-09-22.py
"""

from __future__ import annotations

import glob
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import List, Optional, Tuple

REPO = Path(__file__).resolve().parents[1]
RUNNER = REPO / "bench" / "reference_runner_v3.py"
EXHIBIT = (REPO / "bench" / "logs" /
           "commissioning_arm1_panel_20260921T215405Z" /
           "r0_chatgpt-sim_20260921T220848Z.json")


def load_shipped_namespace() -> dict:
    """Exec the R_k extraction block out of the REAL runner file.

    The full module cannot be imported standalone, so the extraction block --
    regexes, statement reader, validator, section extractor -- is exec'd from
    the file's own text: byte-for-byte the shipped code, not a paraphrase.
    """
    lines = RUNNER.read_text().splitlines(keepends=True)
    start = next(i for i, ln in enumerate(lines)
                 if "_RK_RE_R_OLD = re.compile" in ln)
    end = next(i for i, ln in enumerate(lines)
               if ln.startswith("def validate_round_rk"))
    ns = {"re": re, "Tuple": Tuple, "Optional": Optional, "List": List}
    exec("".join(lines[start:end]), ns)
    return ns


def main() -> int:
    ns = load_shipped_namespace()
    doc = json.loads(EXHIBIT.read_text())
    section0 = ns["_extract_corroboration_sections"](doc["response"])[0]

    p = ns["_rk_stated_value"](ns["_RK_RE_P"], section0)
    status, model_rk, recomputed = ns["_validate_rk_computation"](section0)
    print(f"exhibit: {EXHIBIT.name} section 0")
    print("  seat stated      : R_old=0.50, eta=0.90, d=0.85, p=0.80, "
          "q=0.612, S_k=0.97, nu_eff=0.0443, R_k=0.318 (arithmetic correct)")
    print(f"  extractor read p : {p}")
    print(f"  validator verdict: {status}  model_rk={model_rk} "
          f"recomputed={recomputed}")

    c: Counter = Counter()
    for path in sorted(glob.glob(str(REPO / "bench/logs/commissioning_*/r*_*.json"))):
        try:
            d = json.loads(Path(path).read_text())
        except Exception:
            continue
        if not isinstance(d, dict) or "response" not in d:
            continue
        for s in ns["_extract_corroboration_sections"](d["response"]):
            st, _, _ = ns["_validate_rk_computation"](s)
            c[st] += 1
    print(f"  census over all archived raw sections: {dict(c)}")

    assert p == 0.80, (
        f"FALSIFIED: the extractor read p={p} where the seat wrote p=0.80; "
        f"the statement ran through the arrow into the q-derivation")
    assert status != "FAIL", (
        f"FALSIFIED: correct seat arithmetic scored {status} "
        f"(recomputed={recomputed} vs stated {model_rk})")
    print("clean exit: the arrow boundary is present and the exhibit passes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
