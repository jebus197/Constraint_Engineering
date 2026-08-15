# Open Brain project backfill — for your spot check

**2026-08-06.** 106 records classified by five readers over disjoint batches, each with its own
arithmetic check, plus an independent second opinion on every non-HIGH or unclassified call.
Applied to the store. Fully reversible from `~/CDSFL_ob_backups/open_brain_full_export_pre_backfill.json`.

**Result:** CDSFL 57, project_genesis 32, open_brain 13, unclassified 4. Zero rows now carry no project key.

**Safe by measurement, not assumption:** all 106 carried no content hash and no signature, so
relabelling them breaks no integrity chain. The single lower-case `cdsfl` row is the opposite case
and was deliberately left alone — last section.

---

## The 4 left UNCLASSIFIED

A wrong label is worse than none, so where the text did not decide the question the record now
*says* so and is selectable with `--project UNCLASSIFIED`, rather than being invisibly NULL.

**2026-03-06** · `f6706bf6` · agent `cc`
> STANDING DIRECTIVE: CX must consult CC before making or committing any prose-level changes. CX reports prose issues as FINDINGS with suggested direction; CC mak
*Why:* "CX retains full autonomy over code logic, tests, constitutional parameters, structural/routing, and technical documentation." Constitutional parameters is the Genesis constitutional_params.json surface, and structural/routing is the Genesis web app; the prose being governed is t
*Second opinion overrode the first pass (which said project_genesis):* DISAGREE — they said project_genesis; I say UNCLASSIFIED. The operative clause carries no project qualifier: "CX must consult CC before making or committing any prose-level changes. CX reports prose issues as FINDINGS with suggested direction; CC makes the actual edits." The sing

**2026-03-11** · `09495573` · agent `cc`
> test_anchor
*Why:* The entire record text is "test_anchor" (11 characters). There is nothing in it that names or implies a project.

**2026-03-11** · `20a2ae3a` · agent `cc`
> FILE_INTEGRITY_ROLLUP merkle_root=sha256:c2a1eab458e1290bf5bb51c3e8333d77cf9224caf6dc0074fcbac9a69fb9bbd8 entries=3 timestamp=2026-03-11T17:46:13.998903+00:00
*Why:* The entire text is one machine-emitted line: "FILE_INTEGRITY_ROLLUP merkle_root=sha256:c2a1eab... entries=3 timestamp=2026-03-11T17:46:13". The unprefixed token FILE_INTEGRITY_ROLLUP is emitted by exactly one file on disk, Project_Genesis/cw_handoff/file_integrity.py; the Metis t
*Second opinion overrode the first pass (which said project_genesis):* DISAGREE — they said project_genesis; I say UNCLASSIFIED. Their emitter fact is correct and I reproduced it: the unprefixed token comes from Project_Genesis/cw_handoff/file_integrity.py:424, while Metis/coordination/file_integrity.py:409 emits METIS_FILE_INTEGRITY_ROLLUP, and the

**2026-03-06** · `6430d9a3` · agent `cc`
> P-pass methodology correction (George, 2026-03-06): A P-pass does NOT mean 'identify problems and defer them.' It means: identify/falsify issues → iterate to fi
*Why:* "A P-pass does NOT mean 'identify problems and defer them.'"; "Same iterative method that produced Option C from the distributed ledger discovery."; "Applies to CC for backend work, CX for UX work. This is now a standing directive."


## The 3 the second opinion OVERRODE

**2026-04-18** · `7a1cba01` · first pass **UNCLASSIFIED** → applied **CDSFL**
> CDSFL standing directive — factual synthesis over agreement amplification. When the founder corrects a framing, deliver the correction grounded in the
DISAGREE — this should be CDSFL, not UNCLASSIFIED. The decisive problem is internal inconsistency with the first agent's own verdict on the twin record fdd8c6a2, which they labelled CDSFL. The two were written by the same agent 1.24 seconds apart (2026-04-18T06:34:57.588 and 06:34:58.829), same type "decision", same area "general", from the same named incident ("the Expert_Encodings_Tradable_Assets TTS incident"); bo

**2026-03-06** · `f6706bf6` · first pass **project_genesis** → applied **UNCLASSIFIED**
> STANDING DIRECTIVE: CX must consult CC before making or committing any prose-level changes. CX reports prose issues as FINDINGS with suggested directi
DISAGREE — they said project_genesis; I say UNCLASSIFIED. The operative clause carries no project qualifier: "CX must consult CC before making or committing any prose-level changes. CX reports prose issues as FINDINGS with suggested direction; CC makes the actual edits." The single project-specific token, "constitutional parameters" (Project_Genesis/config/constitutional_params.json, verified unique to Genesis), sits

**2026-03-11** · `20a2ae3a` · first pass **project_genesis** → applied **UNCLASSIFIED**
> FILE_INTEGRITY_ROLLUP merkle_root=sha256:c2a1eab458e1290bf5bb51c3e8333d77cf9224caf6dc0074fcbac9a69fb9bbd8 entries=3 timestamp=2026-03-11T17:46:13.9989
DISAGREE — they said project_genesis; I say UNCLASSIFIED. Their emitter fact is correct and I reproduced it: the unprefixed token comes from Project_Genesis/cw_handoff/file_integrity.py:424, while Metis/coordination/file_integrity.py:409 emits METIS_FILE_INTEGRITY_ROLLUP, and the capture call in that function passes --agent cc --type insight --area ops, matching this record's metadata exactly. But that identifies the


## The 10 flagged CROSS-PROJECT — the finding that may need your view

A single project key cannot express a record that genuinely spans two projects. These were labelled
by weight of content, which means the minority project's material becomes invisible to a filtered
query. If that matters, the fix is a **second key**, not a different label. Flagging rather than
deciding, because it changes the schema.

1. **2026-03-04** · `9bfe4c3a` → **project_genesis** (MEDIUM)
   CROSS-PROJECT. Opens with "Open Brain system just built by dedicated agent — 50 tests passing". Decisive point: the record itself draws the line, treating Open Brain as a newly built tool and then naming "Current project state" separately — and that state is entirely Genesis. Roughly one quarter of the text is an Open Brain milestone that a project=open_brain query will not see.

2. **2026-03-05** · `85306c45` → **project_genesis** (MEDIUM)
   CROSS-PROJECT, and the sharpest case in my batch. Item (1) is a real Open Brain milestone — "OpenBrain standalone package completed — project-agnostic, launchd daemon live (PID 94926), replaces crontab, tested end-to-end" — which becomes invisible to a project=open_brain query under a single-label scheme. Labelled by weight of content, not by the opening item. Flagging for human override.

3. **2026-03-07** · `d1a094d0` → **open_brain** (MEDIUM)
   CROSS-PROJECT by its own header, "CX OB/IM access diagnosis". The fix ("use im_service.py directly") points back at the Genesis-resident IM service, and the RECOVERY.md/MEMORY.md note is repo-ambiguous. Classified open_brain because what broke, and what is diagnosed, is the memory store's access path. A reviewer could reasonably move this.

4. **2026-03-04** · `ecef145c` → **open_brain** (MEDIUM)
   CROSS-PROJECT — flag for human review. The record closes with a Genesis repo state stamp: "1857 tests (1799 core + 58 web). All uncommitted on b9921e8." The core+web test split and HEAD b9921e8 are the Genesis working tree (same HEAD as the clearly-Genesis record at index 11). So the session was sitting in Genesis while doing Open Brain plumbing. I labelled on subject, not on host repo. If the pro

5. **2026-03-05** · `96bba3ab` → **open_brain** (MEDIUM)
   CROSS-PROJECT — flag for human review. Same hybrid shape as the record above: it also carries a Genesis blocker line ("Blocked on visual design pass until plumbing complete") and a Genesis state stamp ("1820 tests (1741 core + 79 web). HEAD b9921e8"). Written by cw, the Genesis UX agent, but about Open Brain plumbing. Note also that the test counts disagree with the other b9921e8 record (1820 vs 1

6. **2026-03-06** · `f6706bf6` → **UNCLASSIFIED** (MEDIUM)
   This is an agent working-practice directive, not project content, and it may have been intended to apply globally. Its only project-specific anchor is "constitutional parameters". If a human judges it a cross-project standing rule, UNCLASSIFIED would be the safer label. I classified it Genesis because the prose-versus-code division it settles arose from the Genesis storyboard and FAQ work, and it 

7. **2026-03-04** · `3acb060e` → **open_brain** (MEDIUM)
   CROSS-PROJECT RECORD, primary is Open Brain but not stated in-text. The record never names which MCP server is being wired. The immediately preceding session records make it explicit: index 5 — "Open Brain system built and verified. 50 tests passing. CLI working — status, capture, search, pending-tasks, session-context all tested. MCP server NOT yet wired into Claude Code settings (doing that now)

8. **2026-04-18** · `fdd8c6a2` → **CDSFL** (MEDIUM)
   CROSS-PROJECT BY ITS OWN WORDS: "Applies across all projects, all sessions, all written outputs where the founder's framing is cited back." I labelled it CDSFL because it self-identifies as a CDSFL standing directive and its canonical home is the CE repo, and because UNCLASSIFIED would hide it from EVERY project-scoped query rather than just the non-CDSFL ones. But the honest state is that this is

9. **2026-03-05** · `cb9c8e32` → **open_brain** (HIGH)
   Index 13. Cross-project edge: the remedy names the IM ack protocol and CW, both Genesis-hosted, and the blocker surfaced during a Genesis-era CX session. Labelled open_brain because the record is about OB's bridge architecture, but a reviewer scoping Genesis infra should know it exists.

10. **2026-03-06** · `6430d9a3` → **UNCLASSIFIED** (MEDIUM)
   CROSS-PROJECT BY CONSTRUCTION, and I am deliberately not forcing it. Its two project-specific anchors both point at the web platform (the distributed-ledger discovery, and the CC-backend / CX-UX split that was the platform build split at that date), which argues for Genesis. But its actual content is the definition of P-pass declared as a standing directive over all work, and P-pass is the central


## The one row deliberately left alone

One record reads `cdsfl`, ten read `CDSFL`. The obvious one-line `UPDATE` would break three things
at once — the row's own content hash, its Ed25519 signature, and the `previous_hash` link of the row
that chains to it — so a cosmetic fix would render as tampering. Instead every read predicate is now
case-insensitive: both spellings return all 68 CDSFL rows today, verified.

Written under CDSFL note standard v1.2 (14 May 2026).