"""Every policy layer that EXISTS must be validated, derived from disk.

THE DEFECT THIS HOLDS SHUT, found by execution 2026-11-09 while measuring which
of B21's 5 steps were built. `validate_all_policies()` enumerated `domains`,
`models` and `tasks` BY NAME. B21's step 3 added a 4th layer,
`bench/cdsfl_registry/roles/`, with 3 configs, and the 3-item list was not
updated -- so the validator returned 17 keys whose layer prefixes were exactly
`['domain', 'model', 'universal']` and reported 0 role entries. A whole policy
layer was invisible to the thing whose job is to check every layer.

WHY IT IS WORSE THAN AN OMISSION. B21's step 4 wires this function as a
run-level preflight that reports every missing registration at once AND REFUSES
THE RUN. A preflight that refuses on 3 layers while silently skipping a 4th
reads as a clean bill of health for the layer it never examined.

★ THE ASSERTION IS DERIVED AND NOT A LIST, WHICH IS THE WHOLE LESSON. A guard
that said "roles must be validated" would need editing when layer 5 arrives --
the identical failure, one layer later. This walks the registry directory and
requires every subdirectory holding `*.toml` to be represented in the results,
so the next layer is covered on the day it is created. Pinning a SET and not a
COUNT, recorded 2026-10-16.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from bench.cdsfl_registry import registry as R        # noqa: E402


def _layer_dirs() -> list[pathlib.Path]:
    """Every registry subdirectory that actually holds policy configs."""
    return sorted(p for p in R.REGISTRY_DIR.iterdir()
                  if p.is_dir() and any(p.glob("*.toml")))


def _synthetic_registry(tmp_path: pathlib.Path, layer: str,
                        files: dict[str, str]) -> pathlib.Path:
    """A registry whose `universal.toml` is the REAL one.

    ★ THE FIRST VERSION OF THESE FIXTURES WROTE A MINIMAL `[limits]` UNIVERSAL
    AND EVERY TEST USING IT FAILED FOR A REASON THAT HAD NOTHING TO DO WITH THE
    SUBJECT. `_check_monotonicity` requires `constraints.anti_deference`,
    `convergence.method` and `protocol.stop_rule` among others, so a stub
    universal is itself a HARD violation and `validate_all_policies()` returns
    early with only that key -- which looks exactly like the layer-coverage
    defect under test. A fixture that manufactures the failure it is probing
    for proves nothing, which is recorded against 2026-11-02.

    So the real universal is copied in and only the OVERLAY layer is synthetic.
    """
    reg = tmp_path / "registry"
    (reg / layer).mkdir(parents=True)
    real = (R.REGISTRY_DIR / "universal.toml").read_text(encoding="utf-8")
    (reg / "universal.toml").write_text(real, encoding="utf-8")
    for name, body in files.items():
        (reg / layer / name).write_text(body, encoding="utf-8")
    return reg


class TestEveryLayerOnDiskIsValidated:
    def test_there_is_at_least_one_layer_to_check(self):
        """Anti-vacuity: an empty registry would make every test below pass."""
        dirs = _layer_dirs()
        assert dirs, (
            "no registry subdirectory holds any .toml, so the checks below "
            "would be vacuous. If the registry moved, fix this guard")
        assert len(dirs) >= 3, [p.name for p in dirs]

    def test_every_layer_directory_is_represented_in_the_results(self):
        """THE DEFECT. roles/ existed with 3 configs and 0 were validated."""
        res = R.validate_all_policies()
        prefixes = {k.split("/")[0] for k in res if "/" in k}
        missing = []
        for d in _layer_dirs():
            n = len(list(d.glob("*.toml")))
            singular = {"domains": "domain", "models": "model",
                        "tasks": "task", "roles": "role"}.get(
                            d.name, d.name.rstrip("s"))
            if singular not in prefixes:
                missing.append(f"{d.name} ({n} config(s), expected prefix "
                               f"'{singular}')")
        assert not missing, (
            f"these policy layers exist on disk and are NOT validated: "
            f"{missing}. validate_all_policies() reported prefixes "
            f"{sorted(prefixes)}. A preflight silent on a layer reads as a "
            f"clean bill of health for a layer it never examined")

    def test_every_config_file_gets_its_own_result(self):
        """Not just the layer: each file. A layer validated 1-of-3 is not validated."""
        res = R.validate_all_policies()
        for d in _layer_dirs():
            singular = {"domains": "domain", "models": "model",
                        "tasks": "task", "roles": "role"}.get(
                            d.name, d.name.rstrip("s"))
            for f in sorted(d.glob("*.toml")):
                key = f"{singular}/{f.stem}"
                assert key in res, (
                    f"{key} exists on disk and has no result; "
                    f"validate_all_policies() returned {len(res)} key(s)")

    def test_the_partition_closes(self):
        """1 universal plus every config file, and nothing else."""
        res = R.validate_all_policies()
        expected = 1 + sum(len(list(d.glob("*.toml"))) for d in _layer_dirs())
        assert len(res) == expected, (
            f"{len(res)} result(s) against {expected} expected (1 universal "
            f"plus every config); a key is duplicated or invented")


class TestAnUnreadableFileIsNotAPolicyViolation:
    def test_a_malformed_config_is_reported_as_unreadable(self, tmp_path,
                                                          monkeypatch):
        """AN INFRASTRUCTURE FAILURE REPORTED AS A POLICY ERROR MISLEADS.

        The original handler was `except (PolicyViolationError, Exception)`,
        which catches Exception -- subsuming the first name and making the
        tuple decorative -- and wrote a TOML parse failure into the same field
        as a monotonicity violation. A reader is then told the config is wrong
        when the truth is that it could not be read.
        """
        reg = _synthetic_registry(
            tmp_path, "models", {"broken.toml": "this is not = = valid toml\n"})
        monkeypatch.setattr(R, "REGISTRY_DIR", reg)
        res = R.validate_all_policies()
        assert "model/broken" in res, res
        v = res["model/broken"]
        assert v != "ok", v
        assert "UNREADABLE" in v.upper(), (
            f"a malformed config was reported as {v!r}, which a reader cannot "
            f"tell from a policy violation")

    def test_a_sound_registry_still_passes_clean(self, tmp_path, monkeypatch):
        """DISCRIMINATION: the check above must not pass by always failing."""
        reg = _synthetic_registry(tmp_path, "roles", {"fine.toml": "\n"})
        monkeypatch.setattr(R, "REGISTRY_DIR", reg)
        res = R.validate_all_policies()
        assert res.get("role/fine") == "ok", res
        assert all(v == "ok" for v in res.values()), res


class TestTheRepairIsDerivedNotEnumerated:
    def test_a_new_layer_needs_no_edit_here(self, tmp_path, monkeypatch):
        """THE POINT. A 5th layer invented in a fixture must be validated.

        If this fails, the validator is enumerating names again and the next
        layer will be skipped exactly as `roles` was.
        """
        reg = _synthetic_registry(tmp_path, "widgets", {"alpha.toml": "\n"})
        monkeypatch.setattr(R, "REGISTRY_DIR", reg)
        res = R.validate_all_policies()
        assert "widget/alpha" in res, (
            f"a layer directory the code has never heard of was not validated; "
            f"got {sorted(res)}. The validator is enumerating layer names "
            f"again, so the next layer added will be skipped as roles was")

class TestAPreflightMustNotCertifyAnUnusableRegistry:
    """THE CONSEQUENCE, DEMONSTRATED RATHER THAN ARGUED.

    The checks above establish that a layer is skipped. This one shows what
    being skipped COSTS, and it is the test worth keeping if only one survives.

    The role layer is DELIBERATELY INERT unless a caller asks for it --
    `scripts/the_role_layer_changes_nothing_until_asked_2026-11-02.py` proves
    that without a role 0 files under `roles/` are read and the rendered output
    is byte-identical. That design makes the validator gap WORSE, not milder: a
    latent layer is exactly the one a preflight must check, because nothing
    else will notice until a run asks for it and dies mid-flight.

    MEASURED on the unrepaired code 2026-11-09: a role config relaxing a HARD
    requirement gave `validate_all_policies() == {'universal': 'ok'}` -- the
    role not mentioned at all -- while `load_effective_policy(role=...)` raised
    `PolicyViolationError: protocol.stop_rule: got 'whatever_you_like',
    required 'counting_plus_verify'`. Preflight green, run red. B21's step 4
    would have shipped that.
    """

    def test_a_violating_role_is_caught_by_the_preflight_not_by_the_run(
            self, tmp_path, monkeypatch):
        reg = _synthetic_registry(tmp_path, "roles", {
            "saboteur.toml": '[protocol]\nstop_rule = "whatever_you_like"\n'})
        monkeypatch.setattr(R, "REGISTRY_DIR", reg)

        # the run DOES refuse it -- that half was never broken
        with pytest.raises(R.PolicyViolationError):
            R.load_effective_policy(domain="software", role="saboteur")

        # and the PREFLIGHT must refuse it too, which is the half that was
        res = R.validate_all_policies()
        assert "role/saboteur" in res, (
            f"the preflight does not mention the violating role at all; it "
            f"returned {res}. A registry that cannot be used was certified")
        assert res["role/saboteur"] != "ok", (
            f"the preflight passed a role config that makes a run raise: "
            f"{res['role/saboteur']!r}")
        assert "stop_rule" in res["role/saboteur"], (
            f"the preflight refuses it but does not say WHICH constraint, so a "
            f"reader cannot act on it: {res['role/saboteur']!r}")

    def test_a_sound_role_is_not_refused(self, tmp_path, monkeypatch):
        """DISCRIMINATION: the check above must not pass by refusing everything."""
        reg = _synthetic_registry(tmp_path, "roles", {"ok.toml": "\n"})
        monkeypatch.setattr(R, "REGISTRY_DIR", reg)
        res = R.validate_all_policies()
        assert res.get("role/ok") == "ok", res
        pol = R.load_effective_policy(domain="software", role="ok")
        assert isinstance(pol, dict) and pol, pol

