# Panel Review. Adapting The Instrument From Code To Prose

**Preserved into the repository 2026-08-06 02:15 .** The 5-model panel review on adapting the instrument from code to prose. LOAD-BEARING: `OUTSTANDING_QUEUE_to_BR2.md` cites this file as where the panel's DISSENT is recorded, and preserved disagreement is the whole point of `pr` as against the retired compelled-convergence directive. Until now that artefact existed on one machine only.

**Provenance.** This is the plain-text text-to-speech document from `~/Desktop/CDSFL_tts/Panel_Review_Prose_Adaptation_2026-08-01.txt`,
preserved VERBATIM below rather than rewritten. It is a record, and rewriting a record is a fault in
this project. It was cited by name in `OUTSTANDING_QUEUE_to_BR2.md`
while existing on one machine's Desktop only — and `resources/RECOVERY.md` opens by promising a reader
can rebuild everything from the repository alone. That promise now holds for this document.

---

Panel Review. Adapting The Instrument From Code To Prose

2026-08-01, 11:30 BST. Supersedes the 10:35 version, which was written before the fifth model answered.


What Was Asked And What Came Back

Five models were asked to examine everything uncovered over the past day, to evaluate the founder's proposed fix, to judge whether the instrument is merely buggy or unfit for prose, and to converge on one definitive way forward. This assistant participated with its own position rather than only collating, which is a departure from normal practice.

All five completed. The Anthropic seat was nearly lost: it exhausted three five minute windows and then a fifteen minute one. That was diagnosed wrongly at first as a timeout problem. It was not. That seat answers the same question in under a minute when asked for a bounded reply, and had simply been writing at unlimited length. It was the last to speak, it saw the other four positions, and it produced the sharpest answer of the five. It corrected all four of them and it corrected this assistant.

Where the panel disagreed, the disagreement is recorded rather than smoothed away.


The Founder's Own Hypothesis Was Confirmed, Unanimously

Every model independently reached the conclusion the founder proposed: the mathematical framework is sound and is not implicated. The decay curve, the convergence gate and the risk trajectory are independent of what the target is made of. What failed is the mechanical layer bridging that framework to the document, which was written when every target was a Python module and was never adapted.

One model put the diagnostic test crisply. On a prose target, a parsing failure says wrong substrate, not bad fix. The machinery could not tell those apart, and it could not tell them apart silently.


What Was Actually Broken

Seven distinct faults of one kind were found in a single day, all reproduced by execution rather than argued. Each is a mechanism built for code, quietly applied to prose.

Two of them jammed the run. Fixes were rejected because the document would not parse as computer code, so nothing could ever be resolved. And falsifiers written for prose, which necessarily open the document and examine its text rather than importing it as a module, were discarded before they ran and the models were recorded as having failed. Both were active for every round of both attempts at the control experiment.

The worst fault was introduced by this assistant while repairing the first. Removing the parse barrier exposed that the quality gates behind it were incapable of failing on a prose target. One measures how much English was added. Another cannot read the file at all and reports a clean result forever, at the heaviest weight in the calculation. A third is permanently unavailable. Measured end to end against the real document, a fix that injects a destructive shell command scored full marks and was admitted, while a correct prose fix scored lower. The ranking was inverted and nothing could ever be rejected.

That is a loud failure converted into a silent one, and it is the more dangerous direction. It was the second time in one day the same class of error was made.


The Decision The Panel Reached

Unanimous, with no dissent on any of it.

Disable the fix scoring pipeline for prose targets. Do not repair it in place. Critically, when it is disabled it must report that it has no score, not report a passing score. Two models stated independently that a gate which cannot fail is more dangerous than no gate, because it presents an unmeasured fix as a measured one.

Block the code analysis tools from ever seeing a whole prose document.

Tell the panel why its fixes were rejected. Fifty rejections occurred across four rounds and not one model was informed. A frontier model shown a parse error about leading zeros, against a fix it wrote for a prose document, does not conclude its fix was bad. It concludes the harness is reading prose as code. That is a better detector of mechanical failure than any counter.


The Single Best Idea, And How The Last Seat Corrected It

Declare what kind of thing each target is, and refuse to launch when the machinery does not match it.

The check costs nothing. It reads the configuration before any model is contacted. Applied to the eight prose experiments already queued, every one of them fails all three basic tests: fix scoring switched on for a document target, no test suite so one gate can never report, and a threshold set to admit everything.

Every fault found today would have been caught by that check, for nothing, before a penny was spent. Roughly thirteen hours of paid work across two halted attempts went into discovering what a short script would have refused to start.

The correction matters. Three seats proposed enforcing this by setting a switch in the eight configuration files. The last seat refused to sign that, and it is right. A setting that lives only in a configuration file is exactly what the launcher has silently discarded six times in this project's history. Its words were that it would not sign any plan whose enforcement lives in a configuration file. The target type must be detected in the harness itself and the scoring pipeline forced off there, with the configuration merely declaring intent.


Two Corrections That Change The Recommendation

The last seat found that the destructive command used to demonstrate the inverted ranking was placed inside a code listing. Two other seats had proposed, as the future path, extracting those listings and analysing them. That would not have caught it. The conclusion is that such analysis may only ever act as a veto, able to reject a fix, and must never contribute a passing score. This assistant missed that too.

It also found that one seat's proposal, to make unresolvable findings block progress until a human clears them, would have reproduced today's halt by a second route. That part of the founder's design, that such findings must not block, was already correct and must not be reversed.


The Founder's Proposed Design

Endorsed, with one addition, by every model that examined it.

The design was that a classifier flags an item as possibly beyond mechanical resolution, that flag is a signal rather than a verdict, the item goes to the panel to adjudicate, and only on their agreement does it reach human review, without blocking progress in the meantime.

Two thirds of it is already built. Items of that kind already do not block the finishing decision.

The addition is the one that makes it work. Without the rejection evidence attached, the panel would adjudicate blind and would have endorsed today's fault as genuine difficulty. One model set out the reasoning the panel would have followed: this finding is hard to verify, therefore it cannot be resolved, therefore it can be set aside. The true state was that the harness was reading prose as code, so every fix was rejected mechanically. With the evidence attached, the design becomes a better fault detector than the alarm it replaces.


The Free Test Nobody Else Proposed

The last seat observed that none of the other four, this assistant included, had made the acceptance test compulsory, and that the constraint binding hardest here is money, and the test is free.

The demonstration run by hand this morning, in which a destructive fix scored full marks and a correct one scored lower, should become a permanent offline test: the real control document, the destructive fix, the correct fix, and an assertion that neither is admitted, neither closes a finding, and the risk estimate does not fall. It runs locally in seconds and it is the single thing that would have caught this assistant's bad repair at the moment it was made.


The Evidence That The Instrument Already Works On Maths In Prose

A reasonable worry about all of the above is that disabling the fix scoring pipeline for prose amounts to a refusal to handle any target where logic and mathematics live side by side in ordinary language. A structural engineering problem, say. That worry is answerable from the record, and the answer is reassuring.

Two such experiments have already been run. The chemistry exam and the engineering exam are exactly that kind of target: buckling loads, factors of safety, unit algebra, molar masses, all argued in prose. Both converged, at rounds five and six. Thirty one of thirty two criticals in one, and thirty one of thirty one in the other, were confirmed by a runnable demonstration and then closed.

They did that while the fix scoring pipeline rejected every single proposed fix. All thirty one and all thirty two scored zero. The parse barrier described earlier was already in force, so the pipeline contributed nothing but rejections, and the experiments succeeded regardless.

The reason is that findings are not resolved by the scoring pipeline. They are resolved by a falsifier: a short program that computes the true value and compares it against what the document claims. For a mathematical claim in prose that is entirely natural and it is what actually did the work in both experiments.

So disabling the scoring pipeline for prose changes almost nothing that was working. It was already disabled, by accident. What changes is honesty. Instead of stamping every fix as rejected, which reads as a judgement that the fix was poor when it really means the machinery could not read the file, it will report that it has no score to give.

There is a second point that runs in the project's favour. A rejected fix pushes the risk estimate upward, which makes finishing harder, not easier. Both experiments therefore converged against a headwind from a broken gate, so their results are conservative rather than inflated. The repair made this morning would have reversed that, pushing the estimate down on every fix and pulling the finish forward on evidence that did not exist. The danger was in the repair, not in the disabling.

What genuinely remains unsolved is narrower than prose. There is no way to score a proposed edit to a document. For a review exercise, whose product is demonstrated findings rather than applied edits, that does not bite. It would bite only if the panel were ever asked to repair a document and be judged on the repair. That is what the structural checks proposed for later are for, and it is correctly filed as later rather than now.

Where The Panel Genuinely Disagreed

Two splits, preserved rather than resolved.

On naming. One model calls the faults stragglers within a well defined unsound region. The other four call it structural unfitness. One observed correctly that this is a naming disagreement and not an action disagreement, since all five converge on the same operational rule: any mechanism treating a whole prose document as computer source is invalid and must be disabled or replaced. The last seat was blunter, noting that the model arguing for stragglers then spent two paragraphs describing a region that must be replaced rather than repaired, so its headline contradicts its own body.

On the alarm. One model wants the queue threshold removed entirely. The other four want it kept but retargeted, so that instead of refusing to finish it halts, notifies, and attaches the evidence. The last seat named the removal proposal for what it is: this assistant's own error, promoted to architecture. That alarm was correct today, it was suppressed twice, and deleting it because it proved inconvenient would discard the only instrument that noticed anything was wrong.

Worth recording: the model proposing removal had earlier proposed raising the threshold to two hundred, which was precisely the error made twice this morning. Two other models rejected that independently and named it as the error it was, without being told which position belonged to whom. The panel caught the mistake from inside.


Cost

The review itself cost single digits. Five seats, two rounds, no tools.

The recommended work requires no paid runs at all before the next experiment can start. The type detection, the refusal to launch, and the offline acceptance test are all local. Disabling the scoring pipeline is a code change. Surfacing rejection reasons changes what the panel is told. The structural quality gates proposed for a future prose scoring stage are the only part needing calibration, and they belong after the immediate work, calibrated on local fixtures before they are ever allowed to admit anything.


Written under CDSFL note standard v1.2 (14 May 2026).
