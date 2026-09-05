"""Mechanically generated seeded-defect catalogues, with machine-checkable ground truth.

WHY THIS EXISTS, AND WHY A HAND-WRITTEN CATALOGUE IS NOT A SUBSTITUTE
====================================================================
Andrews, Briand and Labiche (ICSE 2005) measured that hand-seeded faults are NOT
a valid substitute for real faults, while mechanically generated mutants ARE;
Just and colleagues (FSE 2014) found mutant detection tracks real-fault detection
independently of coverage. Dissent is recorded in the project runway at 0C.55
(Gopinath and colleagues, ISSRE 2014, and the 2023 coupling study question how
tightly common operators couple to real faults), and it does not change the
direction of the correction.

Both catalogues this project has used so far were written by hand, and the first
one failed in exactly the way the ICSE result predicts. Measured 2026-09-01, and
recorded in `bench/canary_seeding.py`: 3 of 5 plants contradicted a formula
stated verbatim in the adjacent docstring and were killed by all 6 seats, while
the 2 that required reasoning about an invariant were missed by everybody. Both
of those sat in the CALIBRATION split, which `detection_rate` does not report --
so p_hat came back 1.000 while 40% of the plants went unfound.

That failure has 3 distinguishable causes, and this module is built against all 3:

  1. The author chose the plants, so detection rate measured the author's
     expectations as much as the panel's detection. -> Plants are produced by
     declared mutation operators over sites found by declared extractors. The
     author picks the operators and the seed, never the individual plant.

  2. The catalogue could not be regenerated, so a benchmark could not be re-run
     against a changed system. -> Generation is DETERMINISTIC given a seed. The
     same seed yields a byte-identical catalogue. `random.Random(seed)` only; the
     global `random` module is never touched.

  3. Difficulty tracked the scored boundary invisibly. -> Difficulty is MEASURED
     from the seeded document -- the plant's line is isolated and asked whether it
     contradicts itself -- and splits are stratified by (generator, difficulty) so
     no tier can land entirely in the unreported split. It is measured AFTER the
     mutation because it depends on which value the mutation drew, which an
     earlier version of this module got wrong; see `_measure_difficulty`.

WHAT MAKES THE GROUND TRUTH MACHINE-CHECKABLE
=============================================
Every defect records the exact span it occupies, the value that stood there
before, the value that stands there now, and the MECHANISM by which the document
refutes the plant -- one of `recompute_identity`, `cross_reference_quantity`, or
`evaluate_relation`. Each mechanism is a function that runs over the text.

`verify_ground_truth` does not read the stored values back and agree with itself.
It re-seeds the single defect through the real `canary_seeding.seed`, re-runs the
extractors over both documents, and requires the refutation mechanism to HOLD on
the clean text and FAIL on the seeded text. A record whose stored values disagree
with what the documents actually contain is reported as broken. This is the
project's `execute-do-not-grep` rule applied to a generator: the generator's own
account of what it did is not evidence, and the 2 texts are.

ONLY DEFECTS THE DOCUMENT CAN REFUTE
====================================
The generator refuses to emit a plant whose refutation is not present in the
document. A plant detectable only against outside knowledge is unfalsifiable by a
reviewer reading the artefact, so a miss on it measures nothing. This is a
deliberate narrowing and it is stated rather than assumed: the catalogue covers
internal-consistency defects, not domain-knowledge defects.

WHAT IS DELIBERATELY NOT HERE
=============================
No bridge from a model's PROSE finding to a machine-readable claim. `check_detection`
grades a claim of the form {"line": int, "corrected_line": str}; producing that
claim from a reviewer's paragraph is item D8, the execution-based matcher, and it
belongs in D8's files, not these. This module defines the target D8 must hit.

No scoring of a live run and no wiring into the convergence gate, for the same
reason `canary_seeding` gives: whether a missed plant should BLOCK convergence is
a founder ruling, not a default.

THE CATALOGUE IS ANSWER-KEY MATERIAL
====================================
It names defects reviewers are about to be scored on finding. `write_catalogue`
and `load_generated_catalogue` therefore refuse any path inside a git work tree,
using the SAME containment check as `canary_seeding`, imported rather than
copied. That check has already had 2 defects fixed in it -- work-tree walking,
and `os.path.normcase` for case-insensitive volumes -- and a second copy would
not have received either fix.

    ITEM D10, founder verdict 2026-09-05: "The mechanically generated seeded
    defect catalogue, approved but not started. Verdict: Do it."
"""
from __future__ import annotations

import argparse
import ast
import dataclasses
import hashlib
import json
import pathlib
import random
import re
import sys
from typing import Any, Callable, Sequence

_REPO = pathlib.Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:  # so the module also runs as a bare script path
    sys.path.insert(0, str(_REPO))

# `_in_a_git_worktree` is imported, not reimplemented. Duplicating a containment
# guard forks it: this one has already absorbed 2 fixes (walk for `.git` so ANY
# work tree is protected, and `os.path.normcase` because `Path.resolve()` does
# not case-normalise on macOS), and a copy would have received neither. If the
# name is ever renamed upstream this import fails loudly at collection time,
# which is the correct outcome for a guard -- a silently absent guard is worse
# than a broken import.
from bench.canary_seeding import (  # noqa: E402
    CALIBRATION,
    HELD_OUT,
    Canary,
    CanaryIntegrityError,
    _in_a_git_worktree,
    seed,
)

CATALOGUE_FORMAT = "cdsfl-seeded-defect-catalogue/1"


class CatalogueGenerationError(RuntimeError):
    """The generator could not produce a catalogue it is willing to stand behind."""


# --------------------------------------------------------------------------- #
# Declared difficulty tiers                                                    #
# --------------------------------------------------------------------------- #
# Difficulty is MEASURED, not assigned: `_measure_difficulty` isolates the plant's
# line and asks whether that line, read alone, contradicts itself. The tier is the
# MINIMUM over all available refutations, because a reader takes the easiest route,
# not the one the catalogue author had in mind.
#
# The prefix before the first "-" is what `canary_seeding.split_difficulty_balance`
# groups on, so these names are shaped to compose with that function.
DIFFICULTY_LOCAL = "local-same-line"
DIFFICULTY_DISTRIBUTED = "distributed-cross-line"


# --------------------------------------------------------------------------- #
# Declared defect classes                                                      #
# --------------------------------------------------------------------------- #
@dataclasses.dataclass(frozen=True)
class DefectClass:
    """1 mutation operator, with every parameter of it declared up front.

    `severity` is a DECLARED PARAMETER of the class and not a measurement. It is
    recorded with its basis so a reader can disagree with the ordering rather
    than having to reverse-engineer it. What IS measured per defect is
    `relative_error` and `cross_check_sites`, both recomputed by
    `verify_ground_truth` from the documents.
    """

    name: str
    generator: str
    severity: str
    severity_basis: str
    refutation_kind: str
    description: str


SEVERITY_CRITICAL = "critical"
SEVERITY_HIGH = "high"
SEVERITY_MEDIUM = "medium"

CLASS_STATED_RESULT = DefectClass(
    name="stated_result_error",
    generator="mutate_identity_result",
    severity=SEVERITY_HIGH,
    severity_basis=(
        "the document reports a number its own stated arithmetic does not produce, so a "
        "reader who trusts the reported number carries a wrong value forward"),
    refutation_kind="recompute_identity",
    description=(
        "The stated result of an in-text arithmetic identity is replaced by a value the "
        "expression does not evaluate to."),
)

CLASS_OPERAND = DefectClass(
    name="operand_error",
    generator="mutate_identity_operand",
    severity=SEVERITY_HIGH,
    severity_basis=(
        "the reported result becomes unreachable from the inputs the document states, so "
        "the computation cannot be reproduced from the document at all"),
    refutation_kind="recompute_identity",
    description=(
        "An operand of an in-text arithmetic identity is replaced, leaving the stated "
        "result unchanged and therefore no longer derivable."),
)

CLASS_QUANTITY_SCALE = DefectClass(
    name="quantity_scale_error",
    generator="mutate_quantity_scale",
    severity=SEVERITY_CRITICAL,
    severity_basis=(
        "1 symbol is left carrying 2 authoritative magnitudes in the same document, and "
        "a reader cannot tell which occurrence governs; every later use inherits the "
        "ambiguity"),
    refutation_kind="cross_reference_quantity",
    description=(
        "1 assignment of a symbol that the document defines identically in 2 or more "
        "places is rescaled by a declared factor."),
)

CLASS_RELATION = DefectClass(
    name="relation_reversal",
    generator="mutate_relation",
    severity=SEVERITY_MEDIUM,
    severity_basis=(
        "no quantity changes; only the relation drawn between 2 unchanged quantities "
        "becomes false, so the corruption is confined to the conclusion at that site"),
    refutation_kind="evaluate_relation",
    description=(
        "A comparison whose 2 operands both resolve to numbers is replaced by its "
        "opposite, making the stated relation arithmetically false."),
)

DEFECT_CLASSES: tuple[DefectClass, ...] = (
    CLASS_STATED_RESULT,
    CLASS_OPERAND,
    CLASS_QUANTITY_SCALE,
    CLASS_RELATION,
)
_CLASS_BY_NAME: dict[str, DefectClass] = {c.name: c for c in DEFECT_CLASSES}

#: Declared perturbations, drawn from with `random.Random(seed)`. They are ordered
#: tuples rather than sets so the draw is reproducible: set iteration order is
#: hash-dependent and would make the catalogue non-regenerable across processes.
RESULT_FACTORS: tuple[float, ...] = (2.0, 0.5, 10.0, 0.1, 100.0)
OPERAND_FACTORS: tuple[float, ...] = (2.0, 0.5, 4.0, 10.0)
SCALE_FACTORS: tuple[float, ...] = (1000.0, 0.001, 100.0, 0.01, 60.0)

#: A plant must move the value by at least this much, relative. A perturbation
#: inside the document's own rounding is not a defect a reader could ever
#: legitimately call, and scoring reviewers on it would measure nothing.
MIN_RELATIVE_ERROR = 0.05

#: How far `find` may be widened on each side to become unique in the document.
MAX_CONTEXT_PAD = 240

#: How far either side of a worded relation the operands may sit, in characters.
RELATION_WINDOW = 80


# --------------------------------------------------------------------------- #
# Records                                                                      #
# --------------------------------------------------------------------------- #
@dataclasses.dataclass(frozen=True)
class Location:
    """Exact position of the mutated span in the CLEAN document.

    Line and column are carried alongside the absolute offset because a reviewer
    reports a line, and because the offsets stay valid in the seeded document
    only while no plant changes the newline count -- which the generator
    guarantees by never mutating across a newline.
    """

    line: int  # 1-based, as a reader counts
    col: int  # 0-based within the line
    offset: int  # absolute, into the clean text
    end: int  # exclusive
    text: str  # exactly clean_text[offset:end]

    def as_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


@dataclasses.dataclass(frozen=True)
class Refutation:
    """How the document contradicts the plant, and where the evidence sits."""

    kind: str  # recompute_identity | cross_reference_quantity | evaluate_relation
    spans: tuple[tuple[int, int, str], ...]  # (offset, end, text) in the clean document
    explanation: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "spans": [list(s) for s in self.spans],
            "explanation": self.explanation,
        }


@dataclasses.dataclass(frozen=True)
class Detection:
    """What a correct detection looks like, in machine-checkable form.

    A correct detection names the line and supplies the line as it should read.
    `check_detection` applies it and grades the outcome. Prose is not accepted
    here on purpose: matching a reviewer's wording against a summary scores the
    reviewer on phrasing, which is the failure `canary_seeding.catches` already
    refuses to commit.
    """

    line: int
    correct_text: str  # the exact span text in the clean document
    seeded_text: str  # the exact span text in the seeded document
    correct_value: float | None  # None where the mutation is not numeric
    seeded_value: float | None
    tolerance: float

    def as_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


@dataclasses.dataclass(frozen=True)
class SeededDefect:
    """1 mechanically generated plant with fully machine-checkable ground truth."""

    id: str
    domain: str
    defect_class: str
    generator: str
    severity: str
    severity_basis: str
    split: str
    difficulty: str
    find: str
    replace: str
    location: Location
    detection: Detection
    refutation: Refutation
    relative_error: float | None
    cross_check_sites: int
    summary: str

    def as_dict(self) -> dict[str, Any]:
        d = dataclasses.asdict(self)
        d["location"] = self.location.as_dict()
        d["detection"] = self.detection.as_dict()
        d["refutation"] = self.refutation.as_dict()
        return d

    def to_canary(self) -> Canary:
        """The blinded view that `canary_seeding` consumes.

        `Canary(**c)` rejects unknown keys, so the ground-truth record cannot ride
        along inside the canary. It travels beside it in the catalogue file
        instead, under a separate top-level key that `load_catalogue` ignores.
        """
        return Canary(
            id=self.id,
            domain=self.domain,
            defect_class=self.defect_class,
            generator=self.generator,
            split=self.split,
            find=self.find,
            replace=self.replace,
            summary=self.summary,
            difficulty=self.difficulty,
        )


@dataclasses.dataclass(frozen=True)
class Catalogue:
    """A regenerable catalogue: the seed and the source hash reproduce it exactly."""

    format: str
    seed: int
    domain: str
    source_sha256: str
    seeded_sha256: str
    defects: tuple[SeededDefect, ...]
    coverage: dict[str, Any]

    def canaries(self) -> list[Canary]:
        return [d.to_canary() for d in self.defects]

    def by_id(self) -> dict[str, SeededDefect]:
        return {d.id: d for d in self.defects}


@dataclasses.dataclass(frozen=True)
class GroundTruthCheck:
    """The result of re-deriving a defect's ground truth from the 2 documents."""

    defect_id: str
    ok: bool
    failures: tuple[str, ...]
    clean_refutation_holds: bool
    seeded_refutation_holds: bool


# --------------------------------------------------------------------------- #
# Arithmetic, without `eval`                                                   #
# --------------------------------------------------------------------------- #
_ALLOWED_BINOPS = (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow)


def _eval_node(node: ast.AST) -> float:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) \
            and not isinstance(node.value, bool):
        return float(node.value)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        value = _eval_node(node.operand)
        return value if isinstance(node.op, ast.UAdd) else -value
    if isinstance(node, ast.BinOp) and isinstance(node.op, _ALLOWED_BINOPS):
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        if isinstance(node.op, ast.Mult):
            return left * right
        if isinstance(node.op, ast.Pow):
            return left ** right
        if right == 0.0:
            raise ValueError("the divisor is 0 in a document identity")
        return left / right
    raise ValueError(f"expression node not permitted: {type(node).__name__}")


def safe_eval(expression: str) -> float:
    """Evaluate a numeric-literal arithmetic expression without `eval`.

    The expressions come out of a review target, which is untrusted text. `eval`
    on document content would execute whatever the document contains, so the walk
    is restricted to numeric constants, unary sign, and the 5 binary operators.
    Anything else raises rather than being silently skipped.
    """
    tree = ast.parse(expression, mode="eval")
    return _eval_node(tree.body)


def stated_tolerance(literal: str) -> float:
    """Half a unit in the last decimal place the document actually wrote.

    A document that prints "0.333" has rounded, and holding it to full precision
    would reject every real identity in a real article. The tolerance is read off
    the literal's own precision rather than fixed, so the document sets its own
    standard.
    """
    if "." in literal:
        places = len(literal.split(".", 1)[1])
        return 0.5 * (10.0 ** -places)
    return 0.5


def format_like(value: float, template: str) -> str | None:
    """Render `value` in the same shape as `template`, or None if it cannot be.

    Returns None rather than a mangled literal when the template is an integer and
    the scaled value is not: writing "0" where the document wrote "400" would
    change the class of the defect without saying so.
    """
    if "." in template:
        places = len(template.split(".", 1)[1])
        return f"{value:.{places}f}"
    if abs(value - round(value)) > 1e-9:
        return None
    rendered = str(int(round(value)))
    if rendered in ("0", "-0"):
        return None  # a scale factor that annihilates the quantity is not a plant
    return rendered


# --------------------------------------------------------------------------- #
# Text helpers                                                                 #
# --------------------------------------------------------------------------- #
def line_col(text: str, offset: int) -> tuple[int, int]:
    line = text.count("\n", 0, offset) + 1
    col = offset - (text.rfind("\n", 0, offset) + 1)
    return line, col


def line_bounds(text: str, line: int) -> tuple[int, int]:
    """(start, end) offsets of a 1-based line, excluding its newline."""
    lines = text.split("\n")
    if line < 1 or line > len(lines):
        raise IndexError(f"line {line} is outside a document of {len(lines)} lines")
    start = 0
    for existing in lines[: line - 1]:
        start += len(existing) + 1
    return start, start + len(lines[line - 1])


_NUMBER = r"-?\d+(?:\.\d+)?"
_IDENT = r"[A-Za-z_][A-Za-z0-9_]*"
_OPERATOR_CHARS = set("+-*/^=<>")
#: Words that follow a number but are prose rather than a unit.
_NOT_UNITS = frozenset({
    "and", "or", "the", "a", "an", "in", "of", "to", "is", "are", "for", "with",
    "at", "on", "by", "as", "that", "which", "so", "then", "but", "if", "when",
    "was", "were", "be", "it", "its", "this", "these", "each", "per",
})


def _non_space_before(text: str, index: int) -> str:
    i = index - 1
    while i >= 0 and text[i] in " \t":
        i -= 1
    return text[i] if i >= 0 else ""


def _non_space_after(text: str, index: int) -> str:
    i = index
    while i < len(text) and text[i] in " \t":
        i += 1
    return text[i] if i < len(text) else ""


def _read_unit(text: str, index: int) -> tuple[str, int]:
    """Read an optional unit token immediately after a number. Returns (unit, end)."""
    match = re.compile(r"[ \t]*([A-Za-z°%][A-Za-z0-9°%/·\^\-]*)").match(text, index)
    if not match:
        return "", index
    token = match.group(1)
    if token.lower() in _NOT_UNITS:
        return "", index
    return token, match.end()


# --------------------------------------------------------------------------- #
# Extractor 1: symbol assignments                                              #
# --------------------------------------------------------------------------- #
@dataclasses.dataclass(frozen=True)
class Assignment:
    symbol: str
    value: float
    literal: str
    unit: str
    offset: int  # of the numeric literal
    end: int
    line: int


_ASSIGN_RE = re.compile(rf"({_IDENT})\s*=\s*({_NUMBER})")


def symbol_table(text: str) -> list[Assignment]:
    """Every `symbol = <number>` binding the document actually makes.

    THE BOUNDARY RULES ARE THE WHOLE POINT OF THIS FUNCTION, and without them the
    catalogue is poisoned at the source. The control target
    `bench/cdsfl_registry/targets/control_two_distinct_defects.md` contains the
    chained equality

        df = f_s / N = 400 / 256 = 1.5625 Hz

    A bare `symbol = number` regex reads "N = 400" out of that and binds N to 400,
    which is false: the chain says f_s/N equals 400/256. Every plant built on that
    binding would be a plant on a defect the generator invented. So:

      LEFT: the nearest non-space character before the symbol must not be an
      operator. In "f_s / N = 400" the character before N is "/", so the symbol is
      inside an expression and the match is refused.

      RIGHT: the nearest non-space character after the number, and after any unit
      token, must not be an operator or a digit. In "= 400 / 256" the character
      after 400 is "/", so the right-hand side is an expression rather than a
      literal, and the match is refused.

    Both rules independently reject the N = 400 reading. Belt and braces, because
    a single guard here is a single point of failure for the whole catalogue.
    """
    out: list[Assignment] = []
    for match in _ASSIGN_RE.finditer(text):
        symbol = match.group(1)
        literal = match.group(2)
        if _non_space_before(text, match.start(1)) in _OPERATOR_CHARS:
            continue
        num_start = match.start(2)
        num_end = match.end(2)
        unit, after_unit = _read_unit(text, num_end)
        following = _non_space_after(text, after_unit)
        if following in _OPERATOR_CHARS or following.isdigit():
            continue
        out.append(Assignment(
            symbol=symbol,
            value=float(literal),
            literal=literal,
            unit=unit,
            offset=num_start,
            end=num_end,
            line=line_col(text, num_start)[0],
        ))
    return sorted(out, key=lambda a: a.offset)


def resolve_symbols(text: str) -> tuple[dict[str, Assignment], list[str]]:
    """(symbol -> single binding, symbols the document binds inconsistently).

    A symbol the document already gives 2 different values is a PRE-EXISTING
    defect. Planting on top of one would corrupt the measurement -- the reviewer
    would be scored against a contradiction that was there before -- so those
    symbols are excluded from every extractor and reported in the coverage block
    instead. The document being already broken is information the catalogue owner
    needs, not something to route around silently.
    """
    grouped: dict[str, list[Assignment]] = {}
    for assignment in symbol_table(text):
        grouped.setdefault(assignment.symbol, []).append(assignment)
    resolved: dict[str, Assignment] = {}
    inconsistent: list[str] = []
    for symbol in sorted(grouped):
        values = {(a.value, a.unit) for a in grouped[symbol]}
        if len(values) > 1:
            inconsistent.append(symbol)
            continue
        resolved[symbol] = grouped[symbol][0]
    return resolved, inconsistent


# --------------------------------------------------------------------------- #
# Extractor 2: arithmetic identities                                           #
# --------------------------------------------------------------------------- #
@dataclasses.dataclass(frozen=True)
class Identity:
    expr: str
    expr_offset: int
    expr_end: int
    result_literal: str
    result_offset: int
    result_end: int
    computed: float
    stated: float
    tolerance: float
    line: int
    operands: tuple[tuple[int, int, str], ...]  # (offset, end, literal) inside expr
    holds: bool


_IDENTITY_RE = re.compile(
    rf"(?P<expr>{_NUMBER}(?:\s*[-+*/]\s*{_NUMBER})+)\s*=\s*(?P<result>{_NUMBER})")


def identity_candidates(text: str) -> list[Identity]:
    """Every syntactic `expression = result` the document states, holding or not.

    Separate from `find_identities` because `_refutation_holds` needs to see the
    FAILING ones. An earlier draft filtered here and then asked "is there a holding
    identity on this line?", which cannot tell a broken identity from a line that
    never had one -- and a mutation that shifts the line's character offsets would
    then be graded against whichever identity the search happened to reach first.
    Consistency of a line is now a property of ALL its candidates, so it does not
    depend on offsets surviving an edit.
    """
    out: list[Identity] = []
    for match in _IDENTITY_RE.finditer(text):
        expr = match.group("expr")
        result_literal = match.group("result")
        before = _non_space_before(text, match.start("expr"))
        if before.isdigit() or before == ".":
            continue
        unit, after_unit = _read_unit(text, match.end("result"))
        following = _non_space_after(text, after_unit)
        if following.isdigit() or following == "." or following in _OPERATOR_CHARS:
            continue
        try:
            computed = safe_eval(expr)
        except (SyntaxError, ValueError, ZeroDivisionError, OverflowError):
            continue
        stated = float(result_literal)
        tolerance = stated_tolerance(result_literal)
        operands: list[tuple[int, int, str]] = []
        for number in re.finditer(_NUMBER, expr):
            operands.append((
                match.start("expr") + number.start(),
                match.start("expr") + number.end(),
                number.group(0),
            ))
        out.append(Identity(
            expr=expr,
            expr_offset=match.start("expr"),
            expr_end=match.end("expr"),
            result_literal=result_literal,
            result_offset=match.start("result"),
            result_end=match.end("result"),
            computed=computed,
            stated=stated,
            tolerance=tolerance,
            line=line_col(text, match.start("expr"))[0],
            operands=tuple(operands),
            holds=abs(computed - stated) <= tolerance,
        ))
    return out


def find_identities(text: str) -> list[Identity]:
    """Arithmetic identities the document states AND currently satisfies.

    Only identities that HOLD are sites. An identity that already fails is a
    pre-existing defect, and planting there would score a reviewer against a
    contradiction the generator did not create.

    The expression must contain at least 1 operator, which is what the `+`
    quantifier in `_IDENTITY_RE` enforces. `x = 5` is a definition, not a
    computation, and mutating it produces nothing a reader could recompute.
    """
    return [i for i in identity_candidates(text) if i.holds]


# --------------------------------------------------------------------------- #
# Extractor 3: numeric relations                                               #
# --------------------------------------------------------------------------- #
@dataclasses.dataclass(frozen=True)
class Relation:
    op_text: str
    op_offset: int
    op_end: int
    reversed_text: str
    lhs_value: float
    rhs_value: float
    lhs_span: tuple[int, int, str]
    rhs_span: tuple[int, int, str]
    holds: bool
    line: int
    evidence_lines: tuple[int, ...]


#: Worded and symbolic relations, each with its opposite and its comparison sense.
#: Ordered longest-first so "is greater than" is matched before any shorter form
#: that could sit inside it.
_RELATIONS: tuple[tuple[str, str, str], ...] = (
    ("is greater than", "is less than", ">"),
    ("is less than", "is greater than", "<"),
    ("is above", "is below", ">"),
    ("is below", "is above", "<"),
    ("exceeds", "is less than", ">"),
    (">=", "<=", ">="),
    ("<=", ">=", "<="),
    (">", "<", ">"),
    ("<", ">", "<"),
)
_RELATION_RE = re.compile(
    "|".join(
        rf"(?<![A-Za-z]){re.escape(phrase)}(?![A-Za-z])" if phrase[0].isalpha()
        else re.escape(phrase)
        for phrase, _, _ in _RELATIONS
    )
)
_TOKEN_RE = re.compile(rf"{_NUMBER}|{_IDENT}")


def _resolve_token(token: str, symbols: dict[str, Assignment],
                   bindings: Sequence[Assignment], near_line: int) -> tuple[float, int] | None:
    """(value, defining line) for a token, or None when it names no number.

    An identifier resolves to its NEAREST binding by line, not to the first one.
    Measured on `bench/cdsfl_registry/targets/control_two_distinct_defects.md`:
    line 14 reads "`f_s = 400 Hz` exceeds `f_max = 180 Hz`", and f_max is also
    bound on line 8. Resolving to the first binding put the refuting evidence on
    line 8 and labelled the plant `distributed`, when a reader refutes it without
    leaving line 14. Difficulty is the EASIEST available route, so taking the
    furthest binding would have overstated difficulty on every plant of this shape.
    """
    try:
        return float(token), near_line
    except ValueError:
        pass
    if token not in symbols:
        return None  # unbound, or bound inconsistently and therefore excluded
    same_symbol = [a for a in bindings if a.symbol == token]
    if not same_symbol:
        return None
    nearest = min(same_symbol, key=lambda a: (abs(a.line - near_line), a.offset))
    return nearest.value, nearest.line


def relation_candidates(text: str, symbols: dict[str, Assignment],
                        bindings: Sequence[Assignment]) -> list[Relation]:
    """Every resolvable comparison the document states, holding or not.

    Operands are taken as the nearest resolvable token on each side, within
    RELATION_WINDOW characters and never across a line break. A comparison whose
    operands sit further apart than that is not one a reader would read as a
    single claim, and guessing at it would manufacture defects.

    Equal operands are refused: reversing a comparison between equal values gives
    a statement that was already false in 1 direction, so the plant would not be
    a plant.
    """
    out: list[Relation] = []
    for match in _RELATION_RE.finditer(text):
        phrase = match.group(0)
        opposite = next((b for a, b, _ in _RELATIONS if a == phrase), None)
        sense = next((c for a, _, c in _RELATIONS if a == phrase), None)
        if opposite is None or sense is None:
            continue
        line = line_col(text, match.start())[0]
        line_start, line_end = line_bounds(text, line)
        left_lo = max(line_start, match.start() - RELATION_WINDOW)
        right_hi = min(line_end, match.end() + RELATION_WINDOW)

        left_tokens = list(_TOKEN_RE.finditer(text, left_lo, match.start()))
        right_tokens = list(_TOKEN_RE.finditer(text, match.end(), right_hi))
        lhs = rhs = None
        for token in reversed(left_tokens):
            got = _resolve_token(token.group(0), symbols, bindings, line)
            if got is not None:
                lhs = (got[0], token.start(), token.end(), token.group(0), got[1])
                break
        for token in right_tokens:
            got = _resolve_token(token.group(0), symbols, bindings, line)
            if got is not None:
                rhs = (got[0], token.start(), token.end(), token.group(0), got[1])
                break
        if lhs is None or rhs is None or lhs[0] == rhs[0]:
            continue

        holds = {
            ">": lhs[0] > rhs[0],
            "<": lhs[0] < rhs[0],
            ">=": lhs[0] >= rhs[0],
            "<=": lhs[0] <= rhs[0],
        }[sense]
        evidence = tuple(sorted({lhs[4], rhs[4]}))
        out.append(Relation(
            op_text=phrase,
            op_offset=match.start(),
            op_end=match.end(),
            reversed_text=opposite,
            lhs_value=lhs[0],
            rhs_value=rhs[0],
            lhs_span=(lhs[1], lhs[2], lhs[3]),
            rhs_span=(rhs[1], rhs[2], rhs[3]),
            holds=holds,
            line=line,
            evidence_lines=evidence,
        ))
    return out


def find_relations(text: str, symbols: dict[str, Assignment],
                   bindings: Sequence[Assignment] | None = None) -> list[Relation]:
    """Resolvable comparisons the document states AND currently satisfies.

    A comparison that is already false is a pre-existing defect, not a site.
    """
    if bindings is None:
        bindings = symbol_table(text)
    return [r for r in relation_candidates(text, symbols, bindings) if r.holds]


# --------------------------------------------------------------------------- #
# Candidate sites                                                              #
# --------------------------------------------------------------------------- #
@dataclasses.dataclass(frozen=True)
class _Site:
    """A mutable position, before any mutation has been chosen for it."""

    defect_class: str
    offset: int
    end: int
    line: int
    find_lo: int
    find_hi: int
    symbol: str  # "" when the site is not symbol-bound
    payload: Any


def _unique_span(text: str, start: int, end: int) -> tuple[int, int]:
    """Widen (start, end) until the substring occurs exactly once in `text`.

    `canary_seeding.seed` refuses an ambiguous `find`, so a plant whose context
    cannot be made unique is dropped here rather than blowing up at seeding time.
    """
    lo, hi = start, end
    while text.count(text[lo:hi]) > 1:
        grew = False
        if lo > 0 and (start - lo) < MAX_CONTEXT_PAD:
            lo -= 1
            grew = True
        if hi < len(text) and (hi - end) < MAX_CONTEXT_PAD:
            hi += 1
            grew = True
        if not grew:
            raise ValueError("span cannot be made unique within the context budget")
    return lo, hi


def _try_site(text: str, defect_class: str, offset: int, end: int,
              symbol: str, payload: Any) -> _Site | None:
    """Build a site, with its `find` window ANCHORED AT THE START OF ITS LINE.

    Measured while building this module: with minimal `find` windows, generation
    on the 45-line test fixture failed at the self-seed check with "`find` text
    occurs 2 times" -- an EARLIER plant's replacement text had created a second
    copy of a LATER plant's `find`. Disjoint spans cannot prevent that, because
    the collision is between an edit's OUTPUT and another site's input. Starting
    the window at the line start drags in the line's own prose, which no numeric
    replacement elsewhere can reproduce.

    ANCHORING IS A YIELD OPTIMISATION, NOT THE CORRECTNESS GUARD, and the
    distinction was established by removing it and re-running rather than assumed.
    Unanchored generation is still CORRECT -- the progressive check in
    `generate_catalogue` catches the collision and drops the offending pair -- it
    simply keeps fewer plants. Saying anchoring "fixes" the collision would credit
    the wrong mechanism.

    It also makes the 1-plant-per-line rule redundant on present settings: 2
    plants on 1 line both anchor at the line start, so their windows overlap and
    the disjointness check already rejects the second. The rule is kept anyway,
    because that redundancy is a consequence of anchoring rather than a property
    of the design, and a later change to either would silently remove the
    guarantee that a line-level detection claim is unambiguous.
    """
    if "\n" in text[offset:end]:
        return None  # a mutation across a newline would move every later line number
    line_start = text.rfind("\n", 0, offset) + 1
    try:
        lo, hi = _unique_span(text, line_start, end)
    except ValueError:
        return None
    return _Site(
        defect_class=defect_class,
        offset=offset,
        end=end,
        line=line_col(text, offset)[0],
        find_lo=lo,
        find_hi=hi,
        symbol=symbol,
        payload=payload,
    )


def collect_sites(text: str) -> tuple[list[_Site], dict[str, Any]]:
    """Every position the declared operators could mutate, plus a coverage report.

    Difficulty is NOT decided here, and an earlier version deciding it here was
    wrong. Difficulty is a property of the seeded document, not of the position,
    because it depends on the value the mutation happens to choose. Measured over
    20 seeds before the correction: 7 of 426 plants were labelled `distributed`
    while being refutable from their own line. `_measure_difficulty` settles it
    after the mutation is known.
    """
    bindings = symbol_table(text)
    symbols, inconsistent = resolve_symbols(text)
    identities = find_identities(text)
    relations = find_relations(text, symbols, bindings)
    identity_spans = [(i.expr_offset, i.result_end) for i in identities]

    sites: list[_Site] = []

    for identity in identities:
        site = _try_site(text, CLASS_STATED_RESULT.name, identity.result_offset,
                         identity.result_end, "", identity)
        if site is not None:
            sites.append(site)
        for offset, end, literal in identity.operands:
            site = _try_site(text, CLASS_OPERAND.name, offset, end,
                             "", (identity, literal))
            if site is not None:
                sites.append(site)

    # A symbol the document binds identically on 2 or more distinct lines. Only
    # then does rescaling 1 occurrence leave a contradiction the document itself
    # can settle; rescaling a symbol bound once is a domain-knowledge defect, and
    # this module does not emit those.
    grouped: dict[str, list[Assignment]] = {}
    for assignment in bindings:
        if assignment.symbol in inconsistent:
            continue
        grouped.setdefault(assignment.symbol, []).append(assignment)
    repeated = 0
    for symbol in sorted(grouped):
        occurrences = grouped[symbol]
        if len({a.line for a in occurrences}) < 2:
            continue
        repeated += 1
        for assignment in occurrences:
            inside_identity = any(lo <= assignment.offset < hi for lo, hi in identity_spans)
            if inside_identity:
                continue  # that is an identity plant wearing a different label
            site = _try_site(text, CLASS_QUANTITY_SCALE.name, assignment.offset,
                             assignment.end, symbol,
                             (assignment, tuple(occurrences)))
            if site is not None:
                sites.append(site)

    for relation in relations:
        site = _try_site(text, CLASS_RELATION.name, relation.op_offset, relation.op_end,
                         "", relation)
        if site is not None:
            sites.append(site)

    sites.sort(key=lambda s: (s.offset, s.defect_class))
    report = {
        "symbols_bound": len(symbols),
        "symbols_bound_inconsistently": inconsistent,
        "symbols_repeated_across_lines": repeated,
        "identities_found": len(identities),
        "relations_found": len(relations),
        "sites_by_class": {
            name: sum(1 for s in sites if s.defect_class == name)
            for name in sorted(_CLASS_BY_NAME)
        },
    }
    return sites, report


# --------------------------------------------------------------------------- #
# Mutators                                                                     #
# --------------------------------------------------------------------------- #
def _pick_factor(rng: random.Random, factors: Sequence[float], literal: str,
                 value: float) -> tuple[float, str] | None:
    """Draw a factor that renders faithfully and moves the value far enough.

    The draw is a shuffle of the DECLARED tuple rather than a `choice` retry loop,
    so the number of rng calls does not depend on how many factors happen to be
    rejected. A variable number of draws would make 1 site's rejection shift
    every later site's mutation, which is regenerable but needlessly fragile.
    """
    order = list(factors)
    rng.shuffle(order)
    for factor in order:
        rendered = format_like(value * factor, literal)
        if rendered is None or rendered == literal:
            continue
        seeded = float(rendered)
        if value == 0.0:
            continue
        if abs(seeded - value) / abs(value) < MIN_RELATIVE_ERROR:
            continue
        return seeded, rendered
    return None


def _mutate(site: _Site, text: str, rng: random.Random) -> tuple[str, float, float] | None:
    """(replacement literal, correct value, seeded value) for a site, or None."""
    original = text[site.offset:site.end]
    if site.defect_class == CLASS_STATED_RESULT.name:
        identity: Identity = site.payload
        got = _pick_factor(rng, RESULT_FACTORS, original, identity.stated)
        if got is None:
            return None
        return got[1], identity.stated, got[0]
    if site.defect_class == CLASS_OPERAND.name:
        value = float(original)
        got = _pick_factor(rng, OPERAND_FACTORS, original, value)
        if got is None:
            return None
        return got[1], value, got[0]
    if site.defect_class == CLASS_QUANTITY_SCALE.name:
        assignment: Assignment = site.payload[0]
        got = _pick_factor(rng, SCALE_FACTORS, original, assignment.value)
        if got is None:
            return None
        return got[1], assignment.value, got[0]
    if site.defect_class == CLASS_RELATION.name:
        relation: Relation = site.payload
        return relation.reversed_text, 0.0, 0.0
    raise CatalogueGenerationError(f"no mutator for class {site.defect_class!r}")


def line_is_self_refuting(fragment: str) -> bool:
    """Does this text, read ALONE, contradict itself?

    The fragment is normally 1 line, and it is analysed with no access to the rest
    of the document: symbols resolve only against bindings the fragment itself
    makes. That is what "a reader who does not leave this line" means, expressed as
    something that runs.
    """
    bindings = symbol_table(fragment)
    symbols, inconsistent = resolve_symbols(fragment)
    if inconsistent:
        return True
    if any(not i.holds for i in identity_candidates(fragment)):
        return True
    return any(not r.holds for r in relation_candidates(fragment, symbols, bindings))


@dataclasses.dataclass(frozen=True)
class _Mutation:
    """A site with its mutation chosen and its difficulty measured."""

    site: _Site
    replacement: str
    correct_value: float
    seeded_value: float
    difficulty: str


def _measure_difficulty(text: str, site: _Site, replacement: str) -> str:
    """How far a reader must travel to refute THIS plant. Measured, not assigned.

    DIFFICULTY IS A PROPERTY OF THE SEEDED DOCUMENT, NOT OF THE SITE, and getting
    that wrong is the failure this whole module is built against. An earlier
    version labelled every `quantity_scale_error` `distributed` because rescaling
    a symbol contradicts its OTHER binding, which lives on another line. True as
    far as it goes, and wrong as a difficulty: on FIXTURE line 9, "`f_s = 480 Hz`
    is greater than `f_max = 180 Hz`", rescaling f_max UP to 10800 also makes the
    relation on that very line false, so a reader refutes it without going
    anywhere. Rescaling f_max DOWN to 0.18 leaves the relation true, and that
    plant really is distributed. Same site, same operator, 2 different
    difficulties, decided by the factor drawn.

    Measured over 20 seeds before the correction: 7 of 426 plants carried the
    wrong label. Small, and it mislabels in the damaging direction -- easy plants
    counted as hard, inflating the apparent difficulty of the split that gets
    reported.

    The rule is unchanged and is now enforced rather than asserted: difficulty is
    the EASIEST refutation available, so a line that refutes itself is `local`
    whatever else the document could also say about it.
    """
    line_start, line_end = line_bounds(text, site.line)
    clean_line = text[line_start:line_end]
    seeded_line = (clean_line[: site.offset - line_start] + replacement
                   + clean_line[site.end - line_start:])
    if line_is_self_refuting(clean_line):
        # The clean line already contradicts itself, so a plant here would be
        # scored against a defect the generator did not create. Callers drop it.
        return ""
    return DIFFICULTY_LOCAL if line_is_self_refuting(seeded_line) else DIFFICULTY_DISTRIBUTED


def _count_cross_check_sites(text: str, site: _Site) -> int:
    """Other places a reader could check the mutated token against.

    Deliberately narrow, and named for exactly what it counts. It is the number of
    OTHER occurrences in the clean document of the symbol the site binds, or of the
    literal text the site mutates. It is a detectability signal, not a blast
    radius, and it is not a measure of downstream damage -- calling it one would be
    a number invented to sound like a measurement.
    """
    if site.symbol:
        return max(0, len(re.findall(rf"\b{re.escape(site.symbol)}\b", text)) - 1)
    token = text[site.offset:site.end]
    return max(0, len(re.findall(re.escape(token), text)) - 1)


def _refutation(text: str, site: _Site) -> Refutation:
    if site.defect_class in (CLASS_STATED_RESULT.name, CLASS_OPERAND.name):
        identity: Identity = (site.payload if site.defect_class == CLASS_STATED_RESULT.name
                              else site.payload[0])
        return Refutation(
            kind="recompute_identity",
            spans=((identity.expr_offset, identity.result_end,
                    text[identity.expr_offset:identity.result_end]),),
            explanation=(
                f"evaluating {identity.expr!r} gives {identity.computed!r}, which the "
                f"stated result must match to within {identity.tolerance!r}"),
        )
    if site.defect_class == CLASS_QUANTITY_SCALE.name:
        occurrences: tuple[Assignment, ...] = site.payload[1]
        spans = tuple(
            (a.offset, a.end, text[a.offset:a.end])
            for a in occurrences if a.offset != site.offset
        )
        return Refutation(
            kind="cross_reference_quantity",
            spans=spans,
            explanation=(
                f"the document binds {site.symbol} to the same value at "
                f"{len(occurrences)} places; after the edit those bindings disagree"),
        )
    relation: Relation = site.payload
    return Refutation(
        kind="evaluate_relation",
        spans=(relation.lhs_span, relation.rhs_span),
        explanation=(
            f"the relation is stated between {relation.lhs_value!r} and "
            f"{relation.rhs_value!r}; reversing the operator makes it false"),
    )


# --------------------------------------------------------------------------- #
# Generation                                                                   #
# --------------------------------------------------------------------------- #
def generate_catalogue(text: str, *, seed_value: int, domain: str,
                       per_stratum_limit: int | None = None) -> Catalogue:
    """Produce a deterministic catalogue of mechanically generated plants.

    Determinism is the property the whole exercise rests on: a benchmark that
    cannot be regenerated cannot be re-run against a changed system. Every random
    choice here comes from `random.Random(seed_value)`. The global `random` module
    is never read or seeded, and no `set` or `dict` iteration reaches the output
    ordering -- both would make the catalogue depend on process state rather than
    on the seed.

    Splits are stratified by (generator, difficulty), and every stratum
    contributes an EVEN number of plants, half to each split. That is a direct
    answer to the 2026-09-01 measurement recorded in `bench/canary_seeding.py`:
    both plants requiring real reasoning landed in the calibration split, which
    `detection_rate` does not report, so p_hat read 1.000 while 40% of the plants
    went unfound. A stratum offering only 1 site is dropped and counted, because a
    single member lands entirely in 1 split and reproduces that failure exactly.
    """
    rng = random.Random(seed_value)
    sites, report = collect_sites(text)

    # Feasibility, greedily, over an rng-shuffled copy of the offset-sorted list.
    # 3 constraints, each with a reason:
    #   disjoint widened spans -- an earlier edit inside a later `find` makes that
    #     `find` unfindable and `seed()` raises;
    #   1 plant per line -- a detection claim names a line, so 2 plants on 1 line
    #     make the claim ambiguous and the grading arbitrary;
    #   1 plant per symbol -- 2 rescalings of the same symbol leave no unmutated
    #     occurrence to refute either of them.
    shuffled = list(sites)
    rng.shuffle(shuffled)
    feasible: list[_Site] = []
    used_lines: set[int] = set()
    used_symbols: set[str] = set()
    taken: list[tuple[int, int]] = []
    for site in shuffled:
        if site.line in used_lines:
            continue
        if site.symbol and site.symbol in used_symbols:
            continue
        if any(site.find_lo < hi and lo < site.find_hi for lo, hi in taken):
            continue
        feasible.append(site)
        used_lines.add(site.line)
        if site.symbol:
            used_symbols.add(site.symbol)
        taken.append((site.find_lo, site.find_hi))
    feasible.sort(key=lambda s: (s.offset, s.defect_class))

    # MUTATE BEFORE STRATIFYING. Difficulty is a property of the mutation, not of
    # the site (see `_measure_difficulty`), so it cannot be known until the factor
    # has been drawn. Doing it in this order also removes a defect the earlier
    # order carried silently: a chosen site whose mutation failed used to leave its
    # pair partner behind, tilting that stratum by 1 plant with nothing to show it.
    # A site that cannot be mutated now drops before pairing, so pairs are always
    # whole.
    mutated: list[_Mutation] = []
    unmutatable = 0
    self_refuting = 0
    for site in feasible:
        mutation = _mutate(site, text, rng)
        if mutation is None:
            unmutatable += 1
            continue
        replacement, correct_value, seeded_value = mutation
        difficulty = _measure_difficulty(text, site, replacement)
        if not difficulty:
            self_refuting += 1  # the clean line already contradicts itself
            continue
        mutated.append(_Mutation(site, replacement, correct_value, seeded_value,
                                 difficulty))

    strata: dict[tuple[str, str], list[_Mutation]] = {}
    for entry in mutated:
        generator = _CLASS_BY_NAME[entry.site.defect_class].generator
        strata.setdefault((generator, entry.difficulty), []).append(entry)

    # A "pair" is 1 site for the held-out split and 1 for calibration, drawn from
    # the same stratum. Plants are only ever added or removed in pairs, so the 2
    # splits keep the same (generator, difficulty) profile no matter what is
    # dropped later. That is the whole defence against the 2026-09-01 failure.
    chosen: list[tuple[_Mutation, str, str]] = []  # (mutation, split, pair key)
    dropped_singletons: dict[str, int] = {}
    for key in sorted(strata):
        members = list(strata[key])
        rng.shuffle(members)
        limit = len(members) if per_stratum_limit is None else min(per_stratum_limit,
                                                                   len(members))
        limit -= limit % 2  # even, so the 2 splits get equal shares
        if limit == 0:
            dropped_singletons[f"{key[0]}|{key[1]}"] = len(members)
            continue
        for index, entry in enumerate(members[:limit]):
            pair_key = f"{key[0]}|{key[1]}|{index // 2}"
            chosen.append((entry, HELD_OUT if index % 2 == 0 else CALIBRATION, pair_key))

    chosen.sort(key=lambda item: (item[0].site.offset, item[0].site.defect_class))

    defects: list[SeededDefect] = []
    pair_of: dict[str, str] = {}
    for index, (entry, split, pair_key) in enumerate(chosen):
        site = entry.site
        replacement = entry.replacement
        correct_value = entry.correct_value
        seeded_value = entry.seeded_value
        difficulty = entry.difficulty
        klass = _CLASS_BY_NAME[site.defect_class]
        original = text[site.offset:site.end]
        find = text[site.find_lo:site.find_hi]
        replace = (text[site.find_lo:site.offset] + replacement
                   + text[site.end:site.find_hi])
        line, col = line_col(text, site.offset)
        numeric = site.defect_class != CLASS_RELATION.name
        relative_error = (abs(seeded_value - correct_value) / abs(correct_value)
                          if numeric and correct_value != 0.0 else None)
        detection = Detection(
            line=line,
            correct_text=original,
            seeded_text=replacement,
            correct_value=correct_value if numeric else None,
            seeded_value=seeded_value if numeric else None,
            tolerance=(stated_tolerance(original) if numeric else 0.0),
        )
        refutation = _refutation(text, site)
        defect_id = f"SDC-{seed_value}-{index:03d}"
        pair_of[defect_id] = pair_key
        summary = (
            f"{klass.name} at line {line}, column {col}: the document reads "
            f"{replacement!r} where it should read {original!r}. "
            f"Refutation is {refutation.kind}: {refutation.explanation}. "
            f"Severity {klass.severity} (declared): {klass.severity_basis}."
        )
        defects.append(SeededDefect(
            id=defect_id,
            domain=domain,
            defect_class=klass.name,
            generator=klass.generator,
            severity=klass.severity,
            severity_basis=klass.severity_basis,
            split=split,
            difficulty=difficulty,
            find=find,
            replace=replace,
            location=Location(line=line, col=col, offset=site.offset, end=site.end,
                              text=original),
            detection=detection,
            refutation=refutation,
            relative_error=relative_error,
            cross_check_sites=_count_cross_check_sites(text, site),
            summary=summary,
        ))

    # Progressive uniqueness repair. `seed()` applies plants in order, so plant k
    # must be unique in the text AFTER plants 0..k-1 have landed -- a stricter
    # condition than uniqueness in the clean text, and the 1 that actually failed
    # in practice. A colliding plant is removed WITH ITS PAIR, so the split profile
    # is preserved rather than quietly tilting by 1 plant in 1 stratum.
    ambiguity_dropped: list[str] = []
    for _ in range(len(defects) + 1):
        colliding = _first_ambiguous(text, defects)
        if colliding is None:
            break
        pair_key = pair_of[colliding]
        ambiguity_dropped.extend(sorted(d.id for d in defects if pair_of[d.id] == pair_key))
        defects = [d for d in defects if pair_of[d.id] != pair_key]
    else:  # pragma: no cover - the loop bound exceeds the number of removable pairs
        raise CatalogueGenerationError(
            "could not reach a catalogue whose plants all seed unambiguously")

    if not defects:
        raise CatalogueGenerationError(
            "no plant survived generation. The document offered "
            f"{len(sites)} sites, {len(feasible)} of them feasible, and "
            f"{unmutatable} feasible sites could not be mutated within the declared "
            f"relative-error floor of {MIN_RELATIVE_ERROR}. A catalogue of nothing "
            "is not a measurement.")

    held_out_generators = sorted({d.generator for d in defects if d.split == HELD_OUT})
    if len(held_out_generators) < 2:
        raise CatalogueGenerationError(
            f"the held-out split uses {len(held_out_generators)} generator(s) "
            f"({held_out_generators}). `canary_seeding.detection_rate` refuses a "
            "single-generator held-out set, because p_hat would then measure whether "
            "reviewers have learned that 1 generator. Supply a document that "
            "supports at least 2 operators, or raise per_stratum_limit.")

    # Prove the catalogue seeds before returning it. The generator's own account
    # of what it built is not evidence; `seed()` succeeding on it is. This also
    # catches the residual case where an earlier edit CREATES a second occurrence
    # of a later `find`, which the disjointness rule alone cannot rule out.
    canaries = [d.to_canary() for d in defects]
    try:
        _, manifest = seed(text, canaries)
    except (ValueError, CanaryIntegrityError) as exc:
        raise CatalogueGenerationError(
            f"the generated catalogue does not seed cleanly: {exc}") from exc

    coverage = dict(report)
    coverage.update({
        "sites_feasible": len(feasible),
        "sites_mutated": len(mutated),
        "sites_chosen": len(chosen),
        "defects_emitted": len(defects),
        "feasible_but_unmutatable": unmutatable,
        "dropped_clean_line_already_self_refuting": self_refuting,
        "dropped_odd_or_singleton_strata": dropped_singletons,
        "dropped_for_seeding_ambiguity": ambiguity_dropped,
        "defects_by_class": {
            name: sum(1 for d in defects if d.defect_class == name)
            for name in sorted(_CLASS_BY_NAME)
        },
        "split_difficulty_grid": _grid(defects),
        "held_out_generators": held_out_generators,
        "min_relative_error": MIN_RELATIVE_ERROR,
    })
    return Catalogue(
        format=CATALOGUE_FORMAT,
        seed=seed_value,
        domain=domain,
        source_sha256=hashlib.sha256(text.encode("utf-8")).hexdigest(),
        seeded_sha256=manifest["seeded_sha256"],
        defects=tuple(defects),
        coverage=coverage,
    )


def _first_ambiguous(text: str, defects: Sequence[SeededDefect]) -> str | None:
    """The id of the first plant that would not seed cleanly, applying them in order.

    Mirrors what `canary_seeding.seed` does -- a progressive `str.replace` -- so
    that a collision is found here, where it can be repaired, rather than at
    seeding time where it is a hard failure.
    """
    working = text
    for defect in defects:
        if working.count(defect.find) != 1:
            return defect.id
        working = working.replace(defect.find, defect.replace, 1)
    return None


def _grid(defects: Sequence[SeededDefect]) -> dict[str, dict[str, int]]:
    out: dict[str, dict[str, int]] = {}
    for defect in defects:
        tier = defect.difficulty.split("-")[0]
        out.setdefault(defect.split, {}).setdefault(tier, 0)
        out[defect.split][tier] += 1
    return out


# --------------------------------------------------------------------------- #
# Serialisation                                                                #
# --------------------------------------------------------------------------- #
def catalogue_to_json(catalogue: Catalogue) -> dict[str, Any]:
    """The 2 views of 1 catalogue, in 1 file.

    `canaries` is the blinded seeding view and is exactly what
    `canary_seeding.load_catalogue` reads -- it does `Canary(**c)`, which rejects
    any extra key, so the ground truth cannot ride inside it. `ground_truth`
    carries the machine-checkable record beside it under a key `load_catalogue`
    ignores. Both describe the same plants and are keyed by the same ids.
    """
    return {
        "format": catalogue.format,
        "seed": catalogue.seed,
        "domain": catalogue.domain,
        "source_sha256": catalogue.source_sha256,
        "seeded_sha256": catalogue.seeded_sha256,
        "coverage": catalogue.coverage,
        "canaries": [dataclasses.asdict(c) for c in catalogue.canaries()],
        "ground_truth": [d.as_dict() for d in catalogue.defects],
    }


def catalogue_from_json(payload: dict[str, Any]) -> Catalogue:
    if payload.get("format") != CATALOGUE_FORMAT:
        raise CatalogueGenerationError(
            f"unknown catalogue format {payload.get('format')!r}; expected "
            f"{CATALOGUE_FORMAT!r}")
    defects = []
    for record in payload["ground_truth"]:
        record = dict(record)
        record["location"] = Location(**record["location"])
        record["detection"] = Detection(**record["detection"])
        refutation = dict(record["refutation"])
        refutation["spans"] = tuple(tuple(s) for s in refutation["spans"])
        record["refutation"] = Refutation(**refutation)
        defects.append(SeededDefect(**record))
    return Catalogue(
        format=payload["format"],
        seed=payload["seed"],
        domain=payload["domain"],
        source_sha256=payload["source_sha256"],
        seeded_sha256=payload["seeded_sha256"],
        defects=tuple(defects),
        coverage=payload["coverage"],
    )


def fingerprint(catalogue: Catalogue) -> str:
    """A stable hash of the whole catalogue, for regeneration checks."""
    blob = json.dumps(catalogue_to_json(catalogue), sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def _refuse_in_repo(path: pathlib.Path) -> None:
    worktree = _in_a_git_worktree(path)
    if worktree is not None:
        raise CanaryIntegrityError(
            f"catalogue path is inside a git work tree ({worktree}): {path}\n"
            "A generated catalogue names the defects reviewers are about to be scored "
            "on finding. Committing it publishes the answer key, silently. It belongs "
            "in the key store outside any tracked tree (see bench/vault_keys.sh).")


def write_catalogue(catalogue: Catalogue, path: str | pathlib.Path) -> pathlib.Path:
    target = pathlib.Path(path).expanduser()
    _refuse_in_repo(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(catalogue_to_json(catalogue), indent=2, sort_keys=True,
                   ensure_ascii=False) + "\n",
        encoding="utf-8")
    return target


def load_generated_catalogue(path: str | pathlib.Path) -> Catalogue:
    source = pathlib.Path(path).expanduser()
    _refuse_in_repo(source)
    if not source.is_file():
        raise FileNotFoundError(f"catalogue not found: {source}")
    return catalogue_from_json(json.loads(source.read_text(encoding="utf-8")))


# --------------------------------------------------------------------------- #
# Ground-truth verification, by execution                                      #
# --------------------------------------------------------------------------- #
def seed_one(defect: SeededDefect, clean_text: str) -> str:
    """Seed exactly 1 defect, through the real seeder.

    Going through `canary_seeding.seed` rather than a local `str.replace` is
    deliberate: verification then exercises the function that will actually be used
    in a run, including its uniqueness and blinding guards. A private replacement
    path here would let this module certify a plant that the production seeder
    would refuse.
    """
    seeded, _ = seed(clean_text, [defect.to_canary()])
    return seeded


def _refutation_holds(defect: SeededDefect, text: str) -> bool:
    """True when the document is SELF-CONSISTENT at the plant's site.

    Everything is re-extracted from `text`. Nothing stored on the defect is used
    except the line and the symbol under test, so a record whose stored values are
    wrong cannot make this function agree with it.

    CONSISTENCY IS A PROPERTY OF THE WHOLE LINE, not of 1 located expression, and
    that is a correction rather than a convenience. Locating the identity by
    offset broke whenever a mutation changed the span's LENGTH -- "1.5625" scaled
    by 10 renders "15.6250", 1 character longer, so every offset after it moves.
    Asking instead whether EVERY candidate identity on the line holds is
    offset-free, survives a reviewer rewriting the whole line in
    `check_detection`, and cannot mistake a line that never had an identity for a
    line whose identity was broken.
    """
    kind = defect.refutation.kind
    line = defect.location.line
    if kind == "recompute_identity":
        start, end = line_bounds(text, line)
        on_line = [i for i in identity_candidates(text) if start <= i.expr_offset < end]
        return bool(on_line) and all(i.holds for i in on_line)
    if kind == "cross_reference_quantity":
        symbol = _symbol_of(defect)
        bindings = [a for a in symbol_table(text) if a.symbol == symbol]
        if len(bindings) < 2:
            return False
        return len({(a.value, a.unit) for a in bindings}) == 1
    if kind == "evaluate_relation":
        start, end = line_bounds(text, line)
        bindings = symbol_table(text)
        symbols, _ = resolve_symbols(text)
        on_line = [r for r in relation_candidates(text, symbols, bindings)
                   if start <= r.op_offset < end]
        return bool(on_line) and all(r.holds for r in on_line)
    raise CatalogueGenerationError(f"unknown refutation kind {kind!r}")


def _symbol_of(defect: SeededDefect) -> str:
    """The symbol a cross-reference plant attacks, read out of its explanation.

    The explanation is generated text with a fixed shape, so this is a parse of the
    module's own output rather than a guess about prose.
    """
    match = re.search(r"binds ([A-Za-z_][A-Za-z0-9_]*) to", defect.refutation.explanation)
    return match.group(1) if match else ""


def verify_ground_truth(defect: SeededDefect, clean_text: str) -> GroundTruthCheck:
    """Re-derive a defect's ground truth from the documents. The record is not evidence.

    THIS IS THE `execute-do-not-grep` RULE APPLIED TO A GENERATOR. A test that
    reads the catalogue and agrees with it proves only that the catalogue is
    internally consistent -- which a generator that emitted the constant 42
    everywhere would also satisfy, as long as it recorded 42. So this function
    ignores the stored values wherever it can, re-runs the extractors over both
    documents, and requires:

      the recorded span in the clean text to hold exactly the recorded original;
      the same span in the seeded text to hold the mutation;
      the refutation mechanism to HOLD on the clean text;
      the refutation mechanism to FAIL on the seeded text;
      the recorded numbers to recompute from the re-extracted values.

    Failing the third or fourth is the interesting case: it means the plant is not
    a defect, or the clean document was already broken there.
    """
    failures: list[str] = []
    try:
        seeded_text = seed_one(defect, clean_text)
    except (ValueError, CanaryIntegrityError) as exc:
        return GroundTruthCheck(defect.id, False, (f"seeding failed: {exc}",), False, False)

    if len(seeded_text.split("\n")) != len(clean_text.split("\n")):
        failures.append("the edit changed the line count, so every recorded line is wrong")

    location = defect.location
    observed_clean = clean_text[location.offset:location.end]
    if observed_clean != location.text:
        failures.append(
            f"clean text at offset {location.offset} is {observed_clean!r}, "
            f"not the recorded {location.text!r}")
    if observed_clean != defect.detection.correct_text:
        failures.append(
            f"detection.correct_text {defect.detection.correct_text!r} is not what the "
            f"clean document holds at the recorded span ({observed_clean!r})")

    observed_seeded = seeded_text[location.offset:location.offset
                                  + len(defect.detection.seeded_text)]
    if observed_seeded != defect.detection.seeded_text:
        failures.append(
            f"seeded document holds {observed_seeded!r} at the recorded offset, not the "
            f"recorded {defect.detection.seeded_text!r}")

    recorded_line = location.line
    computed_line, computed_col = line_col(clean_text, location.offset)
    if (computed_line, computed_col) != (recorded_line, location.col):
        failures.append(
            f"recorded line/column ({recorded_line}, {location.col}) does not match the "
            f"offset, which is at ({computed_line}, {computed_col})")

    if defect.detection.correct_value is not None:
        try:
            if abs(float(observed_clean) - defect.detection.correct_value) > 1e-9:
                failures.append(
                    f"correct_value {defect.detection.correct_value!r} is not the number "
                    f"the clean document holds ({observed_clean!r})")
            if abs(float(observed_seeded) - defect.detection.seeded_value) > 1e-9:
                failures.append(
                    f"seeded_value {defect.detection.seeded_value!r} is not the number "
                    f"the seeded document holds ({observed_seeded!r})")
            correct = float(observed_clean)
            seeded_value = float(observed_seeded)
            if correct != 0.0:
                measured = abs(seeded_value - correct) / abs(correct)
                if measured < MIN_RELATIVE_ERROR:
                    failures.append(
                        f"relative error {measured!r} is below the declared floor "
                        f"{MIN_RELATIVE_ERROR!r}, so the plant sits inside the "
                        "document's own rounding")
                if defect.relative_error is None or abs(measured - defect.relative_error) > 1e-9:
                    failures.append(
                        f"recorded relative_error {defect.relative_error!r} does not "
                        f"recompute from the documents ({measured!r})")
        except ValueError:
            failures.append("a numeric plant does not hold a number at its recorded span")

    clean_holds = _refutation_holds(defect, clean_text)
    seeded_holds = _refutation_holds(defect, seeded_text)
    if not clean_holds:
        failures.append(
            f"the {defect.refutation.kind} refutation does not hold on the CLEAN "
            "document, so the plant sits on top of a pre-existing defect")
    if seeded_holds:
        failures.append(
            f"the {defect.refutation.kind} refutation still holds on the SEEDED "
            "document, so the edit did not plant a defect")

    for offset, end, text_span in defect.refutation.spans:
        if clean_text[offset:end] != text_span:
            failures.append(
                f"refutation span at {offset} reads {clean_text[offset:end]!r}, not the "
                f"recorded {text_span!r}")

    klass = _CLASS_BY_NAME.get(defect.defect_class)
    if klass is None:
        failures.append(f"defect class {defect.defect_class!r} is not a declared class")
    else:
        if defect.severity != klass.severity:
            failures.append(
                f"severity {defect.severity!r} is not the declared severity for "
                f"{klass.name} ({klass.severity!r}); severity is a class parameter and "
                "must not be assigned per defect")
        if defect.generator != klass.generator:
            failures.append(
                f"generator {defect.generator!r} does not match the declared generator "
                f"for {klass.name} ({klass.generator!r})")

    recount = _count_cross_check_sites(clean_text, _Site(
        defect_class=defect.defect_class, offset=location.offset, end=location.end,
        line=location.line, find_lo=location.offset,
        find_hi=location.end, symbol=_symbol_of(defect), payload=None))
    if recount != defect.cross_check_sites:
        failures.append(
            f"cross_check_sites {defect.cross_check_sites} does not recount from the "
            f"clean document ({recount})")

    # Difficulty is a measurement, so it is re-measured rather than trusted. It
    # decides which stratum a plant sits in, and a stratum is what keeps hard
    # plants out of the unreported split -- the 2026-09-01 failure exactly.
    start, end = line_bounds(seeded_text, recorded_line)
    remeasured = (DIFFICULTY_LOCAL if line_is_self_refuting(seeded_text[start:end])
                  else DIFFICULTY_DISTRIBUTED)
    if remeasured != defect.difficulty:
        failures.append(
            f"difficulty {defect.difficulty!r} does not re-measure from the seeded "
            f"document ({remeasured!r}); a reader refutes this plant at a different "
            "distance from the one recorded")

    return GroundTruthCheck(
        defect_id=defect.id,
        ok=not failures,
        failures=tuple(failures),
        clean_refutation_holds=clean_holds,
        seeded_refutation_holds=seeded_holds,
    )


def verify_catalogue(catalogue: Catalogue, clean_text: str) -> list[GroundTruthCheck]:
    """Verify every plant, and first check the document is the RIGHT document.

    `verify_ground_truth` checks a plant at its own recorded span, so a change
    ELSEWHERE in the article leaves it verifying clean -- correctly, for 1 plant.
    At catalogue level that is a hole, and it is the hole
    `bench/cdsfl_registry/targets/MANIFEST.md` exists to close: a result means
    nothing unless it is tied to the exact revision of the article that produced
    it, and the manifest records a revision of the control being restated after 7
    claim repairs, so a result could have been attributed to the wrong text.

    Found by this module's own test suite, which tampered with a line AFTER the
    defect under test and watched verification pass. Refusing loudly is right:
    silently verifying against a different article is the failure mode, not the
    exception to it.
    """
    actual = hashlib.sha256(clean_text.encode("utf-8")).hexdigest()
    if actual != catalogue.source_sha256:
        raise CatalogueGenerationError(
            f"this catalogue was generated from a document with sha256 "
            f"{catalogue.source_sha256}, and the text supplied hashes to {actual}. "
            "Verifying a catalogue against a different revision of the article ties "
            "the result to the wrong document.")
    return [verify_ground_truth(d, clean_text) for d in catalogue.defects]


# --------------------------------------------------------------------------- #
# Grading a detection                                                          #
# --------------------------------------------------------------------------- #
EXACT = "EXACT"
CONSISTENT = "CONSISTENT"
MISS = "MISS"


def check_detection(defect: SeededDefect, claim: dict[str, Any], clean_text: str) -> str:
    """Grade a machine-readable detection claim: EXACT, CONSISTENT or MISS.

    `claim` is {"line": int, "corrected_line": str} -- the reviewer names a line and
    supplies it as it should read. The claim is APPLIED to the seeded document and
    the outcome is measured, so grading never depends on wording.

    3 outcomes rather than 2, because collapsing them loses a real distinction.
    Consider an operand plant: the clean line reads "400 / 256 = 1.5625" and the
    seeded line reads "400 / 512 = 1.5625". A reviewer who blames the RESULT
    proposes "400 / 512 = 0.78125". That restores internal consistency but not the
    clean text -- the reviewer found the inconsistency and attributed it to the
    wrong span. Scoring that as a clean hit overstates detection; scoring it as a
    miss understates it. It is its own outcome, and the gap between the 2 rates is
    itself worth reporting.
    """
    seeded_text = seed_one(defect, clean_text)
    line = claim.get("line")
    corrected = claim.get("corrected_line")
    if not isinstance(line, int) or not isinstance(corrected, str):
        return MISS
    lines = seeded_text.split("\n")
    if line < 1 or line > len(lines):
        return MISS
    lines[line - 1] = corrected
    repaired = "\n".join(lines)
    if repaired == clean_text:
        return EXACT
    if line != defect.location.line:
        return MISS
    try:
        if _refutation_holds(defect, repaired):
            return CONSISTENT
    except (IndexError, CatalogueGenerationError):
        return MISS
    return MISS


def make_verifier(catalogue: Catalogue, clean_text: str, *,
                  accept: Sequence[str] = (EXACT,)) -> Callable[[dict, Canary], bool]:
    """A `canary_seeding.catches` verifier backed by execution, not by wording.

    The default accepts EXACT only, which is the strict reading. Widening to
    CONSISTENT is a parameter rather than a default so the choice appears in the
    caller's code and in the run record, instead of being baked in where nobody
    sees it.

    The finding must carry a `claim` in the shape `check_detection` grades.
    Producing that claim from a reviewer's prose is item D8 and is not done here.
    """
    by_id = catalogue.by_id()
    accepted = tuple(accept)

    def verifier(finding: dict, canary: Canary) -> bool:
        defect = by_id.get(canary.id)
        claim = finding.get("claim")
        if defect is None or not isinstance(claim, dict):
            return False
        return check_detection(defect, claim, clean_text) in accepted

    return verifier


# --------------------------------------------------------------------------- #
# CLI                                                                          #
# --------------------------------------------------------------------------- #
def main(argv: Sequence[str] | None = None) -> int:
    """Generate a catalogue from a target file. No network, no model dispatch.

    `--help` costs nothing and reaches no API, which is a standing project rule
    after 15 of 17 runners were measured billing a live dispatch on any
    unrecognised argument.
    """
    parser = argparse.ArgumentParser(
        prog="seeded_defect_catalogue",
        description="Generate a deterministic, machine-checkable seeded-defect catalogue.")
    parser.add_argument("--target", required=True, help="path to the clean review target")
    parser.add_argument("--seed", type=int, required=True, help="generator seed")
    parser.add_argument("--domain", required=True, help="domain label for every plant")
    parser.add_argument("--out", help="write the catalogue here (must be outside any git tree)")
    parser.add_argument("--per-stratum-limit", type=int, default=None,
                        help="cap plants per (generator, difficulty) stratum; rounded down to even")
    parser.add_argument("--verify", action="store_true",
                        help="re-derive every plant's ground truth from the documents")
    args = parser.parse_args(argv)

    # Check the destination BEFORE generating. Refusing afterwards is correct but
    # rude: on a full-length article the caller pays for the whole generation to
    # be told the path was never acceptable.
    if args.out:
        _refuse_in_repo(pathlib.Path(args.out).expanduser())
    text = pathlib.Path(args.target).expanduser().read_text(encoding="utf-8")
    catalogue = generate_catalogue(text, seed_value=args.seed, domain=args.domain,
                                   per_stratum_limit=args.per_stratum_limit)
    print(f"defects: {len(catalogue.defects)}  fingerprint: {fingerprint(catalogue)}")
    print(json.dumps(catalogue.coverage, indent=2, sort_keys=True))
    if args.verify:
        checks = verify_catalogue(catalogue, text)
        bad = [c for c in checks if not c.ok]
        for check in bad:
            print(f"BROKEN {check.defect_id}: " + "; ".join(check.failures))
        print(f"verified {len(checks) - len(bad)} of {len(checks)}")
        if bad:
            return 1
    if args.out:
        written = write_catalogue(catalogue, args.out)
        print(f"written: {written}")
    return 0


if __name__ == "__main__":  # pragma: no cover - exercised by the CLI, not the suite
    raise SystemExit(main())
