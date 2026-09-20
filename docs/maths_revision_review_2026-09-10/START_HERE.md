# CDSFL mathematical review suite

Prepared for George Jackson | 10 September 2026 | Proposed mathematical revision 1.1

This package contains the complete mathematical review and revision materials produced in this work. Adoption remains undecided. The calculations have stated assumptions; empirical calibration, broad STEM usefulness, and historical novelty remain open questions.

## Start here

For a convenient reading copy, open **READING_COPY.pdf**. It contains the current specification, lineage explanation, experimental plan, preceding critique, panel brief, and response template. **READING_COPY.html** contains the same documents as an offline browser reading copy with native mathematical markup. Neither reading copy needs an internet connection to display its contents; external source links naturally require one.

For an initially independent panel review, read **PANEL_REVIEW_BRIEF.md first** and follow its source-first sequence before opening the reading copy, previous critique, or test results.

All substantive documents are also included as editable Markdown. Their equations and wording are the authoritative review sources. The PDF uses high-resolution equation images; the HTML and Markdown preserve editable mathematical expressions.

## Main documents

1. [Revised mathematical specification](outputs/CDSFL_revised_model_specification.md): compact and expanded forms, derivation, assumptions, worked cases, severe testing, circularity checks, and a self-audit.
2. [Lineage and decay clarification](outputs/CDSFL_lineage_and_decay_clarification.md): exact links to the original model and the continuing role of coverage and discovery-rate curves.
3. [Experimental validation and falsification plan](outputs/CDSFL_revised_model_validation_plan.md): a staged programme beginning with independently resolvable tasks.
4. [Preceding mathematical review](outputs/CDSFL_mathematical_review_2026-09-09.md): original criticisms, counterexamples, and bounded conclusions.
5. [Panel review brief](PANEL_REVIEW_BRIEF.md) and [individual response template](PANEL_REVIEW_RESPONSE_TEMPLATE.md).

## Checks and recorded results

The Python checks use the standard library. They do not contact models or external services.

From the extracted package directory, reviewers who wish to execute them can run:

    python3 outputs/CDSFL_math_counterexamples.py
    python3 outputs/CDSFL_revised_model_checks.py
    python3 outputs/CDSFL_severe_testing_checks.py

The exact reference arithmetic is in [CDSFL_revised_core.py](outputs/CDSFL_revised_core.py). Recorded results are [the main report](outputs/CDSFL_revised_model_check_results.json) and [the severe-test report](outputs/CDSFL_severe_testing_check_results.json).

These tests check mathematical consequences in constructed worlds. Their case counts are not empirical samples or probabilities that the framework is correct.

## Original material and history

- **work/math-review/**: the four frozen original source documents and the supplied transcript concerning circular reasoning.
- **work/revision-core/**: separate derivation and checks.
- **work/revision-challenge/**: counterexamples and challenge records, including the abstention correction.
- **work/revision-validation/**: validation-design material and the surviving final-review note.
- **work/revision-history/**: earlier proposal versions and explanatory history.
- **outputs/CDSFL_revision_plan_and_log.md**: chronological work and correction record.
- **outputs/CDSFL_revision_checkpoint.md**: current status and future work.
- **outputs/CDSFL_revision_input_manifest.json** and **outputs/CDSFL_revision_final_manifest.json**: source and review-file provenance.

The original repository snapshot is commit **9e3dfe9d68b428acb98e65c0ad3800ec571a4da4** of jebus197/Constraint_Engineering. The package includes the four source documents examined, not the entire software repository. Links inside those unchanged source documents may refer to other files in the full repository.

A qualification about the archive: work/revision-validation/final_review.md was present on disk despite the corresponding additional agent turn ending with a usage-limit error. It is retained as a surviving note; that interrupted pass was not counted as completed supporting evidence. The earlier validation-design pass did complete.

The supplied transcript is source material for the circularity concern. Its claims about particular current proofs, models, or companies were not independently verified or used to establish the revision.

## How to treat heterogeneous review

The proposal may be accepted, amended, rejected, or left unresolved. Different reviewers can reveal different blind spots, but different names or architectures do not establish statistical independence. Record an individual derivation and critique before comparing conclusions where practical, and resolve disagreements through inspectable arguments and external evidence.

Existing delegated reviews in this archive used instances of the same model and shared some context or assumptions. They are not presented as the heterogeneous external panel proposed by the founder.

## Integrity and package verification

PACKAGE_MANIFEST.json records the SHA-256 digest of each included file other than itself. Run:

    python3 VERIFY_PACKAGE.py

This checks file integrity only. [PACKAGE_CHECKS.md](PACKAGE_CHECKS.md) records archive assembly and portability checks; [PACKAGE_ASSEMBLY_LOG.md](PACKAGE_ASSEMBLY_LOG.md) records the packaging plan, interruptions, and completion. The packaging audit and reading-copy checks are preserved under **work/package-audit/**. Nothing in the archive authorizes repository changes, external communications, purchases, or deployment.

The package preserves the distinction between the scientific proposal and the harness built to investigate it. No software implementation is required to examine its mathematics or design an independent test.
