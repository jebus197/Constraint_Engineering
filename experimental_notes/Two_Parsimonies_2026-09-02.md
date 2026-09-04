# Two Parsimonies: What The Panel Answered About Simplest Sufficient Fix

**2026-09-02 18:54 BST** — analysis, no code change. Sources: `bench/logs/confer_stage1_audit_2026-08-18/BRIEF.md` (read end-to-end); `experimental_notes/Panel_Stage1_Audit_FULL_RECORD_2026-08-18.md`, questions 2 and 5, all five models, read in full; the project's correction commits from 2026-08-14 to 2026-09-02.

## The question that was already asked and answered

On 18 August a five-model panel (Gemini 3.1 Pro, ChatGPT GPT-5.5, Codex GPT-5.5, DeepSeek V4 Pro, Claude Opus 4.7) was asked whether the Bugzilla model of defect resolution survives translation from software to STEM research, and specifically whether the principle of the "simplest sufficient fix" survives with it. Four of the five said it does not survive intact. The sharpest statement came from Opus 4.7: in Bugzilla, parsimony is a maintenance virtue, meaning minimise the risk of breaking code you own; in science, parsimony is an epistemic claim about explanations, in the tradition of Ockham; and the two coincide only sometimes. Gemini put the same point differently: nature does not optimise for patch parsimony. DeepSeek added that a false claim is not repaired by a small patch at all, because false claims require new evidence.

## The distinction

There are two different parsimonies wearing one name.

Maintenance parsimony asks for the smallest change to an artefact under the maintainer's control. It is safe because sufficiency is cheap to establish: the test suite runs in seconds and either passes or does not. Because the check is cheap, it can be applied to every candidate, and simplicity can then be used freely to choose among the candidates that passed.

Epistemic parsimony, the razor attributed to Ockham, says that entities are not to be multiplied beyond necessity. The governing clause is "beyond necessity". The razor only ever ranks explanations that already account for the whole of the evidence. An explanation that does not account for the evidence is not a simpler competitor; it is not a competitor at all.

The two are two sides of one coin only where something enforces the sufficiency side. In Bugzilla that enforcement is structural: a defect cannot be moved into the resolved state without a fix that demonstrably makes the failing case pass. Every member of the resolved set is therefore already sufficient, and preferring the smallest member of that set costs nothing. Remove the enforcement and the coin has one face. The unfiltered set contains every candidate, sufficient or not, and the smallest member of an unfiltered set is not the best explanation. It is the first plausible thing that came to mind.

## What the founder's ruling resolved that the panel did not credit

The panel's strongest objection was that Bugzilla's duplicate relation is an equivalence relation on causes in a single inspectable codebase, whereas the harness's duplicate relation is a similarity judgement over prose, and that importing Bugzilla's confidence in duplicate-marking imports confidence the harness has not earned. The runner records this as a known limitation in terms: location-only keying cannot see a second distinct defect in an already-flagged function (`bench/reference_runner_v3.py:6457`).

The founder's ruling does not import the confidence. It imports the record. Duplicates are preserved with pointers rather than discarded; a resolution must be demonstrated effective rather than merely plausible; and the resolution is explicitly provisional, kept on file in the event that the fix adopted needs to be revisited. Those four properties are what make a small fix safe, and they are properties of the state machine surrounding the fix, not of the fix's size. An unreliable duplicate relation is tolerable inside such a record because a wrong duplicate mark is recoverable. It is not tolerable in a lossy record.

The consequence for the mathematical model agrees with the panel's own recommendation: parsimony belongs in the process, not as a scoring term in the convergence gate. Two panellists gave independent reasons. Any computable proxy for simplicity, such as diff size or token count, is open to being gamed by a model that has been told it is scored on it; and a parsimony term would let a run register convergence because proposed fixes got shorter, which is not the property the gate exists to certify.

## A thesis proposed and refuted in the same session

The first reading drawn from this material was that the harness author's failures were failures of lossiness: that each defective fix destroyed the thing it superseded. Three cases fit well. A finding-absorption rule deleted findings rather than marking them duplicate; a filter for simulated content excluded nine genuine panel transcripts rather than labelling them; and an acceptance gate discarded a seventy-seven kilobyte patch because the covering message was short.

The full correction record refutes the thesis as a general claim. Across forty-six correction commits between 2026-08-14 and 2026-09-02, vocabulary indicating destruction or exclusion of existing data appears in five, which is 10.9 percent, with a 95 percent Wilson confidence interval from 4.7 to 23.0 percent. The interval was computed twice, once with statsmodels and once from the closed-form expression through scipy, and the two agree to machine precision. The remaining eighty-nine percent are claim-class: incorrect statements about data that was intact and available to be checked. The boundary on this measurement is that the classifier reads commit subject lines, so it measures how each defect was described at the time of its fix, not the defect itself.

The refutation sharpens rather than weakens the conclusion. The dominant failure is not discarding evidence. It is treating a simple reading of the evidence as an established one, before the set it quantifies over has been checked. That is epistemic parsimony applied without its governing clause.

## The connection to the process question

The same panel was asked, in the same session, whether the author's self-diagnosis of that failure was sufficient. All five said it was necessary but not sufficient, and each proposed the same mechanical remedy in different words: no claim quantified over a set may stand without the exact command that enumerates the set and the count of members checked, run before the claim is written rather than after. DeepSeek stated the missing discipline plainly: the cheapest refuting command should be run before the claim is made. Opus 4.7 went further on the mechanism, observing that in each traced case the single member checked was the one named in the prose the author was working from, so the failure was not sampling but treating prose citations as an index into the code; and that on this failure mode a panel briefed with a narrative summary is worse than useless, because five models agreeing on an inherited error produces confidence rather than correction. Its remedy was to withhold the conclusion from the brief and supply the tool instead: not "the gate reads the settled series, verify", but "here is the repository and the run archive, determine what the gate reads".

The two questions turn out to be one question. A claim asserted after checking one member of a set is a fix that is simple without having been shown sufficient. The remedy the panel proposed for the process question is the same remedy the Bugzilla model supplies for the resolution question: make the sufficiency check a precondition of the state transition, so that simplicity operates only inside the set that has already passed.
