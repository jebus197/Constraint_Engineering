#!/usr/bin/env python3
"""Does the credential store's guard actually bite? Revert each property and look.

★ WHY. A guard that passes proves nothing on its own: it may be asserting
something the code could not violate anyway. The only evidence that a guard
catches a defect is that REMOVING the defence turns it red. 38 tests passing in
`bench/tests/test_the_credential_store_holds_nothing_in_plaintext_2026-11-10.py`
is a claim; this script is the measurement behind it.

THE 8 MUTATIONS BELOW ARE NOT ARBITRARY. Each one removes a DIFFERENT security
property of `bench/credential_store.py`, and each names the test that must go
red. A mutation that leaves the whole guard green is reported as an ESCAPE, which
means the guard has a hole and the hole is the finding.

★ THE ANCHORS ARE DERIVED FROM THE SUBJECT, NOT TYPED FROM EXPECTATION. Every
mutation asserts its own anchor is present in the live file before editing, and
reports a SKIP rather than a pass if the code has moved on. A harness whose
anchor has rotted silently measures nothing, which this project has already paid
for once.

★ IT RESTORES WHAT IT FOUND, BYTE FOR BYTE, and that is not the same as checking
out from git. The working copy may hold uncommitted work -- it did when this was
written -- so the original BYTES are held in memory and written back in a
`finally`, never recovered with `git checkout --`, which would silently discard
the subject.

Usage:
    python3 scripts/the_credential_store_mutations_2026-11-10.py
    python3 scripts/the_credential_store_mutations_2026-11-10.py --only aad

`--help` runs no test and edits nothing.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SUBJECT = ROOT / "bench" / "credential_store.py"
GUARD = ROOT / "bench" / "tests" / \
    "test_the_credential_store_holds_nothing_in_plaintext_2026-11-10.py"

#: (key, what is removed, old, new, the test that must go red)
#: A 6th element, when present, is a SECOND (old, new) pair applied in the same
#: mutation. It exists for `aad_both`: mutating only the writer breaks the
#: round-trip, so the guard goes red in its FIXTURE and the downgrade attack is
#: never actually reached. Mutating both sides keeps the store working and
#: isolates the property under test, which is the honest measurement.
#: The last field is a pytest node-id FRAGMENT, run with `-k`, so only the tests
#: that should move are executed. A full guard run per mutation would cost 8
#: times 30 seconds on an 8-core machine that is a fixed resource here.
MUTATIONS = [
    (
        "aad",
        "the envelope is no longer authenticated, so its parameters can be rewritten",
        'ct = AESGCM(key).encrypt(nonce, plain, _aad(env))',
        'ct = AESGCM(key).encrypt(nonce, plain, None)',
        "downgraded_key_derivation or swapped_salt",
    ),
    (
        "aad_read",
        "the reader stops checking the envelope it was given",
        'nonce, base64.b64decode(blob["ciphertext"]), _aad(env))',
        'nonce, base64.b64decode(blob["ciphertext"]), None)',
        "downgraded_key_derivation or swapped_salt",
    ),
    (
        "aad_both",
        "the envelope is unauthenticated on BOTH sides, so the store still "
        "round-trips and only the downgrade attack becomes possible",
        'ct = AESGCM(key).encrypt(nonce, plain, _aad(env))',
        'ct = AESGCM(key).encrypt(nonce, plain, None)',
        "envelope_field_that_does_not_feed_the_key",
        ('nonce, base64.b64decode(blob["ciphertext"]), _aad(env))',
         'nonce, base64.b64decode(blob["ciphertext"]), None)'),
    ),
    (
        "nonce",
        "the nonce is fixed, which is the one catastrophic misuse of this cipher",
        'nonce = secrets.token_bytes(NONCE_BYTES)     # fresh on EVERY write',
        'nonce = b"0" * NONCE_BYTES  # MUTATION: reused',
        "fresh_nonce",
    ),
    (
        "plaintext",
        "the secrets are written unencrypted beside the ciphertext",
        'return {"envelope": env, "ciphertext": base64.b64encode(ct).decode("ascii")}',
        'return {"envelope": env, "ciphertext": base64.b64encode(ct).decode("ascii"),\n'
        '            "DEBUG_plain": plain.decode("utf-8")}',
        "no_secret_appears",
    ),
    (
        "refusal",
        "a vendor account password becomes storable",
        'if kind in KIND_REFUSED:',
        'if False:  # MUTATION: the refusal is gone',
        "account_password or every_spelling",
    ),
    (
        "listing",
        "the listing returns the secret value alongside its metadata",
        '''        rows.append({
            "name": name,''',
        '''        rows.append({
            "value": entry.get("value", ""),
            "name": name,''',
        "listing_returns_metadata or unlocked_view",
    ),
    (
        "mode",
        "the store file becomes world-readable",
        'os.chmod(tmp, stat.S_IRUSR | stat.S_IWUSR)           # 0600',
        'os.chmod(tmp, 0o644)  # MUTATION: world-readable',
        "readable_by_its_owner",
    ),
    (
        "version",
        "an unknown on-disk version is read rather than refused",
        'if int(blob.get("envelope", {}).get("version", -1)) != STORE_VERSION:',
        'if False:  # MUTATION: version check removed',
        "future_version",
    ),
]


def run_guard(selector: str) -> tuple[bool, str]:
    """True when the selected tests are GREEN. Returns (green, tail)."""
    done = subprocess.run(
        [sys.executable, "-m", "pytest", str(GUARD), "-q", "-k", selector,
         "--netguard-strict", "-p", "no:cacheprovider"],
        capture_output=True, text=True, cwd=str(ROOT), timeout=900)
    tail = (done.stdout or "").strip().splitlines()
    return done.returncode == 0, (tail[-1] if tail else "(no output)")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--only", help="run just this mutation key")
    args = ap.parse_args()

    original = SUBJECT.read_bytes()          # held in MEMORY, restored in `finally`
    chosen = [m for m in MUTATIONS if not args.only or m[0] == args.only]
    if not chosen:
        print(f"no mutation named {args.only!r}; "
              f"known: {', '.join(m[0] for m in MUTATIONS)}")
        return 2

    print("=" * 78)
    print("CREDENTIAL STORE: DOES THE GUARD BITE?")
    print("=" * 78)
    green, tail = run_guard("not nothing_impossible")
    print(f"\n  baseline, unmutated: {'GREEN' if green else 'RED'} -- {tail}")
    if not green:
        print("  the guard is already red, so no mutation can be interpreted. Stopping.")
        return 1

    red = escaped = skipped = 0
    try:
        for mutation in chosen:
            key, what, old, new, selector = mutation[:5]
            extra = mutation[5] if len(mutation) > 5 else None
            text = original.decode("utf-8")
            pairs = [(old, new)] + ([extra] if extra else [])
            rotted = [o for o, _ in pairs if text.count(o) != 1]
            if rotted:
                print(f"\n  [SKIP] {key:<10} an anchor does not appear exactly once "
                      f"-- the code has moved and this mutation measures nothing")
                skipped += 1
                continue
            for o, n in pairs:
                text = text.replace(o, n)
            SUBJECT.write_text(text, encoding="utf-8")
            ok, tail = run_guard(selector)
            if ok:
                print(f"\n  [ESCAPE] {key:<10} {what}")
                print(f"           the guard stayed GREEN. THAT IS THE FINDING: "
                      f"nothing tests this.")
                print(f"           selector: -k {selector!r} -- {tail}")
                escaped += 1
            else:
                print(f"\n  [RED]    {key:<10} {what}")
                print(f"           caught by -k {selector!r} -- {tail}")
                red += 1
            SUBJECT.write_bytes(original)
    finally:
        SUBJECT.write_bytes(original)        # always, on any exit path
        assert SUBJECT.read_bytes() == original, "the subject was NOT restored"

    total = red + escaped
    print("\n" + "=" * 78)
    print(f"  {red} of {total} mutations RED"
          + (f", {skipped} skipped on a rotted anchor" if skipped else ""))
    if escaped:
        print(f"  {escaped} ESCAPED -- the guard has that many holes.")
    print(f"  subject restored byte-for-byte: {SUBJECT.read_bytes() == original}")
    print("=" * 78)
    return 1 if escaped else 0


if __name__ == "__main__":
    raise SystemExit(main())
