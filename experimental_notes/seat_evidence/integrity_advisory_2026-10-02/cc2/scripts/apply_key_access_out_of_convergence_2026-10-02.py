# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'integrity_advisory_2026-10-02', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: c0f36b749400f9ba4e3033b3ded9f65ab74099af178711ec3e0b2304cdc5ac97
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Apply the 2026-10-02 founder ruling: a key-access check REPORTS, it never
blocks convergence and never terminates a run.

Every edit is an EXACT-STRING replacement with a unique anchor, applied
idempotently: running this twice is a no-op and prints `already applied`. It
exists as a script rather than as prose so the diff that was actually applied is
reproducible by anyone, per `measured-rate-travels-with-its-script`.

  D1  bench/falsifier_verify.py     PRE-execution gate: refuse on ACCESS
                                    evidence only; record vocabulary matches as
                                    advisories instead of refusals; add
                                    `seeded_faults?` to the ACCESS field list.
                                    The OUTPUT net keeps the full rule set.
  D2  bench/reference_runner_v3.py  INTEGRITY_VIOLATION leaves the convergence
                                    machinery via a dedicated `integrity_advisory`
                                    flag: it cannot halt and it cannot block.
  D3  bench/key_access_forensics.py POST-run scanner precision + the end-of-run
                                    advisory (silent when clean).

Usage:  python3 scripts/apply_key_access_out_of_convergence_2026-10-02.py [--check]
"""
from __future__ import annotations

import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
CHECK = "--check" in sys.argv
APPLIED: list[str] = []
SKIPPED: list[str] = []


def patch(rel: str, anchor: str, new: str, tag: str) -> None:
    p = REPO / rel
    text = p.read_text(encoding="utf-8")
    if new in text:
        SKIPPED.append(f"{tag} (already applied)")
        return
    n = text.count(anchor)
    if n != 1:
        raise SystemExit(f"ANCHOR NOT UNIQUE for {tag}: {n} occurrence(s) in {rel}")
    if CHECK:
        APPLIED.append(f"{tag} (would apply)")
        return
    p.write_text(text.replace(anchor, new, 1), encoding="utf-8")
    APPLIED.append(tag)


# ─────────────────────────────────────────────────────────────────────────────
# D2 — bench/reference_runner_v3.py
# ─────────────────────────────────────────────────────────────────────────────
R = "bench/reference_runner_v3.py"

_D2_CONSTS_ANCHOR = (
    'ROUTABLE_INSTRUMENT_FAULTS = EQUIPMENT_FAILURE_VERDICTS '
    '| frozenset({"NON_DISCRIMINATING"})\n'
)
patch(R, _D2_CONSTS_ANCHOR, _D2_CONSTS_ANCHOR + '''
#: The integrity gate's verdict (bench/falsifier_verify.INTEGRITY_VIOLATION),
#: duplicated as a bare string so these counters never import the gate.
#:
#: FOUNDER RULING 2026-10-02, verbatim: "If a key was accessed and read, report it
#: at the end of a run. If no key was accessed, say nothing ... But convergence
#: should not be blocked and runs should not be terminated even if a key was read.
#: That is a reporting and post run fix issue (as it always has been), not part of
#: the convergence machinery of the schema."
#:
#: WHAT THE VERDICT DOES WITHOUT THIS, measured rather than read.
#: `INTEGRITY_VIOLATION` is in NEITHER `EQUIPMENT_FAILURE_VERDICTS` NOR
#: `ROUTABLE_INSTRUMENT_FAULTS`, so in `_apply_routing` it falls past the
#: deferral `elif` into the terminal `else` and is stamped
#: `irreducible_escalation=True`. `irreducible_queue_count` counts that, and
#: `build_irreducible_queue_alarm` HALTS the run on a count above
#: `max_irreducible_queue` (default 2). That is the termination the ruling
#: forbids: run 1b (prose_convergence_run1b_2026-10-02_20261002T044234Z) halted
#: at round 2 on a queue of 3, two of which carried a ladder verdict of
#: INTEGRITY_VIOLATION, with BOTH sides of the two-sided gate satisfied
#: (gamma_critical 0.336 >= 0.30 and the zero-new-critical window).
#:
#: WHY A NEW FLAG AND NOT "STOP STAMPING THE OLD ONE". `irreducible_escalation`
#: does TWO jobs, as its own docstring says: it counts toward the halt alarm AND
#: it is the `unverified_critical_count` A4 exclusion. Removing the stamp removes
#: the halt and REINTRODUCES the A4 block -- a critical with neither
#: `irreducible_escalation` nor `routing_deferred` that "blocked convergence to
#: the round cap while never entering the irreducible-queue count", the exact
#: shape recorded at the empty-ladder repair below. `integrity_advisory` carries
#: the A4 exclusion WITHOUT the queue count, so the event is reported at the end
#: of the run and decides nothing.
INTEGRITY_VIOLATION_VERDICT = "INTEGRITY_VIOLATION"

#: Entry flag: this finding's falsifier was refused by the integrity gate. It is
#: REPORTED (bench.key_access_forensics.build_key_access_advisory) and excluded
#: from every convergence reader: it cannot halt (`_irreducible_queue_split`) and
#: it cannot block (`unverified_critical_count`).
INTEGRITY_ADVISORY_FLAG = "integrity_advisory"
''', "D2a: INTEGRITY_VIOLATION_VERDICT / INTEGRITY_ADVISORY_FLAG constants")

patch(R, '''    _TERMINAL = {"MERGED", "CLOSED", "REFUTED", "DUPLICATE", "CONFIRMED"}
    locked = deferred = 0
    for e in entries.values():
        if e.get("status") in _TERMINAL:
            continue
        if (e.get("severity") or 0.0) < CRITICAL_SEVERITY_THRESHOLD:
            continue
        if e.get("irreducible_escalation"):''',
      '''    _TERMINAL = {"MERGED", "CLOSED", "REFUTED", "DUPLICATE", "CONFIRMED"}
    locked = deferred = 0
    for e in entries.values():
        if e.get("status") in _TERMINAL:
            continue
        if (e.get("severity") or 0.0) < CRITICAL_SEVERITY_THRESHOLD:
            continue
        # INTEGRITY IS NOT IRREDUCIBILITY (founder ruling 2026-10-02). A falsifier
        # the integrity gate REFUSED is a reporting matter: the claim was never
        # measured, and the queue this function feeds TERMINATES the run. Counting
        # it here is what halted run 1b with both sides of the gate satisfied.
        # Reported instead, by build_key_access_advisory, at the end of the run.
        if e.get(INTEGRITY_ADVISORY_FLAG):
            continue
        if e.get("irreducible_escalation"):''',
      "D2b: _irreducible_queue_split excludes integrity_advisory (cannot HALT)")

patch(R, '''            if e.get("irreducible_escalation"):
                continue
            # SEVERITY NO LONGER GATES''',
      '''            if e.get("irreducible_escalation"):
                continue
            # AND NEITHER MAY AN INTEGRITY REFUSAL BLOCK (founder ruling
            # 2026-10-02). This exclusion is the HALF OF THE OLD FLAG THAT MUST
            # SURVIVE: drop it and the entry blocks A4 to the round cap while
            # entering no queue at all, which is the shape the empty-ladder
            # repair at _apply_routing records as the cost of exactly that.
            if e.get(INTEGRITY_ADVISORY_FLAG):
                continue
            # SEVERITY NO LONGER GATES''',
      "D2c: unverified_critical_count excludes integrity_advisory (cannot BLOCK)")

patch(R, '''            if verdict in EQUIPMENT_FAILURE_VERDICTS:
                if e.get("status") in TERMINAL_STATUSES:
                    registry.resolve(cid, "UNCONFIRMED", round_idx)
                    e["verified"] = False
            elif e.get("status") == "CONFIRMED":
                registry.resolve(cid, "UNCONFIRMED", round_idx)
            tally["HIL"] += 1''',
      '''            # STAMPED HERE, NOT ONLY IN ROUTING (founder ruling 2026-10-02).
            # `_apply_routing` is default-off (`routing_enabled`), so an integrity
            # refusal reaches the routing branches on SOME runs only -- while the
            # demotion two lines below runs on EVERY gated run and is what can put
            # the entry into status UNCONFIRMED, where `unverified_critical_count`
            # blocks A4. The flag therefore has to be set at the moment the
            # verdict is read, or the no-routing configuration keeps the block the
            # ruling removes.
            if verdict == INTEGRITY_VIOLATION_VERDICT:
                e[INTEGRITY_ADVISORY_FLAG] = True
                e.setdefault(
                    "integrity_advisory_reason",
                    f"the integrity gate refused this falsifier at round "
                    f"{round_idx}; the CLAIM is unmeasured and is handed to the "
                    f"post-run advisory. Per founder ruling 2026-10-02 this "
                    f"neither halts the run nor blocks convergence.")
            if verdict in EQUIPMENT_FAILURE_VERDICTS:
                if e.get("status") in TERMINAL_STATUSES:
                    registry.resolve(cid, "UNCONFIRMED", round_idx)
                    e["verified"] = False
            elif e.get("status") == "CONFIRMED":
                registry.resolve(cid, "UNCONFIRMED", round_idx)
            tally["HIL"] += 1''',
      "D2d: apply_falsifier_verdicts stamps integrity_advisory on the verdict")

patch(R, '''            e["irreducible_escalation"] = True
            e["hil_escalated"] = True''',
      '''            # AN INTEGRITY REFUSAL IS NOT AN EXHAUSTED LADDER (founder ruling
            # 2026-10-02). "Irreducible" asserts that machines tried and could
            # not. A gate refusal says the instrument was never allowed to run,
            # which is a reporting outcome. Stamping `irreducible_escalation`
            # here is what fed the halt alarm; the advisory flag keeps the A4
            # exclusion without the queue count.
            if (e.get("falsifier_verdict") or "").strip().upper() == \\
                    INTEGRITY_VIOLATION_VERDICT:
                e[INTEGRITY_ADVISORY_FLAG] = True
                e["hil_escalated"] = True
                e.setdefault(
                    "integrity_advisory_reason",
                    f"the integrity gate refused this falsifier; the routing "
                    f"ladder could not measure the claim at round {round_idx}. "
                    f"Reported post-run; it neither halts nor blocks.")
                tally["hil"] += 1
                continue
            e["irreducible_escalation"] = True
            e["hil_escalated"] = True''',
      "D2e: _apply_routing routes an integrity verdict to the advisory lane")


# ─────────────────────────────────────────────────────────────────────────────
# D1 — bench/falsifier_verify.py
# ─────────────────────────────────────────────────────────────────────────────
F = "bench/falsifier_verify.py"

patch(F, '''_KEY_FIELDS = (
    r"planted_false_by_tier|n_planted_false|planted_per_cluster_in_document_order"
    r"|clean_clusters|difficulty_ladder|difficulty_tier|planted_false|sibling_pairs"
    r"|tier_counts|verify_tool|contrast_pairs"
)''',
      '''_KEY_FIELDS = (
    r"planted_false_by_tier|n_planted_false|planted_per_cluster_in_document_order"
    r"|clean_clusters|difficulty_ladder|difficulty_tier|planted_false|sibling_pairs"
    # `seeded_faults` IS A GROUND-TRUTH FIELD and was absent from this list
    # (2026-10-02). The benchmark task records carry it -- 14 occurrences across 5
    # production entry points -- so `task["seeded_faults"]` reads which faults were
    # planted. It is listed in the PLURAL FIRST and the trailing `s` is optional,
    # because Python alternation takes the first match and the singular would
    # otherwise shadow it.
    r"|seeded_faults?"
    r"|tier_counts|verify_tool|contrast_pairs"
)''', "D1a: seeded_faults? added to _KEY_FIELDS")

patch(F, '''_KEY_MATERIAL_RULES: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"[\\w./~$-]*answer[_-]key[\\w.-]*\\.json"),
     "an answer-key file path"),''',
      '''# SPLIT INTO ACCESS AND VOCABULARY (founder ruling 2026-10-02: "The role of
# experiments is to provide solutions to any problem that is posed. Not to choke
# on minor prose/syntax issues of this nature.").
#
# ACCESS rules describe a falsifier HOLDING key material: a key path, a key field
# subscripted or fetched, the claims->truth schema walked, a protected location or
# environment variable named. These REFUSE execution.
#
# VOCABULARY rules describe a falsifier TALKING ABOUT key material. They are
# retained in full and are still applied to OUTPUT (see `scan_falsifier_output`)
# and still recorded against SOURCE as advisories, but on source they no longer
# refuse. MEASURED on this archive before the change: 10 of 14 refusal events
# (71.4286%, Wilson [45.3509%, 88.2786%]) were the single token `seeded_fault`
# matched inside the plural field name, while 0 of 94 recorded falsifier fragments
# subscripted or `.get`-ed that field -- so every one of those refusals stopped a
# mention, not an access. The producer is
# scripts/guard_false_positive_blind_spot_2026-10-02.py.
_KEY_ACCESS_RULES: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"[\\w./~$-]*answer[_-]key[\\w.-]*\\.json"),
     "an answer-key file path"),''',
      "D1b: open the _KEY_ACCESS_RULES tuple")

patch(F, '''    (re.compile(rf"\\[\\s*{_Q}claims{_Q}\\s*\\][^\\x00]{{0,240}}?{_Q}truth{_Q}"),
     "a claims->truth lookup (the answer-key schema)"),
    (re.compile(r"answer[_\\- ]?key", re.I),
     "answer-key vocabulary"),''',
      '''    (re.compile(rf"\\[\\s*{_Q}claims{_Q}\\s*\\][^\\x00]{{0,240}}?{_Q}truth{_Q}"),
     "a claims->truth lookup (the answer-key schema)"),
    (re.compile(r"CDSFL_(?:STORE|VAULT|TARGETS|KEY_DIR|LEGACY_STORES|SCORING_CONF)"),
     "a protected environment variable by name"),
)

#: Vocabulary-only signals. Advisory against SOURCE, still refusing against
#: OUTPUT -- and the OUTPUT side is the load-bearing one. Exp 48's damage was not
#: that C0012 read the key, it was that C0012 PRINTED the planted set into a
#: channel every other seat read. A printed set carries no Python subscript, so
#: the access rules above cannot see it and these are the only rules that can.
_KEY_VOCABULARY_RULES: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"answer[_\\- ]?key", re.I),
     "answer-key vocabulary"),''',
      "D1c: close access tuple, open vocabulary tuple")

patch(F, '''    (re.compile(rf"\\b(?:{_KEY_FIELDS})\\b"),
     "an answer-key schema field named"),
    (re.compile(r"\\bMANIFEST\\b"),
     "the target manifest (carries per-target planted counts)"),
    (re.compile(r"CDSFL_(?:STORE|VAULT|TARGETS|KEY_DIR|LEGACY_STORES|SCORING_CONF)"),
     "a protected environment variable by name"),
)''',
      '''    (re.compile(rf"\\b(?:{_KEY_FIELDS})\\b"),
     "an answer-key schema field named"),
    (re.compile(r"\\bMANIFEST\\b"),
     "the target manifest (carries per-target planted counts)"),
)

#: UNCHANGED AND STILL THE WHOLE SET. `scan_falsifier_output` reads this, and a
#: narrower output net is how a leaked planted set reaches the panel.
_KEY_MATERIAL_RULES: tuple[tuple[re.Pattern[str], str], ...] = (
    _KEY_ACCESS_RULES + _KEY_VOCABULARY_RULES
)

#: Vocabulary matched against SOURCE and allowed through. Appended to, never
#: cleared: an advisory that is not reported is the same as no advisory.
KEY_VOCABULARY_ADVISORIES: list[dict] = []

#: Set to refuse on vocabulary again, as the gate did before 2026-10-02. The old
#: behaviour is retained rather than removed, because this flag is the only
#: measurement that can show the narrowing was right or wrong.
import os as _os_strict  # noqa: E402

STRICT_VOCABULARY_GATE = bool(_os_strict.environ.get("CDSFL_KEY_GATE_STRICT"))''',
      "D1d: close vocabulary tuple, rebuild _KEY_MATERIAL_RULES, add advisories")

patch(F, '''    violations: list[tuple[str, str]] = []
    for pattern, reason in _KEY_MATERIAL_RULES + _SOURCE_ONLY_RULES:
        m = pattern.search(code)
        if m:
            violations.append((reason, m.group(0)[:200]))''',
      '''    violations: list[tuple[str, str]] = []
    # ACCESS REFUSES; VOCABULARY IS RECORDED AND ALLOWED (founder ruling
    # 2026-10-02). `STRICT_VOCABULARY_GATE` restores the pre-ruling behaviour for
    # anyone who wants to measure the difference.
    _rules = _KEY_ACCESS_RULES + _SOURCE_ONLY_RULES
    if STRICT_VOCABULARY_GATE:
        _rules = _KEY_ACCESS_RULES + _KEY_VOCABULARY_RULES + _SOURCE_ONLY_RULES
    for pattern, reason in _rules:
        m = pattern.search(code)
        if m:
            violations.append((reason, m.group(0)[:200]))
    if not STRICT_VOCABULARY_GATE:
        for pattern, reason in _KEY_VOCABULARY_RULES:
            m = pattern.search(code)
            if m:
                KEY_VOCABULARY_ADVISORIES.append(
                    {"reason": reason, "matched": m.group(0)[:200],
                     "code_head": code[:200]})''',
      "D1e: scan_falsifier_source refuses on access only, records vocabulary")

print("APPLIED:" if not CHECK else "WOULD APPLY:")
for a in APPLIED:
    print("  +", a)
for s in SKIPPED:
    print("  =", s)
if not APPLIED:
    print("  (nothing to do)")
