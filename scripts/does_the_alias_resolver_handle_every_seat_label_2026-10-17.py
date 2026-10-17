#!/usr/bin/env python3
"""Does `_resolve_merge_source` resolve a composed finding id for every seat?

HIS CORRECTION, 2026-10-16: *"Stage 1 item 1.2 is marked done on an incomplete
repair. Its own text is the panel's finding word for word, and within its own
stated scope it still fails for 2 of 8 model labels, 25 per cent, interval
7.1479 to 59.0725."*

THE MECHANISM. `_resolve_merge_source` finds the finding id inside a MERGE
evidence line with `re.search(r'(?:F|C)(\\d+)', evidence)`. That pattern is
unanchored, so it matches the FIRST place in the string where a C or an F is
followed by digits -- and a seat label may itself contain one. On `CC2-SIM_F004`
it matches `C2` at offset 1, inside the label, and returns a local id that no
alias key holds. The resolver then returns None, and the specification converts
an unresolved MERGE source into a CONFIRM on the target. So a seat whose label
carries a digit after a C or an F has its merges silently inverted.

THIS CALLS THE RESOLVER. It does not re-implement the pattern, because a
re-implementation agrees with itself by construction -- the defect class this
project records as `execute-do-not-grep`, which has now found 5 faults here and
was found by reading in none of them.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[1]
for p in (str(REPO), str(REPO / "bench")):
    if p not in sys.path:
        sys.path.insert(0, p)

import reference_runner_v3 as R  # noqa: E402

#: The paid panel and its simulated stand-ins. The 6 vendor labels are the ones
#: `run_simulated_experiment.py` dispatches, and the `-SIM` suffix is mandatory
#: on a stand-in by his ruling of 2026-08-08, so both forms are live id prefixes.
VENDORS = ("CC2", "DeepSeek", "ChatGPT", "Gemini", "Codex", "Fable")
LABELS = VENDORS + tuple(f"{v}-SIM" for v in VENDORS)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()

    rows, bad = [], []
    for label in LABELS:
        local = "F004"
        composed = f"{label}_{local}"          # what `parse_findings` mints
        canonical = "C0040"
        reg = R.FindingRegistry()
        reg.entries[canonical] = {
            "id": canonical, "model": label, "status": "UNCONFIRMED",
            "severity": 0.8, "description": "the target of the merge",
        }
        # POPULATED THE WAY `register()` DOES IT, at line 3237:
        #   self._alias_map[f"{model_id}:{finding.finding_id}"] = canonical_id
        # and `finding_id` is the PREFIXED form, which is the whole point of
        # stage 1 item 1.2. A harness that registers the BARE id would make the
        # resolver look correct for the wrong reason.
        reg._alias_map[f"{label}:{composed}"] = canonical
        # THE EVIDENCE IS GROUP 3 OF `_VERDICT_RE`, which is the text AFTER the
        # verdict keyword and the canonical id -- so it carries the SOURCE id
        # and not the target. A first version of this script put the target in
        # the string too, which let the regex match the target's own `C0040`
        # and measured something that cannot occur.
        evidence = f"<- {composed} is the same defect"
        got = R._resolve_merge_source(evidence, label, reg)
        ok = got == canonical
        rows.append((label, composed, got, ok))
        if not ok:
            bad.append(label)

    n = len(rows)
    print(f"seat labels tested .................. {n}")
    print(f"resolved to the composed id ......... {n - len(bad)}")
    print(f"FAILED to resolve ................... {len(bad)}")
    if not a.quiet:
        print()
        print("  label           composed id        resolver returned   ok")
        for label, composed, got, ok in rows:
            print(f"  {label:<15} {composed:<18} {str(got):<19} {'yes' if ok else 'NO'}")

    if bad:
        try:
            from statsmodels.stats.proportion import proportion_confint
            lo, hi = proportion_confint(len(bad), n, method="beta")
            ci = f", Clopper-Pearson [{lo*100:.4f}%, {hi*100:.4f}%]"
        except Exception:                                   # noqa: BLE001
            ci = ""
        print()
        print(f"failure rate: {len(bad)} of {n} = {100*len(bad)/n:.4f}%{ci}")
        print(f"failing labels: {', '.join(bad)}")
        print()
        print("A failure here is not a dropped merge. The specification converts")
        print("an unresolved MERGE source into a CONFIRM on the target, so the")
        print("verdict INVERTS rather than being lost.")
    else:
        print("\nevery seat label resolves.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
