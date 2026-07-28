# Compliance Framework

**A mapping of CDSFL technical primitives to modern AI and data-governance regimes, with an honest statement of what the framework supplies, what it does not, and a set of templates for filling the gaps.**

---

## 0. What This Document Is, and What It Is Not

This document is a technical audit. It names the primitives the CDSFL framework supplies, names the primitives each of four external governance regimes commonly requires, and states which CDSFL primitives line up with which external requirement. Where the framework supplies something commonly required by a regime, that is said. Where it does not, that is said too.

This document is not legal advice. It does not claim that any project using CDSFL is compliant with any named regime. Compliance is a property of the deploying organisation's full control environment, not of any single framework within it. Whether a deployment satisfies the EU AI Act, the GDPR, the NIST AI RMF, ISO/IEC 42001, or any other applicable regime is a determination for qualified legal and audit professionals working with the specifics of that deployment. The framework's authors are not qualified to make that determination and do not attempt to make it here.

The framing throughout is deliberately conservative:

- **Provides:** CDSFL contains a running, tested implementation of the primitive.
- **Provides partially:** CDSFL contains part of the primitive; the rest must be supplied.
- **Does not provide:** the primitive sits outside the framework's scope and must be built or procured separately.
- **Out of scope:** the primitive concerns organisational, legal, or procedural matters the framework cannot address in software.

The mapping tables in Part 2 use these four labels. The templates in Part 3 are drafts intended to be adapted to specific deployments. They are not ready-to-file compliance artefacts.

---

## 1. Honest Gap Statement

The CDSFL framework was built to operationalise Popperian falsification for AI-assisted technical work. Governance alignment was not a design goal, and the framework's authors did not set out to build a compliance product. What happened, during the April 2026 consolidation, is that the primitives the framework requires for its own discipline — auditable persistence, tamper-evident sealing, signed findings, programmatic admissibility, immune-pipeline logging, human sign-off on escalation — turned out to coincide closely with primitives that four parallel strands of modern governance ask of any serious AI system.

That coincidence is genuine. It is also partial. The following gaps are known and are recorded here without softening:

**G1 — Key management.** The framework uses Ed25519 signatures over findings. It does not supply the surrounding key-management infrastructure: generation protocol, secure storage, rotation policy, revocation procedure, quorum rules for signing operations, or separation-of-duties controls. A deployment must provide these. See §3.1 for a template.

**G2 — Incident response.** The framework records and preserves findings, including refuted ones, but does not by itself define an incident-response protocol for production failures, safety events, or governance triggers. A deployment must define its own. See §3.2 for a template.

**G3 — Third-party audit procedure.** The framework produces auditable artefacts, but does not define the procedure by which an external auditor would examine them: scope, evidence package, interview protocol, sampling methodology, reporting format, or remediation process. A deployment must define this with its chosen auditor. See §3.3 for a template.

**G4 — System and model cards.** The framework's architecture documents describe the framework itself. It does not produce per-deployment system or model cards that name the specific models in use, the specific data and task domains, the known limitations, the intended and prohibited uses, and the residual risks. A deployment must produce these. See §3.4 for a template.

**G5 — Complaint mechanism.** The framework does not supply a user-facing complaint, appeal, or redress mechanism for decisions affecting individuals. Where such decisions are in scope, a deployment must provide one. See §3.5 for a template.

**G6 — Data protection impact assessment.** Where personal data is processed, the framework does not by itself constitute a DPIA. A DPIA considers necessity, proportionality, risk to data subjects, and mitigating measures in the context of the specific processing activity. A deployment must produce one under qualified guidance. See §3.6 for a template.

**G7 — Conformity documentation.** For EU AI Act high-risk systems, the framework does not produce the Annex IV technical documentation package. It supplies inputs that can be incorporated, but the package itself must be assembled by the deploying organisation.

**G8 — Fundamental rights impact assessment.** Where the EU AI Act's fundamental-rights impact assessment applies, the framework does not produce it. This is a governance artefact that sits outside the framework's scope.

**G9 — Post-market monitoring.** The framework supplies a running audit trail, but does not by itself constitute a post-market monitoring plan. A deployment must maintain one.

**G10 — Supply chain assurance.** The framework's dependencies (Python, SymPy, z3, RDKit, Biopython, scikit-learn, NetworkX, CrossHair, and others) are themselves subject to supply-chain risk. The framework does not supply a software bill of materials, dependency-provenance attestation, or vulnerability-monitoring process. A deployment must maintain these.

These ten gaps are not a comprehensive list of every possible governance obligation. They are the ten that most commonly come up when the framework is examined against the regimes named in Part 2. A deployment should expect its own audit to surface additional items.

---

## 2. Regime Mappings

Each table below names a primitive and reports what the framework supplies. The regime clauses are cited to aid location, not to claim completeness of coverage.

### 2.1 EU AI Act (Regulation (EU) 2024/1689)

| Obligation | Article(s) | What CDSFL supplies | Status |
|---|---|---|---|
| Risk management system | Art. 9 | Falsification discipline producing iterative risk identification; immune-pipeline rejection of unverified findings | Provides partially |
| Data and data governance | Art. 10 | No data-management layer of its own | Does not provide |
| Technical documentation (Annex IV) | Art. 11 | Architecture docs, mathematical appendix, experimental record, test suite, registry TOMLs | Provides partially (inputs only) |
| Record-keeping (logging) | Art. 12 | Append-only record store, SHA-256 hash chain, Merkle sealing, immune-pipeline audit trail | Provides |
| Transparency and information to deployers | Art. 13 | README, PAPER, EXTENDED_RATIONALE, FOUNDERS_NOTES, GLOSSARY, REPRODUCING | Provides partially |
| Human oversight | Art. 14 | HIL sign-off on escalation; HIL role named in directives; no auto-apply of fixes | Provides |
| Accuracy, robustness, cybersecurity | Art. 15 | Admissibility gates, hard-gate tool verification, formal-methods cells (z3, CrossHair), rejection of unverified claims | Provides partially |
| Quality management system | Art. 17 | Bench test suite, QC scripts, recovery protocol | Provides partially |
| Post-market monitoring | Art. 72 | Running audit trail persists; no explicit plan | Does not provide |
| Incident reporting | Art. 73 | No incident-reporting mechanism | Does not provide |
| Conformity assessment | Arts. 43–49 | Out of scope — organisational procedure | Out of scope |
| CE marking | Art. 48 | Out of scope — legal attestation | Out of scope |
| Registration in the EU database | Art. 49 | Out of scope — organisational procedure | Out of scope |
| Fundamental rights impact assessment | Art. 27 | Out of scope — governance artefact | Out of scope |

### 2.2 GDPR (Regulation (EU) 2016/679)

| Obligation | Article(s) | What CDSFL supplies | Status |
|---|---|---|---|
| Lawfulness, fairness, transparency | Art. 5(1)(a) | Documentation of methodology and limitations | Provides partially |
| Purpose limitation | Art. 5(1)(b) | Out of scope — deployment decision | Out of scope |
| Data minimisation | Art. 5(1)(c) | Out of scope — deployment decision | Out of scope |
| Accuracy | Art. 5(1)(d) | Admissibility gates; hard-gate tool verification; refutation-aware persistence | Provides partially |
| Storage limitation | Art. 5(1)(e) | Append-only record with explicit retention decisions deferred to deployment | Provides partially |
| Integrity and confidentiality | Art. 5(1)(f), Art. 32 | Hash chain, Merkle sealing, Ed25519 signatures | Provides |
| Accountability | Art. 5(2), Art. 24 | Full audit trail; signed findings; HIL sign-off record | Provides |
| Records of processing activities | Art. 30 | Immune-pipeline audit trail as input; explicit RoPA document not produced | Provides partially |
| Data protection by design and default | Art. 25 | Architecture supports auditability; does not enforce minimisation | Provides partially |
| Security of processing | Art. 32 | Cryptographic integrity; application-layer security; infrastructure security out of scope | Provides partially |
| Data protection impact assessment | Art. 35 | Not produced by framework | Does not provide |
| Data subject rights (access, rectification, erasure, restriction, portability, objection) | Arts. 15–22 | Append-only record complicates erasure; deployment must design per-subject controls | Does not provide |
| Rights in automated decision-making | Art. 22 | HIL sign-off surface; meaningful-information documentation deployment-specific | Provides partially |
| Breach notification | Arts. 33–34 | Out of scope — organisational procedure | Out of scope |
| International transfers | Arts. 44–50 | Out of scope — deployment decision | Out of scope |

A specific note on the Art. 17 right to erasure. An append-only cryptographic record is in structural tension with the right to erasure. The framework's position is that personal data should not be written into the immutable chain in the first place; where processing of personal data is unavoidable, a deployment must implement a separate erasable data store with the chain holding only hashes or references. This is a deployment-level design decision and must be taken before deployment begins.

### 2.3 NIST AI Risk Management Framework (AI RMF 1.0, 2023)

| Function | Category | What CDSFL supplies | Status |
|---|---|---|---|
| GOVERN 1 | Policies, processes, procedures | CDSFL directives layer; composer; registry TOMLs | Provides partially |
| GOVERN 2 | Accountability and roles | HIL role named; expert-encoding authorship tracked | Provides partially |
| GOVERN 3 | Workforce practices | Out of scope — organisational | Out of scope |
| GOVERN 4 | Team engagement | Out of scope — organisational | Out of scope |
| GOVERN 5 | External engagement | Multi-vendor panel; external-review discipline | Provides partially |
| GOVERN 6 | Supply chain, third-party | No SBOM; no provenance attestation | Does not provide |
| MAP 1 | Context | Deployment-specific — not supplied by framework | Does not provide |
| MAP 2 | Characterisation of the AI system | Architecture documents; registry; cell types | Provides partially |
| MAP 3 | AI capabilities and limits | Known limitations sections in README and PAPER | Provides partially |
| MAP 4 | Risks and benefits | Falsifiable claims; open questions; invitation to falsify | Provides partially |
| MAP 5 | Impacts | Deployment-specific | Does not provide |
| MEASURE 1 | Methods, metrics, tools | Mathematical appendix; bench metrics; tool manifest | Provides |
| MEASURE 2 | Evaluation of AI performance | Bench test suite; experimental record; P-Pass corpus | Provides |
| MEASURE 3 | Mechanisms to track | Merkle chain; hash chain; signed findings; persistent record | Provides |
| MEASURE 4 | Feedback from end users | Not supplied — requires complaint mechanism | Does not provide |
| MANAGE 1 | Response to risks | Immune-pipeline rejection; HIL escalation | Provides partially |
| MANAGE 2 | Strategies for transparency | Documentation set; audit trail | Provides |
| MANAGE 3 | Maintenance and mitigation | QC scripts; recovery protocol; documentation sweeps | Provides partially |
| MANAGE 4 | Responses to risks over time | Post-market monitoring plan not supplied | Does not provide |

### 2.4 ISO/IEC 42001:2023

| Clause | Topic | What CDSFL supplies | Status |
|---|---|---|---|
| Cl. 4 | Context of the organisation | Out of scope — organisational | Out of scope |
| Cl. 5.1 | Leadership and commitment | Out of scope — organisational | Out of scope |
| Cl. 5.2 | AI policy | Directive layer provides input | Provides partially |
| Cl. 5.3 | Roles, responsibilities, authorities | HIL role; expert-encoding authorship | Provides partially |
| Cl. 6.1 | Actions for risks and opportunities | Falsification discipline as structural risk-addressing mechanism | Provides partially |
| Cl. 6.2 | AI objectives | Mathematical appendix defines formal objectives | Provides partially |
| Cl. 7.1 | Resources | Out of scope — organisational | Out of scope |
| Cl. 7.2 | Competence | Expert encoding tier ladder | Provides partially |
| Cl. 7.3 | Awareness | Out of scope — organisational | Out of scope |
| Cl. 7.4 | Communication | Out of scope — organisational | Out of scope |
| Cl. 7.5 | Documented information | Full documentation set; audit trail; test suite | Provides |
| Cl. 8.1 | Operational planning and control | Composer; directive layering; interaction patterns | Provides partially |
| Cl. 8.2 | AI system impact assessment | Not produced by framework | Does not provide |
| Cl. 8.3 | AI system lifecycle | Admissibility tier ladder; encoding promotion rules | Provides partially |
| Cl. 8.4 | Operational records | Append-only chain; Merkle sealing; immune-pipeline audit trail | Provides |
| Cl. 9.1 | Monitoring, measurement, analysis | Bench test suite; metrics; falsification events | Provides partially |
| Cl. 9.2 | Internal audit | Not supplied — deployment procedure | Does not provide |
| Cl. 9.3 | Management review | Out of scope — organisational | Out of scope |
| Cl. 10.1 | Continual improvement | Falsification-driven revision; documented failure cases | Provides partially |
| Cl. 10.2 | Nonconformity and corrective action | Immune-pipeline rejection; refutation persistence; not a full NCCA process | Provides partially |

---

## 3. Supplementary-Artefact Templates

The templates in this part are drafts. They are intended to be adapted to the specifics of a deployment, and in every case reviewed by qualified legal and compliance professionals before being put into effect. They are written in a form that is close enough to working language that a deployment can use them as a starting point without mistaking them for finished artefacts.

### 3.1 Key-Management Specification (Template)

**Purpose.** To govern the lifecycle of cryptographic keys used by the CDSFL framework, specifically the Ed25519 signing keys that attest findings and the keys protecting the persistence chain.

**Scope.** This specification covers: key generation, key storage, key rotation, key revocation, signing authority, separation of duties, and key-compromise response.

**Generation.** Ed25519 keys shall be generated on [hardware security module / secure enclave / offline air-gapped workstation]. Generation shall use [libsodium / OpenSSL EVP / named HSM API] with entropy drawn from [hardware RNG / OS CSPRNG after 128-bit entropy seeding]. Private-key material shall not leave its generation boundary in cleartext form.

**Storage.** Private keys shall be stored in [HSM / sealed TPM / encrypted key vault]. Access shall require [quorum of N-of-M holders / dual-control MFA / named role attestation]. Public keys and key identifiers shall be published to the persistence chain at the moment of first use.

**Rotation.** Signing keys shall rotate on a [quarterly / annual / event-driven] schedule. Rotation events shall be recorded in the persistence chain as a first-class event type. Old keys shall remain valid for signature verification after rotation, with no retroactive re-signing; keys shall be revoked only for compromise.

**Revocation.** A revocation event shall be published to the persistence chain within [named SLA]. Revocation events shall name the key identifier, the effective revocation timestamp, the reason code, and the signing authority for the revocation itself. Findings signed by a revoked key prior to the revocation timestamp shall retain their signatures but shall be flagged for re-review.

**Signing authority.** Only [named roles] are authorised to invoke the signing key. Attempted signing by any other party shall be logged as a security event. Automated signing for routine findings shall operate under [delegated credential / restricted signing scope]; escalation findings shall require explicit human signing.

**Separation of duties.** Generation authority, storage authority, signing authority, and revocation authority shall be held by distinct roles. No single role shall possess all four.

**Key-compromise response.** A suspected key compromise shall trigger the incident-response protocol (§3.2). Compromise response shall include: immediate revocation, publication of revocation to the chain, re-review of findings signed after the earliest plausible compromise timestamp, and notification of affected parties per the incident-response protocol's notification matrix.

**Record-keeping.** Every key lifecycle event shall be recorded in the persistence chain with at minimum: event type, key identifier, timestamp, authorising role, and reason code.

### 3.2 Incident-Response Protocol (Template)

**Purpose.** To define the procedure by which the deployment responds to incidents affecting the integrity, availability, confidentiality, or governance of the CDSFL framework.

**Definitions.** An *incident* is any event that (a) calls into question the integrity of a finding or chain entry, (b) affects the availability of a production service, (c) exposes information outside its authorised boundary, (d) triggers a regulatory notification obligation, or (e) is designated an incident by the named incident commander.

**Severity tiers.**

| Tier | Criterion | Response SLA |
|---|---|---|
| SEV-1 | Integrity compromise of the persistence chain; suspected key compromise; confirmed external unauthorised access | Within 1 hour |
| SEV-2 | Integrity concern for a specific finding or batch; confirmed erroneous HIL sign-off; production service degraded below defined availability | Within 4 hours |
| SEV-3 | Bug affecting reasoning quality without integrity concern; near-miss; external report requiring investigation | Within 24 hours |
| SEV-4 | Quality issue visible only in post-hoc review; documentation drift with governance implications | Within 5 business days |

**Roles.**

- *Incident commander.* Named on-call role; single point of decision authority during active response.
- *Scribe.* Records timeline, decisions, and actions taken, in the persistence chain.
- *Technical lead.* Directs remediation.
- *Legal/compliance liaison.* Manages external notifications and regulator communications.
- *Communications lead.* Manages internal and external messaging.

**Phases.**

1. *Declare.* Any party may declare a suspected incident. Declaration creates an incident record in the chain.
2. *Triage.* The incident commander assigns severity and activates the role roster.
3. *Contain.* Remediation halts further harm. For integrity incidents, this includes chain-level measures such as adding a contested-findings marker rather than mutating history.
4. *Investigate.* The technical lead identifies root cause.
5. *Remediate.* Fixes are applied; affected findings are re-reviewed; chain entries are added to record the remediation.
6. *Notify.* Regulators, affected parties, and internal stakeholders are notified per the notification matrix.
7. *Close.* The incident record is closed with a post-incident review linked from the chain.
8. *Learn.* A falsifiable post-mortem claim is published and added to the system's open-questions list.

**Notification matrix.** [To be filled per deployment, with specific reference to applicable regulatory obligations such as GDPR Art. 33–34 breach notification, EU AI Act Art. 73 serious-incident reporting, and sector-specific obligations.]

**Record-keeping.** Every phase transition shall be recorded in the persistence chain with at minimum: incident identifier, phase, timestamp, authorising role, and summary.

### 3.3 Third-Party Audit Procedure (Template)

**Purpose.** To define the procedure by which an external auditor examines a CDSFL deployment against applicable governance regimes.

**Scope definition.** The auditor and the deployment shall jointly agree an audit scope document naming: applicable regime(s), in-scope and out-of-scope systems, the review period, sampling approach, access rights, and confidentiality constraints.

**Evidence package.** The following artefacts shall be made available to the auditor on request:

- Full persistence chain for the review period (read-only access).
- Bench test suite and test results for the review period.
- Experimental record for the review period.
- All directive layers, registry TOMLs, and tool manifests in effect during the review period.
- Key-management records per §3.1.
- Incident records per §3.2.
- System and model cards per §3.4.
- DPIAs per §3.6 where applicable.
- Personnel records for authorised signing and HIL roles (scope-limited).
- Change-management records for the framework version in use.

**Access rights.** The auditor shall have read-only access to the persistence chain and supporting documentation. Any write access shall be read-justified and time-bounded. Chain entries created by audit activity shall be marked as such.

**Sampling methodology.** Where full review is impractical, the auditor shall apply a documented sampling methodology. The sampled items, the selection basis, and the non-sampled population shall be named in the final report.

**Interview protocol.** The auditor may interview named roleholders (HIL, incident commanders, expert-encoding authors, signing-key holders). Interviews shall be scheduled and scoped in the audit scope document. Interview notes shall be shared with interviewees for factual verification before final report.

**Reporting format.** The final report shall name: audit scope, methodology, findings (with severity), evidence supporting each finding, and recommended remediation. The report shall distinguish material findings, observations, and improvement opportunities.

**Remediation process.** The deployment shall respond to each material finding within a deployment-defined SLA. Remediation evidence shall be recorded in the persistence chain. A follow-up audit shall verify closure.

**Independence.** The auditor shall have no conflict of interest with the deployment. Audit firm rotation shall follow deployment-defined policy, consistent with applicable regime requirements.

### 3.4 System and Model Card Template

This template is adapted from the Model Cards and System Cards literature. It is intended to be produced per deployment, per model, and updated on any material change.

**System identification.**

- System name:
- System version:
- Deployment organisation:
- Contact:
- First deployed:
- Last updated:

**Purpose and scope.**

- Intended use:
- Intended users:
- Prohibited uses:
- Out-of-scope uses:

**Models in use.**

For each model in the panel:

- Model name and version:
- Provider:
- Access route (API, local, other):
- Role in the framework (panel member, HIL support, specialist cell backer):
- Known limitations at the time of deployment:
- Training data disclosure (to the extent the provider discloses):

**Framework configuration.**

- Directive layers active:
- Interaction-pattern preset(s) in use:
- Cells enabled:
- Tools in the tool manifest:
- HIL role occupants:
- Key-management authority:

**Performance characteristics.**

- Bench test suite status at deployment:
- Experimental-record summary:
- Known failure modes:
- Known strengths:

**Risk and governance.**

- Applicable regimes:
- DPIA status (where applicable):
- Post-market monitoring plan:
- Incident-response protocol owner:
- Complaint-mechanism owner:
- Audit schedule:

**Falsifiable claims.**

- Deployment-specific claims:
- Open questions:

**Change log.**

| Date | Version | Change | Signing authority |
|---|---|---|---|

### 3.5 Complaint Mechanism (Template)

**Purpose.** To provide a mechanism by which affected parties — data subjects, end users, or third parties materially affected by a decision involving the CDSFL framework — can raise a complaint, request review, and seek redress.

**Who may complain.** Any natural person whose data has been processed by the deployment, any end user who has interacted with the deployment, and any third party who has been materially affected by a decision the deployment has taken or supported.

**Channels.**

- Web form at [named URL], available in [named languages].
- Email to [named address], monitored during business hours.
- Postal address for written complaints.
- Accessibility: channels shall meet applicable accessibility standards.

**Acceptance criteria.** A complaint shall be accepted if it names: the complainant, the subject of the complaint, the nature of the harm alleged, and the requested redress. Anonymous complaints may be accepted at deployment discretion.

**Triage SLA.** Acknowledgement within [2 business days]. Initial classification within [5 business days].

**Review process.** A complaint shall be reviewed by a role that was not involved in the original decision. The reviewer shall have access to the full persistence-chain record relevant to the decision. The reviewer's determination shall be recorded in the chain with at minimum: complaint identifier, reviewer role, determination, reasoning, and remedy where applicable.

**Escalation.** The complainant may escalate an unsatisfactory determination to a named independent party within the deployment. Where applicable, the complainant retains the right to complain to the competent supervisory authority.

**Remedies.** Remedies may include: correction of the underlying record; reversal of the decision; compensatory action; formal apology; referral to the incident-response protocol; or such other remedy as the reviewer determines appropriate.

**Record-keeping.** All complaints, determinations, and remedies shall be recorded in the persistence chain. Aggregate statistics shall be included in the deployment's periodic governance reporting.

**No retaliation.** No adverse action shall be taken against a complainant for having raised a complaint in good faith.

### 3.6 Data Protection Impact Assessment (Template)

This template is adapted from the DPIA guidance issued by the European Data Protection Board and the Article 29 Working Party. It is intended to be used only under qualified guidance, and only where processing of personal data is in scope.

**1. Description of the processing.**

- Nature of the processing:
- Scope of the processing:
- Context of the processing:
- Purposes of the processing:
- Controllers and processors:
- Data categories:
- Data subject categories:
- Retention period:
- Recipients:

**2. Necessity and proportionality.**

- Lawful basis:
- Purpose limitation compatibility:
- Data minimisation:
- Accuracy provisions:
- Storage limitation:
- Data-subject rights provisions:
- Processor obligations:
- International transfer safeguards:

**3. Risks to data subjects.**

For each identified risk:

- Risk description:
- Likelihood (low / medium / high):
- Severity (low / medium / high):
- Overall risk level:

**4. Measures to address risk.**

For each risk:

- Existing measures:
- Additional measures proposed:
- Residual risk level:

**5. Framework-specific considerations.**

- Treatment of personal data in the persistence chain: [personal data shall not be written to the append-only chain; where references are unavoidable, they shall be keyed through a separate erasable store].
- HIL review of personal-data decisions: [required / not required].
- Rejection of findings involving personal data under admissibility gates: [named rules].

**6. Consultation.**

- DPO consulted (date):
- Data subjects or representatives consulted (where appropriate):
- Prior consultation with supervisory authority (where applicable):

**7. Sign-off.**

- Author:
- Review:
- Approval:
- Review date:

---

## 4. Versioning and Review

This document is versioned with the CDSFL framework. Substantive changes shall be recorded in the change log below and committed to the persistence chain as a first-class event.

| Date | Change | Authority |
|---|---|---|
| 20 April 2026 | Initial version. Mapping to EU AI Act, GDPR, NIST AI RMF, ISO/IEC 42001. Ten identified gaps. Six supplementary-artefact templates. | CDSFL project |

---

## 5. Final Note on Framing

The CDSFL framework does not claim to solve compliance. It claims to supply technical primitives that modern governance regimes commonly require, to name honestly the primitives it does not supply, and to offer starting-point templates for the supplementary artefacts a deploying organisation must build or procure separately. The project's position on this point is deliberately modest: auditable cognitive infrastructure is a useful thing, and it is a harder thing to retrofit than to build in. What the framework offers is a running system in which the audit trail was never optional. What it does not offer is a legal conclusion about whether any particular use of that system is compliant with any particular regime. That conclusion belongs to qualified professionals acting in the context of a specific deployment.

The framework's authors welcome correction of any specific claim in this document and will update it accordingly when qualified guidance surfaces an error. The discipline the framework applies to its own scientific claims applies equally here: the mapping is offered as falsifiable, and where it is wrong it will be fixed.

---

*CDSFL Compliance Framework. 20 April 2026. Not legal advice. Technical primitives and honest gaps. Templates are drafts, not finished artefacts. See [README.md](../README.md) §8 for the public framing, [PAPER.md](../PAPER.md) Part V for the technical statement, and [EXTENDED_RATIONALE.md](EXTENDED_RATIONALE.md) §Auditable Cognitive Infrastructure for the reasoning behind this document's creation.*
