"""Latent-tagger — the missing upstream producer for severity calibration.

Severity calibration (``_apply_severity_calibration`` in
``bench/reference_runner_v3.py``, commit 050f17c, 2026-06-10) demotes a finding
iff it is (1) critical, (2) falsifier-CONFIRMED real, (3) explicitly flagged
``latent``, and (4) not in a never-demote category. Condition (3) has never had
a producer, so the mechanism has been inert since it was written. This module is
that producer.

WHAT "LATENT" MEANS HERE
-----------------------
Taken from the calibration design and the frozen critical-definition
pre-registration (``bench/exp40_baseline/CRITICAL_DEFINITION_PREREG_2026-05-18.md``):
a finding is LATENT when the defect is *genuine* but *requires a trigger absent
from the artefact's usage contract* — no caller can reach it, the code path is
shadow/telemetry only, or it fires only under a configuration nobody runs. A
latent defect is real; it is simply not consequential at the artefact's intended
function, so it should not perpetually re-block convergence as a critical.

Latency is a claim about REACHABILITY. It is NOT the same as "low severity",
"non-critical", "hard to trigger", or "the falsifier could not demonstrate it".

WHERE THE EVIDENCE COMES FROM
-----------------------------
In precedence order:

  1. An EXPLICIT panel-emitted field (``REACHABILITY:`` / ``TRIGGER:`` /
     ``LATENT:``). This is the intended long-run source: the panel states
     reachability because the finding schema asks it to. Nothing in the current
     schema asks, so this source is empty on all historical runs — see the
     measured base rates in ``bench/tests/test_latent_tagger.py``.
  2. An EXPLICIT prose claim of unreachability in the finding's own text, matched
     against a deliberately narrow, high-precision marker set.
  3. Otherwise: NOT latent.

Both sources read ``_latency_text`` — the DESCRIPTION with fenced code blocks
removed — and never the proposed fix or the falsifier code. See that function
for the rule and the measured cases that forced it.

(3) is the fail-safe and it is load-bearing. A wrong "latent" tag demotes a real
critical out of the convergence gate, which is the one failure this whole
subsystem must never cause. Silence is therefore read as "reachable", never as
"probably fine".

WHAT THIS MODULE DELIBERATELY DOES NOT DO
-----------------------------------------
An earlier design inferred latency from the falsifier's own source: a falsifier
that has to write private attributes or monkeypatch module functions was taken
to be constructing a trigger no real caller supplies. That inference was tested
against all 293 archival findings from Exp 44-49 and REFUTED. Of the ten
findings whose falsifiers write private state, inspection shows every one is
ordinary test scaffolding (stub chains, fake loggers, monkeypatched helpers)
attached to defects the finding text explicitly places on the real path — e.g.
Exp 44 C0047, whose description opens "On the real ingestion path". The AST
signal measures test-authoring style, not reachability, so it is not used. The
negative result is retained in the test suite as a regression guard.
"""

from __future__ import annotations

import re
from typing import Any, Dict, Iterable, Optional, Tuple

__all__ = [
    "NEVER_DEMOTE_CATEGORIES",
    "classify_category",
    "tag_entry",
    "tag_registry",
]

# ── Category classification ────────────────────────────────────────────────
# Mirrors _SEVERITY_CALIB_NEVER_DEMOTE_CATEGORIES in reference_runner_v3. A
# category assigned here that lands in that set makes the finding permanently
# undemotable, so this classifier is deliberately LIBERAL: it is a safety
# interlock, and a false "this is a safety finding" costs nothing but a
# retained critical, while a false "this is cosmetic" costs a demoted real one.
NEVER_DEMOTE_CATEGORIES = frozenset(
    {"safety", "core", "core_functionality", "security", "data_loss"}
)

_CATEGORY_PATTERNS: Tuple[Tuple[str, str], ...] = (
    ("security", r"\b(?:security|injection|credential|secret|token leak|"
                 r"auth(?:entication|orisation|orization)|privilege|sandbox escape|"
                 r"path traversal|deserial)\w*"),
    # Clause 4 of the frozen rubric is "silent evidence loss" — loss,
    # suppression, or misclassification of a finding. Any "silently <verb>"
    # construction over results/records is that clause on its face, so the
    # verb list is open rather than enumerated.
    ("data_loss", r"\b(?:data[- ]loss|silent(?:ly)?[a-z ]{0,20}\b"
                  r"(?:drop|discard|lose|lost|empty|missing|skip|omit|swallow)\w*|"
                  r"corrupt\w*|overwrit\w+|truncat\w+ (?:the )?(?:record|chain|log)|"
                  r"unrecoverab\w+|evidence loss)"),
    ("safety", r"\b(?:safety|unsafe|hazard\w*|injur\w+|fatal|physical harm)\b"),
    # Clauses 1-5 of the frozen critical rubric: wrong result, hard-constraint
    # violation, verification-integrity corruption, silent evidence loss,
    # unreproducibility. Any of these is core functionality by definition.
    # NOTE the trailing s? on every noun. Without it "silently wrong results"
    # slipped the interlock while "wrong result" caught it — a plural typo in a
    # safety veto, found in the Exp 47 C0024 audit.
    ("core_functionality",
     r"\b(?:wrong (?:result|answer|value|output|verdict|order)s?|incorrect\w*|"
     r"mathematically wrong|violates? (?:a )?(?:hard )?constraint|"
     r"convergence|severity accounting|novelty accounting|reconciliation|"
     r"masks? a real|silently (?:accept|pass|succeed)\w*|"
     r"unreproducib\w+|crash\w*|raises? an unhandled|infinite loop|deadlock)\b"),
)


def classify_category(text: str) -> str:
    """Best-effort consequence category for a finding.

    Returns one of the never-demote category names when the text carries a
    marker for that consequence class, else "" (unclassified — which leaves the
    finding demotable if it is independently tagged latent).
    """
    low = text.lower()
    for name, pattern in _CATEGORY_PATTERNS:
        if re.search(pattern, low):
            return name
    return ""


# ── Source 1: explicit panel-emitted reachability field ────────────────────
# The intended long-run input. A finding that answers "what triggers this?" can
# be tagged from its own answer instead of from marker archaeology. Accepts the
# three field spellings a schema change would plausibly use.
_EXPLICIT_FIELD_RE = re.compile(
    r"^\s*(?:#{0,4}\s*)?(?:\*\*)?"
    r"(?P<key>REACHABILITY|TRIGGER|LATENT)"
    r"(?:\*\*)?\s*[:=]\s*(?P<val>.+?)\s*$",
    re.IGNORECASE | re.MULTILINE,
)

# Values on those fields that assert the defect is NOT reachable in the contract.
_EXPLICIT_LATENT_VALUES = re.compile(
    r"\b(?:latent|unreachable|not reachable|no (?:\w+[- ]){0,3}"
    r"(?:caller|call site|consumer)s?|"
    r"future[- ]only|hypothetical|shadow|dormant|dead code|"
    r"non[- ]default (?:config|configuration))\b",
    re.IGNORECASE,
)
# "reachable" phrasing. Two traps, both found by test:
#   * bare "no"/"false" must be the WHOLE value — otherwise "no in-repo caller"
#     (a latency claim) is read as the boolean "no";
#   * "default configuration" must not match inside "non-default configuration",
#     which is the exact opposite claim. The hyphen is a word boundary, so a
#     plain \bdefault\b matches the negation too.
_EXPLICIT_REACHABLE_VALUES = re.compile(
    r"\b(?:reachable|live|real path|production|current caller|"
    r"(?<!non-)(?<!non )default (?:config|configuration|path))\b",
    re.IGNORECASE,
)
_WHOLE_VALUE_BOOL_LATENT = re.compile(r"^\s*(?:true|yes|latent)\s*\.?\s*$",
                                      re.IGNORECASE)
_WHOLE_VALUE_BOOL_REACHABLE = re.compile(r"^\s*(?:false|no|none|n/?a)\s*\.?\s*$",
                                         re.IGNORECASE)


def _explicit_field(text: str) -> Optional[Tuple[bool, str]]:
    """Read a panel-emitted reachability field. None when absent."""
    for m in _EXPLICIT_FIELD_RE.finditer(text):
        key = m.group("key").upper()
        val = m.group("val").strip()
        if not val:
            continue
        # Bare booleans first, and only when they are the entire value.
        if _WHOLE_VALUE_BOOL_REACHABLE.match(val):
            return (False, f"{key}: {val[:120]}")
        if _WHOLE_VALUE_BOOL_LATENT.match(val):
            return (True, f"{key}: {val[:120]}")
        # Then prose. An affirmative latency phrase wins over an incidental
        # "reachable" mention, since latency phrasing is the more specific claim.
        if _EXPLICIT_LATENT_VALUES.search(val):
            return (True, f"{key}: {val[:120]}")
        if _EXPLICIT_REACHABLE_VALUES.search(val):
            return (False, f"{key}: {val[:120]}")
    return None


# ── Source 2: explicit prose claim of unreachability ───────────────────────
# Narrow by construction. Every pattern here is an assertion that the defect
# cannot be reached through the artefact's intended use. Phrases that merely
# describe a conditional code path ("only if x is None") are EXCLUDED: they are
# how any defect is described, they dominate the corpus, and they say nothing
# about whether a caller supplies that condition.
#
# EXCLUDED, after auditing what they actually matched on the 293-finding corpus:
#   "unreachable" / "not reachable" / "never reached|invoked|called|executed"
#   and "dead code" / "vestigial" / "orphaned code".
# Every one of these is ambiguous in its referent. A finding that says "the
# severe penalty tier is never reached" is reporting dead code AS THE BUG — the
# branch was supposed to fire and does not — which is the opposite of a latency
# claim, and it is the more common usage. Exp 47 C0024 (severity 0.75, falsifier
# CONFIRMED, "silently wrong results; the severe penalty tier is never reached")
# was demoted on exactly that misreading before these were removed. Prose cannot
# be relied on to disambiguate "this code is never reached, which is the defect"
# from "this code is never reached, so the defect does not matter". Recall is
# given up to keep the demotion decision sound.
_LATENCY_MARKERS: Tuple[Tuple[str, str], ...] = (
    ("cannot_trigger", r"\bcannot be (?:reached|triggered|invoked|hit) "
                       r"(?:by|from|through)\b|\bno code path (?:can |could )?"
                       r"(?:reach|trigger)\b"),
    ("no_caller", r"\bno (?:current |in-?repo |live |real |production )?"
                  r"(?:caller|call site|consumer|invocation)s?\b"),
    ("shadow_path", r"\b(?:shadow[/ -]?(?:only|observation)|observation[- ]only|"
                    r"telemetry[- ]only|shadow instrumentation|"
                    r"never gates?|not load[- ]bearing|"
                    r"(?:zero|no) effect on the (?:load[- ]bearing |verdict )?path)\b"),
    ("future_only", r"\b(?:only a future|if a future|should a future|"
                    r"were a (?:future )?caller to|future[- ]only)\b"),
    ("non_default", r"\bnon[- ]default (?:config\w*|option|mode|flag)\b"),
    ("explicit_latent", r"\b(?:is|are|remains?) latent\b|\blatent (?:defect|bug|"
                        r"issue|finding)\b"),
)

# The falsifier idiom "prints FALSIFIED / fails / exits ... only if the defect is
# present" is boilerplate describing the TEST, not the defect's trigger. It is
# the dominant false positive for any conditional-language matcher and is
# excluded explicitly. (Measured: 3 of the 4 corpus-wide conditional hits.)
_TEST_BOILERPLATE_RE = re.compile(
    r"\b(?:fail|fails|failing|exit|exits|print|prints|raise|raises|assert\w*)\b"
    r"[^.]{0,60}\bonly if\b|\bif and only if\b",
    re.IGNORECASE,
)


def _prose_latency(text: str) -> Optional[Tuple[bool, str]]:
    """Match an explicit prose claim of unreachability. None when absent."""
    scrubbed = _TEST_BOILERPLATE_RE.sub(" ", text)
    for name, pattern in _LATENCY_MARKERS:
        m = re.search(pattern, scrubbed, re.IGNORECASE)
        if m:
            start = max(0, m.start() - 60)
            snippet = scrubbed[start:m.end() + 60].replace("\n", " ").strip()
            return (True, f"{name}: ...{snippet}...")
    return None


# ── Public API ─────────────────────────────────────────────────────────────

# A fenced block is QUOTED MATERIAL — target source, a prior finding's header, a
# proposed patch. Its words are not the finding's own claim about reachability.
_FENCED_BLOCK_RE = re.compile(r"```.*?(?:```|\Z)", re.DOTALL)

# What replaces a stripped fence, and it is NOT a bare space. ADVERSARIAL PASS,
# 2026-08-12: substituting " " lets the strip FUSE the two fragments either side
# of the fence into a marker match the raw text never contained — every marker
# pattern joins its words with a single literal space, so a single space is
# exactly the character needed to manufacture one. Measured counter-examples,
# both of which raw text does NOT match and a space-substituted strip DOES:
#   "There is no in-repo```x```caller guard missing here."  -> no_caller
#   "Marked observation```z```only in the header."          -> shadow_path
# That is a MANUFACTURED FALSE LATENT — the one failure this subsystem must
# never cause — and it refuted this function's own "can only REMOVE" claim.
# A newline would be worse, not better: ``_EXPLICIT_FIELD_RE`` is MULTILINE and
# anchored at ``^``, so a newline sentinel would let a stripped fence CREATE a
# line start and hand the designed source a field it never had. The placeholder
# must therefore contain a non-space, non-newline character. It also reads
# clearly in ``latent_evidence`` when a match lands beside one.
_QUOTED_PLACEHOLDER = " [quoted] "


def _category_text(entry: Dict[str, Any]) -> str:
    """The WIDEST text the consequence classifier may read.

    Deliberately wide, and deliberately wider than ``_latency_text``: the
    classifier is a safety interlock, so a false "this is a data-loss finding"
    costs one retained critical while a false "this is cosmetic" costs a demoted
    real one. Reading the proposed fix as well as the description can only ADD
    vetoes, never remove one.
    """
    return "\n".join(
        str(entry.get(k) or "") for k in ("description", "proposed_fix")
    )


def _latency_text(entry: Dict[str, Any]) -> str:
    """The NARROW text a reachability judgement may legitimately be read from.

    THE RULE, which is the module's existing ``falsifier_code`` rule applied
    consistently: a latency tag may be read only from text the finding ASSERTS,
    never from text the finding QUOTES. Three exclusions follow from it.

      * ``falsifier_code`` — a test program; inferring reachability from it was
        measured and REFUTED (see module docstring).
      * ``proposed_fix`` — a SEARCH/REPLACE patch by construction, so it carries
        the TARGET's own comments verbatim, and the registry caps it at 5000
        bytes against the description's 500, so it dominated what was read.
        MEASURED, 2026-08-12: Exp 40 `slice_records` C0020 and C0048 were both
        tagged latent on the target file's comment "observation-only collision
        detection", quoted inside their patch bodies, while each finding's own
        description says the opposite ("silently drops duplicate findings ...
        misrouted or lost"). CORRECTED 2026-08-12 (adversarial pass): the
        earlier note here said the data-loss interlock was all that kept them.
        It was not, and the correction matters because it names which gate did
        the work — both carry ``falsifier_verdict`` empty, so
        ``_is_demotion_eligible`` refuses at condition (2) and never reaches the
        category at all. Clearing ``finding_category`` leaves them ineligible;
        setting ``falsifier_verdict="CONFIRMED"`` with the category cleared makes
        them eligible. Under the modern falsifier-CONFIRMED regime the category
        would indeed be the only thing left. The identical argument that
        excluded ``falsifier_code`` excludes this.
      * fenced code blocks inside the description — same contamination, same
        reason. A description that quotes an obsolete ``REACHABILITY:`` header
        in order to REFUTE it was read as asserting it.

    Category classification is unaffected: it reads ``_category_text``, so no
    never-demote veto is lost.

    NARROWING IS ONLY FAIL-SAFE IF THE STRIP CANNOT FUSE, which the first
    version of this function got wrong — see ``_QUOTED_PLACEHOLDER``. With a
    non-space placeholder the removal of text can only reduce matches, so the
    latent set after this function is a subset of the set before it, on the
    archive (asserted in ``test_latent_tagger_evaluation.py``) and by
    construction (asserted there too, by probe).
    """
    return _FENCED_BLOCK_RE.sub(
        _QUOTED_PLACEHOLDER, str(entry.get("description") or ""))


def tag_entry(entry: Dict[str, Any]) -> bool:
    """Tag one registry entry in place with ``latent`` and ``finding_category``.

    Sets, always:
      * ``finding_category`` — consequence class ("" when unclassified);
      * ``latent`` — True only on explicit evidence of unreachability;
      * ``latent_source`` — which evidence source decided ("explicit_field",
        "prose", or "default_reachable");
      * ``latent_evidence`` — the matched text, so any demotion is auditable.

    Returns True iff the entry was tagged latent. Idempotent: re-tagging an
    entry that already carries an externally-supplied ``latent`` flag leaves
    that flag alone (an upstream adjudication outranks this classifier).
    """
    entry.setdefault("finding_category", classify_category(_category_text(entry)))
    text = _latency_text(entry)

    if "latent" in entry and entry.get("latent_source") is None:
        # Externally adjudicated (HIL, or a future classifier cell). Respect it.
        entry["latent_source"] = "external"
        entry.setdefault("latent_evidence", "")
        return bool(entry.get("latent"))

    verdict = _explicit_field(text)
    source = "explicit_field"
    if verdict is None:
        verdict = _prose_latency(text)
        source = "prose"
    if verdict is None:
        verdict, source = (False, ""), "default_reachable"

    is_latent, evidence = verdict
    entry["latent"] = bool(is_latent)
    entry["latent_source"] = source
    entry["latent_evidence"] = evidence
    return bool(is_latent)


def tag_registry(registry: Any, skip_statuses: Iterable[str] = ()) -> int:
    """Tag every entry of a FindingRegistry. Returns the count tagged latent.

    ``skip_statuses`` is supplied by the caller. NOTE, corrected 2026-08-12: the
    runner's call site passes ``{MERGED, CLOSED, DUPLICATE}`` while
    ``_apply_severity_calibration`` additionally skips ``REFUTED``, so this does
    NOT sweep the identical population the calibrator does — the earlier claim
    that it "mirrors" that skip was wrong. It is currently harmless in both
    directions: a REFUTED entry tagged here can never be demoted, because the
    calibrator skips it AND ``_is_demotion_eligible`` requires
    ``falsifier_verdict == "CONFIRMED"``. Measured over all 28 archived runs
    (2247 findings): zero entries carry ``status == "REFUTED"`` with
    ``falsifier_verdict == "CONFIRMED"``, so the divergence is unreachable on
    the record. Adding ``REFUTED`` at the runner call site would close it by
    construction rather than by that coincidence.
    """
    skip = set(skip_statuses)
    entries = getattr(registry, "entries", registry)
    if not isinstance(entries, dict):
        return 0
    n = 0
    for entry in entries.values():
        if entry.get("status") in skip:
            continue
        if tag_entry(entry):
            n += 1
    return n
