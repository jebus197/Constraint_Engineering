# Gemini's duplicate detection advice, tested against the project's own data

2026-08-16, 04:10 BST. Written under CDSFL note standard version one point four. Every claim below was tested with tools against real project data rather than assessed by reading. No paid model dispatch.


## The short answer

Gemini's mathematics is correct. Its recommendation does not apply to this project, and adopting it would make the similarity function measurably worse.

Nothing it proposes is new to the project. One thing it identifies as the critical weakness of the method turns out not to apply at all, and the reason is a design choice made here some time ago.

The advice would be sound for a different problem: ten thousand documents, long texts, general vocabulary. This project has one hundred and sixty five critical findings, signatures of four tokens, and a vocabulary of numbers.


## Claim one. Jaccard similarity over n-grams is the right measure

Correct, and the project already does exactly this. Tier two of the similarity function computes Jaccard overlap. No change indicated.


## Claim two. Comparing every pair is prohibitively slow, so use MinHash

This is the load bearing claim and it fails on measurement.

Gemini's worked example is ten thousand papers, which requires roughly fifty million comparisons. The project's whole archive is one hundred and sixty five critical findings, which is thirteen thousand five hundred and thirty pairs.

Measured: those thirteen thousand five hundred and thirty exact comparisons complete in fifteen milliseconds.

The problem Gemini solves is about three thousand seven hundred times larger than the one this project has.


## Claim three. The MinHash theorem

Gemini states that the probability of two sets sharing a minimum hash value is exactly their Jaccard similarity. This was tested directly: two sets with a true Jaccard of zero point three three three were passed through four thousand independent hash functions, and the collision rate came out at zero point three zero one.

The theorem holds. Gemini is right about the mathematics.


## Claim four. Error shrinks as one over the square root of k

True in general, and misleading here. This was tested at two set sizes.

On large sets of three hundred tokens, the scaling behaves as advertised: mean absolute error falls from zero point zero eight three at sixteen hash functions to zero point zero three one at one thousand and twenty four.

On the project's actual signatures, which have a measured median of four tokens, the same sixty four fold increase in computation improves error from zero point zero nine four to zero point zero six eight, and then it plateaus.

The reason is that with four tokens, Jaccard can only take a few discrete values. The error floor is set by the coarseness of the sets, not by the number of hash functions. Buying more hashing buys almost nothing.

Tested against real project signatures rather than synthetic ones, MinHash at two hundred and fifty six hash functions produced a mean absolute error of zero point zero zero seven, but a maximum error of zero point three five eight.

That maximum matters. Same defect pairs sit at a median overlap of zero point five five nine, and different defect pairs at zero. A worst case error of zero point three five is large enough to move a pair across the decision boundary.

So the trade is: introduce up to zero point three five of error into a decision made near zero point five, in order to save fifteen milliseconds. That is a straightforward loss.


## Claim five. The semantic boundary, which Gemini calls the critical limitation

Gemini's argument is that lexical methods fail when two documents use different words for the same idea. Its own worked example is one document saying reduced thermal load and another saying decreased heat dissipation. It states that n-gram methods would register zero similarity, and recommends vector embeddings to fix this, while noting they are far more expensive.

That example was run through the project's actual signature extractor.

Both sentences produced the identical signature: the tokens seventeen, two, three hundred and fifty, four hundred, and Z C dash seventeen. The Jaccard score was one point zero zero zero. A perfect match.

The reason is that the similarity function does not extract words. It extracts numbers, units, claim identifiers and symbols. Numbers do not have synonyms. Four hundred is four hundred in every phrasing.

As a control, a sentence on the same topic with different quantities scored zero point one one one.

So the vulnerability Gemini presents as the critical weakness requiring expensive machinery is a weakness of general word based n-gram matching. It is not a weakness of what this project built. The design already sidesteps it, and did so before the question was asked.


## Claim six. Machines converge, humans vary

Gemini asserts this, marks it as requiring verification, and the founder notes that Gemini earlier argued the opposite in a turn that is no longer visible. A source that reverses itself on the same question within one conversation is not evidence in either direction.

The project already has a better answer from peer reviewed measurement, obtained independently. Researchers ran identical duplicate detection algorithms over messy human written bug reports and over structured machine generated output. Simple word counting scored zero point four zero on human text and zero point nine six on machine output. A deep neural network scored zero point three two and then zero point nine five. Language model embeddings scored zero point six two and then zero point nine three.

The founder's original instinct is supported by that measurement. It does not need Gemini's assertion, and it should not rest on it.


## What would be worth adopting

Nothing.

Every technique Gemini names is either already implemented here, or solves a problem this project does not have, or would reduce accuracy at this project's scale.


## Where Gemini would be right

At scale, and it is worth knowing where that line sits.

Exact all pairs comparison was measured at increasing sizes. One hundred and sixty five findings takes five milliseconds. One thousand takes zero point one six seconds. Two thousand takes zero point six five seconds. Five thousand takes four and a half seconds.

The argument for MinHash becomes real somewhere past two thousand findings in a single comparison set. The largest single run this project has produced carried forty eight critical findings. That is roughly forty times of growth before the question arises at all.

If Bench Run Two produces runs an order of magnitude larger than anything so far, this should be revisited. Not before.


## What generalises beyond this case

Three things, offered as hypotheses rather than conclusions.

The first is that the choice of features mattered more than the choice of algorithm. Gemini optimised the algorithm while assuming the features were words. The advantage this project has comes from choosing features that are immune to paraphrase, not from any cleverness in the comparison. Where a domain has canonical identifiers, preferring the identifiers over the prose appears to be the higher leverage decision.

The second is that a technique can be standard, correct and widely recommended, and still be wrong for a given scale. MinHash exists to trade accuracy for speed. A system that does not need the speed is paying the accuracy cost for nothing.

The third is a boundary condition worth stating because it is testable. The reason MinHash performs poorly here is that signatures are small, with a median of four tokens. If findings grew richer in quantities, that error would fall toward the large set curve. This yields a falsifiable prediction: at a median signature size around thirty tokens, MinHash error at two hundred and fifty six hash functions should approach the large set figure of roughly zero point zero three five. That has not been tested and no run currently produces signatures of that size.


## A note on how this was assessed

Gemini's response was not evaluated by reading it and forming a view. Each checkable claim was run against project data or against a controlled experiment: the theorem was verified over four thousand hash functions, the scaling was tested at two set sizes, the error was measured against one thousand one hundred and forty four real signatures extracted from the archive by the project's own function, and Gemini's own worked failure case was executed through the live extractor.

That is the only reason the semantic boundary claim was caught. Read on its own terms it is persuasive, correctly reasoned, and would have justified building something expensive and unnecessary.

Written under CDSFL note standard v1.4 (13 August 2026).
