# External research: how the similarity function compares to published work

2026-08-16. Three independent research strands, run under `re`. Full unedited text below;
nothing is summarised away. Sources cited inline as URLs, with peer-reviewed work
distinguished from preprints throughout.


---

## Strand: Duplicate bug report detection as a benchmark

# Duplicate bug report detection as a benchmark for the CDSFL similarity function

Timestamp of research: 2026-08-16T01:48 BST → 02:05 BST.

---

## 1. How the task is defined and evaluated, and what strong systems actually achieve

### Task formulation

The literature uses two distinct formulations, and they are **not** interchangeable. This distinction is the single most important thing for interpreting the CDSFL numbers.

**(a) Retrieval / ranking.** Given a newly filed report, rank the entire existing corpus and return the top *k* candidates. Metrics: **Recall Rate@k (RR@k)**, sometimes called recall-rate@k, and **Mean Average Precision (MAP)**. This is the dominant formulation and the one that reflects deployment.

**(b) Pairwise classification.** Given two reports, output duplicate / not-duplicate. Metrics: accuracy, precision, recall, F1, AUC. This is the minority formulation and is widely regarded as inflated, because the negative pairs are usually randomly sampled and the sets artificially balanced.

**CDSFL Tier 2 as described is formulation (b), on a pre-filtered candidate set.** That matters enormously and I return to it in §3.

### Real numbers, peer-reviewed

| System | Venue (status) | Dataset | Result |
|---|---|---|---|
| Runeson et al., NLP prototype | ICSE 2007 (**peer-reviewed**) | Sony Ericsson defect reports | ~**40%** of marked duplicates found; authors argue this is ~2/3 of the findable subclass |
| Sun et al., **REP** (BM25F extension + non-textual fields) | ASE 2011 (**peer-reviewed**) | 209,058 Eclipse reports | **RR@k 37–71%**, **MAP 0.47**; 10–27% relative RR@k gain and 17–23% relative MAP gain over their own prior model, validated on Mozilla + Eclipse + OpenOffice |
| Lazar, Ritchey, Sharif corpora | MSR 2014 (**peer-reviewed**) | Eclipse, OpenOffice, NetBeans, Mozilla Bugzilla, 1998–Jan 2014 | Not a method; the standard corpus. Duplicate rate **12.67%–23%** of all reports |
| Zhang et al., *Duplicate Bug Report Detection: How Far Are We?* | **ACM TOSEM 2023** (**peer-reviewed**) | New benchmark: Eclipse 27,583 / Mozilla 193,587 / Hadoop 14,016 / Spark 9,579 / Kibana 17,016 / VSCode 62,092 reports, duplicate rates 2.7%–10.4% | REP (2011) beats all deep-learning successors on 5 of 6 projects, by **22.3% on average in RR@10** over SABD |
| He et al., **DC-CNN** | ICPC 2020 (**peer-reviewed**) | OpenOffice / Eclipse / NetBeans / combined | Pairwise accuracy **0.9429 / 0.9685 / 0.9534 / 0.9552** — but on balanced sampled pairs |
| Ahasanuzzaman et al., **Dupe** (BM25 + logistic regression) | MSR 2016 (**peer-reviewed**) | Stack Overflow | **recall@20 = 66.11%** (Ruby), **53.02%** (Java); a later reproducibility study found absolute recall-rate drops of up to **28.5%** on re-implementation |

Absolute numbers on the current realistic benchmark, taken from the Cupid paper's replication of the TOSEM benchmark (arXiv **preprint**, no confirmed venue):

| | Spark RR@1 / @5 / @10 | Hadoop | Kibana |
|---|---|---|---|
| REP | 0.346 / 0.481 / **0.556** | 0.402 / 0.576 / **0.609** | 0.364 / 0.587 / **0.620** |
| SABD | 0.202 / 0.304 / **0.331** | 0.215 / 0.324 / **0.411** | 0.293 / 0.489 / **0.555** |
| Siamese Pair | 0.037 / 0.074 / **0.121** | 0.033 / 0.076 / **0.093** | 0.020 / 0.076 / **0.092** |
| Cupid (ChatGPT keyword extraction + REP) | 0.360 / 0.519 / **0.602** | 0.420 / 0.587 / **0.637** | 0.389 / 0.605 / **0.654** |

**The state of the art, honestly stated: RR@10 of roughly 0.55–0.65, RR@1 of roughly 0.35–0.42, MAP under 0.50.** After nineteen years of work. On the VSCode data the TOSEM paper's Figure 7 tops out below RR@5 = 0.5 for every tool including Microsoft's production VSCodeBot.

Sources: [Sun et al. ASE 2011](https://swag.uwaterloo.ca/publications/towards-more-accurate-retrieval-of-duplicate-bug-reports.html) · [Zhang et al. TOSEM 2023](https://dl.acm.org/doi/full/10.1145/3576042), preprint at [arXiv:2212.00548](https://arxiv.org/abs/2212.00548), replication package [github.com/soarsmu/TOSEM-DBRD](https://github.com/soarsmu/TOSEM-DBRD) · [Lazar et al. MSR 2014](https://dl.acm.org/doi/10.1145/2597073.2597128) · [He et al. ICPC 2020](https://dl.acm.org/doi/10.1145/3387904.3389263) · [Cupid, arXiv:2308.10022](https://arxiv.org/html/2308.10022v3) · [Ahasanuzzaman et al. MSR 2016](https://clones.usask.ca/pubfiles/articles/AhasanuzzamanDuplicateMSR2016.pdf) · [Runeson et al. ICSE 2007](https://www.semanticscholar.org/paper/Detection-of-Duplicate-Defect-Reports-Using-Natural-Runeson-Alexandersson/0d459e3be20f7f529bc0d92d42fa63e60fc1e1ba)

---

## 2. Lexical vs embedding/transformer: is the gap large?

**No. The gap is small, frequently zero, and frequently negative.** This is one of the better-established negative results in software engineering research.

**The headline peer-reviewed finding.** Zhang et al. (TOSEM 2023) built a bias-controlled benchmark specifically to answer this and found REP — a 2011 BM25F variant with gradient-descent-tuned field weights — outperformed SABD, Siamese Pair, DC-CNN and HINDBR on 5 of 6 projects, by **22.3% average RR@10** over the best deep model. Their own summary: *"a simpler technique outperforms recently proposed sophisticated techniques on most projects."* They further found that **FTS** — plain Elasticsearch full-text search on report titles, i.e. exact word matching, the thing Mozilla actually runs — beat HINDBR and DC-CNN on **all six** projects and beat Siamese Pair on **four of six**. Their stated implication: *"Since FTS is based on exact word matching, the relatively good performance of FTS indicates that many duplicate BRs are more likely to carry the same words in BR titles."*

**Where lexical loses.** Jahan & Rahman (arXiv:2212.09976, **preprint**) split 92,854 Eclipse/Firefox/Mobile reports into textually similar and textually dissimilar duplicate pairs by n-gram quartile. BM25 recall-rate: Eclipse 22.64 / 36.60 / 42.03 / 57.31 at k = 1/5/10/100; Firefox 16.11 / 27.98 / 33.64 / 52.68; Mobile 17.25 / 28.95 / 35.38 / 57.60. The gap between similar and dissimilar duplicates at k=100 is **10.20%–18.45%** for BM25 but only **2.00%–6.49%** for LDA+GloVe. So embeddings do help — but specifically and only on the **19%–23%** of duplicate pairs that are textually dissimilar, and LDA+GloVe's absolute recall-rate@100 was ~38% *lower* than BM25's overall.

**Where embeddings clearly win.** A **preprint** comparing five encoders on Firefox/Eclipse/MozillaCore/JDT/Thunderbird ranks BERT > ADA > Gensim > TF-IDF > FastText, with BERT at 26–36% recall@5 vs TF-IDF at 13–24% ([arXiv:2308.09193](https://arxiv.org/html/2308.09193)). Note the same paper runs no BM25 or Jaccard baseline, which the authors acknowledge.

**Outside software engineering, same story.** BEIR (Thakur et al., **NeurIPS 2021 Datasets & Benchmarks, peer-reviewed**) evaluated 10 retrieval systems across 18 datasets and found BM25 a robust zero-shot baseline that most dense retrievers fail to beat out of domain without adaptation. [openreview.net/forum?id=wCu6T5xFjeJ](https://openreview.net/forum?id=wCu6T5xFjeJ)

**Verdict on Q2: a token-based method being competitive with, or better than, a transformer on this task is completely unremarkable in this literature. It is close to the expected outcome.** The CDSFL choice to skip the model call is well-supported by evidence and is not a bold call.

---

## 3. Is the CDSFL setting easier or harder than bug reports? — **Much easier, on four axes; harder on one**

This is where comparability breaks, and it breaks decisively.

### Easier: vocabulary is not independently generated

The entire difficulty of duplicate bug report detection stems from a single fact quantified in Jahan & Rahman, citing the vocabulary-problem literature: *"the probability of two persons using the same text to explain the same issue is very low (e.g., 10%–15%)."* Two humans, two mental models, two vocabularies, two bug trackers, sometimes two languages.

CDSFL findings are produced by frontier models, under a **common directive**, against the **same document**, and the hard tokens are **lifted verbatim from that shared source**. A quantity like `1.6 × 10⁻¹⁹ C` or a claim identifier like `Eq. 4.7` appears identically in both findings not because two agents independently converged on wording but because both copied the same string out of the same artefact. That is not the duplicate-bug-report problem. That is **near-duplicate detection over a shared substrate**, which is a different and much easier task with its own literature (Broder shingling, MinHash, SimHash; see Manning, Raghavan & Schütze, *Introduction to Information Retrieval*, ch. 19, [nlp.stanford.edu/IR-book/html/htmledition/near-duplicates-and-shingling-1.html](https://nlp.stanford.edu/IR-book/html/htmledition/near-duplicates-and-shingling-1.html)).

**How much does this matter? A lot, and there is a direct measurement.** The stack-trace deduplication literature runs the *same algorithms* over inputs of *differing structural density*:

| Method | Ubuntu | Eclipse | NetBeans | Gnome | **SlowOps** (structured, machine-generated) |
|---|---|---|---|---|---|
| Lerch (TF-IDF) | 0.40 | 0.60 | 0.22 | 0.37 | **0.96** |
| FaST (lexical heuristic) | 0.41 | 0.72 | 0.30 | 0.32 | **0.97** |
| S3M (deep, BiLSTM) | 0.32 | 0.52 | 0.25 | 0.25 | **0.95** |
| text-embedding-3-small | 0.62 | 0.73 | 0.46 | 0.40 | **0.93** |

Acc@1, from [arXiv:2412.14802](https://arxiv.org/html/2412.14802v1) (**preprint**, JetBrains Research). Identical code, 0.30 → 0.96 purely from input structure. And note that on the dense structured input the LLM embedding is the *worst* performer.

**This is the strongest external support your founder's claim has.** The published record shows that identifier-dense, machine-generated text makes duplicate identity decidable lexically at near-ceiling accuracy, and that the neural methods stop paying for themselves exactly there. It also shows the credit belongs to the **input**, not to the tier design.

### Easier: candidate-set size differs by three to four orders of magnitude

RR@10 on Mozilla means finding the one true master among **55,701 test reports**. CDSFL Tier 2 operates on **438 same-location pairs** after Tier 1 blocking. The blocking step is doing enormous work, and correctly so — location blocking is textbook candidate generation from the record-linkage tradition — but it means **no RR@k number from the bug literature is comparable to any CDSFL number.** Do not put them in the same table.

### Easier: the ambiguous band was discarded

28 + 290 = **318 labelled pairs out of 438 reported same-location pairs**. **120 pairs, 27.4% of the total, fall in the 0.70–0.90 embedding band and are excluded from the evaluation.** By construction those are the hard cases. Removing the ambiguous middle before measuring separation is a known separability inflator. A bug-report paper that reported near-total separation after silently dropping 27% of pairs on a similarity-score band would be asked to redo the evaluation. If those 120 pairs were included with any reasonable adjudication, the reported medians would move.

### Easier, and this is the serious one: the ground truth is not ground truth

In every peer-reviewed DBRD study above, the label is a **human triager's `duplicate of` link**. Noisy, but independent and semantically grounded. Campbell et al. explicitly flag their own gold set (Ubuntu volunteers' manual classification) as the main threat to validity.

CDSFL's labels come from a **sentence-embedding backend thresholded at ≥0.90 and ≤0.70**. Two consequences:

1. What is being measured is **agreement between Jaccard-over-hard-tokens and an embedding model's cosine score.** It is not agreement with a fact about defect identity. The claim "Tier 2 decides identity without understanding" is not established by the experiment; what is established is "Tier 2 tracks an embedding model on the subset where the embedding model is confident."
2. The tier being defended and the tier being trusted as truth are both automated similarity functions over the same text. The argument that the embedding backend "is part of neither tier" addresses circularity of *implementation*, not circularity of *evidence*. Agreement between two similarity functions on easy cases is weak evidence that either is right about identity.

**The fix is cheap and I would do it before publishing any of these numbers: hand-label a stratified random sample of 60–80 pairs — including the excluded 0.70–0.90 band — and re-run the whole thing against human labels.** That converts the result from "two automated measures agree" to "the measure is correct."

### Harder: same-location negatives are a genuinely adversarial pool

Credit where it is due. Because Tier 1 has already partitioned by symbol/heading, the 290 different-defect pairs are pairs of findings **about the same symbol** — a much more confusable negative pool than the random-negative sampling used to build the balanced pairwise datasets that DC-CNN and its relatives were trained on (the practice the MDPI 2026 survey and others flag as inflating those 0.94–0.97 accuracy figures). A median Jaccard of exactly 0.000 for different-defect pairs *at the same location* says hard tokens are finer-grained than location. That is a real finding and it is the most interesting empirical claim in your description.

**But it has a competing explanation you have not ruled out.** If hard-token sets are small — say a median of 2–4 tokens per finding — then Jaccard of two sparse sets is 0 unless they share a literal token, and the resulting distribution is bimodal *by construction*, not by discrimination. Coverage is reported as "97.6% carry **at least one** hard token", which is consistent with sets being very small. **Falsification test: report the hard-token set-size distribution, then re-run the same/different comparison conditioned on both findings having ≥4 hard tokens.** If the separation survives, the finding is real. If it collapses, the medians were a sparsity artefact.

---

## 4. Is near-total lexical separation plausible, or surprising?

**Plausible, with direct precedent — and for that reason, not surprising.** The precedent is SlowOps at 0.96–0.97 Acc@1 for lexical methods (§3), and the entire near-duplicate detection tradition where Jaccard over shingles is the standard tool precisely because literal token overlap is decisive when documents share source text.

What *would* be surprising is near-total separation on **human-written, independently-authored** reports. Nobody has that. BM25 RR@1 is 16–23%. The best system on the current benchmark reaches RR@10 = 0.654.

### What your numbers actually say, translated into the literature's metric

I back-calculated using scipy (`scipy.stats.mannwhitneyu`, `binomtest` Wilson intervals, `fisher_exact`), cross-checked against the closed-form tie-corrected normal approximation. Two independent routes, agreeing.

**Tier 2.** The Mann-Whitney U statistic *is* the AUC: AUC = U / (n₁n₂). With n₁=28, n₂=290:

- With **no ties**, perfect separation gives the smallest attainable two-sided p of about **2.4 × 10⁻¹⁸**. Your reported **p = 1.9 × 10⁻²⁵ is below that floor**, so it is only reachable via the tie correction shrinking the variance — which requires roughly **≥73% of different-defect pairs sitting at exactly Jaccard 0**. That is internally consistent with the reported median of 0.000, so the number is not wrong. But it means **the p-value is measuring your tie mass, not your discrimination.** Simulated distributions matching your summary reproduce p from 2.8 × 10⁻¹⁸ (AUC 0.917) to 5.6 × 10⁻²⁹ (AUC 1.000).
- **Implied AUC ≈ 0.95–1.00.** State that. Drop the p-value from any external-facing document; at z = 10.4 the normal approximation is far outside its validated regime and a reviewer will say so.

**The medians do not identify an operating point, and this is the biggest gap.** Median 0.000 for the different-defect group means *at least* 145 of 290 sit at exactly zero — it says nothing about the other 145. If all 145 have Jaccard > 0, then thresholding at "any hard-token overlap" gives precision of **28/173 = 0.162**. Your two medians plus a p-value are compatible with precision anywhere in **[0.16, 1.00]**. **You need the ROC and precision-recall curves over the threshold sweep. Two medians and a p-value are not an evaluation.**

**Tier 3, and this one is a finding you should see.** I reproduced your reported Fisher p exactly: **p = 1.425 × 10⁻⁷** comes from the 2×2 table [[19, 0], [14, 30]] — UNKNOWN dropped. That is a legitimate and *conservative* test (including UNKNOWN as non-SAME gives p = 2.2 × 10⁻¹⁵), so no complaint there. But look at Tier 3 as the merge decision it actually is:

- Tier 3 returns SAME on 19 same-defect and **14 different-defect** pairs → **precision 19/33 = 0.576, 95% Wilson CI [0.408, 0.728]**. Recall 0.679. **F1 = 0.623.**
- **Roughly 42% of Tier 3's merge decisions are wrong.** Given that a false merge is exactly the failure mode that ends a review run early, this is the highest-consequence number in the whole description and it is not in your summary.
- "Never called a same-defect pair DIFFERENT" is 0/28. By the rule of three, the 95% upper bound on the false-split rate is **10.7%**, not zero. Say "below about 11%", not "never".
- 19/28 = 0.679 has a 95% CI of **[0.493, 0.821]**. Every Tier 3 proportion is this wide. **n = 28 is the binding constraint on the entire study.**

For calibration: precision 0.58 / recall 0.68 is respectable for a pairwise DBRD system, and roughly where strong published systems sit. It is not "near-total separation." **The near-total separation belongs to Tier 2 only, and only under the caveats in §3.**

---

## 5. Where no comparable benchmark exists — stated plainly

**There is no published benchmark for deduplicating LLM-generated review findings against a common document.** I searched the 2025–2026 LLM code-review benchmark literature — Sphinx, CR-Bench, AACR-bench, and a 2026 survey covering 99 code-review benchmark papers from 2015–2025. All of them evaluate *review quality*: does the model find the defect, is the comment useful, does it over-correct. **None of them evaluates finding-level deduplication, and none reports a same-defect/different-defect separation statistic.** I could not find a single directly comparable number, and I am not going to manufacture one by analogy.

This cuts both ways. You have no baseline to beat, so no external claim of superiority is available to you. But you also have a genuinely unmeasured quantity, and the archive itself — 6 runs, 165 critical findings, 438 same-location pairs with pair-level labels — is the closest thing to a dataset for it that I found evidence of anywhere. **The archive is more publishable than the tier.**

---

## 6. Rating — accurate, not generous

**The similarity function as a methodological contribution: 2/10. Ordinary.**

Jaccard over an extracted token class is Broder 1997. Location blocking is textbook candidate generation from record linkage. A cheap-filter → lexical → semantic-adjudication cascade is the standard IR cascade. Choosing lexical over embedding is well-supported by evidence (§2) but is the *conventional* choice in this literature, not a contrarian one — REP has been beating deep learning on this task in a top-tier ACM journal since 2023. Nothing in Tiers 1–3 as described would be novel to a reviewer at MSR, ICSME or TOSEM.

**The evaluation as evidence for the founder's density claim: 4/10. Directionally right, currently unable to carry the claim.**

The direction matches the strongest available external analogue (SlowOps, §3) and I think the claim is probably *true*. But the evidence as described has four defects that a reviewer would raise, in descending order of severity: machine-generated ground truth rather than human labels; a 27.4% ambiguous band discarded before measurement; medians and a p-value in place of an ROC/PR curve, leaving the operating point unidentified between precision 0.16 and 1.00; and n = 28 positives, which makes every proportion carry a ±17-point confidence interval. There is also no baseline — no BM25 over full finding text, no TF-IDF cosine, no "use the embedding backend directly." Without those, "Tier 2 works" is not falsifiable against the null hypothesis "in this domain *any* lexical measure works."

**The engineering fit to the CDSFL stop criterion: 7/10. Good.**

Tier 3's merge-only asymmetry is the correct design given that false merges end runs early and false splits merely cost a round. Tier 1 blocking before Tier 2 is right. Skipping the model call is defensible on both evidence and cost. The 57.6% merge precision is the thing to fix, not the architecture.

**The killed tier: this is the best thing here.**

Building a component to a model panel's design, measuring it against the archive, getting Fisher p = 0.71, and *removing it* is a working falsification loop. The published DBRD literature has a documented reproducibility problem in exactly this area — the Stack Overflow reproducibility study found absolute recall-rate drops of up to 28.5% on re-implementation of published methods. Against that background, a retained negative result is worth more than the tier that survived.

**Overall: competent internal engineering with no publishable novelty in the similarity function, resting on an evaluation that is currently too small and too circular to support the claim being made of it. The claim is probably true. It is not yet shown.**

### Three things that would change the rating, in priority order

1. **Human-label 60–80 stratified pairs including the 0.70–0.90 band, and re-run against those.** This removes the circularity and is the single highest-value action.
2. **Publish the ROC/PR sweep for Tier 2 and the hard-token set-size distribution**, plus the conditional analysis at set size ≥4. This distinguishes discrimination from sparsity.
3. **Add BM25 and TF-IDF-cosine over full finding text as baselines.** If Tier 2 does not beat them, the honest finding is "this domain is lexically easy" — which is still a real finding, and is exactly what the SlowOps result predicts.

---

## Sources

**Peer-reviewed**
- Zhang, Han, Vinayakarao, Irsan, Xu, Thung, Lo, Jiang — *Duplicate Bug Report Detection: How Far Are We?*, ACM TOSEM 2023 — https://dl.acm.org/doi/full/10.1145/3576042 (preprint https://arxiv.org/abs/2212.00548, package https://github.com/soarsmu/TOSEM-DBRD)
- Sun, Lo, Khoo, Jiang — *Towards More Accurate Retrieval of Duplicate Bug Reports*, ASE 2011 — https://swag.uwaterloo.ca/publications/towards-more-accurate-retrieval-of-duplicate-bug-reports.html · https://dl.acm.org/doi/abs/10.1109/ASE.2011.6100061
- Runeson, Alexandersson, Nyholm — *Detection of Duplicate Defect Reports Using Natural Language Processing*, ICSE 2007 — https://www.semanticscholar.org/paper/0d459e3be20f7f529bc0d92d42fa63e60fc1e1ba
- Wang, Zhang, Xie, Anvik, Sun — *An Approach to Detecting Duplicate Bug Reports Using Natural Language and Execution Information*, ICSE 2008 — https://dl.acm.org/doi/10.1145/1368088.1368151
- Lazar, Ritchey, Sharif — *Generating Duplicate Bug Datasets*, MSR 2014 — https://dl.acm.org/doi/10.1145/2597073.2597128
- He, Xu, Yan, Xia, Lei — *Duplicate Bug Report Detection Using Dual-Channel CNNs*, ICPC 2020 — https://dl.acm.org/doi/10.1145/3387904.3389263
- Campbell, Santos, Hindle — *The Unreasonable Effectiveness of Traditional Information Retrieval in Crash Report Deduplication*, MSR 2016 — https://softwareprocess.es/pubs/campbell2016MSR-partycrasher.pdf
- Dang, Wu, Zhang, Zhang, Nobel — *ReBucket: Clustering Duplicate Crash Reports Based on Call Stack Similarity*, ICSE 2012 — https://www.microsoft.com/en-us/research/wp-content/uploads/2016/07/rebucket-icse2012.pdf
- Lerch, Mezini — *Finding Duplicates of Your Yet Unwritten Bug Report*, CSMR 2013 — https://dl.acm.org/doi/10.1109/CSMR.2013.17
- Ahasanuzzaman, Asaduzzaman, Roy, Schneider — *Mining Duplicate Questions in Stack Overflow*, MSR 2016 — https://clones.usask.ca/pubfiles/articles/AhasanuzzamanDuplicateMSR2016.pdf
- Thakur, Reimers, Rücklé, Srivastava, Gurevych — *BEIR*, NeurIPS 2021 Datasets & Benchmarks — https://openreview.net/forum?id=wCu6T5xFjeJ
- Manning, Raghavan, Schütze — *Introduction to Information Retrieval*, ch. 19, near-duplicates and shingling — https://nlp.stanford.edu/IR-book/html/htmledition/near-duplicates-and-shingling-1.html

**Preprints, not peer-reviewed**
- Zhang, Irsan, Thung, Lo — *Cupid: Leveraging ChatGPT for More Accurate Duplicate Bug Report Detection* — https://arxiv.org/html/2308.10022v3
- Jahan, Rahman — *Towards Understanding the Impacts of Textual Dissimilarity on Duplicate Bug Report Detection*, arXiv:2212.09976 — https://arxiv.org/pdf/2212.09976
- *Stack Trace Deduplication: Faster, More Accurately, and in More Realistic Scenarios*, arXiv:2412.14802 — https://arxiv.org/html/2412.14802v1
- *Comparative Analysis of Text Embedding Models for Bug Report Semantic Similarity*, arXiv:2308.09193 — https://arxiv.org/html/2308.09193
- *GitBugs: Bug Reports for Duplicate Detection, RAG, and More*, arXiv:2504.09651 — https://arxiv.org/html/2504.09651v2
- *Automated Duplicate Bug Report Detection in Large Open Bug Repositories*, arXiv:2504.14797 — https://arxiv.org/html/2504.14797
- *A Survey of Code Review Benchmarks and Evaluation Practices in Pre-LLM and LLM Era*, arXiv:2602.13377 — https://arxiv.org/html/2602.13377

**Verification scripts** (SciPy 2-route cross-check of every number I computed, per multi-tool cross-verification): `/private/tmp/claude-501/-Users-georgejackson-Developer-Projects/6142171c-97c7-4e77-9a9a-8d36d795bb89/scratchpad/auc_backout.py`, `/private/tmp/claude-501/-Users-georgejackson-Developer-Projects/6142171c-97c7-4e77-9a9a-8d36d795bb89/scratchpad/mw_check.py`, `/private/tmp/claude-501/-Users-georgejackson-Developer-Projects/6142171c-97c7-4e77-9a9a-8d36d795bb89/scratchpad/cis.py`

[VERIFY:current] Venue status for Cupid (arXiv:2308.10022) and Jahan & Rahman (arXiv:2212.09976) could not be confirmed from the copies retrieved; both are treated as preprints above. Suggested search: `Cupid duplicate bug report Zhang Lo journal published venue 2024`.

---

## Strand: What good looks like for same-different decisions

# Same/Different Decisions: What "Good" Looks Like, and Where CDSFL's Similarity Function Actually Sits

## 0. Headline rating

| Axis | Rating | One-line justification |
|---|---|---|
| Engineering design | **7/10** | Three-tier cascade with a merge-only asymmetry is a sound, appropriate design. Removing the rival tier on a null result is exactly right. |
| Measurement rigour | **3/10** | Headline statistics answer a narrower question than claimed; no AUC, no CI, no operating threshold, no held-out split, ground truth is filtered in a way that removes the hard cases, and the 318 "observations" are not independent. |
| Novelty of the mechanism | **2/10** | Hard-token / numeric-identifier overlap as a matching signal is standard practice in entity resolution, citation matching and biomedical record linkage. This is a competent re-application, not a new idea. |
| Honesty of reporting | **8/10** | The p=0.71 negative result on the panel-designed rival tier is reported and acted on. That is rarer than it should be. |

**Overall: competent internal engineering with a below-publication evaluation.** The function is probably good enough for its job. The *evidence* presented does not establish that, and one design choice in the ground truth makes the numbers look better than they are.

---

## 1. What separations and effect sizes count as strong in this literature

### 1a. Semantic textual similarity (graded)

The benchmark region for STS-B (Spearman ρ ×100), all peer-reviewed:

| System | STS-B | SICK-R | Avg 7 STS |
|---|---|---|---|
| GloVe embeddings (avg) | 58.02 | 53.76 | 61.32 |
| Unsupervised SimCSE-BERT_base | 76.85 | 72.23 | 76.25 |
| Supervised SimCSE-RoBERTa_large | 86.70 | 81.95 | 83.76 |
| DeBERTa (GLUE test) | 92.75 | — | — |
| **Human baseline (GLUE)** | **92.65** | — | — |

Sources: [SimCSE, EMNLP 2021](https://aclanthology.org/2021.emnlp-main.552/) ([full tables](https://ar5iv.labs.arxiv.org/html/2104.08821)); [Microsoft DeBERTa blog / GLUE leaderboard](https://www.microsoft.com/en-us/research/blog/microsoft-deberta-surpasses-human-performance-on-the-superglue-benchmark/).

Read that table as the calibration scale. A *lexical-only, no-training* signal that lands anywhere near 0.86 Spearman on genuinely hard pairs would be a publishable surprise. Nothing in the CDSFL numbers is on this scale, because CDSFL isn't scoring a graded correlation — but the table tells you what the ceiling looks like when a system genuinely understands the pairs.

### 1b. Binary same/different — and the crucial adversarial case

This is the one that matters most for your claim. PAWS (Zhang, Baldridge & He, NAACL 2019, peer-reviewed) was built *precisely* to break lexical-overlap matchers. Its negative pairs are constructed to have bag-of-words cosine α = 1.0 (word-swapping) or ≥ 0.9 (back-translation) — i.e. **the negatives share the same word set as the positives.**

Exact numbers from [PAWS Table 7](https://aclanthology.org/N19-1131.pdf), accuracy % / PR-AUC %:

| Model | QQP→QQP | QQP→PAWS_QQP | QQP+PAWS→PAWS_QQP |
|---|---|---|---|
| BOW | 83.2 / 89.5 | **29.0 / 27.1** | 30.0 / 27.3 |
| DecAtt | 87.8 / 93.9 | 33.3 / 26.3 | 67.4 / 51.1 |
| DIIN | 89.2 / 95.2 | 32.8 / 32.4 | 83.8 / 77.8 |
| BERT | 90.5 / 96.3 | 33.5 / 35.1 | 85.0 / 83.1 |

And on PAWS_Wiki (Table 8), supervised: BOW acc 55.8 / AUC 41.1; BERT acc 90.4 / AUC 93.7.

**The single most important number in this whole report is BOW's 27.1 AUC.** The same class of mechanism CDSFL Tier 2 uses — token-set overlap, no model, no embedding — scores 89.5 AUC when the negatives are ordinary and 27.1 AUC (worse than chance) when the negatives are lexically matched. The mechanism carries almost none of the signal; the *negative distribution* carries it.

### 1c. Near-duplicate detection (the closest algorithmic cousin)

- [Manku, Jain & Das Sarma, WWW 2007](https://research.google.com/pubs/archive/33026.pdf) — SimHash at web scale, 8B pages.
- Large-scale comparison of Broder's shingling vs Charikar's simhash: neither works for same-site near-duplicates; on cross-site pairs, **Charikar precision 0.50, Broder 0.38**. ([Henzinger, SIGIR 2006](https://www.researchgate.net/publication/221299744_Finding_near-duplicate_web_pages_A_large-scale_evaluation_of_algorithms))
- [NAACL 2025 industry track, NDD-MAC](https://aclanthology.org/2025.naacl-industry.73.pdf): on the paraphrase-heavy NDD-NS corpus, MinHash-LSH and SimHash reach **micro-F1 ≈ 30–35**; on a high-surface-overlap vendor news corpus, SimHash ≈ 77, MinHash ≈ 63; their embedding+community method reaches **≈ 87** micro-F1 at threshold 0.6.

So: purely lexical near-duplicate methods live in the F1 = 0.30–0.77 band depending entirely on how surface-similar the corpus is. That is the honest peer group for Tier 2, and CDSFL's Tier 3 F1 of 0.62 (computed below) sits squarely inside it.

### 1d. Duplicate defect reports (the closest *task*)

- [Cupid (ChatGPT-assisted), 2023 preprint](https://arxiv.org/html/2308.10022v3): Recall Rate@10 ≈ 0.654, ~8% over prior SOTA.
- Historic Eclipse/Firefox/OpenOffice benchmarks: recall < 80%.
- [Efficient feature extraction, Inf. Softw. Technol. 2020](https://www.sciencedirect.com/science/article/abs/pii/S0950584920301117) reports 91–99% but on a classification framing that is not comparable to retrieval.

Note the peer-reviewed SOTA is *ranking* recall around 0.65, not 0.95. Duplicate-defect identity is a genuinely hard task and nobody has solved it.

---

## 2. What the CDSFL statistics do and do not establish

### 2a. The Mann-Whitney p = 1.9e-25

**It establishes:** the two Jaccard distributions are not the same distribution. Nothing more.

**It does not establish:** accuracy, calibration, an operating threshold, or that the function would work on a new run.

Three specific problems, verified computationally:

**(i) The p-value is arithmetically impossible without ties, which tells you the ties are doing the work.**
With n₁=28, n₂=290, the two-sided p of 1.9e-25 requires |z| = 10.43. The untied Mann-Whitney normal approximation has σ = 464.6 and a *maximum attainable* |z| of 8.74 — even for perfect separation. The reported p can only arise from a tie-corrected (or exact/permutation) computation. Reconstructing under tie correction:

| assumed # exact-zero Jaccard values | implied AUC |
|---|---|
| 240 | 0.950 |
| 260 | 0.902 |
| 270 | 0.872 |
| 280 | 0.836 |

So **the true AUC is plausibly 0.84–0.95** — respectable, comparable to a mid-tier lexical near-dup system, and *nowhere near* what "p = 1.9e-25" rhetorically suggests. The astronomical p comes from the ties collapsing the null variance, not from an astronomical effect. This is exactly what [the ASA's statement on p-values](https://www.tandfonline.com/doi/full/10.1080/00031305.2016.1154108) warns about: "Smaller p-values do not necessarily imply the presence of larger or more important effects."

**(ii) The 318 pairs are not 318 independent observations.** 438 pairs are drawn from 165 findings across 6 runs — each finding appears in ~5.3 pairs on average, and all pairs within a run share a target document. Mann-Whitney assumes independence. The effective number of independent clusters is closer to **6** than to 318. Every reported p-value is therefore anticonservative by an unknown but probably large factor. A run-level (cluster) bootstrap is the minimum correct treatment.

**(iii) Effect size is not reported.** The corresponding Cliff's delta (= 2·AUC − 1) would be ≈ 0.67–0.90. Under the standard [Romano/Hess–Kromrey thresholds](https://cran.r-project.org/web/packages/effsize/effsize.pdf) (|δ| < 0.147 negligible, 0.147–0.33 small, 0.33–0.474 medium, > 0.474 large) that is unambiguously **large** — a real and reportable result. It just happens to be a much less impressive-sounding number than 1.9e-25, and it is the honest one.

### 2b. The Fisher p = 1.4e-07 is on a subset, and this is not disclosed

I reconstructed which 2×2 produces exactly that value:

| Table tested | OR | Fisher p |
|---|---|---|
| **SAME vs DIFFERENT only (UNKNOWN dropped)** | **∞** | **1.425e-07** ✅ matches |
| SAME vs not-SAME (all 318) | 41.6 | 2.24e-15 |
| DIFFERENT vs not-DIFFERENT (all 318) | 0.00 | **0.090 — not significant** |
| resolved vs UNKNOWN | 11.8 | 6.43e-09 |

Two consequences.

First, the reported headline conditions on Tier 3 having produced a verdict — it uses **63 of 318 pairs (19.8%)**. It answers "when Tier 3 speaks, is it right?", not "is Tier 3 useful?". The *unconditional* test is stronger (p = 2.2e-15), so the reported figure is conservative — but it is the wrong statistic for the claim being made, and the subsetting must be stated.

Second, and more seriously: **"it NEVER called a same-defect pair DIFFERENT" is not supported by the data at the confidence it implies.** The DIFFERENT-vs-not-DIFFERENT test is p = 0.090 — not significant. And 0/28 gives a 95% Clopper-Pearson interval of **[0, 0.123]**; the rule of three gives 3/28 = 10.7%. The true false-split rate could be as high as **1 in 8**. For a mechanism whose whole safety argument is "can only merge, never split," that upper bound is the number that matters and it is not small.

### 2c. Tier 3 as a merge classifier — the numbers that should be published

From the confusion matrix (TP=19, FP=14, FN=9, TN=276):

| Metric | Value | 95% CI |
|---|---|---|
| Precision (PPV) | 0.576 | 0.408–0.728 (Wilson) / 0.392–0.745 (exact) |
| Recall (sensitivity) | 0.679 | 0.493–0.821 / 0.476–0.841 |
| F1 | 0.623 | — |
| **MCC** | **0.586** | — |
| FPR | 0.048 | 0.029–0.079 |
| Balanced accuracy | 0.815 | — |
| Prevalence | 0.088 | — |
| Lift over base rate | 6.5× | — |

This is a genuinely useful classifier — MCC 0.59 at 8.8% prevalence is real signal, and 6.5× lift is not nothing. It is also **not** an exceptional one: it sits inside the same band as the lexical near-dup baselines above. And note the precision CI spans 0.41–0.73, because 28 positives is well below the [commonly cited minimum of 50–100 events per class](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8352630/) for stable performance estimation.

### 2d. The problem I would raise first at review: the ground truth throws away the hard cases

438 same-location pairs; 318 labelled (28 + 290). **120 pairs — 27.4% — fall in the 0.70–0.90 embedding dead-band and were discarded.**

Those 120 are, by construction, the *most confusable pairs in the archive*. They are exactly the cases where a similarity function earns or loses its keep. Removing them and then measuring separation on the remaining 73% is a selection procedure that inflates every metric reported. It is not fraud — the dead-band is a defensible way to get clean labels — but the evaluation must be described as **"performance on pairs an embedding model finds unambiguous,"** which is a materially weaker claim than "performance on the archive."

Secondary point: the labels come from a sentence-embedding backend. It is fair that this backend is in neither tier — that removes the direct circularity. But it means the reported result is *agreement with an embedding model on the cases the embedding model is confident about*, not agreement with ground truth. Human adjudication of a sample (even 60–80 pairs, stratified to over-sample the dead band) would convert this from a proxy study into a real one, cheaply.

---

## 3. Is a negative-class median of 0.000 clean, or trivially separable?

**Mostly trivially separable, and the design amplifies it.** A median of 0.000 over n=290 means at least 146 negative pairs share *not one* hard token. That is not the fingerprint of a discriminative feature; it is the fingerprint of a negative class drawn from "some other finding that happened to land at the same location" rather than "a plausible near-miss."

The literature on this is unambiguous. In dense retrieval, [randomly sampled negatives are known to be "too easy for the model to discriminate"](https://arxiv.org/pdf/2104.08051), and the entire hard-negative-mining subfield exists because random negatives inflate reported metrics. PAWS is the same finding stated as a dataset: build negatives with matched surface form and a BOW matcher collapses from AUC 89.5 to 27.1.

Three things follow.

**(a) The founder's claim is half-right and half-untested.** The half that is right: STEM prose *is* token-dense, hard tokens *do* exist at 97.6% coverage, and set overlap *does* separate the labelled pairs. The half that is untested: nothing here shows that hard tokens decide identity *between confusable findings*. Two findings that both cite "Eq. 14, κ_set = 0.461, 3484 tests" and disagree about whether the value is wrong will have Jaccard ≈ 1.0 and are a *different* defect. Those are precisely the pairs in the discarded 0.70–0.90 band.

**(b) The right name for Tier 1 + Tier 2 is *blocking*, not *matching*.** In [entity resolution](https://arxiv.org/pdf/1905.06167), a cheap high-recall filter that generates candidate pairs is a blocking scheme, evaluated on **Pair Completeness** (recall of true duplicates retained), **Pairs Quality** (precision), and **Reduction Ratio** (comparison savings) — and the standard guidance is that "the blocking phase typically prioritises pair completeness" because discarded pairs cannot be recovered. That framing is a strictly better fit and it makes the merge-only asymmetry principled rather than ad hoc.

**(c) The one genuinely defensible domain claim is narrower than stated.** Not "identity is decidable without understanding." Rather: *in quantity-dense technical prose, hard-token disjointness is a high-specificity signal of non-identity, sufficient to prune the comparison space cheaply.* That is a real, useful, publishable-as-engineering claim. The stronger version is not supported by this evidence.

---

## 4. How to report a same/different classifier so a reviewer can judge it

Compute and publish all of the following. Every one is a few lines of scipy against data you already have.

**Discrimination**
1. **ROC-AUC with 95% CI** — [DeLong 1988](https://www.medcalc.org/en/manual/comparison-of-roc-curves.php) or, preferably here, a **cluster bootstrap resampling whole runs** (B=2000), not pairs. The cluster bootstrap is non-negotiable given the 6-run structure.
2. **PR-AUC / average precision with CI.** At 8.8% prevalence this is the more honest curve — [Saito & Rehmsmeier, PLOS ONE 2015](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0118432) show ROC is visually deceptive under imbalance. Report the no-skill baseline (0.088) alongside it.
3. **Cliff's delta with CI**, and drop the p-value to a parenthetical.

**Operating point** — state the actual threshold, then:
4. Precision, recall, F1, **and MCC**, each with Wilson or Clopper-Pearson intervals. [Chicco & Jurman, BMC Genomics 2020](https://link.springer.com/article/10.1186/s12864-019-6413-7) is the standard citation for MCC over F1/accuracy under imbalance. Your MCC is 0.586 — lead with it.
5. The full 3×3 (SAME/DIFFERENT/UNKNOWN × same/different) table as raw counts, always, so a reader can recompute any statistic including the ones you didn't choose.
6. **Abstention rate**, and precision/recall computed *both* with UNKNOWN as a miss (the honest denominator) and conditioned on a verdict (the diagnostic one). Report both; label which is which.

**As a blocking stage** (Tiers 1–2)
7. **Pair Completeness, Pairs Quality, Reduction Ratio** ([Papadakis et al., ACM CSUR 2020](https://helios2.mi.parisdescartes.fr/~themisp/publications/csur20-blockingfiltering.pdf)).

**Validity**
8. **A held-out split.** Right now the tiers were designed against these 6 runs and evaluated on these 6 runs. Leave-one-run-out cross-validation is the minimum fix and is free.
9. **Adversarial / hard-negative evaluation.** Construct a PAWS-style set: pairs at the same location citing the same quantities but asserting different things. If Tier 2's AUC survives that, you have a real result. If it collapses to ~0.5, you have learned the thing worth knowing.
10. **Human-adjudicated subsample**, stratified to over-weight the 0.70–0.90 dead band.
11. **Report the discarded 120 pairs explicitly**, with the exclusion criterion, in the results — not in a footnote.

**Downstream, and this is the one nobody will ask for but should**
12. The stopping rule is a *discovery-curve* problem, not a similarity problem. The mature literature is capture-recapture defect estimation in software inspection ([Eick et al. 1992](https://ieeexplore.ieee.org/document/852741/); [Wohlin, STVR 1995](https://onlinelibrary.wiley.com/doi/10.1002/stvr.4370050403); [Petersson et al., JSS 2004](https://www.sciencedirect.com/science/article/abs/pii/S0164121203000906)). Report **the sensitivity of run length to the merge threshold** — how many rounds early does the run stop if precision drops 10 points? That converts an abstract similarity metric into the operational quantity you actually care about.
13. If the tiers are ever evaluated as *clustering* rather than pairwise, the standard metric set is MUC / B³ / CEAF and the CoNLL F1 average ([nlpprogress](http://nlpprogress.com/english/coreference_resolution.html)). Pairwise F1 alone is known to mis-rank clustering systems.

---

## 5. Where I could not find a comparable number — stated plainly

**No directly comparable benchmark exists for "did two LLM reviewers raise the same defect against a technical document."**

I looked. The LLM-peer-review benchmark literature is active and growing — [MMReview](https://arxiv.org/abs/2508.14146), [PRISM](https://prism-benchmark.github.io/), FLAWS, DeepReview, Review-5k — and the automated-code-review benchmark literature likewise ([SWR-Bench](https://arxiv.org/pdf/2509.01494); [Atlassian's RovoDev 12-month deployment](https://arxiv.org/html/2601.01129v2), 54,000 comments across 2,000 repos). Redundancy is repeatedly named as a *problem* — "generative models frequently produce redundant or irrelevant comments" — but **none of these benchmarks defines a finding-identity task or publishes a same/different confusion matrix.** There is no leaderboard number to compare 0.586 MCC against.

That is a real gap, and it is the most defensible novelty claim available: **not the mechanism, but the task.** If CDSFL published the 438-pair archive with human-adjudicated labels and a documented protocol, it would be the first dataset of its kind that I can find. That is worth more than the similarity function itself.

Two caveats on that claim: (a) I searched in English, across arXiv, ACL Anthology and general web, in a single session — absence of evidence at this depth is not proof of absence; (b) several of the most relevant benchmark papers are **preprints, not peer-reviewed** (MMReview, PRISM, SWR-Bench, Cupid, RovoDev, NV-Retriever). Peer-reviewed anchors in this report are: SimCSE (EMNLP 2021), PAWS (NAACL 2019), PAWS-X (EMNLP 2019), Manku et al. (WWW 2007), NDD-MAC (NAACL 2025 industry track), Papadakis et al. (ACM CSUR 2020), Saito & Rehmsmeier (PLOS ONE 2015), Chicco & Jurman (BMC Genomics 2020), Wasserstein & Lazar (Am. Stat. 2016), DeLong et al. (Biometrics 1988), and the capture-recapture inspection papers (IEEE TSE / JSS / STVR).

---

## 6. Blunt summary

The similarity function is a reasonable piece of engineering that has been measured with the wrong instruments and then described with the wrong adjectives.

**What is ordinary here:** hard-token overlap as a matching signal (standard entity resolution); a three-tier cascade (standard blocking/matching architecture); an abstaining classifier (standard); AUC in the 0.84–0.95 band for a lexical matcher on easy negatives (standard); MCC 0.59 (respectable, unremarkable).

**What is genuinely good:** the merge-only asymmetry is the correct safety orientation for a stopping rule; 97.6% hard-token coverage is a real empirical finding about the domain; and killing the panel's own perturbation tier on p = 0.71 is intellectually honest in a way most projects are not.

**What must be fixed before this is shown to anyone external:** report AUC and CIs instead of p-values; use a run-level cluster bootstrap; disclose the 27.4% dead-band exclusion in the results; hold out runs; and build one PAWS-style hard-negative set. Until that last one exists, the claim that hard-token density makes identity decidable without understanding is a **hypothesis with supportive but non-diagnostic evidence**, because the one experiment that could falsify it — confusable pairs sharing all their hard tokens — has been systematically excluded from the test set.

**Sources:**
- [SimCSE (EMNLP 2021)](https://aclanthology.org/2021.emnlp-main.552/) · [full tables](https://ar5iv.labs.arxiv.org/html/2104.08821)
- [PAWS (NAACL 2019)](https://aclanthology.org/N19-1131.pdf) · [PAWS-X (EMNLP 2019)](https://aclanthology.org/D19-1382/)
- [DeBERTa / GLUE](https://www.microsoft.com/en-us/research/blog/microsoft-deberta-surpasses-human-performance-on-the-superglue-benchmark/)
- [Manku et al., WWW 2007 (SimHash)](https://research.google.com/pubs/archive/33026.pdf) · [Henzinger, SIGIR 2006](https://www.researchgate.net/publication/221299744_Finding_near-duplicate_web_pages_A_large-scale_evaluation_of_algorithms)
- [NDD-MAC, NAACL 2025 industry](https://aclanthology.org/2025.naacl-industry.73.pdf)
- [Blocking & filtering survey, ACM CSUR 2020](https://helios2.mi.parisdescartes.fr/~themisp/publications/csur20-blockingfiltering.pdf)
- [Saito & Rehmsmeier, PLOS ONE 2015](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0118432) · [Chicco & Jurman, BMC Genomics 2020](https://link.springer.com/article/10.1186/s12864-019-6413-7)
- [ASA statement on p-values](https://www.tandfonline.com/doi/full/10.1080/00031305.2016.1154108) · [DeLong method](https://www.medcalc.org/en/manual/comparison-of-roc-curves.php) · [Cliff's delta thresholds](https://cran.r-project.org/web/packages/effsize/effsize.pdf)
- [Hard negatives in dense retrieval](https://arxiv.org/pdf/2104.08051) *(preprint)*
- [Capture-recapture in inspections](https://www.sciencedirect.com/science/article/abs/pii/S0164121203000906) · [comprehensive evaluation, IEEE TSE](https://ieeexplore.ieee.org/document/852741/) · [Wohlin, STVR 1995](https://onlinelibrary.wiley.com/doi/10.1002/stvr.4370050403)
- [Coreference metrics (MUC/B³/CEAF/CoNLL)](http://nlpprogress.com/english/coreference_resolution.html)
- [Cupid](https://arxiv.org/html/2308.10022v3), [MMReview](https://arxiv.org/abs/2508.14146), [PRISM](https://prism-benchmark.github.io/), [SWR-Bench](https://arxiv.org/pdf/2509.01494), [RovoDev](https://arxiv.org/html/2601.01129v2) *(all preprints)*
- [Sample size for prediction-model validation](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8352630/)

---

## Strand: Novelty, prior art, and what would strengthen it

## Verdict first

The similarity function is a competent recombination of established techniques. Nothing in the three tiers is methodologically new. What has no direct prior art, as far as I can find, is the *application*: a deterministic, non-LLM identity function over machine-generated findings, used to decide when an automated falsification loop has stopped producing new defects. That application gap is real but narrow, and the evidence currently offered for it is weaker than the write-up implies, primarily because the ground truth is generated by a model rather than by humans, and because 27% of the pairs, specifically the hard ones, were excluded before any statistic was computed.

Honest ratings, stated separately because they differ a lot:

| Axis | Rating | Why |
|---|---|---|
| Method novelty | **2/10** | Every component is standard IR from 1997–2023. |
| Application novelty | **5/10** | No direct prior art found for deterministic dedup of LLM findings as a stop criterion. Adjacent literature is dense and moving fast. |
| Evidence strength as reported | **3/10** | Circular labels, excluded middle band, p-values instead of operating points, no baselines, no independence handling. |
| Publishability today | **2/10** | Not yet. With fixes 1–4 below, a credible workshop paper. With fix 7, potentially more. |
| Engineering artefact | **6/10** | It works, it is cheap, it is auditable, and the negative-result discipline (removing the p=0.71 tier) is better than most published work. |

---

## 1. Is "extract quantities, units, constants and identifiers, then compare the token set" established?

Yes. Unambiguously. Each half of it is established separately and the combination is standard practice.

**Hard-token extraction from scientific prose is a solved, named subfield.** The closest precise prior art is CQE, the Comprehensive Quantity Extractor (Almasian et al., **EMNLP 2023, peer-reviewed**), which extracts value, unit, change/condition and the concept the quantity attaches to, from exactly the kind of text described. https://aclanthology.org/anthology-files/pdf/emnlp/2023.emnlp-main.793.pdf. Earlier, "Mining Measured Information from Text" (preprint https://arxiv.org/pdf/1505.01072) does measurement extraction; there is a CRF-based line of work on unit-of-measure extraction from scientific documents. The framing "scientific and technical documents describe methods and results using measured quantities, a numeric value paired with a unit" is boilerplate in that literature, not a new observation.

**Set-overlap on extracted structural tokens is the standard formula-retrieval baseline.** This is the closest structural match to Tier 2, and it is close enough that a reviewer will name it. The Tangent family represents a formula as a **bag of symbol pairs** drawn from its Symbol Layout Tree, then scores candidates with **Dice's coefficient for set similarity**. That is Tier 2's architecture with a different token extractor.
- Tangent search engine, symbol-pair bags and set-agreement metrics: https://arxiv.org/pdf/1507.06235 (**preprint** of the peer-reviewed line)
- Tangent-L, math-tuple features for BM25 ranking, **ACM DocEng 2018, peer-reviewed**: https://cs.uwaterloo.ca/~fwtompa/.papers/doceng2018-tangent-l-final.pdf
- Tangent-CFT, **ACM ICTIR 2019, peer-reviewed**: https://dl.acm.org/doi/abs/10.1145/3341981.3344235
- ARQMath (CLEF lab, refereed overviews): https://cs.rit.edu/~dprl/ARQMath/2021/ ; a recent survey of structural/symbolic formula-search representations: https://link.springer.com/chapter/10.1007/978-3-031-88708-6_8

**Jaccard-on-token-sets for deduplicating machine-generated defect reports is also established, in the exact adjacent domain.** Static-analysis warning deduplication uses **MinHash/LSH estimating Jaccard similarity** as a state-of-the-art method, and Fry & Weimer found **over 30% of automatically produced defect reports were duplicates** (WCRE 2013, **peer-reviewed**): https://web.eecs.umich.edu/~weimerw/p/weimer-wcre2013-static-preprint.pdf. Survey context, IEEE TSE 2023, **peer-reviewed**: https://dl.acm.org/doi/10.1109/TSE.2023.3329667.

**Tier 1 (location) is the oldest part of all.** In duplicate bug report detection, the REP retrieval function (Sun et al., ASE 2011, **peer-reviewed**) explicitly combines textual similarity with *non-textual structured fields* (product, component, version) for exactly the reason CDSFL uses location: https://www.researchgate.net/publication/220883724_Towards_more_accurate_retrieval_of_duplicate_bug_reports. Survey: https://www.researchgate.net/publication/339077162_Duplicate_Detection_Models_for_Bug_Reports_of_Software_Triage_Systems_A_Survey.

**Quantity-aware retrieval as an explicit research problem.** "Numbers Matter! Bringing Quantity-awareness to Retrieval Systems" (Almasian, Bruseva, Gertz, Heidelberg, **preprint** arXiv:2407.10283, https://arxiv.org/html/2407.10283) builds a concept/unit index where unit matching is enforced by an indicator function so quantities only score when units match exactly. That is Tier 2's unit-handling logic. It introduces FinQuant (306,291 sentences / 420 queries) and MedQuant (153,252 / 210).

**Closest single statement of prior art for Tier 2:** *a bag of extracted domain tokens compared by a set-overlap coefficient, with structured non-textual fields as a pre-filter.* Tangent (formulas) + REP (structured fields) + MinHash-Jaccard warning dedup (defect reports) together cover it. The specific token vocabulary (numbers, units, claim IDs, symbols, chemical formulae) is a sensible engineering choice, not a contribution.

---

## 2. Is comparing the COMPUTED VALUE rather than the wording established? Under what name?

Yes, and it has at least three names depending on which literature you enter from.

**"Answer equivalence"** is the precise term in QA evaluation. Bulian, Buck, Gajewski, Börschinger & Schuster, "Tomayto, Tomahto. Beyond Token-level Answer Equivalence for Question Answering Evaluation", **EMNLP 2022, peer-reviewed**: https://aclanthology.org/2022.emnlp-main.20/. 23k human judgements; dataset at https://github.com/google-research-datasets/answer-equivalence-dataset. This is the canonical citation for "decide whether two textual assertions assert the same answer, independent of surface form."

**"Self-consistency" / answer-level marginalisation** is the same idea used as an aggregation operator rather than an evaluation one. Wang et al., "Self-Consistency Improves Chain of Thought Reasoning in Language Models", **ICLR 2023, peer-reviewed**: https://iclr.cc/virtual/2023/poster/11718 ; https://dblp.org/rec/conf/iclr/0002WSLCNCZ23.html. It marginalises over reasoning paths by grouping on the *final answer*, which is exactly Tier 3's move: ignore the prose, group on the value. Universal Self-Consistency (**preprint**, https://arxiv.org/pdf/2311.17311) extends it to free-form answers using an LLM to adjudicate equivalence, i.e. the LLM-based alternative to Tier 3.

**"Symbolic/numeric answer verification"** is the deterministic implementation. Math benchmarks canonicalise answers (strip `\boxed{}`, normalise `0.5` / `1/2` / `\frac{1}{2}`) and check equivalence by simplifying the difference in SymPy to zero, falling back to an LLM judge when symbolic simplification fails. See e.g. ASyMOB (**preprint**, https://arxiv.org/html/2505.23851v3) and Putnam-AXIOM (**preprint**, https://arxiv.org/pdf/2508.08292) for explicit descriptions of this two-stage design.

**Numerical consistency checking in scientific prose has a peer-reviewed 10-year track record, and it is the closest thing to Tier 3's actual use case.** `statcheck` extracts reported NHST results (test statistic, df, reported p) from psychology papers and **recomputes** the p-value, flagging mismatches. Nuijten & Polanin, *Research Synthesis Methods* 2020, **peer-reviewed**: https://onlinelibrary.wiley.com/doi/full/10.1002/jrsm.1408 ; package https://cran.r-project.org/package=statcheck. Applied to 30,000+ papers; roughly half contained at least one inconsistency, one in eight had one that changed the statistical conclusion. This is directly relevant: an established, deterministic, no-model, recompute-and-compare check over quantities in STEM prose that is taken seriously by the methods-reform community.

**Adjacent quantity-verification in NLG.** Herman (Zhao, Cohen & Webber, **Findings of EMNLP 2020, peer-reviewed**, https://aclanthology.org/2020.findings-emnlp.203/) verifies quantity entities (dates, numbers, sums of money) in generated summaries against the source. Same primitive: extract quantities, compare, act on the comparison. QuanTemp (**SIGIR 2024, peer-reviewed**, https://dl.acm.org/doi/pdf/10.1145/3626772.3657874) is the benchmark for fact-checking numerical claims and reports that LLMs are *worse* than smaller NLI models fine-tuned for numeracy, which is a useful argument in favour of the founder's non-LLM design.

**Bottom line for Tier 3.** The idea is established, well named, and has both a peer-reviewed evaluation-theory home (answer equivalence) and a peer-reviewed scientific-prose home (statcheck-style recomputation). Do not claim it as new. Claim the *combination* with tiers 1 and 2 under a run-stopping criterion, if you claim anything.

---

## 3. Is applying this to deduplicating machine-generated findings novel?

Partly. This is where the strongest claim lives, and also where the literature is closing fastest.

**What already exists.** Deduplicating findings from multiple LLM reviewers is standard production practice and is described in the preprint literature. Multi-agent code review orchestrators "deduplicate findings, resolve conflicts between agents, and produce the final unified review"; Multi-Review runs n independent passes and aggregates with an additional LLM call, filtering single-pass findings as noise (F1 +43.67% at n=10, plateau at n=5–10). Source: "Benchmarking and Studying the LLM-based Code Review", **preprint** arXiv:2509.01494, https://arxiv.org/abs/2509.01494. MARG (D'Arcy et al., **preprint** arXiv:2401.04259, https://arxiv.org/abs/2401.04259) does multi-agent review of scientific papers and cut generic comments from 60% to 29%; I could not confirm from the abstract page whether its comment-merging step is rule-based or LLM-based, and I would not assert either way.

**What the state of the art actually uses for the identity decision: an LLM judge.** This is the finding that matters most for the novelty claim, and it cuts both ways.
- The code-review benchmark above uses an **LLM-as-judge** to decide whether a predicted defect "hits" a ground-truth defect, and validates it against humans at **89.2%–94.9% hit-agreement**.
- FLAWS, a benchmark for error identification and localisation in scientific papers (Xi, Rao, Payan & Shah, **preprint** arXiv:2511.21843, https://arxiv.org/pdf/2511.21843, dataset at https://github.com/xasayi/FLAWS), also uses **LLM-based judgement** to decide whether a model-found error matches a ground-truth annotation.

So: the two closest benchmarks to CDSFL's task both solve the identity problem with an LLM judge, and both validate that judge against humans. A deliberately deterministic alternative is therefore a *defensible* contribution, because it is cheap, reproducible, auditable and immune to the documented pathologies of LLM judges (flip rates of 25–50% under position swaps; https://arxiv.org/abs/2406.07791, **preprint**, reported as later appearing at IJCNLP-AACL 2025, which I could not independently confirm; broader reliability evidence at https://arxiv.org/pdf/2606.19544, **preprint**). But it is defensible as an *engineering trade*, not as a conceptual discovery, and it has to be measured against the LLM judge to be worth saying.

**What appears genuinely unoccupied.** I found no work that:
1. uses a deterministic, non-LLM, non-embedding identity function over machine-generated findings, *and*
2. couples that function to a **run-termination criterion** for an iterative multi-reviewer falsification loop, *and*
3. targets STEM technical prose rather than code.

Deterministic checking of *manuscripts* exists in preprint form: "Deterministic Integrity Gates for LLM-Assisted Clinical Manuscript Preparation" (Nam, Jeong & Kim, **preprint** arXiv:2606.09500, https://arxiv.org/pdf/2606.09500) does numeric-consistency validation, unit standardisation and cross-reference integrity with no LLM. That is the nearest neighbour in spirit, but it checks the *document*, not the *findings about* the document.

**The stopping-criterion framing has a 20-year-old ancestor you are not citing and should be.** "Return only content that is new given what has already been seen" is the **TREC Novelty Track** (2002–2004), where the winning approaches used word-overlap and named-entity-overlap features against previously-seen sentences and reported gains of 5–9% over baseline. Overview: https://trec.nist.gov/pubs/trec13/papers/OVERVIEW13.pdf ; UMass system: https://trec.nist.gov/pubs/trec13/papers/umass.novelty.hard.pdf ; retrospective "Novelty detection: the TREC experience" (**peer-reviewed**, HLT/EMNLP 2005): https://www.researchgate.net/publication/220817129_Novelty_detection_the_TREC_experience. A reviewer who knows IR will ask why this is not the framing. The honest answer, which is a good one, is that hard-token overlap is the domain-specialised version of TREC's word-overlap novelty features. Say it first.

**Answer to the question as asked:** the *technique* is not novel, the *domain* (LLM findings) is already occupied by LLM-judge methods, and the *specific combination* of determinism + STEM hard tokens + run termination is, as far as I can find, unoccupied. That is a narrow strip of ground. It is enough for a workshop paper and not enough for a claim of a new method.

---

## 4. What would take this from suggestive to publishable

Before the list, the problems a reviewer will raise, because the further work follows from them. I re-derived the reported statistics to check them.

**The reported Fisher p reproduces exactly.** `scipy.stats.fisher_exact([[19,0],[14,30]])` gives **p = 1.42e-07**, confirming the Tier 3 test was run on the SAME/DIFFERENT contingency with UNKNOWN excluded. That is a legitimate conditional test, but it conditions on coverage, so it neither credits nor penalises the large coverage asymmetry (32% UNKNOWN on same-defect pairs vs 85% on different-defect pairs). That asymmetry is itself a possible confound: same-defect pairs may simply be more numeric-dense, in which case part of the "association" is coverage, not value agreement.

**Six specific problems.**

1. **The ground truth is a model, not a human.** Labels come from a sentence-embedding backend. The study therefore measures "does hard-token Jaccard agree with embedding cosine", not "does it identify the same defect". Every headline number inherits the embedding model's errors, and the p-values measure agreement between two automated methods. This is the finding that kills the paper at review. Both closest benchmarks (FLAWS, arXiv:2509.01494) validate against humans and report agreement rates; that is the bar.

2. **The hard cases were removed before measurement.** 438 same-location pairs, 28 + 290 = **318 labelled**, so **120 pairs (27.4%) fall in the 0.70–0.90 grey band and are discarded**. Those are precisely the pairs where identity is genuinely ambiguous. Reporting a separation statistic after deleting the ambiguous middle inflates every number in the report. This is not a minor caveat.

3. **p-values are the wrong statistic.** Mann-Whitney p = 1.9e-25 tells you the two Jaccard distributions differ. It does not tell you the operating point, and with n = 28 vs n = 290 a tiny effect would also produce a small p. What is needed is ROC-AUC and, because same-defect prevalence is only **28/318 = 8.8%**, **PR-AUC**, which is the honest metric at that prevalence.

4. **The pairs are not independent.** 438 pairs are drawn from 165 findings across 6 runs. Pairs share findings; findings share runs. Any test that treats pairs as i.i.d. is anticonservative by an unknown factor. The effective sample size is closer to 6 than to 438.

5. **"It NEVER called a same-defect pair DIFFERENT" is a claim about 28 observations.** Exact Clopper-Pearson gives a 95% upper bound of **12.3%** (rule of three: 10.7%). The true split rate could be as high as one in eight. State it that way.

6. **Tier 3's operating characteristics are much less impressive than its p-value, and the design leans the wrong way.** As a merge rule, Tier 3 has **recall 19/28 = 67.9%** and **precision 19/33 = 57.6%**. Roughly **two in five Tier-3 merges are wrong.** Worse: because Tier 3 "can only merge, never split", *every* Tier-3 error is a false merge, and a false merge is exactly the error that makes a new defect look old and ends the run early. The tier is constrained so that its only possible failure is the failure you say you care about. That needs either a defence or a redesign, and either way it belongs in the abstract, not in a footnote. Note also that the reported Fisher test credits Tier 3 for its 30 DIFFERENT calls on different-defect pairs, which are operationally inert if DIFFERENT never overrides Tier 2.

### Further work, ordered by value-for-effort

**1. Human ground truth on a stratified sample. (Highest value, moderate effort. Everything else is worthless without it.)**
150–200 pairs, two independent annotators, adjudicated, with Cohen's kappa reported. **Stratify to over-sample the 120 grey-band pairs**, since those decide whether the method works where it matters. Then re-run every statistic against human labels and report the embedding backend's own agreement with humans as a separate number. If the embedding backend agrees with humans at 85% and hard-token Jaccard agrees with the embedding backend at 90%, you have a chain, not a measurement. Benchmark to beat: 89–95% (arXiv:2509.01494).

**2. Replace p-values with classifier metrics and confidence intervals. (Highest value, lowest effort. One afternoon.)**
ROC-AUC and PR-AUC with **clustered bootstrap CIs resampling runs, not pairs**. Choose an operating threshold and report precision, recall, F1 and the false-merge rate at that threshold. Report 0/28 as "0 observed, 95% CI [0, 12.3%]". Report Tier 3 as recall 67.9% / precision 57.6% up front.

**3. Baselines and ablations. (High value, low-to-moderate effort. This is the experiment that tests the founder's actual claim.)**
In priority order:
   - **(a) Plain word-level Jaccard on the raw finding text with stopwords removed.** This is the decisive ablation. Hard tokens are also *rare* tokens, and rare tokens dominate Jaccard anyway. If plain Jaccard scores nearly as well, the hard-token extractor earns nothing and the paper's premise fails. Run this first; it is cheap and it is the reviewer's first question.
   - **(b) TF-IDF / BM25 cosine on finding text** (the IR baseline; REP/BM25F is the named comparator from bug-report dedup).
   - **(c) The embedding backend used directly as the classifier.** It is the label source, so it defines the ceiling; the gap is the price of determinism.
   - **(d) An LLM judge**, to price determinism against accuracy and cost. This is what FLAWS and arXiv:2509.01494 use, so it is the standard you are implicitly claiming to replace.
   - **(e) IDF-weighted hard tokens** instead of raw Jaccard.
   - **(f) Token-class leave-one-out**: numbers only, units only, identifiers only, symbols only. Shows which class carries the signal. My prediction, offered as a prediction and not a finding, is that numbers and claim identifiers carry nearly all of it and units carry almost none. [SPECULATIVE]

**4. Fix the independence problem and report leave-one-run-out. (Moderate value, low effort.)**
Six runs gives six folds. Leave-one-run-out performance is both the correct significance treatment and a free external-validity estimate. Also characterise **the 4 findings with no hard token** — 97.6% coverage sounds excellent, but if the misses are systematically the structural/qualitative defects, those are the ones most exposed to wrong merges, and the coverage number is hiding the risk rather than measuring it.

**5. Test the density claim directly. (High value for the thesis, moderate effort.)**
The claim is that STEM quantity density is what makes identity decidable without understanding. That is a claim about a *contrast*, and there is currently no contrast condition. Two arms: (i) the same pipeline on a low-density corpus (a design document, a policy document, a humanities paper); (ii) a **quantity-masked** version of the same STEM corpus. If performance barely drops, the density claim is false and should be dropped rather than defended. If it collapses, that is the paper's headline and it is a genuinely interesting one.

**6. Evaluate the decision, not the function. (Highest scientific value, highest effort.)**
The similarity function is not the object of interest; the run-stopping decision is. Seed N known defects into a target document, run the loop, and measure **recall at stop** and **rounds to stop**, with the real similarity function versus each baseline from (3). The number that matters is: *how many real defects are missed because a false merge ended the run early?* Nothing else in this list demonstrates that the function is load-bearing; this does.

**7. Reframe the stop rule as capture-recapture. (High value, moderate effort, and the strongest available reframing — mostly writing, not code.)**
Software inspection solved "when do we stop" more than thirty years ago. Capture-recapture estimators use the *overlap* between defects found by multiple independent reviewers to estimate remaining defect content, and the matching step in capture-recapture **is** the similarity function.
   - Briand et al., "A Comprehensive Evaluation of Capture-Recapture Models for Estimating Software Defect Content", **IEEE TSE 2000, peer-reviewed**: https://ieeexplore.ieee.org/document/852741/
   - Petersson, Thelin, Runeson & Wohlin, "Capture-recapture in software inspections after 10 years research", **JSS 2004, peer-reviewed**: https://wohlin.eu/jss04-1.pdf
   - Confidence intervals for the estimates, **peer-reviewed**: https://www.sciencedirect.com/science/article/abs/pii/S0950584902000952

   Adopting this gives three things at once: a principled stop rule with a **confidence interval on residual defects** instead of "no new findings appeared"; a thirty-year literature to situate the work in; and a natural sensitivity analysis showing how estimator error responds to matcher error, which converts the similarity function from an unmotivated component into the measurable input of a well-studied estimator. If I could recommend only one structural change, it is this one.

**8. Publish the negative result in full. (Moderate value, low effort.)**
The panel-designed perturbation tier at Fisher p = 0.71 deserves its own subsection with the full design, the data, and the removal decision. Negative results about mechanisms designed by model panels are scarce, and this is the part of the work that most clearly demonstrates the falsification discipline actually bites.

**9. External corpus. (Necessary eventually, high effort.)**
Six runs on one project's own documents is not external validity. The cheapest route out is **FLAWS** (https://github.com/xasayi/FLAWS), which already contains annotated, localised errors in scientific papers; pairs of model-found errors against those annotations would give same/different labels without building a new corpus, and would let you report directly against a benchmark that a reviewer already knows.

---

## Where I could not find a comparable number

I could not find a benchmark that measures **identity decisions between machine-generated findings** with human labels, reported as precision/recall, in a form directly comparable to the Jaccard medians and Fisher result here. The nearest quantities are of a different kind: the LLM-judge *hit-agreement with humans* of 89.2–94.9% in arXiv:2509.01494, and duplicate-detection recall@k figures from bug-report dedup, which are a retrieval metric over a different unit. **No directly comparable benchmark exists.** That is genuinely a gap, and it is the most publishable thing in this whole area: a small, human-labelled, open dataset of finding-pairs with same/different labels over STEM documents would be cited by everyone building review loops, and would be a larger contribution than the similarity function itself.

## The blunt part

The three tiers are Tangent's bag-of-symbol-pairs with a different token vocabulary, REP's structured-field pre-filter, and answer equivalence restricted to extracted quantities. A reviewer familiar with MathIR and software-engineering defect dedup will recognise all three within a page. The measured effect is real and the p-values are computed correctly, but they are answering a question nobody asked, on labels produced by a model, after the ambiguous 27% was removed. Tier 3, taken as the merge rule it actually is, is right about 58% of the time and can only fail in the direction that ends runs early.

The work is not fraudulent, not sloppy, and not trivial as engineering. It is simply not yet evidence. Items 1, 2 and 3(a) together are about two days of work and would move the evidence rating from 3/10 to about 6/10. Item 7 is what would make it interesting to somebody other than the founder.

**Sources:**
- [CQE: A Comprehensive Quantity Extractor, EMNLP 2023](https://aclanthology.org/anthology-files/pdf/emnlp/2023.emnlp-main.793.pdf)
- [Mining Measured Information from Text (preprint)](https://arxiv.org/pdf/1505.01072)
- [Numbers Matter! Bringing Quantity-awareness to Retrieval Systems (preprint)](https://arxiv.org/html/2407.10283)
- [The Tangent Search Engine (preprint)](https://arxiv.org/pdf/1507.06235)
- [Choosing Math Features for BM25 Ranking with Tangent-L, DocEng 2018](https://cs.uwaterloo.ca/~fwtompa/.papers/doceng2018-tangent-l-final.pdf)
- [Tangent-CFT, ICTIR 2019](https://dl.acm.org/doi/abs/10.1145/3341981.3344235)
- [ARQMath lab home](https://cs.rit.edu/~dprl/ARQMath/2021/)
- [Advancing Math Formula Search Using Diverse Structural and Symbolic Representations](https://link.springer.com/chapter/10.1007/978-3-031-88708-6_8)
- [Clustering Static Analysis Defect Reports to Reduce Maintenance Costs, WCRE 2013](https://web.eecs.umich.edu/~weimerw/p/weimer-wcre2013-static-preprint.pdf)
- [Mitigating False Positive Static Analysis Warnings, IEEE TSE 2023](https://dl.acm.org/doi/10.1109/TSE.2023.3329667)
- [Towards more accurate retrieval of duplicate bug reports (REP), ASE 2011](https://www.researchgate.net/publication/220883724_Towards_more_accurate_retrieval_of_duplicate_bug_reports)
- [Duplicate Detection Models for Bug Reports: A Survey](https://www.researchgate.net/publication/339077162_Duplicate_Detection_Models_for_Bug_Reports_of_Software_Triage_Systems_A_Survey)
- [Tomayto, Tomahto: Beyond Token-level Answer Equivalence, EMNLP 2022](https://aclanthology.org/2022.emnlp-main.20/)
- [Answer Equivalence dataset](https://github.com/google-research-datasets/answer-equivalence-dataset)
- [Self-Consistency Improves Chain of Thought Reasoning, ICLR 2023](https://iclr.cc/virtual/2023/poster/11718)
- [Universal Self-Consistency (preprint)](https://arxiv.org/pdf/2311.17311)
- [ASyMOB symbolic equivalence validation (preprint)](https://arxiv.org/html/2505.23851v3)
- [Putnam-AXIOM (preprint)](https://arxiv.org/pdf/2508.08292)
- [statcheck, Research Synthesis Methods 2020](https://onlinelibrary.wiley.com/doi/full/10.1002/jrsm.1408)
- [statcheck R package](https://cran.r-project.org/package=statcheck)
- [Reducing Quantity Hallucinations in Abstractive Summarization, Findings of EMNLP 2020](https://aclanthology.org/2020.findings-emnlp.203/)
- [QuanTemp, SIGIR 2024](https://dl.acm.org/doi/pdf/10.1145/3626772.3657874)
- [Benchmarking and Studying the LLM-based Code Review (preprint)](https://arxiv.org/abs/2509.01494)
- [FLAWS: Error Identification and Localization in Scientific Papers (preprint)](https://arxiv.org/pdf/2511.21843)
- [FLAWS dataset](https://github.com/xasayi/FLAWS)
- [MARG: Multi-Agent Review Generation (preprint)](https://arxiv.org/abs/2401.04259)
- [Deterministic Integrity Gates for LLM-Assisted Clinical Manuscript Preparation (preprint)](https://arxiv.org/pdf/2606.09500)
- [Judging the Judges: Position Bias in LLM-as-a-Judge (preprint)](https://arxiv.org/abs/2406.07791)
- [Reliability without Validity: LLM-as-a-Judge evaluation (preprint)](https://arxiv.org/pdf/2606.19544)
- [SelfCheckGPT, EMNLP 2023](https://aclanthology.org/2023.emnlp-main.557/)
- [Overview of TREC 2004 (Novelty Track)](https://trec.nist.gov/pubs/trec13/papers/OVERVIEW13.pdf)
- [UMass at TREC 2004: Novelty and HARD](https://trec.nist.gov/pubs/trec13/papers/umass.novelty.hard.pdf)
- [Novelty detection: the TREC experience, HLT/EMNLP 2005](https://www.researchgate.net/publication/220817129_Novelty_detection_the_TREC_experience)
- [Capture-Recapture Models for Estimating Software Defect Content, IEEE TSE 2000](https://ieeexplore.ieee.org/document/852741/)
- [Capture-recapture in software inspections after 10 years research, JSS 2004](https://wohlin.eu/jss04-1.pdf)
- [Confidence intervals for capture-recapture estimations in software inspections](https://www.sciencedirect.com/science/article/abs/pii/S0950584902000952)