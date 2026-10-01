"""A python listing in a LIST ITEM must not be triaged as pure prose.

FREE PANEL, 2026-10-01, Q2. `_MD_PY_FENCE_ANY`'s prefix group admitted only
spaces, tabs and blockquote markers, so a fence opened on the same line as a
list marker matched nothing -- and `_gateable_source` reports exactly that as
"target carries no code; syntax gates not applicable". A document WITH code was
therefore gated as prose and S_k reached NO_SCORE on it.

THE ARBITER IS A REAL PARSER, NOT THIS FILE'S OPINION. `markdown-it-py` is a
port of the CommonMark reference implementation and `mistune` is the second
tool; a form counts as a listing only if a parser extracts non-empty python
from it. The two non-material forms are kept in the table on purpose, so a
future widening that starts matching them fails here rather than passing
quietly:

  * "See: ```python" is not a code fence to either parser, and the UNANCHORED
    orphan pattern accepting it was a defect, not a capability.
  * "- ```python" with a col-0 body is a VALID fence whose content is EMPTY,
    because the col-0 line closes the list item before the body is reached.

The additive half is guarded too: `scripts/md_fence_marker_is_additive_2026-10-01.py`
compares the pre-widening pattern with the live one over 7069 documents and
requires 0 lost and 0 changed bodies. This file requires the GAIN.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
for _p in (str(ROOT), str(ROOT / "bench")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

FALSIFIER = ROOT / "scripts" / "md_fence_prefix_blind_spot_2026-10-01.py"
ADDITIVE = ROOT / "scripts" / "md_fence_marker_is_additive_2026-10-01.py"

#: (document, must the extractor see it?). The flag is what the parsers say.
CASES = [
    ("- ```python\n  x = 1\n  print(x)\n  ```\n", True, "bullet marker"),
    ("* ```python\n  x = 1\n  ```\n", True, "star marker"),
    ("+ ```python\n  x = 1\n  ```\n", True, "plus marker"),
    ("1. ```python\n   x = 1\n   ```\n", True, "ordered marker"),
    ("2) ```python\n   x = 1\n   ```\n", True, "ordered paren marker"),
    ("> - ```python\n>   x = 1\n>   ```\n", True, "quoted bullet"),
    ("- item\n\n  ```python\n  x = 1\n  ```\n", True, "nested, 2-space"),
    ("```python\nx = 1\n```\n", True, "column-0 fence, unchanged"),
    ("  ```python\n  x = 1\n  ```\n", True, "indented fence, unchanged"),
    ("See: ```python\nx = 1\n```\n", False, "not a fence to either parser"),
]


def _mod(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, str(path))
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


@pytest.mark.parametrize("doc,expected,label", CASES,
                         ids=[c[2] for c in CASES])
def test_the_extractor_agrees_with_a_commonmark_parser(doc, expected, label):
    from reference_runner_v3 import _MD_PY_FENCE_ANY
    assert bool(_MD_PY_FENCE_ANY.search(doc)) is expected, (
        f"{label}: extractor says {not expected}, the parsers say {expected}; "
        f"doc={doc!r}")


@pytest.mark.parametrize("doc,label",
                         [(d, l) for d, e, l in CASES if e],
                         ids=[l for d, e, l in CASES if e])
def test_a_list_item_listing_is_not_reported_as_no_code(doc, label):
    """The consequence, at the call site that triages the target."""
    from reference_runner_v3 import _gateable_hunks, _gateable_source
    src, reason = _gateable_source(doc, "note.md")
    assert src is not None, (
        f"{label}: a document carrying python was gated as {reason!r}")
    assert "x = 1" in src, f"{label}: extracted {src!r}"
    assert _gateable_hunks(doc, "note.md"), f"{label}: no hunks"


def test_the_falsifier_for_this_finding_exits_clean():
    """The panel's own falsifier must now pass, and it is the real one."""
    assert FALSIFIER.is_file(), f"missing {FALSIFIER}"
    m = _mod(FALSIFIER, "md_fence_blind_spot_probe")
    assert m.main() == 0


def test_the_widening_is_still_additive():
    """0 documents lost, 0 bodies changed, over 7069 documents."""
    assert ADDITIVE.is_file(), f"missing {ADDITIVE}"
    m = _mod(ADDITIVE, "md_fence_additive_probe")
    assert m.main() == 0


def test_the_dominance_corpus_varies_the_prefix_axis():
    """Why 0-of-560 was not a measurement.

    AST-FREE BUT NOT SOURCE-TEXT: this imports the corpus module and inspects
    its ACTUAL tuples, so it cannot be satisfied by a comment
    (`execute-do-not-grep`).
    """
    probe = _mod(FALSIFIER, "md_fence_blind_spot_probe2")
    dom = _mod(ROOT / "scripts" / "md_fence_orphan_dominance_2026-10-01.py",
               "md_fence_dominance_probe")
    refused = [p for p in probe.MARKERS if p]
    assert refused, "the probe lost its list-marker axis"
    assert not (set(refused) & set(dom.PREFIXES)), (
        "the dominance corpus now varies the prefix axis; fold the extension "
        "into it and delete this guard")
    assert len(probe.shapes()) > len(dom.shapes()), (
        "the extension must be a strict superset of the 560-shape corpus")
