"""Which `claude` binary the harness will run, which versions exist, and the gap.

ENTRY B173, 2026-11-13. `_find_claude_cli` was duplicated in 2 modules and held 4
faults in 18 lines, 3 of them masked by the 1st:

  1. `shutil.which("claude")` returns immediately, so the application-bundle
     branch below it is UNREACHABLE whenever `claude` is on PATH.
  2. The bundle glob is 1 directory level short -- the real path carries a build
     hash between the version and `claude.app` -- so it matched 0 installations
     where a corrected pattern matches 2. Even with PATH empty it returned None.
  3. `sorted(matches, reverse=True)` is LEXICOGRAPHIC beneath a comment reading
     "newest version first": among 2.1.317, 2.1.9, 2.1.220 and 2.1.90 it selects
     2.1.90. Verified by execution.
  4. Duplicated. Compared by syntax tree the 2 copies have NOT drifted -- the only
     difference is where `glob` is imported -- but 2 declarations of 1 fact is the
     shape this project keeps finding, so they are collapsed here.

★ THIS MODULE DOES NOT CHANGE WHICH BINARY IS SELECTED, AND THAT IS DELIBERATE.
`resolve()` reproduces today's preference exactly -- PATH first, bundles only as
a fallback -- because changing which client serves a dispatch changes which MODEL
answers, and that is an experimental condition, not a bug fix. It belongs to the
founder. What this module adds is the half that was missing entirely: the harness
can now say WHICH binary it chose, WHAT version that is, and WHETHER a newer one
is installed. Detect and record; never mutate. That is the conclusion the free
panel reached on 2026-11-13 about standards currency, applied to the same defect
one level down -- a pinned dependency that has gone stale and that nothing was
recording.

MEASURED ON THE MACHINE THAT PROMPTED IT: PATH holds 2.1.220 while the desktop
application bundles 2.1.309 and 2.1.317, a gap of 97 patch releases, and the
model identifier `claude-fable-5-2` requires 2.1.290. Nothing in the repository
could report that, because the aliveness probe asks whether a route answers and
never which client or which model answered.
"""
from __future__ import annotations

import glob as _glob
import os
import pathlib
import re
import shutil
import subprocess
from typing import NamedTuple, Optional

#: The application-bundle layouts, WITH the build-hash level the old pattern
#: missed. `claude-code/<version>/<build hash>/claude.app/...` is the real shape;
#: the `-vm` layout has no hash. Both are kept: dropping either would be a
#: removal with no measurement behind it.
_BUNDLE_PATTERNS = (
    ("claude-code", "*", "*", "claude.app", "Contents", "MacOS", "claude"),
    ("claude-code", "*", "claude.app", "Contents", "MacOS", "claude"),
    ("claude-code-vm", "*", "claude"),
)

_VERSION_IN_TEXT = re.compile(r"(\d+)\.(\d+)\.(\d+)")


class Candidate(NamedTuple):
    path: str
    source: str                      # "PATH" or "bundle"
    version: Optional[tuple]         # parsed, or None when not determinable


def parse_version(text: str) -> Optional[tuple]:
    """A version tuple from any text, or None. Never raises."""
    if not isinstance(text, str):
        return None
    m = _VERSION_IN_TEXT.search(text)
    return tuple(int(g) for g in m.groups()) if m else None


def _version_from_path(p: str) -> Optional[tuple]:
    """The version a bundle path carries, read rather than executed.

    A bundle path names its own version, so no subprocess is needed. That matters:
    a module that shells out once per candidate on import would make every caller
    pay for a question most of them never ask.
    """
    for part in pathlib.Path(p).parts:
        v = parse_version(part)
        if v is not None:
            return v
    return None


def _version_by_running(p: str, timeout: float = 30.0) -> Optional[tuple]:
    """`<binary> --version`. Free, and NEVER a dispatch -- it prints and exits."""
    try:
        r = subprocess.run([p, "--version"], capture_output=True, text=True,
                           timeout=timeout)
    except Exception:                                              # noqa: BLE001
        return None
    return parse_version((r.stdout or "") + (r.stderr or ""))


def candidates(probe_path_version: bool = True) -> list[Candidate]:
    """Every `claude` binary this machine offers, newest FIRST by parsed version.

    Ordering is by VERSION TUPLE, never lexicographic: `sorted(reverse=True)` on
    strings puts 2.1.90 above 2.1.317, which is fault 3 above.
    """
    out: list[Candidate] = []
    on_path = shutil.which("claude")
    if on_path:
        v = _version_by_running(on_path) if probe_path_version else None
        out.append(Candidate(on_path, "PATH", v))
    app = pathlib.Path.home() / "Library" / "Application Support" / "Claude"
    seen = {c.path for c in out}
    for parts in _BUNDLE_PATTERNS:
        for hit in _glob.glob(str(app.joinpath(*parts))):
            if hit in seen or not os.path.isfile(hit):
                continue
            seen.add(hit)
            out.append(Candidate(hit, "bundle", _version_from_path(hit)))
    # Newest first. A candidate whose version could not be determined sorts last
    # rather than being dropped -- `feedback_never_delete_bulk_resources`.
    out.sort(key=lambda c: (c.version is not None, c.version or (0, 0, 0)),
             reverse=True)
    return out


def resolve(probe_path_version: bool = False) -> Optional[str]:
    """The binary the harness WILL run. Identical to the behaviour it replaces.

    ★ PATH STILL WINS. This is not an oversight: preferring a newer client would
    change which model serves a dispatch, which is an experimental condition and
    the founder's decision. `resolution_report()` surfaces the gap instead.
    """
    on_path = shutil.which("claude")
    if on_path:
        return on_path
    for c in candidates(probe_path_version=probe_path_version):
        if c.source == "bundle":
            return c.path
    return None


def resolution_report(probe_path_version: bool = True,
                      cands: "Optional[list]" = None,
                      chosen: Optional[str] = None) -> dict:
    """What was selected, what exists, and whether something newer is installed.

    `cands` and `chosen` are injection points, added so this function's LOGIC can
    be tested without running a binary. The test suite runs under a netguard that
    refuses subprocess attempts, so a contract depending on `--version` could only
    ever pass vacuously -- and did, twice, until a mutation exposed it.
    """
    cands = candidates(probe_path_version=probe_path_version) if cands is None else list(cands)
    chosen = resolve(probe_path_version=False) if chosen is None else chosen
    chosen_c = next((c for c in cands if c.path == chosen), None)
    chosen_v = chosen_c.version if chosen_c else None
    newer = [c for c in cands
             if c.version is not None and chosen_v is not None and c.version > chosen_v]
    return {
        "selected": chosen,
        "selected_source": chosen_c.source if chosen_c else None,
        "selected_version": chosen_v,
        "candidates": cands,
        "newer_available": newer,
        "patch_gap": (max(c.version for c in newer)[2] - chosen_v[2]
                      if newer and chosen_v else 0),
        #: ★ WITHOUT THIS, AN ABSENCE OF DATA RENDERED AS A POSITIVE VERDICT.
        #: `newer` requires `chosen_v is not None`, so an unread version gave an
        #: EMPTY list, and `describe` had only 2 branches -- a gap, or "the
        #: newest this machine offers". Measured 2026-11-13 on the live machine:
        #: unprobed it claimed the selected client was newest while 2.1.317 sat
        #: installed beside the selected 2.1.220, a real gap of 97 patch
        #: releases. The selection is still correctly left alone; the REASON
        #: printed for it was false, which is `a fail-safe must not be recorded
        #: as a fact`. It bites hardest in the suite, where the netguard forces
        #: `probe_path_version=False` on every test.
        "comparable": chosen_v is not None,
    }


def _fmt(v) -> str:
    return ".".join(str(x) for x in v) if v else "unknown"


def describe(report: Optional[dict] = None) -> str:
    """1 human-readable line per candidate, plus the verdict. Never raises."""
    r = report if report is not None else resolution_report()
    lines = [f"claude client SELECTED: {r['selected']} "
             f"({r['selected_source']}, version {_fmt(r['selected_version'])})"]
    for c in r["candidates"]:
        mark = "  <- selected" if c.path == r["selected"] else ""
        lines.append(f"  {_fmt(c.version):>10}  {c.source:<7} {c.path}{mark}")
    if r["newer_available"]:
        newest = max(c.version for c in r["newer_available"])
        lines.append(
            f"  ★ A NEWER CLIENT IS INSTALLED: {_fmt(newest)} against the selected "
            f"{_fmt(r['selected_version'])}, a gap of {r['patch_gap']} patch "
            f"release(s). Selection is NOT changed automatically, because which "
            f"client serves a dispatch decides which model answers.")
    elif not r.get("comparable", r["selected_version"] is not None):
        #: `.get` with a fallback so an OLDER report dict still renders: this is
        #: an ADDED state, and nothing that worked before may stop working.
        lines.append(
            "  CANNOT TELL: the selected client's version was not read, so NO "
            "comparison was made. This is NOT a statement that it is current. "
            "Call resolution_report(probe_path_version=True) to find out.")
    else:
        lines.append("  the selected client is the newest this machine offers")
    return "\n".join(lines)


if __name__ == "__main__":                                         # pragma: no cover
    print(describe())
