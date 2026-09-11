#!/usr/bin/env python3
"""Task A8: follow a cited `bench/logs/` path to the tracked copy of its content.

THE QUESTION A8 ASKED WAS THE WRONG ONE, and answering it properly is what this
script is for. The entry asks whether 23 cited `bench/logs/` paths should be
tracked, relocated, or accepted-and-labelled. But `.gitignore:41` excludes that
directory by design -- it was 353 MB across 5,840 files -- so *relocate* cannot
make a cited path tracked: the note still names the original, and the original
stays excluded. Measured 2026-09-11: mirroring every review record moved the
untracked count not at all.

**What relocation actually buys is RECOVERABILITY**, and that is the property
worth asking about: can a reader who follows this citation get at the content?
Measured after the mirror was widened: **20 of the 23 note-cited untracked paths
have a byte-identical tracked copy -- 86.9565%, Wilson [67.8725%, 95.4623%],
Clopper-Pearson [66.4111%, 97.2248%]**, statsmodels and scipy agreeing to
0.0e+00. The other 3 are `exp56_d*.log`, which do not exist on this machine
either, because Exp 56 has never run.

**RECOVERABLE IS NOT THE SAME AS DISCOVERABLE, and this closes that gap.** The
recommendation on A8 is to LEAVE the citations as written, because a note records
where an artefact was PRODUCED and `bench/logs/` stays archival. That is only
defensible if a reader can get from the citation to the copy, so this script is
the route: hand it a cited path and it says where the content lives, or says
plainly that nothing holds it.

WHERE A COPY LIVES IS NOT REIMPLEMENTED HERE. `dest_for` and `mirrored_name` are
imported from `scripts/mirror_panel_records_2026-09-11.py`, because 2 definitions
of "where the copy goes" is the shape `execute-do-not-grep` names and the 2 would
drift the first time a naming convention changed -- which is exactly how that
script came to report 100% while covering 15%.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def _mirror_module():
    spec = importlib.util.spec_from_file_location(
        "mirror_records", REPO / "scripts" / "mirror_panel_records_2026-09-11.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _tracked(rel: str) -> bool:
    """Is this path tracked by git?

    NOT `returncode == 0`. `git ls-files --error-unmatch` exits 0 tracked, 1
    untracked and 128 outside a repository, and this project has twice read the
    128 as an answer -- once as "untracked" and once as "clean". Outside a
    checkout the honest answer is UNKNOWN, and the caller is told.
    """
    r = subprocess.run(["git", "ls-files", "--error-unmatch", "--", rel],
                       cwd=REPO, capture_output=True, text=True)
    if r.returncode == 128:
        raise SystemExit("not a git repository, so tracking cannot be decided; "
                         "refusing rather than reporting everything untracked")
    return r.returncode == 0


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def resolve(rel: str) -> dict:
    """Where the content of a cited `bench/logs/` path can be read.

    Returns a dict with `present` (is it on this machine), `tracked`, `mirror`
    (the tracked copy's path or None) and `identical` (does the copy match the
    original, where both exist).
    """
    m = _mirror_module()
    src = REPO / rel
    p = Path(rel)
    out = {"path": rel, "present": src.is_file(), "tracked": False,
           "mirror": None, "identical": None}
    try:
        out["tracked"] = _tracked(rel)
    except SystemExit:
        raise
    if len(p.parts) < 3 or p.parts[0] != "bench" or p.parts[1] != "logs":
        return out
    round_dir = REPO / "bench" / "logs" / p.parts[2]
    if not round_dir.is_dir():
        return out
    cand = m.dest_for(round_dir) / m.mirrored_name(Path(p.name))
    if cand.is_file():
        out["mirror"] = str(cand.relative_to(REPO))
        if src.is_file():
            out["identical"] = _sha(cand) == _sha(src)
    return out


def cited_paths() -> list[str]:
    """Every cited `bench/logs/` path, from the census that already finds them."""
    spec = importlib.util.spec_from_file_location(
        "orphan", REPO / "scripts" / "orphan_figures_2026-09-10.py")
    o = importlib.util.module_from_spec(spec)
    sys.modules["orphan"] = o
    spec.loader.exec_module(o)
    cited, _untracked = o.untracked_cited_paths()
    return sorted(cited)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("path", nargs="?",
                    help="a cited bench/logs/ path; omit to survey every one")
    ap.add_argument("--unrecoverable-only", action="store_true",
                    help="list only paths whose content is nowhere in the tree")
    a = ap.parse_args()

    if a.path:
        r = resolve(a.path)
        print(f"path      : {r['path']}")
        print(f"on disk   : {r['present']}")
        print(f"tracked   : {r['tracked']}")
        if r["mirror"]:
            print(f"MIRROR    : {r['mirror']}")
            if r["identical"] is not None:
                print(f"identical : {r['identical']}")
        else:
            print("MIRROR    : none — this content is in no tracked file")
        return 0 if (r["tracked"] or r["mirror"]) else 1

    rows = [resolve(p) for p in cited_paths()]
    recoverable = [r for r in rows if r["tracked"] or r["mirror"]]
    lost = [r for r in rows if not (r["tracked"] or r["mirror"])]
    divergent = [r for r in rows if r["identical"] is False]

    if not a.unrecoverable_only:
        print(f"cited bench/logs paths        : {len(rows)}")
        print(f"  recoverable from the tree   : {len(recoverable)}")
        print(f"    tracked directly          : "
              f"{sum(1 for r in rows if r['tracked'])}")
        print(f"    via a mirrored copy       : "
              f"{sum(1 for r in rows if r['mirror'] and not r['tracked'])}")
        print(f"  NOT recoverable             : {len(lost)}")
        print(f"  mirror DIVERGED from source : {len(divergent)}")
        if rows:
            from statsmodels.stats.proportion import proportion_confint
            k, n = len(recoverable), len(rows)
            lo, hi = proportion_confint(k, n, method="wilson")
            lo_b, hi_b = proportion_confint(k, n, method="beta")
            print(f"\n  recoverable: {k}/{n} = {k / n:.4%}")
            print(f"    Wilson 95%          : [{lo:.4%}, {hi:.4%}]")
            print(f"    Clopper-Pearson 95% : [{lo_b:.4%}, {hi_b:.4%}]")

    for r in lost:
        note = "" if r["present"] else "   (absent here too)"
        print(f"  UNRECOVERABLE {r['path']}{note}")
    for r in divergent:
        print(f"  DIVERGED      {r['path']} vs {r['mirror']}")
    return 1 if divergent else 0


if __name__ == "__main__":
    raise SystemExit(main())
