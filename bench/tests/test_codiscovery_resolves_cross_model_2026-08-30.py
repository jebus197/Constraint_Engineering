"""Co-discovery must record the CROSS-MODEL case, which is the only case it is for.

THE DEFECT, MEASURED 2026-08-30 ON THE FIRST RUN AFTER THE RECORDER LANDED
--------------------------------------------------------------------------
``record_codiscovery`` was added 2026-08-23 to close a measured defect: across
566 findings of the modern arc, ``source_aliases`` held exactly 1.00 entry per
finding and ZERO findings were raised by two or more models. Its own docstring
names the cause -- ``_alias_map`` is keyed ``model_id:finding_id``, so a
model-keyed lookup "can only ever match the SAME model re-raising its own
finding across rounds -- never a different model raising the same defect."

The call site then did exactly that. It resolved with
``lookup_alias(<the DUPLICATE's model>, <the ORIGINAL's finding_id>)``. In a
cross-model duplicate those belong to different models, so the lookup always
returned None; the fallback was a raw finding_id that is not a key of
``registry.entries``; the ``if _cid in registry.entries`` guard never passed;
and the recorder was never reached. The fix reproduced the defect it documented.

MEASURED on the v3.1 simulated run (bench/logs/sim45_memory_20260830T161215Z):
17 duplicate records, every ``duplicate_of`` a foreign-model finding ID
(``Fable-SIM_F003``, ``DeepSeek-SIM_F002``, ``Gemini-SIM_F001`` ...), NK v2
reporting 7 intra-round duplicates -- and ``source_aliases`` still exactly 1 on
all 19 entries. No error was logged, because nothing failed; the guard simply
never opened.
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import reference_runner_v3 as R


def _finding(model_id, finding_id, desc="off-by-one in _prune"):
    return R.Finding(finding_id=finding_id, model_id=model_id, round_idx=0,
                     flaw_class="code_behavioral", severity=0.5,
                     abstraction_index=0.5, description=desc)


def _resolve(reg, dup_model, duplicate_of):
    """The production call site's resolution chain, verbatim."""
    return (reg.lookup_alias(dup_model, duplicate_of)
            or reg.lookup_alias_any(duplicate_of)
            or duplicate_of)


class TestCrossModelCoDiscovery:
    def test_a_foreign_model_duplicate_resolves_to_the_canonical(self):
        reg = R.FindingRegistry()
        cid = reg.register(_finding("Gemini-SIM", "Gemini-SIM_F001"), "Gemini-SIM")
        assert _resolve(reg, "Codex-SIM", "Gemini-SIM_F001") == cid

    def test_and_the_recorder_is_actually_reached(self):
        reg = R.FindingRegistry()
        cid = reg.register(_finding("Gemini-SIM", "Gemini-SIM_F001"), "Gemini-SIM")
        resolved = _resolve(reg, "Codex-SIM", "Gemini-SIM_F001")
        assert resolved in reg.entries          # the guard the old code failed
        reg.record_codiscovery(resolved, "Codex-SIM", "Codex-SIM_F009", 0.91)
        assert len(reg.entries[cid]["source_aliases"]) == 2

    def test_the_old_model_keyed_lookup_alone_still_misses(self):
        """Pins the diagnosis, so a later 'simplification' cannot undo it."""
        reg = R.FindingRegistry()
        reg.register(_finding("Gemini-SIM", "Gemini-SIM_F001"), "Gemini-SIM")
        assert reg.lookup_alias("Codex-SIM", "Gemini-SIM_F001") is None


class TestItDoesNotOverReach:
    def test_same_model_re_raise_is_unchanged(self):
        reg = R.FindingRegistry()
        cid = reg.register(_finding("A", "A_F1"), "A")
        assert reg.lookup_alias("A", "A_F1") == cid

    def test_an_ambiguous_id_is_refused_not_guessed(self):
        """Two models minting one local ID must not attribute to an arbitrary one."""
        reg = R.FindingRegistry()
        reg.register(_finding("A", "F1", "first"), "A")
        reg.register(_finding("B", "F1", "second"), "B")
        assert reg.lookup_alias_any("F1") is None

    def test_a_suffix_is_not_a_match(self):
        """'F1' must not resolve through 'A:XF1' -- the separator is part of the key."""
        reg = R.FindingRegistry()
        reg.register(_finding("A", "XF1"), "A")
        assert reg.lookup_alias_any("F1") is None

    def test_empty_and_unknown_ids(self):
        reg = R.FindingRegistry()
        reg.register(_finding("A", "A_F1"), "A")
        assert reg.lookup_alias_any("") is None
        assert reg.lookup_alias_any("nope") is None


class TestTheCallSiteUsesIt:
    def test_production_call_site_falls_back_to_the_model_agnostic_lookup(self):
        src = (pathlib.Path(__file__).resolve().parents[1]
               / "reference_runner_v3.py").read_text(encoding="utf-8")
        i = src.index("registry.record_codiscovery(")
        window = src[max(0, i - 800):i]
        assert "lookup_alias_any(" in window, (
            "the co-discovery call site no longer resolves model-agnostically; "
            "cross-model duplicates will silently stop being recorded again"
        )
