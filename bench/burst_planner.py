"""Burst decomposition planner for CDSFL experiments.

Automatically decomposes large test articles into focused phases based on
code structure and model capability fingerprints. Each phase converges
independently before a final integration round where models verify that
individually-converged findings integrate correctly.

The models see no difference — each phase is an ordinary review task.
The burst orchestration is entirely in the runner.
"""
from __future__ import annotations

import ast
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────

CHARS_PER_TOKEN = 3.5
OVERHEAD_CHARS = 15_000  # preamble + task instructions + headers + system prompt
RESPONSE_RESERVE_TOKENS = 16_000
SIGNATURE_OVERHEAD_CHARS = 3_000  # approximate size of out-of-phase signatures
MIN_SECTIONS_FOR_STRUCTURAL_BURST = 8
QUALITY_DECAY_FACTOR = 0.65  # D_decay scaling: L * (1 - D_decay * factor)

# Quality target: focused phases produce more accurate SEARCH/REPLACE blocks.
# ~30K chars ≈ 9K tokens per phase — leaves ample room for reasoning.
PHASE_TARGET_CHARS = 30_000


# ─────────────────────────────────────────────────────────────────────────────
# Data structures
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class CodeSection:
    """A logical section of source code identified by comment markers."""
    name: str
    start_line: int
    end_line: int
    source: str
    definitions: List[str] = field(default_factory=list)

    @property
    def char_count(self) -> int:
        return len(self.source)


@dataclass
class BurstPhase:
    """One phase of a burst-decomposed experiment."""
    name: str
    index: int
    sections: List[CodeSection]
    char_count: int

    @property
    def definition_names(self) -> List[str]:
        names = []
        for s in self.sections:
            names.extend(s.definitions)
        return names


@dataclass
class BurstPlan:
    """Complete burst decomposition plan."""
    phases: List[BurstPhase]
    signatures: str
    total_source_chars: int
    budget_chars_per_phase: int
    trigger_reason: str
    target_file: str


# ─────────────────────────────────────────────────────────────────────────────
# Section detection
# ─────────────────────────────────────────────────────────────────────────────


def detect_sections(source: str) -> List[CodeSection]:
    """Parse source and identify logical sections by comment markers.

    Detects the pattern:
        # ─────────...
        # Section title
        # ─────────...

    Falls back to treating the entire source as one section if no markers found.
    """
    lines = source.split("\n")
    separator_re = re.compile(r"^#\s*[─━═]{10,}")

    # Find all separator lines
    separator_lines: List[int] = []
    for i, line in enumerate(lines):
        if separator_re.match(line):
            separator_lines.append(i)

    # Extract section boundaries: look for title line between separators
    boundaries: List[Tuple[str, int]] = []  # (name, start_line_0indexed)
    i = 0
    while i < len(separator_lines) - 1:
        sep1 = separator_lines[i]
        sep2 = separator_lines[i + 1]
        # Title is between the two separators
        if sep2 - sep1 == 2:
            title_line = lines[sep1 + 1].strip().lstrip("# ").strip()
            if title_line:
                boundaries.append((title_line, sep1))
                i += 2
                continue
        i += 1

    if not boundaries:
        return [CodeSection(
            name="entire_file",
            start_line=1,
            end_line=len(lines),
            source=source,
            definitions=_extract_definition_names(source, 1, len(lines)),
        )]

    sections: List[CodeSection] = []

    # Module header (before first section marker)
    if boundaries[0][1] > 0:
        header_source = "\n".join(lines[:boundaries[0][1]])
        if header_source.strip():
            sections.append(CodeSection(
                name="module_header",
                start_line=1,
                end_line=boundaries[0][1],
                source=header_source,
                definitions=_extract_definition_names(
                    header_source, 1, boundaries[0][1]),
            ))

    # Named sections
    for idx, (name, start_0) in enumerate(boundaries):
        if idx + 1 < len(boundaries):
            end_0 = boundaries[idx + 1][1]
        else:
            end_0 = len(lines)
        section_source = "\n".join(lines[start_0:end_0])
        sections.append(CodeSection(
            name=name,
            start_line=start_0 + 1,
            end_line=end_0,
            source=section_source,
            definitions=_extract_definition_names(
                section_source, start_0 + 1, end_0),
        ))

    return sections


def _extract_definition_names(
    source: str, start_line: int, end_line: int,
) -> List[str]:
    """Extract top-level function and class names from a source fragment."""
    names: List[str] = []
    try:
        # Wrap in try — fragments may not parse standalone
        tree = ast.parse(source)
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef,
                                 ast.ClassDef)):
                names.append(node.name)
    except SyntaxError:
        # Fall back to regex for unparseable fragments
        for m in re.finditer(r"^(?:def|class)\s+(\w+)", source, re.MULTILINE):
            names.append(m.group(1))
    return names


# ─────────────────────────────────────────────────────────────────────────────
# Signature extraction
# ─────────────────────────────────────────────────────────────────────────────


def extract_signatures(source: str) -> str:
    """Extract function/class signatures with first-line docstrings.

    Produces a compact representation that gives models enough context
    to understand interfaces without consuming context budget.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return "# (could not parse source for signatures)\n"

    lines = source.split("\n")
    sigs: List[str] = []

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            sig = _function_signature(node, lines)
            sigs.append(sig)
        elif isinstance(node, ast.ClassDef):
            sig = _class_signature(node, lines)
            sigs.append(sig)

    return "\n\n".join(sigs) + "\n" if sigs else ""


def _function_signature(node: ast.FunctionDef, lines: List[str]) -> str:
    """Extract a function's signature + first docstring line."""
    # Collect the def line(s) up to the colon
    sig_lines: List[str] = []
    for i in range(node.lineno - 1, min(node.end_lineno or node.lineno, len(lines))):
        sig_lines.append(lines[i])
        if lines[i].rstrip().endswith(":"):
            break

    sig = "\n".join(sig_lines)

    # Add first line of docstring if present
    doc = _first_docstring_line(node)
    if doc:
        indent = "    "
        sig += f'\n{indent}"""{doc}"""'

    sig += "\n    ..."
    return sig


def _class_signature(node: ast.ClassDef, lines: List[str]) -> str:
    """Extract a class definition + method signatures."""
    # Class def line
    class_line = lines[node.lineno - 1]
    parts = [class_line]

    doc = _first_docstring_line(node)
    if doc:
        parts.append(f'    """{doc}"""')

    # Method signatures
    for item in node.body:
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
            method_sig = _function_signature(item, lines)
            # Indent method signatures (they're already indented in source)
            parts.append(method_sig)

    return "\n".join(parts)


def _first_docstring_line(node: ast.AST) -> Optional[str]:
    """Get the first line of a node's docstring, if any."""
    if (hasattr(node, "body") and node.body and
            isinstance(node.body[0], ast.Expr) and
            isinstance(node.body[0].value, ast.Constant) and
            isinstance(node.body[0].value.value, str)):
        return node.body[0].value.value.strip().split("\n")[0].strip()
    return None


# ─────────────────────────────────────────────────────────────────────────────
# Burst decision
# ─────────────────────────────────────────────────────────────────────────────


def should_burst(
    source_chars: int,
    context_chars: int,
    model_specs: Dict[str, Dict[str, float]],
    fingerprints: Dict[str, Any],
    models: List[str],
) -> Tuple[bool, str]:
    """Decide whether burst decomposition is needed.

    Returns (needed, reason). Three trigger conditions — any one fires burst:
    1. Prompt won't fit in at least one model's context window
    2. Prompt exceeds quality threshold for at least one model (D_decay)
    3. Source has enough independent sections for structural benefit
    """
    total_chars = source_chars + context_chars + OVERHEAD_CHARS
    total_tokens = total_chars / CHARS_PER_TOKEN

    reasons: List[str] = []

    for model in models:
        spec = model_specs.get(model, {})
        model_L = spec.get("L", float("inf"))

        # Condition 1: hard overflow
        if total_tokens + RESPONSE_RESERVE_TOKENS > model_L:
            reasons.append(
                f"{model}: {total_tokens:,.0f} + {RESPONSE_RESERVE_TOKENS:,} "
                f"tokens > L={model_L:,.0f}"
            )

        # Condition 2: quality degradation from attention decay
        fp = fingerprints.get(model)
        if fp is not None:
            d_decay = getattr(fp, "D_decay", 0.0)
            quality_L = model_L * (1.0 - d_decay * QUALITY_DECAY_FACTOR)
            if total_tokens > quality_L:
                reasons.append(
                    f"{model}: {total_tokens:,.0f} tokens > quality "
                    f"threshold {quality_L:,.0f} (D_decay={d_decay})"
                )

    if reasons:
        return True, f"Context overflow: {'; '.join(reasons[:3])}"

    return False, ""


# ─────────────────────────────────────────────────────────────────────────────
# Phase planning
# ─────────────────────────────────────────────────────────────────────────────


def plan_phases(
    source: str,
    model_specs: Dict[str, Dict[str, float]],
    fingerprints: Dict[str, Any],
    models: List[str],
    target_file: str,
) -> BurstPlan:
    """Create a burst decomposition plan for the given source.

    Groups logical sections into phases that fit within the smallest
    model's effective context budget. Returns a BurstPlan with phases
    and pre-computed signatures for out-of-phase context.
    """
    sections = detect_sections(source)
    signatures = extract_signatures(source)

    # Compute effective budget per phase.
    # Two constraints: must fit in models, and should be focused for quality.
    # Use the TIGHTER of the two.
    min_L_tokens = min(
        model_specs.get(m, {}).get("L", float("inf")) for m in models
    )
    overhead_tokens = (OVERHEAD_CHARS + SIGNATURE_OVERHEAD_CHARS) / CHARS_PER_TOKEN
    model_budget_tokens = min_L_tokens - overhead_tokens - RESPONSE_RESERVE_TOKENS
    model_budget_chars = int(model_budget_tokens * CHARS_PER_TOKEN)

    # Use the tighter of model capacity and quality target
    budget_chars = min(model_budget_chars, PHASE_TARGET_CHARS)
    budget_chars = max(budget_chars, 15_000)  # floor: never smaller than 15K

    # Group sections into phases that fit within budget
    phases: List[BurstPhase] = []
    current_sections: List[CodeSection] = []
    current_chars = 0

    for section in sections:
        # If adding this section would exceed budget and we have content,
        # close the current phase
        if (current_chars + section.char_count > budget_chars
                and current_sections):
            phases.append(_make_phase(phases, current_sections, current_chars))
            current_sections = []
            current_chars = 0

        current_sections.append(section)
        current_chars += section.char_count

    # Don't forget the last group
    if current_sections:
        phases.append(_make_phase(phases, current_sections, current_chars))

    # If we only got one phase, burst decomposition isn't needed at this level
    # but we still return the plan — the caller can decide whether to use it
    need_burst, reason = should_burst(
        len(source),
        0,  # context not included in phases
        model_specs, fingerprints, models,
    )

    return BurstPlan(
        phases=phases,
        signatures=signatures,
        total_source_chars=len(source),
        budget_chars_per_phase=budget_chars,
        trigger_reason=reason,
        target_file=target_file,
    )


def _make_phase(
    existing: List[BurstPhase],
    sections: List[CodeSection],
    char_count: int,
) -> BurstPhase:
    """Create a BurstPhase from accumulated sections."""
    idx = len(existing)
    # Name from section names, truncated for readability
    names = [s.name for s in sections]
    if len(names) == 1:
        name = names[0]
    elif len(names) <= 3:
        name = " + ".join(names)
    else:
        name = f"{names[0]} + {len(names) - 1} more"
    return BurstPhase(
        name=name,
        index=idx,
        sections=sections,
        char_count=char_count,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Prompt builders
# ─────────────────────────────────────────────────────────────────────────────


def build_phase_code(
    phase: BurstPhase,
    target_file: str,
    signatures: str,
    prior_findings_summary: str = "",
) -> str:
    """Build the code payload for a specific phase dispatch.

    Includes:
    - Full source of the phase's sections (the code to review)
    - Signatures of all other sections (interface context)
    - Prior phase findings summary (cross-phase awareness)
    """
    # Phase source: concatenate section sources
    phase_source = "\n\n".join(s.source for s in phase.sections)
    section_names = ", ".join(s.name for s in phase.sections)

    parts = [
        f"=== TARGET FILE (REVIEW THIS): {target_file} ===",
        f"=== PHASE FOCUS: {section_names} ({len(phase_source):,} chars) ===",
        f"Review ONLY the code in this section. Other sections shown as "
        f"signatures for interface context only.",
        "",
        phase_source,
        "",
        f"=== SIGNATURES: Other sections ({len(signatures):,} chars) ===",
        f"(Interface context only — do NOT review these)",
        "",
        signatures,
    ]

    if prior_findings_summary:
        parts.extend([
            "",
            "=== PRIOR CONVERGED FINDINGS ===",
            "(From earlier phases — for cross-reference awareness only)",
            "",
            prior_findings_summary,
        ])

    return "\n".join(parts)


def build_integration_code(
    full_source: str,
    target_file: str,
    all_findings_summary: str,
    context_signatures: str = "",
) -> str:
    """Build the code payload for the integration round.

    All models see the full target source + all converged findings.
    Context files are included as signatures only (interface context).
    """
    parts = [
        f"=== INTEGRATION REVIEW: {target_file} ({len(full_source):,} chars) ===",
        "Previous phases identified the findings listed below. Each finding "
        "converged independently. Your task: verify these findings integrate "
        "correctly and identify any CROSS-CUTTING issues the focused phase "
        "reviews missed. Do NOT re-report findings already listed below unless "
        "you have new evidence that changes the verdict.",
        "",
        f"=== FULL SOURCE: {target_file} ===",
        full_source,
    ]

    if context_signatures:
        parts.extend([
            "",
            f"=== CONTEXT SIGNATURES ({len(context_signatures):,} chars) ===",
            "(Interface context for cross-file references)",
            context_signatures,
        ])

    parts.extend([
        "",
        f"=== CONVERGED FINDINGS ({len(all_findings_summary):,} chars) ===",
        all_findings_summary,
    ])

    return "\n".join(parts)


def build_findings_summary(
    registry_entries: Dict[str, Any],
    phase_name: Optional[str] = None,
) -> str:
    """Build a compact findings summary for cross-phase awareness.

    One line per finding: ID, severity, status, description first line.
    """
    lines: List[str] = []
    for cid, entry in sorted(registry_entries.items()):
        status = entry.get("status", "UNKNOWN")
        severity = entry.get("severity", 0.0)
        desc = entry.get("description", "")
        first_line = desc.split("\n")[0][:120] if desc else "(no description)"
        phase_tag = f" [{phase_name}]" if phase_name else ""
        lines.append(
            f"  {cid}: severity={severity:.2f} status={status}"
            f"{phase_tag} — {first_line}"
        )
    return "\n".join(lines) if lines else "(no findings)"


# ─────────────────────────────────────────────────────────────────────────────
# Phase convergence config
# ─────────────────────────────────────────────────────────────────────────────


def phase_convergence_overrides(phase_round_offset: int) -> Dict[str, Any]:
    """Return convergence config overrides for a burst phase.

    Tighter convergence: focused prompts produce higher-quality findings
    faster, so phases converge in fewer rounds.
    """
    return {
        "earliest_stop_round": phase_round_offset + 3,
        "rho_earliest_round": phase_round_offset + 3,
        "gamma_telemetry_only_until": phase_round_offset + 2,
        "gamma_soft_gate_until": phase_round_offset + 4,
        "gamma_soft_threshold": 0.25,
        "gamma_hard_threshold": 0.30,
        "stall_earliest_round": phase_round_offset + 5,
        "consecutive_rounds_required": 2,
    }


def integration_convergence_overrides(
    integration_round_offset: int,
) -> Dict[str, Any]:
    """Return convergence config overrides for the integration round.

    Integration is a single-pass verification — converge quickly.
    """
    return {
        "earliest_stop_round": integration_round_offset + 1,
        "rho_earliest_round": integration_round_offset + 1,
        "gamma_telemetry_only_until": integration_round_offset,
        "gamma_soft_gate_until": integration_round_offset + 2,
        "gamma_soft_threshold": 0.20,
        "gamma_hard_threshold": 0.25,
        "stall_earliest_round": integration_round_offset + 3,
        "consecutive_rounds_required": 2,
    }
