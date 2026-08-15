# What The Testing Found Before Anything Was Switched On

2026-07-31, 18:16 BST.


## The Headline

Four dormant parts of the machinery were built, wired and tested. None was switched on. An independent check then went over all four and downgraded two of them that the builders had marked ready.

Three of the four turned out to have problems that would have caused real damage if they had been enabled without testing. One of those problems would have quietly ruined the capstone experiment. Another would have crashed every run it touched. A third would have fed the reviewing panel academic papers about the wrong subject entirely.

Total cost, nothing. No reviewing model was paid to run. Everything was tested against the two hundred and ninety three findings already sitting in the six completed experiments.

There is one decision needed urgently and two that can wait.


## Part One. The Convergence Question, Which Turned Out To Be The Important One

The question asked was whether the rule used to decide that an experiment has finished is too lenient. There is an older, stricter rule, built earlier in the project and since retired. The test was to replay all six completed experiments and work out what each rule would have said, round by round, without spending anything.

The replay is trustworthy. It reproduces the recorded outcomes exactly, including working out independently why one experiment finished at round thirteen rather than round eleven. Where it initially disagreed with the record on one experiment, it chased the discrepancy rather than rounding it away, and found the cause: a counting bug that was fixed after that experiment had already run.

The answer is that the criterion is indeed too lenient, and the reason is on the record already.

The system decides an experiment is finished when three consecutive rounds produce no new serious findings. To avoid counting the same problem twice, a finding is identified by the place in the code it points at. A later finding counts as new only if it names at least one location nobody has complained about yet.

The consequence is that a second, genuinely different fault in a function the panel has already criticised counts as nothing at all. Not as a duplicate, not as a lesser finding. It adds zero to the number the finishing rule reads.

This was not discovered this week. It was known, written down, and deliberately tested when the counting method was built in June. The function that does the counting carries a warning in its own description saying it must never be used to decide convergence, and names this exact blindness as the reason. A test exists whose entire purpose is to demonstrate the blindness. The plan written at the time states that switching this method on to decide convergence remained future work, conditional on building a component that can tell two different faults in one function apart, and on a confirming run.

That component was never built. The method was switched on to decide convergence anyway, in sixteen configuration files, covering every experiment from the sixth completed run onwards and every experiment still queued.

It then did what the warning said it would, twice, at the worst possible moment.

In one experiment, at the exact round the system declared itself finished, a confirmed serious finding was raised showing that a component never checks whether one of its settings is negative, and that a negative value makes an internal calculation exceed one, which is impossible for a quantity that is supposed to be a probability. It named three places in the code. All three had been complained about before, so it counted as zero.

In another, at the exact round that experiment finished, a confirmed and more serious finding was raised showing that a comparison strips out part of the text before checking whether two items are the same, so it compares the wrong things. It named two places. Both had been complained about before, so it counted as zero.

In both cases the finishing counter read zero, zero, zero, and the system stopped.

What this does not mean is that anything was lost. Both findings are demonstrated, recorded, and sitting in the results where anyone can read them. Nothing was hidden.

What it does mean is narrower and still serious. In those two experiments the phrase "no new serious findings" was not true. It meant "no new serious findings in a part of the code nobody had mentioned yet", which is a different and much weaker statement. Those two convergences were reached with a counter that was known to be blind in precisely the way that mattered.

Under the older stricter rule, two of the three experiments that finished on this criterion would have been refused, by a margin far wider than the uncertainty in reconstructing the numbers. The agent doing the work tried to explain that away as a technical artefact of how the calculation is indexed, and disproved its own explanation.

One correction to the framing of the original question. Only three of the six experiments finished on this rule at all. The other three finished on a different rule. So tightening this one alone would change nothing for half of them.

A correction to an earlier version of this document, which was circulated before the underlying data had been checked directly. That version said the two findings had been flagged fourteen and eleven times previously, and described them as two separate problems, one of which was the negative-setting fault. Both details were wrong. The counts are not what matters and were not accurate; what matters is that every location each finding named had already been mentioned, so both counted as zero. The negative-setting fault is one of the two findings, not a separate third one. The substance of the finding survives the correction unchanged, and is if anything firmer: it has now been reproduced by running the system's own counting function over the recorded results, which returns the same zero, zero, zero that the experiments recorded at the time.


## Part Two. The Cross Experiment Memory, And The One That Nearly Ruined The Capstone

The system keeps a memory across experiments, recording how often each class of flaw turned out to be real. That memory has been recording faithfully and feeding nothing. The task was to connect it, so the memory informs the starting estimate of how risky a piece of work is.

The mechanism was built correctly and the arithmetic checks out. The starting estimate moves in the right direction and by a bounded amount, and the memory never overrides a verdict reached by running code, which was tested by deliberately feeding it a maximally wrong belief and confirming the evidence still won.

But the independent check found what the builder missed, and it is serious.

The connection was attached to a switch that is already turned on in eleven configuration files, including the four cells of the capstone experiment, the zero plant control, and the physics and biology experiments that are next in the queue. None of those files was written with any intention of connecting the memory to anything.

Two consequences follow.

The zero plant control would stop being a control, because its starting estimate would be shaped by memory accumulated during three earlier experiments. That is an uncontrolled variable inside the one instrument built to have none.

Worse, the memory accumulates as experiments run. The capstone crosses two mechanisms on and off across four cells, and the whole design depends on those four cells being independent of one another. With the memory connected, the fourth cell's starting estimate would depend on the first three having already run. The cells would be coupled, and the comparison the capstone exists to make would be worthless.

That would not have announced itself. The experiment would have completed and produced numbers.

The fix is one line of intent: a separate switch, defaulting to off, so connecting the memory becomes a deliberate act rather than something inherited from eleven files written for other reasons.

One honest correction to my own earlier description. I called the memory advisory only. That is slightly too strong. It cannot override a verdict, which was proven. But the risk estimate does feed a downstream threshold, and a case can be constructed where it changes an outcome. Replaying the real archive found no such case at any setting tested, so this is a property of the data rather than a guarantee of the design, and it should be described that way.


## Part Three. The Literature Retrieval, Which Reaches The Prompt And Then Breaks

The component that fetches academic papers has been fetching them for weeks and delivering them nowhere. The task was to connect it.

It is now genuinely connected. The independent check built a prompt at the shipped settings and found the paper summary inside it, which is what was demanded as proof this time rather than a count of characters parsed.

Two things stop it being switched on.

Turning it on crashes the run report. A character in one paper's extracted text is an unpaired fragment of a symbol, left over from the way the PDF was converted, and the code that writes the final report cannot encode it. That write is unprotected, unlike the one directly above it. The experiment would complete and then fail to record itself.

And the retrieval is fetching the wrong papers. A finding about a numerical rounding problem in a variance calculation produced a search that got truncated part way through a two word technical phrase, leaving one ambiguous word. The search engine matched that word in a completely different field and returned a paper about machine learning forgetting its training. There are three separate faults in how the search text is built: it cuts multi word technical terms in half, it prepends an internal label that means nothing to an academic search, and it feeds programming identifiers into a search of scientific literature.

That last point matters more than it sounds. If this had been switched on as instructed, it would have looked like it was working. Papers fetched, summaries written, injection recorded in the logs. And the panel would have been reading irrelevant material on every round.


## Part Four. The Severity Adjuster, Which Works And Does Not Earn Its Place

A component exists to bring down the severity of findings that models have overstated. It needed a missing part built first, which was done, and it was then tested against the two hundred and ninety three real findings already recorded.

Its own verdict, and the independent check agrees after reproducing the numbers, is that it should not be switched on. It does not improve the honesty of the severity scores enough to justify the risk of distorting them.

That is a perfectly good outcome. The instruction was to use it only if it demonstrably helps, and it does not, so it stays off and the reasoning is recorded.


## Part Five. Two Faults Found And Fixed While Testing

Neither of these was on the list of things to check. Both were found by following the first set of problems outward.

The first. Turning on literature retrieval crashes the report, and the reason is a single character. Text pulled out of a PDF can contain half of a character, the leftover of a symbol that did not survive extraction whole. The most common one is the first half of the block of characters used for mathematical italics, so it appears in exactly the kind of paper this component fetches. The programming language stores that half character quite happily and refuses to write it out, so nothing complains until the moment something is saved.

Three places were tested, and all three fail. Writing the report fails, which means an experiment finishes and then cannot record itself. Writing to the log fails. And sending the text to one of the reviewing models fails, which kills the round in progress rather than the record at the end. That last one is the worst of the three and was not in the original diagnosis.

Both have been fixed, and in the right order: the character is now cleaned out at the point the text enters the system, which protects all three, rather than patching each place it leaves. The report writing has a second guard as well, because a completed experiment should never be lost to a stray character, and when that guard fires it says so inside the report rather than quietly substituting.

The second. Running the test suite writes into the archive.

The archive is the record of what the reviewing panel actually did. It is never edited, and corrections are filed beside it rather than applied to it. But one part of the machinery opens an archive file for writing the moment it is loaded, and the tests load it, so every test run has been appending imitation results into the same file that holds real experiment history. Three hundred and thirty two such lines have accumulated, continuously since the middle of May. Someone reading that file afterwards cannot tell the imitation entries from the real ones without checking the names line by line, and nothing in the file says any of it is artificial.

This was found by noticing that the archive showed as changed after a test run that should have touched nothing.

The fix sends the test output to a temporary location instead. The existing three hundred and thirty two lines are being left exactly where they are, because they sit interleaved with genuine records, and rewriting an archive to tidy it is the thing the rule against editing exists to prevent.


## What Is Needed From You

One decision is now settled and needs only your confirmation rather than your ruling. The cross experiment memory has been given its own separate switch, defaulting to off, so that connecting it is always a deliberate act and never something inherited. That was the recommendation and it is now built and tested, including tests that were checked by deliberately restoring the old behaviour and confirming they fail against it. Nothing in the current queue connects the memory. If you want it connected anywhere, say where.

One genuine decision is open, and it is the more consequential of the two.

The counting method that decides when an experiment is finished is running in a mode its own authors wrote down as not yet fit for that job, and it has twice let a confirmed serious finding pass unseen at the closing round. Three choices follow. Build the missing component that can tell two different faults in one function apart, which is real work and delays the queue. Switch the counting back to the stricter method, which would have refused two of the three convergences and means those experiments run longer and cost more. Or continue as is and record plainly, in the results and in any paper, that convergence in these experiments means no new serious findings in previously unmentioned parts of the code, which is a weaker claim than the one currently being made.

There is a fourth option worth naming because it is cheap. The blindness only bites when a confirmed serious finding lands in the final rounds. That is checkable after the fact, at no cost, on every run. A run could be allowed to finish as it does now, and then simply be flagged if a confirmed serious finding arrived during the closing rounds, which is exactly the check that surfaced both of these cases in the first place.

Two decisions can wait until the retrieval work finishes. Whether to switch on literature retrieval at all once the search text is fixed, and which model should judge whether a retrieved paper is actually relevant. That second question is being tested now, comparing the current choice against two alternatives on a set of deliberately difficult cases, including several traps where a paper shares a word with the finding in an entirely different technical sense.


## A Note On Method

Every one of these problems was found before anything ran. The pattern that has repeated all week held again: the components were individually correct and broke against the things they had to coexist with. Two of the four were marked ready by the agents that built them, and downgraded only when a separate check reproduced the work rather than reading the reports.

The memory and capstone coupling in particular was invisible from inside the component. It was only findable by asking which configuration files already had the relevant switch turned on.


Written under CDSFL note standard v1.2 (14 May 2026).
