# CDSFL Schema Toggle Design Brief

6 October 2026, 05:30 BST (Europe/London)

## What this brief decides

How a person who has just installed CDSFL chooses what the schema does, without reading 93 configuration fields or any source code. It covers every switch and dial that changes what a run measures, says what each one is set to today, and recommends a default.

It replaces nothing. The earlier brief, *CDSFL UX Vision Sketch* of 28 March 2026, sets out what the interface should feel like and names none of these features; this one is about the control surface behind it. Read together, not instead.

## The figures here are produced, not quoted

Every count below comes from `scripts/schema_toggle_inventory_2026-10-06.py`, which reads the switch definitions out of the runner, reads what the simulated launcher sets, and counts the shipped real configuration files. Re-run it and the table rebuilds. 49 real configuration files were scanned.

The script was wrong twice before this brief was written, and both faults are worth stating because they are the kind that make a design document confidently misleading. It first counted 47 configuration files, having looked only inside the per-experiment directories and missed 2 that sit beside them; a denominator that silently drops members makes every proportion built on it wrong. It also reported 8 features as enabled nowhere when 2 of those 8 are switched on by the launcher through a command-line flag, which cannot be read off the source at all. Both are fixed and the honest category, "computed from a flag, not classifiable by inspection", now exists.

## The shape of the problem

There are 93 configuration fields. 25 are true or false switches. 65 are dials carrying a number, a path or a word. A person installing this project should never see 90 controls, and the recommendation at the end of this brief is that they see 3.

## What a run does today if nobody touches anything

6 switches are on by default, and together they are the behaviour a user gets for free: the divergence channel, the feedback channel, in-round re-asking, location shadowing, the prior-fix summary, and windowed context. These are the ones already judged safe enough to be unconditional, and nothing here proposes changing that.

Everything else is off by default and has to be asked for.

## The gap between what real runs use and what the simulation rehearses

This is the most useful column in the table, because it is where a reader can see the schema being studied under conditions no real experiment has ever used, or the reverse.

The settled facilities, armed in a substantial share of real configuration files: S_k scoring in 45 of 49, the prior-fix summary in 33 of 49, windowed context in 33 of 49, in-round re-asking in 32 of 49, merge arbitration in 28 of 49, the falsifier gate in 25 of 49, location-keyed convergence in 21 of 49, location shadowing in 21 of 49.

The thinly-used facilities, which the simulation now switches on: immune memory in 13 of 49, routing in 5 of 49, the hardened gate in 4 of 49, and folding fixes forward in 1 of 49. The simulation enabling these is deliberate — it is how they get rehearsed before a real run depends on them — but it is a divergence from real conditions and should be read as one.

6 switches are enabled nowhere at all: the blocking form of the discrimination control, human-in-the-loop review, immune-memory consumption at zero residual risk, the declared-models marker, resume, and stall-based termination. An addition nothing reaches is not additive. Each of these is either awaiting a study or is dead weight, and that distinction is not something this brief can settle by inspection — it needs a decision per row, which is listed at the end as a single question rather than 6.

## Burst is not a switch, and that matters for the interface

Burst has 3 settings, not 2: automatic, always on, always off. Automatic is the default, and it decides per round whether a burst is needed. Presenting it as a checkbox would silently collapse a 3-way choice into 2, and the automatic setting is the one most users want. It belongs in the interface as 3 options with automatic preselected.

## Independent thought contamination has no switch at all

This is a genuine gap rather than an oversight to be papered over. The gamma-aware suppression of degradation restarts exists in the runner and is documented there as a named mechanism, but it is governed by the measured residual-risk value at the time, not by any configuration field. There is nothing to toggle.

So one of the controls requested for this brief cannot be delivered as a toggle without first building a configuration surface for it. Whether that surface should exist is a design decision, not a bug: gamma-aware restart suppression responds to the measured residual-risk value, which is arguably better than a switch a user sets once and forgets, and switching it off would let a run continue through exactly the degradation that suppression exists to catch. The recommendation is to leave it unswitched and surface it as a reported condition instead, so a user can see it fire without being able to disable it.

## The recommendation: 3 profiles, not 25 checkboxes

A person should choose once, from 3 named profiles, and only then be offered individual controls. Converging on one recommendation rather than presenting a menu is the point; the profiles are:

**Standard.** The 6 default-on facilities, plus S_k scoring, the falsifier gate, merge arbitration, in-round re-asking and the prior-fix summary. This is what the majority of real configuration files already use, so it is the profile with the most evidence behind it. It should be preselected.

**Full.** Standard, plus immune memory, routing with the ladder exhausting rather than capped, the hardened gate, and folding fixes forward. This is what the simulation now runs. It exercises more of the schema and is the right profile for someone studying the schema itself rather than using it.

**Minimal.** The 6 default-on facilities and nothing else. For a first run on an unfamiliar target, or for establishing a baseline against which the other profiles can be compared.

Individual controls stay available behind the profile choice, because a researcher who wants one facility from Full without the rest should not have to take all of it. The profile is the default path, not a cage.

## Clearing and exporting an experiment's records

Founder ruling, 6 October 2026: a researcher may want to clear an experiment's records or to keep them, and that is their decision rather than the designer's. Clear therefore offers a sub-choice of Archive or Delete, and Archive points at one clear location where archived results are kept. The intent is a familiar environment, close to a standard desktop operating system. Whether that paradigm extends to the rest of the interface is not yet decided.

The unit is one experiment. That already matches how runs are stored on disk: across 324 run directories there are 59 carrying a registry and no registry is shared between runs, so per-experiment is the existing boundary rather than a new one.

Export fits the current design with no structural change. Every field an exported entry needs to stand on its own, which is its identifier, status, severity, originating model, the round it opened in, and its description, is present in all 3,158 archived entries. Export-all and export-one are serialisations of something already serialised per experiment.

Archiving is cheap, and that is worth knowing before anyone designs around size. The 324 run directories hold 0.696 GiB in total. The median run is 0.2 MiB and the mean 2.2 MiB, and exactly 1 of the 324 exceeds 100 MiB, which is 0.3086 percent with a 95 percent interval of 0.0545 to 1.7273 percent. Keeping everything costs very little. The genuinely large artefacts are the per-seat sandbox copies, which live outside these directories and are the only thing that would need a size policy.

### The one engineering consequence, and it is the reason Delete needs care

Every run stores its derived measurements outside its registry rather than inside it. All 59 runs that carry a registry also carry separately stored series for the decay curve, the gate history, the churn history and the novelty counts. Deleting an experiment's entries therefore leaves those numbers standing with nothing behind them. On a real example, a clear would remove 75 entries and leave 5 series intact, and the experiment would continue to report a decay figure it can no longer derive.

A desktop operating system does not actually have this problem, which is why the metaphor needs one addition rather than a caveat. Deleting a document there does not leave a stale summary of that document elsewhere, still claiming to be current. Here it would. So an archive or a delete must take the experiment's evidence together with the numbers derived from it, as one unit. Then Delete is honest, because what disappears is the whole claim rather than only its support, and Archive is honest for the same reason.

### Where archived results should go

A location already exists at the path CDSFL_archive on the desktop, created on 19 August 2026 for the project's own encrypted evidence store. The interface should either adopt that location deliberately or choose a visibly distinct one. Two different things both called the archive, in a design whose stated aim is familiarity, is the one outcome to avoid.

### What follows for recording failures

The same ruling makes a sibling ledger the natural home for dispatch failures. A failure is an event about the run rather than a finding about the target, and the convergence gate is handed how many registry entries exist, so recording failures as entries would feed them to the decay measure. Held in their own per-experiment ledger, nothing is derived from them, which means clearing them is safe whichever sub-choice the researcher makes, and the record a researcher needs in order to retrace every step is still kept.

## The one thing this brief needs ruled on

The 6 switches enabled nowhere: each is retained, scheduled for a study, or retired. Retirement under the additive standard needs a committed measurement showing something better makes it redundant, so the honest default is retained-and-scheduled unless there is a reason otherwise. That is a single decision taken 6 times, and it is the only question in this document.

Written under CDSFL note standard v1.7 (26 August 2026).
