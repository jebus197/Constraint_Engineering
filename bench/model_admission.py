#!/usr/bin/env python3
"""ONE DECLARATION ADMITS A MODEL EVERYWHERE. The single registration point.

NAMED WITHOUT A DATE, DELIBERATELY, and the reason is mechanical. Every dated
module in `bench/` is path-loaded or unused -- checked across 6 of them on
2026-11-02 -- because a dash is not legal in a dotted import, so a dated name
makes a module unimportable as `bench.<name>`. This is a LIBRARY that live runner
code must import, like `runner_core`, `routing` and `ticket_store`, not a dated
measurement script. It was first written as `model_admission_2026-11-02.py` and
renamed before anything depended on it.

HIS INSTRUCTION, 2026-11-02, verbatim: *"The ideal scenario if you look at the UX
work is that researchers should be able to search for/add models trivially from a
search box in the UX, enter all their API keys, and logins for OpenRouter, and
for the various model vendors they might have access to, and from any local
models they have on their machines. They shouldn't need to think, or concern
themselves with the underlying mechanics of how this works in reality. Which is
what I mean by making the process trivial."*

And on 2026-11-01, annotation 11 of `Closing_Report_2026-11-01.txt`: *"fixing a
failing registration should also preferably be made as trivial for a HIL to fix
as possible."*

THIS IS THE BACKEND HALF. It does not build a search box; it makes the thing a
search box would write sufficient on its own.

WHY IT WAS OWED, MEASURED, and the figure is not mine.
`scripts/how_many_places_must_change_to_add_a_model_2026-10-16.py` reports that a
researcher must edit 12 per-model tables across 6 live harness files plus add 1
per-model registry file, and that of the 10 steps a new seat passes through 1
still fails SILENTLY (0.100000, Wilson 95% [0.017876, 0.404150]). That script's
own conclusion names this module: *"a single registration point is the fix, and
it needs his ruling because it changes how every seat is configured."* He gave
that ruling above.

TWO THINGS THIS PROJECT HAS ALREADY PAID FOR, so the failure mode is not
hypothetical:
  * 2026-08-30: Fable had no Layer 4 file, composition raised, the caller fell
    back, and 1 panellist of 6 ran on an EMPTY system prompt. Measured split:
    CC2/Gemini/ChatGPT 6,787 characters, DeepSeek/Codex 3,731, Fable 0.
  * 2026-11-02: Fable was in MODEL_SPECS and absent from COMPOSER_MODEL_MAP, and
    because that lookup is `.get(label, label)` the miss was not an error --
    "Fable" resolved to "Fable", which keys neither phenotype table, so BOTH
    silently defaulted. Its directive budget sat at 8,000 against its sibling's
    12,000, a third less, on every run it ever joined.

THE DESIGN, and why it is this one rather than a resolver change.
`models/<Name>.toml` is ALREADY Layer 4 of the policy registry and is ALREADY
read by live code (`registry.py:273`, `engine.py:264`), so the declaration point
exists and is wired -- it simply never covered the 5 tables that live as Python
source literals. The alternative was to teach `routing.resolve_or_alarm` to
consult a declaration, which would have meant editing all 9 of its live call
sites and would have made `routing` import `composer` for its value types, a
circular import. This fills the tables instead, so 0 call sites change and every
existing lookup, alarm and ledger entry behaves exactly as before.

IT IS GAPS-ONLY AND THAT IS DELIBERATE. A hard-coded entry ALWAYS wins. So this
cannot alter the configuration of any of the 6 seats that already run, which
keeps it additive in the strict sense: it adds admission for models that have
none and changes nothing for models that do. Whether a declaration should be
allowed to OVERRIDE a hard-coded value is a separate question and is HIS, because
it would change how existing seats are configured.

ITS OWN FAILURE MODE IS GUARDED, because this project has the receipt.
`scripts/the_coherence_recalibration_is_inert_three_ways_2026-10-15.py` records a
function of exactly this shape -- one that updated a module dict and turned out
to be inert 3 ways. So `admit_declared_models()` RETURNS what it changed, and its
guard asserts the tables differ afterwards rather than asserting the code looks
right.
"""
from __future__ import annotations

import pathlib
import tomllib
from typing import Any

REPO = pathlib.Path(__file__).resolve().parents[1]
MODELS_DIR = REPO / "bench" / "cdsfl_registry" / "models"

# RUN AS A SCRIPT, `bench` is not importable, because the script's own directory
# is on the path rather than the repository root. Imported as a module it already
# is. Both entry points matter here: a researcher checking a declaration will run
# this file directly, and that is the whole point of it.
if str(REPO) not in __import__("sys").path:
    __import__("sys").path.insert(0, str(REPO))

#: The section a researcher (or the UX) writes. It is NAMED rather than inferred
#: from the file's other sections, so an existing `[model]` or `[protocol]` block
#: cannot be mistaken for an admission declaration. Fable.toml has carried both
#: of those since 2026-08-30 and neither describes a per-model table.
SECTION = "admission"

#: The 5 live tables, each with the declaration key that fills it and how to
#: decode the declared value into that table's type. Decoding is per field and
#: EXPLICIT: a coherence budget is a float, a phenotype is a dataclass, a
#: fingerprint is a different dataclass, and a model spec is a dict. A single
#: generic "just put the value in" would have put a dict where a dataclass was
#: expected and failed at the call site rather than here.
#:
#: `composer_key` is listed FIRST on purpose. It is the resolver: 1 missing entry
#: there produced 3 reported absences on 2026-11-02, because the 2 phenotype
#: tables are keyed by composer key and not by seat label.
FIELDS = ("composer_key", "coherence_budget", "phenotype", "fingerprint", "spec")


def _decl_path(model: str) -> pathlib.Path:
    return MODELS_DIR / f"{model}.toml"


def declaration(model: str) -> dict[str, Any]:
    """The `[admission]` block for one model, or {} when there is none.

    NEVER RAISES ON A BAD FILE. A malformed declaration must not take down a
    run, and it must not be silent either: the reason is returned under
    `_error` so a caller can report it. `feedback_a_swallowed_exception_is_not_a_record`
    records the cost of writing an exception into the evidence and nobody
    reading it, so the caller is given something it can print.
    """
    p = _decl_path(model)
    if not p.is_file():
        return {}
    try:
        d = tomllib.loads(p.read_text(encoding="utf-8"))
    except Exception as exc:                                  # noqa: BLE001
        return {"_error": f"{type(exc).__name__}: {exc}", "_path": str(p)}
    sec = d.get(SECTION)
    return dict(sec) if isinstance(sec, dict) else {}


def declared_models() -> dict[str, dict[str, Any]]:
    """Every model that carries an `[admission]` block, keyed by file stem."""
    out: dict[str, dict[str, Any]] = {}
    if not MODELS_DIR.is_dir():
        return out
    for p in sorted(MODELS_DIR.glob("*.toml")):
        decl = declaration(p.stem)
        if decl:
            out[p.stem] = decl
    return out


def registration_targets(model: str, ckey: str) -> list[tuple]:
    """The 5 per-model tables and WHICH KEY each one is keyed on.

    ★ EXTRACTED 2026-11-02 SO THERE IS ONE DECLARATION OF THE KEYING, NOT TWO.
    `bench/seat_readiness.py` has to know the same thing in order to report which
    tables a seat is missing from, and a second copy got it WRONG on its first
    attempt: it keyed all 5 on the composer key, where `INITIAL_FINGERPRINTS` and
    `MODEL_SPECS` are keyed on the LABEL. The symptom was 6 of 6 seats reported as
    gapped -- a uniform result, which is the cheapest signal that a predicate is
    wrong rather than a finding about the world.

    Returning the live mappings themselves (not their names) is deliberate: a
    caller cannot then look up a table this function did not hand it.

    Each entry is (table, key, declaration field, decoder, human name).
    """
    from bench import runner_core as rc
    from bench.cdsfl_registry import composer as co

    return [
        (co.COMPOSER_MODEL_MAP, model, "composer_key",
         lambda v, _c=ckey: str(v), "composer.COMPOSER_MODEL_MAP"),
        (co.COMPOSER_MODEL_MAP, ckey, "composer_key",
         lambda v, _c=ckey: _c, "composer.COMPOSER_MODEL_MAP (self)"),
        (co.MODEL_COHERENCE_BUDGETS, ckey, "coherence_budget",
         float, "composer.MODEL_COHERENCE_BUDGETS"),
        (co.PHENOTYPE_TRANSFORMS, ckey, "phenotype",
         lambda v: co.PhenotypeTransform(**dict(v)),
         "composer.PHENOTYPE_TRANSFORMS"),
        (rc.INITIAL_FINGERPRINTS, model, "fingerprint",
         lambda v: rc.CapabilityFingerprint(**dict(v)),
         "runner_core.INITIAL_FINGERPRINTS"),
        (rc.MODEL_SPECS, model, "spec",
         lambda v: dict(v), "runner_core.MODEL_SPECS"),
    ]


def admit_declared_models(*, dry_run: bool = False) -> dict[str, Any]:
    """Fill the 5 per-model tables from every declaration. GAPS ONLY.

    Returns a record of what it did, because a function that mutates module
    dicts and returns nothing cannot be distinguished from one that is inert --
    which is the defect `the_coherence_recalibration_is_inert_three_ways` found
    in a function of this exact shape on 2026-10-15.
    """
    from bench import runner_core as rc
    from bench.cdsfl_registry import composer as co

    applied: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []

    for model, decl in declared_models().items():
        if decl.get("_error"):
            errors.append({"model": model, "error": decl["_error"],
                           "path": decl.get("_path")})
            continue
        ckey = str(decl.get("composer_key") or "").strip() or model

        targets = registration_targets(model, ckey)

        for table, key, field, decode, name in targets:
            if field not in decl:
                continue
            if key in table:
                # A HARD-CODED ENTRY ALWAYS WINS. This is what keeps the change
                # additive: it cannot alter any seat that already runs.
                skipped.append({"model": model, "table": name, "key": key,
                                "reason": "already present; a hard-coded entry wins"})
                continue
            try:
                value = decode(decl[field])
            except Exception as exc:                          # noqa: BLE001
                errors.append({"model": model, "table": name, "field": field,
                               "error": f"{type(exc).__name__}: {exc}"})
                continue
            if not dry_run:
                table[key] = value
            applied.append({"model": model, "table": name, "key": key,
                            "field": field, "value": repr(value)[:120]})

    return {"applied": applied, "skipped": skipped, "errors": errors,
            "models_declared": sorted(declared_models()),
            "dry_run": dry_run}


def main() -> int:
    import argparse
    import json

    ap = argparse.ArgumentParser(
        prog="model_admission.py",
        description="Admit every declared model into the per-model tables, "
                    "or report what a declaration would do. Reads and reports; "
                    "--apply mutates only the in-process tables.")
    # NOT `required`, and NOT defaulting to apply: a --help must never cost
    # anything and an operational script must name an unknown flag rather than
    # reporting a missing required one first (the 2026-10-01 --help sweep).
    ap.add_argument("--apply", action="store_true",
                    help="actually fill the tables (default: dry run)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--model", default=None,
                    help="report just this model's declaration")
    a = ap.parse_args()

    if a.model:
        d = declaration(a.model)
        print(json.dumps({a.model: d}, indent=1, default=str))
        return 0 if d and not d.get("_error") else 1

    rec = admit_declared_models(dry_run=not a.apply)
    if a.json:
        print(json.dumps(rec, indent=1, default=str))
        return 2 if rec["errors"] else 0

    print("=" * 74)
    print("MODEL ADMISSION FROM DECLARATIONS"
          + ("  (DRY RUN)" if rec["dry_run"] else "  (APPLIED)"))
    print("=" * 74)
    print(f"  declarations found : {rec['models_declared'] or 'none'}")
    print(f"  entries filled     : {len(rec['applied'])}")
    for r in rec["applied"]:
        print(f"     + {r['table']}[{r['key']!r}] <- {r['field']} = {r['value']}")
    print(f"  entries left alone : {len(rec['skipped'])}"
          f"   (a hard-coded entry always wins)")
    print(f"  errors             : {len(rec['errors'])}")
    for r in rec["errors"]:
        print(f"     ! {r}")
    if not rec["models_declared"]:
        print()
        print("  NO MODEL CARRIES AN [admission] BLOCK YET, so this filled nothing.")
        print("  That is the honest state and not a pass: the 6 seats that run")
        print("  today are admitted by hard-coded tables, and this module exists")
        print("  so the NEXT one does not have to be.")
    return 2 if rec["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
