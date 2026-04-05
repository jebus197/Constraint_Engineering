"""
Comprehensive tests for bench/verification_chain.py

Covers:
- Deterministic canonicalization
- Hash changes on any semantic change
- Timestamp tamper detection
- Chain break detection (deletion, insertion, reordering)
- JSON round-trip
- Inclusion proof valid/invalid
- Empty, single, odd-leaf epochs
- full_payload and hash_only modes
- CLI exit codes
- RFC 9162 Merkle tree correctness for various leaf counts
"""

import copy
import hashlib
import json
import os
import sys
import tempfile
import unittest

# Ensure bench/ is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from verification_chain import (
    GENESIS_CONSTANT,
    SCHEMA_VERSION,
    VerificationChain,
    canonical_json,
    main,
    rfc9162_inclusion_proof,
    rfc9162_merkle_root,
    rfc9162_verify_inclusion,
    sha256_digest,
    _digest_bytes,
    _leaf_hash,
    _node_hash,
    _normalize_timestamp,
    _largest_power_of_two_less_than,
)


# ---- Helpers ----

def _make_chain(n: int, **kwargs) -> VerificationChain:
    """Build a chain with n records using deterministic data."""
    chain = VerificationChain(**kwargs)
    for i in range(n):
        chain.append_record(
            artifact_type="finding",
            payload={"value": i},
            recorded_by="test",
            timestamp=f"2026-01-01T00:00:{i:02d}Z",
        )
    return chain


class TestCanonicalJson(unittest.TestCase):
    """Deterministic canonicalization."""

    def test_sorted_keys(self):
        obj = {"b": 2, "a": 1}
        self.assertEqual(canonical_json(obj), '{"a":1,"b":2}')

    def test_compact_separators(self):
        obj = {"x": [1, 2, 3]}
        result = canonical_json(obj)
        self.assertNotIn(" ", result)
        self.assertEqual(result, '{"x":[1,2,3]}')

    def test_stable_across_calls(self):
        obj = {"z": None, "a": True, "m": [1, {"nested": "value"}]}
        self.assertEqual(canonical_json(obj), canonical_json(obj))

    def test_nested_dicts_sorted(self):
        obj = {"outer": {"z": 1, "a": 2}}
        result = canonical_json(obj)
        self.assertEqual(result, '{"outer":{"a":2,"z":1}}')

    def test_unicode_deterministic(self):
        """Unicode chars produce a stable canonical form."""
        obj = {"emoji": "\u2603"}
        r1 = canonical_json(obj)
        r2 = canonical_json(obj)
        self.assertEqual(r1, r2)
        # json.dumps defaults to ensure_ascii=True, so escaped form
        self.assertIn("\\u2603", r1)


class TestHashChangesOnSemanticChange(unittest.TestCase):
    """Any semantic change must change the entry hash."""

    def _record_hash(self, **overrides):
        defaults = {
            "artifact_type": "finding",
            "payload": {"data": "test"},
            "recorded_by": "CC2",
            "timestamp": "2026-01-01T00:00:00Z",
        }
        defaults.update(overrides)
        chain = VerificationChain()
        rec = chain.append_record(**defaults)
        return rec["entry_hash"]

    def test_different_payload(self):
        h1 = self._record_hash(payload={"data": "A"})
        h2 = self._record_hash(payload={"data": "B"})
        self.assertNotEqual(h1, h2)

    def test_different_type(self):
        h1 = self._record_hash(artifact_type="finding")
        h2 = self._record_hash(artifact_type="solution")
        self.assertNotEqual(h1, h2)

    def test_different_recorder(self):
        h1 = self._record_hash(recorded_by="CC2")
        h2 = self._record_hash(recorded_by="CX")
        self.assertNotEqual(h1, h2)

    def test_different_timestamp(self):
        h1 = self._record_hash(timestamp="2026-01-01T00:00:00Z")
        h2 = self._record_hash(timestamp="2026-01-01T00:00:01Z")
        self.assertNotEqual(h1, h2)

    def test_different_metadata(self):
        h1 = self._record_hash(metadata=None)
        h2 = self._record_hash(metadata={"tag": "x"})
        self.assertNotEqual(h1, h2)

    def test_different_storage_mode(self):
        h1 = self._record_hash(storage_mode="full_payload")
        h2 = self._record_hash(storage_mode="hash_only")
        self.assertNotEqual(h1, h2)


class TestTimestampTamperDetection(unittest.TestCase):
    """Modifying a timestamp after sealing must be detectable."""

    def test_tampered_timestamp_fails_verification(self):
        chain = _make_chain(3)
        # Tamper with the timestamp of record 1
        chain._records[1]["sealed_body"]["timestamp_utc"] = "2099-12-31T23:59:59Z"
        valid, msg = chain.verify_chain()
        self.assertFalse(valid)
        self.assertIn("Record 1", msg)
        self.assertIn("entry_hash mismatch", msg)


class TestTimestampNormalization(unittest.TestCase):
    """Timestamps are normalized to UTC before hashing."""

    def test_z_suffix(self):
        self.assertEqual(_normalize_timestamp("2026-01-01T12:00:00Z"),
                         "2026-01-01T12:00:00Z")

    def test_offset_converted_to_utc(self):
        result = _normalize_timestamp("2026-01-01T13:00:00+01:00")
        self.assertEqual(result, "2026-01-01T12:00:00Z")

    def test_same_instant_same_hash(self):
        """Two equivalent timestamps produce the same normalized form."""
        a = _normalize_timestamp("2026-01-01T12:00:00Z")
        b = _normalize_timestamp("2026-01-01T14:00:00+02:00")
        self.assertEqual(a, b)


class TestChainBreakDetection(unittest.TestCase):
    """Deletion, insertion, and reordering must be detected."""

    def test_deletion_detected(self):
        chain = _make_chain(5)
        # Delete record 2
        del chain._records[2]
        valid, msg = chain.verify_chain()
        self.assertFalse(valid)

    def test_insertion_detected(self):
        chain = _make_chain(3)
        # Insert a duplicate of record 1 between 1 and 2
        fake = copy.deepcopy(chain._records[1])
        chain._records.insert(2, fake)
        valid, msg = chain.verify_chain()
        self.assertFalse(valid)

    def test_reordering_detected(self):
        chain = _make_chain(4)
        # Swap records 1 and 2
        chain._records[1], chain._records[2] = (
            chain._records[2], chain._records[1]
        )
        valid, msg = chain.verify_chain()
        self.assertFalse(valid)

    def test_payload_tamper_detected(self):
        """Payload tampering is caught — either as entry_hash mismatch
        (because the sealed body changed) or payload_hash mismatch."""
        chain = _make_chain(3)
        chain._records[0]["sealed_body"]["payload"]["value"] = 999
        valid, msg = chain.verify_chain()
        self.assertFalse(valid)
        # The entry_hash check fires first because the sealed body changed,
        # but either detection path is correct.
        self.assertTrue(
            "entry_hash mismatch" in msg or "payload_hash mismatch" in msg,
            f"Expected hash mismatch in message: {msg}"
        )


class TestJsonRoundTrip(unittest.TestCase):
    """save_json -> load_json -> verify_chain must succeed."""

    def test_round_trip_preserves_chain(self):
        chain = _make_chain(5)
        epoch = chain.seal_epoch()

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            chain.save_json(path)
            loaded = VerificationChain.load_json(path)

            valid, msg = loaded.verify_chain()
            self.assertTrue(valid, msg)
            self.assertEqual(len(loaded.records), 5)
            self.assertEqual(len(loaded.epochs), 1)
            self.assertEqual(loaded.epochs[0]["merkle_root"],
                             epoch["merkle_root"])
        finally:
            os.unlink(path)

    def test_round_trip_empty_chain(self):
        chain = VerificationChain()
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            chain.save_json(path)
            loaded = VerificationChain.load_json(path)
            valid, msg = loaded.verify_chain()
            self.assertTrue(valid)
            self.assertEqual(len(loaded.records), 0)
        finally:
            os.unlink(path)


class TestInclusionProof(unittest.TestCase):
    """Inclusion proof construction and verification."""

    def test_valid_proof(self):
        chain = _make_chain(8)
        for i in range(8):
            proof = chain.build_inclusion_proof(i)
            epoch = chain.seal_epoch()
            valid = chain.verify_inclusion_proof(proof, epoch["merkle_root"])
            self.assertTrue(valid, f"Proof for index {i} should be valid")
            # Re-create chain for next iteration to avoid stacking epochs
            chain = _make_chain(8)

    def test_invalid_proof_wrong_root(self):
        chain = _make_chain(4)
        proof = chain.build_inclusion_proof(2)
        fake_root = "sha256:" + "00" * 32
        valid = chain.verify_inclusion_proof(proof, fake_root)
        self.assertFalse(valid)

    def test_invalid_proof_wrong_chain_hash(self):
        chain = _make_chain(4)
        proof = chain.build_inclusion_proof(2)
        epoch = chain.seal_epoch()
        proof["chain_hash"] = "sha256:" + "ff" * 32
        valid = chain.verify_inclusion_proof(proof, epoch["merkle_root"])
        self.assertFalse(valid)

    def test_proof_out_of_range(self):
        chain = _make_chain(3)
        with self.assertRaises(IndexError):
            chain.build_inclusion_proof(5)

    def test_proof_single_record(self):
        chain = _make_chain(1)
        proof = chain.build_inclusion_proof(0)
        self.assertEqual(proof["proof"], [])
        epoch = chain.seal_epoch()
        valid = chain.verify_inclusion_proof(proof, epoch["merkle_root"])
        self.assertTrue(valid)


class TestEpochs(unittest.TestCase):
    """Empty, single, and odd-leaf epoch handling."""

    def test_empty_epoch_rejected(self):
        """Sealing an empty chain should raise ValueError."""
        chain = VerificationChain()
        with self.assertRaises(ValueError):
            chain.seal_epoch()

    def test_duplicate_epoch_idempotent(self):
        """Sealing when no new records exist returns existing epoch."""
        chain = _make_chain(3)
        e1 = chain.seal_epoch()
        e2 = chain.seal_epoch()
        self.assertEqual(e1, e2)
        self.assertEqual(len(chain.epochs), 1)

    def test_single_record_epoch(self):
        chain = _make_chain(1)
        epoch = chain.seal_epoch()
        self.assertEqual(epoch["record_count"], 1)
        # Root should be leaf hash of the single chain_hash
        leaf_data = _digest_bytes(chain.records[0]["chain_hash"])
        expected = _leaf_hash(leaf_data)
        self.assertEqual(epoch["merkle_root"], "sha256:" + expected.hex())

    def test_odd_leaf_epoch(self):
        for count in [3, 5, 7, 9, 11]:
            chain = _make_chain(count)
            epoch = chain.seal_epoch()
            # Verify the root is consistent with direct computation
            leaves = [_digest_bytes(r["chain_hash"]) for r in chain.records]
            expected = rfc9162_merkle_root(leaves)
            self.assertEqual(epoch["merkle_root"],
                             "sha256:" + expected.hex(),
                             f"Failed for {count} leaves")

    def test_multiple_epochs(self):
        chain = _make_chain(3)
        e1 = chain.seal_epoch()
        chain.append_record("finding", {"extra": True}, "test",
                            timestamp="2026-01-01T01:00:00Z")
        e2 = chain.seal_epoch()
        self.assertNotEqual(e1["merkle_root"], e2["merkle_root"])
        self.assertEqual(e2["record_count"], 4)


class TestStorageModes(unittest.TestCase):
    """full_payload and hash_only modes."""

    def test_full_payload_stores_payload(self):
        chain = VerificationChain()
        rec = chain.append_record("finding", {"x": 1}, "test",
                                  timestamp="2026-01-01T00:00:00Z")
        self.assertEqual(rec["sealed_body"]["payload"], {"x": 1})
        self.assertEqual(rec["sealed_body"]["storage_mode"], "full_payload")

    def test_hash_only_omits_payload(self):
        chain = VerificationChain()
        rec = chain.append_record("finding", {"x": 1}, "test",
                                  storage_mode="hash_only",
                                  timestamp="2026-01-01T00:00:00Z")
        self.assertNotIn("payload", rec["sealed_body"])
        self.assertEqual(rec["sealed_body"]["storage_mode"], "hash_only")
        # payload_hash is still recorded
        self.assertTrue(rec["sealed_body"]["payload_hash"].startswith("sha256:"))

    def test_hash_only_verifies_chain_integrity(self):
        chain = VerificationChain()
        chain.append_record("finding", {"x": 1}, "test",
                            storage_mode="hash_only",
                            timestamp="2026-01-01T00:00:00Z")
        chain.append_record("finding", {"x": 2}, "test",
                            timestamp="2026-01-01T00:00:01Z")
        valid, msg = chain.verify_chain()
        self.assertTrue(valid, msg)

    def test_invalid_storage_mode_raises(self):
        chain = VerificationChain()
        with self.assertRaises(ValueError):
            chain.append_record("finding", {}, "test",
                                storage_mode="compressed")

    def test_full_payload_and_hash_only_different_hashes(self):
        """Same payload in different modes produces different entry hashes."""
        c1 = VerificationChain()
        r1 = c1.append_record("finding", {"x": 1}, "test",
                              storage_mode="full_payload",
                              timestamp="2026-01-01T00:00:00Z")
        c2 = VerificationChain()
        r2 = c2.append_record("finding", {"x": 1}, "test",
                              storage_mode="hash_only",
                              timestamp="2026-01-01T00:00:00Z")
        self.assertNotEqual(r1["entry_hash"], r2["entry_hash"])


class TestRFC9162MerkleTree(unittest.TestCase):
    """RFC 9162 Merkle tree correctness for various leaf counts."""

    def test_empty_tree(self):
        root = rfc9162_merkle_root([])
        self.assertEqual(root, hashlib.sha256(b"").digest())

    def test_single_leaf(self):
        leaf = b"hello"
        root = rfc9162_merkle_root([leaf])
        expected = _leaf_hash(leaf)
        self.assertEqual(root, expected)

    def test_two_leaves(self):
        leaves = [b"a", b"b"]
        root = rfc9162_merkle_root(leaves)
        expected = _node_hash(_leaf_hash(b"a"), _leaf_hash(b"b"))
        self.assertEqual(root, expected)

    def test_three_leaves(self):
        """RFC 9162 split: 3 leaves -> split at 2 (left: 2, right: 1)."""
        leaves = [b"a", b"b", b"c"]
        root = rfc9162_merkle_root(leaves)
        left = _node_hash(_leaf_hash(b"a"), _leaf_hash(b"b"))
        right = _leaf_hash(b"c")
        expected = _node_hash(left, right)
        self.assertEqual(root, expected)

    def test_four_leaves(self):
        leaves = [b"a", b"b", b"c", b"d"]
        root = rfc9162_merkle_root(leaves)
        left = _node_hash(_leaf_hash(b"a"), _leaf_hash(b"b"))
        right = _node_hash(_leaf_hash(b"c"), _leaf_hash(b"d"))
        expected = _node_hash(left, right)
        self.assertEqual(root, expected)

    def test_five_leaves(self):
        """5 leaves -> split at 4 (left: 4, right: 1)."""
        leaves = [b"a", b"b", b"c", b"d", b"e"]
        root = rfc9162_merkle_root(leaves)
        ll = _node_hash(_leaf_hash(b"a"), _leaf_hash(b"b"))
        lr = _node_hash(_leaf_hash(b"c"), _leaf_hash(b"d"))
        left = _node_hash(ll, lr)
        right = _leaf_hash(b"e")
        expected = _node_hash(left, right)
        self.assertEqual(root, expected)

    def test_six_leaves(self):
        """6 leaves -> split at 4 (left: 4, right: 2)."""
        leaves = [b"a", b"b", b"c", b"d", b"e", b"f"]
        root = rfc9162_merkle_root(leaves)
        ll = _node_hash(_leaf_hash(b"a"), _leaf_hash(b"b"))
        lr = _node_hash(_leaf_hash(b"c"), _leaf_hash(b"d"))
        left = _node_hash(ll, lr)
        right = _node_hash(_leaf_hash(b"e"), _leaf_hash(b"f"))
        expected = _node_hash(left, right)
        self.assertEqual(root, expected)

    def test_seven_leaves(self):
        """7 leaves -> split at 4 (left: 4, right: 3)."""
        leaves = [b"a", b"b", b"c", b"d", b"e", b"f", b"g"]
        root = rfc9162_merkle_root(leaves)
        # Left: 4 leaves
        ll = _node_hash(_leaf_hash(b"a"), _leaf_hash(b"b"))
        lr = _node_hash(_leaf_hash(b"c"), _leaf_hash(b"d"))
        left = _node_hash(ll, lr)
        # Right: 3 leaves -> split at 2 (left: 2, right: 1)
        rl = _node_hash(_leaf_hash(b"e"), _leaf_hash(b"f"))
        rr = _leaf_hash(b"g")
        right = _node_hash(rl, rr)
        expected = _node_hash(left, right)
        self.assertEqual(root, expected)

    def test_deterministic(self):
        """Same leaves always produce the same root."""
        leaves = [os.urandom(32) for _ in range(10)]
        r1 = rfc9162_merkle_root(leaves)
        r2 = rfc9162_merkle_root(leaves)
        self.assertEqual(r1, r2)

    def test_order_matters(self):
        """Different leaf order produces a different root."""
        leaves = [b"a", b"b", b"c"]
        r1 = rfc9162_merkle_root(leaves)
        r2 = rfc9162_merkle_root([b"c", b"b", b"a"])
        self.assertNotEqual(r1, r2)

    def test_not_duplicate_last(self):
        """RFC 9162 does NOT use the duplicate-last-leaf strategy.

        3-leaf tree should differ from a 4-leaf tree where leaf 4 == leaf 3.
        """
        three = rfc9162_merkle_root([b"a", b"b", b"c"])
        four_dup = rfc9162_merkle_root([b"a", b"b", b"c", b"c"])
        self.assertNotEqual(three, four_dup)

    def test_inclusion_proof_all_indices_power_of_two(self):
        """Inclusion proofs for a power-of-two tree (8 leaves)."""
        leaves = [f"leaf{i}".encode() for i in range(8)]
        root = rfc9162_merkle_root(leaves)
        for i in range(8):
            proof = rfc9162_inclusion_proof(leaves, i)
            valid = rfc9162_verify_inclusion(leaves[i], proof, root)
            self.assertTrue(valid, f"Proof failed for index {i}")

    def test_inclusion_proof_all_indices_non_power(self):
        """Inclusion proofs for a non-power-of-two tree (5 leaves)."""
        leaves = [f"leaf{i}".encode() for i in range(5)]
        root = rfc9162_merkle_root(leaves)
        for i in range(5):
            proof = rfc9162_inclusion_proof(leaves, i)
            valid = rfc9162_verify_inclusion(leaves[i], proof, root)
            self.assertTrue(valid, f"Proof failed for index {i}")

    def test_inclusion_proof_single_leaf(self):
        leaves = [b"only"]
        root = rfc9162_merkle_root(leaves)
        proof = rfc9162_inclusion_proof(leaves, 0)
        self.assertEqual(proof, [])
        valid = rfc9162_verify_inclusion(leaves[0], proof, root)
        self.assertTrue(valid)

    def test_inclusion_proof_empty_tree_raises(self):
        with self.assertRaises(ValueError):
            rfc9162_inclusion_proof([], 0)

    def test_inclusion_proof_out_of_range(self):
        with self.assertRaises(IndexError):
            rfc9162_inclusion_proof([b"a", b"b"], 5)

    def test_largest_power_of_two(self):
        self.assertEqual(_largest_power_of_two_less_than(2), 1)
        self.assertEqual(_largest_power_of_two_less_than(3), 2)
        self.assertEqual(_largest_power_of_two_less_than(4), 2)
        self.assertEqual(_largest_power_of_two_less_than(5), 4)
        self.assertEqual(_largest_power_of_two_less_than(8), 4)
        self.assertEqual(_largest_power_of_two_less_than(9), 8)
        self.assertEqual(_largest_power_of_two_less_than(16), 8)
        self.assertEqual(_largest_power_of_two_less_than(17), 16)

    def test_leaf_prefix_distinct_from_node_prefix(self):
        """Leaf and node hashes use different domain-separation prefixes."""
        data = b"same"
        leaf = _leaf_hash(data)
        # A node with both children == data would be different
        node = _node_hash(data, data)
        self.assertNotEqual(leaf, node)


class TestGenesisConstant(unittest.TestCase):
    def test_genesis_is_sha256_of_marker(self):
        expected = hashlib.sha256(b"CDSFL_GENESIS").hexdigest()
        self.assertEqual(GENESIS_CONSTANT, expected)

    def test_first_record_prev_hash(self):
        chain = _make_chain(1)
        rec = chain.records[0]
        self.assertEqual(rec["prev_hash"], f"sha256:{GENESIS_CONSTANT}")


class TestChainVerification(unittest.TestCase):
    def test_valid_chain(self):
        chain = _make_chain(10)
        valid, msg = chain.verify_chain()
        self.assertTrue(valid, msg)

    def test_empty_chain(self):
        chain = VerificationChain()
        valid, msg = chain.verify_chain()
        self.assertTrue(valid)
        self.assertIn("empty", msg.lower())

    def test_single_record_chain(self):
        chain = _make_chain(1)
        valid, msg = chain.verify_chain()
        self.assertTrue(valid, msg)

    def test_verify_single_record(self):
        chain = _make_chain(5)
        for i in range(5):
            valid, msg = chain.verify_record(i)
            self.assertTrue(valid, f"Record {i}: {msg}")

    def test_verify_record_out_of_range(self):
        chain = _make_chain(3)
        valid, msg = chain.verify_record(10)
        self.assertFalse(valid)
        self.assertIn("out of range", msg)


class TestHead(unittest.TestCase):
    def test_head_empty(self):
        chain = VerificationChain()
        self.assertIsNone(chain.head())

    def test_head_returns_latest(self):
        chain = _make_chain(3)
        h = chain.head()
        self.assertEqual(h["sealed_body"]["seq"], 2)


class TestSchemaVersion(unittest.TestCase):
    def test_schema_version_in_records(self):
        chain = _make_chain(1)
        self.assertEqual(chain.records[0]["sealed_body"]["schema_version"],
                         SCHEMA_VERSION)


class TestDigestBytes(unittest.TestCase):
    def test_valid_digest(self):
        hex_val = "abcdef0123456789" * 4
        result = _digest_bytes(f"sha256:{hex_val}")
        self.assertEqual(result, bytes.fromhex(hex_val))

    def test_invalid_prefix(self):
        with self.assertRaises(ValueError):
            _digest_bytes("md5:abcdef")


class TestHashBytesNotStrings(unittest.TestCase):
    """Confirm chain_hash is computed from hash bytes, not string concat."""

    def test_chain_hash_uses_bytes(self):
        chain = _make_chain(2)
        rec = chain.records[1]
        prev_bytes = _digest_bytes(rec["prev_hash"])
        entry_bytes = _digest_bytes(rec["entry_hash"])
        expected = "sha256:" + hashlib.sha256(prev_bytes + entry_bytes).hexdigest()
        self.assertEqual(rec["chain_hash"], expected)


class TestSignature(unittest.TestCase):
    """Signature presence (without requiring cryptography library)."""

    def test_no_signer_claimed_only(self):
        chain = _make_chain(1)
        sig = chain.records[0]["signature"]
        self.assertEqual(sig["attribution"], "claimed_only")
        self.assertIsNone(sig["algorithm"])

    def test_signer_requires_crypto_library(self):
        """If cryptography is available, test signing; otherwise skip."""
        try:
            from verification_chain import Signer, _HAS_CRYPTO
            if not _HAS_CRYPTO:
                self.skipTest("cryptography library not installed")
            from cryptography.hazmat.primitives.asymmetric.ed25519 import (
                Ed25519PrivateKey,
            )
            key = Ed25519PrivateKey.generate()
            signer = Signer(key, "test-key-001")
            chain = VerificationChain(signer=signer)
            rec = chain.append_record("finding", {"x": 1}, "CC2",
                                      timestamp="2026-01-01T00:00:00Z")
            sig = rec["signature"]
            self.assertEqual(sig["algorithm"], "Ed25519")
            self.assertEqual(sig["key_id"], "test-key-001")
            self.assertEqual(sig["attribution"], "authenticated")
            self.assertIsNotNone(sig["signature"])
        except ImportError:
            self.skipTest("cryptography library not installed")


class TestCLI(unittest.TestCase):
    """CLI exit codes and basic functionality."""

    def test_no_command_returns_1(self):
        rc = main([])
        self.assertEqual(rc, 1)

    def test_record_creates_file(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        os.unlink(path)  # Let the CLI create it
        try:
            rc = main([
                "record", "--type", "finding", "--by", "test",
                "--payload", '{"x": 1}', "--chain", path,
            ])
            self.assertEqual(rc, 0)
            self.assertTrue(os.path.exists(path))
        finally:
            if os.path.exists(path):
                os.unlink(path)

    def test_verify_chain_valid(self):
        chain = _make_chain(3)
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            chain.save_json(path)
            rc = main(["verify-chain", path])
            self.assertEqual(rc, 0)
        finally:
            os.unlink(path)

    def test_verify_chain_invalid(self):
        chain = _make_chain(3)
        chain._records[1]["sealed_body"]["timestamp_utc"] = "2099-01-01T00:00:00Z"
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            chain.save_json(path)
            rc = main(["verify-chain", path])
            self.assertEqual(rc, 1)
        finally:
            os.unlink(path)

    def test_verify_record_valid(self):
        chain = _make_chain(3)
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            chain.save_json(path)
            rc = main(["verify-record", path, "--index", "1"])
            self.assertEqual(rc, 0)
        finally:
            os.unlink(path)

    def test_verify_record_invalid(self):
        chain = _make_chain(3)
        chain._records[0]["sealed_body"]["payload"]["value"] = 999
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            chain.save_json(path)
            rc = main(["verify-record", path, "--index", "0"])
            self.assertEqual(rc, 1)
        finally:
            os.unlink(path)

    def test_seal_epoch_cli(self):
        chain = _make_chain(3)
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            chain.save_json(path)
            rc = main(["seal-epoch", path])
            self.assertEqual(rc, 0)
            reloaded = VerificationChain.load_json(path)
            self.assertEqual(len(reloaded.epochs), 1)
        finally:
            os.unlink(path)

    def test_show_head_cli(self):
        chain = _make_chain(2)
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            chain.save_json(path)
            rc = main(["show-head", path])
            self.assertEqual(rc, 0)
        finally:
            os.unlink(path)

    def test_prove_and_verify_proof_cli(self):
        chain = _make_chain(4)
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            chain_path = f.name
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            proof_path = f.name
        try:
            chain.save_json(chain_path)

            # Build proof via API (CLI prove-record prints to stdout)
            proof = chain.build_inclusion_proof(2)
            with open(proof_path, "w") as f:
                json.dump(proof, f)

            epoch = chain.seal_epoch()
            rc = main(["verify-proof", proof_path, "--root",
                        epoch["merkle_root"]])
            self.assertEqual(rc, 0)
        finally:
            os.unlink(chain_path)
            os.unlink(proof_path)

    def test_verify_proof_invalid_root(self):
        chain = _make_chain(4)
        proof = chain.build_inclusion_proof(1)
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            proof_path = f.name
        try:
            with open(proof_path, "w") as f:
                json.dump(proof, f)
            rc = main(["verify-proof", proof_path, "--root", "00" * 32])
            self.assertEqual(rc, 1)
        finally:
            os.unlink(proof_path)

    def test_record_appends_to_existing(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        os.unlink(path)
        try:
            # First record
            main(["record", "--type", "finding", "--by", "CC2",
                  "--payload", '{"step": 1}', "--chain", path])
            # Second record
            main(["record", "--type", "solution", "--by", "CX",
                  "--payload", '{"step": 2}', "--chain", path])
            loaded = VerificationChain.load_json(path)
            self.assertEqual(len(loaded.records), 2)
            valid, msg = loaded.verify_chain()
            self.assertTrue(valid, msg)
        finally:
            if os.path.exists(path):
                os.unlink(path)

    def test_record_hash_only_mode(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        os.unlink(path)
        try:
            rc = main(["record", "--type", "finding", "--by", "CC2",
                        "--payload", '{"data": "test"}',
                        "--mode", "hash_only", "--chain", path])
            self.assertEqual(rc, 0)
            loaded = VerificationChain.load_json(path)
            self.assertEqual(
                loaded.records[0]["sealed_body"]["storage_mode"], "hash_only"
            )
        finally:
            if os.path.exists(path):
                os.unlink(path)


class TestEdgeCases(unittest.TestCase):
    """Miscellaneous edge cases."""

    def test_null_payload(self):
        chain = VerificationChain()
        rec = chain.append_record("finding", None, "test",
                                  timestamp="2026-01-01T00:00:00Z")
        valid, msg = chain.verify_chain()
        self.assertTrue(valid, msg)

    def test_large_payload(self):
        chain = VerificationChain()
        big = {"data": "x" * 100_000}
        chain.append_record("finding", big, "test",
                            timestamp="2026-01-01T00:00:00Z")
        valid, msg = chain.verify_chain()
        self.assertTrue(valid, msg)

    def test_nested_payload(self):
        chain = VerificationChain()
        nested = {"a": {"b": {"c": [1, 2, {"d": True}]}}}
        chain.append_record("finding", nested, "test",
                            timestamp="2026-01-01T00:00:00Z")
        valid, msg = chain.verify_chain()
        self.assertTrue(valid, msg)

    def test_metadata_included_in_hash(self):
        c1 = VerificationChain()
        r1 = c1.append_record("finding", {"x": 1}, "test",
                              metadata={"tag": "a"},
                              timestamp="2026-01-01T00:00:00Z")
        c2 = VerificationChain()
        r2 = c2.append_record("finding", {"x": 1}, "test",
                              metadata={"tag": "b"},
                              timestamp="2026-01-01T00:00:00Z")
        self.assertNotEqual(r1["entry_hash"], r2["entry_hash"])

    def test_seq_field_is_zero_indexed(self):
        chain = _make_chain(5)
        for i in range(5):
            self.assertEqual(chain.records[i]["sealed_body"]["seq"], i)

    def test_chain_hash_changes_with_history(self):
        """Two records with identical sealed bodies at different positions
        produce different chain_hashes because prev_hash differs."""
        chain = VerificationChain()
        r0 = chain.append_record("finding", {"x": 0}, "test",
                                 timestamp="2026-01-01T00:00:00Z")
        r1 = chain.append_record("finding", {"x": 0}, "test",
                                 timestamp="2026-01-01T00:00:00Z")
        # entry_hash will differ (different seq), so chain_hash differs anyway.
        # But even if we could force same entry_hash, prev_hash differs.
        self.assertNotEqual(r0["chain_hash"], r1["chain_hash"])


class TestRunnerIntegration(unittest.TestCase):
    """Verify run_round_robin.py imports from the canonical module."""

    def test_runner_uses_canonical_chain(self):
        """The runner's VerificationChain must delegate to the canonical module."""
        runner_path = os.path.join(os.path.dirname(__file__), "..", "run_round_robin.py")
        with open(runner_path, "r") as f:
            source = f.read()
        # Must import from verification_chain, not define its own hashing
        self.assertIn("from verification_chain import", source)
        # Must NOT have the old string-concatenation hashing
        self.assertNotIn('f"{prev_hash}:{content_hash}"', source)
        self.assertNotIn('f"{left}:{right}"', source)


class TestSwappedChainHash(unittest.TestCase):
    """Swapping chain_hash values between records must be detected."""

    def test_swap_chain_hashes_detected(self):
        chain = _make_chain(4)
        # Swap chain_hash of records 1 and 2
        chain._records[1]["chain_hash"], chain._records[2]["chain_hash"] = (
            chain._records[2]["chain_hash"], chain._records[1]["chain_hash"]
        )
        valid, msg = chain.verify_chain()
        self.assertFalse(valid)


class TestEpochVerification(unittest.TestCase):
    """Epoch Merkle root verification."""

    def test_valid_epoch_passes_verify(self):
        chain = _make_chain(5)
        chain.seal_epoch()
        valid, msg = chain.verify_chain()
        self.assertTrue(valid, msg)

    def test_tampered_epoch_root_detected(self):
        chain = _make_chain(5)
        chain.seal_epoch()
        chain._epochs[0]["merkle_root"] = "sha256:" + "ff" * 32
        valid, msg = chain.verify_chain()
        self.assertFalse(valid)
        self.assertIn("merkle_root mismatch", msg)

    def test_tampered_epoch_record_count(self):
        chain = _make_chain(5)
        chain.seal_epoch()
        chain._epochs[0]["record_count"] = 3
        valid, msg = chain.verify_chain()
        self.assertFalse(valid)
        self.assertIn("merkle_root mismatch", msg)


class TestMalformedProof(unittest.TestCase):
    """Malformed proof inputs should return False, not raise."""

    def test_malformed_proof_step(self):
        result = rfc9162_verify_inclusion(
            b"test", [{"bad_key": "no_hash"}], b"\x00" * 32
        )
        self.assertFalse(result)

    def test_invalid_hex_in_proof(self):
        result = rfc9162_verify_inclusion(
            b"test", [{"hash": "not_hex", "side": "right"}], b"\x00" * 32
        )
        self.assertFalse(result)

    def test_malformed_root_in_verify_inclusion_proof(self):
        chain = _make_chain(3)
        proof = chain.build_inclusion_proof(1)
        # Pass a root that can't be parsed
        self.assertFalse(chain.verify_inclusion_proof(proof, "garbage"))


class TestSignatureVerification(unittest.TestCase):
    """Signature verification integration (requires cryptography library)."""

    def test_valid_signature_verified(self):
        try:
            from verification_chain import Signer, Verifier, _HAS_CRYPTO
            if not _HAS_CRYPTO:
                self.skipTest("cryptography library not installed")
            from cryptography.hazmat.primitives.asymmetric.ed25519 import (
                Ed25519PrivateKey,
            )
            key = Ed25519PrivateKey.generate()
            signer = Signer(key, "test-key")
            verifier = Verifier(key.public_key())

            chain = VerificationChain(signer=signer)
            chain.append_record("finding", {"x": 1}, "CC2",
                                timestamp="2026-01-01T00:00:00Z")
            valid, msg = chain.verify_chain(verifier=verifier)
            self.assertTrue(valid, msg)
        except ImportError:
            self.skipTest("cryptography library not installed")

    def test_corrupted_signature_detected(self):
        try:
            from verification_chain import Signer, Verifier, _HAS_CRYPTO
            if not _HAS_CRYPTO:
                self.skipTest("cryptography library not installed")
            from cryptography.hazmat.primitives.asymmetric.ed25519 import (
                Ed25519PrivateKey,
            )
            import base64

            key = Ed25519PrivateKey.generate()
            signer = Signer(key, "test-key")
            verifier = Verifier(key.public_key())

            chain = VerificationChain(signer=signer)
            chain.append_record("finding", {"x": 1}, "CC2",
                                timestamp="2026-01-01T00:00:00Z")
            # Corrupt the signature
            chain._records[0]["signature"]["signature"] = base64.b64encode(
                b"\x00" * 64
            ).decode("ascii")
            valid, msg = chain.verify_chain(verifier=verifier)
            self.assertFalse(valid)
            self.assertIn("signature verification failed", msg)
        except ImportError:
            self.skipTest("cryptography library not installed")

    def test_wrong_key_detected(self):
        try:
            from verification_chain import Signer, Verifier, _HAS_CRYPTO
            if not _HAS_CRYPTO:
                self.skipTest("cryptography library not installed")
            from cryptography.hazmat.primitives.asymmetric.ed25519 import (
                Ed25519PrivateKey,
            )

            sign_key = Ed25519PrivateKey.generate()
            wrong_key = Ed25519PrivateKey.generate()
            signer = Signer(sign_key, "key-a")
            verifier = Verifier(wrong_key.public_key())

            chain = VerificationChain(signer=signer)
            chain.append_record("finding", {"x": 1}, "CC2",
                                timestamp="2026-01-01T00:00:00Z")
            valid, msg = chain.verify_chain(verifier=verifier)
            self.assertFalse(valid)
            self.assertIn("signature verification failed", msg)
        except ImportError:
            self.skipTest("cryptography library not installed")


if __name__ == "__main__":
    unittest.main()
