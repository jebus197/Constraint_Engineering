<!-- PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'fmea_level_and_draft_encodings_2026-11-14', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: fda41ed321819b3fef2f633f72eb604850feef3492fa10aa2a29137064d86e59
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited. -->
# Panel record — where the FMEA critical level sits, and which of the 22 draft
# encodings may leave DRAFT

Seat: single free-panel seat, one-shot dispatch, 2026-11-14.
Artefact digests verified against the dispatch stamps before any measurement:
all 6 matched.

Measurement script: `scripts/where_does_a_critical_level_land_2026-11-14.py`
Guard: `bench/tests/test_the_severity_declaration_is_complete_2026-11-14.py`

## Q1 — RECOMMEND RETAIN 7; the level change itself is the founder's

Four independent grounds, three of them executed.

1. **The project's own materiality definition.** `cdsfl_core_formal.md` §10
   names five material-defect categories. Only one of them — hard-constraint
   violation, and only its law/safety sub-case — reaches FMEA's 9-10 SAFETY OR
   REGULATORY band. Wrong result, verification-integrity corruption, silent
   evidence loss and unreproducibility all sit in 7-8 HIGH. A cut at 9 would
   demote **4 of the project's own 5 material categories** below critical.
   This is an argued mapping, written out in full in the script's M6 so it can
   be disputed. It is the decisive ground, and it is about this project's
   definition of material, not about the handbook.

2. **Cross-scale rank consistency, measured.** Rank of the declared critical
   level counted from the top of its own band list: software (CVSS v4.0 /
   High) = 2, chemistry (GHS Rev. 11 / Category 2) = 2, biology (CTCAE v5.0 /
   Grade 3) = 3, engineering at 7 = 2. Engineering at 9 = 1. Nine would make
   engineering the only scale whose critical level is the MAXIMAL band,
   outside the observed range [2, 3].

3. **Degeneracy.** At the maximal band the predicate `c_d(f) ≽_d θ_d` is
   equivalent to `c_d(f) = max` — an identity test, not an ordinal threshold.
   The up-set collapses to one element and the ordering above the cut carries
   no information. `cdsfl_core_formal.md` defines θ_d as "a distinguished
   element OF that ordering"; the maximum distinguishes nothing, since every
   scale has one by construction.

4. **Ambiguity direction.** `p-pass-ambiguity-default` resolves an ambiguous
   HARD constraint toward the tighter reading. The sources are secondary and
   the handbook names two landmarks, so the ambiguity is real and resolves
   to 7.

### The decision procedure, stated so it applies to the next standard

Given a standard naming landmark bands B_1 ≺ … ≺ B_m:

1. **Enumerate the landmarks the standard itself labels.** Do not collapse
   two into one; record both in `severity_levels`.
2. **Reject B_m as a candidate cut** unless the standard states that only the
   top band carries consequence. A cut at the maximum is an identity test.
3. **Map the consuming project's own material-defect categories onto the
   bands.** The cut is the LOWEST band that at least one material category
   reaches. This is the operative step and it makes the cut a property of the
   consumer's materiality definition, not of the standard's vocabulary.
4. **Check the rank from the top against the project's other declared
   scales.** A rank outside the observed range is not disqualifying but must
   be justified in `critical_level_note`.
5. **Where steps 3 and 4 disagree, resolve toward the tighter cut** and record
   the disagreement. Ambiguity is HARD by §1.
6. **Record which landmark was NOT chosen, and why**, in the note. Both
   landmarks continue to reach a seat on the `LEVELS:` line regardless.

Applied here, step 3 yields **7** and step 4 agrees. For CVSS the same
procedure yields High (7.0), which is what the manifest declares. For CTCAE it
yields Grade 3. The procedure reproduces all three existing declarations.

### The third option — declare both landmarks — is REJECTED, measured

`domain_vocabulary.severity()` returns exactly one `critical_level` key.
`composer._severity_declaration` emits exactly one `CRITICAL LEVEL:` line.
Product modules referencing `critical_level`: two (`composer.py`,
`domain_vocabulary.py`). **Nothing in the harness can consume a second cut**,
so declaring one is an addition nothing reaches — the failure class this
project has shipped 11 times since 2026-08-01.

And it is unnecessary: **both landmarks already reach the seat**, on the
`LEVELS:` line of the delivered declaration —
`1 no effect; 2-3 very minor to minor; 4-6 moderate; 7-8 high; 9-10 safety or
regulatory`. What a second field would add is a second CUT, not a second
landmark.

### Consequence of a move to 9, measured

- `reference_runner_v3.CRITICAL_SEVERITY_THRESHOLD` = `0.7` (float). Mutating
  the manifest level 7 → 9 on a copy left it at `0.7`. **Two distinct
  quantities.**
- `convergence_location.py` contains `critical_level` 0 times and
  `severity_scale` 0 times. All three novelty series take a float
  `critical_threshold` (default 0.7) and have no `domain` parameter. **The
  named level does not enter convergence.**
- What changes is the one `CRITICAL LEVEL:` line in a seat's composed
  directive. So the move is a REPORTING change, and that bounds it.

## Q2 — 11 of 22 may move to CROSS_VERIFIED; 11 may not

Criteria applied, stated before use: (a) the cited standard is named with
edition/version and confirmed current, or the encoding honestly declares no
scale with a stated reason; (b) a majority of its HARD constraints are
tool-checkable; (c) no `[VERIFY:current]` sits on a load-bearing citation.

11 of 22 = 50.0000%, Wilson [30.7221%, 69.2779%]. Coverage: 22 of 22 examined.
Across the 22, 115 of 152 HARD constraints are tool-checkable = 75.6579%,
Wilson [68.2581%, 81.7928%].

**Recommended CROSS_VERIFIED (11):** biology_genetics,
information_science_retrieval, mathematics_applied, mathematics_numerical,
mathematics_proof, physics_classical, physics_general, physics_quantum,
software_general, statistics_inference, statistics_time_series.

**Must stay DRAFT (11), with the blocking reason:**
biology_natural_world (3/7 tool-checkable, below majority);
biology_zoology (1/7; animal-welfare scale `[VERIFY:current]`, no scale
confirmed); chemistry_general (Rev. 11 currency is SECONDARY-sourced);
cross_general (cites no published standard — the rule is the founder's, which
is authoritative but is not an external standard);
information_science_data_management (ISO 11179 unversioned,
`[VERIFY:current]`); information_science_general (same ISO citation);
information_science_knowledge_representation (ISO 11179 and Dublin Core
unversioned); logistics_warehousing ("None confirmed primary");
physics_thermodynamics (inherits chemistry's Rev. 11 currency defect);
statistics_experimental_design (CONSORT/PRISMA explicitly cited without a
version, `[VERIFY:current]`); statistics_general (ISO 3534 no edition).

**The tier promotions are NOT applied to the manifest.** `encoding_tier`
appears 0 times in `composer.py` and 0 times in `reference_runner_v3.py`;
flipping every tier DRAFT → CROSS_VERIFIED on a copy left the composed
declaration byte-identical. The tier is validated for membership in `tiers`
and printed by the `domain_vocabulary` CLI, and gates nothing. Writing
promotions now would be an addition nothing reaches. Promote when a consumer
exists.

## The one material defect found, and it is repaired

`_severity_declaration` returns `""` whenever the composed text already
matches `^SEVERITY SCALE:`, on the stated ground that the encoding is "the
narrower, better-sourced statement". **Tested on version-carrying — the exact
property the CVSS v3.1 → v4.0 and GHS Rev. 10 → Rev. 11 corrections were
about — that ground was false for 11 citations across 7 of the 22 files.**
A seat was told to report a `(value, scale-name)` pair and handed
`FMEA severity applies with critical at 7`, `CTCAE with critical at Grade 3`,
`GHS health hazard category` — scale names with no edition — while the
manifest held the edition and the suppression rule prevented it arriving.

Repaired by adding the edition to each citation (no level changed, no gate
touched): chemistry_general, mathematics_applied, physics_classical,
physics_thermodynamics, statistics_experimental_design, statistics_inference,
software_general. Offenders 11 → 0.

## Residual, named rather than left silent

`physics_general.txt` cites **INES** with no revision. INES is not declared in
the manifest, so the new guard's family table does not cover it, and no
manifest entry holds its edition to supply. This is a real gap and it is
recorded rather than repaired, because inventing an INES revision is the
failure this project calls a magic wand.

A seat is told to report a `(value, scale-name)` pair on a 1-10 ordinal scale.
The gate reads `float(entry["severity"])` and compares it to `0.7`. Searched
for a conversion from a named ordinal rank to that float: **0 definitions** in
`reference_runner_v3.py`, `composer.py` and `domain_vocabulary.py`. The route
from the delivered declaration to the field the gate reads is undefined. This
is the strongest candidate for the next round; it is stated as a measured
absence and not claimed as a confirmed defect, because no falsifier here
demonstrates a wrong outcome from it.
