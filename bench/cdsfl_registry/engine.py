"""CDSFL PolicyEngine — Unified facade for the hierarchical policy system.

Wraps the existing 4-layer registry (registry.py) and directive composer
(composer.py) with a single query interface, parameter introspection, and
schema validation.

The engine does not replace the registry or composer. It consolidates access
to their functionality and adds:

1. Parameter-level provenance: which layer set each parameter value.
2. Schema-driven validation: every parameter has a defined type, default,
   constraint class (HARD/SOFT), and minimum layer.
3. Unified query: one call for "give me the effective value of X for this
   domain/task/model, with its source layer".
4. Introspection: list all parameters, filter by section/type/class.

Usage::

    engine = PolicyEngine()
    engine.validate()  # check all configs

    # Get a single parameter with provenance
    val = engine.get_parameter("convergence.v_comp_threshold",
                               domain="mathematics", model="opus_4_6")
    print(val.value, val.source_layer, val.constraint_class)

    # Get full effective policy
    policy = engine.query(domain="code", model="deepseek_v3")
    print(policy.effective)  # merged dict
    print(policy.provenance)  # {dotpath: layer_name}

    # List all parameters
    for param in engine.list_parameters():
        print(param.dotpath, param.type, param.constraint_class)
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore[no-redef]

from .registry import (
    REGISTRY_DIR,
    HARD_CONSTRAINTS,
    HARD_THRESHOLDS,
    HARD_STRINGS,
    DOMAIN_MAP,
    PolicyViolationError,
    _load_toml,
    _deep_merge,
    _check_monotonicity,
    _dotpath_get,
    _MISSING,
    load_effective_policy,
    validate_all_policies,
)


# ---------------------------------------------------------------------------
# Schema types
# ---------------------------------------------------------------------------

SCHEMA_PATH = REGISTRY_DIR / "schema.toml"

# Valid parameter types in the schema
VALID_TYPES = {"bool", "int", "float", "string", "enum"}
VALID_CLASSES = {"HARD", "SOFT"}
VALID_LAYERS = {"universal", "domain", "task", "model"}
LAYER_ORDER = ["universal", "domain", "task", "model"]


@dataclass(frozen=True)
class ParameterDef:
    """Schema definition for a single policy parameter."""
    dotpath: str
    type: str               # "bool", "int", "float", "string", "enum"
    default: Any
    constraint_class: str   # "HARD" or "SOFT"
    min_layer: str          # lowest layer that may define it
    description: str
    allowed_values: Optional[List[str]] = None


@dataclass
class ParameterValue:
    """A resolved parameter value with provenance."""
    dotpath: str
    value: Any
    source_layer: str       # "universal", "domain/<name>", "task/<id>", "model/<name>"
    constraint_class: str
    type: str
    description: str


@dataclass
class PolicyResult:
    """Result of a full policy query."""
    domain: str
    task_id: Optional[str]
    model: Optional[str]
    effective: Dict[str, Any]           # merged policy dict
    provenance: Dict[str, str]          # dotpath -> source layer
    violations: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Schema loading
# ---------------------------------------------------------------------------

def _flatten_schema(raw: Dict[str, Any], prefix: str = "") -> Dict[str, Dict[str, Any]]:
    """Flatten the nested TOML schema into {dotpath: {type, default, ...}}."""
    result: Dict[str, Dict[str, Any]] = {}
    for key, value in raw.items():
        full_key = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict) and "type" in value:
            # This is a parameter definition
            result[full_key] = value
        elif isinstance(value, dict):
            # This is a section, recurse
            result.update(_flatten_schema(value, full_key))
    return result


def load_schema() -> Dict[str, ParameterDef]:
    """Load the parameter schema from schema.toml.

    Returns:
        Dict mapping dotpath to ParameterDef.

    Raises:
        FileNotFoundError: if schema.toml is missing.
        ValueError: if any parameter definition is malformed.
    """
    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(f"Schema not found: {SCHEMA_PATH}")

    raw = _load_toml(SCHEMA_PATH)
    flat = _flatten_schema(raw)

    schema: Dict[str, ParameterDef] = {}
    errors: List[str] = []

    for dotpath, defn in flat.items():
        ptype = defn.get("type", "")
        if ptype not in VALID_TYPES:
            errors.append(f"{dotpath}: invalid type '{ptype}'")
            continue

        pclass = defn.get("constraint_class", "")
        if pclass not in VALID_CLASSES:
            errors.append(f"{dotpath}: invalid constraint_class '{pclass}'")
            continue

        min_layer = defn.get("min_layer", "")
        if min_layer not in VALID_LAYERS:
            errors.append(f"{dotpath}: invalid min_layer '{min_layer}'")
            continue

        schema[dotpath] = ParameterDef(
            dotpath=dotpath,
            type=ptype,
            default=defn.get("default"),
            constraint_class=pclass,
            min_layer=min_layer,
            description=defn.get("description", ""),
            allowed_values=defn.get("allowed_values"),
        )

    if errors:
        raise ValueError(
            f"Schema validation errors:\n" + "\n".join(f"  {e}" for e in errors)
        )

    return schema


# ---------------------------------------------------------------------------
# Provenance tracking
# ---------------------------------------------------------------------------

def _flatten_dict(d: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
    """Flatten a nested dict to {dotpath: leaf_value}."""
    result: Dict[str, Any] = {}
    for key, value in d.items():
        full_key = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            result.update(_flatten_dict(value, full_key))
        else:
            result[full_key] = value
    return result


def _compute_provenance(
    domain: str,
    task_id: Optional[str],
    model: Optional[str],
) -> Dict[str, str]:
    """Trace which layer set each parameter in the effective policy.

    Builds the policy layer by layer and records when each dotpath
    first appears or changes value.
    """
    provenance: Dict[str, str] = {}

    # Layer 1: Universal
    universal_path = REGISTRY_DIR / "universal.toml"
    if not universal_path.exists():
        return provenance
    current = _load_toml(universal_path)
    for dp, val in _flatten_dict(current).items():
        provenance[dp] = "universal"

    # Layer 2: Domain
    domain_key = DOMAIN_MAP.get(domain)
    if domain_key:
        domain_path = REGISTRY_DIR / "domains" / f"{domain_key}.toml"
        if domain_path.exists():
            domain_config = _load_toml(domain_path)
            for dp, val in _flatten_dict(domain_config).items():
                provenance[dp] = f"domain/{domain_key}"
            current = _deep_merge(current, domain_config)

    # Layer 3: Task
    if task_id:
        task_path = REGISTRY_DIR / "tasks" / f"{task_id}.toml"
        if task_path.exists():
            task_config = _load_toml(task_path)
            for dp, val in _flatten_dict(task_config).items():
                provenance[dp] = f"task/{task_id}"
            current = _deep_merge(current, task_config)

    # Layer 4: Model
    if model:
        model_path = REGISTRY_DIR / "models" / f"{model}.toml"
        if model_path.exists():
            model_config = _load_toml(model_path)
            for dp, val in _flatten_dict(model_config).items():
                provenance[dp] = f"model/{model}"

    return provenance


# ---------------------------------------------------------------------------
# PolicyEngine
# ---------------------------------------------------------------------------

class PolicyEngine:
    """Unified facade for the CDSFL policy system.

    Instantiate once, query many times. The schema is loaded on construction.
    """

    def __init__(self) -> None:
        self._schema = load_schema()

    @property
    def schema(self) -> Dict[str, ParameterDef]:
        """All parameter definitions."""
        return dict(self._schema)

    def query(
        self,
        domain: str,
        task_id: Optional[str] = None,
        model: Optional[str] = None,
    ) -> PolicyResult:
        """Build the effective policy with full provenance tracking.

        Args:
            domain: Task domain (e.g. "mathematics", "code").
            task_id: Optional task identifier.
            model: Optional model config name.

        Returns:
            PolicyResult with effective policy and per-parameter provenance.
        """
        effective = load_effective_policy(domain, task_id, model)
        provenance = _compute_provenance(domain, task_id, model)

        return PolicyResult(
            domain=domain,
            task_id=task_id,
            model=model,
            effective=effective,
            provenance=provenance,
        )

    def get_parameter(
        self,
        dotpath: str,
        domain: str,
        task_id: Optional[str] = None,
        model: Optional[str] = None,
    ) -> ParameterValue:
        """Get a single parameter's effective value with provenance.

        Args:
            dotpath: Dot-separated parameter path (e.g. "convergence.v_comp_threshold").
            domain: Task domain.
            task_id: Optional task identifier.
            model: Optional model config name.

        Returns:
            ParameterValue with value, source layer, and schema metadata.

        Raises:
            KeyError: if dotpath is not in the schema.
        """
        if dotpath not in self._schema:
            raise KeyError(
                f"Unknown parameter: {dotpath}. "
                f"Known parameters: {sorted(self._schema.keys())[:10]}..."
            )

        defn = self._schema[dotpath]
        effective = load_effective_policy(domain, task_id, model)
        provenance = _compute_provenance(domain, task_id, model)

        value = _dotpath_get(effective, dotpath)
        if value is _MISSING:
            value = defn.default

        source = provenance.get(dotpath, "default")

        return ParameterValue(
            dotpath=dotpath,
            value=value,
            source_layer=source,
            constraint_class=defn.constraint_class,
            type=defn.type,
            description=defn.description,
        )

    def list_parameters(
        self,
        section: Optional[str] = None,
        constraint_class: Optional[str] = None,
    ) -> List[ParameterDef]:
        """List all parameter definitions, optionally filtered.

        Args:
            section: Filter to parameters starting with this section
                     (e.g. "constraints", "convergence").
            constraint_class: Filter to "HARD" or "SOFT".

        Returns:
            List of matching ParameterDef objects.
        """
        result = []
        for dp, defn in sorted(self._schema.items()):
            if section and not dp.startswith(section + "."):
                continue
            if constraint_class and defn.constraint_class != constraint_class:
                continue
            result.append(defn)
        return result

    def validate(self) -> Dict[str, str]:
        """Validate all config files against monotonicity rules.

        Delegates to validate_all_policies() and adds schema coverage check.

        Returns:
            Dict mapping config names to "ok" or error message.
        """
        results = validate_all_policies()

        # Additional check: verify schema covers all HARD constraints
        schema_hard_bools = {
            dp for dp, defn in self._schema.items()
            if defn.constraint_class == "HARD" and defn.type == "bool"
        }
        registry_hard_bools = set(HARD_CONSTRAINTS.keys())
        missing = registry_hard_bools - schema_hard_bools
        if missing:
            results["schema_coverage/hard_bools"] = (
                f"Schema missing HARD bool constraints: {sorted(missing)}"
            )

        schema_hard_thresholds = {
            dp for dp, defn in self._schema.items()
            if defn.constraint_class == "HARD" and defn.type in ("int", "float")
        }
        registry_hard_thresholds = set(HARD_THRESHOLDS.keys())
        missing_thresh = registry_hard_thresholds - schema_hard_thresholds
        if missing_thresh:
            results["schema_coverage/hard_thresholds"] = (
                f"Schema missing HARD threshold constraints: {sorted(missing_thresh)}"
            )

        schema_hard_strings = {
            dp for dp, defn in self._schema.items()
            if defn.constraint_class == "HARD" and defn.type == "string"
        }
        registry_hard_strings = set(HARD_STRINGS.keys())
        missing_str = registry_hard_strings - schema_hard_strings
        if missing_str:
            results["schema_coverage/hard_strings"] = (
                f"Schema missing HARD string constraints: {sorted(missing_str)}"
            )

        return results

    def get_schema_for(self, dotpath: str) -> Optional[ParameterDef]:
        """Get the schema definition for a single parameter.

        Returns None if the parameter is not in the schema.
        """
        return self._schema.get(dotpath)

    def diff_policies(
        self,
        domain_a: str,
        domain_b: str,
        model_a: Optional[str] = None,
        model_b: Optional[str] = None,
    ) -> Dict[str, tuple]:
        """Compare two effective policies and return differences.

        Returns:
            Dict of {dotpath: (value_a, value_b)} for parameters that differ.
        """
        policy_a = load_effective_policy(domain_a, model=model_a)
        policy_b = load_effective_policy(domain_b, model=model_b)

        flat_a = _flatten_dict(policy_a)
        flat_b = _flatten_dict(policy_b)

        all_keys = set(flat_a.keys()) | set(flat_b.keys())
        diffs: Dict[str, tuple] = {}
        for key in sorted(all_keys):
            va = flat_a.get(key, _MISSING)
            vb = flat_b.get(key, _MISSING)
            if va != vb:
                diffs[key] = (
                    va if va is not _MISSING else "<absent>",
                    vb if vb is not _MISSING else "<absent>",
                )
        return diffs

    def parameter_count(self) -> Dict[str, int]:
        """Count parameters by constraint class."""
        counts: Dict[str, int] = {"HARD": 0, "SOFT": 0}
        for defn in self._schema.values():
            counts[defn.constraint_class] = counts.get(defn.constraint_class, 0) + 1
        return counts
