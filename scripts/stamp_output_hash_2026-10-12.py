#!/usr/bin/env python3
"""Give every delivered note and TTS file its own verifiable hash, and track it.

HIS ORDER, 2026-10-12: *"As for giving each text/tts output its own hash value. Do it.
It will allow you to track these outputs more exactly going forward."*

TWO JUDGEMENTS HE ASKED ME TO MAKE RATHER THAN PUT TO HIM
----------------------------------------------------------
**The FILENAME stays human-readable.** `Morning_Report_2026-10-12.txt` tells him what a
file is; `Morning_Report_a3f9b2c1.txt` does not, and he reads these by speech. The hash
goes INSIDE the file and into a ledger, which is what "track these outputs more exactly"
actually needs.

**The hash EXCLUDES its own stamp line.** A hash written into the file it describes would
change the file and invalidate itself. So the digest is taken over the content with any
existing stamp line removed, which makes it stable, recomputable and verifiable by anyone.

WHAT IT GIVES HIM. A short digest he can quote back ("the report with hash 7b2f...") that
names one exact version of one file; `--verify` says whether the file on disk is still
that version; and `experimental_notes/data/output_hashes.json` records digest, path, byte
count and the commit it was stamped at, so a delivered output can always be identified
after the fact.

A --help COSTS NOTHING, and an unknown flag EXITS 2 -- the defect found in 4 scripts in
one day, fixed here by calling the shared helper rather than a 5th hand-rolled block.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
LEDGER = REPO / "experimental_notes" / "data" / "output_hashes.json"
STAMP_RE = re.compile(r"^Output hash: [0-9a-f]{12} .*$", re.M)
DIGEST_CHARS = 12


def _answer_help(doc, path, args):
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    from _cli_help import answer_help
    answer_help(doc, path, list(args), takes_no_arguments=False)


def strip_stamp(text: str) -> str:
    """The content WITHOUT its stamp line, which is what the digest is taken over."""
    return STAMP_RE.sub("", text).rstrip("\n") + "\n"


def digest(text: str) -> str:
    return hashlib.sha256(strip_stamp(text).encode("utf-8")).hexdigest()[:DIGEST_CHARS]


def head_sha() -> str:
    r = subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                       cwd=str(REPO), capture_output=True, text=True)
    return (r.stdout or "").strip() or "unknown"


def stamp(path: pathlib.Path) -> tuple[str, bool]:
    """Write the stamp line. Returns (digest, changed)."""
    text = path.read_text(encoding="utf-8")
    d = digest(text)
    line = (f"Output hash: {d} ({path.name}, {len(strip_stamp(text).encode())} bytes, "
            f"stamped at commit {head_sha()})")
    body = strip_stamp(text)
    new = body + "\n" + line + "\n"
    changed = new != text
    if changed:
        path.write_text(new, encoding="utf-8")
    return d, changed


def verify(path: pathlib.Path) -> tuple[str, str | None]:
    """Returns (recomputed, stamped_or_None)."""
    text = path.read_text(encoding="utf-8")
    m = STAMP_RE.search(text)
    stamped = m.group(0).split()[2] if m else None
    return digest(text), stamped


def record(entries: list[dict]) -> None:
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    data = json.loads(LEDGER.read_text(encoding="utf-8")) if LEDGER.is_file() else {}
    rows = data.get("outputs", [])
    known = {(r["digest"], r["path"]) for r in rows}
    for e in entries:
        if (e["digest"], e["path"]) not in known:
            rows.append(e)
    data["_what_this_is"] = (
        "Every delivered note and TTS file, by its own content hash. The digest EXCLUDES "
        "the stamp line inside the file, so it is stable and recomputable. His order of "
        "2026-10-12: give each output its own hash value, to track them exactly.")
    data["outputs"] = rows
    LEDGER.write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8")


def main(argv: list[str]) -> int:
    _answer_help(__doc__, __file__, argv[1:])
    # AN UNRECOGNISED FLAG IS A FLAG, NOT A FILENAME. `takes_no_arguments=False`
    # disables the shared helper's own refusal because this script takes paths, so the
    # refusal is made here instead -- otherwise `--bogus` is reported as a missing file,
    # which is an unrecognised argument reading as an ordinary failure.
    KNOWN = {"--verify"}
    unknown = [a for a in argv[1:] if a.startswith("-") and a not in KNOWN]
    if unknown:
        print(f"unrecognised argument(s): {' '.join(unknown)}")
        print(f"usage: {pathlib.Path(argv[0]).name} [--verify] FILE [FILE ...]")
        return 2
    args = [a for a in argv[1:] if a != "--verify"]
    checking = "--verify" in argv[1:]
    if not args:
        print("give one or more file paths to stamp, or --verify with them")
        return 2
    entries, bad = [], 0
    for a in args:
        p = pathlib.Path(a).expanduser()
        if not p.is_file():
            print(f"  MISSING {p}")
            bad += 1
            continue
        if checking:
            got, was = verify(p)
            ok = (was is not None and got == was)
            print(f"  {'OK     ' if ok else 'CHANGED'} {got} "
                  f"{'(stamped ' + str(was) + ')' if was != got else ''} {p.name}")
            bad += 0 if ok else 1
        else:
            d, changed = stamp(p)
            print(f"  {d}  {'stamped' if changed else 'already current'}  {p.name}")
            entries.append({"digest": d, "path": str(p),
                            "bytes": len(strip_stamp(p.read_text(encoding='utf-8')).encode()),
                            "commit": head_sha(),
                            "stamped": dt.datetime.now().astimezone().isoformat(timespec="seconds")})
    if entries:
        record(entries)
        print(f"  recorded {len(entries)} output(s) in {LEDGER.relative_to(REPO)}")
    return 3 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
