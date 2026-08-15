#!/usr/bin/env python3
"""Seal logs/ contents into tamper-evident Merkle chains.

Walks `logs/confer/` and `logs/chat/` for subdirectories containing log
artefacts (.json, .log, .md, .txt) and creates a sealed_chain.json per
subdirectory. Uses the existing VerificationChain infrastructure from
`bench/verification_chain.py` (RFC 9162 Merkle tree, SHA-256 leaves).

Modes:
  Default       — seal every unsealed directory under logs/confer and logs/chat.
  --dry-run     — list what would be sealed; write nothing.
  --verify      — verify existing seals; exit non-zero on tamper.
  --force       — re-seal directories that already have a sealed_chain.json.

The current implementation uses unsigned Merkle sealing (matching the
existing `bench/seal_experiment_logs.py` convention). This provides
tamper evidence — any modification to a sealed file invalidates the
Merkle root — but does not provide non-repudiation. Upgrading to signed
sealing is a configuration change: provide an Ed25519 signer to
`VerificationChain(signer=...)`. The private key must remain outside
the repository and the public key committed at a documented path.

Usage:
    python3 scripts/cdsfl_seal_logs.py              # seal unsealed dirs
    python3 scripts/cdsfl_seal_logs.py --dry-run    # show plan
    python3 scripts/cdsfl_seal_logs.py --verify     # check existing seals
    python3 scripts/cdsfl_seal_logs.py --force      # re-seal everything
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from bench.verification_chain import (  # noqa: E402
    VerificationChain,
    canonical_json,
    sha256_digest,
)


LOGS_ROOT = REPO_ROOT / "logs"
SEALABLE_SUBTREES = ("confer", "chat")
SEALABLE_EXTENSIONS = {".json", ".log", ".md", ".txt"}
SEAL_FILENAME = "sealed_chain.json"


def _sanitise(obj):
    """Convert floats to strings; VerificationChain rejects floats for determinism."""
    if isinstance(obj, float):
        return str(obj)
    if isinstance(obj, dict):
        return {k: _sanitise(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_sanitise(v) for v in obj]
    return obj


def _payload_for(path: Path) -> dict:
    """Produce a sealable payload for a given file.

    JSON files are parsed and sanitised. Other files are wrapped as a
    text record carrying their content (so the Merkle leaf covers the
    content, not just the filename).
    """
    if path.suffix == ".json":
        try:
            return _sanitise(json.loads(path.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, OSError):
            pass
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as err:
        text = f"<unreadable: {err}>"
    return {
        "filename": path.name,
        "size_bytes": path.stat().st_size,
        "content": text,
    }


def _seal_dir(dir_path: Path, dry_run: bool, force: bool) -> dict | None:
    """Seal every eligible file in a directory into a new Merkle chain.

    Skips if a sealed_chain.json already exists and --force is not set.
    """
    seal_path = dir_path / SEAL_FILENAME
    if seal_path.exists() and not force:
        return {
            "dir": str(dir_path.relative_to(LOGS_ROOT)),
            "records": 0,
            "merkle_root": "(already sealed — skipped)",
        }

    chain = VerificationChain()
    records_staged: list[tuple[str, dict, dict]] = []

    for f in sorted(dir_path.iterdir()):
        if not f.is_file() or f.name == SEAL_FILENAME:
            continue
        if f.suffix not in SEALABLE_EXTENSIONS:
            continue
        payload = _payload_for(f)
        meta = {
            "subtree": dir_path.parent.name,
            "directory": dir_path.name,
            "source_file": f.name,
        }
        records_staged.append(("log_archive", payload, meta))

    if not records_staged:
        return None

    if dry_run:
        for artifact_type, _, meta in records_staged:
            print(f"  [DRY RUN] would seal: {meta['source_file']}")
        return {
            "dir": str(dir_path.relative_to(LOGS_ROOT)),
            "records": len(records_staged),
            "merkle_root": "(dry run)",
        }

    for artifact_type, payload, meta in records_staged:
        chain.append_record(
            artifact_type=artifact_type,
            payload=payload,
            recorded_by="cdsfl_seal_logs",
            metadata=meta,
            storage_mode="hash_only",
        )

    epoch = chain.seal_epoch()
    chain.save_json(str(seal_path))
    return {
        "dir": str(dir_path.relative_to(LOGS_ROOT)),
        "records": len(records_staged),
        "merkle_root": epoch["merkle_root"],
    }


def _verify_contents(dir_path: Path, chain: VerificationChain) -> tuple[bool, str]:
    """Re-read every sealed source file and compare it to the sealed hash.

    `verify_chain()` only proves the seal file is internally self-consistent.
    Records here are written in `hash_only` mode, so that check never touches
    the log files at all — a rewritten log verifies OK against an untouched
    seal. This re-reads each file from disk and recomputes its payload hash
    exactly as `append_record` did, so content tampering is actually detected.

    A file present in the directory but absent from the seal is NOT reported:
    directories are sealed once and new logs land in them during normal
    operation, so flagging additions would be a false positive.
    """
    errors: list[str] = []
    records = chain.records

    # An emptied seal is self-consistent — verify_chain() calls a chain with no
    # records "empty, nothing to verify". If the directory still holds sealable
    # files, that seal covers nothing and must not read as OK.
    if not records:
        eligible = [
            f for f in dir_path.iterdir()
            if f.is_file() and f.name != SEAL_FILENAME
            and f.suffix in SEALABLE_EXTENSIONS
        ]
        if eligible:
            return False, (
                f"seal contains 0 records but {len(eligible)} sealable "
                f"file(s) are present"
            )

    for record in records:
        body = record.get("sealed_body", {})
        seq = body.get("seq", "?")
        name = (body.get("metadata") or {}).get("source_file")
        if not name:
            errors.append(f"record {seq}: no source_file in metadata")
            continue
        src = dir_path / name
        if not src.is_file():
            errors.append(f"{name}: sealed file is missing from disk")
            continue
        actual = sha256_digest(canonical_json(_payload_for(src)).encode("utf-8"))
        if actual != body.get("payload_hash"):
            errors.append(
                f"{name}: content hash mismatch — sealed "
                f"{body.get('payload_hash')}, on disk {actual}"
            )
    if errors:
        return False, "; ".join(errors)
    return True, f"{len(records)} sealed file(s) re-read and matched"


def _verify_dir(dir_path: Path) -> bool:
    seal_path = dir_path / SEAL_FILENAME
    rel = dir_path.relative_to(LOGS_ROOT)
    if not seal_path.exists():
        print(f"  {rel}: UNSEALED", file=sys.stderr)
        return False
    try:
        chain = VerificationChain.load_json(str(seal_path))
        # verify_chain returns (bool, message). Testing the tuple itself for
        # truth is always True and silently discards the verdict.
        ok, msg = chain.verify_chain()
        if ok:
            ok, msg = _verify_contents(dir_path, chain)
    except Exception as err:  # noqa: BLE001
        print(f"  {rel}: ERROR — {err}", file=sys.stderr)
        return False
    if not ok:
        print(f"  {rel}: TAMPERED — {msg}", file=sys.stderr)
        return False
    print(f"  {rel}: OK — {msg}")
    return True


def _discover_dirs() -> list[Path]:
    """Return every directory under logs/confer or logs/chat that contains sealable files."""
    found: list[Path] = []
    for subtree in SEALABLE_SUBTREES:
        root = LOGS_ROOT / subtree
        if not root.is_dir():
            continue
        has_loose_files = any(
            f.is_file()
            and f.suffix in SEALABLE_EXTENSIONS
            and f.name != SEAL_FILENAME
            for f in root.iterdir()
        )
        if has_loose_files:
            found.append(root)
        for entry in sorted(root.iterdir()):
            if entry.is_dir() and not entry.name.startswith("_"):
                found.append(entry)
    return found


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Seal logs/ contents with tamper-evident Merkle chains."
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="Show plan without writing seals.")
    parser.add_argument("--verify", action="store_true",
                        help="Verify existing seals; exit non-zero on tamper.")
    parser.add_argument("--force", action="store_true",
                        help="Re-seal directories that are already sealed.")
    args = parser.parse_args()

    dirs = _discover_dirs()
    if not dirs:
        print("No sealable directories found under logs/.", file=sys.stderr)
        return 1

    if args.verify:
        print(f"Verifying {len(dirs)} sealed director{'y' if len(dirs) == 1 else 'ies'}.\n")
        all_ok = True
        for d in dirs:
            if not _verify_dir(d):
                all_ok = False
        return 0 if all_ok else 1

    print(f"Found {len(dirs)} director{'y' if len(dirs) == 1 else 'ies'} to consider.\n")
    summaries: list[dict] = []
    for d in dirs:
        print(f"Sealing {d.relative_to(LOGS_ROOT)} ...")
        s = _seal_dir(d, dry_run=args.dry_run, force=args.force)
        if s is not None:
            summaries.append(s)

    if not summaries:
        print("\nNothing to seal.")
        return 0

    print("\n" + "=" * 72)
    print(f"{'Directory':<45} {'Records':>7}  Merkle Root (first 32)")
    print("-" * 72)
    for s in summaries:
        root_preview = s["merkle_root"][:32]
        print(f"{s['dir']:<45} {s['records']:>7}  {root_preview}")
    print("=" * 72)
    return 0


if __name__ == "__main__":
    sys.exit(main())
