#!/usr/bin/env python3
"""A password-protected store for vendor API keys and OAuth refresh tokens.

★ WHY THIS EXISTS. Founder requirement, 2026-11-10, in his own words: the
advanced settings surface needs *"a password protected option to add and delete
vendor API keys and AI vendor logins"*, and those values must be *"encrypted
(not stored as plain text, which would clearly be a bad practice to begin with),
and can only be read, added to, or edited by the user/researcher entering the
correct password"*. Tracked as `fr:e8951f2ed269`, the credential store, under
entry B142, the settings surface.

WHAT IT REPLACES, AND THE MEASUREMENT THAT JUSTIFIES IT. `.env` at the
repository root holds 10 live vendor credentials in plain text. It is gitignored
and excluded from panel sandboxes, so it is not exposed to a routed model, but it
is readable by every process running as this user and it survives in backups. An
encrypted store behind a passphrase the operator supplies is strictly better on a
named property -- confidentiality at rest -- and costs 1 prompt.

WHAT IT IS NOT, STATED HERE BECAUSE 2 EXISTING MECHANISMS LOOK LIKE CANDIDATES
AND NEITHER IS ONE.
  * `bench/verification_chain.py` is a hash-chained Merkle structure with
    optional Ed25519 signing. It proves a record has not been ALTERED. That is
    integrity, not secrecy, and it would not hide a key from anything.
  * `bench/vault_keys.sh` seals the experiment ANSWER KEYS so a routed model
    cannot read ground truth mid-run. Same cryptography, different subject and a
    different threat model: it protects the EXPERIMENT from the models, while
    this protects the OPERATOR'S credentials from everything on the machine.
    Its hard-won lesson is carried over here -- it once had a data-loss path
    where a failed `tar` still reached the `rm` -- which is why every write below
    is atomic and keeps the previous file.

WHAT IT DELIBERATELY REFUSES TO HOLD, AND THIS IS THE ONE PIECE OF PUSHBACK.
Vendor ACCOUNT PASSWORDS are refused, with the reason stated at the point of
refusal rather than in a document nobody opens. 3 reasons, none of them
squeamishness: a stored password cannot pass a second factor, so it does not
achieve the automatic sign-in it would be stored for; every vendor command-line
tool authenticates by device flow and then holds a short-lived session token, so
the password is not the credential the tool actually wants; and automating a
sign-in with a stored password is fragile and probably outside vendor terms. The
OAuth REFRESH TOKEN those tools already issue achieves the same goal, exists for
exactly this purpose, and is revocable from the vendor's own console without
changing a password a human also uses. So: API keys yes, refresh tokens yes,
account passwords no. He can overrule this; the refusal names itself so the
conversation is about the right thing.

THE CRYPTOGRAPHY, AND WHY EACH CHOICE.
  * Key derivation is Argon2id where the installed `cryptography` provides it,
    falling back to scrypt where it does not. Both are memory-hard, so a stolen
    store file resists offline guessing far better than a plain hash would. The
    algorithm and its parameters are recorded IN the file, so a store written by
    one build opens in another and the parameters can be raised later without
    orphaning existing stores.
  * Encryption is AES-256-GCM. It is AUTHENTICATED, which is the property that
    matters here: a tampered store fails to open rather than opening to altered
    contents, and a wrong passphrase is indistinguishable from a corrupt file
    because both surface as the same authentication failure.
  * The envelope -- version, algorithm, parameters, salt, nonce -- is plain, and
    none of it is secret. It is bound in as ADDITIONAL AUTHENTICATED DATA, so an
    attacker cannot swap a strong set of parameters for a weak one without the
    open failing.
  * A fresh nonce is drawn on EVERY write. Reusing a nonce under one key is the
    single catastrophic mistake available with GCM, so the nonce is never
    carried over from the file being replaced.

WHERE THE FILE LIVES. Outside the repository, at `~/.cdsfl/credentials.enc`,
mode 0600. Outside, because a credential store inside a git working tree is 1
careless `git add -A` from being committed, and the save gate's own
`no credential tracked` postcondition exists because that class of accident is
real. `CDSFL_CREDENTIAL_STORE` overrides the path, which is what the tests use.

SECRETS NEVER ARRIVE ON THE COMMAND LINE. `ps` shows another process's argv on
this platform, so a secret passed as a flag is readable by any other user for as
long as the process lives. Values and passphrases are read from a terminal prompt
or from standard input, never from `sys.argv`.

Usage:
    python3 bench/credential_store.py init
    python3 bench/credential_store.py add   --name openrouter --kind api_key
    python3 bench/credential_store.py list
    python3 bench/credential_store.py get   --name openrouter
    python3 bench/credential_store.py delete --name openrouter
    python3 bench/credential_store.py change-password
    python3 bench/credential_store.py verify

`--help` reads nothing, writes nothing and touches no network.
"""
from __future__ import annotations

import argparse
import base64
import getpass
import hashlib
import json
import os
import secrets
import stat
import sys
import tempfile
import datetime as dt
from pathlib import Path
from typing import Any

# ───────────────────────── format and limits ─────────────────────────

#: Bumped only when the on-disk shape changes incompatibly. A reader refuses a
#: version it does not know rather than guessing at the layout.
STORE_VERSION = 1

#: The 2 kinds this store will hold. An account password is NOT among them and
#: `KIND_REFUSED` says so at the point of refusal.
KIND_API_KEY = "api_key"
KIND_REFRESH_TOKEN = "oauth_refresh_token"
ALLOWED_KINDS = (KIND_API_KEY, KIND_REFRESH_TOKEN)

#: Spellings a researcher might reasonably try for the thing this refuses, so
#: the refusal is specific rather than a generic "unknown kind".
KIND_REFUSED = (
    "account_password", "password", "login_password", "vendor_password",
    "account_login", "login",
)

#: Argon2id parameters. Memory is the expensive axis for an attacker, so it is
#: the one set deliberately high; 64 MiB per attempt makes large-scale offline
#: guessing costly while staying comfortable on an 8 GiB machine, which is a
#: fixed resource here.
ARGON2_MEMORY_KIB = 65536
ARGON2_ITERATIONS = 3
ARGON2_LANES = 4

#: scrypt fallback, used only where the installed `cryptography` has no
#: Argon2id. 2**16 is the widely published interactive-login setting.
SCRYPT_N = 1 << 16
SCRYPT_R = 8
SCRYPT_P = 1

KEY_BYTES = 32          # AES-256
SALT_BYTES = 16
NONCE_BYTES = 12        # the size AES-GCM is specified for

#: A passphrase shorter than this is refused on creation. Not a strength oracle
#: -- it is the one check that is honest to make without pretending to measure
#: entropy the store cannot see.
MIN_PASSPHRASE_CHARS = 12

DEFAULT_STORE_PATH = Path.home() / ".cdsfl" / "credentials.enc"
STORE_PATH_ENV = "CDSFL_CREDENTIAL_STORE"
PASSPHRASE_ENV = "CDSFL_CREDENTIAL_PASSPHRASE"


class CredentialStoreError(RuntimeError):
    """Anything a caller should see as a clean failure rather than a traceback."""


class WrongPassphrase(CredentialStoreError):
    """The passphrase did not open the store, or the store was tampered with.

    THESE 2 CASES ARE DELIBERATELY NOT DISTINGUISHED. Both surface as an AEAD
    authentication failure, and reporting which one occurred would tell an
    attacker holding a stolen file whether a guessed passphrase was close.
    """


# ───────────────────────── paths ─────────────────────────

def store_path() -> Path:
    """Where the encrypted file lives. The environment override is for tests."""
    override = os.environ.get(STORE_PATH_ENV)
    return Path(override).expanduser() if override else DEFAULT_STORE_PATH


# ───────────────────────── key derivation ─────────────────────────

def _derive(passphrase: str, salt: bytes, kdf: dict[str, Any]) -> bytes:
    """Derive the AES key from the passphrase using the RECORDED parameters.

    The parameters come out of the file rather than out of this module, so
    raising them later cannot orphan a store written under the old ones.
    """
    name = kdf.get("name")
    if name == "argon2id":
        from cryptography.hazmat.primitives.kdf.argon2 import Argon2id
        return Argon2id(
            salt=salt,
            length=KEY_BYTES,
            iterations=int(kdf["iterations"]),
            lanes=int(kdf["lanes"]),
            memory_cost=int(kdf["memory_kib"]),
        ).derive(passphrase.encode("utf-8"))
    if name == "scrypt":
        from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
        return Scrypt(
            salt=salt, length=KEY_BYTES,
            n=int(kdf["n"]), r=int(kdf["r"]), p=int(kdf["p"]),
        ).derive(passphrase.encode("utf-8"))
    raise CredentialStoreError(
        f"unknown key-derivation function {name!r} in the store envelope; "
        f"this build cannot open it")


def _best_kdf() -> dict[str, Any]:
    """Argon2id where the installed `cryptography` has it, else scrypt."""
    try:
        from cryptography.hazmat.primitives.kdf.argon2 import Argon2id  # noqa: F401
    except Exception:                                        # noqa: BLE001
        return {"name": "scrypt", "n": SCRYPT_N, "r": SCRYPT_R, "p": SCRYPT_P}
    return {"name": "argon2id", "memory_kib": ARGON2_MEMORY_KIB,
            "iterations": ARGON2_ITERATIONS, "lanes": ARGON2_LANES}


# ───────────────────────── envelope ─────────────────────────

def _envelope(salt: bytes, nonce: bytes, kdf: dict[str, Any]) -> dict[str, Any]:
    return {
        "version": STORE_VERSION,
        "cipher": "AES-256-GCM",
        "kdf": kdf,
        "salt": base64.b64encode(salt).decode("ascii"),
        "nonce": base64.b64encode(nonce).decode("ascii"),
    }


def _aad(envelope: dict[str, Any]) -> bytes:
    """The envelope, bound into the ciphertext as additional authenticated data.

    Without this, the parameters are unauthenticated and an attacker holding the
    file could swap Argon2id for a trivially cheap KDF and then attack the
    passphrase at that lower cost. Binding them makes such an edit fail to open.
    Serialised with sorted keys so the bytes are reproducible.
    """
    return json.dumps(envelope, sort_keys=True, separators=(",", ":")).encode("utf-8")


# ───────────────────────── read and write ─────────────────────────

def _read_file(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise CredentialStoreError(
            f"no credential store at {path}. Create one with: "
            f"python3 bench/credential_store.py init")
    try:
        blob = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:                                 # noqa: BLE001
        raise CredentialStoreError(f"{path} is not a readable store: {exc}") from exc
    if int(blob.get("envelope", {}).get("version", -1)) != STORE_VERSION:
        raise CredentialStoreError(
            f"{path} is version {blob.get('envelope', {}).get('version')}; "
            f"this build reads version {STORE_VERSION} only")
    return blob


def _atomic_write(path: Path, blob: dict[str, Any]) -> None:
    """Write the store so an interruption cannot leave a truncated file.

    ★ THE PREVIOUS FILE IS KEPT, and the reason is a defect this project has
    already paid for once: `bench/vault_keys.sh` had a path where a failed
    archive step still reached the delete, destroying the only plaintext copy of
    29 scoring keys. Here the sequence is write-temp, fsync, keep the old file as
    `.bak`, then rename -- so no step between them can leave 0 readable copies.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    os.chmod(path.parent, stat.S_IRWXU)          # 0700, owner only
    text = json.dumps(blob, indent=2, sort_keys=True) + "\n"
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".cred-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(text)
            fh.flush()
            os.fsync(fh.fileno())
        os.chmod(tmp, stat.S_IRUSR | stat.S_IWUSR)           # 0600
        if path.is_file():
            backup = path.with_suffix(path.suffix + ".bak")
            os.replace(path, backup)
            os.chmod(backup, stat.S_IRUSR | stat.S_IWUSR)
        os.replace(tmp, path)
    except Exception:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def _encrypt(secrets_map: dict[str, Any], passphrase: str,
             kdf: dict[str, Any] | None = None) -> dict[str, Any]:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    kdf = kdf or _best_kdf()
    salt = secrets.token_bytes(SALT_BYTES)
    nonce = secrets.token_bytes(NONCE_BYTES)     # fresh on EVERY write
    env = _envelope(salt, nonce, kdf)
    key = _derive(passphrase, salt, kdf)
    plain = json.dumps(secrets_map, sort_keys=True).encode("utf-8")
    ct = AESGCM(key).encrypt(nonce, plain, _aad(env))
    return {"envelope": env, "ciphertext": base64.b64encode(ct).decode("ascii")}


def _decrypt(blob: dict[str, Any], passphrase: str) -> dict[str, Any]:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    env = blob["envelope"]
    salt = base64.b64decode(env["salt"])
    nonce = base64.b64decode(env["nonce"])
    key = _derive(passphrase, salt, env["kdf"])
    try:
        plain = AESGCM(key).decrypt(
            nonce, base64.b64decode(blob["ciphertext"]), _aad(env))
    except Exception as exc:                                 # noqa: BLE001
        raise WrongPassphrase(
            "the store did not open. Either the passphrase is wrong or the file "
            "has been altered -- these are not distinguished, deliberately."
        ) from exc
    return json.loads(plain.decode("utf-8"))


# ───────────────────────── the API the backend calls ─────────────────────────

def _now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def fingerprint(value: str) -> str:
    """A short, stable, NON-REVERSING tag for a secret, so `list` can show that
    2 entries differ without showing either. Truncated SHA-256 over a domain
    separator plus the value; 12 hex characters is plenty to spot a change and
    far too few to attack the value."""
    h = hashlib.sha256(b"cdsfl-credential-fingerprint\x00" + value.encode("utf-8"))
    return h.hexdigest()[:12]


def init_store(passphrase: str, path: Path | None = None) -> Path:
    path = path or store_path()
    if path.is_file():
        raise CredentialStoreError(
            f"a store already exists at {path}. Use change-password to re-key "
            f"it, or delete the file yourself if you mean to start again.")
    if len(passphrase) < MIN_PASSPHRASE_CHARS:
        raise CredentialStoreError(
            f"the passphrase must be at least {MIN_PASSPHRASE_CHARS} characters")
    _atomic_write(path, _encrypt({"entries": {}, "created": _now()}, passphrase))
    return path


def _load(passphrase: str, path: Path | None = None) -> tuple[Path, dict[str, Any]]:
    path = path or store_path()
    return path, _decrypt(_read_file(path), passphrase)


def add_credential(name: str, kind: str, value: str, passphrase: str,
                   vendor: str = "", path: Path | None = None,
                   replace: bool = False) -> dict[str, Any]:
    """Add or replace 1 credential. Returns its metadata, never its value."""
    name = name.strip()
    if not name:
        raise CredentialStoreError("a credential needs a name")
    kind = kind.strip().lower()
    if kind in KIND_REFUSED:
        raise CredentialStoreError(
            "this store does not hold vendor account passwords, and the reason "
            "is practical rather than squeamish: a stored password cannot pass a "
            "second factor, so it would not achieve the automatic sign-in it is "
            "being stored for; every vendor command-line tool signs in by device "
            "flow and then holds a short-lived session token, so the password is "
            "not the credential the tool wants; and automating a sign-in with one "
            "is fragile and probably outside vendor terms. Store the OAuth "
            f"refresh token instead, with --kind {KIND_REFRESH_TOKEN}. It exists "
            "for exactly this, and it can be revoked from the vendor's console "
            "without changing a password a human also uses.")
    if kind not in ALLOWED_KINDS:
        raise CredentialStoreError(
            f"unknown kind {kind!r}; this store holds {' or '.join(ALLOWED_KINDS)}")
    if not value:
        raise CredentialStoreError("refusing to store an empty value")
    path, data = _load(passphrase, path)
    entries = data.setdefault("entries", {})
    if name in entries and not replace:
        raise CredentialStoreError(
            f"{name!r} is already in the store. Pass --replace to overwrite it.")
    meta = {
        "kind": kind,
        "vendor": vendor.strip(),
        "fingerprint": fingerprint(value),
        "created": entries.get(name, {}).get("created") or _now(),
        "updated": _now(),
    }
    entries[name] = {**meta, "value": value}
    _atomic_write(path, _encrypt(data, passphrase))
    return {"name": name, **meta}


def get_credential(name: str, passphrase: str,
                   path: Path | None = None) -> str:
    _, data = _load(passphrase, path)
    entry = (data.get("entries") or {}).get(name)
    if entry is None:
        raise CredentialStoreError(f"no credential named {name!r} in the store")
    return entry["value"]


def list_credentials(passphrase: str, path: Path | None = None) -> list[dict[str, Any]]:
    """Metadata for every credential. NEVER a value -- not even truncated."""
    _, data = _load(passphrase, path)
    rows = []
    for name, entry in sorted((data.get("entries") or {}).items()):
        rows.append({
            "name": name,
            "kind": entry.get("kind", ""),
            "vendor": entry.get("vendor", ""),
            "fingerprint": entry.get("fingerprint", ""),
            "created": entry.get("created", ""),
            "updated": entry.get("updated", ""),
        })
    return rows


def delete_credential(name: str, passphrase: str,
                      path: Path | None = None) -> bool:
    path, data = _load(passphrase, path)
    entries = data.get("entries") or {}
    if name not in entries:
        return False
    del entries[name]
    data["entries"] = entries
    _atomic_write(path, _encrypt(data, passphrase))
    return True


def change_passphrase(old: str, new: str, path: Path | None = None) -> Path:
    """Re-key the store. A fresh salt and nonce are drawn, so the new file shares
    no key material with the old one."""
    if len(new) < MIN_PASSPHRASE_CHARS:
        raise CredentialStoreError(
            f"the new passphrase must be at least {MIN_PASSPHRASE_CHARS} characters")
    path, data = _load(old, path)
    _atomic_write(path, _encrypt(data, new))
    return path


def verify_store(passphrase: str, path: Path | None = None) -> dict[str, Any]:
    """Prove the store opens and report WHAT IS IN IT without revealing any of it."""
    path, data = _load(passphrase, path)
    entries = data.get("entries") or {}
    kinds: dict[str, int] = {}
    for e in entries.values():
        kinds[e.get("kind", "")] = kinds.get(e.get("kind", ""), 0) + 1
    return {"path": str(path), "opens": True, "entries": len(entries),
            "by_kind": kinds, "created": data.get("created", "")}


# ───────────────────────── passphrase input ─────────────────────────

def read_passphrase(prompt: str = "Store passphrase: ", *,
                    confirm: bool = False) -> str:
    """From the environment for non-interactive use, else from a hidden prompt.

    NEVER from argv: `ps` exposes another process's command line on this
    platform, so a passphrase passed as a flag is readable by anything running
    for as long as the process lives.
    """
    env = os.environ.get(PASSPHRASE_ENV)
    if env:
        return env
    if not sys.stdin.isatty():
        line = sys.stdin.readline()
        if not line:
            raise CredentialStoreError(
                "no passphrase on standard input and no terminal to prompt on")
        return line.rstrip("\n")
    first = getpass.getpass(prompt)
    if confirm and getpass.getpass("Confirm passphrase: ") != first:
        raise CredentialStoreError("the 2 passphrases did not match")
    return first


def read_secret_value(prompt: str = "Secret value (not echoed): ") -> str:
    """The secret itself, by the same rule and for the same reason."""
    if not sys.stdin.isatty():
        line = sys.stdin.readline()
        if not line:
            raise CredentialStoreError("no value on standard input")
        return line.rstrip("\n")
    return getpass.getpass(prompt)


# ───────────────────────── command line ─────────────────────────

def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog="credential_store.py",
        description=(__doc__ or "").splitlines()[0],
        epilog=("Secrets are never read from the command line, because `ps` shows "
                "another process's arguments. Values and passphrases come from a "
                "hidden prompt, or from standard input when there is no terminal."))
    ap.add_argument("--path", help="store file (default: ~/.cdsfl/credentials.enc)")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init", help="create an empty encrypted store")
    a = sub.add_parser("add", help="add or replace 1 credential")
    a.add_argument("--name", required=True)
    a.add_argument("--kind", required=True, choices=list(ALLOWED_KINDS))
    a.add_argument("--vendor", default="")
    a.add_argument("--replace", action="store_true")
    g = sub.add_parser("get", help="print 1 value to standard output")
    g.add_argument("--name", required=True)
    sub.add_parser("list", help="names and metadata only, never values")
    d = sub.add_parser("delete", help="remove 1 credential")
    d.add_argument("--name", required=True)
    sub.add_parser("change-password", help="re-key the store")
    sub.add_parser("verify", help="prove the store opens; reveals nothing")
    return ap


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    path = Path(args.path).expanduser() if args.path else None
    try:
        if args.cmd == "init":
            p = init_store(read_passphrase("New store passphrase: ", confirm=True), path)
            print(f"created {p} (mode 0600, owner only)")
        elif args.cmd == "add":
            value = read_secret_value()
            pw = read_passphrase()
            meta = add_credential(args.name, args.kind, value, pw,
                                  vendor=args.vendor, path=path, replace=args.replace)
            print(json.dumps(meta, indent=2) if args.json else
                  f"stored {meta['name']} ({meta['kind']}) "
                  f"fingerprint {meta['fingerprint']}")
        elif args.cmd == "get":
            sys.stdout.write(get_credential(args.name, read_passphrase(), path))
            if sys.stdout.isatty():
                sys.stdout.write("\n")
        elif args.cmd == "list":
            rows = list_credentials(read_passphrase(), path)
            if args.json:
                print(json.dumps(rows, indent=2))
            elif not rows:
                print("the store is empty")
            else:
                print(f"{'NAME':<22} {'KIND':<22} {'VENDOR':<14} FINGERPRINT")
                for r in rows:
                    print(f"{r['name']:<22} {r['kind']:<22} "
                          f"{r['vendor']:<14} {r['fingerprint']}")
        elif args.cmd == "delete":
            gone = delete_credential(args.name, read_passphrase(), path)
            print(f"deleted {args.name}" if gone else f"no credential named {args.name}")
        elif args.cmd == "change-password":
            old = read_passphrase("Current passphrase: ")
            new = read_passphrase("New passphrase: ", confirm=True)
            print(f"re-keyed {change_passphrase(old, new, path)}")
        elif args.cmd == "verify":
            print(json.dumps(verify_store(read_passphrase(), path), indent=2))
    except CredentialStoreError as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
