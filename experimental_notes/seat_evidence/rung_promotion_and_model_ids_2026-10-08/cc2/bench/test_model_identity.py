# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'rung_promotion_and_model_ids_2026-10-08', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 56e325bb0461a209de53953c82c979ab2196f8784aad4c238b9b28a89fbbe9ab
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""Falsifiers for bench/model_identity.py and for the model_id defect it fixes.

Run: python3 -m pytest bench/test_model_identity.py -q -s
"""
from __future__ import annotations

import collections
import re
from pathlib import Path

import pytest

from bench.model_identity import DISPATCH_DETERMINING, assign_uids, canonical, model_uid

ROOT = Path(__file__).resolve().parents[1]

BASE = {"provider": "openrouter", "model": "openai/gpt-5.5",
        "temperature": 0.0, "max_tokens": 8192, "system_prompt": "cdsfl core"}


def test_the_live_model_id_field_collides_and_cannot_key_a_record():
    """OBSERVED against bench/experiment_11_orchestrator.py."""
    src = (ROOT / "bench" / "experiment_11_orchestrator.py").read_text()
    lits = re.findall(r'model_id\s*[=:]\s*["\']([^"\']+)["\']', src)
    c = collections.Counter(lits)
    dupes = {k: v for k, v in c.items() if v > 1}
    versioned = [k for k in c if re.search(r'\d+\.\d+|v\d+', k)]
    print(f"\n  {len(lits)} literal model_id assignments, {len(c)} distinct; "
          f"colliding: {dupes}; version-bearing: {len(versioned)} of {len(lits)}")
    assert dupes, "model_id is already unique -> no identifier defect"
    assert set(dupes) == {"opus", "gpt-5.5"}
    assert len(lits) == 12 and len(c) == 10


def test_two_identical_configurations_are_not_split():
    a = dict(BASE)
    b = {k: BASE[k] for k in reversed(list(BASE))}        # different key order
    b["max_tokens"] = 8192.0                             # int/float representation
    assert canonical(a) == canonical(b)
    assert model_uid(a) == model_uid(b)
    groups = assign_uids([a, b])
    print(f"\n  one configuration listed twice -> {len(groups)} uid(s), "
          f"indices {list(groups.values())}")
    assert len(groups) == 1 and groups[model_uid(a)] == [0, 1]


def test_one_configuration_is_not_merged_with_a_different_one():
    """Every dispatch-determining field must move the identifier."""
    moved = {}
    for fld in DISPATCH_DETERMINING:
        cfg = dict(BASE)
        cfg[fld] = {"temperature": 0.7, "top_p": 0.5, "max_tokens": 4096,
                    "reasoning_effort": "high", "tools": ["execute_python"],
                    "provider": "anthropic", "model": "openai/gpt-5.6",
                    "system_prompt": "other"}[fld]
        moved[fld] = model_uid(cfg) != model_uid(BASE)
    print(f"\n  fields that move the uid: {moved}")
    assert all(moved.values()), f"merged on {[k for k,v in moved.items() if not v]}"
    # five instances of the same model that differ only in temperature stay five
    five = [dict(BASE, temperature=t) for t in (0.0, 0.2, 0.4, 0.6, 0.8)]
    assert len(assign_uids(five)) == 5


def test_presentation_fields_do_not_split_a_configuration():
    noisy = dict(BASE, display_name="Codex (fast)", cost_note="$3/Mtok",
                 comment="added 2026-10-08")
    assert model_uid(noisy) == model_uid(BASE)


def test_a_vendor_release_yields_a_new_identifier_at_zero_attempts():
    """Open question 2: the slug carries the version, so this is forced."""
    old = dict(BASE, model="openai/gpt-5.5")
    new = dict(BASE, model="openai/gpt-5.6")
    print(f"\n  {model_uid(old)} -> {model_uid(new)} (both records retained)")
    assert model_uid(old) != model_uid(new)
    # cost of the new identifier, taken from the DERIVED gate, not asserted here
    from bench.promotion_gate import derive_attempts_per_rung
    g = derive_attempts_per_rung(p_good=0.90, floor=0.50, beta=0.05, rungs=5)
    print(f"  cost of starting over: {g.attempts_to_climb} attempts "
          f"({g.attempts_per_rung}/rung x {g.rungs} rungs)")
    assert g.attempts_to_climb == 95


def test_the_identifier_carries_no_vendor_name():
    for cfg in (BASE, dict(BASE, model="anthropic/claude-opus-4.7")):
        uid = model_uid(cfg)
        assert re.fullmatch(r"m-[0-9a-f]{16}", uid)
        for vendor in ("openai", "gpt", "anthropic", "claude", "opus", "google"):
            assert vendor not in uid


def test_identifier_length_is_validated_rather_than_silently_truncated():
    with pytest.raises(ValueError):
        model_uid(BASE, length=4)


def test_the_briefs_model_id_diagnosis_names_the_WRONG_mechanism():
    """CORRECTION. The brief says `model_id` "collides". It SPLITS.

    The brief's count comes from matching the `model_id` SUFFIX, which also
    captures `secondary_model_id`. Separated by field:
      * `model_id=`           : 6 occurrences, 6 distinct -> no collision.
      * `secondary_model_id=` : 6 occurrences, 5 distinct, and the repeat
        ("gpt-5.5" at lines 188 and 200) is reached by the SAME api
        (`codex_exec`), so it is genuinely one model named once - correct
        behaviour, not a defect.
    The real defect is the opposite: ONE model carried under TWO strings -
    "openai/gpt-5.5" on `openrouter` (line 192) and "gpt-5.5" on `codex_exec`
    (188, 200). A capability record keyed on the string splits that model's
    evidence in two. Falsified if the primary field collides, or if no such
    split exists.
    """
    src = (ROOT / "bench" / "experiment_11_orchestrator.py").read_text()
    prim = re.findall(r'(?<!secondary_)model_id\s*=\s*["\']([^"\']+)["\']', src)
    sec = re.findall(r'secondary_model_id\s*=\s*["\']([^"\']+)["\']', src)
    print(f"\n  primary model_id: {len(prim)} occurrences, "
          f"{len(set(prim))} distinct -> {sorted(set(prim))}")
    print(f"  secondary_model_id: {len(sec)} occurrences, {len(set(sec))} distinct")
    assert len(prim) == len(set(prim)) == 6, "the primary field does collide"
    assert len(sec) == 6 and len(set(sec)) == 5
    # the split: one model, two strings
    bare = {s.split("/")[-1] for s in prim} & {s.split("/")[-1] for s in sec}
    assert "gpt-5.5" in bare
    assert "openai/gpt-5.5" in prim and "gpt-5.5" in sec
    print(f"  SPLIT: one model under 2 strings {sorted(bare)} -> "
          f"evidence divided across 2 records")
    # and the uid fixes it, because provider+slug are hashed together
    a = {"provider": "openrouter", "model": "openai/gpt-5.5", "temperature": 0.0}
    b = {"provider": "openrouter", "model": "openai/gpt-5.5", "temperature": 0.0}
    c = {"provider": "codex_exec", "model": "openai/gpt-5.5", "temperature": 0.0}
    assert model_uid(a) == model_uid(b)      # one config, one record
    assert model_uid(a) != model_uid(c)      # different route, different record
