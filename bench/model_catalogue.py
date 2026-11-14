"""B21 step 5: the selectable model list, generated rather than hand-written.

HIS DESIGN INTENT, verbatim, 2026-10-17: "model selection should preferably be
a simple box, containing a scrollable list of models available from OpenRouter
and models available on a user's local machine ... with available models on a
user's local machine at the top of this list", with "role management, such as
'worker' ... 'classifier' ... and 'orchestrator'" individually selectable, plus
a recommended list and a note that untested models in a given role carry
unknown performance.

HIS ARGUMENT FOR IT, verbatim: "We clearly cannot make such claims, and then
say 'Oh, btw, that isn't really true. Here is a list of the only models you can
use.'"

THREE SOURCES, LOCAL FIRST AS HE SPECIFIED:
  1. LOCAL    -- models served by an Ollama-compatible daemon on this machine.
  2. REGISTRY -- bench/cdsfl_registry/models/*.toml, the ones this project has
                 policy for. These carry role evidence; everything else does not.
  3. REMOTE   -- OpenRouter's public model list.

THIS MODULE NEVER COSTS MONEY. Listing models is a free endpoint and the probe
is opt-in: `catalogue()` does not touch the network unless `include_remote=True`
is passed, and `--help` never does. That is the founder's standing rule after
15 of 17 runners were found to bill on `--help`.

UNTESTED IS SAID, NOT IMPLIED. Every entry carries `role_evidence`, which is
the roles this project has actually run that model in. An empty list means
unknown performance in every role, and the renderer says so in words.
"""
from __future__ import annotations

import json
import os
import pathlib
import urllib.error
import urllib.request

REPO = pathlib.Path(__file__).resolve().parent.parent
MODELS_DIR = REPO / "bench" / "cdsfl_registry" / "models"
ROLES_DIR = REPO / "bench" / "cdsfl_registry" / "roles"
OPENROUTER_MODELS_URL = "https://openrouter.ai/api/v1/models"
LOCAL_ENDPOINTS = ("http://127.0.0.1:11434/api/tags",)   # Ollama-compatible


def registry_models() -> list[dict]:
    """Models this project holds policy for. Never empty on a healthy tree."""
    out = []
    if not MODELS_DIR.is_dir():
        return out
    for p in sorted(MODELS_DIR.glob("*.toml")):
        out.append({"id": p.stem, "source": "registry", "local": False,
                    "has_policy": True})
    return out


#: HIS RULING OF 2026-11-12, verbatim: *"Verdict. Yes do both. stm"*, against
#: the item asking *"whether the 4 interface roles map onto the harness roles,
#: and whether the credential store is built now or after the runway"*. That is
#: the policy B21 recorded as owed by him and
#: `test_the_functional_vocabulary_is_NOT_declared` refused to let me decide.
#:
#: ★ THE MAP LIVES HERE AND NOT IN THE ROLE FILES, because
#: `bench/tests/test_the_role_layer_cannot_collide_2026-11-02.py` enforces
#: `keys <= {"name", "axis"}` on every role file -- the layer's mechanism is
#: mine, its content is his -- so a `maps_to` key there would be refused, and
#: correctly so.
#:
#: ★ 2 OF THE 4 MAP TO NOTHING, AND THAT IS MEASURED RATHER THAN MISSING. The
#: panel round of 2026-10-31 found the structural and functional vocabularies
#: are 2 DISTINCT DIMENSIONS whose reconciliation is lossy in both directions:
#: `classifier` names no seat position in the structural enum, and `collator`
#: names the HARNESS rather than a seat, so it has no functional counterpart
#: either. `researcher` is newer than that round and has no counterpart
#: measured. Forcing any of them onto `participant` would invent exactly the
#: policy this layer exists not to invent, so the gap is DECLARED as None and
#: a caller must handle it rather than receive a guess.
#:
#: ★ THIS MAP DOES NOT STEER DISPATCH, and that boundary is deliberate.
#: `bench/dm/_role_assignment.py` scores models against the `Role` ENUM in
#: `bench/dm/_types.py`, not against these files, so adding them changes which
#: names the SELECTOR can offer and changes 0 dispatch decisions. Wiring a
#: functional role into that scorer would change how a run selects models,
#: which B21 records as his and which his settings-surface ruling does not
#: cover.
FUNCTIONAL_TO_STRUCTURAL: dict[str, str | None] = {
    "orchestrator": "player_manager",
    "worker": "participant",
    "classifier": None,
    "researcher": None,
}

#: The reverse direction, including the structural name his list has no word
#: for. Declared rather than derived, because the 2 directions are not inverses:
#: the map above is many-to-one with holes.
STRUCTURAL_TO_FUNCTIONAL: dict[str, str | None] = {
    "player_manager": "orchestrator",
    "participant": "worker",
    "collator": None,
}


def role_axis(role: str) -> str | None:
    """The declared axis of `role`, or None when no such role file exists.

    Read from the file rather than from a list in this module, so a role added
    to the registry cannot be invisible here -- the defect `registry.py` records
    at its layer walk, where a 3-item hardcoded list left layer 5 unvalidated.
    """
    import tomllib
    path = ROLES_DIR / f"{role}.toml"
    if not path.is_file():
        return None
    try:
        cfg = tomllib.loads(path.read_text(encoding="utf-8"))
    except Exception:                                              # noqa: BLE001
        return None
    axis = (cfg.get("role") or {}).get("axis")
    return str(axis) if axis else None


def known_roles(axis: str | None = None) -> list[str]:
    """Every role the registry declares, or only those on one axis.

    ★ THE DEFAULT IS UNCHANGED ON PURPOSE. `known_roles()` with no argument
    still returns every role file's stem, so
    `bench/tests/test_b21_steps_are_built_2026-11-09.py` keeps the meaning it
    was written with. The filter is opt-in, which is what a caller wanting the
    4 interface roles needs.

    ★ AND MIXING THE AXES IS THE DEFECT THE FILTER EXISTS FOR. Before the
    functional names were declared, every role file was structural and an
    unfiltered list was unambiguous. It is not any more: 7 names from 2
    vocabularies that do not reconcile would reach the selector as 1 list.
    """
    if not ROLES_DIR.is_dir():
        return []
    stems = sorted(p.stem for p in ROLES_DIR.glob("*.toml"))
    if axis is None:
        return stems
    return [s for s in stems if role_axis(s) == axis]


def structural_for(functional: str) -> str | None:
    """The structural role `functional` maps onto, or None where it maps to none.

    RAISES `KeyError` for a name that is not one of his 4, because silently
    returning None for a typo would be indistinguishable from the 2 genuine
    holes -- and those 2 holes are a measurement this must not blur.
    """
    if functional not in FUNCTIONAL_TO_STRUCTURAL:
        raise KeyError(
            f"{functional!r} is not one of the 4 interface roles "
            f"{sorted(FUNCTIONAL_TO_STRUCTURAL)}; a name outside that set has "
            f"no ruling behind it")
    return FUNCTIONAL_TO_STRUCTURAL[functional]


def local_models(timeout: float = 0.5) -> list[dict]:
    """Models served locally. Fails SILENTLY and fast -- absence is normal."""
    out = []
    for url in LOCAL_ENDPOINTS:
        try:
            with urllib.request.urlopen(url, timeout=timeout) as r:
                data = json.loads(r.read().decode())
        except Exception:                                          # noqa: BLE001
            continue
        for m in data.get("models", []):
            name = m.get("name") or m.get("model")
            if name:
                out.append({"id": name, "source": "local", "local": True,
                            "has_policy": False})
    return out


def remote_models(timeout: float = 5.0) -> list[dict]:
    """OpenRouter's public catalogue. A FREE endpoint; no key, no charge."""
    req = urllib.request.Request(
        OPENROUTER_MODELS_URL, headers={"User-Agent": "cdsfl-model-catalogue"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = json.loads(r.read().decode())
    except (urllib.error.URLError, OSError, ValueError):
        return []
    return [{"id": m.get("id"), "source": "openrouter", "local": False,
             "has_policy": False}
            for m in data.get("data", []) if m.get("id")]


def role_evidence() -> dict[str, list[str]]:
    """Which roles this project has ACTUALLY run each model in.

    Read from the registry's own role configs rather than asserted, so a model
    with no recorded role returns an empty list and the renderer can say
    `unknown performance` instead of implying it is fine.
    """
    import tomllib
    ev: dict[str, list[str]] = {}
    for p in sorted(ROLES_DIR.glob("*.toml")) if ROLES_DIR.is_dir() else []:
        try:
            cfg = tomllib.loads(p.read_text(encoding="utf-8"))
        except Exception:                                          # noqa: BLE001
            continue
        for m in (cfg.get("role") or {}).get("observed_models", []) or []:
            ev.setdefault(str(m), []).append(p.stem)
    return ev


def catalogue(include_remote: bool = False, include_local: bool = True) -> list[dict]:
    """The selectable list, LOCAL FIRST, then registry, then remote.

    `include_remote` defaults to False so that no call path reaches the network
    by accident. Duplicates are merged on `id`, keeping the earliest (and so
    most local) source and OR-ing `has_policy`.
    """
    rows: list[dict] = []
    if include_local:
        rows += local_models()
    rows += registry_models()
    if include_remote:
        rows += remote_models()
    ev = role_evidence()
    seen: dict[str, dict] = {}
    for r in rows:
        k = r["id"]
        if k in seen:
            seen[k]["has_policy"] = seen[k]["has_policy"] or r["has_policy"]
            continue
        r = dict(r)
        r["role_evidence"] = sorted(ev.get(k, []))
        r["untested_note"] = ("" if r["role_evidence"] else
                              "no role evidence in this project: performance "
                              "in any role is unknown")
        seen[k] = r
    order = {"local": 0, "registry": 1, "openrouter": 2}
    return sorted(seen.values(), key=lambda r: (order[r["source"]], r["id"]))


#: ★ B79, HIS RULING OF 2026-11-08, verbatim: *"This is about naming models that
#: no longer exist? Correct? So what we need is a way to dynamically record what
#: models do exist and which are in use, rather than going back and renaming them
#: by hand? fr"*
#:
#: `catalogue()` above answers WHAT EXISTS. This answers WHICH ARE IN USE, and
#: the 2 are different questions: a label can be declared in the registry and
#: never dispatched, or dispatched for months and then quietly dropped. Neither
#: is visible from the registry alone, which is why the record was being
#: corrected by hand -- the failure his ruling names.
#:
#: DERIVED FROM THE RUN ARCHIVE, NEVER FROM A HAND-MAINTAINED LIST. The source
#: is each run's own `completion_signal.json`, which records the `active_models`
#: that run actually dispatched plus its timestamp. So a model falls out of this
#: answer by not being used, with no edit anywhere, which is exactly the
#: "rather than going back and renaming them by hand" he asked for.
def in_use(since: str = "", logs_dir: "pathlib.Path | None" = None) -> list[dict]:
    """Which model labels the run archive shows actually dispatched.

    `since` is an optional ISO date; a run older than it is not counted. Rows
    carry `label`, `runs`, `first`, `last` and `simulated`, sorted by `last`
    descending so the most recently used label is first.

    THE `simulated` FLAG IS STRUCTURAL, NOT A GUESS. A simulated stand-in
    carries the `-SIM` suffix by the project's standing rule that a simulated
    agent is never labelled with a real model's name, so the suffix IS the
    record of what it was. Reading it here rather than inferring from a run's
    config means a row cannot claim a paid dispatch it did not make.
    """
    import collections
    import json as _json

    root = pathlib.Path(logs_dir) if logs_dir else (REPO / "bench" / "logs")
    runs = collections.Counter()
    first: dict = {}
    last: dict = {}
    for sig in sorted(root.glob("*/completion_signal.json")):
        try:
            j = _json.loads(sig.read_text(encoding="utf-8"))
        except Exception:
            continue
        stamp = str(j.get("timestamp") or "")[:10]
        if since and stamp and stamp < since:
            continue
        for label in (j.get("active_models") or []):
            label = str(label).strip()
            if not label:
                continue
            runs[label] += 1
            if stamp:
                if label not in first or stamp < first[label]:
                    first[label] = stamp
                if label not in last or stamp > last[label]:
                    last[label] = stamp
    out = []
    for label, n in runs.items():
        out.append({
            "label": label,
            "runs": n,
            "first": first.get(label, ""),
            "last": last.get(label, ""),
            "simulated": label.upper().endswith("-SIM"),
        })
    out.sort(key=lambda r: (r["last"], r["runs"]), reverse=True)
    return out


def declared_but_unused(since: str = "",
                        logs_dir: "pathlib.Path | None" = None) -> list[str]:
    """Labels the registry declares that the archive shows 0 dispatches for.

    This is the half that cannot be seen from either source alone, and it is
    the answer to his question about names that no longer correspond to
    anything: a label here is declared and never used.
    """
    used = {r["label"].upper()
            for r in in_use(since=since, logs_dir=logs_dir)}
    # A registry label matches a used label either exactly or as its -SIM
    # stand-in, because a simulated run of a seat still evidences that the
    # seat is IN USE as a configuration.
    out = []
    for row in registry_models():
        name = str(row.get("label") or row.get("name") or "").strip()
        if not name:
            continue
        if name.upper() in used or f"{name.upper()}-SIM" in used:
            continue
        out.append(name)
    return sorted(out)


def never_dispatched_for_real(since: str = "",
                              logs_dir: "pathlib.Path | None" = None) -> list[str]:
    """Labels the archive shows ONLY as a simulated stand-in.

    WHY THIS IS SEPARATE FROM `declared_but_unused`, AND WHY THE FIRST
    VERSION OF THIS MODULE HID IT. `declared_but_unused` treats a `-SIM` run
    as evidence that a seat is in use as a CONFIGURATION, which is true and
    which is also how `Fable` disappeared from that answer: it has 15
    simulated runs and **0** real ones, so it was reported as in use while no
    paid dispatch of it has ever been recorded. A seat that has only ever been
    stood in for is exactly the case his ruling is about, so it gets its own
    answer rather than being absorbed into a kinder one.
    """
    rows = in_use(since=since, logs_dir=logs_dir)
    real = {r["label"].upper() for r in rows if not r["simulated"]}
    sim_only = []
    for r in rows:
        if not r["simulated"]:
            continue
        base = r["label"][:-4] if r["label"].upper().endswith("-SIM") else r["label"]
        if base.upper() not in real:
            sim_only.append(base)
    return sorted(set(sim_only))


def render(rows: list[dict]) -> str:
    lines = [f"{len(rows)} selectable model(s). Local first, as he specified.",
             f"roles available -- structural: "
             f"{', '.join(known_roles('structural')) or 'none'}; "
             f"functional (the interface's): "
             f"{', '.join(known_roles('functional')) or 'none'}", ""]
    for r in rows:
        tag = "LOCAL" if r["local"] else r["source"].upper()
        pol = "policy" if r["has_policy"] else "no policy"
        note = f"  -- {r['untested_note']}" if r["untested_note"] else \
               f"  -- run here as: {', '.join(r['role_evidence'])}"
        lines.append(f"  [{tag:10}] {r['id']:38} ({pol}){note}")
    return "\n".join(lines)


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--remote", action="store_true",
                    help="also list OpenRouter's public catalogue (free endpoint)")
    ap.add_argument("--no-local", action="store_true",
                    help="skip the local-daemon probe")
    ap.add_argument("--json", action="store_true")
    #: ★ B79: WHAT EXISTS AND WHAT IS IN USE ARE 2 QUESTIONS, so the CLI
    #: answers both. `--in-use` is the half his 2026-11-08 ruling asked for,
    #: derived from each run's own completion signal rather than from a list
    #: anyone maintains by hand.
    ap.add_argument("--in-use", action="store_true",
                    help="which model labels the run archive shows dispatched")
    ap.add_argument("--since", default="",
                    help="with --in-use, ignore runs older than this ISO date")
    a = ap.parse_args(argv)
    if a.in_use:
        rows = in_use(since=a.since)
        unused = declared_but_unused(since=a.since)
        if a.json:
            print(json.dumps({"in_use": rows, "declared_but_unused": unused},
                             indent=1))
            return 0
        print(f"{'LABEL':20s} {'RUNS':>5s}  {'FIRST':10s} {'LAST':10s} KIND")
        for r in rows:
            kind = "simulated" if r["simulated"] else "paid/real"
            print(f"{r['label']:20s} {r['runs']:5d}  {r['first']:10s} "
                  f"{r['last']:10s} {kind}")
        print(f"\n{len(rows)} label(s) dispatched"
              + (f" since {a.since}" if a.since else " in the whole archive"))
        if unused:
            print(f"declared in the registry but never dispatched: "
                  f"{', '.join(unused)}")
        sim_only = never_dispatched_for_real(since=a.since)
        if sim_only:
            print(f"stood in for but NEVER dispatched for real: "
                  f"{', '.join(sim_only)}")
        _real = [r for r in rows if not r["simulated"]]
        if _real:
            print(f"most recent REAL dispatch: "
                  f"{max(r['last'] for r in _real)}")
        return 0
    rows = catalogue(include_remote=a.remote, include_local=not a.no_local)
    print(json.dumps(rows, indent=1) if a.json else render(rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
