"""Domain parameterisation for the immune verification pipeline.

Phase B4: the immune pipeline's 6-stage architecture is domain-agnostic,
but stages 1-3 need domain-specific content:

    Stage 1 (Dendritic Cell):  Claim classification patterns
    Stage 2a (Cytotoxic T):    Prompt template + citation format
    Stage 2b (B Cell):         Tool selection per claim type
    Stage 3 (NK Cell):         Known false-positive patterns

Stages 4-5 (Helper T, Regulatory T) are fully domain-agnostic.

Domain configs are loaded from TOML files in bench/cdsfl_registry/domains/immune/.
Each immune TOML contains only the [immune] section with domain-specific content.
The main domain TOMLs in domains/ contain only PolicyEngine Layer 2 config.

Usage:
    from bench.domain_immune import load_domain_config, domain_classify_claim

    cfg = load_domain_config("mathematics")
    claim_type, assertion = domain_classify_claim(finding, cfg)
    tools = domain_b_cell_tools(claim_type, cfg)
    fp_list = domain_false_positives(cfg)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore[no-redef]  # Python < 3.11 fallback
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from bench.dm._types import Finding


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_DOMAINS_DIR = Path(__file__).parent / "cdsfl_registry" / "domains"
_IMMUNE_DIR = _DOMAINS_DIR / "immune"

# Re-use the pipeline's ClaimType enum via string mapping so this module
# has no circular import on immune_agents.  The canonical enum lives there;
# here we work with string keys and convert on the boundary.
_CLAIM_TYPE_VALUES = {
    "mathematical", "logical", "code_structural", "code_behavioral",
    "statistical", "uncategorised",
}


# ---------------------------------------------------------------------------
# DomainConfig dataclass
# ---------------------------------------------------------------------------

@dataclass
class DomainConfig:
    """Domain-specific configuration consumed by immune pipeline stages 1-3.

    Loaded from the [immune] section of a domain TOML file.
    """

    # Identity
    domain: str                                     # e.g. "mathematics"

    # Stage 1 — Dendritic Cell: claim classification
    # Maps ClaimType value string -> list of regex pattern strings.
    # Patterns are compiled lazily on first access via compiled_patterns().
    claim_patterns: Dict[str, List[str]] = field(default_factory=dict)

    # Stage 2a — Cytotoxic T Cell
    ct_prompt_template: str = ""                    # domain-specific prompt header
    citation_format: str = ""                       # regex for extracting citations

    # Stage 2b — B Cell: tool selection
    # Maps ClaimType value string -> ordered list of tool names.
    # First tool is primary; rest are class-switch fallbacks.
    verification_tools: Dict[str, List[str]] = field(default_factory=dict)

    # Stage 3 — NK Cell: known false-positive patterns
    # Each entry: {"pattern": regex_str, "source": str, "expected_model": optional str}
    false_positive_patterns: List[Dict[str, str]] = field(default_factory=list)

    # Cached compiled regexes (populated on first call)
    _compiled_claim: Optional[Dict[str, List["re.Pattern[str]"]]] = field(
        default=None, init=False, repr=False,
    )
    _compiled_fp: Optional[List[Dict[str, Any]]] = field(
        default=None, init=False, repr=False,
    )
    _compiled_citation: Optional["re.Pattern[str]"] = field(
        default=None, init=False, repr=False,
    )

    # -- lazy compilation --------------------------------------------------

    def compiled_claim_patterns(self) -> Dict[str, List["re.Pattern[str]"]]:
        """Return claim_patterns with regexes compiled and cached."""
        if self._compiled_claim is None:
            self._compiled_claim = {}
            for ctype, patterns in self.claim_patterns.items():
                self._compiled_claim[ctype] = [
                    re.compile(p, re.IGNORECASE | re.DOTALL) for p in patterns
                ]
        return self._compiled_claim

    def compiled_false_positives(self) -> List[Dict[str, Any]]:
        """Return false_positive_patterns with compiled regex objects.

        Output format matches _KNOWN_FALSE_POSITIVES in immune_agents.py:
        each dict has "pattern" (compiled), "source" (str),
        and optionally "expected_model" (str).
        """
        if self._compiled_fp is None:
            self._compiled_fp = []
            for entry in self.false_positive_patterns:
                compiled: Dict[str, Any] = {
                    "pattern": re.compile(
                        entry["pattern"], re.IGNORECASE | re.DOTALL,
                    ),
                    "source": entry.get("source", "domain FP"),
                }
                if "expected_model" in entry:
                    compiled["expected_model"] = entry["expected_model"]
                self._compiled_fp.append(compiled)
        return self._compiled_fp

    def compiled_citation_regex(self) -> Optional["re.Pattern[str]"]:
        """Return compiled citation_format regex, or None if unset."""
        if self._compiled_citation is None and self.citation_format:
            self._compiled_citation = re.compile(self.citation_format)
        return self._compiled_citation


# ---------------------------------------------------------------------------
# TOML loader
# ---------------------------------------------------------------------------

def _parse_immune_section(domain: str, raw: Dict[str, Any]) -> DomainConfig:
    """Extract the [immune] section from a parsed TOML dict.

    If [immune] is absent, returns a minimal DomainConfig with the
    domain name set but no patterns — the pipeline falls back to
    its built-in hardcoded patterns.
    """
    imm = raw.get("immune", {})

    claim_patterns: Dict[str, List[str]] = {}
    for ctype, patterns in imm.get("claim_patterns", {}).items():
        if ctype not in _CLAIM_TYPE_VALUES:
            continue  # skip unknown claim types silently
        if isinstance(patterns, list):
            claim_patterns[ctype] = patterns
        elif isinstance(patterns, str):
            claim_patterns[ctype] = [patterns]

    verification_tools: Dict[str, List[str]] = {}
    for ctype, tools in imm.get("verification_tools", {}).items():
        if ctype not in _CLAIM_TYPE_VALUES:
            continue
        if isinstance(tools, list):
            verification_tools[ctype] = tools
        elif isinstance(tools, str):
            verification_tools[ctype] = [tools]

    fp_list: List[Dict[str, str]] = []
    for entry in imm.get("false_positive_patterns", []):
        if "pattern" in entry:
            fp_list.append(entry)

    return DomainConfig(
        domain=domain,
        claim_patterns=claim_patterns,
        ct_prompt_template=imm.get("ct_prompt_template", ""),
        citation_format=imm.get("citation_format", ""),
        verification_tools=verification_tools,
        false_positive_patterns=fp_list,
    )


def load_domain_config(domain: str) -> DomainConfig:
    """Load a DomainConfig from the matching TOML file.

    Lookup order:
        1. bench/cdsfl_registry/domains/immune/{domain}.toml
        2. bench/cdsfl_registry/domains/immune/cross_domain.toml (fallback)
        3. bench/cdsfl_registry/domains/{domain}.toml (legacy: [immune] in main TOML)
        4. bench/cdsfl_registry/domains/cross_domain.toml (legacy fallback)

    Returns a minimal DomainConfig if no file exists.
    """
    candidates = [
        _IMMUNE_DIR / f"{domain}.toml",
        _IMMUNE_DIR / "cross_domain.toml",
        _DOMAINS_DIR / f"{domain}.toml",
        _DOMAINS_DIR / "cross_domain.toml",
    ]

    for path in candidates:
        if path.is_file():
            with open(path, "rb") as f:
                raw = tomllib.load(f)
            cfg = _parse_immune_section(domain, raw)
            # If this file had no [immune] section, keep looking
            if cfg.claim_patterns or cfg.verification_tools or cfg.false_positive_patterns or cfg.ct_prompt_template or cfg.citation_format:
                return cfg

    # No TOML with immune content found — return empty config
    return DomainConfig(domain=domain)


def load_all_domain_configs() -> Dict[str, DomainConfig]:
    """Load all domain configs from the domains directory.

    Scans both the immune subdirectory and the main domains directory.
    Returns a dict mapping domain name to DomainConfig.
    Useful for preloading at pipeline start.
    """
    configs: Dict[str, DomainConfig] = {}
    # Collect domain names from both directories
    seen: set[str] = set()
    for directory in (_IMMUNE_DIR, _DOMAINS_DIR):
        if directory.is_dir():
            for path in sorted(directory.glob("*.toml")):
                domain = path.stem
                if domain not in seen:
                    seen.add(domain)
                    configs[domain] = load_domain_config(domain)
    return configs


# ---------------------------------------------------------------------------
# Stage 1 adapter: Dendritic Cell claim classification
# ---------------------------------------------------------------------------

def domain_classify_claim(
    finding: Finding,
    config: DomainConfig,
) -> Tuple[str, str]:
    """Classify a finding's claim type using domain-specific patterns.

    Returns (claim_type_value, extracted_assertion).

    If the domain config has no claim_patterns, returns ("uncategorised", desc)
    so the pipeline can fall through to its built-in patterns.

    Priority order matches the existing pipeline: statistical > logical >
    code_structural > mathematical > code_behavioral (default).
    """
    desc = finding.description
    compiled = config.compiled_claim_patterns()

    if not compiled:
        return "uncategorised", desc

    # Priority ordering — most specific first, broadest last.
    # This mirrors _classify_claim() in immune_agents.py.
    priority = [
        "statistical",
        "logical",
        "code_structural",
        "mathematical",
        "code_behavioral",
    ]

    for ctype in priority:
        patterns = compiled.get(ctype, [])
        for pat in patterns:
            if pat.search(desc):
                # For mathematical claims, try to extract backtick expressions
                if ctype == "mathematical":
                    eq_matches = re.findall(
                        r'`([^`]+[=<>+\-*/^][^`]+)`', desc,
                    )
                    if eq_matches:
                        extracted = ", ".join(eq_matches)
                        return ctype, extracted
                return ctype, desc

    return "uncategorised", desc


# ---------------------------------------------------------------------------
# Stage 2b adapter: B Cell tool selection
# ---------------------------------------------------------------------------

def domain_b_cell_tools(
    claim_type: str,
    config: DomainConfig,
) -> List[str]:
    """Return the ordered tool list for a claim type in this domain.

    First tool is primary. Remaining tools are class-switch fallbacks
    (tried in order if the primary returns UNCERTAIN).

    Returns empty list if no tools are configured — pipeline uses
    its built-in routing.
    """
    return config.verification_tools.get(claim_type, [])


# ---------------------------------------------------------------------------
# Stage 2a adapter: Cytotoxic T Cell prompt
# ---------------------------------------------------------------------------

def domain_ct_prompt_header(config: DomainConfig) -> str:
    """Return the domain-specific CT prompt header.

    This is prepended to the standard CT investigation prompt.
    Returns empty string if no domain-specific header is configured.
    """
    return config.ct_prompt_template


def domain_ct_citation_regex(config: DomainConfig) -> Optional["re.Pattern[str]"]:
    """Return the compiled citation regex for this domain, or None."""
    return config.compiled_citation_regex()


# ---------------------------------------------------------------------------
# Stage 3 adapter: NK Cell false-positive patterns
# ---------------------------------------------------------------------------

def domain_false_positives(config: DomainConfig) -> List[Dict[str, Any]]:
    """Return compiled false-positive patterns for the NK Cell.

    Format matches _KNOWN_FALSE_POSITIVES in immune_agents.py:
    list of dicts with "pattern" (compiled re), "source" (str),
    and optionally "expected_model" (str).

    Returns empty list if none configured — pipeline uses its
    built-in FP database.
    """
    return config.compiled_false_positives()


# ---------------------------------------------------------------------------
# Merge helper: combine domain FPs with built-in FPs
# ---------------------------------------------------------------------------

def merge_false_positives(
    builtin_fps: List[Dict[str, Any]],
    domain_config: DomainConfig,
) -> List[Dict[str, Any]]:
    """Merge built-in false-positive patterns with domain-specific ones.

    Domain patterns are checked first (higher priority), then built-in.
    No deduplication — patterns from different sources may overlap,
    and that is intentional (the first match wins in the NK Cell loop).
    """
    domain_fps = domain_false_positives(domain_config)
    return domain_fps + builtin_fps


# ---------------------------------------------------------------------------
# Convenience: full pipeline integration point
# ---------------------------------------------------------------------------

def get_immune_domain_context(domain: str) -> Dict[str, Any]:
    """One-call entry point: load domain config and return everything
    the immune pipeline needs in a single dict.

    Keys:
        config:           DomainConfig instance
        claim_patterns:   compiled claim patterns dict
        ct_header:        CT prompt header string
        citation_regex:   compiled citation regex or None
        false_positives:  compiled FP pattern list
        tool_map:         claim_type -> tool list
    """
    config = load_domain_config(domain)
    return {
        "config": config,
        "claim_patterns": config.compiled_claim_patterns(),
        "ct_header": domain_ct_prompt_header(config),
        "citation_regex": domain_ct_citation_regex(config),
        "false_positives": domain_false_positives(config),
        "tool_map": config.verification_tools,
    }
