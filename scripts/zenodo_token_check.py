#!/usr/bin/env python3
"""Task Z1: is the Zenodo token in `.env` valid? Answers without printing it.

He asked on 2026-08-19, verbatim: "You need to give me clear instructions how to
do this!" The instructions were never supplied and the token has not been
rotated. This is the half a machine can do: tell him whether the token in `.env`
works, before and after he replaces it, so the rotation is confirmed rather than
assumed.

IT NEVER PRINTS THE TOKEN. Not in output, not in an error, not in a traceback.
It reports the length and the first 4 characters only, which is enough to see
that a paste landed and not enough to use. A rotation tool that echoes the
credential it is rotating would be worse than no tool.

IT MAKES ONE NETWORK CALL, to `zenodo.org`, and only when asked with `--live`.
The default is offline: it reads `.env`, reports the shape, and stops. This
project's suite runs under `--netguard-strict`, and a script that reaches the
network by default cannot be run inside it.
"""
from __future__ import annotations

import argparse
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
ENV = REPO / ".env"
KEY = "ZENODO_TOKEN"


def read_token() -> str | None:
    if not ENV.is_file():
        return None
    for line in ENV.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if line.startswith("export "):
            line = line[7:]
        if line.startswith(f"{KEY}="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def shape(tok: str) -> str:
    return (f"{len(tok)} characters, starts {tok[:4]}..., "
            f"alphanumeric: {tok.isalnum()}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--live", action="store_true",
                    help="make one call to zenodo.org to test the token")
    a = ap.parse_args()

    tok = read_token()
    if tok is None:
        print(f"{KEY} is not in {ENV}. Nothing to check.")
        return 2
    print(f"{KEY} found in .env: {shape(tok)}")
    print(f".env last modified: "
          f"{__import__('datetime').datetime.fromtimestamp(ENV.stat().st_mtime)}")

    # WHO USES IT. Measured rather than assumed: nothing in this repository reads
    # ZENODO_TOKEN, so rotating it cannot break a running process here.
    users = []
    for p in list((REPO / "scripts").glob("*.py")) + list((REPO / "bench").glob("*.py")):
        try:
            if KEY in p.read_text(encoding="utf-8", errors="replace"):
                users.append(str(p.relative_to(REPO)))
        except OSError:
            continue
    users = [u for u in users if not u.endswith("zenodo_token_check.py")]
    print(f"files in this repository that read {KEY}: {len(users)} {users}")
    if not users:
        print("  -> nothing here uses it, so rotating it breaks nothing locally.")

    if not a.live:
        print("\noffline check only. Add --live to test the token against "
              "zenodo.org.")
        return 0

    import json
    import urllib.error
    import urllib.request
    req = urllib.request.Request(
        "https://zenodo.org/api/deposit/depositions",
        headers={"Authorization": f"Bearer {tok}"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            # READ THE WHOLE BODY. This was `r.read(2000)` until 2026-09-19, and
            # the real response is 3,718 bytes, so it parsed a TRUNCATED array,
            # raised JSONDecodeError, and the catch-all below reported that as
            # "could not reach zenodo.org" -- on a run where the server answered
            # HTTP 200 and the token was perfectly good. An instrument that
            # truncates its own evidence and then reports the truncation as an
            # outage is the failure class this project exists to catch: a failed
            # measurement described as something it is not.
            body = r.read()
            try:
                parsed = json.loads(body)
                n = len(parsed) if isinstance(parsed, (list, dict)) else "?"
            except ValueError:
                # A 200 we cannot parse is NOT a rejection and NOT an outage.
                print(f"\nLIVE: HTTP {r.status} — the token was ACCEPTED (the "
                      f"server answered), but the {len(body)}-byte body did not "
                      f"parse as JSON. The token is fine; the reader is not.")
                return 4
            print(f"\nLIVE: HTTP {r.status} — the token WORKS. "
                  f"{n} deposition(s) visible.")
            return 0
    except urllib.error.HTTPError as e:
        # The token must not appear in the error either.
        print(f"\nLIVE: HTTP {e.code} — the token was REJECTED."
              f" {'Revoked or wrong.' if e.code in (401, 403) else ''}")
        return 1
    except Exception as e:                                # noqa: BLE001
        print(f"\nLIVE: could not reach zenodo.org: {type(e).__name__}. "
              f"This says nothing about the token.")
        return 3


if __name__ == "__main__":
    sys.exit(main())
