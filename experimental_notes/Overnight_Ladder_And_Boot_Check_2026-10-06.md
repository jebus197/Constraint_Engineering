# Overnight Report, Capability Ladder And The Boot Check

6 October 2026, 07:15 BST, Europe London

## THE ONE DECISION NEEDED FIRST

Removing the rung cap is not only a question of spend. It moves the convergence gate in the direction that makes convergence harder, and it can stop a run converging that converges today.

The second panel seat predicted the opposite, measured it, and was refuted by its own measurement. Over 14 archived runs of at least 3 rounds, resolving every unresolved critical finding moves the critical gamma value DOWN in 9 runs, up in 3, and leaves it unchanged in 2. Two of the 14 cross the 0.30 convergence arm downward: the run named exp40_gate falls from 0.3018 to 0.2328, and the run named commissioning_arm1_panel falls from 0.3236 to 0.1883. That is 14.29 percent of runs, with a Wilson 95 percent interval of 4.0094 percent to 39.9414 percent. Three independent tools agree to 7 significant figures: statsmodels, a hand written closed form, and Wolfram Language running on the local Wolfram Engine.

The reason the curve steepens is visible in the data rather than argued. The findings that get resolved carry a later mean round than the registry average, 18.00 against 13.31 in the first run and 6.50 against 3.19 in the second. An unresolved critical is one the ladder has not yet reached, which places it late in the run, and adding weight to the late end of a cumulative curve steepens that curve. A steeper curve means a higher beta, and gamma is 1 minus beta.

This matters immediately because exhaustion of the ladder was enabled in the simulated launcher earlier the same night, on the standing instruction that the problem should run until it is resolved or the ladder is exhausted. The rung budget is therefore an undeclared input to the convergence gate, and that was not known when the instruction was given.

The seat's own recommendation is recording only. Log the critical gamma a second way, so the coupling is visible every round, while the gate continues to read exactly what it reads today. No change to what the gate decides until there is evidence to change it on. That recommendation was not acted on overnight, because it alters the most protected part of the model and the decision belongs to the human in the loop.

The claim was not taken on trust. The seat's script was re-run against the live archive and reproduced every figure exactly. A first attempt reported zero runs measured, which turned out to be an operator path error rather than a fault in the seat's work, and the correction is recorded because the figures would otherwise read as unreproduced.

## THE LADDER STILL CANNOT CLIMB, AND THAT ALSO NEEDS A RULING

The capability ladder is consulted only when the simulated launcher is given the ladder setting for seat models, and that setting defaults to uniform, which answers every seat with a single model. This is the second of the two recorded causes of the inert ladder, and it was never fixed at the launcher. The repair that landed on 5 October was the rung budget, which is a different thing.

The default was deliberately left alone, because changing it alters what the simulation dispatches against the Max subscription, and that is a cost decision rather than a technical one. The new boot check halts and names it instead.

There is a second limit worth knowing. Even with the ladder setting switched on, the simulated ladder maps 6 seats onto only 2 distinct underlying models. It can therefore distinguish 2 behaviours, not 6, and a ladder intended to become a measured statistic over per model falsification ability cannot be calibrated on 2 behaviours.

## THE BOOT CHECK, AND THE DEFECT IT WAS HIDING

The preflight check was rebuilt as a power on self test, printing pass or fail against each row and halting the boot at the first failure, on the instruction that this is how a computer reports its own health and that it suits a schema meant to run over many models and many systems.

The rebuild found a defect in the previous version of the same check, and it is the exact class of defect the check exists to catch. The earlier version reported three states, and the middle state never set the exit code. A check whose own code crashed was mapped to that middle state, so a broken check passed and the experiment launched anyway. This was measured by injecting a deliberately broken check into the old version and reading back an exit code of zero. A guard that cannot fail is not a guard. A crashing check is now a failure that names its own exception.

Halting at the first failure makes the order of the checks load bearing, which it was not when every row ran regardless. A check that runs before the check it depends on is reporting on an unestablished premise, and the halt then stops at the wrong row. The order is held against the declared dependencies by the z3 solver, cross checked by an independent scan that has to agree, and a deliberately reversed order is rejected, so the check is able to say no.

There is a diagnostic mode that runs every row instead of halting, and it is not a weakening of the instruction. Clearing 5 separate failures under halt on first costs 5 boot cycles, against 1 run of the diagnostic listing. That was derived symbolically and confirmed by simulation on 2000 of 2000 trials.

The boot check is called by the launcher rather than left as a script someone has to remember. On its first honest run it halted the launcher with zero model dispatches and reported the inert ladder described above.

## WHAT THE PANEL FOUND, AND WHERE IT AGREED WITHOUT CONTACT

Both free seats answered a byte identical brief on what the routing ladder should rank on, each blind to the other, with no paid dispatches. The first seat returned 1693 words after 50 tool calls. The second returned 2581 words after 49 tool calls.

The most useful result is an agreement neither seat could have copied. Both independently rejected the figure the brief leaned on. That figure, a chi square of 280.0138 on 4 degrees of freedom giving a probability of 2.213221 times 10 to the minus 59, measures how many findings each model produces per round. That is productivity, not falsification ability. Ranking the ladder on it puts the most productive model first, and that is the model shown in Experiment 55 confirming 2 findings out of 2 with tests that never read their target. Wiring the ladder to the live capability fingerprint as currently written would reproduce the precise inversion that the provenance gate exists to prevent. Agreement reached blind is evidence. The same agreement reached after the seats had read each other would not have been.

The second seat also derived that once the cap is removed, the order of the ladder cannot change which findings get resolved, only what they cost, because routing stops at the first confirmation and the probability of eventual resolution is symmetric in the rungs. It further derived that the cost minimising order is each model's success probability divided by its cost, checked by exhaustive search over 4000 random rosters with a worst case gap of zero. If that holds, the two standing instructions are coupled: removing the cap is what makes an imperfect measurement safe to use.

Both seats declined to delete the existing frozen list of vendor names, and both said plainly that this is weaker than the instruction to stop caring what a model is called. Their reason is the same: with no data every model scores identically, something has to break the tie, and the frozen list is the only ordering in the project with a validated end to end result behind it. Both demote it to a tie break rather than a decider.

## WHAT THE NIGHT'S NETWORK TROUBLE COST, AND WHAT WAS BUILT FROM IT

One seat consumed 2423.7 seconds and returned nothing. A later attempt consumed another 1800 seconds, made 88 tool calls, and also returned nothing. The successful attempt answered in 1020 seconds after 49 tool calls.

The per call rate was effectively identical across all three attempts, at 20.455 and 20.816 seconds, so the seat was never slowed down. What changed was the number of calls. During the outages it issued nearly twice as many calls and never reached an answer, because the calls themselves were failing and being retried. That is a diagnostic signature worth keeping: a model on a degraded connection keeps working at its normal speed and simply never converges.

A timeout was raised from 1800 to 3600 seconds on the reasoning that the clock was the binding constraint. That reasoning was wrong and the change was reverted within the hour, because the successful run finished in 1020 seconds, comfortably inside the original limit. A longer clock would have let a degraded round churn for an hour instead of half an hour, which is worse. The refutation is recorded in the code beside the setting rather than quietly dropped.

The right remedy was already proposed, and it was built. Each seat is now asked to print the single word Ready before any brief is sent, with up to 3 attempts. It established that a route was working in 5.91 seconds, against the 3258 seconds the failed round took to establish the same fact. A seat that does not answer refuses the whole round rather than being quietly dropped, because skipping a model is benching it and that is not allowed. A separate watcher re-dispatches a free round until a real answer arrives, and refuses outright to dispatch any paid seat, because an unattended retry loop is the worst possible place to spend money.

The star topology is now enforced rather than remembered. Two rounds asking the same question have a byte identical brief, so a checksum over the brief finds them with nothing to label and nothing to forget. A round dispatched without being made blind to a sibling that has already answered is refused, with the exact command to fix it printed. Tested against the real situation: the second seat's dispatch would have been refused had the blindness setting been forgotten, and the refusal costs no network because it runs before anything is sent.

## THE TEST SUITE

A full run took 58 minutes 43 seconds and returned 10210 passed, 26 failed, 20 skipped.

Of those 26, a majority were consequences of the night's own work and have been fixed: the memory index line length, the memory ledger accounting, the panel record mirrors, the two missing panel records, a script that rejected an unknown flag by complaining about the wrong thing, a listing that truncated itself in silence, a configuration default read from a class that a test legitimately replaces, and a round directory that carried a bare vendor name in its path, which is a provenance rule violation.

Eight failures remain and they are not from this work. Five concern panel rounds from 3 and 5 October where a seat recorded no tool calls or a round left no file, and the guards offer a designed remedy: record each shortfall with its measured cause. That needs a per round investigation that has not been done. One is a test stub that has not been updated to match a change made on 5 October. One is a census of source text assertions that has grown past its declared ceiling, and the honest response is to convert the weakest of those assertions into checks that execute, not to raise the ceiling. One concerns archive classification.

## ALSO DONE

A design brief now exists covering every switch and dial in the schema, with a measured inventory behind it rather than a hand written table. There are 93 configuration fields, of which 25 are switches and 65 are dials. Six switches are on by default. Six are enabled nowhere at all, in no real configuration and not in simulation, and each of those needs to be retained, scheduled for study, or retired. The recommendation is that a person installing the project chooses once from 3 named profiles rather than facing 25 switches, with individual controls still available behind that choice.

The brief also records an honest gap. One of the controls requested for it, the suppression of restarts when a run degrades, has no configuration field at all. It responds to a measured value rather than a setting. The recommendation is to leave it unswitchable and report when it fires, since switching it off would let a run continue through exactly the degradation it detects.

The state restore now reports what ran last as well as the highest numbered experiment. Verified on the live archive, it names the study run from 3 October rather than an experiment from 23 August, which is what it reported before.

The provenance gate now credits the model that wrote a routed test rather than the model that filed the finding. Of 3158 archived entries, 210 carry a routed resolution, and all 210 named a different model: 100 percent of routed entries, and 6.6498 percent of all entries with a Wilson interval of 5.8324 to 7.5725 percent. The second seat confirmed this repair is live and identified what remains, which is that the filing model's failure is still missing from its own denominator, inverting 5 of 11 rankings.

## WHAT WAS NOT DONE

The joint round has not run. Both blind rounds are in, which is the precondition for it.

The gamma recording recommendation has not been implemented, pending a decision.

The eight remaining suite failures are diagnosed but not repaired.

Written under CDSFL note standard v1.7 (26 August 2026).
