### RESEARCH_FINDINGS
- The current public transparency-log reference is [RFC 9162](https://www.rfc-editor.org/rfc/rfc9162.html), published in December 2021 and explicitly obsoleting RFC 6962. Its main implementation takeaways are: ordered append-only logs, binary Merkle trees, inclusion proofs, consistency proofs, and algorithm agility.
- For hashing and signing JSON, the best standard reference is [RFC 8785](https://www.rfc-editor.org/rfc/rfc8785). It recommends canonical JSON before cryptographic use; that is the cleanest way to make independent recomputation work.
- For timestamps, use RFC 3339-compatible UTC strings such as `2026-03-28T14:05:12Z` rather than ad hoc formatting. Source: [RFC 3339](https://datatracker.ietf.org/doc/html/rfc3339.html).
- For Python primitives, keep the base dependency light: `hashlib.sha256()` is guaranteed in Python’s stdlib and is the right default for Layer 1-3 hashing. Source: [Python hashlib docs](https://docs.python.org/3/library/hashlib.html).
- For optional signatures, Ed25519 is the sane default. The official `cryptography` docs say to strongly consider it when legacy interoperability is not required. Source: [cryptography Ed25519 docs](https://cryptography.io/en/latest/hazmat/primitives/asymmetric/ed25519/).
- For provenance-style record structure, there is no standard “reasoning checkpoint” schema, but [W3C PROV-DM](https://www.w3.org/TR/2013/REC-prov-dm-20130430/) is the closest fit: it models entities, activities, agents, time, derivations, and “provenance of provenance,” which maps well to checkpoints and later verification records.
- On Merkle libraries, the ecosystem is fragmented. `pymerkle` is the most relevant Python reference I found because it supports inclusion and consistency proofs and says its topology is essentially RFC 9162-style, but its docs also say it “requires security review,” and PyPI lists GPLv3 licensing. That makes it a good design reference, not a dependency I would take by default. Sources: [pymerkle docs](https://pymerkle.readthedocs.io/en/latest/), [PyPI](https://pypi.org/project/pymerkle/).
- Inference from the standards above: sparse Merkle trees are not the right default here. They are mainly for keyed state maps and non-membership proofs. CDSFL Layer 3 is an ordered append-only batch log, so a standard ordered binary Merkle tree is the better fit.

### EXISTING_ASSESSMENT
- The CE implementation in [run_round_robin.py](/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/run_round_robin.py#L217) gets the layering right and is pleasantly small, but it is not a portable record store yet. The biggest gaps are that the stored entry omits raw `content`, and the `timestamp` is not included in the hashed payload, so “what” and “when” are not fully sealed in the exported chain.
- The Genesis implementation in [file_integrity.py](/Users/georgejackson/Developer_Projects/Project_Genesis/cw_handoff/file_integrity.py#L1) is stronger operationally: optional Ed25519, compact canonical JSON, CLI, graceful degradation, and a good test matrix in [test_file_integrity.py](/Users/georgejackson/Developer_Projects/Project_Genesis/cw_handoff/test_file_integrity.py#L1). That part is reusable.
- Genesis is still the wrong module to lift directly. It is file-path-centric, tied to OB key locations and OB anchoring, and its unsigned mode still counts entries as “valid,” which is fine for migration but too loose for a reusable CDSFL verification module.
- The Genesis Merkle helper in [merkle.py](/Users/georgejackson/Developer_Projects/Project_Genesis/src/genesis/crypto/merkle.py#L50) is useful as proof-shape inspiration, but its sorted-leaf policy should not be reused for CDSFL epochs. Audit logs should preserve append order, not normalize it away.

### PROPOSED_ARCHITECTURE
- Use a small package, not one giant file:
  `bench/persistence/__init__.py`, `models.py`, `canonical.py`, `merkle.py`, `signing.py`, `verification_chain.py`, `cli.py`.
- Public API lives in `verification_chain.py`:
  `VerificationChain.load_json()`, `save_json()`, `append_record()`, `seal_epoch()`, `verify_chain()`, `verify_record()`, `build_inclusion_proof()`, `verify_inclusion_proof()`.
- Record format should be self-contained and hash the full semantic body, not just content text:
  `schema_version`, `record_id`, `record_type`, `recorded_by`, `recorded_at`, `payload`, `links`, `context_dependencies`.
  Derived fields live alongside it:
  `content_hash`, `prev_hash`, `chain_hash`, optional `signature`.
- Reasoning checkpoints are just a `record_type="reasoning_checkpoint"` payload with fields for `plan_state`, `progress`, `rationale`, `hypotheses`, `key_decisions`, and `context_dependencies`. That matches Part V without pretending to store sub-token internals.
- Hashing rules:
  canonicalize JSON first; hash bytes, not ad hoc Python repr; include timestamp and claimed source inside the hashed record body; prefix digests as `sha256:<hex>` for clarity and future agility.
- Merkle rules:
  default to an ordered RFC 9162-style binary tree for new epochs; leaves are the ordered `chain_hash` values for the sealed contiguous batch. Generate inclusion proofs in v1. Keep the API compatible with future consistency proofs, but do not make cumulative CT-style roots mandatory now because Layer 2 already provides append-only ordering.
- Optional Ed25519:
  if a signer is configured, sign the canonical record body and store `algorithm`, `key_id`, and `signature`. If not, the module must explicitly report attribution as `claimed_only`, not `authenticated`.
- Serialization:
  one portable JSON snapshot for import/export. If later you want an append-only JSONL journal, add it as a backend, not as the canonical interchange format.
- CLI:
  `record`, `verify-chain`, `verify-record`, `seal-epoch`, `prove-record`, `verify-proof`, `show-head`. Output JSON and use exit code `1` on verification failure.
- Documentation must say this plainly:
  proves content integrity, ordering, epoch inclusion, and authenticated source only when signatures are present; does not prove genuine reasoning, correctness, or trusted wall-clock accuracy.

### PLAYER_BRIEF
- CC2 should own the core implementation: package layout, canonical JSON, record dataclasses, chain append/load/save, epoch sealing, CLI, and the unsigned/signed verification reports.
- Gemini should own cryptographic correctness review: verify the hash-domain choices, Merkle proof logic, failure cases, and the wording of the “proves / does not prove” documentation. If any part is mathematically shaky, Gemini should block it early.
- Shared interfaces to implement first:
  `VerificationRecord`, `EpochSeal`, `MerkleInclusionProof`, `RecordVerificationReport`, `ChainVerificationReport`, `Signer`.
- Minimum tests:
  deterministic canonicalization; hash changes on any semantic change; timestamp tamper detection; chain break on deletion/insertion/reordering; JSON round-trip; inclusion proof valid/invalid; empty/single/odd leaf epochs; signed and unsigned modes; wrong-key signature failure; CLI exit-code behavior.
- Nice-to-have, not v1-critical:
  legacy import adapter for current CE outputs; cumulative-root mode for future Genesis anchoring; JSONL backend.

### CONSTRAINT_CLASSIFICATION
- HARD: standalone from `run_round_robin.py` and Genesis; reusable importable module; Layers 1-3 implemented; JSON load/save; reasoning-checkpoint support; chain verification; Merkle proof generation; optional Ed25519 with graceful unsigned mode; explicit Part VI limits.
- SOFT: exact package layout; whether to ship one file or a package; whether to support legacy CE hash mode immediately; whether to add JSONL backend now; whether to expose cumulative-root consistency proofs in v1.

### STRONGEST_OBJECTION
- Objection: optional Ed25519 weakens the claim that the system proves “who recorded it.”
- Response: that objection is correct, so the module should not hide it. In unsigned mode, the system proves that a record claiming to be from `CX` was stored untampered in order; it does not cryptographically prove that `CX` authored it. The API and docs should surface `claimed_only` versus `authenticated` attribution explicitly.

No files were changed.