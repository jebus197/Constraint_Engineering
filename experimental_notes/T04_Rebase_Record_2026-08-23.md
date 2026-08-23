# T04 rebase record: exactly what CC1 changed in Fable's patch

**23 August 2026.** `bench/logs/**` is gitignored by a deliberate rule — raw
per-model responses are preserved in the separate archive, not in the repository —
so the rebased candidate itself is not tracked. This file is the tracked record of
the edit, so the change is auditable without force-adding into an ignored path.

## Why a rebase was needed

Both disputed composition orders gave the identical result: 9 of 10 patches applied,
**T04 conflicting either way**, zero new suite failures. So the CC2/Fable
disagreement about ordering was moot. **Fable was right** that T05's earlier
conflict was manufactured by CC1's composer (no rollback on partial application);
with rollback, T05 applies cleanly in both orders. **CC2 was right** that T04's
conflict is real — and it is with T03, not T05, which is why reordering changed
nothing.

## Two edits, and the second is the interesting one

**(a) Hunk 2, against T03.** T03 inserts `_to_ledger(cid, e, "UNTOOLABLE")` inside
T04's anchor. The union keeps the ledger write **and** widens the demotion from
`== "CONFIRMED"` to `in TERMINAL_STATUSES`. Both reviewers described this rebase
independently.

**(b) Hunk 4, against T01 — which neither reviewer saw**, because T01 was still in
HIL when they composed.

Both patches modify **the same line for the same reason**: an equipment failure
should reach the routing ladder.

- T01 (Fable) widens `"ERROR"` to `("ERROR", "NON_DISCRIMINATING")`
- T04 (Fable) generalises to a named `frozenset EQUIPMENT_FAILURE_VERDICTS = {"ERROR", "UNTOOLABLE"}`

**They are the same design reached independently**, so the union is T04's named set
carrying T01's member: `{"ERROR", "UNTOOLABLE", "NON_DISCRIMINATING"}`. That is
also precisely what CC2 asked for in Q1 — name the constant so the write site and
the read site cannot drift apart on a bare literal.

The comment records the distinction rather than flattening it: **ERROR and
UNTOOLABLE mean the instrument produced no reading; NON_DISCRIMINATING means it
produced a reading that does not depend on the target.** Different faults, same
remedy.

## Two of CC1's own errors on the way, both caught by assertions

- A line-based edit commented out the `T05` entry in the composer's dict, giving a
  `KeyError`. Caught on the first run.
- T04's sixth hunk was reported as failing at parent; it does not. The check was
  comparing a test-file hunk against the runner's source. Caught before the rebase.

Neither reached a verdict about anyone's work.

## The diff, verbatim

```diff
--- T04_rung3 (Fable, original)
+++ T04_REBASED (CC1, 2026-08-23)
@@ -1,3 +1,11 @@
+<!-- REBASED 2026-08-23 by CC1. The ONLY change to Fable's patch is that hunk 2's
+     SEARCH and REPLACE both now carry T03's inserted line
+     `_to_ledger(cid, e, "UNTOOLABLE")`. T03 inserts it at what becomes line 3183,
+     inside T04's anchor. The union keeps the ledger write AND widens the demotion
+     from `== "CONFIRMED"` to `in TERMINAL_STATUSES`. Both reviewers independently
+     described this same rebase. Nothing else in Fable's patch is altered, and the
+     original file is untouched. -->
+
 All three harness conditions verified mechanically in a throwaway worktree at ec95acb: the new test fails 6/11 at the parent, passes 11/11 with the patch, and the full suite runs 3615 passed / 22 skipped. The single failure (`test_falsifier_cannot_read_the_key.py::test_the_guard_rejects_nothing_else_in_the_whole_tracked_archive`) fails at the *unpatched* parent in any worktree too — archived falsifiers carry absolute paths under the real repo root — and passes in the main checkout; my patch's failure delta is zero. Every SEARCH block below was byte-verified unique against the parent commit.
 
 <<<< SEARCH bench/reference_runner_v2.py
@@ -17,7 +25,16 @@
 # given up on WITHOUT verification, which is exactly what these are.
 # MEASURED 2026-08-22: 4 of 24 findings whose falsifier returned ERROR or
 # UNTOOLABLE carried a terminal status; two carried REFUTED, verified=False.
-EQUIPMENT_FAILURE_VERDICTS = frozenset({"ERROR", "UNTOOLABLE"})
+EQUIPMENT_FAILURE_VERDICTS = frozenset(
+    # ERROR and UNTOOLABLE: the instrument produced NO reading.
+    # NON_DISCRIMINATING (added 2026-08-23, merging T01): the instrument
+    # produced a reading that does not depend on the target -- it fired
+    # against a corrected copy. A different fault, the same remedy: a
+    # stronger writer, once, via this ladder. Named here rather than
+    # repeated as a bare literal so the write site and the read site
+    # cannot drift apart.
+    {"ERROR", "UNTOOLABLE", "NON_DISCRIMINATING"}
+)
 TERMINAL_STATUSES = frozenset(
     {"CONFIRMED", "REFUTED", "CLOSED", "MERGED", "DUPLICATE"})
 
@@ -69,6 +86,7 @@
 <<<< SEARCH bench/reference_runner_v2.py
             if is_critical:
                 e["falsifier_verdict"] = "UNTOOLABLE"
+                _to_ledger(cid, e, "UNTOOLABLE")
                 e["escalated"] = True
                 if e.get("status") == "CONFIRMED":
                     registry.resolve(cid, "UNCONFIRMED", round_idx)
@@ -77,6 +95,7 @@
 ==== REPLACE
             if is_critical:
                 e["falsifier_verdict"] = "UNTOOLABLE"
+                _to_ledger(cid, e, "UNTOOLABLE")
                 e["escalated"] = True
                 # T04 (2026-08-22): demote EVERY terminal status, not only
                 # CONFIRMED — the vote pass runs BEFORE the gate and can
@@ -113,7 +132,8 @@
 >>>>
 
 <<<< SEARCH bench/reference_runner_v2.py
-            if e.get("falsifier_verdict") != "ERROR" or e.get("error_routed"):
+            if (e.get("falsifier_verdict") not in ("ERROR", "NON_DISCRIMINATING")
+                    or e.get("error_routed")):
                 continue
 ==== REPLACE
             # T04 (founder ruling 2026-08-22): UNTOOLABLE joins ERROR. Both
```

Written under CDSFL note standard v1.4 (13 August 2026, Rule 24 added 16 August).
