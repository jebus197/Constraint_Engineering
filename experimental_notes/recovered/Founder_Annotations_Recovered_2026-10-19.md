# Annotations of the founder's that no longer exist in his own files

Recovered 2026-10-19T23:43:36+01:00 under CDSFL note standard v1.8, from `experimental_notes/data/annotation_verdicts_2026-10-17.json`, which was at that moment their only surviving copy.

**How they were lost, as far as it can be established.** `Responses/TASK_LIST_48_Hours_And_Rulings_2026-10-17.txt` is 108 lines long and holds 8 annotations. The verdicts recorded against it on 2026-10-17 name anchors at lines 108, 114, 116 and 120, which lie beyond the file's current end, so the file is shorter than the one the verdicts were taken from rather than merely rearranged. Its modification time is 2026-10-19T07:19:02+01:00. **No committed code can have done it:** 22 Python files under `scripts/`, `bench/` and `hooks/` reference that directory and 0 of them contain a write, delete or move call. An ad-hoc shell command cannot be excluded from the record, and is not claimed.

**Why this file exists.** His words are the project's primary record and 3 of the items below are questions still owed to him. A verdict row is a claim about an annotation; it is not a substitute for the annotation. Holding the recovered text in a tracked file means a second loss cannot be silent.

**12 annotations recovered.**

## `TASK_LIST_48_Hours_And_Rulings_2026-10-17.txt#48` — recorded verdict ACTED_ON

<!-- verbatim-begin: the founder's own words, 2026-10-17 -->

> There may be a need for a small amount of adaption in this facility where if I (or you) make a new proposal like the CDSFL bounded orchestrator model, this can count as an open ticket until it is either resolved/implemented, merged or rejected, just as real Firefox Bugzilla proposals/feature requests are treated, and largely as the current CDSFL Bugzilla mechanics deals with these kind of issues now. The knack will be in building this facility in such a way that it can be recognised by you and by any mechanical extractor in chat, or from my tts responses, in such a way that it can extract them reliably. I propose a small extension to out MC command list where I (or you) will either mark/label new proposes with either ‘fr’ (feature request) or ‘pr’ (proposed fix). Then perhaps your extractor can look for these signals in our exchanges and extract them and place them within the Bugzilla framework with two distinct sections? (Again one for ‘fr’ and one for ‘pr’.) Would this work, or do you have a better way? If you do gauge this to be optimal, you will need to update your own MC command list in your local and global CLAUDE.md files and in my existing desktop MC command list too. (Although don’t alter the format pf my desktop version. Just append these new MC commands to the end of the excising file.)

<!-- verbatim-end -->

Evidence recorded against it: bench/ticket_store.py propose and merge, guarded by bench/tests/test_a_shared_mechanism_does_not_decide_2026-10-17.py

## `TASK_LIST_48_Hours_And_Rulings_2026-10-17.txt#54` — recorded verdict NOTED

<!-- verbatim-begin: the founder's own words, 2026-10-17 -->

> Agreed.

<!-- verbatim-end -->

Evidence recorded against it: his own annotation of 2026-10-17

## `TASK_LIST_48_Hours_And_Rulings_2026-10-17.txt#58` — recorded verdict NOTED

<!-- verbatim-begin: the founder's own words, 2026-10-17 -->

> We can see. Given the above framing, it might work better than expected. We will soon see!

<!-- verbatim-end -->

Evidence recorded against it: his own annotation of 2026-10-17

## `TASK_LIST_48_Hours_And_Rulings_2026-10-17.txt#66` — recorded verdict TRACKED

<!-- verbatim-begin: the founder's own words, 2026-10-17 -->

> So would running the test as two simulated experiments, rather than just the proposed 1 settle it? If so that is what you should do. I would also like to nominate Fable as the proposed orchestrator model for this experiment. We can also test it relatively cheaply, and relatively quickly, by having fable sit in as the orchestrator in one of the two simulated experiments. Then we get useful feedback, without risking anything very much, and I assume the risk of a meaningful confound then also evaporates, since the experiment itself is largely simulated and it remains cheap, because Fable already comes with my paid Max subscription, and is often significantly underused anyway. As for when to run this experiment, I would say there is no need to delay it unnecessarily and that it should be safe to run it at the end of all of the work resulting from your master task list. Again we can use the same target as in all our other recent simulated experiments, as this at least gives us a bassline against which to measure its performance. Your job during this test would be minimalist. You would simply monitor/observe the performance of the orchestrator and make sure the whole experiment runs smoothly and as expected. You would only step in if something was broken, or looked as though it wasn’t functioning correctly, pause the test, fix the issue under cy protocol, and then either resume the experiment, or restart it; whichever presets the saner choice at that time. It might be worth noting that the ‘job description’ for the orchestrator model would be slightly different from the job description given to the other models, in that it would perform your current role exactly when monitoring experiments under full cy discipline/protocol. The goal should be to have it run end to end in experiments with the minimum of human/HIL intervention, while remaining fully bound within the framework of the harness. (Which means it should continue to use the full machinery of the harness throughout). In a certain very real sense, this will be the first real test of how the harness was always envisaged to work. There is little point having all of the complex machinery of the harness and CDSFL in general, if any model can continue to function almost fully outside of the harness and of any of the constraints that the harness places on it.

<!-- verbatim-end -->

Evidence recorded against it: entry B20 is DEFERRED on his own instruction not to be sidetracked on the orchestrator

## `TASK_LIST_48_Hours_And_Rulings_2026-10-17.txt#70` — recorded verdict NOTED

<!-- verbatim-begin: the founder's own words, 2026-10-17 -->

> Well I guess that will be the test. The prediction (and the bet) made overall about CDSFL is that it could/should potentially make all our models more useful, more accurate and more reliable. However the converse could be proved to be true, and the kind of degradation you have observed in your own performance could persist. This initial prediction could be falsified. Again we will have to see. That is the point of this particular test.

<!-- verbatim-end -->

Evidence recorded against it: his own annotation of 2026-10-17

## `TASK_LIST_48_Hours_And_Rulings_2026-10-17.txt#74` — recorded verdict TRACKED

<!-- verbatim-begin: the founder's own words, 2026-10-17 -->

> If there is more than one opportunity to test it then fine, that is what we should do. First in shadow as you have suggested, then in a subsequent simulated experiment (all being well) in live mode in that experiment. Then report all your findings. You can add this to your master task list too.

<!-- verbatim-end -->

Evidence recorded against it: entry B20 is DEFERRED on his own instruction not to be sidetracked on the orchestrator

## `TASK_LIST_48_Hours_And_Rulings_2026-10-17.txt#84` — recorded verdict RULING

<!-- verbatim-begin: the founder's own words, 2026-10-17 -->

> Is this where you said there was a conflict/collision between CC2’s findings and Fable’s? Did you not look at this and find that the collision was overstated and that the solution was potentially composable (under our formal simplest sufficient fix, additive and composability standards?) Or did you say that one of these fixes was preferable in isolation over the other? Or are we talking about something else? And why would we adopt a fix whose conclusions we cannot reproduce? Either way if you can’t fix it simply, or if the ‘collision’ continues to exist, you should attempt to resolve it and then put your fix to the free panel, before then subsequently testing their work and then applying the final fix. You can do this in a separate panel review of its own, or in one of the other recently agreed panel reviews that may still be outstanding. In either case the objective will be to clear this problem so that it can unblock access to our remaining runway items. It should not simply be left as untesolved.

<!-- verbatim-end -->

Evidence recorded against it: his own question of 2026-10-17; it remains owed to him

## `TASK_LIST_48_Hours_And_Rulings_2026-10-17.txt#102` — recorded verdict TRACKED

<!-- verbatim-begin: the founder's own words, 2026-10-17 -->

> Run it. Add this to the master task list too.

<!-- verbatim-end -->

Evidence recorded against it: entry C4 is OPEN; it is the owed free-panel run itself

## `TASK_LIST_48_Hours_And_Rulings_2026-10-17.txt#108` — recorded verdict TRACKED

<!-- verbatim-begin: the founder's own words, 2026-10-17 -->

> And the conclusion is/was? Or perhaps you should add this to one of the panel review questions too. However your statement in this regard is too vague for me to remember exactly what you are referring to? But as I will go to sleep, it probably is best to put this question to the panel in one of the panel reviews too, and then explain it in more detail once your full master task list is complete, so that you can complete all of the work in your master task list without requiring further interaction from me. If the models recommend the fix is sound, then apply it, and then explain it more fully to me once all the work from your master task list is complete. However logically the HIL review stage is always part of the process anyway, because first the HIL proposes and reviews their own experiment, and can monitor it through cy protocol in their local machine terminal as it proceeds, where they can intervene at any time of they wish, and finally they are presented with the opportunity to review all work when an experiment completes. The only other potential exception to this is if the models encounter a genuinely computationally irreducible problem, or if a problem emerges that impacts on core system safety, legal issues/prohibition, ethics that could lead to real world harm to the HIL (or to other humans), or that impacts negatively on core system performance, or unresolvable errors. But these have all been longstanding principles of the project from the outset, and so should continue to stand for all our models now. (Including the proposed new CDSFL bounded orchestrator.) Indeed these constraints are almost certainly part of the core CDSFL directive set/system prompt, currently fed to all our models.

<!-- verbatim-end -->

Evidence recorded against it: entry C9 is DONE on bench/tests/test_the_review_pause_is_a_pause_not_a_review_2026-10-17.py

## `TASK_LIST_48_Hours_And_Rulings_2026-10-17.txt#114` — recorded verdict RULING

<!-- verbatim-begin: the founder's own words, 2026-10-17 -->

> What are the ‘94’ unsavable blockers?’ I don’t remember hearing about this before? What exactly if anything do they block? If the answer is nothing that would prevent you from completing your work, then save your explanation of this until the end of your work on the master task list too. But I won’t tell you to make 94 potentially significant code changes to clear these ‘blockers’ without first knowing if they are real, or what they are, or if it I just you again regurgitating old material?

<!-- verbatim-end -->

Evidence recorded against it: his own question of 2026-10-17; it remains owed to him

## `TASK_LIST_48_Hours_And_Rulings_2026-10-17.txt#116` — recorded verdict ACTED_ON

<!-- verbatim-begin: the founder's own words, 2026-10-17 -->

> One thing I have noticed that is missing from the above task list is the Bugzilla mechanics we have only just been discussing. Again this work should be done first and placed at the top of your outstanding

<!-- verbatim-end -->

Evidence recorded against it: bench/ticket_store.py with bench/tests/test_the_register_holds_the_whole_history_2026-10-17.py

## `TASK_LIST_48_Hours_And_Rulings_2026-10-17.txt#120` — recorded verdict RULING

<!-- verbatim-begin: the founder's own words, 2026-10-17 -->

> Apart from answering this one item, if the ‘94 blockers’ will block you from completing your master task list or not, the entire task list as presented is approved, with the above additions. Once built you should begin using/populating your new Bugzilla mechanics immediately, and indeed you can begin by populating it with work already done, work proposed, work completed etc with the full Bugzilla framing we have already discussed, and use this as a final check to ensure your master task list is both up to date and is fully complete. One small but useful refinement would probably be to give each issue and each resolution its own unique hashed value/ID and then to store these in a searchable registry within the Bugzilla framework, and arrange it so that you must search for these hashed values before you do, or suggest any new work. You should arrange it so that this is much more useful to you as a way of listing, proposing, searching, applying and remembering which fixes have and have not been done or applied that just relying on semantic searches/vocabulary/word searches on their own. You will need to set this up and test it and ensure that it does work better than other methods for this purpose and so that it doesn’t risk simply becoming decoration that does nothing useful. The full harness already has a registry, but I don’t know if it currently works this way either? But if it doesn’t and you do gauge it to be genuinely useful you should probably apply these principles to the harness registry too.

<!-- verbatim-end -->

Evidence recorded against it: his own question of 2026-10-17; it remains owed to him


## Further annotations whose anchor survives but whose text was replaced

## `TASK_LIST_48_Hours_And_Rulings_2026-10-17.txt#40` — recorded verdict TRACKED, text superseded in the live file

<!-- verbatim-begin: the founder's own words, 2026-10-17 -->

> Then if this isn’t built, add it to the master task list and build it, then check and test your work, both first with the free panel and in 1 (hopefully final) simulated run, to test how this facility performs exactly. Just reuse the same target as the last 3 simulated runs in this task.

<!-- verbatim-end -->

## `TASK_LIST_48_Hours_And_Rulings_2026-10-17.txt#80` — recorded verdict ACTED_ON, text superseded in the live file

<!-- verbatim-begin: the founder's own words, 2026-10-17 -->

> We fix going forward and leave the archive alone. Going back and rewriting the archive, as I have said before could potentially be seen as dishonest, and as an attempt to rewrite history. So as ever we simply record our decisions honestly and appropriately and focus our attention on what can and should be fixed going forward.

<!-- verbatim-end -->

## `TASK_LIST_48_Hours_And_Rulings_2026-10-17.txt#88` — recorded verdict ACTED_ON, text superseded in the live file

<!-- verbatim-begin: the founder's own words, 2026-10-17 -->

> Make the guard aware of negation as you have suggested.

<!-- verbatim-end -->
