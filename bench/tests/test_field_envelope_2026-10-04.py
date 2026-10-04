"""The field envelope, EXECUTED against the readers it layers over.

WHAT THIS FILE IS FOR. `bench/field_envelope.py` adds a self-locating envelope for
finding fields: the field name and the owning finding id live INSIDE the sentinel,
so nothing about the surrounding prose, indentation, decoration, position or line
order is read. This file holds 2 claims, and every assertion in it CALLS both
forms rather than reading either -- `execute-do-not-grep`, which this project's
record credits with 4 defects that reading found none of.

CLAIM 1, THE ENVELOPE IS BETTER WHERE IT MATTERS. Not asserted, demonstrated at
the deciding layer: `TestTheDecidingLayer` builds 1 sound proof and 1 broken one
and runs the real `validate_round_rk`. Without an envelope the 2 verdicts come
back INVERTED -- the sound proof FAIL, the broken one PASS -- and with an
envelope both are right. That is the 2026-10-03 pairing defect, still reachable
through a shape neither prose reader can own.

CLAIM 2, A SEAT THAT IGNORES IT LOSES NOTHING. `TestTheArchiveIsUnchanged` runs
`parse_findings` and the pre-envelope pipeline over every archived seat reply in
the repository and requires them to be identical, field by field. None of those
replies carries an envelope, which is the point: the overlay must be invisible
until a seat uses it.

THE MUTATION CHECK IS PART OF THE DELIVERY, not an afterthought. Reverting
`_apply_field_envelopes` to `return findings`, and `_corroboration_sections_by_owner`
to the prose-only map, must turn assertions in here RED. A test that still passes
with the fix reverted proves nothing, and the result of running it both ways is
recorded in the session note that accompanies this file.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
for _p in (str(REPO), str(REPO / "bench")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import field_envelope as fe                                    # noqa: E402
import reference_runner_v3 as R                                # noqa: E402
import runner_core as rc                                       # noqa: E402
from dynamic_management import Finding                         # noqa: E402
from run_exp17_immune import FINDING_FORMAT                    # noqa: E402

BEG = fe.FIELD_BEGIN_PREFIX
END = fe.FIELD_END_TOKEN

#: 2 proof blocks whose recomputed R_k differ by 0.27, so a mis-pairing cannot
#: hide inside the 0.05 WARN band. Values taken from `_validate_rk_computation`
#: itself rather than typed: A recomputes to 0.5106370192307692 and B to
#: 0.2370437601296596.
PROOF_A = "R_old=0.50, eta=0.80, d=0.70, p=0.60, S_k=0.75, nu_eff=0.15"
PROOF_B = "R_old=0.20, eta=0.40, d=0.40, p=0.40, S_k=0.30, nu_eff=0.05"
A_SOUND = f"{PROOF_A}; R_k = 0.5106"
B_BROKEN = f"{PROOF_B}; R_k = 0.9900"


def _finding(fid: str, **kw) -> Finding:
    base = dict(finding_id=fid, model_id="Seat", round_idx=1, flaw_class=1,
                severity=0.9, abstraction_index=0.5, description="x")
    base.update(kw)
    return Finding(**base)


def _pre_envelope_pipeline(model_id: str, round_idx: int, response: str):
    """The parser EXACTLY as it stood before the overlay existed.

    Not a reconstruction from memory: it is the body of `parse_findings` with the
    one new line removed, calling the same 3 live functions. That is what makes
    `TestTheArchiveIsUnchanged` a comparison of 2 executing forms rather than an
    assertion about one.
    """
    text = rc._normalise_field_labels(response)
    return rc._attach_falsifiers(rc._parse_findings_core(model_id, round_idx, text),
                                 text)


def _load_measurement():
    """The producing script, loaded as a module.

    `measured-rate-travels-with-its-script` requires the script beside the
    number; this is the other half -- the guard RE-RUNS it, so a figure cannot
    become a remembered figure. It also supplies the ONE definition of the
    corpus, so the script and this file cannot come to disagree about what
    "every archived reply" means.
    """
    import importlib.util
    path = REPO / "scripts" / "field_envelope_measurement_2026-10-04.py"
    spec = importlib.util.spec_from_file_location("fe_measure", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


MEASURE = _load_measurement()
_seat_replies = MEASURE.seat_replies


# ─────────────────────────────────────────────────────────────────────────────
class TestTheGrammarCannotBeBrokenByDecoration:
    """The 6 shapes that break the existing sentinel form, re-run here.

    `_CORRECTED_COPY_RE` is the project's one implemented sentinel reader and the
    brief called it "unambiguous by construction". Measured over 12 shapes of the
    same content, 6 fail -- because its grammar is a HYBRID: the sentinel must sit
    immediately below a bare-regex `CORRECTED_COPY: <key>` label with only
    horizontal whitespace between. The owner therefore lives OUTSIDE the sentinel,
    in exactly the free prose the brief indicts. These tests fix the envelope's
    behaviour on the same 6 shapes.
    """

    @pytest.mark.parametrize("name,text", [
        ("inline", f"{BEG} field=SEVERITY id=F001>>>0.9{END}"),
        ("block", f"{BEG} field=SEVERITY id=F001>>>\n0.9\n{END}"),
        ("bold wrapped", f"**{BEG} field=SEVERITY id=F001>>>**0.9**{END}**"),
        ("blockquote and bullet", f"> - {BEG} field=SEVERITY id=F001>>>0.9{END}"),
        ("indented", f"    {BEG} field=SEVERITY id=F001>>>\n    0.9\n    {END}"),
        ("crlf", f"{BEG} field=SEVERITY id=F001>>>\r\n0.9\r\n{END}"),
        ("quoted attributes", f'{BEG} field="SEVERITY" id="F001">>>0.9{END}'),
        ("prose above", f"Here is the severity.\n{BEG} field=SEVERITY id=F001>>>0.9{END}"),
        ("blank line above", f"anything\n\n{BEG} field=SEVERITY id=F001>>>0.9{END}"),
        ("inside a fence", f"```\n{BEG} field=SEVERITY id=F001>>>0.9{END}\n```"),
    ])
    def test_every_shape_reads_the_same_value(self, name, text):
        accepted, refusals = fe.extract_field_envelopes(text)
        assert len(accepted) == 1, (
            f"shape {name!r} did not yield exactly 1 envelope; "
            f"refusals={[r['reason'] for r in refusals]}")
        env = accepted[0]
        assert (env.field, env.owner) == ("SEVERITY", "F001")
        assert fe.scalar(env.payload) == "0.9", (
            f"shape {name!r} read {env.payload!r}, not 0.9 -- a delimiter that "
            f"survives decoration must also hand back the value undecorated")

    def test_the_existing_sentinel_form_really_does_fail_on_some_of_them(self):
        """The control. Without this the comparison above has nothing to beat.

        If a later repair makes `_CORRECTED_COPY_RE` decoration-tolerant, this
        test goes red and should be retired WITH that repair named -- which is
        the point: the claim is dated and re-derived, not remembered.
        """
        orig, corr, fin = (R._CORRECTED_ORIGINAL_SENTINEL,
                           R._CORRECTED_CORRECTED_SENTINEL,
                           R._CORRECTED_END_SENTINEL)
        canonical = f"CORRECTED_COPY: C0007\n{orig}\nthe passage here\n{corr}\nthe passage there\n{fin}\n"
        assert R._extract_corrected_copies(canonical), (
            "the canonical corrected-copy form must still parse; if this fails "
            "the comparison below is measuring a broken fixture, not a defect")
        broken = {
            "blank line between label and sentinel":
                f"CORRECTED_COPY: C0007\n\n{orig}\nthe passage here\n{corr}\nthe passage there\n{fin}\n",
            "markdown bold around the sentinel":
                f"CORRECTED_COPY: C0007\n**{orig}**\nthe passage here\n{corr}\nthe passage there\n{fin}\n",
            "payload on the sentinel's own line":
                f"CORRECTED_COPY: C0007\n{orig} the passage here\n{corr}\nthe passage there\n{fin}\n",
            "one line of prose before the sentinel":
                f"CORRECTED_COPY: C0007\nHere it is:\n{orig}\nthe passage here\n{corr}\nthe passage there\n{fin}\n",
            "no label at all":
                f"{orig}\nthe passage here\n{corr}\nthe passage there\n{fin}\n",
        }
        still_broken = {k for k, v in broken.items()
                        if not R._extract_corrected_copies(v)}
        assert len(still_broken) == 5, (
            f"expected all 5 shapes to fail the hybrid sentinel grammar; "
            f"these parsed after all: {sorted(set(broken) - still_broken)}")


# ─────────────────────────────────────────────────────────────────────────────
class TestTheDecidingLayer:
    """`validate_round_rk` is where a mis-read proof changes a recorded verdict.

    `feedback_verify_the_deciding_layer`: 4 failures in 1 night came from tests
    that checked a helper and not the layer that decides. So these call the real
    `validate_round_rk` with real `Finding` objects.
    """

    #: ChatGPT emits findings as a JSON array -- the parser carries a whole arm
    #: for it. In that shape the CORROBORATION value is a JSON string, so neither
    #: prose reader can own it: the frozen reader splits on the bare word and
    #: hands back fragments beginning `": "`, and the owner-aware reader requires
    #: a line-anchored header and returns nothing at all. Pairing therefore falls
    #: back to POSITION, and here the 2 objects are in the opposite order to the
    #: findings.
    JSON_REVERSED = (
        '[{"FINDING_ID": "F002", "SEVERITY": 0.4, "DESCRIPTION": "second",\n'
        f'   "CORROBORATION": "{B_BROKEN}"}},\n'
        '  {"FINDING_ID": "F001", "SEVERITY": 0.9, "DESCRIPTION": "first",\n'
        f'   "CORROBORATION": "{A_SOUND}"}}]\n'
    )

    def _rows(self, text):
        findings = [_finding("Seat_F001"), _finding("Seat_F002")]
        return {fid: (status, model_rk) for fid, status, model_rk, _rec
                in R.validate_round_rk(findings, {"Seat": text})["Seat"]}

    def test_without_an_envelope_the_two_verdicts_come_back_inverted(self):
        """The defect, reproduced. F001's proof is sound and F002's is broken."""
        rows = self._rows(self.JSON_REVERSED)
        assert rows["Seat_F001"][0] == "FAIL", (
            "F001's own proof recomputes to within 0.0005 of what it states, so "
            "a FAIL here is the positional fallback handing it F002's numbers")
        assert rows["Seat_F002"][0] == "PASS", (
            "F002 states R_k = 0.99 against parameters giving 0.237; a PASS here "
            "is the silent half of the defect -- a broken proof validated "
            "against someone else's arithmetic")

    def test_with_an_envelope_both_verdicts_are_right(self):
        text = self.JSON_REVERSED + (
            f"{BEG} field=CORROBORATION id=F002>>>{B_BROKEN}{END}\n"
            f"{BEG} field=CORROBORATION id=F001>>>{A_SOUND}{END}\n")
        rows = self._rows(text)
        assert rows["Seat_F001"] == ("PASS", 0.5106)
        assert rows["Seat_F002"][0] == "FAIL"
        assert rows["Seat_F002"][1] == 0.99

    def test_the_order_of_the_envelopes_does_not_matter(self):
        """Position is not consulted at all when the owner is declared."""
        text = self.JSON_REVERSED + (
            f"{BEG} field=CORROBORATION id=F001>>>{A_SOUND}{END}\n"
            f"{BEG} field=CORROBORATION id=F002>>>{B_BROKEN}{END}\n")
        assert self._rows(text)["Seat_F001"] == ("PASS", 0.5106)

    @pytest.mark.parametrize("name,reply", [
        ("bullet header",
         "FINDING_ID: F001\nSEVERITY: 0.9\nDESCRIPTION: x\n"
         f"- CORROBORATION: {A_SOUND}\n"),
        ("markdown table row",
         "FINDING_ID: F001\nSEVERITY: 0.9\nDESCRIPTION: x\n"
         f"| CORROBORATION | {A_SOUND} |\n"),
        ("proof stated before the id is declared",
         f"SEVERITY: 0.9\nCORROBORATION. {A_SOUND}\n"
         "FINDING_ID: F001\nDESCRIPTION: x\n"),
        ("json value",
         '[{"FINDING_ID": "F001", "SEVERITY": 0.9, "DESCRIPTION": "x",\n'
         f'   "CORROBORATION": "{A_SOUND}"}}]\n'),
    ])
    def test_four_real_shapes_the_prose_readers_cannot_own(self, name, reply):
        """Each is a shape a seat actually writes, and the owner is lost in all 4.

        The ASSERTION IS ON THE OWNER, not on the section count: the frozen
        reader does find a fragment in each case, which is precisely why the
        failure is silent -- something is returned and it belongs to nobody.
        """
        owned = R._extract_corroboration_sections_with_ids(reply)
        assert not [o for o, _s in owned if o], (
            f"{name}: the owner-aware prose reader claimed an owner after all; "
            f"the fixture no longer measures what it was built to measure")
        enveloped = reply + (
            f"{BEG} field=CORROBORATION id=F001>>>{A_SOUND}{END}\n")
        by_owner = R._corroboration_sections_by_owner(enveloped)
        assert "f001" in by_owner, f"{name}: the envelope did not recover the owner"
        assert by_owner["f001"][1] == "envelope"
        assert by_owner["f001"][0].strip() == A_SOUND


# ─────────────────────────────────────────────────────────────────────────────
class TestTheArchiveIsUnchanged:
    """A seat that never adopts the envelope must parse byte-identically.

    `A SUBSET IS NOT A BOARD` and `measured-rate-travels-with-its-script` both
    bear on this: the claim is over EVERY archived seat reply in the repository,
    and the proportion is produced by
    `scripts/field_envelope_measurement_2026-10-04.py`, not typed here.
    """

    FIELDS = ("finding_id", "severity", "flaw_class", "abstraction_index",
              "description", "proposed_fix", "target_file", "verified",
              "falsifier_code", "falsification_present")

    #: A FLOOR, NOT AN EQUALITY. `.gitignore` has dropped raw per-model replies
    #: since 2026-08-13, so the corpus is the runs that predate that rule plus
    #: the panel records: 4,808 reply files are tracked and a maintainer's tree
    #: carries more. 5,000 is comfortably under the tracked count and well over
    #: the 312 panel records alone, so this fails if either root stops
    #: contributing -- which is the failure mode a fresh clone produces, and the
    #: one that made task A2's "a fresh clone is green" untrue.
    CORPUS_FLOOR = 5000

    def test_the_corpus_is_not_empty(self):
        replies = _seat_replies()
        assert len(replies) >= self.CORPUS_FLOOR, (
            f"only {len(replies)} archived replies found, under the floor of "
            f"{self.CORPUS_FLOOR}; a no-regression claim shrinks silently when "
            f"its corpus does, and `bench/logs` is the root most likely to have "
            f"stopped contributing")

    def test_the_overlay_changes_nothing_on_any_archived_reply(self):
        """The FULL corpus, and it costs 0.09 s because of what it does not do.

        WHY THIS SHAPE. Running `parse_findings` against the pre-envelope
        pipeline over all 5,445 replies means TWO core parses of 57 MB, measured
        at 238 s -- past this suite's 300 s per-test backstop and roughly as long
        as the whole suite. The core parse is 118.9 s of that and the overlay is
        0.09 s, so the expensive part is code this repair did not touch.

        So this calls the overlay DIRECTLY on every real reply's text, with a
        known findings list, and requires it to hand that list back untouched.
        That is the property at issue -- the overlay must be invisible on text
        carrying no envelope -- executed over the whole board rather than argued
        from the early return. The end-to-end `parse_findings` comparison runs
        below over the panel root in full, and over the whole 5,445 in
        `scripts/field_envelope_measurement_2026-10-04.py` section 3, whose
        result the session note carries.

        NOT A CAPABILITY GUARD, and it says so: reverting the overlay to a no-op
        leaves this green by construction. The capability guards are
        `TestTheDecidingLayer` and `TestTheOverlayAddsAndNeverTakesAway`, and the
        mutation check is run against those.
        """
        probe = [_finding("Seat_F001", severity=0.42, description="untouched"),
                 _finding("Seat_F002", severity=0.77, description="also untouched")]
        changed = []
        for path, text in _seat_replies():
            out = rc._apply_field_envelopes("Seat", 1, text, list(probe))
            if len(out) != len(probe):
                changed.append((path, f"{len(probe)} -> {len(out)} findings"))
                continue
            for b, a in zip(probe, out):
                diffs = [f for f in self.FIELDS
                         if getattr(b, f, None) != getattr(a, f, None)]
                if diffs:
                    changed.append((path, f"{b.finding_id}: {diffs}"))
        assert not changed, (
            f"the overlay altered findings on {len(changed)} archived reply(s), "
            f"none of which carries an envelope:\n"
            + "\n".join(f"  {p}: {w}" for p, w in changed[:10])
            + (f"\n  ... and {len(changed) - 10} more not shown"
               if len(changed) > 10 else ""))

    def test_every_archived_PANEL_reply_parses_identically_end_to_end(self):
        """`parse_findings` against the pre-envelope pipeline, in full, over 1 root.

        312 panel seat replies, complete, no sampling. The same comparison over
        the run root is in the measurement script because of its cost, and the
        corpus each claim is over is named in the claim -- a figure whose
        denominator is left implicit is how `282 of 711` became irreproducible.
        """
        replies = [(p, t) for p, t in _seat_replies()
                   if "panel_records_" in p]
        assert len(replies) >= 300, f"panel root contributed only {len(replies)}"
        changed = []
        for path, text in replies:
            before = _pre_envelope_pipeline("Seat", 1, text)
            after = rc.parse_findings("Seat", 1, text)
            if len(before) != len(after):
                changed.append((path, f"{len(before)} -> {len(after)} findings"))
                continue
            for b, a in zip(before, after):
                diffs = [f for f in self.FIELDS
                         if getattr(b, f, None) != getattr(a, f, None)]
                if diffs:
                    changed.append((path, f"{b.finding_id}: {diffs}"))
        assert not changed, (
            f"{len(changed)} panel reply/findings changed under the overlay:\n"
            + "\n".join(f"  {p}: {w}" for p, w in changed[:10]))

    def test_no_archived_reply_carries_an_envelope(self):
        """Which is what makes the tests above no-regression tests and not ties."""
        carrying = [p for p, t in _seat_replies() if BEG in t]
        assert not carrying, (
            "an archived reply now carries an envelope, so the identity tests "
            f"above are no longer measuring the non-adopting case: {carrying[:5]}")


# ─────────────────────────────────────────────────────────────────────────────
class TestTheOverlayAddsAndNeverTakesAway:

    def test_an_enveloped_severity_wins_and_nothing_else_moves(self):
        reply = ("FINDING_ID: F001\nSEVERITY: 0.1\nFLAW_CLASS: 3\n"
                 "DESCRIPTION: the gate reads a stale label.\n"
                 "PROPOSED_FIX: read the live one.\n"
                 f"{BEG} field=SEVERITY id=F001>>>0.9{END}\n")
        plain = _pre_envelope_pipeline("Seat", 1, reply)
        out = rc.parse_findings("Seat", 1, reply)
        assert len(out) == len(plain) == 1
        assert plain[0].severity == 0.1 and out[0].severity == 0.9
        for field in ("description", "proposed_fix", "flaw_class",
                      "abstraction_index", "finding_id"):
            assert getattr(out[0], field) == getattr(plain[0], field), (
                f"the overlay changed {field}, which no envelope supplied")

    def test_a_bolded_envelope_survives_the_whole_pipeline(self):
        """Not just `extract_field_envelopes` -- `_normalise_field_labels` too.

        `_MD_LABEL` rewrites `**LABEL:**` into `LABEL: ` at line start, and the
        core parser then strips every `**` from its own working copy. Neither
        touches the envelope, but asserting that on the GRID alone would test the
        extractor in isolation and miss the normaliser entirely. Bold is the
        decoration that defeated the `FINDING_ID` pattern, so it is the one worth
        driving end to end.
        """
        reply = ("FINDING_ID: F001\nSEVERITY: 0.1\nDESCRIPTION: a claim.\n"
                 f"**{BEG} field=SEVERITY id=F001>>>**0.9**{END}**\n")
        out = rc.parse_findings("Seat", 1, reply)
        assert len(out) == 1 and out[0].severity == 0.9

    def test_a_minted_id_passes_the_same_structural_gate_the_arms_apply(self):
        """`Fable-SIM_F609` is a real seat alias and NOT a valid minted id.

        `_structurally_valid_fid` admits alphanumerics and underscores only, and
        every one of arms 1, 1b, 2, 3 and 4 calls it on the model-written id
        before prefixing. Executed both ways here: the pre-envelope pipeline
        refuses the same id in prose, so the envelope is not being held to a
        stricter rule than the parser it layers over -- it is being held to the
        same one.
        """
        prose = ("FINDING_ID: Fable-SIM_F609\nSEVERITY: 0.9\n"
                 "DESCRIPTION: a claim under a prefixed alias.\n")
        assert not [f for f in _pre_envelope_pipeline("Seat", 1, prose)
                    if "F609" in f.finding_id], (
            "the arms accept this id after all, so mirroring their gate is the "
            "wrong behaviour and this test is asserting the wrong thing")
        reply = (f"{BEG} field=DESCRIPTION id=Fable-SIM_F609>>>a claim.{END}\n"
                 f"{BEG} field=SEVERITY id=Fable-SIM_F609>>>0.9{END}\n")
        assert not [f for f in rc.parse_findings("Seat", 1, reply)
                    if "F609" in f.finding_id]

    def test_the_same_alias_still_ENRICHES_a_finding_that_exists(self):
        """The asymmetry is deliberate: an overlay creates no id, so no gate."""
        reply = ("FINDING_ID: F609\nSEVERITY: 0.1\nDESCRIPTION: a claim.\n"
                 f"{BEG} field=SEVERITY id=F609>>>0.9{END}\n")
        out = rc.parse_findings("Seat", 1, reply)
        assert len(out) == 1 and out[0].severity == 0.9

    def test_an_ambiguous_id_mints_nothing_and_overlays_nothing(self):
        """Two parsed findings normalising to one key is not an identification.

        And minting would then put a third row under a colliding `finding_id` --
        the shape `{f.finding_id: f for f in findings}` silently overwrote on in
        the Exp 40 continuation.
        """
        reply = ("FINDING_ID: F001\nSEVERITY: 0.2\nDESCRIPTION: first.\n\n"
                 "FINDING_ID: F001\nSEVERITY: 0.3\nDESCRIPTION: second.\n\n"
                 f"{BEG} field=SEVERITY id=F001>>>0.9{END}\n"
                 f"{BEG} field=DESCRIPTION id=F001>>>a third claim.{END}\n")
        plain = _pre_envelope_pipeline("Seat", 1, reply)
        out = rc.parse_findings("Seat", 1, reply)
        assert len(plain) == 2, "fixture no longer produces an ambiguous key"
        assert len(out) == 2, (
            "an ambiguous owner must not mint a third finding under an id two "
            "findings already share")
        assert [f.severity for f in out] == [f.severity for f in plain], (
            "an ambiguous owner must not overlay either candidate")

    def test_a_prose_finding_and_an_enveloped_one_both_survive(self):
        reply = ("FINDING_ID: F001\nSEVERITY: 0.7\nDESCRIPTION: the first claim.\n\n"
                 f"{BEG} field=DESCRIPTION id=F002>>>the second claim.{END}\n"
                 f"{BEG} field=SEVERITY id=F002>>>0.8{END}\n")
        ids = {f.finding_id: f for f in rc.parse_findings("Seat", 1, reply)}
        assert set(ids) == {"Seat_F001", "Seat_F002"}, (
            "an envelope must not displace a finding stated in prose, and a "
            "prose finding must not suppress one stated in envelopes")
        assert ids["Seat_F001"].severity == 0.7
        assert ids["Seat_F002"].severity == 0.8
        assert ids["Seat_F002"].description == "the second claim."

    def test_an_owner_with_no_description_enriches_and_does_not_mint(self):
        """A CORROBORATION envelope alone is evidence, not a claim."""
        reply = (f"{BEG} field=CORROBORATION id=F009>>>{A_SOUND}{END}\n"
                 "Some prose that is not a finding at all, and is long enough "
                 "to clear the fallback's 50-character floor comfortably.\n")
        out = rc.parse_findings("Seat", 1, reply)
        assert "Seat_F009" not in {f.finding_id for f in out}, (
            "minting a finding from an owner that stated no claim would "
            "manufacture a claim the seat never made")

    def test_the_unstructured_fallback_stands_down_for_an_enveloped_reply(self):
        reply = (f"{BEG} field=DESCRIPTION id=F001>>>the only claim here.{END}\n"
                 f"{BEG} field=SEVERITY id=F001>>>0.9{END}\n"
                 "A paragraph of surrounding prose, long enough on its own to "
                 "clear the fallback's 50-character floor.\n")
        ids = {f.finding_id for f in rc.parse_findings("Seat", 1, reply)}
        assert ids == {"Seat_F001"}, (
            "a reply written entirely in envelopes was recorded twice: once "
            "correctly and once as a severity-0.3 blob of its own raw text")

    def test_the_unstructured_fallback_is_NOT_removed(self):
        """The other half of the additive standard. The mechanic still fires."""
        reply = ("Some unstructured prose about a defect, with no schema fields "
                 "at all, comfortably over the fifty character floor.")
        ids = {f.finding_id for f in rc.parse_findings("Seat", 1, reply)}
        assert ids == {"Seat_UNSTRUCTURED"}

    def test_an_enveloped_verdict_also_stands_the_fallback_down(self):
        reply = (f"{BEG} field=VERDICT id=C0042>>>CONFIRM{END}\n"
                 "Nothing else to add this round, and this sentence exists only "
                 "to carry the reply past the fallback's length floor.\n")
        assert rc.parse_findings("Seat", 1, reply) == [], (
            "a verdict-only reply is valid in star topology and must not become "
            "a severity-0.3 finding; the regex path already knows this")

    def test_corroboration_present_survives_an_unrelated_overlay(self):
        """`dataclasses.replace` would silently drop it. See `_replace_preserving_extras`."""
        reply = ("FINDING_ID: F001\nSEVERITY: 0.1\n"
                 "DESCRIPTION: the gate is wrong, CORROBORATION: R_k = 0.4\n"
                 f"{BEG} field=SEVERITY id=F001>>>0.9{END}\n")
        plain = _pre_envelope_pipeline("Seat", 1, reply)
        assert getattr(plain[0], "corroboration_present", None) is True, (
            "fixture no longer sets the flag it exists to protect")
        out = rc.parse_findings("Seat", 1, reply)
        assert out[0].severity == 0.9
        assert getattr(out[0], "corroboration_present", None) is True

    def test_a_falsification_envelope_raises_the_flag(self):
        """Written entirely in envelopes, so the flag has ONE possible source.

        An earlier version of this test put the claim in prose, and the
        description then ran to the end of the block and swallowed the word
        FALSIFICATION out of the envelope markup -- so `_FALSIF_MARKERS` set the
        flag whether the overlay ran or not, and the test passed with the overlay
        reverted. It measured nothing. Named here because a test that cannot fail
        is the exact shape this file exists to avoid.
        """
        reply = (f"{BEG} field=DESCRIPTION id=F001>>>the gate reads a stale "
                 f"label, and nothing downstream notices.{END}\n"
                 f"{BEG} field=SEVERITY id=F001>>>0.9{END}\n"
                 f"{BEG} field=FALSIFICATION id=F001>>>reverted the fix and "
                 f"re-ran; 4 of 5 assertions go red{END}\n")
        out = rc.parse_findings("Seat", 1, reply)
        assert [f.finding_id for f in out] == ["Seat_F001"]
        assert getattr(out[0], "falsification_present", None) is True

    def test_a_minted_finding_cannot_self_certify_without_falsifying(self):
        """The same rule the 5 arms above apply, mirrored rather than skipped."""
        reply = (f"{BEG} field=DESCRIPTION id=F001>>>a claim with no attempt "
                 f"to break it.{END}\n"
                 f"{BEG} field=VERIFIED id=F001>>>TRUE{END}\n")
        out = rc.parse_findings("Seat", 1, reply)
        assert [f.finding_id for f in out] == ["Seat_F001"]
        assert out[0].verified is False, (
            "VERIFIED: TRUE with no FALSIFICATION is self-certification, and "
            "the envelope must not be a way around the gate the arms apply")

    def test_a_severity_that_does_not_parse_leaves_the_parsed_one_alone(self, capsys):
        reply = ("FINDING_ID: F001\nSEVERITY: 0.7\nFLAW_CLASS: 1\n"
                 "DESCRIPTION: a claim.\n"
                 f"{BEG} field=SEVERITY id=F001>>>very high indeed{END}\n"
                 f"{BEG} field=FLAW_CLASS id=F001>>>5{END}\n")
        out = rc.parse_findings("Seat", 1, reply)
        assert out[0].flaw_class == 5, (
            "the readable envelope beside the unreadable one must still apply, "
            "or this test cannot tell a refusal from an inert overlay")
        assert out[0].severity == 0.7, (
            "an envelope that cannot be read must leave the value the arms "
            "above computed; writing 0.0 would be worse than no envelope")
        assert "SEVERITY" in capsys.readouterr().err, (
            "the refusal was silent. A seat that wrapped a field correctly and "
            "put something unreadable inside it is the one case worth saying "
            "out loud, and a rejection list nothing consumes is an addition "
            "nothing reaches")


# ─────────────────────────────────────────────────────────────────────────────
class TestVerdicts:

    def test_an_enveloped_verdict_is_read(self):
        text = (f"{BEG} field=VERDICT id=C0042>>>CHALLENGE{END}\n"
                f"{BEG} field=VERDICT_EVIDENCE id=C0042>>>the test passes at "
                f"HEAD{END}\n")
        assert R._parse_verdicts(text, "Seat", 1) == [
            ("CHALLENGE", "C0042", "the test passes at HEAD")]

    def test_a_payload_that_is_not_a_keyword_is_not_a_verdict(self):
        """The `NOT FALSIFIED`-read-as-`FALSIFIED` class, closed by equality."""
        for payload in ("NOT CONFIRM", "no longer CHALLENGE", "CONFIRMED-ish",
                        "I would CONFIRM if the test ran"):
            text = f"{BEG} field=VERDICT id=C0042>>>{payload}{END}"
            assert fe.envelope_verdicts(text) == [], (
                f"{payload!r} was read as a verdict; the payload is compared "
                f"for equality precisely so that it cannot be")

    def test_the_plain_form_still_parses_exactly_as_before(self):
        text = ("CONFIRM C0001 — the fix is correct\n"
                "CHALLENGE C0002 | the evidence does not reach it\n")
        assert R._parse_verdicts(text, "Seat", 1) == [
            ("CONFIRM", "C0001", "the fix is correct"),
            ("CHALLENGE", "C0002", "the evidence does not reach it")]

    def test_a_repeated_envelope_verdict_is_recorded_once(self):
        """`auto_resolve_contested` counts distinct models, but the per-reply
        dedupe is still what stops one reply producing 3 rows."""
        text = ((f"{BEG} field=VERDICT id=C0042>>>CHALLENGE{END}\n") * 3)
        assert len(R._parse_verdicts(text, "Seat", 1)) == 1

    def test_prose_evidence_fills_an_envelope_that_carried_none(self):
        """Sealing an empty string would DISCARD the prose beside it."""
        text = (f"{BEG} field=VERDICT id=C0042>>>CONFIRM{END}\n"
                "CONFIRM C0042 — ran the falsifier, it goes quiet\n")
        assert R._parse_verdicts(text, "Seat", 1) == [
            ("CONFIRM", "C0042", "ran the falsifier, it goes quiet")]

    def test_envelope_evidence_is_not_overwritten_by_a_longer_prose_line(self):
        text = (f"{BEG} field=VERDICT id=C0042>>>CONFIRM{END}\n"
                f"{BEG} field=VERDICT_EVIDENCE id=C0042>>>short but declared{END}\n"
                "CONFIRM C0042 — a much longer line of prose that would win the "
                "longest-evidence tie-break if the envelope were not sealed\n")
        assert R._parse_verdicts(text, "Seat", 1) == [
            ("CONFIRM", "C0042", "short but declared")]


# ─────────────────────────────────────────────────────────────────────────────
class TestEveryRefusalIsLoudAndNamed:

    @pytest.mark.parametrize("reason,text", [
        ("no_id", f"{BEG} field=SEVERITY>>>0.9{END}"),
        ("bad_id", f"{BEG} field=SEVERITY id=\"F 001!\">>>0.9{END}"),
        ("example_id", f"{BEG} field=SEVERITY id={fe.EXAMPLE_ONLY_ID}>>>0.9{END}"),
        ("no_field", f"{BEG} id=F001>>>0.9{END}"),
        ("unknown_field", f"{BEG} field=BANANA id=F001>>>0.9{END}"),
        ("unknown_attribute", f"{BEG} field=SEVERITY id=F001 weight=3>>>0.9{END}"),
        ("unterminated", f"{BEG} field=SEVERITY id=F001>>>0.9"),
        ("nested_begin",
         f"{BEG} field=SEVERITY id=F001>>>\n{BEG} field=SEVERITY id=F002>>>0.8{END}"),
        ("empty", f"{BEG} field=SEVERITY id=F001>>>{END}"),
        ("placeholder", f"{BEG} field=SEVERITY id=F001>>><0.0 to 1.0>{END}"),
        ("duplicate",
         f"{BEG} field=SEVERITY id=F001>>>0.9{END}{BEG} field=SEVERITY id=F001>>>0.1{END}"),
    ])
    def test_each_reason_is_reachable(self, reason, text):
        _accepted, refusals = fe.extract_field_envelopes(text)
        assert reason in {r["reason"] for r in refusals}, (
            f"reason {reason!r} is unreachable; a refusal path nothing can "
            f"trigger is an addition nothing reaches")

    def test_a_nested_begin_still_recovers_the_inner_envelope(self):
        text = (f"{BEG} field=SEVERITY id=F001>>>\n"
                f"{BEG} field=SEVERITY id=F002>>>0.8{END}")
        accepted, _ = fe.extract_field_envelopes(text)
        assert [(e.field, e.owner) for e in accepted] == [("SEVERITY", "F002")], (
            "refusing the outer must not discard the inner, which is probably "
            "the well-formed one")

    def test_the_end_token_is_never_read_as_a_header(self):
        accepted, refusals = fe.extract_field_envelopes(END + END + END)
        assert not accepted and not refusals

    def test_a_duplicate_keeps_the_first(self):
        text = (f"{BEG} field=SEVERITY id=F001>>>0.9{END}"
                f"{BEG} field=SEVERITY id=F001>>>0.1{END}")
        assert fe.fields_by_owner(text) == {"F001": {"SEVERITY": "0.9"}}

    def test_telemetry_counts_what_it_refused_and_decides_nothing(self):
        text = (f"{BEG} field=SEVERITY id=F001>>>0.9{END}"
                f"{BEG} field=BANANA id=F001>>>x{END}")
        t = fe.envelope_telemetry(text)
        assert t["headers_seen"] == 2 and t["accepted"] == 1 and t["refused"] == 1
        assert t["refusals_by_reason"] == {"unknown_field": 1}
        assert t["_decides_nothing"] is True


# ─────────────────────────────────────────────────────────────────────────────
class TestThePromptTeachesWhatTheParserAccepts:
    """The prompt and the parser are 2 forms of 1 convention, so EXECUTE both.

    `execute-do-not-grep` in its exact shape: a test that read the prompt string
    and a test that read the regex would each pass while the 2 disagreed, because
    each would be individually consistent. So the prompt's own example text is
    fed to the live extractor.
    """

    def test_the_taught_syntax_is_accepted_once_the_example_id_is_replaced(self):
        block = fe.envelope_instruction_block()
        accepted, refusals = fe.extract_field_envelopes(
            block.replace(fe.EXAMPLE_ONLY_ID, "F001"))
        assert not refusals, [r["reason"] for r in refusals]
        assert {(e.field, e.owner) for e in accepted} == {
            ("SEVERITY", "F001"), ("DESCRIPTION", "F001")}

    def test_a_verbatim_echo_of_the_taught_template_files_nothing(self):
        """The schema-echo hazard, closed by the reserved example id."""
        for block in (fe.envelope_instruction_block(),
                      fe.verdict_envelope_instructions()):
            accepted, refusals = fe.extract_field_envelopes(block)
            assert not accepted, (
                "the prompt's own example parsed as a real field; a model that "
                "echoes the schema would file a phantom finding")
            assert {r["reason"] for r in refusals} == {"example_id"}

    def test_an_echoed_template_mints_no_finding_through_the_whole_parser(self):
        reply = ("Here is the format I will use:\n"
                 + fe.envelope_instruction_block()
                 + "\nI found nothing this round.\n")
        assert [f.finding_id for f in rc.parse_findings("Seat", 1, reply)] == [
            "Seat_UNSTRUCTURED"], (
            "an echoed template must not become a finding; the UNSTRUCTURED "
            "fallback is the correct and unchanged answer for a reply that "
            "states no finding")

    def test_the_verdict_example_cannot_mint_a_verdict(self):
        assert fe.envelope_verdicts(fe.verdict_envelope_instructions()) == []

    def test_the_finding_format_prompt_carries_the_form(self):
        """Taught where a seat will see it, or it is an addition nothing reaches."""
        rendered = FINDING_FORMAT.format(prefix="IM_")
        assert BEG in rendered and END in rendered
        assert fe.EXAMPLE_ONLY_ID in rendered
        assert R._MACHINE_COMMS_INSTRUCTION.count(BEG) >= 2, (
            "the verdict envelope is not taught, so no seat can issue one")

    def test_the_canonical_field_list_in_the_prompt_is_the_parser_s_own(self):
        """Not 2 lists. The prompt renders `CANONICAL_FIELDS` itself."""
        for field in fe.CANONICAL_FIELDS:
            assert field in fe.ENVELOPE_WHY
            text = f"{BEG} field={field} id=F001>>>payload text{END}"
            accepted, refusals = fe.extract_field_envelopes(text)
            assert len(accepted) == 1, (
                f"{field} is advertised to seats and refused by the parser: "
                f"{[r['reason'] for r in refusals]}")


# ─────────────────────────────────────────────────────────────────────────────
class TestTheMeasurementIsReDerivedNotRemembered:
    """The committed figures are RE-RUN here, so a regression fails the suite.

    `measured-rate-travels-with-its-script` requires the script to be committed
    beside the number. This class is the other half: a figure nothing re-executes
    becomes a remembered figure, and the project's record holds the 282-of-711
    case where exactly that happened one day after the rule was written.
    """

    @pytest.fixture(scope="class")
    def mod(self):
        return MEASURE

    def test_the_hybrid_sentinel_grammar_still_refuses_six_of_twelve(self, mod):
        iv = mod.section1(R)
        assert (iv["k"], iv["n"]) == (6, 12), (
            "the committed figure is 6 of 12; if the sentinel grammar has been "
            "repaired, update the figure and the claim together -- fixing one "
            "leaves the pair lying")
        assert iv["wilson_agree"] < 1e-9, "the 2 Wilson computations disagree"

    def test_the_envelope_recovers_every_owner_and_the_prose_reader_does_not(self, mod):
        out = mod.section2(R, fe)
        assert out["envelope"]["k"] == out["n"] == 8
        assert out["owner_aware"]["k"] == 4, (
            f"the committed figure is 4 of 8 for the prose reader; measured "
            f"{out['owner_aware']['k']}")

    def test_the_decoration_grid_is_invariant(self, mod):
        out = mod.section4(fe)
        assert not out["bad"], out["bad"][:5]
        assert out["iv"]["n"] == 1440, (
            f"the committed grid size is 1440 shapes; measured {out['iv']['n']}")

    def test_the_scripts_verdict_can_say_no(self, mod, monkeypatch):
        """A gate that cannot refuse is not a gate.

        The repository reports 0 failing grid shapes and 0 changed replies, so a
        test asserting the LICENSED verdict would pass whether or not the
        criterion works. Both section 3 and section 4 are replaced by cheap
        stand-ins -- section 3 because re-running it would walk 5,445 replies a
        second time for no new information -- and `main()` is CALLED twice: once
        with a reported grid failure, which must exit 1, and once with clean
        stand-ins, which must exit 0. The second call is what shows the refusal
        came from the criterion and not from the stubbing.
        """
        clean3 = {"iv": mod.intervals(5445, 5445), "changed": [],
                  "carrying": 0, "findings": 17127}
        clean4 = {"iv": mod.intervals(1440, 1440), "bad": []}
        monkeypatch.setattr(mod, "section3", lambda _rc, _fe: clean3)
        monkeypatch.setattr(
            mod, "section4",
            lambda _fe: {"iv": mod.intervals(1439, 1440),
                         "bad": [(("fabricated shape",), ["unknown_field"], [])]})
        assert mod.main() == 1
        monkeypatch.setattr(mod, "section4", lambda _fe: clean4)
        assert mod.main() == 0, (
            "with clean stand-ins the verdict must license the repair, or the "
            "previous assertion proved only that the script is broken")

    def test_the_verdict_also_refuses_a_changed_reply(self, mod, monkeypatch):
        """The other refusal condition, which section 4's stub cannot reach."""
        monkeypatch.setattr(
            mod, "section3",
            lambda _rc, _fe: {"iv": mod.intervals(5444, 5445),
                              "changed": ["bench/logs/fabricated/reply.json"],
                              "carrying": 0, "findings": 17127})
        monkeypatch.setattr(
            mod, "section4",
            lambda _fe: {"iv": mod.intervals(1440, 1440), "bad": []})
        assert mod.main() == 1
