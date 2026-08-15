"""A falsifier that mentions a markdown fence must not truncate itself.

Found 2026-08-12 by inspecting the ERROR verdicts on the zero-plant control run of
2026-08-01. Five criticals (C0013-C0017) each carried a falsifier cut to exactly
134 characters, ending mid-literal at ``re.findall(r'``, every one dying with
"unterminated string literal" and recorded as ERROR. Five of 22 criticals — 23%.

The extractor terminated on the first triple-backtick anywhere in the block. A
falsifier that opens a markdown target and parses its fenced code blocks has to
mention the fence delimiter, so it cut itself off at that point.

The selection pressure ran the wrong way: falsifiers that correctly opened and
parsed the target were destroyed, while ones pasting an inline copy of the code
survived. Every Exp 48-54 target is markdown.
"""
from __future__ import annotations

import pytest

from bench.runner_core import extract_falsifiers


# The real shape that failed, reconstructed from the truncated remains in the
# 2026-08-01 registry. The inner fences are what used to end extraction early.
REALISTIC = '''FINDING_ID: F001
FALSIFIER:
```python
import re
with open('/tmp/target.md', 'r') as f:
    code = "\\n".join(re.findall(r'```python\\n(.*?)\\n```', f.read(), re.S))
ns = {}
exec(code, ns)
tb = ns["TokenBucket"](capacity=1, refill_per_sec=0.0)
tb.allow(1.0)
assert tb.allow(-10.0) is False, "FALSIFIED: negative cost admitted"
```
'''


def test_falsifier_mentioning_a_fence_is_captured_whole():
    """The regression itself."""
    _by_key, ordered = extract_falsifiers(REALISTIC)
    assert len(ordered) == 1
    code = ordered[0]
    assert "FALSIFIED: negative cost admitted" in code, (
        "truncated at the inner fence — the tail of the falsifier was lost")


def test_the_captured_falsifier_actually_compiles():
    """134 chars of valid-looking Python that will not parse is the failure mode.

    compile() parses without executing, so this is a pure text check.
    """
    _by_key, ordered = extract_falsifiers(REALISTIC)
    compile(ordered[0], "<falsifier>", "exec")


def test_multiple_blocks_still_split_at_the_right_places():
    """The risk of a laxer terminator is swallowing everything to the last fence."""
    response = '''FINDING_ID: A1
FALSIFIER:
```python
assert False, "FALSIFIED: first"
```

Some prose between the blocks.

FINDING_ID: B2
FALSIFIER:
```python
assert False, "FALSIFIED: second"
```
'''
    _by_key, ordered = extract_falsifiers(response)
    assert len(ordered) == 2, f"expected 2 blocks, got {len(ordered)}"
    assert "first" in ordered[0] and "second" not in ordered[0], (
        "first block ran past its own closing fence")
    assert "second" in ordered[1]


def test_a_response_with_no_falsifier_is_still_untouched():
    """Extraction is documented as additive — this pins that."""
    by_key, ordered = extract_falsifiers("FINDING: something\nNo code here at all.")
    assert by_key == {} and ordered == []


def test_labelled_extraction_also_survives_an_inner_fence():
    """by_key uses a second pattern, which carried the identical defect."""
    by_key, _ordered = extract_falsifiers(REALISTIC)
    assert by_key, "labelled extraction produced nothing"
    code = next(iter(by_key.values()))
    assert "FALSIFIED: negative cost admitted" in code
    compile(code, "<falsifier>", "exec")


@pytest.mark.parametrize("closer", ["```", "```   ", "``` \t"])
def test_trailing_whitespace_on_the_closing_fence_is_tolerated(closer):
    response = f'FALSIFIER:\n```python\nassert False, "FALSIFIED"\n{closer}\n'
    _by_key, ordered = extract_falsifiers(response)
    assert len(ordered) == 1 and "FALSIFIED" in ordered[0]


def test_block_closing_at_end_of_string_without_trailing_newline():
    response = 'FALSIFIER:\n```python\nassert False, "FALSIFIED"\n```'
    _by_key, ordered = extract_falsifiers(response)
    assert len(ordered) == 1, "block ending at EOF was not captured"


def test_the_exact_truncated_artefact_would_now_be_avoided():
    """Reproduces the measured 134-character remains as a direct regression pin."""
    truncated = (
        "import re\n"
        "with open('/Users/x/SW-21-REF-04.md', 'r') as f:\n"
        "    code = \"\\n\".join(re.findall(r'"
    )
    with pytest.raises(SyntaxError):
        compile(truncated, "<f>", "exec")

    _by_key, ordered = extract_falsifiers(REALISTIC)
    assert not ordered[0].endswith("re.findall(r'"), "still truncating"
