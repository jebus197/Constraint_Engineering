#!/usr/bin/env python3
"""Reverse each property the fix comparator claims and confirm its guard goes RED.

The comparator's whole value is that it REFUSES when ranking is undecidable, so
the mutations that matter most are the ones that make it answer anyway. A
mutation left green names a property the suite does not check; a mutation that
cannot be APPLIED is a SKIP and proves nothing either way.
"""
from __future__ import annotations
import pathlib, subprocess, sys

import sys as _sys, pathlib as _pl  # noqa: E402
for _cand in (_pl.Path(__file__).resolve().parent, *_pl.Path(__file__).resolve().parents):
    if (_cand / "_cli_help.py").is_file():
        if str(_cand) not in _sys.path:
            _sys.path.insert(0, str(_cand))
        break
from _cli_help import answer_help  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[1]
MOD = REPO / "bench" / "fix_comparator.py"
TEST = (REPO / "bench" / "tests" /
        "test_the_fix_comparator_refuses_to_rank_2026-11-02.py")

MUTATIONS = [
    ("it ranks by extent, which is the RUBRIC it exists not to be",
     '''        ranked, why = None, (
            f"{len(survivors)} candidate(s) survive the additive check''',
     '''        survivors.sort(key=lambda r: r["extent"]["new_chars"])
        ranked, why = (survivors[0]["label"] if survivors else None), (
            f"{len(survivors)} candidate(s) survive the additive check'''),
    ("a composition is allowed with NO measurement",
     '''    m = (composed or Candidate("composed", "")).measurement
    if not m:''',
     '''    m = (composed or Candidate("composed", "")).measurement
    if False:'''),
    # ★ RECLASSIFIED 2026-11-02 AS INEFFECTIVE, not as an unguarded property.
    # Removing `direction` from `need` leaves the requirement standing, because
    # the NEXT check rejects any direction that is not one of the 2 valid
    # strings and an absent key reads as the empty string. So the mutation does
    # not invert the property; it removes 1 of 2 guards on it. A green from an
    # ineffective mutation says nothing, exactly like a SKIP, and reporting it
    # as "NOT GUARDED" would have been a false finding about my own guard --
    # the same call made twice on the cy gate the same day.
    # ★ ANCHOR REPOINTED 2026-11-03. The subject's key set was hoisted to a
    # module-level `_COMPOSED_MEASUREMENT_KEYS` so the refusal MESSAGE could be
    # derived from it rather than retyped beside it -- the message had named 4
    # keys while the check enforced 5, and a caller obeying the message was
    # refused for `direction`. That hoist changed this anchor's text, and this
    # harness reported the mutation as SKIP while still printing "11 of 11
    # applied", so a property went untested behind a line that read green. The
    # anchor now names the module-level set, which is the 1 place the key set
    # lives, so it cannot drift from the subject again by a retype.
    ("the declared direction requirement is removed from BOTH checks",
     '''    need = set(_COMPOSED_MEASUREMENT_KEYS)''',
     '''    need = set(_COMPOSED_MEASUREMENT_KEYS) - {"direction"}
    m = dict(m); m.setdefault("direction", "higher_is_better")'''),
    ("direction is ignored, so lower-is-better inverts",
     '''    dominates = ((comp > aa and comp > bb) if d == "higher_is_better"
                 else (comp < aa and comp < bb))''',
     '''    dominates = (comp > aa and comp > bb)'''),
    ("a non-dominating composition is recommended anyway",
     '''    if dominates:
        return SATISFIES, (''',
     '''    if True:
        return SATISFIES, ('''),
    ("an unparseable fix reads as SATISFYING the additive standard",
     '''    if not r.success:
        return UNDECIDABLE, f"no parseable edit in the fix text: {r.reason}"''',
     '''    if not r.success:
        return SATISFIES, f"no parseable edit in the fix text: {r.reason}"'''),
    ("a deleted capability stops being a breach",
     '''    if deleted:
        return BREACHES, (''',
     '''    if False:
        return BREACHES, ('''),
    ("the RETIRED exemption is dropped, so retired names count as losses",
     '''        and n not in retired)''',
     '''        and n not in set())'''),
    ("mc_commands come back, which is the false-positive generator",
     '''CODE_IDENTIFIER_BUCKETS = ("runner_config_fields", "runner_public_entry_points",
                           "vault_subcommands")''',
     '''CODE_IDENTIFIER_BUCKETS = ("runner_config_fields", "runner_public_entry_points",
                           "vault_subcommands", "mc_commands")'''),
    ("the identifier length floor is dropped",
     '''_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]{2,}$")''',
     '''_IDENTIFIER = re.compile(r"^.+$")'''),
    ("a decision by elimination stops being labelled as one",
     '''            f"That is a decision by ELIMINATION and not a judgement of quality.")''',
     '''            f"That is the better fix.")'''),
    ("simplest-sufficient starts being scored",
     '''                     "simplest_sufficient": UNDECIDABLE,''',
     '''                     "simplest_sufficient": SATISFIES,'''),
]


def run_suite() -> bool:
    p = subprocess.run([sys.executable, "-m", "pytest", str(TEST), "-q",
                        "--no-header", "-x"], capture_output=True, text=True,
                       timeout=300, cwd=str(REPO))
    return p.returncode == 0


def main() -> int:
    answer_help(__doc__, __file__)
    original = MOD.read_text()
    print("=" * 78)
    print("FIX COMPARATOR MUTATION TEST")
    print("=" * 78)
    if not run_suite():
        print("  THE SUITE IS ALREADY RED. Nothing can be concluded. Stopping.")
        return 2
    print("  baseline: GREEN\n")
    red = applied = 0
    try:
        for label, old, new in MUTATIONS:
            if original.count(old) != 1:
                print(f"  [SKIP  ] {label}")
                print(f"           anchor appears {original.count(old)} times, "
                      f"not 1 -- NOT APPLIED, so nothing is tested")
                continue
            applied += 1
            MOD.write_text(original.replace(old, new, 1))
            if run_suite():
                print(f"  [GREEN ] {label}\n           *** NOT GUARDED. ***")
            else:
                red += 1
                print(f"  [RED   ] {label}")
            MOD.write_text(original)
    finally:
        MOD.write_text(original)
    print(f"\n  {red} of {applied} applied mutation(s) turned the suite RED")
    print(f"  module restored to its original text: {MOD.read_text() == original}")
    # ★ A SKIPPED ANCHOR USED TO EXIT 0, corrected 2026-11-03. The test was
    # `red == applied`, and a mutation whose anchor no longer matches lowers
    # `applied` AND is absent from `red`, so the equality still held and this
    # harness reported success while a property went untested. It happened:
    # a fix to the subject rewrote 1 anchor, this printed "11 of 11 applied"
    # and exited 0, and the direction requirement was unguarded until the
    # SKIP line was read by eye. The denominator is now the number of
    # mutations DECLARED, which a skip cannot move.
    return 0 if (red == applied == len(MUTATIONS)) else 1


if __name__ == "__main__":
    sys.exit(main())
