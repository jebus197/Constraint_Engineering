# The routing repair works, and the literature cell's reader is live

2026-08-04 01:10 BST

## The routing repair — 6 of 8, against a null of 0 of 25

The 2026-08-01 control run locked every escalated finding as irreducible with the
reason *"no model produced a runnable test"*. That reason was false: the ladder's
prompt was code-only and no model was ever given the target document. Repaired at
`1bd7605`.

**Paired replay, not a fresh run.** The SAME findings the ladder went 0-for-25 on
were put through the REAL repaired code — `_apply_routing` itself, with `cfg`
built by `launcher_core.build_runner_config_from_dict` on the shipped config, so
both config-ingestion boundaries were exercised. A fresh experiment produces
different findings and could only give an unpaired number.

| | |
|---|---|
| Null (measured, both pre-repair runs) | **0 resolved / 25** |
| Post-repair, same findings | **6 resolved / 8** |
| Fisher exact, one-sided | **p = 2.5×10⁻⁵** |
| Binomial vs rule-of-three bound (rate ≤ 0.12) | p = 6.7×10⁻⁵ |
| mpmath exact tail (cross-check) | 6.73112×10⁻⁵ — agrees |
| Post-repair rate, 95% Jeffreys interval | 0.75 [0.41, 0.94] |

Resolved by four of the five panel models: Codex ×4, CC2, ChatGPT. Two remain
irreducible, which is the expected residue — some findings genuinely have nothing
runnable to demonstrate.

**Prompt check, in the live call path** (not a unit test): target path present,
full target text present (25–26 k character prompts against a 24 k document),
instructed to open by path, system message says PROSE DOCUMENT, and no longer
tells the model to import a registry module that does not exist on this target.

Cost: 11 dispatches, £1.43–2.31. Raw log:
`adversarial_records/routing_replay_evidence_2026-08-04.log`.

## The literature cell's reader — exercised live for the first time

The founder asked whether the cell demonstrably feeds real material back, and
whether that could be confirmed irrefutably. The honest answer had three parts,
and the third was "never run live". Two of the three are now closed.

**Query construction.** The reported "~6% meaningless fallback" was not findings
with nothing searchable in them. Measured on 274 real archived descriptions:
19 (6.9%) produced the fixed phrase *"pipeline anomaly detection"*, and every one
opened `VERDICT: CONFIRM C0019. <the actual defect>`. `VERDICT` and `CONFIRM` sat
in the machinery label list, so the stripper discarded the segment after them —
the whole description. A good sentence in, the empty string out.

The distinction that fixes it is what a label *introduces*: `FALSIFIER` is
followed by Python and stays machinery; a verdict header is followed by the
reasoning. **Re-measured: 6.9% → 1.5%.** The residual 1.5% now return empty and
are skipped and counted, because a query that cannot be about the finding burns a
retrieval and risks an unrelated paper the reader may over-rate.

**The relevance reader.** Previously wired but never exercised. Run live
2026-08-04 01:00 BST against a real target and paper text:

    reader_model : 'haiku'      relevance : HIGH      error : ''
    elapsed      : 10.0 s       brief     : 528 chars, correctly identifying
                                            the paper's bearing on the target
    passes require_model_reader : True

**Guard verified, not assumed.** A concern that a fallback-judged brief might slip
past `require_model_reader` was checked and is unfounded: the guard tests
`reader_model` and refuses `None`, `""` and `"extractive_fallback"` alike.

## What remains before the cell influences a run

Only the config flip. `inject_brief` and `c_ext_enabled` exist, are tested, and
default off; no archived run has ever had injection enabled. Every component
beneath them is now proven live and separately. Holding the flip is a scheduling
decision, not a readiness one: chemistry and engineering already ran with the cell
observing only, so switching it to influencing mid-arc would confound the
capstone's four-way comparison.

Written under CDSFL note standard v1.2 (14 May 2026).
