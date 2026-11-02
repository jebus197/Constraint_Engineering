#!/usr/bin/env python3
"""Reverse each property the admission module claims and confirm its guard goes RED.

A suite that cannot fail proves nothing. Each mutation inverts ONE property. Any
mutation leaving the suite green names a property the suite does not check, and a
mutation that cannot be APPLIED is reported as a skip rather than as a pass --
2 mutations on 2026-11-02 were discarded for exactly that, one because it merely
prepended text and one because it removed the first of 2 occurrences.
"""
from __future__ import annotations
import pathlib, subprocess, sys

# `_cli_help` lives in scripts/.
import sys as _sys, pathlib as _pl  # noqa: E402
for _cand in (_pl.Path(__file__).resolve().parent, *_pl.Path(__file__).resolve().parents):
    if (_cand / "_cli_help.py").is_file():
        if str(_cand) not in _sys.path:
            _sys.path.insert(0, str(_cand))
        break
from _cli_help import answer_help  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[1]
MOD = REPO / "bench" / "model_admission.py"
DECL = REPO / "bench" / "cdsfl_registry" / "models" / "Fable.toml"
TEST = (REPO / "bench" / "tests" /
        "test_one_declaration_admits_a_model_2026-11-02.py")

MUTATIONS = [
    (MOD, "admission applies nothing at all",
     "            if not dry_run:\n                table[key] = value",
     "            if False:\n                table[key] = value"),
    (MOD, "a hard-coded entry no longer wins, so the change stops being additive",
     '            if key in table:\n                # A HARD-CODED ENTRY ALWAYS WINS.',
     '            if False:\n                # A HARD-CODED ENTRY ALWAYS WINS.'),
    (MOD, "the composer key map is no longer filled, the 1 entry that caused 3 absences",
     '            (co.COMPOSER_MODEL_MAP, model, "composer_key",\n'
     '             lambda v, _c=ckey: str(v), "composer.COMPOSER_MODEL_MAP"),',
     '            # removed by mutation'),
    (MOD, "the fingerprint is no longer filled",
     '            (rc.INITIAL_FINGERPRINTS, model, "fingerprint",',
     '            (dict(), model, "fingerprint",'),
    (MOD, "a malformed declaration is swallowed instead of reported",
     '        return {"_error": f"{type(exc).__name__}: {exc}", "_path": str(p)}',
     '        return {}'),
    (MOD, "the record of what changed is dropped, so an inert run looks the same",
     '    return {"applied": applied, "skipped": skipped, "errors": errors,',
     '    applied = []\n    return {"applied": applied, "skipped": skipped, "errors": errors,'),
    (DECL, "the declared work bound drops to the silent 8000 default",
     "max_directive_chars = 12000", "max_directive_chars = 8000"),
    (DECL, "the declared composer key is wrong, so the 2 phenotype tables miss",
     'composer_key = "fable_5_1"', 'composer_key = "fable_WRONG"'),
    (DECL, "the specification bound is set, against his 2026-10-14 ruling",
     "max_directive_chars = 12000\nformat_style = \"full\"",
     "max_directive_chars = 12000\nspec_chars = 4000\nformat_style = \"full\""),
]


def run_suite() -> bool:
    p = subprocess.run([sys.executable, "-m", "pytest", str(TEST), "-q",
                        "--no-header", "-x"], capture_output=True, text=True,
                       timeout=300, cwd=str(REPO))
    return p.returncode == 0


def main() -> int:
    answer_help(__doc__, __file__)
    originals = {MOD: MOD.read_text(), DECL: DECL.read_text()}
    print("=" * 78)
    print("DECLARATION-ADMISSION MUTATION TEST")
    print("=" * 78)
    if not run_suite():
        print("  THE SUITE IS ALREADY RED. Nothing can be concluded. Stopping.")
        return 2
    print("  baseline: GREEN\n")
    red = applied = 0
    try:
        for path, label, old, new in MUTATIONS:
            src = originals[path]
            if src.count(old) != 1:
                print(f"  [SKIP  ] {label}")
                print(f"           anchor appears {src.count(old)} times, not 1 -- "
                      f"NOT APPLIED, so nothing is tested")
                continue
            applied += 1
            path.write_text(src.replace(old, new, 1))
            if run_suite():
                print(f"  [GREEN ] {label}")
                print(f"           *** NOT GUARDED. ***")
            else:
                red += 1
                print(f"  [RED   ] {label}")
            path.write_text(src)
    finally:
        for p, src in originals.items():
            p.write_text(src)
    print(f"\n  {red} of {applied} applied mutation(s) turned the suite RED")
    ok = all(p.read_text() == s for p, s in originals.items())
    print(f"  every mutated file restored to its original text: {ok}")
    return 0 if (red == applied and applied and ok) else 1


if __name__ == "__main__":
    sys.exit(main())
