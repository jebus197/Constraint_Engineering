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


# Reviving the orphan: this module was imported by nothing before 2026-11-10.


def _resolve_domain_alias(domain: str) -> str:
    """Map a run's domain name onto the one the TOMLs declare.

    IMPORTED FROM THE LIVE PATH, NEVER COPIED.
    `immune_agents._DOMAIN_ALIAS` is the 1 map the immune pipeline
    uses; a second spelling here would be 2 tables that can drift,
    which is the defect this exists to close. An import failure
    leaves the domain unchanged, so the worst case is today's
    behaviour rather than an exception on a telemetry path.
    """
    try:
        import immune_agents as _ia
        return str(_ia._DOMAIN_ALIAS.get(domain, domain) or domain)
    except Exception:                                 # noqa: BLE001
        return domain


#: ★ TOOLS WHOSE CONFIRMED VERDICT CARRIES 0 BITS ABOUT THE CLAIM.
#: A verdict that takes the SAME value on a claim and on a false variant of
#: it is an admission by vocabulary, not by tool. Each member is measured,
#: with a committed producer:
#: `scripts/which_admissions_are_truth_blind_2026-11-10.py`.
#:   dimensional_analysis -- CONFIRMS `1 km = 1000 m` AND `1 km = 2000 m`;
#:       it tests dimensional homogeneity and reports it as correctness (B136)
#:   astronomical         -- NOT truth-blind, and the first version of this
#:       comment said it was. It is a TOLERANT COMPARATOR: it CONFIRMS
#:       `the speed of light is 299792458 m/s` and also
#:       `the speed of light is 299792459 m/s`, which is FALSE by 1 m/s but
#:       inside its own 1% tolerance, while REJECTING 3000000 m/s. So it
#:       discriminates coarsely and can still SOLELY ADMIT a false
#:       exact-value claim, which is why it may not admit alone. The earlier
#:       "truth-blind" reading came from a probe pair whose BOTH members were
#:       in km/s, where its separate unit defect (B136) rejects everything --
#:       the probe pair shared the feature that caused the result.
#: ★ `chemistry_structure` WAS IN THIS SET AND HAS BEEN MOVED TO THE BRANCH
#: GATE BELOW, 2026-11-10, ON A FREE PANEL SEAT'S FINDING THAT REPRODUCED.
#: Putting it here destroyed a LIVE, REACHABLE, DISCRIMINATING admission:
#: `the molecule 'CCO' has formula C2H6O` routes to chemistry/mathematical,
#: the tool is dispatched, its formula branch CONFIRMS with `matches claim`
#: and REJECTS the C3H8O variant -- and the tool-level bar refused the
#: admission anyway. That is `additive-standard`'s removal clause broken by
#: the very repair that cited it, and the measurement said it dominated only
#: because the probe set enumerated 1 of the tool's 3 favourable branches.
#: IT IS THE SAME 1-BRANCH-OF-N ERROR THIS FILE ALREADY RECORDS AGAINST A
#: PANEL SEAT'S READING OF `biological_sequence`, COMMITTED IMMEDIATELY
#: AFTER REFUSING IT. The 2 verifiers are anatomically identical: comparing
#: branches that print `matches claim`, plus 1 validity-only fallback that
#: cannot. They are now treated identically.
#: ★ MEMBERSHIP IS NOT PERMANENT AND MUST NOT OUTLIVE ITS EVIDENCE: the
#: producer's probe for a member FAILS if that tool learns to discriminate,
#: and the entry must then be removed.
#: ★ 2 ROUTES WERE MEASURED AND THE WIDER ONE WAS REFUSED. A free panel seat
#: proposed excluding `biological_sequence` at the TOOL level. Measured on 2
#: named properties -- truth-blind paths barred, and discriminating paths
#: retained -- the tool-level set scores 2 of 3 and 1 of 2, while gating that
#: tool at the BRANCH scores 3 of 3 and 2 of 2. The tool-level exclusion
#: removes a capability that demonstrably works, so under the additive
#: standard's removal clause it is refused. There is NO composability claim:
#: the branch gate alone beats the exclusion alone, and his definition
#: explicitly excludes composing 2 fixes merely because they can be composed.
CANNOT_ADMIT_ALONE = frozenset({
    "dimensional_analysis",
    "astronomical",
})

#: tool -> the substring its evidence must carry for a CONFIRMED verdict of
#: its to admit alone. BOTH members have the same anatomy, established by
#: bounding each verifier's body with the syntax tree rather than by a
#: character window, because a window scan leaked across the function
#: boundary and attributed one verifier's branches to its neighbour:
#:   biological_sequence -- 5 favourable branches, 4 COMPARING
#:       (translation, reverse complement, length, GC content), 1 validity-only
#:   chemistry_structure -- 3 favourable branches, 2 COMPARING
#:       (molecular formula, molecular weight), 1 validity-only
#: A COMPARING branch is one that computes a value and checks it against what
#: the claim states, so its verdict can come out either way; each prints
#: `matches claim` on its favourable arm and a MISMATCH line otherwise.
#: The marker is read off those verifiers' own sources and is TOOL-SCOPED --
#: applying it globally barred `stoichiometric_balance`, which discriminates
#: with no marker at all, having no truth-blind branch to be told apart from.
#: ★ A TOOL NEEDS BRANCH GATING ONLY IF IT HAS BOTH KINDS OF FAVOURABLE
#: BRANCH. `dimensional_analysis` has 0 comparing branches, so a tool-level
#: bar there removes nothing; `stoichiometric_balance` has 0 truth-blind
#: ones, so it needs no gate. That is the rule the 2 tables encode.
BRANCH_GATED_ADMISSION = {
    "biological_sequence": "matches claim",
    "chemistry_structure": "matches claim",
}


def _may_admit_alone(name: str, evidence: str) -> bool:
    """Whether a favourable verdict from `name` may admit a fix by itself."""
    if name in CANNOT_ADMIT_ALONE:
        return False
    need = BRANCH_GATED_ADMISSION.get(name)
    if need is not None:
        return need in (evidence or "")
    return True


def domain_verification_set(domain: str, finding: Any) -> Dict[str, Any]:
    """The verification set a STEM topic assigns to one finding, and its verdicts.

    HIS RULING, 2026-11-10, verbatim: the suite "will come from which ever STEM
    topic area under discussion and the tools/falsifiers/B-Cell machinery
    attached to that STEM topic", because a researcher submitting a STEM paper
    "will almost certainly have ... included both prose and calulations/formulas
    they wish to be considered", so the models' job is to "use the
    tools/falsifiers assigned to that subject area to calculate those elements
    of any given paper that are computationally available/reducible to them."

    THE OPERATIVE WORDS ARE "AVAILABLE/REDUCIBLE TO THEM". Most prose sentences
    reduce to nothing a symbolic tool can evaluate, and the verifiers correctly
    return UNCERTAIN on them -- measured 2026-11-10 on 3 sentences drawn from
    this project's own notes, where 4 of 4 resolved tool calls returned
    UNCERTAIN at confidence 0.2 to 0.3. So this function can only ever ADD a
    route to admission for content the domain's tools genuinely reduce. It must
    never loosen a refusal, and `admits` is False unless a tool returns a
    definitive verdict in favour with none against.

    Returns a dict rather than a dataclass so a caller can record the whole
    decision in a ledger line without a second schema to keep in step:
        domain, claim_type, tools, verdicts, admits, detail

    `tools` is the ORDERED list the domain assigns, so the record shows what was
    asked as well as what answered -- an empty list is a real answer (the domain
    assigns nothing to this claim type) and is reported as such rather than as a
    silent refusal.
    """
    #: THE SAME ALIAS THE LIVE IMMUNE PATH APPLIES, IMPORTED RATHER
    #: THAN RESTATED. Without it this function is inert on the
    #: canonical runner's DEFAULT domain, `software`, which is not 1
    #: of the 10 declared immune domains and resolves only through
    #: `immune_agents._DOMAIN_ALIAS`.
    domain = _resolve_domain_alias(domain)
    out: Dict[str, Any] = {
        "domain": domain,
        "claim_type": "unknown",
        "tools": [],
        "verdicts": [],
        "admits": False,
        "detail": "",
    }
    try:
        config = load_domain_config(domain)
    except Exception as exc:                                  # noqa: BLE001
        out["detail"] = f"domain-config-failed:{type(exc).__name__}"
        return out

    try:
        claim_type, _why = domain_classify_claim(finding, config)
    except Exception as exc:                                  # noqa: BLE001
        out["detail"] = f"classify-failed:{type(exc).__name__}"
        return out
    out["claim_type"] = claim_type

    tools = domain_b_cell_tools(claim_type, config)
    out["tools"] = list(tools)
    if not tools:
        out["detail"] = (f"{domain} assigns no verification tool to a "
                         f"{claim_type} claim")
        return out

    # Resolve and CALL. The verifiers take a plain claim string and return a
    # CellVerdict, established by execution 2026-11-10 -- so no TriagedFinding
    # is needed and the impedance mismatch reported against this wiring does
    # not hold for the primary walk.
    claim = getattr(finding, "description", "") or ""
    try:
        import immune_agents as _ia
        manifest = _ia._load_tool_manifest()
    except Exception as exc:                                  # noqa: BLE001
        out["detail"] = f"manifest-failed:{type(exc).__name__}"
        return out

    definitive_for: List[str] = []
    definitive_against: List[str] = []
    #: Tools whose CONFIRMED verdict may never admit a fix BY ITSELF, and
    #: the 1 tool gated at the BRANCH rather than at the tool. Both are
    #: measured, not chosen -- see `CANNOT_ADMIT_ALONE` at module level.
    computing_for: List[str] = []
    for name in tools:
        entry = manifest.get(name)
        if not entry:
            out["verdicts"].append((name, "NOT_IN_MANIFEST", None))
            continue
        if entry.get("needs_file"):
            # A file tool aimed at prose is bypassed, not run -- the A6 rule.
            out["verdicts"].append((name, "NOT_APPLICABLE", None))
            continue
        fn = entry.get("verifier")
        f = fn if callable(fn) else getattr(_ia, str(fn), None)
        if not callable(f):
            out["verdicts"].append((name, "UNRESOLVED", None))
            continue
        try:
            v = f(claim)
        except Exception as exc:                              # noqa: BLE001
            out["verdicts"].append((name, f"RAISED_{type(exc).__name__}", None))
            continue
        verdict = getattr(v, "verdict", None)
        conf = getattr(v, "confidence", None)
        out["verdicts"].append((name, verdict, conf))
        if verdict in ("CONFIRMED", "VERIFIED", "SUPPORTED"):
            definitive_for.append(name)
            if _may_admit_alone(name, getattr(v, "evidence", "")):
                computing_for.append(name)
        elif verdict in ("REFUTED", "REJECTED", "CONTRADICTED"):
            definitive_against.append(name)

    #: ★ AN ADMISSION NEEDS A VERDICT THAT COULD HAVE COME OUT THE OTHER WAY.
    #: `definitive_for` still carries every favourable verdict, so nothing is
    #: discarded and a corroborating voice is still recorded; only the
    #: ADMISSION is narrowed to the verdicts measured to discriminate.
    out["admits"] = bool(computing_for) and not definitive_against
    _mute = [n for n in definitive_for if n not in computing_for]
    out["detail"] = (
        f"{domain}/{claim_type} tools={','.join(tools)} "
        f"for={','.join(computing_for) or '-'} "
        f"for_but_cannot_admit={','.join(_mute) or '-'} "
        f"against={','.join(definitive_against) or '-'}")
    return out
