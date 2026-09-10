"""Give a panel seat its own copy of the repository instead of the live one.

FOUNDER RULING 35, and the half of it that was missed. The ruling was "confine real
runs so panel agents cannot write to the canonical repo". CC1 hardened the
FALSIFIER overlay -- a different path -- reported 35 done, and then dispatched 3
more panels into the live tree. On 2026-09-06 a seat edited 4 tracked files during
a review and described its own edit as the pre-existing state of the world. That is
the second confirmed instance; runway item 0C.9 has carried it as HIGH since August.

WHY THE TOOL GRANT WAS NOT ENOUGH. `--allowedTools` already withholds Write and
Edit, and its comment says "No file modification". The seat wrote anyway, through
Bash, which no tool-list can restrain. Confinement has to be positional, not
permissional.

WHY A cwd ALONE IS NOT ENOUGH EITHER, stated rather than glossed. `vault_keys.sh`
records the limit exactly: confining the working directory "stops discovery by
proximity and stops a repository grep, but it does not stop... an absolute path it
has guessed or been told". A seat that writes to /Users/.../Constraint_Engineering
explicitly still reaches the real tree. This module therefore does 2 things: it
puts the seat in a COPY so every relative path is harmless, and it MEASURES the
canonical tree before and after so an absolute-path write is DETECTED rather than
silently absorbed. Prevention for the common case, detection for the rest, and the
gap named instead of papered over.

WHAT THE SEAT CHANGES IS KEPT, NOT DISCARDED. The 2026-09-06 seat's edit was
correct on the merits -- it repaired a real false-convergence path. Throwing such
work away to enforce hygiene would be its own kind of loss, so the sandbox diff is
returned to the caller as a PROPOSAL for CC1 to test under f and sy, which is what
the founder asked for: "their job is not simply to find problems but to find the
simplest and most sufficient fixes... to then suggest them to you".
"""
from __future__ import annotations

import hashlib
import fnmatch
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Dict

_NEVER_COPY = frozenset({".git"})

# SECRETS MUST NOT SURVIVE INTO THE SANDBOX, added 2026-09-07.
#
# The containment fix CREATED this exposure. Confining a seat to a copy of the
# repo is worthless if the copy carries the credentials: measured on the first
# working sandbox, `.env` arrived readable, 1264 bytes, declaring 10 live API
# keys (OpenAI, Google, Gemini, GitHub, Groq, DeepSeek, OpenRouter, Semantic
# Scholar). A seat with shell access -- which is exactly what a seat has, and why
# positional confinement was needed in the first place -- could simply `cat` it.
# Nothing a falsifier or a review seat does requires a credential; the dispatcher
# holds the keys and makes the calls.
#
# Glob patterns, matched at every depth. Deletion happens AFTER the flag clear,
# because `.env` carries the BSD `uchg` flag that `cp -Rc` faithfully preserves
# and that made 264 earlier clones permanently undeletable.
_NEVER_EXPOSE = (
    ".env", ".env.*", "*.env",
    "*.key", "*.pem", "*.p12", "*.pfx",
    "id_rsa", "id_ed25519", "*.keystore",
    ".netrc", ".pgpass", ".npmrc", ".pypirc",
    "credentials.json", "client_secret*.json", "service_account*.json",
    "*answer_key*.json", "*_KEY.json", "*_KEY.md", "*GROUND_TRUTH.json",
)
# `.env.example` holds NAMES and no values, and removing it would change what the
# repo looks like to a seat for no security gain.
_EXPOSE_EXEMPT = frozenset({".env.example", ".env.sample", ".env.template"})


def secret_ignore(*extra_patterns):
    """An ignore callable for `shutil.copytree` that also drops credentials.

    The 4 other places in bench/ that copy the repo into a temporary directory
    all pass `shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache",
    "*.pyc", "logs")` -- a list about SIZE and NOISE that says nothing about
    secrets, so every one of them materialises `.env` outside the repo. Wrapping
    the same list here keeps their existing exclusions and adds the credential
    patterns, rather than leaving 4 copies of the rule to drift apart.
    """
    base = shutil.ignore_patterns(*extra_patterns) if extra_patterns else None

    def _ignore(src, names):
        drop = set(base(src, names)) if base is not None else set()
        for name in names:
            if name in _EXPOSE_EXEMPT:
                continue
            if any(fnmatch.fnmatch(name, pattern) for pattern in _NEVER_EXPOSE):
                drop.add(name)
        return drop

    return _ignore


def _scrub_secrets(dest: Path) -> int:
    """Delete credential-bearing files from the sandbox. Returns the count."""
    removed = 0
    for pattern in _NEVER_EXPOSE:
        for victim in list(dest.rglob(pattern)):
            if victim.name in _EXPOSE_EXEMPT:
                continue
            try:
                if victim.is_dir() and not victim.is_symlink():
                    shutil.rmtree(victim, ignore_errors=True)
                else:
                    victim.unlink(missing_ok=True)
                removed += 1
            except OSError:
                pass
    return removed


def _surviving_secrets(dest: Path) -> list:
    return [p for pattern in _NEVER_EXPOSE for p in dest.rglob(pattern)
            if p.exists() and p.name not in _EXPOSE_EXEMPT]


def _tracked_digest(repo: Path) -> Dict[str, str]:
    """Fingerprint of the canonical tree: tracked files AND untracked paths.

    THE BLIND SPOT THIS FIXES, 2026-09-06. The first version used `git ls-files`
    alone, which lists TRACKED files only. On the very run that was supposed to
    prove containment, a seat created `SEAT_WAS_HERE.txt` in the canonical tree --
    a NEW, UNTRACKED file -- and this function reported the tree "unchanged". The
    one check meant to catch what a sandbox cannot prevent was structurally
    incapable of seeing the most likely form of write: creating a new file.

    `--others` adds untracked paths; `--exclude-standard` keeps .gitignore honoured
    so build noise does not drown the signal.
    """
    out = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=str(repo), capture_output=True, text=True)
    digest: Dict[str, str] = {}
    for rel in out.stdout.split("\0"):
        if not rel:
            continue
        f = repo / rel
        try:
            digest[rel] = hashlib.sha256(f.read_bytes()).hexdigest()
        except OSError:
            continue
    return digest


def build(repo: Path) -> Path:
    """A throwaway copy of `repo` a seat may write to freely.

    Clone if the filesystem supports it (metadata cost), else copy. Flags are
    cleared immediately: `.env` carries BSD `uchg`, `cp -Rc` preserves it, and an
    overlay containing an undeletable file leaks its whole size forever -- 264 such
    clones were found orphaned in TMPDIR on 2026-09-06 before this was understood.
    """
    base = Path(tempfile.mkdtemp(prefix="cdsfl_panel_"))
    dest = base / "repo"
    rc = subprocess.run(["cp", "-Rc", str(repo), str(dest)], capture_output=True)
    if rc.returncode != 0 or not dest.is_dir():
        shutil.rmtree(dest, ignore_errors=True)
        shutil.copytree(repo, dest, symlinks=True,
                        ignore=shutil.ignore_patterns(*_NEVER_COPY))
    subprocess.run(["chflags", "-R", "nouchg,noschg", str(base)], capture_output=True)
    for name in _NEVER_COPY:
        victim = dest / name
        if victim.is_dir() and not victim.is_symlink():
            shutil.rmtree(victim, ignore_errors=True)
        elif victim.exists() or victim.is_symlink():
            victim.unlink(missing_ok=True)
    # A link that resolves outside the sandbox is a way back into the real tree.
    for link in dest.rglob("*"):
        if link.is_symlink():
            target = Path(os.readlink(link))
            resolved = (link.parent / target).resolve()
            if target.is_absolute() or not str(resolved).startswith(str(dest.resolve()) + os.sep):
                link.unlink()
    # Credentials last, and VERIFIED rather than assumed: a scrub that silently
    # missed a file would leave the sandbox looking safe while it is not, which is
    # worse than no scrub at all because it would be trusted.
    _scrub_secrets(dest)
    survivors = _surviving_secrets(dest)
    if survivors:
        shutil.rmtree(base, ignore_errors=True)
        raise RuntimeError(
            "panel sandbox still exposes credential-bearing files after scrub: "
            + ", ".join(sorted(str(p.name) for p in survivors))
        )
    return dest


def changes(sandbox: Path, repo: Path) -> Dict[str, str]:
    """What the seat changed inside its copy, as {relative path: unified diff}."""
    found: Dict[str, str] = {}
    for path in sandbox.rglob("*"):
        if not path.is_file() or path.is_symlink():
            continue
        rel = str(path.relative_to(sandbox))
        original = repo / rel
        try:
            if original.is_file() and original.read_bytes() == path.read_bytes():
                continue
        except OSError:
            continue
        d = subprocess.run(
            ["diff", "-u", str(original) if original.is_file() else "/dev/null", str(path)],
            capture_output=True, text=True)
        if d.stdout.strip():
            found[rel] = d.stdout
    return found


#: Tools that can modify a file. A read naming a path is not evidence of a write.
_WRITING_TOOLS = {"Edit", "Write", "NotebookEdit", "MultiEdit", "str_replace_editor"}

#: Shell verbs that write. `sed -n ... p` prints; `sed -i` edits in place.
_WRITING_SHELL = (">", ">>", "tee ", "cp ", "mv ", "rm ", "sed -i", "truncate",
                  "install ", "dd ", "patch ", "git apply", "git checkout")

#: Shell verbs that only read, listed so the intent is visible rather than
#: inferred from the absence of a writing verb.
_READING_SHELL = ("sed -n", "cat ", "head ", "tail ", "grep ", "rg ", "wc ",
                  "ls ", "diff ", "md5", "shasum", "git show", "git log",
                  # ADDED 2026-09-11 after round 10 reported a CONTAINMENT
                  # FAILURE on the strength of a seat RUNNING THE TEST SUITE.
                  # `python3 -m pytest <path>` names a path and modifies nothing
                  # in it; it fell through to the conservative default and was
                  # counted as a write. An alarm that fires when a seat does
                  # exactly what the brief told it to do is on its way to being
                  # ignored -- this file's own docstring says so about a
                  # different alarm.
                  "pytest", "python3 -m pytest", "-m pytest",
                  "git status", "git diff", "git rev-parse", "git ls-files",
                  "find ", "stat ", "file ")


def _call_can_write(tool_name, preview: str) -> bool:
    """Could this tool call have modified a file? Conservative: unsure is YES."""
    name = str(tool_name or "")
    if name in _WRITING_TOOLS:
        return True
    if name != "Bash":
        return False                       # a non-Bash, non-editing tool reads
    low = str(preview or "").lower()
    if any(w in low for w in _WRITING_SHELL):
        return True
    if any(r in low for r in _READING_SHELL):
        return False
    # An unrecognised shell command is treated as capable of writing. An alarm
    # that under-reports is worse than one that over-reports HERE, because this
    # half is the escape check.
    return True


def attribute_canonical_touch(touched, log_dir, sandbox_root=None,
                              repo_root=None) -> Dict[str, Dict]:
    """For each touched canonical path, can any SEAT be shown to have touched it?

    TASK A5. The alarm fired on 14 files in panel round 2, on 11 in round 8 and
    on 11 again in round 9 -- and every one was the assistant's own concurrent
    edit. Confinement held in all 3: no seat referenced a canonical path. But the
    alarm could not say so, so a human had to re-derive it each time by reading
    the tool logs, and "an alarm that fires on the ordinary case is on its way to
    being ignored" is this project's own warning about its irreducible-queue
    alarm.

    THE EVIDENCE ALREADY EXISTED. Each seat's `*.tools.json` records every call
    it made with an input preview. A seat that wrote to the canonical tree must
    have named the path. So the question "was this seat's doing" is answerable
    from what is already on disk, and this answers it.

    WHAT IT CANNOT DO, said plainly rather than implied. An input preview is
    TRUNCATED, so a path named beyond the cut is invisible here. This therefore
    supports "no seat is shown to have touched it" and never "no seat did". The
    return value says which of those it means.
    """
    import json as _json
    log_dir = Path(log_dir)
    seats = {}
    for f in sorted(log_dir.glob("*.tools.json")):
        try:
            seats[f.name.replace(".tools.json", "")] = _json.loads(f.read_text())
        except (ValueError, OSError):
            continue

    # ONE OR MANY. Each seat now gets its own sandbox, so this accepts a list
    # and excludes ALL of them; passing only the first would report every other
    # seat's own correct edits as escapes.
    if sandbox_root is None:
        sandbox_roots = []
    elif isinstance(sandbox_root, (list, tuple, set)):
        sandbox_roots = [str(x) for x in sandbox_root]
    else:
        sandbox_roots = [str(sandbox_root)]
    out: Dict[str, Dict] = {}
    truncated_previews = 0
    for rel in touched:
        hits = []
        for seat, log in seats.items():
            for call in log.get("calls") or []:
                prev = str(call.get("input_preview") or "")
                if prev.endswith("...") or prev.endswith("\u2026"):
                    truncated_previews += 1
                if rel not in prev:
                    continue
                # A sandbox path CONTAINING the relative path is the ordinary,
                # correct case: the seat edited its own copy.
                if any(r in prev for r in sandbox_roots):
                    continue
                # A RELATIVE PATH CANNOT REACH THE CANONICAL TREE. Added
                # 2026-09-11 after round 10 declared a containment failure and
                # was wrong. The seat ran
                #   python3 - <<'PYEOF' ... pathlib.Path("bench/repo_paths.py")
                # with its cwd INSIDE the sandbox. The preview holds the relative
                # path and not the sandbox root, so the exclusion above missed it
                # and a correct, instructed edit to the seat's own copy was
                # reported as an escape.
                #
                # This file's own `canonical_was_touched` already states the
                # mechanism: "A sandbox stops relative writes. It cannot stop a
                # seat writing to an absolute path it already knows." So the
                # ABSOLUTE canonical path is the only form that is evidence, and
                # requiring it is not a weakening -- it is the rule the docstring
                # already described.
                if repo_root:
                    absolute = str(Path(repo_root) / rel)
                    if absolute not in prev:
                        continue
                # A READ IS NOT A WRITE, and counting it as one is how an alarm
                # earns its reputation for crying wolf. The first version of this
                # counted any mention, and reported round 8 as attributable on
                # the strength of a `sed -n '3733,3739p'` -- a seat READING a
                # note. Only a call that can modify a file is evidence.
                if not _call_can_write(call.get("name"), prev):
                    continue
                hits.append({"seat": seat, "tool": call.get("name"),
                             "preview": prev[:160]})
        out[rel] = {
            "attributable_to_a_seat": bool(hits),
            "hits": hits,
            "verdict": ("A SEAT NAMED THIS CANONICAL PATH" if hits else
                        "no seat is shown to have touched it"),
        }
    return {"_per_path": out,
            "_seats_examined": sorted(seats),
            "_any_attributable": any(v["attributable_to_a_seat"] for v in out.values()),
            "_truncated_previews_seen": truncated_previews,
            "_limit": ("an input preview is truncated, so this supports 'no seat "
                       "is SHOWN to have touched it' and never 'no seat did'")}


def canonical_was_touched(before: Dict[str, str], repo: Path) -> Dict[str, str]:
    """Tracked files whose content changed in the CANONICAL tree. Detection half.

    A sandbox stops relative writes. It cannot stop a seat writing to an absolute
    path it already knows, and this project's own key-vault comment says so. This
    is how that residue is caught rather than assumed away.
    """
    after = _tracked_digest(repo)
    touched = {}
    for rel, sha in after.items():
        if rel not in before:
            touched[rel] = "CREATED"        # the case that was invisible before
        elif before[rel] != sha:
            touched[rel] = "modified"
    for rel in before:
        if rel not in after:
            touched[rel] = "deleted"
    return touched


def fingerprint(repo: Path) -> Dict[str, str]:
    return _tracked_digest(repo)


# THE CONTROL PLANE LIVES OUTSIDE THE REPO, AND NOTHING WATCHED IT.
#
# 2026-09-07, 15:04:45: a seat running under this sandbox wrote to the operator's
# REAL ~/.claude/settings.json. `canonical_was_touched` did not fire and could
# not have -- it digests the repo's tracked files, and $HOME is not among them.
# The write happened to be benign (it appended a hook entry and removed nothing),
# which is luck, not containment.
#
# These paths are not ordinary files. ~/.claude/settings.json names HOOKS, which
# are commands executed on every turn of every session; ~/.claude/hooks/ holds
# their code; ~/.claude/CLAUDE.md is the directive set every model is handed; the
# memory directory is the record those directives are built from. A seat editing
# any of them changes the behaviour of the operator's other sessions, silently
# and after the panel has ended.
#
# DETECTION, NOT PREVENTION, AND DELIBERATELY SO. The obvious prevention is to
# rewrite HOME for the seat process. This project already ran that experiment
# from the other end: `--bare` was added to confine the CLI, and because it also
# skips keychain reads it selected an auth mode this account does not have, so
# every headless dispatch returned "Not logged in" (experiment_11_orchestrator,
# 2026-07-29). Moving HOME would break OAuth the same way. The layered position
# taken everywhere else applies here too: the pointer stays reachable, the use
# is detected. See `canonical_was_touched`, whose docstring states the same
# limit for the repo half.
_CONTROL_PLANE = (
    ".claude/settings.json",
    ".claude/settings.local.json",
    ".claude/CLAUDE.md",
)
_CONTROL_PLANE_GLOBS = (
    ".claude/hooks/*.py",
    ".claude/projects/-Users-georgejackson-Developer-Projects/memory/*.md",
)


def control_plane_fingerprint(home: "Path | None" = None) -> Dict[str, str]:
    """Digest the operator files a seat could reach by absolute path.

    Missing files are recorded as absent rather than skipped, so a seat CREATING
    one is caught. That was the hole in the repo-side check until it started
    reporting "CREATED".
    """
    base = Path(home) if home else Path.home()
    out: Dict[str, str] = {}
    paths = [base / rel for rel in _CONTROL_PLANE]
    for pat in _CONTROL_PLANE_GLOBS:
        paths.extend(sorted(base.glob(pat)))
    for path in paths:
        rel = str(path.relative_to(base))
        try:
            out[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
        except (OSError, ValueError):
            out[rel] = "ABSENT"
    return out


def control_plane_was_touched(
    before: Dict[str, str], home: "Path | None" = None
) -> Dict[str, str]:
    """What changed in the operator's control plane while the panel ran."""
    after = control_plane_fingerprint(home)
    touched: Dict[str, str] = {}
    for rel, sha in after.items():
        if rel not in before:
            touched[rel] = "CREATED"
        elif before[rel] != sha:
            touched[rel] = "CREATED" if before[rel] == "ABSENT" else "modified"
    for rel, sha in before.items():
        if rel not in after:
            touched[rel] = "deleted"
        elif after[rel] == "ABSENT" and sha != "ABSENT":
            touched[rel] = "deleted"
    return {k: v for k, v in touched.items() if v != "ABSENT"}


def teardown(sandbox: Path) -> None:
    """Remove a sandbox. REFUSES to remove the system temp root itself.

    THE ACCIDENT THIS PREVENTS, 2026-09-07. A cleanup line written as
    `rmtree(x.parent)` is correct when `x` is a CHILD of a mkdtemp directory and
    catastrophic when `x` IS one: `_build_discrimination_overlay` returns the
    mkdtemp directory itself, so its `.parent` is TMPDIR. One such line removed
    179 sibling entries in a single call -- pytest's own working tree among them,
    producing 388 errors in one suite run -- and destroyed a panel sandbox that
    was live in another terminal, a loss then mistakenly written up as a review
    seat deleting its own working directory. Nothing a caller passes here should
    ever be the temp root, so saying so out loud costs nothing.
    """
    base = sandbox.parent if sandbox.name == "repo" else sandbox
    _tmp = Path(tempfile.gettempdir()).resolve()
    _base = base.resolve()
    if _base == _tmp or _base in _tmp.parents:
        raise ValueError(
            f"refusing to remove {base}: that is the system temp root, not a "
            f"sandbox. A caller has passed a mkdtemp directory where a child of "
            f"one was expected.")
    subprocess.run(["chflags", "-R", "nouchg,noschg", str(base)], capture_output=True)
    shutil.rmtree(base, ignore_errors=True)
