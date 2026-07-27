"""Falsifier for the finding:

    EvidenceStore.verify_bundle provides no cryptographic authentication
    because it does not validate the bundle's Merkle root against any
    trusted anchor.

Strategy
--------
1. Build a LEGITIMATE store over a real VerificationChain (the trusted
   verifier's data). Snapshot its trusted Merkle root.
2. Have an ATTACKER build a completely SEPARATE chain over fabricated
   records that were never sealed into the legitimate store, and export
   a self-consistent EvidenceBundle from it (its own root + valid
   inclusion proofs against that root).
3. Feed the forged bundle to the LEGITIMATE store's verify_bundle().

If verify_bundle returns (True, []) for a bundle whose root differs from
the store's trusted root and whose records are absent from the store,
then authentication is purely self-referential -> defect present.
"""

import importlib.util
import os

# --- Import the REAL modules by absolute path ------------------------------
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
EVID_PATH = os.path.join(REPO, "bench", "evidence.py")

# Ensure `import bench.*` works for the real package (evidence.py does
# `from bench.verification_chain import ...`).
import sys
if REPO not in sys.path:
    sys.path.insert(0, REPO)

spec = importlib.util.spec_from_file_location("bench.evidence", EVID_PATH)
evidence = importlib.util.module_from_spec(spec)
sys.modules["bench.evidence"] = evidence
spec.loader.exec_module(evidence)

EvidenceStore = evidence.EvidenceStore
from bench.verification_chain import VerificationChain

print("Loaded EvidenceStore from:", evidence.__file__)


def build_chain(tag, n=3):
    chain = VerificationChain()  # no signer -> attribution "claimed_only"
    for i in range(n):
        chain.append_record(
            artifact_type="finding_report",
            payload={"finding_id": f"{tag}{i:04d}", "verdict": "CONFIRMED"},
            recorded_by=f"{tag}-model",
            metadata={"round": i},
        )
    return chain


# --- 1. Legitimate, trusted store ------------------------------------------
legit_chain = build_chain("REAL", n=3)
legit_store = EvidenceStore(legit_chain, experiment_name="legit-exp")
legit_bundle = legit_store.export_bundle(record_indices=[0, 1, 2])

# SNAPSHOT the store's trusted root and its real record hashes BEFORE any
# verification call (verify_bundle is read-only, but we snapshot to prove
# the forged data never touches trusted state).
trusted_root = legit_store.summary().merkle_root
trusted_hashes = {r["chain_hash"] for r in legit_chain.records}

# Sanity: the legit bundle verifies against its own store.
ok_real, err_real = legit_store.verify_bundle(legit_bundle)
assert ok_real and not err_real, f"legit bundle should verify: {err_real}"

# --- 2. Attacker forges a wholly separate bundle ---------------------------
attacker_chain = build_chain("FORGED", n=3)
attacker_store = EvidenceStore(attacker_chain, experiment_name="attacker-exp")
forged_bundle = attacker_store.export_bundle(record_indices=[0, 1, 2])

# The forged bundle carries its OWN self-consistent root, different from the
# trusted store's root, and its records were never in the legit chain.
forged_root = forged_bundle.merkle_root
forged_hashes = {r["chain_hash"] for r in forged_bundle.records}

assert forged_root != trusted_root, (
    "test setup invalid: forged root coincidentally equals trusted root"
)
assert forged_hashes.isdisjoint(trusted_hashes), (
    "test setup invalid: forged records overlap trusted records"
)

# --- 3. Feed the forged bundle to the TRUSTED store ------------------------
ok_forged, err_forged = legit_store.verify_bundle(forged_bundle)

# Confirm trusted state was not mutated by the verification call.
assert legit_store.summary().merkle_root == trusted_root, "store root mutated!"

print(f"trusted_root : {trusted_root[:26]}...")
print(f"forged_root  : {forged_root[:26]}...  (differs from trusted)")
print(f"forged records in trusted chain? {not forged_hashes.isdisjoint(trusted_hashes)}")
print(f"verify_bundle(forged) -> ok={ok_forged}, errors={err_forged}")

if ok_forged and not err_forged:
    print(
        "FALSIFIED: verify_bundle accepted a forged bundle whose Merkle root "
        "({}) differs from the store's trusted root ({}) and whose records "
        "were never sealed into the store. It authenticates the bundle only "
        "against the bundle's OWN embedded root — no trusted anchor is "
        "consulted.".format(forged_root[:20] + "...", trusted_root[:20] + "...")
    )
    raise AssertionError(
        "verify_bundle provides no cryptographic authentication: forged "
        "bundle accepted with no trusted-anchor validation."
    )
else:
    print("Defect ABSENT: verify_bundle rejected the forged bundle.")
