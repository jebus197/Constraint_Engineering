# Regulatory Compliance Framework — 20 April 2026

## What This Document Covers

On 20 April 2026 the Constraint-Driven Synthesis and Falsification (CDSFL) project added three pieces of regulatory-compliance material to its documentation set:

1. A new subsection added to Part V of the white paper (`PAPER.md`) — *Alignment with Modern Governance Frameworks*.
2. A new section added to the general-audience rationale (`docs/EXTENDED_RATIONALE.md`) — *Auditable Cognitive Infrastructure (April 2026)*.
3. A new standalone document at `docs/COMPLIANCE_FRAMEWORK.md`.

This note describes what each of the three pieces says, what framing they use, and why they were added at this point in the project's timeline.

---

## Background

The CDSFL framework was built to operationalise Popperian falsification for AI-assisted technical work. Governance alignment was not a design goal. What happened during the April 2026 consolidation is that the primitives the framework requires for its own discipline coincide closely with primitives that four parallel strands of modern governance ask of any serious AI system.

The primitives:

- auditable persistence
- tamper-evident sealing of records
- Ed25519 signatures over findings
- admissibility gates with hard-gate tool verification
- programmatic rejection of unverified claims
- a full immune-pipeline audit trail
- HIL sign-off on escalation
- preservation of findings across revisions

The coincidence is genuine. It is also partial, and the partiality is load-bearing. The framework supplies the primitives. It does not supply the surrounding apparatus — key management, incident response, third-party audit procedures, conformity documentation, DPIAs, complaint mechanisms, model and system cards — without which no compliance claim can be made. All three pieces of material added this session state this partiality plainly.

---

## 1. PAPER.md Part V — *Alignment with Modern Governance Frameworks*

A new subsection was inserted into Part V (Persistence and Verification), between *Reasoning State as Verified Memory* and the closing subsection.

### Structure

- **Opening paragraph.** Names the alignment as genuine but partial. States CDSFL provides primitives, not conformity packages.
- **Mapping table.** Eight rows × four regimes. Each row names a CDSFL primitive and identifies the clauses in each regime that most directly rely on it.
- **Closing paragraph.** States the table is technical, not legal; reiterates partiality; points to `COMPLIANCE_FRAMEWORK.md`.

### The four regimes

| Regime | Full name |
|---|---|
| EU AI Act | Regulation (EU) 2024/1689 |
| GDPR | Regulation (EU) 2016/679 |
| NIST AI RMF | NIST AI Risk Management Framework 1.0 (2023) |
| ISO/IEC 42001 | ISO/IEC 42001:2023 — AI management system |

### The eight primitives

1. Append-only record store + SHA-256 hash chain
2. Epoch Merkle tree sealing (RFC 9162)
3. Ed25519 signatures over findings
4. Admissibility gates + hard-gate tool verification
5. Programmatic rejection of unverified claims
6. Immune-pipeline audit trail
7. HIL sign-off on escalation
8. Findings persistence across revisions

### Load-bearing framing

> CDSFL is not a governance product. It is a scientific-method framework that happens to leave behind the kind of audit trail governance bodies increasingly ask for. Projects that adopt the framework inherit the primitives; they do not inherit compliance.

---

## 2. EXTENDED_RATIONALE.md — *Auditable Cognitive Infrastructure (April 2026)*

A new section, positioned between *Experiment 40 and Operational Closure (17–19 April 2026)* and the closing cross-reference footer.

### Structure

- **Observation.** A consequence of the persistence and verification layer that was not initially a design goal has become visible during the April 2026 consolidation.
- **Four regimes named in plain language.** What each asks of a serious AI system, and how the framework's primitives line up.
- **Partiality stated directly.** Enumeration of what the framework does not supply; explicit statement that this surrounding apparatus is what the deploying organisation is correctly expected to put in place.
- **Term introduced.** *Auditable cognitive infrastructure* — a running system whose operational record happens to be the kind of record regulators have started asking for, and whose failure modes are visible in the same audit trail that its successful runs are recorded in.
- **Closing sentence.** The structures a Popperian cognitive architecture needs in order to maintain its own discipline turn out to coincide with the structures a modern regulatory environment asks of any serious AI system. That convergence is not a coincidence.

---

## 3. docs/COMPLIANCE_FRAMEWORK.md

A new standalone document, approximately 500 lines, organised into five parts plus an opening framing and a closing note.

### Part 0 — What this document is, and what it is not

- A technical audit. Not legal advice.
- Four labels used throughout: **Provides**, **Provides partially**, **Does not provide**, **Out of scope**.

### Part 1 — Honest gap statement

Ten gaps identified, each with an identifier:

| ID | Gap |
|---|---|
| G1 | Key management |
| G2 | Incident response |
| G3 | Third-party audit procedure |
| G4 | System and model cards |
| G5 | Complaint mechanism |
| G6 | Data protection impact assessment |
| G7 | Conformity documentation |
| G8 | Fundamental rights impact assessment |
| G9 | Post-market monitoring |
| G10 | Supply chain assurance |

### Part 2 — Per-regime mapping tables

Four tables, one per regime:

| Regime | Table coverage |
|---|---|
| EU AI Act | 14 obligations (Art. 9 risk management → Art. 27 FRIA) |
| GDPR | 15 obligations (Art. 5(1)(a) lawfulness → Arts. 44–50 international transfers) |
| NIST AI RMF | 20 categories across GOVERN / MAP / MEASURE / MANAGE |
| ISO/IEC 42001 | 20 clauses (Cl. 4 context → Cl. 10.2 nonconformity and corrective action) |

**Tables are honest, not flattering.** Where the framework does not provide something, the table says so. Where it provides something only partially, the table says so. Where something is out of scope, the table says so.

**Specific note on GDPR Art. 17 right to erasure.** An append-only cryptographic record is in structural tension with the right to erasure. The framework's position: personal data should not be written into the immutable chain in the first place; where processing of personal data is unavoidable, a deployment must implement a separate erasable data store with the chain holding only hashes or references. This is a deployment-level design decision and must be taken before deployment begins.

### Part 3 — Six supplementary-artefact templates

Each template addresses one of the gaps. Each is drafted in form close enough to working language that a deployment can use it as a starting point without mistaking it for a finished artefact. Each explicitly requires adaptation and qualified review before being put into effect.

| Template | Addresses gap | Key contents |
|---|---|---|
| §3.1 Key-management specification | G1 | Generation, storage, rotation, revocation, signing authority, separation of duties, compromise response |
| §3.2 Incident-response protocol | G2 | Definitions, severity tiers, role roster, eight phases (declare → learn), notification matrix |
| §3.3 Third-party audit procedure | G3 | Scope definition, evidence package, access rights, sampling methodology, interview protocol, reporting format, remediation, independence |
| §3.4 System and model card | G4 | System identification, purpose and scope, models in use, framework configuration, performance, risk and governance, falsifiable claims, change log |
| §3.5 Complaint mechanism | G5 | Who may complain, channels, acceptance criteria, triage SLA, review process, escalation, remedies, record-keeping, no-retaliation clause |
| §3.6 Data protection impact assessment | G6 | Description of processing, necessity and proportionality, risks to data subjects, measures to address risk, framework-specific considerations, consultation, sign-off |

### Part 4 — Versioning and review

- Initial version, dated 20 April 2026.
- Substantive changes will be recorded in a change log committed to the persistence chain.

### Part 5 — Final framing

- CDSFL does not claim to solve compliance.
- Authors welcome correction of any specific claim and will update accordingly.
- The discipline the framework applies to its own scientific claims applies equally here: the mapping is offered as falsifiable, and where it is wrong it will be fixed.

---

## Framing Throughout

Deliberately conservative. The three pieces do not claim:

- that CDSFL is compliant with any named regime;
- that adoption of the framework produces a compliant system;
- any particular legal status.

They do claim:

- that the framework supplies certain technical primitives;
- that those primitives happen to line up with primitives certain governance regimes require;
- that the framework does not supply certain other things;
- that the other things can be produced from the supplementary-artefact templates.

Voice: same as the rest of the project's documentation. British spelling. Known limits stated plainly. No overstatement. No minimisation either.

---

## Why This Was Added Now

The framework had reached a point in April 2026 where its persistence and verification layer was mature, and the alignment with modern governance requirements visible, that not documenting the alignment would have been the omission.

At the same time, documenting the alignment without stating its limits honestly would have been a different kind of omission, and a more damaging one. A framework that claimed more than it delivered would undermine the project's own commitment to Popperian falsification.

The three pieces are the project's attempt to state the position accurately: what the framework supplies, what it does not, how it lines up with what modern governance regimes ask, and what a deployment would need to add on top.

---

## Summary

Three pieces of regulatory-compliance material added:

1. **`PAPER.md` Part V** — compact, table-driven subsection for the formal technical statement.
2. **`docs/EXTENDED_RATIONALE.md`** — plain-language section introducing *auditable cognitive infrastructure* as a term.
3. **`docs/COMPLIANCE_FRAMEWORK.md`** — standalone 500-line document with full mapping, ten identified gaps, six supplementary-artefact templates.

Framing throughout: primitives provided, gaps named, legal judgement reserved. Templates are drafts. Tables are falsifiable. Corrections welcomed.

---

*Companion TTS file: `~/Desktop/CDSFL_tts/Regulatory_Compliance_Framework_2026-04-20.txt`. Context: 20 April 2026 five-batch documentation consolidation sweep — Batch D. Related mirrors: `Founders_Notes_Revisions_2026-04-20.md` (Batch A), `README_Promotion_2026-04-20.md` (Batch B).*
