"""The approved work list for the build experiment, 2026-08-22.

Founder-approved. Anything a model proposes OUTSIDE this list is RECORDED, NOT
APPLIED. Each task must be closable by a patch plus a test that FAILS at the
parent commit and PASSES with the patch -- including the documentation tasks,
where the test asserts document content (this project already does that for the
memory ledger and the qc checks).
"""

TASKS = [
    {"id": "T01", "title": "Route discrimination failures up the escalation ladder",
     "why": "The ladder already exists and does exactly the right thing, but a falsifier "
            "that fails the discrimination control is CONFIRMED (it fired), and the ladder "
            "only fires on `escalated=True AND not CONFIRMED`, so such a falsifier never "
            "reaches it. Founder ruling 2026-08-22: use the mechanism that exists.",
     "where": "bench/reference_runner_v3.py — `_apply_routing` (~:3279), and the "
              "discrimination outcome constants `DISC_FAILED` / `DISC_PASSED` (~:2176).",
     "done": "A finding whose falsifier returned NO_DISCRIMINATION is routed to a "
             "stronger writer by `_apply_routing`, and a test proves it was NOT before."},

    {"id": "T02", "title": "Feed the discrimination control from the finding's own proposed fix",
     "why": "`run_discrimination_control` is built, has 8 outcomes and 3 self-probes, and "
            "HAS NEVER FIRED ONCE in this project's life, because it is presence-gated on "
            "`entry['corrected_copy']` and nothing supplies one. Measured 2026-08-22: 367 "
            "of 437 archived findings carry a machine-applyable SEARCH/REPLACE fix, so the "
            "missing input already exists.",
     "where": "bench/reference_runner_v3.py — `_apply_discrimination_control` (~:2810), "
              "`_ingest_corrected_copies`, and the call site (~:9127).",
     "done": "When a finding carries a proposed_fix that applies to the target, "
             "`corrected_copy` is populated from it and the control runs. A test proves "
             "the control returns DISCRIMINATES for a falsifier that goes quiet and "
             "NO_DISCRIMINATION for one that does not."},

    {"id": "T03", "title": "Wire the survived-falsification ledger",
     "why": "`SurvivedFalsificationLedger` (bench/evidence.py, built 2026-08-08) has a full "
            "test suite and NOTHING IN THE RUNNER CALLS IT. It records that a claim was "
            "TESTED AND STOOD, closing the gap where a clean run of the zero-plant control "
            "produces an ABSENCE indistinguishable from a dispatch failure or a document "
            "nobody read. Founder ruling 2026-08-22: wire it, do not withdraw it.",
     "where": "bench/evidence.py (the ledger), bench/reference_runner_v3.py (the runner, "
              "which currently never mentions it).",
     "done": "A REFUTED falsifier writes a ledger row during a run; CONFIRMED, ERROR and "
             "UNTOOLABLE write nothing; an un-fed ledger reports NEVER_INVOKED rather than "
             "zero survivals; and the report carries the ledger. A test proves each."},

    {"id": "T04", "title": "A crashed falsifier must not write a terminal status, and must be re-routed",
     "why": "MEASURED 2026-08-22: 4 of 24 findings whose falsifier returned ERROR or "
            "UNTOOLABLE still carry a terminal status; two wrote REFUTED with "
            "verified=False. A falsifier that did not run is not evidence in either "
            "direction. Founder ruling: equipment error counts as UNRESOLVED, escalates to "
            "HIL, and is subject to re-routing.",
     "where": "bench/reference_runner_v3.py — `apply_falsifier_verdicts` (~:2936) and "
              "`_apply_routing`.",
     "done": "An ERROR or UNTOOLABLE verdict can never leave a finding in CLOSED, "
             "CONFIRMED, REFUTED or MERGED; it lands UNRESOLVED, is escalated, and enters "
             "the routing ladder. A test proves the old behaviour is gone."},

    {"id": "T05", "title": "The Bugzilla status vocabulary and a machine-readable catalogue",
     "why": "The design was reviewed by two models on 2026-08-21 and MEASURED 2026-08-22: "
            "`WITHHELD` has 0 references in the live runner and `CORROBORATED` has 1, a "
            "comment. The blocking BEHAVIOUR landed (5 sites record `merge_candidate_of` "
            "and `merge_blocked_reason`); the vocabulary and the catalogue did not. The "
            "founder's requirement is that everything is registered and catalogued so it "
            "can be accessed and understood trivially by both humans and machines.",
     "where": "experimental_notes/Design_Reviews_Bugzilla_And_Perturbation_2026-08-21.md "
              "carries the agreed status table and which transitions are TOOL-ONLY. "
              "bench/reference_runner_v3.py holds the statuses.",
     "done": "CORROBORATED and WITHHELD exist as real statuses with the agreed transition "
             "rules; a catalogue export writes one machine-readable record per finding "
             "carrying status, the evidence that decided it, and the mechanism. A test "
             "proves a model attestation can NEVER write CONFIRMED, CLOSED or MERGED."},

    {"id": "T06", "title": "Shelve the load balancer and mark it in the documentation",
     "why": "Founder ruling 2026-08-22: SHELVE, do not retire -- deleting widens the error "
            "surface, quarantining does not. It has never run outside its own tests, "
            "reports an impossible allocation as a success, and its self-description has "
            "been false for four and a half months.",
     "where": "bench/dm/_load_balancer.py, and wherever project documentation describes it.",
     "done": "The module is clearly marked SHELVED with the date and the reason; the docs "
             "say so; and a test asserts the runner does not call it."},

    {"id": "T07", "title": "`--dry-run` for the null-perturbation control",
     "why": "It writes its output file unconditionally. On 2026-08-22 a read-only reviewer "
            "ran it with `--limit 12` and overwrote the committed 397-row result with a "
            "12-row one. It disclosed this and the file was restored from git.",
     "where": "scripts/null_perturbation_control.py",
     "done": "`--dry-run` computes and prints without writing; a partial run (`--limit`) "
             "refuses to overwrite a larger existing record unless forced. A test proves "
             "the committed record survives a limited run."},

    {"id": "T08", "title": "Move the memory-ledger recount into the save-state path",
     "why": "resources/MEMORY_EXCLUSIONS.md has now needed the same manual correction FIVE "
            "times in a row. The remedy was recorded on 2026-08-17 -- move the recount into "
            "the `sv` path so it stops depending on an author remembering -- and was never "
            "built. The check keeps working; the habit is the defect.",
     "where": "scripts/cdsfl_sv.py (which has 0 references to MEMORY_EXCLUSIONS), "
              "resources/MEMORY_EXCLUSIONS.md, bench/tests/test_recovery_memory_doc_repairs.py.",
     "done": "`sv` recomputes and updates the ledger counts; a test proves it does."},

    {"id": "T09", "title": "Cite the frozen critical-severity pre-registration from the live queue",
     "why": "CRITICAL_SEVERITY_THRESHOLD = 0.7 is described in code as the operational "
            "proxy for a frozen consequence-based rubric at "
            "bench/exp40_baseline/CRITICAL_DEFINITION_PREREG_2026-05-18.md. The live work "
            "queue's top open item is that threshold, and it does not cite the "
            "pre-registration at all -- so an agent could move the float without knowing a "
            "frozen pre-registration governs it. Founder ruling: keep 0.7, make the "
            "pre-registration visible.",
     "where": "experimental_notes/OUTSTANDING_QUEUE_to_BR2.md, resources/RECOVERY.md.",
     "done": "Both name the pre-registration path; a test asserts the citation is present "
             "and that the referenced file exists."},

    {"id": "T10", "title": "Explain the 67 unmatchable fixes and the 30 errored falsifiers",
     "why": "MEASURED 2026-08-22: of 372 archived CONFIRMED falsifiers, 67 could not be "
            "scored because the fix's SEARCH block matches NO stored version of its target, "
            "and 30 errored. A quarter of the population could not be tested at all and "
            "nobody knows why.",
     "where": "scripts/discrimination_control_archive.py and its output at "
              "experimental_notes/data/discrimination_control_archive.json.",
     "done": "A script classifies every one of the 97 by cause with counts, and a test "
             "pins the classification so it cannot silently drift."},

    {"id": "T11", "title": "Confirm or refute the instrument inventory, with tools",
     "why": "Founder ruling 2026-08-22. CC1 produced the inventory; its detection heuristic "
            "already scored the falsifier gate as COMMISSIONED when direct measurement says "
            "it is not, so the 27 remaining 'yes' rows are UNVERIFIED. Tools decide.",
     "where": "scripts/instrument_inventory.py, "
              "experimental_notes/data/instrument_inventory.json.",
     "done": "For each row you check, RUN the component against a known-good and a "
             "known-bad input and report what it did. This task accepts a REPORT rather "
             "than a patch; say plainly which rows you verified and which you could not.",
     "report_only": True},
]
