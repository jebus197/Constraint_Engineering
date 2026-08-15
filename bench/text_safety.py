"""Make external text safe to carry through the system.

Everything the panel touches eventually gets encoded as UTF-8: written to a log,
piped to a subprocess as a prompt, or serialised into a run report. A Python
string can hold a character that cannot be encoded at all, and nothing complains
until the encode — which is usually a long way from where the character entered.

The character is a LONE SURROGATE. Codepoints U+D800 to U+DFFF exist only as the
two halves of a UTF-16 pair; a single one is not a character. Python stores it
happily. UTF-8 refuses it. So a string containing one behaves normally until it
crosses a boundary, and then it raises.

They arrive with text extracted from PDFs. U+D835 is the usual one — the high
half of the mathematical-alphanumeric block, so it is common in exactly the
papers the literature-retrieval cell fetches. Found 2026-07-31 while wiring that
cell's brief into the panel prompt.

Three boundaries were measured. All three are real:

    subprocess stdin (CC2, Codex)  UnicodeEncodeError  — kills the round mid-run
    log file write                 UnicodeEncodeError  — kills whatever logs it
    run report (strict, no-ASCII)  UnicodeEncodeError  — run completes, no report

Only the JSON request body survives, and only by accident: `json.dumps` defaults
to `ensure_ascii=True`, which escapes the surrogate rather than encoding it, so
the vendor's parser receives it and the problem becomes someone else's.

Scrub at INGEST, not at each boundary. There is one place text enters and many
places it leaves, and a guard on every exit is a guard that will be forgotten on
the next exit added.
"""
from __future__ import annotations

import re
from typing import Optional

# Any surrogate codepoint present in a Python str is by definition unpaired:
# astral characters are stored as a single codepoint, never as a pair. So this
# pattern cannot match legitimate text.
_SURROGATES = re.compile(r"[\ud800-\udfff]")

REPLACEMENT = "�"  # U+FFFD REPLACEMENT CHARACTER — the standard marker


def has_unencodable(text: str) -> bool:
    """True if `text` would raise on a strict UTF-8 encode."""
    return bool(_SURROGATES.search(text))


def scrub_surrogates(text: str, where: str = "", log=None) -> str:
    """Return `text` safe to encode as UTF-8.

    Clean text is returned unchanged — the same object, not a copy — so this is
    cheap enough to call on every piece of external text. Only when a surrogate
    is actually present is anything allocated or logged.

    Degradation is announced. A silently scrubbed brief reads exactly like a
    clean one, and the whole point of the retrieval cell is that a human can
    check what the panel was given.

    Args:
        text:  the string to make safe.
        where: short description of the source, used only in the warning.
        log:   optional callable for the warning; falls back to `warnings`.
    """
    if not text or not _SURROGATES.search(text):
        return text
    scrubbed, n = _SURROGATES.subn(REPLACEMENT, text)
    msg = (f"{n} unpaired surrogate(s) replaced with U+FFFD"
           f"{f' in {where}' if where else ''} — this text cannot be encoded as "
           f"UTF-8 and would otherwise break the prompt, the log or the report")
    if log is not None:
        log(f"  *** WARNING: {msg} ***")
    else:  # pragma: no cover — exercised only when no logger is threaded through
        import warnings
        warnings.warn(msg, RuntimeWarning, stacklevel=2)
    return scrubbed


def scrub_deep(obj, where: str = "", log=None):
    """Recursively scrub every string in a dict/list/tuple structure.

    For whole payloads assembled from external text — a retrieved paper's
    metadata, say — where the offending string may sit at any depth.
    """
    if isinstance(obj, str):
        return scrub_surrogates(obj, where, log)
    if isinstance(obj, dict):
        return {scrub_deep(k, where, log): scrub_deep(v, where, log)
                for k, v in obj.items()}
    if isinstance(obj, list):
        return [scrub_deep(v, where, log) for v in obj]
    if isinstance(obj, tuple):
        return tuple(scrub_deep(v, where, log) for v in obj)
    return obj
