"""B21's role layer: it exists, it raises loudly, and it CANNOT collide.

HIS DESIGN, quoted in B21: *"role management, such as 'worker'... 'classifier'...
and 'orchestrator'"* individually selectable. B21 records that the 4-layer policy
engine has layers for universal constraints, domain, task and model and NO LAYER
FOR ROLE, and that this is the one part of his design with no home in the 4.

WHAT THIS FILE ADDS THAT THE MEASUREMENT DID NOT.
`scripts/what_does_layer_order_actually_decide_2026-10-30.py` already measured
B21's precedence question and answered it: "Keys the ORDER actually decides: 0",
because 0 of 60 (domain, model) pairs share any leaf dotpath, Wilson 95%
[0.000000, 0.060172], and monotonicity compares against MODULE CONSTANTS rather
than the previous layer, so the protected set is order-independent BY
CONSTRUCTION.

BUT IT ALSO WARNS, in its own words, that the layers are disjoint *"by
convention, not by any enforced rule -- nothing in the merge engine requires
it"*. That is the gap this file closes. A convention that nothing enforces is one
role file away from making precedence matter again, and precedence is a question
B21 reserves for the panel.

I ALSO REBUILT A WEAKER VERSION OF THAT MEASUREMENT BEFORE FINDING IT, which is
recorded here because it is the 7th near-rebuild of the same night and the only
one I actually carried out rather than caught in time.

WHY RAISE AND NOT SKIP. B21 names 2 precedents for an absent layer; execution
finds 3 -- a missing MODEL file RAISES, a missing TASK file is SILENT, an unknown
DOMAIN WARNS. RAISE matches the model layer, which is what a role most resembles,
and his ruling of 2026-11-01 is explicit that a registration a researcher gets
wrong must fail loudly rather than default.

WHAT IS DELIBERATELY NOT HERE: the role files' CONTENT, which is policy and his,
and the FUNCTIONAL vocabulary, which composer.py records as "POLICY and not
plumbing".
"""
from __future__ import annotations

import pathlib
import sys
import tomllib

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from bench.cdsfl_registry import registry as R          # noqa: E402

REG = REPO / "bench" / "cdsfl_registry"
STRUCTURAL = {"collator", "player_manager", "participant"}


def _leaves(d, pre=""):
    out = set()
    for k, v in (d or {}).items():
        p = f"{pre}.{k}" if pre else k
        if isinstance(v, dict):
            out |= _leaves(v, p)
        else:
            out.add(p)
    return out


def _layer_leaves(subdir: str) -> set[str]:
    out: set[str] = set()
    d = REG / subdir
    if d.is_dir():
        for f in d.glob("*.toml"):
            out |= _leaves(tomllib.loads(f.read_text()))
    return out


class TestTheLayerExistsAndIsReached:

    def test_the_role_layer_directory_exists_with_the_structural_roles(self):
        d = REG / "roles"
        assert d.is_dir(), "roles/ is gone, so the layer has no files to load"
        have = {f.stem for f in d.glob("*.toml")}
        assert STRUCTURAL <= have, (
            f"the settled structural roles are {STRUCTURAL} and roles/ holds "
            f"{have}; a role the `Role` literal declares has no file")

    def test_the_signature_takes_a_role(self):
        import inspect
        sig = inspect.signature(R.load_effective_policy)
        assert "role" in sig.parameters, "load_effective_policy takes no role"
        names = list(sig.parameters)
        assert names.index("role") > names.index("model"), (
            "`role` must come AFTER `model`: engine.py calls "
            "load_effective_policy(domain, task_id, model) POSITIONALLY, so an "
            "earlier parameter would silently receive the model name")

    def test_passing_a_role_actually_changes_the_merged_policy(self):
        """Otherwise the layer is an addition nothing reaches."""
        without = R.load_effective_policy(domain="mathematics", model="opus_4_6")
        withrole = R.load_effective_policy(domain="mathematics", model="opus_4_6",
                                           role="collator")
        assert withrole != without, "the role layer changed nothing"
        assert set(withrole) - set(without) == {"role"}, (
            f"the role layer added {set(withrole) - set(without)}, not just role")


class TestItCannotCollide:

    def test_the_role_namespace_is_disjoint_from_every_other_layer(self):
        """THE ENFORCEMENT. The producer measured the disjointness and warned it
        was convention only. This makes it a rule."""
        roles = _layer_leaves("roles")
        assert roles, "no role leaves at all, so this test is vacuous"
        for other in ("domains", "models", "tasks"):
            clash = roles & _layer_leaves(other)
            assert not clash, (
                f"a role file and a {other[:-1]} file both set {sorted(clash)}. "
                f"Layer ORDER now decides a key, which is the question B21 "
                f"reserves for the panel -- take it to him rather than choosing.")
        univ = _leaves(tomllib.loads((REG / "universal.toml").read_text()))
        clash = roles & univ
        assert not clash, (
            f"a role file sets {sorted(clash)}, which universal.toml also sets")

    def test_every_role_file_writes_only_under_role(self):
        for f in (REG / "roles").glob("*.toml"):
            top = set(tomllib.loads(f.read_text()))
            assert top == {"role"}, (
                f"{f.name} writes top-level {sorted(top)}; the role layer owns "
                f"the `role` namespace and nothing else")

    def test_order_still_decides_nothing(self):
        """The producer's result, re-asserted with the 5th layer present."""
        a = R.load_effective_policy(domain="mathematics", model="opus_4_6",
                                    role="participant")
        b = R.load_effective_policy(domain="mathematics", model="opus_4_6",
                                    role="participant")
        assert a == b, "the merge is not deterministic"
        roles = _layer_leaves("roles")
        merged = _leaves(a)
        assert roles <= merged, (
            f"role leaves {sorted(roles - merged)} did not survive the merge, so "
            f"another layer is overwriting them")


class TestAnUnknownRoleFailsLoudly:

    def test_it_raises_like_the_model_layer(self):
        with pytest.raises(FileNotFoundError) as ei:
            R.load_effective_policy(domain="mathematics", role="not_a_real_role")
        msg = str(ei.value)
        assert "Role config not found" in msg
        assert "Available roles" in msg, (
            "his ruling was that a failed registration must be raised loudly "
            "AND be trivial to fix; the message must name what IS available")

    def test_the_3_absence_behaviours_are_still_what_was_measured(self):
        """B21 named 2 precedents; execution found 3. If these change, the choice
        of RAISE for a role needs re-arguing."""
        with pytest.raises(FileNotFoundError):
            R.load_effective_policy(domain="mathematics", model="not_a_model")
        # a missing task is SILENT
        ok = R.load_effective_policy(domain="mathematics", task_id="no-such-task")
        assert ok, "a missing task file is no longer silent"


class TestWhatIsDeliberatelyAbsent:

    def test_the_functional_vocabulary_is_NOT_declared(self):
        """His worker/classifier/orchestrator mapping is POLICY and still his."""
        have = {f.stem for f in (REG / "roles").glob("*.toml")}
        for his in ("worker", "classifier", "orchestrator"):
            assert his not in have, (
                f"roles/{his}.toml exists. Which declared member each of his "
                f"functional names maps to is the definition B21 records as "
                f"still owed by him; creating the file decides it for him.")

    def test_no_role_file_invents_policy(self):
        for f in (REG / "roles").glob("*.toml"):
            d = tomllib.loads(f.read_text())
            keys = set(d.get("role", {}))
            assert keys <= {"name", "axis"}, (
                f"{f.name} sets {sorted(keys - {'name', 'axis'})}. The layer's "
                f"mechanism is mine; its content is his.")
