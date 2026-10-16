"""
CDSFL Dynamic Directive Composer

Assembles per-dispatch directive sets from four layers + interaction overrides.
Pure function, deterministic, fail-loud. Canonical ordering:

    Universal → Domain (transformed by phenotype) → Phenotype → Situation

Coherence budget: constraint density (constraint count / token length) must
stay below a per-model threshold. When exceeded, SOFT constraints are pruned
in reverse priority order. HARD constraints are NEVER pruned.

Phenotype is a TRANSFORM OPERATOR, not an additive packet. It modifies how
domain and universal directives are rendered for a specific model (e.g.,
simplify language, strip examples, cap directive length).

Composition provenance: every composed directive set has a deterministic
CID (composition identity hash) for attribution in analysis.

Built from 5-model confer findings (31 March 2026). All solutions are
concrete resolutions of identified problems, not open questions.

Fixes applied from Composer Review Confer (31 March 2026, 2 rounds, 5 models):
  Problem 1: Universal minimal rendering for small-context models
  Problem 2: Intra-packet SOFT directive pruning
  Problem 3: Enhanced phenotype transform with dedup + header flattening
  Problem 4: Cross-layer conflict resolution
  Problem 5: Coherence threshold calibration from experiment data
  Problem 6: Orchestrator integration helpers
"""

from __future__ import annotations

import hashlib
import json
import re
import warnings
try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib  # Python < 3.11 fallback
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any


from .registry import (
    HARD_CONSTRAINTS,
    HARD_THRESHOLDS,
    HARD_STRINGS,
    REGISTRY_DIR,
    PolicyViolationError,
    _check_monotonicity,
    _deep_merge,
    _load_toml,
)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DIRECTIVES_DIR = Path(__file__).parent.parent / "directives"

# Per-model coherence budget: max constraint density (constraints / tokens).
# Conservative defaults. Calibrate from experiment data via
# calibrate_coherence_thresholds().
DEFAULT_COHERENCE_BUDGET = 0.015  # ~15 constraints per 1000 tokens
MODEL_COHERENCE_BUDGETS: dict[str, float] = {
    "opus_4_6": 0.020,       # handles dense instructions well
    "chatgpt_5_4": 0.015,    # moderate
    "codex_5_3": 0.012,      # needs tighter, simpler prompts
    "gemini_3_1_pro": 0.015, # moderate
    "deepseek_v3": 0.010,    # needs simplest prompts
}

# Phenotype transform rules per model. These modify HOW directives are
# rendered, not WHAT constraints are active. The phenotype layer is a
# transformation operator (functor), not an additive constraint set.
@dataclass
class PhenotypeTransform:
    """Transform rules for rendering directives for a specific model.

    ★ `max_directive_chars` BOUNDS WORK, NOT SPECIFICATION — founder's ruling,
    2026-10-14. His words: *"as far as any caps have ever existed, their
    intention was to never feed any model more work than they were demonstrably
    able to handle, especially for weaker models like Deepseek, and we built
    considerable machinery around this principle. There was never an intent as
    far as I recall to applying this same reasoning to the core operational
    directives themselves."* And: *"7000 or so words for a system prompt is
    hardly excessive for any modern model? Why should we need to cut it at all?"*

    So the 2 bounds are now SEPARATE FIELDS and they mean different things:

      * `max_directive_chars` — the WORK bound. It governs the domain and
        situation layers: the review target, the code extracts, the adversarial
        brief, the domain checklist. This is the quantity the harness measures
        per experiment and the quantity the routing ladder exists to respect.
        Values and behaviour are UNCHANGED.
      * `spec_chars` — the SPECIFICATION bound, and `None` means "deliver the
        project's own specification whole". Every model defaults to `None`,
        because no measurement has ever shown that any panel model cannot take
        3,991 words of specification, and the project gates its models on that
        specification. A model that genuinely cannot take it is given an
        explicit integer here, and then `_render_universal_minimal` is used --
        which, since 2026-10-15, carries EVERY HARD block rather than 0 of 22.

    Measured 2026-10-15 by `scripts/the_spec_is_not_work_2026-10-15.py`: with
    the bounds conflated, 5 of 5 models had a cap below the core specification
    (100.0000%, Wilson [56.5518%, 100.0000%]) so the reduced form was served
    unconditionally, and that reduced form carried 0 of 22 HARD blocks
    (0.0000%, Wilson [0.0000%, 14.8655%]) -- the 22 it dropped including the
    whole of "Falsifier Integrity -- Do Not Reach for the Answer".
    """
    max_directive_chars: int = 8000     # cap total WORK (domain + situation) length
    spec_chars: int | None = None        # cap on the SPECIFICATION; None = deliver whole
    strip_examples: bool = False         # remove example blocks from directives
    strip_rationale: bool = False        # remove "Why:" explanations
    simplify_language: bool = False      # use shorter sentences, simpler vocab
    compress_tables: bool = False        # convert tables to inline text
    format_style: str = "full"           # "full", "concise", "minimal"


PHENOTYPE_TRANSFORMS: dict[str, PhenotypeTransform] = {
    "opus_4_6": PhenotypeTransform(
        max_directive_chars=12000,
        format_style="full",
    ),
    "chatgpt_5_4": PhenotypeTransform(
        max_directive_chars=8000,
        format_style="concise",
    ),
    "codex_5_3": PhenotypeTransform(
        max_directive_chars=6000,
        strip_examples=True,
        strip_rationale=True,
        format_style="concise",
    ),
    "gemini_3_1_pro": PhenotypeTransform(
        max_directive_chars=8000,
        format_style="concise",
    ),
    "deepseek_v3": PhenotypeTransform(
        # ★ WORK settings UNCHANGED: the 4000-char work bound, the example and
        # rationale stripping, the language simplification and the table
        # compression all stand. This is the weakest seat and the machinery
        # built around that is exactly what the founder's ruling protects.
        max_directive_chars=4000,
        strip_examples=True,
        strip_rationale=True,
        simplify_language=True,
        compress_tables=True,
        # `format_style` moved "minimal" -> "concise" on 2026-10-15. "minimal"
        # was the ONLY route by which a per-model style setting decided whether
        # the project's own specification was delivered, and the ruling of
        # 2026-10-14 separates the 2 questions. The reduced form remains
        # reachable for this or any seat by setting `spec_chars`, and it now
        # carries every HARD block rather than 0 of 22.
        format_style="concise",
    ),
}


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class DirectivePacket:
    """A single directive module with metadata."""
    layer: str                    # "universal", "domain", "phenotype", "situation"
    name: str                     # human-readable name
    text: str                     # the directive text
    constraint_class: str         # "HARD" or "SOFT"
    domain: str | None = None     # which domain this belongs to
    model: str | None = None      # which model this is for
    tags: set[str] = field(default_factory=set)


@dataclass
class ComposedDirectiveSet:
    """The output of the composer: a fully assembled directive set."""
    packets: list[DirectivePacket]
    rendered_text: str            # the final assembled prompt text
    policy: dict[str, Any]        # the merged TOML policy
    cid: str                      # composition identity hash
    constraint_count: int         # total active constraints
    token_estimate: int           # rough token estimate (chars / 4)
    constraint_density: float     # constraint_count / token_estimate
    coherence_budget: float       # the model's budget
    pruned_soft: list[str]        # names of SOFT packets pruned for budget
    manifest: dict[str, Any]      # full provenance record


@dataclass(frozen=True)
class ConflictRecord:
    """Record of a detected and resolved inter-layer conflict.

    `deleted` distinguishes a conflict that was RECORDED from one that removed
    text. Added 2026-10-15: a HARD directive is now always kept, and a record
    that cannot say whether its loser survived is a record a reader can
    misread. Defaulted to True so every pre-existing construction is unchanged.
    """
    topic: str
    winner_layer: str
    winner_packet: str
    winner_text: str
    loser_layer: str
    loser_packet: str
    loser_text: str
    reason: str
    deleted: bool = True


# ---------------------------------------------------------------------------
# Problem 1: Universal minimal rendering for small-context models
# ---------------------------------------------------------------------------

# Static fallback — covers all HARD behavioural directives from
# cdsfl_core_formal.md §Non-Formalisable Directives. Used if the
# regex extraction from the live doc fails.
HARD_BEHAVIOURAL_FALLBACK: tuple[str, ...] = (
    "Push back on impossible, contradictory, or ill-advised requirements. "
    "Say 'no' or 'I don't know' when honest. Never fabricate certainty.",
    "Default to the simplest sufficient solution. Justified complexity is "
    "complexity the user cannot do without.",
    "Do not silently comply with tangential requests. Flag them and state "
    "the priority path instead.",
    "End with a definitive stance: what was done and what comes next. "
    "Never trail off with engagement-seeking questions.",
    "Communicate as with a serious engineering colleague.",
)


def _flatten_policy_items(data: dict[str, Any], prefix: str = "policy") -> list[str]:
    """Flatten a nested TOML dict into deterministic key=value lines."""
    items: list[str] = []

    def _walk(value: Any, path: str) -> None:
        if isinstance(value, dict):
            for key in sorted(value):
                _walk(value[key], f"{path}.{key}" if path else key)
            return
        if isinstance(value, list):
            for index, item in enumerate(value):
                _walk(item, f"{path}[{index}]")
            return
        rendered = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
        items.append(f"{path}={rendered}")

    _walk(data, prefix)
    return items


def _extract_hard_behavioural_directives(universal_text: str) -> list[str]:
    """Extract HARD behavioural directives from the Non-Formalisable section."""
    section_match = re.search(
        r"##\s+Non-Formalisable Directives.*?(?=\n## |\Z)",
        universal_text,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if not section_match:
        return list(HARD_BEHAVIOURAL_FALLBACK)

    bullets: list[str] = []
    current: list[str] = []
    for raw_line in section_match.group(0).splitlines():
        line = raw_line.strip()
        if line.startswith("- "):
            if current:
                bullets.append(" ".join(current))
            current = [line[2:].strip()]
        elif current and line:
            current.append(line)
    if current:
        bullets.append(" ".join(current))

    cleaned: list[str] = []
    seen: set[str] = set()
    for bullet in bullets:
        bullet = re.sub(r"`+", "", bullet)
        bullet = re.sub(r"\s+", " ", bullet).strip().rstrip(".")
        signature = re.sub(r"[^a-z0-9]+", " ", bullet.lower()).strip()
        if signature and signature not in seen:
            seen.add(signature)
            cleaned.append(f"{bullet}.")
    return cleaned or list(HARD_BEHAVIOURAL_FALLBACK)


def _render_universal_minimal(max_chars: int | None = None) -> str:
    """Render Layer 1 in minimal form, carrying EVERY HARD block of the spec.

    ★ THE DOCSTRING USED TO SAY "preserving all HARD constraints" AND IT WAS
    FALSE. Measured 2026-10-15 by `scripts/the_spec_is_not_work_2026-10-15.py`,
    over the 22 blocks that `_block_is_hard()` -- the project's OWN HARD
    predicate -- identifies in
    `cdsfl_core_formal.md`, BY VERBATIM CONTAINMENT: **0 of 22 carried,
    0.0000%, Wilson [0.0000%, 14.8655%], Clopper-Pearson [0.0000%, 15.4373%]**,
    against **22 of 22 after this repair, 100.0000%, Wilson [85.1345%,
    100.0000%], Clopper-Pearson [84.5627%, 100.0000%]**. Among the 22 dropped were
    the whole of "Falsifier Integrity -- Do Not Reach for the Answer", "Do not
    read a scoring key or answer file", "Do not modify, delete, weaken or skip
    a test to make it pass" and "Do not terminate early to obtain a passing
    result" -- the anti-cheating section every verdict in this project rests on.

    WHY IT WAS FALSE. It extracted bullets from ONE section,
    `## Non-Formalisable Directives`, and called that the HARD set. The HARD set
    is whatever `_block_is_hard()` says it is, and that predicate reads MUST,
    NEVER, HARD, REQUIRED and the rest across the WHOLE file. 2 definitions of
    HARD existed in 1 module and only 1 of them was live code the models saw.

    WHAT IT DOES NOW, in order, so a reader can predict the output:
      1. the flattened `universal.toml` policy keys, as before;
      2. the behavioural bullets of `## Non-Formalisable Directives`, as before;
      3. EVERY block of `cdsfl_core_formal.md` that `_block_is_hard()` accepts,
         verbatim, deduplicated against what 1 and 2 already carried.

    `max_chars` is unchanged in meaning and still RAISES rather than silently
    truncating: a specification cut to fit is the defect this repair exists to
    close, so a caller that cannot afford the HARD set must learn that from an
    exception and not from a shorter prompt. It is `None` on every live call.
    """
    universal_policy = _load_toml(REGISTRY_DIR / "universal.toml")

    formal_path = DIRECTIVES_DIR / "universal" / "cdsfl_core_formal.md"
    prose_path = DIRECTIVES_DIR / "universal" / "cdsfl_core.txt"
    universal_text = ""
    if formal_path.exists():
        universal_text = formal_path.read_text(encoding="utf-8")
    elif prose_path.exists():
        universal_text = prose_path.read_text(encoding="utf-8")

    lines = ["CDSFL CORE MINIMAL"]
    lines.extend(_flatten_policy_items(universal_policy, "policy"))
    for i, directive in enumerate(
        _extract_hard_behavioural_directives(universal_text), 1
    ):
        lines.append(f"behaviour.{i}={directive}")

    # ★ EVERY HARD BLOCK, BY THE PROJECT'S OWN PREDICATE (2026-10-15).
    #
    # THE DEDUP IS ON VERBATIM CONTAINMENT, AND THE FIRST ATTEMPT USED A
    # FIRST-8-WORDS PROBE INSTEAD. That probe space-joins the first 8 words
    # ACROSS NEWLINES, so it can never match a multi-line block against text
    # that keeps its newlines -- and 9 of the 22 HARD blocks are multi-line. It
    # reported 13 of 22 carried where verbatim containment reports 22 of 22, and
    # it reported the PRE-REPAIR render as carrying 1 of 22 where the honest
    # figure is 0 of 22. THE INSTRUMENT WAS THE DEFECT, NOT THE RENDER, which is
    # this project's recurring shape: check what could make a check return
    # nothing even though the thing is there. Dedup and measurement now use the
    # same verbatim test.
    already_text = "\n".join(lines)
    hard_blocks = [
        b for b in _split_packet_directives(universal_text) if _block_is_hard(b)
    ]
    carried: list[str] = []
    for block in hard_blocks:
        if block in already_text or block in carried:
            continue
        carried.append(block)
    if carried:
        lines.append("")
        lines.append("HARD CONSTRAINTS — VERBATIM, EVERY BLOCK")
        for block in carried:
            lines.append("")
            lines.append(block)

    rendered = "\n".join(lines)
    if max_chars is not None and len(rendered) > max_chars:
        raise ValueError(
            f"Minimal universal directive too large: {len(rendered)} > {max_chars}"
        )
    return rendered


# ---------------------------------------------------------------------------
# Problem 3: Enhanced phenotype transform
# ---------------------------------------------------------------------------

_STOPWORDS = frozenset({
    "a", "an", "and", "as", "at", "be", "by", "for", "from", "if", "in",
    "into", "is", "it", "of", "on", "or", "that", "the", "to", "use",
    "with", "without",
})

_SYNONYMS = {
    "brief": "concise", "minimal": "concise", "short": "concise",
    "simple": "concise", "simpler": "concise",
    "detailed": "detailed", "detail": "detailed",
    "proofs": "proof", "proof": "proof",
    "examples": "example", "rationales": "rationale",
    "reasons": "rationale", "tables": "table", "tabular": "table",
}


def _normalise_tokens(text: str) -> set[str]:
    """Extract normalised content tokens for deduplication."""
    lowered = re.sub(r"`([^`]*)`", r"\1", text.lower())
    lowered = re.sub(r"[*_~]+", " ", lowered)
    tokens = set()
    for token in re.findall(r"[a-z0-9]+", lowered):
        token = _SYNONYMS.get(token, token)
        if token not in _STOPWORDS:
            tokens.add(token)
    return tokens


def _semantically_duplicate(left: str, right: str) -> bool:
    """Two directives are duplicates if Jaccard >= 0.85 or containment >= 0.95."""
    left_tokens = _normalise_tokens(left)
    right_tokens = _normalise_tokens(right)
    if not left_tokens or not right_tokens:
        return False
    if left_tokens == right_tokens:
        return True
    intersection = len(left_tokens & right_tokens)
    union = len(left_tokens | right_tokens)
    jaccard = intersection / union
    if jaccard >= 0.85:
        return True
    # Containment check: shorter contained in longer
    smaller = min(len(left_tokens), len(right_tokens))
    if smaller > 0 and intersection / smaller >= 0.95:
        return True
    return False


def _starts_new_block(line: str) -> bool:
    return bool(
        re.match(r"^(\d+[.)]|[-*])\s+", line)
        or line.endswith(":")
        or line.startswith("[")
        or line.startswith("===")
    )


def _apply_phenotype_transform(text: str, transform: PhenotypeTransform) -> str:
    """Apply phenotype transformation rules to directive text.

    The phenotype layer is a functor: it transforms the directive text
    without changing the underlying constraints. HARD constraints are
    preserved exactly. Only presentation is modified.

    Transformations (in order):
    1. Strip examples (if enabled)
    2. Strip rationale (if enabled)
    3. Compress tables (if enabled)
    4. Remove markdown headers → plain text labels
    5. Collapse multi-line directives to single-line
    6. Deduplicate semantically similar directives
    7. Simplify language (if enabled)
    8. Enforce max length
    """
    text = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    if not text:
        return text

    # --- 0. PROTECT CONTENT WHERE PRESENTATION *IS* SUBSTANCE (2026-10-15) ---
    #
    # THE DEFECT, MEASURED DIRECTLY. This function's own docstring promises that
    # it "transforms the directive text without changing the underlying
    # constraints" and that "only presentation is modified". For CODE UNDER
    # REVIEW that promise is false, because in Python indentation IS syntax and
    # a repeated definition IS the thing a reviewer must see.
    #
    # On a situation packet holding 20 repeated function definitions, measured
    # 2026-10-15 by calling this function on both styles:
    #
    #     format_style="full"     2,277 chars, 20 `def `, 80 indented lines
    #     format_style="concise"    193 chars,  1 `def `,  0 indented lines
    #
    # That is 2,085 characters lost, 91.5277%, and 19 of 20 function definitions
    # DELETED. Step 5 strips every line and joins blocks with a space; step 6
    # then deduplicates lines that are semantically similar, which near-identical
    # function definitions always are. 4 of the 5 live models receive the concise
    # rendering, so 4 of 5 seats asked to review code were being shown 1 function
    # of 20, unindented.
    #
    # THE CODE IS NOT FENCED, so protecting fenced blocks alone would not have
    # worked: `_build_situation_packet` emits it under a plain `=== CODE
    # EXTRACTS ===` section marker. Both forms are protected here -- the named
    # section because that is the project's own structure, and fenced blocks
    # because that is how a model writes code back.
    #
    # RESTORED BEFORE THE LENGTH CAP, deliberately, so step 9 measures the true
    # size. Restoring after it would let a seat's capacity limit be computed
    # against a placeholder.
    _verbatim_stash: list[str] = []

    def _stash_verbatim(match: "re.Match[str]") -> str:
        _verbatim_stash.append(match.group(0))
        return f"\n\nZZVERBATIMBLOCK{len(_verbatim_stash) - 1}ZZ\n\n"

    text = re.sub(r"```.*?```", _stash_verbatim, text, flags=re.DOTALL)
    for _section in _VERBATIM_SITUATION_SECTIONS:
        text = re.sub(
            rf"(?m)^=== {re.escape(_section)} ===\n.*?(?=^=== |\Z)",
            _stash_verbatim, text, flags=re.DOTALL)

    # --- 1. Strip examples ---
    if transform.strip_examples:
        lines = text.split("\n")
        filtered: list[str] = []
        skipping = False
        for line in lines:
            stripped_lower = line.strip().lower()
            if stripped_lower.startswith(
                ("example:", "examples:", "e.g.,", "e.g.", "for example:")
            ):
                skipping = True
                continue
            if skipping and (
                not line.strip()
                or re.match(r"^(#{1,6}\s+|\[[^\]]+\]|===|---)", line.strip())
            ):
                skipping = False
            if not skipping:
                filtered.append(line)
        text = "\n".join(filtered)

    # --- 2. Strip rationale ---
    if transform.strip_rationale:
        lines = text.split("\n")
        filtered = []
        for line in lines:
            stripped_lower = line.strip().lower()
            if stripped_lower.startswith(
                ("why:", "rationale:", "motivation:", "reason:")
            ):
                continue
            filtered.append(line)
        text = "\n".join(filtered)

    # --- 3. Compress tables ---
    if transform.compress_tables:
        lines = text.split("\n")
        filtered = []
        for line in lines:
            if "|" in line and line.strip().startswith("|"):
                cells = [c.strip() for c in line.split("|") if c.strip()]
                is_separator = cells and all(
                    set(c) <= {"-", ":"} for c in cells
                )
                if cells and not is_separator:
                    filtered.append(", ".join(cells))
            else:
                filtered.append(line)
        text = "\n".join(filtered)

    # --- 4. Remove markdown headers → plain text labels ---
    lines = text.split("\n")
    filtered = []
    for line in lines:
        header_match = re.match(r"^#{1,6}\s+(.*)$", line.strip())
        if header_match:
            label = header_match.group(1).strip().strip(":")
            if label:
                filtered.append(f"{label}:")
        elif re.match(r"^\s*[-=]{3,}\s*$", line.strip()):
            continue
        else:
            filtered.append(line)
    text = "\n".join(filtered)

    # --- 5. Collapse multi-line directives to single-line ---
    if transform.format_style in ("concise", "minimal"):
        blocks: list[list[str]] = []
        current: list[str] = []

        for line in text.split("\n"):
            stripped = line.strip()
            if not stripped:
                if current:
                    blocks.append(current)
                    current = []
                continue
            if _starts_new_block(stripped):
                if current:
                    blocks.append(current)
                current = [stripped]
            else:
                if not current:
                    current = [stripped]
                else:
                    current.append(stripped)
        if current:
            blocks.append(current)

        collapsed: list[str] = []
        for block in blocks:
            head = block[0]
            tail = block[1:]
            if re.match(r"^(\d+[.)]|[-*])\s+", head):
                prefix_match = re.match(r"^(\d+[.)]|[-*])\s+", head)
                prefix = prefix_match.group(0) if prefix_match else ""
                rest = head[len(prefix):]
                payload = " ".join([rest] + tail).strip()
                payload = re.sub(r"\s+", " ", payload)
                collapsed.append(f"{prefix}{payload}".strip())
            elif head.endswith(":") and not tail:
                collapsed.append(head)
            else:
                payload = " ".join(block)
                payload = re.sub(r"\s+", " ", payload).strip()
                collapsed.append(payload)

        text = "\n".join(collapsed)

    # --- 6. Deduplicate ---
    if transform.format_style in ("concise", "minimal"):
        deduped: list[str] = []
        for line in text.split("\n"):
            if not line.strip():
                continue
            if not any(_semantically_duplicate(line, existing) for existing in deduped):
                deduped.append(line)
        text = "\n".join(deduped)

    # --- 7. Simplify language ---
    if transform.simplify_language:
        replacements = {
            "therefore": "so", "however": "but", "additionally": "also",
            "approximately": "about", "sufficient": "enough",
            "prioritise": "prefer", "commence": "start",
            "must not": "do not", "should not": "avoid",
            "is required to": "must",
        }
        for src, dst in replacements.items():
            text = re.sub(
                rf"\b{re.escape(src)}\b", dst, text, flags=re.IGNORECASE
            )

    # --- 7b. RESTORE THE PROTECTED CONTENT, before the length cap ---
    for _i, _block in enumerate(_verbatim_stash):
        text = text.replace(f"ZZVERBATIMBLOCK{_i}ZZ", _block)

    # --- 8. Clean up blank lines ---
    text = re.sub(r"\n{3,}", "\n\n", text).strip()

    # --- 9. Enforce max length ---
    if len(text) > transform.max_directive_chars:
        text = (
            text[: transform.max_directive_chars].rstrip()
            + "\n[... truncated for model capacity]"
        )

    return text


# ---------------------------------------------------------------------------
# Problem 2: Intra-packet SOFT directive pruning
# ---------------------------------------------------------------------------

_DIRECTIVE_START_RE = re.compile(
    r"^(?:\d+[.)]\s+|[-*\u2022]\s+|[A-Z][A-Z0-9 _/-]+:\s*|=== .+ ===\s*)"
)

_HARD_BLOCK_MARKERS = (
    " HARD ", " MUST ", " NEVER ", " REQUIRED ",
    " NON-NEGOTIABLE ", " FORBIDDEN ", " DO NOT ", " ALWAYS ",
)


def _split_packet_directives(text: str) -> list[str]:
    """Split directive text into individual blocks by structure."""
    blocks: list[str] = []
    current: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped:
            if current:
                blocks.append("\n".join(current).strip())
                current = []
            continue
        if current and _DIRECTIVE_START_RE.match(stripped):
            blocks.append("\n".join(current).strip())
            current = [stripped]
            continue
        current.append(stripped)
    if current:
        blocks.append("\n".join(current).strip())
    return [b for b in blocks if b]


def _block_is_hard(block: str) -> bool:
    """Determine if a directive block contains HARD constraint content."""
    upper = f" {block.upper()} "
    return any(m in upper for m in _HARD_BLOCK_MARKERS)


def _prune_packet_directives(
    packet: DirectivePacket, max_chars: int
) -> DirectivePacket:
    """Prune individual SOFT directives within a packet to meet a char budget.

    HARD directives within the packet are NEVER removed. SOFT directives are
    removed from the end (lowest priority) until the packet fits.
    """
    if len(packet.text) <= max_chars or packet.constraint_class == "HARD":
        return packet

    blocks = _split_packet_directives(packet.text)
    classified = [(block, _block_is_hard(block)) for block in blocks]
    retained = classified[:]

    while len("\n\n".join(b for b, _ in retained)) > max_chars:
        removed = False
        for index in range(len(retained) - 1, -1, -1):
            if not retained[index][1]:  # SOFT block
                retained.pop(index)
                removed = True
                break
        if not removed:
            break  # only HARD blocks remain

    pruned_text = "\n\n".join(b for b, _ in retained).strip()
    return replace(
        packet,
        text=pruned_text if pruned_text else packet.text,
        tags=set(packet.tags) | {"intra_pruned"},
    )


# ---------------------------------------------------------------------------
# Packet loading
# ---------------------------------------------------------------------------

def _load_universal_directive(model: str | None = None) -> DirectivePacket:
    """Load the universal CDSFL directive (Layer 1) — the SPECIFICATION.

    ★ THE DECISION IS NO LONGER ABOUT CAPACITY (2026-10-15). It used to read
    "For small-context models (format_style=minimal or text exceeds
    max_directive_chars) ... Full text for large-context models", and that last
    clause described a branch NO MODEL COULD REACH: the specification is 27,803
    characters and the most generous `max_directive_chars` is 12,000, so 5 of 5
    models received the reduced form unconditionally. Finding C0040.

    It now reads `spec_chars`, which is `None` for every model, so the
    specification is delivered WHOLE. `max_directive_chars` is the WORK bound
    and is not consulted here at all. A model is put on the reduced form only by
    an explicit `spec_chars` or by `format_style="minimal"`, and the reduced
    form itself now carries every HARD block verbatim rather than 0 of 22.

    See `PhenotypeTransform` for the founder's ruling that separates the 2
    bounds, and `bench/tests/test_falsifier_C0040_universal_directive_2026-09-10.py`
    for the executing guard.
    """
    formal_path = DIRECTIVES_DIR / "universal" / "cdsfl_core_formal.md"
    prose_path = DIRECTIVES_DIR / "universal" / "cdsfl_core.txt"

    path = formal_path if formal_path.exists() else prose_path
    full_text = path.read_text(encoding="utf-8") if path.exists() else ""

    transform = PHENOTYPE_TRANSFORMS.get(model or "", PhenotypeTransform())
    # ★ THE SPECIFICATION IS NOT WORK (founder's ruling 2026-10-14; see
    # `PhenotypeTransform`). This decision used to read `max_directive_chars`,
    # the WORK bound, whose most generous value is 12,000 against a 27,803-char
    # specification -- so the reduced form was served to 5 of 5 models
    # unconditionally and the docstring's "Full text for large-context models"
    # described a branch no model could reach. It now reads `spec_chars`, which
    # is `None` for every model, so the specification is delivered whole.
    #
    # `format_style == "minimal"` is RETAINED as an explicit per-model request
    # and still selects the reduced form, because a model that genuinely needs
    # it must still be able to say so. The reduced form itself is now faithful.
    use_minimal = (
        transform.format_style == "minimal"
        or (transform.spec_chars is not None
            and len(full_text) > transform.spec_chars)
    )
    text = (
        # ★ THE SPECIFICATION BOUND, NOT THE WORK BOUND (2026-10-15). This
        # passed `max_directive_chars` and would now RAISE for any model
        # configured `format_style="minimal"` with a work bound under 8,367,
        # because the faithful render is 8,367 characters and `max_chars`
        # raises rather than truncating. `deepseek_v3` was the only such model
        # and moved to "concise", so no live model reaches it -- but a latent
        # raise on a reachable branch is a defect whether or not a current
        # config hits it, and the same spec/work distinction fixes it.
        _render_universal_minimal(max_chars=transform.spec_chars)
        if use_minimal
        else full_text
    )

    return DirectivePacket(
        layer="universal",
        name="cdsfl_core",
        text=text,
        constraint_class="HARD",
        tags={"falsification", "hard_soft", "anti_deference", "verification"},
    )


def _load_domain_directive(
    domain: str, variant: str | None = None
) -> DirectivePacket | None:
    """Load a domain-specific directive (Layer 2), or None, LOUDLY.

    ★ A DOMAIN NAME THAT MATCHES NOTHING USED TO RETURN `None` IN SILENCE
    (2026-10-15). The manifest records `"domain": "statistics"` whether the
    layer was composed or not, so a reader could not tell a run that wasted its
    entire domain layer from one whose domain simply had little to say.

    FOUND WHILE CHOOSING THE DOMAIN FOR THE 2 FREE RUNS: the launcher's own
    resume command says `--domain statistics` and there is no `statistics`
    directory, so every such run composed NO domain layer. Measured by
    `scripts/a_domain_name_that_matches_nothing_2026-10-15.py` over every
    `"domain"` value in every shipped `bench/exp*_configs/*.json`, resolved
    through this function rather than by comparing strings:

      * **16 of 47 references resolve to nothing — 34.0426%, Wilson [22.1674%,
        48.3291%], Clopper-Pearson [20.8641%, 49.3132%]**.
      * **6 of the 9 distinct names match nothing — 66.6667%, Wilson [35.4202%,
        87.9416%]**: `biology`, `cs_software`, `engineering`,
        `information_science`, `physics`, `statistics`.

    IT WARNS AND DOES NOT REFUSE, DELIBERATELY. Refusing would break 16 of 47
    shipped config references at once, and deciding that those 6 names should
    either acquire directories or be renamed is the founder's call, not a
    repair. The warning uses the same channel the coherence budget already
    warns on, so a run's console carries it where a reader is already looking.
    """
    domain_dir = DIRECTIVES_DIR / domain

    def _nothing(reason: str) -> None:
        available = sorted(
            d.name for d in DIRECTIVES_DIR.iterdir()
            if d.is_dir() and d.name != "universal"
        )
        warnings.warn(
            f"Composer: domain {domain!r} composes NO DOMAIN LAYER ({reason}). "
            f"The manifest will still record domain={domain!r}, so this is the "
            f"only notice. Shipped domains: {', '.join(available)}.",
            stacklevel=3,
        )
        return None

    if not domain_dir.exists():
        return _nothing("no such directory under bench/directives")

    if variant:
        path = domain_dir / f"{domain}_{variant}.txt"
    else:
        txt_files = sorted(domain_dir.glob("*.txt"))
        if not txt_files:
            return _nothing("the directory exists but holds no .txt directive")
        path = txt_files[0]

    if not path.exists():
        return _nothing(f"the named variant file {path.name!r} is missing")

    return DirectivePacket(
        layer="domain",
        name=path.stem,
        text=path.read_text(encoding="utf-8"),
        constraint_class="SOFT",
        domain=domain,
        tags={domain},
    )


#: Situation-layer sections whose PRESENTATION IS SUBSTANCE, so the phenotype
#: transform must pass them through character for character. `CODE EXTRACTS`
#: carries the code under review, where indentation is Python syntax and a
#: repeated definition is the thing the reviewer is being asked to look at.
#: `INTERACTION SURFACE` carries signatures for the same reason.
_VERBATIM_SITUATION_SECTIONS = ("CODE EXTRACTS", "INTERACTION SURFACE")


def _build_situation_packet(
    review_target: str,
    code_extracts: str = "",
    verified_facts: str = "",
    explicit_unknowns: str = "",
    adversarial_brief: str = "",
    interaction_surface: str = "",
) -> DirectivePacket:
    """Build a situation-layer directive packet (Layer 4 — per-dispatch)."""
    sections = []
    if review_target:
        sections.append(f"=== REVIEW TARGET ===\n{review_target}")
    if code_extracts:
        sections.append(f"=== CODE EXTRACTS ===\n{code_extracts}")
    if interaction_surface:
        sections.append(f"=== INTERACTION SURFACE ===\n{interaction_surface}")
    if verified_facts:
        sections.append(f"=== VERIFIED FACTS ===\n{verified_facts}")
    if explicit_unknowns:
        sections.append(f"=== EXPLICIT UNKNOWNS ===\n{explicit_unknowns}")
    if adversarial_brief:
        sections.append(
            f"=== ADVERSARIAL BRIEF ===\n{adversarial_brief}\n"
            f"=== END ADVERSARIAL BRIEF ==="
        )

    return DirectivePacket(
        layer="situation",
        name="confer_packet",
        text="\n\n".join(sections),
        constraint_class="SOFT",
        tags={"situation", "task_specific"},
    )


# ---------------------------------------------------------------------------
# Interaction pattern presets (Situation layer)
#
# Interaction patterns are user-configurable parameters in the constraint box
# (protocol × focus × context), not competing methodologies. Each preset is
# a DirectivePacket factory. The runner selects one by name.
#
# Evidence: C1-C5 HIL comparison (4 April 2026). C1+C4 union = 32% more
# coverage than best single condition. Different patterns find different
# things — the choice is a Situation layer configuration, not architecture.
# ---------------------------------------------------------------------------

# Proven in Exp 18, Runs 8-11. Mandatory FFF structure.
_PRESET_FFF = (
    "## Find-Follow-Fix Protocol (MANDATORY for this round)\n\n"
    "For EVERY finding, you MUST provide all three steps:\n\n"
    "**FIND:** Describe the issue precisely. Include the specific location "
    "(file, section, line if applicable), what is wrong, and evidence that "
    "it is wrong.\n\n"
    "**FOLLOW:** After identifying the issue, trace its consequences through ALL "
    "other sections, functions, or formulas that reference the same variables, "
    "interfaces, or assumptions. Report any new issues the bug creates or "
    "reveals.\n\n"
    "**ANALYSE:** Before proposing a fix, state dispassionately whether this "
    "finding is CONFIRMED (you have concrete evidence it is real), UNCERTAIN "
    "(you cannot determine from the code alone), or REJECTED (you traced "
    "through the code and the issue does not exist as described). Do not "
    "conflate separate issues. Do not soften or hedge a clear conclusion. "
    "State what the code does, not what it might do.\n\n"
    "**FIX:** Provide the exact corrected text, code, or formula. Not a "
    "suggestion -- the actual replacement. Use <<<< (old) ==== (new) >>>> "
    "markers for code fixes. Only provide a fix for CONFIRMED findings.\n\n"
    "If your fix creates no consequences, state \"FOLLOW: No downstream "
    "impact identified\" -- but this should be rare for non-trivial fixes.\n"
)

# From C4/C5 conditions. Structured certificates with explicit premises,
# execution traces, and formal conclusions. Meta's semi-formal format.
_PRESET_META_STRUCTURED = (
    "## Structured Certificate Protocol (MANDATORY for this round)\n\n"
    "For EVERY finding, you MUST provide:\n\n"
    "1. **STRUCTURED CERTIFICATE:** State your premises explicitly. "
    "Trace execution through concrete examples (with specific inputs "
    "and expected outputs). Derive a formal conclusion.\n\n"
    "2. **FIND-FOLLOW-ANALYSE-FIX:** For every issue —\n"
    "   FIND: State the bug, its location, and your evidence.\n"
    "   FOLLOW: Before proposing any fix, trace consequences through the "
    "entire system. What depends on this? What interfaces does it cross? "
    "What state does it propagate? What breaks downstream?\n"
    "   ANALYSE: State dispassionately whether this is CONFIRMED, UNCERTAIN, "
    "or REJECTED based on what the code does, not what it might do. Do not "
    "conflate separate issues into one finding.\n"
    "   FIX: For CONFIRMED findings only, apply the simplest sufficient "
    "correction that addresses both the root cause AND the downstream "
    "consequences. Classify as PATCH, NOVEL CONSTRUCT, or ARCHITECTURAL.\n\n"
    "3. **FALSIFICATION:** Actively try to disprove your own conclusions "
    "before presenting them. Retract claims you can disprove. Only present "
    "claims that survive your own attempted falsification.\n\n"
    "4. **MATHEMATICAL RIGOUR:** Where applicable, provide formal proofs "
    "(symbolic, set-theoretic, or by contradiction).\n\n"
    "5. **CROSS-COMPONENT AWARENESS:** This is a multi-component pipeline. "
    "Bugs in one component cascade through others. Always consider how "
    "findings interact across the full system.\n\n"
    "Show your working. Depth over breadth.\n"
)

# From C1 condition. No format enforcement. Natural conversation.
_PRESET_CONVERSATIONAL = (
    "## Conversational Review Protocol\n\n"
    "Review the artifact naturally. Report issues as you find them in "
    "whatever format is most natural. Focus on cross-component interactions "
    "and real-world failure modes. There is no required output structure — "
    "prioritise thoroughness and genuine analysis over format compliance.\n\n"
    "For each issue, explain what is wrong, why it matters, and how to "
    "fix it. Trace consequences when relevant.\n"
)

# From C5 condition. Conversational default with ITC fallback.
_PRESET_THREE_LAYER_SCHEMA = (
    "## Three-Layer Schema Protocol\n\n"
    "Operate in conversational mode by default. Report findings naturally, "
    "trace consequences, and show your working.\n\n"
    "If you find yourself repeating prior findings or producing diminishing "
    "returns, switch to structured certificate format: explicit premises, "
    "concrete execution traces, formal conclusions.\n\n"
    "If structured certificates also plateau, switch to Meta structured "
    "prompting: classify each finding as PATCH / NOVEL CONSTRUCT / "
    "ARCHITECTURAL, provide formal proofs where applicable, and apply "
    "systematic falsification to your own claims.\n\n"
    "The three layers are fallback positions, not simultaneous requirements. "
    "Start natural, escalate only when needed.\n"
)

# Combined 4-layer schema: Meta Structured + FFAFP + Extended Falsification + Conversational.
# First deployment: novelty extension confer (9 April 2026). Combines the
# structured certificate rigour of Meta SRP with FFAFP (5-step: Find-Follow-
# Analyse-Fix-P-pass) and global multi-pass falsification. Conversational
# fallback where structure adds no rigour.
_PRESET_FOUR_LAYER = (
    "## Combined 4-Layer Review Protocol (MANDATORY for this round)\n\n"
    "Apply ALL four layers simultaneously. They are complementary, not alternatives.\n\n"
    "### Layer 1 — Structured Certificates\n\n"
    "For EVERY finding, state your premises explicitly. Trace execution "
    "through concrete examples (with specific inputs and expected outputs). "
    "Derive a formal conclusion. Do not assert conclusions without the "
    "derivation that supports them.\n\n"
    "### Layer 2 — FFAFP (Find-Follow-Analyse-Fix-P-pass)\n\n"
    "For EVERY finding, apply all five steps:\n"
    "   FIND: State the bug, its location, and your evidence.\n"
    "   FOLLOW: Before proposing any fix, trace consequences through the "
    "entire system. What depends on this? What interfaces does it cross? "
    "What breaks downstream?\n"
    "   ANALYSE: State dispassionately whether this is CONFIRMED, UNCERTAIN, "
    "or REJECTED based on what the code does, not what it might do.\n"
    "   FIX: For CONFIRMED findings only, apply the simplest sufficient "
    "correction that addresses root cause AND downstream consequences.\n"
    "   P-PASS: Actively try to disprove your own fix. Does it introduce "
    "new problems? Does it address the root cause or just the symptom? "
    "Retract claims you can disprove.\n\n"
    "### Layer 3 — Extended Falsification (Multi-Pass)\n\n"
    "After completing FFAFP on all findings, run a global P-pass across "
    "your entire output. Look for cross-finding contradictions, missed "
    "interactions, and assumptions that don't survive scrutiny. "
    "Continue for up to 5 passes or until two consecutive passes produce "
    "no new findings above consequence threshold. Only present claims that "
    "survive all passes.\n\n"
    "### Layer 4 — Conversational Fallback\n\n"
    "Where structured format does not naturally apply (context-setting, "
    "qualitative observations, boundary identification), use natural "
    "conversational prose. Do not force structure where it adds no rigour. "
    "Depth over format compliance.\n\n"
    "Show your working. Depth over breadth.\n"
)

# Control condition. No CDSFL, no structure.
_PRESET_UNCONSTRAINED = (
    "## Review Protocol\n\n"
    "Review the artifact and report any issues you find.\n"
)

# Registry: name → (text, constraint_class, tags)
INTERACTION_PATTERN_PRESETS: dict[str, tuple[str, str, set[str]]] = {
    "fff": (_PRESET_FFF, "HARD", {"fff", "baseline"}),
    "meta_structured": (_PRESET_META_STRUCTURED, "HARD", {"meta", "structured", "certificates"}),
    "conversational": (_PRESET_CONVERSATIONAL, "SOFT", {"conversational", "hil", "c1"}),
    "three_layer_schema": (_PRESET_THREE_LAYER_SCHEMA, "SOFT", {"three_layer", "c5", "adaptive"}),
    "unconstrained": (_PRESET_UNCONSTRAINED, "SOFT", {"control", "unconstrained"}),
    "four_layer": (_PRESET_FOUR_LAYER, "HARD", {"meta", "structured", "fff", "ffaf", "p_pass", "four_layer"}),
}


def build_interaction_pattern(name: str) -> DirectivePacket:
    """Build a Situation layer DirectivePacket from a named interaction pattern.

    Available patterns: fff, meta_structured, conversational,
    three_layer_schema, unconstrained.

    Usage::

        situation = build_interaction_pattern("meta_structured")
        composed = compose("software", "opus_4_6", situation=situation)
    """
    if name not in INTERACTION_PATTERN_PRESETS:
        available = ", ".join(sorted(INTERACTION_PATTERN_PRESETS))
        raise ValueError(
            f"Unknown interaction pattern {name!r}. "
            f"Available: {available}"
        )
    text, constraint_class, tags = INTERACTION_PATTERN_PRESETS[name]
    return DirectivePacket(
        layer="situation",
        name=f"interaction_pattern_{name}",
        text=text,
        constraint_class=constraint_class,
        tags=tags | {"interaction_pattern"},
    )


# ---------------------------------------------------------------------------
# Coherence enforcement (with intra-packet pruning — Problem 2)
# ---------------------------------------------------------------------------

def _count_constraints(policy: dict[str, Any]) -> int:
    """Count active constraints in a merged policy."""
    count = 0
    constraints = policy.get("constraints", {})
    for v in constraints.values():
        if isinstance(v, bool) and v:
            count += 1
        elif isinstance(v, str):
            count += 1
    verification = policy.get("verification", {})
    for v in verification.values():
        if v is not None and v is not False:
            count += 1
    protocol = policy.get("protocol", {})
    for v in protocol.values():
        if v is not None and v is not False:
            count += 1
    return count


def _prune_for_coherence(
    packets: list[DirectivePacket],
    policy: dict[str, Any],
    budget: float,
) -> tuple[list[DirectivePacket], list[str]]:
    """Prune SOFT content if constraint density exceeds budget.

    Two-pass strategy:
    1. Intra-packet pruning: remove individual SOFT directives within packets
    2. Whole-packet pruning: remove entire SOFT packets if still over budget

    HARD packets are NEVER pruned. Universal is NEVER pruned.
    """
    total_chars = sum(len(p.text) for p in packets)
    token_estimate = max(total_chars // 4, 1)
    constraint_count = _count_constraints(policy)
    density = constraint_count / token_estimate

    if density <= budget:
        return packets, []

    pruned_names: list[str] = []
    mutable_packets = list(packets)

    prunable = [
        (i, p) for i, p in enumerate(mutable_packets)
        if p.constraint_class == "SOFT" and p.layer != "universal"
    ]
    prune_order = {"situation": 0, "domain": 1, "phenotype": 2}
    prunable.sort(key=lambda x: prune_order.get(x[1].layer, 3))

    # Pass 1: intra-packet pruning — trim SOFT directives within each packet
    for idx, packet in prunable:
        target_chars = max(int(len(packet.text) * 0.7), 1)
        new_packet = _prune_packet_directives(packet, target_chars)
        if len(new_packet.text) < len(packet.text):
            mutable_packets[idx] = new_packet
            pruned_names.append(f"{packet.name}::intra")

        remaining_chars = sum(len(p.text) for p in mutable_packets)
        remaining_tokens = max(remaining_chars // 4, 1)
        density = constraint_count / remaining_tokens
        if density <= budget:
            return mutable_packets, pruned_names

    # Pass 2: whole-packet pruning if still over budget
    keep_indices = set(range(len(mutable_packets)))
    for idx, packet in prunable:
        keep_indices.discard(idx)
        pruned_names.append(packet.name)

        remaining = [mutable_packets[i] for i in sorted(keep_indices)]
        remaining_chars = sum(len(p.text) for p in remaining)
        remaining_tokens = max(remaining_chars // 4, 1)
        density = constraint_count / remaining_tokens
        if density <= budget:
            return remaining, pruned_names

    return [mutable_packets[i] for i in sorted(keep_indices)], pruned_names


# ---------------------------------------------------------------------------
# Problem 4: Cross-layer conflict resolution
# ---------------------------------------------------------------------------

_LAYER_PRIORITY = {
    "universal": 4,
    "domain": 3,
    "phenotype": 2,
    "situation": 1,
}


def _directive_topic_and_stance(text: str) -> tuple[str | None, str | None]:
    """Extract semantic topic and stance from a directive for conflict detection."""
    lower = text.lower()

    if any(w in lower for w in ("minimal", "concise", "brief", "simple format")):
        return "verbosity", "low"
    if any(w in lower for w in ("detailed", "exhaustive", "full proof", "formal proof")):
        return "verbosity", "high"

    if "example" in lower:
        if any(w in lower for w in ("do not", "avoid", "strip", "remove", "without")):
            return "examples", "exclude"
        return "examples", "include"

    if any(w in lower for w in ("rationale", "reason", "motivation", "why")):
        if any(w in lower for w in ("do not", "avoid", "strip", "remove", "without")):
            return "rationale", "exclude"
        return "rationale", "include"

    if "table" in lower or "tabular" in lower:
        if any(w in lower for w in ("inline", "plain text", "compress", "without")):
            return "table", "exclude"
        return "table", "include"

    return None, None


def _specificity_score(packet: DirectivePacket) -> int:
    """Higher score = more specific directive."""
    score = 0
    if packet.domain:
        score += 2
    if packet.model:
        score += 1
    if packet.layer == "domain":
        score += 1
    return score


#: Does a cross-layer SOFT loser get DELETED, or RECORDED and kept?
#:
#: ★ DEFAULT CHANGED TO RECORD-ONLY, 2026-10-15, AND THE CAPABILITY IS RETAINED
#: BEHIND THIS FLAG -- the same treatment the mechanical directive pruner got on
#: the founder's ruling of 2026-10-13, retired from the default path and left
#: reachable so the lean-versus-full comparison can still be run.
#:
#: THE MEASUREMENT BEHIND THE CHANGE, on the named property "fraction of domain
#: directive blocks delivered": with deletion on, 1 domain block is deleted
#: across 10 domains; with it off, 0 are. The deletion that fires is
#: `product_automotive`'s *"Material specification per OEM standard (VW TL, BMW
#: GS, GM GMW, Ford WSS-M)"* losing to the core specification's FORMALISATION
#: TABLE, on topic `table`, because `_directive_topic_and_stance` assigns that
#: topic to any text containing the word "table" or a pipe-delimited row. The 2
#: texts are about different things; the conflict is an artefact of a keyword
#: heuristic, and the cost of the artefact is an engineering requirement a model
#: is then never told. Producer: `scripts/the_spec_is_not_work_2026-10-15.py`.
#:
#: WHAT IS GIVEN UP, STATED RATHER THAN DISCOVERED: a model may now receive 2
#: directives that a cruder reading calls contradictory. Whether that costs
#: anything is exactly the question a simulated run answers, and it is carried
#: into the programme of study as a high-priority item rather than assumed.
CONFLICT_DELETES_SOFT_LOSER = False


def resolve_layer_conflicts(
    composed: ComposedDirectiveSet,
    *,
    delete_soft_loser: bool | None = None,
) -> tuple[ComposedDirectiveSet, list[ConflictRecord]]:
    """Resolve conflicts between directives from different layers.

    Resolution rules:
    1. HARD always wins over SOFT, regardless of layer. A HARD loser is
       RECORDED and KEPT -- never deleted (2026-10-15). Rule 1 never licensed
       deleting a HARD, and `p-pass-hard-precedence` RANKS conflicting HARD
       constraints rather than discarding one.
    2. For SOFT vs SOFT conflicts: higher layer wins.
       Layer priority: universal > domain > phenotype > situation.
    3. For same-layer SOFT conflicts: more specific (domain-tagged) wins.
    4. A PACKET NEVER RESOLVES AGAINST ITSELF (2026-10-15). This function
       resolves conflicts "between directives from different layers", and 2
       blocks of 1 packet are 1 author's text at 1 layer with 1 specificity, so
       rules 1 to 3 have nothing to decide and the tie broke on list order.
    5. Whether a cross-layer SOFT loser is DELETED or merely RECORDED is
       `CONFLICT_DELETES_SOFT_LOSER`, default False; `delete_soft_loser`
       overrides it per call.

    MEASURED 2026-10-15 with the specification delivered whole, over 10 domains
    (`scripts/the_spec_is_not_work_2026-10-15.py`): before these rules, 40 of 42
    conflicts were SAME-PACKET (95.2381%, Wilson [84.2101%, 98.6842%]), 0 were
    same-layer and 2 were cross-layer. **41 of the 42 deletions had a HARD
    loser** by this function's OWN HARD predicate -- `constraint_class == "HARD"
    or _block_is_hard(text)`, the same tuple it sorts on -- because the
    universal packet IS classed HARD, so 40 of them were removing the project's
    own specification and the 41st was the biomedical
    pre-specified-sample-size formula. **A FIRST READING SAID 11 AND IS
    WITHDRAWN**: it applied `_block_is_hard` to `ConflictRecord.loser_text`,
    which is truncated to 100 characters and drops the packet class entirely.
    After: 2 conflicts recorded, 0 HARD deletions, 0 packets altered.
    """
    if delete_soft_loser is None:
        delete_soft_loser = CONFLICT_DELETES_SOFT_LOSER
    entries: list[dict[str, Any]] = []
    for packet_index, packet in enumerate(composed.packets):
        for directive_index, directive_text in enumerate(
            _split_packet_directives(packet.text)
        ):
            entries.append({
                "id": f"{packet.layer}:{packet.name}:{directive_index}",
                "packet_index": packet_index,
                "packet": packet,
                "text": directive_text,
                "hard": packet.constraint_class == "HARD" or _block_is_hard(directive_text),
                "priority": (
                    1 if (packet.constraint_class == "HARD" or _block_is_hard(directive_text)) else 0,
                    _LAYER_PRIORITY.get(packet.layer, 0),
                    _specificity_score(packet),
                    -packet_index,
                    -directive_index,
                ),
            })

    # Sort by priority descending — highest priority first
    entries.sort(key=lambda e: e["priority"], reverse=True)

    kept: list[dict[str, Any]] = []
    conflicts: list[ConflictRecord] = []

    for entry in entries:
        topic, stance = _directive_topic_and_stance(entry["text"])
        if topic is None:
            # No detectable conflict dimension — always keep
            kept.append(entry)
            continue

        losing = False
        for winner in kept:
            # ★ GUARD 1: A PACKET MAY NOT RESOLVE AGAINST ITSELF (2026-10-15).
            # This function is `resolve_layer_conflicts` and its own docstring
            # says it resolves conflicts "between directives from different
            # layers". Two blocks of the SAME packet are one author's text at
            # one layer with one `_specificity_score`, so every rule below has
            # nothing to decide on and the tie broke on list order -- deleting
            # half of a document because its own §3 says "concise" and its own
            # §7 says "full proof", which are different scopes, not a conflict.
            # MEASURED 2026-10-15 over 10 domains with the specification
            # delivered whole: 40 of 42 conflicts were SAME-PACKET, 95.2381%,
            # Wilson [84.2101%, 98.6842%], against 2 genuinely cross-layer and
            # 0 same-layer. Producer:
            # `scripts/the_spec_is_not_work_2026-10-15.py`.
            if winner["packet_index"] == entry["packet_index"]:
                continue
            winner_topic, winner_stance = _directive_topic_and_stance(winner["text"])
            if winner_topic == topic and winner_stance != stance:
                # ★ GUARD 2: A HARD DIRECTIVE IS RECORDED, NEVER DELETED
                # (2026-10-15). Rule 1 of this function is "HARD always wins
                # over SOFT". It never said a HARD may be deleted by anything,
                # and `p-pass-hard-precedence` RANKS conflicting HARD
                # constraints rather than discarding one. Measured on the same
                # run: 41 of 42 deletions had a HARD loser by this
                # function's own predicate -- 40 of them blocks of the
                # project's own specification, which the universal packet
                # classes HARD, and 1 the biomedical
                # pre-specified-sample-size formula. An earlier reading of 11
                # is WITHDRAWN: it tested the 100-character truncated
                # `loser_text` and so could not see the packet class.
                conflicts.append(ConflictRecord(
                    topic=topic,
                    winner_layer=winner["packet"].layer,
                    winner_packet=winner["packet"].name,
                    winner_text=winner["text"][:100],
                    loser_layer=entry["packet"].layer,
                    loser_packet=entry["packet"].name,
                    loser_text=entry["text"][:100],
                    reason=(
                        "HARD is recorded and KEPT; a SOFT loser is dropped. "
                        "Higher layer wins; same-layer tie goes to the more "
                        "specific packet; a packet never resolves against itself."
                    ),
                    deleted=bool(delete_soft_loser) and not entry["hard"],
                ))
                if entry["hard"] or not delete_soft_loser:
                    break
                losing = True
                break
        if not losing:
            kept.append(entry)

    # Rebuild packets from kept directives
    #
    # ★ A PACKET THAT LOST NOTHING PASSES THROUGH BYTE-IDENTICAL (2026-10-15).
    # The rebuild joins blocks with a SINGLE newline and `_split_packet_directives`
    # strips every line, so a round trip through here used to destroy blank-line
    # structure and indentation even when it dropped nothing: measured on the
    # structural domain packet, 4,515 characters and 18 blocks in, 4,403 and 5
    # out, with 0 blocks lost. Harmless for a flat checklist; NOT harmless for
    # the project's own specification, which is markdown carrying fenced blocks,
    # formal notation and tables, all of which are delimited by blank lines.
    #
    # FOUND BY THE GUARD, NOT BY READING: once the specification was delivered
    # whole, `test_the_specification_survives_every_models_cap` compared its
    # first 400 characters against the render and they differed at the first
    # blank line. A rebuild that preserves content while silently reflowing
    # structure is the kind of lossy no-op this project keeps finding.
    kept_ids = {e["id"] for e in kept}
    total_by_packet: dict[int, int] = {}
    for e in entries:
        total_by_packet[e["packet_index"]] = total_by_packet.get(
            e["packet_index"], 0) + 1
    rebuilt_packets: list[DirectivePacket] = []
    for packet_index, packet in enumerate(composed.packets):
        kept_texts = [
            e["text"] for e in kept
            if e["packet_index"] == packet_index and e["id"] in kept_ids
        ]
        if not kept_texts:
            continue
        if len(kept_texts) == total_by_packet.get(packet_index, 0):
            # Nothing was dropped from this packet: hand back the original text.
            rebuilt_packets.append(packet)
            continue
        rebuilt_packets.append(DirectivePacket(
            layer=packet.layer,
            name=packet.name,
            text="\n".join(kept_texts),
            constraint_class=packet.constraint_class,
            domain=packet.domain,
            model=packet.model,
            tags=set(packet.tags),
        ))

    rendered = _render_directive_text(rebuilt_packets)
    cid = _compute_cid(rebuilt_packets, composed.manifest.get("model", "unknown"))
    token_estimate = max(len(rendered) // 4, 1)
    density = composed.constraint_count / token_estimate

    manifest = dict(composed.manifest)
    manifest["cid"] = cid
    manifest["resolved_conflicts"] = [
        {
            "topic": c.topic,
            "winner_layer": c.winner_layer,
            "winner_packet": c.winner_packet,
            "loser_layer": c.loser_layer,
            "loser_packet": c.loser_packet,
        }
        for c in conflicts
    ]

    resolved = ComposedDirectiveSet(
        packets=rebuilt_packets,
        rendered_text=rendered,
        policy=composed.policy,
        cid=cid,
        constraint_count=composed.constraint_count,
        token_estimate=token_estimate,
        constraint_density=density,
        coherence_budget=composed.coherence_budget,
        pruned_soft=list(composed.pruned_soft),
        manifest=manifest,
    )
    return resolved, conflicts


# ---------------------------------------------------------------------------
# Problem 5: Coherence threshold calibration from experiment data
# ---------------------------------------------------------------------------

def calibrate_coherence_thresholds(
    log_root: str | Path,
    *,
    quality_drop_fraction: float = 0.10,
    min_points_per_model: int = 5,
) -> dict[str, float]:
    """Calibrate per-model coherence budget thresholds from experiment data.

    Reads experiment log JSON files. Each entry should contain: model, chars,
    and a response field. The optimal threshold per model is the constraint
    density value above which finding quality (findings per 1000 tokens of
    response) drops by more than quality_drop_fraction from peak.

    Returns dict mapping model name → calibrated threshold.
    """
    log_dir = Path(log_root)
    model_samples: dict[str, list[tuple[float, float]]] = {}

    for json_path in sorted(log_dir.rglob("*.json")):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue

        entries = data if isinstance(data, list) else [data]

        for entry in entries:
            if not isinstance(entry, dict):
                continue
            model = entry.get("model") or entry.get("model_label")
            if not isinstance(model, str) or not model:
                continue

            # Extract density.
            #
            # ★ 2026-10-16: ALSO LOOK IN `metadata`, matching the idiom this
            # function already uses for `findings_count` two blocks below.
            # The runner records composer provenance through `save_output`'s
            # free-form `metadata` dict, so a top-level-only read found 0 of
            # 30,442 archived entries and fell through to the estimator every
            # time. The estimator is `(chars//70)/(chars//4)`, and 3,589 of
            # 3,709 entries carry `prompt_length = 203` -- the length of the
            # TRUNCATED prompt copy that `save_output` is passed -- so it
            # returned 2/50 = 0.04 for essentially every entry and every
            # calibrated threshold was an artefact of that constant.
            # Producer: scripts/what_budget_does_each_seat_actually_get_2026-10-16.py
            _meta = entry.get("metadata") or {}
            if not isinstance(_meta, dict):
                _meta = {}
            # ★ 2026-10-16 (CC3): A COMPOSER FALLBACK CARRIES NO CONSTRAINT
            # DATA, SO NO DENSITY IS ESTIMATED FROM IT.
            #
            # `_composer_record_fields` (bench/reference_runner_v3.py) writes
            # `composer_fallback: true` at 4 dispatch sites, deliberately
            # recording a FAILED composition rather than omitting the keys,
            # "since an absent key and a failed composition are different
            # facts". That is right, and until now nothing read the flag: it
            # was written at 4 sites and consumed at 0, which is the
            # addition-nothing-reaches class this project has confirmed 11
            # times since 2026-08-01.
            #
            # Worse than inert. The same helper writes `directive_chars` and
            # `prompt_chars_full` on the FALLBACK branch too, and both sit
            # AHEAD of `prompt_length` in the `or`-chain below, while
            # `constraint_count` is absent on that branch. So a fallback entry
            # took the `floor(c/70)/floor(c/4)` estimator on the FULL prompt
            # size. Executed 2026-10-16 on an 8-entry fixture: the archive's
            # old shape calibrates to 0.04 (the forced 1/25 that
            # scripts/the_recorded_prompt_length_forces_the_estimator_2026-10-16.py
            # measures at 3589/3709 entries), and the same entries with the
            # new fallback keys calibrate to 0.0567 -- the asymptote 2/35 of
            # the very same character arithmetic. The repair would therefore
            # have replaced an obviously-constant artefact with a
            # varying-and-so-credible one, computed from a prompt in which the
            # composer placed no constraints at all.
            #
            # Skipping is `simplest sufficient`: one guard, no new flag, no new
            # table. Archived entries carry no `composer_fallback` key, so
            # `is True` leaves every one of them on exactly the path it took
            # before and replay is unchanged.
            if (_meta.get("composer_fallback") is True
                    or entry.get("composer_fallback") is True):
                continue

            density = None
            _recorded = entry.get("constraint_density")
            if not isinstance(_recorded, (int, float)):
                _recorded = _meta.get("constraint_density")
            if isinstance(_recorded, (int, float)):
                density = float(_recorded)
            else:
                chars = (
                    entry.get("directive_chars")
                    or _meta.get("directive_chars")
                    or _meta.get("prompt_chars_full")
                    or entry.get("chars")
                    or entry.get("prompt_length")
                )
                if isinstance(chars, (int, float)) and chars > 0:
                    constraint_count = entry.get("constraint_count")
                    if not isinstance(constraint_count, (int, float)):
                        constraint_count = _meta.get("constraint_count")
                    if isinstance(constraint_count, (int, float)) and constraint_count > 0:
                        density = float(constraint_count) / max(int(chars) // 4, 1)
                    else:
                        density = max(int(chars) // 70, 1) / max(int(chars) // 4, 1)

            if density is None:
                continue

            # Extract response quality
            response = entry.get("response", "")
            response_text = (
                response if isinstance(response, str)
                else response.get("text", response.get("content", ""))
                if isinstance(response, dict) else str(response)
            )
            if not response_text:
                continue

            # Count findings
            findings_count = 0
            for key in ("findings_count", "N"):
                val = entry.get(key) or entry.get("metadata", {}).get(key)
                if isinstance(val, int) and val > 0:
                    findings_count = val
                    break

            if findings_count == 0:
                patterns = [
                    r"(?im)^FINDING_ID\s*:",
                    r"(?im)^finding\s*\d*\s*:",
                    r"(?im)^issue\s*\d*\s*:",
                    r"(?im)^problem\s*\d*\s*:",
                    r"(?im)^bug\s*\d*\s*:",
                ]
                findings_count = sum(
                    len(re.findall(p, response_text)) for p in patterns
                )
                if findings_count == 0:
                    paragraphs = [
                        p for p in response_text.split("\n\n")
                        if len(p.strip()) > 80
                    ]
                    findings_count = len(paragraphs)

            response_tokens = max(len(response_text) // 4, 1)
            quality = (findings_count / response_tokens) * 1000.0

            model_samples.setdefault(model, []).append((density, quality))

    # Compute thresholds
    thresholds: dict[str, float] = {}

    for model, samples in model_samples.items():
        if len(samples) < min_points_per_model:
            continue

        # Bin by density and average quality
        bins: dict[float, list[float]] = {}
        for d, q in samples:
            bucket = round(d, 4)
            bins.setdefault(bucket, []).append(q)

        curve = sorted(
            (d, sum(qs) / len(qs)) for d, qs in bins.items()
        )
        peak_density, peak_quality = max(curve, key=lambda pair: pair[1])

        threshold = peak_density
        seen_peak = False
        consecutive_drop_bins = 0

        for d, q in curve:
            if d < peak_density:
                continue
            if d == peak_density and not seen_peak:
                seen_peak = True
                threshold = d
                continue
            if q < peak_quality * (1.0 - quality_drop_fraction):
                consecutive_drop_bins += 1
                if consecutive_drop_bins >= 2 or d == curve[-1][0]:
                    break
            else:
                consecutive_drop_bins = 0
                threshold = d

        thresholds[model] = round(threshold, 4)

    # Fill in defaults for known models not in data
    for model, fallback in MODEL_COHERENCE_BUDGETS.items():
        thresholds.setdefault(model, fallback)

    return thresholds


def update_coherence_budgets_from_experiments(log_root: str | Path) -> None:
    """Convenience: calibrate and update the global MODEL_COHERENCE_BUDGETS."""
    calibrated = calibrate_coherence_thresholds(log_root)
    MODEL_COHERENCE_BUDGETS.update(calibrated)


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

def _render_directive_text(packets: list[DirectivePacket]) -> str:
    """Render the final assembled directive text from ordered packets.

    Canonical order: universal → domain → situation.
    Phenotype transform is already applied to individual packet text.
    """
    sections = []
    for packet in packets:
        if packet.text.strip():
            sections.append(packet.text.strip())
    return "\n\n---\n\n".join(sections)


# ---------------------------------------------------------------------------
# Composition identity
# ---------------------------------------------------------------------------

def _compute_cid(packets: list[DirectivePacket], model: str) -> str:
    """Compute a deterministic composition identity hash."""
    components = [
        f"{p.layer}:{p.name}:{len(p.text)}" for p in packets
    ]
    components.append(f"model:{model}")
    raw = "|".join(components)
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def compose(
    task_domain: str,
    model: str,
    situation: DirectivePacket | None = None,
    domain_variant: str | None = None,
    *,
    review_target: str = "",
    code_extracts: str = "",
    verified_facts: str = "",
    explicit_unknowns: str = "",
    adversarial_brief: str = "",
    interaction_surface: str = "",
    coherence_pruning: bool = False,
) -> ComposedDirectiveSet:
    """Compose a per-dispatch directive set from all applicable layers.

    This is the core function. It is:
    - Pure: no side effects, no state mutation
    - Deterministic: same inputs always produce same output
    - Fail-loud: raises on monotonicity violations, never silently degrades

    Args:
        task_domain: Problem domain (e.g. "mathematics", "software", "structural").
        model: Model config name (e.g. "opus_4_6", "codex_5_3").
        situation: Pre-built situation packet, OR use the keyword args below.
        domain_variant: Optional variant within domain (e.g. "bridge", "security").
        review_target: What is being reviewed (for auto-built situation packet).
        code_extracts: Code under review.
        verified_facts: Known facts.
        explicit_unknowns: What we don't know.
        adversarial_brief: Devil's advocate framing.
        interaction_surface: How the system interacts.

    Returns:
        ComposedDirectiveSet with rendered text, provenance, and coherence metrics.

    Raises:
        PolicyViolationError: if any composition weakens a HARD constraint.
    """
    packets: list[DirectivePacket] = []

    # --- Layer 1: Universal (NEVER pruned; minimal for small-context models) ---
    universal = _load_universal_directive(model=model)
    packets.append(universal)

    # --- Layer 2: Domain ---
    domain_packet = _load_domain_directive(task_domain, variant=domain_variant)
    if domain_packet:
        packets.append(domain_packet)

    # --- Layer 3: Phenotype transform (applied to existing packets) ---
    transform = PHENOTYPE_TRANSFORMS.get(model, PhenotypeTransform())

    # Apply phenotype transform to domain packet text (NOT to universal — HARD).
    #
    # REPLACED, NOT MUTATED (2026-09-10, task 2.2, falsifier for exp42 C0002).
    # CC2 raised this at severity 0.7 on 2026-06-06 and it was recorded
    # UNCONFIRMED with an empty falsifier and the verdict UNTOOLABLE. It is
    # entirely toolable: this function's own docstring promises "Pure: no side
    # effects, no state mutation" and these 2 lines wrote through to objects the
    # CALLER owns.
    #
    # NO LIVE CALLER WAS HARMED, and that is stated rather than implied.
    # `_load_domain_directive` builds a fresh packet per call and
    # `build_interaction_pattern` constructs a new DirectivePacket from the
    # preset tuple rather than handing back the preset, so nothing shared was
    # being corrupted. The defect was a false docstring and a latent trap for the
    # first caller to reuse a packet -- at which point the transform would
    # compound on each pass.
    packets = [
        replace(p, text=_apply_phenotype_transform(p.text, transform))
        if p.layer == "domain" else p
        for p in packets
    ]

    # --- Layer 4: Situation (per-dispatch) ---
    if situation is None and review_target:
        situation = _build_situation_packet(
            review_target=review_target,
            code_extracts=code_extracts,
            verified_facts=verified_facts,
            explicit_unknowns=explicit_unknowns,
            adversarial_brief=adversarial_brief,
            interaction_surface=interaction_surface,
        )
    if situation:
        # The caller's object is left exactly as it was handed in; the transform
        # goes onto a copy. See the note on the domain packets above.
        packets.append(
            replace(situation,
                    text=_apply_phenotype_transform(situation.text, transform)))

    # --- Build merged TOML policy ---
    from .registry import load_effective_policy, DOMAIN_MAP
    policy = load_effective_policy(domain=task_domain, model=model)

    # --- Coherence enforcement (with intra-packet pruning) ---
    # ABLATION SWITCH (2026-10-13 free panel, Item 5; default True preserves
    # behaviour byte-for-byte). `_prune_for_coherence` provably worsens the
    # density it enforces: `_count_constraints` reads only the merged TOML
    # policy, so the numerator is independent of the text, and a shorter text
    # strictly raises constraints-per-token (SymPy: d(L2)-d(L1) =
    # 4*C*(L1-L2)/(L1*L2) > 0 for L2 < L1; z3: "pruning shortened the text AND
    # density did not worsen" is unsat; committed proof:
    # bench/tests/test_falsifier_C0001_prune_inversion_2026-09-10.py). Whether
    # the pruning nonetheless helps the models it was built for is exactly the
    # kind of question the founder says simulated runs exist to answer, so the
    # next simulated run carries an arm with coherence_pruning=False
    # (cfg.composer_coherence_pruning) and the lean-vs-full comparison the
    # 2026-07-18 pruning review already gates every cut on.
    budget = MODEL_COHERENCE_BUDGETS.get(model, DEFAULT_COHERENCE_BUDGET)
    if coherence_pruning:
        packets, pruned_soft = _prune_for_coherence(packets, policy, budget)
    else:
        pruned_soft = []

    # --- Conflict resolution (Problem 4) ---
    # Build preliminary ComposedDirectiveSet for conflict resolver
    preliminary_rendered = _render_directive_text(packets)
    constraint_count = _count_constraints(policy)
    preliminary_cid = _compute_cid(packets, model)

    preliminary = ComposedDirectiveSet(
        packets=packets,
        rendered_text=preliminary_rendered,
        policy=policy,
        cid=preliminary_cid,
        constraint_count=constraint_count,
        token_estimate=max(len(preliminary_rendered) // 4, 1),
        constraint_density=constraint_count / max(len(preliminary_rendered) // 4, 1),
        coherence_budget=budget,
        pruned_soft=pruned_soft,
        manifest={
            "model": model,
            "domain": task_domain,
            "domain_variant": domain_variant,
        },
    )
    resolved, conflict_log = resolve_layer_conflicts(preliminary)
    packets = resolved.packets

    # --- Render ---
    rendered = _render_directive_text(packets)

    # Apply global phenotype length cap.
    #
    # ★ RECORDED, NOT SILENT (2026-10-14, joint round J1, fable's finding,
    # verified independently by CC1 before applying).
    #
    # THE DEFECT. This cap runs on the FINAL render, AFTER packet assembly, so a
    # packet is listed in `manifest["packets"]` at its full length while the cap
    # has removed most of its text from what was actually delivered. Measured on
    # the real compose path with the pruner retired: deepseek_v3 (cap 4000)
    # receives 49% of the domain directive and **1 character of the situation
    # packet** -- the review target, the code extracts and the adversarial brief
    # -- while the manifest claimed full delivery and `pruned_soft` was empty.
    # 2 of 10 model x domain rows are cut, 20.0000%, Wilson [5.6682%, 50.9838%].
    #
    # WHY THE EXISTING GUARD CANNOT SEE IT.
    # `test_falsifier_C0001_prune_inversion_2026-09-10.py` counts packet
    # MEMBERSHIP (`"domain" not in {p.layer for p in c.packets}`), which is the
    # layer ABOVE the cap, so its 0-of-50 with pruning off is consistent with
    # total text loss underneath.
    #
    # WHAT THIS CHANGES AND WHAT IT DOES NOT. It makes the manifest TRUTHFUL. It
    # changes NO delivered byte -- asserted by
    # `test_the_manifest_records_the_length_cap_cut_2026-10-14.py`. It does NOT
    # remove or raise the cap: both panel seats refused outright removal on the
    # additive standard, since no committed measurement shows removal dominates,
    # and that measurement belongs to the next simulated run.
    #
    # THE OFFSET ARITHMETIC IS EXACT, not approximate. `_render_directive_text`
    # joins `packet.text.strip()` in packet order with "\n\n---\n\n" and skips
    # empty packets, so cumulative offsets locate each packet precisely. Verified
    # by execution against the live renderer at all 3 packet positions before
    # this was applied.
    #
    # Producer: `scripts/the_cap_cuts_what_the_manifest_claims_2026-10-14.py`.
    # ★ THE CAP BOUNDS WORK AND EXEMPTS THE SPECIFICATION — founder's ruling
    # 2026-10-14, applied 2026-10-15. Before this, the cap ran against the whole
    # assembled render with the universal specification FIRST in packet order.
    # Delivering the specification whole under that arithmetic would have
    # truncated INSIDE the specification and deleted the domain and situation
    # packets outright for every seat whose work bound is below 27,803 -- which
    # is all 5. So the repair that delivers the specification and the repair
    # that keeps the cap meaningful are the SAME repair, and neither is safe
    # alone.
    #
    # `max_directive_chars` KEEPS ITS VALUE AND ITS JOB: deepseek_v3 still
    # receives at most 4000 characters of domain-plus-situation work, which is
    # the quantity the harness measures per experiment and the quantity the
    # routing ladder respects. What changes is that the specification no longer
    # competes with the work for that budget.
    _spec_chars = sum(
        len(p.text.strip()) for p in packets if p.layer == "universal"
    )
    _sep_chars = len("\n\n---\n\n") if _spec_chars else 0
    _effective_cap = _spec_chars + _sep_chars + transform.max_directive_chars
    length_cap_record: dict[str, Any] = {
        "fired": False,
        "cap": transform.max_directive_chars,
        "work_cap": transform.max_directive_chars,
        "spec_chars_exempt": _spec_chars,
        "effective_cap": _effective_cap,
        "chars_cut": 0,
        "packets_cut": [],
    }
    if len(rendered) > _effective_cap:
        kept = rendered[: _effective_cap]
        length_cap_record["fired"] = True
        length_cap_record["chars_cut"] = len(rendered) - len(kept)
        offset = 0
        sep = len("\n\n---\n\n")
        for p in packets:
            body = p.text.strip()
            if not body:
                continue
            survived = min(max(len(kept) - offset, 0), len(body))
            if survived < len(body):
                length_cap_record["packets_cut"].append({
                    "layer": p.layer,
                    "name": p.name,
                    "chars_delivered": survived,
                    "chars_total": len(body),
                })
            offset += len(body) + sep
        rendered = kept + "\n[... work truncated for model capacity; "\
                   "the CDSFL specification above is complete]"

    # --- Metrics ---
    token_estimate = max(len(rendered) // 4, 1)
    density = constraint_count / token_estimate

    # --- Provenance ---
    cid = _compute_cid(packets, model)
    manifest = {
        "cid": cid,
        "model": model,
        "domain": task_domain,
        "domain_variant": domain_variant,
        "packets": [
            {
                "layer": p.layer,
                "name": p.name,
                "chars": len(p.text),
                "class": p.constraint_class,
            }
            for p in packets
        ],
        "pruned_soft": pruned_soft,
        "length_cap": length_cap_record,
        "constraint_count": constraint_count,
        "token_estimate": token_estimate,
        "constraint_density": round(density, 6),
        "coherence_budget": budget,
        "conflicts_resolved": len(conflict_log),
        "conflict_log": [
            {
                "topic": c.topic,
                "winner": f"{c.winner_layer}:{c.winner_packet}",
                "loser": f"{c.loser_layer}:{c.loser_packet}",
            }
            for c in conflict_log
        ],
        "phenotype_transform": {
            "max_directive_chars": transform.max_directive_chars,
            "spec_chars": transform.spec_chars,
            "strip_examples": transform.strip_examples,
            "strip_rationale": transform.strip_rationale,
            "simplify_language": transform.simplify_language,
            "compress_tables": transform.compress_tables,
            "format_style": transform.format_style,
        },
    }

    # --- Final monotonicity check ---
    _check_monotonicity(policy, f"composed/{cid}")

    # --- Budget warning ---
    if density > budget:
        import warnings
        warnings.warn(
            f"Composer: {model} over coherence budget "
            f"(density={density:.4f}, budget={budget}). "
            # ★ 2026-10-16 (CC3): THE WARNING NO LONGER ASSERTS A PENALTY
            # THAT IS NOT IN FORCE. It read "Coherence penalty κ(m,g) < 1
            # applies to effective detection", and nothing in this repository
            # computes or applies such a κ. Executed: the only match for
            # "κ" in bench/cdsfl_registry/ was this string, and every
            # `kappa` in the live tree is `kappa_set`, the convergence metric
            # of §7.13 -- a different quantity entirely. An operator reading
            # the log was told a detection penalty had been applied to this
            # dispatch. None had. The budget comparison IS real and is still
            # reported; only the unsupported consequence is withdrawn.
            f"No detection penalty is applied: this is a density report, and "
            f"the only effectful consumer of the budget, _prune_for_coherence, "
            f"is retired by default (founder ruling 2026-10-13). "
            f"Pruned: {pruned_soft or 'nothing further prunable'}.",
            stacklevel=2,
        )

    return ComposedDirectiveSet(
        packets=packets,
        rendered_text=rendered,
        policy=policy,
        cid=cid,
        constraint_count=constraint_count,
        token_estimate=token_estimate,
        constraint_density=density,
        coherence_budget=budget,
        pruned_soft=pruned_soft,
        manifest=manifest,
    )


# ---------------------------------------------------------------------------
# Problem 6: Orchestrator integration helpers
# ---------------------------------------------------------------------------

# Model name mapping: orchestrator labels → composer model keys
COMPOSER_MODEL_MAP: dict[str, str] = {
    "CC2": "opus_4_6",
    "Codex": "codex_5_3",
    "CX": "codex_5_3",
    "ChatGPT": "chatgpt_5_4",
    "Gemini": "gemini_3_1_pro",
    "DeepSeek": "deepseek_v3",
    # Direct model keys also work
    "opus_4_6": "opus_4_6",
    "codex_5_3": "codex_5_3",
    "chatgpt_5_4": "chatgpt_5_4",
    "gemini_3_1_pro": "gemini_3_1_pro",
    "deepseek_v3": "deepseek_v3",
}


def compose_for_dispatch(
    model_label: str,
    task_domain: str = "software",
    *,
    domain_variant: str | None = None,
    review_target: str = "",
    code_extracts: str = "",
    verified_facts: str = "",
    explicit_unknowns: str = "",
    adversarial_brief: str = "",
    interaction_surface: str = "",
) -> ComposedDirectiveSet:
    """Convenience wrapper for orchestrator integration.

    Accepts orchestrator model labels (CC2, CX, ChatGPT, Gemini, DeepSeek)
    and maps them to composer model keys. Returns the ComposedDirectiveSet
    whose .rendered_text replaces the static system prompt.

    Usage in orchestrator:
        from cdsfl_registry.composer import compose_for_dispatch
        composed = compose_for_dispatch("DeepSeek", "software",
            review_target="Review the dispatch efficiency...")
        system_prompt = composed.rendered_text
    """
    composer_model = COMPOSER_MODEL_MAP.get(model_label, model_label)
    return compose(
        task_domain=task_domain,
        model=composer_model,
        domain_variant=domain_variant,
        review_target=review_target,
        code_extracts=code_extracts,
        verified_facts=verified_facts,
        explicit_unknowns=explicit_unknowns,
        adversarial_brief=adversarial_brief,
        interaction_surface=interaction_surface,
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    """Demo: compose directives for each model on a sample task."""
    models = [
        "opus_4_6", "codex_5_3", "chatgpt_5_4", "gemini_3_1_pro", "deepseek_v3"
    ]
    domain = "software"

    print("=" * 70)
    print("CDSFL Dynamic Composer — Demo")
    print("=" * 70)

    for model in models:
        result = compose(
            task_domain=domain,
            model=model,
            review_target="Review the dispatch efficiency of the multi-model orchestrator.",
            verified_facts=(
                "1. CX takes ~480s per dispatch vs ChatGPT ~35s.\n"
                "2. Same base model (gpt-5.4)."
            ),
            explicit_unknowns="1. Whether CLI overhead accounts for the difference.",
            adversarial_brief="The real bottleneck may be outside the code shown.",
        )
        print(f"\n--- {model} (CID: {result.cid}) ---")
        print(f"  Packets: {len(result.packets)}")
        print(f"  Rendered: {len(result.rendered_text)} chars (~{result.token_estimate} tokens)")
        print(f"  Constraints: {result.constraint_count}")
        print(f"  Density: {result.constraint_density:.4f} (budget: {result.coherence_budget})")
        print(f"  Pruned: {result.pruned_soft or 'none'}")
        print(f"  Conflicts resolved: {result.manifest.get('conflicts_resolved', 0)}")
        print(f"  Manifest: {json.dumps(result.manifest, indent=2)}")

    print("\n" + "=" * 70)
    print("All compositions valid. No monotonicity violations.")


if __name__ == "__main__":
    main()
