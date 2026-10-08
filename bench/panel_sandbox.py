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
import json
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

    THIS DESCRIBES THE 4 `copytree` CALLERS AND NOT `build` BELOW, a distinction
    that cost a containment breach on 2026-09-30. `build` clones with `cp -Rc`,
    which takes NO ignore callable, so nothing in this paragraph ever applied to
    the panel sandbox: it carried `__pycache__` and `*.pyc` through, and a `.pyc`
    embeds the absolute source path it was compiled from. See `_purge_bytecode`,
    which removes them after the copy because the copy itself cannot filter.
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


def _purge_bytecode(dest: Path) -> int:
    """Remove every compiled-bytecode artefact from a fresh sandbox. Returns the count.

    WHY THIS EXISTS, and it is a CONTAINMENT repair rather than a size one. Found
    2026-09-30 by the fable seat inspecting its OWN failure: its regression run
    inside a sandbox produced tracebacks naming paths in the REAL repository. A
    `.pyc` embeds the absolute source path it was compiled from in `co_filename`,
    so a cached test module imported inside the sandbox reports a `__file__`
    OUTSIDE the sandbox, and anything deriving a path from `__file__` can then
    import real-repository modules into a panel measurement. It demonstrated this
    by running `strings` over the `.pyc`, purging, and re-running.

    THE PRIMARY COPY PATH CANNOT FILTER, WHICH IS WHY THIS IS A POST-COPY PURGE.
    `build` clones with `cp -Rc` for the metadata cost, and a clone takes
    everything; `shutil.copytree(..., ignore=...)` is only the FALLBACK when the
    clone fails. So the ignore list never ran on this machine's filesystem. The
    `_NEVER_COPY` delete loop beside it is also NON-RECURSIVE -- it removes
    `dest / name` only -- while caches are scattered throughout a tree. Both
    reasons force a recursive sweep here.

    Measured before the fix, over the 104 sandboxes still on disk from the
    2026-09-30 rounds: individual sandboxes carried 61, 83, 24 and 4 `.pyc`
    files. `secret_ignore`'s docstring already CLAIMED that callers exclude
    `__pycache__` and `*.pyc`; that describes the callers of `secret_ignore`, not
    this path, and the claim is corrected there.

    Directories are removed before files so the file sweep has less to walk, and
    both are tolerant of a racing removal.
    """
    removed = 0
    for d in sorted(dest.rglob("__pycache__"), key=lambda q: -len(q.parts)):
        if d.is_dir() and not d.is_symlink():
            removed += sum(1 for _ in d.rglob("*") if _.is_file())
            shutil.rmtree(d, ignore_errors=True)
    for pattern in ("*.pyc", "*.pyo"):
        for f in dest.rglob(pattern):
            try:
                if f.is_file() or f.is_symlink():
                    f.unlink(missing_ok=True)
                    removed += 1
            except OSError:
                continue
    return removed


def purge_round_evidence(dest: Path, round_names) -> int:
    """Remove every artefact of the named panel round(s) from a sandbox copy.

    WHY THIS EXISTS. Panel review runs in star topology: each seat answers BLIND
    first, and a joint round follows once the blind replies are in. A blind round
    is only blind if the seat cannot read what the other seat said -- and the
    sandbox is a whole-repository clone, so the moment round 1's replies are
    harvested into the tree, every later sandbox carries them.

    THIS HAS ALREADY HAPPENED ONCE AND WAS RECORDED RATHER THAN FIXED. The
    2026-10-03 session state says of the three-round sequence: "ROUND 2 WAS NOT
    BLIND WITH RESPECT TO ROUND 1: every round-2 sandbox contained round 1's
    harvested seat evidence, so its richer output cannot be attributed to the
    standards alone. The containment fix is to exclude prior rounds' seat evidence
    from a blind round's sandbox copy." That fix is this function.

    It reproduced again on 2026-10-05: a cc2 blind re-run was dispatched at 04:33
    after the fable seat's full reply had been harvested into the tree at 03:18,
    and the sandbox was verified to contain both
    `experimental_notes/seat_evidence/<round>/fable_FULL_REPLY.md` and the mirrored
    `experimental_notes/evidence/panel_records_*/<round>/fable.json`. The run was
    killed rather than allowed to produce a contaminated comparison.

    A POST-COPY PURGE, for the reason `_purge_bytecode` gives: `build` clones with
    `cp -Rc`, a clone takes everything, and the `ignore=` callable only runs on the
    fallback path. Filtering at copy time is therefore not available here.

    VERIFIED, NOT ASSUMED, to the same standard as the credential scrub: the caller
    re-walks for survivors and refuses the sandbox if any remain. A purge that
    silently missed a file would leave the sandbox looking blind while it is not,
    which is worse than no purge because it would be trusted.
    """
    removed = 0
    for name in round_names:
        name = str(name).strip()
        if not name:
            continue
        for q in sorted(dest.rglob(f"*{name}*"), key=lambda z: -len(z.parts)):
            try:
                if q.is_dir() and not q.is_symlink():
                    removed += sum(1 for _ in q.rglob("*") if _.is_file())
                    shutil.rmtree(q, ignore_errors=True)
                elif q.exists() or q.is_symlink():
                    q.unlink(missing_ok=True)
                    removed += 1
            except OSError:
                continue
    return removed


def round_fingerprints(round_dir: Path, n: int = 12, min_len: int = 40) -> list:
    """Distinctive phrases from a round's seat replies, for CONTENT checking.

    A path check alone cannot establish blindness, and assuming it could is the
    error this function exists to prevent. Measured 2026-10-05: after purging every
    path containing the round id, the sandbox still carried the other seat's
    verdict through `Panel_FULL_RECORD_Fingerprint_Ladder_2026-10-05.md` and
    `The_Blockers_Were_Shown_As_Settled_2026-10-05.md` -- both written FROM that
    round, neither named for it. The purge reported 0 survivors and the seat could
    still read the whole review.

    Phrases are drawn from the replies themselves so the check cannot drift from
    what was actually said.

    `n` IS 12 WORDS, NOT 6. At 6 the first version returned 0 fingerprints on a
    real reply and the guard would have passed over nothing: a 6-word English
    phrase averages about 31 characters, below the 40-character floor that keeps
    common phrases out, so every candidate was rejected. Caught by its own test.
    """
    out = []
    for q in sorted(round_dir.glob("*.json")):
        if q.name.endswith(".tools.json"):
            continue
        try:
            d = json.loads(q.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        body = d.get("response") if isinstance(d, dict) else None
        if not isinstance(body, str) or not body.strip():
            continue
        words = body.split()
        for i in range(0, max(0, len(words) - n), max(1, (len(words) - n) // 24 or 1)):
            phrase = " ".join(words[i:i + n])
            if len(phrase) >= min_len and phrase not in out:
                out.append(phrase)
    return out


def surviving_round_evidence(dest: Path, round_names, blind_text=()) -> list:
    """What a sandbox can still reach of a round it must be blind to.

    Returns PATHS naming the round plus any file whose CONTENT carries one of
    `blind_text`. Empty means blind. A caller passing only `round_names` gets the
    path check alone, which 2026-10-05 showed is NOT sufficient on its own.
    """
    out = []
    for name in round_names:
        name = str(name).strip()
        if name:
            out.extend(dest.rglob(f"*{name}*"))
    if blind_text:
        seen = set(out)
        for q in dest.rglob("*"):
            if not q.is_file() or q in seen:
                continue
            try:
                if q.stat().st_size > 4_000_000:
                    continue
                body = q.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            if any(t in body for t in blind_text):
                out.append(q)
                seen.add(q)
    return out


#: THE 1 FILE OF ITS OWN ROUND A SEAT IS SUPPOSED TO SEE.
OWN_ROUND_KEEP = ("BRIEF.md",)


def coseat_survivors(dest: Path, own_round) -> list:
    """What a sandbox can still reach of ITS OWN round, brief excluded.

    THE GAP THIS CLOSES, PROVEN BY EXECUTION 2026-10-08 against the live tree of
    `division_count_and_bidirectional_ladder_blind_2026-10-08`. `blind_of` names
    OTHER rounds. It has no way to say "blind of my own round's other seats", and
    the first dispatch of a 2-seat blind round cannot know a co-seat will land
    while it is still running. Measured on that round: built with `blind_of=()`
    -- which is what it was running under -- a fresh sandbox carried
    `fable.json` and `fable.tools.attempt1.json.txt`, the co-seat's whole 12,299
    character reply. That is what a RETRY would have been handed, because
    `fresh_sandbox_for_attempt` clones the LIVE tree at retry time.

    AND THE EXISTING CONTROL CANNOT BE USED INSTEAD. Passing the round's own name
    to `blind_of` removes the WHOLE directory, `BRIEF.md` with it, measured in the
    same probe: a seat told to work in the tree would find no brief there at all.
    So the fix needs file-level selectivity, not another entry in `blind_of`.

    THE WALK IS `surviving_round_evidence`'S, NOT A SECOND ONE. Two predicates
    about what counts as "an artefact of this round" would be the producer and
    consumer drift this project keeps paying for -- each individually correct and
    disagreeing at the boundary. This EXPANDS that function's output rather than
    re-deriving it.

    AND THE EXPANSION IS THE WHOLE POINT, because the first version of this
    function got it wrong in the direction that reports success. The round name
    appears in the DIRECTORY name, not in `fable.json`, so
    `surviving_round_evidence`'s `rglob(f"*{name}*")` matches the directory and
    nothing inside it. A first version discarded directories as "not evidence"
    and therefore returned an EMPTY survivor list while the co-seat's reply sat
    untouched in the sandbox -- a check that agreed with what it was hoping for.
    Caught by looking at the files instead of at the predicate, which is this
    project's own standing rule: check the predicate before the result.
    """
    if not own_round:
        return []
    keep = {(dest / "bench" / "logs" / str(own_round) / k).resolve()
            for k in OWN_ROUND_KEEP}
    out, seen = [], set()
    for q in surviving_round_evidence(dest, (own_round,)):
        # A MATCH MAY BE A DIRECTORY, and then its CONTENTS are the evidence.
        members = sorted(q.rglob("*")) if q.is_dir() else [q]
        for m in members:
            if not m.is_file():
                continue
            try:
                rm = m.resolve()
            except OSError:
                rm = m
            if rm in keep or rm in seen:
                continue
            seen.add(rm)
            out.append(m)
    return out


def purge_coseat_evidence(dest: Path, own_round) -> int:
    """Remove this round's own seat artefacts, keeping only the brief."""
    n = 0
    for q in coseat_survivors(dest, own_round):
        try:
            q.unlink(missing_ok=True)
            n += 1
        except OSError:
            continue
    return n


def build(repo: Path, blind_of=(), blind_text=(), own_round=None) -> Path:
    """A throwaway copy of `repo` a seat may write to freely.

    `blind_of` names panel rounds this sandbox must NOT be able to read, so a
    blind round in star topology is genuinely blind. Default empty: every existing
    caller behaves exactly as before, which is what makes this additive.

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
    # BYTECODE FIRST, because a stale `.pyc` is a route back into the real tree
    # (see `_purge_bytecode`), and because removing these directories shrinks the
    # symlink walk below.
    _purge_bytecode(dest)
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
    # PRIOR-ROUND EVIDENCE, before the credential scrub so a refusal below leaves
    # nothing half-purged. Default empty, so this is inert unless a caller asks.
    if blind_of or blind_text:
        if blind_of:
            purge_round_evidence(dest, blind_of)
        if blind_text:
            # CONTENT-BEARING FILES ARE REMOVED TOO, not merely detected. A file
            # carrying the other seat's verdict defeats blindness whatever it is
            # called.
            for q in list(surviving_round_evidence(dest, (), blind_text)):
                try:
                    q.unlink(missing_ok=True)
                except OSError:
                    continue
        leaked = surviving_round_evidence(dest, blind_of, blind_text)
        if leaked:
            shutil.rmtree(base, ignore_errors=True)
            raise RuntimeError(
                f"panel sandbox still exposes {len(leaked)} artefact(s) of the "
                f"round(s) it must be blind to, e.g. "
                + ", ".join(sorted(str(q.relative_to(dest)) for q in leaked[:4]))
                + ". A blind round that can read the other seat's reply is not a "
                "blind round."
            )
    # ITS OWN ROUND'S CO-SEAT REPLIES, same verify-and-refuse shape as the 2
    # blocks above and for the same stated reason. Inert when `own_round` is None,
    # so every existing caller behaves exactly as before.
    if own_round:
        purge_coseat_evidence(dest, own_round)
        left = coseat_survivors(dest, own_round)
        if left:
            shutil.rmtree(base, ignore_errors=True)
            raise RuntimeError(
                f"panel sandbox still exposes {len(left)} artefact(s) of its OWN "
                f"round {own_round!r}, e.g. "
                + ", ".join(sorted(str(q.relative_to(dest)) for q in left[:4]))
                + ". A seat that can read its co-seat's reply is not answering "
                "blind, and a retry clones the live tree at retry time."
            )

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
    # VERIFIED RATHER THAN ASSUMED, to the same standard as the credential scrub
    # directly above, and for the same reason its comment gives: a purge that
    # silently missed a file would leave the sandbox looking contained while it is
    # not, which is worse than no purge because it would be trusted.
    stale = [q for pat in ("*.pyc", "*.pyo") for q in dest.rglob(pat)]
    stale += [q for q in dest.rglob("__pycache__") if q.is_dir()]
    if stale:
        shutil.rmtree(base, ignore_errors=True)
        raise RuntimeError(
            f"panel sandbox still carries {len(stale)} compiled-bytecode "
            f"artefact(s) after the purge, e.g. "
            + ", ".join(sorted(str(q.relative_to(dest)) for q in stale[:4]))
            + ". A .pyc embeds the absolute path it was compiled from, so an "
            "import inside the sandbox can resolve to the real repository."
        )
    return dest



#: A seat's own scratch directory. EXCLUDED FROM THE PROPOSALS DIFF ONLY, never
#: from the harvest.
#:
#: WHY THE ASYMMETRY, MEASURED 2026-09-20. `seat_proposals.diff` is mirrored
#: into the TRACKED evidence record, and on this round it introduced 6,430 of
#: the 7,032 unique `bench/logs/...` paths in the whole tracked tree -- 91% of
#: the population the citation census reads -- entirely from `.scratch` dumps
#: of `git rev-list` and `git ls-tree` output that the seats produced while
#: answering a git-history question. A machine dump is not a citation, and a
#: record that swamps the thing it records is not a record.
#:
#: NOTHING IS DISCARDED, which is the founder's ruling (j) and the reason this
#: is not simply added to `_VCS_DIRS`. `harvest` still takes the whole of
#: `.scratch` into the run's log directory, so every byte a seat produced
#: survives on disk. What changes is only what the mirrored DIFF carries.
#:
#: IT ALSO MATCHES WHAT THE SEATS WERE TOLD. The brief requires each fix
#: "delivered as a file in your sandbox repository tree, at a real path", and
#: `.scratch` is by construction not one. cc2 followed that and delivered
#: `scripts/a8_shell_crossverify_2026-09-20.sh`; the scratch material either
#: side of it is working-out, not the work.
_SCRATCH_DIRS = (".scratch",)


def _is_seat_scratch(rel: str) -> bool:
    """Is this the seat's working-out rather than its delivered proposal?"""
    return any(d in Path(rel).parts for d in _SCRATCH_DIRS)


def changes(sandbox: Path, repo: Path, *, include_scratch: bool = False) -> Dict[str, str]:
    """What the seat changed inside its copy, as {relative path: unified diff}.

    `include_scratch` DEFAULTS TO FALSE because the common caller is the
    proposals diff, which is mirrored into the tracked record. `harvest` passes
    True: it writes to the run's own log directory, where nothing is discarded.
    Getting this backwards would have silently dropped the seats' working
    material from the harvest -- the exact outcome founder ruling (j) forbids --
    while appearing to fix a measurement, so it is a parameter rather than a
    blanket rule, and a test drives both values.
    """
    found: Dict[str, str] = {}
    for path in sandbox.rglob("*"):
        if not path.is_file() or path.is_symlink():
            continue
        rel = str(path.relative_to(sandbox))
        # A CLONED OBJECT STORE IS NOT A SEAT'S PROPOSAL (2026-09-20). The same
        # rule `harvest` applies, and it belongs here too because THIS is where
        # the damage was done: on the 2026-09-20 round both seats cloned the
        # repository's git objects into their sandboxes so the git-dependent
        # questions in their brief could be answered, and every object then
        # read as a change. `seat_proposals.diff` came out at 7,823,216 bytes
        # and opened with diffs of `.git/ORIG_HEAD` and `.git/config`.
        #
        # THE COST WAS NOT ONLY SIZE. That file is mirrored into the tracked
        # evidence record, and it alone contributed 50,297 of the 63,631
        # `bench/logs/...` path strings in the whole tracked tree -- 79 percent
        # of the corpus the citation census reads. A transcript of a cloned
        # object store was about to become the dominant source of "citations".
        if _is_vcs_metadata(rel) or (not include_scratch and _is_seat_scratch(rel)):
            continue
        original = repo / rel
        try:
            if original.is_file() and original.read_bytes() == path.read_bytes():
                continue
        except OSError:
            continue
        # BYTES, NOT TEXT. `text=True` decodes as UTF-8 and RAISES on the first
        # byte that is not -- and on 2026-09-11 round 15 died exactly there,
        # `UnicodeDecodeError: invalid start byte 0x91`, AFTER both seats had
        # replied. The replies survived on disk; what was lost was
        # `seat_proposals.diff`, which is the artefact carrying the seats' FIXES.
        # The founder's whole instruction for these rounds is "they need to
        # supply fixes, not just problems", so the one step that captures the
        # fixes is the worst possible place for a decode to be fatal.
        #
        # A seat can legitimately produce such a file: a test fixture of raw
        # bytes, a smart quote in latin-1, a truncated binary. Refusing to
        # describe it is right; killing the run is not.
        d = subprocess.run(
            ["diff", "-u", str(original) if original.is_file() else "/dev/null", str(path)],
            capture_output=True)
        out = d.stdout.decode("utf-8", errors="replace")
        if out.strip():
            found[rel] = out
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


#: Directories a seat may CREATE but does not AUTHOR. Harvesting them is not
#: preserving work.
#:
#: MEASURED ON THE 2026-09-20 ROUND, which is why the list is what it is. The
#: proposals diff came out at 7,645,357 bytes across 104 files. 15.6% of it was
#: a single `.pytest_cache/v/cache/nodeids`, which is pytest's own bookkeeping
#: and nothing a seat wrote. The git stores the seats cloned in, so that the
#: git-dependent questions in their brief could be answered at all, accounted
#: for the rest of this list.
#:
#: `.scratch` IS DELIBERATELY NOT HERE. It holds 80.3% of that diff, and
#: dropping it would be the bigger saving -- but a seat can and does deliver
#: real work there: fable named `.scratch/shell_classifier.sh` as an artefact
#: in its reply. The founder's ruling (j) is that results must not be
#: discarded, so the ephemeral caches go and the working material stays.
_VCS_DIRS = (".git", ".hg", ".svn", ".pytest_cache", "__pycache__",
             ".mypy_cache", ".ruff_cache")


def _run_log_dir(dest: Path, repo: Path) -> str | None:
    """The run's own log directory, relative to the repo, or None.

    Identified as the ancestor of `dest` sitting directly inside a directory named
    `logs`, which holds for every harvest destination this project uses:
      <run>/sandbox_harvest/<seat>/attempt-N   (confer_maths_panel)
      <run>/worktree_harvest/<tag>             (confer_convergence_panel, build_experiment_run)
      <run>/panel_worktree_harvest             (run_simulated_experiment)
    Returning None means "exclude nothing", which is the old behaviour and the
    safe direction: over-harvesting is untidy, under-harvesting loses seat work.
    """
    try:
        d = dest.resolve()
        root = repo.resolve()
    except OSError:
        return None
    for anc in [d, *d.parents]:
        if anc.parent.name == "logs":
            try:
                return str(anc.relative_to(root))
            except ValueError:
                return None
    return None


def _is_dispatcher_own_output(rel: str, run_log_rel: str | None) -> bool:
    """Is this path the DISPATCHER'S own log output rather than seat-written work?

    MEASURED 2026-09-28, AND IT IS THE SAME SHAPE AS THE `.git` CASE BELOW. The
    sandbox is a copy of the repository, and the dispatcher writes its run log
    INTO `bench/logs/<run>/` -- which exists inside that copy too. Every one of
    those writes then read as a CHANGED FILE, so the harvest copied the
    dispatcher's own output back out and announced it as seat work.

    On the founder_verdicts_2026-09-28 round BOTH seats failed at authentication
    with 0 tool calls and wrote nothing at all, and the run still printed "seats
    proposed edits to 8 file(s)" and "harvested 3394 byte(s) of seat-written
    files". All 9 captured paths were dispatcher or harvest artefacts, the only
    "change" in the diff was `elapsed_s` differing by 0.9 between the canonical
    log and the copy's, and `sandbox_harvest/cc2/attempt-1/changes.diff` appears
    INSIDE the harvested files -- the harvest harvesting itself.

    THAT IS A PROVENANCE DEFECT, not untidiness. A reader of that log would
    conclude 2 seats did work on a round where neither ran, and on a round where
    seats DO work their real deliverables arrive mixed with this noise.

    SCOPED TO THE CURRENT RUN, DELIBERATELY. Excluding `bench/logs/` wholesale
    would discard a measurement a seat was ASKED to write there. Only the run's
    own directory is excluded, derived from the harvest destination, so a seat
    writing anywhere else in the tree is unaffected.
    """
    if not run_log_rel:
        return False
    run_log_rel = run_log_rel.replace(os.sep, "/").strip("/")
    rel = rel.replace(os.sep, "/").strip("/")
    return rel == run_log_rel or rel.startswith(run_log_rel + "/")


def _is_vcs_metadata(rel: str) -> bool:
    """Is this path inside a version-control store rather than seat-written work?

    MEASURED 2026-09-20, ON THE FIRST ROUND AFTER THE HARVEST LANDED. Both seats
    reported their sandbox arriving with no `.git` -- `build()` removes it by
    design -- and each cloned the repository's object store in, read-only, so
    that the git-dependent claims in their brief could be answered at all. Every
    object they cloned then read as a CHANGED FILE, so the harvest copied the
    store back out: 112 MB across 63 files, 15 of them inside `.git`, including
    pack files already present in the repository 1 directory up.

    IT ALSO TRIPPED A PROVENANCE GUARD, which is how it was found.
    `test_no_bare_vendor_name_in_any_simulated_artefact` classified the harvest
    tree as a simulated artefact -- any copy of this repository contains the
    string `-SIM`, because the codebase implements simulated labels -- and then
    read the seat directory name `cc2` as a bare vendor name. 44 hits. The same
    false-positive class this guard's own docstring records for 2026-08-30, one
    level deeper, and the fix is the same in spirit: do not reclassify a copy of
    the repository as a statement about the run.

    NOT AN EXCLUSION LIST AND NOT A WEAKENING. Nothing a seat authors is lost:
    a seat's own files, scripts, tests and data still harvest exactly as before.
    What stops being copied is a store the seat cloned rather than wrote.
    """
    parts = Path(rel).parts
    return any(d in parts for d in _VCS_DIRS)


def harvest(sandbox: Path, repo: Path, dest: Path) -> dict:
    """Take everything a seat changed OUT of `sandbox` and put it in `dest`.

    FOUNDER RULING (j), 2026-09-17: *"Take care when a panel review or an
    experiment completes however that the sandbox does not simply get
    automatically deleted and that the results do not end up simply being
    discarded, as has happened in the recent past."*

    `changes()` describes the edits as diffs, which is enough to READ them and
    not enough to RE-RUN them: a seat that wrote a new script, a data file or a
    figure leaves an artefact whose value is the file itself. This copies the
    whole changed file, keeps the diff beside it, and returns a manifest saying
    exactly what was taken, so a later reader can tell "nothing was changed"
    from "the harvest failed".
    """
    dest = Path(dest)
    files_dir = dest / "files"
    taken, bytes_taken, failed = [], 0, []
    # include_scratch=True: the harvest is the place nothing is discarded.
    diffs = changes(Path(sandbox), Path(repo), include_scratch=True)
    skipped_vcs = [r for r in diffs if _is_vcs_metadata(r)]

    # THE RUN'S OWN LOG DIRECTORY, derived rather than passed, so all 3 harvest
    # call sites get the fix without changing 3 signatures.
    #
    # DERIVED STRUCTURALLY, NOT BY DEPTH, and the first version of this was WRONG.
    # It used `parents[2]`, which is right only for the dispatcher's
    # `<run>/sandbox_harvest/<seat>/attempt-N`. The other 2 callers are shallower:
    # `<run>/worktree_harvest/<tag>` would have resolved to `bench/logs` and
    # `<run>/panel_worktree_harvest` to `bench` -- excluding the ENTIRE bench tree
    # from every simulated run's harvest. Found by tracing the call sites rather
    # than by the tests, which only ever exercised the deepest shape.
    #
    # The rule that holds for all 3: the run directory is the ancestor of `dest`
    # that sits DIRECTLY INSIDE a directory named `logs`.
    run_log_rel = _run_log_dir(Path(dest), Path(repo))
    skipped_own = [r for r in diffs if _is_dispatcher_own_output(r, run_log_rel)]

    for rel in sorted(set(diffs) - set(skipped_vcs) - set(skipped_own)):
        src = Path(sandbox) / rel
        try:
            target = files_dir / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, target)
            taken.append(rel)
            bytes_taken += target.stat().st_size
        except OSError as exc:                                  # noqa: PERF203
            failed.append({"path": rel, "error": str(exc)})
    dest.mkdir(parents=True, exist_ok=True)
    if skipped_vcs:
        print(f"    harvest skipped {len(skipped_vcs)} version-control file(s) "
              f"the seat cloned rather than wrote", flush=True)
    if skipped_own:
        print(f"    harvest skipped {len(skipped_own)} file(s) of this run's OWN "
              f"log output, which the dispatcher wrote inside the copy", flush=True)
    # The diff excludes them too. A changes.diff listing the dispatcher's own
    # `elapsed_s` drift is what made a 0-work round look like an 8-file round.
    seat_diffs = {rel: d for rel, d in diffs.items()
                  if rel not in set(skipped_vcs) | set(skipped_own)}
    if seat_diffs:
        (dest / "changes.diff").write_text(
            "\n".join(f"### {rel}\n{d}" for rel, d in sorted(seat_diffs.items())),
            encoding="utf-8")
    # SEAT EVIDENCE OUT OF THE IGNORED TREE, 2026-10-01. Wired HERE rather than
    # at the 3 call sites, for the same reason `run_log_rel` is derived here:
    # one place to fix, and no call site can forget it.
    preserved = preserve_seat_evidence(Path(dest), Path(repo))
    if preserved.get("preserved"):
        print(f"    harvest preserved {len(preserved['preserved'])} seat-written "
              f"file(s) to {preserved['dir']} -- they exist nowhere else a clone "
              f"can reach", flush=True)
    if preserved.get("failed"):
        print(f"    harvest FAILED to preserve {len(preserved['failed'])} "
              f"seat-written file(s); they remain only in the ignored tree",
              flush=True)
    return {"sandbox": str(sandbox), "dest": str(dest), "changed": len(seat_diffs),
            "changed_including_excluded": len(diffs),
            "skipped_own_log_output": len(skipped_own),
            "files_taken": taken, "bytes": bytes_taken, "failed": failed,
            "seat_evidence_preserved": preserved,
            "harvested": not failed}


def release(sandbox: Path, repo: Path, dest: Path, reap: bool = False) -> dict:
    """Harvest a sandbox, then remove it ONLY if asked AND the harvest succeeded.

    The default keeps the copy on disk. Deleting it is a choice a caller makes
    explicitly, and it is refused outright when anything failed to come out --
    the ruling above exists because results went with the sandbox once already.
    """
    m = harvest(sandbox, repo, dest)
    m["reaped"] = False
    if reap and m["harvested"]:
        teardown(Path(sandbox))
        m["reaped"] = True
    elif reap:
        m["reap_refused"] = ("the harvest did not complete, so removing the copy "
                             "would destroy the only surviving record")
    m["exists"] = Path(sandbox).exists()
    return m


# ═════════════════════════════════════════════════════════════════════════════
# PREVENTION FOR THE BASH HALF, added 2026-10-01 on the founder's "Fix it".
#
# THE GAP, reported by the cc2 seat in the free panel of 2026-09-30 and left
# unaddressed until now: confinement was ASYMMETRIC ACROSS TOOLS. `--allowedTools`
# withholds Write and Edit, so those are prevented; a shell write through Bash is
# not, and Bash cannot be withheld because every STEM tool the seats are required
# to use runs through it. This module's own header says so -- "The seat wrote
# anyway, through Bash, which no tool-list can restrain" -- and answered with
# position plus detection: a COPY so relative paths are harmless, and a
# before/after fingerprint so an absolute-path write is caught afterwards.
#
# Detection is not prevention, and the founder's rule is prevention: "none of the
# models ... should ever be able to reach the real repo, let alone edit it".
#
# WHAT THIS ADDS: a macOS kernel sandbox profile that DENIES WRITES to the
# canonical tree for the seat process and everything it spawns, including a shell
# redirection, which is precisely what no tool-list can reach.
#
# MEASURED 2026-10-01 against the real canonical path, 6 properties:
#   write inside the sandbox copy        ALLOWED
#   `echo > <canonical>/new`             DENIED, file not created
#   `echo >> <canonical>/README.md`      DENIED
#   `git -C <canonical> config --local`  DENIED, "could not lock config file"
#   reading the canonical tree           ALLOWED  (a seat must read source)
#   python3 with sympy, and HOME writes  ALLOWED  (STEM tools stay primary)
#
# A TARGETED DENY, NOT A GLOBAL ONE, and the choice is deliberate. A profile that
# denied all writes and allow-listed the sandbox also broke the CLI's own state
# and cache directories, so it would have traded a confinement gap for a dead
# seat. Denying exactly the canonical subpath is the smallest rule that closes
# the founder's stated hole, and `control_plane_fingerprint` already covers the
# home directory by detection.
#
# IT DEGRADES BY REPORTING, NEVER BY PRETENDING. On a machine with no
# `sandbox-exec` -- every non-macOS host -- `confine` returns the command
# unchanged and a mechanism string saying so, and the caller records that string.
# The alternative, failing the dispatch, would make the harness unrunnable
# elsewhere; the alternative of silence would let a reader believe a control was
# in force that was not. Same shape as the Wolfram ruling: nobody is compelled to
# have it, and where it exists it is used.
_CONFINE_PROFILE = ".cdsfl_deny_canonical_writes.sb"

#: What `confine` returns when it could not confine. A caller that records this
#: string is recording the ABSENCE of the control, which is the point.
NO_CONFINEMENT = "none: sandbox-exec unavailable"
NOT_CONFINABLE = "none: cwd is inside the canonical tree"
CONFINED = "sandbox-exec: writes to the canonical tree denied"


def _sandbox_exec() -> str | None:
    """The kernel sandbox binary, or None where there is none."""
    return shutil.which("sandbox-exec")


def confinement_profile(repo: Path, where: Path) -> Path:
    """Write the deny-canonical-writes profile into `where`, returning its path.

    Both paths are RESOLVED. `subpath` in a sandbox profile matches the real
    filesystem path, so an unresolved `/var/...` (a symlink to `/private/var`)
    silently matches nothing -- measured while building this, where an
    allow-rule on the unresolved temp path denied the sandbox its own writes.
    """
    real = Path(repo).resolve()
    path = Path(where) / _CONFINE_PROFILE
    rules = ["(version 1)", "(allow default)",
             f'(deny file-write* (subpath "{real}"))']
    rules += _control_plane_denies()
    path.write_text("\n".join(rules) + "\n", encoding="utf-8")
    return path


#: The surfaces under the operator's config that a LATER session EXECUTES.
#: Everything else there is state the CLI must keep writing.
_EXECUTED_SURFACES = ("hooks", "plugins", "scheduled-tasks", "commands", "agents")
_EXECUTED_FILES = ("settings.json", "CLAUDE.md", "mcp_settings.json")


def _control_plane_denies() -> list:
    """Deny the config surfaces a later session would EXECUTE.

    FOUND BY THE cc2 SEAT, 2026-10-01, running under this very profile and
    attacking it: *"`~/.claude` is writable. A seat cannot write the repo, but it
    can write something the operator's NEXT session executes with full rights.
    The deny-list covers the artefact and not the agent that edits it."* It
    demonstrated the write and removed the file.

    THAT IS A PERSISTENCE ROUTE INTO THE REPO BY PROXY, and it defeats the
    founder's rule -- *"none of the models ... should ever be able to reach the
    real repo, let alone edit it"* -- without ever touching the repo.

    WHY THIS IS SURGICAL AND NOT A BLANKET DENY ON `~/.claude`. A blanket deny
    was measured as breaking the CLI's own state when the repo profile was first
    built, which would trade a confinement gap for a dead seat. Measured on this
    machine, the directory holds BOTH kinds: `hooks/`, `settings.json`,
    `CLAUDE.md`, `mcp_settings.json`, `plugins/` and `scheduled-tasks/` are read
    and EXECUTED by a later session, while `cache/`, `sessions/`, `projects/`,
    `file-history/`, `debug/` and `history.jsonl` are state a running seat
    writes. Only the first group is denied.

    BOTH PATHS ARE DENIED. `~/.claude` is a symlink into iCloud here, and a
    sandbox profile matches the REAL path, so the resolved target is the one
    that binds; the symlink path is listed too so the rule still holds on a
    machine where it is a real directory.
    """
    import os

    home = Path(os.path.expanduser("~"))
    roots = {home / ".claude"}
    try:
        roots.add((home / ".claude").resolve())
    except OSError:                                           # pragma: no cover
        pass
    out = []
    for root in sorted(str(r) for r in roots):
        for d in _EXECUTED_SURFACES:
            out.append(f'(deny file-write* (subpath "{root}/{d}"))')
        for f in _EXECUTED_FILES:
            out.append(f'(deny file-write* (literal "{root}/{f}"))')
    return out


def confine(cmd, repo: Path, cwd: "Path | str | None") -> tuple[list, str]:
    """Wrap `cmd` so it cannot WRITE into `repo`. Returns (argv, mechanism).

    `mechanism` is always a sentence a report can carry verbatim, so whether the
    control was in force is recorded rather than assumed. The command is
    returned unchanged whenever it cannot be applied.
    """
    argv = list(cmd)
    if cwd is None:
        return argv, NOT_CONFINABLE
    real_repo, real_cwd = Path(repo).resolve(), Path(cwd).resolve()
    # A cwd INSIDE the canonical tree cannot be confined by this rule: the deny
    # would also refuse the seat its own working directory. `.claude/worktrees`
    # is the live example. Reported, not silently skipped.
    if real_cwd == real_repo or real_repo in real_cwd.parents:
        return argv, NOT_CONFINABLE
    binary = _sandbox_exec()
    if not binary:
        return argv, NO_CONFINEMENT
    try:
        profile = confinement_profile(real_repo, real_cwd)
    except OSError as exc:                                    # noqa: BLE001
        return argv, f"none: profile not written ({exc})"
    return [binary, "-f", str(profile), *argv], CONFINED


# ═════════════════════════════════════════════════════════════════════════════
# SEAT EVIDENCE REACHES A CLONE, added 2026-10-01 on the founder's ruling that a
# recurring fault be repaired rather than re-reported.
#
# THE FAULT. A harvest lands under `bench/logs/<run>/.../files/<rel>`, and
# `.gitignore:48` ignores `bench/logs/**`. So EVERY seat-written file is
# invisible to git by construction. Measured by
# `scripts/seat_evidence_is_gitignored_2026-09-30.py`, which decides each case
# by CALLING `git check-ignore` and `git ls-files` rather than reading the
# ignore file: 251 seat `.py` files across 22 panel rounds, 251 of 251 = 100%
# ignored, and 46 of 251 = 18.3267% UNPRESERVED, Wilson [14.0302%, 23.5781%] --
# existing nowhere a clone could reach. 11 rounds have stranded evidence.
#
# WHY IT MATTERS BEYOND TIDINESS. `measured-rate-travels-with-its-script` says a
# rate may be cited only if the script that produced it is committed alongside
# it. A producer in a gitignored directory is that rule's own defect wearing a
# filename: `scripts/panel_figure_provenance_2026-09-20.py` names harvest paths
# as the producer of published figures, so in a fresh clone those producers are
# simply absent. 12 scripts and 2 design notes were rescued BY HAND on
# 2026-09-30, which is exactly the manual step this replaces.
#
# WHY NOT JUST UN-IGNORE THE HARVEST. That was tried and reverted for cause: the
# harvest also holds copies of files ALREADY TRACKED at their canonical paths,
# and un-ignoring it staged 20 byte-identical duplicates totalling 47 MB while
# still leaving the unique evidence out. 144 of the 251 are seat EDITS to
# tracked files, where the canonical file already reaches a clone and only the
# diff is new -- and `changes.diff` already carries that. So only the files with
# NO tracked counterpart are copied out, which is the set that is actually lost.
#
# `.scratch/` IS DELIBERATELY NOT PRESERVED. The stranding measurement calls it
# "the only group that SHOULD be unpreserved": a seat's scratch space is working
# residue, not evidence.
_PRESERVE_SUFFIXES = (".py", ".md")
_NO_PRESERVE_PARTS = (".scratch", "__pycache__", ".git")

#: Where preserved evidence lands. Inside `experimental_notes/` because that
#: tree is tracked and is already where this project keeps its record.
SEAT_EVIDENCE_DIR = Path("experimental_notes") / "seat_evidence"


def _harvest_identity(dest: Path, repo: Path) -> tuple[str, str]:
    """(round, seat) for a harvest destination, derived from its position.

    Derived rather than passed, for the reason `_run_log_dir` gives: the 3
    harvest call sites have different depths and a signature change would have
    to reach all 3. The run directory is the ancestor sitting directly inside a
    directory named `logs`; the seat is whatever lies between it and `dest`.
    """
    dest = Path(dest).resolve()
    parts = dest.parts
    run = seat = ""
    for i, part in enumerate(parts[:-1]):
        if part == "logs" and i + 1 < len(parts):
            run = parts[i + 1]
            tail = [p for p in parts[i + 2:]
                    if not p.startswith("attempt-")
                    and p not in ("sandbox_harvest", "worktree_harvest",
                                  "panel_worktree_harvest", "files")]
            seat = tail[0] if tail else "seat"
            break
    return run or dest.parent.name, seat or "seat"


def _should_preserve(rel: str) -> bool:
    p = Path(rel)
    if p.suffix not in _PRESERVE_SUFFIXES:
        return False
    return not any(part in _NO_PRESERVE_PARTS for part in p.parts)


def preserve_seat_evidence(dest: Path, repo: Path) -> dict:
    """Copy harvested seat files that NO tracked file corresponds to into the
    tracked tree, so a clone can reach them.

    Returns a manifest. Never raises: a preservation failure must not fail a
    harvest, and must not be silent either -- every skip and every error is
    named in the returned dict.
    """
    dest, repo = Path(dest), Path(repo)
    files_dir = dest / "files"
    out = {"preserved": [], "already_tracked": [], "skipped": [],
           "failed": [], "dir": "", "round": "", "seat": ""}
    if not files_dir.is_dir():
        return out
    run, seat = _harvest_identity(dest, repo)
    out["round"], out["seat"] = run, seat
    target_root = repo / SEAT_EVIDENCE_DIR / run / seat
    for src in sorted(files_dir.rglob("*")):
        if not src.is_file():
            continue
        rel = src.relative_to(files_dir).as_posix()
        if not _should_preserve(rel):
            out["skipped"].append(rel)
            continue
        # A file that already exists at its canonical path reaches a clone
        # without this; the harvest's `changes.diff` carries what the seat
        # altered. Copying it out again is the 47 MB of duplicates.
        if (repo / rel).is_file():
            out["already_tracked"].append(rel)
            continue
        try:
            target = target_root / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            body = src.read_bytes()
            digest = hashlib.sha256(body).hexdigest()
            # PROVENANCE AT SOURCE, so the file says where it came from even if
            # it is read on its own. The seat's own sha256 is recorded BEFORE
            # the header is prepended, so byte-identity with the harvest copy
            # stays checkable afterwards.
            # THE HARVEST PATH IS DELIBERATELY NOT CITED, corrected 2026-10-01.
            #
            # This header first read "Harvested from <absolute path under
            # bench/logs/...>, which `.gitignore` places outside version
            # control" -- and `test_cited_evidence_is_recoverable_2026-09-11`
            # caught it on the first live round: 11 preserved files cited 11
            # paths a reader cannot reach, taking the unrecoverable-citation
            # ratchet from 20 to 25. The header was announcing its own defect
            # in the same sentence.
            #
            # The round and the seat above identify the origin and ARE
            # reachable, and the sha256 pins the bytes, so naming the ignored
            # path added nothing a reader could use.
            header = (
                f"# PRESERVED SEAT EVIDENCE. Written by seat {seat!r} during "
                f"panel round {run!r}, at the path shown above.\n"
                f"# Rescued from that round's sandbox harvest, which "
                f"`.gitignore` keeps out of version control; the harvest path "
                f"is NOT cited here because a citation a reader cannot follow "
                f"is not evidence.\n"
                f"# sha256 of the seat's original, before this header: {digest}\n"
                f"# Copied by bench/panel_sandbox.py:preserve_seat_evidence. "
                f"NOT edited.\n"
            )
            if src.suffix == ".md":
                header = header.replace("# ", "<!-- ", 1).rstrip("\n") + " -->\n"
            target.write_bytes(header.encode("utf-8") + body)
            out["preserved"].append({"rel": rel, "sha256": digest,
                                     "path": str(target.relative_to(repo))})
        except OSError as exc:                                  # noqa: PERF203
            out["failed"].append({"path": rel, "error": str(exc)})
    if out["preserved"]:
        out["dir"] = str(target_root.relative_to(repo))
        try:
            man = target_root / "PROVENANCE.json"
            man.write_text(json.dumps(
                {"round": run, "seat": seat,
                 "harvest": str(dest),
                 "preserved": out["preserved"]}, indent=2), encoding="utf-8")
        except OSError as exc:                                  # noqa: BLE001
            out["failed"].append({"path": "PROVENANCE.json", "error": str(exc)})
    return out
