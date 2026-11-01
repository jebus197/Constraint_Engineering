#!/usr/bin/env python3
"""MUTATION HARNESS for the primary/secondary falsifier rule, 2026-10-31.

A guard that does not go RED when the fix is reverted is not a guard. Each
mutation below undoes ONE property of the 2026-10-31 work and the harness
asserts the guard file notices. Exit 0 only if every mutation is caught.

EXACT BYTES ARE RESTORED IN A `finally`, so an interrupted run cannot leave the
tree mutated. The restore is verified by re-reading each file afterwards.
"""
from __future__ import annotations

import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
GUARD = "bench/tests/test_the_secondary_falsifier_rule_2026-10-31.py"

IA = REPO / "bench" / "immune_agents.py"
FP = REPO / "bench" / "falsifier_pairing.py"
ORT = REPO / "bench" / "openrouter_tools.py"
WS = REPO / "bench" / "wolfram_standard.py"
TOML = REPO / "bench" / "cdsfl_registry" / "tool_manifest.toml"

# (label, file, find, replace)
MUTATIONS = [
    ("wolfram loses secondary_only -> it could become a primary",
     TOML, 'independence_class = "reference"\nsecondary_only = true',
     'independence_class = "reference"'),
    ("an entry loses its independence_class",
     TOML, '[tools.sympy]\ndescription = "Symbolic mathematics: algebraic identities, limits, equation solving."\nverifier = "_verify_sympy"\nneeds_file = false\nclaim_types = ["mathematical", "logical"]\nindependence_class = "symbolic"',
     '[tools.sympy]\ndescription = "Symbolic mathematics: algebraic identities, limits, equation solving."\nverifier = "_verify_sympy"\nneeds_file = false\nclaim_types = ["mathematical", "logical"]'),
    ("independence ignores a shared verifier",
     FP, "    if shares_verifier(primary, candidate, manifest):\n        return False",
     "    if False:\n        return False"),
    ("an unclassified tool is treated as independent",
     FP, "    if not cp or not cc:\n        return False", "    if not cp or not cc:\n        return True"),
    ("a paid route becomes selectable by default",
     FP, "    pool = unpaid or ([] if not allow_paid else independent)",
     "    pool = unpaid or independent"),
    ("the delegate filter is dropped from the primary pool",
     FP, "    return [c for c in candidates\n            if not is_secondary_only(c, manifest)\n            and not is_delegated(c, manifest)]",
     "    return [c for c in candidates if not is_secondary_only(c, manifest)]"),
    ("primary-only and corroborated become indistinguishable",
     FP, '        return f"[falsifier:primary-only {primary} reason={reason} ({detail})]"',
     '        return f"[falsifier:secondary {primary} agreement=AGREES ({detail})]"'),
    ("install_check is no longer executed",
     FP, '            exec(compile(chk, f"<install_check:{tool}>", "exec"), {})  # noqa: S102\n            ok = True',
     "            ok = True"),
    ("the dispatch stops using the primary pool (secondary_only unenforced)",
     IA, "for tool_name in _fpair.primary_candidates(specialist_tools, manifest):",
     "for tool_name in specialist_tools:"),
    ("the dispatch stops writing a pairing note",
     IA, "            if sec is None:\n                v.evidence += \" \" + _fpair.pairing_note(\n                    primary_name, None, reason, detail)",
     "            if sec is None:\n                pass"),
    ("the translator guard reverts to lowercase-only",
     IA, '_ANY_CALL = re.compile(r"\\b([A-Za-z][A-Za-z0-9_]*)\\s*\\(")',
     '_ANY_CALL = re.compile(r"\\b([a-z][A-Za-z0-9_]*)\\s*\\(")'),
    ("wolfram_verify leaves the host-side tool surface",
     ORT, "    MYPY_TOOL_SPEC,\n    WOLFRAM_TOOL_SPEC,\n]", "    MYPY_TOOL_SPEC,\n]"),
    ("the serial clause reverts to naming only the shell route",
     WS, '"call the `wolfram_verify` tool, which evaluates on the host\'s kernel and returns its output. "',
     '""'),
    ("the near-expiry licence text reverts to the by-hand advice",
     WS, 'f"EXPECTED: renewal is automated under the LaunchAgent "',
     'f"EXPECTED: renew it by hand. Automated under the LaunchAgent "'),
]


def run_guard() -> tuple[int, str]:
    r = subprocess.run(
        [sys.executable, "-m", "pytest", GUARD, "-q", "--no-header", "-x"],
        cwd=REPO, capture_output=True, text=True)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def main() -> int:
    originals = {p: p.read_bytes() for p in (IA, FP, ORT, WS, TOML)}

    rc, out = run_guard()
    if rc != 0:
        print("BASELINE IS NOT GREEN -- mutation results would be meaningless")
        print(out[-3000:])
        return 1
    print(f"baseline: GREEN  ({out.strip().splitlines()[-1]})")
    print()

    caught, missed = 0, []
    try:
        for label, path, find, repl in MUTATIONS:
            src = path.read_text(encoding="utf-8")
            if find not in src:
                missed.append((label, "ANCHOR NOT FOUND -- mutation never applied"))
                print(f"  SKIP  {label}\n        anchor missing, so this says nothing")
                continue
            path.write_text(src.replace(find, repl, 1), encoding="utf-8")
            try:
                rc, out = run_guard()
            finally:
                path.write_text(src, encoding="utf-8")
            if rc != 0:
                caught += 1
                print(f"  RED   {label}")
            else:
                missed.append((label, "guard stayed GREEN"))
                print(f"  GREEN {label}   <-- NOT CAUGHT")
    finally:
        for p, b in originals.items():
            p.write_bytes(b)
        bad = [str(p) for p, b in originals.items() if p.read_bytes() != b]
        print()
        print(f"restore verified byte-for-byte: {not bad}" + (f" FAILED: {bad}" if bad else ""))
        if bad:
            return 1

    rc, out = run_guard()
    print(f"post-restore baseline: {'GREEN' if rc == 0 else 'RED -- RESTORE BROKE SOMETHING'}")

    print()
    print(f"caught {caught} of {len(MUTATIONS)} mutations")
    for label, why in missed:
        print(f"   NOT CAUGHT: {label} ({why})")
    return 0 if (not missed and rc == 0) else 1


if __name__ == "__main__":
    sys.exit(main())
