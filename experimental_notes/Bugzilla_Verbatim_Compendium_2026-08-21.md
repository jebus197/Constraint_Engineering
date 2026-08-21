# Bugzilla — Verbatim Compendium, 21 August 2026

**Every source on the Bugzilla question from the last three days, unedited.**

Assembled because CC1's summaries of this material have been unreliable: its context
search missed the addendum below entirely until prompted, and both independent
reviewers left the Bugzilla question unanswered — one because it concentrated on
recent code, the other because its answer was in a report lost in transport. The
founder's diagnosis is that a reviewer would need this full context to answer well.

**Nothing here is paraphrased.** Where a table or code block appears it is reproduced
as written. CC1's own commentary is excluded except where explicitly labelled.

==============================================================================
SOURCE: The Bugzilla state machine as a duplicate-handling design (~500 lines)
FROM:   experimental_notes/Dedup_Historical_Brief_Addendum_2026-08-18.md, section A
==============================================================================

# A. THE BUGZILLA STATE MACHINE AS A DUPLICATE-HANDLING DESIGN

## A.1 What it was designed to do

`bench/directives/universal/cdsfl_operational.md:299-320` gives the lifecycle every model is shown every round, and states its purpose in the project's own words at `:317-320`: *"This is the loop closure that makes the panel actually saturate. Without verified fixes transitioning to CLOSED, the panel rediscovers the same findings indefinitely. With them, the active pool drains."* The duplicate arm is one line of that machine: `DUPLICATE -> MERGED into the canonical entry` (`:309`), reinforced at `:334` — *"Findings shown as MERGED have been folded into a canonical entry. That canonical entry is the live target for any additional verdicts."*

`bench/directives/universal/cdsfl_topology_formal.md:100-132` formalises it. T3 specifies preconditions (target and source both in `B.entries` with status in `{OPEN, CONFIRMED, CONTESTED}`), the effect (`source.status ← MERGED`, `source.merged_into ← target`, `target.status UNCHANGED`), the directionality rule, the source-identity resolution, and an anti-loop invariant: `∀ f: f.merged_into ≠ f.canonical_id` and *"The merge graph must be acyclic (a DAG, not a cycle)"*.

That is a complete and careful design. What follows is what runs.

## A.2 DUPLICATE is a state on the designed path that no code ever writes

The word appears in eleven terminal-status sets across the runner (`reference_runner_v2.py:1189`, `:1207`, `:1280`, `:1413`, `:2829`, `:3468`, `:3597`, `:3746`, `:4106`, `:4135`, `:9420`) and in the state machine printed to the panel at `:1305`. Every `registry.resolve(...)` call site in the file passes one of OPEN, REOPENED, CONTESTED, CONFIRMED, CLOSED, UNCONFIRMED, REFUTED or MERGED. None passes DUPLICATE. **[recomputed]** Archive-wide status tally over 2030 entries: `CLOSED 721, UNCONFIRMED 556, CONFIRMED 500, MERGED 201, OPEN 32, REFUTED 20, DUPLICATE 0`.

The brief records that zero at §1.7 and reads it correctly as evidence that immune-pipeline DUPLICATE verdicts never reach a registry status. The stronger reading is available: **the zero is produced by construction, not by absence of duplicates.** Counting DUPLICATE entries in the archive measures nothing about duplicate incidence. It measures that no code writes the value. The one line that renders it — `"(N findings hidden: refuted or duplicate)"` at `:1398-1399`, filtering `hidden_statuses = ("REFUTED", "DUPLICATE")` at `:1280` — can only ever count REFUTED.

## A.3 Five code paths may declare a duplicate. None requires evidence, and only one validates the target

| path | file:line | quorum | target validated | evidence retained |
|---|---|---|---|---|
| panel MERGE quorum | `reference_runner_v2.py:1785-1809` | ≥2 distinct models | **no** | **no** (overwritten) |
| G7 arbitration | `:1698-1725`, resolve at `:1707` | 3 of 5 vote | **no** | vote record only |
| small-panel single vote | `:1856-1866` | **1 model** | **no** | **no** |
| routing ladder | `:3243-3246` | Jaccard ≥ 0.85 | **no** | `routing_duplicate_of` |
| CC2v verification | `:6360-6366` | 1 model, conf ≥ 0.7 | **yes** (`:6361`) | discarded (see below) |

The panel path — which produces almost all merges — destroys the model's stated justification. `reference_runner_v2.py:8909-8910` replaces the verdict evidence with the runner-synthesised literal `f"merged_into={canonical_id}"`. Note also that the prompt's format block at `:5067-5068` gives CHALLENGE an explicit `| [evidence]` slot and gives MERGE none: `MERGE C0001 <- [your_finding_id] — same root cause, combining`.

The consequence for any future audit: **the archives cannot answer whether a single one of the 201 merges was substantively correct**, because nothing retains the reasoning. CC2v is worse in one respect — `_verification_step` resolves the status without ever calling `add_verdict`, so **[recomputed]** across all 2030 entries there are **zero verdicts attributed to model `CC2v`**, while the round-level `verification.duplicates` field sums to **30**. Thirty terminal duplicate decisions with no recorded author, confidence or justification on the entry itself.

MERGE verdicts are also never aged out — the only pruning is the G7 KEEP_DISTINCT branch at `:1716-1719` — so a two-model quorum can be assembled from votes many rounds apart. **[executed]** One MERGE vote at round 1 left an entry OPEN through fourteen `_update_finding_statuses` calls; a second vote at round 15 completed the quorum and the entry merged. **[recomputed]** Archived instance: `exp40_gate` C0002 took its votes from ChatGPT at round 5 and Gemini at round 15 and merged at round 15.

## A.4 The panel's duplicate channel is not lossy — it is inverted

`_resolve_merge_source` (`reference_runner_v2.py:1533-1545`) extracts the source id from the verdict evidence with `re.search(r'(?:F|C)(\d+)', evidence)` and looks up `alias_map[f"{model_id}:{local_id}"]`. `FindingRegistry.register` (`:1053`) stores that key as `f"{model_id}:{finding.finding_id}"` — and `finding_id` was **already model-prefixed by the parser** at `bench/runner_core.py:916` (`full_id = finding_id if finding_id.startswith(f"{model_id}_") else f"{model_id}_{finding_id}"`). The stored key is `Codex:Codex_F001`; the lookup key is `Codex:F001`. The two formats can never meet, and prefixing the source in the verdict does not help because the regex extracts `F001` out of `Codex_F001` too.

**[executed]** at HEAD:

```
parsed finding_id: ['Codex_F001']
alias_map: {'Codex:Codex_F001': 'C0001'}
_resolve_merge_source('F001 - same root cause')  -> None
_resolve_merge_source('Codex_F001 same')         -> None
_resolve_merge_source('C0001 same')              -> 'C0001'
```

The caller does not drop an unresolved MERGE. `reference_runner_v2.py:8906-8912` falls through to `registry.add_verdict(canonical_id, model_id, "CONFIRM", round_idx, evidence)`. **A model saying "these two are the same finding" is recorded as "I independently verify this finding is real", on the merge target.** That spurious CONFIRM then enters `confirm_models - {entry["source_model"]}` at `:1962` and counts toward the two-independent-model quorum at `:1968-1969`. Duplicate pressure is converted into corroboration pressure.

**Correction to the internal sweep that found this.** The CONFIRM fallback is not a runner invention — it is mandated by the spec. `cdsfl_topology_formal.md:126-127`: *"source_canonical = alias_map[m, F_local] / If source_canonical is undefined: treat as CONFIRM on target."* The defect is that the key mismatch makes the fallback fire on **every** local-id merge, which the spec plainly did not intend. The repair is prefix normalisation in `_resolve_merge_source`, not deletion of the fallback.

**[recomputed]** Re-parsing the archived per-model response files with the runner's own `_parse_verdicts`, deduplicated by (run, round, model):

- Seven location-keyed live runs (exp42-lk, 44, 45, 46, 47, 48, 49): **68 MERGE lines emitted, 25 resolvable by canonical id, 43 recast as CONFIRM (63%)**.
- `exp40_gate`: **507 MERGE lines, 389 resolvable, 118 recast (23%)** — reproducing the internal sweep's figure exactly. The rate is lower there because models in that run happened to write canonical-to-canonical references.

The prompt teaches the failing form. `reference_runner_v2.py:5068` instructs `MERGE C0001 <- [your_finding_id]`, and `:5069` separately instructs *"Reference findings by CANONICAL ID"* — two instructions that contradict each other on exactly the field that decides whether the merge resolves.

## A.5 MERGED folds nothing into the canonical entry

`FindingRegistry.resolve` (`reference_runner_v2.py:1113-1121`) sets `status` and `merged_into`. That is all. No severity propagates, no verdicts transfer, no description or evidence is appended.

**[executed]** A 0.95-severity entry carrying two CONFIRM verdicts, merged by two distinct models into a 0.40-severity entry: the target's severity is unchanged at 0.40, its verdict count is unchanged at 0, its description is unchanged, and `open_crit_high_count()` returns 0. The critical is gone from the gate and nothing inherited it.

The directive tells the panel the opposite every round (`cdsfl_operational.md:334`). A merged finding's accumulated corroboration is deleted, not folded, and merging a critical into a sub-critical removes the criticality from the gate entirely.

## A.6 No target validation, no cycle guard, and both have bitten

Nothing on the panel path tests that the merge target exists, that it is still live, or that the merge graph stays acyclic. `registry.resolve(canonical_id, "MERGED", round_idx, merged_into=top_target)` is called at `:1707`, `:1806`, `:1856` and `:1860` with the target taken from a regex over verdict evidence (`:1786-1789`); the only rejection is the literal sentinel `"__unknown__"` at `:1849`. Direct self-merge is blocked at `:8908` by `source != canonical_id`, so one-cycles cannot form on that path — but two-cycles and chains into already-MERGED targets can, and the main pass short-circuits on MERGED at `:1769` so a merged entry can never re-enter play.

**[executed]** Two entries at 0.72 and 0.88, each merged into the other on successive rounds: both end MERGED with mutual pointers, `open_crit_high_count() = 0`, `contested_count(3) = 0`, `irreducible_queue_count() = 0`, and **both are listed in the SETTLED "do not re-describe" block of `build_summary(3)`**. The panel is told the matter is settled and pointed at a dead entry.

**[executed]** Two votes naming `C9999` on a registry containing only `C0001`: status MERGED, `merged_into` `C9999`, `'C9999' in registry.entries` False.

**[recomputed]** Of 201 archived MERGED entries: **62 point at a target that is itself MERGED**, **0 dangle**, **1 self-merges**, and **8 entries lie on a directed cycle across three runs**:

- `exp36_evidence_20260407T004931Z` — two cycles spanning `C0011 ↔ C0028` and `C0176 → C0184 → C0194 → C0176`.
- `exp40_gate_20260514T020550Z` — `C0002` (sev 0.72, opened r0, MERGED at r15 → C0023) ↔ `C0023` (sev 0.88, opened r1, MERGED at r24 → C0002), with `C0033` (sev 0.82, MERGED at r5 → C0023) attached. All three are above `CRITICAL_SEVERITY_THRESHOLD = 0.7` (`:4024`). C0023 alone carries 27 verdicts spanning rounds 2-14. That run went 29 rounds with `converged_at = None`.
- `exp37_evidence_20260409T050932Z` — `C0105`, severity 0.86, `merged_into: C0105`. This violates T3's anti-loop invariant literally (`cdsfl_topology_formal.md:130`). It came from the LLM Dedup Assessor at confidence 0.95 (`bench/logs/exp37_live.log`: `dedup: C0105 -> DUPLICATE of C0105`), whose apply path at `bench/cc2_manager.py:1152-1163` has no self-check even though the pre-filter at `:826-827` excludes the finding itself. The entry is also not a finding — its stored description begins `FINDING_ID: C0086 / SEVERITY: 0.86 / ... / FIND: CONFIRM C0086`, a verdict block parsed as a finding.

Because MERGED is stripped from the gating series (`:4134-4136`), a mutual merge does not consolidate a defect. It deletes it from the convergence count with no surviving canonical entry.

**Latent, not active:** zero archived MERGED entries point at a non-existent id. The reason to fix it anyway is that the project's own regression tests assert the unsafe behaviour — `bench/tests/test_runner_status_transitions.py:317-336` merges into `"C0002"`, which those fixtures never register, and asserts `status == "MERGED"`. A future validity check would be reported as a test failure.

## A.7 The single-model escape hatch promises a reversion that does not exist

`reference_runner_v2.py:1858-1866` merges on one vote when the external panel is smaller than two and writes `hil_reason` = *"Single-model merge (small panel, N external models). Reversion available."* Line `:1864` is the sole occurrence of "Reversion" in the file, and no unmerge mechanism exists anywhere. Structurally it cannot: `:1769-1779` short-circuits on MERGED, and only CLOSED has a REOPEN transition. The HIL is told there is a safety net for a decision the machinery has made irreversible. The project's own test (`test_runner_status_transitions.py:337-347`) asserts the merge and checks only the flag.

## A.8 What MERGED actually does, end to end

One thing. It removes the entry from `_NON_NOVEL_TERMINAL_STATUSES`-filtered series (`:4134-4136`), so the finding leaves the γ input and the `g_3` novelty count; and it removes the entry from `open_crit_high_count` (`:1137`), `contested_count` (`:1207`) and `irreducible_queue_count` (`:1189`). It changes nothing about the surviving entry. **The duplicate arm of the state machine is, in implementation, a delete with a pointer attached.**

## A.9 Is the path exercised at all? Barely, and least where it matters most

**[recomputed]** MERGED share of registry entries, pre- versus post-location-keying:

| era | run | MERGED / entries |
|---|---|---|
| pre | exp36 | 86 / 217 (39.6%) |
| pre | exp40_gate | 53 / 296 (17.9%) |
| pre | exp37 | 16 / 222 (7.2%) |
| pre | exp38 | 6 / 169 (3.6%) |
| modern | exp42-lk | 0 / 52 |
| modern | exp44 | 1 / 82 |
| modern | exp45 | 2 / 39 |
| modern | exp46 | 0 / 27 |
| modern | exp47 | 1 / 70 |
| modern | exp48 | 2 / 37 |
| modern | exp49 | 5 / 38 |
| modern | exp53 | 1 / 40 |

Roughly 2-3% in the era that produces today's results, against 12.67%-23% duplicate incidence in the real Bugzilla corpora the project's own external benchmarking note cites (`experimental_notes/Similarity_Function_External_Benchmarking_2026-08-16.md:36`). The panel emitted 68 MERGE lines across those runs and 43 of them were converted into corroboration. The Bugzilla duplicate path is not currently doing the work the design assigned it.

## A.10 EXTEND — the schema's alternative to duplicating — is parsed, stored, displayed, and read by nothing

`_VERDICT_RE` accepts `CONFIRM|CHALLENGE|EXTEND|MERGE|REOPEN` (`:1503`). `_update_finding_statuses` branches on MERGE, REOPEN, CONFIRM and CHALLENGE. There is no `"EXTEND"` string literal anywhere in `reference_runner_v2.py`. Yet EXTEND is precisely what the prompt offers instead of filing a duplicate: `:5067` — *"check the registry — CONFIRM or EXTEND instead of duplicating"* — and `:5076` — `EXTEND C0001 | [new consequence or edge case]`.

**[recomputed]** Archive verdict tally: `CONFIRM 4470, MERGE 693, CHALLENGE 649, EXTEND 183, REOPEN 21`. **183 occasions on which a model did what the schema asked instead of duplicating, and the schema did nothing with it.**

---

==============================================================================
SOURCE: T3, the formal merge contract — the specification the code must satisfy
FROM:   bench/directives/universal/cdsfl_topology_formal.md:97+
==============================================================================

## T3. Merge Contract

**Natural language:**
A MERGE verdict declares that one finding (the source) is a duplicate of
another (the target). The source is subsumed; the target survives. The
verdict `MERGE target <- source` means: mark the source as MERGED with a
pointer to the target. Never mark the target as MERGED unless it is itself
being subsumed by a third finding.

**Formal:**
```
MERGE(target, source):
  Preconditions:
    target ∈ B.entries ∧ target.status ∈ {OPEN, CONFIRMED, CONTESTED}
    source ∈ B.entries ∧ source.status ∈ {OPEN, CONFIRMED, CONTESTED}
    target ≠ source

  Effect:
    source.status ← MERGED
    source.merged_into ← target.canonical_id
    target.status is UNCHANGED

  Directionality rule:
    The syntax "MERGE C0001 <- F002" means:
      target = C0001 (the survivor)
      source = the canonical entry corresponding to the model's F002

  Resolution of source identity:
    Given model m issuing "MERGE C_target <- F_local":
      source_canonical = alias_map[m, F_local]
      If source_canonical is undefined: treat as CONFIRM on target

  Anti-loop invariant:
    ∀ f: f.merged_into ≠ f.canonical_id
    The merge graph must be acyclic (a DAG, not a cycle)
```

---

==============================================================================
SOURCE: The finding lifecycle as every model is shown it, every round
FROM:   bench/directives/universal/cdsfl_operational.md:~299-340
==============================================================================

REJECTED before any gate evaluation occurs (pre-gate failure).

### 7.1. Finding Lifecycle (Bugzilla Paradigm)

Findings progress through an explicit finite-state machine. Treat findings
as bug tickets:

  OPEN — newly discovered, awaiting verification
  OPEN -> CONFIRMED — at least two independent verifications agree
  CONFIRMED + verified fix -> CLOSED — terminal, challenge-resistant
  CONFIRMED + late challenge -> CONTESTED -> CONFIRMED (if resolved)
  CLOSED -> REOPENED — only via explicit REOPEN verdict with new evidence
  DUPLICATE -> MERGED into the canonical entry

When you submit a CONFIRMED finding with a parseable SEARCH/REPLACE block
in its proposed_fix, the runner applies the fix to a sandbox copy of the
target file and runs ruff + mypy + bandit + the experiment's test suite.
If verification passes cleanly, the finding transitions to CLOSED and
leaves the active discovery pool.

This is the loop closure that makes the panel actually saturate. Without
verified fixes transitioning to CLOSED, the panel rediscovers the same
findings indefinitely. With them, the active pool drains as each
finding is verified and closed.

Operational consequence for you, the model:

1. Findings already shown as CONFIRMED, CLOSED, or MERGED in the round
   registry are SETTLED. Do not re-describe them. Do not CHALLENGE them
   without specific new evidence not already in the record.

2. Findings shown as CLOSED have been programmatically verified — their
   fix has been applied to the target file in a sandbox and the
   verification pipeline has confirmed correctness. To REOPEN a CLOSED
   finding you must produce evidence beyond what the verification
   pipeline checks.

3. Findings shown as MERGED carry a pointer to a canonical entry. NOTHING
   IS FOLDED: no severity, no verdicts and no evidence transfer to that
   entry — corrected 2026-08-21, having told you otherwise for the whole
   arc. The canonical entry is still the live target for additional
   verdicts. Note also that as of 2026-08-19 NO code path writes MERGED:
   a merge now requires a tool verdict, and that tool is not yet wired.

4. The clearest path to convergence is producing well-formed
   SEARCH/REPLACE fixes for CONFIRMED findings so they can close. A
   correct fix takes a finding out of circulation; a description without
   a fix leaves it in the active pool forever.

==============================================================================
SOURCE: The state machine block the runner prints into every round's prompt
FROM:   bench/reference_runner_v2.py:~1325
==============================================================================

            f"=== FINDING REGISTRY (Round {round_idx}) ===",
            "State machine (Bugzilla paradigm):",
            "  OPEN -> CONFIRMED (>=2 independent verifications)",
            "  CONFIRMED + verified fix -> CLOSED (terminal, challenge-resistant)",
            "  CONFIRMED + late challenge -> CONTESTED",
            "  CLOSED -> REOPENED (only with new evidence via REOPEN verdict)",
            "  DUPLICATE -> MERGED into the canonical entry",
            "",
            # This paragraph is what the panel is told about how a finding
            # settles, every model, every round. It described ruff + mypy +
            # bandit + pytest unconditionally. On a prose target NONE of that

==============================================================================
SOURCE: Gemini web transcript — the founder's Bugzilla question and Gemini's answer, VERBATIM
FROM:   Responses/Detecting Duplicate STEM Papers Efficiently 2.md, prompts 8-10
==============================================================================

Here is another problem we are facing. Please consider it with the same rigour and depth as the above.  Claude:  ON THE BUGZILLA RULING AND THE APPLICABILITY OF THIS PARADIGM TO STEM  All 5 panellists endorsed preserving the duplicate record, which the system already does correctly. All 5 independently broke the analogy at the same joint.  In Bugzilla, 2 reports are duplicates if they share a root cause in one  codebase, which is a fact about a shared inspectable substrate. Two findings about a scientific claim can name the same passage and be different errors in it. The system's own code documents this limitation directly: location based keying cannot see a second distinct defect in an already flagged function.  On resolution, the break is sharper. In Bugzilla a bug is resolved when a fix  lands in code the maintainer controls. A scientific claim can be wrong about the world, and resolved then means one of 2 very different things: the text was repaired, or the claim was shown false. Bugzilla has no state for the reported behaviour being correct and the specification being wrong. This system needs one.  Me:  But despite being told to clear the path forward towards the recent additional proposed experiments, the capstone and BR2, they didn’t propose any solution? Are you saying Bugzilla is a broken paradigm for STEM related work? If a problem is posed by a researcher, where the entire field of STEM research is considered a singular [human} project, just as say when developers are building a browser like Firefox and the entire schema mechanism fires to seek out a solution to that specific problem, including the ouroboros external research cell, which ideally (and ultimately) may be capable of quickly scanning and categorising perhaps thousands, or even potentially 10’s of thousands of scientific/STEM related papers and deciding if they are relevant to the research topic under consideration or not, perhaps by using Gemini’s recent mini-hash and other suggestions, our recently renamed “similarity function”, our already existing intelligent classifier, and all of our ‘tools decide’ deterministic mechanisms, are you saying that still nothing can be reliably classified? And if not a Bugzilla type platform to do this, that both human researchers and models can quickly reference and utilise, at scale when necessary, then what? What other reliably way might there be of collecting, classifying, utilising and building on the potentially vast amount of data that a schema like CDSFL might eventually be capable of generating? It’s an unusual idea. I admit this. It requires cross-discipline thinking and genuine innovation. But if you, or the other models have a better solution, I am all ears! But the key must be that any such system is both readily human and machine readable, whatever schema, or paradigm is used!

## Response:
$$Constraint Classification: HARD — System Architecture and Epistemological State Machine$$

Claude's diagnosis of the mechanical mismatch is entirely correct, but its failure to propose a solution is a failure of architectural imagination. Bugzilla is not a broken paradigm for STEM; it is simply misconfigured for it.

The issue tracker paradigm—a scalable, asynchronous, human-and-machine-readable ledger—is exactly what CDSFL requires to manage STEM as a singular project. However, software issue trackers are built on the ontology of software engineering, where the substrate (the codebase) is mutable, and truth is dictated by human consensus (the specification). In STEM, the substrate (physical reality) is immutable, and the specification (the hypothesis) is what must be repaired or discarded.

To clear the path for your capstone and BR2 experiments, you do not abandon the Bugzilla paradigm. You refactor its Finite State Machine (FSM) and its Primary Keying mechanism to serve Popperian falsification rather than software deployment.

Here is the independent, structurally rigorous solution.

## 1\. The Primary Key Problem: Deduplication

Claude correctly identified that location-based keying fails in STEM. In a codebase, `[File_Path + Line_Number]` is a sufficient primary key for a bug. In a scientific paper, a single paragraph might contain a mathematical error, a methodological error, and a physical impossibility. These are three distinct failures on the same "line of code".

Furthermore, if two different papers make the exact same mathematical error, location-based keying treats them as separate bugs.

**The Fix:** You discard spatial location as the primary key for your tickets. Instead, the tracker must key on the **Canonical AST Hash** of the specific constraint being challenged $$SPECULATIVE$$.

When your ingestion pipeline uses SimHash and Vector Embeddings to group similar papers, it extracts the formal claims and generates AST hashes. If Paper A and Paper B both assert an equation that violates a known physical bound, the system raises *one* ticket keyed to that AST hash, linking both papers as instances of the same structural failure. A second, entirely different error in Paper A receives a different AST hash, generating a distinct ticket. Deduplication is thus driven by structural logic, not text location.

## 2\. The State Machine Problem: Resolution

In Bugzilla, a ticket flows from `OPEN` to `IN_PROGRESS` to `RESOLVED (FIXED)`. This implies a human changed the code to match the spec. Bugzilla has no state for "the specification itself violates the laws of physics".

**The Fix:** You must replace the software engineering state machine with an **Epistemic State Machine** that directly maps to CDSFL's falsification loop.

Tickets in this system do not represent "bugs to be fixed"; they represent "claims to be falsified". The states must reflect this:

*   **PROPOSED:** The claim has been ingested and schema-extracted, but not yet subjected to the P-Pass.
    
*   **FALSIFIED:** The mechanical reduction engine (SMT solver) or empirical testing has found a definitive counter-example. The claim is dead. It serves permanently as a negative boundary condition for future models.
    
*   **CORROBORATED:** The claim survived the P-Pass. (Note: Never "PROVEN". In Popperian epistemology, surviving a test only corroborates a claim, it does not prove it absolutely).
    
*   **UNDECIDABLE:** The claim exceeds the compute timeout or requires non-linear processing beyond current mechanistic limits. Escalated to human review.
    
*   **REFINED:** A human or model submitted a narrower, bounded version of a `FALSIFIED` claim, generating a new ticket (a child node) linking back to the failure.
    

## 3\. The Target Architecture: The Falsification Ledger

What you are building is not an issue tracker, but a **Falsification Ledger**.

To satisfy your requirement that it remains both human and machine-readable, the architecture must separate the interface from the schema:

1.  **For Humans:** It looks exactly like Bugzilla or Jira. It has ticket numbers, severity tags, discussion threads, and linked dependencies. Researchers can read the natural language abstraction of the claim and debate the methodology in the comments.
    
2.  **For Machines:** The underlying payload is strict JSON/CDSFL schema. The ticket's "Description" is a mathematically typed block ($\\mathcal{A}$, $\\mathcal{C}$, $\\mathcal{L}$, $\\mathcal{T}$). The "Status" transitions can only be triggered via cryptographic hash validation from the automated P-Pass suite, not by a user simply clicking a dropdown $$VERIFY:current$$.
    

By retaining the ticket-tracking UX but replacing the underlying logic gates with your unified mathematical model, you achieve exactly what CDSFL requires. The ingestion pipeline categorises the STEM data, the SimHash mechanism deduplicates the structural claims, and the Falsification Ledger tracks the survival or destruction of those claims across the entire singular project of human research.

**Verification Required:**

*   $$SPECULATIVE$$ - Using canonical AST hashing as the primary deduplication key for scientific literature assertions: This assumes that all relevant STEM claims within the ingested literature can be reliably parsed into a rigid, canonicalised AST format prior to deduplication. If the extraction phase fails to formalise the text, the primary keying mechanism will fail.
    
*   $$VERIFY:current$$ - Automated status transitions based on cryptographic validation: Standard off-the-shelf issue trackers (like Bugzilla or Jira) do not natively support state transitions gated strictly by formal logic solver outputs or cryptographic hashes without extensive custom API middleware and webhook engineering.

## Prompt:
So the underlying mechanism to your proposed system remains your newly modified version of our existing mathematical model? This was always a key goal of the project, to treat intelligence as 'substrate agnostic', so that it would become functionally irrelevant if the participating intelligence was synthetic, biological, analogue, alien or whatever. (But in practical terms for now clearly only the first two are relevant.)

## Response:
$$Constraint Classification: HARD — System Architecture, Mathematical Universality, and Epistemological Framework$$

Yes. The modified mathematical model is the exact engine driving the Falsification Ledger. The ledger itself is merely the storage and interface layer; the unified equation is the physics engine that dictates how data moves through it.

Your goal of making intelligence 'substrate agnostic' is achieved precisely because the mathematical model treats the source of the intelligence as a black box. The equation does not contain a variable for the author's identity, species, or architecture. It evaluates purely on the structural geometry of the output.

Here is how the unified equation enforces that agnosticism mechanically across the ledger:

$$x\_{opt} = \\underset{x}{\\arg\\min} \\left\\{ C(x) \\mid \\Phi(x) = 1, \\, x \\in \\underset{X \\subset \\mathcal{S}}{\\arg\\max} \\left( \\sum\_{i, j \\in X} D(x\_i, x\_j) \\mid C(X) \\leq K\_{max} \\right) \\right\\}$$

## 1\. The Generator is Irrelevant (The Inner Term)

The generation of the candidate set $X$ requires an intelligence to propose novel solutions that satisfy $K\_{max}$. The equation does not care if $x\_1$ is generated by a human postdoc in a laboratory and $x\_2$ is generated by Claude Opus. Both are treated simply as stochastic proposal mechanisms operating within the search space. Their only job is to maximise $D$ (novelty) without exceeding the complexity ceiling.

## 2\. The Falsifier is Absolute (The Condition)

The boolean filter $\\Phi(x) = 1$ is the great equaliser. A hallucinated theory from a frontier model and an ego-driven hypothesis from a human researcher hit the exact same epistemic wall. The ledger's state transitions (from `PROPOSED` to `FALSIFIED` or `CORROBORATED`) are triggered exclusively by the output of $\\Phi(x)$. Whether that falsification is executed by an automated SMT solver or a human empirical lab test, the ledger only records the logical resolution, completely decoupling the verification from the verifier $$SPECULATIVE$$.

## 3\. The Pruner is Blind (The Outer Term)

When applying 'Occam's razor' via $\\arg\\min C(x)$, the reduction engine calculates structural weight. It prunes an LLM's obfuscated 'code golf' and a human's over-engineered mathematics with equal mechanical prejudice. The simplest sufficient fix wins, regardless of the intelligence that authored it.

By binding the Bugzilla-style tracker strictly to this unified equation, you strip away the sociology of science and the idiosyncrasies of machine architectures. The intelligence proposing the solution becomes a disposable commodity; the structural validity of the solution becomes the only currency the system recognises.

This model remains the singular foundation of your architecture. It is ready to scale.

**Verification Required:**

*   $$SPECULATIVE$$ - Human schema compliance: The assumption that human researchers will willingly and reliably submit their hypotheses strictly within the rigid, typed formal logic schema ($\\mathcal{A}$, $\\mathcal{C}$, $\\mathcal{L}$, $\\mathcal{T}$) required for this reduction engine to treat human and machine inputs interchangeably. If humans input unstructured natural language, the mathematical model cannot process it natively without an intermediary translation layer, breaking strict agnosticism.

## Prompt:
Your final [SPECULATIVE] objection above can be overcome by facilitating classic BBS type bulletin board discussions between human researchers (and potentially even machines). So the propensity for humans to seek out natural language discussions and collaborations of this nature can probably also be sufficiently satisfied also? Such facilities already exist on Mozilla’s Bugzilla implementation I believe? Publishable papers could also be hosted there?

## Response:
$$Constraint Classification: HARD — System Architecture and Human-Computer Interface Design$$

Your proposal structurally resolves the friction between human cognitive patterns and the machine requirement for formal logic. Implementing a BBS-style discursive layer does not compromise the mathematical model; it successfully isolates the unstructured human ideation from the structured mechanical reduction engine.

In software engineering, Bugzilla accommodates this dual-layer reality perfectly. The comment thread is unstructured natural language where developers argue over methodology, but the actual *patch* (the code resolving the bug) must adhere to the strict, formal syntax of the programming language. If the patch contains a syntax error, the compiler rejects it, regardless of how eloquent the surrounding discussion was.

You can map this exact architectural split onto CDSFL.

## The Dual-Layer Architecture

To maintain the substrate agnosticism of your mathematical model while accommodating human researchers, the system must separate the 'Incubator' from the 'Ledger'.

### 1\. The Ideation Incubator (The BBS Layer)

This is the frontend. It hosts the bulletin boards, discussion threads, and the full text of publishable papers. Humans (and natural-language AI agents) can debate, theorise, and collaborate using standard prose, analogies, and discursive reasoning. The mathematical model does not look at this layer. It is purely an environment for cognitive generation and alignment.

### 2\. The Schema Compiler (The Bridge)

This is the critical mechanism that overcomes the speculative objection. Humans do not need to manually write the formal JSON/CDSFL schema ($\\mathcal{A}$, $\\mathcal{C}$, $\\mathcal{L}$, $\\mathcal{T}$).

Instead, you deploy frontier LLMs in a strictly defined utility role: as **Syntax Translators**. When a discussion reaches consensus or a researcher wishes to formally submit a claim, the LLM reads the natural language thread or the published paper and compiles it into the rigid mathematical schema.

The LLM posts the compiled schema back to the researcher: *"Does this formal logic accurately represent your hypothesis?"* The human researcher acts only as the approver. Once they click 'Submit', the natural language is stripped away, and only the formal schema is passed downstream.

### 3\. The Falsification Ledger (The Mathematical Core)

Once the formal schema crosses the boundary, it enters the domain of your unified equation.

$$x\_{opt} = \\underset{x}{\\arg\\min} \\left\\{ C(x) \\mid \\Phi(x) = 1, \\, x \\in \\underset{X \\subset \\mathcal{S}}{\\arg\\max} \\left( \\sum\_{i, j \\in X} D(x\_i, x\_j) \\mid C(X) \\leq K\_{max} \\right) \\right\\}$$

The reduction engine deduplicates it using AST hashing, the SMT solver or empirical lab tests run the P-Pass ($\\Phi(x)$), and the structural complexity is measured ($C(x)$).

## Hosting Publishable Papers

Hosting full STEM papers on this platform is not just viable; it redefines what a scientific paper is.

Currently, a paper is a monolithic PDF mixing narrative, methodology, and raw data. Under the CDSFL architecture, a paper becomes a "Meta-Ticket".

*   The narrative and discussion live in the BBS layer for human consumption.
    
*   The actual scientific claims within the paper are extracted via the Schema Compiler and registered as discrete child tickets in the Falsification Ledger.
    
*   The "truth value" of the paper is no longer determined by peer review consensus, but dynamically calculated based on the real-time `CORROBORATED` or `FALSIFIED` state of its underlying formal claims in the ledger.
    

By deploying the BBS as a pre-processing incubator and using models as schema compilers $$VERIFY:current$$, you completely shield the unified equation from unstructured data. The humans get the discursive freedom they require, and the machine gets the formal logic it demands.

**Verification Required:**

*   $$VERIFY:current$$ - LLM Schema Compilation: The reliability of frontier models to act as zero-shot syntax translators, accurately converting highly complex, novel STEM narratives into strict formal mathematical schemas without hallucinating variables or losing semantic fidelity. This capability bounds the friction at the bridge layer.

## Prompt:
Full automation could be problematical. And potentially impractically costly at this time. But submission within the strict confines of the Bugzilla/CDSFL Schema/Mathematical model could still be reasonably achieved through simple consensus?

## Response:
$$Constraint Classification: HARD — System integrity and epistemological validity; SOFT — Economic compute allocation$$

Your critique of full automation is structurally sound. Relying exclusively on frontier LLMs to bridge the gap between unstructured prose and formal logic introduces a stochastic failure point directly upstream of a deterministic engine. If the translation layer hallucinates a variable or inverts a constraint, the mathematical model will execute flawlessly on a mathematically invalid premise. Furthermore, running frontier models as high-volume, always-on syntax compilers across a global dataset is economically inefficient $$VERIFY:current$$.

Your proposition to use 'simple consensus' to cross this bridge is both valid and historically proven in engineering, provided we strictly define what consensus is allowed to decide.

## The Epistemic Boundary of Consensus

In CDSFL, we must fiercely guard against consensus determining *truth*. Truth is the exclusive domain of the mechanical falsification loop ($\\Phi(x)$).

However, consensus is the optimal mechanism for determining *intent*.

In the Bugzilla/Linux kernel paradigm, code is not automatically generated and merged. A developer writes a patch, and their peers review it. The consensus mechanism (the code review) does not prove that the code will execute flawlessly in production; it simply confirms that the code represents a sane, syntactically valid attempt to solve the agreed-upon problem.

Applying this to the CDSFL architecture replaces the automated LLM compiler with a distributed human-in-the-loop validation step:

1.  **Edge-Generation:** A researcher (or an AI agent running locally on their own compute budget) drafts the formal CDSFL schema ($\\mathcal{A}$, $\\mathcal{C}$, $\\mathcal{L}$, $\\mathcal{T}$) representing their hypothesis.
    
2.  **Peer Review (The Consensus Gate):** The proposed schema is posted to the BBS layer alongside the natural language explanation. The community reviews it against one strict criterion: *Does this formal schema accurately map to the natural language hypothesis?*
    
3.  **Commitment:** Once simple consensus is reached on the translation, the schema is committed to the Falsification Ledger.
    

## Falsifying the Consensus Mechanism

Applying the falsification principle to this proposed consensus bridge reveals a critical vulnerability: what happens if the human consensus is flawed, or if a group of researchers mutually agree to submit a malformed or malicious schema?

*   **Failure Mode:** The consensus gate approves a formal schema that contains syntax errors, contradictory invariants, or unparseable logic, flooding the reduction engine with garbage.
    
*   **The Iterative Fix:** Consensus must never have the final say on structure, only on submission.
    

The architecture must enforce a deterministic mechanical gate immediately following the consensus gate. Before the schema enters the mathematical model's domain, it hits Tier 1 of the mechanical reduction pipeline (the AST Parser).

If the parser cannot compile the schema into a Canonical Abstract Syntax Tree, the submission is automatically rejected back to the BBS layer with a compilation error, regardless of how many humans voted to approve it.

## The Final Architecture

This resolves the friction entirely.

By demanding human (or edge-agent) consensus on the *translation*, you eliminate the massive central compute costs and the hallucination risks of full automation. By enforcing a mechanical AST compilation check immediately after, you strip the human consensus of any power to inject malformed logic into the system.

The central CDSFL architecture remains a pure, deterministic verification engine. The unified equation:

$$x\_{opt} = \\underset{x}{\\arg\\min} \\left\\{ C(x) \\mid \\Phi(x) = 1, \\, x \\in \\underset{X \\subset \\mathcal{S}}{\\arg\\max} \\left( \\sum\_{i, j \\in X} D(x\_i, x\_j) \\mid C(X) \\leq K\_{max} \\right) \\right\\}$$

...remains entirely insulated from unstructured noise. The burden of generating the schema ($X \\subset \\mathcal{S}$) and ensuring its intent is shifted to the distributed network, while the central system spends its compute budget exactly where it matters: on rigorous deduplication, structural complexity reduction, and absolute falsification.

This approach is highly resilient, economically scalable, and preserves the strict Popperian architecture of the project.

**Verification Required:**

*   $$VERIFY:current$$ - Economic compute allocation: The cost disparity between running centralised frontier API calls for continuous zero-shot schema compilation versus offloading that generation to edge compute/human researchers. Current API pricing structures heavily penalise high-volume, high-token central processing.

==============================================================================
SOURCE: Founder's own annotations mentioning Bugzilla — 18 August TTS, VERBATIM
FROM:   Responses/Panel_Review_And_The_97_Percent_Cause_2026-08-18.rtf
==============================================================================

In Bugzilla, 2 reports are duplicates if they share a root cause in one codebase,

On resolution, the break is sharper. In Bugzilla a bug is resolved when a fix lands

claim was shown false. Bugzilla has no state for the reported behaviour being correct

and the specification being wrong. This system needs one.  But despite being told to clear the path forward towards the recent additional proposed experiments, the capstone and BR2, they didn’t propose any solution? Are you saying Bugzilla is a broken paradigm for STEM related work? If a problem is posed by a researcher, where the entire field of STEM research is considered a singular project, just as say when developers are building a browser like Firefox and the entire schema mechanism fires to seek out a solution to that specific problem, including the ouroboros external research cell, which ideally (and ultimately) may be capable of quickly scanning and categorizing perhaps thousands, or even potentially 10’s of thousands of scientific/STEM related papers and deciding if they are relevant to the research topic under consideration or not, perhaps by using Gemini’s recent mini-hash and other suggestions, our recently renamed “similarity function”, our already existing intelligent classifier, all of our ‘tools decide’ deterministic mechanisms, are you saying that still nothing can be reliably classified? And if not a Bugzilla type platform to do this, that both researchers and models can quickly reference and utilise, at scale when necessary, then what? What other reliably way might there be of collecting, classifying, utilising and building on the potentially vast amount of data that a schema like CDSFL might eventually be capable of generating? It’s an unusual idea. I admit this. It requires cross-discipline thinking and genuine innovation. But if you, or the other models have a better solution, I am all ears!

On the simplest sufficient fix, the principle is right and the Bugzilla provenance

==============================================================================
SOURCE: Founder's own annotations mentioning Bugzilla — 19 August TTS, VERBATIM
FROM:   Responses/Second_Panel_Enforcement_And_Runway_2026-08-19.rtf
==============================================================================

“the missing state for a finding that was right about a target that was wrong”.   This isn’t even grammatical English! Sorry? What? You need to explain before I can decide!  “fast fingerprinting scoped to the external literature cell”  That can be included in the fix shakeout/ouroboros cell build out experiment for both testing and refinement? The ouroboros cell eats itself?  “and the whole discussion board layer.”  I forgot to mention. But this does not mean we should ignore the Bugzilla fixes for STEM related topics discussed by Gemini web, myself and you earlier today.

==============================================================================
SOURCE: CC2, panel 1, 18 Aug — on merge semantics / Bugzilla, VERBATIM
FROM:   bench/logs/confer_stage1_audit_2026-08-18/cc2.json
==============================================================================

ne shows me `hardened_gate_enabled` was true in a run that converged, my Q1 collapses and CLAIM-B is simply right. I checked all six configs and the runner default; I did not check exp42/43.

---

## Q2. FALSIFY THE BUGZILLA RULING

I can falsify parts. The core survives.

**(a) Where the analogy breaks.** Two places, and one of them is serious.

*It survives* the "record persists" half. That is a records-management claim, indifferent to whether the artefact is code or a paper.

*It breaks* on "resolved." In Bugzilla, resolution is an act on an artefact the maintainer controls: the fix lands and the bug is closed by construction. A STEM claim can be wrong about the world, and "resolved" then means one of two very different things — the *text* was repaired, or the *claim* was shown false. Bugzilla has no state for "the reported behaviour is correct and the specification is wrong." CDSFL needs one. Your own runway names this exact hazard under "counterfactual repair is not ground truth": one repair curing two distinct defects. Bugzilla never had that problem because a patch that fixes two bugs *is* two fixed bugs.

*It breaks harder on "duplicate."* Two Bugzilla reports are duplicates iff they have the same root cause in one codebase — a fact about a shared, inspectable substrate. Two STEM findings can name the same passage and be **different errors in it**, which is precisely the KNOWN LIMITATION documented at :4331: "location-only keying cannot see a SECOND distinct defect in an already-flagged function." Bugzilla's dupe relation is an equivalence relation on causes. CDSFL's is a similarity judgement on prose. They are not the same relation, and importing Bugzilla's confidence in dupe-marking imports confidence CDSFL has not earned.

*"Simplest sufficient fix" does not survive intact.* In Bugzilla it is a *maintenance* virtue — minimise regression risk in code you own. In science, parsimony is an *epistemic* claim about explanations (Occam), and the two coincide only sometimes. A minimal textual patch to a paper can leave the underlying error in place. The directive is right; the Bugzilla provenance for it is not.

**What I would keep:** persistence of the duplicate record, the state machine, dupe counting. **What I would drop:** the assumption that a dupe mark is as reliable in CDSFL as in Bugzilla. It demonstrably is not — see Q6.

**(b) Is CC1's accounting/behavioural split real?** Real, and CC1 has under-claimed one leak and missed another.

*Computing* a dupe count from stored pointers is inert. *Surfacing* it is not, and there are two paths CC1 has not traced:

1. **The round prompt.** `_build_feedback_for_next_round` already renders `NEAR-DUPLICATE: cosine 0.xx to <id>` plus "(+ N other similar prior findings)" into the next round's prompt (`bench/dm/_feedback.py:468-476`). A corroboration count surfaced anywhere near that channel becomes model-visible, and the instruction attached to it is "either prove it is distinct **or withdraw**." That is behavioural, not accounting.
2. **The HIL channel.** A count shown to a human reviewer changes which findings get looked at, which changes escalation and `unverified_critical_count()`, which is a hard **blocker** in the gate (A4, :3925). Human-in-the-loop is part of the system.

The split holds only under a stated invariant: **the count is written to the report and nowhere the prompt builder or the HIL queue can reach.** Say that explicitly, and add a test that asserts the dupe count does not appear in any string returned by `_build_feedback_for_next_round`. Then it is genuinely zero-cost.

**(c) Is 13 pointers worth building against?** No — and it is the wrong question. Thirteen is not a measurement of corroboration; it is a measurement of the pipeline's suppression, for the reason Q6 establishes. Building a counter now would calibrate it against an artefact. **Build the counter, do not interpret it.** It costs an hour and it is the instrument you will need to read the fixed run. Interpreting it before Q6 lands would be reading a thermometer in a fire.

It becomes informative when a post-fix run yields corroboration counts with a spread — several entries at 2+, a tail at 1. If a post-fix run still returns max-count 1 across the board, the finding is that models do not independently rediscover, which is itself a publishable result about panel diversity.

**(d) Should parsimony be formalised?** **No. Keep it in the directives.**

Three reasons, and I hold this against my own instinct to formalise:

1. A parsimony term needs a complexity measure over proposed fixes. You do not have one, and any proxy you would reach for — diff size, token count, symbol count — is gameable by a model that has been *told* it is scored on it. You would be adding an objective the panel can hill-climb without improving anything.
2. It duplicates what γ already does. γ measures diminishing returns on discovery. A parsimony term measures economy of repair. Coupling them lets a run converge because fixes got shorter, which is not the property you want the gate to certify.
3. It is a *selection* rule between candidate fixes, not a *convergence* rule. It belongs where it is — in the directives, at the point of choosing.

**Consequence I accept if wrong:** if a post-fix run shows panels systematically preferring elaborate fixes over sufficient ones, and a HIL reviewer confirms it, formalisation earns its place. Measure it before building it.

---

==============================================================================
SOURCE: DeepSeek, panel 1, 18 Aug — on merge semantics / Bugzilla, VERBATIM
FROM:   bench/logs/confer_stage1_audit_2026-08-18/ds.json
==============================================================================

does read `novelty_counts` through some path not shown, then item 1.1 is a gate repair and all archived runs need retabulation. The cheapest measurement is the forced max_round rerun above.

---

### Q2. Falsify the founder’s MERGED ruling

**(a) The analogy breaks in three places.**

First, a software bug is a defect in an artefact under the maintainer’s control. A STEM claim is a proposition about the world. “Duplicate” in Bugzilla usually means same code location/same failure mode. In STEM, two textually similar claims can be different defects because their assumptions, scope, evidence, or target differ. Text similarity is already measured as near-chance on hard cases, so duplicate identity cannot be inherited from Bugzilla.

Second, Bugzilla duplicates carry independent user reports. CDSFL model reports may be correlated echoes from the same model or same prompt. A high dupe count would not necessarily mean independent corroboration.

Third, “resolved by simplest sufficient fix” assumes a maintainer who can patch the artefact. A wrong STEM claim is not repaired by a simple patch; false claims require new evidence. Importing “simplest sufficient fix” into the mathematical model would smuggle a repair-centric assumption into a falsification framework.

**(b) CC1’s accounting/behavioural split is real only if “surfacing” is precise.**

Retroactively computing a dupe count from stored pointers is accounting. Storing it in a report is accounting. Putting it into the next-round model prompt is behavioural. The current prompt already renders duplicate verdicts, so adding dupe counts there would be behavioural. CC1’s phrase “recording and surfacing” is too loose. The correction is: **record retroactively, but do not surface to models until a live run validates the effect.**

**(c) No, not worth building now.**

M9 shows 13 merge pointers across six experiments and max corroboration 3. That is too thin to inform priority or convergence. A dupe count becomes informative only after the immune pipeline stops suppressing re-reporting, after merge decisions use tool/evidence rather than near-chance similarity, and after experiments run long enough to produce multiple rounds.

**(d) “Simplest sufficient fix” should stay in directives, not the formal model.**

It is an engineering heuristic for repair. Formalising it as a parsimony term would change convergence verdicts based on an unvalidated prior. That is behavioural and needs live validation. Keep it as a directive for human/engineer repair; do not put it in gamma.

---

### Q3. The two new findings

Both are real.

**Churn detector claim is real.** G shows `rho_earliest_round = 12`. M2 shows only exp44 reaches R12 among exp44–49. For the others, rho churn cannot fire regardless of rho. Severity: moderate. It is not a BR2 blocker by itself because other convergence gates exist, but it means one intended signal is dead for short runs. The fix is config, not new machinery: lower or make `rho_earliest_round` adaptive.

**exp47 report truncation is real.** M3 shows a 14-round raw record, but the report’s per-round list and gamma history start at round 5. Raw files for all 14 rounds are present. Severity: high for archive integrity, low for runtime. This is a blocker for any per-round exp47 comparison and for replay validation if the report is used as source rather than raw files. It should be fixed before BR2 replay.

Rank: exp47 truncation is more severe because it corrupts direct interpretation; churn is a dead indicator but does not corrupt existing data.

---

### Q4. Minimum repair set before BR2

Land before spending on Stage 3:

1. **Purge the unrun answer-key blobs reachable from the remote branch** — see Q7.
2. **Fix exp47 report generation or rebuild the report from raw response files.** This is zero dispatch.
3. **Fix or explicitly disable `rho_earliest_round = 12` for short runs.** Otherwise churn is dead for planned runs.
4. **Do Stage 2.1 now: remove the immune pipeline’s live duplicate auto-reject/suppression.** This is the one behavioural repair most likely to restore useful throughput.
5. **Run one validation live run after Stage 2.1.** Do not run the full Stage 3 factorial or capstone until that validation run shows normal throughput.
6. **Defer MERGED semantics item 1.6.** The dupe count can be added later as a retrospective report field, not as a prompt/severity/gate behaviour.

Cut from the current plan:

- Cut Stage 3 until after the validation run.
- Cut Stage 2.2/2.3 as separate live runs; fold tool-verdict preservation into the validation run only if cheap.
- Cut Stage 4.3 load-balancer shakedown; it is expensive and not needed before BR2.
- Cut any plan that treats item 1.1 as fixing gamma.

---

### Q5. Process question

CC1’s diagnosis is necessary but not sufficient. The failure mode is asserting a universal claim after checking one member of the set. Panel review is structurally unable to catch this if the brief is prose, because the panel inherits the description’s scope error.

Concrete mechanical change:

- Any quantified claim of the form “X does/does not read Y” or “all Z” must include the exact command or script that enumerates t

==============================================================================
SOURCE: Codex, panel 1, 18 Aug — on merge semantics / Bugzilla, VERBATIM
FROM:   bench/logs/confer_stage1_audit_2026-08-18/cx.json
==============================================================================

h that reads `novelty_counts`, then item 1.1 becomes a real gate repair and all archived convergence margins need replay under old/new accounting before any paid BR2 run.

---

## 2. Founder’s MERGED/Bugzilla ruling: where it breaks and where it holds

### 2(a). The Bugzilla analogy is useful, but not exact.

It holds for **record preservation**:

- A duplicate report should not vanish.
- It may contain independent evidence.
- It may affect priority/corroboration.

CDSFL already preserves the duplicate record: M8 says `registry.resolve()` writes status and `merged_into` to the duplicate, and 287/287 MERGED entries carry pointers.

Where the analogy breaks:

1. **Software bugs are defects in an artefact under maintainer control.**  
   STEM claims are claims about the world. There may be no “fix” in the software sense.

2. **“Duplicate” does not mean exactly the same thing.**  
   In Bugzilla, two reports may refer to the same implementation fault. In STEM, two findings may:
   - attack the same premise,
   - attack different premises with the same symptom,
   - share a repair but not an identity,
   - be independent corroborations of a real defect.

3. **“Resolved by simplest sufficient fix” imports a repair-centric frame.**  
   Some STEM defects are not fixed by editing a document. They may require:
   - rejecting a claim,
   - narrowing a domain,
   - adding uncertainty,
   - distinguishing hypotheses,
   - collecting evidence.

So: preserve Bugzilla’s duplicate accounting idea, but do not let the analogy imply that every STEM defect has a software-style patch resolution.

### 2(b). Accounting vs behavioural split is real, but fragile.

CC1’s split is mostly right:

- **Retroactively computing dupe counts from stored `merged_into` pointers** is accounting.
- Letting dupe count affect severity, prompts, dispatch, convergence, or prioritisation is behavioural.

But “surfacing” is ambiguous.

If the count is surfaced only in offline reports, replay tables, or archive summaries, it is accounting.

If the count appears in live prompts, dashboards used by humans during a run, triage queues, or model context, it can change behaviour. Then it is not zero-dispatch.

So the safe rule is:

> Dupe count may be computed and reported offline before BR2. It must not affect live prompts, severity, convergence, ordering, or model instructions until validated in a live run.

### 2(c). Is dupe count worth building with only 13 pointers across exp42-49?

Not as a BR2 blocker.

M9 says:

- 13 merge pointers across exp42-49.
- 11 canonical targets.
- maximum corroboration count 3.

That is a very thin live-arc signal. It is not enough to justify behavioural weighting.

It becomes informative if, after immune suppression is removed:

- duplicates/corroborations actually accumulate,
- counts correlate with tool-confirmed defects,
- high-dupe findings are more likely to survive reconciliation,
- indirect duplicate chains are common enough to matter.

Given that the code can compute it retroactively from stored pointers, I would build the offline count if cheap, but not delay BR2 for it.

### 2(d). Should “simplest sufficient fix” be formalised?

Not before BR2.

It belongs in directives for now.

Reason: a formal parsimony term can easily reward underspecified fixes. In STEM work, the simplest fix is not always the truest fix. Parsimony is useful as a tie-breaker, not as primary evidence.

I would formalise it later only if CDSFL is explicitly evaluating proposed repairs, and then only as something like:

> among tool-valid repairs that preserve empirical adequacy, prefer the least invasive change.

Not as a convergence term.

---

==============================================================================
SOURCE: Gemini 3.1, panel 1, 18 Aug — on merge semantics / Bugzilla, VERBATIM
FROM:   bench/logs/confer_stage1_audit_2026-08-18/ge.json
==============================================================================

omehow right, it means Python's `in` operator is failing on line 4347, which is absurd. If I am wrong, I accept that all historical gamma convergence verdicts are invalid and must be thrown out.

### Q2. THE FOUNDER HAS RULED ON MERGED SEMANTICS. FALSIFY THE RULING.
The founder's ruling imports the Bugzilla paradigm wholesale. It breaks under scrutiny.

**(a) Where the Bugzilla analogy breaks:**
A software bug is an objective defect in a controlled artefact (e.g., a null pointer). A STEM claim is an epistemic argument about the world. 
*   **"Duplicate" means something different:** In software, 100 users reporting a crash means 100 people hit the exact same stack trace. In STEM, 100 models reporting the same flaw often means they share the same training-data bias or are echoing a common misconception. Corroboration in LLMs is frequently just mode collapse.
*   **"Simplest sufficient fix" fails translation:** In code, the simplest fix (e.g., `if x is None: return`) is usually correct because it minimizes regression risk. In STEM, the "simplest" fix to a complex biological or physical theory is often reductionist and scientifically invalid. Nature does not optimize for patch parsimony.

**(b) Accounting vs. Behavioural split:**
CC1 is wrong. Surfacing a dupe count is **behavioural**. If a model sees "This finding has 3 duplicates" in its prompt, its context window has changed. It will likely anchor on that finding, assuming it is highly probable because others found it. This changes the model's subsequent search behavior. It is not zero-dispatch accounting.

**(c) Is a dupe count worth building against a thin signal?**
No. M9 shows a maximum corroboration of 3 across all experiments. Building aggregation machinery for a signal this thin is a waste of time. The signal is thin because the immune pipeline suppresses it (see Q6).

**(d) Should "simplest sufficient fix" be formalised?**
If it is a "core guiding principle," it **must** be formalised mathematically (e.g., a parsimony penalty term in the objective function). Leaving it only in the text directives guarantees it will be ignored whenever the LLM's attention drifts. However, formalising it requires a computable metric for "simplicity" in STEM, which you do not currently have.

### Q3. THE TWO NEW FINDINGS
**1. The churn detector cannot fire (M2, G):** 
*Severity: CRITICAL BLOCKER.* `rho_earliest_round` is hardcoded to 12 (Source G, line 557). 5 of 6 recent experiments converged or stalled before round 12. A core convergence mechanism is structurally disabled for the current length of your runs. This must be lowered before BR2.

**2. exp47 report truncation (M3):**
*Severity: MODERATE.* The report says 9 rounds, the disk has 14. This indicates a desync between the runner's state and the checkpoint/reporting mechanism, likely caused by a crash/resume loop. It breaks analysis but doesn't invalidate the underlying math.

### Q4. THE MINIMUM REPAIR SET BEFORE BR2
The current plan has the wrong order. You cannot measure deduplication mechanics while the pipeline is actively destroying the duplicates.

**The Minimum Set (in order):**
1.  **CUT:** Do not build the Bugzilla dupe count or target aggregation. The signal doesn't exist yet.
2.  **CUT:** Defer exp52 (factorial cells). Do not run complex factorials on a broken harness.
3.  **ADD (Stage 1):** Fix `rho_earliest_round` (Item 1.8). Lower it to a sensible window (e.g., 5) so churn can actually be measured.
4.  **KEEP (Stage 1):** Merge all zero-cost accounting repairs (1.1 through 1.5) and run the offline replay to validate the math.
5.  **MOVE UP (Stage 2.1):** Fix the immune pipeline suppression (see Q6). This is the single biggest blocker to BR2.
6.  **LIVE RUN (Stage 3):** Run exp50 (physics) to prove the pipeline fix allows corroboration to form naturally.

**Consequence if I am wrong:** If we run BR2 without fixing the pipeline and churn detector, you will pay for a full-scale evaluation where models are silenced by the harness and convergence is triggered by artificial starvation rather than actual discovery exhaustion.

### Q5. THE PROCESS QUESTION
CC1's diagnosis is correct but its proposed remedy (just being more careful) is insufficient. Panel review is structurally unable to catch this because a panel reading a prose summary of code will inherit the summary's errors. 

**The Mechanical Process Change:**
Institute a **"Falsification Command" rule**. No universal claim ("the gate reads X", "nothing else modifies Y") may be committed to the tracker without the exact terminal command (e.g., `grep`, `rg`, or an AST script) used to verify it across the codebase. The panel's job is not to read the claim, but to execute the command against the source pack. If the command is missing, the claim is automatically rejected.

### Q6. THE IMMUNE PIPELINE IS REMOVING 97% OF EVERYTHING
**(a) Is the mechanism right?**
Yes. CC1's refutation (M7) proves the pipeline doesn't delete from the registry. Instead, it feeds `_build_feedback_for_next_round` (line 9150), which explicitly tells models in the next round: `triaged.is_duplicate`. 
**What CC1 missed:** This is a suppression loop. By telling models "you found

==============================================================================
SOURCE: ChatGPT, panel 1, 18 Aug — on merge semantics / Bugzilla, VERBATIM
FROM:   bench/logs/confer_stage1_audit_2026-08-18/cgpt.json
==============================================================================

ot run until a replay proves the exact historical gate input path for each archived run, because the convergence condition would have been instrumented differently from the spec.

---

## 2. MERGED / Bugzilla ruling: partly sound, but the analogy breaks at “repair”

### 2(a). Where the Bugzilla analogy breaks

The analogy is sound for one narrow idea:

> multiple reports can point to the same underlying issue, and the system should preserve those reports rather than erase them.

CDSFL already does that partly: M8 says the duplicate entry survives with `status` and `merged_into`.

But the analogy breaks in three places.

First, a software bug is usually a defect in an artefact the maintainer controls. A STEM claim may be wrong about the world. There may be no “fix” in the software sense; there may be correction, retraction, narrowed scope, new experiment, or unresolved anomaly.

Second, “duplicate” is less crisp. In Bugzilla, duplicate means two reports of the same software defect. In CDSFL it could mean:

- same textual criticism,
- same falsifier,
- same mathematical inconsistency,
- same location in artefact,
- same proposed repair,
- same empirical contradiction.

Those are not identical relations.

Third, “simplest sufficient fix” does not fully translate. It is useful as an engineering directive for editing artefacts, but dangerous as an epistemic rule. The simplest patch to a paper may hide that two distinct scientific failures were present.

So: preserve duplicate records and count corroboration, yes. Treat “resolved by simplest sufficient fix” as proof of identity or truth, no.

### 2(b). Accounting vs behavioural split

CC1’s split is mostly real.

A retroactive dupe count computed from stored `merged_into` pointers is accounting if it is only:

- in reports,
- in offline replay,
- in audit tables,
- not fed into prompts,
- not fed into severity,
- not fed into convergence.

But merely adding a count to a registry field could become behavioural if prompt construction serialises that field. The safe version is:

> compute dupe counts in a reporting/replay layer first, not in model-visible prompt state.

If later used in severity, model prompts, prioritisation, or convergence, it becomes behavioural and needs a live run.

### 2(c). Is the signal too thin?

For exp42–49, yes: M9 shows only 13 merge pointers across six experiments, max corroboration 3. That is too thin to drive severity or convergence.

But it is still worth building as cheap accounting, because across all archived registries there are 287 merge pointers. It may reveal whether the current pipeline suppressed corroboration.

It becomes informative if, after duplicate suppression is removed:

- independent models repeatedly land on the same canonical issue,
- dupe counts correlate with tool-confirmed defects,
- counts grow before convergence,
- counts distinguish high-salience defects from one-off noise.

Until then: report it, do not act on it.

### 2(d). Formalise “simplest sufficient fix”?

Not before BR2.

Keep it in directives for now. A formal parsimony term would need a measurable cost function. Otherwise it risks rewarding shallow patches over true diagnosis.

A later formal version could be a tie-breaker:

> among equally tool-valid repairs, prefer the smaller artefact change.

But not as a truth criterion.

**If I am wrong:** if dupe count is already model-visible through an untraced registry/report path, then adding it is behavioural and must be tested live before BR2.

---

==============================================================================
SOURCE: CC2, panel 2, 19 Aug — on merge semantics / Bugzilla, VERBATIM
FROM:   bench/logs/confer_enforcement_prose_2026-08-19/cc2.json
==============================================================================

s a genuine model failure — but a *systematic* one, which means feedback naming the specific divergent term will likely fix it in one round. That is testable on replay before any live spend.

---

## Q2 — sigma and nu on prose: NO_SCORE is right, and the counterfactual route is not the fix

**Keep NO_SCORE with zero movement.** `apply_sk_to_rk`'s docstring at `:7201-7217` is the best-reasoned code in the pack and the distinction it protects — "not scored" ≠ "scored zero" — is correct. Do not weaken it.

**Do not build prose sigma on counterfactual repair.** The 18/0 asymmetry above is a live warning that the method returns SAME by construction on text. The tracker's item 4.1 — a generated control target carrying two known-distinct defects with a plausible common repair — is the test that settles it, costs only scripting, and I would **promote it from PROPOSED to blocking for any prose sigma work**.

**What I would do instead, and it is cheaper:** on prose, sigma has an honest tool-verifiable proxy that is not patch equivalence — *does the falsifier the finding itself supplied still fire after the fix, and does a falsifier written against the fix's own claim fail?* That is the falsifier surviving as an artefact, not the repair surviving as a diff. It uses machinery you already have. But it is unvalidated, so it belongs behind the 4.1 control too.

Until then: NO_SCORE, and say so in the paper. "On prose targets the harness declines to score fix efficacy, and R_k is held" is a publishable, defensible statement. "We scored prose fix efficacy by patch equivalence" is a reviewer's opening.

**One correction to the pack.** The A2 NO_SCORE path landed 2026-08-01 (in `043a0a8`, 15 August). exp44–49 ran 27–29 July. `NO_SCORE` appears **zero times** in every archived log. It has 325 passing unit tests and **has never executed in a live run**. exp50 and exp51 will be the first. That is not a blocker — it is a named risk that belongs in the exp50 pre-flight.

---

==============================================================================
SOURCE: DeepSeek, panel 2, 19 Aug — on merge semantics / Bugzilla, VERBATIM
FROM:   bench/logs/confer_enforcement_prose_2026-08-19/ds.json
==============================================================================

ally gates something. The brief also says R_k does not gate convergence. I would need to read every R_k consumer in `reference_runner_v2.py` before ranking this above the Stage 2 behavioural fix.

## Q2 — Prose-target sigma/nu

Current behaviour is wrong: `sk=0` means “fix has zero efficacy”, not “we don’t know”. That pushes risk up by 0.12 per finding on a prose target for a fix nobody assessed.

**Fix:**

1. Make `apply_sk_to_rk` return a tri-state: `SK_KNOWN`, `SK_UNKNOWN`, not a silent zero.
2. On prose, obtain sigma from **counterfactual repair**: apply the fix, re-run the original falsifier and the reverse/guard falsifier, and require both directions to agree. Sigma becomes the share of falsifier-direction tests that pass after repair.
3. Do not let `SK_UNKNOWN` trigger the re-injection penalty. Propagate R_k as “not computable” rather than forcing a penalty.

The measured surprise does change my answer. Markdown falsifiers are executable without a compiler; 41.9% decisiveness versus 16.7% on Python means prose is not the wall for sigma. The wall is the code’s assumption that no AST means no assessment.

================================================================================
WHAT IS NOT IN THIS FILE, AND WHY
================================================================================

Deliberately excluded: CC1's own summaries, syntheses and recommendations on this
topic. They are the thing the founder is trying to check, so including them would
defeat the purpose. They live in the session record and in the TTS files.

One CC1 finding IS stated here because it is a measurement rather than an opinion,
and it is checkable in one command:

  EXTEND is parsed by _VERDICT_RE, offered to models in the prompt as the explicit
  alternative to filing a duplicate ("check the registry - CONFIRM or EXTEND
  instead of duplicating"), used 183 times across the archive, and there is no
  "EXTEND" string literal anywhere in reference_runner_v2.py. Verify with:

      grep -c '"EXTEND"' bench/reference_runner_v2.py

================================================================================
THE QUESTION THIS COMPENDIUM EXISTS TO ANSWER
================================================================================

The founder's words, 21 August 2026:

  "We just need a definitive status for each issue, how they are marked as
  confirmed/unconfirmed, merged, dupes, resolved, or whatever, and to do this in a
  way that Bugzilla doesn't simply become a 'ledger' of what we did (although that
  is clearly also necessary), but also a way of gathering and assessing fixes and
  how they should be applied to improve/add to a better solution to any given
  problem, but to do so in a way that is both applicable to software development
  and STEM more generally."
