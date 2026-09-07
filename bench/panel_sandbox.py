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


def teardown(sandbox: Path) -> None:
    base = sandbox.parent if sandbox.name == "repo" else sandbox
    subprocess.run(["chflags", "-R", "nouchg,noschg", str(base)], capture_output=True)
    shutil.rmtree(base, ignore_errors=True)
