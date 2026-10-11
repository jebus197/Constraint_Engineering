"""An archived run's config is never edited. Its confound is recorded instead.

HIS RULING, 2026-10-11: *"No one ever said we should go back and 'fake the record'. Like every
confound, or deficit we find, when we find them, we mark them explicitly in our docs and correct
them going forward. Verdict fix it. Do exactly that."*

WHAT THIS GUARDS. `burst_mode` was pinned "off" in 43 of 47 configs against his ruling of
2026-10-05. 33 of those describe runs that have already completed. Editing them would falsify
the experimental record; leaving them unmarked would let a future reader quote those results
without knowing the runner was missing a facility. So: the 33 keep their value AND are named in
`bench/directives/universal/archived_run_confounds.json`, and the 10 that had not yet run were
corrected.
"""
from __future__ import annotations

import glob
import json
import os
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
REGISTER = REPO / "bench" / "directives" / "universal" / "archived_run_confounds.json"


def _flat(o, out=None, top=True):
    out = {} if out is None else out
    if isinstance(o, dict):
        for k, v in o.items():
            if isinstance(k, str) and k.startswith("_"):
                continue
            if isinstance(v, (dict, list)):
                _flat(v, out, False)
            elif top or k not in out:
                out[k] = v
    elif isinstance(o, list):
        for v in o:
            _flat(v, out, False)
    return out


def _configs():
    return sorted(glob.glob(str(REPO / "bench/exp*_configs/*.json")))


def _has_archived_run(name: str) -> bool:
    logs = {os.path.basename(p) for p in glob.glob(str(REPO / "bench/logs/*"))}
    return any(name.split("_")[0] in L or name in L for L in logs)


class TestTheConfoundIsRecorded:
    def test_the_register_exists_and_names_the_ruling(self):
        assert REGISTER.is_file(), "the archived-run confound register is missing"
        d = json.loads(REGISTER.read_text(encoding="utf-8"))
        blurb = " ".join(d.get("_what_this_is", []))
        assert "fake the record" in blurb, "the register must carry his words, not a paraphrase"
        assert d.get("confounds"), "a register with no entries records nothing"

    def test_every_archived_run_still_pinned_off_is_named_in_the_register(self):
        """The condition that makes this guard able to fail: an archived run carrying the
        confound but absent from the register is an unmarked confound."""
        d = json.loads(REGISTER.read_text(encoding="utf-8"))
        entry = next(c for c in d["confounds"] if c["id"] == "burst-mode-off-in-archived-runs")
        named = {x["config"] for x in entry["archived_configs_NOT_edited"]}
        unmarked = []
        for f in _configs():
            fl = _flat(json.loads(Path(f).read_text(encoding="utf-8")))
            if fl.get("burst_mode") != "off":
                continue
            name = fl.get("experiment_name") or os.path.basename(f).replace(".json", "")
            if _has_archived_run(name) and os.path.basename(f) not in named:
                unmarked.append(os.path.basename(f))
        assert not unmarked, f"archived runs carry the confound but are not marked: {unmarked}"

    def test_no_config_without_an_archived_run_still_carries_the_confound(self):
        """The correction half: anything that has NOT run must be fixed, not recorded."""
        stragglers = []
        for f in _configs():
            fl = _flat(json.loads(Path(f).read_text(encoding="utf-8")))
            if fl.get("burst_mode") != "off":
                continue
            name = fl.get("experiment_name") or os.path.basename(f).replace(".json", "")
            if not _has_archived_run(name):
                stragglers.append(os.path.basename(f))
        assert not stragglers, (
            f"these have not run and should have been corrected going forward: {stragglers}")

    def test_the_factorial_cells_were_corrected_and_burst_is_not_one_of_its_factors(self):
        """An earlier claim that these 5 were a design decision was WITHDRAWN on measurement.
        The factors are the 2 channels; burst was held constant at "off" across all 4 cells."""
        cells = sorted(glob.glob(str(REPO / "bench/exp52_configs/52_factorial_cell_*.json")))
        if not cells:
            pytest.skip("the exp52 factorial cells are not in this checkout")
        rows = [_flat(json.loads(Path(f).read_text(encoding="utf-8"))) for f in cells]
        varying = {k for k in set().union(*[set(r) for r in rows])
                   if len({str(r.get(k)) for r in rows}) > 1}
        assert "burst_mode" not in varying, (
            "burst_mode now VARIES across the factorial cells, so it has become a factor and "
            "correcting it would change the design -- this needs his ruling, not a patch")
        for r in rows:
            assert r.get("burst_mode") != "off", "a factorial cell is still pinned off"
