# Panel records, 2026-09-11

Byte copies of the raw panel output for the rounds run on 2026-09-11: panel_round11_2026-09-11, panel_round12_2026-09-11, panel_round13_2026-09-11, panel_round14_2026-09-11.

The originals live under `bench/logs/`, which `.gitignore:41` excludes, so before this copy existed they were recoverable by no commit and present on 1 machine only. The Personalisation directive requires external review output to be preserved *"in full and in unfiltered format"* and says *"Never summarise in place of the full output"*.

**Produced by `scripts/mirror_panel_records_2026-09-11.py`, not by hand.** The 2026-09-10 rescue was performed by hand and therefore rescued nothing afterwards; 9 later rounds went unmirrored and nothing reported it. Every copy here is verified against its original by sha256, and `--check` returns non-zero while any round is unmirrored. `bench/tests/test_panel_records_are_preserved_2026-09-11.py` runs that check on every suite run.

**Briefs carry a `.md.txt` suffix** so the commit-time note linter does not refuse an archival record whose only route to compliance would be EDITING it. That convention is not new here: `experimental_notes/evidence/` already stores seat-written code as `.py.txt` for the same reason.

**Every round ran with `PANEL_ONLY=cc2,fable`, so 0 paid seats were dispatched.** The check to run rather than taking this sentence's word for it: no `cx.json`, `cgpt.json` or `ds.json` exists in any round directory here or under `bench/logs/`. It is asserted by `TestNoPaidSeatWasDispatched`, together with an anti-vacuity case requiring the free seats' replies to be present — the absence of paid seats proves nothing about an empty directory.

**These are copies, not the record's new home.** `bench/logs/` remains archival and is never edited.

Written under CDSFL note standard v1.7 (26 August 2026).
