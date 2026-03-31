"""
CDSFL Verification Chain — Tamper-Evident Persistence for Reasoning Artifacts

This module implements a hash-chained, Merkle-tree-backed verification layer
for CDSFL reasoning artifacts (checkpoints, findings, solutions). It is
standalone: no dependency on run_round_robin.py, Genesis, or any external
Merkle library.

Dependencies: Python stdlib only (hashlib, json, argparse, datetime).
Optional: `cryptography` library for Ed25519 signing.

What This Layer PROVES
----------------------
- Content integrity: any modification to a sealed record's payload, metadata,
  timestamp, sequence number, artifact type, or recorder identity changes the
  entry hash and breaks the chain from that point forward.
- Ordering: the hash chain enforces a strict append-only sequence. Deletion,
  insertion, or reordering of records is detectable.
- Epoch inclusion: RFC 9162-compliant Merkle trees over sealed epochs allow
  compact inclusion proofs for any individual record.
- Authenticated source (when signed): if an Ed25519 signer is provided,
  records carry a cryptographic signature binding the sealed body to a
  specific key. Without a signer, attribution is claimed only.

What This Layer DOES NOT PROVE
------------------------------
- Whether reasoning was genuine: a record attesting "I considered alternative
  X" proves the attestation exists, not that the reasoning occurred.
- Whether a conclusion was correct: content integrity says nothing about
  content truth.
- Whether the timestamp is accurate: timestamps are claimed wall-clock UTC.
  The chain proves they were not altered after sealing, not that they were
  accurate when recorded.
- Timeliness of record submission: a record could be created and signed but
  withheld for an arbitrary period before being appended to the chain. The
  chain proves order of insertion, not immediacy of recording.
- Non-repudiation without key management: Ed25519 signatures prove possession
  of the signing key at signing time. Implementers must provide secure key
  storage, define a key lifecycle (rotation), and have a policy for handling
  key compromise (revocation/distrust). Without these, the non-repudiation
  guarantee is operationally weak.
- On-chain anchoring: this is Layer 3 (local persistence). Layer 4 (blockchain
  anchoring) is a separate concern.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import sys
import tempfile
from datetime import datetime, timezone
from typing import Any, Optional

__all__ = [
    "VerificationChain",
    "Signer",
    "Verifier",
    "GENESIS_CONSTANT",
    "SCHEMA_VERSION",
    "canonical_json",
    "sha256_digest",
    "rfc9162_merkle_root",
    "rfc9162_inclusion_proof",
    "rfc9162_verify_inclusion",
]

SCHEMA_VERSION = "1.0"
GENESIS_CONSTANT = hashlib.sha256(b"CDSFL_GENESIS").hexdigest()

# ---------------------------------------------------------------------------
# Optional Ed25519 support
# ---------------------------------------------------------------------------

try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import (
        Ed25519PrivateKey,
        Ed25519PublicKey,
    )
    from cryptography.hazmat.primitives.serialization import (
        Encoding,
        PublicFormat,
    )
    import base64 as _base64

    _HAS_CRYPTO = True
except ImportError:
    _HAS_CRYPTO = False


class Signer:
    """Ed25519 signer wrapper. Requires the `cryptography` library."""

    def __init__(self, private_key: "Ed25519PrivateKey", key_id: str):
        if not _HAS_CRYPTO:
            raise RuntimeError(
                "Ed25519 signing requires the 'cryptography' library"
            )
        self._key = private_key
        self.key_id = key_id

    def sign(self, data: bytes) -> str:
        """Return base64-encoded signature."""
        sig = self._key.sign(data)
        return _base64.b64encode(sig).decode("ascii")

    def public_key_bytes(self) -> bytes:
        return self._key.public_key().public_bytes(
            Encoding.Raw, PublicFormat.Raw
        )


class Verifier:
    """Ed25519 verifier wrapper."""

    def __init__(self, public_key: "Ed25519PublicKey"):
        if not _HAS_CRYPTO:
            raise RuntimeError(
                "Ed25519 verification requires the 'cryptography' library"
            )
        self._key = public_key

    def verify(self, signature_b64: str, data: bytes) -> bool:
        """Verify a base64-encoded Ed25519 signature.

        Returns False for invalid signatures or malformed base64.
        Raises on unexpected errors (library bugs, bad key state).
        """
        import binascii
        from cryptography.exceptions import InvalidSignature
        try:
            sig = _base64.b64decode(signature_b64, validate=True)
            self._key.verify(sig, data)
            return True
        except (InvalidSignature, binascii.Error):
            return False


# ---------------------------------------------------------------------------
# Core hashing utilities
# ---------------------------------------------------------------------------


def canonical_json(obj: Any) -> str:
    """Deterministic JSON serialization: sorted keys, compact separators.

    IMPORTANT: Sealed record bodies must not contain floating-point values.
    Float serialization varies across platforms and can break determinism.
    Use fixed-precision decimal strings if numeric precision is needed.

    Raises TypeError if any float is found in the object tree.
    """
    _reject_floats(obj)
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def _reject_floats(obj: Any) -> None:
    """Recursively check for float values and raise TypeError if found."""
    if isinstance(obj, float):
        raise TypeError(
            f"Float values break cross-platform determinism. "
            f"Use string representation instead: {obj!r}"
        )
    if isinstance(obj, dict):
        for v in obj.values():
            _reject_floats(v)
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            _reject_floats(v)


def sha256_digest(data: bytes) -> str:
    """Return 'sha256:<hex>' digest string."""
    return "sha256:" + hashlib.sha256(data).hexdigest()


_DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


def _digest_bytes(digest_str: str) -> bytes:
    """Extract raw hash bytes from 'sha256:<hex>' string.

    Validates strict canonical format: lowercase hex, exactly 64 characters,
    no whitespace or uppercase.
    """
    if not _DIGEST_RE.match(digest_str):
        raise ValueError(
            f"Expected digest matching 'sha256:<64 lowercase hex chars>', "
            f"got: {digest_str!r}"
        )
    return bytes.fromhex(digest_str[7:])


def _normalize_timestamp(ts: str) -> str:
    """Parse a timestamp string and return RFC 3339 UTC.

    Accepts ISO 8601 timestamps with explicit timezone (Z or +/-HH:MM).
    Rejects naive timestamps (no timezone) to prevent ambiguous audit records.
    """
    ts = ts.strip()
    # Only replace a trailing Z, not Z appearing elsewhere in the string
    if ts.endswith("Z"):
        dt = datetime.fromisoformat(ts[:-1] + "+00:00")
    else:
        dt = datetime.fromisoformat(ts)
    # Reject naive timestamps — ambiguous in an audit context
    if dt.tzinfo is None:
        raise ValueError(
            f"Timestamp must include explicit timezone (Z or +/-HH:MM), "
            f"got naive timestamp: {ts!r}"
        )
    # Convert to UTC
    dt = dt.astimezone(timezone.utc)
    # Format as RFC 3339 UTC
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def _utc_now() -> str:
    """Current UTC timestamp in RFC 3339 format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# RFC 9162 Merkle tree
# ---------------------------------------------------------------------------

_LEAF_PREFIX = b"\x00"
_NODE_PREFIX = b"\x01"


def _leaf_hash(data: bytes) -> bytes:
    """RFC 9162 leaf hash: SHA-256(0x00 || data)."""
    return hashlib.sha256(_LEAF_PREFIX + data).digest()


def _node_hash(left: bytes, right: bytes) -> bytes:
    """RFC 9162 internal node hash: SHA-256(0x01 || left || right)."""
    return hashlib.sha256(_NODE_PREFIX + left + right).digest()


def _largest_power_of_two_less_than(n: int) -> int:
    """Return the largest power of 2 strictly less than n.

    This implements the RFC 9162 split point calculation.
    """
    if n <= 1:
        raise ValueError("n must be > 1")
    k = 1
    while k * 2 < n:
        k *= 2
    return k


def rfc9162_merkle_root(leaves: list[bytes]) -> bytes:
    """Compute RFC 9162 Merkle tree root hash.

    Args:
        leaves: list of raw leaf data (chain_hash bytes).

    Returns:
        Root hash bytes. For empty list, returns SHA-256(b"").
    """
    n = len(leaves)
    if n == 0:
        return hashlib.sha256(b"").digest()
    if n == 1:
        return _leaf_hash(leaves[0])

    k = _largest_power_of_two_less_than(n)
    left = rfc9162_merkle_root(leaves[:k])
    right = rfc9162_merkle_root(leaves[k:])
    return _node_hash(left, right)


def rfc9162_inclusion_proof(leaves: list[bytes], index: int) -> list[dict]:
    """Build an RFC 9162 inclusion proof for leaf at `index`.

    Returns a list of {"hash": <hex>, "side": "left"|"right"} dicts,
    bottom-up from the leaf to the root.
    """
    n = len(leaves)
    if n == 0:
        raise ValueError("Cannot build inclusion proof for empty tree")
    if not (0 <= index < n):
        raise IndexError(f"Leaf index {index} out of range [0, {n})")

    if n == 1:
        return []  # Root is the leaf hash; no siblings needed.

    k = _largest_power_of_two_less_than(n)

    if index < k:
        # Target is in the left subtree
        proof = rfc9162_inclusion_proof(leaves[:k], index)
        right_root = rfc9162_merkle_root(leaves[k:])
        proof.append({"hash": right_root.hex(), "side": "right"})
    else:
        # Target is in the right subtree
        proof = rfc9162_inclusion_proof(leaves[k:], index - k)
        left_root = rfc9162_merkle_root(leaves[:k])
        proof.append({"hash": left_root.hex(), "side": "left"})

    return proof


def rfc9162_verify_inclusion(
    leaf_data: bytes, proof: list[dict], expected_root: bytes
) -> bool:
    """Verify an RFC 9162 inclusion proof.

    Args:
        leaf_data: raw leaf bytes (not yet hashed).
        proof: list of {"hash": <hex>, "side": "left"|"right"}.
        expected_root: expected Merkle root bytes.

    Returns:
        True if the proof is valid. False on any malformed input.
    """
    try:
        current = _leaf_hash(leaf_data)
        for step in proof:
            sibling = bytes.fromhex(step["hash"])
            if step["side"] == "right":
                current = _node_hash(current, sibling)
            elif step["side"] == "left":
                current = _node_hash(sibling, current)
            else:
                return False
        return current == expected_root
    except (KeyError, ValueError, TypeError, AttributeError):
        return False


# ---------------------------------------------------------------------------
# Record construction
# ---------------------------------------------------------------------------


def _build_sealed_body(
    seq: int,
    artifact_type: str,
    timestamp_utc: str,
    recorded_by: str,
    storage_mode: str,
    payload_hash: str,
    metadata: Optional[dict],
    payload: Any = None,
) -> dict:
    """Build the sealed record body (all fields included in the hash)."""
    body = {
        "schema_version": SCHEMA_VERSION,
        "seq": seq,
        "artifact_type": artifact_type,
        "timestamp_utc": timestamp_utc,
        "recorded_by": recorded_by,
        "storage_mode": storage_mode,
        "payload_hash": payload_hash,
        "metadata": metadata,
    }
    if storage_mode == "full_payload":
        body["payload"] = payload
    return body


def _compute_entry_hash(sealed_body: dict) -> str:
    """SHA-256 of the canonical JSON of the sealed body."""
    return sha256_digest(canonical_json(sealed_body).encode("utf-8"))


def _compute_chain_hash(prev_hash: str, entry_hash: str) -> str:
    """SHA-256(prev_hash_bytes || entry_hash_bytes) — hash bytes, not strings.

    Design note: this construction relies on both inputs being exactly 32 bytes
    (SHA-256 digests), producing a fixed 64-byte concatenation. This prevents
    ambiguity without explicit length prefixing. If input sizes ever change,
    a domain-separated construction would be required.
    """
    combined = _digest_bytes(prev_hash) + _digest_bytes(entry_hash)
    return "sha256:" + hashlib.sha256(combined).hexdigest()


# ---------------------------------------------------------------------------
# VerificationChain
# ---------------------------------------------------------------------------


class VerificationChain:
    """Append-only hash chain with RFC 9162 Merkle epoch sealing."""

    def __init__(self, signer: Optional[Signer] = None):
        self._records: list[dict] = []
        self._epochs: list[dict] = []
        self._signer = signer
        self._schema_version = SCHEMA_VERSION

    # -- Public API --------------------------------------------------------

    def append_record(
        self,
        artifact_type: str,
        payload: Any,
        recorded_by: str,
        metadata: Optional[dict] = None,
        storage_mode: str = "full_payload",
        timestamp: Optional[str] = None,
    ) -> dict:
        """Append a new record to the chain. Returns the full record dict."""
        if storage_mode not in ("full_payload", "hash_only"):
            raise ValueError(f"Invalid storage_mode: {storage_mode!r}")

        seq = len(self._records)
        ts = _normalize_timestamp(timestamp) if timestamp else _utc_now()
        payload_hash = sha256_digest(
            canonical_json(payload).encode("utf-8")
        )

        sealed_body = _build_sealed_body(
            seq=seq,
            artifact_type=artifact_type,
            timestamp_utc=ts,
            recorded_by=recorded_by,
            storage_mode=storage_mode,
            payload_hash=payload_hash,
            metadata=metadata,
            payload=payload if storage_mode == "full_payload" else None,
        )

        entry_hash = _compute_entry_hash(sealed_body)
        prev_hash = (
            self._records[-1]["chain_hash"] if self._records else
            f"sha256:{GENESIS_CONSTANT}"
        )
        chain_hash = _compute_chain_hash(prev_hash, entry_hash)

        record = {
            "sealed_body": sealed_body,
            "entry_hash": entry_hash,
            "prev_hash": prev_hash,
            "chain_hash": chain_hash,
        }

        # Optional signing
        if self._signer is not None:
            sig_data = canonical_json(sealed_body).encode("utf-8")
            record["signature"] = {
                "algorithm": "Ed25519",
                "key_id": self._signer.key_id,
                "signature": self._signer.sign(sig_data),
                "attribution": "authenticated",
            }
        else:
            record["signature"] = {
                "algorithm": None,
                "key_id": None,
                "signature": None,
                "attribution": "claimed_only",
            }

        self._records.append(record)
        return record

    def seal_epoch(self) -> dict:
        """Seal all current records into a Merkle epoch.

        Returns an epoch dict containing the merkle_root and record count.
        Raises ValueError if the chain is empty or no new records exist
        since the last sealed epoch.
        """
        if not self._records:
            raise ValueError("Cannot seal epoch on empty chain")
        if (self._epochs
                and self._epochs[-1]["record_count"] == len(self._records)):
            raise ValueError("No new records since last epoch seal")
        leaves = [
            _digest_bytes(r["chain_hash"]) for r in self._records
        ]
        root = rfc9162_merkle_root(leaves)
        epoch = {
            "epoch_index": len(self._epochs),
            "record_count": len(self._records),
            "merkle_root": "sha256:" + root.hex(),
            "sealed_at": _utc_now(),
        }
        self._epochs.append(epoch)
        return epoch

    def verify_chain(
        self, verifier: Optional["Verifier"] = None
    ) -> tuple[bool, str]:
        """Verify the entire chain. Returns (valid, message).

        If a Verifier is provided, signatures on authenticated records are
        also checked. Records with attribution "claimed_only" are not checked.

        All records and epochs are checked even if early failures are found,
        so the returned message contains a complete diagnostic.
        """
        if not self._records:
            return True, "Chain is empty — nothing to verify."

        errors: list[str] = []

        for i, record in enumerate(self._records):
            ok, msg = self._verify_single(i, record, verifier=verifier)
            if not ok:
                errors.append(f"Record {i}: {msg}")

        # Verify epochs if any exist
        for epoch in self._epochs:
            ok, msg = self._verify_epoch(epoch)
            if not ok:
                errors.append(
                    f"Epoch {epoch.get('epoch_index', '?')}: {msg}"
                )

        if errors:
            return False, "; ".join(errors)
        return True, f"All {len(self._records)} records verified."

    def verify_record(
        self, index: int, verifier: Optional["Verifier"] = None
    ) -> tuple[bool, str]:
        """Verify a single record by index."""
        if not (0 <= index < len(self._records)):
            return False, f"Index {index} out of range [0, {len(self._records)})"
        return self._verify_single(index, self._records[index], verifier=verifier)

    def build_inclusion_proof(self, index: int) -> dict:
        """Build an RFC 9162 inclusion proof for the record at `index`."""
        if not (0 <= index < len(self._records)):
            raise IndexError(
                f"Index {index} out of range [0, {len(self._records)})"
            )
        leaves = [_digest_bytes(r["chain_hash"]) for r in self._records]
        proof_steps = rfc9162_inclusion_proof(leaves, index)
        root = rfc9162_merkle_root(leaves)
        return {
            "index": index,
            "chain_hash": self._records[index]["chain_hash"],
            "proof": proof_steps,
            "merkle_root": "sha256:" + root.hex(),
        }

    def verify_inclusion_proof(self, proof: dict, merkle_root: str) -> bool:
        """Verify an inclusion proof against a given Merkle root.

        merkle_root should be in 'sha256:<hex>' format.
        """
        try:
            leaf_data = _digest_bytes(proof["chain_hash"])
            root_bytes = _digest_bytes(merkle_root)
            return rfc9162_verify_inclusion(leaf_data, proof["proof"], root_bytes)
        except (KeyError, ValueError, TypeError):
            return False

    def save_json(self, path: str) -> None:
        """Serialize the full chain to a JSON file.

        Uses atomic write (write to temp file, then rename) to prevent
        corruption from crashes or interruptions during write.
        """
        data = {
            "schema_version": self._schema_version,
            "records": self._records,
            "epochs": self._epochs,
        }
        # Write to temp file first, then atomically replace
        dir_name = os.path.dirname(os.path.abspath(path))
        fd, tmp_path = tempfile.mkstemp(dir=dir_name, suffix=".tmp")
        try:
            with os.fdopen(fd, "w") as f:
                json.dump(data, f, indent=2)
            os.replace(tmp_path, path)
        except BaseException:
            # Clean up temp file on any failure
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise

    @classmethod
    def load_json(cls, path: str) -> "VerificationChain":
        """Deserialize a chain from a JSON file.

        Preserves the schema_version from the loaded file to prevent
        silent version downgrades on round-trip.
        """
        with open(path, "r") as f:
            data = json.load(f)
        chain = cls()
        chain._schema_version = data.get("schema_version", SCHEMA_VERSION)
        chain._records = data.get("records", [])
        chain._epochs = data.get("epochs", [])
        return chain

    def head(self) -> Optional[dict]:
        """Return a deep copy of the latest record, or None if empty.

        Returns a copy to prevent accidental mutation of internal state.
        """
        return copy.deepcopy(self._records[-1]) if self._records else None

    @property
    def records(self) -> list[dict]:
        """Read-only access to the record list."""
        return list(self._records)

    @property
    def epochs(self) -> list[dict]:
        """Read-only access to the epoch list."""
        return list(self._epochs)

    # -- Internal ----------------------------------------------------------

    def _verify_single(
        self, index: int, record: dict,
        verifier: Optional["Verifier"] = None,
    ) -> tuple[bool, str]:
        """Verify a single record's hashes, chain linkage, and optionally signature."""
        sealed_body = record["sealed_body"]

        # 1. Verify entry_hash
        expected_entry = _compute_entry_hash(sealed_body)
        if record["entry_hash"] != expected_entry:
            return False, (
                f"entry_hash mismatch: stored {record['entry_hash']}, "
                f"computed {expected_entry}"
            )

        # 2. Verify prev_hash linkage
        if index == 0:
            expected_prev = f"sha256:{GENESIS_CONSTANT}"
        else:
            expected_prev = self._records[index - 1]["chain_hash"]
        if record["prev_hash"] != expected_prev:
            return False, (
                f"prev_hash mismatch: stored {record['prev_hash']}, "
                f"expected {expected_prev}"
            )

        # 3. Verify chain_hash
        expected_chain = _compute_chain_hash(
            record["prev_hash"], record["entry_hash"]
        )
        if record["chain_hash"] != expected_chain:
            return False, (
                f"chain_hash mismatch: stored {record['chain_hash']}, "
                f"computed {expected_chain}"
            )

        # 4. Verify payload_hash (only for full_payload mode)
        if sealed_body["storage_mode"] == "full_payload":
            expected_payload = sha256_digest(
                canonical_json(sealed_body["payload"]).encode("utf-8")
            )
            if sealed_body["payload_hash"] != expected_payload:
                return False, (
                    f"payload_hash mismatch: stored {sealed_body['payload_hash']}, "
                    f"computed {expected_payload}"
                )

        # 5. Verify sequence number
        if sealed_body["seq"] != index:
            return False, (
                f"seq mismatch: stored {sealed_body['seq']}, expected {index}"
            )

        # 6. Verify signature (if verifier provided and record is authenticated)
        if verifier is not None:
            if not _HAS_CRYPTO:
                raise RuntimeError(
                    "Signature verification requested but 'cryptography' "
                    "library is not available"
                )
            sig_info = record.get("signature", {})
            if sig_info.get("attribution") == "authenticated":
                # Validate algorithm field matches expected scheme
                algo = sig_info.get("algorithm")
                if algo != "Ed25519":
                    return False, (
                        f"unsupported signature algorithm: {algo!r}"
                    )
                sig_b64 = sig_info.get("signature")
                if not sig_b64:
                    return False, "authenticated record has no signature data"
                sig_data = canonical_json(sealed_body).encode("utf-8")
                if not verifier.verify(sig_b64, sig_data):
                    return False, "signature verification failed"

        return True, "OK"

    def _verify_epoch(self, epoch: dict) -> tuple[bool, str]:
        """Verify a stored epoch's Merkle root against the chain records."""
        record_count = epoch.get("record_count", 0)
        if record_count > len(self._records):
            return False, (
                f"epoch claims {record_count} records but chain has "
                f"{len(self._records)}"
            )
        leaves = [
            _digest_bytes(r["chain_hash"])
            for r in self._records[:record_count]
        ]
        expected_root = "sha256:" + rfc9162_merkle_root(leaves).hex()
        stored_root = epoch.get("merkle_root", "")
        if stored_root != expected_root:
            return False, (
                f"merkle_root mismatch: stored {stored_root}, "
                f"computed {expected_root}"
            )
        return True, "OK"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _cli_record(args: argparse.Namespace) -> int:
    """Handle the 'record' subcommand."""
    chain_path = args.chain or "chain.json"

    # Load existing chain or create new
    try:
        chain = VerificationChain.load_json(chain_path)
    except FileNotFoundError:
        chain = VerificationChain()

    payload = json.loads(args.payload)
    record = chain.append_record(
        artifact_type=args.type,
        payload=payload,
        recorded_by=args.by,
        storage_mode=args.mode,
        metadata=json.loads(args.metadata) if args.metadata else None,
    )
    chain.save_json(chain_path)

    print(f"Appended record seq={record['sealed_body']['seq']} "
          f"to {chain_path}")
    print(f"  entry_hash: {record['entry_hash']}")
    print(f"  chain_hash: {record['chain_hash']}")
    return 0


def _cli_verify_chain(args: argparse.Namespace) -> int:
    """Handle the 'verify-chain' subcommand."""
    chain = VerificationChain.load_json(args.chain_file)
    valid, msg = chain.verify_chain()
    print(msg)
    return 0 if valid else 1


def _cli_verify_record(args: argparse.Namespace) -> int:
    """Handle the 'verify-record' subcommand."""
    chain = VerificationChain.load_json(args.chain_file)
    valid, msg = chain.verify_record(args.index)
    print(f"Record {args.index}: {msg}")
    return 0 if valid else 1


def _cli_seal_epoch(args: argparse.Namespace) -> int:
    """Handle the 'seal-epoch' subcommand."""
    chain = VerificationChain.load_json(args.chain_file)
    valid, msg = chain.verify_chain()
    if not valid:
        print(f"Chain verification failed: {msg}", file=sys.stderr)
        return 1
    epoch = chain.seal_epoch()
    chain.save_json(args.chain_file)
    print(f"Epoch {epoch['epoch_index']} sealed: "
          f"{epoch['record_count']} records, root={epoch['merkle_root']}")
    return 0


def _cli_prove_record(args: argparse.Namespace) -> int:
    """Handle the 'prove-record' subcommand."""
    chain = VerificationChain.load_json(args.chain_file)
    proof = chain.build_inclusion_proof(args.index)
    print(json.dumps(proof, indent=2))
    return 0


def _cli_verify_proof(args: argparse.Namespace) -> int:
    """Handle the 'verify-proof' subcommand."""
    try:
        with open(args.proof_file, "r") as f:
            proof = json.load(f)
        # Accept both 'sha256:<hex>' and bare hex for the root
        root_str = args.root
        if root_str.startswith("sha256:"):
            root_bytes = bytes.fromhex(root_str[7:])
        else:
            root_bytes = bytes.fromhex(root_str)
        # Warn if supplied root differs from proof's embedded root
        if "merkle_root" in proof:
            proof_root_hex = proof["merkle_root"].replace("sha256:", "")
            supplied_hex = root_str.replace("sha256:", "")
            if proof_root_hex != supplied_hex:
                print(
                    "WARNING: supplied root differs from proof's "
                    "embedded merkle_root",
                    file=sys.stderr,
                )
        valid = rfc9162_verify_inclusion(
            _digest_bytes(proof["chain_hash"]),
            proof["proof"],
            root_bytes,
        )
    except (KeyError, ValueError, TypeError, json.JSONDecodeError) as e:
        print(f"Proof verification failed: {e}", file=sys.stderr)
        return 1
    if valid:
        print("Inclusion proof is VALID.")
        return 0
    else:
        print("Inclusion proof is INVALID.")
        return 1


def _cli_show_head(args: argparse.Namespace) -> int:
    """Handle the 'show-head' subcommand."""
    chain = VerificationChain.load_json(args.chain_file)
    h = chain.head()
    if h is None:
        print("Chain is empty.")
    else:
        print(json.dumps(h, indent=2))
    return 0


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="CDSFL Verification Chain — tamper-evident persistence"
    )
    sub = parser.add_subparsers(dest="command")

    # record
    p_rec = sub.add_parser("record", help="Append a record")
    p_rec.add_argument("--type", required=True, help="Artifact type")
    p_rec.add_argument("--by", required=True, help="Recorded by")
    p_rec.add_argument("--payload", required=True, help="JSON payload")
    p_rec.add_argument("--mode", default="full_payload",
                       choices=["full_payload", "hash_only"])
    p_rec.add_argument("--metadata", default=None, help="JSON metadata")
    p_rec.add_argument("--chain", default=None, help="Chain file path")

    # verify-chain
    p_vc = sub.add_parser("verify-chain", help="Verify entire chain")
    p_vc.add_argument("chain_file", help="Path to chain JSON")

    # verify-record
    p_vr = sub.add_parser("verify-record", help="Verify a single record")
    p_vr.add_argument("chain_file", help="Path to chain JSON")
    p_vr.add_argument("--index", type=int, required=True)

    # seal-epoch
    p_se = sub.add_parser("seal-epoch", help="Seal current epoch")
    p_se.add_argument("chain_file", help="Path to chain JSON")

    # prove-record
    p_pr = sub.add_parser("prove-record", help="Build inclusion proof")
    p_pr.add_argument("chain_file", help="Path to chain JSON")
    p_pr.add_argument("--index", type=int, required=True)

    # verify-proof
    p_vp = sub.add_parser("verify-proof", help="Verify inclusion proof")
    p_vp.add_argument("proof_file", help="Path to proof JSON")
    p_vp.add_argument("--root", required=True, help="Expected Merkle root hex")

    # show-head
    p_sh = sub.add_parser("show-head", help="Show latest record")
    p_sh.add_argument("chain_file", help="Path to chain JSON")

    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 1

    handlers = {
        "record": _cli_record,
        "verify-chain": _cli_verify_chain,
        "verify-record": _cli_verify_record,
        "seal-epoch": _cli_seal_epoch,
        "prove-record": _cli_prove_record,
        "verify-proof": _cli_verify_proof,
        "show-head": _cli_show_head,
    }

    try:
        return handlers[args.command](args)
    except (json.JSONDecodeError, FileNotFoundError, PermissionError,
            ValueError, IndexError, OSError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
