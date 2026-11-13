"""The claude client resolver: 1 declaration, correct ordering, unchanged selection.

ENTRY B173. The resolver was duplicated across 2 modules and held 4 faults in 18
lines, 3 masked by the 1st. These contracts pin the repair AND, just as
importantly, pin the thing the repair deliberately did NOT change.

★ C3 IS THE ONE TO READ. Preferring a newer client would change which model
serves a dispatch, which is an experimental condition rather than a bug. The
repair reports the gap and leaves the selection alone. A later change that
"helpfully" starts preferring the newest client will turn C3 red, which is the
point: it is a decision for the founder, not a tidy-up.
"""
from __future__ import annotations

import ast
import importlib.util
import pathlib
import shutil
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent.parent
MOD = REPO / "bench" / "claude_cli_resolution.py"


def _load(path, name):
    sys.path.insert(0, str(REPO / "bench"))
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    try:
        spec.loader.exec_module(m)
    except SystemExit:
        pass
    return m


@pytest.fixture(scope="module")
def r():
    assert MOD.is_file(), f"the shared resolver is missing: {MOD}"
    return _load(MOD, "cdsfl_client_resolution")


def test_c1_the_bundle_glob_reaches_the_installed_clients(r):
    """Fault 2: the pattern was 1 directory level short and matched 0."""
    bundles = [c for c in r.candidates(probe_path_version=False)
               if c.source == "bundle"]
    assert bundles, (
        "the bundle search found 0 installed clients. The real path carries a "
        "build hash between the version and claude.app; a pattern 1 level short "
        "matches nothing, and then the fallback cannot work even when reached.")
    # ★ THE HASH-LEVEL LAYOUT SPECIFICALLY. Asserting only that SOME bundle was
    # found is too weak: the `claude-code-vm/<version>/claude` layout has no hash
    # level and satisfies it, so removing the hash pattern left this test GREEN.
    # Found by mutation P1 of scripts/the_client_resolution_mutations_2026-11-13.py.
    hashed = [c for c in bundles
              if "claude.app" in c.path
              and len(pathlib.Path(c.path).parts) >
                  len(pathlib.Path(c.path).parts[:pathlib.Path(c.path).parts.index("claude.app")])
              and any(part and not r.parse_version(part) and len(part) >= 8
                      and all(ch in "0123456789abcdef" for ch in part)
                      for part in pathlib.Path(c.path).parts)]
    assert hashed, (
        f"no client was found at the build-hash layout "
        f"claude-code/<version>/<hash>/claude.app/..., which is the exact layout "
        f"the old pattern was 1 level short of. Found: "
        f"{[c.path for c in bundles]}")
    assert all(c.version is not None for c in bundles), (
        f"a bundle path names its own version and must not need executing: "
        f"{[c.path for c in bundles if c.version is None]}")


def test_c2_ordering_is_by_version_tuple_not_lexicographic(r):
    """Fault 3: sorted(reverse=True) on strings puts 2.1.90 above 2.1.317."""
    assert r.parse_version("claude-code/2.1.317/x") == (2, 1, 317)
    assert r.parse_version("2.1.9") == (2, 1, 9)
    assert r.parse_version("no version here") is None
    lex = sorted(["2.1.317", "2.1.9", "2.1.220", "2.1.90"], reverse=True)
    assert lex[0] == "2.1.90", "fixture no longer demonstrates the defect"
    best = max(r.parse_version(v) for v in ["2.1.317", "2.1.9", "2.1.220", "2.1.90"])
    assert best == (2, 1, 317), f"version ordering picked {best}, not 2.1.317"
    # And the live list must actually be ordered newest-first.
    vs = [c.version for c in r.candidates(probe_path_version=False)
          if c.version is not None]
    assert vs == sorted(vs, reverse=True), f"candidates are not newest-first: {vs}"


def test_c3_selection_is_unchanged_and_path_still_wins(r):
    """★ The contract the repair deliberately did NOT change.

    Selecting a newer client changes which MODEL answers a dispatch. That is the
    founder's decision. If this test ever goes red because someone made the
    resolver prefer the newest, that is not an improvement -- it is an
    experimental condition altered without a ruling.
    """
    on_path = shutil.which("claude")
    if on_path is None:
        pytest.skip("no claude on PATH; the preference cannot be observed here")
    assert r.resolve() == on_path, (
        f"resolve() returned {r.resolve()!r} but PATH holds {on_path!r}. PATH "
        f"must still win: changing it changes which model serves a dispatch.")
    rep = r.resolution_report(probe_path_version=False)
    assert rep["selected"] == on_path, "the report must describe what is selected"


def test_c4_one_declaration_two_readers(r):
    """Fault 4: the resolver was duplicated. Both modules must now DELEGATE."""
    for rel in ("bench/experiment_11_orchestrator.py", "bench/cc2_manager.py"):
        src = (REPO / rel).read_text()
        tree = ast.parse(src)
        fn = next((n for n in ast.walk(tree)
                   if isinstance(n, ast.FunctionDef) and n.name == "_find_claude_cli"),
                  None)
        assert fn is not None, f"{rel} no longer defines _find_claude_cli"
        body = "\n".join(ast.unparse(x) for x in fn.body)
        assert "claude_cli_resolution" in body, (
            f"{rel}'s resolver does not delegate to the shared module, so the "
            f"duplication is back")
        assert "claude.app" not in body, (
            f"{rel} still carries its own bundle search, so there are 2 "
            f"declarations of 1 fact again")


def test_c5_a_newer_client_is_reported_rather_than_silently_used(r):
    """The half that was missing entirely: the harness can now say so.

    ★ TESTED ON AN INJECTED CANDIDATE LIST, not on this machine's state. The
    suite runs under a netguard that refuses subprocess attempts, so reading a
    real version here is impossible and any contract requiring one passes
    VACUOUSLY. Mutation P5 of scripts/the_client_resolution_mutations_2026-11-13.py
    stayed GREEN twice because of that, first through a conditional the mutation
    switched off and then through an unknown version.
    """
    C = r.Candidate
    cands = [C("/bundle/new", "bundle", (2, 1, 317)),
             C("/bundle/mid", "bundle", (2, 1, 309)),
             C("/usr/bin/claude", "PATH", (2, 1, 220))]
    rep = r.resolution_report(cands=cands, chosen="/usr/bin/claude")
    assert rep["selected_version"] == (2, 1, 220)
    assert len(rep["newer_available"]) == 2, (
        f"2 newer clients exist and the report names {len(rep['newer_available'])}")
    assert rep["patch_gap"] == 97, f"patch gap should be 97, got {rep['patch_gap']}"
    text = r.describe(rep)
    assert "NEWER CLIENT IS INSTALLED" in text, "the gap is not reported in words"
    assert "/usr/bin/claude" in text, "the report must name the selected binary"

    # ...and the selection must NOT have moved to the newer one.
    assert rep["selected"] == "/usr/bin/claude", (
        "the report changed the selection; it must only describe it")

    # The no-newer case must read differently, or the 2 states are indistinguishable.
    only = r.resolution_report(cands=[C("/usr/bin/claude", "PATH", (2, 1, 317))],
                               chosen="/usr/bin/claude")
    assert only["newer_available"] == [] and only["patch_gap"] == 0
    assert "newest this machine offers" in r.describe(only)

    # ★ AN UNREAD VERSION MUST SAY SO, NOT CLAIM TO BE NEWEST. Added
    # 2026-11-13. `newer` requires `chosen_v is not None`, so an unread version
    # gave an EMPTY list and `describe` fell through to "the newest this machine
    # offers" -- an ABSENCE OF DATA rendering as a POSITIVE VERDICT. Measured on
    # the live machine: unprobed it claimed newest while 2.1.317 sat installed
    # beside the selected 2.1.220, a real gap of 97 patch releases.
    unread = r.resolution_report(
        cands=[C("/bundle/new", "bundle", (2, 1, 317)),
               C("/usr/bin/claude", "PATH", None)],
        chosen="/usr/bin/claude")
    assert unread["comparable"] is False, (
        "the report claims a comparison was possible with no selected version")
    utext = r.describe(unread)
    assert "CANNOT TELL" in utext, (
        f"an unread version must say so; got:\n{utext}")
    assert "newest this machine offers" not in utext, (
        "an absence of data is reported as a positive verdict, which is the "
        "defect this case exists for")

    # And the LIVE report must be self-consistent with its own candidate list.
    # ★ ASSERT THE FLAG, NOT A RE-DERIVATION. This block read
    #     derived = [c for c in live["candidates"]
    #                if c.version is not None and sel_v is not None and ...]
    # which RE-IMPLEMENTED the producer's own `sel_v is not None` condition, so
    # when the selected version was unknown both sides were 0 and the assertion
    # passed VACUOUSLY -- in precisely the case that was wrong. A consistency
    # check written as a copy of the producer can only confirm that the producer
    # agrees with itself. The flag is the one thing it cannot copy.
    live = r.resolution_report(probe_path_version=False)
    sel_v = live["selected_version"]
    assert live["comparable"] == (sel_v is not None), (
        f"`comparable` disagrees with the selected version it describes: "
        f"comparable={live['comparable']} selected_version={sel_v}")
    if live["comparable"]:
        derived = [c for c in live["candidates"]
                   if c.version is not None and c.version > sel_v]
        assert len(live["newer_available"]) == len(derived), (
            "the live report disagrees with its own evidence")
    else:
        assert live["newer_available"] == [] and live["patch_gap"] == 0, (
            "no comparison was possible, so there can be no newer list or gap")
        assert "CANNOT TELL" in r.describe(live), (
            "the LIVE unprobed report does not say it cannot tell")


def test_c6_the_module_never_dispatches(r):
    """A resolver that cost a dispatch would be a resolver nobody dares call.

    RESTORED after an over-wide edit deleted it, noticed because the test count
    fell from 6 to 5. A count that drops without a deletion being intended is the
    signature of exactly this.
    """
    src = MOD.read_text()
    tree = ast.parse(src)
    calls = [ast.unparse(n) for n in ast.walk(tree)
             if isinstance(n, ast.Call) and "subprocess.run" in ast.unparse(n)]
    assert calls, "expected at least 1 subprocess call (--version)"
    for c in calls:
        assert "--version" in c, (
            f"this module runs a subprocess that is not --version: {c}. Reading a "
            f"version is free; a dispatch is not, and must never happen here.")
