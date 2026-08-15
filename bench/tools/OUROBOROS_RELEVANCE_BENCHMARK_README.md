# Ouroboros relevance benchmark

`ouroboros_relevance_benchmark.json` is labelled ground truth for one question: **which model
judges academic relevance best?** It is the scoring set for the librarian bake-off over
`OuroborosCell._cheap_reader_read` (`bench/ouroboros_cell.py`), which currently dispatches to
`haiku`, `deepseek`, or `none`.

The ouroboros cell retrieves papers for findings the model panel raises. Retrieval returns
candidates; a "librarian" reads each one and returns `RELEVANCE: HIGH|MEDIUM|LOW|NONE` plus a
brief. If the librarian cannot tell a bearing paper from one that merely shares a word, the cell
either muddies the panel's evidence or contributes nothing. This file measures that ability.

## How it was built

1. **Findings.** Fourteen real findings were taken from six completed runs, read-only, from
   `bench/logs/exp4[4-9]_*/*_report.json`. Each item records the experiment, round, model finding
   id, source model, severity, and review target, so any label can be traced back to the run that
   produced it. Finding text is verbatim as the runner stored it, including the runner's own
   truncation of long descriptions — that truncated text is exactly what the live cell sees.
   One item (`B07`) uses the model's FIND plus FOLLOW clauses from the raw round file, because the
   stored description drops the clause carrying the phrase "catastrophic progressive collapse".
2. **Candidates.** Each finding carries five or six real papers, retrieved from the arXiv API
   (titles and abstracts verbatim). Eight candidates were not retrieved for this exercise at all:
   they are papers the **live shadow ouroboros cell actually pulled** during Exp 45 to Exp 49,
   lifted from `bench/logs/*/ouroboros_shadow_r*.json`. Their `paper_provenance` field says so.
3. **Labels.** Every candidate carries a true label, a kind, and a one-sentence reason, so a human
   can audit the labelling without re-deriving it.

## Relevance criterion used

A candidate is **RELEVANT** if a domain expert adjudicating the finding would be materially helped
by the paper: it addresses the same technical phenomenon, method, or failure mode named in the
finding, so it could support, refute, or refine the finding or its fix.

A candidate is **IRRELEVANT** if it would not help. This includes papers that share salient
vocabulary in a different technical sense, and papers from the same field that address a different
problem.

Where the label was genuinely contested, the candidate is marked **AMBIGUOUS** and excluded from
scoring (`scored: false`). Guessing on those would make the benchmark measure nothing.

## Candidate kinds

| kind | true label | purpose |
| --- | --- | --- |
| `relevant` | RELEVANT | genuinely bears on the finding |
| `word_collision_trap` | IRRELEVANT | shares a salient word or acronym in a different technical sense — the discriminating items |
| `topic_adjacent_near_miss` | IRRELEVANT | same field, wrong problem — harder than the traps |
| `obvious_irrelevance` | IRRELEVANT | unrelated field — a floor; a reader that misses these is unusable |
| `ambiguous` | AMBIGUOUS | excluded from scoring, retained for audit |

The traps are modelled on the documented live failure: a finding about floating-point
*catastrophic cancellation* retrieved "Overcoming Catastrophic Forgetting by XAI", a neural-network
paper, because the query was severed after the word "catastrophic". That exact paper appears in
`B07` against a structural-engineering finding whose text contains "catastrophic progressive
collapse". Other traps are of the same shape and several are real: `B10` carries a Carina Nebula
stellar survey and a floating wind turbine paper, both of which arXiv returns for "SMARTS" against
a cheminformatics finding about SMARTS substructure queries; `B08` carries two liquid-argon
particle-physics papers that the live cell genuinely retrieved for a Le Chatelier finding about
argon injection.

## Composition

- 14 findings, 79 candidates (5 or 6 per finding).
- Labels: 25 RELEVANT, 46 IRRELEVANT, 8 AMBIGUOUS. Scored set: 71 candidates, 35 per cent positive.
- Kinds: 25 relevant, 26 word-collision traps, 14 topic-adjacent near misses, 6 obvious
  irrelevancies, 8 ambiguous.
- Domains: structural and mechanical engineering (3), frequentist statistics (2), optimisation (1),
  materials fatigue (1), physical chemistry and metrology (2), cheminformatics (1), cryptographic
  data structures (1), Bayesian statistics (1), crash consistency (1), text similarity and
  tokenisation (1). Source runs: Exp 44 (1), Exp 45 (2), Exp 47 (1), Exp 48 (3), Exp 49 (7).
- One item, `B08` (argon and Le Chatelier), has **no relevant candidate at all** and is flagged
  `all_negative: true`. This is not a construction artefact: arXiv holds no paper bearing on
  whether adding an inert gas at constant volume shifts a gas-phase equilibrium. Items like this
  measure precision and refusal, not recall, and should be reported separately.

## How the bake-off should consume it

For each item, for each candidate, put `finding_text` in the RESEARCH TARGET slot of
`OuroborosCell._READER_PROMPT` and the candidate `title` and `abstract` in the paper slots. Parse
the `RELEVANCE:` line and map it to a binary judgement:

- **primary mapping** — `HIGH`/`MEDIUM` count as RELEVANT, `LOW`/`NONE` as IRRELEVANT. This
  matches the live cell, which drops only `NONE` and weights the rest.
- **strict mapping** — only `HIGH` counts as RELEVANT. This tests whether a model reserves its
  top grade for genuinely bearing work.

Report both. Report accuracy, precision, recall, and F1 on the scored set, plus three rejection
rates that matter more than aggregate accuracy for this use: trap rejection, near-miss rejection,
and floor rejection. Skip every candidate with `scored: false`.

Each candidate also carries `label_confidence` (`high` for 67, `medium` for 12). Where two models
finish close, re-score on the high-confidence subset before declaring a winner.

## Limitations

- **The labels are one agent's judgement.** They should be spot-checked by the founder before any
  model ranking derived from them is treated as established. The `why` field on every candidate
  exists to make that spot-check cheap: read the finding, read the title and abstract, and decide
  whether the stated reason holds.
- Candidates give title and abstract only. The live cell reads full text when an open-access copy
  resolves, so absolute scores here understate full-text performance. Relative ranking between
  models is the intended output, not an absolute capability estimate.
- Every candidate is an arXiv record, so the benchmark inherits arXiv's coverage. Chemistry and
  civil engineering are thin there; software, statistics, and machine learning are dense. That
  asymmetry is real and affects what the ouroboros cell can ever retrieve.
- Traps are denser here than in a live round, because they were sought deliberately. Absolute
  error rates will therefore look worse than a live run; the comparison between models is the
  signal.
- The benchmark measures relevance judgement only. It does not measure brief quality, latency, or
  cost. Those must be recorded separately by the bake-off.
- The 25 relevant labels rest on the criterion stated above. A stricter reading — "only papers
  that could settle the specific numeric claim" — would reclassify several of them. `B01` (Euler
  critical load), `B10` (SMARTS substructure), and `B14` (numeric tokenisation) are the items most
  exposed to that reading, and their positives are flagged `medium` confidence for exactly this
  reason.

## Regeneration

The build script lives outside the repo (session scratchpad) because the benchmark is data, not
code: the file is the artefact. Nothing in the repo imports it yet. To extend it, add findings from
further runs under `bench/logs/`, retrieve candidates from the arXiv API, and keep the same schema
and labelling discipline — in particular, mark contested items AMBIGUOUS rather than guessing.
