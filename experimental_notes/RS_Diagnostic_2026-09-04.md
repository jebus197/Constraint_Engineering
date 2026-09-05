## Context Restore And Self Diagnostic, 2026-09-04 03:18 Bst

> **Retrospective mirror, created 2026-09-05.** This note was written as a spoken-word file only; `tts-output-protocol` requires both forms and the markdown copy was never made. Content is the spoken version's, unaltered apart from headings. Source: `~/Desktop/CDSFL_tts/RS_Diagnostic_2026-09-04.txt`.


## Your Diagnosis Was Correct

You suspected that several compactions running without a context restore had left me working from a summary rather than from the project's actual state. That is what was happening, and the restore changed three substantive conclusions I had already given you. Two of them I had given you as finished work.

## What The Restore Changed

First, and most importantly, the threshold defect. I reported it as a defect that had gone unnoticed for 146 days. That was wrong in an important way. The recovery record shows that on 28 August a two model instrument panel mutation tested this very gate: they replaced it with a function that always returns yes, and 321 tests still passed. The record states plainly that the gate, live in every one of nineteen configurations, could admit every fix silently. So the project had already measured the symptom eight days before last night's review found the cause.

What last night added is the mechanism, and it is still worth having: the threshold formula was derived with one variable frozen at the value one, and that variable is the very quantity the gate tests.

But there is a sharper finding underneath, which only appeared once both halves were in view. The gap was closed on 28 August by a test, and the test works. It uses parameter values that make the threshold positive, so the gate genuinely rejects and the mutation is caught. At the parameter values every real run actually uses, the threshold comes out as minus one nineteenth, which clamps to zero and admits everything. So the test proves the gate can reject in principle while never touching the case that occurs in practice. That is the same failure the whole reduction discussion has been about, appearing inside the instrument built to prevent it.

Second, the rubric, which you asked me to check on the grounds that it sounded like a very old term. It is not archaic. It is the authority. The live work queue records a standing ruling: the numeric severity cut of 0.7 stays, and it is described there as the operational proxy for a consequence based rubric that was pre-registered and frozen in May, which is authoritative wherever the rubric and the number disagree. Moving the number requires a new dated pre-registration. So my audit finding is sharper than I presented it: the authority and its proxy disagree on 45.6 percent of cases in exactly the band where the gate is decided, and nothing reports that gap.

Third, the seat contrast, which you approved. The tracker gives the reasoning I could not find last night. Nine of twenty eight archived runs were already effectively single model runs, six seats all filled by one model, and they converged. The recorded finding states that with one model, diversity has to come from instruction conditions, which is exactly the contrast that lapsed in April. So it is the mechanism that decides whether a lone researcher can use the harness at all.

## What Else The Restore Surfaced That I Did Not Have

A live work queue to the second bench run that I did not know existed. A recovery script that is named as the authority on live state. A standing proposal of yours, recorded as decision 7, for a free simulated experiment against an external and entirely untested target, on the grounds that the machinery has spent too long examining itself. A measured figure for scaling: correlation between architectures of 0.564 across 289 observations, from which panel size is not the scaling axis. And a note that the local Wolfram licence expires on 11 September, which is one week away.

## Self Diagnostic

Before the restore I made four measurement errors in three hours. Every one had the same shape: a conclusion drawn from a narrow slice without checking the population it claimed to describe. I scanned four configuration files out of forty four. I called four settings unreachable without checking for command line flags. I counted a verdict using a text label the code never writes. I read phrase occurrences inside model replies as if they were events.

After the restore I have made four substantive claims and verified each with at least two independent tools, including one that corrected the headline finding of the entire previous night. The difference is not carefulness. It is that the restore supplied the record those checks needed. Your diagnosis identified the cause correctly and the remedy worked.

The honest caveat is the hour. It is now past four in the morning. The panel process you named is the right control and I intend to use it on everything from here, but the reviewers are most useful against work that is already written down, and there is little value in generating more of that tonight.

## One Question Back To You

You asked whether you had answered the first part of decision 3, the question about where the reduction work belongs and whether it should enter the unified equation. You have not. You replied with a long and substantive question of your own, not a ruling, and it deserves a considered answer from me rather than a four in the morning one. You also asked whether I had missed the collapsed single equation the way the outside models did. I have not checked that yet, and with the restore now done it is a straightforward thing to check properly rather than a guess.

