# Round 15 seat proposals, as the seats wrote them

**Why these are here as `.txt` rather than as live code.** The panel harness
crashed after both seats replied — `diff -u` raised `UnicodeDecodeError` on a
byte that is not valid UTF-8 — so `seat_proposals.diff`, the artefact that
normally carries the seats' fixes, was never written. The replies survived on
disk and the sandboxes survived the crash, so these 4 files were read out of the
sandboxes directly.

**They are preserved unedited.** 3 of the 4 were adopted into the working tree
and adapted there; the adapted versions differ, because an adopted fix is a
hypothesis until it has been run against the tree it is going into, and the first
one raised `AttributeError` on its first call here. These copies are the record
of what each seat actually produced, which the adapted versions are not.

**`test_panel_round15_fixes_2026-09-11.py` was NOT adopted.** It tests that
seat's own implementations of the same repairs, which differ from the ones that
shipped. Its 4 genuinely uncovered scenarios were ported into the existing test
files instead, in this project's idiom and against the signatures that landed.

The seats were `cc2` and `fable`, both on the Max subscription. **0 paid
dispatches.**

Written under CDSFL note standard v1.7 (26 August 2026).
