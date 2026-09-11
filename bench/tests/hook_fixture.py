"""Install the real pre-commit hook into a scratch repository, with what it needs.

WHY THIS EXISTS, and the reason is written in one of its own callers.
`test_note_lint_guard_2026-09-09.py`'s fixture carries this note:

    "THE GUARD LIST IS READ OUT OF THE HOOK, NOT TYPED HERE. It was typed, as 4
     names, and the hook has since grown to 6 ... This is the same defect as
     everything else found on 2026-09-10: a list written down in 2 places, where
     one place moved."

On 2026-09-11 the hook grew a SIBLING FILE -- `hooks/stage0_restage.sh`, which it
sources and REFUSES without -- and the identical defect happened again one level
out. Both scratch fixtures copied `hooks/pre-commit` and nothing beside it, so
the hook correctly refused every commit and 13 tests went red across 2 files:
3 in `test_precommit_guard_2026-09-09.py` and 10 here. The hook was right and
both fixtures were stale.

A GLOB CANNOT GO STALE THE WAY A LIST CAN, and there is now 1 glob rather than 2.
Anything added beside the hook is installed by both callers automatically.
"""
from __future__ import annotations

import os
import shutil
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
HOOKS = REPO / "hooks"


def install_hook(dest_hooks: Path, hook_name: str = "pre-commit") -> list[str]:
    """Copy the hook and every shell library beside it into `dest_hooks`.

    Returns the names installed, so a caller can assert the set is not empty --
    an install that silently copied nothing would leave the scratch repository
    with no hook at all and every "the hook refused" test would pass vacuously.
    """
    dest_hooks.mkdir(parents=True, exist_ok=True)
    installed = []
    src_hook = HOOKS / hook_name
    shutil.copy2(src_hook, dest_hooks / hook_name)
    os.chmod(dest_hooks / hook_name, 0o755)
    installed.append(hook_name)
    for lib in sorted(HOOKS.glob("*.sh")):
        shutil.copy2(lib, dest_hooks / lib.name)
        installed.append(lib.name)
    return installed
