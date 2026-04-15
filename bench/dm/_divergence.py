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
  / tradeoff).
* **Structure B** — Primary solution + a scoped null-alternative
  justification (analogous to anti-deference `null_find_requires_scoped_
  justification`).

This module parses the raw model output for alternative / null-justification
blocks, validates them against the directive, scores cosmetic-isomorphism
(Jaccard over token sets; embedding backend deferred), and exposes a
penalty multiplier that the R_k pipeline can apply at the finding level.

Design notes:

* MVP uses Jaccard similarity over normalised token sets — deterministic,
  fast, no model dependency. Swapping in sentence-transformer embeddings
  is a follow-up and will use the shared similarity backend (§Phase 2 of
  the Exp 39 plan).
* No schema math changes. No change to R_k(i) structure. The penalty
  multiplier is a pre-factor applied to the contribution of a finding
  that violates the directive.
* Validator is permissive on parse (many header styles accepted) and
  strict on semantics (dimension must be one of the five allowed; isomorphism
  threshold is enforced; null-justification must meet minimum length).
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
    """

    enabled: bool = True
    min_alternatives: int = 1
    max_chars_per_alternative: int = 2000
    mode: str = "imperative"  # "imperative" | "advisory"
    isomorphism_threshold: float = 0.85
    null_justification_min_chars: int = 60


# ─────────────────────────────────────────────────────────────────────────────
# Data carriers
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class AlternativeRecord:
    """Parsed and validated alternative block for a single finding.

    Produced by :func:`parse_alternative_block` and consumed by the R_k
    pipeline for divergence-penalty application. Failure modes are encoded
    in ``admissible`` + ``rejection_reasons`` rather than exceptions — a
    malformed alternative is never fatal, only penalised.
    """

    primary_finding_id: str
    alternative_text: str
    dimension: Optional[str]  # None = missing / unparseable
    isomorphism_score: float = 0.0  # Jaccard vs primary; 0.0 = orthogonal
    admissible: bool = False
    rejection_reasons: List[str] = field(default_factory=list)


@dataclass
class DivergenceRecord:
    """Per-finding divergence audit for one round.

    Collected by :func:`build_divergence_records`; the aggregate outcome
    ``compliant`` governs whether the divergence penalty is applied.
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
    Kept deliberately simple — we are detecting *cosmetic rewording*, not
    doing paraphrase detection.
    """
    tokens = _WORD_RE.findall(text.lower())
    return {t for t in tokens if t not in _STOPWORDS and len(t) >= 2}


def score_isomorphism(primary: str, alternative: str) -> float:
    """Jaccard similarity between primary and alternative token sets.

    Returns in [0.0, 1.0]. 0.0 means disjoint vocabulary; 1.0 means identical
    after stopword removal. The intended interpretation is *lexical overlap*
    — a high score flags a likely surface-level rewording, not a semantic
    duplicate per se.
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


def parse_alternative_block(
    text: str,
    primary_finding_id: str,
    primary_text: str,
    config: Optional[DivergenceConfig] = None,
) -> List[AlternativeRecord]:
    """Extract alternative blocks from raw model output for one finding.

    Accepts several header forms (see ``_ALT_HEADER_RE``). For each
    alternative found, attempts to resolve its declared dimension from
    inline tag, follow-up ``Dimension:`` line, or marks it missing. Computes
    Jaccard isomorphism vs ``primary_text`` and stores the result.

    Does not itself gate admissibility — see :func:`validate_alternative`.
    Returns ``[]`` if no alternative blocks found.
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
        score = score_isomorphism(primary_text, body)

        records.append(
            AlternativeRecord(
                primary_finding_id=primary_finding_id,
                alternative_text=body,
                dimension=dimension,
                isomorphism_score=score,
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

    * ``dimension`` is one of :data:`ALLOWED_DIMENSIONS`;
    * ``alternative_text`` is non-empty;
    * ``alternative_text`` is ≤ ``max_chars_per_alternative``;
    * ``isomorphism_score`` < ``isomorphism_threshold``.

    Reasons are accumulated so a failing alternative reports every failure,
    not just the first.
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

    admissible = not reasons
    alternative.admissible = admissible
    alternative.rejection_reasons = list(reasons)
    return admissible, reasons


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
) -> DivergenceRecord:
    """Assemble a DivergenceRecord for a single finding from raw model output.

    The record captures every alternative parsed (admissible or not), the
    optional null-justification, and a top-level ``compliant`` verdict the
    pipeline uses to decide whether to apply the divergence penalty.

    ``compliant`` is true iff:

    * at least ``min_alternatives`` alternatives pass :func:`validate_alternative`,
      **OR**
    * a valid null-justification is supplied per :func:`validate_null_justification`.

    When the directive is disabled, returns a compliant record with empty
    content so downstream code never needs to branch on the toggle.
    """
    if config is None:
        config = DivergenceConfig()

    record = DivergenceRecord(finding_id=finding_id)

    # Disabled: emit a compliant empty record. The pipeline treats this as
    # "divergence not required this round" and applies no penalty.
    if not config.enabled:
        record.compliant = True
        return record

    alternatives = parse_alternative_block(
        raw_output, finding_id, primary_text, config
    )
    for alt in alternatives:
        validate_alternative(alt, config)
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


def divergence_penalty_multiplier(
    record: DivergenceRecord,
    config: Optional[DivergenceConfig] = None,
) -> float:
    """Return a scalar in (0, 1] that scales a finding's contribution to R_k.

    Design:

    * Compliant finding → 1.0 (no penalty).
    * Non-compliant finding with at least one parsed-but-inadmissible
      alternative → 0.85 (soft penalty; the model engaged with the directive
      but failed the gate).
    * Non-compliant finding with neither alternative nor null-justification
      → 0.70 (hard penalty; the model ignored the directive entirely).
    * Isomorphic-only submission (alternatives present, all flagged cosmetic)
      → 0.60 (double penalty per §18 — treated as null submission *and*
      without the required justification).

    These multipliers are deliberately conservative in the MVP. The penalty
    exists to shift the equilibrium toward compliance; it is not meant to
    dominate R_k calculation. Final calibration depends on Exp 39 / Exp 40
    baselines.
    """
    if config is None:
        config = DivergenceConfig()
    if not config.enabled or record.compliant:
        return 1.0

    has_any_alt = bool(record.alternatives)
    has_null = record.null_justification is not None

    if has_any_alt:
        all_isomorphic = all(
            any(r.startswith("cosmetic_isomorphism") for r in a.rejection_reasons)
            for a in record.alternatives
        )
        if all_isomorphic:
            return 0.60
        return 0.85

    if has_null:
        # Null block supplied but failed validation (too short, etc.)
        return 0.85

    return 0.70


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
    )
