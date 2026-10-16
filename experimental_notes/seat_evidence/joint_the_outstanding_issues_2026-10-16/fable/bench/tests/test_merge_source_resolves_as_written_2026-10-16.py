# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'joint_the_outstanding_issues_2026-10-16', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: bd47442af50acb6dbdfce399cdd89cc25e169ebff82d6ba59f8639a04c137993
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""A merge source names its owner; the resolver must not strip the owner away.

THE DEFECT, EXECUTED 2026-10-16 (joint panel round). `_resolve_merge_source`
reduces its evidence to the first `[FC]\\d+` match, discarding everything to the
left -- including the one token that names the OWNER. In a registry where every
seat holds its own F004, a cross-seat merge source written as `Gemini-SIM_F004`
by `CC2-SIM` resolved to CC2-SIM's OWN F004: the writer's distinct finding was
merged away and the finding actually named got no verdict. 30 of 48 cross-seat
forms mis-attributed (62.5000%, Wilson [48.4039%, 74.7631%]). The form is real:
the v3.1 run's duplicate records cite foreign composed ids verbatim
(`Fable-SIM_F003`, `DeepSeek-SIM_F002`, ...).

THE FIX resolves the id AS WRITTEN (left-expansion from the same regex match,
`lookup_alias_any`) before the stripped candidates run. Ambiguity is refused,
not guessed, and a miss falls through to the prior behaviour unchanged.

`execute-do-not-grep`: every test CALLS the resolver against a live registry.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from bench.reference_runner_v3 import (  # noqa: E402
    Finding, FindingRegistry, _resolve_finding_key, _resolve_merge_source,
)
from bench.runner_core import _compose_finding_id  # noqa: E402


def _finding(fid: str, model: str) -> Finding:
    return Finding(finding_id=fid, model_id=model, round_idx=0, flaw_class=1,
                   severity=0.8, abstraction_index=0.5, description="d" * 40)


def _registry_where_every_seat_holds_f004():
    reg = FindingRegistry()
    canon = {}
    for seat, raw in [("CC2-SIM", "CC2_F004"), ("Gemini-SIM", "GEMINI_F004"),
                      ("Codex-SIM", "CODEX_F004"), ("Fable-SIM", "FABLE_F004")]:
        composed = _compose_finding_id(raw, seat)   # the parser's own path
        canon[seat] = reg.register(_finding(composed, seat), seat)
    return reg, canon


# ───────────────────────── _resolve_merge_source ─────────────────────────────

def test_a_cross_seat_composed_source_resolves_to_its_owner_not_the_writer():
    reg, canon = _registry_where_every_seat_holds_f004()
    got = _resolve_merge_source("duplicate of Gemini-SIM_F004", "CC2-SIM", reg)
    assert got == canon["Gemini-SIM"], (
        f"MERGE source `Gemini-SIM_F004` written by CC2-SIM resolved to {got}; "
        f"it names Gemini-SIM's finding {canon['Gemini-SIM']}, and resolving it "
        f"onto the writer's own {canon['CC2-SIM']} merges away a distinct "
        f"finding while the named one gets no verdict"
    )


def test_every_cross_seat_composed_form_resolves_to_its_owner():
    reg, canon = _registry_where_every_seat_holds_f004()
    seats = list(canon)
    for writer in seats:
        for owner in seats:
            if writer == owner:
                continue
            got = _resolve_merge_source(f"{owner}_F004", writer, reg)
            assert got == canon[owner], (writer, owner, got)


def test_an_own_model_prefixed_source_resolves_exactly_as_before():
    """`Codex_F001` written by Codex: the 2026-08-18 repair's own case."""
    reg = FindingRegistry()
    cid = reg.register(_finding("Codex_F001", "Codex"), "Codex")
    assert _resolve_merge_source("Codex_F001", "Codex", reg) == cid
    assert _resolve_merge_source("F001", "Codex", reg) == cid


def test_an_unprefixed_source_is_untouched_by_the_as_written_step():
    reg, canon = _registry_where_every_seat_holds_f004()
    # Bare F004 carries no owner token: it means the writer's own finding,
    # which is the documented contract ("their own stable finding id").
    assert _resolve_merge_source("F004", "CC2-SIM", reg) == canon["CC2-SIM"]


def test_an_ambiguous_as_written_alias_is_refused_and_falls_through():
    reg = FindingRegistry()
    # Two models minting the literal same alias string: lookup_alias_any
    # must refuse, and the fall-through resolves by the writer's own key.
    a = reg.register(_finding("SHARED_F009", "CC2-SIM"), "CC2-SIM")
    reg.register(_finding("SHARED_F009", "Gemini-SIM"), "Gemini-SIM")
    assert reg.lookup_alias_any("SHARED_F009") is None
    assert _resolve_merge_source("SHARED_F009", "CC2-SIM", reg) == a


def test_a_pre_repair_archive_form_resolves_through_its_recorded_alias():
    """Run-2 era ids (`Gemini-SIM_GEMINI_F004`) are aliases and must resolve."""
    reg = FindingRegistry()
    cid = reg.register(_finding("Gemini-SIM_GEMINI_F004", "Gemini-SIM"),
                       "Gemini-SIM")
    got = _resolve_merge_source("see Gemini-SIM_GEMINI_F004", "CC2-SIM", reg)
    assert got == cid, got


def test_known_limit_a_bare_vendor_foreign_form_still_resolves_to_the_writer():
    """PINS the residual, deliberately unfixed. `GEMINI_F004` written by
    CC2-SIM was never REGISTERED as an alias (the parser composes before
    register), so the as-written step misses and the strip resolves to the
    writer's own F004. Closing it needs a vendor table or a raw-alias record
    at register time; the form appears 0 times in the archive as a FOREIGN
    reference, so under the additive standard nothing is built for it. If this
    test goes red because the residual got FIXED, delete it and its pin."""
    reg, canon = _registry_where_every_seat_holds_f004()
    got = _resolve_merge_source("GEMINI_F004", "CC2-SIM", reg)
    assert got == canon["CC2-SIM"], got


# ───────────────────────── _resolve_finding_key ──────────────────────────────

def test_finding_key_resolves_a_foreign_composed_id_instead_of_unmatched():
    reg, canon = _registry_where_every_seat_holds_f004()
    got = _resolve_finding_key(reg, "CC2-SIM", "Gemini-SIM_F004")
    assert got == canon["Gemini-SIM"], got


def test_finding_key_still_resolves_bare_and_own_forms_first():
    reg, canon = _registry_where_every_seat_holds_f004()
    assert _resolve_finding_key(reg, "CC2-SIM", "F004") == canon["CC2-SIM"]
    assert _resolve_finding_key(reg, "CC2-SIM", "CC2-SIM_F004") == canon["CC2-SIM"]
    assert _resolve_finding_key(reg, "CC2-SIM", canon["Codex-SIM"]) == canon["Codex-SIM"]


def test_finding_key_refuses_an_ambiguous_cross_model_alias():
    reg = FindingRegistry()
    own = reg.register(_finding("SHARED_F009", "CC2-SIM"), "CC2-SIM")
    reg.register(_finding("SHARED_F009", "Gemini-SIM"), "Gemini-SIM")
    # The writer's own key wins through lookup_alias before any-model runs.
    assert _resolve_finding_key(reg, "CC2-SIM", "SHARED_F009") == own
    # A third model citing the shared string gets a refusal, not a guess.
    assert _resolve_finding_key(reg, "Codex-SIM", "SHARED_F009") == ""


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-q"]))
