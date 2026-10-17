#!/usr/bin/env python3
"""Does the credential redactor withhold ordinary CONFIG fields? -- found under B28.

WHY IT MATTERS. `_declared_config` in each run report exists so a reader can see
what the run was told to do. Entry B28 reconciles each declared mode against
whether that mode was actually OPERATING, which needs the declared value to be
readable. If the redactor withholds a field because its NAME resembles a secret,
the reconciliation cannot be performed for that mode at all -- not wrongly, but
not at all, which is worse because nothing reports the absence.

FOUND CONCRETELY, not hypothesised: in leg 3 of the shakedown the report records
`location_crit_series_is_gating = True`, so the mode was operating, while its
declared value reads `<withheld: name matches a credential pattern>` because
`location_keyed_convergence` contains the substring "key".

This script counts how many declared-config fields are withheld across the whole
archive and names them, so the scope is a measured set rather than one example.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
WITHHELD = re.compile(r"withheld|redact", re.I)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--logs", default=str(REPO / "bench" / "logs"))
    args = ap.parse_args()

    names: Counter = Counter()
    reports_with = 0
    reports_seen = 0
    for p in sorted(Path(args.logs).rglob("*_report.json")):
        if "sandbox_harvest" in str(p):
            continue
        try:
            d = json.loads(p.read_text(errors="ignore"))
        except Exception:                                          # noqa: BLE001
            continue
        dc = d.get("_declared_config")
        if not isinstance(dc, dict):
            continue
        reports_seen += 1
        hit = [k for k, v in dc.items() if isinstance(v, str) and WITHHELD.search(v)]
        if hit:
            reports_with += 1
            names.update(hit)

    print(f"reports carrying a declared config: {reports_seen}")
    if not reports_seen:
        print("none found -- the question could not be asked, which is not a pass")
        return 2
    pct = 100.0 * reports_with / reports_seen
    print(f"of those, reports withholding at least 1 config field: "
          f"{reports_with}, {pct:.4f}%")
    print()
    print("THE WITHHELD FIELD NAMES, with how many reports each appears in:")
    for name, n in names.most_common():
        looks_secret = bool(re.search(r"(secret|token|password|credential|api)", name, re.I))
        verdict = "plausibly a secret" if looks_secret else "★ NOT a secret"
        print(f"  {n:4}x  {name:44} {verdict}")
    print()
    false_positives = [n for n in names
                       if not re.search(r"(secret|token|password|credential|api)", n, re.I)]
    if false_positives:
        print(f"★ {len(false_positives)} withheld field name(s) carry no secret-bearing "
              f"word. Each is an ordinary run setting that cannot be read back, so any")
        print("  check comparing what a run was TOLD to do against what it DID is blind")
        print("  for that setting. The substring that triggers it is visible in the name.")
    else:
        print("every withheld name carries a secret-bearing word, so no false positive")
        print("is demonstrated on this archive.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
