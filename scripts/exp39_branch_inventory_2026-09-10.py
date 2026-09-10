#!/usr/bin/env python3
"""Task 8.2: what does `exp39-experimental` hold that exists nowhere else?

MEASURED, and committed alongside the figures (`measured-rate-travels-with-its-script`).

HIS RULING, verbatim: "Get Fable and CC2 to look at this with you, decide which
elements on this branch remain useful and should be adopted in light of
everything else we have done and which should be considered superseded."

This script establishes the FACTS the adjudication needs. It decides nothing and
deletes nothing. Deleting a git ref is one of the 3 categories reserved to the
founder in person, and no path here approaches it.

WHAT THE ENTRY SAID, AND WHAT IS ACTUALLY TRUE. The entry records "12 file paths
existing nowhere else". That is right, and it does not say what they are. They
are 5 EXAM ANSWER KEYS and the 6 exam targets they belong to, plus 1 note.

HARDENED 2026-09-10 (panel round 9). Three defects, all in the measurement
machinery rather than in the conclusion, all of which made the script report a
confident number it had not earned:

  (1) SILENT SUCCESS OUTSIDE A GIT REPOSITORY. `git()` swallowed the return code
      and returned "" for every call, so in any tree without `.git` -- including
      `bench/panel_sandbox.py`'s own staged sandbox, the environment in which the
      panel is asked to re-run these very figures -- the script printed
      "no branch ... nothing to measure" and exited 0. A measuring script that
      cannot measure must fail LOUD, not green. `git()` now raises
      `GitUnavailable`, and absence-of-branch is distinguished from
      absence-of-git by exit codes 3 and 4 respectively.

  (2) WHITESPACE-SPLIT PATH PARSING. `ls-tree --name-only ... .split()` shreds any
      path containing a space. This repository holds two of them today
      (`docs/Experiment 40 response.docx`, `.txt`). Both currently sit in BOTH
      trees so the fragments cancel and the printed figures are unaffected -- but
      a spaced path unique to either side would emit fabricated path names into
      the founder's inventory. Now NUL-delimited (`-z`) throughout.

  (3) THE 400-COMMIT CUT-OFF, REMOVED. The old comparison scanned only the most
      recent 400 of main's 1021 commits "for tractability". A cut-off cannot make
      the branch look cleaner, only dirtier: a path that lives ONLY in main's
      older history is invisible to the window and is reported as "exists nowhere
      else". Measured on 2026-09-10, none of the 12 was manufactured this way --
      the figure was right, by luck, not by construction. The window is gone, and
      it cost nothing: the union of paths over main's FULL history from one
      `git log --name-only` call is set-identical to the union of `ls-tree` over
      every commit (8293 == 8293, both differences empty) and runs in 0.2s
      against 18.6s. Full history is now 93x CHEAPER than the cut-off it replaces.
"""
from __future__ import annotations

import argparse
import fnmatch
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
BRANCH = "exp39-experimental"
MAIN = "origin/main"

EXIT_OK = 0
EXIT_NO_BRANCH = 3
EXIT_NO_GIT = 4


class GitUnavailable(RuntimeError):
    """git is missing, or the directory is not a git repository.

    Distinct from "the branch does not exist here", which is a legitimate
    measurement outcome. This one means NOTHING was measured.
    """


def git(*args, repo=None, check: bool = True) -> str:
    """Run git and return stdout.

    Unlike the original, this does not silently return "" when git fails. A
    failure meaning "no repository / no git binary" raises GitUnavailable; with
    check=False an ordinary non-zero exit (e.g. `rev-parse --verify` on a ref
    that does not exist) returns "" as before.
    """
    cwd = repo or REPO
    try:
        p = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    except FileNotFoundError as exc:  # no git binary at all
        raise GitUnavailable("git executable not found on PATH") from exc
    if p.returncode != 0:
        err = (p.stderr or "").lower()
        if "not a git repository" in err or "dubious ownership" in err:
            raise GitUnavailable(
                f"not a usable git repository: {cwd}\n{p.stderr.strip()}")
        if check:
            raise GitUnavailable(
                f"git {' '.join(args)} failed (rc={p.returncode}): {p.stderr.strip()}")
    return p.stdout


def _nul(s: str) -> set:
    return {x for x in s.split("\0") if x}


def tree_paths(rev: str, repo=None) -> set:
    """Every path in the tree at `rev`. NUL-delimited: spaces are safe."""
    return _nul(git("ls-tree", "-r", "-z", "--name-only", rev, repo=repo))


def history_paths(rev: str, repo=None) -> set:
    """Every path that has EVER existed anywhere in `rev`'s full history.

    One `git log` call, no commit cap. Equivalent to the union of `ls-tree` over
    every reachable commit -- verified set-identical on this repository's main
    (8293 paths both ways) -- and ~93x faster. `--full-history -m` keeps merge
    sides, `--no-renames` splits an R into its A and D so BOTH names are counted,
    and `-z` keeps spaced paths intact.
    """
    out = git("log", rev, "--full-history", "-m", "--no-renames",
              "--format=", "--name-only", "-z", repo=repo)
    return _nul(out)


def history_paths_capped(rev: str, cap: int, repo=None) -> set:
    """The ORIGINAL, DEFECTIVE method, retained so the test can demonstrate the
    difference. Union of tree_paths over only the newest `cap` commits. Never
    called by main(); it exists to be falsified."""
    out = set()
    for c in git("rev-list", rev, repo=repo).split()[:cap]:
        out |= tree_paths(c, repo)
    return out


KEY_MARKER = "answer_key"

# THE AUTHORITATIVE KEY-MATERIAL PATTERNS, lifted verbatim from the corrected scan
# in bench/vault_keys.sh:493-494. Added 2026-09-10 (panel round 9).
#
# WHY. `KEY_MARKER = "answer_key"` alone is the SAME blindness this project already
# diagnosed and fixed in vault_keys.sh four days earlier, on 2026-09-06, and wrote a
# regression suite for at
# bench/tests/test_vault_status_sees_the_real_keys_2026-09-06.py: "It matched only
# '*answer_key*.json'. The BR2 keys are 'ft-NNN_KEY.json' and the exp55 pair are
# '*_KEY.md' / '*GROUND_TRUTH.json' -- 0 of 29 real keys matched the pattern."
# Those 29 files are key material by this project's own register
# (vault_keys.sh:204-206). An inventory blind to them prints "ANSWER KEYS: 0" over a
# branch carrying 27 of them and, worse, reports the refs that carry them as
# carrying none -- which is the number a push disposition turns on.
#
# STRICTLY WIDER, NEVER NARROWER. is_key_path() matches the old substring test OR
# any authoritative glob, so its result set is a superset of the old one on every
# input. That dominance is the committed measurement justifying the change, and it
# is asserted by test_new_matcher_is_a_strict_superset_of_the_old.
KEY_PATTERNS = ("*answer_key*.json", "*_KEY.json", "*_KEY.md", "*GROUND_TRUTH.json")


def is_key_path(path: str) -> bool:
    """True if `path` names key material under this project's own definition."""
    # KEY_MARKER is tested against the FULL path, exactly as the original did
    # (`"answer_key" in p`), so that a directory such as `answer_keys/x.json` that
    # the old test matched is still matched. Testing only the basename here would
    # have made the new matcher NARROWER on that input, breaking the very dominance
    # claim above. Caught by test_new_matcher_is_a_strict_superset_of_the_old.
    name = path.rsplit("/", 1)[-1]
    return KEY_MARKER in path or any(fnmatch.fnmatch(name, p) for p in KEY_PATTERNS)


def touches(ref: str, path: str, repo=None) -> bool:
    """Does any commit reachable from `ref` carry `path`?

    `rev-list <ref> --count -- <path>` applies history simplification and can
    report 0 for a path that is genuinely reachable (e.g. a TREESAME merge side).
    `--full-history` defeats that. Used for every reachability question here so a
    "0 commits" answer means absent, not merely simplified away.
    """
    n = git("rev-list", ref, "--full-history", "--count", "--", path,
            repo=repo, check=False).strip()
    return n not in ("", "0")


def refspec_sends(refspec: str, branches) -> list:
    """Which of `branches` (full refnames) a plain `git push` would send, given an
    explicit `remote.origin.push` refspec.

    Only the source side matters for "what leaves this machine". A leading '+'
    (force) and a trailing '*' wildcard are handled; anything else is compared
    exactly, after normalising a bare short name to refs/heads/.
    """
    out = []
    for spec in refspec.split():
        src = spec.lstrip("+").split(":", 1)[0]
        if not src:
            continue
        if not src.startswith("refs/"):
            src = "refs/heads/" + src
        for b in branches:
            if (fnmatch.fnmatch(b, src) if "*" in src else b == src):
                out.append(b)
    return sorted(set(out))


def key_bearing_refs(repo=None) -> dict:
    """Every ref in this clone that reaches at least one answer key, and how
    many key paths each reaches.

    The original inventory answered "is the BRANCH on the remote", which is a
    fact about one ref. The question the disposition actually turns on is which
    refs carry the keys AT ALL -- a tag added later carries them just as a
    branch does, and a tag is published by a different, easier command.
    """
    keys = sorted({p for p in history_paths("--all", repo) if is_key_path(p)})
    out = {}
    for ref in git("for-each-ref", "--format=%(refname)", repo=repo).split():
        hit = [k for k in keys if touches(ref, k, repo)]
        if hit:
            out[ref] = hit
    return out


def push_exposure(repo=None) -> dict:
    """What a push would actually send.

    "Nothing here was ever published" is true of the past and says nothing about
    the next command typed. `git push` sends no tag by default, but
    `git push --tags` sends EVERY tag, and this clone has no pre-push hook to
    stop it. That is a measurement, not a warning: it is read off the config.
    """
    def cfg(name):
        return git("config", "--get", name, repo=repo, check=False).strip()

    root = git("rev-parse", "--git-dir", repo=repo).strip()
    hook = pathlib.Path(root)
    if not hook.is_absolute():
        hook = pathlib.Path(repo or REPO) / root
    hook = hook / "hooks" / "pre-push"

    bearing = key_bearing_refs(repo)
    branches = [r for r in bearing if r.startswith("refs/heads/")]
    tags = [r for r in bearing if r.startswith("refs/tags/")]
    follow = cfg("push.followTags").lower() in ("true", "1", "yes")

    # WHAT A PLAIN `git push` SENDS -- COMPUTED, NEVER ASSERTED. This was hardcoded
    # False under the comment "`git push` with no args pushes the current branch
    # only", which is true and does not imply the answer: if the CURRENT branch is
    # the key-bearing one, or if remote.origin.push carries a wildcard, a plain push
    # sends key material. The refspec was already read into
    # `explicit_push_refspec` on the line above and then discarded before the
    # verdict -- the evidence that falsifies the answer was in hand and unused.
    # Measured 2026-09-10 against a fixture: with
    # remote.origin.push=refs/heads/*:refs/heads/*, `git push --dry-run` reported
    # " * [new branch]      exp39-experimental -> exp39-experimental" while this
    # field printed False.
    refspec = cfg("remote.origin.push")
    mode = cfg("push.default").lower() or "simple"   # git's own default since 2.0
    head = git("symbolic-ref", "--quiet", "--short", "HEAD",
               repo=repo, check=False).strip()
    head_ref = f"refs/heads/{head}" if head else ""

    if refspec:
        sent = refspec_sends(refspec, branches)
        why = f"explicit remote.origin.push={refspec!r} sends {sent or 'no key-bearing branch'}"
    elif mode == "nothing":
        sent, why = [], "push.default=nothing sends nothing"
    elif mode == "current":
        sent = [head_ref] if head_ref in branches else []
        why = f"push.default=current sends HEAD ({head or 'detached'})"
    elif mode == "matching":
        # Only branches that already exist on the remote are matched.
        on_remote = {f"refs/heads/{r}" for r in
                     [ln.split()[-1].removeprefix("refs/heads/")
                      for ln in git("ls-remote", "--heads", "origin", repo=repo,
                                    check=False).splitlines() if ln.split()]}
        sent = sorted(set(branches) & on_remote)
        why = "push.default=matching sends only branches already on the remote"
    else:  # simple / upstream / tracking -- require a configured upstream
        up = git("rev-parse", "--abbrev-ref", f"{head}@{{upstream}}",
                 repo=repo, check=False).strip() if head else ""
        sent = [head_ref] if (up and head_ref in branches) else []
        why = (f"push.default={mode} sends HEAD only with an upstream "
               f"(upstream={up or 'none'})")

    return {
        "plain_push_branches": sent,
        "plain_push_reason": why,
        "key_bearing_refs": bearing,
        "key_bearing_branches": branches,
        "key_bearing_tags": tags,
        "push_default": cfg("push.default") or "(unset)",
        "push_follow_tags": follow,
        "explicit_push_refspec": cfg("remote.origin.push") or "(unset)",
        "pre_push_hook": hook.exists(),
        "plain_push_sends_keys": bool(sent),
        "push_tags_sends_keys": bool(tags),
        "follow_tags_sends_keys": bool(tags) and follow,
    }


def unreachable_commits(branch: str, main: str, repo=None) -> list:
    return git("rev-list", branch, "--not", main, repo=repo).split()


def inventory(branch: str = BRANCH, main: str = MAIN, repo=None,
              main_history_cap=None) -> dict:
    """The whole measurement, as data.

    Raises GitUnavailable if nothing can be measured. `branch_present` False
    means the branch is genuinely absent from a WORKING repository.
    `main_history_cap` reproduces the old defective window; leave it None.
    """
    remote = [line.split()[-1] for line in
              git("ls-remote", "--heads", "origin", repo=repo, check=False).splitlines()]

    if not git("rev-parse", "--verify", branch, repo=repo, check=False).strip():
        return {"branch_present": False, "remote_heads": remote}

    tip_only = sorted(tree_paths(branch, repo) - tree_paths(main, repo))
    unreachable = unreachable_commits(branch, main, repo)

    hist = set()
    for c in unreachable:
        hist |= tree_paths(c, repo)
    if main_history_cap is None:
        main_hist = history_paths(main, repo)          # FULL history, no cut-off
    else:
        main_hist = history_paths_capped(main, main_history_cap, repo)
    only_hist = sorted(hist - main_hist)
    keys = [p for p in only_hist if is_key_path(p)]

    return {
        "branch_present": True,
        "remote_heads": remote,
        "on_remote": f"refs/heads/{branch}" in remote,
        "tip_only": tip_only,
        "unreachable_commits": len(unreachable),
        "only_hist": only_hist,
        "keys": keys,
        "key_reachability": {
            k: (git("rev-list", main, "--full-history", "--count", "--", k,
                    repo=repo, check=False).strip() or "0") for k in keys},
        "main_history_commits": len(git("rev-list", main, repo=repo).split()),
        "push_exposure": push_exposure(repo),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="exp39-experimental branch inventory")
    ap.add_argument("--branch", default=BRANCH)
    ap.add_argument("--main", default=MAIN)
    ap.add_argument("--repo", default=None, type=pathlib.Path)
    a = ap.parse_args(argv)

    try:
        inv = inventory(a.branch, a.main, a.repo)
    except GitUnavailable as exc:
        # LOUD. Exit 0 here is what let a sandbox with no .git report a clean
        # "nothing to measure" while measuring nothing at all.
        print(f"REFUSING TO REPORT: {exc}", file=sys.stderr)
        print("NOTHING WAS MEASURED. This is not a clean result.", file=sys.stderr)
        return EXIT_NO_GIT

    if not inv["branch_present"]:
        print(f"no branch {a.branch} in this clone -- nothing to measure.")
        return EXIT_NO_BRANCH

    print("--- what is on the REMOTE ---")
    print(f"  remote heads: {inv['remote_heads'] or '(none reachable)'}")
    print(f"  {a.branch} is on the remote: {inv['on_remote']}")

    print("\n--- tip trees ---")
    print(f"  paths on the {a.branch} tip and not on {a.main}: {len(inv['tip_only'])}")
    for p in inv["tip_only"]:
        print(f"     {p}")

    print("\n--- the branch's UNREACHABLE history ---")
    print(f"  commits on {a.branch} unreachable from {a.main}: {inv['unreachable_commits']}")
    print(f"  paths in that history and in no {a.main}-history tree: {len(inv['only_hist'])}")
    print(f"    (compared against ALL {inv['main_history_commits']} commits of "
          f"{a.main}; no cut-off)")
    for p in inv["only_hist"]:
        print(f"     {'*** KEY *** ' if p in inv['keys'] else '             '}{p}")

    print(f"\n--- ANSWER KEYS: {len(inv['keys'])} ---")
    for k in inv["keys"]:
        print(f"  {pathlib.Path(k).name}: reachable from {a.main} in "
              f"{inv['key_reachability'][k]} commit(s)")
    px = inv["push_exposure"]
    print("\n--- WHICH REFS CARRY A KEY, AND WHAT A PUSH WOULD SEND ---")
    for ref, ks in sorted(px["key_bearing_refs"].items()):
        print(f"  {ref}: {len(ks)} key path(s)")
    print(f"  push.default={px['push_default']}  "
          f"push.followTags={px['push_follow_tags']}  "
          f"remote.origin.push={px['explicit_push_refspec']}  "
          f"pre-push hook installed={px['pre_push_hook']}")
    print(f"  `git push`               sends a key-bearing ref: "
          f"{px['plain_push_sends_keys']}  ({px['plain_push_reason']})")
    print(f"  `git push --tags`        sends a key-bearing ref: "
          f"{px['push_tags_sends_keys']}")
    print(f"  `git push --follow-tags` sends a key-bearing ref: "
          f"{px['follow_tags_sends_keys']}")

    print("\n  REACHABILITY IS NOT EXPOSURE -- the founder's own ruling of "
          "2026-09-07.\n  These objects sit in a LOCAL branch. The remote carries "
          "main alone, so\n  nothing here was ever published. The branch's own "
          "commit eecdb0f says the\n  same thing in its title and names the "
          "residual: 'git-history recovery by\n  deliberate archaeology'.")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
