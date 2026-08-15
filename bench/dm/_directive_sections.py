"""Directive-section selection — omit a named mechanism's directive text.

Why this exists
---------------

The Exp 52 capstone is a 2x2 factorial: the same frozen target is run four
times, crossing the §17 feedback channel (off/on) with the §18 divergence
directive (off/on), and the recall difference between cells is attributed to
the mechanisms. That design only works if "off" actually removes something.

Before this module, "off" could remove at most *half* of each mechanism:

* the feedback channel had a runner-side switch (``feedback_channel_enabled``)
  that stopped the SCHEMA FEEDBACK section being assembled, but the §17
  directive text — which tells the model the channel exists and is
  prescriptive — was sent to every model regardless;
* the divergence directive had no switch at all: the runner hard-coded
  ``DivergenceConfig(enabled=True)`` and the §18 directive text was likewise
  sent unconditionally.

This module supplies the missing directive-text half: given the assembled
system prompt and a set of factors to suppress, it returns the prompt with
those factors' directive material removed cleanly.

What "removed cleanly" means
----------------------------

Three kinds of material belong to a factor and all three are removed:

1. **The section itself** — the whole ``## `` heading block, including the
   markdown horizontal rule that separates it from its neighbour, so the
   result contains no orphan heading and no doubled ``---`` separator.
2. **Dedicated cross-reference paragraphs elsewhere** — e.g. §18 carries a
   paragraph headed ``**Interaction with §17 feedback.**`` whose entire
   subject is the feedback channel. Left behind when §17 is omitted, it
   would point the model at a section it cannot see. These are declared
   explicitly per factor (``dependent_paragraph_patterns``), not detected
   heuristically, so every removal is auditable.
3. **Policy-dump lines** — the registry composer renders the effective
   policy as flat ``policy.<group>.<key>=<value>`` lines into the same
   system prompt. ``policy.divergence.min_alternatives=1`` is a divergence
   mandate in miniature, so those lines go too.

Numbering is deliberately **not** renumbered. The directive's sections
cross-reference each other by number throughout (§3, §15, §16 …); renumbering
would silently redirect every one of those references. A gap in the sequence
(``## 16`` followed by ``## §18``) is honest and self-evident to a reader;
a section 17 that is secretly the old section 18 is not.

Failure mode this module refuses to have
----------------------------------------

A section-omission function that quietly does nothing when it cannot find its
target is exactly the silent-drop failure that has already collapsed three
CDSFL config keys (see ``feedback_launcher_config_drop``). So
:func:`omit_directive_sections` raises :class:`DirectiveSectionError` when a
requested factor's section heading is absent from the text. A loud crash
before the money is spent beats a null result after.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Sequence, Tuple

__all__ = [
    "DirectiveSectionError",
    "FactorSpec",
    "FACTOR_SPECS",
    "omit_directive_sections",
    "find_section_span",
]


class DirectiveSectionError(RuntimeError):
    """Raised when a requested directive section cannot be located.

    Deliberately fatal: a no-op omission produces a factorial cell that is
    byte-identical to its counterpart, i.e. a guaranteed null result that
    looks like a real measurement.
    """


@dataclass(frozen=True)
class FactorSpec:
    """Everything that belongs to one experimental factor's directive text.

    Attributes
    ----------
    name
        Factor key used in configs and logs (``"feedback"`` / ``"divergence"``).
    section_heading_re
        Matches the ``## `` heading line that opens the factor's section.
        Written against the section *number* rather than its title, because
        the numbers are what the rest of the directive cross-references.
    heading_keyword
        A word the heading must also contain. If the number matches but the
        keyword does not, the directive file has been renumbered underneath
        us and we refuse to guess — see :class:`DirectiveSectionError`.
    dependent_paragraph_res
        Matches the FIRST line of a paragraph elsewhere in the directive
        whose entire subject is this factor. Removed with the section.
        Best-effort: a dependent that is already gone (because it lived
        inside another omitted section) is not an error.
    policy_line_prefixes
        Prefixes of composer policy-dump lines belonging to this factor.
        Best-effort for the same reason: a prompt assembled without the
        composer carries no policy dump at all.
    """

    name: str
    section_heading_re: re.Pattern
    heading_keyword: str
    dependent_paragraph_res: Sequence[re.Pattern] = field(default_factory=tuple)
    policy_line_prefixes: Sequence[str] = field(default_factory=tuple)


# ── Factor registry ──────────────────────────────────────────────────────────
#
# Headings as they stand in bench/directives/universal/cdsfl_operational.md:
#
#     ## 17. Feedback Channel — Corrective Loop (Load-Bearing)
#     ## §18 Divergence Directive
#
# The two use different numbering styles (bare "17." vs "§18"), hence the
# optional section-sign in the pattern.

FACTOR_SPECS: Dict[str, FactorSpec] = {
    "feedback": FactorSpec(
        name="feedback",
        section_heading_re=re.compile(r"^##\s+§?\s*17(?![0-9])"),
        heading_keyword="feedback",
        dependent_paragraph_res=(
            # §18's paragraph about how divergence interacts with the
            # feedback channel. Meaningless once §17 is absent.
            re.compile(r"^\*\*Interaction with §?\s*17\b", re.IGNORECASE),
        ),
        policy_line_prefixes=("policy.feedback_channel.",),
    ),
    "divergence": FactorSpec(
        name="divergence",
        section_heading_re=re.compile(r"^##\s+§?\s*18(?![0-9])"),
        heading_keyword="divergence",
        dependent_paragraph_res=(),
        policy_line_prefixes=("policy.divergence.",),
    ),
}


_H2_RE = re.compile(r"^##\s")
_H1_RE = re.compile(r"^#\s")
_RULE_RE = re.compile(r"^\s*-{3,}\s*$")


def _is_boundary(line: str) -> bool:
    """True if `line` opens a new top-level (h1 or h2) directive section.

    ``### 8.1`` is deliberately NOT a boundary: sub-sections belong to their
    parent. (``"### x".startswith("## ")`` is False, so the h2 test already
    excludes them; the explicit note is here so a future edit does not
    "helpfully" loosen the pattern.)
    """
    return bool(_H2_RE.match(line) or _H1_RE.match(line))


def find_section_span(lines: Sequence[str], spec: FactorSpec) -> Tuple[int, int]:
    """Return the half-open ``[start, end)`` line span of `spec`'s section.

    The span starts at the heading line and ends at the line before the next
    top-level heading (or end of text). Raises :class:`DirectiveSectionError`
    if the heading is absent, or present but carrying an unexpected title.
    """
    start = -1
    for i, line in enumerate(lines):
        if spec.section_heading_re.match(line):
            if spec.heading_keyword.lower() not in line.lower():
                raise DirectiveSectionError(
                    f"factor {spec.name!r}: heading matched the section number "
                    f"but not the expected keyword {spec.heading_keyword!r} — "
                    f"got {line.strip()!r}. The directive file has been "
                    f"renumbered or retitled; refusing to guess which section "
                    f"is the {spec.name} mechanism."
                )
            start = i
            break
    if start < 0:
        raise DirectiveSectionError(
            f"factor {spec.name!r}: no section heading matching "
            f"{spec.section_heading_re.pattern!r} found in the directive text. "
            f"Omission would be a silent no-op, which for a factorial cell "
            f"means a guaranteed null result."
        )

    end = len(lines)
    for j in range(start + 1, len(lines)):
        if _is_boundary(lines[j]):
            end = j
            break
    return start, end


def _expand_span_over_separator(
    lines: Sequence[str], start: int, end: int,
) -> Tuple[int, int]:
    """Widen ``[start, end)`` so that EXACTLY ONE ``---`` separator goes with it.

    Sections here are written ``…body… / --- / ## Heading / …body…``, so the
    separator that visually precedes a heading actually belongs, structurally,
    to the section BEFORE it. A section's span — heading up to the next
    top-level heading — therefore already contains the rule that follows its
    own body.

    Two cases:

    * **Span already ends in a rule** (every section but the last). Deleting
      the span removes one separator along with one section, which is right.
      Absorbing the PRECEDING rule as well would remove two separators for one
      section and leave the surviving neighbours jammed together with no rule
      and no blank line between them — the exact "dangling" outcome this
      module exists to prevent.
    * **Span ends without a rule** (the last section in the file). Deleting
      only the span would strand the preceding rule at the end of the
      document, so that rule is absorbed instead, together with the blank
      lines around it.
    """
    tail = end - 1
    while tail >= start and not lines[tail].strip():
        tail -= 1
    if tail >= start and _RULE_RE.match(lines[tail]):
        return start, end  # span already carries its own trailing separator

    new_start = start
    k = start - 1
    while k >= 0 and not lines[k].strip():
        k -= 1
    if k >= 0 and _RULE_RE.match(lines[k]):
        new_start = k
        while new_start > 0 and not lines[new_start - 1].strip():
            new_start -= 1
    return new_start, end


def _drop_dependent_paragraphs(
    lines: List[str], patterns: Iterable[re.Pattern],
) -> List[str]:
    """Remove whole paragraphs whose FIRST line matches any pattern.

    A paragraph is a maximal run of non-blank lines. The paragraph's trailing
    blank line is removed with it so the surrounding prose does not gain an
    extra gap.
    """
    pats = list(patterns)
    if not pats:
        return lines
    out: List[str] = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        if line.strip() and any(p.match(line) for p in pats):
            j = i
            while j < n and lines[j].strip():
                j += 1
            while j < n and not lines[j].strip():
                j += 1
            i = j
            continue
        out.append(line)
        i += 1
    return out


def _drop_policy_lines(lines: List[str], prefixes: Iterable[str]) -> List[str]:
    pfx = tuple(prefixes)
    if not pfx:
        return lines
    return [ln for ln in lines if not ln.lstrip().startswith(pfx)]


def _merge_spans(spans: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    """Coalesce overlapping or touching line spans.

    Two adjacent sections can lay claim to the same separator: the earlier
    section's span ends with the rule that the later section — if it is last
    in the file — absorbs as its own leading separator. Deleting overlapping
    ranges independently corrupts the indices, so they are merged first.
    """
    if not spans:
        return []
    merged = [spans[0]]
    for start, end in sorted(spans)[1:]:
        last_start, last_end = merged[-1]
        if start <= last_end:
            merged[-1] = (last_start, max(last_end, end))
        else:
            merged.append((start, end))
    return merged


def _normalise_blank_runs(text: str) -> str:
    """Collapse runs of 3+ blank lines to 2, drop a stranded trailing rule,
    and trim the edges.

    Purely cosmetic, but the point of this module is that an omitted-section
    prompt should look like a prompt that never had the section, not like a
    prompt someone cut a hole in. A document that ends on a horizontal rule
    is the tell-tale of a cut-out final section.
    """
    text = re.sub(r"\n{3,}", "\n\n", text).rstrip()
    while True:
        stripped = re.sub(r"\n\s*-{3,}\s*$", "", text)
        if stripped == text:
            break
        text = stripped.rstrip()
    return text + "\n"


def omit_directive_sections(
    text: str,
    factors: Iterable[str],
    *,
    strict: bool = True,
) -> str:
    """Return `text` with every named factor's directive material removed.

    Parameters
    ----------
    text
        The assembled system prompt: composer policy dump + core directive +
        operational directive, in whatever order the caller built it.
    factors
        Factor keys from :data:`FACTOR_SPECS` (``"feedback"``,
        ``"divergence"``). Unknown keys raise :class:`DirectiveSectionError`
        — a typo in a config must not silently leave the mechanism running.
    strict
        When True (default) a missing section heading is fatal. Set False
        only for callers operating on text that legitimately may not carry
        the operational directive (e.g. connectivity preflight).

    Returns
    -------
    str
        The prompt with the factors' sections, dedicated cross-reference
        paragraphs, and policy-dump lines removed, and blank-line runs
        normalised.
    """
    wanted = list(factors)
    if not wanted:
        return text

    specs: List[FactorSpec] = []
    for key in wanted:
        spec = FACTOR_SPECS.get(key)
        if spec is None:
            raise DirectiveSectionError(
                f"unknown directive factor {key!r}; known factors: "
                f"{sorted(FACTOR_SPECS)}"
            )
        specs.append(spec)

    lines = text.splitlines()

    # 1. Whole sections. Collect spans first, then delete back-to-front so
    #    earlier indices stay valid.
    spans: List[Tuple[int, int]] = []
    for spec in specs:
        try:
            start, end = find_section_span(lines, spec)
        except DirectiveSectionError:
            if strict:
                raise
            continue
        spans.append(_expand_span_over_separator(lines, start, end))
    for start, end in sorted(_merge_spans(spans), reverse=True):
        del lines[start:end]

    # 2. Dedicated cross-reference paragraphs left behind in retained text.
    for spec in specs:
        lines = _drop_dependent_paragraphs(lines, spec.dependent_paragraph_res)

    # 3. Composer policy-dump lines.
    for spec in specs:
        lines = _drop_policy_lines(lines, spec.policy_line_prefixes)

    return _normalise_blank_runs("\n".join(lines))
