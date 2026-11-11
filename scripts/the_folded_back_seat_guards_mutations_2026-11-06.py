#!/usr/bin/env python3
"""Mutation harness for the 2 guards folded back from the free panel round.
import sys

WHY THIS IS OWED. `fff-external` says FFAFP applies with equal force to fixes
proposed by other models: "someone else already checked it" is not a
substitute. 2 guards arrived from the seats, 60 tests passed, and until this
script ran NOT ONE had been seen to fail under my own hand.

2 OF THEM WERE ALREADY SEEN RED, NATURALLY AND BEFORE ANY MUTATION, which is
stronger evidence than a mutation: folding back cc2's guard WITHOUT its
appendix edit left `test_1c_...` and `test_1d_...` failing, and applying the
edit turned them green. That is a real red observed on real content.

This harness covers the rest by breaking the APPENDIX the guards read -- the
subject, not the guards -- and requiring the named test to go red. The
appendix is restored from the bytes this script read.
"""
from __future__ import annotations
import pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
APPENDIX = ROOT / "docs" / "MATHEMATICAL_APPENDIX.md"
CC2 = ROOT / "bench/tests/test_no_severity_bound_above_one_half_is_a_magnitude_test_2026-11-06.py"
FABLE = ROOT / "bench/tests/test_severity_composition_key_property_2026-11-06.py"
#: ★ 3 OF 4 MUTATIONS WENT GREEN AGAINST THE SEATS' OWN GUARDS, so the gaps
#: they left are now pinned by a guard of this project's own and the
#: mutations are re-aimed at it. The seats' guards are UNCHANGED: editing a
#: delivered guard would muddy whose work is whose. Each mutation records
#: BOTH verdicts, so the gap itself stays visible rather than being tidied
#: away by the fix.
PINNED = ROOT / "bench/tests/test_the_severity_factor_values_are_pinned_2026-11-06.py"


def _anchor(src: str, needle: str, label: str) -> str:
    n = src.count(needle)
    if n != 1:
        raise SystemExit(f"ANCHOR {label!r} found {n} times, expected 1 -- "
                         f"the harness is stale, not the guard")
    return needle


def mutations(src: str):
    out = []

    a = _anchor(src, "**`S_v` is a credence, not a severity**", "credence clarification")
    out.append(("M1 the credence clarification is deleted",
                src.replace(a, "**S_v**"), CC2,
                "section_7_8_marks_S_v_as_a_credence"))

    a = _anchor(src, "| W(SOFT) | 0.5 | Soft preference |", "W(SOFT) row")
    out.append(("M2 W(SOFT) is raised to 1.0, so the 2 classes stop differing "
                "(seat guard: GREEN, missed it)",
                src.replace(a, "| W(SOFT) | 1.0 | Soft preference |"), PINNED,
                "two_classes_differ"))

    a = _anchor(src, "| Ver(False) | 0.0 | Computationally disproved |", "Ver(False) row")
    out.append(("M3 Ver(False) becomes 0.1, so a disproved finding stops scoring 0 "
                "(seat guard: GREEN, missed it)",
                src.replace(a, "| Ver(False) | 0.1 | Computationally disproved |"), PINNED,
                "scores_exactly_zero or product_really_is_zero"))

    a = _anchor(src, "selected(f) ≡ (Sev(f) > τ_sev) ∧ (S_v(f) ≥ 0.5)",
                "the 7.11 conjunction")
    out.append(("M4 7.11 stops conjoining Sev and S_v "
                "(seat guard: GREEN, missed it)",
                src.replace(a, "selected(f) ≡ (Sev(f) > τ_sev)"), PINNED,
                "requires_both_quantities"))
    return out


def main() -> int:
    found = APPENDIX.read_bytes()
    src = found.decode()
    muts = mutations(src)
    print(f"subject: {APPENDIX.relative_to(ROOT)}")
    print(f"{len(muts)} mutations; each must turn its guard red\n")
    red = 0
    try:
        for label, mutated, test, kexpr in muts:
            if mutated == src:
                print(f"  INERT  {label}"); continue
            APPENDIX.write_text(mutated)
            cmd = [sys.executable, "-m", "pytest", str(test), "-q", "--no-header"]
            if kexpr:
                cmd += ["-k", kexpr]
            r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=900)
            n_fail = len(re.findall(r"(?m)^FAILED ", r.stdout))
            if r.returncode != 0:
                red += 1
                print(f"  RED    {label}\n           -> {test.name}, {n_fail} test(s) failed")
            else:
                print(f"  GREEN  {label}  <- {test.name} DID NOT CATCH THIS")
    finally:
        APPENDIX.write_bytes(found)
        assert APPENDIX.read_bytes() == found, "RESTORE FAILED -- the appendix is damaged"
        print(f"\nappendix restored byte-identical ({len(found)} bytes)")
    print(f"\n{red} of {len(muts)} mutations red")
    return 0 if red == len(muts) else 1


if __name__ == "__main__":
    import pathlib as _pl
    sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
    from _cli_help import answer_help as _answer_help
    _answer_help(__doc__, __file__)
    raise SystemExit(main())
