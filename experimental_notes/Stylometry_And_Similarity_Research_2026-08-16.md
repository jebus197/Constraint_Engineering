# External research: Bletchley fingerprinting, stylometry, and the similarity function

2026-08-16. Three strands under `re`, prompted by the founder's question about whether
Bletchley Park's operator-recognition work is the same kind of measurement the similarity
function performs. Full unedited text; sources cited inline, peer-reviewed work
distinguished from preprints.


---

## Strand: The Bletchley operator-identification claim, checked against primary sources

**RESEARCH FINDINGS: THE BLETCHLEY OPERATOR-IDENTIFICATION CLAIM, CHECKED**

---

## 1. Did they actually identify individual operators by habit? Yes — but two separate things are being run together

The historical record contains **two distinct practices** that the founder's framing merges. Keeping them apart is the whole analytical payload of this answer.

### Track A — Identifying *who* was transmitting (real, documented, but not part of the Enigma break)

**Operator "fist" recognition by ear.** Bletchley Park's own institutional account states it plainly: intercept operators "were able to recognise the characteristic Morse style (or 'fist') of an enemy radio operator, which was as distinctive as handwriting, which often helped track down a station transmitting on an unexpected frequency." ([Bletchley Park, Y Stations: Interception](https://www.bletchleypark.org.uk/about-y-stations/work-at-the-y-stations/y-stations-interception/)) — institutional history, not peer-reviewed, and the "as distinctive as handwriting" comparison is museum phrasing, never measured.

**TINA and RFP — the mechanised versions.** The strongest primary source I found is the declassified US Navy SRH-025, *Battle of the Atlantic IV: Technical Intelligence from Allied Communications Intelligence*, §11, verbatim:

> "TINA, the purpose of which was to identify a radio operator by his sending characteristics, consisted of making a tape recording of each U-boat transmission and taking mathematical measurements of each dot, dash, and space. RFP was a method of transmitter identification in which high-speed photographs were taken of a transmission, making possible an analysis of the transmitter's power supply."

and that both were "extensively utilized in conjunction with HF/DF in **attempting** to identify individual U-boats." ([HyperWar/ibiblio transcription of SRH-025, ch. 8](https://www.ibiblio.org/hyperwar/ETO/Ultra/SRH-025/SRH025-8.html)) Note the word "attempting," and note that the document gives **no** success rates, false-positive rates, or effectiveness assessment whatsoever.

So: TINA = the *human* (behaviour, keying rhythm). RFP = the *machine* (transmitter power-supply signature). These are different targets and the distinction matters for question 3.

**The internal SIGINT view, twelve years later.** The best evidence on how well fist-matching actually worked comes from an NSA Technical Journal article, now declassified — Wayne E. Stoffel, "Chatter Patterns: A Last Resort," *NSA Technical Journal*, October 1957, 63–75, reprinted in Vera R. Filby (ed.), *A Collection of Writings on Traffic Analysis*, US Cryptologic History, Sources in Cryptologic History Vol. 4, NSA Center for Cryptologic History, 1993 ([full PDF, governmentattic.org](https://www.governmentattic.org/8docs/NSA-TrafficAnalysisMonograph_1993.pdf)). Stoffel writes:

> "There have been considerable experimentation with and study of the variable characteristics of a Morse operator's transmitting habits or 'fist' in an effort to develop a systematic process of recording and analysis which would permit ready recognition of the individual at the key."

Read that carefully. In 1957, inside NSA, mechanised fist recognition was still described as an *effort to develop* a systematic process — not a working routine. Stoffel's entire paper proposes analysing operators' **chatter habits** (which procedure signals they favour, in what combinations) as an alternative, and titles it *A Last Resort*. His conclusion: the method "has application only in limited cases," is complex, and "would undoubtedly require the services of a skilled chatter reader."

The same paper also documents that fist recognition was real enough to be used as *informal authentication by the operators themselves*: "Many experienced operators prefer to rely on aural recognition of 'fist' characteristics and frequently ask the other end to 'send V's' (QSV)." A human challenge–response over style.

**The organisational home of this work at BP** was traffic analysis, not cryptanalysis: SIXTA (Hut Six Traffic Analysis, so named November 1943), log readers reconstructing networks from call signs and frequencies, a Direction Finding Plotting Room, and a "Fusion Room" where traffic analysis met decrypts. ([Bletchley Park, Traffic Analysis](https://www.bletchleypark.org.uk/our-story/traffic-analysis/); the GC&CS Sixta History is [TNA HW 43/68, catalogue ref C11177401](https://discovery.nationalarchives.gov.uk/details/r/C11177401)).

### Track B — Exploiting operator *habit* to break keys (this is what broke Enigma, and it is not operator identification)

**The Herivel tip.** John Herivel arrived at BP January 1940 and reasoned in February 1940 about what a lazy or rushed operator would physically do: if he set the ring settings with the rotors already in the machine, he might leave the rotors where they sat and use those three letters as the ground setting for his first message of the day. Hut 6 plotted first-message indicators from every station on a grid — the "Herivel square" — and when several lazy operators were present on a net, entries clustered around the true ring setting, "narrowing the options for the ring settings down from 17,576 to a small set of possibilities, perhaps 6 to 30." First success 22 May 1940; superseded once the bombes arrived from August 1940. It yielded ring settings only, not rotor order or plugboard. ([Wikipedia, Herivel tip](https://en.wikipedia.org/wiki/Herivel_tip), citing Sebag-Montefiore 2000; Welchman, *The Hut Six Story*, 1982/1997; Smith, *Station X*, 1998; Herivel, *Herivelismus and the German Military Enigma*, M&M Baldwin, 2008; Good, "Enigma and Fish," in *Codebreakers*, OUP 1993.)

**Cillies.** Easily-guessed message settings — AAA, BBB, keyboard-adjacent or diagonal sequences; on the four-rotor Abwehr machine, four-letter names and German obscenities; and failing to change the rotors between parts of a multi-part message. ([Wikipedia, Cillies](https://en.wikipedia.org/wiki/Cillies), citing Kahn 1991, p. 113.) Attribution of the coinage is itself disputed — Dennis Babbage wrote to Welchman in October 1982 suggesting Dilly Knox named them ([Joel Greenberg, Babbage's monograph on Cillies](https://www.joelgreenberg.co.uk/copy-of-key-facts-welchman-1)).

**Stereotyped openings and the crib.** *Keine besonderen Ereignisse* ("nothing to report" — "a phrase regularly used by one German outpost in North Africa"), *An die Gruppe*, weather-station formats, and Rejewski's own note that "the greater number of messages began with the letters ANX — German for 'to', followed by X as a spacer." Deliberately provoking such a message was called *gardening*. ([Wikipedia, Cryptanalysis of the Enigma](https://en.wikipedia.org/wiki/Cryptanalysis_of_the_Enigma), citing Taunt 1993 p. 108, Kahn 1991.)

**The operator who sent the same message twice — this is Lorenz, not Enigma.** On 30/31 August 1941 a German operator sent a ~4,500-character message on the Lorenz SZ40, the far end asked in clear for a repeat, and he retransmitted it **on the same key setting** (indicator HQIBPEXEZMUG) — but not identically: he abbreviated *SPRUCHNUMMER* to *NR*, used further abbreviations, and altered punctuation, shortening it to ~4,000 characters. John Tiltman worked out both plaintexts over about ten days, yielding roughly 4,000 characters of key, from which Bill Tutte derived the entire machine structure. ([Wikipedia, Cryptanalysis of the Lorenz cipher](https://en.wikipedia.org/wiki/Cryptanalysis_of_the_Lorenz_cipher); [Bill Tutte Memorial Fund, The Tiltman Break](https://billtuttememorial.org.uk/codebreaking/the-tiltman-break/))

**The critical negative finding.** The main survey article on Enigma cryptanalysis — drawing on Kahn, Welchman, Taunt and Rejewski — contains **no claim anywhere that individual operators were identified by habit for cryptanalytic purposes**. The habits exploited were *class-level*: "German operators do X." Not "operator 47 does X." I searched specifically for a documented case of a named or individually-tracked German operator feeding the Enigma break and did not find one.

---

## 2. Was it genuinely similarity measurement, or retrospective framing?

**Split verdict, and the split is the useful part.**

**Track A (fist/TINA/RFP) genuinely was similarity measurement**, and the retrospective framing is fair. TINA took physical measurements of dot, dash and space durations off undulator tape and compared them against a held file of previously recorded signatures. That is nearest-neighbour matching against a template library, executed with paper tape and calipers. What was compared: *timing vectors*, not content. What was being matched: *the human at the key*, treated as a stable class with many samples.

**Track B (Herivel, cillies, cribs) was not similarity measurement at all**, and calling it that is a genuine misreading:

- **Herivel** is a *density estimate*. Plot the day's first-message indicators; the lazy ones cluster near the true ring setting. Nothing is compared to anything pairwise — a prior is imposed on a key space and the mass is read off.
- **Cillies** are a *constrained search*. The operator's free choice is drawn from a small predictable subset, so brute force gets cheap. That is a reduction of the hypothesis space, not a comparison.
- **Cribs are a rejection test, and this is the point most worth carrying forward.** The bombe did not search for a match. It exploited Enigma's property that no letter ever enciphers to itself: you slide the crib along the ciphertext and *eliminate* every position where a letter maps to itself, then run the survivors and stop on a logical contradiction. The bombe was a contradiction-finding machine. Turing and Welchman built a falsifier, not a matcher.

So the precise answer: Bletchley's operator work contained one real similarity measurement (fist matching, in the traffic-analysis department) and one thing that looks like similarity measurement but is actually a prior plus a falsification procedure (the Enigma break). The founder's intuition has correctly spotted that *something* similarity-shaped happened. It happened in the department that wasn't reading the messages.

One concept from Track A that transfers cleanly and is worth naming: Stoffel's **"continuity"** — "bridging a communications change by equating a given element appearing before the change with a different element appearing after it… without reference to the underlying meaning." That is structurally identical to asking whether a finding raised in round 3 and a finding raised in round 5 denote the same defect, without needing to understand the defect. Stoffel is explicit that continuity is achieved "by means of whatever characteristics are available that can be trusted to be **unique**" — cheapest and most reliable characteristics first, stylistic ones held in reserve for hard cases. That is precisely the hard-token-first architecture already in place.

---

## 3. Fist recognition in Morse: real, and mechanised how far?

**Real as a human capability:** yes, well attested, and attested independently of Bletchley. The claim predates the war — telegraph operators recognising each other by keying rhythm is documented from the late nineteenth century, cited in the peer-reviewed literature by Monrose & Rubin, "Keystroke dynamics as a biometric for authentication," *Future Generation Computer Systems* 16(4), 2000, 351–359, and in Kristen Haring, *Ham Radio's Technical Culture*, MIT Press, 2007, p. 23 (via [Wikipedia, Keystroke dynamics](https://en.wikipedia.org/wiki/Keystroke_dynamics)). Caveat: the WWII "fist of the sender" origin story is repeated widely across the biometrics literature, often citing each other rather than a primary military source. Treat the *existence* of the capability as solid and the *standard origin narrative* as thinly sourced.

**The most consequential documented use of fist recognition was a false positive — engineered.** Before Pearl Harbor, the Imperial Japanese Navy put the Strike Force's radio operators **ashore** at Kure, Sasebo and Yokosuka to transmit routine traffic, precisely because American analysts knew those operators' fists and would pair them with direction-finding on the carriers' call signs and conclude the carriers were still in home waters. The technique tracked the *operator*, and the Japanese exploited exactly that gap. Source: Robert J. Hanyok, "'Catching the Fox Unaware': Japanese Radio Denial and Deception and the Attack on Pearl Harbor," *Naval War College Review* 61(4), Autumn 2008, 99–124 ([JSTOR 26396966](https://www.jstor.org/stable/26396966); [USNWC Digital Commons](https://digital-commons.usnwc.edu/nwc-review/vol61/iss4/10/)). Rochefort is widely quoted as saying he knew where *Akagi* was because he recognised her "same ham-fisted radio operators" — I could not fetch a primary text for that exact quote (403 on both USNI and the USNWC PDF) and flag it as attributed-but-unverified. Note also that Philip H. Jacobsen contested substantial parts of the surrounding radio-deception narrative in *Cryptologia* (e.g. "Foreknowledge of Pearl Harbor? No!", July 2003), establishing that the Strike Force kept genuine radio silence — the deception traffic came from shore. That refines rather than removes the point: fist recognition worked *as designed*, identified the right humans, and produced the wrong strategic conclusion.

**Mechanisation:** attempted from the war onward, never cleanly solved for the human component.
- TINA *was* the mechanisation attempt — measure every dot, dash and space off tape. As of Stoffel 1957 it still had not become a systematic routine.
- Machine *decoding* of hand-sent Morse succeeded much earlier and separately: MIT Lincoln Laboratory's MAUDE (Morse Automatic DEcoder), late 1950s. Decoding what was sent turned out far more tractable than identifying who sent it.

**The modern descendants split along the TINA/RFP line, and only one of them has a real genealogy:**

- **RFP → Specific Emitter Identification / RF fingerprinting.** This is the *hardware* branch, and it is a large active field. But the honest finding: the recent systematic survey traces the field's earliest literature contribution to Langley's 1993 radar SEI work, and locates its origins in "military radar," **not** in WWII operator work. (Aziz, Huso, Sciancalepore, Oligeri, "The Chronicles of Radio Frequency Fingerprinting," [arXiv:2606.10031](https://arxiv.org/html/2606.10031v1), June 2026 — **preprint, not peer-reviewed**, PRISMA methodology.) The Bletchley→SEI line of descent is largely folk history.
- **TINA → keystroke dynamics.** This is the *behavioural* branch, and here the genealogy is explicitly claimed in the peer-reviewed literature (Monrose & Rubin 2000, above). This is the true modern descendant of the fist.

**Both descendants carry quantified, sobering limits:**

- RF fingerprinting: peer-reviewed, ACSAC '23. Accuracy roughly *halves* — from about 1.0 to about 0.5 — merely because the radios were powered off and on between collecting training and test data. Not different radios, not different days of weather: the same radios, power-cycled. Best mitigation via I-Q preprocessing lifted accuracy from ~0.45 to ~0.85. (AlHazbi, Sciancalepore, Oligeri, "The Day-After-Tomorrow: On the Performance of Radio Fingerprinting over Time," *Proc. 39th ACSAC*, 2023, [DOI 10.1145/3627106.3627192](https://dl.acm.org/doi/10.1145/3627106.3627192); [arXiv:2305.05285](https://arxiv.org/abs/2305.05285).) Also relevant: Al-Shawabka et al., "Exposing the Fingerprint: Dissecting the Impact of the Wireless Channel on Radio Fingerprinting," IEEE INFOCOM 2020 — models were partly learning the *channel*, not the transmitter.
- Keystroke dynamics: peer-reviewed, DSN 2009, and the numbers are the single most useful calibration point in this whole answer. 51 subjects each typing the *same* 10-character password 400 times on the *same* keyboard — about as controlled as a behavioural biometric can possibly get. Best three of fourteen detectors achieved equal-error rates of **9.6% to 10.2%**. Against that, the European access-control standard EN-50133-1 requires a false-alarm rate under 1% with a miss rate no worse than **0.001%**, and the authors state flatly that "no anomaly detector has achieved these error rates in repeated evaluation." (Killourhy & Maxion, "Comparing Anomaly-Detection Algorithms for Keystroke Dynamics," *IEEE/IFIP DSN-2009*, 125–134, [PDF](https://www.cs.cmu.edu/~maxion/pubs/KillourhyMaxion09.pdf).)

Roughly four orders of magnitude between what behavioural style delivers under ideal conditions and what a modest operational standard demands.

---

## 4. The honest through-line — and where the analogy breaks

### What genuinely transfers

**(a) The real Bletchley lesson is "attack the rigid, low-entropy part of the message," and the project has already implemented it.** Herivel, cillies, ANX, the weather formats, *Keine besonderen Ereignisse* — every one of these works because the *protocol* was constrained and the operator's free choices were few. None of them work on the free prose. A similarity function keyed on numbers, units, claim identifiers, symbols and formulae lifted verbatim from a shared source document is the same move: it operates on the constrained, protocol-fixed part of a finding and ignores the free prose. Median Jaccard 0.559 same-defect versus 0.000 different-defect is a clean separation of exactly the kind Bletchley lived on. The founder implemented the actual lesson and is now asking whether he should adopt the more romantic half instead.

**(b) The residual belongs to a human, and that is the historical answer too.** 97.6% coverage leaves 2.4%. Stoffel's answer for the analogous residual was not a cleverer algorithm — it was "a skilled chatter reader," deployed as an explicit last resort on a small number of hard cases. Human-in-the-loop for the residual is what the record actually recommends.

**(c) The bombe is a better import than the fist.** If the failure mode that matters is *merging two real defects into one and ending the review early*, then the historically-warranted mechanism is not a better matcher but a **rejection rule**: a deterministic veto that refuses a merge on hard contradiction — different numeric values, incompatible units, different claim identifiers, mismatched formulae — regardless of how high the Jaccard score is. That is the no-letter-encodes-to-itself constraint, and it is the reason the bombe worked. Cheap, deterministic, and it fails in the safe direction (splitting rather than merging).

### Where it breaks — and I think the founder is over-reading it

**(1) Attribution and co-reference are different problems.** Fist recognition asks *who sent this?* — author identity is the answer. The similarity function asks *do these two findings denote the same defect?* — author identity is a **nuisance variable**. And in CDSFL, author identity is already known: you have the metadata telling you which model produced which finding. The skill the founder is describing — telling four frontier models apart by their writing — is not hard for the machine, it is *free*, and it answers a question the system does not need to ask.

**(2) Using style would likely make the system worse in a specific, predictable way.** Two findings from the same model share house style. If any stylistic-similarity signal enters the merge decision, same-model pairs get a similarity bonus that cross-model pairs do not. Since the stopping rule depends on merges, that biases toward **over-merging same-model duplicates and under-merging cross-model agreements** — precisely inverting the value ordering, because two different models converging on the same defect is the higher-information event. This is testable now, with no new machinery: on your existing labelled pairs, compute similarity within-model versus across-model, restricted to *known-different-defect* pairs. If within-model scores systematically higher, style is a confound, not a signal, and the current hard-token design is protecting you from it.

**(3) The statistical basis is not there.** Every documented fist-recognition capability rests on sustained observation of the same operator: Stoffel requires "a significant volume of activity" with "preferably verbatim" chatter copy; keystroke dynamics needed 400 repetitions per subject to reach 9.6% EER. A handful of findings per model per round is not that regime.

**(4) Style is unstable in a way hard tokens are not.** RF fingerprints halve in accuracy across a power cycle; keystroke rhythm gives 9.6% EER under laboratory-ideal conditions. LLM style is *less* stable than either — it shifts with temperature, system prompt, and model version. A determinism requirement and a style-based signal are close to incompatible: your similarity function would silently change behaviour on every model update.

**(5) Style is spoofable; hard tokens are anchored outside the model.** The most consequential documented deployment of fist recognition in history was defeated by moving the operators. The current hard tokens are lifted *verbatim from the shared source document* — they are anchored to an artefact neither model controls. That is a real and underrated security property of the existing design.

**(6) The topic/author confound cuts against style here specifically.** Authorship attribution degrades sharply when topic shifts, and under topic-controlled conditions simple word-level n-grams beat BERT and RoBERTa (Altakrori, Cheung, Fung, "The Topic Confusion Task: A Novel Scenario for Authorship Attribution," Findings of EMNLP 2021, [arXiv:2104.08530](https://arxiv.org/abs/2104.08530) — peer-reviewed). In CDSFL the topic is *held constant by construction* — every finding is about the same source document. That strips out the variance authorship attribution feeds on while leaving intact the topic-driven, source-anchored signal that hard tokens already capture. Two independent arguments landing on the same conclusion: you are already measuring the right variable.

**(7) A caution about the founder's own intuition — it is almost certainly true and still not evidence.** Telling four frontier models apart is closed-set attribution over four classes with thousands of prior samples per class and unlimited deliberation time. That is the easy end of the problem. Machines do it well too (Uchendu, Le, Shu & Lee, "Authorship Attribution for Neural Text Generation," EMNLP 2020, [ACL Anthology](https://aclanthology.org/2020.emnlp-main.673/) — peer-reviewed; eight neural generators plus human text, distinguishable). The machine is not failing at the founder's task. It is being asked a different one.

---

## Verification status

**[VERIFY:current]** Three items I could not confirm against a primary or peer-reviewed source and which should not be repeated as established: (a) the etymology of TINA from *Serpentina* (undulator tape) and the "Z service / Z intelligence" designation — these appear only on [jproc.ca/rrp/rfp_tina.html](http://jproc.ca/rrp/rfp_tina.html), an amateur-historian site that is Cloudflare-blocked to automated fetch and which I therefore could not read directly; (b) the claim, from the same source, that "British and American RFP gave poor results when a TINA analysis was performed" — plausible and consistent with Stoffel 1957, but unverified; (c) Rochefort's "same ham-fisted radio operators" quotation — both USNI and the USNWC PDF returned HTTP 403.

**Peer-reviewed:** Killourhy & Maxion (DSN 2009); AlHazbi et al. (ACSAC 2023); Al-Shawabka et al. (INFOCOM 2020); Altakrori et al. (Findings of EMNLP 2021); Uchendu et al. (EMNLP 2020); Monrose & Rubin (FGCS 2000); Hanyok (*Naval War College Review*, professional peer-reviewed journal); Mosteller & Wallace (*JASA* 58(302), 1963, 275–309).
**Preprint, explicitly not peer-reviewed:** Aziz et al., arXiv:2606.10031.
**Declassified government primary/near-primary:** SRH-025; Stoffel 1957 in Filby (ed.), NSA CCH 1993.
**Institutional history, not peer-reviewed:** Bletchley Park museum pages; TNA HW 43/68 catalogue record.
**Tertiary, used only where it names its own primary citations (Kahn, Welchman, Taunt, Rejewski, Sebag-Montefiore, Herivel):** Wikipedia.

**Concrete falsifiable test this analysis generates:** on the existing labelled finding-pair corpus, compute within-model versus across-model similarity restricted to known-different-defect pairs. The prediction is that any style-sensitive metric scores within-model pairs systematically higher — which would confirm style as a confound and independently justify the current hard-token design rather than supplementing it.

---

## Strand: Stylometry and authorship attribution: what transfers, and what does not

# Stylometry and Authorship Attribution: What Transfers to CDSFL's Similarity Function

## Headline answer

Stylometry is a mature field with real numbers, and the founder's intuition about telling frontier models apart is **empirically supported** — machines do it at 97.1% five-way, and trained humans beat most commercial detectors. But it answers a different question from the one CDSFL asks, and for CDSFL's specific case the two signals are worse than orthogonal: they are **anti-correlated**. Two findings about the same defect written by different models are, by construction, stylometrically maximally distant. Adding style features to the similarity function would push same-defect cross-model pairs *apart*, which is exactly the failure mode (early convergence via missed merges, or the reverse) that the project is trying to avoid.

The historical Bletchley analogy also inverts under scrutiny — see §5.

---

## 1. Established stylometry: methods and real numbers

**Burrows's Delta** (Burrows 2002, *Literary and Linguistic Computing* 17(3):267–287, peer-reviewed) z-scores the frequencies of the *n* most frequent words and takes mean absolute difference. Reported accuracies are high but on generous conditions:

- Early Modern English plays: 87 of 94 single-authored plays correctly attributed, **92.6%** (Segarra et al., arXiv:1610.05670 — **preprint**). Candidate set is small (dozens of playwrights); texts are whole plays, ~20,000+ words.
- Optimisation work finds 200–300 most-frequent-words is the sweet spot, and that switching Delta's distance to cosine gives a substantial gain (Rybicki & Eder, *JQL* 18(1), 2011, peer-reviewed; Evert et al. on cosine Delta).

**Text length is the binding constraint.** Eder, "Does size matter? Authorship attribution, small samples, big problem", *DSH* 30(2):167–182, 2015 (peer-reviewed) ran controlled degradation across English, German, Polish, Hungarian and Latin. The minimum sample for stable attribution was **2,500 words (Latin prose) to ~5,000 words (most vernacular novels)**. Critically, this floor was **method-independent** — SVM, k-NN, character 3-/4-grams and POS-trigrams all needed roughly the same amount of text. Below ~5,000 words the signal is noise.

This is the single most important number for CDSFL. A finding is a paragraph. It is two orders of magnitude below the floor at which stylometry is known to work.

**Author-set size is the second constraint.** Luyckx & Daelemans, "The effect of author set size and data size in authorship attribution", *LLC* 26(1):35–55, 2011 (peer-reviewed) systematically varied both. On their Personae corpus of **145 authors**, accuracy sits around **50%** — high above the 0.7% chance baseline, but nowhere near usable. Their comparison sets were 8 authors (ABC_NL1) and 13 (AAAC_A), where accuracy is far higher.

**At web scale it degrades further.** Koppel, Schler & Argamon, "Authorship attribution in the wild", *Language Resources and Evaluation* 45:83–94, 2011 (peer-reviewed) used **10,000 blogger.com authors** with an open candidate set (the true author might be absent). Their contribution was a *robustness* score that lets the system abstain: you buy high precision by answering only on the subset where the similarity margin is large. Precision and recall trade against candidate-set size, known-text quantity and snippet length — the paper's four named parameters.

**Character n-grams** are the workhorse feature. Stamatatos, "A survey of modern authorship attribution methods", *JASIST* 60(3):538–556, 2009 (peer-reviewed) reports that in head-to-head comparisons on the same corpora, character n-grams beat lexical and syntactic features, and that they hold up better than word features when train and test corpora differ.

**Modern neural.** LUAR (Rivera-Soto et al., "Learning Universal Authorship Representations", EMNLP 2021, peer-reviewed, https://aclanthology.org/2021.emnlp-main.70/) trains contrastively over hundreds of thousands of authors (Reddit, Amazon reviews, fanfiction) and produces 512-d author embeddings. Its finding relevant here: "a surprising degree of transfer is possible between certain domains, it is not so successful between others" — i.e. cross-domain generalisation is patchy, not solved.

**Shared-task reality check.** At PAN 2021 (fanfiction, cross-domain authorship verification) the winning meta-classifier scored AUC 0.917 / c@1 0.917 / F1 0.916 (https://ceur-ws.org/Vol-2936/paper-147.pdf). The PAN 2022 organisers then changed the task to *cross-discourse-type* pairs (essays, emails, text messages, memos) and explicitly wrote that the earlier fanfiction results "may have given the false impression that authorship verification is an almost solved problem" (https://ceur-ws.org/Vol-3180/paper-184.pdf). It is not. Shared-task overviews are lightly reviewed, not journal peer-reviewed — treat accordingly.

---

## 2. "I could tell four frontier models apart" — supported, with caveats

**Yes, and the numbers are strong.**

Sun, Yin, Xu, Kolter & Liu, "Idiosyncrasies in Large Language Models", **ICML 2025** (peer-reviewed; https://arxiv.org/abs/2502.12150). Fine-tuning a text embedding model on LLM outputs gives **97.1% accuracy on five-way classification of ChatGPT / Claude / Grok / Gemini / DeepSeek**, with pairwise comparisons often above 99%. Two findings matter for the founder's question:

- The signal is **rooted in word-level distributions** — shuffling the words in a response barely dents accuracy.
- It **survives rewriting, translation and summarisation by an external LLM**, which the authors read as the idiosyncrasy also being encoded at the semantic level.

That second point is the one that should give the founder pause about his own framing. If model identity survives paraphrase *because it is partly semantic*, then model identity and content identity are not cleanly separable — they are entangled. That cuts against, not for, using style as an independent axis.

**Code is even easier.** Bhattacharjee et al., "I Know Which LLM Wrote Your Code Last Summer", ACM AISec 2025 workshop (peer-reviewed; https://arxiv.org/abs/2506.17323): **95.40% five-way** attribution across Gemini 2.5 Flash, Claude 3.5 Haiku, GPT-4.1, Llama 3.3, DeepSeek-V3, and **97.56%** binary between GPT-4.1 and GPT-4o, on 32,000 compilable C programs from 8 LLMs.

**Humans: the founder is probably in the good tail, not the average.** Two peer-reviewed anchors bracket it:

- Clark et al., "All That's 'Human' Is Not Gold", **ACL 2021** (https://aclanthology.org/2021.acl-long.565/): untrained non-experts distinguish GPT-3 from human text **at chance**, and three training interventions lift them only to **55%**.
- Russell, Karpinska & Iyyer, **ACL 2025** (https://aclanthology.org/2025.acl-long.267/): annotators who *frequently use LLMs for writing* are excellent detectors without training; the **majority vote of five such experts misclassified 1 of 300 articles**, beating most commercial and open-source detectors, and holding up **under paraphrasing and humanisation attacks**. Their reported cues were a mix of lexical clues ("AI vocabulary") and higher-order judgements of formality, originality and clarity.

That last paper is the founder's claim, near enough, validated — for AI-vs-human. I found no peer-reviewed study measuring *human* accuracy at four-way discrimination *among* frontier models. His specific claim is plausible by extension but **not directly evidenced**. [SPECULATIVE on the four-way human case.]

**Does it survive paraphrase and prompt change? Partly, and much less than the headline numbers suggest.**

- Krishna et al., "Paraphrasing evades detectors of AI-generated text, but retrieval is an effective defense", **NeurIPS 2023** (https://arxiv.org/abs/2303.13408): their 11B DIPPER paraphraser drops DetectGPT from **70.3% to 4.6%** detection at 1% FPR without appreciably changing semantics.
- Wang et al., **M4GT-Bench**, ACL 2024 (https://arxiv.org/abs/2402.11175): on the *multi-way "which model generated this"* task, RoBERTa reaches **99.26% accuracy in-distribution** — and collapses to **60.30%** when the target generator (BLOOMz) is held out of training. Attribution is a memorisation of seen generators, not a general capability.
- Dugan et al., **RAID**, ACL 2024 (https://arxiv.org/abs/2405.07940): 6M generations, 11 models, 8 domains, 11 adversarial attacks. Detectors are "easily fooled by adversarial attacks, variations in sampling strategies, repetition penalties, and unseen generative models."
- Soto et al., "Few-Shot Detection of Machine-Generated Text using Style Representations", ICLR 2024 (https://arxiv.org/abs/2401.06712): using LUAR-style authorship embeddings, pAUC 0.905 at N=5 documents and 0.9806 at N=10, on ~128-token documents; degrades under DIPPER and recovers only when paraphrased examples are added to the support set.

**Bottom line for §2:** model identity is legible, but it is legible *to a classifier trained on that model's outputs*, over multiple documents, in-distribution. Change the prompt regime, the domain, or the generator, and it falls over. And CDSFL already knows which model produced each finding — the provenance is a label in the pipeline, not something to be recovered. **The whole capability is free and already available, which means it adds nothing.**

Also, a terminology trap worth flagging: "LLM fingerprinting" in the current literature (LLMmap, Chain & Hash, DuFFin, zeroth-order gradient methods) means *IP-protection provenance* — probing a served model with crafted queries to prove it is a copy of yours. It is not text attribution. Searching that term will return the wrong literature.

---

## 3. The critical distinction — and it is worse than orthogonal

**These are different problem families.** Authorship attribution asks *who wrote this*, and treats topic as the **nuisance variable to be suppressed**. CDSFL asks *do these describe the same defect*, and must treat author (model) as the nuisance variable to be suppressed. Same confound, opposite ends of the telescope.

The evidence that these two signals genuinely fight each other is strong and peer-reviewed:

- **Bischoff et al., "The Importance of Suppressing Domain Style in Authorship Analysis"** (arXiv:2005.14714, **preprint**; https://arxiv.org/pdf/2005.14714). Fixed authors, swapped domains between train and test. Character-trigram approaches lost **up to 55.4 percentage points** of accuracy — meaning over half of what looked like "author signal" was domain/topic signal. Domain-adversarial training cut the loss to 3.6%.
- **Altakrori, Cheung & Fung, "The Topic Confusion Task"**, Findings of EMNLP 2021 (peer-reviewed; https://aclanthology.org/2021.findings-emnlp.359/). By deliberately switching the author–topic configuration between train and test they separate errors caused by topic shift from errors caused by failure to capture style. Stylometric features augmented with POS tags were **least** susceptible to topic variation; BERT and RoBERTa **performed poorly and were beaten by simple word n-grams**.
- **Wegmann, Schraagen & Nguyen, "Same Author or Just Same Topic?"**, RepL4NLP @ ACL 2022 (peer-reviewed; https://aclanthology.org/2022.repl4nlp-1.26/). The title is the whole point: representations trained on authorship-verification objectives encode content, because authors write about recurring topics. They had to *construct* same-author/different-topic triplets to force content-invariance.
- **"Style or Content? Evaluating Style Classifiers with Controlled Content Overlap"** (arXiv:2606.07103, **preprint**). Uses parallel Bible translations to vary content overlap α continuously. Low-overlap-trained classifiers collapse when content cues are removed — i.e. much of what is called "style classification" is content shortcut.

**Now apply that to CDSFL directly.** The similarity function's target label is *same defect*. Its input population contains two kinds of same-defect pair:

1. Same defect, same model (e.g. two rounds of the same reviewer) — high style similarity, high content similarity.
2. Same defect, **different** models — high content similarity, and *by §2's evidence, systematically low style similarity*, because models are 97% separable on style.

A style-augmented similarity would score type-2 pairs lower than type-1 pairs on the same underlying defect. Since type-2 pairs are precisely the ones whose merge matters (cross-model corroboration of a real defect), style would inject a bias exactly where the cost is highest. **Style is not merely uninformative here; its expected contribution has the wrong sign.**

**So: does stylometry help topical/semantic identity at all? No, and the field's own methodology says so** — every serious style-representation paper in the last five years spends its effort *removing* content from style representations, or content-controlling the evaluation. Nobody is running the arrow the other way, because there is no reason to.

**One honest exception.** Style helps when the task is *segmentation* — "did the author change partway through this document" (intrinsic plagiarism detection, PAN multi-author writing style analysis). That is boundary detection, not equivalence. And it performs badly even at that: PAN-PC-2011 intrinsic systems report plagdet around **0.168** (recall 0.428, precision 0.108), versus far higher scores for extrinsic (reference-comparison) detection. Where you have the source text to compare against — which CDSFL *does*, since findings quote a shared document — you use the content anchors and ignore style.

---

## 4. Combining lexical/content with stylistic features for near-duplicate / same-topic detection

The literature here is not stylometry — it is **duplicate detection**, and CDSFL is squarely inside it whether or not it has been framed that way.

**Duplicate bug report detection** is the closest published analogue: many reporters, one underlying defect, free-text descriptions, and a merge decision. Findings:

- Jiang, Su, Treude, Shang & Wang, "Does Deep Learning improve the performance of duplicate bug report detection? An empirical study", *Journal of Systems and Software*, 2023 (peer-reviewed; https://www.sciencedirect.com/science/article/abs/pii/S016412122300002X). Indexed summaries of this paper report the finding that **lexical similarity is more important than semantic similarity** for the duplicate decision, and that IR+DL combined beats either alone in the *ranking* formulation. **Caveat: the full text is paywalled and returned HTTP 403; I could not verify the exact figures. Treat the direction as reported, the magnitudes as unverified.**
- The same body of work reports that deep-learning approaches **lose to plain IR** when the repository contains fewer than ~10k duplicate pairs. CDSFL's data is far below that.
- "Duplicate Bug Report Detection: How Far Are We?" (arXiv:2212.00548, **preprint**, later TOSEM) makes the same point about simple methods remaining competitive.

**Static-analysis warning deduplication** — the direct industrial analogue — uses **MinHash/LSH over Jaccard similarity**. That is the founder's current design, arrived at independently, and it is the standard answer in that domain. (Broder, "On the resemblance and containment of documents", SEQUENCES 1997, peer-reviewed, is the origin.)

**Hard content anchors beat text similarity in exactly CDSFL's setting.** Meuschke, Schubotz & Gipp's line of work on STEM plagiarism uses **mathematical expressions and identifiers** as text-independent features, on NTCIR-11 MathIR (~60M expressions across 105,120 arXiv documents), combined with citation patterns and images in the HyPlag hybrid system (Foltýnek, Meuschke & Gipp, "Academic Plagiarism Detection: A Systematic Literature Review", *ACM Computing Surveys* 52(6), 2019, peer-reviewed; https://dl.acm.org/doi/10.1145/3345317; and https://arxiv.org/pdf/1906.11761). The rationale is identical to the founder's: **formulae and citations survive paraphrase because they cannot be reworded.** So do claim IDs, units and chemical formulae. This is independent convergent validation of the hard-token design from a completely separate research community.

**Topic Detection and Tracking / story link detection** — "are these two stories about the same event" — found that weighting **event words** (named entities, times, places) gives significant improvement over bag-of-words baselines. Again: named-entity anchors, not style.

**Retrieval generally.** Thakur et al., **BEIR**, NeurIPS 2021 Datasets & Benchmarks (peer-reviewed; https://arxiv.org/abs/2104.08663): BM25 lexical matching is a highly competitive zero-shot baseline that beats dense neural retrievers out of domain. Hybrid sparse+dense is usually best; neither involves style.

**What I did not find:** any peer-reviewed work on deduplicating *review findings across multiple LLM reviewers of the same document*. The nearest published neighbours are the two above. That is a genuine gap, and worth stating plainly rather than dressing a blog post up as prior art.

---

## 5. The Bletchley framing, corrected

The historical record supports the founder's factual premise but inverts its lesson.

Operator idiosyncrasies were real and were exploited: **"cillies"** (predictable message keys — the canonical story is a clerk who kept using *CIL*, his girlfriend's name), and the Morse operator's **"fist"** (individual sending rhythm, later formalised as TINA), which was used alongside direction-finding and callsign analysis to **segregate traffic by operator and network** (sources: The National Museum of Computing, https://www.tnmoc.org/bh-16-menus-and-cribs; Bletchley Park, https://www.bletchleypark.org.uk/our-story/enigma-red-messages/; GCHQ, https://www.gchq.gov.uk/information/the-brown-network).

But the thing that actually drove the Bombe was the **crib** — a predicted literal plaintext string, from stereotyped messages: weather reports, "nothing to report", fixed openings. A crib is a **content anchor**, not a style signature. Style told the analysts *which pile a message belonged in*; the crib told them *what the message said*.

Mapped onto CDSFL: style = which model produced the finding (already known, no work required). Crib = the hard token lifted verbatim from the shared source document. **The project already implemented the crib. It is the right half of the Bletchley method, and the half that did the actual work.** [This mapping is my interpretation of the historical sources, not a claim any of them make.]

---

## 6. Two things that do transfer — both deterministic, neither requiring a model call

**(a) The impostors method, as a threshold replacement.** Koppel & Winter, "Determining if two documents are written by the same author", *JASIST* 65(1):178–187, 2014 (peer-reviewed); best PAN 2013 and 2014 systems were built on it. The idea, stripped of its authorship context: instead of thresholding sim(A,B) directly, ask whether A is more similar to B than A is to a randomly drawn crowd of *impostors*, repeated across randomly sampled feature subspaces. The output is a fraction in [0,1] that is **calibrated against the local difficulty of the comparison**, rather than a fixed cutoff.

For CDSFL: given two findings A and B, sample k other findings from the same review round as impostors, repeatedly sample random subsets of A's hard-token set, and count the fraction of trials in which B is A's nearest neighbour. Fully deterministic given a fixed seed, no embeddings, no model call. It converts "Jaccard 0.559 median" into a per-pair decision that adapts when a round happens to contain many near-neighbours — which is exactly when a fixed threshold over-merges and ends a review early.

**(b) The topic-confusion evaluation design, run in reverse.** Altakrori et al. deliberately crossed author against topic to attribute errors to the right cause. The CDSFL analogue is a stratification the project can run on data it already has:

> Split the same-defect pairs into (i) same-model pairs and (ii) cross-model pairs. Compare the hard-token Jaccard distributions. If cross-model same-defect pairs have materially lower Jaccard than same-model same-defect pairs, then the reported median of 0.559 is inflated by same-model pairs, and the function is weakest precisely where cross-model corroboration should be strongest.

A second, related check: the reported medians (0.559 same-defect, 0.000 different-defect) describe the *centres* of the two distributions, and the separation looks total. But the merge decision lives in the **tails**. The number that determines early stopping is the overlap between the upper tail of the different-defect distribution and the lower tail of the same-defect distribution — e.g. the different-defect 99th percentile against the same-defect 5th percentile. A median of 0.000 is consistent with a long right tail. That comparison, plus the coverage question for the 2.4% of findings with no hard tokens, is where the real risk sits.

---

## Verdict on the four questions

1. **Established methods work, at scale conditions CDSFL does not have.** Delta and character n-grams reach 90%+ on small candidate sets with 5,000+ word samples; ~50% at 145 authors; degrading and abstention-dependent at 10,000. The hard floor of ~2,500–5,000 words is method-independent. A finding is a paragraph.
2. **The founder's claim is supported for machines (97.1% five-way, ICML 2025) and plausible for a heavy LLM user (ACL 2025 experts near-perfect on AI-vs-human, robust to paraphrase).** But attribution collapses on unseen generators (99.26% → 60.30%) and paraphrase (70.3% → 4.6%), and CDSFL already knows the provenance for free. The capability is real and useless here.
3. **Different problem families, and for cross-model same-defect pairs the style signal has the wrong sign.** Every modern style-representation paper works to *strip content out of style*; nobody runs it the other way. Adding style would penalise exactly the pairs the project most needs to merge.
4. **Yes, there is combination work — and it consistently combines lexical with semantic, never with stylistic.** Duplicate bug reports (lexical > semantic; DL loses to IR below ~10k duplicates), math/citation-anchored plagiarism detection (independent convergent validation of the hard-token design), event-word story link detection, and BM25-plus-dense hybrid retrieval. The hard-token function is a well-precedented member of this family, not an improvisation.

**The honest recommendation: do not add stylometry. Add impostor-based calibration and run the same-model/cross-model stratification. Both are deterministic, both are cheap, and the second one is a falsification test the current design has not yet faced.**

[VERIFY:current] Two items rest on sources I could not fully open: the Jiang et al. 2023 lexical-vs-semantic magnitudes (ScienceDirect 403), and Luyckx & Daelemans' exact per-condition accuracies (Oxford Academic paywall). Directions are reported consistently across secondary indexes; exact figures unverified.

## Sources

**Peer-reviewed**
- Stamatatos, *A Survey of Modern Authorship Attribution Methods*, JASIST 2009 — https://onlinelibrary.wiley.com/doi/abs/10.1002/asi.21001 (PDF: https://icsdweb.aegean.gr/stamatatos/papers/survey.pdf)
- Burrows, *'Delta': A Measure of Stylistic Difference*, LLC 2002 — https://academic.oup.com/dsh/article/17/3/267/928360
- Eder, *Does size matter?*, DSH 30(2), 2015 — https://academic.oup.com/dsh/article-abstract/30/2/167/390738
- Luyckx & Daelemans, *The effect of author set size and data size*, LLC 26(1), 2011 — https://academic.oup.com/dsh/article-abstract/26/1/35/1009428
- Koppel, Schler & Argamon, *Authorship attribution in the wild*, LREC 45, 2011 — https://link.springer.com/article/10.1007/s10579-009-9111-2
- Koppel & Winter, *Determining if two documents are written by the same author*, JASIST 65(1), 2014
- Rybicki & Eder, *Improving Authorship Attribution: Optimizing Burrows' Delta*, JQL 18(1), 2011 — https://www.tandfonline.com/doi/abs/10.1080/09296174.2011.533591
- Rivera-Soto et al., *Learning Universal Authorship Representations*, EMNLP 2021 — https://aclanthology.org/2021.emnlp-main.70/
- Altakrori, Cheung & Fung, *The Topic Confusion Task*, Findings of EMNLP 2021 — https://aclanthology.org/2021.findings-emnlp.359/
- Wegmann, Schraagen & Nguyen, *Same Author or Just Same Topic?*, RepL4NLP @ ACL 2022 — https://aclanthology.org/2022.repl4nlp-1.26/
- Sun et al., *Idiosyncrasies in Large Language Models*, ICML 2025 — https://arxiv.org/abs/2502.12150
- Bhattacharjee et al., *I Know Which LLM Wrote Your Code Last Summer*, ACM AISec 2025 — https://dl.acm.org/doi/10.1145/3733799.3762964
- Krishna et al., *Paraphrasing evades detectors of AI-generated text*, NeurIPS 2023 — https://arxiv.org/abs/2303.13408
- Dugan et al., *RAID*, ACL 2024 — https://arxiv.org/abs/2405.07940
- Wang et al., *M4GT-Bench*, ACL 2024 — https://arxiv.org/abs/2402.11175
- Soto et al., *Few-Shot Detection of Machine-Generated Text using Style Representations*, ICLR 2024 — https://arxiv.org/abs/2401.06712
- Clark et al., *All That's 'Human' Is Not Gold*, ACL 2021 — https://aclanthology.org/2021.acl-long.565/
- Russell, Karpinska & Iyyer, ACL 2025 — https://aclanthology.org/2025.acl-long.267/
- Thakur et al., *BEIR*, NeurIPS 2021 D&B — https://arxiv.org/abs/2104.08663
- Foltýnek, Meuschke & Gipp, *Academic Plagiarism Detection: A Systematic Literature Review*, ACM CSUR 52(6), 2019 — https://dl.acm.org/doi/10.1145/3345317
- Jiang et al., *Does Deep Learning improve duplicate bug report detection?*, JSS 2023 — https://www.sciencedirect.com/science/article/abs/pii/S016412122300002X
- Huang et al., *Authorship Attribution in the Era of LLMs*, SIGKDD Explorations 26, 2024 — https://arxiv.org/abs/2408.08946

**Preprints / shared-task overviews (lighter review)**
- Bischoff et al., *The Importance of Suppressing Domain Style in Authorship Analysis* — https://arxiv.org/pdf/2005.14714
- *Style or Content? Evaluating Style Classifiers with Controlled Content Overlap* — https://arxiv.org/pdf/2606.07103
- Segarra et al., *Stylometric Analysis of Early Modern Period English Plays* — https://arxiv.org/pdf/1610.05670
- Meuschke et al., *Improving Academic Plagiarism Detection for STEM Documents* — https://arxiv.org/pdf/1906.11761
- *Duplicate Bug Report Detection: How Far Are We?* — https://arxiv.org/pdf/2212.00548
- PAN 2021 cross-domain AV overview — https://ceur-ws.org/Vol-2936/paper-147.pdf
- PAN 2022 AV overview — https://ceur-ws.org/Vol-3180/paper-184.pdf
- PAN 2024 Voight-Kampff overview — https://pan.webis.de/clef24/pan24-web/generated-content-analysis.html

**Historical**
- TNMOC, *Menus and Cribs* — https://www.tnmoc.org/bh-16-menus-and-cribs
- Bletchley Park, *Enigma Red messages* — https://www.bletchleypark.org.uk/our-story/enigma-red-messages/
- GCHQ, *The BROWN Story* — https://www.gchq.gov.uk/information/the-brown-network

---

## Strand: What this project should actually do next

## Direct answer first

The Bletchley analogy is a good instinct about *what similarity measurement is* and a poor guide to *what this project should build*. Operator fingerprinting solves "who wrote this" when the author is hidden. Your task is "do these two texts point at the same defect" when the author is already recorded in your own metadata. The stylometric tradition therefore has almost nothing to give you — but the record-linkage tradition, which is the other descendant of the same problem, has a great deal, and you are currently using about a third of it.

The judgement you asked for at the end, stated up front: **under-evidencing a sound method.** The method is close to what the literature would prescribe. The evaluation cannot currently support any claim about it.

---

## 1. What actually transfers from the Bletchley lineage

Two things worth separating.

**Authorship attribution does not transfer as a similarity feature — and may point the wrong way.** Your intuition that four frontier models are distinguishable by style is empirically correct: CodeT5-Authorship reports 95.40% multi-class accuracy across five LLMs on C programs and 97.56% on the harder GPT-4.1-vs-GPT-4o pair ([arXiv preprint 2506.17323](https://arxiv.org/abs/2506.17323); subsequently refereed at ACM AISec 2025, [10.1145/3733799.3762964](https://dl.acm.org/doi/10.1145/3733799.3762964)). A peer-reviewed PLOS One study finds stylometric features separate human from seven LLMs with near-perfect discrimination ([PLOS One 2025](https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0335369)). So the capability is real.

It is also useless to you, for two reasons. First, you already hold the author label — your own provenance discipline records which model raised each finding. The Bletchley problem was hard *because* the author label was missing. Second, and more interesting: in a multi-model panel, same-defect pairs are disproportionately **cross-model** (that is the whole point of convening a panel), while different-defect pairs include every within-model pair. If that holds in your data, author-style similarity is a *negative* predictor of defect identity, and adding it as a similarity feature pushes the wrong way.

That is falsifiable in one query on your existing 318 pairs: compute P(same model | same defect) against P(same model | different defect). If the first is lower, style is anti-correlated and must never enter as a similarity term. I would not assert the direction without that check — cross-round repeats by a single model are a real same-defect within-model case that could weaken it.

**What does transfer is the structural role.** Bletchley used operator habits to *partition traffic* before attacking it — that is blocking, not similarity. Author identity belongs in your system as a prior or a blocking key, never as a similarity score.

There is also a quiet strength in your current design worth naming. Because you lift only hard tokens from the shared source document, model-specific boilerplate ("Severity: High", stock phrasings) cannot inflate overlap. Systems that score full finding text are vulnerable to exactly this. You have already solved the stylometric contamination problem by construction.

---

## 2. The five evaluation weaknesses, ordered by value for effort

### (i) p-values instead of an operating characteristic — free, do this first

A p-value on 318 pairs answers "are these distributions different at all", which nobody doubts given 0.559 against 0.000. It says nothing about the decision you make.

Worse, the medians hide the failure mode. A different-defect median of 0.000 means most such pairs share no hard tokens — it tells you nothing about the *upper tail*, and false merges live entirely in that tail. Report the full distributions, an ROC and a precision-recall curve, and the chosen threshold with its false-positive and false-negative counts. PR matters because same-defect pairs are the minority class among all pairs ([Davis & Goadrich, ICML 2006](https://dl.acm.org/doi/10.1145/1143844.1143874) — peer-reviewed).

Do not report AUC alone. Hand shows AUC is incoherent with respect to misclassification costs, because it implicitly uses a different cost distribution for each classifier ([Hand, *Machine Learning* 77:103–123, 2009](https://link.springer.com/article/10.1007/s10994-009-5119-5) — peer-reviewed journal). Your costs are grossly asymmetric: a false merge can terminate a review early and lose a real defect; a false split costs one more round. So the operationally meaningful number is *recall on same-defect pairs at the threshold that bounds false merges near zero*. Cost: an afternoon, no new data.

### (ii) Model-derived ground truth and the excluded 27.4% — coupled, and the only fix that raises your ceiling

These are one problem. The band was almost certainly excluded because the embedding labeller could not resolve it, so re-including it requires human labels. That coupling is good news: you need to label 87 pairs, not 318.

Excluding the ambiguous middle has a name — it is a spectrum problem, and the diagnostic-accuracy literature is unambiguous that indeterminate cases must not be dropped, because doing so restricts the sample to an unrepresentative spectrum of extremes and inflates every accuracy measure ([Pavlou et al., *Radiology Research and Practice*, 2021](https://onlinelibrary.wiley.com/doi/10.1155/2021/5801662) — peer-reviewed; [Catalogue of Bias, Oxford CEBM](https://catalogofbias.org/biases/spectrum-bias/) — curated, not peer-reviewed). The standard remedy is a three-way table: positive, indeterminate, negative, reported separately.

On the labels themselves: using a sentence-embedding model as reference standard is imperfect-reference-standard bias. Direction of bias depends on whether index and reference errors are correlated ([Reitsma et al., *J Clin Epidemiol* 62(8):797–806, 2009](https://www.jclinepi.com/article/S0895-4356(09)00063-8/fulltext) — peer-reviewed). Here they probably are not strongly correlated — hard-token Jaccard and dense embeddings fail differently — which means your current numbers are more likely *attenuated* than inflated. That is the un-flattering-to-your-critics direction and I should say so plainly.

The fatal problem is not bias but ceiling. You cannot measure better-than-the-embedding-model, only agreement-with-it. The case you most care about — where hard tokens are right and embeddings smear two distinct numeric claims together — is invisible to this evaluation by construction.

Fix: double-annotate the 87 excluded pairs plus a stratified sample of the rest, adjudicate disagreements, report Cohen's κ or Krippendorff's α, and report the embedding labeller's own accuracy against the human labels. Cost: a few hours of your time.

Note the framing gift here. Fellegi and Sunter's original decision rule has three outcomes — link, non-link, and a middle band routed to clerical review ([Fellegi & Sunter, *JASA* 64:1183–1210, 1969](https://www.tandfonline.com/doi/abs/10.1080/01621459.1969.10501049) — peer-reviewed). Your 27.4% is not an embarrassment to be excluded; it is the review band, and its *size* is a headline result. That aligns exactly with your own HIL-is-by-design position.

### (iii) No baseline — cheap, and the first thing any reviewer asks

Three baselines, all trivial: unfiltered all-token Jaccard (does the hard-token restriction earn its keep?); character n-gram or TF-IDF cosine over full finding text; and a prevalence baseline of always-say-different. Include the embedding model itself, and expect it to look perfect — that artefact is itself the cleanest demonstration of why the labels must be human. Cost: hours.

### (iv) 318 pairs treated as independent — cheap, but only widens error bars

Each finding appears in many pairs, and findings cluster by defect and by source document; effective n is far below 318. Fix: bootstrap by resampling *findings* (or source documents), not pairs. Pang et al. show naive bootstrap coverage for AUC falling to 55–82% against a nominal 95% under substantial subject-level random effects, while cluster and hierarchical bootstrap hold ~95% ([*Frontiers in Veterinary Science* 10:1274786, 2023](https://pmc.ncbi.nlm.nih.gov/articles/PMC10728486/) — peer-reviewed). Cost: an hour. Value: lowest of the four, because it changes intervals, not point estimates. Do it last, for external credibility.

---

## 3. Should you add a stylometric or embedding tier?

**Stylometric: no.** Argued above — wrong quantity, input already known, plausibly wrong sign.

**Embedding: not yet, and not for the reason you usually give.** One honest correction: a pinned local checkpoint run on CPU is bit-reproducible, so "we avoid models because determinism" is not quite right. The real costs are reproducibility across *time* (checkpoint drift breaks old results) and **inexplicability** — you cannot tell a reviewer *why* two findings merged. That second one is the load-bearing objection and it is a good one.

The evidence also favours restraint. On the closest applied analogue — duplicate bug report detection — a systematic replication found a simple retrieval technique outperforming recently proposed deep-learning approaches on most projects, with REP (proposed a decade earlier) the overall best performer ([Zhang et al., *TOSEM* 32(4), 2023](https://dl.acm.org/doi/full/10.1145/3576042) — peer-reviewed journal; [preprint arXiv:2212.00548](https://arxiv.org/abs/2212.00548)). The fact-checking analogue reaches similar conclusions, with BM25 as a strong component rather than a discarded baseline ([Shaar et al., ACL 2020](https://aclanthology.org/2020.acl-main.332/) — refereed).

Recommendation: exhaust the deterministic upgrades in §4 first, measure them against human labels, and only then consider embeddings — as a **third tier applied solely to the review band**, with the merge decision still requiring a human. That is composable with what you have, not an alternative to it. And you must retire the embedding labeller from ground truth before it can enter the system, or you lose the ability to measure it at all.

---

## 4. The cheap deterministic signals you are not using

**IDF weighting of hard tokens — the highest-value change available.** Your Jaccard treats "mm" and "6.674e-11" as equally evidential. They are not. A single shared rare identifier should outweigh five shared common units. This is precisely what Fellegi-Sunter's log(m/u) weight derives from first principles, and what TF-IDF token metrics implement in practice; Cohen, Ravikumar and Fienberg found TF-IDF-weighted token metrics among the best performers on exactly this class of task ([IJCAI-03 IIWeb workshop, refereed](https://www.cs.cmu.edu/~wcohen/postscript/kdd-2003-match-ws.pdf)). IDF is deterministic, needs no model, and is computed from your own corpus. Zero new dependencies.

Falsification test before you build it: plot the IDF distribution of your hard-token vocabulary. If it is bimodal — a mass of common units and small integers plus a tail of rare constants and equation IDs — IDF will help substantially, mostly in the ambiguous band. If it is uniformly rare, IDF is near-uniform and gains little. One query.

**Containment alongside Jaccard.** Jaccard penalises size mismatch. A terse finding and a verbose one describing the same defect score low even when one token set contains the other. Broder's containment c(A,B) = |A∩B|/|A| is the right measure here ([SEQUENCES 1997, refereed](https://dblp.org/rec/conf/sequences/Broder97.html)). Caveat from my own falsification pass: raw containment is dangerous for low-cardinality findings — a finding whose only token is "10%" is fully contained in any long finding mentioning 10%. **IDF-weighted containment fixes both problems simultaneously**, and that combination is my concrete recommendation.

**Graded numeric tolerance, not string equality.** "9.8", "9.81", "9.807", "9.8 m/s^2" and "9.8 m s^-2" are five distinct tokens today. Canonicalise numbers and units, then compare with graded levels rather than binary equality — exactly Splink's `AbsoluteNumericDifferenceLevel` and percentage-difference levels ([Splink docs, MoJ](https://moj-analytical-services.github.io/splink/api_docs/comparison_level_library.html) — production tool, not a paper). Unit extraction and normalisation for scientific text is a solved tooling problem (grobid-quantities; see also [Numbers Matter!, arXiv:2407.10283](https://arxiv.org/abs/2407.10283) — **preprint**).

Critically: tolerance must be **graded, never collapsing**. The difference between 9.8 and 9.81 can itself be the defect. Exact / within 0.1% / within 1% / different, as weighted levels — the Fellegi-Sunter comparison-level design.

**The 2.4% coverage gap is a bigger risk than the number suggests.** Findings with no hard tokens cannot be compared at all. These are systematically the *conceptual* findings — "the argument in section 4 is circular" — which may be your most valuable ones. Check whether the 2.4% is random or structurally skewed toward architectural findings. If skewed, the coverage figure understates the problem badly. A deterministic fallback (section-anchor matching, or character 4-gram Jaccard) costs nothing.

**Blocking and MinHash/LSH: file, do not build.** At 318 pairs, irrelevant. At Bench Run 2 scale, token-blocking on rare tokens becomes worthwhile ([Papadakis et al., *ACM Computing Surveys* 53(2), 2020](https://dl.acm.org/doi/abs/10.1145/3377455) — peer-reviewed; [open PDF](https://helios2.mi.parisdescartes.fr/~themisp/publications/csur20-blockingfiltering.pdf)). But be clear that MinHash *approximates* Jaccard — it buys speed and costs accuracy. Adopting it now would be a strict loss.

---

## 5. Blunt closing judgement

**Under-evidencing a sound one.** Not close.

The method is right for the material. Identifier-dense technical text is the best case for token-based linkage, the separation you measured is large, and the strongest peer-reviewed evidence on the nearest analogous task says simple retrieval beats sophisticated learned models. Your instinct to stay deterministic is defensible on auditability grounds — just stop justifying it on determinism grounds, which is not quite true of a pinned checkpoint.

But your headline statistics describe the easy 72.6%, against labels a model generated, with no baseline, no operating threshold, and error bars assuming an independence the data does not have. None of that is a reason to change the method. All of it is a reason to distrust the numbers.

**Single highest-value next action:** hand-label the 87 excluded ambiguous pairs — double-annotated, adjudicated, κ reported — and re-report performance on the full 318 as a three-way operating characteristic (auto-merge / review / auto-split), with the threshold chosen to bound the false-merge rate and recall reported at that point.

That one action closes the spectrum problem, replaces model-derived labels exactly where they were failing, converts a p-value into an operating point, and creates the only test set against which IDF weighting can be evaluated. It is a few hours of your time and it unblocks everything else on this list.

The project's risk is not that the method is too simple. It is that nobody can currently tell how well it works on the cases where it matters.

---

## Sources

**Peer-reviewed (journal or refereed conference)**
- Fellegi & Sunter, "A Theory for Record Linkage", *JASA* 64:1183–1210, 1969 — https://www.tandfonline.com/doi/abs/10.1080/01621459.1969.10501049
- Cohen, Ravikumar & Fienberg, "A Comparison of String Distance Metrics for Name-Matching Tasks", IJCAI-03 IIWeb workshop (refereed workshop) — https://www.cs.cmu.edu/~wcohen/postscript/kdd-2003-match-ws.pdf
- Broder, "On the resemblance and containment of documents", SEQUENCES 1997 — https://dblp.org/rec/conf/sequences/Broder97.html
- Davis & Goadrich, "The relationship between Precision-Recall and ROC curves", ICML 2006 — https://dl.acm.org/doi/10.1145/1143844.1143874
- Hand, "Measuring classifier performance: a coherent alternative to the area under the ROC curve", *Machine Learning* 77:103–123, 2009 — https://link.springer.com/article/10.1007/s10994-009-5119-5
- Papadakis, Skoutas, Thanos & Palpanas, "Blocking and Filtering Techniques for Entity Resolution: A Survey", *ACM Computing Surveys* 53(2), 2020 — https://dl.acm.org/doi/abs/10.1145/3377455
- Zhang, Han, Vinayakarao, Irsan, Xu, Thung, Lo & Jiang, "Duplicate Bug Report Detection: How Far Are We?", *TOSEM* 32(4), 2023 — https://dl.acm.org/doi/full/10.1145/3576042
- Shaar, Babulkov, Da San Martino & Nakov, "That is a Known Lie: Detecting Previously Fact-Checked Claims", ACL 2020 — https://aclanthology.org/2020.acl-main.332/
- Reitsma, Rutjes, Khan, Coomarasamy & Bossuyt, "A review of solutions for diagnostic accuracy studies with an imperfect or missing reference standard", *J Clin Epidemiol* 62(8):797–806, 2009 — https://www.jclinepi.com/article/S0895-4356(09)00063-8/fulltext
- Pavlou et al., "Diagnostic Accuracy Studies in Radiology: How to Recognize and Address Potential Sources of Bias", *Radiology Research and Practice*, 2021 — https://onlinelibrary.wiley.com/doi/10.1155/2021/5801662
- Pang, Ju, Welch, Gauger, Liu, Zhang & Wang, "Nonparametric bootstrap methods for interval estimation of the AUC with correlated diagnostic test data", *Frontiers in Veterinary Science* 10:1274786, 2023 — https://pmc.ncbi.nlm.nih.gov/articles/PMC10728486/
- "Stylometry can reveal artificial intelligence authorship, but humans struggle", *PLOS One*, 2025 — https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0335369
- CodeT5-Authorship / LLM-AuthorBench, ACM AISec 2025 (refereed workshop) — https://dl.acm.org/doi/10.1145/3733799.3762964

**Preprints (not peer-reviewed)**
- "I Know Which LLM Wrote Your Code Last Summer", arXiv:2506.17323 — https://arxiv.org/abs/2506.17323 *(arXiv listing does not record the AISec publication above; treat the ACM entry as the refereed version)*
- Zhang et al., DBRD preprint, arXiv:2212.00548 — https://arxiv.org/abs/2212.00548 *(superseded by the TOSEM version)*
- "Numbers Matter! Bringing Quantity-awareness to Retrieval Systems", arXiv:2407.10283 — https://arxiv.org/abs/2407.10283

**Tooling and curated references (not peer-reviewed)**
- Splink comparison level library, UK Ministry of Justice — https://moj-analytical-services.github.io/splink/api_docs/comparison_level_library.html
- Catalogue of Bias (Oxford CEBM), spectrum bias — https://catalogofbias.org/biases/spectrum-bias/

**Verification note.** [VERIFY:current] Splink's API surface and the publication status of arXiv:2407.10283 are both version- and time-dependent; check before citing either in a paper.