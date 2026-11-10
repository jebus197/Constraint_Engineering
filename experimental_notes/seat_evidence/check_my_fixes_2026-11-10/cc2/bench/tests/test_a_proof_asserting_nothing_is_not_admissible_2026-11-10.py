# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'check_my_fixes_2026-11-10', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 44d9c1e0b296313f244bfb846c5c8b913f9b15a8edb0b2a4da7649f741b2fe22
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""A proof with 0 assertions must not score ADMISSIBLE by any route.

THE DEFECT THIS PINS, FOUND BY EXECUTION 2026-11-10. The fold-back of
2026-11-01 added `asserts_something` to stop a vacuous proof being admitted,
and the predicate had a second route straight back into the hole: it accepted a
string literal containing the token ANYWHERE in the tree, a module docstring
included. Measured against the real module, both of

    a module DOCSTRING reading "Proof: prints FALSIFIED if the identity
    fails." followed by nothing but print("ok"), and
    print("NOT FALSIFIED: the identity holds")

have 0 `Assert` and 0 `Raise` nodes, exited cleanly and returned
SK_ADMISSIBLE with the reason "its own assertions held". The second is the form
`_read_verdict` itself reads as an honest negative.
`docs/PROOF_AND_FALSIFIER_DEFINITION.md` section 2 states a proof "must contain
an assertion or a raise", so the code was WIDER than the definition that cites
it.

WHAT IS GUARDED HERE, AND IN BOTH DIRECTIONS. The vacuous shapes must be
refused (the repair) AND the legitimate token shape must still be accepted (the
repair must not remove a working behaviour). The second half is the load-bearing
one: a narrowing is only additive if nothing that worked stops working.

IT ALSO PINS THE EXTRACTION. `declares_falsified` and the 2 named patterns were
lifted out of `_read_verdict` so this module could read the rule rather than
restate it. The lift is only safe if `_read_verdict` still returns what it
returned, so its verdicts over a token battery are pinned here too.
"""
from __future__ import annotations

import ast

import pytest

from bench.falsifier_verify import (
    FALSIFIED_TOKEN_RE,
    NOT_FALSIFIED_RE,
    _read_verdict,
    declares_falsified,
)
from bench.proof_verify import asserts_something

#: Proofs with 0 Assert and 0 Raise nodes. None may be called a proof.
VACUOUS = [
    ('"""Proof: prints FALSIFIED if the identity fails."""\nprint("ok")\n',
     "token in a docstring"),
    ('print("NOT FALSIFIED: the identity holds")\n',
     "the honest-negative form only"),
    ('# FALSIFIED\nprint("ok")\n', "token in a comment"),
    ('MSG = "FALSIFIED"\nprint("ok")\n', "token assigned, never emitted"),
    ('"FALSIFIED"\n', "token as a bare expression"),
    ('print("ok")\n', "no token at all"),
    ('import os\nprint(os.getcwd())\n', "an import and a print"),
    ('', "empty"),
]

#: Proofs that DO check something. Every one must still be accepted.
SUBSTANTIVE = [
    ('assert 2 + 2 == 4\n', "a plain assertion"),
    ('if 2 + 2 != 4:\n    print("FALSIFIED: arithmetic")\n',
     "a conditional token print"),
    ('x = 5\nif x != 5:\n    print(f"FALSIFIED {x}")\n',
     "an f-string token print"),
    ('if False:\n    print("FALSIFIED: " + "why")\n',
     "a concatenated token print"),
    ('import sys\nif False:\n    sys.stdout.write("FALSIFIED\\n")\n',
     "a stdout write"),
    ('raise AssertionError("does not hold")\n', "an explicit raise"),
    ('print("ok", end="FALSIFIED")\n', "a keyword argument"),
]


@pytest.mark.parametrize("code,why", VACUOUS, ids=[w for _, w in VACUOUS])
def test_a_proof_with_no_assertion_is_not_a_proof(code: str, why: str) -> None:
    if code.strip():
        tree = ast.parse(code)
        assert not any(isinstance(n, (ast.Assert, ast.Raise))
                       for n in ast.walk(tree)), (
            f"the fixture {why!r} is meant to contain no assertion")
    assert asserts_something(code) is False, (
        f"{why}: a proof with 0 assertions was treated as asserting something, "
        "so a clean exit would be read as its assertions holding")


@pytest.mark.parametrize("code,why", SUBSTANTIVE,
                         ids=[w for _, w in SUBSTANTIVE])
def test_a_proof_that_checks_something_is_still_accepted(code: str,
                                                         why: str) -> None:
    assert asserts_something(code) is True, (
        f"{why}: this proof does check something and the narrowing of "
        "2026-11-10 must not have removed it")


def test_the_token_patterns_are_the_ones_read_verdict_carried() -> None:
    """The extraction is only safe if the patterns are byte-identical."""
    assert NOT_FALSIFIED_RE.pattern == r"\bNOT[\s_-]?FALSIFIED\b"
    assert FALSIFIED_TOKEN_RE.pattern == r"(?<![A-Z_])FALSIFIED\b"


@pytest.mark.parametrize("stdout,verdict", [
    ("FALSIFIED", "CONFIRMED"),
    ("FALSIFIED: x", "CONFIRMED"),
    ("NOT FALSIFIED", "REFUTED"),
    ("NOT_FALSIFIED", "REFUTED"),
    ("not falsified", "REFUTED"),
    ("UNFALSIFIED", "REFUTED"),
    ("", "REFUTED"),
])
def test_read_verdict_still_returns_what_it_returned(stdout: str,
                                                     verdict: str) -> None:
    assert _read_verdict(stdout, "", 0) == verdict


@pytest.mark.parametrize("text,declared", [
    ("FALSIFIED", True),
    ("FALSIFIED: why", True),
    ("NOT FALSIFIED", False),
    ("NOT_FALSIFIED", False),
    ("UNFALSIFIED", False),
    ("", False),
])
def test_declares_falsified_agrees_with_read_verdict(text: str,
                                                     declared: bool) -> None:
    """The helper and the verdict reader must not be able to disagree."""
    assert declares_falsified(text) is declared
    assert (_read_verdict(text, "", 0) == "CONFIRMED") is declared
