#!/usr/bin/env python3
"""Record the shape of every file in his Responses folder, so a silent loss shows.

WHY THIS EXISTS, measured 2026-10-19/20. 12 of his annotations on
`TASK_LIST_48_Hours_And_Rulings_2026-10-17.txt` stopped existing. The verdicts
recorded against that file on 2026-10-17 name anchors at lines 108, 114, 116 and
120; the file is 108 lines long. The text of all 12 is absent from the file body
as well as from its line starts, and absent from all 682 of his live annotations.

THE AGENT WAS ALMOST CERTAINLY MICROSOFT WORD, and the evidence is 3-fold:
  1. `~$SK_LIST_48_Hours_And_Rulings_2026-10-17.txt`, a Word owner file, existed
     at 01:08:24 on 2026-10-20 and the document's mtime moved to 01:09:04.
  2. EVERY one of his .txt files is CR-only with 0 LF and 0 CRLF, and cp1252
     rather than UTF-8. No modern editor writes classic-Mac line endings; Word's
     "Macintosh Text" save does. So Word rewrites these files whenever it saves.
  3. He states he was not at the machine when the 2026-10-19T07:19:02 change
     happened, and 0 of the 22 committed Python files that reference the folder
     contain a write, delete or move call.

He had already named this cause and it was wrongly discounted: "You said it was
something to do with my using Word. Which you then subsequently discounted, and
blamed your own parser."

WHAT THIS RECORDS AND WHY THOSE FIELDS. A hash alone says a file changed, which
Word does on every save, so a hash alone cries wolf. The load-bearing number is
the ANNOTATION COUNT: his annotations are the primary record, and a drop in that
count is a loss of his words regardless of what else moved. Size and line count
are kept beside it because they separate a re-encoding from a truncation.

Run it to refresh:  python3 scripts/his_responses_manifest_2026-10-20.py --write
Run it to check:    python3 scripts/his_responses_manifest_2026-10-20.py
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "experimental_notes" / "data" / "his_responses_manifest.json"
READER = ROOT / "scripts" / "read_founder_responses_2026-10-11.py"


def _reader():
    spec = importlib.util.spec_from_file_location("_rfr", READER)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_rfr"] = mod
    spec.loader.exec_module(mod)
    return mod


def shape() -> dict:
    """The current shape of every annotated file, keyed by name."""
    r = _reader()
    counts: dict[str, int] = {}
    for a in r.annotations():
        counts[pathlib.Path(str(a["file"])).name] = counts.get(
            pathlib.Path(str(a["file"])).name, 0) + 1

    out: dict[str, dict] = {}
    for p in sorted(r.RESPONSES.glob("*")):
        if not p.is_file() or not r.is_a_response_file(p):
            continue
        raw = p.read_bytes()
        try:
            text = raw.decode("utf-8")
            enc = "utf-8"
        except UnicodeDecodeError:
            text = r.decode_bytes(raw) if hasattr(r, "decode_bytes") else raw.decode("cp1252")
            enc = "legacy"
        out[p.name] = {
            "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "lines": len(text.splitlines()),
            "annotations": counts.get(p.name, 0),
            "encoding": enc,
            # CR-only is the Word signature; recorded so the cause stays visible.
            "cr_only": raw.count(b"\r") > 0 and raw.count(b"\n") == 0,
        }
    return out


def load() -> dict:
    if not OUT.is_file():
        return {}
    return json.loads(OUT.read_text(encoding="utf-8")).get("files", {})


def losses(previous: dict, current: dict) -> list[str]:
    """Only a LOSS is a finding. He adds annotations constantly; that is not one."""
    bad = []
    for name, was in previous.items():
        now = current.get(name)
        if now is None:
            bad.append(f"{name}: FILE HAS VANISHED (held {was['annotations']} annotation(s))")
            continue
        if now["annotations"] < was["annotations"]:
            bad.append(
                f"{name}: annotations fell from {was['annotations']} to "
                f"{now['annotations']} -- {was['annotations'] - now['annotations']} "
                f"of his annotations are gone")
    return bad


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--write", action="store_true",
                    help="refresh the manifest to the current shape")
    args = ap.parse_args()

    cur = shape()
    prev = load()
    bad = losses(prev, cur)

    tot_ann = sum(f["annotations"] for f in cur.values())
    cr = sum(1 for f in cur.values() if f["cr_only"])
    print(f"annotated files : {len(cur)}")
    print(f"annotations     : {tot_ann}")
    print(f"CR-only (Word)  : {cr} of {len(cur)}  <- rewritten by Word on save")
    if prev:
        print(f"manifest held   : {len(prev)} file(s), "
              f"{sum(f['annotations'] for f in prev.values())} annotation(s)")

    if bad:
        print("\nLOSSES:")
        for b in bad:
            print(f"  {b}")
    elif prev:
        print("\nNo file has lost an annotation since the manifest was taken.")

    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps({"files": cur}, indent=2, sort_keys=True) + "\n",
                       encoding="utf-8")
        print(f"\nwritten: {OUT.relative_to(ROOT)}")
        return 0
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
