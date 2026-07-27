"""Falsifier for the finding:

    EvidenceStore.verify_bundle provides no cryptographic authentication
    because it does not validate the bundle's Merkle root against any
    trusted anchor.

Strategy: build a legitimate EvidenceStore backed by a REAL chain that
commits to a genuine Merkle root R_real. Then hand verify_bundle a
FORGED EvidenceBundle whose records/chain_hashes never appeared in that
chain, with a self-consistent forged root R_fake != R_real and inclusion
proofs built against R_fake. If verify_bundle returns (True, []) despite
R_fake bearing no relationship to the store's trusted chain, the method
authenticates nothing — the defect is present.
"""

import importlib.util
from pathlib import Path

# --- Import the REAL modules by absolute path (no reliance on cwd/sys.path) ---
REPO = Path("/Users/georgejackson/Developer_Projects/Constraint_Engineering")

def _load(mod_name, rel):
    spec = importlib.util.spec_from_file_location(mod_name, REPO / rel)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

# evidence.py imports `bench.verification_chain`, so load via the package path.
import sys
sys.path.insert(0, str(REPO))
from bench.evidence import EvidenceStore, EvidenceBundle
from bench.verification_chain import (
    VerificationChain,
    rfc9162_merkle_root,
    rfc9162_inclusion_proof,
    _digest_bytes,
)

# --- 1. Build a REAL chain with a genuine, trusted Merkle root ------------
chain = VerificationChain()
for k in range(3):
    chain.append_record(
        artifact_type="experiment_report",
        payload={"real": k, "note": "genuine sealed record"},
        recorded_by="cc1",
        metadata={"experiment": "real_exp", "round": k},
    )
store = EvidenceStore(chain, experiment_name="real_exp")

real_leaves = [_digest_bytes(r["chain_hash"]) for r in chain.records]
R_real = "sha256:" + rfc9162_merkle_root(real_leaves).hex()

# --- 2. Fabricate records that were NEVER in the chain --------------------
# Attacker invents arbitrary chain_hashes / payloads.
forged_records = []
for k in range(3):
    forged_records.append({
        "chain_hash": "sha256:" + ("%064x" % (0xdead0000 + k)),
        "sealed_body": {
            "seq": k,
            "artifact_type": "experiment_report",
            "payload": {"FORGED": True, "claim": f"fabricated evidence #{k}"},
            "recorded_by": "attacker",
        },
    })

# --- 3. Compute a self-consistent forged root + proofs over the forgeries -
forged_leaves = [_digest_bytes(r["chain_hash"]) for r in forged_records]
R_fake = "sha256:" + rfc9162_merkle_root(forged_leaves).hex()

forged_proofs = []
for i, r in enumerate(forged_records):
    steps = rfc9162_inclusion_proof(forged_leaves, i)
    forged_proofs.append({
        "chain_hash": r["chain_hash"],
        "proof": steps,
        "merkle_root": R_fake,
    })

# Sanity: the forged root must differ from the store's trusted root,
# otherwise the demonstration would be vacuous.
assert R_fake != R_real, "test setup broken: forged root collided with real root"

forged_bundle = EvidenceBundle(
    experiment="real_exp",
    created_at="2026-07-27T00:00:00Z",
    merkle_root=R_fake,                # attacker-chosen; no trusted anchor
    records=forged_records,
    inclusion_proofs=forged_proofs,
    chain_metadata={"note": "entirely fabricated by attacker"},
)

# --- 4. Reach the real buggy path ----------------------------------------
all_valid, errors = store.verify_bundle(forged_bundle)

print(f"trusted store root R_real = {R_real}")
print(f"forged  bundle root R_fake = {R_fake}")
print(f"verify_bundle -> all_valid={all_valid}, errors={errors}")

# --- 5. Verdict ----------------------------------------------------------
if all_valid and not errors:
    print("FALSIFIED: verify_bundle accepted a wholly fabricated bundle whose "
          "root is unrelated to the store's trusted chain. No cryptographic "
          "authentication — the Merkle root is never checked against any anchor.")
    raise AssertionError(
        "verify_bundle authenticated a forged, un-anchored bundle (defect present)"
    )
else:
    print("CLEAN: verify_bundle rejected the forged bundle — root is anchored.")
