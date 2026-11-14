<!-- PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'fmea_level_and_draft_encodings_2026-11-14_joint', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 7868d74b3ee776169cf5186dbc3fce12c9191239fd30fcd79f2c6b080d212d8c
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited. -->
# JOINT ROUND `fmea_level_and_draft_encodings_2026-11-14` — tier adjudication record

Seat: third seat, joint half. This file is the record the brief asked for: the
per-encoding adjudication a consumer reads BEFORE any `TIER:` line is written.
No tier line was flipped this round — see "why the tiers are held" below.

## THE FACT THAT REFRAMES Q2 (measured this round, wired to a test)

The brief said `encoding_tier` is consumed by 0 decisions, by AST. True of the
MANIFEST field; FALSE of the file-level `TIER:` line. Measured by execution:
`composer.compose(<domain>, "fable_5_1").rendered_text` carries the default
encoding's `TIER: DRAFT` line VERBATIM for 8 of the 9 routable domains
(logistics' default encoding carries no TIER line). The consumer the AST sweep
cannot see is the SEAT MODEL. A tier flip is therefore a change to what every
seat is told about the authority of its own constraint box — prompt-delivered
epistemic framing, the same class as the Q1 critical level. Wired to
`bench/tests/test_the_tier_line_reaches_the_seat_2026-11-14.py` (executed red
on the as-dispatched tree for the CTCAE guard, green after repair).

## Q1 — RETAIN 7, HOLD ANY MOVE FOR THE FOUNDER (3 seats, 2 distinct routes, 1 answer)

The blind seats' procedures are 2 RULES, not 1 rule in 2 wordings:
cc2 maps the project's material categories to the band their CONSEQUENCE
MAGNITUDE sits in; fable asks whether a band's PUBLISHED DEFINITION entails
materiality. On AIAG-VDA FMEA they coincide (bands partition by consequence of
function, S7 degradation / S8 loss of primary function), which is why both
landed on 7. On a standard whose lowest band is defined intensionally ("any
deviation beyond nominal tolerance") they separate: executed in
`scripts/the_two_q1_procedures_can_disagree_2026-11-14.py` — fable's rule cuts
at class 1 of 4, cc2's at class 3 of 4, same standard, same materiality
definition. So the agreement on 7 survives NOT as corroboration-by-vote but
because both coordinates coincide on this standard; for a future standard with
intensional bands the rules split, the ambiguity is HARD (§1), resolve to the
tighter cut and hold for the founder (cc2's step 5, now demonstrated).

## Q2 — adjudication of the 11 rows the seats classify differently (not 5: 16−11=5 is net, the symmetric difference is 11)

Citations below were checked against PRIMARY publishers 2026-11-14 by this seat.

| encoding | cc2 | fable | ADJUDICATED | ground |
|---|---|---|---|---|
| biology_genetics | CV | DRAFT | **fable right at dispatch; CV-ELIGIBLE after this round's repair** | cc2 accepted the "confirmed current 2026-11-12" claim at face value — the exact failure J3 names. v5.0→v6.0 corrected in-file this round (primary: NCI, v6.0 published 2025-07-22, Grade 3 wording unchanged). |
| is_retrieval | CV | DRAFT | **fable right — DRAFT** | SOURCES names "standard information-retrieval evaluation practice", an UNNAMED basis; nothing exists to cross-verify against. Route up: name the evaluation literature. |
| mathematics_proof | CV | DRAFT | **fable right — DRAFT** | CROSS_VERIFIED marks a verification EVENT. cc2's "5/8 tool-checkable" is checkABILITY, not a check that happened. No standard exists and no 2-source verification of the constraint content was executed by anyone. Route up is VALIDATED (HIL) directly. |
| chemistry_general | DRAFT | CV | **fable right — CV-ELIGIBLE (discharged)** | GHS Rev. 11 confirmed against UNECE primary: ST/SG/AC.10/30/Rev.11, published 2025-09-12; Rev. 11 changes do not touch acute-toxicity categories. Flag discharged in file + manifest this round. |
| cross_general | DRAFT | CV | **fable right — CV-ELIGIBLE, weakest promotion, flag to founder** | No external standard exists BY CONSTRUCTION; the load-bearing content is the founder's verbatim rule + computations executed by 2 independent tools (pint, SymPy, re-executed by fable). A verification event exists, unlike mathematics_proof. |
| info_science_general | DRAFT | CV | **fable right — CV-ELIGIBLE (discharged)** | ISO/IEC 11179-1:2023, Edition 4, published 2023-01-16, confirmed current. Flag discharged in file this round. |
| info_science_data_management | DRAFT | CV | **fable right — CV-ELIGIBLE (discharged)** | same discharge. |
| info_science_knowledge_representation | DRAFT | CV | **fable right — CV-ELIGIBLE (discharged)** | ISO/IEC 11179-1:2023 + DCMI Metadata Terms 2020-01-20 / ISO 15836-1:2017, -2:2019. Flag discharged in file this round. |
| physics_thermodynamics | DRAFT | CV | **fable right — CV-ELIGIBLE** | its own sources are primary and exact (SI 9th ed; k fixed); the GHS inheritance names scale+level only, and the VERSION lives in the manifest (now primary-confirmed) — duplicating it in the encoding would be 2 tables that can drift. Boundary traced per §3: the dependency chain terminates at the discharged chemistry citation. |
| statistics_experimental_design | DRAFT | CV | **fable right — CV-ELIGIBLE (discharged)** | CONSORT 2025 (2025-04-15, five journals) + PRISMA 2020 confirmed; flag discharged in file this round. |
| statistics_general | DRAFT | CV | **fable right in verdict, wrong in remedy — CV-ELIGIBLE (pinned)** | fable's "not load-bearing" carve-out left the citation unversioned, the CVSS-v3.1 failure shape. Pinned instead: ISO 3534-1:2006 Ed 2 (corrected 2007-09; reviewed and confirmed 2021; ISO marks it for revision as of 2026-06-24 — this citation AGES, recorded in-file). |

Shared 8 (both CV): software_general, mathematics_applied, mathematics_numerical,
physics_general, physics_classical, physics_quantum, statistics_inference,
statistics_time_series — confirmed, load-bearing figures re-executed by fable
and editions re-checked (CVSS v4.0 current, spec doc v1.2; IEEE 754-2019
current, next revision ~2029; SI Brochure still 9th edition, revised to v4.01
June 2026, 28th CGPM held 2026-10-13/15).
Shared 3 (both DRAFT): biology_natural_world (tool-checkability below majority),
biology_zoology (animal-welfare scale unresolved, flag live), logistics_warehousing
(honest absence of a primary).

**TOTAL: 17 of 22 CV-ELIGIBLE (0.772727, Wilson [0.565600, 0.898770], Wolfram
concurring), 5 stay DRAFT.** Neither 11 nor 16: cc2's 11 was right against the
staged tree except biology_genetics (stale confirmation accepted) and its 2
semantics calls; fable's 16 was right conditional on edits that died with its
sandbox and is 17 once biology_genetics' only named defect is repaired.

## Why the tiers are HELD rather than flipped

The TIER line is prompt-delivered (measured above). A flip changes every seat's
dispatched directive — the same class of change as the Q1 critical level, which
BOTH blind seats held for the founder. Consistency requires the same discipline
here: this record carries the per-row evidence; flipping 17 lines is one
founder-confirmable action. A WRONG CROSS_VERIFIED in a prompt is worse than a
late one: it is exactly the "false sense of security" the tier exists to
prevent (manifest, Gemini 3.1 Pro caution, 2026-04-09).

## J3 — the other declared scales, checked against primaries 2026-11-14

| scale | confirmation it carried | primary check 2026-11-14 | verdict |
|---|---|---|---|
| CVSS v4.0 (software) | primary read 2026-11-12 ("Table 22 read directly") | v4.0 current; no v5; spec document v1.2, metrics unchanged since 2023-11 | **NOT STALE** |
| GHS Rev. 11 (chemistry) | SECONDARY, self-flagged [VERIFY:current] | Rev. 11 primary at UNECE, published 2025-09-12, current; Rev. 12 expected 2027 (biennial cadence) | **CONFIRMED, flag discharged** |
| AIAG-VDA FMEA (engineering) | SECONDARY, self-flagged | **STALE AT PRINTING LEVEL**: current is 1st Edition 2nd Printing, August 2022, incorporating errata; manifest cited "1st edition 2019 (errata June 2020)" only. Same staleness shape as CTCAE/CVSS. Bands remain secondary-sourced (handbook paywalled) — flag retained for the band definitions. Corrected in manifest this round. | **CORRECTED** |
| CTCAE (biology) | "CONFIRMED 2026-11-12 against the NCI source" — WRONG by ~16 months | corrected to v6.0 by the orchestrator 2026-11-14; the 3 ENCODINGS still cited v5.0 and were corrected this round | **was stale; repaired** |

Staleness base rates, honestly small-n: of the 2 citations that CLAIMED a
confirmation, 1 was wrong — 0.500000, Wilson [0.094531, 0.905469]; of all 4
declared-scale citations, 2 were stale in some respect — 0.500000, Wilson
[0.150039, 0.849961]. The intervals are wide because n is 4; the mechanism
matters more than the rate: A CONFIRMATION IS A DATED EVENT AND NOTHING
RE-CHECKS IT. What this round adds mechanically:
`test_no_directive_cites_ctcae_v5_as_current` re-checks the one failure shape
that has now occurred twice (version-name staleness), and every declared-scale
source now carries its check DATE and its expected supersession cadence where
known, so the next reader can see the age of the confirmation at a glance.
A scheduled re-verification is named as the residual gap, not built: building
an unrequested scheduler in a one-shot panel round would be an addition nothing
reaches until the founder wires it.

## Files delivered this round

- `bench/directives/biology/biology_{genetics,natural_world,zoology}.txt` — v5.0→v6.0, refuted claims preserved verbatim inside corrections
- `bench/directives/chemistry/chemistry_general.txt` — GHS Rev. 11 discharged (UNECE primary)
- `bench/directives/information_science/information_science_{general,data_management,knowledge_representation}.txt` — ISO/IEC 11179-1:2023 Ed 4 + DCMI 2020-01-20 discharged
- `bench/directives/statistics/statistics_experimental_design.txt` — CONSORT 2025 + PRISMA 2020 discharged
- `bench/directives/statistics/statistics_general.txt` — ISO 3534-1:2006 pinned, revision-pending flag recorded
- `bench/cdsfl_registry/domain_manifest.toml` — chemistry source primary-confirmed; engineering source corrected to 2nd Printing Aug 2022
- `bench/tests/test_the_tier_line_reaches_the_seat_2026-11-14.py` — 4 guards, executed red-then-green
- `scripts/the_two_q1_procedures_can_disagree_2026-11-14.py` — J2 divergence, executed
