"""Commissioned tests for the mechanically generated seeded-defect catalogue.

3 rules govern this file, and each is a founder ruling with an incident behind it.

EXECUTE, DO NOT GREP. Nothing here asserts on the source text of
`bench/seeded_defect_catalogue.py`. Where 2 forms of a thing exist as live code,
both are CALLED and their outputs compared: the module's own `safe_eval` against
SymPy, the module's catalogue against the real `canary_seeding.seed`,
`load_catalogue`, `detection_rate` and `split_difficulty_balance`. 4 defects in
this project have been found by executing 2 forms against each other and none by
reading.

EVERY TEST MUST BE ABLE TO FAIL. A guard is fed the case it must accept AND the
case it must refuse. The verification tests go further: they take a catalogue
that verifies clean, corrupt 1 field, and require the corruption to be caught.
That is the only way to tell `verify_ground_truth` apart from a function that
reads the record back and agrees with itself -- which is what 3 tests recently
found in this project were doing, passing with the model replaced by the
constant 42.

A MEASURED NUMBER TRAVELS WITH ITS SCRIPT. Every count quoted in a docstring here
is produced by the test that quotes it, run over `FIXTURE` below. Nothing is
asserted from a comment.
"""
import dataclasses
import json
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from bench.canary_seeding import (  # noqa: E402
    CALIBRATION,
    HELD_OUT,
    CanaryIntegrityError,
    catches,
    detection_rate,
    load_catalogue,
    seed,
    split_difficulty_balance,
)
import bench.seeded_defect_catalogue as sdc  # noqa: E402
from bench.seeded_defect_catalogue import (  # noqa: E402
    CONSISTENT,
    EXACT,
    MISS,
    MIN_RELATIVE_ERROR,
    CatalogueGenerationError,
    Detection,
    Location,
    Refutation,
    SeededDefect,
    catalogue_from_json,
    catalogue_to_json,
    check_detection,
    collect_sites,
    fingerprint,
    find_identities,
    find_relations,
    generate_catalogue,
    identity_candidates,
    load_generated_catalogue,
    make_verifier,
    relation_candidates,
    resolve_symbols,
    safe_eval,
    seed_one,
    symbol_table,
    verify_catalogue,
    verify_ground_truth,
    write_catalogue,
)

CONTROL = REPO / "bench" / "cdsfl_registry" / "targets" / "control_two_distinct_defects.md"

#: A synthetic target rich enough to exercise all 4 declared operators. Every
#: arithmetic claim in it is TRUE, and `test_the_fixture_is_arithmetically_sound`
#: proves that with SymPy rather than asserting it here. A fixture with a
#: pre-existing error would make every later result meaningless, because the
#: generator would be planting on top of a defect it did not create.
FIXTURE = """# Thermal and Sampling Budget for the Zone Controller

## 1. Acquisition chain

The front-end samples at `f_s = 480 Hz` into a ring buffer of `N = 512` samples.
The band of interest is limited to `f_max = 180 Hz` by the anti-alias filter.
The transform bin spacing is therefore `480 / 512 = 0.9375` hertz.
The buffer spans `512 / 480 = 1.0667` seconds of signal.
Because `f_s = 480 Hz` is greater than `f_max = 180 Hz`, no aliasing occurs in band.

## 2. Power budget

Each of the sensor boards draws `I_board = 145 mA` from the rail.
With `n_boards = 6` fitted, the total is `145 * 6 = 870` milliamps.
The rail is specified at `V_rail = 12 V`, so the load is `12 * 0.87 = 10.44` watts.
The supply is rated at `P_max = 25 W`, and `10.44 < 25` leaves headroom.

## 3. Thermal path

The heatsink has a thermal resistance of `R_th = 2.4 K/W`.
Dissipation in the regulator is `10.44 - 8.7 = 1.74` watts.
The rise above ambient is `1.74 * 2.4 = 4.176` kelvin.
Ambient is taken as `T_amb = 35 C`, giving a junction figure of `35 + 4.176 = 39.176` degrees.
The device limit is `T_max = 85 C`, and `39.176 < 85` is comfortable.

## 4. Link budget

The radio transmits at `P_tx = 14 dBm` into a feeder of `L_feed = 1.8 dB`.
Radiated power is therefore `14 - 1.8 = 12.2` dBm.
Free-space loss over the span is `L_fs = 92 dB`, so the arriving level is `12.2 - 92 = -79.8` dBm.
The receiver sensitivity is `S_rx = -95 dBm`, and `-79.8 > -95` closes the link.

## 5. Storage

Each record occupies `B_rec = 48 bytes` and the log holds `n_rec = 2500` records.
The log therefore occupies `48 * 2500 = 120000` bytes.
The partition is `P_size = 262144 bytes`, and `120000 < 262144` fits.
Recording at `I_board = 145 mA` for an hour costs `145 * 1 = 145` milliamp hours.
The cell is specified at `C_cell = 2200 mAh`, so `145 < 2200` is a small fraction.
The partition `P_size = 262144 bytes` is reported in the manifest as well.
The board current `I_board = 145 mA` is repeated in the parts list.
The ambient figure `T_amb = 35 C` also appears in the environmental section.
The rail voltage `V_rail = 12 V` is restated in the wiring note.
The sensitivity `S_rx = -95 dBm` is restated in the radio appendix.
The buffer depth `N = 512` is restated in the firmware note.
"""


@pytest.fixture(scope="module")
def catalogue():
    return generate_catalogue(FIXTURE, seed_value=0, domain="engineering")


# --------------------------------------------------------------------------- #
# The extractors, against the real project target                              #
# --------------------------------------------------------------------------- #
def test_symbol_table_refuses_a_chained_equality():
    """The 1 parse that would poison every catalogue built from this document.

    `control_two_distinct_defects.md` line 17 reads

        `df = f_s / N = 400 / 256 = 1.5625 Hz`

    and a bare `symbol = number` regex reads "N = 400" out of it. N is 256. Every
    plant resting on that binding would be a plant on a defect the generator
    invented, and it would verify clean, because the generator and the verifier
    would share the mistake. Both halves are asserted: the 3 real bindings must be
    present, and the false 1 must be absent.
    """
    text = CONTROL.read_text(encoding="utf-8")
    bindings = symbol_table(text)
    got = sorted({(a.symbol, a.value, a.unit) for a in bindings})
    assert got == [("N", 256.0, ""), ("f_max", 180.0, "Hz"), ("f_s", 400.0, "Hz")]
    assert ("N", 400.0) not in {(a.symbol, a.value) for a in bindings}


def test_symbol_table_accepts_ordinary_assignments():
    """The known-GOOD half. Without it the boundary rules could be `continue` always."""
    bindings = {a.symbol: a.value for a in symbol_table(FIXTURE)}
    assert bindings["f_s"] == 480.0
    assert bindings["N"] == 512.0
    assert bindings["S_rx"] == -95.0
    assert bindings["P_size"] == 262144.0


@pytest.mark.parametrize("snippet,symbol,rule", [
    ("the ratio a / b = 12 holds", "b", "left"),
    ("the sum a + b = 7 overall", "b", "left"),
    ("we have x = 2 * y = 10 overall", "x", "right"),
    ("the ratio a / b = 12 / 4 = 3 holds", "b", "both"),
])
def test_an_operand_position_never_becomes_a_binding(snippet, symbol, rule):
    """Each boundary rule gets a case that ONLY it catches.

    This list started as 2 cases and both were caught by the RIGHT rule alone, so
    deleting the LEFT rule entirely left the whole suite green. `a / b = 12 holds`
    is the separating case: the character after 12 is ordinary prose, so only the
    character BEFORE b can reject the binding. A guard no test can kill is
    indistinguishable from no guard, which is the failure this project keeps
    finding in its own tests.
    """
    assert symbol not in {a.symbol for a in symbol_table(snippet)}


def test_identity_extractor_finds_the_control_identity():
    text = CONTROL.read_text(encoding="utf-8")
    identities = find_identities(text)
    assert len(identities) == 1
    got = identities[0]
    assert text[got.expr_offset:got.expr_end] == "400 / 256"
    assert text[got.result_offset:got.result_end] == "1.5625"
    assert got.computed == pytest.approx(1.5625)
    assert got.holds


def test_a_failing_identity_is_not_a_site():
    """An identity that is ALREADY wrong is a pre-existing defect, not a plant site.

    Planting there would score a reviewer against a contradiction the generator did
    not create, and the clean-side half of `verify_ground_truth` would fail.
    """
    broken = "the bin spacing is 400 / 256 = 2.5000 hertz\n"
    assert find_identities(broken) == []
    assert [i.holds for i in identity_candidates(broken)] == [False]


def test_a_relation_resolves_to_its_nearest_binding():
    """Difficulty is the EASIEST refutation, so a symbol resolves to its nearest binding.

    Measured on the control document: line 14 reads "`f_s = 400 Hz` exceeds
    `f_max = 180 Hz`", and f_max is ALSO bound on line 8. Resolving to the first
    binding put the refuting evidence on line 8 and labelled the plant
    `distributed`, when a reader refutes it without leaving line 14.
    """
    text = CONTROL.read_text(encoding="utf-8")
    symbols, _ = resolve_symbols(text)
    relations = find_relations(text, symbols)
    assert len(relations) == 1
    assert relations[0].op_text == "exceeds"
    assert relations[0].line == 14
    assert relations[0].evidence_lines == (14,)


def test_a_false_relation_is_not_a_site():
    text = "the supply gives 5 V and 5 > 9 was claimed\n"
    symbols, _ = resolve_symbols(text)
    assert find_relations(text, symbols) == []
    assert [r.holds for r in relation_candidates(text, symbols, symbol_table(text))] == [False]


def test_a_symbol_bound_2_ways_is_reported_and_never_planted():
    """A document already contradicting itself is information, not a site.

    Both halves: the inconsistent symbol is named in the coverage report, and no
    site is offered on it.
    """
    text = ("The gain is `G = 4 dB` in the datasheet.\n"
            "Elsewhere the gain is `G = 9 dB` in the same note.\n")
    _, inconsistent = resolve_symbols(text)
    assert inconsistent == ["G"]
    sites, report = collect_sites(text)
    assert report["symbols_bound_inconsistently"] == ["G"]
    assert [s for s in sites if s.symbol == "G"] == []


# --------------------------------------------------------------------------- #
# Arithmetic, cross-verified with a second tool                                #
# --------------------------------------------------------------------------- #
def test_the_fixture_is_arithmetically_sound_and_sympy_agrees():
    """Every identity in FIXTURE is true, and 2 independent evaluators say so.

    `safe_eval` is this module's own AST walker. SymPy is an independent
    implementation with independent parsing and exact rational arithmetic. Agreeing
    with itself would prove nothing; agreeing with SymPy is evidence. This is the
    project's multi-tool cross-verification rule applied to the 1 computation the
    whole catalogue rests on.

    Measured: 11 identities in FIXTURE, all holding, all confirmed by SymPy.
    """
    sympy = pytest.importorskip("sympy")
    identities = find_identities(FIXTURE)
    assert len(identities) == 11
    for identity in identities:
        exact = sympy.Rational(str(sympy.sympify(identity.expr, rational=True)))
        assert float(exact) == pytest.approx(safe_eval(identity.expr), abs=1e-12)
        assert abs(float(exact) - identity.stated) <= identity.tolerance


def test_safe_eval_refuses_anything_that_is_not_arithmetic():
    """The expressions come out of an untrusted review target, so `eval` is not an option."""
    assert safe_eval("400 / 256") == pytest.approx(1.5625)
    for hostile in ("__import__('os').getcwd()", "open('x')", "a + 1", "[1,2][0]"):
        with pytest.raises((ValueError, SyntaxError)):
            safe_eval(hostile)


# --------------------------------------------------------------------------- #
# Determinism -- the property the whole exercise rests on                      #
# --------------------------------------------------------------------------- #
def test_the_same_seed_gives_a_byte_identical_catalogue():
    first = generate_catalogue(FIXTURE, seed_value=11, domain="engineering")
    second = generate_catalogue(FIXTURE, seed_value=11, domain="engineering")
    dumped = json.dumps(catalogue_to_json(first), sort_keys=True)
    assert dumped == json.dumps(catalogue_to_json(second), sort_keys=True)
    assert fingerprint(first) == fingerprint(second)


def test_the_global_random_module_cannot_change_the_catalogue():
    """Proof that no unseeded global draw reaches the output.

    An unseeded `random.random()` anywhere in the generator would make the
    catalogue depend on process history rather than on the seed, and the
    same-seed test above would still pass whenever the 2 calls happened to be
    adjacent. Re-seeding the GLOBAL module differently between the 2 calls is what
    tells them apart.
    """
    import random

    random.seed(1)
    first = fingerprint(generate_catalogue(FIXTURE, seed_value=5, domain="engineering"))
    random.seed(999999)
    [random.random() for _ in range(50)]
    second = fingerprint(generate_catalogue(FIXTURE, seed_value=5, domain="engineering"))
    assert first == second


def _plant_set(catalogue):
    """What was actually planted, with the bookkeeping stripped out.

    NOT `fingerprint`, and the difference is the whole point of the 2 tests below.
    A defect id embeds the seed, and the catalogue records the seed as a field, so
    the fingerprint varies with the seed even when the PLANTS are identical.
    Established by removing the seed from the generator and re-running: every test
    stayed green while the plants stopped varying at all. A determinism test that
    a seed-ignoring generator passes is not a determinism test.
    """
    return tuple((d.location.offset, d.location.line, d.defect_class,
                  d.detection.seeded_text, d.split) for d in catalogue.defects)


def test_the_fingerprint_alone_cannot_tell_2_catalogues_apart(catalogue):
    """Why the determinism tests below compare plants and not fingerprints.

    Executed rather than argued: hold the plants fixed, change only the recorded
    seed, and watch the fingerprint move. Anything that varies with the seed for
    bookkeeping reasons will pass a fingerprint-based determinism test while the
    plants stand still.
    """
    relabelled = dataclasses.replace(catalogue, seed=catalogue.seed + 1)
    assert _plant_set(relabelled) == _plant_set(catalogue)
    assert fingerprint(relabelled) != fingerprint(catalogue)


def test_different_seeds_plant_different_defects():
    """Over 50 seeds on FIXTURE the plant sets must not collapse.

    The threshold sits well below what the generator achieves, so an ordinary
    change to the operator table does not break it. A generator that ignored its
    seed scores 1, which is what makes the assertion worth making.
    """
    sets = {_plant_set(generate_catalogue(FIXTURE, seed_value=s, domain="engineering"))
            for s in range(50)}
    assert len(sets) >= 20, f"only {len(sets)} distinct plant sets over 50 seeds"


def test_the_same_seed_plants_the_same_defects():
    """The other half: same seed, same plants, not merely the same ids."""
    first = generate_catalogue(FIXTURE, seed_value=23, domain="engineering")
    second = generate_catalogue(FIXTURE, seed_value=23, domain="engineering")
    assert _plant_set(first) == _plant_set(second)


def test_defects_are_emitted_in_document_order(catalogue):
    """Output order comes from sorted offsets, never from set or dict iteration.

    KNOWN LIMIT, stated rather than glossed: `PYTHONHASHSEED` cannot be varied
    inside this process, and the suite's conftest denies subprocess launch, so
    hash-seed independence is not directly executable here. Document order is the
    observable consequence of the sorting that provides it, and it fails
    immediately if any output ordering is taken from an unordered container.
    """
    offsets = [d.location.offset for d in catalogue.defects]
    assert offsets == sorted(offsets)
    lines = [d.location.line for d in catalogue.defects]
    assert lines == sorted(lines)


# --------------------------------------------------------------------------- #
# Ground truth, re-derived from the documents                                  #
# --------------------------------------------------------------------------- #
def test_every_plant_verifies_against_the_2_documents(catalogue):
    """Every plant at seed 0 on FIXTURE, re-derived from the clean and seeded texts.

    The plant count is asserted, not quoted, so the figure in this docstring cannot
    drift away from what the generator does.
    """
    assert len(catalogue.defects) == 20
    checks = verify_catalogue(catalogue, FIXTURE)
    broken = [(c.defect_id, c.failures) for c in checks if not c.ok]
    assert broken == [], broken
    assert len(checks) == len(catalogue.defects)
    assert all(c.clean_refutation_holds and not c.seeded_refutation_holds for c in checks)


def test_all_4_declared_operators_actually_fire(catalogue):
    """Coverage is stateable, and it is stated by counting, not by claiming."""
    emitted = {d.defect_class for d in catalogue.defects}
    assert emitted == {c.name for c in sdc.DEFECT_CLASSES}
    counts = catalogue.coverage["defects_by_class"]
    assert sum(counts.values()) == len(catalogue.defects)
    assert all(count > 0 for count in counts.values())


def _first(catalogue, defect_class):
    for defect in catalogue.defects:
        if defect.defect_class == defect_class:
            return defect
    raise AssertionError(f"no {defect_class} plant in the catalogue")


def test_a_wrong_correct_value_is_caught(catalogue):
    """Corrupt the record, leave the text mutation alone. The documents must win."""
    good = _first(catalogue, "stated_result_error")
    assert verify_ground_truth(good, FIXTURE).ok
    bad = dataclasses.replace(good, detection=dataclasses.replace(
        good.detection, correct_value=good.detection.correct_value * 3.0))
    result = verify_ground_truth(bad, FIXTURE)
    assert not result.ok
    assert any("correct_value" in f for f in result.failures), result.failures


def test_a_wrong_offset_is_caught(catalogue):
    good = _first(catalogue, "operand_error")
    bad = dataclasses.replace(good, location=dataclasses.replace(
        good.location, offset=good.location.offset + 3, end=good.location.end + 3))
    result = verify_ground_truth(bad, FIXTURE)
    assert not result.ok
    assert any("not the recorded" in f or "does not match the offset" in f
               for f in result.failures), result.failures


def test_a_wrong_line_number_is_caught(catalogue):
    good = _first(catalogue, "quantity_scale_error")
    bad = dataclasses.replace(good, location=dataclasses.replace(
        good.location, line=good.location.line + 1))
    result = verify_ground_truth(bad, FIXTURE)
    assert not result.ok
    assert any("line/column" in f for f in result.failures), result.failures


def test_a_plant_that_breaks_nothing_is_caught(catalogue):
    """The case that separates verification from self-agreement.

    The edit is real -- the text changes -- and the record describes it correctly.
    What it does NOT do is create a defect: "0.9375" becomes "0.93750", which the
    identity still satisfies. A verifier that read the record back would pass this.
    One that re-evaluates the document cannot.
    """
    good = _first(catalogue, "stated_result_error")
    original = good.location.text
    padded = original + "0"
    bad = dataclasses.replace(
        good,
        replace=good.find[: -len(original)] + padded,
        detection=dataclasses.replace(good.detection, seeded_text=padded,
                                      seeded_value=float(padded)),
        relative_error=0.0,
    )
    result = verify_ground_truth(bad, FIXTURE)
    assert not result.ok
    assert result.seeded_refutation_holds
    assert any("still holds on the SEEDED" in f for f in result.failures), result.failures


def test_a_severity_invented_per_defect_is_caught(catalogue):
    """Severity is a class parameter. A per-defect value would be a fabricated number."""
    good = _first(catalogue, "relation_reversal")
    bad = dataclasses.replace(good, severity="critical")
    result = verify_ground_truth(bad, FIXTURE)
    assert not result.ok
    assert any("severity" in f for f in result.failures), result.failures


def test_a_wrong_relative_error_is_caught(catalogue):
    good = _first(catalogue, "operand_error")
    bad = dataclasses.replace(good, relative_error=(good.relative_error or 0.0) + 0.5)
    result = verify_ground_truth(bad, FIXTURE)
    assert not result.ok
    assert any("relative_error" in f for f in result.failures), result.failures


def test_a_wrong_cross_check_count_is_caught(catalogue):
    good = _first(catalogue, "quantity_scale_error")
    bad = dataclasses.replace(good, cross_check_sites=good.cross_check_sites + 7)
    result = verify_ground_truth(bad, FIXTURE)
    assert not result.ok
    assert any("cross_check_sites" in f for f in result.failures), result.failures


def test_verification_reads_the_document_it_is_given(catalogue):
    """Tamper with the plant's OWN line and the record must lose to the document."""
    good = _first(catalogue, "operand_error")
    assert verify_ground_truth(good, FIXTURE).ok
    lines = FIXTURE.split("\n")
    lines[good.location.line - 1] = "  " + lines[good.location.line - 1]
    tampered = "\n".join(lines)
    result = verify_ground_truth(good, tampered)
    assert not result.ok
    assert any("not the recorded" in f or "does not match the offset" in f
               for f in result.failures), result.failures


def test_verifying_against_the_wrong_revision_is_refused(catalogue):
    """A per-plant check cannot see an edit elsewhere in the article. This can.

    Found by this suite: tampering with a line AFTER the plant under test left
    `verify_ground_truth` passing, correctly, because the plant's own span was
    untouched. At catalogue level that would tie a result to the wrong revision --
    exactly what `bench/cdsfl_registry/targets/MANIFEST.md` records happening once
    already, when the control's fingerprint was left stale across 7 claim repairs.
    Both halves: the right text is accepted, a 1-character edit anywhere is not.
    """
    assert len(verify_catalogue(catalogue, FIXTURE)) == len(catalogue.defects)
    elsewhere = FIXTURE.replace("The heatsink has a thermal resistance",
                                "The heat sink has a thermal resistance")
    assert elsewhere != FIXTURE
    with pytest.raises(CatalogueGenerationError, match="different revision"):
        verify_catalogue(catalogue, elsewhere)


def test_every_relative_error_clears_the_declared_floor(catalogue):
    """A perturbation inside the document's own rounding is not a defect a reader could call.

    2 assertions, because the obvious 1 is self-referential: comparing plants
    against `MIN_RELATIVE_ERROR` imported from the module means zeroing the
    constant lowers the bar with it, and the test stays green -- confirmed by
    doing exactly that. So the parameter is checked for being non-degenerate, and
    separately the plants are checked against it.
    """
    assert MIN_RELATIVE_ERROR >= 0.05, "the declared floor has been zeroed"
    numeric = [d for d in catalogue.defects if d.relative_error is not None]
    assert numeric
    assert all(d.relative_error >= MIN_RELATIVE_ERROR for d in numeric)


# --------------------------------------------------------------------------- #
# Seeding, through the production seeder                                       #
# --------------------------------------------------------------------------- #
def test_the_catalogue_seeds_through_canary_seeding(catalogue):
    """`canary_seeding.seed` is the function a real run uses. It is what must accept this."""
    seeded, manifest = seed(FIXTURE, catalogue.canaries())
    assert seeded != FIXTURE
    assert manifest["seeded_sha256"] == catalogue.seeded_sha256
    assert len(manifest["canaries"]) == len(catalogue.defects)


def test_seeding_never_changes_the_line_count(catalogue):
    """Every recorded line number depends on this, in both documents."""
    seeded, _ = seed(FIXTURE, catalogue.canaries())
    assert len(seeded.split("\n")) == len(FIXTURE.split("\n"))
    for defect in catalogue.defects:
        assert len(seed_one(defect, FIXTURE).split("\n")) == len(FIXTURE.split("\n"))


def test_no_2_plants_share_a_line_or_overlap(catalogue):
    """A detection claim names a line, so 2 plants on 1 line make grading arbitrary.

    The PROPERTY is asserted, not the mechanism that delivers it, because 3
    overlapping mechanisms deliver it: line-anchored `find` windows, the
    1-plant-per-line rule, and the span-disjointness check. On this fixture any 1
    of them suffices -- removing the disjointness check alone changes no test
    outcome -- so no test here can claim to guard that check individually. What
    the suite does guarantee is that the property survives; if all 3 mechanisms
    were weakened together this fails.
    """
    lines = [d.location.line for d in catalogue.defects]
    assert len(lines) == len(set(lines))
    spans = sorted((FIXTURE.index(d.find), FIXTURE.index(d.find) + len(d.find))
                   for d in catalogue.defects)
    for (_, first_end), (second_start, _) in zip(spans, spans[1:]):
        assert first_end <= second_start


def test_an_earlier_plant_creating_a_later_plants_find_is_detected():
    """The collision that disjoint spans cannot prevent, and that actually happened.

    While building this module, generation on FIXTURE failed at the self-seed check
    with "`find` text occurs 2 times": an earlier plant's REPLACEMENT had created a
    second copy of a later plant's `find`. The cure was to anchor every `find` at
    the start of its line; `_first_ambiguous` is the backstop, and this is its test.
    Both halves -- the colliding pair is caught, the same pair without the collision
    is not.
    """
    text = "aaa 1\nbbb 2\n"

    def _defect(defect_id, find, replace):
        return SeededDefect(
            id=defect_id, domain="d", defect_class="stated_result_error",
            generator="mutate_identity_result", severity="high", severity_basis="b",
            split=HELD_OUT, difficulty=sdc.DIFFICULTY_LOCAL, find=find, replace=replace,
            location=Location(line=1, col=0, offset=0, end=1, text="a"),
            detection=Detection(line=1, correct_text="a", seeded_text="b",
                                correct_value=None, seeded_value=None, tolerance=0.0),
            refutation=Refutation(kind="recompute_identity", spans=(), explanation="e"),
            relative_error=None, cross_check_sites=0, summary="s")

    colliding = _defect("A", "aaa 1", "bbb 2")
    later = _defect("B", "bbb 2", "bbb 9")
    assert sdc._first_ambiguous(text, [colliding, later]) == "B"
    assert sdc._first_ambiguous(text, [later]) is None


def test_seeding_introduces_no_inconsistency_the_catalogue_does_not_record():
    """A defect the catalogue does not name would be scored as a reviewer's false positive.

    Measured over 30 seeds on FIXTURE: 0 unattributed inconsistencies. That is not
    luck, and the reason is worth recording, because it constrains any operator
    added later. A `quantity_scale_error` leaves its symbol bound 2 ways, and
    `resolve_symbols` then EXCLUDES that symbol, so a remote relation resting on it
    becomes unresolvable rather than false. Identities never reference symbols at
    all. A future operator that can falsify a claim on another line would break
    this test, which is the point of keeping it.
    """
    def inconsistencies(text):
        bindings = symbol_table(text)
        symbols, inconsistent = resolve_symbols(text)
        found = {("identity", i.line) for i in identity_candidates(text) if not i.holds}
        found |= {("relation", r.line)
                  for r in relation_candidates(text, symbols, bindings) if not r.holds}
        found |= {("symbol", s) for s in inconsistent}
        return found

    assert inconsistencies(FIXTURE) == set(), "the fixture must start clean"
    for seed_value in range(30):
        cat = generate_catalogue(FIXTURE, seed_value=seed_value, domain="engineering")
        seeded, _ = seed(FIXTURE, cat.canaries())
        planted_lines = {d.location.line for d in cat.defects}
        planted_symbols = {sdc._symbol_of(d) for d in cat.defects
                           if d.refutation.kind == "cross_reference_quantity"}
        for kind, where in inconsistencies(seeded):
            attributed = (where in planted_symbols if kind == "symbol"
                          else where in planted_lines)
            assert attributed, f"seed {seed_value}: unrecorded {kind} at {where!r}"


# --------------------------------------------------------------------------- #
# The splits, against the real scorer                                          #
# --------------------------------------------------------------------------- #
def test_the_held_out_split_satisfies_detection_rate(catalogue):
    """`detection_rate` refuses a single-generator held-out set. It must accept this one."""
    canaries = catalogue.canaries()
    seeded_ids = [d.id for d in catalogue.defects]
    held_out = [d.id for d in catalogue.defects if d.split == HELD_OUT]
    assert len({d.generator for d in catalogue.defects if d.split == HELD_OUT}) >= 2
    rates = detection_rate({"alpha": held_out[:2]}, canaries,
                           models=["alpha", "beta"], seeded_ids=seeded_ids)
    assert rates["beta"] == 0.0
    assert rates["alpha"] == pytest.approx(2 / len(held_out))


def test_every_difficulty_label_is_true_of_its_plant():
    """The label is re-derived by isolating the plant's line. It is not taken on trust.

    `local` means a reader refutes the plant without leaving its line, so the line
    ALONE must contradict itself; `distributed` means it must not. Checked over 20
    seeds, every plant, both directions.

    This test exists because the labels were WRONG when it was first written.
    Difficulty was being decided from the site before the mutation was chosen, and
    on FIXTURE line 9 -- "`f_s = 480 Hz` is greater than `f_max = 180 Hz`" --
    rescaling f_max UP falsifies the relation on that very line while rescaling it
    DOWN does not. Same site, same operator, 2 different difficulties. 7 of 426
    plants carried the wrong label, all in the damaging direction: easy plants
    counted as hard, inflating the apparent difficulty of the split that gets
    reported. Reproduce by moving the difficulty decision back into
    `collect_sites`.
    """
    checked = 0
    for seed_value in range(20):
        cat = generate_catalogue(FIXTURE, seed_value=seed_value, domain="engineering")
        for defect in cat.defects:
            seeded = seed_one(defect, FIXTURE)
            start, end = sdc.line_bounds(seeded, defect.location.line)
            alone = sdc.line_is_self_refuting(seeded[start:end])
            assert alone == defect.difficulty.startswith("local"), (
                f"seed {seed_value} {defect.id} {defect.defect_class} labelled "
                f"{defect.difficulty} but line-alone refutable={alone}")
            checked += 1
    assert checked > 300, f"only {checked} plants checked"


def test_a_clean_line_must_not_already_refute_itself():
    """Both directions of `line_is_self_refuting`, which the labels rest on."""
    assert not sdc.line_is_self_refuting("the spacing is `480 / 512 = 0.9375` hertz")
    assert sdc.line_is_self_refuting("the spacing is `480 / 512 = 9.3750` hertz")
    assert not sdc.line_is_self_refuting("the margin holds because `10.44 < 25` here")
    assert sdc.line_is_self_refuting("the margin holds because `10.44 > 25` here")
    assert sdc.line_is_self_refuting("`G = 4 dB` in one place and `G = 9 dB` in another")


def test_a_site_on_an_already_broken_line_is_dropped():
    """A plant on a line that already contradicts itself would score the wrong thing.

    The reviewer would find the pre-existing contradiction, and the catalogue would
    credit them with detecting a plant that had nothing to do with it. FIXTURE has
    no such line -- it is arithmetically sound by construction -- so the guard
    needs its own document or it can never fire, and a guard that can never fire is
    indistinguishable from no guard.

    Both halves: a site on the broken line yields no tier, and the same operator on
    a sound line yields a real one.
    """
    broken = "The spacing is `480 / 512 = 0.9375` hertz, although `2 * 3 = 7` was printed.\n"
    sites, _ = collect_sites(broken)
    results = [s for s in sites if s.defect_class == "stated_result_error"]
    assert results, "the holding identity should still be offered as a site"
    assert sdc._measure_difficulty(broken, results[0], "9.3750") == ""

    sound = "The spacing is `480 / 512 = 0.9375` hertz in the current build.\n"
    sites, _ = collect_sites(sound)
    results = [s for s in sites if s.defect_class == "stated_result_error"]
    assert sdc._measure_difficulty(sound, results[0], "9.3750") == sdc.DIFFICULTY_LOCAL


def test_difficulty_tiers_are_balanced_across_the_2_splits(catalogue):
    """The 2026-09-01 failure, closed by construction and checked by the real function.

    Both plants that needed real reasoning landed in the calibration split, which
    `detection_rate` does not report, so p_hat read 1.000 while 40% of the plants
    went unfound. Strata contribute an EVEN number of plants split evenly, so a
    tier cannot land entirely on 1 side.
    """
    balance = split_difficulty_balance(catalogue.canaries())
    assert set(balance) == {HELD_OUT, CALIBRATION}
    assert balance[HELD_OUT] == balance[CALIBRATION]
    assert "unlabelled" not in balance[HELD_OUT]
    assert set(balance[HELD_OUT]) == {"local", "distributed"}


def test_both_splits_carry_the_same_generators(catalogue):
    held = {d.generator for d in catalogue.defects if d.split == HELD_OUT}
    calibration = {d.generator for d in catalogue.defects if d.split == CALIBRATION}
    assert held == calibration


def test_a_document_too_small_for_2_generators_is_refused():
    """The control target really is too small, and the refusal names the reason.

    After 1 plant per line and 1 per symbol, `control_two_distinct_defects.md`
    leaves only the quantity-scale stratum with an even number of members, so the
    held-out split would rest on a single generator. `detection_rate` would then
    measure whether reviewers had learned that 1 operator. Refusing is the correct
    outcome, and it is asserted here rather than assumed.
    """
    text = CONTROL.read_text(encoding="utf-8")
    with pytest.raises(CatalogueGenerationError, match="held-out split uses"):
        generate_catalogue(text, seed_value=1, domain="dsp")


def test_per_stratum_limit_caps_the_catalogue_and_stays_even(catalogue):
    small = generate_catalogue(FIXTURE, seed_value=0, domain="engineering",
                               per_stratum_limit=2)
    assert len(small.defects) < len(catalogue.defects)
    balance = split_difficulty_balance(small.canaries())
    assert balance[HELD_OUT] == balance[CALIBRATION]


# --------------------------------------------------------------------------- #
# Grading a detection                                                          #
# --------------------------------------------------------------------------- #
def test_an_exact_restoration_grades_exact(catalogue):
    defect = _first(catalogue, "operand_error")
    clean_line = FIXTURE.split("\n")[defect.location.line - 1]
    assert check_detection(defect, {"line": defect.location.line,
                                    "corrected_line": clean_line}, FIXTURE) == EXACT


def test_silence_and_a_wrong_line_both_grade_miss(catalogue):
    defect = _first(catalogue, "operand_error")
    seeded = seed_one(defect, FIXTURE).split("\n")
    other = 1 if defect.location.line != 1 else 2
    assert check_detection(defect, {}, FIXTURE) == MISS
    assert check_detection(defect, {"line": defect.location.line,
                                    "corrected_line": seeded[defect.location.line - 1]},
                           FIXTURE) == MISS
    assert check_detection(defect, {"line": other,
                                    "corrected_line": seeded[other - 1]}, FIXTURE) == MISS


def test_the_right_inconsistency_at_the_wrong_span_grades_consistent(catalogue):
    """The outcome a 2-valued grader would have to get wrong in 1 direction or the other.

    An operand plant leaves the line reading "10.44 - 4.3 = 1.74". A reviewer who
    blames the RESULT proposes "10.44 - 4.3 = 6.14": consistent, but not the clean
    text. Scoring it as a hit overstates detection; scoring it as a miss understates
    it. It is its own outcome.
    """
    graded = []
    for defect in catalogue.defects:
        if defect.defect_class != "operand_error":
            continue
        seeded = seed_one(defect, FIXTURE)
        start, end = sdc.line_bounds(seeded, defect.location.line)
        broken = [i for i in identity_candidates(seeded)
                  if start <= i.expr_offset < end and not i.holds]
        if not broken:
            continue
        identity = broken[0]
        repaired_result = sdc.format_like(identity.computed, identity.result_literal)
        if repaired_result is None:
            continue
        line_text = seeded[start:end]
        repaired = (line_text[: identity.result_offset - start] + repaired_result
                    + line_text[identity.result_end - start:])
        graded.append(check_detection(defect, {"line": defect.location.line,
                                               "corrected_line": repaired}, FIXTURE))
    assert graded, "no operand plant supported a consistent-but-misattributed claim"
    assert CONSISTENT in graded, graded


def test_make_verifier_scores_through_canary_seeding_catches(catalogue):
    """The real scorer, driven by execution rather than by wording.

    `catches` is given findings carrying machine-readable claims. Only the model
    whose claim actually restores the document is credited, and the model that
    caught nothing must still appear in `detection_rate` with 0.0 -- the 1 result
    that must never go missing.
    """
    target = _first(catalogue, "stated_result_error")
    clean_line = FIXTURE.split("\n")[target.location.line - 1]
    findings = [
        {"model": "alpha", "claim": {"line": target.location.line,
                                     "corrected_line": clean_line}},
        {"model": "beta", "claim": {"line": target.location.line,
                                    "corrected_line": "nothing to see here"}},
    ]
    verifier = make_verifier(catalogue, FIXTURE)
    caught = catches(findings, catalogue.canaries(), verifier=verifier)
    assert caught == {"alpha": [target.id]}
    assert catches(findings, catalogue.canaries(), verifier=None) == {}


def test_widening_to_consistent_is_a_visible_parameter(catalogue):
    """Accepting a misattributed catch must be a choice in the caller, not a default."""
    defect = None
    claim = None
    for candidate in catalogue.defects:
        if candidate.defect_class != "operand_error":
            continue
        seeded = seed_one(candidate, FIXTURE)
        start, end = sdc.line_bounds(seeded, candidate.location.line)
        broken = [i for i in identity_candidates(seeded)
                  if start <= i.expr_offset < end and not i.holds]
        if not broken:
            continue
        identity = broken[0]
        repaired_result = sdc.format_like(identity.computed, identity.result_literal)
        if repaired_result is None:
            continue
        line_text = seeded[start:end]
        repaired = (line_text[: identity.result_offset - start] + repaired_result
                    + line_text[identity.result_end - start:])
        if check_detection(candidate, {"line": candidate.location.line,
                                       "corrected_line": repaired}, FIXTURE) != CONSISTENT:
            continue
        defect, claim = candidate, {"line": candidate.location.line,
                                    "corrected_line": repaired}
        break
    assert defect is not None
    findings = [{"model": "alpha", "claim": claim}]
    strict = make_verifier(catalogue, FIXTURE)
    wide = make_verifier(catalogue, FIXTURE, accept=(EXACT, CONSISTENT))
    assert catches(findings, catalogue.canaries(), verifier=strict) == {}
    assert catches(findings, catalogue.canaries(), verifier=wide) == {"alpha": [defect.id]}


# --------------------------------------------------------------------------- #
# The catalogue file                                                           #
# --------------------------------------------------------------------------- #
def test_json_round_trip_preserves_every_plant(catalogue):
    restored = catalogue_from_json(json.loads(json.dumps(catalogue_to_json(catalogue))))
    assert fingerprint(restored) == fingerprint(catalogue)
    assert restored.defects == catalogue.defects
    assert [c.ok for c in verify_catalogue(restored, FIXTURE)] == \
           [True] * len(catalogue.defects)


def test_canary_seeding_can_load_the_generated_file(tmp_path, catalogue):
    """The 2 views of 1 file, checked against the reader that will actually read it.

    `load_catalogue` does `Canary(**c)`, which rejects any unknown key, so this
    also proves the ground-truth record is not leaking into the blinded view.
    """
    path = write_catalogue(catalogue, tmp_path / "cat.json")
    loaded = load_catalogue(path)
    assert [c.id for c in loaded] == [d.id for d in catalogue.defects]
    assert all(c.difficulty for c in loaded)
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert set(payload["canaries"][0]) == {
        "id", "domain", "defect_class", "generator", "split", "find", "replace",
        "summary", "difficulty"}
    assert "ground_truth" in payload


def test_writing_the_catalogue_into_the_repository_is_refused(catalogue):
    """A catalogue committed to the tree is a published answer key, and the publication is silent."""
    with pytest.raises(CanaryIntegrityError, match="inside a git work tree"):
        write_catalogue(catalogue, REPO / "bench" / "_sdc_probe.json")
    assert not (REPO / "bench" / "_sdc_probe.json").exists()


def test_writing_and_reading_outside_the_repository_is_allowed(tmp_path, catalogue):
    """The known-GOOD half. Without it the guard could be `raise` on every path."""
    path = write_catalogue(catalogue, tmp_path / "nested" / "cat.json")
    assert path.is_file()
    restored = load_generated_catalogue(path)
    assert fingerprint(restored) == fingerprint(catalogue)


def test_reading_a_catalogue_from_inside_the_repository_is_refused():
    """Refused on the PATH, before the file is even opened.

    Deliberately points at a path that does not exist: containment is decided
    before `is_file()`, so the test needs to create nothing inside the tree. A
    test that writes into the repository to prove the repository is protected has
    to be trusted to clean up after itself, and this suite runs alongside other
    agents' work.
    """
    with pytest.raises(CanaryIntegrityError, match="inside a git work tree"):
        load_generated_catalogue(REPO / "bench" / "_sdc_read_probe.json")


def test_an_unknown_catalogue_format_is_refused(catalogue):
    payload = catalogue_to_json(catalogue)
    payload["format"] = "something-else/9"
    with pytest.raises(CatalogueGenerationError, match="unknown catalogue format"):
        catalogue_from_json(payload)


def test_the_catalogue_records_the_source_it_was_built_from(catalogue):
    """A result is only tied to an article if the article's hash travels with it."""
    import hashlib

    assert catalogue.source_sha256 == hashlib.sha256(FIXTURE.encode("utf-8")).hexdigest()
    seeded, _ = seed(FIXTURE, catalogue.canaries())
    assert catalogue.seeded_sha256 == hashlib.sha256(seeded.encode("utf-8")).hexdigest()


def test_a_document_with_no_sites_is_refused():
    with pytest.raises(CatalogueGenerationError):
        generate_catalogue("Nothing here but prose about nothing at all.\n",
                           seed_value=0, domain="empty")
