#!/usr/bin/env python3
"""A SELF-LOCATING envelope for finding fields — the delimiter is never content.

WHY THIS EXISTS. Parser defects have recurred through this project's whole life,
and the founder's ruling on 2026-10-04 was that the class be closed rather than
patched again: *"I don't recall using almost any major software package in the
past, and then being told it couldn't do what I asked it to do, 'because of a
parsing issue'... That is why we need a definitive fix to this issue for once and
for all."*

THE DIAGNOSIS THAT WAS HANDED TO THIS MODULE, and the part of it that did not
survive execution. The brief said the runner runs two regimes side by side --
sentinel-delimited payloads, "unambiguous by construction", and bare regexes over
free prose -- and that every fault in the record belongs to the second. The FAULT
DISTRIBUTION claim survives. The MECHANISM claim does not, and the difference is
what this module is shaped by.

Executed against the one implemented sentinel form, `_CORRECTED_COPY_RE` in
`bench/reference_runner_v3.py`, over 12 plausible shapes of the same content
(`scripts/field_envelope_measurement_2026-10-04.py`, section 1):

    canonical                            PARSE
    blank line between label and sentinel  FAIL
    `**<<<CDSFL_ORIGINAL>>>**`             FAIL
    payload starting on the sentinel line  FAIL
    one line of prose before the sentinel  FAIL
    sentinels with no `CORRECTED_COPY:` label  FAIL
    label and sentinel on one line         FAIL

6 of 12 fail. The TOKEN `<<<CDSFL_ORIGINAL>>>` cannot occur in prose by accident,
and that much of the brief is right. But the GRAMMAR built around it is a hybrid:
the pattern requires a bare-regex label line, `CORRECTED_COPY: <key>`, to sit
IMMEDIATELY above the sentinel with only horizontal whitespace between. So the
information that says *which finding this payload belongs to* lives OUTSIDE the
sentinel, in exactly the free prose the brief indicts -- and markdown bold around
the sentinel, the same decoration that broke `FINDING_ID`, breaks it too.

SO THE PROPERTY THAT MATTERS IS NOT "SENTINEL VERSUS REGEX". It is two
properties, and the existing form has only the first:

  1. DISJOINT ALPHABET -- the delimiter is drawn from a token space the payload
     cannot enter by accident.
  2. SELF-LOCATING AND SELF-DESCRIBING -- the delimiter is found by a plain
     substring scan, and everything load-bearing (the field name, the owning
     finding id) sits INSIDE it. Nothing about the surrounding prose, indentation,
     decoration, line order or position is read.

An envelope with both properties cannot be confused with content, cannot be
mis-attributed by position, and cannot be broken by decoration, because no part
of the decision depends on anything outside the two tokens.

THE FORM.

    <<<CDSFL_FIELD field=SEVERITY id=F001>>>0.9<<<CDSFL_FIELD_END>>>

    <<<CDSFL_FIELD field=DESCRIPTION id=F001>>>
    the claim, over as many lines as it takes
    <<<CDSFL_FIELD_END>>>

WHAT EACH DOCUMENTED FAULT BECOMES UNDER IT.

  * `_extract_corroboration_sections` splits case-insensitively on the bare word
    and so fires on the JSON key `corroboration_fit` and on the prose "independent
    corroboration" -- 226 phantom sections on top of 109 real ones in one run,
    67.4627% of everything it reported. Under the envelope the word CORROBORATION
    is only a delimiter when it is the `field=` attribute of a sentinel, so a JSON
    key spelled `corroboration_fit` is payload, never a boundary.
  * `**FINDING_ID:**` was missed because of markdown bold. The envelope scan is an
    unanchored substring scan; `**` before the token is simply outside the match,
    and a scalar payload is stripped of `*`, `_` and backticks before it is read
    (the same normalisation `_parse_flaw_class` already applies).
  * `NOT FALSIFIED` once matched as containing `FALSIFIED`. A verdict payload here
    is COMPARED, not searched: `NOT FALSIFIED` is not equal to any of the 5
    keywords, so it is refused with a reason rather than silently inverted.
  * The 12-character anchor minimum is a POLICY on the corrected-copy mechanism,
    not a delimiting failure, and no envelope changes it. Named here so the claim
    "this closes every documented class" is not made: it closes 3 of 4.

WHAT THIS MODULE DELIBERATELY DOES NOT DO.

  * It never replaces a reader. `parse_findings`, `_parse_verdicts` and the
    corroboration readers keep every path they have; the envelope is consulted
    FIRST and the existing path runs underneath it. A seat that emits no envelope
    is parsed byte-identically to before -- measured over 326 archived seat
    replies at 326 of 326 identical
    (`scripts/field_envelope_measurement_2026-10-04.py`, section 3).
  * It never carries a nonce. The target sentinels do, and a nonce would also shut
    out a model that quotes the output format back at us. Threading one through
    every prompt builder is a change this repair does not need, so the echo hazard
    is handled by the two cheap guards that ARE wired -- a placeholder payload is
    refused, and a scalar that does not parse as a number is refused -- and is
    named below as the thing that would refute this design.

EVERY REFUSAL IS LOUD, which is the convention the corrected-copy section already
set: a refusal is counted with a NAMED reason and returned alongside the
accepted envelopes, so the runner can render it back to the seat. Nothing is
silently dropped, and nothing is half-read.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

#: The two tokens. `FIELD_END_TOKEN` begins with the same 14 characters as the
#: opener, so the opening pattern below requires either horizontal whitespace or
#: `>>>` immediately after `<<<CDSFL_FIELD` -- `_END` is neither, which is what
#: stops an end token being read as a header.
FIELD_BEGIN_PREFIX = "<<<CDSFL_FIELD"
FIELD_END_TOKEN = "<<<CDSFL_FIELD_END>>>"

_BEGIN_RE = re.compile(
    re.escape(FIELD_BEGIN_PREFIX)
    + r"(?:[ \t]+(?P<attrs>[^>\n]*?))?[ \t]*>>>"
)

#: `key=value`, value bare or quoted. A BARE value may not contain whitespace or
#: `>`, which is what keeps the header on one line and unambiguous: a parser that
#: allowed a space in a bare value would have to GUESS where the value ends, and
#: guessing is the failure this module exists to remove. A value that needs a
#: space is quoted -- `field="FLAW CLASS"` -- and `field=FLAW CLASS` is refused
#: with `unknown_field` naming what it read, `FLAW`, so a seat can see that its
#: value was cut at the space. Attribute ORDER and spacing around `=` are free.
#: Held by `test_the_header_is_read_whatever_order_or_spacing_it_uses` and
#: `test_a_space_in_an_UNQUOTED_value_is_refused_loudly`.
_ATTR_RE = re.compile(
    r"""(?P<key>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*"""
    r"""(?:"(?P<dq>[^"]*)"|'(?P<sq>[^']*)'|(?P<bare>[^\s>'"]+))""",
)

#: The attribute keys the grammar knows. Anything else is REFUSED rather than
#: ignored, so the form cannot drift by accretion the way the field regexes did.
_KNOWN_ATTRS = frozenset({"field", "id"})

#: Canonical field names, and the aliases observed in this project's own replies.
#: FIND and DESCRIPTION are the same slot (the 2026-07-27 Gemini repair), as are
#: FIX and PROPOSED_FIX (the CC2 habit the marker parser already allows for).
#: FALSIFIER is deliberately NOT an alias of FALSIFICATION: the former is a
#: separate mechanism carrying runnable code, extracted by `extract_falsifiers`.
CANONICAL_FIELDS = (
    "FINDING_ID",
    "SEVERITY",
    "FLAW_CLASS",
    "ABSTRACTION_INDEX",
    "DESCRIPTION",
    "PROPOSED_FIX",
    "TARGET_FILE",
    "VERIFIED",
    "FALSIFICATION",
    "CORROBORATION",
    "VERDICT",
    "VERDICT_EVIDENCE",
)

_FIELD_ALIASES = {
    "FIND": "DESCRIPTION",
    "FINDING": "DESCRIPTION",
    "DESC": "DESCRIPTION",
    "FIX": "PROPOSED_FIX",
    "FALSIFIED": "FALSIFICATION",
    "EVIDENCE": "VERDICT_EVIDENCE",
}

#: The five verdict keywords, compared for EQUALITY rather than searched for.
VERDICT_KEYWORDS = ("CONFIRM", "CHALLENGE", "EXTEND", "MERGE", "REOPEN")

#: A payload that is one angle-bracketed token with no newline is the placeholder
#: convention this project's own prompts use (`<the same id>`, `<0.0 to 1.0>`), so
#: it is a schema echo rather than a value. Refused with reason `placeholder`.
_PLACEHOLDER_RE = re.compile(r"^<[^<>\n]*>$")

#: THE ID THE PROMPT'S OWN EXAMPLE CARRIES, AND THE ONE ID THAT IS REFUSED.
#:
#: A prompt has to show the real syntax or a seat cannot comply, and a shown
#: syntax is a syntax a seat may echo verbatim. This project has measured that
#: hazard: the permissive `[A-Z][A-Z_ ]{2,20}:` verdict form promoted 8 of 12
#: adversarial constructions -- FORMAT:, EXAMPLE:, TEMPLATE:, OUTPUT: -- and the
#: note on it says plainly that *"this is precisely what a schema-echoing model
#: emits, and the directives teach the schema"*.
#:
#: The existing prompts already carry that exposure: `FINDING_FORMAT` shows
#: `FINDING_ID: F001` beside `SEVERITY: 0.0-1.0`, and a verbatim echo of those 2
#: lines mints an F001 at severity 0.0 through the marker arm today. Rather than
#: add a second route to the same place, the envelope's example carries an id
#: that the extractor refuses by name. The syntax is taught concretely, the
#: instruction says in terms that this id is refused, and an echoed template
#: produces a NAMED REFUSAL instead of a phantom finding.
EXAMPLE_ONLY_ID = "EXAMPLE_ONLY"

#: Decoration a scalar payload may be wrapped in. Mirrors `_parse_flaw_class`'s
#: own `.strip().strip("*").strip()` rather than inventing a second convention.
_SCALAR_DECORATION = " \t\r\n*_`\"'"

#: A finding id is the same single token the rest of the parser accepts
#: (`_VALID_FID_STRUCTURE` in runner_core), widened only by `-` and `.`, which
#: `_resolve_finding_key` already tolerates in a model-written key.
_OWNER_RE = re.compile(r"^[A-Za-z0-9_.\-]{1,64}$")


@dataclass(frozen=True)
class FieldEnvelope:
    """One accepted envelope. `payload` is the bytes between the two tokens."""

    field: str              #: canonical field name
    owner: str              #: the `id=` attribute, AS THE MODEL WROTE IT
    payload: str            #: verbatim, less one structural newline at each end
    raw_field: str          #: what the model actually spelled, before aliasing
    start: int              #: index of the opening token in the source text
    end: int                #: index just past the closing token


def _strip_one_structural_newline(body: str) -> str:
    """Make the inline and the block form yield the same payload.

    `>>>0.9<<<` and `>>>\\n0.9\\n<<<` must both be `0.9`, and a multi-line
    DESCRIPTION must keep its own internal blank lines untouched. So exactly ONE
    leading line break is removed, and exactly ONE trailing line break plus the
    horizontal whitespace that indented the closing token. Nothing else.
    """
    out = re.sub(r"^\r?\n", "", body, count=1)
    return re.sub(r"\r?\n[ \t]*\Z", "", out, count=1)


def _normalise_field(raw: str) -> str:
    key = re.sub(r"[\s\-]+", "_", (raw or "").strip().strip(_SCALAR_DECORATION))
    key = key.upper()
    return _FIELD_ALIASES.get(key, key)


def _parse_attrs(attrs: str) -> Tuple[Dict[str, str], List[str]]:
    """Return (attributes, unknown keys). Unknown keys are REFUSED by the caller."""
    found: Dict[str, str] = {}
    unknown: List[str] = []
    for m in _ATTR_RE.finditer(attrs or ""):
        key = m.group("key").lower()
        val = m.group("dq")
        if val is None:
            val = m.group("sq")
        if val is None:
            val = m.group("bare") or ""
        if key in _KNOWN_ATTRS:
            found.setdefault(key, val)
        else:
            unknown.append(key)
    return found, unknown


def extract_field_envelopes(
    text: str,
) -> Tuple[List[FieldEnvelope], List[Dict[str, object]]]:
    """Pull every well-formed field envelope out of one model reply.

    Returns ``(accepted, refusals)``. Pure text: nothing is executed, nothing is
    stored, nothing is scored. First `(owner, field)` wins, mirroring
    `extract_falsifiers` and `_extract_corrected_copies`; a later repeat is
    refused with reason ``duplicate`` rather than overwriting, so a seat that
    re-emits a field cannot change what was already read.

    Refusal reasons, all of them named so a seat can be told what went wrong:
    ``no_id``, ``bad_id``, ``example_id``, ``no_field``, ``unknown_field``,
    ``unknown_attribute``, ``unterminated``, ``nested_begin``, ``empty``,
    ``placeholder``, ``duplicate``.
    """
    accepted: List[FieldEnvelope] = []
    refusals: List[Dict[str, object]] = []
    if not text or FIELD_BEGIN_PREFIX not in text:
        return accepted, refusals

    seen: set = set()
    cursor = 0
    while True:
        m = _BEGIN_RE.search(text, cursor)
        if m is None:
            break
        header_end = m.end()
        end_at = text.find(FIELD_END_TOKEN, header_end)
        nxt = _BEGIN_RE.search(text, header_end)

        def _refuse(reason: str, **extra: object) -> None:
            row: Dict[str, object] = {
                "reason": reason,
                "at": m.start(),
                "header": text[m.start():header_end][:200],
            }
            row.update(extra)
            refusals.append(row)

        if end_at < 0:
            # A header with no terminator anywhere. Stop rather than reach past
            # the whole remaining reply: an unbounded payload is exactly the
            # truncation-shaped failure this project refuses to ship.
            _refuse("unterminated")
            cursor = header_end
            continue
        if nxt is not None and nxt.start() < end_at:
            # The seat opened a second envelope before closing this one, so this
            # header's terminator is missing. Refuse the OUTER and resume at the
            # inner one, which is probably well formed -- recovering rather than
            # discarding both.
            _refuse("nested_begin")
            cursor = nxt.start()
            continue

        attrs, unknown = _parse_attrs(m.group("attrs") or "")
        if unknown:
            _refuse("unknown_attribute", keys=sorted(set(unknown)))
            cursor = end_at + len(FIELD_END_TOKEN)
            continue

        raw_field = attrs.get("field", "")
        owner = (attrs.get("id") or "").strip().strip(_SCALAR_DECORATION)
        field = _normalise_field(raw_field)
        body = _strip_one_structural_newline(text[header_end:end_at])

        if not raw_field.strip():
            _refuse("no_field")
        elif field not in CANONICAL_FIELDS:
            _refuse("unknown_field", field=field)
        elif not owner:
            # THE OWNER IS MANDATORY, and this is the whole point of the design.
            # `_extract_corroboration_sections_with_ids` has to guess the owner
            # from "the nearest FINDING_ID preceding the header", and
            # `validate_round_rk` had to pair BY POSITION before 2026-10-03 --
            # which stamped a finding SKIP for a proof the parser would have
            # passed, and, in the other direction, validated finding i's claimed
            # R_k against finding j's parameters. An envelope with no owner would
            # reintroduce exactly that guess, so it is refused instead.
            _refuse("no_id")
        elif not _OWNER_RE.match(owner):
            _refuse("bad_id", id=owner[:80])
        elif owner.upper() == EXAMPLE_ONLY_ID:
            # The prompt's own example. See `EXAMPLE_ONLY_ID`.
            _refuse("example_id", field=field)
        elif not body.strip():
            _refuse("empty", field=field, id=owner)
        elif _PLACEHOLDER_RE.match(body.strip()):
            _refuse("placeholder", field=field, id=owner,
                    payload=body.strip()[:80])
        elif (owner.lower(), field) in seen:
            _refuse("duplicate", field=field, id=owner)
        else:
            seen.add((owner.lower(), field))
            accepted.append(FieldEnvelope(
                field=field, owner=owner, payload=body, raw_field=raw_field,
                start=m.start(), end=end_at + len(FIELD_END_TOKEN),
            ))
        cursor = end_at + len(FIELD_END_TOKEN)

    return accepted, refusals


def fields_by_owner(text: str) -> Dict[str, Dict[str, str]]:
    """``{owner_id: {canonical_field: payload}}`` for one reply, in document order.

    The convenience shape the finding builder wants. Refusals are dropped here
    BY DESIGN -- a caller that needs them calls `extract_field_envelopes`, and
    `envelope_telemetry` counts them -- so that no consumer of this shape can
    mistake a refused envelope for a read one.
    """
    out: Dict[str, Dict[str, str]] = {}
    for env in extract_field_envelopes(text)[0]:
        out.setdefault(env.owner, {})[env.field] = env.payload
    return out


def envelope_verdicts(text: str) -> List[Tuple[str, str, str]]:
    """``[(keyword, canonical_id, evidence)]`` from VERDICT envelopes only.

    The keyword is COMPARED FOR EQUALITY against the 5 keywords after decoration
    is stripped, which is what makes `NOT FALSIFIED`-shaped payloads impossible to
    read as a verdict: the 2026 defect in which a verdict reader matched
    `NOT FALSIFIED` as *containing* `FALSIFIED` cannot recur through this path.

    The target must be a canonical registry id (`C` plus at least 4 digits),
    because that is what every verdict consumer resolves. A verdict on anything
    else is not returned.
    """
    return verdicts_from_fields(fields_by_owner(text))


def verdicts_from_fields(
    by_owner: Dict[str, Dict[str, str]],
) -> List[Tuple[str, str, str]]:
    """`envelope_verdicts` over an ALREADY-EXTRACTED field map.

    ONE IMPLEMENTATION, 2 ENTRY POINTS, because a caller that already holds the
    map should not scan the text again. Two scans of one reply are 2
    representations of 1 truth with no comparator -- the shape
    `execute-do-not-grep` names -- and they could drift apart the moment either
    is touched. `envelope_verdicts` is now a 1-line wrapper over this.
    """
    out: List[Tuple[str, str, str]] = []
    for owner, fields in by_owner.items():
        kw = (fields.get("VERDICT") or "").strip().strip(_SCALAR_DECORATION)
        if kw.upper() not in VERDICT_KEYWORDS:
            continue
        if not re.fullmatch(r"C\d{4,}", owner.upper()):
            continue
        evidence = (fields.get("VERDICT_EVIDENCE") or "").strip()
        out.append((kw.upper(), owner.upper(), evidence))
    return out


def scalar(payload: Optional[str]) -> str:
    """A scalar payload with decoration removed. `**0.9**` reads as `0.9`."""
    return (payload or "").strip().strip(_SCALAR_DECORATION).strip()


def envelope_telemetry(text: str) -> Dict[str, object]:
    """What the envelope reader SAW against what it ACCEPTED, for one reply.

    The same shape and the same discipline as `falsifier_intake_telemetry`: a
    recovery rate needs a denominator, and a reader that keeps no record of what
    it passed over cannot be studied by a run. PURE TEXT AND IT DECIDES NOTHING.
    No gate reads it and no status turns on it.

    Called on EVERY reply by `_note_intake`, including the ones carrying no
    envelope, because ADOPTION is the quantity of interest and a reply with 0
    envelopes is a real observation of it. The zero case short-circuits on a
    substring test rather than 3 regex scans, so the denominator costs nothing.
    """
    if FIELD_BEGIN_PREFIX not in (text or ""):
        return {
            "headers_seen": 0, "end_tokens_seen": 0, "accepted": 0,
            "refused": 0, "refusals_by_reason": {}, "owners": 0,
            "fields_accepted": [], "acceptance_rate_over_headers": None,
            "_decides_nothing": True,
        }
    raw_opens = len(_BEGIN_RE.findall(text or ""))
    accepted, refusals = extract_field_envelopes(text or "")
    reasons: Dict[str, int] = {}
    for r in refusals:
        key = str(r.get("reason"))
        reasons[key] = reasons.get(key, 0) + 1
    owners = {e.owner for e in accepted}
    return {
        "headers_seen": raw_opens,
        "end_tokens_seen": (text or "").count(FIELD_END_TOKEN),
        "accepted": len(accepted),
        "refused": len(refusals),
        "refusals_by_reason": reasons,
        "owners": len(owners),
        "fields_accepted": sorted({e.field for e in accepted}),
        "acceptance_rate_over_headers": (
            len(accepted) / raw_opens if raw_opens else None),
        "_decides_nothing": True,
    }


def envelope_instructions(indent: str = "") -> str:
    """The literal response form, rendered identically in every prompt.

    ONE STRING, EVERY CALL SITE, for the reason `_corrected_copy_instructions`
    already records: a convention rendered separately in the round directive, the
    routing prompt and the sweep prompt is a convention that drifts apart, which
    is how the sweep prompt and the routing prompt came to disagree about prose
    targets on 2026-08-01.
    """
    i = indent
    e = EXAMPLE_ONLY_ID
    return (
        f"{i}{FIELD_BEGIN_PREFIX} field=SEVERITY id={e}>>>0.9{FIELD_END_TOKEN}\n"
        f"{i}{FIELD_BEGIN_PREFIX} field=DESCRIPTION id={e}>>>\n"
        f"{i}the claim, over as many lines as it takes\n"
        f"{i}{FIELD_END_TOKEN}\n"
    )


#: KEPT SHORT BECAUSE THE BUDGET IS REAL. Measured 2026-10-04: the first draft of
#: this paragraph plus the example came to 1,497 characters, which is 4.99% of
#: the TIGHTEST per-model prompt budget in `CONTEXT_CHAR_BUDGET` (CC2, 30,000) --
#: a prompt addition that displaces target content is not free, and this project
#: decomposes a prompt rather than let it overflow. Trimmed to the instruction a
#: seat needs and nothing more. The field list stays, long as it is, because
#: `bench/tests/test_field_envelope_2026-10-04.py` executes every name in it
#: against the parser: a list that drifted from what the parser accepts would
#: advertise a field that is silently refused.
ENVELOPE_WHY = (
    "OPTIONAL, PREFERRED, and free to use. Wrap any field of any finding and it "
    "is read EXACTLY as written -- located by the sentinel alone, never guessed "
    "from headings, indentation, bold, position or surrounding prose. A reply "
    "with no envelope is parsed as it is today, so plain fields cost you "
    "nothing. `id=` is MANDATORY and names the finding; `field=` must be one of "
    + ", ".join(CANONICAL_FIELDS)
    + "; everything between the sentinels is the value, verbatim. Wrap "
    "CORROBORATION and FALSIFICATION above all: both are words that also occur "
    "in sentences and as keys in data structures, so a heading cannot always be "
    "told from a mention. Replace " + EXAMPLE_ONLY_ID + " with your real id -- "
    "that literal word is REFUSED, so copying the template files nothing."
)


def envelope_instruction_block(indent: str = "") -> str:
    """The prompt paragraph: why, then the form. The only text prompts embed."""
    return (
        f"{indent}UNAMBIGUOUS FIELD ENVELOPE ({ENVELOPE_WHY})\n"
        + envelope_instructions(indent + "  ")
    )


def verdict_envelope_instructions(indent: str = "") -> str:
    """The verdict form, which carries its target in the sentinel."""
    i = indent
    e = EXAMPLE_ONLY_ID
    return (
        f"{i}{FIELD_BEGIN_PREFIX} field=VERDICT id={e}>>>CONFIRM"
        f"{FIELD_END_TOKEN}\n"
        f"{i}{FIELD_BEGIN_PREFIX} field=VERDICT_EVIDENCE id={e}>>>\n"
        f"{i}what you checked and what it showed\n"
        f"{i}{FIELD_END_TOKEN}\n"
    )

