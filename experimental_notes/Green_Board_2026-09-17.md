# Green board, and the defects behind it

**17 September 2026, 06:22 BST.** Full suite green at commit `725d1f9`, clean tree.

## The board

**7447 passed, 0 failed, 5 skipped, 1 xfailed, 1339.35s (22m19s).** Pass rate 7447 of 7447 = 100.0000%, Wilson 95% [99.9484%, 100.0000%], Clopper-Pearson [99.9505%, 100.0000%], computed with statsmodels, a scipy closed form and mpmath at 30 dp agreeing to 8.39e-17.

The suite could not finish before this session: projected over 4 hours, abandoned twice.

## W1's phantom dependency

`blocker_triage` reported entry W1 naming `verdict-tuple` inside a declared dependency. W1 contains it 0 times.

Entry bodies slice from each heading to the next, and the **last** entry ran to EOF. The `# SUPPLEMENTARY LIST` of 59 items appended on 2026-09-11 was absorbed by it — 7,612 characters of table carrying a row about the verdict-tuple guard. W1's BLOCKED state then short-circuited the dependency check.

**6 consumers carried the identical slice.** They now share `task_list_markers.end_of_entries`. W1's body is 15 lines, 3,113 characters, 0 occurrences.

Guard: `bench/tests/test_entry_bodies_stop_at_the_supplementary_list_2026-09-17.py`.

## The 611-second test file

`cited_where` ran `git grep -l` per path — 1.42s against 8,705 tracked files — and every caller looped it over the untracked set, which had grown 58 to 95 because the A8 reversal untracked 37 `bench/logs` files.

| approach | cost |
|---|---|
| 95 separate `git grep` calls | 135.4s |
| 1 `git grep`, 95 patterns | 127.8s |
| 1 pass, 95-branch alternation | >660s |
| 1 pass, 1 extraction regex | 2.0s |

The alternation attempt was mine and was 5 times worse than what it replaced. Adopted: 1 index, 1 simple pattern after a `"bench/logs/" not in text` reject. All 95 paths classify identically — CODE ONLY 41, NOTE 27, TESTS ONLY 18, ELIDED 9. File: 611s to 7s.

Producer `scripts/orphan_figures_2026-09-10.py`; guard `bench/tests/test_citation_index_agrees_with_git_2026-09-17.py`.

## The 97% has a producer

`Panel_Stage1_Audit_FULL_RECORD_2026-08-18.md` states the removal rate 6 times and named no script. `scripts/immune_removal_rate_exp46_2026-09-17.py` reproduces **9 of 9** declared figures over the same 27 findings and 351 pairs, using the live backend in `bench/dm/_similarity.py` rather than a copy.

~~**Unreproduced:** that module's comment claims clamping gave 15.8%; the same 351 pairs give 18.5% hypothetical and 21.4% actual. Carried, not dropped.~~

**Correction, 2026-09-17 11:17 BST: the paragraph above is wrong.** The comment's 97.4% and 15.8% both reproduce exactly on the set they were measured on: the 272 of the 351 pairs whose findings do not share a flaw class, 265 of 272 flagged before the clamp and 43 of 272 after. Measurement M10 of the 2026-08-18 panel record labelled that set "(n=272)"; the plain-English note of the same day qualified the 15.8% "for pairs without a class match" but called the 97.4% a rate "of all pairs", so it carried both labels, and the code comment kept the wrong one. The overnight check computed rates over all 351 pairs and over the 79 that share a class, never over the other 272, and did not consult M10. Arithmetic over that class partition leaves only the 272 but cannot exclude every other subset, since 20 pair counts up to 351 admit both figures; the identification rests on M10's label, with its medians as corroboration. The record's measurement blocks also state 15 figures, not the 9 counted above, and all 15 reproduce. The comment now names each set, and `scripts/immune_removal_rate_exp46_2026-09-17.py` checks every figure and exits 1 if one fails.

## Introduced and caught within the session

1. The Desktop mirror went stale on a byte-length-identical edit (431 to 435).
2. A new script had no argparse, so `--help` ran the whole measurement.
3. A second foot-line broke the v1.7 selector: `FOOTLINE.search` takes the **first** match, so `findall` returning `[('1','4'),('1','7')]` meant the live selector read 1.4 while the revision reader read 1.7 — identical bytes, opposite answers.

## Latent, reported not fixed (fixed 2026-09-17, below)

5 notes carry more than 1 foot-line marker, all identical, **0 live victims**. A note quoting an earlier version before its own v1.7 line would be silently exempt from v1.7 enforcement. Needs a ruling.

**Update, 2026-09-17 11:17 BST: fixed on the founder's instruction.** Both readers now use 1 rule, in `bench/tests/test_note_standard_v17_enforced_2026-08-26.py`: a note is held to the highest version declared on any line shaped like a foot-line -- including list markers, HTML tags and comments, headings, and a short date stamp or list number before it -- and a mention in the middle of a sentence never counts. The highest rather than the last, because an independent review showed that a quoted older foot-line placed after the real one would otherwise exempt the note; exemption is silent, while over-enforcement fails loudly. The revision reader now parses `git grep` output as bytes, so its answer no longer depends on git settings such as line numbers, which had made it read 0 of 379. Measured before adoption: the same 61 notes, and the same 29 of 379 at `b593500`. Guard: `bench/tests/test_footline_is_read_from_the_footline_2026-09-17.py`.

## Open

23 commits unpushed. The 2 stashes await founder-in-person deletion. The memory ledger has needed 8 consecutive manual corrections; the 2026-08-17 remedy is unbuilt.

Written under CDSFL note standard v1.7 (26 August 2026).
