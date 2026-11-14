<!-- PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'fmea_level_and_draft_encodings_2026-11-14_joint', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 9e0f49b87d4c7164af67b802db05dc5ce398b035ddc8dc6c438728e63704d138
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited. -->
# Joint round — FMEA critical level and the 22 DRAFT encodings, 2026-11-14

Seat `claude` (joint half). Blind seats: `cc2` (11 of 22) and `fable` (16 of 22).

## 1. The brief's disagreement count was the NET, not the disagreement
`|16 - 11| = 5`. The SYMMETRIC DIFFERENCE is **11** — `cc2` alone promotes 3
(biology_genetics, information_science_retrieval, mathematics_proof), `fable`
alone promotes 8. Only 8 encodings are promoted by both. Confirmed by set
arithmetic in Python and by Wolfram Language (`3+8 = 11`, `Abs[16-11] = 5`).

## 2. Q1 — the agreement survives, the procedures do not
Both seats recommend RETAIN 7, and I concur. But the 2 decision procedures are
**not one rule**, proved by z3:
  `cc2`   qualifies a band B iff  B ∩ Material ≠ ∅   (existential overlap)
  `fable` qualifies a band B iff  B ⊆ Material       (entailment)
Entailment implies overlap, so `fable`'s cut ≥ `cc2`'s cut ALWAYS (z3 `unsat`
for the reverse), and a partially-material band separates them (z3 `sat`, with
a 4-band witness). Each then breaks on a DIFFERENT one of the project's own
scales: `cc2`'s existential predicate has no lower bound and collapses the CVSS
cut toward Medium; `fable`'s entailment predicate needs band CRITERIA TEXT,
which CVSS Table 22 does not have (numeric ranges only). The answer 7 is right;
neither route is yet a general procedure. Script:
`scripts/two_cut_procedures_are_not_one_rule_2026-11-14.py`.

## 3. The material finding — a correction that reached nobody
`composer._severity_declaration` returns `""` when the encoding carries its own
`^SEVERITY SCALE:` line. The manifest was corrected to CTCAE v6.0; the 3 biology
ENCODINGS still said v5.0. Demonstrated by importing the real composer: the seat
saw `CTCAE v5.0` and 0 occurrences of `v6.0`. §10 category 4.

## 4. Staleness audit of the other declared scales (primary sources, 2026-11-14)
| scale | dated claim in repo | primary re-check | verdict |
|---|---|---|---|
| CVSS v4.0 | "Confirmed 2026-11-12" | first.org — v4.0 current, no successor | **STANDS** |
| SI Brochure 9th ed. | "(BIPM, 2019)" ×5 files | bipm.org — **v4.01, 2026-06-04**, 28th CGPM 13–15 Oct 2026 | **STALE, repaired** |
| ISO/IEC 11179 | unversioned, `[VERIFY:current]` ×3 | IEC webstore pub 81976 — **11179-1:2023 Ed 4.0, 2023-01-16** | **DISCHARGED** |
| GHS Rev. 11 | `[VERIFY:current]`, secondary | unece.org **HTTP 403** from sandbox, 2 URLs | **OPEN** |
| AIAG-VDA FMEA | `[VERIFY:current]`, secondary | no 2nd edition found; 1st ed. 2019 + Jun 2020 errata | **secondary only** |
| CTCAE | corrected to v6.0 today | manifest's own primary cite | STANDS (manifest); encodings repaired |

The SI result is the one that matters: **4 of the 8 encodings BOTH seats
promoted rested on a 5-month-stale citation.** The agreed set was not clean.

## 5. Delivered
13 citation repairs across 8 encodings (3 CTCAE, 5 SI, 3 ISO 11179 + 1 partial);
`bench/tests/test_the_manifest_correction_reaches_the_seat_2026-11-14.py`
(7 tests, red on the as-dispatched text, green after); a consumer-facing record
in the `domain_manifest.toml` tier block. **No tier was written**: `encoding_tier`
is consumed by 0 decisions (AST-verified), so a promotion is not a repair.

## 6. Open
GHS Rev. 11 primary unreachable from this sandbox. Dublin Core unversioned in
information_science_knowledge_representation, flagged rather than invented.
IEEE 754-2019, ASA 2016, CONSORT, ISO 3534 not primary-re-checked this round.
