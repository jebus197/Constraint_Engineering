#!/usr/bin/env python3
"""THE ONE READER for the one domain vocabulary.

`bench/cdsfl_registry/domain_manifest.toml` declares it; this module is the only
thing that parses it. Before both existed there were 2 domain vocabularies --
the registry configs under `domains/` and the expert encoding families under
`bench/directives/` -- agreeing on 3 names of 17, Wilson [0.061911, 0.410295].

WHAT THIS CLOSES, each measured 2026-11-11/12 rather than asserted:

  * `composer._load_domain_directive` picked an encoding with
    `sorted(domain_dir.glob("*.txt"))[0]` -- the first file ALPHABETICALLY --
    whenever no variant was passed. 9 of 10 families were defaulted that way,
    Wilson [0.595850, 0.982124]; 19 of 29 encodings were unreachable without a
    flag, Wilson [0.473451, 0.800593], that 0 task files ever set.
  * 7 config domains had no encoding directory and 7 encoding families had no
    config, so a run could reach a domain with a severity scale and no
    constraints, or the reverse, for 14 of the 17 names in use.

FAIL CLOSED, DELIBERATELY. A malformed manifest raises `VocabularyError` rather
than falling back to the alphabetical pick. A reader that silently degrades to
the behaviour it was built to replace is the defect wearing the repair's name --
and this project has that failure 3 times over in its own record.

ONE TABLE, NOT TWO. `bench/immune_agents.py:_DOMAIN_ALIAS` is DERIVED from this
manifest by `alias_map()`, never transcribed. That module's own comment already
records why: "a second spelling here would be 2 tables that can drift, which is
the defect this exists to close."
"""
from __future__ import annotations

import functools
import pathlib
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:                                  # pragma: no cover
    import tomli as tomllib                                  # type: ignore

HERE = pathlib.Path(__file__).resolve().parent
MANIFEST = HERE / "domain_manifest.toml"
DIRECTIVES = HERE.parent / "directives"
CONFIGS = HERE / "domains"

#: Keys at the top of the manifest that are NOT domains.
_NON_DOMAIN_KEYS = {"manifest_version", "written", "tiers", "composition",
                    "subdomain_aliases"}


class VocabularyError(RuntimeError):
    """The manifest is unusable. Raised rather than degraded."""


@functools.lru_cache(maxsize=1)
def load() -> dict[str, Any]:
    """Parse and VALIDATE the manifest. Cached; `load.cache_clear()` to re-read."""
    if not MANIFEST.is_file():
        raise VocabularyError(f"no domain manifest at {MANIFEST}")
    try:
        raw = tomllib.loads(MANIFEST.read_text(encoding="utf-8"))
    except Exception as exc:                                 # noqa: BLE001
        raise VocabularyError(f"{MANIFEST} does not parse: {exc}") from exc

    tiers = raw.get("tiers")
    if not isinstance(tiers, list) or not tiers:
        raise VocabularyError("the manifest declares no `tiers` list")

    doms = {k: v for k, v in raw.items()
            if k not in _NON_DOMAIN_KEYS and isinstance(v, dict)}
    if not doms:
        raise VocabularyError("the manifest declares no domains")

    seen_alias: dict[str, str] = {}
    for name, d in doms.items():
        for required in ("family", "config", "default_encoding", "encoding_tier"):
            if not d.get(required):
                raise VocabularyError(f"domain {name!r} declares no {required!r}")
        if d["encoding_tier"] not in tiers:
            raise VocabularyError(
                f"domain {name!r} declares tier {d['encoding_tier']!r}, "
                f"which is not one of {tiers}")
        subs = d.get("subdomains") or {}
        if not subs:
            raise VocabularyError(f"domain {name!r} declares no subdomains")
        if d["default_encoding"] not in subs:
            raise VocabularyError(
                f"domain {name!r} names default_encoding "
                f"{d['default_encoding']!r}, which is not one of its "
                f"subdomains {sorted(subs)}")
        for label, s in subs.items():
            if not isinstance(s, dict) or not s.get("path"):
                raise VocabularyError(
                    f"subdomain {name}.{label} declares no path")
        # A severity scale is either recognised, or `none`/`composed` WITH a reason.
        scale = d.get("severity_scale")
        if not scale:
            raise VocabularyError(f"domain {name!r} declares no severity_scale; "
                                  f"use \"none\" with a reason rather than omitting it")
        if scale in ("none", "composed") and not d.get("severity_scale_reason"):
            raise VocabularyError(
                f"domain {name!r} declares severity_scale={scale!r} and no "
                f"severity_scale_reason. An unexplained absence is "
                f"indistinguishable from an oversight.")
        if scale not in ("none", "composed") and not d.get("critical_level"):
            raise VocabularyError(
                f"domain {name!r} declares a scale and no critical_level. An "
                f"ordering without a distinguished level cannot support a gate "
                f"-- z3 unsat for the ranked cut, sat for the fixed one.")
        # An alias may not be claimed twice, and may not shadow a canonical name.
        for a in d.get("aliases") or []:
            if a in doms:
                raise VocabularyError(
                    f"{name!r} claims alias {a!r}, which is itself a domain")
            if a in seen_alias:
                raise VocabularyError(
                    f"alias {a!r} is claimed by both {seen_alias[a]!r} and {name!r}")
            seen_alias[a] = name
    #: A SUBDOMAIN ALIAS resolves to a (domain, subdomain) PAIR. Validated here
    #: rather than at use, because a pair naming a subdomain that does not exist
    #: would route a task to no encoding and the warning would read as the
    #: domain simply having little to say -- the silence this file exists to end.
    sub_alias: dict[str, tuple[str, str]] = {}
    for spelling, pair in (raw.get("subdomain_aliases") or {}).items():
        if not (isinstance(pair, list) and len(pair) == 2):
            raise VocabularyError(
                f"subdomain alias {spelling!r} must be [domain, subdomain], got {pair!r}")
        dom, lab = pair
        if dom not in doms:
            raise VocabularyError(
                f"subdomain alias {spelling!r} names domain {dom!r}, which is not declared")
        if lab not in (doms[dom].get("subdomains") or {}):
            raise VocabularyError(
                f"subdomain alias {spelling!r} names {dom}.{lab!r}, which is not "
                f"a declared subdomain of {dom!r}")
        if spelling in doms:
            raise VocabularyError(
                f"subdomain alias {spelling!r} is itself a domain name")
        if spelling in seen_alias:
            raise VocabularyError(
                f"{spelling!r} is both a domain alias (of {seen_alias[spelling]!r}) "
                f"and a subdomain alias")
        sub_alias[spelling] = (dom, lab)

    raw["_domains"] = doms
    raw["_alias_to_domain"] = seen_alias
    raw["_subdomain_alias"] = sub_alias
    return raw


def domains() -> list[str]:
    """Canonical top-level domain names, sorted."""
    return sorted(load()["_domains"])


def tiers() -> list[str]:
    return list(load()["tiers"])


def composition_rule() -> dict[str, Any]:
    """The founder's rule, read as data rather than restated in prose."""
    return dict(load().get("composition") or {})


def resolve(name: str) -> str:
    """An alias or a canonical name in; the canonical name out.

    An UNKNOWN name is returned unchanged rather than guessed at, and
    `is_known()` is how a caller tells the difference. Guessing a domain is how
    a target reaches the wrong constraint box.
    """
    m = load()
    key = (name or "").strip()
    if key in m["_domains"]:
        return key
    if key in m["_alias_to_domain"]:
        return m["_alias_to_domain"][key]
    pair = m["_subdomain_alias"].get(key)
    if pair:
        return pair[0]
    return key


def is_known(name: str) -> bool:
    return resolve(name) in load()["_domains"]


def entry(name: str) -> dict[str, Any]:
    d = load()["_domains"].get(resolve(name))
    if d is None:
        raise VocabularyError(f"{name!r} resolves to no declared domain")
    return d


def subdomain_alias_map() -> dict[str, tuple[str, str]]:
    """Old spellings that name a SUBDOMAIN: spelling -> (domain, subdomain)."""
    return dict(load()["_subdomain_alias"])


def resolve_pair(name: str) -> tuple[str, str | None]:
    """A spelling in; (canonical domain, subdomain or None) out.

    `structural` returns ("engineering", "structural") -- the pair -- while
    `engineering` returns ("engineering", None) meaning "use the declared
    default". This is what lets an old directory name route into the new
    vocabulary without becoming an alias of the whole domain, which is the
    distinction that stopped a structural task loading a hardware box.
    """
    m = load()
    key = (name or "").strip()
    pair = m["_subdomain_alias"].get(key)
    if pair:
        return pair
    return resolve(key), None


def alias_map() -> dict[str, str]:
    """DERIVED, never transcribed. This is what `_DOMAIN_ALIAS` should be."""
    return dict(load()["_alias_to_domain"])


def config_alias_map() -> dict[str, str]:
    """EVERY spelling -> the CONFIG STEM its TOML is declared under.

    ★ THIS IS NOT `alias_map()` AND CONFLATING THEM WOULD HAVE BEEN A SILENT
    MIS-WIRING, caught by measuring before wiring. `_DOMAIN_ALIAS` in
    `bench/immune_agents.py` is documented as mapping "a run's domain name onto
    the one the TOMLs declare" -- a CONFIG STEM. `alias_map()` returns the
    canonical DOMAIN, which for software is `software` while its config stem is
    `cs_software`. Substituting one for the other would have pointed the immune
    pipeline at a TOML that does not exist, and the failure mode is a domain
    composing no layer at all.

    A domain whose config is still OWED is OMITTED, so the caller keeps today's
    behaviour for it rather than being sent to an absent file. `config_owed()`
    reports those, so the omission is visible rather than silent.
    """
    out: dict[str, str] = {}
    for dom in domains():
        d = entry(dom)
        if d.get("config_owed"):
            continue
        stem = str(d["config"])
        out[dom] = stem
        for a in d.get("aliases") or []:
            out[a] = stem
    return out


def config_owed() -> list[str]:
    """Domains whose registry config does not exist yet."""
    return [d for d in domains() if entry(d).get("config_owed")]


def config_path(name: str) -> pathlib.Path:
    return CONFIGS / f"{entry(name)['config']}.toml"


def subdomains(name: str) -> dict[str, dict[str, Any]]:
    return dict(entry(name).get("subdomains") or {})


def default_subdomain(name: str) -> str:
    return str(entry(name)["default_encoding"])


def encoding_path(name: str, subdomain: str | None = None) -> pathlib.Path:
    """The encoding file for a domain, by DECLARED default when none is named.

    This is the replacement for `sorted(domain_dir.glob("*.txt"))[0]`.
    """
    subs = subdomains(name)
    label = subdomain or default_subdomain(name)
    s = subs.get(label)
    if s is None:
        raise VocabularyError(
            f"{resolve(name)!r} has no subdomain {label!r}; declared: {sorted(subs)}")
    return DIRECTIVES / str(s["path"])


def severity(name: str) -> dict[str, Any]:
    """The domain's scale, its levels and its critical LEVEL -- or an honest none.

    The scale NAME is returned beside the levels because a severity number
    without its scale cannot be compared with anything: measured with pint,
    a clinical grade and a software score are both dimensionless, so
    `CTCAE 3 + CVSS 7.0` evaluates to 10.0 and dimensional analysis has nothing
    to refuse. The refusal has to be on the name.
    """
    d = entry(name)
    return {
        "domain": resolve(name),
        "scale": d.get("severity_scale"),
        "levels": list(d.get("severity_levels") or []),
        "critical_level": d.get("critical_level"),
        "note": d.get("critical_level_note"),
        "reason": d.get("severity_scale_reason"),
        "inherits_from_application": bool(d.get("inherits_from_application")),
        "composes_from_selected": bool(d.get("composes_from_selected")),
    }


def may_compose(a: str, b: str) -> tuple[bool, str]:
    """May 2 domains' severities be combined into 1 number?

    The founder's rule, 2026-11-12: report both in their own scale, UNLESS a
    formally defined conversion between them already exists. Same scale is the
    only case where one presently does, so this answers False for every
    distinct pair and NAMES the reason rather than returning a bare bool.
    """
    sa, sb = severity(a), severity(b)
    if sa["scale"] == sb["scale"] and sa["scale"] not in (None, "none", "composed"):
        return True, f"both report on {sa['scale']!r}, so they are the same scale"
    if sa["scale"] in ("none",) or sb["scale"] in ("none",):
        return False, (
            "at least one domain declares no scale of its own and inherits the "
            "application's, so there is nothing to convert between")
    return False, (
        f"{sa['scale']!r} and {sb['scale']!r} are different scales with no "
        f"formally defined conversion; report each in its own context")


#: ★ THE 2 QUESTIONS A STEERING SURFACE MUST ANSWER, AND THEY ARE NOT 1.
#: Added 2026-11-12 as entry B162, on his instruction to build the fix for the
#: steering disagreement. A seat answering as a harness seat contradicted the
#: orchestrator's own proposer about a pooled hazard ratio from 3 unlike trial
#: sites: the proposer said statistics, the seat said biology, and the seat was
#: right for a reason the manifest already states. Statistics declares
#: `severity_scale = "none"` with the reason that a statistical error's
#: consequence belongs to the application it serves, and the application was a
#: vaccine dosing claim, so the consequence is patient harm.
#:
#: BOTH ANSWERS WERE CORRECT ABOUT DIFFERENT QUESTIONS. The SUBJECT domain
#: decides which expert encoding a seat receives. The CONSEQUENCE domain decides
#: what counts as a critical finding. A surface returning 1 label cannot express
#: that, and the run record then cannot say which scale a finding was judged on.
#:
#: THE DATA WAS ALREADY DECLARED AND THE FLAG WAS ALREADY DEAD. Measured before
#: writing this: 5 of the 10 real domains declare `severity_scale = "none"` with
#: `inherits_from_application = true` -- mathematics, physics, statistics,
#: information_science and logistics -- and `cross_domain` declares a composed
#: scale, so 6 of 10 are cases where subject and consequence can differ. The
#: flag `inherits_from_application` was written into `severity()`'s return by
#: exactly 1 line and read by 0 callers: `may_compose` infers inheritance from
#: `scale == "none"` instead, and the command-line report reads only the scale
#: and the critical level. So this is not a new field; it is a declaration
#: nothing reached, which the additive standard forbids in its symmetric form.
#:
#: AN UNRESOLVED CONSEQUENCE IS NAMED, NEVER DEFAULTED. The case that matters is
#: a subject which inherits and no application given. Today that silently yields
#: a scale of "none" and nothing notices. Here it returns `resolved=False` with
#: a reason, so a caller must handle it rather than inherit a blank -- a gate
#: admitting findings on an unresolved scale is the fault B143 and B144 already
#: record from the other side.
def consequence_domain(subject: str,
                       application: str | None = None) -> dict[str, Any]:
    """The domain whose severity scale judges a finding about `subject`.

    Returns the subject's own scale where it declares one; the application's
    where the subject declares none and inherits; and an UNRESOLVED answer,
    named, where it inherits and no application is given.

    `how` is always one of "own", "inherited", "composed" or "unresolved", so a
    caller can record WHY a scale was used and not merely which.
    """
    subj = resolve(subject)
    sev = severity(subj)
    if sev["scale"] not in (None, "none", "composed"):
        return {"subject": subj, "consequence": subj, "how": "own",
                "scale": sev["scale"], "critical_level": sev["critical_level"],
                "resolved": True,
                "why": f"{subj} declares {sev['scale']!r} as its own scale"}
    if sev["composes_from_selected"] or sev["scale"] == "composed":
        #: `scale` is None, not "composed". The CONTRACT a caller depends on is
        #: that `scale` holds a USABLE scale or nothing at all, so an
        #: unresolved answer can never be read as one -- `how` already carries
        #: the "composed" information. Its own guard caught this: the first
        #: version returned "composed" here while reporting resolved=False,
        #: which is a scale on an answer that has none.
        return {"subject": subj, "consequence": None, "how": "composed",
                "scale": None, "critical_level": None, "resolved": False,
                "why": (f"{subj} composes its scale from the domains selected "
                        f"for a run, so it cannot be resolved from the subject "
                        f"alone")}
    if not sev["inherits_from_application"]:
        return {"subject": subj, "consequence": None, "how": "unresolved",
                "scale": None, "critical_level": None, "resolved": False,
                "why": (f"{subj} declares no scale and does not declare that it "
                        f"inherits one, so the manifest cannot say what judges "
                        f"a finding about it")}
    if application is None:
        return {"subject": subj, "consequence": None, "how": "unresolved",
                "scale": None, "critical_level": None, "resolved": False,
                "why": (f"{subj} inherits its scale from the application it "
                        f"serves and no application was given; "
                        f"{sev['reason'] or 'no reason recorded'}")}
    app = resolve(application)
    app_sev = severity(app)
    if app_sev["scale"] in (None, "none", "composed"):
        return {"subject": subj, "consequence": app, "how": "unresolved",
                "scale": None, "critical_level": None, "resolved": False,
                "why": (f"{subj} inherits from the application and the "
                        f"application {app} declares no scale of its own "
                        f"either, so the chain does not terminate")}
    return {"subject": subj, "consequence": app, "how": "inherited",
            "scale": app_sev["scale"],
            "critical_level": app_sev["critical_level"], "resolved": True,
            "why": (f"{subj} declares no scale and inherits from the "
                    f"application; {app} declares {app_sev['scale']!r}")}


def inheriting_domains() -> list[str]:
    """Every domain whose consequence scale is not its own. 6 of 10 on the
    manifest of 2026-11-12, which is the figure B162 rests on."""
    out = []
    for dom in domains():
        sev = severity(dom)
        if (sev["inherits_from_application"] or sev["composes_from_selected"]
                or sev["scale"] in (None, "none", "composed")):
            out.append(dom)
    return out


def owed() -> list[tuple[str, str, pathlib.Path, str]]:
    """(domain, subdomain, path, reason) for every encoding not yet written."""
    out = []
    for dom in domains():
        for label, s in subdomains(dom).items():
            if s.get("owed"):
                out.append((dom, label, DIRECTIVES / str(s["path"]),
                            str(s.get("owed_reason") or "")))
    return out


def missing_on_disk() -> list[tuple[str, str, pathlib.Path]]:
    """Declared encodings whose file is absent and NOT marked owed.

    An undeclared absence is the defect; a declared one is a backlog.
    """
    out = []
    for dom in domains():
        for label, s in subdomains(dom).items():
            if s.get("owed"):
                continue
            p = DIRECTIVES / str(s["path"])
            if not p.is_file():
                out.append((dom, label, p))
    return out


def main(argv: list[str]) -> int:
    if any(a in ("-h", "--help") for a in argv):
        print("usage: domain_vocabulary.py [-h]")
        print(__doc__)
        return 0
    print("=" * 74)
    print("THE ONE DOMAIN VOCABULARY")
    print("=" * 74)
    print(f"manifest : {MANIFEST}")
    print(f"tiers    : {', '.join(tiers())}")
    c = composition_rule()
    print(f"composition rule : {c.get('rule')}")
    print(f"           except: {c.get('exception')}")
    print()
    for dom in domains():
        sev = severity(dom)
        scale = sev["scale"]
        lvl = f" critical at {sev['critical_level']!r}" if sev["critical_level"] else ""
        print(f"{dom:22s} {len(subdomains(dom)):2d} subdomain(s)  "
              f"default={default_subdomain(dom)!r}")
        print(f"{'':22s} scale={scale!r}{lvl}  tier={entry(dom)['encoding_tier']}")
    print()
    print(f"aliases resolving into the above: {len(alias_map())}")
    for a, d in sorted(alias_map().items()):
        print(f"   {a:24s} -> {d}")
    o = owed()
    print(f"\nencodings declared OWED (not yet written): {len(o)}")
    for dom, label, p, why in o:
        print(f"   {dom}.{label:22s} {p.relative_to(DIRECTIVES.parent.parent)}")
    miss = missing_on_disk()
    print(f"\nUNDECLARED absences (a defect, not a backlog): {len(miss)}")
    for dom, label, p in miss:
        print(f"   {dom}.{label}  {p}")
    return 1 if miss else 0


if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv[1:]))
