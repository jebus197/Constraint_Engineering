"""Code-location novelty keying for convergence detection.

Root cause of CDSFL's recurring non-convergence (verified 2026-06-08): novelty was
decided by free-text similarity (model-chosen finding-id, Jaccard/embedding kappa,
gamma-on-novelty-count). All free-text signals fail on code review because every finding
about one source file looks similar — they cannot tell two distinct defects in the same
file apart, nor recognise a re-worded re-find of the same defect. Empirically: the embedding
ConvergenceDetector at tau_sim_embed=0.55 over-merges Exp 42's findings into ~1 class/round
and FALSELY converges at round 2; the inline model-id path NEVER converges (every re-find
gets a fresh id). Both are the same disease — keying novelty on free text.

The signal that DOES separate code-review defects is the CODE LOCATION: which function /
method / class the finding is about. This module extracts the target file's symbols (AST)
and keys each finding by the symbols it names. A critical finding is "novel" iff it names a
code location not yet flagged by any prior critical.

On Exp 42 this converges at round 7 with a stable zero tail (rounds 5-15 all zero), matching
the signature-trace ground truth (all distinct defects found by ~round 4). The result is
ROBUST to the exact re-find rule (two reasonable variants both give round 7).

Conservative-by-design: a finding counts as NEW if it introduces ANY previously-unseen
location. This biases toward NOT converging (one extra round is cheaper than a missed defect).

Domain-general: works for any Python target file. `target_symbols` accepts source or a path.
For non-Python targets, supply a symbol set directly.

Created 2026-06-08 (T2 discovery). Calibration of the severity threshold and the convergence
window belongs to a null test (clean module -> fast converge) + seeded test (N known defects
-> all found before converge), NEVER to a single experiment's desired answer.
"""
from __future__ import annotations

import ast
import re
from dataclasses import dataclass, field
from typing import FrozenSet, Iterable, List, Optional, Sequence, Set

# Generic identifiers that carry no location information (entry points / dunders).
# Findings naming ONLY these fall back to a single generic bucket.
_GENERIC = frozenset({"main", "compose", "run"})
_MIN_LEN = 4
_GENERIC_BUCKET = "<generic>"


def target_symbols(source_or_path: str) -> FrozenSet[str]:
    """AST-extract function/method/class names from a Python target file.

    Accepts raw source or a filesystem path (``*.py``). Returns names with len > _MIN_LEN
    (short/dunder names are too ambiguous to use as location keys).
    """
    src = source_or_path
    if "\n" not in source_or_path and source_or_path.endswith(".py"):
        with open(source_or_path, "r", encoding="utf-8") as fh:
            src = fh.read()
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return frozenset()
    names: Set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if len(node.name) > _MIN_LEN:
                names.add(node.name)
    return frozenset(names)


def finding_locations(description: str, symbols: Iterable[str]) -> FrozenSet[str]:
    """The subset of `symbols` named (word-boundary match) in a finding description,
    excluding generic identifiers. Empty result means no specific code location."""
    desc = description or ""
    return frozenset(
        s for s in symbols
        if s not in _GENERIC and re.search(r"\b" + re.escape(s) + r"\b", desc)
    )


@dataclass
class LocationNoveltyTracker:
    """Counts NEW critical code-locations per round; declares convergence after K
    consecutive zero-new-critical rounds.

    A critical finding (severity >= severity_threshold) is NEW iff it names at least one
    code location not previously flagged by a critical. Locations named by any critical
    (new or re-find) are accumulated, so an incidental later mention of an already-flagged
    location does not re-trigger novelty.

    Parameters
    ----------
    symbols : the target file's symbol set (from `target_symbols`).
    severity_threshold : critical iff severity >= this (default 0.7 = runner CRITICAL_SEVERITY_THRESHOLD).
    consecutive_required : K consecutive zero-new rounds to converge (default 3).
    earliest_round : do not declare convergence before this round (default 2).
    """
    symbols: FrozenSet[str]
    severity_threshold: float = 0.7
    consecutive_required: int = 3
    earliest_round: int = 2

    _seen_locations: Set[str] = field(default_factory=set)
    _new_per_round: List[int] = field(default_factory=list)
    _zero_streak: int = 0
    _converged_round: Optional[int] = None

    def add_round(self, round_idx: int, findings: Sequence[object]) -> int:
        """Register a round's findings. Returns the count of NEW critical findings
        (those naming a not-yet-flagged code location)."""
        new = 0
        for f in findings:
            sev = getattr(f, "severity", 0.0) or 0.0
            if sev < self.severity_threshold:
                continue
            locs = finding_locations(getattr(f, "description", "") or "", self.symbols)
            key = set(locs) if locs else {_GENERIC_BUCKET}
            if key - self._seen_locations:        # introduces >=1 unseen location
                new += 1
            self._seen_locations |= key
        while len(self._new_per_round) <= round_idx:
            self._new_per_round.append(0)
        self._new_per_round[round_idx] = new
        self._zero_streak = self._zero_streak + 1 if new == 0 else 0
        if (self._converged_round is None
                and round_idx >= self.earliest_round
                and self._zero_streak >= self.consecutive_required):
            self._converged_round = round_idx
        return new

    @property
    def new_per_round(self) -> List[int]:
        return list(self._new_per_round)

    @property
    def converged_round(self) -> Optional[int]:
        return self._converged_round

    def converged(self) -> bool:
        return self._converged_round is not None
