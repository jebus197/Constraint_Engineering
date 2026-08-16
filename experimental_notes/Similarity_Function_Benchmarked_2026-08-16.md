# The similarity function, measured against the outside world

2026-08-16, 03:20 BST. Written under CDSFL note standard version one point four. Two rounds of external research, six independent strands, no paid model dispatch beyond the research itself.


## What the similarity function is

The similarity function is the rule that decides whether two critical findings describe the same defect or two different ones. The founder named it on 16 August 2026. Before that the code called it the combined identity rule, and this assistant had been calling it several invented things, which is why the founder did not recognise his own criterion when it was described back to him.

The decision matters because a review ends when no new critical findings appear. Merging two real defects into one can therefore end a review early, and an early stop looks exactly like success.

The rule has three tiers and none of them asks a model to judge.

Tier one is location. A finding naming a symbol or heading that nothing has flagged before is new. This costs nothing to compute.

Tier two is the stem signature. It takes the hard tokens out of two findings, meaning the numbers, the units, the claim identifiers, the symbols and the formulae, and measures how much those two sets overlap. It ignores the prose entirely.

Tier three is the computed outcome. It asks one narrow question per pair: do these two findings assert the same computed value? It answers same, different, or unknown. It can only merge two findings. It can never grant novelty to one. That bound is deliberate, and it is what makes its mistakes cheap: a wrong merge costs a finding, whereas a wrong split could fake a convergence.


## What was measured internally

Across six completed runs and one hundred and sixty five critical findings.

Tier two covers one hundred and sixty one of those one hundred and sixty five findings, which is ninety seven point six percent. Pairs labelled as the same defect share a median overlap of zero point five five nine. Pairs labelled as different defects share a median of exactly zero. The separation test returns a probability of one point nine times ten to the power minus twenty five.

That median of zero is the striking figure. It does not mean different pairs overlap a little. It means the typical pair of findings about different defects shares no hard token at all.

Tier three covers ninety four of the one hundred and sixty five, which is fifty seven percent. On pairs labelled the same defect it answered same nineteen times and unknown nine times. It answered different zero times. Not once in the entire sample did it call a same defect pair different.

For comparison, a rival tier was built to a design proposed by the model panel. That rival perturbed the target document and compared how two falsifiers responded. Measured on the same archive it returned a probability of zero point seven one, meaning no association whatever between its output and defect identity. It was removed from the code on 12 August 2026.


## How this compares to published work

The nearest established problem is duplicate bug report detection: given a newly filed bug report, decide whether it describes a fault someone has already reported.

After nineteen years of published research, the best systems find the right match roughly fifty five to sixty five percent of the time when allowed ten guesses, and roughly thirty five to forty two percent of the time on a single guess.

A second finding from that literature is more surprising and it supports the choice made here. A benchmark published in the ACM Transactions on Software Engineering and Methodology in 2023 found that a keyword matching method from 2011 outperformed every deep learning successor on five of six projects, by an average of twenty two percent. Plain full text search, meaning exact word matching, beat two neural models on all six.

So choosing token matching over neural methods is not a bold call. In this literature it is close to the expected outcome.


## Why the internal numbers look so clean

Because the problem here is easier than the published one, on four counts, and the reason is worth understanding.

When two humans report the same bug, they use the same words only about ten to fifteen percent of the time. Two people, two vocabularies, two mental models. That vocabulary problem is the entire difficulty of the published task.

Findings in this project are written by frontier models, under one shared directive, against the same document, and the hard tokens are copied verbatim out of that shared source. A quantity or a claim identifier appears in both findings because both models quoted the same string from the same artefact, not because two minds independently converged. That is a different and much easier task, and it has its own name in the literature: near duplicate detection over a shared substrate.

There is a direct measurement of how much this matters. Researchers ran the same duplicate detection algorithms over messy human written bug reports and over structured machine generated output. Simple word counting scored zero point four zero on human text and zero point nine six on machine output. A simple lexical rule scored zero point four one and then zero point nine seven. A deep neural network scored zero point three two and then zero point nine five. Language model embeddings scored zero point six two and then zero point nine three.

Identical code. Accuracy rises from about a third to near perfect purely because the input is dense with identifiers. And on the dense input, the language model embedding is the worst of the four methods.

That table is the strongest published support the founder's original claim has. Where text is packed with numbers and identifiers, sameness becomes decidable without understanding anything, and understanding stops paying for itself at exactly that point. The credit belongs to the material, not to the design.


## The ratings, stated without softening

Two research strands rated the work independently and broadly agreed.

Engineering design: seven out of ten. Engineering artefact: six out of ten. Honesty of reporting: eight out of ten. Application novelty: five out of ten. Evidence strength as reported: three out of ten. Novelty of the similarity function itself: two out of ten. Publishable today: two out of ten.

The summary verdict was competent internal engineering with a below publication evaluation.

The similarity function is not a new idea. Extracting quantities and identifiers and comparing the resulting token sets is standard practice in record linkage, citation matching and biomedical record matching. The closest single piece of prior art is the Comprehensive Quantity Extractor, published at the EMNLP conference in 2023 and peer reviewed, which extracts value, unit, condition and the concept a quantity attaches to, from exactly this kind of text.

What has no direct prior art, as far as the research could find, is the application: a deterministic identity function over machine generated findings, used to decide when an automated falsification loop has stopped producing new defects. That gap is real but narrow.


## The Bletchley Park question, checked against primary sources

The founder asked whether the wartime cryptanalysts who learned to recognise individual German operators were doing the same kind of measurement. The historical record supports the premise and inverts the lesson, and the correction is useful.

Two distinct practices are being merged.

The first is identifying who was transmitting. Morse operators have a characteristic sending rhythm, called a fist. Bletchley Park's own institutional history records that intercept operators could recognise an enemy operator's fist and use it to track a station that had moved frequency. The Allies later mechanised this as TINA, which tape recorded transmissions and took mathematical measurements of every dot, dash and space, described in a declassified United States Navy document on technical intelligence from Allied communications intelligence.

But that work belonged to traffic analysis, which is the business of working out which pile a message belongs in, which network it came from, which submarine sent it. It was not part of breaking Enigma. And it never worked especially well. An article in the NSA Technical Journal from October 1957, now declassified, still describes mechanised fist recognition as an effort to develop a systematic process, twelve years after the war ended. That article is titled A Last Resort.

The second practice is exploiting operator habit to break keys. This includes the Herivel tip, where a lazy operator left the rotors where they sat and so revealed the ring setting. It includes cillies, meaning easily guessed message keys, the canonical case being a clerk who kept using the letters C I L, his girlfriend's name. And it includes stereotyped message openings, such as the German for nothing to report.

This second practice is what broke Enigma. It is not operator identification at all.

The thing that actually drove the Bombe was the crib, meaning a predicted literal piece of plaintext. The distinction that matters, in the researcher's words: style told the analysts which pile a message belonged in, and the crib told them what the message said. A crib is a content anchor, not a style signature.

Mapped onto this project: style would identify which model wrote a finding, which is already known and requires no work. The crib is the hard token lifted verbatim from the shared document.

The similarity function already implements the crib. It is the half of the Bletchley method that did the actual work.


## Whether adding a writing style tier would help

It would not. It would actively hurt, for two reasons.

The first is that the two signals are anti correlated rather than independent. Two findings about the same defect, written by two different models, are by construction as far apart in writing style as it is possible to be. Adding a style measure would push apart precisely the pairs that need merging.

The second is a hard floor on text length. A peer reviewed study published in Digital Scholarship in the Humanities in 2015 tested authorship attribution across English, German, Polish, Hungarian and Latin, and found that stable attribution needs between two thousand five hundred and five thousand words. Critically, that floor was method independent: support vector machines, nearest neighbour classifiers, character n-grams and part of speech trigrams all needed roughly the same amount of text. Below it the signal is noise.

A finding is a paragraph. That is two orders of magnitude below the floor.

The founder's separate intuition, that he could tell four frontier models apart by how they write, is empirically supported. Machines do this at ninety seven point one percent accuracy across five candidate models, and trained humans outperform most commercial detectors. But that is a different question asked of far more text.


## The blunt judgement

The research's closing verdict was that this project is under evidencing a sound method, and that it is not a close call.

The method is right for the material. The separation measured is large. The strongest peer reviewed evidence on the nearest analogous task says simple retrieval beats sophisticated learned models.

But the headline statistics describe the easy seventy two point six percent of pairs, against labels a model generated, with no baseline comparison, no stated operating threshold, and error bars that assume an independence the data does not have.

None of that is a reason to change the method. All of it is a reason to distrust the numbers.

The risk this project carries is not that the similarity function is too simple. It is that nobody can currently tell how well it works on the cases where it matters.


## Three specific weaknesses

The first is that the hard cases were discarded before measurement. Three hundred and eighteen pairs were labelled out of four hundred and thirty eight same location pairs. The remainder sat in an ambiguous band and were excluded. Those are, by construction, the difficult ones. Removing the ambiguous middle before measuring separation is a known way to make results look better than they are, and a reviewer would send the evaluation back.

The second is that the answer key is a machine. Every peer reviewed study in this area uses a human triager's judgement as ground truth. This project used a sentence embedding model to decide which pairs were really the same. That model is independent of both tiers, so the measurement is not circular, but it is a machine grading machine output.

The third is that the wrong statistic was reported. A probability value states that two groups differ. What a reviewer needs is the operating point: at the setting actually used, how often is the rule right, how often is it wrong, and with what confidence interval.


## The recommendation

Change nothing about the method.

Fix the evaluation, and one action fixes most of it. Hand label the excluded ambiguous pairs, using two annotators with disagreements adjudicated and the agreement rate reported. Then re-report performance across the full set as a three way outcome: merge automatically, send to a human, or split automatically, with the threshold chosen to bound how often the rule wrongly merges two findings.

That single action replaces the model generated labels exactly where they were failing, converts a probability value into an operating point a reviewer can act on, closes the excluded band problem, and creates the only test set against which any future improvement can be measured. The research estimates a few hours of founder time.

Status of that work: proposed only. No code exists and no labelling has begun.


## Two corrections to earlier reporting

The first concerns coverage. This assistant reported fifty seven percent coverage as though it described the similarity function as a whole. Fifty seven percent is tier three's coverage alone. The rule's reach is tier two's ninety seven point six percent. The earlier figure understated the work.

The second concerns determinism. This assistant defended the design on the grounds that it is fully deterministic. That is not quite true, because the ground truth labels came from a pinned embedding checkpoint, so the evaluation pipeline was never purely deterministic end to end. The defensible claim is auditability: every step can be read and checked by hand. That claim holds. The stronger one did not.


## One figure that remains unresolved

Two research strands disagree on how many pairs were excluded from the evaluation. Simple arithmetic gives one hundred and twenty, being four hundred and thirty eight same location pairs less the three hundred and eighteen labelled. One strand reports eighty seven. The discrepancy has not been reconciled and neither number should be quoted until it is.

Written under CDSFL note standard v1.4 (13 August 2026).
