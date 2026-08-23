# The panel has never once recorded two models finding the same thing, and four of the components that decide when a run ends have never been tested.

23 August 2026


## Why This Was Measured

The founder asked what a six model panel working in turn buys over one capable model, and pointed out that the star arrangement and the machinery built over the preceding months exist precisely to answer that question. The build experiment of 22 August used a serial ladder instead, and so could not answer it at all.

The archive can answer it, because the existing runner puts every model on the same target in the same round. So the question was put to the archive rather than argued about.


## What The Star Arrangement Actually Does

Verified in the code. In the star branch, the runner injects the mathematical model into every model's prompt, every round. The discovery efficiency figure, its three round rolling average, the reliability growth figure, and the registry counts of open, confirmed and closed findings are all written into the panel's prompt.

So the mathematical model is not bookkeeping in the existing runner. It is a feedback signal to the panel, which is how the models are meant to calibrate how much effort to spend. A serial ladder with no rounds has nothing to inject, no registry state to summarise, and no figures to calibrate against. That capability is real, and last night's harness discarded it.


## But Co Discovery Has Never Been Recorded. Not Once

There is a field that records every model which raised a finding, before deduplication collapses them into a single canonical entry. Across the modern arc, experiments 42 through 49:

566 findings. 566 total source aliases. Exactly 1.00 alias per finding. Findings raised by two or more models: zero.

Not one finding in the entire modern arc was ever recorded as having been raised independently by more than one model.

That is not evidence of remarkable diversity. It is the aliasing mechanism never firing, and it is already a known open item: the runway records that the alias map is a one to one mapping in all 28 registries and that no entry has ever gained a second alias.

The consequence is the one that matters. The project cannot currently measure whether its models find different things. The field that would show it is structurally empty. So the central claim for running a multi model panel at all has no measurement behind it in this project's own archive.


## A Correction, Made The Same Day And Before This Was Read

The section above says the project cannot currently measure whether its models find different things. That is too strong and is withdrawn. It asserted a general claim after checking a single field, which is the same error shape this project has recorded repeatedly.

Co discovery does happen, and it has been measured, under a different name.

The 133 similarity pairs that were adjudicated by counterfactual repair were checked against the model that raised each finding. 106 of the 133 pairs were raised by different models. 27 were raised by the same model. And of the cross model pairs, 21 were judged by the tool to be the same defect in both directions.

Those 21 are co discovery. Two different models independently raised one defect, and a tool rather than a vote confirmed they were the same. They sit in the archive as two separate entries because nothing links them.

So the corrected finding is narrower and more useful. The registry cannot record co discovery, because the alias field is written once at creation and no code anywhere appends to it. Verified on one experiment: 82 map entries for 82 findings, and zero entries with more than one alias. There is no mechanism, rather than a mechanism that fails to fire. But the similarity and deduplication analysis does capture it, and found at least 21 confirmed instances. The rate is therefore unknown, and the archive systematically under represents agreement, because only the pairs falling inside the similarity function's candidate band were ever adjudicated. Twenty one is a floor, not an estimate.

The practical consequence is unchanged and now better supported. The fix is an append at the deduplication site, so that a finding recognised as another model's defect adds its identifier to the alias list instead of creating an unlinked twin. It is a small change, and it turns something the project currently recovers by expensive after the fact adjudication into something the registry records for free.


## Cross Examination, The Weaker Signal

Do the models at least pass judgement on each other's findings, even if co discovery goes unrecorded?

Of 566 findings, 299, or 52.8 percent, carry any verdict at all. 156, or 27.6 percent, are judged by at least one model other than the one that raised them. That leaves 410, or 72.4 percent, raised by one model and never examined by another.

There are two readings and the data cannot separate them. Either the panel genuinely cross examines only about a quarter of the time, or the recording of it is as under populated as the aliasing. This note does not choose between them. It is the same shape as yesterday's discrimination finding: the mechanism may work, and the record cannot show it.


## The Discovery Efficiency Figure: What It Is, And What Is Actually Wrong With It

What it is. This figure, written as rho, is the discovery efficiency or semantic novelty rate. Of the raw findings a round produced, what fraction were genuinely new rather than restatements of something already in the registry. The function returns the current round's value, a rolling average over three rounds, and a churn verdict. A falling value means the panel is going round in circles.

Both the value and its rolling average are computed every round and shown to the panel. That is how models are meant to calibrate effort.

What is wrong. Only the churn verdict is gated, and it is gated on a constant requiring twelve completed rounds, a number which the code's own comment says has no derivation on record. The rolling window is three rounds, so a defensible floor would be two full windows, which is six.

Measured across the modern arc: at the live threshold of twelve rounds, 5 of 11 runs are long enough for the churn verdict to fire at all. At the derived floor of six, 9 of 11 would be.

A correction is owed to the runway document. It states that of experiments 44 through 49, only experiment 44 with its thirteen rounds reaches round twelve. Measured now, experiment 44 and experiment 47, which has fourteen rounds, both reach it, so two of six rather than one of six, and five of eleven across the whole arc. The runway figure was written on 18 August, before experiment 47's missing rounds were reconstructed on 20 August. It is stale rather than wrong in principle, and it should be corrected where it stands.

The distinction that must not be blurred: the discovery efficiency figure itself is live and feeds the panel every round. It is the churn detector built on top of it that cannot fire in half the arc. Saying that rho does not work would be false.

The fix is a founder ruling rather than an engineering choice. Either derive the twelve round threshold and record the derivation, or adopt the two window floor of six which is already computed in shadow and has never gated anything. Promoting it changes convergence behaviour, so it needs clean data from a live run first.


## The Inventory Sweep: What Else Is Inactive, And What Has Never Been Tested

Of the 34 instruments enumerated yesterday, six cannot affect a live run today. The discrimination control, which is gated on the presence of a corrected copy and is fed by nothing until yesterday's first patch is merged. The fix complexity measure, in shadow. The load balancer, shelved by founder ruling. Shadow stage six. The survived falsification ledger, which is not wired at all. And the null perturbation control, which exists only as a standalone script.

Seven have no commissioning evidence whatsoever, meaning no test that feeds them a known good and a known bad input and asserts that they answer differently.

Four of those seven are convergence deciders. They are what ends a run. They are the two sided gamma gate, the state convergence check, the stall convergence check, and the budget extension check.

The first of those is the two sided gamma gate, which the founder holds as a standing directive: gamma is load bearing.

None of the four has ever been shown to answer differently on a known good and a known bad input.

That is not a claim that they are wrong. It is a claim that nothing on the record shows they are right, which is exactly the position the falsifier gate was in before it was tested yesterday and found to accept a bare print statement as a confirmation.


## What The First Task Was, And Why Its Failure Matters

The task that went to human review asks for discrimination failures to be routed up the escalation ladder.

The ladder already exists and already does the right thing: it routes a failed critical finding to progressively stronger writers, and escalates to a human only when the strongest cannot resolve it. But it fires only when a finding is escalated and not confirmed. A test that fails the discrimination control is confirmed, because it fired. So such a finding never reaches the ladder at all.

Three independent writers produced patches that applied and then failed to make their own tests pass. It escalated to human review.

The consequence for the next run is direct. Merging the six patches that compose cleanly wires the discrimination control, but leaves its failures unable to reach the ladder. That is a half repair and must be stated as one.


## What The Next Run Has To Be

The founder's framing is right. Build the revised runner, merge the fixes, then run live to gather the data that does not exist. Specifically it must establish four things.

First, whether wiring the discrimination control changes what a run yields. Yesterday's fifty percent figure was measured on an archive produced without it.

Second, whether the panel co discovers at all. That requires the aliasing mechanism to record a second model. Until it does, no run can answer the question about six models versus one.

Third, whether the six patches hold in a live run rather than merely composing statically.

Fourth, whether the first task is genuinely hard or the brief for it was poorly written.

The second of these is the cheapest, and it is about the existing runner rather than anything built yesterday. Until aliasing records a second model, every future run reproduces the same silence.

Written under CDSFL note standard v1.4 (13 August 2026, Rule 24 added 16 August).
