"""One path-delimited predicate for "is this archived run output, or source?"

TASK 6.4. Founder ruling, verbatim: *"So the sweep (and its original context,
which I shouldn't need to repeat), should be run again if you do this? If so,
do it."*

WHY ONE PREDICATE. Five checkers each decided this question for themselves and
they did not agree. Measured 2026-09-09 by `scripts/archive_root_agreement_2026-09-09.py`:
**1 of 10 pairs agree exactly**, Wilson [1.8%, 40.4%], Clopper-Pearson
[0.3%, 44.5%]. Only 1 of 5 excluded `bench/results/`; **0 of 5 excluded
`bench/logs_quarantine/`**, which exists on disk and holds quarantined run
output; and 1 of 5 tested a bare SUBSTRING (`"bench/logs" not in line`) rather
than a path prefix. So the same file could be production source to 1 checker and
archive to the next, which is the class this project catalogues as "a bounded
traversal standing in for a complete one" -- here, five different bounds.

WHY DELIMITED, with the example sitting in this repository. `bench/logs_quarantine`
starts with the string `bench/logs`, so a bare `startswith("bench/logs")` matches
it by accident while `startswith("bench/logs/")` misses it entirely. Neither is a
decision anyone made. This module compares PATH COMPONENTS, so `logs` can never
be confused with `logs_quarantine` in either direction, and adding a root to
`ARCHIVE_ROOTS` is the only way to change what counts.

WHAT THIS IS NOT. It does not decide whether a file is committed, generated, or
ignored -- only whether its location marks it as the OUTPUT of a run rather than
part of the instrument. `.gitignore` and the tracked-file checks answer the other
questions and are not duplicated here.
"""

from __future__ import annotations

import os
import re
from pathlib import PurePosixPath
from typing import Iterable, Union

#: Repository-relative roots whose contents are the output of runs, not source.
#: Adding one here changes every caller at once, which is the point.
ARCHIVE_ROOTS: tuple[str, ...] = (
    "bench/logs",
    "bench/logs_quarantine",
    "bench/results",
)

PathLike = Union[str, "os.PathLike[str]"]


def _parts(path: PathLike) -> tuple[str, ...]:
    """Repo-relative path as POSIX components, tolerant of Windows separators."""
    text = str(path).replace("\\", "/").strip()
    if text.startswith("./"):
        text = text[2:]
    return PurePosixPath(text).parts


def is_archived_run_output(path: PathLike, roots: Iterable[str] = ARCHIVE_ROOTS) -> bool:
    """True when a repo-relative path lies inside an archive root.

    A root itself counts, so `bench/logs` is archive and so is
    `bench/logs/run/x.json`. `bench/logs_quarantine` is a DIFFERENT root and is
    matched only because it is named in `ARCHIVE_ROOTS`, never by accident of
    sharing a prefix with `bench/logs`.
    """
    parts = _parts(path)
    for root in roots:
        rp = _parts(root)
        if rp and parts[:len(rp)] == rp:
            return True
    return False


def is_production_source(path: PathLike, roots: Iterable[str] = ARCHIVE_ROOTS) -> bool:
    """The complement, named positively because most callers ask it that way."""
    return not is_archived_run_output(path, roots)


#: A quoted string literal, as it appears in source text.
_QUOTED = re.compile(r"""['"]([^'"\n]{1,300})['"]""")
#: A bare path-ish token, for mentions that are not inside quotes.
_TOKEN = re.compile(r"[A-Za-z0-9_./\\-]{4,}")


def line_mentions_archive_path(line: str, roots: Iterable[str] = ARCHIVE_ROOTS) -> bool:
    """True when a SOURCE LINE names a path inside an archive root.

    DISTINCT FROM `is_archived_run_output`, which classifies a path, and the
    distinction is not academic: the first attempt at task 6.4 wired a
    text-scanning checker to the PATH predicate by stripping the line's quotes
    and passing the whole line. Every line then failed the check, every offender
    was skipped, and the test went green while detecting nothing. Executed to
    confirm it: `fp = REPO / "bench/logs/run" / name` classified as not-archive,
    where the substring test it replaced caught it.

    So this scans the line for path-shaped fragments -- quoted literals first,
    then bare tokens containing a separator -- and asks the path predicate about
    each. `ARCHIVE_ROOTS` stays the single place that decides what an archive is.
    """
    for m in _QUOTED.finditer(line):
        if is_archived_run_output(m.group(1), roots):
            return True
    for token in _TOKEN.findall(line):
        if ("/" in token or "\\" in token) and is_archived_run_output(token, roots):
            return True
    return False


# ── This project's identity, for recognising its own tree named from elsewhere ──

#: Names too generic to identify anything. A checkout in a directory called
#: `repo` or `src` must not make every path ending `/repo` this project's tree.
#: The panel sandbox copies to a directory literally named `repo`, so this is
#: not hypothetical.
_NOT_AN_IDENTITY = frozenset({
    "", ".", "..", "repo", "repository", "src", "code", "project", "projects",
    "main", "master", "tmp", "temp", "work", "workspace", "build", "dist",
    "test", "tests", "app", "lib", "home", "user", "data", "output", "sandbox",
    "checkout", "clone", "git",
})

#: The tracked file that DECLARES this project's home, and the only one read.
#: A prose scan would be wrong: `PAPER.md` cites github.com/jebus197/OpenBrain
#: and github.com/jebus197/Project_Genesis, and both would become identities of
#: this project. `.zenodo.json` names its own repository and nothing else.
DECLARED_IDENTITY_FILE = ".zenodo.json"
_GITHUB_REPO = re.compile(r"github\.com/[\w.-]+/([\w.-]+?)(?:\.git)?/?$")


def declared_project_names(repo_root: "os.PathLike[str] | str | None" = None
                           ) -> set[str]:
    """This project's name as the REPOSITORY ITSELF declares it.

    WHY A THIRD TIER, and it is the one that matters most. Found 2026-09-11 by
    the cc2 seat in panel round 10, premise verified before acceptance:
    `bench/panel_sandbox.py:43` is `_NEVER_COPY = frozenset({".git"})`, so the
    project's OWN review sandbox has no git metadata at all -- and neither does
    a ZIP download, a Zenodo archive, or a vendored copy. In every one of those
    the git remote cannot answer and the identity collapsed to the folder name,
    which for the sandbox is the literal string "repo". The A2 rebase then
    recognised 0 of the 35 stale paths it exists to rebase: an addition nothing
    reaches, in the fix for the previous instance of the same defect.

    A TRACKED FILE IS CARRIED BY EVERY DISTRIBUTION FORM, which is exactly the
    property the other 2 tiers lack.
    """
    from pathlib import Path

    root = Path(repo_root) if repo_root else Path(__file__).resolve().parents[1]
    f = root / DECLARED_IDENTITY_FILE
    if not f.is_file():
        return set()
    try:
        import json
        data = json.loads(f.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return set()
    out = set()
    for rel in (data.get("related_identifiers") or []):
        # ONLY THE RELATION THAT MEANS "THIS IS MY OWN REPOSITORY".
        # Found 2026-09-11 by the fable seat in panel round 11 and reproduced
        # before accepting: this read EVERY GitHub-shaped identifier, and the
        # docstring's claim that the file "names its own repository and nothing
        # else" was an unguarded invariant of today's file rather than a property
        # of the format. Appending 1 citation of `github.com/jebus197/OpenBrain`
        # made OpenBrain an identity of THIS project, so `foreign_repo_roots`
        # returned `/home/x/OpenBrain` and the falsifier rebase would have
        # rewritten an unrelated project's absolute paths into the overlay.
        #
        # `isSupplementTo` is Zenodo's relation for "this deposit supplements
        # that repository" -- the only one that asserts ownership. A citation is
        # `cites`, `references` or `isDerivedFrom`, and none of those says the
        # repository is ours.
        if str((rel or {}).get("relation") or "").strip() != "isSupplementTo":
            continue
        ident = (rel or {}).get("identifier") or ""
        m = _GITHUB_REPO.search(str(ident).strip())
        if m and m.group(1).lower() not in _NOT_AN_IDENTITY:
            out.add(m.group(1))
    return out


def project_names(repo_root: "os.PathLike[str] | str | None" = None
                  ) -> tuple[set[str], str]:
    """The names a checkout of THIS project answers to, read from the repository.

    WHY NOT `Path(repo_root).name`. Because a clone sits wherever the reader put
    it. Measured 2026-09-10, task A2: a fresh clone at `/tmp/ce_fresh` is the
    same repository under a different folder name, and an instrument that used
    the folder name reported 0 of the 35 cases it was written to find. That is
    the basename-versus-path defect, which has now recurred 6 times in this
    project, appearing this time inside the fix for its 5th instance.

    The git remote is read first because a clone CARRIES it, in `.git/config`,
    however the directory is named. The folder name is kept as a fallback and
    the caller is told which answered, so a weak identity is visible rather than
    silently assumed.

    Returns (names, source) where source is "remote" or "directory".
    """
    import subprocess
    from pathlib import Path

    #: THIS module's own repository, ALWAYS consulted. The caller may pass an
    #: overlay, a mirror, or a directory that does not exist -- `_retarget_falsifier`
    #: legitimately passes a sandbox root -- and asking git inside one of those
    #: yields nothing, so the project's identity would silently reduce to a
    #: folder name. Found 2026-09-10 by a control that passed `/tmp/here` and
    #: watched the rebase stop recognising its own project. The running code's
    #: repository is the one identity that is always available.
    own = Path(__file__).resolve().parents[1]
    root = Path(repo_root) if repo_root else own
    names, source = set(), "directory"

    declared = declared_project_names(root) or declared_project_names(own)
    if declared:
        names |= declared
        source = "declared"
    try:
        url = subprocess.run(["git", "config", "--get", "remote.origin.url"],
                             cwd=root, capture_output=True, text=True,
                             timeout=30).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        url = ""
    if url:
        base = Path(url.rstrip("/")).name
        if base in (".", ""):                       # a local-path remote
            try:
                base = Path(url).resolve().name
            except OSError:
                base = ""
        if base.endswith(".git"):
            base = base[:-4]
        if base and base.lower() not in _NOT_AN_IDENTITY:
            names.add(base)
            if source == "directory":
                source = "remote"
    # THE FOLDER NAME IS THE WEAKEST TIER AND IS NOW FILTERED. A checkout in a
    # directory called `repo` -- which is what the panel sandbox creates -- would
    # otherwise make every absolute path ending `/repo` this project's tree, and
    # the rebase would rewrite it. Nothing is lost: a project genuinely named
    # `repo` is still recognised by the declared or remote tier.
    if root.name.lower() not in _NOT_AN_IDENTITY:
        names.add(root.name)
    if root != own:
        extra, extra_source = project_names(own)
        names |= extra
        if _SOURCE_RANK[extra_source] > _SOURCE_RANK[source]:
            source = extra_source
    return names, source


#: Strongest first. Used only to report WHICH tier answered, never to choose.
_SOURCE_RANK = {"directory": 0, "remote": 1, "declared": 2}


def foreign_repo_roots(text: str, repo_root: "os.PathLike[str] | str | None" = None
                       ) -> list[str]:
    """Absolute paths in `text` that name a checkout of THIS project elsewhere.

    Longest first, so a caller substituting them cannot leave a shorter prefix
    behind inside a path it has already rewritten.

    WHAT THIS IS FOR. An archived falsifier carries the absolute path of the
    checkout it was WRITTEN in. Replayed anywhere else -- a clone, a worktree,
    another machine -- that path is neither this tree nor reachable, so the
    containment guard refuses it and the finding is thrown to a human for no
    reason but where the directory sits. Measured 2026-09-10: 35 of 640 archived
    falsifiers (5.4688%, Wilson [3.9582%, 7.5107%]) in a fresh clone, and 5 of
    the 15 exp44 execution rows, which is why the headline "12 of 15" could not
    be reproduced by a reader.

    WHAT IT IS NOT FOR, stated so it cannot quietly widen. It recognises ONLY a
    path that ends at a directory named like this project. It does not recognise
    a home directory, a sibling project, or any other absolute path, and it is
    not consulted by the containment guard: a LIVE falsifier naming a path
    outside the current tree is still refused, because containment is about the
    filesystem and not about intent.
    """
    names, _ = project_names(repo_root)
    found = set()
    for name in names:
        if not name:
            continue
        for m in re.finditer(r"(/(?:[^\s'\"`:,;)\]]+/)?" + re.escape(name) + r")(?![\w.-])",
                             text or ""):
            found.add(m.group(1))
    return sorted(found, key=len, reverse=True)


def is_onboarded_checkout(repo_root: "os.PathLike[str] | str | None" = None) -> bool:
    """Has `scripts/cdsfl_onboard.py` been run in THIS checkout?

    WHAT IT DECIDES. Some guards compare the repository against machine-level
    state that a checkout does not own -- the Desktop mirrors, the git hook
    wiring. Exactly 1 checkout on a machine owns those, and a second one
    (a clone made to test reproducibility, a worktree, a sandbox copy) must not
    be judged against them: the mirror it would be compared with is a mirror of
    a DIFFERENT tree, so the comparison reports drift that does not exist.

    Measured 2026-09-10, task A2: a fresh clone at /tmp/ce_fresh failed
    `test_declared_desktop_mirror_matches_its_canonical_copy` because the
    Desktop held the canonical repository's task list, 200,861 bytes against the
    clone's 198,574. Nothing was wrong with either file.

    `cdsfl.onboarded` is written with `git config --local` by
    `wire_git_hooks`, so it lives in `.git/config`, is never cloned, and is not
    removed by unsetting `core.hooksPath` -- which keeps "the guard was turned
    off" distinguishable from "this checkout was never set up".
    """
    import subprocess
    from pathlib import Path

    root = Path(repo_root) if repo_root else Path(__file__).resolve().parents[1]
    try:
        out = subprocess.run(["git", "config", "--local", "--get", "cdsfl.onboarded"],
                             cwd=root, capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return False
    return bool(out.stdout.strip())
