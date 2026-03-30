# CX Prompt Efficiency — Confer Record

Date: 2026-03-30
Participants: CC1 (collator), CC2 (player manager), CX (independent falsifier)

## Problem
CX (Codex 5.3 via `codex exec`) burns its context budget on codebase
investigation instead of producing findings. In the dispatch decomposition
confer round, CX ran 78 shell commands and consumed 155,454 tokens before
producing 5 structured findings. The findings were good (severity 0.84-0.98)
but the process is highly inefficient.

Root cause: confer prompts describe the problem but do not embed the actual
code CX needs to review. CX must go find it itself.

## CC2 Findings (6 structured)

### CC2_F001 (0.95): Stdin piping
The code passes prompts as positional args to `codex exec`. macOS has ~1MB
arg limit. `codex exec` supports reading from stdin via `-` flag. Switching
to stdin removes the constraint entirely.
Fix: Use `subprocess.run(["codex", "exec", "-"], input=prompt)`.

### CC2_F002 (0.92): Briefing document pattern
Core finding. Compare Exp 12 confer (embedded 20-line extracts + specific
questions → CX responds with verdicts, no investigation) vs Exp 17/18
(dumps whole file + names boundary → CX investigates for 78 tool calls).
Fix: CC1 prepares a briefing document: context (2-3 sentences), focused
code (15-30K chars, boundary region + call sites), specific question.

### CC2_F003 (0.78): Pre-digestion bias risk
If CC1 extracts only the code it thinks is relevant, CX cannot find bugs in
code CC1 didn't include (unknown unknowns). But the current alternative (CX
reads the full file) doesn't solve this either — CX made extraction choices
under time pressure and still only produced 5 findings.
Fix: Two-tier approach. Default: focused briefing + skeletal signatures of
adjacent code. Every 3rd round: CX gets repo access with explicit instruction
to spend ≤10 tool calls verifying the extract isn't missing critical context.

### CC2_F004 (0.85): Persistent briefing across rounds
CXReviewChat accumulates CX's prior responses but doesn't carry forward the
embedded code artifact. Each round's prompt is built fresh. If round 2 doesn't
re-embed the code, CX re-investigates.
Fix: Structure multi-round as: briefing (stable) + prior findings (growing,
compressed) + this round's question (new).

### CC2_F005 (0.70): Threshold adjustment
Lower Codex decomposition threshold from 60K to 30K chars and change from
area rotation to briefing document pattern. DEFERRED — secondary to the
structural fix.

### CC2_F006 (0.88): Output schema constraint
`codex exec` accepts `--output-schema` flag for JSON Schema constrained
output. Not used anywhere in the codebase. Would force structured findings
and make parsing deterministic.
Fix: Create CDSFL findings JSON Schema, pass via `--output-schema`.

## CX Findings (6 structured, 33K tokens — 78% reduction from prior round)

### CX_F001 (0.98): VALIDATION — Embedded extracts needed
"The main thing missing from the prior prompt was the primary evidence itself."
CX confirms that a compact review packet — file paths/line anchors, exact
code extracts, one layer of surrounding interaction code, relevant type/data
definitions, exact observed failure facts — would have eliminated most
investigation.

### CX_F002 (0.95): CHALLENGE — Pre-selection bias is real
"CC1 pre-selecting extracts creates a real bias risk. The defect can sit just
outside the chosen snippet." CX proposes anti-bias guards: raw diff or
touched-symbol manifest, one-line reason each snippet was selected, explicit
"possible omission zones" naming nearby code not shown, one bounded follow-up
fetch if the packet leaves a specific gap.

### CX_F003 (0.93): NOVEL — Minimum reliable context template
Six fields only: review target, exact extracts, one-step-in/one-step-out
interaction code, relevant type/data definitions, verified facts, explicit
unknowns/exclusions. "Anything less forces repo search; much more wastes
tokens."

### CX_F004 (0.90): VALIDATION — Verified facts section needed
"I do not need to re-derive counts, timings, exact error text, failing inputs,
or already-checked observations unless the task is specifically to audit those
facts." Separate from hypotheses and proposed explanations.

### CX_F005 (0.88): NOVEL — Two-stage confer protocol
Stage 1: send review packet, request findings strictly from that evidence.
Stage 2: only if CX identifies a concrete missing artifact, allow one targeted
expansion request for a named file, symbol, or error artifact. If the gap
remains, report uncertainty instead of continuing open-ended search.

### CX_F006 (0.84): CHALLENGE — Adversarial brief needed
"Even a well-packed prompt can still bias the review if it is framed as
'here is the fix.'" Add mandatory adversarial brief: "The real defect may be
outside these snippets. Test for omitted assumptions, wrong inputs, wrong
ownership, and wrong problem framing before validating the proposed fix."

## CC1 P-Pass

### Converged (both models agree):
- Embed focused code extracts in confer prompts (CC2_F002 + CX_F001)
- Anti-bias guards with adversarial brief (CC2_F003 + CX_F002 + CX_F006)
- Two-stage protocol with bounded expansion (CC2_F003 tier-2 + CX_F005)

### Accepted (one model, no challenge):
- Stdin piping (CC2_F001) — mechanical fix
- Verified facts section (CX_F004)
- Output schema for structured findings (CC2_F006)
- Persistent briefing across multi-round confers (CC2_F004)
- Minimum 6-field confer template (CX_F003)

### Deferred:
- Threshold adjustment (CC2_F005) — secondary to structural fix

## Converged Design: Standard Confer Packet

Six mandatory sections:

1. REVIEW TARGET — 2-3 sentence problem statement
2. CODE EXTRACTS — focused functions + one layer of call sites (15-30K chars),
   with line anchors and selection rationale per snippet
3. INTERACTION SURFACE — skeletal signatures of adjacent code (names, params,
   return types, no bodies)
4. VERIFIED FACTS — measured sizes, timings, exact errors, commit hashes.
   Labelled separately from hypotheses.
5. EXPLICIT UNKNOWNS — what CC1 doesn't know + "possible omission zones"
   naming nearby code not shown
6. ADVERSARIAL BRIEF — "The real defect may be outside these snippets. Test
   for omitted assumptions, wrong inputs, wrong ownership, and wrong problem
   framing before validating the proposed fix."

Plus mechanical fixes:
- Stdin piping for codex exec (removes arg size limit)
- --output-schema for structured CDSFL findings JSON
- Persistent briefing document across multi-round confers

## Evidence
- CX dispatch confer round: 155,454 tokens, 78 tool calls, 5 findings
- CX process confer round: 33,144 tokens, 0 tool calls, 6 findings
- Token reduction from prompt improvement: 78%
- Both models independently identified the same root cause
