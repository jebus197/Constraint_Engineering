# Pre-Launch Review, Round Two — What the Panel Examined and What Came of It

2026-05-10 19:30 BST

## What this note is

This is the plain-English companion to the technical record of the second pre-launch expert-review round for Experiment 40 in the project's current experimental arc. The arc runs from Experiment 40 to Experiment 54. The first round, in April, reviewed the whole plan end to end. This second round focused on items that the April review had not directly examined and that a founder oversight session in late April had flagged as needing panel input before the first experiment launches.

## How a review round works, briefly

The project's review rounds use a panel of five large language models from different vendors, run independently with no cross-talk between them. Each model receives the same set of questions and is required to give a single definitive answer per question, not a list of options. The agent then synthesises what the panel agreed on, where they disagreed, and what should be folded into the project. The aim is to spare the founder from refereeing technical disagreements between expert systems they are not themselves expert in.

For this round, all five panel slots had been updated to current-frontier model versions earlier in the day. Anthropic's Claude moved to a new Opus version. OpenAI's GPT moved a minor version forward in the two slots that use it. Gemini moved its access route from Google's direct API to a third-party gateway to draw on existing prepaid credits at the same price tier. DeepSeek moved from its older Reasoner model to a newer V4 Pro architecture (the older endpoint had been retired by DeepSeek). Each upgraded route was smoke-tested against a simple known-answer prompt before dispatch, and all four returned schema-conforming responses with the right verdict.

## The five questions Round Two addressed

The first asked the panel to look at a small code correction that had been applied to one of the project's logging paths during the overnight gap-closure shift in April. The correction renamed two keys in a structured-data record so that they matched the actual field names of an underlying data type rather than placeholders that resolved to nothing. The question was whether the fix was correct on the merits and whether the regression tests around it were sufficient to prevent the issue from recurring.

The second asked the panel to evaluate the scope briefs for four test articles that have to be drafted ahead of their respective experiments. These four experiments cover biology, physics, chemistry, and engineering, and each requires a short purpose-built target module (about fifteen to twenty-five thousand characters each) containing four to five clusters of falsifiable claims. The panel was asked whether the briefs were sufficient to exercise the relevant specialist's verification tools at the depth the experiment intends.

The third asked the panel to evaluate the trigger specifications for three further gaps in the runner code that the project deliberately leaves un-implemented at design time. These three concern arbitration rules for cases where specialist subsystems disagree, where a merge between their outputs deadlocks, and where a burst-dispatch mode would need a convergence override. Rather than guessing the correct rules in advance, the project waits for actual post-mortem evidence and writes the rule from observed cases.

The fourth (optional) asked the panel to evaluate the broader policy of trigger-and-wait versus implement-now for those three gaps. This is the Popperian-falsification side of the project speaking: rules built from observed evidence beat rules guessed in advance, but the policy is worth examining periodically.

The fifth asked the panel to evaluate four residual concerns that the founder had raised in a late-April oversight session and that the agent had closed earlier in the day on a directive that explicitly rejected deferral. The four concerns were: a cross-check that the project's first-of-the-arc gate experiment was correctly recorded as complete; an assessment of whether tracking a specific mathematical measurement over time would block any planned experiment; an amendment to the project's locked note-writing standard to formalise a scientific-notation rule that had previously caused a misreading; and a retroactive labelling sweep across the project documentation to apply the maturity-state vocabulary consistently. The panel was asked to ratify or refute the closures on the merits — not to recommend deferral, because the founder had already adjudicated that question.

## What the panel said

On the first question, the code fix, all five models agreed: correct on the merits, regression tests sufficient. Two of them flagged a forward-going consideration relevant to a later experimental analysis (severity information lives on a different data type and would need to be joined back if a downstream calculation needed it), but this was a note for later, not a fix to the current site.

On the second question, the scope briefs, four of five flagged that the biology test article's brief did not exercise one of the specialist's available verification routes (a constraint-solver path), and the same four flagged that the example of an intentional false claim in the biology brief was technically a category error. Both of those corrections were folded into the plan in the same session.

On the third question, the trigger specifications, four of five endorsed the existing structure. The fifth (DeepSeek) argued substantively that the originally-named trigger experiment did not in fact include the multi-specialist interaction that would produce the kind of conflict or deadlock the gaps describe. The first experiment in the arc that does produce that interaction is several places further along. The migration clause in the existing text already handled this technically, but the wording would benefit from being made explicit. A clarifying paragraph was added to the plan in the same session.

On the fourth question, all five agreed that trigger-and-wait is the correct policy for all three gaps. One added a useful refinement: build the instrumentation now (the logging fields and replay scaffolding) without building the arbitration rule itself, so that when the trigger fires the necessary observation infrastructure is already in place.

On the fifth question, all five endorsed the closure of three of the four residual concerns on the merits. The fourth concern — the maturity-state labelling sweep — included a specific labelling decision for a debug-time safety check that did not fit cleanly into any of the existing three labels. Three of the five models argued for one label, two argued for a different label, and the panel did not converge.

## What was folded in immediately

The biology test-article brief gained a new claim cluster covering boolean and logical relationships among genes, with the relevant constraint-solver as the falsifiability route. The same brief's example of an intentional false claim was rewritten to attach the codon-level error to a nucleotide sequence (where codons actually exist) rather than to a protein sequence (where they do not).

The gap-trigger specifications gained a clarifying paragraph explaining the expectation that the first-named trigger experiment is structurally unlikely to surface the relevant phenomena, with the later experiment being the realistic primary site. The migration logic was already correct; the change was wording.

The technical record of the round, this plain-English companion, and a third-format read-aloud file were prepared as paired artefacts.

## What was left open for further review

The disagreement on the third question (which experiment is the realistic primary trigger), although resolved through the migration clause, deserved a follow-up round to lock the wording rather than leaving it half-handled. The split on the maturity-state label for the debug-time safety check needed either a fourth label adopted or a clean defence of one of the existing three. Several smaller refinements to other later-arc test articles had been flagged by two of the five models but had not drawn majority support; those needed a focused yes-or-no per refinement under further questioning. These items collectively prompted a third review round shortly afterwards, which closed them.

## What this round accomplished in the larger picture

Round Two filled the panel-review gap that the late-April founder oversight session had named. Combined with the April plan review, it brought every item that touched Experiment 40's pre-launch state under expert panel scrutiny except the residual divergences that motivated Round Three. The runtime code for Experiment 40 was already closed; this round was about confirming that the plan and the supporting infrastructure around the launch were sound.

The wall-clock cost was about three minutes for the panel to respond in parallel (the slowest model finished at 185 seconds), plus the synthesis and fold-in work that followed.

## What to read alongside this

The technical companion to this note carries the full per-model responses and the detailed convergence record. The agent operational tracker carries the next-step pointer. The consolidated plan carries the full design briefs and trigger specifications. The third-round outcome note carries the resolution of the items left open here.

Written under CDSFL note standard v1.2 (14 May 2026).
