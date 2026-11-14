#!/usr/bin/env python3
"""The reference list a generated report must carry, derived from layer 3.

HIS INSTRUCTION, verbatim: *"There is a very strong argument that any report
generated for researchers should carry a list of accessed references at the end
of it... I don't trust the models exactly to do this themselves, so perhaps this
could be mechanised."*

★ WHY THIS EXISTS AND WHY IT IS THE CALLER LAYER 3 WAS OWED. The researcher
encoding was built on 2026-11-13 as `bench/directives/researchers/`, and
measured on 2026-11-14 **nothing in the tree read it**: every match for
`researchers` across `bench/`, `scripts/` and `hooks/` was prose in an unrelated
file, and the composer has no layer-3 loader. Under `additive-standard`'s
symmetric form an addition nothing reaches is not additive, and this project has
11 confirmed defects of exactly that shape. The encoding needed a consumer, and
he had already named which one.

★ IT REPORTS WHAT WAS ACTUALLY LOADED, NOT WHAT WAS DECLARED. A named encoding
that is absent from disk is reported as MISSING rather than silently dropped,
because the whole value of a mechanised list over a remembered one is that an
omission becomes visible. An empty list in a report is loud; a model forgetting
to mention a source is not.

★ AND IT WILL NOT CALL A SCALE-LESS DOMAIN OVERDUE. `confirmations.toml`
declares `needs_confirmation = false` for a domain with no consequence scale,
with its reason, because a standard that does not exist cannot go stale. A
checker that reported those as overdue would manufacture 2 permanent false
alarms out of 3 domains.

★ THE BACKSTOP IS READ FROM THE FILE, NEVER TYPED HERE. `[policy]` carries
`backstop_days` and the exposure basis it was derived from, so changing the
policy changes the verdict and no constant in this script has to be found and
edited to match.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import pathlib
import sys
import tomllib

REPO = pathlib.Path(__file__).resolve().parent.parent
RESEARCHERS = REPO / "bench" / "directives" / "researchers"


def _load(path: pathlib.Path) -> dict:
    with path.open("rb") as fh:
        return tomllib.load(fh)


def researchers() -> list[str]:
    """Every researcher with a layer-3 encoding, read from disk."""
    if not RESEARCHERS.is_dir():
        return []
    return sorted(p.name for p in RESEARCHERS.iterdir()
                  if p.is_dir() and (p / "standards.toml").is_file())


def reference_list(researcher: str, today: dt.date | None = None) -> dict:
    """The references this researcher's encoding names, and their state.

    Returns `{"researcher", "encodings", "standards", "missing", "overdue",
    "backstop_days"}`. `encodings` carries a sha256 of each file ACTUALLY read,
    so a report can be checked against the bytes it was generated from.
    """
    today = today or dt.date.today()
    base = RESEARCHERS / researcher
    if not (base / "standards.toml").is_file():
        raise FileNotFoundError(f"no layer-3 encoding for {researcher!r}")
    std = _load(base / "standards.toml")
    conf = _load(base / "confirmations.toml") if (base / "confirmations.toml").is_file() else {}

    backstop = int(((conf.get("policy") or {}).get("backstop_days")) or 0)

    encodings, missing = [], []
    doms = std.get("domains") or {}
    for name in (doms.get("primary") or []):
        entry = doms.get(name) or {}
        rel = entry.get("encoding")
        if not rel:
            missing.append({"domain": name, "why": "the encoding names no file"})
            continue
        p = REPO / rel
        if not p.is_file():
            missing.append({"domain": name, "path": rel,
                            "why": "named in standards.toml and absent from disk"})
            continue
        encodings.append({
            "domain": name, "path": rel,
            "sha256": hashlib.sha256(p.read_bytes()).hexdigest()[:16],
            "bytes": p.stat().st_size,
            "severity_scale": entry.get("severity_scale"),
            "critical_level": entry.get("critical_level"),
            "reason": entry.get("reason"),
        })

    standards, overdue = [], []
    for key, rec in (conf.get("confirmed") or {}).items():
        needs = rec.get("needs_confirmation", True)
        last = rec.get("last_confirmed")
        row = {"key": key, "standard": rec.get("standard"),
               "publisher": rec.get("publisher"), "released": rec.get("released"),
               "last_confirmed": last, "needs_confirmation": bool(needs),
               "reason": rec.get("reason")}
        standards.append(row)
        if not needs:
            continue
        if not last:
            overdue.append({**row, "age_days": None,
                            "why": "needs confirmation and carries no date"})
            continue
        age = (today - dt.date.fromisoformat(last)).days
        row["age_days"] = age
        if backstop and age > backstop:
            overdue.append({**row, "why": f"{age} days since the last check, "
                                          f"backstop is {backstop}"})
    return {"researcher": researcher, "encodings": encodings, "standards": standards,
            "missing": missing, "overdue": overdue, "backstop_days": backstop,
            "as_of": today.isoformat()}


def render(ref: dict) -> str:
    """The markdown block a report appends. Plain enough to read aloud."""
    out = [f"## References accessed",
           "",
           f"Derived from the layer-3 encoding for `{ref['researcher']}` on "
           f"{ref['as_of']}, by `scripts/researcher_reference_list_2026-11-14.py`. "
           f"Every file below was READ and its digest taken; a file named by the "
           f"encoding and absent from disk is listed as missing rather than omitted.",
           ""]
    if ref["encodings"]:
        out += ["### Domain encodings", ""]
        for e in ref["encodings"]:
            scale = e["severity_scale"] or "none"
            lvl = f", critical at {e['critical_level']}" if e.get("critical_level") else ""
            out.append(f"- `{e['path']}` — {e['bytes']} bytes, sha256 `{e['sha256']}`. "
                       f"Severity scale: {scale}{lvl}.")
        out.append("")
    if ref["standards"]:
        out += ["### Standards cited", ""]
        for s in ref["standards"]:
            if not s["needs_confirmation"]:
                out.append(f"- {s['key']} — no confirmation needed: {s['reason']}")
                continue
            age = s.get("age_days")
            age_s = f", last checked {s['last_confirmed']}" + (
                f" ({age} days ago)" if age is not None else "")
            pub = f" ({s['publisher']}" + (f", released {s['released']}" if s.get("released") else "") + ")" \
                if s.get("publisher") else ""
            out.append(f"- {s['standard']}{pub}{age_s}.")
        out.append("")
    if ref["missing"]:
        out += ["### MISSING — named by the encoding and not found", ""]
        for mrec in ref["missing"]:
            out.append(f"- **{mrec['domain']}**: {mrec.get('path', '(no path)')} — {mrec['why']}")
        out.append("")
    if ref["overdue"]:
        out += [f"### OVERDUE against the encoding's own {ref['backstop_days']}-day backstop", ""]
        for o in ref["overdue"]:
            out.append(f"- **{o['standard']}**: {o['why']}")
        out.append("")
    if not ref["missing"] and not ref["overdue"]:
        out += ["Nothing missing and nothing overdue against the encoding's own "
                f"{ref['backstop_days']}-day backstop.", ""]
    return "\n".join(out)


def render_spoken(ref: dict) -> str:
    """The same list, speakable.

    ★ WRITTEN AFTER THE COMMIT GATE REFUSED, 2026-11-14, AND THE DEFECT WAS
    MINE. The first wiring appended `render()` to BOTH the markdown and the
    spoken render, and the spoken file must carry no markdown, no backticks, no
    em-dashes, no heading hashes and no file paths. 4 guards caught it at once,
    which is the gate working rather than failing.

    ★ AND IT CANNOT SIMPLY DROP THE PATHS, because naming the files IS what a
    reference list is for. So the spoken form names each encoding by its DOMAIN
    and says plainly that the paths and digests are in the markdown companion.
    The substance a listener needs, which domains were read and whether any
    standard is overdue, survives; the identifiers a reader needs stay where a
    reader will be.
    """
    L = ["REFERENCES ACCESSED", ""]
    L.append(f"This list is derived from the layer 3 encoding for {ref['researcher']} "
             f"on {ref['as_of']}, by a committed script rather than from memory. "
             f"Every file counted below was read and its digest taken. The exact "
             f"paths and digests are in the markdown companion to this file, "
             f"because a file path is not speakable.")
    L.append("")
    if ref["encodings"]:
        names = ", ".join(e["domain"].replace("_", " ") for e in ref["encodings"])
        L.append(f"Domain encodings read: {len(ref['encodings'])}. "
                 f"They are {names}.")
        for e in ref["encodings"]:
            scale = e["severity_scale"] or "none"
            dom = e["domain"].replace("_", " ")
            if scale in ("none", "None"):
                L.append(f"The {dom} encoding declares no consequence scale.")
            else:
                lvl = (f", with its critical level at {e['critical_level']}"
                       if e.get("critical_level") else "")
                L.append(f"The {dom} encoding declares the scale {scale}{lvl}.")
        L.append("")
    needs = [s for s in ref["standards"] if s["needs_confirmation"]]
    exempt = [s for s in ref["standards"] if not s["needs_confirmation"]]
    if needs:
        L.append(f"Standards cited that need periodic confirmation: {len(needs)}.")
        for s in needs:
            age = s.get("age_days")
            when = (f", last checked {s['last_confirmed']}, which is {age} days ago"
                    if age is not None else ", carrying no check date at all")
            pub = f", published by {s['publisher']}" if s.get("publisher") else ""
            L.append(f"{s['standard']}{pub}{when}.")
        L.append("")
    if exempt:
        L.append(f"Declared as needing no confirmation: {len(exempt)}. "
                 f"A domain with no consequence scale has nothing that can go "
                 f"stale, so it is not reported as overdue.")
        L.append("")
    if ref["missing"]:
        L.append(f"MISSING. {len(ref['missing'])} encoding or encodings are named "
                 f"by the layer 3 file and were not found on disk. This is "
                 f"reported rather than omitted, because an absence a reader "
                 f"cannot see is the fault a mechanised list exists to prevent.")
        for mrec in ref["missing"]:
            L.append(f"The {mrec['domain'].replace('_', ' ')} encoding: {mrec['why']}.")
        L.append("")
    if ref["overdue"]:
        L.append(f"OVERDUE. {len(ref['overdue'])} standard or standards are past "
                 f"the backstop of {ref['backstop_days']} days that the encoding "
                 f"itself declares.")
        for o in ref["overdue"]:
            L.append(f"{o['standard']}: {o['why']}.")
        L.append("")
    if not ref["missing"] and not ref["overdue"]:
        L.append(f"Nothing is missing and nothing is overdue against the "
                 f"{ref['backstop_days']} day backstop the encoding declares.")
        L.append("")
    return "\n".join(L)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description=(__doc__ or "").strip().splitlines()[0])
    ap.add_argument("--researcher", default=None,
                    help="whose encoding to read (default: every one found)")
    ap.add_argument("--json", action="store_true")
    ns = ap.parse_args(argv)

    who = [ns.researcher] if ns.researcher else researchers()
    if not who:
        print("no layer-3 encoding found under bench/directives/researchers; "
              "nothing to report, and that is itself the finding")
        return 1
    for r in who:
        ref = reference_list(r)
        if ns.json:
            import json
            print(json.dumps(ref, indent=2, sort_keys=True))
        else:
            print(render(ref))
    return 0


if __name__ == "__main__":
    sys.exit(main())
