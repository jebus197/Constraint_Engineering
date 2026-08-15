"""CDSFL Ouroboros Cell (O1) — External research and self-improvement.

In mythology, the ouroboros is the snake consuming its own tail, representing
cyclical self-reference and self-improvement. In CDSFL, the Ouroboros gathers
external research from sources like arXiv and Semantic Scholar, and can gather
data from other CDSFL-linked network systems. It processes what it finds and
presents candidate claims back to the pipeline for verification by other cells.

Key design decisions (confer 12 April 2026, Gemini 3.1 Pro + Codex 5.3):

1. **Between-round placement**: Ouroboros runs AFTER each round completes,
   not during verification. Stage 2 assumes the batch already exists.
   Inserting a cell that creates new claims during verification is
   architecturally confused. One-round lag is acceptable because the
   Macrophage monitors in real time for emergencies.

2. **Disjoint evidence paths**: If the Ouroboros proposes a finding based
   on a paper, the B-Cell must verify it through a completely different
   method (computation, execution, or a strictly different data source).

3. **Provenance**: All external-origin claims carry explicit provenance
   tags: origin_type, source_ref, retrieval_query, retrieved_at,
   source_hash, source_diversity. Mandatory falsification_debt: high.

CRITICAL: O1 runs in SHADOW mode for Exp 39. It logs what it WOULD have
injected into the pipeline but does NOT actually inject claims. Promotion
to active mode requires explicit HIL approval.

Hard caps for Exp 39: max 3 queries per round, max 2 candidate claims.

Refactored from ouroboros_cell.py: 12 April 2026 (cell type split).
The original ouroboros_cell.py was renamed to macrophage_cell.py (internal
monitor). This file is the NEW external research cell.
"""

from __future__ import annotations

import hashlib
import logging
import re
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger("cdsfl.ouroboros")


@dataclass
class ProvenancePacket:
    """Provenance metadata for an external-origin claim.

    Every claim the Ouroboros produces must carry a complete provenance
    packet. The Macrophage monitors these for source monoculture and
    missing fields.
    """
    origin_type: str = "external_ouroboros"  # Always external for O1
    source_ref: str = ""       # Paper DOI, URL, or identifier
    retrieval_query: str = ""  # The search query that found this source
    retrieved_at: str = ""     # ISO 8601 timestamp of retrieval
    source_hash: str = ""      # SHA-256 of source content
    source_diversity: float = 0.0  # Diversity metric (0-1)

    def to_dict(self) -> dict:
        return {
            "origin_type": self.origin_type,
            "source_ref": self.source_ref,
            "retrieval_query": self.retrieval_query,
            "retrieved_at": self.retrieved_at,
            "source_hash": self.source_hash,
            "source_diversity": str(self.source_diversity),
        }


@dataclass
class OuroborosCandidateClaim:
    """A candidate claim produced by the Ouroboros for pipeline injection.

    In shadow mode, these are logged but NOT injected. In active mode,
    they enter the normal intake and go through standard triage and
    verification gates like any other finding.
    """
    claim_id: str
    description: str
    provenance: ProvenancePacket
    relevance_score: float = 0.0   # How relevant to observed anomalies (0-1)
    falsification_debt: str = "high"  # External claims always start high
    round_observed: int = 0        # Which round triggered this research
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "claim_id": self.claim_id,
            "description": self.description,
            "provenance": self.provenance.to_dict(),
            "relevance_score": str(self.relevance_score),
            "falsification_debt": self.falsification_debt,
            "round_observed": self.round_observed,
            "timestamp": str(self.timestamp),
        }


@dataclass
class OuroborosShadowLog:
    """Shadow replay log: records what the Ouroboros WOULD have done.

    For Exp 39, the Ouroboros does not inject claims. Instead, it logs
    what it noticed, what it queried, what came back, and what claims
    it would have created. This allows evaluation without pipeline risk.
    """
    round_idx: int
    anomalies_observed: List[str] = field(default_factory=list)
    queries_issued: List[Dict[str, str]] = field(default_factory=list)
    metadata_retrieved: List[Dict[str, Any]] = field(default_factory=list)
    candidate_claims: List[OuroborosCandidateClaim] = field(default_factory=list)
    # Real read+brief records for the shadow full-text loop (added 2026-07-12). Each
    # entry carries: target, source_ref (cited DOI/arXiv id), via, fulltext_chars,
    # source_hash, relevance, brief, reader_model, raw_reader_response, elapsed_s, error.
    briefs: List[Dict[str, Any]] = field(default_factory=list)
    would_have_injected: bool = False
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "round_idx": self.round_idx,
            "anomalies_observed": self.anomalies_observed,
            "queries_issued": self.queries_issued,
            "metadata_retrieved": self.metadata_retrieved,
            "candidate_claims": [c.to_dict() for c in self.candidate_claims],
            "briefs": self.briefs,
            "would_have_injected": self.would_have_injected,
            "timestamp": str(self.timestamp),
        }


# ─────────────────────────────────────────────────────────────────────────────
# Query construction  (rebuilt 2026-07-31 — Ouroboros defect 1)
# ─────────────────────────────────────────────────────────────────────────────
#
# The old `_target_to_query` was a chain of deletions ending in `words[:10]`.
# Three faults, each observed on live runs and each fixed below.
#
#   FAULT A — the word cap severed multi-word technical terms. On the loop-close
#   proof run the finding "…which suffers catastrophic cancellation in floating
#   point…" hit the cap after "catastrophic". arXiv matched that one word and
#   returned "Overcoming Catastrophic Forgetting by XAI" — continual learning,
#   not floating-point cancellation. Two unrelated senses of one word, and the
#   extractive reader scored it MEDIUM purely on the overlap.
#
#   FAULT B — the harness's own label vocabulary was searched. Every query began
#   "uncertain finding …", and report-shaped descriptions contributed literal
#   "FINDING_ID: SEVERITY: FLAW_CLASS: ABSTRACTION_INDEX: FIND" (see
#   bench/logs/exp44_.../report.json, DeepSeek_F302). None of it is topical.
#
#   FAULT C — code identifiers were deliberately *harvested* into the query
#   (`_target_to_query` mined backtick spans). No academic index contains
#   `streaming_variance` or `EvidenceStore.verify_bundle`.
#
# The rebuild keeps a term LIST rather than a word list, so the cap can never
# fall inside a phrase, and renders it as quoted phrases joined by AND. That
# render was chosen on measurement, not taste (2026-07-31, live APIs):
#
#   'uncertain finding streaming_variance uses naive sum-of-squares formula,
#    which suffers catastrophic'          → arXiv: "Overcoming Catastrophic
#                                            Forgetting by XAI"  (the defect)
#                                           OpenAlex: nothing at all
#   '"catastrophic cancellation" "numerical stability" variance'   (no AND)
#                                         → arXiv: generic variance papers
#   '"catastrophic cancellation" AND "numerical stability" AND Welford'
#                                         → arXiv AND OpenAlex: "A Tale of
#                                            Three Algorithms for Streaming:
#                                            Covariance Estimation after
#                                            Welford and Chan-Golub-LeVeque"
#
# Quoted phrases give the phrase match; AND gives the conjunction that turns a
# relevance-ranked bag of words into a real constraint. The form is deliberately
# prefix-free (no `all:`), because the same string is also sent to Semantic
# Scholar and OpenAlex, and a bare `AND` degrades to a stopword there whereas an
# arXiv field prefix would degrade to a literal search token.

# The cap is a SPECIFICITY BUDGET, not a term count, because an AND of quoted
# phrases constrains far harder than an AND of words. Measured against the live
# arXiv API on 2026-07-31, from real finding text:
#
#   3 quoted phrases  '"catastrophic cancellation" AND "numerical stability"
#                      AND "standard deviation"'                  → 0 results
#                     '"dichromate oxidation" AND "oxygen unbalanced"
#                      AND "balanced equation"'                   → 0 results
#                     '"Euler critical" AND "own inputs"'         → 0 results
#   1 phrase + words  '"catastrophic cancellation"'  → Laguerre pseudospectral
#                       differentiation matrices; singularity swap quadrature —
#                       numerical-analysis cancellation papers, every one
#                     '"Euler critical"'  → "A buckling question"; "Critical
#                       Buckling Loads of … Power-law Columns"
#
# A phrase costs 2 and a bare word costs 1, against a budget of 3. So the query
# is either one phrase plus one word, or up to three words — never a conjunction
# of exact phrases, which is what emptied the result set.
#
# A phrase's companion has to earn its place. Measured the same day, same API:
#   '"Euler critical" AND inputs'                  → 0     '"Euler critical"'
#                                                   → "A buckling question"
#   '"dichromate oxidation" AND unbalanced'        → 0
#   '"cross-round recidivism" AND alternative'     → 0
#   '"catastrophic cancellation" AND sum-of-squares'
#       → "BETULA: Numerically Stable CF-Trees for BIRCH Clustering"
# The difference is not the count, it is the companion: "sum-of-squares" is a
# recognised technical token, "inputs" is a filler noun. So a single word may
# only join a phrase if it is itself DISTINCTIVE — a lexicon member, a
# hyphenated compound, or a capitalised proper noun (Bayesian, Welford,
# Jaccard). Otherwise the phrase stands alone.
_QUERY_BUDGET = 3
_QUERY_PHRASE_COST = 2
_QUERY_MAX_CHARS = 160
# `_select_targets` cuts descriptions at 200 characters; only text at that cut
# can have a severed final word.
_QUERY_TRUNCATION_FLOOR = 195

# Leading `label:` on a target — `uncertain_finding:`, `round_3_anomalies:`.
# Stripped, never searched (fault B). Applied repeatedly so a target that
# carries both a harness prefix and a report label loses both.
_LABEL_PREFIX_RE = re.compile(r'^\s*"?[A-Za-z_][A-Za-z0-9_]{0,40}"?\s*:\s*')

# CDSFL report step labels. ALL-CAPS in the corpus and always structural, so the
# colon is optional ("FIND `EvidenceBundle.save_json` …" has none).
#
# The labels do more than mark noise: they SEGMENT the finding. A report-shaped
# description is FIND (the defect) followed by FALSIFIER, CORROBORATION,
# ADMISSIBILITY, NOVELTY — machinery, and in the FALSIFIER's case usually raw
# Python. Keeping only the content segments is what stops a query like
# '"import record" AND crashes AND keys' (bench/logs/exp44_…/DeepSeek_F701,
# where the FALSIFIER block's `from bench.evidence import EvidenceRecord`
# outscored the defect itself).
_STEP_LABELS_CONTENT = ("FIND", "FOLLOW", "ANALYSE", "ANALYZE", "DESCRIPTION",
                        "SUMMARY", "ISSUE", "RATIONALE", "MECHANISM")
_STEP_LABELS_MACHINERY = (
    "FINDING_ID", "SEVERITY", "FLAW_CLASS", "ABSTRACTION_INDEX", "FIX",
    "FALSIFIER", "FALSIFICATION", "ATTEMPT", "RESULT", "CORROBORATION",
    "ADMISSIBILITY", "NOVELTY", "DIVERGENCE", "VERIFIED", "LOCATION",
    "EVIDENCE", "PREMISE", "CONCLUSION", "SEARCH", "REPLACE", "CITATIONS",
    "RECOMMENDATION", "CLASSIFICATION", "JUSTIFICATION",
)

# VERDICT HEADERS — a distinction found by measurement, 2026-08-04.
#
# These were in the machinery list, and that silently destroyed 6.9% of real
# findings. Measured over 274 archived descriptions from Exp 45-53: nineteen
# produced the meaningless fallback query, and every one of them opened
# "VERDICT: CONFIRM C0019. <the actual defect>". Because CONFIRM was machinery,
# the segment AFTER it — which is the whole description — was discarded, and
# _query_strip_labels returned the empty string from a perfectly good sentence.
#
# The distinction that matters is what a label INTRODUCES, not whether the label
# is structural. FALSIFIER is followed by Python and must stay machinery (that is
# the DeepSeek_F701 case, where a FALSIFIER block's import outscored the defect).
# A verdict header is followed by the REASONING, which is exactly the content the
# search wants. So they are kept as content-bearing.
_STEP_LABELS_VERDICT = ("VERDICT", "CONFIRM", "WITHDRAW", "REFUTE", "DISPUTE",
                        "RETAIN")
_STEP_LABEL_RE = re.compile(
    r'(?:(?<=^)|(?<=[\s"\'{,;(]))"?('
    + '|'.join(sorted(_STEP_LABELS_CONTENT + _STEP_LABELS_MACHINERY,
                      key=len, reverse=True))
    + r')"?\s*:?'
)
# Mixed-case labels: a label only when it opens a clause and a colon follows
# within a short span, so "Evidence from current code:" is recognised while
# "the impact on the beam" is left alone.
_FIELD_LABEL_RE = re.compile(
    r'(?:^|(?<=[.;\n]))\s*'
    r'(?:Location|Evidence|Mechanism|Impact|Severity|Method|Note|Source|Line'
    r'|Reference|Fix|Finding)\b[^:.\n]{0,30}:',
    re.IGNORECASE,
)

# Code shapes. Removed from the prose, then re-offered as *demoted* natural
# language terms (fault C): `streaming_variance` is unsearchable, but the words
# "streaming variance" are not, and dropping them outright would have thrown
# away the only topical noun in the loop-close finding.
_FENCE_RE = re.compile(r'```.*?```', re.S)
_BACKTICK_RE = re.compile(r'`+[^`]*`+')
_CODE_SHAPES = (
    re.compile(r'\b[\w./\\-]*\.(?:py|json|md|toml|txt|ya?ml|csv|log|cfg|ini|sh)\b'),
    re.compile(r'\b[A-Za-z_][A-Za-z0-9_]*\(\s*\)'),                    # foo()
    re.compile(r'\b[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)+\b'),  # a.b.c
    re.compile(r'\b[A-Za-z][A-Za-z0-9]*_[A-Za-z0-9_]*\b'),             # snake_case
    re.compile(r'\b[a-z]+[A-Z][A-Za-z0-9]*\b'),                        # camelCase
    re.compile(r'\b[A-Z][a-z0-9]+(?:[A-Z][a-z0-9]+)+\b'),              # PascalCase
)
_CAMEL_SPLIT_RE = re.compile(r'(?<=[a-z0-9])(?=[A-Z])')

# LaTeX / maths fragments the panel writes into findings.
_MATH_RES = (
    re.compile(r'\$[^$]*\$'),
    re.compile(r'\\\(.*?\\\)', re.S),
    re.compile(r'\\\[.*?\\\]', re.S),
    re.compile(r'\\[a-zA-Z]+\{[^}]*\}'),
    re.compile(r'\\[a-zA-Z]+'),
)

# Document-local tags: CH-11, EN-06, ZC-13, SW-21-REF-04, F302, C4-02.
# Searchable nowhere; they are coordinates inside the artefact under review.
# The pattern requires a hyphen (or the bare F-number finding shape) so that
# chemical formulae — H2O, CO2, NO2 — are left alone.
_DOC_TAG_RE = re.compile(
    r'\b(?:[A-Z]{1,4}\d{0,2}[-\u2011\u2013]\d+(?:[-\u2011\u2013][A-Za-z0-9]+)*'
    r'|F\d{2,4})\b'
)
_NUMBER_RE = re.compile(
    r'(?<![A-Za-z])\d[\d,.]*\s*'
    r'(?:%|st|nd|rd|th|s|x|ms|kN|kW|kg|km|mm|cm|Hz|MHz|GB|MB|W|V|A|L)?\b'
)
_PAREN_RE = re.compile(r'\(([^()]*)\)')

# Function words. Chunk boundaries: a phrase never spans one.
_QUERY_STOPWORDS = frozenset("""
a an the this that these those it its it's their them they he she his her our we you your my
is are was were be been being am has have had having do does did doing done
of in on at to for from with without within into onto over under above below by via across
and or nor but so than then thus hence therefore because since while when where which who whom
whose what how why if unless until after before during between among per about against toward
not no nor only just also even still yet already again more most less least much many few
can could may might must shall should will would need needs
as such like both either neither each any all some other another same one two three
however moreover therefore thus hence instead meanwhile furthermore additionally
consequently otherwise nevertheless nonetheless ever never always often sometimes
here there where whether once twice very quite rather really exactly only own else
""".split())

# Report/harness vocabulary and near-empty verbs. Present in almost every
# finding, topical in none of them.
_QUERY_GENERIC = frozenset("""
uncertain finding findings anomaly anomalies round rounds severity claim claims verdict
verdicts flaw class abstraction index target file document section statement text line lines
uses use used using cause causes caused causing return returns returned returning provide
provides provided given gives give accept accepts accepted add adds added set sets get gets
make makes made mean means meant require requires required allow allows allowed contain
contains contained include includes included appear appears appeared say says said show shows
shown note notes noted call calls called check checks checked treat treats treated
current currently prior later earlier every another same different possible likely actually
simply silently unconditionally explicitly implicitly correct incorrect wrong missing present
method methods function functions code test tests case cases result results value values
description descriptions summary rationale justification recommendation issue detail details
confirm confirmed confirms withdraw withdrawn withdrawing refute refuted refutes dispute
disputed duplicate duplicates feedback flag flags
fail fails failed failing crash crashes crashed assume assumes assumed assuming
skip skips skipped happen happens occur occurs exist exists
overstate overstates understate understates correspond corresponding correspondingly
gemini chatgpt deepseek codex cc1 cc2 panel
""".split())
# NOTE deliberately absent from the generic list: state, field, key, memory, list,
# record, logic, store. Each is half of a real technical term somewhere in scope
# ("limit state", "oxidation state", "public key", "immune memory", "linked
# list"), and membership here does double duty — it demotes the word AND breaks
# the phrase chunk around it. Breaking a real phrase costs more than letting a
# weak single word through, so the list holds only words that are never part of
# a technical phrase.

# Programming vocabulary. Reachable only through an identifier, and worthless in
# an academic index even after translation to words.
_QUERY_CODE_VOCAB = frozenset("""
json dict dicts tuple str int float bool none null true false self init
args kwargs def cls attr attrs getattr setattr hasattr param params kwarg config cfg
url uri http https api sdk cli repo src lib libs util utils impl func fn method py
dump dumps parse parser serialize deserialize
assert raise except exception traceback keyerror valueerror typeerror attributeerror
stderr stdout stdin logger logging debug warn warning
import export bench elif try finally yield lambda enumerate obj
""".split())
# The same trap as the generic list, and it bit once already: "load" sat here for
# `json.load` and silently deleted the load from "Euler critical load"
# (bench/logs/exp49_..., ChatGPT_F001). Words pruned back out for that reason --
# load, path, index, range, module, package, string, list, state, open, close,
# read, write -- are each half of a real technical term somewhere in scope.

# Report-field words that are demoted in scoring but NOT used as chunk breaks —
# they may still be the middle of a real phrase ("evidence lower bound").
_QUERY_LABEL_WORDS = frozenset(
    "evidence location finding severity impact mechanism note reference source".split()
)

# Curated multi-word technical terms. Matching one pins it as a quoted phrase
# and lifts it above the generic scorer. Deliberately small and deliberately
# not load-bearing: a term absent from this list still survives intact, because
# the cap is on TERMS, not words. The list only decides ordering.
_QUERY_PHRASES = frozenset("""
catastrophic cancellation|numerical stability|floating point|round-off error|rounding error
loss of significance|significant figures|machine epsilon|online algorithm|streaming algorithm
standard deviation|sum of squares|least squares|condition number|error propagation
uncertainty propagation|monte carlo|finite element|order of magnitude|dynamic amplification
limit state|buckling load|critical load|load path|progressive collapse|factor of safety
race condition|hash collision|birthday bound|collision probability|constant time
false positive|false negative|confidence interval|prior distribution|posterior distribution
bayesian inference|statistical power|cross validation|neural network|language model
diminishing returns|exponential decay|convergence criterion|reaction stoichiometry
oxidation state|activation energy|reaction rate|mass balance|dimensional analysis
""".strip().replace("\n", "|").split("|"))


def _query_normalise_phrase(phrase: str) -> str:
    """Lowercase a phrase and treat hyphens as spaces, so the hyphenated token
    ``sum-of-squares`` matches the lexicon entry ``sum of squares`` while still
    being emitted as the single token the panel actually wrote."""
    return re.sub(r'[\u2010-\u2015-]+', ' ', phrase.lower()).strip()


def _query_strip_prefix(text: str) -> str:
    """Drop leading ``label:`` markers — ``uncertain_finding:``,
    ``round_3_anomalies:``, ``FINDING_ID:`` — repeatedly, so a target carrying
    both a harness prefix and a report label loses both."""
    prev = None
    while prev != text:
        prev = text
        text = _LABEL_PREFIX_RE.sub('', text, count=1)
    return text


def _query_strip_labels(text: str) -> str:
    """Remove the harness's own label vocabulary (fault B) and keep only the
    content segments of a report-shaped description."""
    text = _query_strip_prefix(text)

    # re.split with one capturing group → [seg0, label1, seg1, label2, seg2, …]
    parts = _STEP_LABEL_RE.split(text)
    kept = [parts[0]]
    for i in range(1, len(parts) - 1, 2):
        if parts[i] in _STEP_LABELS_CONTENT or parts[i] in _STEP_LABELS_VERDICT:
            kept.append(parts[i + 1])
    text = ' \x00 '.join(kept)

    text = _FIELD_LABEL_RE.sub(' \x00 ', text)
    return text


def _query_drop_truncated_tail(text: str) -> str:
    """``_select_targets`` truncates descriptions at 200 characters, which lands
    mid-word about as often as not — "…the arrangement tolerat", "…which mixi".
    A fragment is a guaranteed zero-recall search term, so the final token is
    dropped — but ONLY for text long enough to be sitting on that cut. Without
    the length guard this fires on every short complete description too, and it
    ate the "bias" from "…possible systemic bias"."""
    stripped = text.rstrip()
    if len(stripped) < _QUERY_TRUNCATION_FLOOR:
        return text
    if not stripped or stripped[-1] in '.!?;:"\')]}`':
        return text
    head, _, tail = stripped.rpartition(' ')
    tail = tail.lstrip('`\'"([{')      # "…flags it as `recidivis" — still a fragment
    if not head or not re.fullmatch(r"[A-Za-z][A-Za-z0-9\-'‐‑]*", tail):
        return text
    return head


def _query_split_identifier(ident: str) -> List[str]:
    """``EvidenceStore.verify_bundle`` → ``['evidence', 'store', 'verify',
    'bundle']``; programming vocabulary and stub words dropped."""
    parts = re.split(r'[^A-Za-z0-9]+', _CAMEL_SPLIT_RE.sub(' ', ident))
    words = []
    for p in parts:
        w = p.lower()
        if len(w) < 4 or not w.isalpha():
            continue
        if w in _QUERY_CODE_VOCAB or w in _QUERY_GENERIC or w in _QUERY_STOPWORDS:
            continue
        words.append(w)
    return words


def _query_extract_code(text: str) -> tuple:
    """Strip code out of the prose and return ``(prose, identifier_terms)``.

    ``identifier_terms`` are natural-language renderings, ordered longest-first:
    a two-word identifier becomes a phrase candidate as well as two singles, so
    ``streaming_variance`` can still contribute "streaming variance" — the only
    topical noun phrase in the loop-close finding — without ever putting the
    literal identifier in front of an academic index (fault C).
    """
    spans: List[str] = []

    def _grab(m):
        spans.append(m.group(0))
        return ' '
    text = _FENCE_RE.sub(_grab, text)
    text = _BACKTICK_RE.sub(_grab, text)
    for pat in _CODE_SHAPES:
        text = pat.sub(_grab, text)

    terms: List[str] = []
    seen = set()
    for span in spans:
        # A filesystem path carries no topic. Harvesting it gave "users" as a
        # search term for an Euler-buckling finding, out of the absolute path
        # /Users/…/exp49_engineering.md (bench/logs/exp49_…, ChatGPT_F001).
        if '/' in span or '\\' in span:
            continue
        for ident in re.findall(r'[A-Za-z_][A-Za-z0-9_.]*', span):
            words = _query_split_identifier(ident)
            if len(words) == 2:
                cand = [' '.join(words)] + words
            else:
                cand = words
            for c in cand:
                if c not in seen:
                    seen.add(c)
                    terms.append(c)
    return text, terms


def _query_scrub(text: str) -> str:
    """Remove maths, document-local tags, numerics and residual punctuation."""
    for pat in _MATH_RES:
        text = pat.sub(' ', text)

    # Parentheticals: keep a short, digit-free aside ("(paracetamol)", "(logic)")
    # as plain words; drop anything numeric or long ("(11/12)", "(0.0002)",
    # "(21.7x median 0.40s)"). Never leave a bracket behind.
    def _paren(m):
        inner = m.group(1).strip()
        if inner and not any(ch.isdigit() for ch in inner) and len(inner.split()) <= 3:
            return ' ' + inner + ' '
        return ' '
    prev = None
    while prev != text:
        prev = text
        text = _PAREN_RE.sub(_paren, text)
    text = re.sub(r'[()\[\]{}]', ' ', text)

    text = _DOC_TAG_RE.sub(' ', text)
    text = _NUMBER_RE.sub(' ', text)
    # Clause boundaries become hard chunk breaks; everything else that is not a
    # letter, an intra-word hyphen or an apostrophe becomes whitespace.
    text = re.sub(r'[.,;:!?/\\|]+', ' \x00 ', text)
    text = re.sub(r'[\u2012-\u2015\u2500-\u25ff]+', ' \x00 ', text)
    text = re.sub(r"[^A-Za-z\u2010\u2011\-'\x00\s]+", ' ', text)
    return text


def _query_chunks(text: str) -> List[List[str]]:
    """Split scrubbed prose into contiguous runs of content words.

    This is the structural cure for fault A: a chunk is the unit the cap counts,
    so no cap can ever fall between "catastrophic" and "cancellation".
    """
    chunks: List[List[str]] = []
    for segment in text.split('\x00'):
        cur: List[str] = []
        for raw in segment.split():
            w = raw.strip("-'\u2010\u2011")
            lw = w.lower()
            if (len(w) < 3 or not re.fullmatch(r"[A-Za-z][A-Za-z\u2010\u2011\-']*", w)
                    or lw in _QUERY_STOPWORDS or lw in _QUERY_GENERIC
                    or lw in _QUERY_CODE_VOCAB):
                if cur:
                    chunks.append(cur)
                    cur = []
                continue
            cur.append(w)
        if cur:
            chunks.append(cur)
    return chunks


def _query_candidates(chunks: List[List[str]]) -> List[tuple]:
    """Score every 1- and 2-word window inside each chunk, plus any 3-word
    window that the lexicon recognises. Returns ``(score, position, term)``."""
    out: List[tuple] = []
    pos = 0
    for chunk in chunks:
        for width in (3, 2, 1):
            for i in range(len(chunk) - width + 1):
                words = chunk[i:i + width]
                term = ' '.join(words)
                norm = _query_normalise_phrase(term)
                in_lex = norm in _QUERY_PHRASES
                if width == 3 and not in_lex:
                    continue
                score = 4.0 if in_lex else 0.0
                if width == 2:
                    score += 1.0
                for w in words:
                    lw = w.lower()
                    if lw in _QUERY_LABEL_WORDS:
                        # Reachable when truncation cuts the description before
                        # the label's colon ("…Evidence from current c"), so the
                        # label regex cannot see it. Score it as the label it is.
                        score -= 1.0
                        continue
                    score += 1.0
                    if len(lw) >= 9:
                        score += 0.5
                    if '-' in w or '\u2010' in w or '\u2011' in w:
                        score += 0.5          # hyphenated compounds are technical
                    if w[:1].isupper() and not w.isupper() and i > 0:
                        # Proper noun (Welford, Jaccard, Bayesian). Chunk-initial
                        # capitals are excluded because chunks break at clause
                        # boundaries, so position 0 is usually just a sentence
                        # start — that false bonus was promoting "Independent
                        # uncertainty" over the real term in a quadrature
                        # finding (bench/logs/exp48_…, Codex_F004).
                        score += 1.0
                out.append((score, pos + i, term))
        pos += len(chunk)
    return out


def _query_is_distinctive(term: str) -> bool:
    """Is this term specific enough to narrow an already-quoted phrase?

    True for lexicon members ("sum-of-squares"), hyphenated compounds
    ("self-assessment", "cross-round"), and proper nouns (Welford, Bayesian,
    Jaccard). False for filler nouns — "inputs", "alternative", "components" —
    which is what emptied the result set when they were AND-ed onto a phrase.
    """
    if _query_normalise_phrase(term) in _QUERY_PHRASES:
        return True
    if any(ch in term for ch in '-‐‑'):
        return True
    return bool(term[:1].isupper() and not term.isupper())


def _query_select(prose_cands: List[tuple], ident_terms: List[str]) -> List[str]:
    """Take the highest-scoring non-overlapping terms, prose ahead of code."""
    ident_cands = [
        (0.5 + 0.5 * len(t.split()), 10_000 + i, t)
        for i, t in enumerate(ident_terms)
    ]
    ranked = sorted(prose_cands, key=lambda c: (-c[0], c[1]))
    ranked += sorted(ident_cands, key=lambda c: (-c[0], c[1]))

    def _stem(w: str) -> str:
        """Crude singular/base form, so "alternative" and "alternatives" are
        not both spent on the same query."""
        if len(w) > 4 and w.endswith('s') and not w.endswith('ss'):
            w = w[:-1]
        if len(w) > 4 and w.endswith('e'):
            w = w[:-1]
        return w

    chosen: List[str] = []
    used: set = set()
    budget = _QUERY_BUDGET
    for score, _pos, term in ranked:
        if score <= 0 or budget <= 0:
            continue
        cost = _QUERY_PHRASE_COST if ' ' in term else 1
        if cost > budget:
            continue
        if any(' ' in c for c in chosen) and not _query_is_distinctive(term):
            continue
        words = {_stem(w.lower()) for w in _query_normalise_phrase(term).split()}
        if words & used:
            continue
        chosen.append(term)
        used |= words
        budget -= cost
    return chosen


def _query_render(terms: List[str]) -> str:
    """``['catastrophic cancellation', 'Welford']`` →
    ``'"catastrophic cancellation" AND Welford'``."""
    rendered: List[str] = []
    for t in terms:
        t = t.replace('"', '').strip()
        if not t:
            continue
        piece = f'"{t}"' if ' ' in t else t
        candidate = ' AND '.join(rendered + [piece])
        if len(candidate) > _QUERY_MAX_CHARS and rendered:
            break
        rendered.append(piece)
    return ' AND '.join(rendered)


class OuroborosCell:
    """O1 cell: external research and self-improvement engine.

    Runs between rounds. Observes what happened in the completed round,
    queries external sources based on anomalies, and produces candidate
    claims for the next round's normal intake.

    Shadow mode (Exp 39): logs only, no pipeline injection.

    Example::

        o1 = OuroborosCell(shadow=True)
        shadow_log = o1.run_between_rounds(
            round_idx=3,
            anomalies=["verdict_cluster detected"],
            immune_response=response,
        )
        # In shadow mode, shadow_log records what O1 would have done
    """

    # Librarian backends. The default is Haiku via the claude CLI, which is on the
    # Max subscription and therefore free at the margin. These two names exist so a
    # route's model is stated once rather than inlined at the dispatch site — the
    # DeepSeek route previously hardcoded `deepseek-chat`, which is not the model
    # the panel runs.
    DEEPSEEK_READER_MODEL: str = "deepseek-v4-pro"
    KIMI_READER_MODEL: str = "moonshotai/kimi-k3"

    # Hard caps for Exp 39
    MAX_QUERIES_PER_ROUND: int = 3
    MAX_CANDIDATE_CLAIMS: int = 2
    # Real-work caps (added 2026-07-12 for the shadow full-text loop). Network+parse
    # and LLM reads are expensive, so both are hard-bounded per round; the reader is
    # handed at most MAX_FULLTEXT_CHARS of extracted text.
    MAX_FULLTEXT_FETCHES_PER_ROUND: int = 2   # network+parse is expensive
    MAX_READER_CALLS_PER_ROUND: int = 2       # one LLM read per fetched paper
    MAX_FULLTEXT_CHARS: int = 24000           # cap text handed to the reader
    MAX_PDF_BYTES: int = 20 * 1024 * 1024     # mirror run_round_robin.py download cap

    def __init__(
        self,
        shadow: bool = True,
        allowed_sources: Optional[List[str]] = None,
        *,
        contact_email: str = "cdsfl-ouroboros@constraint-engineering.local",
        enable_scihub_fallback: bool = False,
        scihub_mirror: str = "",
        # "haiku" (default, free on the Max subscription) | "deepseek" | "kimi"
        # (shadow-wired 2026-07-31, opt-in only) | "none" (deterministic
        # extractive brief; used by CI so tests never depend on a live backend).
        reader_backend: str = "haiku",
        reader_model: str = "",          # override; default per backend
        enable_fulltext: bool = True,    # download+parse OA full text before reading
    ) -> None:
        self.shadow = shadow  # MUST be True for Exp 39
        # OpenAlex added (free, no key, domain-general) as the reliable default fallback.
        self.allowed_sources = allowed_sources or ["arxiv", "semantic_scholar", "openalex"]
        # Full-text resolution config (off by default). enable_scihub_fallback flips on the
        # silent last-resort retrieval path; scihub_mirror overrides the mirror (config/env).
        self.contact_email = contact_email
        self.enable_scihub_fallback = enable_scihub_fallback
        self.scihub_mirror = scihub_mirror
        # Cheap-reader (librarian) config for the shadow full-text loop. reader_backend
        # picks the dispatch route; "none" forces the deterministic extractive brief
        # (used by CI so the test never hard-depends on an LLM backend being reachable).
        self.reader_backend = reader_backend
        self.reader_model = reader_model
        self.enable_fulltext = enable_fulltext
        self._claim_counter = 0
        self._round_logs: List[OuroborosShadowLog] = []

    def _next_claim_id(self) -> str:
        self._claim_counter += 1
        return f"o1_claim_{self._claim_counter:04d}"

    def run_between_rounds(
        self,
        round_idx: int,
        anomalies: Optional[List[str]] = None,
        immune_response: Optional[Any] = None,
        round_findings: Optional[List[Any]] = None,
    ) -> OuroborosShadowLog:
        """Execute Ouroboros between-round research cycle.

        This is the main entry point. Called AFTER a round completes.

        Args:
            round_idx: Index of the just-completed round.
            anomalies: Anomaly descriptions from Macrophage observations.
            immune_response: The ImmuneResponse from the completed round.
            round_findings: Findings from the completed round.

        Returns:
            OuroborosShadowLog recording what O1 did (or would have done).
        """
        shadow_log = OuroborosShadowLog(round_idx=round_idx)

        # Step 1: Target selection — identify what to research based on anomalies
        targets = self._select_targets(
            anomalies or [],
            immune_response,
            round_findings,
        )
        shadow_log.anomalies_observed = targets

        if not targets:
            self._round_logs.append(shadow_log)
            return shadow_log

        # Step 2: Structured metadata fetch (mocked in shadow/Exp 39)
        queries = self._build_queries(targets)
        shadow_log.queries_issued = queries[:self.MAX_QUERIES_PER_ROUND]

        metadata = self._fetch_metadata(
            shadow_log.queries_issued,
        )
        shadow_log.metadata_retrieved = metadata

        # Step 2.5 (SHADOW real work): resolve OA full text, download, read, brief.
        # Briefs are logged only — never injected into a model prompt, never touch the
        # maths. Wrapped so any fetch/reader failure degrades to error fields, not a crash.
        try:
            shadow_log.briefs = self._read_and_brief(
                shadow_log.queries_issued, metadata,
            )
        except Exception as exc:  # noqa: BLE001 — shadow work is strictly non-fatal
            logger.warning("Ouroboros read+brief failed (round %d): %s", round_idx, exc)
            shadow_log.briefs = []

        # Step 3: Candidate claim generation — built from the REAL briefs
        candidates = self._generate_candidates(
            targets, metadata, round_idx, shadow_log.briefs,
        )
        shadow_log.candidate_claims = candidates[:self.MAX_CANDIDATE_CLAIMS]
        shadow_log.would_have_injected = len(candidates) > 0

        # In shadow mode, log only — no pipeline injection
        if shadow_log.would_have_injected:
            logger.info(
                "Ouroboros [shadow] round %d: would inject %d candidate claims "
                "(capped at %d). Queries: %d. Targets: %s",
                round_idx, len(candidates),
                self.MAX_CANDIDATE_CLAIMS,
                len(shadow_log.queries_issued),
                targets[:3],
            )

        self._round_logs.append(shadow_log)
        self._last_shadow_log = shadow_log
        return shadow_log

    def _select_targets(
        self,
        anomalies: List[str],
        immune_response: Optional[Any],
        round_findings: Optional[List[Any]],
    ) -> List[str]:
        """Select research targets based on round anomalies and findings.

        Prioritises:
        1. Macrophage-flagged anomalies (direct signal)
        2. Recurring disputed findings (convergence failures)
        3. High-severity unresolved claims
        """
        targets = []

        # Macrophage anomalies are direct research triggers
        for anomaly in anomalies:
            targets.append(anomaly)

        # Check for disputed/uncertain findings — use descriptions, not IDs
        # (HARD FIX: finding IDs like 'Gemini_F002' are unsearchable)
        if immune_response:
            final_verdicts = getattr(immune_response, "final_verdicts", {})

            # Build fid → description lookup from round findings
            fid_to_desc: Dict[str, str] = {}
            if round_findings:
                for f in round_findings:
                    fid = getattr(f, "finding_id", None)
                    desc = getattr(f, "description", "")
                    if fid and desc:
                        fid_to_desc[fid] = desc[:200]

            for fid, verdict in final_verdicts.items():
                if verdict == "UNCERTAIN":
                    desc = fid_to_desc.get(fid, "")
                    if desc:
                        targets.append(f"uncertain_finding:{desc}")
                    else:
                        # Fallback: use fid but prefix for clarity
                        targets.append(f"uncertain_finding:{fid}")

        return targets[:5]  # Cap targets

    def _build_queries(
        self,
        targets: List[str],
    ) -> List[Dict[str, str]]:
        """Build structured search queries from targets."""
        queries = []
        for target in targets[:self.MAX_QUERIES_PER_ROUND]:
            # Round-robin source selection (HARD FIX: was always [0])
            source_idx = len(queries) % len(self.allowed_sources) if self.allowed_sources else 0
            source = self.allowed_sources[source_idx] if self.allowed_sources else "arxiv"

            _q = self._target_to_query(target)
            if not _q:
                # Skip rather than search a phrase unrelated to the finding.
                # Recorded so the skip is visible instead of looking like a
                # retrieval that found nothing.
                self._skipped_unqueryable = getattr(
                    self, "_skipped_unqueryable", 0) + 1
                continue
            query = {
                "target": target,
                "source": source,
                "query": _q,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            }
            queries.append(query)
        return queries

    def _target_to_query(self, target: str) -> str:
        """Convert a target description into an academic search query.

        Rebuilt 2026-07-31. See the "Query construction" section above this
        class for the three faults this replaces and the live-API measurements
        that chose the output form. In one line: the query is a list of at most
        three TERMS — quoted where multi-word, joined by ``AND`` — never a
        truncated list of words.

        The pipeline is: strip the harness's labels; lift code identifiers out
        of the prose and demote them to natural-language terms; scrub maths,
        document tags and numerics; cut the remainder into phrase chunks at
        function-word boundaries; score every 1–2 word window inside each chunk
        (plus lexicon-recognised 3-word windows); emit the best non-overlapping
        three.

        Example, from the loop-close proof finding:

            "uncertain_finding:streaming_variance uses the naive sum-of-squares
             formula, which suffers catastrophic cancellation in floating point
             numerical stability ... Welford online algorithm avoids it."
            → '"catastrophic cancellation" AND "numerical stability" AND Welford'

        The cap is on terms, so a multi-word technical phrase is never severed
        (fault A); the label vocabulary is deleted rather than searched (fault
        B); and no identifier reaches the wire (fault C).
        """
        # Remove the harness prefix ONLY — one substitution, not the full label
        # loop — so the 200-character truncation test measures the description
        # as `_select_targets` cut it. Stripping report labels first shortens
        # the text below the floor and the severed final word survives.
        raw = _LABEL_PREFIX_RE.sub('', target or "", count=1)
        text = _query_drop_truncated_tail(raw)
        prose, ident_terms = _query_extract_code(_query_strip_labels(text))
        chunks = _query_chunks(_query_scrub(prose))
        terms = _query_select(_query_candidates(chunks), ident_terms)
        result = _query_render(terms)
        # No usable fallback phrase exists. If nothing survives extraction the
        # finding is pure code and labels, and a query that CANNOT be about the
        # finding is worse than no query: it burns a retrieval and risks handing
        # the panel a paper that has nothing to do with the claim, which the
        # relevance reader may then over-rate. Return empty; the caller skips it.
        return result

    def _fetch_metadata(
        self,
        queries: List[Dict[str, str]],
    ) -> List[Dict[str, Any]]:
        """Fetch structured metadata from arXiv and Semantic Scholar.

        Real API calls (wired 13 April 2026). Results are logged even in
        shadow mode — the ouroboros still does not inject claims into the
        pipeline, but now gathers genuine external evidence for calibration.

        Graceful degradation: if an API call fails (network, rate limit,
        package missing), falls back to shadow_mock for that query.
        """
        results = []
        for query in queries:
            source = query.get("source", "arxiv")
            query_text = query.get("query", "")
            fetched_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

            try:
                fetchers = {
                    "arxiv": self._query_arxiv,
                    "semantic_scholar": self._query_semantic_scholar,
                    "openalex": self._query_openalex,
                }
                fetch = fetchers.get(source)
                # Hard-capped primary attempt (libraries' own timeouts are unreliable).
                papers = (self._run_with_timeout(
                    fetch, query_text, timeout_s=20.0, max_results=3) if fetch else [])
                fetched_via = source if papers else None
                # Fallback chain: if the requested source timed out / returned nothing,
                # try a proven-fast source so the cell is never silently empty when an
                # alternate can do the job (OpenAlex: free, no key, domain-general).
                for alt in ("openalex", "arxiv"):
                    if papers or alt == source:
                        continue
                    papers = self._run_with_timeout(
                        fetchers[alt], query_text, timeout_s=20.0, max_results=3)
                    if papers:
                        fetched_via = f"{alt} (fallback from {source})"
                        break

                result = {
                    "query": query_text,
                    "source": source,
                    "fetched_via": fetched_via,
                    "status": "live" if papers else "live_empty",
                    "results_count": len(papers),
                    "papers": papers,
                    "fetched_at": fetched_at,
                }
            except Exception as e:
                logger.warning(
                    "O1 _fetch_metadata failed for %s query %r: %s",
                    source, query_text[:60], e,
                )
                result = {
                    "query": query_text,
                    "source": source,
                    "status": "shadow_mock",
                    "results_count": 0,
                    "papers": [],
                    "fetched_at": fetched_at,
                    "error": f"{type(e).__name__}: {str(e)[:120]}",
                }
            results.append(result)
        return results

    @staticmethod
    def _query_arxiv(query_text: str, max_results: int = 3) -> List[Dict[str, str]]:
        """Query arXiv API. Returns list of {title, authors, abstract, url, published}."""
        import arxiv

        client = arxiv.Client(num_retries=1, page_size=max_results)
        search = arxiv.Search(
            query=query_text,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance,
        )
        papers = []
        for r in client.results(search):
            papers.append({
                "title": r.title,
                "authors": ", ".join(a.name for a in r.authors[:3]),
                "abstract": r.summary[:500] if r.summary else "",
                "url": r.entry_id,
                "published": r.published.isoformat() if r.published else "",
            })
        return papers

    @staticmethod
    def _query_semantic_scholar(
        query_text: str, max_results: int = 3,
    ) -> List[Dict[str, str]]:
        """Query Semantic Scholar API. Returns list of paper metadata.

        Uses SEMANTIC_SCHOLAR_API_KEY (from .env / environment) when present — the
        authenticated key removes the unauthenticated throttling that made this source
        take ~95s (2026-06-09). Unauthenticated still works (slower); the hard-timeout
        wrapper + OpenAlex fallback bound it either way."""
        import os
        from semanticscholar import SemanticScholar

        _s2_key = os.environ.get("SEMANTIC_SCHOLAR_API_KEY") or None
        sch = SemanticScholar(api_key=_s2_key, timeout=15)
        results = sch.search_paper(
            query_text,
            limit=max_results,
            fields=["title", "authors", "abstract", "url", "year",
                     "citationCount"],
        )
        papers = []
        for p in results[:max_results]:
            authors = ", ".join(
                a.get("name", "") if isinstance(a, dict) else str(a)
                for a in (p.authors or [])[:3]
            )
            papers.append({
                "title": p.title or "",
                "authors": authors,
                "abstract": (p.abstract or "")[:500],
                "url": p.url or "",
                "year": str(p.year) if p.year else "",
                "citations": str(p.citationCount) if p.citationCount else "0",
            })
        return papers

    @staticmethod
    def _run_with_timeout(fn, *args, timeout_s: float = 20.0, **kwargs):
        """Hard wall-clock cap on an external call. The source libraries' own
        timeouts are unreliable (Semantic Scholar's ``timeout=15`` was measured at
        95s on 2026-06-09), so this enforces a real ceiling: the call runs in a
        daemon thread; if it overruns, return [] (best-effort) and let the daemon
        die with the process. Never blocks the caller beyond ``timeout_s``."""
        import threading
        box: Dict[str, Any] = {}

        def _w():
            try:
                box["r"] = fn(*args, **kwargs)
            except Exception as exc:  # noqa: BLE001 — surfaced to caller below
                box["e"] = exc

        t = threading.Thread(target=_w, daemon=True)
        t.start()
        t.join(timeout_s)
        if t.is_alive():
            return []  # timed out — best-effort empty
        if "e" in box:
            raise box["e"]
        return box.get("r", [])

    @staticmethod
    def _query_openalex(query_text: str, max_results: int = 3) -> List[Dict[str, str]]:
        """Query OpenAlex (free, NO API key, fast, domain-general — works across
        physics, biology, CS, etc.). The reliable default fallback source.
        Returns the same metadata shape as the other fetchers."""
        import json as _json
        import urllib.parse
        import urllib.request

        url = (
            "https://api.openalex.org/works?search="
            + urllib.parse.quote(query_text)
            + f"&per_page={max_results}&mailto=cdsfl-ouroboros@constraint-engineering.local"
        )
        req = urllib.request.Request(url, headers={"User-Agent": "CDSFL-ouroboros/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:  # noqa: S310 — fixed host
            data = _json.loads(resp.read().decode("utf-8"))
        papers: List[Dict[str, str]] = []
        for w in data.get("results", [])[:max_results]:
            authors = ", ".join(
                ((a.get("author") or {}).get("display_name", ""))
                for a in (w.get("authorships") or [])[:3]
            )
            inv = w.get("abstract_inverted_index")
            abstract = ""
            if inv:
                pos: Dict[int, str] = {}
                for word, idxs in inv.items():
                    for i in idxs:
                        pos[i] = word
                abstract = " ".join(pos[i] for i in sorted(pos))[:500]
            papers.append({
                "title": w.get("title") or w.get("display_name") or "",
                "authors": authors,
                "abstract": abstract,
                "url": w.get("doi") or w.get("id") or "",
                "year": str(w.get("publication_year") or ""),
                "citations": str(w.get("cited_by_count") or 0),
            })
        return papers

    # --- Full-text resolution (for the loop-close: feed real papers to the models) ---
    # Chain: Unpaywall (free, legal open-access) FIRST; Sci-Hub (configurable, OFF by
    # default, best-effort) LAST. The citation/attribution is ALWAYS the original DOI /
    # publisher — Sci-Hub is only ever a retrieval path, never a cited source. Restores
    # the originally-envisaged ouroboros source list (arXiv + Semantic Scholar + Unpaywall
    # + CORE + OpenAlex, planned 14 April 2026) and the founder's silent-Sci-Hub fallback.

    @staticmethod
    def _normalise_doi(url_or_doi: str) -> str:
        """Extract a bare DOI from a DOI URL or raw DOI; '' if not a DOI."""
        s = (url_or_doi or "").strip()
        for pre in ("https://doi.org/", "http://doi.org/", "doi:"):
            if s.lower().startswith(pre):
                s = s[len(pre):]
        return s if s.startswith("10.") else ""

    @staticmethod
    def _unpaywall_oa_pdf(doi: str, email: str, timeout_s: float = 12.0) -> str:
        """Legal open-access PDF URL for a DOI via Unpaywall, or '' if none."""
        import json as _json
        import urllib.parse
        import urllib.request
        url = f"https://api.unpaywall.org/v2/{urllib.parse.quote(doi)}?email={email}"
        req = urllib.request.Request(url, headers={"User-Agent": "CDSFL-ouroboros/1.0"})
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:  # noqa: S310
            data = _json.loads(resp.read().decode("utf-8"))
        if not data.get("is_oa"):
            return ""
        loc = data.get("best_oa_location") or {}
        return loc.get("url_for_pdf") or loc.get("url") or ""

    def full_text_for_doi(self, doi_or_url: str) -> Dict[str, str]:
        """Resolve a full-text URL for a DOI. Returns {url, via, doi}; via is the retrieval
        path ('unpaywall' / 'scihub'), doi is ALWAYS the original (the cited source).
        Unpaywall first (legal OA); Sci-Hub only if ``enable_scihub_fallback`` is on. Empty
        url on failure (best-effort; never blocks > timeout)."""
        doi = self._normalise_doi(doi_or_url)
        if not doi:
            return {"url": "", "via": "", "doi": ""}
        email = getattr(self, "contact_email", "cdsfl-ouroboros@constraint-engineering.local")
        url = self._run_with_timeout(self._unpaywall_oa_pdf, doi, email, timeout_s=15.0)
        if url:
            return {"url": url, "via": "unpaywall", "doi": doi}
        # Configurable, off-by-default, silent last resort. Cite the original DOI only.
        if getattr(self, "enable_scihub_fallback", False):
            mirror = getattr(self, "scihub_mirror", "") or "https://sci-hub.se"
            return {"url": f"{mirror.rstrip('/')}/{doi}", "via": "scihub", "doi": doi}
        return {"url": "", "via": "none", "doi": doi}

    # --- Real full-text loop: resolve OA URL -> download -> extract -> read -> brief ---
    # Added 2026-07-12. Runs SHADOW-only: briefs are logged, never injected into a model
    # prompt and never touch c_ext / nu_k / gamma. Exp 43 stays a clean generalisation test.

    @staticmethod
    def _arxiv_pdf_url(url: str) -> str:
        """arXiv abs/pdf/entry URL -> direct PDF URL; '' if not arXiv.

        arXiv is fully open-access and is the dominant metadata source in live logs,
        so resolving it directly (before Unpaywall) materially raises fetch success.
        """
        raw = (url or "").strip()
        m = re.search(r"arxiv\.org/(?:abs|pdf)/([\w.\-/]+?)(?:v\d+)?/?$", raw)
        if not m:
            return ""
        vm = re.search(r"(v\d+)/?$", raw)   # preserve an explicit version if present
        ver = vm.group(1) if vm else ""
        return f"https://arxiv.org/pdf/{m.group(1)}{ver}"

    def resolve_fulltext_url(self, paper: Dict[str, str]) -> Dict[str, str]:
        """Resolve a fetchable full-text URL for a fetched paper.

        Order: arXiv-direct (OA) -> Unpaywall (OA) -> Sci-Hub (only if enabled).
        Returns {url, via, source_ref}; source_ref is the DOI/arXiv id we cite.
        """
        raw = paper.get("url", "") or ""
        ax = self._arxiv_pdf_url(raw)
        if ax:
            return {"url": ax, "via": "arxiv", "source_ref": raw}
        ft = self.full_text_for_doi(raw)          # existing resolver, unchanged
        if ft["url"]:
            return {"url": ft["url"], "via": ft["via"], "source_ref": ft["doi"]}
        return {"url": "", "via": "none", "source_ref": raw}

    def _download_and_extract(self, url: str, timeout_s: float = 20.0) -> Dict[str, Any]:
        """Download an OA URL and extract text. PDF via pypdf(->pdfplumber); HTML via
        BeautifulSoup. Best-effort, hard-capped, http(s)-only. Never raises.

        The URL originates from Unpaywall/arXiv metadata, never from model output, so
        this is not acting on injected instructions (SSRF guard: scheme + size + timeout).
        """
        import io
        out = {"text": "", "chars": 0, "content_type": "", "error": ""}
        if not url or not url.lower().startswith(("http://", "https://")):
            out["error"] = "bad-scheme"
            return out
        try:
            import requests
        except ImportError:
            out["error"] = "requests-missing"
            return out

        def _get():
            r = requests.get(
                url, timeout=timeout_s,
                headers={"User-Agent": "CDSFL-ouroboros/1.0 (research)"},
                stream=True)
            ctype = r.headers.get("Content-Type", "").lower()
            try:
                clen = int(r.headers.get("Content-Length", 0) or 0)
            except (TypeError, ValueError):
                clen = 0
            if clen > self.MAX_PDF_BYTES:
                return {"skip": f"too-large:{clen}"}
            # Stream with a RUNNING byte cap so MAX_PDF_BYTES bounds the actual download
            # even when Content-Length is absent/understated — r.content would otherwise
            # buffer the whole body into memory before any slice (OOM risk on a lying server).
            chunks, total = [], 0
            for chunk in r.iter_content(chunk_size=65536):
                if not chunk:
                    continue
                total += len(chunk)
                if total > self.MAX_PDF_BYTES:
                    return {"skip": f"too-large-stream:{total}"}
                chunks.append(chunk)
            return {"ctype": ctype, "body": b"".join(chunks), "status": r.status_code}

        # _run_with_timeout re-raises any exception the worker hit; catch it here so
        # _download_and_extract honours its "Never raises" contract and degrades to an
        # error field (per-paper), rather than propagating and wiping the whole round's briefs.
        try:
            got = self._run_with_timeout(_get, timeout_s=timeout_s)   # reused daemon cap
        except Exception as e:  # noqa: BLE001 — best-effort fetch, never fatal
            out["error"] = f"download:{type(e).__name__}"
            return out
        if not got or "skip" in (got or {}):
            out["error"] = (got or {}).get("skip", "timeout") if isinstance(got, dict) else "timeout"
            return out
        if got["status"] != 200 or len(got["body"]) < 1000:
            out["error"] = f"http-{got['status']}-or-tiny"
            return out

        ctype, body = got["ctype"], got["body"]
        out["content_type"] = ctype
        is_pdf = "pdf" in ctype or body[:5] == b"%PDF-"
        out["text"] = (self._pdf_to_text(io.BytesIO(body)) if is_pdf
                       else self._html_to_text(body))
        out["text"] = out["text"][: self.MAX_FULLTEXT_CHARS]
        out["chars"] = len(out["text"])
        if not out["text"].strip():
            out["error"] = "no-text-extracted"
        return out

    @staticmethod
    def _pdf_to_text(fp, max_pages: int = 15) -> str:
        """Extract text from a PDF byte stream. pypdf primary, pdfplumber fallback.
        (PyPDF2 is NOT installed here; pypdf is its supported successor.)"""
        try:
            from pypdf import PdfReader
            reader = PdfReader(fp)
            parts = [(reader.pages[i].extract_text() or "")
                     for i in range(min(max_pages, len(reader.pages)))]
            txt = "\n\n".join(p for p in parts if p)
            if txt.strip():
                return txt
        except Exception:
            pass
        try:
            import pdfplumber
            fp.seek(0)
            with pdfplumber.open(fp) as pdf:
                parts = [(pdf.pages[i].extract_text() or "")
                         for i in range(min(max_pages, len(pdf.pages)))]
            return "\n\n".join(p for p in parts if p)
        except Exception:
            return ""

    @staticmethod
    def _html_to_text(body: bytes) -> str:
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(body, "lxml")
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()
            return re.sub(r"\n{3,}", "\n\n", soup.get_text("\n")).strip()
        except Exception:
            return ""

    _READER_PROMPT = (
        "You are a research librarian. Read the paper text below and assess how "
        "relevant it is to the RESEARCH TARGET. Do not evaluate the target's truth; "
        "only judge whether this paper bears on it, and distil what it says.\n\n"
        "RESEARCH TARGET:\n{target}\n\n"
        "PAPER TITLE: {title}\nPAPER TEXT (may be truncated):\n{body}\n\n"
        "Respond with EXACTLY two lines:\n"
        "RELEVANCE: <HIGH|MEDIUM|LOW|NONE>\n"
        "BRIEF: <=120 words distilling the paper's bearing on the target; "
        "if NONE, say why in one clause"
    )

    def _cheap_reader_read(self, target: str, paper: Dict[str, str],
                           body: str) -> Dict[str, Any]:
        """Dispatch the librarian read to Haiku (primary) or DeepSeek (fallback).
        Deterministic extractive fallback if no backend is reachable. Never raises."""
        prompt = self._READER_PROMPT.format(
            target=(target or "")[:800], title=(paper.get("title", "") or "")[:300],
            body=(body or paper.get("abstract", ""))[: self.MAX_FULLTEXT_CHARS])
        model_used, raw, err, elapsed = "", "", "", 0.0

        if self.reader_backend == "haiku":
            try:
                from bench.cc2_manager import _dispatch_cli, HAIKU_MODEL
                model_used = self.reader_model or HAIKU_MODEL
                raw, elapsed = self._run_with_timeout(
                    _dispatch_cli, model_used, prompt, 60, timeout_s=75.0) or ("", 0.0)
            except Exception as e:  # noqa: BLE001 — degrade to extractive brief
                err = f"haiku:{type(e).__name__}:{str(e)[:80]}"
        elif self.reader_backend == "deepseek":
            try:
                from bench.experiment_11_orchestrator import call_deepseek
                # deepseek-v4-pro is the panel's DeepSeek. This route defaulted to
                # `deepseek-chat`, a different and weaker model, so the librarian
                # would have run on something the panel does not use and nobody
                # had evaluated. Corrected 2026-07-31 on founder directive.
                model_used = self.reader_model or self.DEEPSEEK_READER_MODEL
                raw = self._run_with_timeout(
                    call_deepseek, model_used, None, prompt, timeout_s=75.0) or ""
            except Exception as e:  # noqa: BLE001 — degrade to extractive brief
                err = f"deepseek:{type(e).__name__}:{str(e)[:80]}"
        elif self.reader_backend == "kimi":
            # SHADOW-WIRED 2026-07-31 (founder directive: "wire K3 with an optional
            # shadow switch for now until we can confirm it is fully working").
            # Never the default. Selecting it is a deliberate act, and if the route
            # is unreachable the cell degrades to the extractive brief exactly as
            # the other two do, so a broken K3 cannot take a run down.
            #
            # Measured 2026-07-31 on the 71-candidate relevance benchmark: K3 scored
            # 0.887 against Haiku's 0.873 under the deployed admission rule, and
            # recovered 24 of 25 genuinely relevant papers against Haiku's 21. The
            # difference is not statistically significant (McNemar exact p=1.0), so
            # this is provisioned, not promoted. Two known constraints: K3 refuses
            # temperature 0 (only 1 is permitted), so it is NOT reproducible run to
            # run; and it spends 6-8x more tokens on hidden reasoning than on
            # visible output, so a small max_tokens returns EMPTY content.
            try:
                from bench.experiment_11_orchestrator import call_openrouter
                model_used = self.reader_model or self.KIMI_READER_MODEL
                raw = self._run_with_timeout(
                    call_openrouter, model_used, None, prompt, timeout_s=90.0) or ""
            except Exception as e:  # noqa: BLE001 — degrade to extractive brief
                err = f"kimi:{type(e).__name__}:{str(e)[:80]}"

        if not raw:  # deterministic extractive fallback — keeps the brief real
            rel, brief = self._extractive_brief(target, body or paper.get("abstract", ""))
            return {"relevance": rel, "brief": brief, "raw": "",
                    "reader_model": model_used or "extractive_fallback",
                    "elapsed_s": round(elapsed, 1), "error": err or "no-backend"}

        rel_m = re.search(r"RELEVANCE:\s*(HIGH|MEDIUM|LOW|NONE)", raw, re.I)
        br_m = re.search(r"BRIEF:\s*(.+)", raw, re.I | re.S)
        return {
            "relevance": (rel_m.group(1).upper() if rel_m else "LOW"),
            "brief": (br_m.group(1).strip()[:1200] if br_m else raw.strip()[:1200]),
            "raw": raw[:4000], "reader_model": model_used,
            "elapsed_s": round(elapsed, 1), "error": err,
        }

    @staticmethod
    def _extractive_brief(target: str, text: str):
        """No-LLM fallback: pick the sentences with most target-term overlap."""
        terms = {w.lower() for w in re.findall(r"[a-zA-Z]{4,}", target or "")}
        sents = re.split(r"(?<=[.!?])\s+", text or "")
        scored = sorted(sents, key=lambda s: -len(terms & {w.lower()
                        for w in re.findall(r"[a-zA-Z]{4,}", s)}))
        top = " ".join(scored[:3]).strip()
        overlap = len(terms & {w.lower() for w in re.findall(r"[a-zA-Z]{4,}", text or '')})
        rel = "MEDIUM" if overlap >= 3 else ("LOW" if overlap else "NONE")
        return rel, (top[:600] or "(no extractable overlap with target)")

    def _read_and_brief(self, queries, metadata) -> List[Dict[str, Any]]:
        """For each query's top paper: resolve OA -> download -> extract -> read.
        Returns brief records for the shadow log. Bounded + best-effort; never raises."""
        briefs, fetches, reads = [], 0, 0
        for q, mres in zip(queries, metadata):
            target = q.get("target", "")
            papers = (mres.get("papers", []) or []) if isinstance(mres, dict) else []
            if not papers:
                continue
            paper = papers[0]
            rec = {"target": target, "source_ref": paper.get("url", ""),
                   "title": paper.get("title", ""), "via": "abstract_only",
                   "fulltext_chars": 0, "source_hash": "", "relevance": "",
                   "brief": "", "reader_model": "", "raw_reader_response": "",
                   "elapsed_s": 0.0, "error": ""}
            body = ""
            # One paper's failure must degrade to THAT paper's error field, never lose the
            # round's other briefs. (Belt-and-braces: _download_and_extract/_cheap_reader_read
            # are already non-raising, but this keeps the per-paper contract even if that changes.)
            try:
                if self.enable_fulltext and fetches < self.MAX_FULLTEXT_FETCHES_PER_ROUND:
                    res = self.resolve_fulltext_url(paper)
                    if res["url"]:
                        fetches += 1
                        dl = self._download_and_extract(res["url"])
                        if dl["chars"]:
                            body = dl["text"]
                            rec["via"] = res["via"]
                            rec["fulltext_chars"] = dl["chars"]
                            rec["source_ref"] = res["source_ref"] or rec["source_ref"]
                            rec["source_hash"] = hashlib.sha256(
                                body.encode("utf-8", "ignore")).hexdigest()
                        else:
                            rec["error"] = f"fetch:{dl['error']}"
                if reads < self.MAX_READER_CALLS_PER_ROUND:
                    reads += 1
                    r = self._cheap_reader_read(target, paper, body)
                    rec.update({k: r[k] for k in
                                ("relevance", "brief", "reader_model", "elapsed_s")})
                    rec["raw_reader_response"] = r["raw"]
                    if r["error"]:
                        rec["error"] = (rec["error"] + "; " + r["error"]).strip("; ")
            except Exception as e:  # noqa: BLE001 — per-paper best-effort, never fatal
                rec["error"] = (rec["error"] + f"; paper:{type(e).__name__}").strip("; ")
            briefs.append(rec)
        return briefs

    def _generate_candidates(
        self,
        targets: List[str],
        metadata: List[Dict[str, Any]],
        round_idx: int,
        briefs: Optional[List[Dict[str, Any]]] = None,
    ) -> List[OuroborosCandidateClaim]:
        """Build candidate claims from REAL briefs (was a placeholder before 2026-07-12).

        Each candidate's description is the distilled librarian brief, not a synthetic
        stub; provenance carries the cited source_ref, content hash, and a real
        source_diversity (1.0 iff full text was actually parsed). Falls back to nothing
        when no relevant brief exists — it never re-emits the old placeholder string.
        """
        briefs = briefs or []
        candidates: List[OuroborosCandidateClaim] = []
        rel_map = {"HIGH": 0.9, "MEDIUM": 0.6, "LOW": 0.3}
        for rec in briefs[: self.MAX_CANDIDATE_CLAIMS]:
            if rec.get("relevance") in ("", "NONE"):
                continue
            provenance = ProvenancePacket(
                origin_type="external_ouroboros",
                source_ref=rec.get("source_ref", ""),
                retrieval_query=self._target_to_query(rec.get("target", "")),
                retrieved_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                source_hash=rec.get("source_hash", ""),
                source_diversity=1.0 if rec.get("fulltext_chars", 0) else 0.0,
            )
            candidates.append(OuroborosCandidateClaim(
                claim_id=self._next_claim_id(),
                description=(rec.get("brief") or "")[:800],
                provenance=provenance,
                relevance_score=rel_map.get(rec.get("relevance", "LOW"), 0.3),
                falsification_debt="high",
                round_observed=round_idx,
            ))
        return candidates

    def get_activity_metrics(self) -> Dict[str, Any]:
        """Return activity metrics for Macrophage monitoring.

        The Macrophage monitors these metrics to detect Ouroboros
        pathologies (source monoculture, excessive querying, etc.).
        """
        if not self._round_logs:
            return {
                "queries_total": 0,
                "claims_proposed_total": 0,
                "rounds_active": 0,
                "diversity_score": 1.0,
            }

        total_queries = sum(len(log.queries_issued) for log in self._round_logs)
        total_claims = sum(len(log.candidate_claims) for log in self._round_logs)

        # Compute source diversity across all queries
        all_sources = []
        for log in self._round_logs:
            for q in log.queries_issued:
                all_sources.append(q.get("source", "unknown"))

        if all_sources:
            unique = len(set(all_sources))
            diversity = unique / len(all_sources)
        else:
            diversity = 1.0

        return {
            "queries_total": total_queries,
            "claims_proposed_total": total_claims,
            "rounds_active": len(self._round_logs),
            "diversity_score": diversity,
            "queries_this_round": (
                len(self._round_logs[-1].queries_issued) if self._round_logs else 0
            ),
            "claims_this_round": (
                len(self._round_logs[-1].candidate_claims) if self._round_logs else 0
            ),
        }

    def sign_shadow_log(
        self,
        shadow_log: OuroborosShadowLog,
        chain: Any,  # VerificationChain
    ) -> Optional[dict]:
        """Sign a shadow log entry into the verification chain.

        L1 (provenance): proves this research cycle was executed at this
        time by the Ouroboros. L2/L3 operate downstream.

        Returns the chain record, or None if signing fails.
        """
        try:
            record = chain.append_record(
                artifact_type="ouroboros_shadow_log",
                payload=shadow_log.to_dict(),
                recorded_by="ouroboros_o1",
                metadata={
                    "shadow": self.shadow,
                    "round_idx": shadow_log.round_idx,
                    "would_have_injected": shadow_log.would_have_injected,
                },
            )
            return record
        except Exception as exc:
            logger.warning("Failed to sign shadow log for round %d: %s",
                          shadow_log.round_idx, exc)
            return None


# ─────────────────────────────────────────────────────────────────────────────
# Loop-close: brief -> round prompt  (2026-07-31)
# ─────────────────────────────────────────────────────────────────────────────
#
# Everything above this line produces a brief and stops. `run_between_rounds`
# retrieves, downloads, parses and distils real papers, and `_generate_candidates`
# turns the distillation into candidate claims — but nothing consumed either.
# RECOVERY.md recorded the state precisely: "strictly shadow — never reaches a
# prompt/c_ext/gamma".
#
# `build_brief_prompt_section` is the missing consumer. It renders the briefs of
# round K into a delimited prompt block for round K+1 (the one-round lag is the
# original between-round design, decision 1 in the module docstring). It is a
# pure function of the brief records: no network, no model call, no global state,
# so a test can assert on its exact output and the runner can diff ON/OFF.
#
# Design decision 2 (disjoint evidence paths) is carried INTO the prompt: the
# block tells the panel that a retrieved paper is an external claim which must be
# verified by a different method, never cited as its own proof.

_BRIEF_BEGIN = "=== EXTERNAL RESEARCH (Ouroboros O1 — retrieved literature) ==="
_BRIEF_END = "=== END EXTERNAL RESEARCH ==="

_RELEVANCE_RANK = {"NONE": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3}


def build_brief_prompt_section(
    briefs: List[Dict[str, Any]],
    round_idx: int,
    *,
    max_chars: int = 4000,
    min_relevance: str = "LOW",
    require_model_reader: bool = True,
) -> str:
    """Render round ``round_idx`` briefs as a prompt block for round ``round_idx+1``.

    Returns ``""`` when there is nothing worth injecting — no briefs, none at or
    above ``min_relevance``, or every candidate empty. An empty return is the
    signal the caller uses to leave the prompt untouched, so the OFF path and the
    "on but nothing retrieved" path are the same bytes.

    Args:
        briefs: brief records from ``OuroborosShadowLog.briefs``.
        round_idx: the round the retrieval observed (labelled in the header).
        max_chars: hard ceiling on the rendered block.
        min_relevance: lowest librarian relevance admitted (NONE|LOW|MEDIUM|HIGH).
        require_model_reader: drop briefs whose relevance was scored by the
            no-LLM extractive fallback rather than a librarian model. Default
            True, and it is doing real work: the fallback scores MEDIUM on any
            three-word overlap, and in the first live proof run it rated
            "Overcoming Catastrophic Forgetting by XAI" MEDIUM against a
            floating-point-cancellation finding, purely on the word
            "catastrophic". A reachable librarian correctly rates such a paper
            NONE (see the Exp 45 shadow logs, where Haiku rated an unrelated
            robotics paper NONE). So when no librarian is reachable the block
            degrades to empty — the pre-31-July behaviour — instead of handing
            the panel literature that is not about its problem.

    Deterministic: same input, same bytes. No network, no clock, no RNG.
    """
    floor = _RELEVANCE_RANK.get((min_relevance or "LOW").upper(), 1)
    admitted = []
    # Two panel models filing the same defect give the Ouroboros two identical
    # targets, which resolve to the same paper — caught in the first live proof
    # run, where the block listed one arXiv paper twice as [1] and [2]. Dedupe
    # on the content hash (falling back to the citation) so the block never
    # inflates its own coverage.
    seen: set = set()
    for rec in briefs or []:
        if not isinstance(rec, dict):
            continue
        rel = (rec.get("relevance") or "").upper()
        if _RELEVANCE_RANK.get(rel, 0) < max(floor, 1):
            continue
        if not (rec.get("brief") or "").strip():
            continue
        if require_model_reader and (
                rec.get("reader_model") or "") in ("", "extractive_fallback"):
            continue
        key = rec.get("source_hash") or rec.get("source_ref") or rec.get("title")
        if key in seen:
            continue
        seen.add(key)
        admitted.append(rec)

    if not admitted:
        return ""

    # Strongest relevance first, stable within a band (retrieval order).
    admitted.sort(key=lambda r: -_RELEVANCE_RANK.get(
        (r.get("relevance") or "").upper(), 0))

    head = (
        f"{_BRIEF_BEGIN}\n"
        f"Retrieved after round {round_idx} by the Ouroboros cell from the "
        f"open-access literature, in response to what that round left "
        f"unresolved. This is EXTERNAL EVIDENCE, not a finding.\n\n"
        f"HOW TO USE IT (CDSFL disjoint-evidence rule): a paper may point you at "
        f"a mechanism, a failure mode, or a bound. It may NOT serve as its own "
        f"verification. If you file a finding that rests on one of these papers, "
        f"verify it by a different route — computation, execution, or a strictly "
        f"different data source — and cite the source_ref below in your "
        f"NOVELTY section.\n\n"
    )
    tail = f"{_BRIEF_END}\n\n"
    budget = max_chars - len(head) - len(tail)
    if budget <= 0:
        return ""

    blocks: List[str] = []
    used = 0
    for i, rec in enumerate(admitted, start=1):
        via = rec.get("via") or "unknown"
        chars = int(rec.get("fulltext_chars") or 0)
        provenance = (
            f"full text parsed, {chars:,} chars, sha256 "
            f"{(rec.get('source_hash') or '')[:16]}"
            if chars else "abstract only (no open-access full text resolved)"
        )
        # Finding text carries newlines; collapsing whitespace keeps one field
        # per line so the block cannot be misread as prompt structure.
        target_1l = ' '.join((rec.get('target') or '').split())[:160]
        # WHO judged the relevance is part of the evidence. "extractive_fallback"
        # means no librarian model was reachable and the score came from a word
        # -overlap heuristic, which over-rates (it scored an unrelated paper
        # MEDIUM in the proof run). The panel should see that, not guess it.
        reader = rec.get('reader_model') or 'unknown'
        block = (
            f"[{i}] {(rec.get('title') or '(untitled)')[:200]}\n"
            f"    source_ref: {rec.get('source_ref') or '(none)'}\n"
            f"    retrieval: {via} — {provenance}\n"
            f"    relevance to \"{target_1l}\": "
            f"{(rec.get('relevance') or '').upper()} (judged by {reader})\n"
            f"    brief: {' '.join((rec.get('brief') or '').split())}\n\n"
        )
        if used + len(block) > budget:
            # Truncate the last admitted brief rather than dropping it silently,
            # so the block never claims coverage it did not deliver.
            room = budget - used
            if room > 200:
                blocks.append(block[:room - 20].rstrip() + "\n    [truncated]\n\n")
            break
        blocks.append(block)
        used += len(block)

    if not blocks:
        return ""
    return head + "".join(blocks) + tail
