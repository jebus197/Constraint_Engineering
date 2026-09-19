#!/usr/bin/env python3
"""Rotate ZENODO_TOKEN in .env without the value ever being echoed, logged or shell-historied.

TASK Z1. The founder, 2026-08-19: *"You need to give me clear instructions how to
do this!"* A note was delivered on 2026-09-10 and the token still has not moved:
`.env` was last written 2026-08-16, which is 34 days at the time of writing. The
note asked him to hand-edit the file. THAT IS THE STEP WORTH REMOVING, because
`.env` holds 10 credentials on 10 lines with 6 comment lines between them, and a
hand-edit puts the other 9 at risk to save nothing.

WHY A PROMPT RATHER THAN AN ARGUMENT. A token passed as `--token abc` lands in
shell history, in `ps` output while it runs, and in any transcript of the
session. `getpass` takes it from the terminal with echo off, so it exists only in
this process's memory and in the file it is written to.

WHAT IT GUARANTEES, each asserted by bench/tests/test_zenodo_rotate_2026-09-19.py:
  * the token is NEVER printed -- not on success, not in an error, not in a
    traceback (the value is never interpolated into any message);
  * ONLY the ZENODO_TOKEN line changes: every other line is compared by digest
    before and after, and a mismatch restores the backup and exits non-zero;
  * the line keeps its original shape, so an `export `-prefixed or indented
    assignment stays that way;
  * a timestamped backup is written BEFORE the file is touched;
  * it is OFFLINE -- rotating never contacts Zenodo. Use
    `scripts/zenodo_token_check.py --live` to test the new value.

Read-only unless `--rotate` is given.
"""
from __future__ import annotations

import argparse
import datetime as dt
import getpass
import hashlib
import os
import pathlib
import re
import shutil
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
ENV = REPO / ".env"
KEY = "ZENODO_TOKEN"
#: Matches the assignment whatever its shape: `KEY=`, `export KEY=`, indented.
LINE = re.compile(rf"^(\s*(?:export\s+)?{KEY}\s*=)(.*)$")
MIN_LEN = 20


def shape(tok: str) -> str:
    """Enough to confirm a paste landed; not enough to use. Never the whole value."""
    return f"{len(tok)} characters, starts {tok[:4]}..., alphanumeric: {tok.isalnum()}"


def others_digest(text: str) -> str:
    """SHA-256 of every line EXCEPT the token's, so 'nothing else moved' is provable."""
    keep = [ln for ln in text.splitlines() if not LINE.match(ln)]
    return hashlib.sha256("\n".join(keep).encode("utf-8")).hexdigest()


def key_names(text: str) -> list:
    out = []
    for ln in text.splitlines():
        m = re.match(r"^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=", ln)
        if m:
            out.append(m.group(1))
    return sorted(out)


def report(text: str) -> None:
    names = key_names(text)
    cur = next((m.group(2).strip().strip('"').strip("'")
                for m in (LINE.match(ln) for ln in text.splitlines()) if m), None)
    print(f"  file      : {ENV}")
    print(f"  keys      : {len(names)} -> {', '.join(names)}")
    print(f"  {KEY}: {shape(cur) if cur else 'ABSENT'}")
    print(f"  other keys: digest {others_digest(text)[:16]}...")


def rotate(new: str, text: str) -> str:
    """Return `text` with only the token line's VALUE replaced."""
    out, done = [], False
    for ln in text.splitlines(keepends=True):
        m = LINE.match(ln.rstrip("\n"))
        if m and not done:
            nl = "\n" if ln.endswith("\n") else ""
            out.append(f"{m.group(1)}{new}{nl}")
            done = True
        else:
            out.append(ln)
    if not done:
        raise SystemExit(f"{KEY} is not in {ENV}: refusing to invent a line.")
    return "".join(out)


def main(argv: list | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--rotate", action="store_true",
                    help="prompt for the new token and write it (the only writing mode)")
    a = ap.parse_args(argv)

    if not ENV.is_file():
        print(f"no {ENV}. Nothing to rotate.")
        return 2
    text = ENV.read_text(encoding="utf-8")
    stamp = dt.datetime.fromtimestamp(ENV.stat().st_mtime).isoformat(timespec="seconds")
    print(f"BEFORE (last written {stamp}):")
    report(text)

    if not a.rotate:
        print("\nread-only. Add --rotate to replace the value. Nothing was changed.")
        return 0

    before_digest, before_keys = others_digest(text), key_names(text)
    print(f"\nPaste the NEW token from zenodo.org. It will not be shown as you type.")
    new = getpass.getpass("  new ZENODO_TOKEN: ").strip()
    if len(new) < MIN_LEN or not new.isalnum():
        print(f"\nREFUSED: that is {len(new)} characters"
              f"{' and not alphanumeric' if not new.isalnum() else ''}. "
              f"A Zenodo token is a long alphanumeric string. Nothing was written.")
        return 3

    backup = ENV.with_name(f".env.backup-{dt.datetime.now():%Y%m%d-%H%M%S}")
    shutil.copy2(ENV, backup)
    os.chmod(backup, 0o600)
    print(f"\n  backup    : {backup}")

    updated = rotate(new, text)
    tmp = ENV.with_suffix(".env.tmp")
    tmp.write_text(updated, encoding="utf-8")
    os.chmod(tmp, ENV.stat().st_mode & 0o777)
    tmp.replace(ENV)

    after = ENV.read_text(encoding="utf-8")
    if others_digest(after) != before_digest or key_names(after) != before_keys:
        shutil.copy2(backup, ENV)
        print("  FAILED: another line changed. The backup has been restored and "
              "nothing is lost. Nothing about your other 9 credentials was altered.")
        return 4

    print("AFTER:")
    report(after)
    print("\n  the other keys are byte-identical (same digest above).")
    print(f"  now test it:  python3 scripts/zenodo_token_check.py --live")
    print(f"  if it fails:  cp {backup.name} .env")
    return 0


if __name__ == "__main__":
    sys.exit(main())
