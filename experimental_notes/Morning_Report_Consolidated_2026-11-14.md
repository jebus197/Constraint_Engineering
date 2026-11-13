# Morning Report — consolidated

**2026-11-14** · collating every spoken file since `Outstanding_Work_And_Decisions_2026-11-12.txt`

| | |
|---|---|
| task-list entries | **336** |
| open | **47** |
| of those, awaiting a ruling | **20** |
| open and mine to do | **27** |

---

## 1. Resolved in the last 72 hours

**1. The permission predicate read a description of authority as a claim of it.** A Stop gate separates work the session can do from work needing permission. It matched an entry's record of a *general* rule and took that entry off the movable set. The repair that shipped first failed in the quieter direction: `"only he may authorise a paid panel dispatch, and this entry needs one"` returned `False`.

| rule | correct |
|---|---|
| object rule alone (live that morning) | 6 of 9 |
| subject rule alone | 8 of 9 |
| both, naively composed | **7 of 9** — worse than either part |
| narrowed object + subject | **9 of 9** |

Committed at `84fd2253`.

**2. That measurement was corrected before it shipped.** The first version claimed dominance over 8 cases. An ablation showed 1 half of it changed **0 of 8** verdicts and **0 of 181** live entries. The cause was a hole in the corpus, not a redundant rule; the closing case was added afterwards with that declared in the producer.

**3. `qc` silently spent 3 hours.** Documented on 3 surfaces as a documentation sweep. Its waiter was 1800 s against a suite recorded at **11278.43 s**, so `measure_suite` could only ever time out — the "Suite is GREEN" branch has been **unreachable at every size this project has recorded**. Default run: **1815.47 s → 15.47 s, 117.3542x**. The invariant that the derived waiter outlasts the suite is proved for all inputs on 3 routes (z3 `unsat`, SymPy case analysis, live function 0 violations).

**4. A sentence every seat is given was false.** `cdsfl_core_formal.md` tells each seat *"The ordering and the critical level are the DOMAIN's, and both arrive in your directive. Do not invent either."* Measured by AST, the composer made **0** calls to any severity API. **Engineering** was the live hole — a real scale, a real critical level, a default box declaring neither, and a directive forbidding invention. Now fixed; the gate's own threshold is untouched.

**5. 4 bare severity literals** in the live runner bypassed the named constant, 2 feeding the gamma-critical series. All 4 routed through it at the same value; **0 bare executable literals remain**.

**6. `frx`, his fix-request kind.** The prefix worry was refuted — Python backtracks. The real defect: his *first use* was invisible, because the marker's suffix did not admit `frx (`. Widening changes **1 of 895** annotations, and that 1 is his own sentence.

**7. 36 guards were off the commit gate**, breaching a rule the gate states twice in its own prose. 11 were written the same day they were found. Run together, **7 of 368 failed** — the file's own prediction that *"a guard outside the gate drifts in silence"*. All repaired; **0 of 223 now off-gate**.

**8. 16 annotations had no verdict row.** Each now carries a classification, its evidence, and a separately checkable reason.

**9. 3 tickets were live behind done entries.** Deferred entries left alone deliberately — deferred work is postponed, not finished.

---

## 2. Mine, and what remains

**10. Layer 3 exists.** The architecture declared 3 layers and the runner composed 2; the third had **never been a file**. Now `bench/directives/researchers/founder/` in the agreed 3-file form.

**11. The currency check.** Only **1 of 52** encodings carried a confirmation date. The check reports what is due and **does not pretend to reach the publisher**.

**12. Not yet done.** 2 frozen thresholds in modules the runner reaches · **29 of 51** encodings declare no severity scale, including `software_security.txt` · 3 documents state the old cut as current with no supersession marker · the existing Merkle sealing is not yet pointed at the directives tree.

**13. A delivery failure.** 2 spoken files exist only on the Desktop. Separately, 2 documents were rewritten mid-suite-run by a writer still unidentified after 4 refuted explanations.

**14. The report under-counts his decisions.** 3 entries the record marks as his reached the generated file **0 times**; 1 entry titled for 2 things printed detail covering only the second.

---

## 3. His to rule on — recommendation on each

| # | decision | recommendation |
|---|---|---|
| 15 | Widen `local_resource_budget.py`, the hook that stops delegated work launching heavy verification? It is **0.840000 blind** — 126 of 150 real instructions pass, 8 of 10 phrasings invisible | **Widen.** Additive; leaves the working half alone. Untouched so far because its tripwire requires his permission on record |
| 16 | Exposure ceiling for the currency check | **1 per cent**, giving a 14-day backstop. 0 of his 74 session gaps exceeded it |
| 17 | Does model version share the standards record? | **Separate.** It drifts far faster and would reintroduce the hash-noise the split avoids |
| 18 | Adopt real-world applicability as an additional standard? | **Adopt**, worded as he proposed, requiring that invoking it *names* the consequence |
| 19 | Disjunction as the aggregator across incommensurable scales? | **Adopt.** It cannot under-report a critical finding. **The panel answered this and the answer reached no document he has been given** |
| 20 | Authorise severity-record stamping? 269 sites, 139 files, ~3 per cent overhead, against **0 of 14,452** records carrying any scale field | **Authorise.** It is the precondition for answering 19 empirically |
| 21 | Merge the 621 commits to `main`? | Already ruled overdue with its precondition set — **the last action of this batch** |

**22.** The remaining 14 decisions carry forward unchanged and are described in the generated decisions file on his Desktop.

---

## Answers to questions asked

**23. Are ticket identifiers applied consistently now?** **Yes.** 325 of 325 committed entries, 36 of 36 open, and **36 of 36 received theirs in the same commit as the entry** rather than by backfill. The change is a commit-time guard added 2026-11-06 in answer to his own question about mechanising it. 1 gap stated rather than hidden: an issue raised only in a delivered note acquires no identifier by any mechanism.

**24. Can an optimal reminder interval be derived?** **Not from this record.** The obligation has been injected into *every* prompt since 2026-08-30, so the interval has only ever taken 1 value — no variance to fit. What the record does carry: **54 of 361** memory files record an instruction later not followed; median **3** statements; never more than **5**.

**25. A correction to how that was first reported.** The first version said the evidence *contradicted* the context-drift hypothesis. **It does not.** The compliance figure measures behaviour *under* a reminder; there was never an arm without one, so it is a **level, not an effect**. His claim is also narrower than the one treated as refuted — he said explicitly it is neither universal nor predictable — and he holds evidence this session structurally cannot: he observes across sessions and does the refocusing himself.

**26. Is standards versioning straightforward?** **Yes, and most of it existed.** 38 of 52 encodings already carry a version. The missing field is the confirmation date — present in **1**.

**27. Are plain-text files less secure than structured ones?** **No.** Same directory, same permissions. The real argument is machine-checkability: 5 different header shapes across the existing encodings.

---

## What would refute the main claims

**28.** The currency cadence rests on a session pattern measured over a **20-day** window; a 3-week absence would breach the ceiling and that window cannot see such an absence — which is why the backstop exists. The 3-file split's advantage rests on a tamper-alert precision figure; if confirmations were written far less often than measured, the advantage shrinks.

---

Written under CDSFL note standard v1.9.
