# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'integrity_advisory_2026-10-02', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 46089cda1e410c7b7517ae30ffd040eed4ae650b26b3fc2330b24a44661a68ae
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Revision 7: wire the advisory to a caller.

"An addition that nothing reaches is not additive either -- every new flag, gate
or entry point must be wired to a caller and executed by a test" (founder,
standing). `build_key_access_advisory` had exactly one caller: its own test. It is
now printed by `bench/score_exam.py`, which is the one place that already runs the
post-run scan, and on stdout rather than stderr so it lands in the scored record.

The existing REFUSAL is left exactly as it is. It is a SCORING guard, not the
convergence machinery: the ruling says a key read "is a reporting and post run fix
issue (as it always has been)", and `score_exam` is that post-run stage. Removing
a control because an advisory now exists beside it would be a removal without a
committed measurement showing the replacement dominates.

Usage:  python3 scripts/apply_advisory_wiring_rev7_2026-10-02.py [--check]
"""
from __future__ import annotations

import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
CHECK = "--check" in sys.argv
p = REPO / "bench" / "score_exam.py"
text = p.read_text(encoding="utf-8")

ANCHOR = '''        rep = scan_run(a.run_dir, key_dir=protected)
        compromised = bool(getattr(rep, "confirmed", None))'''
NEW = '''        rep = scan_run(a.run_dir, key_dir=protected)
        compromised = bool(getattr(rep, "confirmed", None))
        # THE END-OF-RUN ADVISORY (founder ruling 2026-10-02): report a key that
        # was read, say nothing when none was. Printed on stdout so it travels
        # with the scored record, and it changes no number here -- `compromised`
        # is computed above, from the same report, and is not re-derived from the
        # advisory's text.
        try:
            from key_access_forensics import build_key_access_advisory  # type: ignore
            _adv = build_key_access_advisory(rep)
        except ImportError:                                # pragma: no cover
            _adv = None
        if _adv:
            print(_adv)'''

if NEW in text:
    print("  = rev7 (already applied)")
elif text.count(ANCHOR) != 1:
    raise SystemExit(f"ANCHOR NOT UNIQUE: {text.count(ANCHOR)}")
elif CHECK:
    print("WOULD APPLY: rev7: score_exam prints the advisory")
else:
    p.write_text(text.replace(ANCHOR, NEW, 1), encoding="utf-8")
    print("APPLIED: rev7: score_exam prints the advisory")
