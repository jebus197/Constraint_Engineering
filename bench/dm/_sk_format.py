"""S_k SEARCH/REPLACE format pre-check (Item 1D.5).

When a finding has a ``proposed_fix`` but the fix is not emitted in the
``<<<< SEARCH ... ==== ... >>>> REPLACE`` format, the S_k solution
verification pipeline cannot evaluate it.  In Exp 39-0 the outcome was
silent rejection: the finding was admitted, but S_k reported
"no blocks for target" and moved on.

This module provides a fast, non-parsing structural check plus a helper
to build reformat requests for inclusion in the next round's prompt
prefix — giving the model a concrete correction target instead of
relying on global directive hygiene.
"""

from __future__ import annotations

import re
from typing import List, Sequence, Tuple

_SEARCH_RE = re.compile(r'<<<<\s*SEARCH', re.IGNORECASE)
_SEPARATOR_RE = re.compile(r'^====', re.MULTILINE)
_CLOSER_RE = re.compile(r'^>>>>', re.MULTILINE)


def check_sk_format_admissible(proposed_fix: str) -> Tuple[bool, str]:
    """Check whether ``proposed_fix`` is parseable as an S_k SEARCH/REPLACE block.

    Returns ``(is_admissible, diagnostic_reason)``.  On success ``reason``
    is the empty string.  On failure ``reason`` is a short human-readable
    explanation suitable for embedding in a reformat-request prompt.

    The check is structural only — it does not attempt to apply the
    replacement.  A ``True`` result means the block structure is present;
    ``parse_search_replace_blocks`` still handles edge cases like
    ambiguous SEARCH text.
    """
    if not proposed_fix or not proposed_fix.strip():
        return False, "proposed_fix is empty"

    has_search = bool(_SEARCH_RE.search(proposed_fix))
    has_separator = bool(_SEPARATOR_RE.search(proposed_fix))
    has_closer = bool(_CLOSER_RE.search(proposed_fix))

    if not has_search and not has_separator and not has_closer:
        # Pure prose / freeform description.
        return False, "no SEARCH/REPLACE markers — emit <<<< SEARCH <file> ... ==== ... >>>> REPLACE"
    if not has_search:
        return False, "missing '<<<< SEARCH <file_path>' opener"
    if not has_separator:
        return False, "missing '====' separator between SEARCH and REPLACE"
    if not has_closer:
        return False, "missing '>>>>' closer at end of REPLACE"

    # Late import to avoid reference_runner_v2 importing us at module load
    # creating a circular path.
    try:
        from bench.reference_runner_v2 import parse_search_replace_blocks
    except ImportError:
        return True, ""  # structural markers present is sufficient for now

    blocks = parse_search_replace_blocks(proposed_fix)
    if not blocks:
        return False, "markers present but no valid blocks parsed — check SEARCH text, file path, and delimiter balance"

    return True, ""


def build_reformat_requests(
    findings_needing_reformat: Sequence[Tuple[str, str]],
    max_entries: int = 10,
    max_chars: int = 2000,
) -> str:
    """Build a reformat-request section for the next round's prompt prefix.

    Args:
        findings_needing_reformat: Sequence of
            ``(canonical_id, diagnostic_reason)`` pairs identifying
            findings whose proposed_fix did not parse as an S_k block.
        max_entries: Cap on number of reformat entries.
        max_chars: Truncation cap on total output length.

    Returns:
        A multi-line plain-text block suitable for injection into the
        ``registry_summary`` prompt prefix, or the empty string if no
        findings need reformat.
    """
    if not findings_needing_reformat:
        return ""

    # Exp 40 fix 1e (post-continuation 15 May 2026): strengthen the
    # reformat request with an explicit STRUCTURE_VIOLATION header and a
    # strict, non-negotiable template. The continuation showed 4-5
    # fixes/round arriving as freeform prose that the S_k extractor
    # could not parse; the prior soft "Re-emit each in the canonical
    # format" wording under-signalled that the format is mandatory.
    # This is the strengthened next-round reject-and-reformat path. An
    # in-round re-dispatch variant (re-send the model its own output
    # mid-round, parse the retry before reconciliation closes) is
    # deliberately deferred: the next-round path is bounded and cheap,
    # whereas an in-round loop adds a new dispatch path, per-round
    # cost, and loop risk for a one-round timing gain. Escalation
    # trigger for the in-round variant: if R17-R21 still shows a
    # material rate of *non-stale* fixes failing extraction AFTER this
    # strengthened request (i.e. the model received the
    # STRUCTURE_VIOLATION header and still produced unparseable output),
    # implement the in-round re-dispatch as a dedicated change. Stale
    # findings (proposed_fix targeting already-modified source) are
    # NOT in scope for either path — they are correctly rejected.
    kept: List[str] = [
        "=== STRUCTURE_VIOLATION — MANDATORY REFORMAT ===",
        "",
        "The proposed fixes listed below were REJECTED. Each one's "
        "PROPOSED_FIX did not parse as an S_k SEARCH/REPLACE block, so "
        "the fix could not be verified or closed. A fix that does not "
        "parse is treated as no fix at all.",
        "",
        "You MUST re-emit each listed fix in EXACTLY this format — no "
        "prose, no markdown fences, no commentary inside the block:",
        "",
        "    <<<< SEARCH <file_path>",
        "    <exact verbatim source text to find>",
        "    ====",
        "    <replacement text>",
        "    >>>> REPLACE",
        "",
        "Rules (all mandatory):",
        "  1. <file_path> is the real path to the target file.",
        "  2. The SEARCH text must be copied byte-for-byte from the "
        "current source — no paraphrase, no '...' elision.",
        "  3. The four markers (<<<< SEARCH, ====, >>>> REPLACE) must "
        "appear exactly, each on its own line.",
        "  4. One block per fix. Do not wrap the block in backticks.",
        "",
        "Findings requiring reformat (canonical id: why it failed):",
    ]
    for canonical_id, reason in list(findings_needing_reformat)[:max_entries]:
        kept.append(f"  - {canonical_id}: {reason}")
    extras = len(findings_needing_reformat) - max_entries
    if extras > 0:
        kept.append(f"  ... and {extras} more (not shown)")

    text = "\n".join(kept)
    if len(text) > max_chars:
        text = text[:max_chars].rsplit("\n", 1)[0] + "\n  ... (truncated)"
    return text
