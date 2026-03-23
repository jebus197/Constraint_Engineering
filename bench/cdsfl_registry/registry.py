"""
CDSFL Registry — Hierarchical Policy Merge Engine

Four-layer configuration hierarchy with monotonicity enforcement:

    Layer 1: universal.toml        — always enforced (HARD constraints live here)
    Layer 2: domains/<domain>.toml — domain-specific additions/overrides
    Layer 3: tasks/<task_id>.toml  — task-specific additions/overrides
    Layer 4: models/<model>.toml   — model-specific tuning

Merge rule: each layer deep-merges into the accumulated policy. If any layer
attempts to weaken a universal HARD constraint (set a boolean HARD to False,
or lower a threshold that is at its hard floor), a PolicyViolationError is
raised. This is monotonicity — lower layers can tighten but never loosen.

Usage:
    policy = load_effective_policy(
        domain="mathematics",
        task_id="ma-001",       # optional
        model="opus_4_6",       # optional
    )
"""

from __future__ import annotations

import copy
import json
import sys
import tomllib
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REGISTRY_DIR = Path(__file__).parent

# Universal HARD constraints — these are the boolean flags in [constraints]
# that no lower layer may set to False. Values here are their mandatory state.
HARD_CONSTRAINTS: dict[str, bool] = {
    "constraints.anti_deference": True,
    "constraints.falsification_required": True,
    "constraints.hard_soft_classification": True,
    "constraints.fail_closed_unassessed": True,
    "constraints.json_schema_required": True,
    "constraints.sympy_auto_verify": True,
    "convergence.hard_veto": True,
    "anti_deference.null_find_requires_scoped_justification": True,
    "anti_deference.agreement_requires_evidence": True,
    "protocol.blind_first": True,
}

# Universal HARD thresholds — these are numeric values that no lower layer
# may reduce below the universal floor.
HARD_THRESHOLDS: dict[str, float] = {
    "convergence.hard_coverage_threshold": 1.0,
    "anti_deference.min_independent_observations": 1,
    "verification.peer_support_min_families": 2,
}

# Universal HARD strings — exact match required, no override permitted.
HARD_STRINGS: dict[str, str] = {
    "convergence.method": "non_compensatory",
    "protocol.stop_rule": "counting_plus_verify",
}

# Domain aliases: map task-file domain strings to registry filenames.
DOMAIN_MAP: dict[str, str] = {
    "mathematics": "mathematics",
    "structural": "engineering",
    "hardware": "engineering",
    "industrial": "engineering",
    "product-engineering": "engineering",
    "engineering": "engineering",
    "software": "code",
    "code": "code",
    "cross-domain": "cross_domain",
    "cross_domain": "cross_domain",
    "physics": "physics",
    "chemistry": "physics",
    "biomedical": "physics",       # closest fit; can be split later
    "logistics": "cross_domain",   # multi-constraint; closest fit
}


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class PolicyViolationError(Exception):
    """Raised when a lower layer attempts to weaken a universal HARD constraint."""


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _load_toml(path: Path) -> dict[str, Any]:
    """Load a TOML file and return its contents as a dict."""
    with open(path, "rb") as f:
        return tomllib.load(f)


def _dotpath_get(d: dict[str, Any], dotpath: str) -> Any:
    """Retrieve a value from a nested dict using dot notation.

    Returns _MISSING sentinel if the path does not exist.
    """
    keys = dotpath.split(".")
    current = d
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return _MISSING
        current = current[key]
    return current


_MISSING = object()


def _deep_merge(base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    """Recursively merge overlay into base. Returns a new dict (no mutation)."""
    result = copy.deepcopy(base)
    for key, value in overlay.items():
        if (
            key in result
            and isinstance(result[key], dict)
            and isinstance(value, dict)
        ):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result


def _check_monotonicity(
    merged: dict[str, Any],
    layer_name: str,
) -> None:
    """Verify that no HARD constraint has been weakened after merge.

    Raises PolicyViolationError with a descriptive message if violated.
    """
    violations: list[str] = []

    # Check boolean HARDs
    for dotpath, required_value in HARD_CONSTRAINTS.items():
        actual = _dotpath_get(merged, dotpath)
        if actual is _MISSING:
            violations.append(
                f"  {dotpath}: missing (required {required_value})"
            )
        elif not isinstance(actual, bool) or actual != required_value:
            # Strict type check: anti_deference = 1 (int) is NOT the same as true (bool)
            violations.append(
                f"  {dotpath}: got {actual!r} (type {type(actual).__name__}), "
                f"required {required_value!r} (type {type(required_value).__name__})"
            )

    # Check threshold HARDs (lower layer cannot reduce below floor)
    for dotpath, floor in HARD_THRESHOLDS.items():
        actual = _dotpath_get(merged, dotpath)
        if actual is _MISSING:
            violations.append(
                f"  {dotpath}: missing (floor is {floor})"
            )
        elif not isinstance(actual, (int, float)):
            violations.append(
                f"  {dotpath}: got {actual!r} (type {type(actual).__name__}), "
                f"expected numeric (floor is {floor})"
            )
        elif actual != actual:  # NaN check: NaN != NaN is True
            violations.append(
                f"  {dotpath}: got NaN, floor is {floor}"
            )
        elif actual < floor:
            violations.append(
                f"  {dotpath}: got {actual}, floor is {floor}"
            )

    # Check string HARDs (exact match, no override)
    for dotpath, required_value in HARD_STRINGS.items():
        actual = _dotpath_get(merged, dotpath)
        if actual is _MISSING:
            violations.append(
                f"  {dotpath}: missing (required {required_value!r})"
            )
        elif actual != required_value:
            violations.append(
                f"  {dotpath}: got {actual!r}, required {required_value!r}"
            )

    if violations:
        detail = "\n".join(violations)
        raise PolicyViolationError(
            f"HARD constraint violation after merging layer '{layer_name}':\n{detail}"
        )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load_effective_policy(
    domain: str,
    task_id: str | None = None,
    model: str | None = None,
) -> dict[str, Any]:
    """Build the effective policy by merging all applicable layers.

    Args:
        domain: Task domain string (e.g. "mathematics", "software").
                Maps to the appropriate domain config via DOMAIN_MAP.
        task_id: Optional task identifier (e.g. "ma-001"). If a file
                 tasks/<task_id>.toml exists, it is merged as Layer 3.
        model:  Optional model config name without extension (e.g.
                "opus_4_6", "deepseek_v3"). Merged as Layer 4.

    Returns:
        The fully merged policy dict.

    Raises:
        PolicyViolationError: if any layer weakens a HARD constraint.
        FileNotFoundError: if universal.toml is missing.
    """
    # Layer 1: Universal (mandatory)
    universal_path = REGISTRY_DIR / "universal.toml"
    if not universal_path.exists():
        raise FileNotFoundError(f"Universal policy not found: {universal_path}")
    policy = _load_toml(universal_path)
    _check_monotonicity(policy, "universal")

    # Layer 2: Domain
    domain_key = DOMAIN_MAP.get(domain)
    if domain_key:
        domain_path = REGISTRY_DIR / "domains" / f"{domain_key}.toml"
        if domain_path.exists():
            domain_config = _load_toml(domain_path)
            policy = _deep_merge(policy, domain_config)
            _check_monotonicity(policy, f"domain/{domain_key}")
    else:
        import warnings
        warnings.warn(
            f"Unknown domain '{domain}' — no Layer 2 policy applied. "
            f"Known domains: {sorted(DOMAIN_MAP.keys())}",
            stacklevel=2,
        )

    # Layer 3: Task-specific
    if task_id:
        task_path = REGISTRY_DIR / "tasks" / f"{task_id}.toml"
        if task_path.exists():
            task_config = _load_toml(task_path)
            policy = _deep_merge(policy, task_config)
            _check_monotonicity(policy, f"task/{task_id}")

    # Layer 4: Model-specific
    if model:
        model_path = REGISTRY_DIR / "models" / f"{model}.toml"
        if model_path.exists():
            model_config = _load_toml(model_path)
            policy = _deep_merge(policy, model_config)
            _check_monotonicity(policy, f"model/{model}")
        else:
            available = [p.stem for p in (REGISTRY_DIR / "models").glob("*.toml")]
            raise FileNotFoundError(
                f"Model config not found: {model_path}\n"
                f"Available models: {available}"
            )

    return policy


def validate_all_policies() -> dict[str, str]:
    """Validate every possible single-layer merge against universal.

    Checks that each domain config and each model config, when merged with
    universal, does not violate monotonicity. Returns a dict mapping
    config names to "ok" or an error message.
    """
    results: dict[str, str] = {}

    # Load universal once
    universal_path = REGISTRY_DIR / "universal.toml"
    if not universal_path.exists():
        return {"universal": "MISSING — cannot validate anything"}
    universal = _load_toml(universal_path)

    try:
        _check_monotonicity(universal, "universal")
        results["universal"] = "ok"
    except PolicyViolationError as e:
        results["universal"] = str(e)
        return results  # If universal itself is broken, stop.

    # Validate each domain config
    domains_dir = REGISTRY_DIR / "domains"
    if domains_dir.exists():
        for toml_file in sorted(domains_dir.glob("*.toml")):
            name = f"domain/{toml_file.stem}"
            try:
                overlay = _load_toml(toml_file)
                merged = _deep_merge(universal, overlay)
                _check_monotonicity(merged, name)
                results[name] = "ok"
            except (PolicyViolationError, Exception) as e:
                results[name] = str(e)

    # Validate each model config
    models_dir = REGISTRY_DIR / "models"
    if models_dir.exists():
        for toml_file in sorted(models_dir.glob("*.toml")):
            name = f"model/{toml_file.stem}"
            try:
                overlay = _load_toml(toml_file)
                merged = _deep_merge(universal, overlay)
                _check_monotonicity(merged, name)
                results[name] = "ok"
            except (PolicyViolationError, Exception) as e:
                results[name] = str(e)

    # Validate each task config
    tasks_dir = REGISTRY_DIR / "tasks"
    if tasks_dir.exists():
        for toml_file in sorted(tasks_dir.glob("*.toml")):
            name = f"task/{toml_file.stem}"
            try:
                overlay = _load_toml(toml_file)
                merged = _deep_merge(universal, overlay)
                _check_monotonicity(merged, name)
                results[name] = "ok"
            except (PolicyViolationError, Exception) as e:
                results[name] = str(e)

    return results


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Validate all configs and print a sample effective policy."""
    print("=" * 70)
    print("CDSFL Registry — Policy Validation")
    print("=" * 70)

    results = validate_all_policies()
    all_ok = True
    for name, status in results.items():
        indicator = "PASS" if status == "ok" else "FAIL"
        if status != "ok":
            all_ok = False
        print(f"  [{indicator}] {name}")
        if status != "ok":
            for line in status.split("\n"):
                print(f"         {line}")

    print()
    if not all_ok:
        print("VALIDATION FAILED — fix the above before running experiments.")
        sys.exit(1)

    print("All configs valid.")
    print()

    # Sample: build effective policy for a maths task on Opus 4.6
    print("-" * 70)
    print("Sample effective policy: domain=mathematics, model=opus_4_6")
    print("-" * 70)
    policy = load_effective_policy(
        domain="mathematics",
        model="opus_4_6",
    )
    print(json.dumps(policy, indent=2, default=str))

    print()
    print("-" * 70)
    print("Sample effective policy: domain=software, model=deepseek_v3")
    print("-" * 70)
    policy = load_effective_policy(
        domain="software",
        model="deepseek_v3",
    )
    print(json.dumps(policy, indent=2, default=str))


if __name__ == "__main__":
    main()
