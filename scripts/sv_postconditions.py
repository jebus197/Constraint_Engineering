#!/usr/bin/env python3
"""What must be TRUE after `sv` has run, executed rather than printed.

FOUNDER, 2026-09-20, verbatim: *"sv should be an entirely mechanical operation.
Yet for several weeks now you keep uncovering issues with it? Can't you devise a
permanent, definitive fix so it can do exactly as it was originally intended to
do, and so that you don't need to keep hand implementing corrections after it
runs?"*

THE MEASUREMENT BEHIND THIS FILE. Since 2026-08-01 the record holds 14 commits
whose subject begins `sv:` and 13 separate commits that REPAIR
`scripts/cdsfl_sv.py` -- a rate of 0.9286 repairs per save. (14 commits touch
the script; the 14th is an 867-file milestone merge that carries it along, and
counting that as a repair would inflate the very rate being established.) The
producing command is committed beside this file as
`scripts/sv_repair_rate_2026-09-20.py`, and it also classifies the 13 and prints
every subject next to its assigned class so the classification can be overruled
by looking. The largest single class, 7 of 13, is 1 shape:

    sv MEASURED something, PRINTED the measurement, and then exited 0 regardless
    of what the measurement said.

`_print_final_state` re-measures the working tree and the remote and prints a
verdict. `_verify_remote_sync` returns a dict naming exactly whether the remote
moved. `main()` reads neither. So a save whose push was refused -- as happened on
2026-09-19, when GitHub's secret scanner rejected the push -- printed its own
refusal and exited 0 anyway, and a human had to notice.

WHAT THIS CHANGES, AND IT IS DELIBERATELY NOT A NEW MEASUREMENT. The readings
sv already takes become a GATE: each one is re-taken here after the commit has
landed, and a failure exits non-zero. The commit is never at risk, because it is
already in the object store before the first check runs; what changes is whether
sv is allowed to call the save a success.

WHAT IT DOES NOT COVER, stated because the other 6 of the 13 repairs are real.
3 were a checker measuring the wrong quantity -- the memory-index audit blind to
15 of 132 entries, the loader's 2 truncation limits with only 1 guarded, and an
over-statement about commissioning. 1 was a Python version floor. 2 remain
unclassified by the producing script, and both are genuine repairs. A
postcondition gate does not reach a checker that is asking the wrong question;
it reaches a checker that asks the right question and is then ignored.

Runnable on its own: `python3 scripts/sv_postconditions.py [--pushed]`.
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

#: The 1 guard whose failure made the suite red immediately after an sv on
#: 2026-09-19: the newest SESSION STATE block in `resources/RECOVERY.md` must
#: name a producer for every suite figure it quotes. It is 1 file and runs in
#: about 1 second, so it is affordable inside sv; the full suite is not.
_RECOVERY_GUARD = "bench/tests/test_recovery_session_state_is_current_2026-09-11.py"

#: Stamped by `update_timestamp`, e.g. `20 September 2026 01:34 BST`. Only this
#: line is checked for a future date. A blanket scan would be wrong: these
#: documents legitimately carry future dates, such as the Wolfram licence
#: expiry of 2026-10-08, and flagging those would be noise, not a finding.
_STAMP = re.compile(r"^Last updated:\s*(\d{1,2} [A-Za-z]+ \d{4} \d{2}:\d{2})", re.M)

_STAMPED = ("resources/ONBOARDING.md", "resources/RECOVERY.md",
            "docs/CURRENT_STATE.md")

#: A tracked file matching any of these is a credential in the history.
#: NARROWER THAN `cdsfl_sv._SENSITIVE_PATTERNS` ON PURPOSE, and the difference is
#: measured: that tuple contains the substrings `secret` and `credentials`, which
#: match 2 tracked files today -- `scripts/gate_environment_secrets_2026-09-17.py`
#: and `bench/tests/test_seat_environment_carries_no_secrets_2026-09-17.py`. Both
#: are guards named after the thing they guard. A predicate that fires on them
#: would be turned off within a week, and a gate that is turned off measures
#: nothing. `.env.example` is the 1 deliberate exception on the other side.
_SECRET_NAMES = re.compile(r"(^|/)(\.env($|\.(?!example$))|scoring\.env$)|\.(key|pem|p12)$")


@dataclass(frozen=True)
class Result:
    name: str
    ok: bool | None          # None == could not be measured; NOT evidence either way
    required: bool
    detail: str

    @property
    def failed(self) -> bool:
        """An unmeasurable REQUIRED check fails.

        The project's own rule, already written into `_print_final_state`: a
        failed check is not evidence the thing worked.
        """
        return self.required and self.ok is not True


def _git(*args: str, root: Path, timeout: int = 30) -> tuple[int, str, str]:
    p = subprocess.run(["git", *args], cwd=root, capture_output=True,
                       text=True, timeout=timeout)
    return p.returncode, p.stdout.strip(), p.stderr.strip()


# ── the checks ───────────────────────────────────────────────────────────

def working_tree_is_clean(root: Path, pushed: bool) -> tuple[bool | None, str]:
    rc, out, err = _git("status", "--porcelain", root=root)
    if rc != 0:
        return None, f"git status failed: {err}"
    if out:
        paths = [line[3:] for line in out.splitlines()]
        shown = paths[:5]
        more = "" if len(paths) <= 5 else f", and {len(paths) - 5} more not shown"
        return False, (f"{len(paths)} path(s) still uncommitted after the save: "
                       + ", ".join(shown) + more)
    return True, "no uncommitted paths"


def head_matches_the_remote(root: Path, pushed: bool) -> tuple[bool | None, str]:
    """Compares LOCAL refs only, and that is the point.

    A successful `git push` updates the remote-tracking ref in this clone; a
    refused push does not. So the comparison needs no network, cannot be
    confounded by an offline machine, and still catches the 2026-09-19 case
    where the push was rejected and sv reported the save complete.
    """
    if not pushed:
        return True, "not a --push run; nothing to compare"
    rc, branch, err = _git("branch", "--show-current", root=root)
    if rc != 0 or not branch:
        return None, f"could not read the branch name: {err or 'detached HEAD'}"
    rc_h, head, _ = _git("rev-parse", "HEAD", root=root)
    rc_r, remote, err_r = _git("rev-parse", f"origin/{branch}", root=root)
    if rc_h != 0:
        return None, "could not read HEAD"
    if rc_r != 0:
        return False, (f"origin/{branch} does not exist in this clone, so the "
                       f"push did not create it: {err_r}")
    if head != remote:
        rc_c, count, _ = _git("rev-list", "--count", f"origin/{branch}..HEAD",
                              root=root)
        ahead = count if rc_c == 0 else "?"
        return False, (f"HEAD is {ahead} commit(s) ahead of origin/{branch}. "
                       f"The push did NOT land.")
    return True, f"origin/{branch} == HEAD ({head[:8]})"


def generated_state_is_committed(root: Path, pushed: bool) -> tuple[bool | None, str]:
    """sv generates `docs/CURRENT_STATE.md`; a save that leaves it out of the
    commit publishes a state file describing the previous save."""
    rel = "docs/CURRENT_STATE.md"
    if not (root / rel).exists():
        return None, f"{rel} is absent from the working tree"
    rc, out, err = _git("diff", "HEAD", "--", rel, root=root)
    if rc != 0:
        return None, f"git diff failed: {err}"
    if out:
        return False, f"{rel} differs from HEAD: sv generated it and did not commit it"
    return True, f"{rel} is identical to HEAD"


def no_stamp_is_in_the_future(root: Path, pushed: bool) -> tuple[bool | None, str]:
    """Catches the 2026-08-26 class: 5 timestamps typed instead of read, 3 of
    them in the future. A stamp 2 minutes ahead is clock skew, not a defect."""
    now = datetime.now() + timedelta(minutes=2)
    seen, offenders = 0, []
    for rel in _STAMPED:
        p = root / rel
        if not p.exists():
            continue
        m = _STAMP.search(p.read_text(encoding="utf-8", errors="replace"))
        if not m:
            continue
        seen += 1
        try:
            when = datetime.strptime(m.group(1), "%d %B %Y %H:%M")
        except ValueError:
            offenders.append(f"{rel}: unparseable stamp {m.group(1)!r}")
            continue
        if when > now:
            offenders.append(f"{rel}: stamped {m.group(1)}, which is in the future")
    if offenders:
        return False, "; ".join(offenders)
    if not seen:
        return None, "no 'Last updated:' line found in any stamped document"
    return True, f"{seen} stamp(s) read, none ahead of the clock"


def no_credential_is_tracked(root: Path, pushed: bool) -> tuple[bool | None, str]:
    """The 2026-09-19 incident: `.env.backup-<timestamp>` was swept into a
    commit by `git add -A` and GitHub's scanner refused the push."""
    rc, out, err = _git("ls-files", root=root, timeout=60)
    if rc != 0:
        return None, f"git ls-files failed: {err}"
    offenders = [f for f in out.splitlines() if _SECRET_NAMES.search(f)]
    if offenders:
        more = "" if len(offenders) <= 5 else f", and {len(offenders) - 5} more not shown"
        return False, (f"{len(offenders)} tracked credential-shaped file(s): "
                       + ", ".join(offenders[:5]) + more)
    return True, f"{len(out.splitlines())} tracked files, none credential-shaped"


def recovery_block_passes_its_own_guard(root: Path, pushed: bool) -> tuple[bool | None, str]:
    """Runs the A23 producer guard against the block sv has just written.

    On 2026-09-19 this is the check that went from green to red BECAUSE of an
    sv: the new SESSION STATE block quoted a suite figure and named nothing
    that produced it, so the sentence recording a green suite is what made the
    suite red. sv wrote the block and did not run the guard over it.
    """
    guard = root / _RECOVERY_GUARD
    if not guard.exists():
        return None, f"{_RECOVERY_GUARD} is not in this clone"
    p = subprocess.run([sys.executable, "-m", "pytest", str(guard), "-q",
                        "--no-header", "-p", "no:cacheprovider"],
                       cwd=root, capture_output=True, text=True, timeout=300)
    tail = [ln for ln in p.stdout.strip().splitlines() if ln.strip()]
    summary = tail[-1] if tail else "(no output)"
    if p.returncode != 0:
        return False, f"the guard is RED after this save: {summary}"
    return True, summary


#: name -> (callable, required). Required checks gate the exit code.
CHECKS: tuple[tuple[str, object, bool], ...] = (
    ("working tree clean",              working_tree_is_clean,             True),
    ("HEAD == origin",                  head_matches_the_remote,           True),
    ("generated state committed",       generated_state_is_committed,      True),
    ("no stamp in the future",          no_stamp_is_in_the_future,         True),
    ("no credential tracked",           no_credential_is_tracked,          True),
    ("RECOVERY block passes A23",       recovery_block_passes_its_own_guard, True),
)


def check_all(root: Path | None = None, *, pushed: bool = False) -> list[Result]:
    root = root or REPO
    out = []
    for name, fn, required in CHECKS:
        try:
            ok, detail = fn(root, pushed)
        except Exception as exc:                                   # noqa: BLE001
            ok, detail = None, f"the check itself raised {type(exc).__name__}: {exc}"
        out.append(Result(name=name, ok=ok, required=required, detail=detail))
    return out


def report(results: list[Result]) -> str:
    bar = "=" * 74
    lines = [bar, "  SV POSTCONDITIONS — re-measured after the save:"]
    for r in results:
        mark = "PASS" if r.ok is True else ("FAIL" if r.ok is False else "NOT MEASURED")
        lines.append(f"    [{mark:>12}]  {r.name}: {r.detail}")
    bad = [r for r in results if r.failed]
    if bad:
        lines.append("")
        lines.append(f"  {len(bad)} REQUIRED postcondition(s) did not hold. The commit "
                     "is safe and already in the object store;")
        lines.append("  what is NOT established is that the save did what it reports.")
    lines.append(bar)
    return "\n".join(lines)


def main(argv: list | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--pushed", action="store_true",
                    help="the save included a push, so require HEAD == origin")
    ap.add_argument("--root", type=Path, default=REPO)
    a = ap.parse_args(argv)
    results = check_all(a.root, pushed=a.pushed)
    print(report(results))
    return 1 if any(r.failed for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
