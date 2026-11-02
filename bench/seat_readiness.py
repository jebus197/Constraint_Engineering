"""Is a seat ready to be dispatched, and if not, exactly what is missing?

HIS ASK, 2026-11-02, verbatim: *"researchers should be able to search for/add
models trivially from a search box in the UX, enter all their API keys, and logins
for OpenRouter, and for the various model vendors they might have access to, and
from any local models they have on their machines. They shouldn't need to think,
or concern themselves with the underlying mechanics of how this works in reality.
Which is what I mean by making the process trivial."* And on doing it: *"This may
require you to make some adjustments to the existing UX work as required. But
there is no reason why you shouldn't do it."*

AND IT IS THE BACKEND HALF OF AN AUTHORISATION THAT REACHED NO ENTRY. His ticket
of 2026-10-20 reads *"I am not asking you to build the UX now. [...] you can build
the UX backend, so that the eventual UX can map cleanly on to it"*. That ticket was
merged into entry B20 on `task_ref` alone without checking the subject matched, so
the UX backend existed as authorised work in exactly 1 place in the project -- a
merged ticket -- and reached no entry at all.

WHAT WAS ACTUALLY MISSING, AND IT IS NOT A SEARCH BOX. A seat needs TWO
independent things and the project had no surface showing either:

  1. A ROUTE -- a `ModelConfig` carrying `api` and `model_id`, plus whatever
     credential that route needs.
  2. CALIBRATION -- an entry in each of the 5 per-model tables
     `bench/model_admission.py` writes.

The Fable seat had (1) and was missing 4 of (2), and that gap was found by a run
FAILING rather than by anything asking. This module is the asking.

★ IT NEVER READS A CREDENTIAL'S VALUE AND NEVER DISPATCHES, and both are
deliberate rather than cautious.

  * On values: `onboarding_dual_purpose` records that the onboarding script
    "never prints key values", and the same must hold here, because this data is
    destined for a UX surface. Readiness is reported as a BOOLEAN over
    `os.environ`, so no value can reach a caller, a log or a screen.
  * On dispatching: `bench/seat_aliveness_2026-10-06.py` can probe a route, and
    its own docstring is explicit that "a probe IS a dispatch" and that it "does
    not and must not carry its own authorisation to dispatch anything". The
    standing rule is that no paid dispatch happens without the founder's express
    authorisation, so a readiness REPORT must not probe. Probing stays the
    separately-authorised act it already is.

  So this module answers "is it configured?", never "does it answer?", and the
  2 questions are kept apart because only 1 of them is free.

WHY THE CREDENTIAL MAP IS CHECKED RATHER THAN TRUSTED. The map below is a SECOND
declaration of something the dispatch code already states by reading env vars in
8 places, and 2 declarations of 1 fact is exactly the drift this project keeps
finding. So `bench/tests/test_a_seat_declares_what_it_is_missing_2026-11-02.py`
lifts the env var names out of the dispatcher's own syntax tree and compares them
with this map. If a route's credential is renamed, the test fails rather than the
UX quietly reporting a seat as unconfigured.
"""
from __future__ import annotations

import os
import pathlib
import sys
from typing import Any

#: Run directly (`python3 bench/seat_readiness.py`) as well as imported. A
#: researcher checking why a seat will not dispatch should not have to know to
#: invoke it as a module, which is the same "trivial to use" property his ask is
#: about. The project's own convention, as in `bench/audit_closing_window.py`.
REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

#: api -> the environment variables that route will accept, in preference order.
#: An EMPTY tuple means the route carries no credential of its own: `claude_cli`
#: and `codex_exec` run through a CLI on the founder's Max subscription, and
#: `sim` reaches no vendor at all. Empty is therefore "nothing to configure",
#: NOT "unconfigured", and the 2 must never be collapsed -- reporting a CLI seat
#: as missing a key would send a researcher hunting for a key that does not exist.
API_CREDENTIALS: dict[str, tuple[str, ...]] = {
    "openrouter": ("OPENROUTER_API_KEY",),
    "deepseek": ("DEEPSEEK_API_KEY",),
    "google": ("GEMINI_API_KEY", "GOOGLE_API_KEY"),
    "claude_cli": (),
    "codex_exec": (),
    "sim": (),
}

#: Routes that reach no vendor, so a run over them spends nothing.
SIMULATED_APIS = frozenset({"sim"})


def _dotenv_names() -> frozenset[str]:
    """The KEY NAMES defined in the repository's .env, and nothing else.

    ★ WHY THIS EXISTS, and it is a defect found by running the report rather than
    by reading it. The first version consulted `os.environ` alone and reported
    the deepseek, google and openrouter credentials as ABSENT -- because this
    project loads `.env` PER MODULE (`bench/build_experiment_run.py:41` and 4
    others each do their own), so a process that has not loaded it sees nothing.
    A researcher told their key is missing when it is sitting in `.env` would go
    looking for a key they already have, which is the opposite of the "trivial"
    property the whole surface is for.

    Only the part before the first `=` is kept. The value is never parsed, never
    stored and never returned, so no caller of this module can obtain one.
    """
    f = REPO_ROOT / ".env"
    names: set[str] = set()
    try:
        for line in f.read_text(errors="replace").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            name = line.split("=", 1)[0].strip()
            if name.startswith("export "):
                name = name[len("export "):].strip()
            if name:
                names.add(name)
    except OSError:
        return frozenset()           # no .env is a normal checkout, not an error
    return frozenset(names)


def credential_source(api: str) -> str | None:
    """Where the route's credential is declared: environment, dotenv, or None.

    None means either "nothing to configure" (a CLI or simulated route) or
    "nowhere" -- `credential_present` distinguishes those 2, and this answers the
    different question of which surface a researcher should look at.
    """
    names = API_CREDENTIALS.get(api) or ()
    if not names:
        return None
    if any(os.environ.get(n, "").strip() for n in names):
        return "environment"
    if set(names) & _dotenv_names():
        return "dotenv"
    return None


def credential_present(api: str) -> bool | None:
    """True / False for a route that needs a credential, None for one that does not.

    ★ THE 3-VALUED RETURN IS THE POINT. A 2-valued answer forces a CLI route to be
    reported either as configured (misleading: nothing was checked) or as missing
    (wrong: nothing is needed). None says "not applicable", which is what a UX
    should render as a dash rather than a warning.

    Only membership and emptiness are tested. The value is never read out.
    """
    names = API_CREDENTIALS.get(api)
    if names is None:
        return False                 # an unknown route cannot be called at all
    if not names:
        return None                  # CLI or simulated: nothing to configure
    return credential_source(api) is not None


def _tables() -> list[tuple[str, dict, str]]:
    """REMOVED as a second declaration; see `registration_gaps`.

    This function used to list the 5 tables and WHICH KEY each is keyed on, which
    `bench/model_admission.py` already states. The copy got it wrong -- it keyed
    all 5 on the composer key, where `INITIAL_FINGERPRINTS` and `MODEL_SPECS` are
    keyed on the LABEL -- and reported 6 of 6 seats as gapped. The keying is now
    imported from `model_admission.registration_targets`, so there is 1
    declaration and this cannot drift again.
    """
    raise NotImplementedError(
        "the table keying is declared once, in "
        "model_admission.registration_targets; call registration_gaps")


def composer_key(label: str) -> str:
    """The phenotype key a seat label resolves to, via the live map.

    The map answers `.get(label, label)`, so a seat with no entry resolves to its
    own label and then misses every key-ed table -- which is precisely how the
    Fable gap stayed invisible.
    """
    from bench.cdsfl_registry import composer as co
    return str(co.COMPOSER_MODEL_MAP.get(label, label))


def registration_gaps(label: str) -> list[str]:
    """Which of the 5 tables have no entry for this seat. Empty means complete.

    The tables AND their key choice come from `model_admission`, the module that
    writes them, so a report of a gap and the act of filling it cannot disagree
    about what a gap is.
    """
    from bench.model_admission import registration_targets

    ckey = composer_key(label)
    missing = []
    for table, key, _field, _decode, where in registration_targets(label, ckey):
        if key not in table:
            missing.append(where)
    return missing


def known_seats() -> list[str]:
    """Every seat label the calibration tables know, sorted.

    `MODEL_SPECS` is the canonical label space -- the composer map holds both
    labels and phenotype keys as keys, so using it would double-count.
    """
    from bench import runner_core as rc
    return sorted(rc.MODEL_SPECS)


def seat_rows(models: Any = None) -> list[dict]:
    """One row per seat, saying exactly what is missing. Reads only.

    `models` may be an iterable of ModelConfig-like objects, which supplies the
    ROUTE half; seats with no such config are still listed, with `api` None, so a
    calibrated-but-unrouted seat is visible rather than silently absent.
    """
    # ★ `models is None` MEANS "NOT ASKED", NOT "ABSENT", and conflating the 2 is
    # the error this project keeps making in other forms. Routes are built per
    # run from a run's own config -- `MODEL_ROSTER` is a label-to-DESCRIPTION map,
    # not a list of ModelConfigs -- so there is no module-level roster to read.
    # The first version reported all 6 seats as "NO ROUTE" when none had been
    # supplied, which reads as a defect in the project rather than as a question
    # that was never put.
    asked_about_routes = models is not None
    by_label: dict[str, Any] = {}
    for m in (models or ()):
        lbl = getattr(m, "label", None)
        if lbl:
            by_label[str(lbl)] = m

    rows = []
    for label in sorted(set(known_seats()) | set(by_label)):
        cfg = by_label.get(label)
        api = getattr(cfg, "api", None) if cfg is not None else None
        gaps = registration_gaps(label)
        cred = credential_present(api) if api else None
        rows.append({
            "label": label,
            "composer_key": composer_key(label),
            "api": api,
            "model_id": getattr(cfg, "model_id", None) if cfg is not None else None,
            "has_route": (cfg is not None) if asked_about_routes else None,
            "simulated": bool(api in SIMULATED_APIS) if api else False,
            "credential": cred,
            "credential_source": credential_source(api) if api else None,
            "credential_names": list(API_CREDENTIALS.get(api or "", ())),
            "registration_gaps": gaps,
            "registered": not gaps,
            # READY means: calibrated, routed, and whatever credential the route
            # needs is present. It does NOT mean the route answers -- that costs
            # money to establish and is a separately authorised act.
            # READY requires a route to have been SUPPLIED and found. With no
            # roster supplied the answer is None -- unknown -- never True.
            "ready": (None if not asked_about_routes
                      else ((not gaps) and cfg is not None and cred is not False)),
        })
    return rows


def roster_declarations_agree(dispatched: Any, counted: Any) -> dict:
    """Do the 2 roster declarations agree? Report the difference BOTH ways.

    ★ WHY THIS BELONGS ON A PRE-RUN SURFACE. The roster is declared TWICE:
    `exp_config.models` holds the ModelConfigs actually dispatched, and
    `cfg.models` is a separate list of labels whose default is a hardcoded 5 --
    the panel from before Fable joined. The runner's own comment states the
    consequence: "Every count, every per-model denominator and every
    `set(cfg.models) - {source}` in this file reads the second list."

    FOUND 2026-08-30 BY THE FIRST SIMULATED RUN TO DRIVE `run_experiment`: 6
    ModelConfigs were supplied, `cfg.models` was left at its default, and the run
    REPORTED A 5-MODEL PANEL WHILE DISPATCHING A SIXTH, with nothing warning at
    all. The runner now logs `** PANEL MISMATCH **` and PROCEEDS, noting that
    every per-model denominator uses the counted list. That is defensible as
    fail-loud-rather-than-block, and it still leaves a run whose per-model
    figures are computed over the wrong roster.

    ★ SO THIS IS NOT A SECOND WARNING, IT IS AN EARLIER ONE. A config slip should
    be caught before a run spends anything, which is the same reasoning the seat
    designs give for refusing to START on a dead route rather than mid-run. This
    function only REPORTS; it refuses nothing and changes no run behaviour.

    The runner's comment records this as the launcher config-drop class the
    project "has now hit seven times", which is why detecting it early is worth a
    surface rather than a log line.
    """
    def _labels(xs: Any) -> list[str]:
        out: list[str] = []
        for x in (xs or ()):
            lbl = getattr(x, "label", None)
            out.append(str(lbl) if lbl is not None else str(x))
        return out

    d = _labels(dispatched)
    c = _labels(counted)
    ds, cs = set(d), set(c)
    # ★ BOTH DIRECTIONS, because they mean different things. A seat dispatched and
    # not counted is work paid for and discarded from every denominator; a seat
    # counted and not dispatched inflates a denominator with a seat that never
    # answered. Reporting only the total would say neither.
    return {
        "dispatched": sorted(ds),
        "counted": sorted(cs),
        "agree": bool(ds) and ds == cs,
        "dispatched_not_counted": sorted(ds - cs),
        "counted_not_dispatched": sorted(cs - ds),
        "either_list_empty": not ds or not cs,
        "why": ("the 2 roster declarations agree" if ds and ds == cs else
                "the dispatched and counted rosters differ; every per-model "
                "denominator in the run will use the COUNTED list, so a seat "
                "dispatched but not counted is paid for and discarded, and a "
                "seat counted but not dispatched inflates a denominator"),
    }


def readiness(models: Any = None) -> dict:
    """The whole picture, as plain data a UX can render without interpreting it."""
    rows = seat_rows(models)
    return {
        "seats": rows,
        "counts": {
            "known": len(rows),
            "registered": sum(1 for r in rows if r["registered"]),
            "routed": sum(1 for r in rows if r["has_route"]),
            "ready": sum(1 for r in rows if r["ready"]),
            "route_unknown": sum(1 for r in rows if r["has_route"] is None),
            "gapped": sum(1 for r in rows if r["registration_gaps"]),
        },
        "routes": {
            api: {
                "credential_names": list(names),
                "credential": credential_present(api),
                "credential_source": credential_source(api),
                "simulated": api in SIMULATED_APIS,
            }
            for api, names in sorted(API_CREDENTIALS.items())
        },
        # ★ THE 2-ROSTER CHECK IS PRESENT BUT NOT RUN HERE, because this function
        # is given no config. A caller with both lists passes them to
        # `roster_declarations_agree`; the key below says so rather than leaving
        # a UX to assume the question was asked and answered.
        "roster_declarations": ("not checked: pass the dispatched and counted "
                                "rosters to roster_declarations_agree"),
        # Stated in the payload rather than only in this docstring, so a UX built
        # against it cannot present readiness as liveness.
        "caveat": ("configuration only; no route was contacted. Whether a route "
                   "answers is established by the aliveness probe, which is a "
                   "dispatch and is separately authorised."),
    }


def main() -> int:
    import argparse
    import json

    ap = argparse.ArgumentParser(
        prog="seat_readiness.py",
        description="Report what each seat is missing. Reads only; contacts "
                    "nothing; never prints a credential value.")
    ap.add_argument("--json", action="store_true", help="emit the raw payload")
    a = ap.parse_args()

    r = readiness()
    if a.json:
        print(json.dumps(r, indent=2, sort_keys=True))
        return 0

    c = r["counts"]
    print(f"  seats known {c['known']}, registered {c['registered']}, "
          f"gapped {c['gapped']}, routed {c['routed']}, ready {c['ready']}")
    if c["route_unknown"]:
        print(f"  no roster was supplied, so the route half is UNKNOWN for "
              f"{c['route_unknown']} seat(s). Routes are declared per run, not "
              f"once in the tree; pass a run's models to settle it.")
    print()
    for row in r["seats"]:
        if row["registration_gaps"]:
            state = "GAPPED"
        elif row["has_route"] is None:
            state = "CALIBRATED"
        elif row["ready"]:
            state = "READY"
        else:
            state = "NO ROUTE"
        print(f"  [{state:9s}] {row['label']:12s} key={row['composer_key']}")
        if row["registration_gaps"]:
            for w in row["registration_gaps"]:
                print(f"                  missing from {w}")
    print()
    for api, info in r["routes"].items():
        cred = info["credential"]
        where = info["credential_source"]
        txt = ("n/a (no credential)" if cred is None
               else (f"present (from {where})" if cred else "ABSENT"))
        print(f"  route {api:12s} credential {txt}")
    print()
    print(f"  {r['caveat']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
