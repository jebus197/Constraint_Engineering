# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'fmea_level_and_draft_encodings_2026-11-14', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: eed13c1db661fe3911740e0602c4e38269897cb69a44e48bbd4625afb4738df6
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Where a domain's critical LEVEL lands, and what a tier word reaches.

RUN:  python3 scripts/where_does_a_critical_level_land_2026-11-14.py

WHAT THIS DECIDES BY EXECUTION, for the panel question of 2026-11-14 on the
engineering critical level and on the 22 DRAFT encodings.

  M1  Is a domain's named `critical_level` the SAME quantity as the live
      `reference_runner_v3.CRITICAL_SEVERITY_THRESHOLD`?  Mutate the first,
      re-read, and see whether the second moves.
  M2  Where does each declared critical level sit in its own band list,
      counted from the TOP?  That rank is invariant under every strictly
      increasing relabel of the scale, so it is an admissible statistic under
      `cdsfl_core_formal.md` ("max, min, any SELECTED order statistic: YES").
  M3  Can anything in this repository consume TWO critical levels for one
      domain?  Count the fields `severity()` returns and the `CRITICAL LEVEL`
      lines `_severity_declaration` emits.
  M4  Does `encoding_tier` gate anything at dispatch?  Count its occurrences
      in the composer and the runner, and compose with the tier flipped.
  M5  Coverage over the 51 encodings, with Wilson intervals.
  M6  THE SUPPRESSION ASYMMETRY.  `_severity_declaration` returns "" whenever
      the composed text already matches `^SEVERITY SCALE:`, on the stated
      ground that the encoding is "the narrower, better-sourced statement".
      Measure whether that is true on the one property this project has
      already been burned by: does the encoding's scale line carry the
      standard's VERSION?

THE MANIFEST IS NOT MUTATED IN PLACE.  M1 and M4 point the vocabulary reader
at a COPY under the system temp directory.  The artefact under review is
opened read-only, which is also what the panel's falsifier-integrity rule
requires: a measurement must not write where a later reader looks.
"""
from __future__ import annotations

import ast
import math
import pathlib
import re
import shutil
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "bench"))

from bench.cdsfl_registry import composer as C                 # noqa: E402
from bench.cdsfl_registry import domain_vocabulary as V        # noqa: E402

MANIFEST = ROOT / "bench" / "cdsfl_registry" / "domain_manifest.toml"
RUNNER = ROOT / "bench" / "reference_runner_v3.py"
DIRECTIVES = ROOT / "bench" / "directives"


def wilson(k: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    """Wilson score interval, written out so the arithmetic is visible:
    centre (p + z^2/2n)/(1 + z^2/n), half-width
    z*sqrt(p(1-p)/n + z^2/4n^2)/(1 + z^2/n)."""
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1.0 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, centre - half), min(1.0, centre + half))


def runner_threshold() -> float:
    """Read CRITICAL_SEVERITY_THRESHOLD by AST, without importing the runner.
    The runner is 1.28 MB with a large dependency set; an AST read gets the
    committed literal with no import side effects."""
    tree = ast.parse(RUNNER.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == "CRITICAL_SEVERITY_THRESHOLD":
                    return float(ast.literal_eval(node.value))
    raise AssertionError("CRITICAL_SEVERITY_THRESHOLD not found in the runner")


def _reload():
    V.load.cache_clear()
    for fn in ("entry", "domains", "alias_map", "resolve", "subdomains",
               "default_subdomain", "tiers"):
        f = getattr(V, fn, None)
        if hasattr(f, "cache_clear"):
            f.cache_clear()


class ManifestCopy:
    """Point the ONE reader at a COPY, so the artefact is never written."""

    def __init__(self, transform):
        self.transform = transform

    def __enter__(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp(prefix="cdsfl_manifest_"))
        dst = self.tmp / "domain_manifest.toml"
        dst.write_text(self.transform(MANIFEST.read_text(encoding="utf-8")),
                       encoding="utf-8")
        self.saved = V.MANIFEST
        V.MANIFEST = dst
        _reload()
        return dst

    def __exit__(self, *exc):
        V.MANIFEST = self.saved
        _reload()
        shutil.rmtree(self.tmp, ignore_errors=True)
        return False


def band_index(levels, critical):
    """Index of the band the declared critical level names, in the declared
    ascending-severity band list."""
    c = str(critical).strip().lower()
    for i, b in enumerate(levels):
        toks = re.findall(r"[A-Za-z0-9.]+", str(b).lower())
        if c in toks:
            return i
    hits = [i for i, b in enumerate(levels) if c in str(b).strip().lower()]
    return hits[0] if hits else None


def main() -> int:
    bad = 0
    print("=" * 78)
    print("WHERE A CRITICAL LEVEL LANDS  --  executed")
    print("=" * 78)
    print(f"manifest sha-read from : {MANIFEST}")
    print(f"manifest writable here : {MANIFEST.stat().st_mode & 0o200 != 0} "
          f"(this script still does not write it)")

    # ---------------------------------------------------------------- M1
    print("\nM1. IS THE NAMED LEVEL THE SAME QUANTITY AS THE GATE FLOAT?")
    before_thr = runner_threshold()
    lvl = V.severity("engineering")["critical_level"]
    before_decl = C._severity_declaration("engineering", "")
    print(f"  runner CRITICAL_SEVERITY_THRESHOLD  = {before_thr!r}  "
          f"({type(before_thr).__name__})")
    print(f"  manifest engineering critical_level = {lvl!r}  "
          f"({type(lvl).__name__})")
    print("  NOTE THE TYPES. One is a float on [0,1] attached to a model-asserted")
    print("  severity; the other is a STRING naming a rank on an external ordinal")
    print("  scale. There is no arithmetic relation between them to break.")

    with ManifestCopy(lambda s: s.replace('\ncritical_level = "7"\n',
                                          '\ncritical_level = "9"\n', 1)):
        after_lvl = V.severity("engineering")["critical_level"]
        after_thr = runner_threshold()
        after_decl = C._severity_declaration("engineering", "")
    print(f"  with the level mutated 7 -> 9 on a COPY:")
    print(f"    manifest level now                = {after_lvl!r}")
    print(f"    runner threshold now              = {after_thr!r}")
    print(f"    composed declaration text changed = {before_decl != after_decl}")
    print(f"  artefact level after, unchanged     = "
          f"{V.severity('engineering')['critical_level']!r}")
    if after_thr != before_thr:
        print("  !! the named level REACHED the gate float"); bad += 1
    if before_decl == after_decl:
        print("  !! the named level reached NOTHING at all"); bad += 1
    if V.severity("engineering")["critical_level"] != "7":
        print("  !! artefact disturbed"); bad += 1
    print("  VERDICT: 2 DISTINCT QUANTITIES. The named level moved; the gate")
    print("           float did not. The named level reaches the PROMPT only.")

    import inspect

    import convergence_location as CL
    ents = [{"round": 1, "severity": 0.80,
             "description": "missing bound check at bench/a.py:10 in foo()"},
            {"round": 2, "severity": 0.80,
             "description": "missing bound check at bench/b.py:20 in bar()"}]
    syms = frozenset({"foo", "bar"})
    for fname in ("combined_novelty_series", "hierarchical_novelty_series",
                  "location_only_series"):
        fn = getattr(CL, fname)
        sig = inspect.signature(fn)
        out = fn(ents, 2, syms)
        print(f"  CL.{fname:28s} -> {out if not isinstance(out, dict) else list(out)[:4]}")
        print(f"     params: {list(sig.parameters)}")
        print(f"     has a `domain` parameter : {'domain' in sig.parameters}")
        print(f"     has a `critical_threshold`: {'critical_threshold' in sig.parameters}"
              f"  default={sig.parameters['critical_threshold'].default if 'critical_threshold' in sig.parameters else None!r}")
    src = (ROOT / "bench/convergence_location.py").read_text(encoding="utf-8")
    print(f"  'critical_level' occurrences in convergence_location.py = "
          f"{src.count('critical_level')}")
    print(f"  'severity_scale' occurrences                            = "
          f"{src.count('severity_scale')}")
    print("  The series takes a FLOAT severity_threshold. No domain name and no")
    print("  named level enter it. Q1 is a REPORTING question, not a convergence")
    print("  one, and that BOUNDS its consequence.")

    # ---------------------------------------------------------------- M2
    print("\nM2. RANK OF EACH DECLARED CRITICAL LEVEL, COUNTED FROM THE TOP")
    print("    (invariant under every strictly increasing relabel -> admissible)")
    rows = []
    for dom in V.domains():
        sev = V.severity(dom)
        if sev["scale"] in (None, "none", "composed") or not sev["critical_level"]:
            continue
        lv = sev["levels"]
        i = band_index(lv, sev["critical_level"])
        rows.append((dom, sev["scale"], sev["critical_level"], len(lv), len(lv) - i))
    for dom, scale, cl, n, ft in rows:
        print(f"  {dom:14s} {scale[:36]:36s} critical={cl!r:14s} bands={n} "
              f"rank_from_top={ft} upset={ft}")
    others = sorted(r[4] for r in rows if r[0] != "engineering")
    eng = [r[4] for r in rows if r[0] == "engineering"][0]
    print(f"\n  engineering at 7 -> rank_from_top = {eng}, upset = {eng}")
    print(f"  the other declared scales            = {others} "
          f"(min {min(others)}, max {max(others)})")
    print("  engineering at 9 -> rank_from_top = 1, upset = 1")
    print("  A cut at the MAXIMAL band makes the predicate `c >= theta` equal to")
    print("  `c == max`: an IDENTITY TEST, not an ordinal threshold, and the")
    print("  ordering above the cut then carries no information. No other declared")
    print(f"  scale does this. 9 puts engineering outside the observed range "
          f"[{min(others)}, {max(others)}].")

    # ---------------------------------------------------------------- M3
    print("\nM3. CAN ANYTHING CONSUME A SECOND CRITICAL LEVEL?")
    keys = sorted(V.severity("engineering").keys())
    lvl_keys = [k for k in keys if "critical" in k and not k.endswith("note")]
    decl = C._severity_declaration("engineering", "")
    n_lines = len(re.findall(r"^\s*CRITICAL LEVEL:", decl, re.M))
    print(f"  severity() keys                            = {keys}")
    print(f"  keys carrying a critical level             = {lvl_keys} "
          f"-> {len(lvl_keys)}")
    print(f"  CRITICAL LEVEL lines reaching the prompt   = {n_lines}")
    prod = []
    for p in sorted(ROOT.glob("bench/**/*.py")) + sorted(ROOT.glob("scripts/**/*.py")):
        rel = p.relative_to(ROOT).as_posix()
        if rel.startswith(("bench/logs/", "bench/tests/")) or "seat_evidence" in rel:
            continue
        if "critical_level" in p.read_text(encoding="utf-8", errors="ignore"):
            prod.append(rel)
    print(f"  product modules mentioning critical_level  = {prod}")
    if len(lvl_keys) != 1 or n_lines != 1:
        print("  !! more than one level is already carried"); bad += 1
    print("  VERDICT: the surface carries EXACTLY 1 level and emits EXACTLY 1")
    print("           line. A SECOND declared cut is an addition nothing reaches.")
    print("  AND THE SECOND LANDMARK ALREADY REACHES THE SEAT ANYWAY, on LEVELS:")
    for ln in decl.splitlines():
        if ln.strip().startswith("LEVELS:"):
            print(f"    {ln.strip()}")

    # ---------------------------------------------------------------- M4
    print("\nM4. DOES `encoding_tier` GATE ANYTHING AT DISPATCH?")
    for name, path in (("composer.py", ROOT / "bench/cdsfl_registry/composer.py"),
                       ("reference_runner_v3.py", RUNNER)):
        t = path.read_text(encoding="utf-8", errors="ignore")
        print(f"  {name:24s} 'encoding_tier'={t.count('encoding_tier')}  "
              f"'CROSS_VERIFIED'={t.count('CROSS_VERIFIED')}  "
              f"'DRAFT'={t.count('DRAFT')}")
    a = C._severity_declaration("engineering", "")
    with ManifestCopy(lambda s: s.replace('encoding_tier = "DRAFT"',
                                          'encoding_tier = "CROSS_VERIFIED"')):
        b = C._severity_declaration("engineering", "")
        tier_now = V.entry("engineering")["encoding_tier"]
    print(f"  with EVERY tier flipped DRAFT -> CROSS_VERIFIED on a copy:")
    print(f"    manifest tier now                  = {tier_now!r}")
    print(f"    composed declaration byte-identical= {a == b}")
    print(f"  artefact tier after, unchanged       = "
          f"{V.entry('engineering')['encoding_tier']!r}")
    if a != b:
        print("  !! the tier DOES change the composed text"); bad += 1
    print("  VERDICT: the tier is VALIDATED for membership in `tiers` and PRINTED")
    print("           by the module CLI. It gates NO dispatch. Q2's answer changes")
    print("           no run until a consumer is wired.")

    # ---------------------------------------------------------------- M5
    print("\nM5. COVERAGE, WITH INTERVALS")
    txts = sorted(DIRECTIVES.rglob("*.txt"))
    dom_txts = [p for p in txts if p.parent.name != "universal"]
    with_scale = [p for p in dom_txts
                  if re.search(r"^SEVERITY SCALE:",
                               p.read_text(encoding="utf-8", errors="ignore"), re.M)]
    k, n = len(with_scale), len(dom_txts)
    lo, hi = wilson(k, n)
    print(f"  .txt under bench/directives            = {len(txts)}")
    print(f"  domain encodings (universal excluded)  = {n}")
    print(f"  carrying their own SEVERITY SCALE line = {k} of {n} = {k/n:.4%}, "
          f"Wilson [{lo:.4%}, {hi:.4%}]")
    tiered = [d for d in V.domains() if V.entry(d).get("encoding_tier")]
    drafts = [d for d in tiered if V.entry(d)["encoding_tier"] == "DRAFT"]
    lo2, hi2 = wilson(len(drafts), len(tiered))
    print(f"  manifest domains declaring a tier      = {len(tiered)}")
    print(f"  of those at DRAFT                      = {len(drafts)} of "
          f"{len(tiered)} = {len(drafts)/len(tiered):.4%}, "
          f"Wilson [{lo2:.4%}, {hi2:.4%}]")

    # ---------------------------------------------------------------- M6
    print("\nM6. THE SUPPRESSION ASYMMETRY -- is the encoding really better-sourced?")
    print("    `_severity_declaration` returns '' when the text matches")
    print("    ^SEVERITY SCALE:, on the ground that the encoding is 'the narrower,")
    print("    better-sourced statement'. Tested on VERSION-CARRYING, the property")
    print("    the CVSS v3.1 -> v4.0 correction was about.")
    # the version token the manifest carries for each declared scale
    manifest_tokens = {
        "FMEA": "2019", "CVSS": "v4.0", "CTCAE": "v5.0", "GHS": "Rev. 11",
    }
    offenders = []
    for p in sorted(with_scale):
        txt = p.read_text(encoding="utf-8", errors="ignore")
        m = re.search(r"^SEVERITY SCALE:.*?(?=^[A-Z][A-Z ]{3,}:)", txt,
                      re.M | re.S)
        block = m.group(0) if m else ""
        for fam, tok in manifest_tokens.items():
            if re.search(rf"\b{fam}\b", block) and tok.lower() not in block.lower():
                # does ANY version token for that family appear in the block?
                if not re.search(r"v\d|Rev\.?\s*\d|\b(19|20)\d\d\b", block):
                    offenders.append((p.relative_to(ROOT).as_posix(), fam, tok))
    print(f"\n  encodings naming a manifest-declared scale with NO version token")
    print(f"  anywhere in their SEVERITY SCALE block: {len(offenders)}")
    for rel, fam, tok in offenders:
        print(f"    {rel:62s} cites {fam} (manifest has {tok!r})")
    ko, no = len(offenders), len(with_scale)
    lo3, hi3 = wilson(ko, no)
    print(f"  {ko} of {no} = {ko/no:.4%}, Wilson [{lo3:.4%}, {hi3:.4%}]")
    print("  Each of these is a seat told to report a (value, scale-name) pair and")
    print("  handed a scale name with no edition, while the manifest HOLDS the")
    print("  edition and the suppression rule prevents it from arriving.")

    print("\n" + "=" * 78)
    print(f"internal consistency checks failed: {bad}")
    print("=" * 78)
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
