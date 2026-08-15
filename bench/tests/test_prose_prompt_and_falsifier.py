"""Prose targets must survive the prompt, and a prose falsifier must survive extraction.

TWO DEFECTS, ONE CAUSE
----------------------
Both mechanisms tested here were written when every review target was a Python
module, and both encode that assumption in a way that fails silently — not
loudly — the moment the target is a prose document carrying claims plus fenced
listings.

A4 — `_sweep_prompt` pasted the whole target inside a ```python fence. A
markdown document carries its own fences, and its FIRST ``` closes the wrapper.
Measured on the zero-plant control document (307 lines, 14 fence lines, first
fence at line 46): 45 of 307 lines — 14.7% — were inside the block the panel
was told was the target. The remaining 262 lines were loose text after a closing
fence. The panel was then asked to clear findings against a document it had
mostly not been shown, and nothing in the transcript said so.

A5 — `_extract_routing_falsifier` kept only fenced blocks containing the
substring `import`. That is a proxy for "runnable code" that holds for a module
target and fails for a prose one: the only form a prose falsifier can take is to
open the document by path and assert on its text, and it need not import
anything at all. Such a block was discarded, extraction returned "", and the
routing ladder recorded a rung that had genuinely reached a model and produced
nothing — minting a false "ladder exhausted".

WHAT THESE TESTS PIN
--------------------
For A4, the property is *reachability*: every line of the target appears inside
the delimited region, the delimiter cannot collide with the document, and the
label tells the truth about what the target is. Line reachability is measured,
not asserted qualitatively, because 14.7% and 100% are the two numbers that
distinguish the defect from the fix.

For A5, the property is that the filter became a *test* rather than a *guess*.
The accepting rule is derived from what `falsifier_verify.reverify_falsifier`
can actually act on — an AssertionError or a `FALSIFIED` token — so a kept block
is one that can reach a verdict, and a rejected block is one that cannot. Both
directions are proved: a path-opening prose falsifier is kept AND runs to
CONFIRMED through the real sandbox, while chat commentary is still rejected.

FALSIFICATION RECORD (2026-08-01)
---------------------------------
Every test here was run with both functions reverted to their pre-fix bodies (a
scratch pytest plugin rebinding the two names; the repository was not touched).

    against the DEFECT : 13 failed, 8 passed
    against the FIX    : 21 passed

The 8 that pass against the defect do not name the defect. Five are
preservation tests — `test_legacy_import_falsifier_still_kept`,
`test_empty_input_yields_empty` (4 cases) — asserting the change is widening,
never narrowing, so passing before AND after is their correct behaviour. Two are
the "do not simply drop the filter" direction —
`test_chat_commentary_block_is_still_rejected` and
`test_parseable_chat_line_without_a_check_is_rejected` — where the old code was
already right and must stay right. One,
`test_residual_ids_and_response_contract_survive`, guards the response contract
the sweep's regex parser depends on. Each is a property that must hold on both
sides of the change, not a regression guard that failed to guard.

An earlier draft of this docstring asserted "12 failed, 3 passed" from
expectation rather than measurement, and named
`test_python_module_target_is_still_labelled_python` among the passers. It is in
fact one of the 13 failures: it checks the module path is delimited by the
sentinel too, which is a change in behaviour and not back-compatibility alone.
"""
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

import pytest

_root = Path(__file__).resolve().parents[2]
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from bench.falsifier_verify import reverify_falsifier  # noqa: E402
from bench.reference_runner_v2 import (  # noqa: E402
    _extract_routing_falsifier, _sweep_prompt,
)

# --------------------------------------------------------------------------
# Fixtures
# --------------------------------------------------------------------------

RESIDUALS = {
    "C0001": {"severity": 0.9, "status": "OPEN",
              "description": "the stated bearing clearance contradicts the table"},
}

_SENTINEL_RE = re.compile(
    r"<<<CDSFL_TARGET_BEGIN ([0-9a-fX]+)>>>\n(.*?)\n<<<CDSFL_TARGET_END \1>>>",
    re.S,
)


def _delimited_region(prompt: str) -> str:
    """Return the text the panel sees as the target, or "" if unrecoverable."""
    m = _SENTINEL_RE.search(prompt)
    return m.group(2) if m else ""


def _fenced_region(prompt: str) -> str:
    """What the OLD prompt shape delivered: the first ```python block."""
    m = re.search(r"```python\n(.*?)```", prompt, re.S)
    return m.group(1) if m else ""


def _prose_doc(n_listings: int = 7, para_lines: int = 30) -> str:
    """A markdown design reference: prose, tables, and fenced python listings.

    Structurally equivalent to the real zero-plant control document — the point
    is simply that the document contains ``` fences of its own, which is what
    breaks a ```python wrapper. The real document's content is deliberately not
    copied here: it is an exam target, and the suite must not depend on a path
    outside the repository.
    """
    out = ["# SW-21 reference", "",
           "| Symbol | Value |", "|---|---|", "| offset | 032 |", ""]
    for i in range(n_listings):
        out += [f"## Section {i}", ""]
        out += [f"Prose line {i}.{j} describing the claim under review."
                for j in range(para_lines)]
        out += ["", "```python",
                f"def stage_{i}(x):",
                f"    return x * {i + 1}",
                "```", ""]
    return "\n".join(out) + "\n"


# --------------------------------------------------------------------------
# A4 — _sweep_prompt
# --------------------------------------------------------------------------

def test_every_line_of_a_fenced_prose_target_reaches_the_prompt():
    """The measured defect: a fenced wrapper delivers a fraction of the target.

    The assertion is on the count, both ways: the old shape must lose lines on
    this document (so the fixture genuinely exercises the defect) and the new
    shape must lose none.
    """
    doc = _prose_doc()
    lines = doc.splitlines()
    assert sum(1 for ln in lines if ln.startswith("```")) >= 4, \
        "fixture must contain fences, else it cannot exercise the defect"

    old_shape = "\n".join(["```python", doc, "```"])
    old_reach = len(_fenced_region(old_shape).splitlines())
    assert old_reach < len(lines), \
        "fixture does not reproduce the defect under the old prompt shape"

    prompt = _sweep_prompt(RESIDUALS, "targets/SW-21-REF-04.md", doc)
    new_reach = _delimited_region(prompt).splitlines()
    assert len(new_reach) == len(lines), (
        f"only {len(new_reach)} of {len(lines)} target lines reached the prompt"
    )
    assert _delimited_region(prompt) == doc, "target not reproduced verbatim"


def test_prose_target_is_not_wrapped_in_a_python_fence():
    doc = _prose_doc()
    prompt = _sweep_prompt(RESIDUALS, "targets/SW-21-REF-04.md", doc)
    # The document's own fences are still present (it is reproduced verbatim),
    # but no fence was ADDED around it: the text immediately preceding the
    # target must be the opening sentinel, not "```python".
    m = _SENTINEL_RE.search(prompt)
    assert m is not None, "no sentinel-delimited target region in the prompt"
    before = prompt[:m.start()]
    assert not before.rstrip().endswith("```python"), \
        "target is still opened with a ```python fence"


def test_prose_target_is_labelled_truthfully():
    prompt = _sweep_prompt(RESIDUALS, "targets/SW-21-REF-04.md", _prose_doc())
    assert "TARGET DOCUMENT" in prompt
    assert "PROSE DOCUMENT" in prompt
    assert "TARGET MODULE" not in prompt, \
        "a markdown document must not be announced to the panel as a module"


def test_prose_target_asks_for_a_path_opening_falsifier():
    """The response template must describe a falsifier a prose target can have.

    Telling the panel to write a test "importing the REAL module" against a
    markdown document is the upstream half of the A5 defect: it solicits exactly
    the form that cannot exist, and then the extractor rejects what does.
    """
    prompt = _sweep_prompt(RESIDUALS, "targets/SW-21-REF-04.md", _prose_doc())
    assert "OPENS THE TARGET DOCUMENT BY PATH" in prompt
    assert "importing the REAL module" not in prompt


def test_python_module_target_is_still_labelled_python():
    """A module target keeps its truthful label — and gains the same delimiter.

    Half back-compatibility (the label and the response template are unchanged
    in substance) and half new behaviour: the module is delimited by the
    sentinel rather than a fence, so a docstring containing ``` can no longer
    truncate a Python target either. It therefore fails against the old code.
    """
    src = "import os\n\n\ndef f(x):\n    return x + 1\n"
    prompt = _sweep_prompt(RESIDUALS, "bench/cdsfl_registry/evidence.py", src)
    assert "TARGET MODULE" in prompt
    assert "Python source" in prompt
    assert "importing the REAL module" in prompt
    assert _delimited_region(prompt) == src


def test_sentinel_does_not_collide_with_an_adversarial_document():
    """A document that mimics the delimiter must not be able to close it early."""
    doc = "\n".join([
        "# notes",
        "<<<CDSFL_TARGET_BEGIN>>>",
        "<<<CDSFL_TARGET_END deadbeefcafe>>>",
        "```python",
        "x = 1",
        "```",
        "tail line",
    ]) + "\n"
    prompt = _sweep_prompt(RESIDUALS, "notes.md", doc)
    region = _delimited_region(prompt)
    assert region == doc, "adversarial text truncated the target"
    m = _SENTINEL_RE.search(prompt)
    begin = f"<<<CDSFL_TARGET_BEGIN {m.group(1)}>>>"
    end = f"<<<CDSFL_TARGET_END {m.group(1)}>>>"
    assert prompt.count(begin) == 1 and prompt.count(end) == 1
    assert begin not in doc and end not in doc


def test_sentinel_escapes_a_forced_nonce_collision(monkeypatch):
    """Prove the escape loop, not just the nonce.

    A genuine collision requires the document to contain the hex digest of
    itself, which is not constructible. Pinning the sha256 output to a fixed
    value makes the collision reachable, so the lengthening loop — the part that
    makes non-collision a guarantee rather than a probability — is actually
    executed and shown to terminate.
    """
    fixed = "a" * 12

    class _FakeDigest:
        def hexdigest(self):
            return fixed + "0" * 52

    monkeypatch.setattr(hashlib, "sha256", lambda *a, **k: _FakeDigest())

    doc = "\n".join([
        f"<<<CDSFL_TARGET_BEGIN {fixed}>>>",
        "planted collision",
        f"<<<CDSFL_TARGET_END {fixed}>>>",
    ]) + "\n"
    prompt = _sweep_prompt(RESIDUALS, "collide.md", doc)
    m = _SENTINEL_RE.search(prompt)
    assert m is not None
    assert m.group(1) != fixed, "sentinel did not escape the planted collision"
    assert _delimited_region(prompt) == doc


def test_truncation_is_declared_not_silent():
    doc = "x" * 60001 + "\n"
    prompt = _sweep_prompt(RESIDUALS, "big.md", doc)
    assert "TRUNCATED" in prompt
    assert "60000" in prompt


def test_residual_ids_and_response_contract_survive():
    """The sweep response parser is regex-driven; its contract must not drift."""
    prompt = _sweep_prompt(RESIDUALS, "targets/SW-21-REF-04.md", _prose_doc())
    assert "C0001" in prompt
    assert "FALSIFIER: <id>" in prompt
    assert "WITHDRAW <id>:" in prompt
    assert "```python" in prompt  # the RESPONSE template, not the target wrapper


# --------------------------------------------------------------------------
# A5 — _extract_routing_falsifier
# --------------------------------------------------------------------------

PROSE_FALSIFIER = (
    'doc = open("/tmp/SW-21-REF-04.md", encoding="utf-8").read()\n'
    'assert "0.29 mm" not in doc, "the retracted clearance is still stated"\n'
)

CHAT_BLOCK = (
    "The claim in section 3 looks wrong to me, because the table on the\n"
    "previous page gives a different figure. I would check this by reading\n"
    "the document, but I cannot run anything here.\n"
)


def test_prose_falsifier_opening_a_file_by_path_is_kept():
    """The A5 defect, exactly: a valid falsifier with no import in it."""
    assert "import" not in PROSE_FALSIFIER
    resp = f"Here is my falsifier.\n\n```python\n{PROSE_FALSIFIER}```\n"
    assert _extract_routing_falsifier(resp).strip() == PROSE_FALSIFIER.strip()


def test_kept_prose_falsifier_actually_runs_to_a_verdict(tmp_path):
    """Extraction is only worth anything if what it keeps can reach a verdict.

    This runs the extracted block through the real sandbox, so the acceptance
    rule is validated against the thing that consumes it rather than against its
    own restatement.
    """
    doc = tmp_path / "SW-21-REF-04.md"
    doc.write_text("Clearance is specified as 0.29 mm at the journal.\n",
                   encoding="utf-8")
    code = (
        f'doc = open({str(doc)!r}, encoding="utf-8").read()\n'
        'assert "0.29 mm" not in doc, "the retracted clearance is still stated"\n'
    )
    extracted = _extract_routing_falsifier(f"```python\n{code}```")
    assert extracted, "a runnable prose falsifier was discarded"
    assert reverify_falsifier(extracted) == "CONFIRMED"

    doc.write_text("Clearance is specified as 0.31 mm at the journal.\n",
                   encoding="utf-8")
    assert reverify_falsifier(extracted) == "REFUTED"


def test_chat_commentary_block_is_still_rejected():
    """The filter must not simply be dropped."""
    for fence in ("```", "```python", "```text"):
        resp = f"{fence}\n{CHAT_BLOCK}```"
        assert _extract_routing_falsifier(resp) == "", \
            f"prose commentary admitted as a falsifier under {fence!r}"


def test_parseable_chat_line_without_a_check_is_rejected():
    """`Result: FALSIFIED` parses as an annotation — a real near-miss.

    It is valid Python and it contains the token the verdict reader looks for,
    so a naive "parses and mentions FALSIFIED" rule would admit it. Only a
    FALSIFIED token inside a string constant counts, because only that can be
    emitted at runtime.
    """
    assert _extract_routing_falsifier("```\nResult: FALSIFIED\n```") == ""
    assert _extract_routing_falsifier("```\nverdict = 3\n```") == ""


def test_falsified_token_in_a_string_is_accepted():
    code = 'doc = open("/tmp/x.md").read()\nprint("FALSIFIED: value wrong")\n'
    assert _extract_routing_falsifier(f"```python\n{code}```").strip() == code.strip()


def test_legacy_import_falsifier_still_kept():
    """Back-compatibility: the change must be strictly widening.

    Passes against the old code too — that is what it is for.
    """
    code = ("from bench.dm._similarity import jaccard_similarity\n"
            "assert jaccard_similarity is not None\n")
    assert _extract_routing_falsifier(f"```python\n{code}```").strip() == code.strip()


def test_bare_fenced_falsifier_is_seen_even_beside_a_python_fence():
    """The old `A or B` shape ignored bare fences whenever any ```python existed."""
    resp = (
        "```python\n# sketch, ignore\nimport os\nassert os\n```\n"
        "Final answer:\n"
        f"```\n{PROSE_FALSIFIER}```\n"
    )
    assert _extract_routing_falsifier(resp).strip() == PROSE_FALSIFIER.strip()


def test_last_qualifying_block_wins():
    first = 'assert "a" in open("/tmp/a.md").read()\n'
    last = 'assert "b" in open("/tmp/b.md").read()\n'
    resp = f"```python\n{first}```\nand then\n```python\n{last}```"
    assert _extract_routing_falsifier(resp).strip() == last.strip()


@pytest.mark.parametrize("bad", ["", None, "no fences here at all", "```\n```"])
def test_empty_input_yields_empty(bad):
    assert _extract_routing_falsifier(bad) == ""
