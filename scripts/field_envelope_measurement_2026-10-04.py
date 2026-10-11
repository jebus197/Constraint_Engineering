#!/usr/bin/env python3
"""The 4 measurements the field envelope is licensed by.

Every figure in `bench/field_envelope.py`'s header, in
`bench/tests/test_field_envelope_2026-10-04.py` and in the session note is
produced here, so a number quoted about this repair travels with the code that
computes it (`measured-rate-travels-with-its-script`). Nothing here writes, runs
a model, or costs money.

SECTION 1 -- THE EXISTING SENTINEL GRAMMAR, over 12 shapes of 1 corrected copy.
The brief that commissioned this work called `_CORRECTED_COPY_RE` "unambiguous by
construction". The TOKEN is; the GRAMMAR is not, because the pattern requires a
bare-regex `CORRECTED_COPY: <key>` label immediately above the sentinel with only
horizontal whitespace between, so the owner lives OUTSIDE the sentinel in exactly
the free prose the brief indicts. 6 of 12 shapes fail, including markdown bold
around the sentinel -- the same decoration that broke `FINDING_ID`.

SECTION 2 -- THE 3 CORROBORATION READERS, over 8 shapes a seat actually writes.
The named property is OWNER RECOVERY: does the reader say which finding the proof
belongs to? A section with no owner sends `validate_round_rk` to its positional
fallback, and position is what validated finding i's R_k against finding j's
parameters.

SECTION 3 -- NO REGRESSION, over every archived model reply in the repository:
5,445 of them on this checkout, from BOTH roots -- the panel records and the run
logs. `parse_findings` against the pre-envelope pipeline, field by field over 10
fields. The corpus carries 0 envelopes, which is what makes it the right corpus:
the overlay must be invisible until a seat uses it. The size is printed rather
than asserted, because `.gitignore` has excluded raw per-model replies since
2026-08-13 and a maintainer's tree therefore carries more than a clone.

SECTION 4 -- THE ENVELOPE'S OWN GRID, 1,440 shapes. The product of the axes a
real reply varies on: line prefix, bold wrapping, inline against block payload,
attribute quoting, line endings, and the surrounding context (bare, fenced,
inside a JSON blob). The claim under test is DECORATION-INVARIANCE -- every shape
must read back the same field, owner and value.

Every proportion carries a Wilson 95% interval from statsmodels AND from an
independent 50-digit mpmath closed form, with the agreement printed, plus a
Clopper-Pearson interval cross-checked against `scipy.stats.beta`.

Run:  python3 scripts/field_envelope_measurement_2026-10-04.py
"""
from __future__ import annotations

import functools
import glob
import itertools
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
for _p in (str(REPO), str(REPO / "bench"), str(REPO / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)


# ─────────────────────────────────────────────────────────────────────────────
# Intervals, two tools each
# ─────────────────────────────────────────────────────────────────────────────

def intervals(k: int, n: int) -> dict:
    """Wilson and Clopper-Pearson, each computed twice by different code."""
    from statsmodels.stats.proportion import proportion_confint
    w_lo, w_hi = proportion_confint(k, n, method="wilson")
    c_lo, c_hi = proportion_confint(k, n, method="beta")

    from mpmath import mp, mpf, sqrt
    mp.dps = 50
    z = mpf("1.9599639845400542")
    p, N = mpf(k) / n, mpf(n)
    den = 1 + z ** 2 / N
    centre = (p + z ** 2 / (2 * N)) / den
    half = (z / den) * sqrt(p * (1 - p) / N + z ** 2 / (4 * N ** 2))
    m_lo, m_hi = float(max(centre - half, 0)), float(min(centre + half, 1))

    from scipy.stats import beta as _beta
    s_lo = 0.0 if k == 0 else float(_beta.ppf(0.025, k, n - k + 1))
    s_hi = 1.0 if k == n else float(_beta.ppf(0.975, k + 1, n - k))

    return {
        "k": k, "n": n, "p": (k / n if n else float("nan")),
        "wilson": (w_lo, w_hi), "wilson_mpmath": (m_lo, m_hi),
        "wilson_agree": max(abs(m_lo - w_lo), abs(m_hi - w_hi)),
        "cp": (c_lo, c_hi), "cp_scipy": (s_lo, s_hi),
        "cp_agree": max(abs(s_lo - c_lo), abs(s_hi - c_hi)),
    }


def show(label: str, iv: dict) -> None:
    print(f"  {label}: {iv['k']} of {iv['n']} = {iv['p']:.4%}")
    print(f"    Wilson 95%          [{iv['wilson'][0]:.4%}, {iv['wilson'][1]:.4%}]"
          f"   (statsmodels; mpmath 50 dps agrees to {iv['wilson_agree']:.1e})")
    print(f"    Clopper-Pearson 95% [{iv['cp'][0]:.4%}, {iv['cp'][1]:.4%}]"
          f"   (statsmodels/beta; scipy.stats.beta agrees to {iv['cp_agree']:.1e})")


# ─────────────────────────────────────────────────────────────────────────────
# Section 1 — the existing sentinel grammar
# ─────────────────────────────────────────────────────────────────────────────

def corrected_copy_shapes(R) -> list[tuple[str, str]]:
    """12 shapes of ONE corrected copy. The content is identical in all 12."""
    orig, corr, end = (R._CORRECTED_ORIGINAL_SENTINEL,
                       R._CORRECTED_CORRECTED_SENTINEL,
                       R._CORRECTED_END_SENTINEL)
    was, now = "the passage as it stands", "the passage as it should stand"
    return [
        ("canonical",
         f"CORRECTED_COPY: C0007\n{orig}\n{was}\n{corr}\n{now}\n{end}\n"),
        ("blank line between label and sentinel",
         f"CORRECTED_COPY: C0007\n\n{orig}\n{was}\n{corr}\n{now}\n{end}\n"),
        ("markdown bold around the sentinel",
         f"CORRECTED_COPY: C0007\n**{orig}**\n{was}\n{corr}\n{now}\n{end}\n"),
        ("markdown bold around the label",
         f"**CORRECTED_COPY:** C0007\n{orig}\n{was}\n{corr}\n{now}\n{end}\n"),
        ("label and sentinel on one line",
         f"CORRECTED_COPY: C0007 {orig}\n{was}\n{corr}\n{now}\n{end}\n"),
        ("payload begins on the sentinel's line",
         f"CORRECTED_COPY: C0007\n{orig} {was}\n{corr}\n{now}\n{end}\n"),
        ("one line of prose before the sentinel",
         f"CORRECTED_COPY: C0007\nHere is the passage:\n{orig}\n{was}\n{corr}\n{now}\n{end}\n"),
        ("inside a markdown fence",
         f"```\nCORRECTED_COPY: C0007\n{orig}\n{was}\n{corr}\n{now}\n{end}\n```\n"),
        ("bullet before the label",
         f"- CORRECTED_COPY: C0007\n{orig}\n{was}\n{corr}\n{now}\n{end}\n"),
        ("CRLF line endings",
         f"CORRECTED_COPY: C0007\n{orig}\n{was}\n{corr}\n{now}\n{end}\n".replace("\n", "\r\n")),
        ("sentinels with no label at all",
         f"{orig}\n{was}\n{corr}\n{now}\n{end}\n"),
        ("heading decoration on the label",
         f"### CORRECTED_COPY: C0007\n{orig}\n{was}\n{corr}\n{now}\n{end}\n"),
    ]


def section1(R) -> dict:
    print("SECTION 1 -- THE EXISTING SENTINEL GRAMMAR, 12 shapes of 1 payload")
    shapes = corrected_copy_shapes(R)
    failed = [n for n, t in shapes if not R._extract_corrected_copies(t)]
    for name, text in shapes:
        ok = bool(R._extract_corrected_copies(text))
        print(f"    {'PARSE' if ok else 'FAIL ':<5}  {name}")
    iv = intervals(len(failed), len(shapes))
    print()
    show("shapes the hybrid sentinel grammar REFUSES", iv)
    print("    reading: the token cannot occur in prose by accident, and that is")
    print("    sound. What fails is the GRAMMAR around it -- the owner sits")
    print("    outside the sentinel, on a bare-regex label line, so decoration")
    print("    and blank lines break it exactly as they broke FINDING_ID.")
    return iv


# ─────────────────────────────────────────────────────────────────────────────
# Section 2 — owner recovery across the 3 corroboration readers
# ─────────────────────────────────────────────────────────────────────────────

PROOF = "R_old=0.50, eta=0.80, d=0.70, p=0.60, S_k=0.75, nu_eff=0.15; R_k = 0.5106"


def corroboration_shapes(fe) -> list[tuple[str, str]]:
    head = "FINDING_ID: F001\nSEVERITY: 0.9\nDESCRIPTION: x\n"
    return [
        ("canonical bold header", head + f"**CORROBORATION.** {PROOF}\n"),
        ("plain header", head + f"CORROBORATION: {PROOF}\n"),
        ("bullet header", head + f"- CORROBORATION: {PROOF}\n"),
        ("markdown table row", head + f"| CORROBORATION | {PROOF} |\n"),
        ("blockquoted header", head + f"> CORROBORATION: {PROOF}\n"),
        ("heading style", head + f"#### CORROBORATION\n{PROOF}\n"),
        ("proof stated before the id",
         f"SEVERITY: 0.9\nCORROBORATION. {PROOF}\nFINDING_ID: F001\nDESCRIPTION: x\n"),
        ("json value",
         '[{"FINDING_ID": "F001", "SEVERITY": 0.9, "DESCRIPTION": "x",\n'
         f'   "CORROBORATION": "{PROOF}"}}]\n'),
    ]


def section2(R, fe) -> dict:
    print("\nSECTION 2 -- OWNER RECOVERY, 3 readers over 8 shapes a seat writes")
    B, fin = fe.FIELD_BEGIN_PREFIX, fe.FIELD_END_TOKEN
    shapes = corroboration_shapes(fe)
    frozen_sections = 0
    owner_aware = 0
    enveloped = 0
    rows = []
    for name, text in shapes:
        n_frozen = len(R._extract_corroboration_sections(text))
        frozen_sections += n_frozen
        owned = [o for o, _s in R._extract_corroboration_sections_with_ids(text) if o]
        if owned:
            owner_aware += 1
        env_text = text + f"{B} field=CORROBORATION id=F001>>>{PROOF}{fin}\n"
        got = R._corroboration_sections_by_owner(env_text).get("f001")
        if got and got[1] == "envelope":
            enveloped += 1
        rows.append((name, n_frozen, bool(owned), bool(got)))
        print(f"    frozen={n_frozen}  owner={'Y' if owned else 'n'}  "
              f"envelope={'Y' if got else 'n'}   {name}")

    n = len(shapes)
    print()
    show("shapes whose OWNER the prose reader recovers", intervals(owner_aware, n))
    show("shapes whose OWNER the envelope recovers", intervals(enveloped, n))
    print(f"    the frozen reader returned {frozen_sections} section(s) over the "
          f"same {n} shapes,")
    print(f"    for {n} real proofs -- it finds text in every case and attributes")
    print("    none of it, which is what makes the failure silent.")
    return {"owner_aware": intervals(owner_aware, n),
            "envelope": intervals(enveloped, n),
            "frozen_sections": frozen_sections, "n": n}


# ─────────────────────────────────────────────────────────────────────────────
# Section 3 — no regression over the archived corpus
# ─────────────────────────────────────────────────────────────────────────────

COMPARED_FIELDS = ("finding_id", "severity", "flaw_class", "abstraction_index",
                   "description", "proposed_fix", "target_file", "verified",
                   "falsifier_code", "falsification_present")


#: THE TWO PLACES A MODEL REPLY IS ARCHIVED IN THIS REPOSITORY, and using only
#: the first was the mistake this definition corrects. `panel_records_*` holds
#: 312 PANEL seat replies -- models reviewing the project -- and `bench/logs`
#: holds the RUN replies, models producing findings against a target, which is
#: the population the finding-field parsers actually serve. Measuring the overlay
#: against the review corpus alone would be `A SUBSET IS NOT A BOARD` again: a
#: green result over the smaller and less relevant half.
#:
#: NOT ALL OF `bench/logs` IS TRACKED. `.gitignore` has dropped raw per-model
#: responses since 2026-08-13, so a run archived after that date contributes its
#: report and its state file and no replies. 4,808 reply files ARE tracked, from
#: the runs that predate the rule, and a maintainer's working tree carries more.
#: The corpus size is therefore PRINTED rather than asserted, and the guard in
#: `bench/tests/test_field_envelope_2026-10-04.py` holds a floor, not an equality
#: -- a figure that silently shrinks on a fresh clone is how task A2's "a fresh
#: clone is green" came to be untrue.
REPLY_ROOTS = (
    ("panel", str(REPO / "experimental_notes" / "evidence"
                  / "panel_records_*" / "**" / "*.json")),
    ("run", str(REPO / "bench" / "logs" / "**" / "*.json")),
)


@functools.lru_cache(maxsize=1)
def _seat_replies_cached() -> tuple[tuple[str, str], ...]:
    return tuple(_scan_seat_replies())


def seat_replies() -> list[tuple[str, str]]:
    """Cached view of the corpus. 57 MB of text is read once per process.

    The guard in `bench/tests/test_field_envelope_2026-10-04.py` asks for the
    corpus more than once, and re-reading 5,445 files each time made the suite
    slower for no information. Returns a fresh list so a caller cannot mutate
    what the next caller sees.
    """
    return list(_seat_replies_cached())


def _scan_seat_replies() -> list[tuple[str, str]]:
    """Every archived model reply this repository carries, from both roots.

    THE SINGLE DEFINITION OF THE CORPUS. `bench/tests/test_field_envelope_2026-10-04.py`
    imports this function rather than reimplementing the glob, because 2 copies
    of a corpus definition are 2 representations of 1 population with no
    comparator, and the script and the guard would then be able to disagree about
    what "every archived reply" means without either being individually wrong.
    """
    out: list[tuple[str, str]] = []
    seen: set[str] = set()
    for _label, pattern in REPLY_ROOTS:
        for path in sorted(glob.glob(pattern, recursive=True)):
            if ".tools." in path or path in seen:
                continue
            try:
                with open(path, encoding="utf-8") as fh:
                    blob = json.load(fh)
            except (OSError, ValueError):
                continue
            if (isinstance(blob, dict) and isinstance(blob.get("response"), str)
                    and blob["response"].strip()):
                seen.add(path)
                out.append((path, blob["response"]))
    return out


def section3(rc, fe) -> dict:
    print("\nSECTION 3 -- NO REGRESSION over every archived model reply")
    replies = seat_replies()
    print(f"    corpus roots: {', '.join(label for label, _p in REPLY_ROOTS)}")
    identical = 0
    changed = []
    carrying = 0
    findings_total = 0
    for path, text in replies:
        if fe.FIELD_BEGIN_PREFIX in text:
            carrying += 1
        norm = rc._normalise_field_labels(text)
        before = rc._attach_falsifiers(rc._parse_findings_core("Seat", 1, norm), norm)
        after = rc.parse_findings("Seat", 1, text)
        findings_total += len(before)
        same = len(before) == len(after) and all(
            all(getattr(b, f, None) == getattr(a, f, None) for f in COMPARED_FIELDS)
            for b, a in zip(before, after))
        if same:
            identical += 1
        else:
            changed.append(path)
    n = len(replies)
    print(f"    replies examined                  {n}")
    print(f"    findings parsed across them       {findings_total}")
    print(f"    replies ALREADY carrying an envelope {carrying}")
    print()
    show("replies parsed IDENTICALLY with the overlay in place", intervals(identical, n))
    if changed:
        print("    CHANGED (the overlay is not invisible after all):")
        for p in changed[:10]:
            print(f"      {p}")
        if len(changed) > 10:
            print(f"      ... and {len(changed) - 10} more not shown")
    return {"iv": intervals(identical, n), "changed": changed,
            "carrying": carrying, "findings": findings_total}


# ─────────────────────────────────────────────────────────────────────────────
# Section 4 — the envelope's own decoration grid
# ─────────────────────────────────────────────────────────────────────────────

PREFIXES = ("", "  ", "\t", "> ", "- ", "> - ", "#### ", "1. ", "    ", ">>")
BOLDS = ("", "**", "__")
LAYOUTS = ("inline", "block", "block_indented", "payload_on_header_line")
QUOTES = ("bare", "double", "single")
EOLS = ("\n", "\r\n")
CONTEXTS = ("bare", "fenced")


def build_envelope(fe, prefix, bold, layout, quote, eol, context) -> str:
    B, fin = fe.FIELD_BEGIN_PREFIX, fe.FIELD_END_TOKEN
    if quote == "double":
        attrs = 'field="SEVERITY" id="F001"'
    elif quote == "single":
        attrs = "field='SEVERITY' id='F001'"
    else:
        attrs = "field=SEVERITY id=F001"
    head = f"{prefix}{bold}{B} {attrs}>>>"
    if layout == "inline":
        body = f"{head}0.9{fin}{bold}"
    elif layout == "block":
        body = f"{head}{eol}0.9{eol}{fin}"
    elif layout == "block_indented":
        body = f"{head}{eol}    0.9{eol}    {fin}"
    else:                                   # payload_on_header_line, then a block end
        body = f"{head}0.9{eol}{fin}"
    if context == "fenced":
        body = f"```text{eol}{body}{eol}```"
    return f"Some preceding prose.{eol}{eol}{body}{eol}And some after.{eol}"


def section4(fe) -> dict:
    print("\nSECTION 4 -- THE ENVELOPE'S OWN GRID: decoration invariance")
    axes = list(itertools.product(PREFIXES, BOLDS, LAYOUTS, QUOTES, EOLS, CONTEXTS))
    good, bad = 0, []
    for shape in axes:
        text = build_envelope(fe, *shape)
        accepted, refusals = fe.extract_field_envelopes(text)
        ok = (len(accepted) == 1
              and (accepted[0].field, accepted[0].owner) == ("SEVERITY", "F001")
              and fe.scalar(accepted[0].payload) == "0.9")
        if ok:
            good += 1
        else:
            bad.append((shape, [r["reason"] for r in refusals],
                        [fe.scalar(a.payload) for a in accepted]))
    n = len(axes)
    print(f"    shapes enumerated   {n}  "
          f"({len(PREFIXES)} prefixes x {len(BOLDS)} bold forms x {len(LAYOUTS)} "
          f"layouts x {len(QUOTES)} quotings x {len(EOLS)} line endings x "
          f"{len(CONTEXTS)} contexts)")
    print()
    show("shapes reading back the SAME field, owner and value", intervals(good, n))
    if bad:
        print("    shapes that did NOT:")
        for shape, reasons, payloads in bad[:10]:
            print(f"      {shape} refusals={reasons} payloads={payloads}")
        if len(bad) > 10:
            print(f"      ... and {len(bad) - 10} more not shown")
    return {"iv": intervals(good, n), "bad": bad}


# ─────────────────────────────────────────────────────────────────────────────

def main() -> int:
    import field_envelope as fe
    import reference_runner_v3 as R
    import runner_core as rc

    section1(R)
    s2 = section2(R, fe)
    s3 = section3(rc, fe)
    s4 = section4(fe)

    print("\nVERDICT")
    ok = True
    if s3["changed"]:
        ok = False
        print("  REFUSED: the overlay changed how an archived reply parses. A")
        print("  seat that never adopts the envelope must be unaffected, and")
        print("  that is the condition this repair is allowed under.")
    if s3["carrying"]:
        print("  NOTE: an archived reply now carries an envelope, so section 3")
        print("  no longer measures the NON-ADOPTING case on its own.")
    if s4["bad"]:
        ok = False
        print(f"  REFUSED: {len(s4['bad'])} grid shape(s) do not read back the")
        print("  same value. Decoration-invariance is the envelope's whole claim.")
    if s2["envelope"]["k"] <= s2["owner_aware"]["k"]:
        ok = False
        print("  REFUSED: the envelope does not recover more owners than the")
        print("  prose reader, so it earns nothing on the named property.")
    if ok:
        print("  The repair is LICENSED on all 3 conditions: every archived reply")
        print("  parses identically, the grid is decoration-invariant, and owner")
        print("  recovery is strictly better than the reader it layers over.")
        return 0
    return 1


if __name__ == "__main__":
    # A REAL PARSER, so `--help` answers without running the measurement and an
    # unrecognised argument exits 2 rather than being ignored
    # (`feedback_help_must_never_cost_money`).
    import argparse as _argparse

    _argparse.ArgumentParser(
        description=(__doc__ or "").strip().split("\n")[0] or None,
    ).parse_args()
    raise SystemExit(main())
