"""Divergence directive — Popper's bold-conjecture arm for CDSFL.

CDSFL's severe-tests arm (falsification pipeline, admissibility gates,
cross-model corroboration, §17 feedback channel) is highly developed. The
bold-conjectures arm has until now been implicit, inherited from whatever
the models happen to produce unprompted. This module operationalises the
missing arm.

Per `cdsfl_operational.md` §18, every non-trivial finding must supply
either:

* **Structure A** — Primary solution + ≥1 alternative differing from the
  primary on a named dimension (mechanism / assumption / scope / timescale
  / tradeoff). Every alternative MUST also declare a contrast statement
  naming explicitly how it differs from the primary on that dimension.
* **Structure B** — Primary solution + a scoped null-alternative
  justification (analogous to anti-deference `null_find_requires_scoped_
  justification`).

This module parses the raw model output for alternative / null-justification
blocks, validates them against the directive, scores lexical near-duplicate
similarity (Jaccard over token sets; embedding backend deferred), runs a
sibling alt-vs-alt admissibility check, and exposes a modulator that the
R_k pipeline applies to **η_int** — never to R_k directly.

─────────────────────────────────────────────────────────────────────────────
CHANNEL ASSIGNMENT — ORTHOGONALITY CONTRACT (round-2 5/5 unanimous)
─────────────────────────────────────────────────────────────────────────────
Stage 6 math has three semantic channels:

    R_k(i) — iterative residual-risk self-assessment   (pipeline outcome)
    ν_k    — literature-grounded novelty yield         (external signal)
    c_ext  — external-citation density                 (external signal)

The divergence modulator operates on **η_int** (internal novelty), which
flows into q via the η decomposition:

    η_combined = η_int · (1 − c_ext · (1 − ν_k))
    q          = η_combined · d · p
    R_k(i)     = R_k(i-1) · (1 − q) / (1 − q · R_k(i-1))

The modulator multiplies η_int only. It is forbidden from entering q_eff
as an independent pre-factor on R_k, and it is forbidden from counting
toward ν_k. The three channels are *assignment-orthogonal* — a divergence
penalty affects R_k through η_int → q → the recurrence, not as a direct
R_k multiplier. This is the channel-assignment invariant that all five
models converged on in round-2 review.

The continuous-suppression weight w(f) is a DIFFERENT construct. It lives
in kappa_set's numerator (weighted) with a raw denominator, and it is
EXCLUDED from q_eff (Corroboration Collapse fix, 12 April 2026). See
`bench/dm/_convergence.py` for w(f). Do not conflate w(f) with the
η_int modulator defined here — they act on different channels.
─────────────────────────────────────────────────────────────────────────────

Design notes:

* MVP uses Jaccard similarity over normalised token sets — deterministic,
  fast, no model dependency. The role is a **lexical near-duplicate
  heuristic**: high Jaccard flags surface-level rewording, not semantic
  equivalence. Swapping in sentence-transformer embeddings is a follow-up
  via the shared similarity backend (§Phase 2 of the Exp 39 plan).
* No schema math changes to R_k. The modulator multiplies η_int at the
  finding level and propagates through q into the recurrence.
* Validator is permissive on parse (many header styles accepted) and
  strict on semantics (dimension must be one of the five allowed;
  isomorphism threshold is enforced; contrast statement must be present
  and ≥min_contrast_chars; sibling alt-vs-alt isomorphism is a
  ship-blocker that flips the second-occurring alternative inadmissible).
* Disabled gracefully — all parse / validate functions return empty or
  neutral results when the directive is off; no pipeline mutation.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────


ALLOWED_DIMENSIONS: Tuple[str, ...] = (
    "mechanism",
    "assumption",
    "scope",
    "timescale",
    "tradeoff",
)
"""The five dimensions on which a valid alternative must differ from the primary.

Per §18. An alternative with no declared dimension, or a dimension outside this
set, is parsed as cosmetic and rejected.
"""


# Header regex — matches several common alternative-block formats models may
# produce. Accepts optional markdown emphasis, optional numbering, and either
# inline `(dimension: X)` / `[dim: X]` / `— dimension: X` tagging or a
# follow-up `Dimension:` line.
_ALT_HEADER_RE = re.compile(
    r"""
    ^\s*
    (?:\#{1,6}\s+|\*{1,2})?        # optional markdown heading / bold
    (?:alt(?:ernative)?|conjecture) # keyword
    \s*
    (?:\#?\s*\d+\s*)?              # optional index
    (?:[:\-—]\s*)?                 # optional separator
    (?P<tag>
        [\(\[]\s*(?:dim(?:ension)?|on)\s*[:=]\s*(?P<dim_inline>[a-zA-Z_-]+)\s*[\)\]]
        |
        [-—]\s*(?:dim(?:ension)?|on)\s*[:=]\s*(?P<dim_dash>[a-zA-Z_-]+)
    )?
    \s*
    (?:\*{1,2})?
    \s*$
    """,
    re.VERBOSE | re.IGNORECASE | re.MULTILINE,
)

# Dimension-on-own-line regex — matches `Dimension: mechanism` or similar
# immediately after a header when no inline tag was present.
_DIM_LINE_RE = re.compile(
    r"""
    ^\s*
    (?:\*{1,2})?
    (?:dim(?:ension)?|differs\s+on)
    \s*[:=]\s*
    (?P<dim>[a-zA-Z_-]+)
    \s*
    (?:\*{1,2})?
    \s*$
    """,
    re.VERBOSE | re.IGNORECASE | re.MULTILINE,
)

# Contrast-statement regex — matches an explicit "differs from primary" /
# "contrast" / "in contrast" line naming how the alternative departs from
# the primary on the declared dimension. This is the round-2 ship-blocker:
# without a contrast statement, an alternative is inadmissible even if its
# Jaccard is low and the dimension is valid.
_CONTRAST_RE = re.compile(
    r"""
    ^\s*
    (?:\*{1,2})?
    (?:
        differs?\s+from\s+primary        # "differs from primary"
        | contrast(?:s)?(?:\s+with\s+primary)?  # "contrast" / "contrasts with primary"
        | in\s+contrast(?:\s+to\s+primary)?     # "in contrast" / "in contrast to primary"
        | departs?\s+from\s+primary      # "departs from primary"
        | vs\.?\s+primary                # "vs primary" / "vs. primary"
    )
    \s*[:\-—]\s*
    (?P<contrast>.+?)
    \s*
    (?:\*{1,2})?
    \s*$
    """,
    re.VERBOSE | re.IGNORECASE | re.MULTILINE,
)

# Null-justification block header — flexible phrasing accepted.
_NULL_HEADER_RE = re.compile(
    r"""
    ^\s*
    (?:\#{1,6}\s+|\*{1,2})?
    (?:no[-_\s]alternative(?:\s+found)?
       |null[-_\s]alternative
       |no[-_\s]distinct[-_\s]alternative
       |alternative[-_\s]search[-_\s]result
    )
    \s*[:\-—]?\s*
    (?:\*{1,2})?
    \s*$
    """,
    re.VERBOSE | re.IGNORECASE | re.MULTILINE,
)

# Minimal English stopword list for Jaccard normalisation. Keep small — we
# want to preserve semantic content and filter only pure function words.
_STOPWORDS = frozenset({
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
    "has", "have", "he", "in", "is", "it", "its", "of", "on", "or",
    "that", "the", "to", "was", "were", "will", "with", "this", "these",
    "those", "which", "but", "not", "no", "if", "then", "than", "so",
    "can", "may", "might", "would", "could", "should", "we", "us", "our",
    "i", "you", "your", "they", "them", "their",
})

_WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9_\-']*")


# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class DivergenceConfig:
    """Runtime configuration for the divergence directive.

    Mirrors the `[divergence]` block in `bench/cdsfl_registry/universal.toml`
    and is schema-validated by the policy engine.

    Round-2 additions:

    * ``min_contrast_chars`` — minimum character length of the mandatory
      contrast statement attached to each alternative.
    * ``near_copy_threshold`` — Jaccard at or above this is treated as a
      near-copy and triggers the severe η_int modulator tier (0.60).
    * ``sibling_isomorphism_threshold`` — Jaccard between two sibling
      alternatives for the same finding at or above this marks the
      later-occurring sibling inadmissible (alt-vs-alt ship-blocker).
    """

    enabled: bool = True
    min_alternatives: int = 1
    max_chars_per_alternative: int = 2000
    mode: str = "imperative"  # "imperative" | "advisory"
    isomorphism_threshold: float = 0.85
    null_justification_min_chars: int = 60
    # Round-2 additions
    min_contrast_chars: int = 20
    near_copy_threshold: float = 0.98
    sibling_isomorphism_threshold: float = 0.85


# ─────────────────────────────────────────────────────────────────────────────
# Data carriers
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class AlternativeRecord:
    """Parsed and validated alternative block for a single finding.

    Produced by :func:`parse_alternative_block` and consumed by the R_k
    pipeline for η_int modulation. Failure modes are encoded in
    ``admissible`` + ``rejection_reasons`` rather than exceptions — a
    malformed alternative is never fatal, only penalised.

    Round-2 additions:

    * ``contrast_statement`` — parsed "differs from primary on X in that
      Y" clause; ``None`` if absent.
    * ``sibling_max_isomorphism`` — highest Jaccard score observed
      against any earlier-indexed sibling alternative for the same
      finding. ``0.0`` if this is the first alternative.
    * ``admissibility_gate_passed`` — composite flag true iff this
      alternative survived the primary-isomorphism gate AND the
      sibling-isomorphism gate AND the contrast-statement gate. This is
      the round-2 ship-blocker aggregate; ``admissible`` mirrors it for
      backward compatibility with existing callers.

    Exp 40 fix 1E.9 (cross-round recidivism):

    * ``prior_round_isomorphism`` — highest Jaccard observed against any
      alternative supplied by the same finding's prior rounds. ``0.0`` if
      no prior-round alternatives were passed to the check. At or above
      ``near_copy_threshold`` this flips ``admissible`` False and
      triggers the severe 0.60 tier in :func:`eta_int_modulator`.
    """

    primary_finding_id: str
    alternative_text: str
    dimension: Optional[str]  # None = missing / unparseable
    isomorphism_score: float = 0.0  # Jaccard vs primary; 0.0 = orthogonal
    admissible: bool = False
    rejection_reasons: List[str] = field(default_factory=list)
    # Round-2 additions
    contrast_statement: Optional[str] = None
    sibling_max_isomorphism: float = 0.0
    admissibility_gate_passed: bool = False
    # Exp 40 1E.9: cross-round recidivism
    prior_round_isomorphism: float = 0.0


@dataclass
class DivergenceRecord:
    """Per-finding divergence audit for one round.

    Collected by :func:`build_divergence_records`; the aggregate outcome
    ``compliant`` governs whether the η_int modulator is applied.
    """

    finding_id: str
    alternatives: List[AlternativeRecord] = field(default_factory=list)
    null_justification: Optional[str] = None  # populated iff structure B used
    compliant: bool = False
    failure_reasons: List[str] = field(default_factory=list)


# ─────────────────────────────────────────────────────────────────────────────
# Tokenisation and similarity
# ─────────────────────────────────────────────────────────────────────────────


def _tokenise(text: str) -> set:
    """Normalise text to a lower-case token set for Jaccard comparison.

    Drops stopwords, numbers-only tokens, and tokens shorter than two chars.
    Kept deliberately simple — we are running a *lexical near-duplicate
    heuristic*, not paraphrase detection.
    """
    tokens = _WORD_RE.findall(text.lower())
    return {t for t in tokens if t not in _STOPWORDS and len(t) >= 2}


def _recidivism_text(record: "AlternativeRecord") -> str:
    """Full-submission text for cross-round recidivism comparison.

    ``alternative_text`` has the contrast statement stripped (so meta-text
    does not inflate the primary-isomorphism gate). Cross-round recidivism,
    however, is about whether the *whole submission* was resubmitted, and the
    contrast statement is part of that submission. Fold it back in so that a
    model which supplies a previously-missing (or materially changed) contrast
    statement is not mis-scored as a verbatim near-copy of the prior round.
    """
    body = getattr(record, "alternative_text", "") or ""
    contrast = getattr(record, "contrast_statement", "") or ""
    if contrast:
        return f"{body} {contrast}".strip()
    return body


def score_isomorphism(primary: str, alternative: str) -> float:
    """Jaccard similarity between primary and alternative token sets.

    Returns in [0.0, 1.0]. 0.0 means disjoint vocabulary; 1.0 means identical
    after stopword removal. The intended interpretation is **lexical
    near-duplicate heuristic** — a high score flags likely surface-level
    rewording, not a semantic duplicate per se. Embedding-based similarity
    (sentence-transformer backend) is the follow-up replacement.
    """
    a = _tokenise(primary)
    b = _tokenise(alternative)
    if not a and not b:
        return 1.0  # two empty strings are trivially identical
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


# ─────────────────────────────────────────────────────────────────────────────
# Parsers
# ─────────────────────────────────────────────────────────────────────────────


def _normalise_dimension(raw: Optional[str]) -> Optional[str]:
    """Map a parsed dimension token to the canonical ALLOWED_DIMENSIONS entry.

    Returns ``None`` if the raw token doesn't map. Hyphens and underscores
    are treated as equivalent; case is ignored.
    """
    if raw is None:
        return None
    cleaned = raw.strip().lower().replace("-", "").replace("_", "")
    # Accept common variants: "trade-off" → "tradeoff", "time-scale" →
    # "timescale", "assumptions" → "assumption", etc.
    synonyms = {
        "mechanisms": "mechanism",
        "mechanistic": "mechanism",
        "assumptions": "assumption",
        "premise": "assumption",
        "premises": "assumption",
        "scopes": "scope",
        "applicability": "scope",
        "regime": "scope",
        "timescales": "timescale",
        "temporal": "timescale",
        "horizon": "timescale",
        "tradeoffs": "tradeoff",
        "trade": "tradeoff",
    }
    canonical = synonyms.get(cleaned, cleaned)
    return canonical if canonical in ALLOWED_DIMENSIONS else None


def parse_contrast_statement(body: str) -> Tuple[Optional[str], str]:
    """Extract a single-line contrast statement from an alternative body.

    Looks for a line matching :data:`_CONTRAST_RE` and returns
    ``(statement, body_without_contrast_line)``. If no contrast line is
    present returns ``(None, body)``. Only the first match is consumed so
    models may include prose discussion of the contrast further in the
    body without it being double-counted in isomorphism scoring.
    """
    if not body:
        return None, body
    m = _CONTRAST_RE.search(body)
    if not m:
        return None, body
    statement = m.group("contrast").strip()
    # Remove the matched contrast line from the body so it doesn't inflate
    # Jaccard against the primary (the contrast line is meta, not primary
    # claim text).
    body_stripped = (body[: m.start()] + body[m.end():]).strip()
    return statement or None, body_stripped


def parse_alternative_block(
    text: str,
    primary_finding_id: str,
    primary_text: str,
    config: Optional[DivergenceConfig] = None,
) -> List[AlternativeRecord]:
    """Extract alternative blocks from raw model output for one finding.

    Accepts several header forms (see ``_ALT_HEADER_RE``). For each
    alternative found, attempts to resolve its declared dimension from
    inline tag, follow-up ``Dimension:`` line, or marks it missing. Parses
    the mandatory contrast statement (round-2 requirement). Computes
    Jaccard isomorphism vs ``primary_text`` and stores the result.

    Does not itself gate admissibility — see :func:`validate_alternative`
    and :func:`check_sibling_admissibility`. Returns ``[]`` if no
    alternative blocks found.
    """
    if config is None:
        config = DivergenceConfig()
    if not text:
        return []

    # Find all header matches with their span so we can slice alternative
    # bodies out between consecutive headers.
    matches = list(_ALT_HEADER_RE.finditer(text))
    if not matches:
        return []

    records: List[AlternativeRecord] = []
    for i, m in enumerate(matches):
        body_start = m.end()
        body_end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[body_start:body_end].strip()

        # Resolve dimension: inline tag takes precedence, else look for a
        # Dimension: line at the start of the body.
        dim_raw = m.group("dim_inline") or m.group("dim_dash")
        if dim_raw is None:
            dim_line_match = _DIM_LINE_RE.match(body)
            if dim_line_match:
                dim_raw = dim_line_match.group("dim")
                # Strip the consumed Dimension: line from the body so it
                # isn't double-counted in the isomorphism calculation.
                body = body[dim_line_match.end():].strip()

        dimension = _normalise_dimension(dim_raw)

        # Parse contrast statement (round-2). Consume it from the body so
        # it doesn't inflate Jaccard against the primary.
        contrast, body_without_contrast = parse_contrast_statement(body)

        score = score_isomorphism(primary_text, body_without_contrast)

        records.append(
            AlternativeRecord(
                primary_finding_id=primary_finding_id,
                alternative_text=body_without_contrast,
                dimension=dimension,
                isomorphism_score=score,
                contrast_statement=contrast,
            )
        )

    return records


def parse_null_justification_block(text: str) -> Optional[str]:
    """Extract a scoped null-alternative justification block from raw text.

    Matches a header of the form ``No alternative found``, ``Null
    alternative``, etc. and returns the following prose block trimmed.
    Returns ``None`` if no block header is present or the block is empty.
    """
    if not text:
        return None
    m = _NULL_HEADER_RE.search(text)
    if not m:
        return None

    body_start = m.end()
    # Terminate at the next markdown heading, rule, or end-of-text — the
    # justification block should be a contiguous prose chunk.
    terminator = re.search(
        r"\n(?:\#{1,6}\s|\-{3,}|\*{3,}|\={3,})",
        text[body_start:],
    )
    body_end = body_start + terminator.start() if terminator else len(text)
    body = text[body_start:body_end].strip()
    return body if body else None


# ─────────────────────────────────────────────────────────────────────────────
# Validation
# ─────────────────────────────────────────────────────────────────────────────


def validate_alternative(
    alternative: AlternativeRecord,
    config: Optional[DivergenceConfig] = None,
) -> Tuple[bool, List[str]]:
    """Gate an alternative against the directive. Returns (admissible, reasons).

    An alternative is admissible iff all of:

    * ``alternative_text`` is non-empty;
    * ``alternative_text`` is ≤ ``max_chars_per_alternative``;
    * ``dimension`` is one of :data:`ALLOWED_DIMENSIONS`;
    * ``isomorphism_score`` < ``isomorphism_threshold`` (lexical
      near-duplicate heuristic against the primary);
    * ``contrast_statement`` is present and ≥ ``min_contrast_chars``
      (round-2: every alternative must explicitly name how it differs
      from the primary on the declared dimension).

    Reasons are accumulated so a failing alternative reports every failure,
    not just the first. Sibling alt-vs-alt isomorphism is checked
    separately in :func:`check_sibling_admissibility` so this function
    stays pairwise primary-vs-alt.
    """
    if config is None:
        config = DivergenceConfig()
    reasons: List[str] = []

    if not alternative.alternative_text:
        reasons.append("empty_alternative_body")
    elif len(alternative.alternative_text) > config.max_chars_per_alternative:
        reasons.append(
            f"exceeds_max_chars ({len(alternative.alternative_text)} > "
            f"{config.max_chars_per_alternative})"
        )

    if alternative.dimension is None:
        reasons.append("missing_or_invalid_dimension")

    if alternative.isomorphism_score >= config.isomorphism_threshold:
        reasons.append(
            f"cosmetic_isomorphism (jaccard={alternative.isomorphism_score:.3f} "
            f">= {config.isomorphism_threshold})"
        )

    # Round-2: mandatory contrast statement
    if alternative.contrast_statement is None:
        reasons.append("missing_contrast_statement")
    elif len(alternative.contrast_statement.strip()) < config.min_contrast_chars:
        reasons.append(
            f"contrast_statement_too_short ({len(alternative.contrast_statement.strip())} < "
            f"{config.min_contrast_chars})"
        )

    admissible = not reasons
    alternative.admissible = admissible
    alternative.rejection_reasons = list(reasons)
    # admissibility_gate_passed is only flipped true by the full gate in
    # build_divergence_record (after sibling check); this function alone
    # cannot grant it.
    return admissible, reasons


def check_sibling_admissibility(
    alternatives: List[AlternativeRecord],
    config: Optional[DivergenceConfig] = None,
    prior_round_alternatives: Optional[List[AlternativeRecord]] = None,
) -> None:
    """Run the sibling alt-vs-alt isomorphism check in place.

    Round-2 ship-blocker: when two alternatives for the same finding are
    lexically near-duplicates of each other (Jaccard ≥
    ``sibling_isomorphism_threshold``), the later-occurring sibling is
    flipped inadmissible. The earlier sibling stands — the penalty lands
    on redundant submission, not on genuine first divergence.

    Mutates each :class:`AlternativeRecord` in place:

    * ``sibling_max_isomorphism`` — filled with the highest sibling
      Jaccard observed against any earlier-indexed alternative.
    * ``admissible`` — flipped to False if the sibling check fails, and
      a ``sibling_cosmetic_isomorphism`` reason is appended.
    * ``admissibility_gate_passed`` — set True iff ``admissible`` is
      still True after this pass (composite gate aggregate).

    Preserves ordering: the first alternative always keeps its existing
    admissibility; only alternatives at index ≥ 1 can be demoted by this
    check.

    Exp 40 fix 1E.9 (cross-round recidivism): when
    ``prior_round_alternatives`` is provided, each current alternative is
    also scored against every prior-round alternative for the same
    finding. The highest Jaccard is written into
    ``prior_round_isomorphism``. At or above ``near_copy_threshold``
    (default 0.98) the alternative is demoted to inadmissible and a
    ``recidivism_near_copy`` rejection reason is appended. The same
    severity tier fires in :func:`eta_int_modulator`.
    """
    if config is None:
        config = DivergenceConfig()
    if not alternatives:
        return

    for i, alt in enumerate(alternatives):
        max_sib = 0.0
        worst_sibling_idx: Optional[int] = None
        for j in range(i):
            sib = alternatives[j]
            sib_iso = score_isomorphism(sib.alternative_text, alt.alternative_text)
            if sib_iso > max_sib:
                max_sib = sib_iso
                worst_sibling_idx = j
        alt.sibling_max_isomorphism = max_sib

        if max_sib >= config.sibling_isomorphism_threshold:
            # Ship-blocker: flip inadmissible if it survived primary gate.
            reason = (
                f"sibling_cosmetic_isomorphism "
                f"(jaccard_vs_alt_{worst_sibling_idx}={max_sib:.3f} "
                f">= {config.sibling_isomorphism_threshold})"
            )
            if reason not in alt.rejection_reasons:
                alt.rejection_reasons.append(reason)
            alt.admissible = False

        # Exp 40 1E.9: cross-round recidivism check.
        if prior_round_alternatives:
            max_prior = 0.0
            worst_prior_idx: Optional[int] = None
            # Recidivism asks "did the model resubmit the same *submission*",
            # so the comparison must span the full submission — body plus its
            # contrast statement. The contrast is stripped from
            # ``alternative_text`` only to keep meta-text from inflating the
            # primary-Jaccard gate; excluding it here would make adding a
            # previously-missing contrast (the exact fix a contrast-rejected
            # alternative needs) invisible and mis-score a genuine fix as a
            # 1.0 near-copy. Fold the contrast back in for this comparison.
            cur_text = _recidivism_text(alt)
            for k, prior in enumerate(prior_round_alternatives):
                prior_text = _recidivism_text(prior)
                if not prior_text:
                    continue
                prior_iso = score_isomorphism(prior_text, cur_text)
                if prior_iso > max_prior:
                    max_prior = prior_iso
                    worst_prior_idx = k
            alt.prior_round_isomorphism = max_prior
            if max_prior >= config.near_copy_threshold:
                reason = (
                    f"recidivism_near_copy "
                    f"(jaccard_vs_prior_round_alt_{worst_prior_idx}="
                    f"{max_prior:.3f} >= {config.near_copy_threshold})"
                )
                if reason not in alt.rejection_reasons:
                    alt.rejection_reasons.append(reason)
                alt.admissible = False

        # Composite gate: passes all stages iff still admissible.
        alt.admissibility_gate_passed = alt.admissible


def validate_null_justification(
    justification: Optional[str],
    config: Optional[DivergenceConfig] = None,
) -> Tuple[bool, List[str]]:
    """Gate a null-alternative justification. Returns (admissible, reasons).

    A justification is admissible iff it exists and meets the minimum length
    threshold. Content quality (did the model actually enumerate the search
    space?) is deferred to HIL review and downstream analysis — we enforce
    the scoped-rationale floor here, not the scientific quality.
    """
    if config is None:
        config = DivergenceConfig()
    reasons: List[str] = []

    if justification is None or not justification.strip():
        reasons.append("missing_null_justification")
        return False, reasons

    cleaned = justification.strip()
    if len(cleaned) < config.null_justification_min_chars:
        reasons.append(
            f"null_justification_too_short ({len(cleaned)} < "
            f"{config.null_justification_min_chars})"
        )

    return not reasons, reasons


# ─────────────────────────────────────────────────────────────────────────────
# Pipeline integration
# ─────────────────────────────────────────────────────────────────────────────


def build_divergence_record(
    finding_id: str,
    primary_text: str,
    raw_output: str,
    config: Optional[DivergenceConfig] = None,
    prior_round_alternatives: Optional[List[AlternativeRecord]] = None,
) -> DivergenceRecord:
    """Assemble a DivergenceRecord for a single finding from raw model output.

    The record captures every alternative parsed (admissible or not), the
    optional null-justification, and a top-level ``compliant`` verdict the
    pipeline uses to decide whether to apply the η_int modulator.

    ``compliant`` is true iff:

    * at least ``min_alternatives`` alternatives pass
      :func:`validate_alternative` **AND** the sibling admissibility check,
      **OR**
    * a valid null-justification is supplied per
      :func:`validate_null_justification`.

    Round-2: sibling admissibility is now part of the compliance decision.
    An alternative that passes primary gates but duplicates an earlier
    sibling is demoted and does NOT count toward ``min_alternatives``.

    Exp 40 fix 1E.9: when ``prior_round_alternatives`` is provided, the
    sibling admissibility pass also checks for recidivism — alternatives
    that replicate a prior-round alternative unchanged incur the severe
    0.60 tier via :func:`eta_int_modulator`.

    When the directive is disabled, returns a compliant record with empty
    content so downstream code never needs to branch on the toggle.
    """
    if config is None:
        config = DivergenceConfig()

    record = DivergenceRecord(finding_id=finding_id)

    # Disabled: emit a compliant empty record. The pipeline treats this as
    # "divergence not required this round" and applies no modulation.
    if not config.enabled:
        record.compliant = True
        return record

    alternatives = parse_alternative_block(
        raw_output, finding_id, primary_text, config
    )
    for alt in alternatives:
        validate_alternative(alt, config)

    # Round-2 ship-blocker: sibling alt-vs-alt isomorphism check.
    # Exp 40 1E.9: sibling check also scans prior-round alternatives
    # for cross-round recidivism when they are supplied.
    check_sibling_admissibility(
        alternatives, config,
        prior_round_alternatives=prior_round_alternatives,
    )

    record.alternatives = alternatives

    null_block = parse_null_justification_block(raw_output)
    record.null_justification = null_block

    admissible_alts = [a for a in alternatives if a.admissible]
    has_enough_alts = len(admissible_alts) >= config.min_alternatives

    null_ok = False
    null_reasons: List[str] = []
    if null_block is not None:
        null_ok, null_reasons = validate_null_justification(null_block, config)

    record.compliant = has_enough_alts or null_ok

    if not record.compliant:
        if not alternatives and null_block is None:
            record.failure_reasons.append("no_alternative_or_null_block")
        else:
            if alternatives and not admissible_alts:
                # All alternatives present but none admissible — surface
                # aggregated reasons.
                for alt in alternatives:
                    for r in alt.rejection_reasons:
                        tag = f"{alt.primary_finding_id}:{r}"
                        if tag not in record.failure_reasons:
                            record.failure_reasons.append(tag)
            if alternatives and len(admissible_alts) < config.min_alternatives:
                record.failure_reasons.append(
                    f"insufficient_admissible_alternatives "
                    f"({len(admissible_alts)} < {config.min_alternatives})"
                )
            if null_block is not None and not null_ok:
                record.failure_reasons.extend(
                    f"null:{r}" for r in null_reasons
                )

    return record


def eta_int_modulator(
    record: DivergenceRecord,
    config: Optional[DivergenceConfig] = None,
) -> float:
    """Return a scalar in (0, 1] that modulates **η_int** for a finding.

    Channel contract (round-2 5/5 unanimous): this scalar multiplies the
    internal-novelty channel η_int; it does NOT pre-multiply R_k, it does
    NOT enter q as an independent factor, and it does NOT count toward ν_k.
    The modulator's effect on R_k flows exclusively through:

        η_int_modulated = m · η_int
        η_combined      = η_int_modulated · (1 − c_ext · (1 − ν_k))
        q               = η_combined · d · p
        R_k(i)          = R_k(i-1) · (1 − q) / (1 − q · R_k(i-1))

    Tier design (four levels; severe 0.60 reserved for near-copy or
    recidivism):

    * Compliant finding → 1.0 (no modulation).
    * Non-compliant finding with at least one parsed-but-inadmissible
      alternative (missing contrast, missing dimension, sibling duplicate,
      etc., where isomorphism stayed below the near-copy threshold) → 0.85
      (soft modulation; the model engaged with the directive but failed
      the gate).
    * Non-compliant finding with neither alternative nor null-justification
      → 0.70 (hard modulation; the model ignored the directive entirely).
    * Near-copy submission (at least one alternative with Jaccard ≥
      ``near_copy_threshold``, default 0.98) → 0.60 (severe; reserved for
      lexical near-duplicates and recidivism). Also applied when every
      alternative is cosmetically isomorphic (all flagged ≥ isomorphism
      threshold but < near-copy threshold → still treated as null
      submission without justification, which is the original §18 double
      penalty).

    The modulators are deliberately conservative in the MVP. They shift
    equilibrium toward compliance; they are not meant to dominate R_k.
    Final calibration depends on Exp 39 / Exp 40 baselines.

    Backward compatibility: the legacy name
    :func:`divergence_penalty_multiplier` is preserved as an alias below.
    """
    if config is None:
        config = DivergenceConfig()
    if not config.enabled or record.compliant:
        return 1.0

    has_any_alt = bool(record.alternatives)
    has_null = record.null_justification is not None

    if has_any_alt:
        # Severe tier 1: any alternative is a near-copy (lexical
        # near-duplicate at or above near_copy_threshold, default 0.98).
        # Exp 40 fix 1E.9: also fires on cross-round recidivism when the
        # current alternative replicates a prior-round alternative for
        # the same finding unchanged.
        any_near_copy = any(
            (a.isomorphism_score >= config.near_copy_threshold)
            or (a.prior_round_isomorphism >= config.near_copy_threshold)
            for a in record.alternatives
        )
        if any_near_copy:
            return 0.60

        # Severe tier 2: every alternative flagged cosmetic (at or above
        # isomorphism_threshold, default 0.85). This is the original §18
        # double-penalty case — null submission without justification.
        all_isomorphic = all(
            any(r.startswith("cosmetic_isomorphism") for r in a.rejection_reasons)
            for a in record.alternatives
        )
        if all_isomorphic:
            return 0.60

        # Soft tier: model engaged with the directive but failed some gate
        # (contrast, sibling, dimension, etc.).
        return 0.85

    if has_null:
        # Null block supplied but failed validation (too short, etc.)
        return 0.85

    # Hard tier: model ignored the directive entirely.
    return 0.70


# Backward-compatibility alias. Existing tests and call sites import
# `divergence_penalty_multiplier`; the round-2 rename relocates the
# function's semantic home onto η_int but keeps the old name working.
divergence_penalty_multiplier = eta_int_modulator


# ─────────────────────────────────────────────────────────────────────────────
# Config loading helper
# ─────────────────────────────────────────────────────────────────────────────


def divergence_config_from_dict(payload: Optional[Dict]) -> DivergenceConfig:
    """Build a DivergenceConfig from a parsed `[divergence]` TOML block.

    Unknown keys are ignored (schema-engine-validated upstream). Missing
    keys fall back to dataclass defaults. Returns a default-disabled config
    if ``payload`` is ``None`` or empty — callers that require the directive
    enabled must supply an explicit payload.
    """
    if not payload:
        return DivergenceConfig(enabled=False)

    defaults = DivergenceConfig()
    return DivergenceConfig(
        enabled=bool(payload.get("enabled", defaults.enabled)),
        min_alternatives=int(payload.get("min_alternatives", defaults.min_alternatives)),
        max_chars_per_alternative=int(
            payload.get("max_chars_per_alternative", defaults.max_chars_per_alternative)
        ),
        mode=str(payload.get("mode", defaults.mode)),
        isomorphism_threshold=float(
            payload.get("isomorphism_threshold", defaults.isomorphism_threshold)
        ),
        null_justification_min_chars=int(
            payload.get(
                "null_justification_min_chars", defaults.null_justification_min_chars
            )
        ),
        min_contrast_chars=int(
            payload.get("min_contrast_chars", defaults.min_contrast_chars)
        ),
        near_copy_threshold=float(
            payload.get("near_copy_threshold", defaults.near_copy_threshold)
        ),
        sibling_isomorphism_threshold=float(
            payload.get(
                "sibling_isomorphism_threshold", defaults.sibling_isomorphism_threshold
            )
        ),
    )
