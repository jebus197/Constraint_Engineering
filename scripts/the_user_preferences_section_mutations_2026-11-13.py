#!/usr/bin/env python3
"""Does the B163 user-preferences guard go RED? 5 mutations, 1 per contract.

★ T5 MUTATES THE ENGINE, not the template, and it is the contract worth reading.
If a `user` layer is ever added to `VALID_LAYERS`, the template's note saying the
layer position is still open becomes a statement contradicting the code. C5 goes
red so that it is updated rather than left standing.
"""
from __future__ import annotations

import hashlib
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
TEMPLATE = REPO / "bench" / "directives" / "universal" / "expert_encoding_template.md"
ENGINE = REPO / "bench" / "cdsfl_registry" / "engine.py"
GUARD = "bench/tests/test_the_encoding_carries_user_preferences_2026-11-13.py"

MUTATIONS = [
    (TEMPLATE, "T1 provenance stops being required",
     "test_c1_the_section_requires_provenance_on_every_entry",
     "#   stated_by        = \"<who said it>\"",
     "#   (no author recorded)",
     "a preference with no author cannot be questioned and so cannot be withdrawn"),

    (TEMPLATE, "T2 a field is invented beside the schema's vocabulary",
     "test_c2_every_field_named_exists_in_the_real_schema",
     "#   constraint_class = \"HARD\"",
     "#   bindingness      = \"HARD\"",
     "a 2nd preferences vocabulary beside the parameter schema's, which is the "
     "2-declarations-of-1-fact drift this project keeps finding"),

    (TEMPLATE, "T3 the write prohibition removed",
     "test_c3_the_harness_may_propose_and_may_not_write",
     "A machine may\n# NOT write this file.",
     "A machine may update this file.",
     "the harness edits a researcher's stated preferences, which is a machine "
     "mutating a human's constraint with no human in the loop"),

    (TEMPLATE, "T4 the deferred decisions stop being named",
     "test_c4_the_contested_decisions_are_named_not_silently_decided",
     "# 4. WHAT IS DELIBERATELY NOT SPECIFIED HERE",
     "# 4. Notes",
     "a reader concludes the length bound and the layer position were forgotten "
     "rather than sequenced and deferred"),

    (ENGINE, "T5 a `user` layer is added to the engine",
     "test_c5_the_layer_decision_is_still_genuinely_open",
     'VALID_LAYERS = {"universal", "domain", "task", "model"}',
     'VALID_LAYERS = {"universal", "domain", "task", "model", "user"}',
     "the template still says the layer position is open while the code has "
     "decided it -- the note must be updated, not left contradicting the engine"),
]


def run(selector: str) -> tuple[int, str]:
    r = subprocess.run([sys.executable, "-m", "pytest", GUARD, "-k", selector,
                        "-q", "--no-header", "-p", "no:cacheprovider"],
                       cwd=REPO, capture_output=True, text=True, timeout=600)
    return r.returncode, (r.stdout + r.stderr)[-300:]


def main() -> int:
    originals = {p: p.read_bytes() for p in {m[0] for m in MUTATIONS}}
    digests = {p: hashlib.sha256(b).hexdigest() for p, b in originals.items()}
    for p, d in digests.items():
        print(f"subject: {p.relative_to(REPO)}  sha256 {d[:16]}")
    print()
    rc, tail = run(" or ".join(m[2] for m in MUTATIONS))
    if rc != 0:
        print(f"REFUSED: baseline is already red (rc={rc}).\n{tail}")
        return 2
    print("BASELINE GREEN\n")
    red, results = 0, []
    try:
        for subject, name, selector, old, new, why in MUTATIONS:
            src = originals[subject].decode()
            if old not in src:
                print(f"  {name}: ANCHOR NOT FOUND -- proves nothing")
                results.append((name, "ANCHOR MISSING"))
                continue
            subject.write_text(src.replace(old, new, 1))
            rc, tail = run(selector)
            ok = rc != 0
            red += ok
            results.append((name, "RED" if ok else "STILL GREEN"))
            print(f"  {name}\n    target  : {selector}\n    why     : {why}")
            print(f"    verdict : {'RED (caught)' if ok else 'STILL GREEN -- BLIND'}")
            if not ok:
                print(f"    tail    : {tail.strip()[:200]}")
            subject.write_bytes(originals[subject])
    finally:
        for p, b in originals.items():
            p.write_bytes(b)
        ok_all = all(hashlib.sha256(p.read_bytes()).hexdigest() == digests[p]
                     for p in originals)
        print(f"\nrestore verified for {len(originals)} file(s): {ok_all}")
        assert ok_all, "THE RESTORE FAILED -- a subject is left mutated"
    print(f"\nmutations_red = {red} of {len(MUTATIONS)}")
    for n, v in results:
        print(f"    {v:<14} {n}")
    rc, _ = run(" or ".join(m[2] for m in MUTATIONS))
    print(f"\npost-restore baseline: {'GREEN' if rc == 0 else f'RED (rc={rc})'}")
    return 0 if red == len(MUTATIONS) and rc == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
