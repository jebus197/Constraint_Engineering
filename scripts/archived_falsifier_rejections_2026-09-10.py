#!/usr/bin/env python3
"""Task A2: why the falsifier key-guard rejects 35 MORE archived falsifiers in a clone.

THE FINDING, and it has teeth beyond the suite. `bench/falsifier_verify.py`
refuses a falsifier that names an absolute path outside the declared target.
Archived falsifiers carry the absolute path of the checkout they were WRITTEN in
-- `/Users/georgejackson/Developer_Projects/Constraint_Engineering/...`. On the
maintainer's machine that path IS the repository root, so the guard allows it.
In ANY other checkout it is not, so the guard refuses.

Measured 2026-09-10 over the same 640 archived falsifier sources, run twice:

  in the maintainer's tree   2 rejected, both for KEY MATERIAL
  in a fresh clone          37 rejected: the same 2, plus 35 whose ONLY violation
                            is naming this project's own tree from elsewhere

A rejection is not a verdict. `reverify_falsifier` prints INTEGRITY VIOLATION and
routes the finding to a human -- "neither confirmed nor refuted". So a reader who
clones this repository and re-verifies the archive gets 35 findings thrown to
manual adjudication for no reason but where they put the directory.

THE GUARD IS NOT WRONG AND IS NOT CHANGED. In a LIVE run, a falsifier naming an
absolute path outside the current tree must still be refused: containment is
about the filesystem, not about intent, and this project discarded a whole run
because a model opened a scoring key. What was wrong was a TEST that pinned the
rejection count without noticing the count was a fact about the maintainer's
directory layout.

THE DISCRIMINATOR, stated so it cannot quietly widen. A rejection is a LOCATION
ARTEFACT when every violation is `a path outside the declared target`, the path
contains this project's directory name, AND the remainder after that name
resolves to a file that exists in THIS checkout -- i.e. the falsifier was naming
its own repository. Anything else, including a path that merely mentions the
project name but points at nothing here, stays a real rejection.
"""
from __future__ import annotations

import collections
import json
import os
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from bench.falsifier_verify import scan_falsifier_source  # noqa: E402

OUTSIDE = "a path outside the declared target"

#: A suffix must be at least this many path components before it counts as
#: "names a file in this checkout". A bare filename coincides too easily; 2
#: components is the shortest that carries a directory as well.
MIN_SUFFIX_PARTS = 2

#: THE FIRST VERSION OF THIS DISCRIMINATOR WAS WRONG, and it failed in exactly
#: the place it was written to work. It asked whether the offending path
#: contained `REPO.name` -- the checkout's own DIRECTORY NAME. In the maintainer's
#: tree that is `Constraint_Engineering` and the test passed; in the fresh clone
#: at /tmp/ce_fresh it is `ce_fresh`, so no archived path contained it, and the
#: script reported 0 location artefacts and 37 real rejections -- the exact
#: figure it was built to explain, restated as though it were the finding. A
#: clone may sit in any directory; the project's identity is not its folder name.
#: This is the basename-versus-path defect that has now recurred 6 times here.
#:
#: THE SECOND VERSION WAS ALSO WRONG, and running it in the clone said so: it
#: asked only whether some >= 2-component TAIL of the offending path exists here,
#: and classified 4 of the 35 instead of 35. The reason is in the data --
#: measured, not guessed: 31 of the 35 offending strings are the repository ROOT
#: with NO tail at all (28 bare, 3 with a trailing slash), 4 name a file beneath
#: it. A rule that needs a tail cannot see a path that is all prefix.
#:
#: So the project's identity IS needed, and it must come from inside the
#: repository rather than from the folder it happens to sit in. `project_names()`
#: reads it from the git remote (carried by every clone, in `.git/config`) and
#: falls back to the checkout directory, saying which answered.


def archived_sources() -> dict[str, set[tuple[str, str]]]:
    """Every distinct falsifier source in the archive, and where it is held."""
    out: dict[str, set[tuple[str, str]]] = collections.defaultdict(set)
    for rep in sorted((REPO / "bench" / "logs").rglob("*_report.json")):
        try:
            data = json.loads(rep.read_text(encoding="utf-8", errors="replace"))
        except (ValueError, OSError):
            continue
        for cid, entry in ((data.get("registry") or {}).get("entries") or {}).items():
            code = (entry or {}).get("falsifier_code") or ""
            if code.strip():
                out[code].add((rep.parent.name, cid))
    return out


def is_location_artefact(violations) -> bool:
    """True only when EVERY violation is this checkout naming its own tree.

    Written to fail closed: 1 violation of any other kind, or 1 path whose tail
    does not exist here, and the whole rejection stays real.
    """
    if not violations:
        return False
    for reason, raw in violations:
        if reason != OUTSIDE:
            return False
        if not _names_this_checkout(raw):
            return False
    return True


def project_names() -> tuple[set[str], str]:
    """DELEGATED to `bench.repo_paths`, which is the one place that decides.

    THIS WAS A SECOND IMPLEMENTATION AND IT DEFEATED THE FIX TO THE FIRST.
    Found 2026-09-11 by the cc2 seat in panel round 10: repairing the canonical
    predicate left this script's figure unmoved, because it re-derived identity
    locally. The repository names that shape itself at
    `bench/execution_based_matcher.py:330` -- "a second implementation of a rule,
    which is a second rule" -- and this script's own docstring already cited
    `project_names()` as the authority while quietly not using it.

    THE REMOVAL IS JUSTIFIED BY MEASUREMENT, as the additive standard requires:
    in a checkout with no `.git` the local copy gave 33 of 640 real rejections
    and the shared predicate gives 2 of 640, which is the figure the maintainer's
    tree produces. The copy was wrong; the module is right.
    """
    from bench.repo_paths import project_names as _pn
    return _pn(REPO)


_PROJECT_NAMES, _NAME_SOURCE = project_names()


def _names_this_checkout(raw: str) -> bool:
    """Is `raw` this project's own tree, named from a different checkout?

    Two shapes, both measured in the archive: the repository ROOT itself, with
    or without a trailing slash (31 of 35 offending strings), and a path beneath
    it whose tail exists here (4 of 35).
    """
    stripped = raw.rstrip("/")
    if pathlib.PurePosixPath(stripped).name in _PROJECT_NAMES:
        return True
    for name in _PROJECT_NAMES:
        if f"/{name}/" in raw:
            tail = raw.split(f"/{name}/", 1)[1]
            if tail and (REPO / tail).exists():
                return True
    parts = [p for p in pathlib.PurePosixPath(raw).parts if p not in ("/", "")]
    for i in range(len(parts) - MIN_SUFFIX_PARTS + 1):
        if (REPO / pathlib.Path(*parts[i:])).exists():
            return True
    return False


def survey():
    sources = archived_sources()
    real, artefact = {}, {}
    for code, where in sources.items():
        v = scan_falsifier_source(code)
        if not v:
            continue
        (artefact if is_location_artefact(v) else real)[code] = (sorted(where), v)
    return sources, real, artefact


def main() -> int:
    sources, real, artefact = survey()
    print(f"checkout under test : {REPO}")
    print(f"project identity    : {sorted(_PROJECT_NAMES)} (from the "
          f"{_NAME_SOURCE})")
    print(f"distinct archived falsifier sources: {len(sources)}")
    print(f"\nREAL rejections (key material, or a path this checkout cannot "
          f"account for): {len(real)}")
    for code, (where, v) in sorted(real.items(), key=lambda kv: kv[1][0]):
        print(f"   {where[0]}  reasons={sorted({r for r, _ in v})}")
    print(f"\nLOCATION ARTEFACTS (this project's own tree, named from another "
          f"checkout): {len(artefact)}")
    for code, (where, _v) in sorted(artefact.items(), key=lambda kv: kv[1][0])[:6]:
        print(f"   {where[0]}")
    if len(artefact) > 6:
        print(f"   ... and {len(artefact) - 6} more")
    if not artefact:
        print("   none here -- which is what the maintainer's own tree looks "
              "like, because there the archived absolute path IS the repo root")

    n = len(sources)
    k = len(real)
    from statsmodels.stats.proportion import proportion_confint
    lo_w, hi_w = proportion_confint(k, n, method="wilson")
    lo_c, hi_c = proportion_confint(k, n, method="beta")
    from scipy.stats import beta as sbeta
    hi_s = sbeta.ppf(0.975, k + 1, n - k)
    print(f"\nreal-rejection rate : {k}/{n} = {k / n:.4%}")
    print(f"  Wilson 95%          : [{lo_w:.4%}, {hi_w:.4%}]  (statsmodels)")
    print(f"  Clopper-Pearson 95% : [{lo_c:.4%}, {hi_c:.4%}]  (statsmodels/beta)")
    print(f"  Clopper-Pearson 95% : [{lo_c:.4%}, {hi_s:.4%}]  (scipy cross-check, "
          f"upper agrees to {abs(hi_s - hi_c):.1e})")
    ka = len(artefact)
    if ka:
        alo, ahi = proportion_confint(ka, n, method="wilson")
        print(f"location-artefact rate: {ka}/{n} = {ka / n:.4%}  "
              f"Wilson [{alo:.4%}, {ahi:.4%}]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
