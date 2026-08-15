"""The shared `<generic>` bucket in the location-keyed novelty series.

THE DEFECT (found 2026-08-04 in panel review, verified live 2026-08-08, fixed
the same day). `_location_keyed_critical_series` in bench/reference_runner_v2.py
keyed every critical from which no code location could be parsed to ONE shared
constant:

    key = set(locs) if locs else {"<generic>"}

The first unlocated critical claimed `<generic>`; every later one was therefore
non-novel forever, whatever it actually said. Measured across the modern
falsifier-live regime (Exp 42-49): 42 of 288 criticals, 14.6%, rising to 25% in
Exp 47. A PARSING failure was silently promoted to an identity judgement.

That is categorically different from the co-location trade-off the module openly
documents. Merging two defects in one already-flagged function is a deliberate
conservative choice with a stated rationale. This had none.

WHY THE PARSE FAILS. `target_symbols` extracts AST function/method/class names
only, so a finding about a module-level constant names no extractable symbol. In
Exp 47 ten distinct criticals about four different module-level regexes
(`_ALT_HEADER_RE`, `_CONTRAST_RE`, `_DIM_LINE_RE`, `_NULL_HEADER_RE`) collapsed
into that single bucket.

WHY IT MATTERS. When `location_keyed_convergence` is set — sixteen configs set
it — the caller overwrites `novel_critical_history[-1]` with this series, feeding
the COUNT side of the two-sided convergence gate. Gamma is NOT affected:
`gamma_critical` is computed independently from the settled series. This fix
touches an INPUT to the gate, never gamma.

WHAT THE FIX DOES. Unlocated criticals key on their own STEM signature (numbers,
claim IDs, backticked identifiers) and merge only when signatures agree by at
least 0.20 Jaccard; an empty signature falls back to a hash of the finding's own
text. So two different unlocated findings are two keys and a re-find is one.

DIRECTION OF ERROR. Splitting. The fix can only partition the old single bucket,
and located findings are untouched, so every per-round count is >= the old count
and a zero round can only become non-zero. Convergence can be DELAYED, never
brought forward. `test_fix_can_never_advance_convergence` pins that as a
property; the archive tests pin that in practice no run's outcome moves.
"""
from __future__ import annotations

import json
import os

import pytest

import bench.reference_runner_v2 as rr
from bench.convergence_location import finding_locations

CRIT = rr.CRITICAL_SEVERITY_THRESHOLD  # 0.7


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

class _Reg:
    """Minimal registry stand-in: the series function reads only `.entries`."""

    def __init__(self, entries):
        self.entries = entries


def _entry(cid, round_idx, description, severity=0.85, status="CLOSED"):
    return {
        "canonical_id": cid,
        "open_since_round": round_idx,
        "description": description,
        "severity": severity,
        "status": status,
    }


def _entries(*items):
    return {e["canonical_id"]: e for e in items}


def _old_rule_series(registry, max_round, symbols):
    """THE PRE-FIX IMPLEMENTATION, verbatim, kept here as the comparison arm.

    This is the code that shipped until 2026-08-08. It exists in this file only
    so the tests can demonstrate the difference on identical inputs; nothing in
    the runner calls it.
    """
    entries = registry.entries if hasattr(registry, "entries") else {}
    vals = list(entries.values()) if isinstance(entries, dict) else list(entries)

    def _ord(e):
        r = e.get("open_since_round")
        return (r if r is not None else 1_000_000, str(e.get("canonical_id", "")))

    seen: set = set()
    series = [0] * (max_round + 1)
    for e in sorted(vals, key=_ord):
        r = e.get("open_since_round")
        if r is None or r < 0 or r > max_round:
            continue
        if e.get("status") in rr._NON_NOVEL_TERMINAL_STATUSES:
            continue
        if (e.get("severity") or 0.0) < CRIT:
            continue
        locs = finding_locations(e.get("description", "") or "", symbols)
        key = set(locs) if locs else {"<generic>"}
        if key - seen:
            series[r] += 1
        seen |= key
    return series


def _zero_tail_at(series, round_idx, window=3):
    """Does the count side of the two-sided gate hold at `round_idx`?"""
    lo = round_idx - window + 1
    if lo < 0 or round_idx >= len(series):
        return False
    return all(v == 0 for v in series[lo:round_idx + 1])


# Two genuinely different criticals about two different module-level regexes.
# Neither names an AST symbol, so neither has an extractable code location —
# the exact shape that collapsed in Exp 47.
UNLOCATED_A = (
    "The regex `_ALT_HEADER_RE` includes an optional separator `(?:[:\\-]\\s*)?` "
    "which greedily consumes an em-dash, so a dash-delimited header at line 74 "
    "never matches and the alternative block is silently dropped."
)
UNLOCATED_B = (
    "`_CONTRAST_RE` truncates multi-line contrast statements at the first "
    "newline, so a valid two-line contrast is rejected and the model takes an "
    "unwarranted penalty."
)
# A re-wording of UNLOCATED_A by a different model: same hard tokens
# (`_alt_header_re`, 74), different prose.
UNLOCATED_A_REWORDED = (
    "Line 74's `_ALT_HEADER_RE` pattern makes the separator optional, and the "
    "optional group swallows the em-dash before the header text is reached. "
    "Dash-delimited alternative headers therefore fail to parse."
)

SYMBOLS = frozenset({"parse_alternative_block", "validate_alternative"})


# ---------------------------------------------------------------------------
# 1. the P-pass case: the defect, and the fix, on identical input
# ---------------------------------------------------------------------------

def test_old_rule_loses_the_second_unlocated_critical():
    """CHARACTERISATION of the defect. Two DIFFERENT unlocated criticals in
    sequence: the old rule counts only the first. The second is not merged, not
    downgraded — it is invisible."""
    reg = _Reg(_entries(
        _entry("C0001", 0, UNLOCATED_A),
        _entry("C0002", 1, UNLOCATED_B),
    ))
    assert finding_locations(UNLOCATED_A, SYMBOLS) == frozenset()
    assert finding_locations(UNLOCATED_B, SYMBOLS) == frozenset()
    assert _old_rule_series(reg, 1, SYMBOLS) == [1, 0]


def test_fix_counts_two_different_unlocated_criticals_as_two():
    """THE FIX, same input. Two different unlocated criticals are two keys."""
    reg = _Reg(_entries(
        _entry("C0001", 0, UNLOCATED_A),
        _entry("C0002", 1, UNLOCATED_B),
    ))
    assert rr._location_keyed_critical_series(reg, 1, SYMBOLS) == [1, 1]


def test_fix_still_counts_a_refind_once_not_twice():
    """The other half, and the half that matters more: a re-find of the SAME
    unlocated critical must stay ONE. Getting this wrong resurrects the
    ID-proxy disease that made location keying necessary — every re-worded
    re-find counting as new, so the series never reaches zero."""
    # byte-identical re-find
    reg = _Reg(_entries(
        _entry("C0001", 0, UNLOCATED_A),
        _entry("C0002", 1, UNLOCATED_A),
    ))
    assert rr._location_keyed_critical_series(reg, 1, SYMBOLS) == [1, 0]

    # re-worded re-find by another model, same hard tokens
    reg = _Reg(_entries(
        _entry("C0001", 0, UNLOCATED_A),
        _entry("C0002", 1, UNLOCATED_A_REWORDED),
    ))
    assert rr._location_keyed_critical_series(reg, 1, SYMBOLS) == [1, 0]


def test_three_distinct_unlocated_criticals_in_one_round():
    """The collapse was unbounded, not off-by-one: under the old rule any number
    of distinct unlocated criticals contributed exactly one."""
    third = ("`_DIM_LINE_RE` is anchored with `.match`, so a dimension line that "
             "does not start the body is never found and section 91 is skipped.")
    reg = _Reg(_entries(
        _entry("C0001", 0, UNLOCATED_A),
        _entry("C0002", 0, UNLOCATED_B),
        _entry("C0003", 0, third),
    ))
    assert _old_rule_series(reg, 0, SYMBOLS) == [1]
    assert rr._location_keyed_critical_series(reg, 0, SYMBOLS) == [3]


# ---------------------------------------------------------------------------
# 2. the co-location rule is untouched
# ---------------------------------------------------------------------------

def test_located_findings_behave_exactly_as_before():
    """The fix must change NOTHING about findings that do name a location. The
    documented co-location trade-off (a second defect in an already-flagged
    function merges) is a deliberate choice and stays."""
    a = "`parse_alternative_block` drops the trailing block when the input ends without a newline."
    b = "`parse_alternative_block` also mis-orders siblings when two share a dimension tag."
    c = "`validate_alternative` accepts an empty contrast statement."
    reg = _Reg(_entries(
        _entry("C0001", 0, a),
        _entry("C0002", 1, b),   # same location -> merged, by design
        _entry("C0003", 2, c),   # new location -> novel
    ))
    expected = [1, 0, 1]
    assert _old_rule_series(reg, 2, SYMBOLS) == expected
    assert rr._location_keyed_critical_series(reg, 2, SYMBOLS) == expected


def test_unlocated_keys_never_collide_with_located_keys():
    """An unlocated key must not accidentally suppress a real symbol, nor be
    suppressed by one."""
    located = "`parse_alternative_block` mishandles the final block."
    reg = _Reg(_entries(
        _entry("C0001", 0, UNLOCATED_A),
        _entry("C0002", 1, located),
        _entry("C0003", 2, UNLOCATED_B),
    ))
    assert rr._location_keyed_critical_series(reg, 2, SYMBOLS) == [1, 1, 1]


# ---------------------------------------------------------------------------
# 3. the fallback key itself
# ---------------------------------------------------------------------------

def test_unlocated_key_is_not_a_shared_constant():
    """Structural guard against the defect returning: two unlocated findings
    with disjoint hard tokens must NOT share a key."""
    buckets = []
    k1 = rr._unlocated_novelty_key(UNLOCATED_A, buckets)
    k2 = rr._unlocated_novelty_key(UNLOCATED_B, buckets)
    assert k1 != k2
    assert k1 != "<generic>" and k2 != "<generic>"
    assert len(buckets) == 2


def test_unlocated_key_merges_on_signature_agreement():
    buckets = []
    k1 = rr._unlocated_novelty_key(UNLOCATED_A, buckets)
    k2 = rr._unlocated_novelty_key(UNLOCATED_A_REWORDED, buckets)
    assert k1 == k2
    assert len(buckets) == 1, "a re-find must not open a second bucket"


def test_empty_signature_falls_back_to_text_not_to_a_shared_bucket():
    """2.5% of criticals carry no number, claim ID or backticked identifier.
    They must still be keyed per-finding — falling back to a shared constant
    here would reinstate the defect in miniature."""
    no_tokens_a = "The parser silently ignores trailing whitespace and drops the final entry."
    no_tokens_b = "The comparison is case sensitive where the specification says it must not be."
    from bench.convergence_location import stem_signature
    assert stem_signature(no_tokens_a) == frozenset()
    assert stem_signature(no_tokens_b) == frozenset()

    buckets = []
    assert (rr._unlocated_novelty_key(no_tokens_a, buckets)
            != rr._unlocated_novelty_key(no_tokens_b, buckets))
    # identical text is still one key
    assert (rr._unlocated_novelty_key(no_tokens_a, buckets)
            == rr._unlocated_novelty_key(no_tokens_a, buckets))


def test_status_and_severity_filters_still_apply():
    """The fix must not smuggle non-novel or sub-critical entries into the
    count. MERGED/DUPLICATE/UNCONFIRMED/REFUTED and severity < 0.7 stay out."""
    reg = _Reg(_entries(
        _entry("C0001", 0, UNLOCATED_A, status="MERGED"),
        _entry("C0002", 0, UNLOCATED_B, severity=0.5),
        _entry("C0003", 0, UNLOCATED_A_REWORDED, status="REFUTED"),
    ))
    assert rr._location_keyed_critical_series(reg, 0, SYMBOLS) == [0]


# ---------------------------------------------------------------------------
# 4. the safety property: the fix can only delay convergence
# ---------------------------------------------------------------------------

def test_fix_can_never_advance_convergence():
    """THE LOAD-BEARING PROPERTY. The fix partitions one key into several and
    leaves located keys alone, so every per-round count is >= the old count.
    A zero round can therefore only become non-zero, and the K-consecutive-zero
    condition can only be satisfied LATER or not at all — never sooner.

    Checked over a mixed stream that exercises located, unlocated, re-found and
    filtered entries together."""
    stream = [
        (0, UNLOCATED_A), (0, "`parse_alternative_block` drops the last block."),
        (1, UNLOCATED_B), (1, UNLOCATED_A_REWORDED),
        (2, "`validate_alternative` accepts an empty contrast."),
        (3, "`_NULL_HEADER_RE` misses bolded colons at line 155."),
        (4, UNLOCATED_A),
        (5, "`parse_alternative_block` also mis-orders siblings."),
    ]
    reg = _Reg(_entries(*[
        _entry(f"C{i:04d}", r, d) for i, (r, d) in enumerate(stream)
    ]))
    old = _old_rule_series(reg, 5, SYMBOLS)
    new = rr._location_keyed_critical_series(reg, 5, SYMBOLS)
    assert len(old) == len(new)
    assert all(n >= o for o, n in zip(old, new)), (old, new)
    for r in range(len(new)):
        if _zero_tail_at(new, r):
            assert _zero_tail_at(old, r), (
                f"round {r}: new series converged where old did not — the fix "
                f"must never advance convergence. old={old} new={new}")


def test_zero_symbols_no_longer_fabricates_an_instant_convergence():
    """THE GOVERNING FAILURE MODE, closed as a consequence.

    When symbol extraction yields nothing — a target file that moved, a parse
    that failed, a non-Python target with no claim IDs — EVERY critical becomes
    unlocated. Under the old rule the whole run collapsed to `[1, 0, 0, 0, ...]`:
    a broken measurement rendered as a textbook clean convergence, and the count
    side of the gate would have closed the run at round 3 on a series that
    described nothing. The caller logs a warning about zero symbols, but the
    warning does not stop the gate.

    Under the fix the same input produces a live series that does not converge.
    A failed parse now looks like a failed parse.
    """
    descs = [UNLOCATED_A, UNLOCATED_B, UNLOCATED_A_REWORDED,
             "`_NULL_HEADER_RE` misses bolded colons at line 155.",
             "`score_isomorphism` divides by a zero token count for empty input."]
    reg = _Reg(_entries(*[
        _entry(f"C{i:04d}", i, d) for i, d in enumerate(descs)
    ]))
    no_symbols = frozenset()
    old = _old_rule_series(reg, 4, no_symbols)
    assert old == [1, 0, 0, 0, 0]
    assert _zero_tail_at(old, 3), "the old zero tail IS the fabricated convergence"

    new = rr._location_keyed_critical_series(reg, 4, no_symbols)
    # A is re-found at index 2, so four distinct findings, not five.
    assert new == [1, 1, 0, 1, 1]
    assert not _zero_tail_at(new, 4), (
        "a run with no extractable symbols must not present a clean zero tail")


# ---------------------------------------------------------------------------
# 5. archive replay — no historical convergence outcome moves
# ---------------------------------------------------------------------------

LOGS = os.path.join(os.path.dirname(__file__), "..", "logs")

EXP47 = os.path.join(
    LOGS, "exp47_divergence_locationkey_live_20260728T230026Z",
    "exp47_divergence_locationkey_live_report.json")
EXP46 = os.path.join(
    LOGS, "exp46_stage6_locationkey_live_20260728T103151Z",
    "exp46_stage6_locationkey_live_report.json")

# The run-time target text is not archived, so the symbol set is pinned here
# rather than re-extracted. These sets are the evidence that the replay is
# faithful: with them, the pre-fix implementation reproduces each run's archived
# `location_crit_shadow_history` exactly (asserted below). Re-extracting from the
# live target file would silently change the measurement basis whenever the
# target — itself a file under study, and repeatedly repaired — is edited.
EXP47_SYMBOLS = frozenset({
    "AlternativeRecord", "DivergenceConfig", "DivergenceRecord",
    "_normalise_dimension", "_recidivism_text", "_tokenise",
    "build_divergence_record", "check_sibling_admissibility",
    "divergence_config_from_dict", "eta_int_modulator",
    "parse_alternative_block", "parse_contrast_statement",
    "parse_null_justification_block", "score_isomorphism",
    "validate_alternative", "validate_null_justification"})
EXP46_SYMBOLS = frozenset({
    "PerFindingNoveltyLog", "PerSourceCoverage", "PerToolFPRLog",
    "ShadowStage6Calibrator", "ShadowStage6RoundLog", "__init__",
    "_assess_finding", "_compute_shadow_e_values", "_estimate_h_ratio",
    "_estimate_retrieval_sparsity", "_estimate_source_coverage",
    "_track_source_cooccurrence", "_track_tool_fpr", "fail_fraction",
    "get_calibration_summary", "observe_round", "shadow_e_pass", "to_dict",
    "total"})


def _load(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


@pytest.mark.skipif(not os.path.exists(EXP47), reason="Exp 47 run log not present")
def test_exp47_replay_is_faithful_to_the_archive():
    """The measurement basis. The pre-fix implementation, run over the archived
    Exp 47 registry with the pinned symbol set, must reproduce the series that
    run actually recorded. Without this the before/after comparison below is a
    comparison against something the run never computed."""
    data = _load(EXP47)
    entries = data["registry"]["entries"]
    archived = data["location_crit_shadow_history"]
    old = _old_rule_series(_Reg(entries), len(archived) - 1, EXP47_SYMBOLS)
    assert old == archived, (
        "replay no longer reproduces the archived series — the comparison basis "
        "has moved and the before/after numbers below are not comparable")


@pytest.mark.skipif(not os.path.exists(EXP47), reason="Exp 47 run log not present")
def test_exp47_surfaces_hidden_criticals_without_moving_convergence():
    """Exp 47, the worst case in the archive (25% of its criticals unlocated).

    The run closed at round 13 on the critical-quiescence path, so the count side
    of the two-sided gate is what this fix could disturb. It does not: the fix
    surfaces five previously invisible criticals and the zero tail at round 13
    still holds, so the run still closes exactly where it did.

    It does tighten rounds 11 and 12, where the old series read a zero tail the
    new one does not. Neither round converged in the real run — other gate
    conditions blocked both — so no outcome changes there either.
    """
    data = _load(EXP47)
    entries = data["registry"]["entries"]
    archived = data["location_crit_shadow_history"]
    converged_at = data["converged_at"]
    assert converged_at == 13
    assert "QUIESCENCE" in data["convergence_reason"]

    new = rr._location_keyed_critical_series(
        _Reg(entries), len(archived) - 1, EXP47_SYMBOLS)

    assert all(n >= o for o, n in zip(archived, new)), (archived, new)
    assert sum(new) - sum(archived) == 5, (
        "five criticals that were permanently invisible should now be counted")
    assert _zero_tail_at(archived, converged_at)
    assert _zero_tail_at(new, converged_at), (
        f"Exp 47 must still close at round {converged_at}: new={new}")


@pytest.mark.skipif(not os.path.exists(EXP46), reason="Exp 46 run log not present")
def test_exp46_refind_merging_is_what_preserves_its_convergence():
    """WHY SIGNATURE MERGING AND NOT PER-FINDING IDENTITY.

    The obvious fix — give every unlocated finding its own key — is wrong, and
    Exp 46 is the case that proves it. Exp 46 carries a re-worded re-find of an
    unlocated critical in round 3. Under per-finding identity that re-find counts
    as new, the zero tail at round 5 is destroyed, and a run that converged in
    reality would not have. Under the shipped rule it merges and the run closes
    where it did.

    This is the same failure that killed lexical Jaccard as a splitter: models
    re-word re-finds enough that any identity keyed on the wording splits genuine
    repeats.
    """
    data = _load(EXP46)
    entries = data["registry"]["entries"]
    archived = data["location_crit_shadow_history"]
    converged_at = data["converged_at"]
    assert converged_at == 5
    assert "QUIESCENCE" in data["convergence_reason"]

    old = _old_rule_series(_Reg(entries), len(archived) - 1, EXP46_SYMBOLS)
    assert old == archived, "replay basis has moved"

    new = rr._location_keyed_critical_series(
        _Reg(entries), len(archived) - 1, EXP46_SYMBOLS)
    assert _zero_tail_at(new, converged_at), (
        f"Exp 46 must still close at round {converged_at}: new={new}")

    # The rejected alternative, replayed on the same registry: key every
    # unlocated finding by its own text.
    strict = _strict_identity_series(_Reg(entries), len(archived) - 1, EXP46_SYMBOLS)
    assert not _zero_tail_at(strict, converged_at), (
        "per-finding identity was expected to break Exp 46's convergence; if it "
        "no longer does, the justification for signature merging needs re-measuring")


def _strict_identity_series(registry, max_round, symbols):
    """The REJECTED alternative: every unlocated finding keyed by its own text.

    Kept so the choice of rule is falsifiable rather than asserted.
    """
    import hashlib
    import re as _re

    entries = registry.entries
    vals = list(entries.values())

    def _ord(e):
        r = e.get("open_since_round")
        return (r if r is not None else 1_000_000, str(e.get("canonical_id", "")))

    seen: set = set()
    series = [0] * (max_round + 1)
    for e in sorted(vals, key=_ord):
        r = e.get("open_since_round")
        if r is None or r < 0 or r > max_round:
            continue
        if e.get("status") in rr._NON_NOVEL_TERMINAL_STATUSES:
            continue
        if (e.get("severity") or 0.0) < CRIT:
            continue
        desc = e.get("description", "") or ""
        locs = finding_locations(desc, symbols)
        if locs:
            key = set(locs)
        else:
            norm = _re.sub(r"\s+", " ", desc.strip().lower())
            key = {"<strict>:" + hashlib.sha1(norm.encode()).hexdigest()[:12]}
        if key - seen:
            series[r] += 1
        seen |= key
    return series


# ---------------------------------------------------------------------------
# 6. the failure path must not report a gate revert as a skipped shadow
#     (added by the adversarial verification pass, 2026-08-08)
# ---------------------------------------------------------------------------

def test_a_failed_gate_computation_does_not_announce_itself_as_shadow():
    """THE GOVERNING FAILURE MODE ON THE ERROR PATH.

    The call site wraps `_location_keyed_critical_series` in a bare
    `except Exception` so a computation failure can never break a run. That
    swallow is deliberate and stays. But when `location_keyed_convergence` is
    set, the series IS the count side of the two-sided gate: on failure the
    round's gate input silently remains the ID-proxy value, i.e. the run
    reverts to the cross-round dedup failure the location key exists to fix.

    The handler used to log that as `[shadow] location-keyed novelty skipped`
    — a real gate reverting, reported as a skipped telemetry computation. It
    now branches on `_gates`, which means `_gates` must be bound BEFORE the
    `try` (inside it, the handler cannot see it on an early raise).

    Structural rather than behavioural, because reaching the handler requires
    a live round loop. It fails loudly if anyone re-nests the assignment.
    """
    import ast
    import inspect
    import textwrap

    src = inspect.getsource(rr.run_experiment) if hasattr(rr, "run_experiment") else None
    if src is None:                                   # pragma: no cover
        path = os.path.join(os.path.dirname(rr.__file__), "reference_runner_v2.py")
        with open(path, "r", encoding="utf-8") as fh:
            src = fh.read()
    tree = ast.parse(textwrap.dedent(src))

    target = None
    for node in ast.walk(tree):
        if not isinstance(node, ast.Try):
            continue
        handler_src = " ".join(ast.dump(h) for h in node.handlers)
        if "location-keyed novelty" in handler_src:
            target = node
            break
    assert target is not None, "call-site try/except for the location series not found"

    assigned_in_try = {
        t.id
        for n in ast.walk(ast.Module(body=target.body, type_ignores=[]))
        if isinstance(n, ast.Assign)
        for t in n.targets
        if isinstance(t, ast.Name)
    }
    assert "_gates" not in assigned_in_try, (
        "_gates is assigned inside the try, so the exception handler cannot read it "
        "and a gate revert is reported as a skipped shadow computation")

    handler_has_gate_branch = any(
        isinstance(n, ast.If) and any(
            isinstance(sub, ast.Name) and sub.id == "_gates"
            for sub in ast.walk(n.test))
        for h in target.handlers
        for n in ast.walk(ast.Module(body=h.body, type_ignores=[]))
    )
    assert handler_has_gate_branch, (
        "the failure handler must distinguish a gating failure from a shadow skip")
