# The steering surface simulated: 5 cases, 2 escalations, and 1 finding that changes the design

12 November 2026, 06:10 UTC

## Summary

The domain steering surface was run in simulation, as instructed, with a small model answering as a harness seat and the orchestrator acting as the human in the loop. 5 task descriptions were put through the proposer; 3 were expected to resolve cleanly and 2 to escalate. The proposer named the correct domain in 5 of 5 cases and the correct subdomain in 4 of 5. 2 cases escalated to a dialogue, so the escalation path was exercised rather than merely described. 1 escalation produced a finding that changes the design: the domain that owns a task and the domain that owns its consequence scale can differ, and a surface returning a single domain conflates them.

## 1. What was simulated, and what was deliberately not

The proposer reads a task's text and offers a domain and subdomain, with an explicit ambiguity flag. It proposes and never decides. Where the proposal is ambiguous, the surface asks; a seat answers; the human in the loop adjudicates.

What was not simulated is the visual interface. That belongs to the authoritative design brief. What was simulated is the decision path, because that is the part whose failure would be silent.

The acceptance condition was fixed before the run and is not that a conversation is possible. It is that unambiguous cases resolve without a dialogue, and that an ambiguous case escalates rather than returning a confident wrong answer. A run in which all 5 cases resolved cleanly would not have tested the escalation path at all.

## 2. The proposer, and why its vocabulary is not hand-written

Scoring is the overlap between the task's content words and the distinctive terms of each candidate's own expert encoding, read through the single vocabulary reader. A term appearing in more than half the encodings is dropped, because a word in every box separates nothing. Overlap is normalised by the square root of the box's vocabulary size, so a long encoding cannot win on length alone: the 22 encodings written on the 12th of November run 109 to 142 lines against a mean of 65.2 lines for the 28 older ones, and a raw count would have handed every verdict to the newer files.

40 candidates carry a distinctive vocabulary, from 156 to 317 terms each. None of those lists was written by hand. A hand-written keyword list would be a second source of truth about what a domain is, and would drift from the manifest the moment a subdomain was re-pathed.

## 3. Ambiguity is measured at domain level, and the first version got that wrong

The first run flagged ambiguity whenever the top 2 candidates were close, whatever domains they belonged to. It scored the domain correctly 4 times out of 4 and the ambiguity signal correctly only 2 times out of 4.

The repair was not a threshold adjustment. It was a correction about what the surface is for. The consequence scale, the critical level and the encoding are all properties of the domain, so 2 subdomains of 1 domain share all 3 and a close call between them changes nothing a researcher needs to confirm. A close call between 2 domains changes which scale a finding is judged on. Ambiguity is therefore measured against the nearest candidate in a different domain, and a contest confined to 1 domain is reported as settled.

A proof-theory task illustrates the difference: it scored mathematics proof first and mathematics applied second, which the original rule would have escalated for no gain, because both carry the same scale.

## 4. The 5 cases and their results

| case | subject | proposed | ambiguous | nearest other domain |
|---|---|---|---|---|
| A | a phase 2 trial toxicity halt decision | biology / zoology | yes | cross_domain |
| B | replica divergence after a healed partition | software / distributed | no | information_science |
| C | whether monotone decrease implies convergence | mathematics / proof | no | biology |
| D | thermal and electrical coupling in a cell pack | cross_domain / thermal_electrical | no | logistics |
| E | a pooled hazard ratio from 3 unlike sites | statistics / experimental_design | yes | information_science |

Against the assignment the human in the loop would make, stated per case before the proposal was read:

- domain correct: 5 of 5, a proportion of 1.000000, with a Wilson 95 per cent interval from 0.565518 to 1.000000 and a Clopper-Pearson interval from 0.478176 to 1.000000.
- subdomain correct: 4 of 5, a proportion of 0.800000, Wilson from 0.375535 to 0.963776, Clopper-Pearson from 0.283582 to 0.994949.

The single subdomain miss is case A, where a phase 2 clinical trial was offered the zoology box rather than the biomedical one. That case had already been flagged ambiguous, so the escalation path had the opportunity to catch it. The pattern is the right way round: the proposer is stronger on the domain, which selects the consequence scale, than on the subdomain, which only selects which encoding file is loaded.

The intervals are wide because 5 cases is a demonstration and not a sample. They are reported because the standing rule attaches an interval to every proportion; the 5 of 5 and 4 of 5 are the evidence.

## 5. The 2 escalations, and what the seat said

Both ambiguous cases were put to a seat as a 3-field question: name the domain, justify it in terms of consequence, and state what would refute the answer. The seat was given the competing domains and their declared scales but not the proposer's numeric scores, which ran from 0.054365 to 0.613139 across the 5 cases.

**Case A.** The seat named biology, on the ground that the harm measured is toxicity to enrolled patients and the protocol's own stopping rule already measures it on that scale. It named as its refuting condition a fact showing the consequence reaches beyond patient harm into a harm the clinical scale does not measure. The human in the loop confirmed the domain and overrode the subdomain from zoology to biomedical. The escalation confirmed the proposer's leading domain rather than changing it, which is the outcome the design predicts for a case where the leader is right and the margin is merely narrow.

**Case E, and this is the one that matters.** The proposer offered statistics. The seat named biology, and its reasoning follows the manifest's own rule rather than contradicting it: statistics declares no scale of its own, with the stated reason that a statistical error's consequence belongs to the application the statistics serve. The application here is a vaccine dosing claim, so the consequence is patient harm, measured on the clinical scale. Its refuting condition was a fact showing the estimate feeds only an internal methods audit with no patient-facing claim attached.

## 6. The finding that changes the design

The seat and the proposer were answering 2 different questions and both answers were correct.

The task's subject is statistics: what is at issue is whether a pooled estimate from unlike sites is admissible, and the encoding a seat needs is the statistics box. The task's consequence scale is biology's, inherited, because statistics declares none and the application is patient-facing.

So a steering surface that returns one domain conflates 2 separable things: which encoding to load, and which scale to judge the finding on. For the 4 domains that declare an external standard the 2 coincide. For the 5 that declare none, and for the 1 that declares a composed scale, they can differ, and the severity_scale of none declaration, with its stated reason, is exactly what makes them differ. 6 of the 10 declared domains are therefore affected.

The surface should resolve and record both: the subject domain, which selects the encoding, and the scale domain, which selects the consequence ordering and the critical level. Where the subject domain declares a scale, the 2 are the same and nothing changes. Where it declares none, the scale domain is what the inheritance resolves to, and it is the one a finding must be judged against.

This was not visible from the design. It was surfaced by an independent seat disagreeing with a construction the orchestrator had written, which is the reason the dialogue was run with a separate model rather than adjudicated alone.

## 7. What this does not establish

5 cases demonstrate that the path works on 5 cases. They do not establish an accuracy figure beyond the 5 of 5 and 4 of 5 reported above: the tasks were written by the same party that wrote the proposer, which is a selection risk running toward the flattering conclusion, and the human in the loop's assignments are that party's judgement rather than an independent label.

The margin threshold is a judgement and is labelled as one. No measurement here relates a margin to an outcome, so it must not be cited as derived.

The seat's 2 answers are a model's reasoning, not a verdict. Under this project's rule a finding is confirmed programmatically or by the human in the loop, never by a model's vote, and the design finding in section 6 is recorded as the orchestrator's adjudication of what the seat raised, not as the seat's ruling.

## Related

The domain steering surface and the vocabulary behind it is the companion document to this record. The authoritative design brief covers the interface itself.

Written under CDSFL note standard v1.9 (1 November 2026).
