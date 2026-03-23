"""
CDSFL Registry — CX Refinements: Independence, Canonicalisation, Novelty Channel

Three features identified by CX as needed for the refined convergence protocol:

1. **Independence-Aware Confirmation**: Peer support requires findings from
   distinct model *families*, not just different model names. Two Anthropic
   models agreeing is corroboration within a family, not independent
   confirmation. Minimum 2 independent families for peer_verified status.

2. **Tuple Canonicalisation**: Structural findings are canonicalised as
   4-tuples (artifact, assumption, violation_mode, witness) before hashing.
   This prevents false negatives (same finding, different wording) and false
   positives (different findings, similar wording). SHA-256 of the canonical
   tuple replaces raw claim hashing for structural dedup.

3. **Validated-Novelty Channel**: Singleton findings (one model, no peer
   confirmation) are NOT penalised. They enter a novelty channel with status
   "unconfirmed_novel". If a later round or SymPy check confirms them, they
   are retroactively promoted to verified. This preserves the value of unique
   observations without inflating v_struct.
"""

from __future__ import annotations

import hashlib
from typing import Any


# ---------------------------------------------------------------------------
# 1. Independence-Aware Confirmation
# ---------------------------------------------------------------------------

MODEL_FAMILIES: dict[str, list[str]] = {
    "anthropic": ["opus_4_6"],
    "openai": ["codex_5_3", "chatgpt_5_4"],
    "google": ["gemini_3_1_pro"],
    "deepseek": ["deepseek_v3"],
}

# Inverted index: model name -> family name (built once at import time).
_MODEL_TO_FAMILY: dict[str, str] = {}
for _family, _models in MODEL_FAMILIES.items():
    for _model in _models:
        _MODEL_TO_FAMILY[_model] = _family


def get_family(model: str) -> str | None:
    """Return the family name for a model, or None if unrecognised.

    Args:
        model: Model identifier (e.g. "opus_4_6", "deepseek_v3").

    Returns:
        Family name string, or None if the model is not in MODEL_FAMILIES.
    """
    return _MODEL_TO_FAMILY.get(model)


def is_independent_confirmation(finding_a_model: str, finding_b_model: str) -> bool:
    """Check whether two models provide independent confirmation.

    Independent confirmation requires the models to belong to distinct
    families. Two models from the same family (e.g. codex_5_3 and
    chatgpt_5_4, both OpenAI) do NOT constitute independent confirmation.

    Args:
        finding_a_model: Model that produced finding A.
        finding_b_model: Model that produced finding B.

    Returns:
        True if the two models are from different families. False if they
        share a family or if either model is unrecognised.
    """
    family_a = get_family(finding_a_model)
    family_b = get_family(finding_b_model)
    if family_a is None or family_b is None:
        return False
    return family_a != family_b


def count_independent_confirmations(
    finding: dict[str, Any],
    all_findings_by_model: dict[str, list[dict[str, Any]]],
) -> int:
    """Count how many distinct families found the same structural finding.

    Matches findings by their canonical hash (see structural_canon_hash).
    The source model's own family is included in the count, so a finding
    confirmed by 3 independent families returns 3.

    Args:
        finding: The finding dict to check. Must contain the 4 canonical
                 fields (artifact, assumption, violation_mode, witness)
                 plus a "model" key identifying who produced it.
        all_findings_by_model: Dict mapping model name to list of finding
                               dicts from that model.

    Returns:
        Number of distinct families that produced a matching finding.
    """
    target_hash = structural_canon_hash(finding)
    confirming_families: set[str] = set()

    for model, findings in all_findings_by_model.items():
        family = get_family(model)
        if family is None:
            continue
        for f in findings:
            if structural_canon_hash(f) == target_hash:
                confirming_families.add(family)
                break  # One match per model is sufficient.

    return len(confirming_families)


# ---------------------------------------------------------------------------
# 2. Tuple Canonicalisation
# ---------------------------------------------------------------------------

_CANONICAL_FIELDS = ("artifact", "assumption", "violation_mode", "witness")


def canonicalise_structural_finding(finding_dict: dict[str, Any]) -> tuple[str, ...]:
    """Canonicalise a structural finding as a normalised 4-tuple.

    Extracts (artifact, assumption, violation_mode, witness) from the
    finding dict, then normalises each field: lowercase, strip whitespace,
    sort space-separated terms alphabetically within each field.

    This ensures that "bridge deck" and "deck bridge" produce the same
    canonical form, preventing false negatives from word-order variation.

    Args:
        finding_dict: Dict containing at minimum the 4 canonical field
                      keys. Missing fields are treated as empty strings.

    Returns:
        A 4-tuple of normalised strings.
    """
    parts: list[str] = []
    for field in _CANONICAL_FIELDS:
        raw = str(finding_dict.get(field, "")).strip().lower()
        # Sort space-separated terms alphabetically within the field.
        terms = sorted(raw.split())
        parts.append(" ".join(terms))
    return tuple(parts)


def structural_canon_hash(finding_dict: dict[str, Any]) -> str:
    """Produce a SHA-256 hash of the canonical tuple for a structural finding.

    This replaces raw claim hashing for structural dedup. Two findings that
    describe the same (artifact, assumption, violation_mode, witness) in
    different words will collide to the same hash after canonicalisation.

    Args:
        finding_dict: Dict containing the 4 canonical fields.

    Returns:
        Hex-encoded SHA-256 digest string.
    """
    canon = canonicalise_structural_finding(finding_dict)
    payload = "|".join(canon).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


# ---------------------------------------------------------------------------
# 3. Validated-Novelty Channel
# ---------------------------------------------------------------------------

# Status constants.
STATUS_SYMPY_VERIFIED = "sympy_verified"
STATUS_PEER_VERIFIED = "peer_verified"
STATUS_UNCONFIRMED_NOVEL = "unconfirmed_novel"
STATUS_REFUTED = "refuted"

_MIN_INDEPENDENT_FAMILIES = 2


def classify_finding_support(
    finding: dict[str, Any],
    all_findings_by_model: dict[str, list[dict[str, Any]]],
    model_families: dict[str, list[str]] | None = None,
) -> str:
    """Classify a finding's support level.

    Decision logic (in priority order):
      1. If finding["sympy_verified"] is True -> "sympy_verified"
      2. If finding["refuted"] is True -> "refuted"
      3. If independent family count >= min_independent_families -> "peer_verified"
      4. Otherwise -> "unconfirmed_novel"

    Unconfirmed findings do NOT count toward v_struct (no penalty) but also
    do not count as verified. They sit in the novelty channel awaiting
    confirmation from a later round, a different model family, or SymPy.

    Args:
        finding: The finding dict. Expected keys: the 4 canonical fields,
                 "model", and optionally "sympy_verified" and "refuted".
        all_findings_by_model: Dict mapping model name to list of finding
                               dicts.
        model_families: Optional override for MODEL_FAMILIES. If None, the
                        module-level MODEL_FAMILIES is used (the parameter
                        exists for testing).

    Returns:
        One of: "sympy_verified", "peer_verified", "unconfirmed_novel",
        "refuted".
    """
    # Update the inverted index if custom families were provided.
    if model_families is not None:
        _update_family_index(model_families)

    # Priority 1: SymPy verification is strongest.
    if finding.get("sympy_verified", False):
        return STATUS_SYMPY_VERIFIED

    # Priority 2: Explicit refutation.
    if finding.get("refuted", False):
        return STATUS_REFUTED

    # Priority 3: Peer confirmation across independent families.
    family_count = count_independent_confirmations(finding, all_findings_by_model)
    if family_count >= _MIN_INDEPENDENT_FAMILIES:
        return STATUS_PEER_VERIFIED

    # Default: novelty channel.
    return STATUS_UNCONFIRMED_NOVEL


def retroactive_promotion(finding: dict[str, Any], new_evidence: dict[str, Any]) -> str:
    """Check if new evidence promotes a previously unconfirmed finding.

    Called when a later round produces new evidence (a matching finding from
    a different family, or a SymPy verification result). Returns the new
    status the finding should be promoted to.

    Args:
        finding: The original finding dict (status "unconfirmed_novel").
        new_evidence: A dict with at least one of:
            - "sympy_verified": bool — if True, promotes to "sympy_verified".
            - "confirming_families": int — total independent family count
              including the new evidence. If >= min_independent_families,
              promotes to "peer_verified".
            - "refuted": bool — if True, demotes to "refuted".

    Returns:
        The new status string. Returns "unconfirmed_novel" if the evidence
        is insufficient for promotion.
    """
    if new_evidence.get("sympy_verified", False):
        return STATUS_SYMPY_VERIFIED

    if new_evidence.get("refuted", False):
        return STATUS_REFUTED

    confirming = new_evidence.get("confirming_families", 0)
    if confirming >= _MIN_INDEPENDENT_FAMILIES:
        return STATUS_PEER_VERIFIED

    return STATUS_UNCONFIRMED_NOVEL


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _update_family_index(families: dict[str, list[str]]) -> None:
    """Rebuild the inverted model-to-family index from a custom families dict."""
    global _MODEL_TO_FAMILY
    _MODEL_TO_FAMILY = {}
    for family, models in families.items():
        for model in models:
            _MODEL_TO_FAMILY[model] = family


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

def _self_test() -> None:
    """Run a self-test with sample data to verify all three features."""
    import sys

    passed = 0
    failed = 0

    def check(description: str, condition: bool) -> None:
        nonlocal passed, failed
        if condition:
            passed += 1
            print(f"  [PASS] {description}")
        else:
            failed += 1
            print(f"  [FAIL] {description}")

    print("=" * 70)
    print("CDSFL Refinements — Self-Test")
    print("=" * 70)

    # --- 1. Independence-Aware Confirmation ---
    print("\n1. Independence-Aware Confirmation")
    print("-" * 40)

    check(
        "opus_4_6 vs deepseek_v3 = independent",
        is_independent_confirmation("opus_4_6", "deepseek_v3") is True,
    )
    check(
        "codex_5_3 vs chatgpt_5_4 = NOT independent (same family: openai)",
        is_independent_confirmation("codex_5_3", "chatgpt_5_4") is False,
    )
    check(
        "opus_4_6 vs unknown_model = NOT independent (unknown)",
        is_independent_confirmation("opus_4_6", "unknown_model") is False,
    )
    check(
        "get_family('opus_4_6') == 'anthropic'",
        get_family("opus_4_6") == "anthropic",
    )
    check(
        "get_family('nonexistent') is None",
        get_family("nonexistent") is None,
    )

    # --- 2. Tuple Canonicalisation ---
    print("\n2. Tuple Canonicalisation")
    print("-" * 40)

    finding_a = {
        "artifact": "Bridge Deck",
        "assumption": "Load bearing capacity",
        "violation_mode": "Fatigue cracking",
        "witness": "Section 4.2",
        "model": "opus_4_6",
    }
    finding_b = {
        "artifact": "  deck bridge  ",
        "assumption": "capacity bearing load",
        "violation_mode": "cracking fatigue",
        "witness": "4.2 section",
        "model": "deepseek_v3",
    }
    finding_c = {
        "artifact": "Bridge Deck",
        "assumption": "Load bearing capacity",
        "violation_mode": "Corrosion",
        "witness": "Section 4.2",
        "model": "gemini_3_1_pro",
    }

    canon_a = canonicalise_structural_finding(finding_a)
    canon_b = canonicalise_structural_finding(finding_b)
    canon_c = canonicalise_structural_finding(finding_c)

    check(
        "Same finding, different wording -> same canonical tuple",
        canon_a == canon_b,
    )
    check(
        "Different finding -> different canonical tuple",
        canon_a != canon_c,
    )
    check(
        "Same finding -> same SHA-256 hash",
        structural_canon_hash(finding_a) == structural_canon_hash(finding_b),
    )
    check(
        "Different finding -> different SHA-256 hash",
        structural_canon_hash(finding_a) != structural_canon_hash(finding_c),
    )
    check(
        "Missing fields treated as empty string",
        canonicalise_structural_finding({}) == ("", "", "", ""),
    )

    # --- 3. Count independent confirmations ---
    print("\n3. Independent Confirmation Counting")
    print("-" * 40)

    all_findings = {
        "opus_4_6": [finding_a],
        "deepseek_v3": [finding_b],      # Same finding, different family.
        "codex_5_3": [finding_a.copy()],  # Same finding, openai family.
        "gemini_3_1_pro": [finding_c],    # Different finding, google family.
    }

    count = count_independent_confirmations(finding_a, all_findings)
    check(
        f"finding_a confirmed by 3 independent families (anthropic, deepseek, openai), got {count}",
        count == 3,
    )

    # finding_c only found by google.
    count_c = count_independent_confirmations(finding_c, all_findings)
    check(
        f"finding_c confirmed by 1 family (google only), got {count_c}",
        count_c == 1,
    )

    # --- 4. Validated-Novelty Channel ---
    print("\n4. Validated-Novelty Channel")
    print("-" * 40)

    # SymPy verified takes priority.
    sympy_finding = {**finding_a, "sympy_verified": True}
    check(
        "sympy_verified finding -> 'sympy_verified'",
        classify_finding_support(sympy_finding, all_findings) == STATUS_SYMPY_VERIFIED,
    )

    # Refuted finding.
    refuted_finding = {**finding_a, "refuted": True}
    check(
        "refuted finding -> 'refuted'",
        classify_finding_support(refuted_finding, all_findings) == STATUS_REFUTED,
    )

    # Peer-verified (3 families >= 2 minimum).
    check(
        "finding_a with 3 families -> 'peer_verified'",
        classify_finding_support(finding_a, all_findings) == STATUS_PEER_VERIFIED,
    )

    # Singleton finding (only one family).
    singleton_findings = {
        "gemini_3_1_pro": [finding_c],
    }
    check(
        "finding_c with 1 family -> 'unconfirmed_novel'",
        classify_finding_support(finding_c, singleton_findings) == STATUS_UNCONFIRMED_NOVEL,
    )

    # --- 5. Retroactive Promotion ---
    print("\n5. Retroactive Promotion")
    print("-" * 40)

    check(
        "SymPy confirmation -> promotes to 'sympy_verified'",
        retroactive_promotion(finding_c, {"sympy_verified": True}) == STATUS_SYMPY_VERIFIED,
    )
    check(
        "New family brings total to 2 -> promotes to 'peer_verified'",
        retroactive_promotion(finding_c, {"confirming_families": 2}) == STATUS_PEER_VERIFIED,
    )
    check(
        "Insufficient evidence -> stays 'unconfirmed_novel'",
        retroactive_promotion(finding_c, {"confirming_families": 1}) == STATUS_UNCONFIRMED_NOVEL,
    )
    check(
        "Refutation evidence -> demotes to 'refuted'",
        retroactive_promotion(finding_c, {"refuted": True}) == STATUS_REFUTED,
    )

    # --- Summary ---
    print()
    print("=" * 70)
    total = passed + failed
    print(f"Results: {passed}/{total} passed, {failed} failed.")
    if failed:
        print("SELF-TEST FAILED.")
        sys.exit(1)
    else:
        print("All self-tests passed.")
    print("=" * 70)


if __name__ == "__main__":
    _self_test()
