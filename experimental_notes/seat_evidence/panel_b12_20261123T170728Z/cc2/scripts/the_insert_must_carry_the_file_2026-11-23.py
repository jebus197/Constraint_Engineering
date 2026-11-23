# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'panel_b12_20261123T170728Z', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 66af7f26d47d0b079eadb4076677079a12f283a5a5183a6885f44078286367d7
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Does the dash-m proxy require the sys.path insert to CARRY the file-derived path?

DESTINATION `scripts/`. Written 2026-11-23, panel batch 12, Q1, seat fable.

THE DEFECT THIS FALSIFIES. `_help_calls_unreachable_under_dash_m` in
`bench/tests/test_help_never_acts_2026-09-11.py` was widened on 2026-11-23 to
credit a `sys.path` insert among the swallowing `try`'s PRECEDING SIBLINGS, and
to reach `__file__` through a module-level name. The widening asked its 2
conditions SEPARATELY of the same bag of statements:

    inserts   = "a sys.path.insert call appears before the import"
    uses_file = "a file-derived name appears before the import"

Nothing required them to be the SAME expression. So a script whose insert takes
a CONSTANT path, with a file-derived name beside it for an unrelated reason, is
credited as answering `--help` under `python3 -m` -- and it does not. Run that
script as `python3 -m scripts.x --help` and its ordinary work runs and WRITES.

The repository's own discrimination case
`test_a_file_derived_name_is_required_not_just_any_insert` does not catch this:
it builds its constant-path variant by REPLACING the `__file__` assignment, so
`__file__` vanishes from the whole module and `uses_file` is False for a reason
the real shape does not share.

WHAT THIS ASSERTS. It imports the REAL predicate from the REAL test module -- no
retyped copy -- and asserts that 3 constant-path shapes are REFUSED while the 4
genuinely-repaired shapes, including the 2 scripts the widening was written for,
are still CREDITED. It raises AssertionError when the defect is present.

IT IS DIFFERENTIAL BY CONSTRUCTION. Both directions are asserted here, so the
check cannot pass by refusing everything -- and it is additionally driven
through `scripts/a_falsifier_must_disagree_with_itself_2026-11-23.py`, which
runs it against the pre-widening-fix bytes and the fixed bytes and requires the
2 verdicts to disagree.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
MATCHERS = REPO / "bench" / "tests" / "test_help_never_acts_2026-09-11.py"

#: A file-derived name used for something OTHER than the insert. The insert
#: itself takes a constant, so `-m` still cannot import `_cli_help`.
CONSTANT_INSERT_DERIVED_NAME_BESIDE = (
    "import sys, pathlib\n"
    "HERE = pathlib.Path(__file__).resolve().parent\n"
    "def main():\n"
    "    open('x','w').write('y')\n"
    "    return 0\n"
    "if __name__ == '__main__':\n"
    "    sys.path.insert(0, '/somewhere/else')\n"
    "    print(HERE)\n"
    "    try:\n"
    "        from _cli_help import answer_help\n"
    "        answer_help(__doc__, __file__)\n"
    "    except ImportError:\n"
    "        pass\n"
    "    sys.exit(main())\n")

#: The same, with the literal `__file__` beside the insert instead of a name.
CONSTANT_INSERT_BARE_FILE_BESIDE = (
    "import sys, pathlib\n"
    "def main():\n"
    "    open('x','w').write('y')\n"
    "    return 0\n"
    "if __name__ == '__main__':\n"
    "    sys.path.insert(0, '/somewhere/else')\n"
    "    print(pathlib.Path(__file__).name)\n"
    "    try:\n"
    "        from _cli_help import answer_help\n"
    "        answer_help(__doc__, __file__)\n"
    "    except ImportError:\n"
    "        pass\n"
    "    sys.exit(main())\n")

#: The insert is INSIDE the try, still constant, with `__file__` used beside it.
CONSTANT_INSERT_INSIDE_TRY = (
    "import sys, pathlib\n"
    "def main():\n"
    "    open('x','w').write('y')\n"
    "    return 0\n"
    "if __name__ == '__main__':\n"
    "    try:\n"
    "        sys.path.insert(0, '/somewhere/else')\n"
    "        print(pathlib.Path(__file__).name)\n"
    "        from _cli_help import answer_help\n"
    "        answer_help(__doc__, __file__)\n"
    "    except ImportError:\n"
    "        pass\n"
    "    sys.exit(main())\n")

MUST_REFUSE = {
    "constant insert, derived name beside it": CONSTANT_INSERT_DERIVED_NAME_BESIDE,
    "constant insert, bare __file__ beside it": CONSTANT_INSERT_BARE_FILE_BESIDE,
    "constant insert inside the try": CONSTANT_INSERT_INSIDE_TRY,
}

#: The insert CARRIES the file-derived path. These are the forms the widening
#: was written to accept and they must not regress.
SIBLING_INSERT_VIA_NAME = (
    "import sys, pathlib\n"
    "REPO = pathlib.Path(__file__).resolve().parents[1]\n"
    "def main():\n"
    "    open('x','w').write('y')\n"
    "    return 0\n"
    "if __name__ == '__main__':\n"
    "    sys.path.insert(0, str(REPO / 'scripts'))\n"
    "    try:\n"
    "        from _cli_help import answer_help\n"
    "        answer_help(__doc__, __file__)\n"
    "    except ImportError:\n"
    "        pass\n"
    "    sys.exit(main())\n")

INSIDE_INSERT_VIA_FILE = (
    "import sys, pathlib\n"
    "def main():\n"
    "    open('x','w').write('y')\n"
    "    return 0\n"
    "if __name__ == '__main__':\n"
    "    try:\n"
    "        sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))\n"
    "        from _cli_help import answer_help\n"
    "        answer_help(__doc__, __file__)\n"
    "    except ImportError:\n"
    "        pass\n"
    "    sys.exit(main())\n")

MUST_CREDIT = {
    "preceding-sibling insert via a file-derived name": SIBLING_INSERT_VIA_NAME,
    "insert inside the try, built from __file__": INSIDE_INSERT_VIA_FILE,
}

#: The 2 real scripts the widening was written for, plus the original subject.
REAL_SUBJECTS = ("the_restore_mutations_2026-11-22.py",
                 "the_majority_separation_mutations_2026-11-22.py",
                 "assemble_panel_record.py")


def main() -> int:
    spec = importlib.util.spec_from_file_location("_hna", MATCHERS)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    answers_help = m.answers_help

    bad = []
    for label, src in MUST_REFUSE.items():
        got = answers_help(src, under_dash_m=True)
        print(f"  must REFUSE  {label:42s} -> {got}")
        if got is not False:
            bad.append(f"CREDITED a constant-path insert: {label}")

    for label, src in MUST_CREDIT.items():
        got = answers_help(src, under_dash_m=True)
        print(f"  must CREDIT  {label:42s} -> {got}")
        if got is not True:
            bad.append(f"REFUSED a genuinely repaired guard: {label}")

    for name in REAL_SUBJECTS:
        p = REPO / "scripts" / name
        got = answers_help(p.read_text(encoding="utf-8"), under_dash_m=True)
        print(f"  must CREDIT  {name:42s} -> {got}")
        if got is not True:
            bad.append(f"REFUSED a real script that does answer --help: {name}")

    if bad:
        print("FALSIFIED")
        raise AssertionError(
            "the dash-m proxy does not require the sys.path insert to carry the "
            "file-derived path:\n  " + "\n  ".join(bad))
    print("\n  the insert must CARRY the file-derived path: upheld in both "
          "directions.")
    return 0


if __name__ == "__main__":
    # argparse is not used: this script takes no arguments, so `_cli_help`'s
    # own contract applies and `answer_help` is the right guard. The insert
    # CARRIES the file-derived path, which is the property under test here.
    sys.path.insert(0, str(REPO / "scripts"))
    try:
        from _cli_help import answer_help
        answer_help(__doc__, __file__)
    except ImportError:
        pass
    raise SystemExit(main())
