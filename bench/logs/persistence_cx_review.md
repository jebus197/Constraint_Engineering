### FINDING_1
- **CATEGORY**: Specification
- **SEVERITY**: BLOCKING
- **DESCRIPTION**: A7 is not implemented. [run_round_robin.py](/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/run_round_robin.py#L250) still defines its own `VerificationChain`, and it still uses legacy string-concatenation hashing at [run_round_robin.py](/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/run_round_robin.py#L222) and duplicate-last Merkle logic at [run_round_robin.py](/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/run_round_robin.py#L229). That leaves two incompatible implementations in the repo, so the bench runner will not actually exercise the new canonical module.
- **FIX**: Remove the inline helpers/class from `run_round_robin.py`, import `VerificationChain` from `bench/verification_chain.py`, and add a regression test that fails if the runner reintroduces a local chain class.
- **CONSTRAINT_CLASS**: HARD

### FINDING_2
- **CATEGORY**: Specification
- **SEVERITY**: BLOCKING
- **DESCRIPTION**: A5 says serialized Merkle roots must be `sha256:<hex>`, but the module emits bare hex instead at [verification_chain.py](/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/verification_chain.py#L428) and [verification_chain.py](/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/verification_chain.py#L465), and the verifier/CLI parse bare hex at [verification_chain.py](/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/verification_chain.py#L471) and [verification_chain.py](/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/verification_chain.py#L636). The tests currently lock in the wrong format at [test_verification_chain.py](/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/tests/test_verification_chain.py#L264) and [test_verification_chain.py](/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/tests/test_verification_chain.py#L297).
- **FIX**: Serialize roots with `sha256_digest(root_bytes)`, parse them with `_digest_bytes`, update CLI help/messages, and rewrite the affected tests to expect the prefixed form.
- **CONSTRAINT_CLASS**: HARD

### FINDING_3
- **CATEGORY**: Correctness
- **SEVERITY**: IMPORTANT
- **DESCRIPTION**: Epoch data is persisted but not verified. `verify_chain()` ignores `_epochs` entirely at [verification_chain.py](/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/verification_chain.py#L434), so a falsified stored epoch root or `record_count` is accepted. Separately, `build_inclusion_proof()` always uses the full current record set at [verification_chain.py](/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/verification_chain.py#L458), so after later appends it cannot rebuild a proof for an earlier sealed epoch.
- **FIX**: Add epoch verification that recomputes each stored epoch root from the recorded cutoff, and add an epoch-bound proof API such as `build_inclusion_proof(index, epoch_index)` so proofs can target historical sealed epochs.
- **CONSTRAINT_CLASS**: HARD

### FINDING_4
- **CATEGORY**: Correctness
- **SEVERITY**: BLOCKING
- **DESCRIPTION**: Signed mode is write-only. Records are signed at [verification_chain.py](/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/verification_chain.py#L396), but neither `verify_chain()` nor `verify_record()` checks signatures at [verification_chain.py](/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/verification_chain.py#L434) and [verification_chain.py](/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/verification_chain.py#L446). `Verifier` exists at [verification_chain.py](/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/verification_chain.py#L111) but is unused. In practice, corrupting a record signature still leaves `verify_chain()` green.
- **FIX**: Either implement public signature verification now, or remove/defer the authenticated-signing claim for v1. The clean fix is `verify_record_signature()` plus optional signature checking in `verify_record()`/`verify_chain()`, with tests for valid signature, corrupted signature, wrong key, and missing signature.
- **CONSTRAINT_CLASS**: HARD

### FINDING_5
- **CATEGORY**: Correctness
- **SEVERITY**: IMPORTANT
- **DESCRIPTION**: Proof verification is not robust against malformed input. `rfc9162_verify_inclusion()` assumes every proof step has valid hex and required keys at [verification_chain.py](/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/verification_chain.py#L279), so malformed proofs raise exceptions instead of returning `False`. The same problem propagates through `verify_inclusion_proof()` at [verification_chain.py](/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/verification_chain.py#L468) and `_cli_verify_proof()` at [verification_chain.py](/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/verification_chain.py#L629).
- **FIX**: Treat malformed proof structures, bad hex, and invalid roots as verification failure, not uncaught exceptions. The CLI should convert those cases into a clean stderr message and a non-zero exit code.
- **CONSTRAINT_CLASS**: HARD

### FINDING_6
- **CATEGORY**: Test Coverage
- **SEVERITY**: IMPORTANT
- **DESCRIPTION**: A8 is only partially covered. The adopted test plan says the runner should import the module instead of defining its own class, but [test_verification_chain.py](/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/tests/test_verification_chain.py) never exercises `run_round_robin.py`, so the A7/A8 regression slipped through. The suite also misses the highest-value negative cases around the actual gaps above: signature tampering, epoch tampering, historical-epoch proofs, malformed proof/root input, and the specific attack you called out of swapping stored `chain_hash` values between records.
- **FIX**: Add runner-integration coverage, plus negative tests for signature corruption, swapped `chain_hash` fields, tampered epoch metadata, malformed proofs, and proofs built against historical epochs.
- **CONSTRAINT_CLASS**: HARD

### FINDING_7
- **CATEGORY**: Integration
- **SEVERITY**: MINOR
- **DESCRIPTION**: `__all__` at [verification_chain.py](/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/verification_chain.py#L55) omits `Signer` and `Verifier`, even though signing is part of the advertised feature set and those classes are defined at [verification_chain.py](/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/verification_chain.py#L89) and [verification_chain.py](/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/verification_chain.py#L111).
- **FIX**: Export `Signer` and `Verifier` if signed mode remains public in v1. If signing is deferred, remove the public-facing signing surface instead of leaving it half-exposed.
- **CONSTRAINT_CLASS**: SOFT

### SUMMARY
Not ready for integration yet. A1-A4 and A6 are mostly in good shape, JSON save/load preserves the persisted record and epoch data, and Gemini’s four actionable documentation findings are incorporated in [verification_chain.py](/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/verification_chain.py). The blockers are the unintegrated runner, the A5 root-format drift, and the fact that signed mode is claimed but not actually verified.

I also ran the test suite with `python3 -m unittest bench.tests.test_verification_chain`. The logic tests mostly passed, but 13 file-based tests could not run in this sandbox because there is no usable writable temp directory here, so I treated those errors as environment-limited rather than product findings.

### BLOCKING_ISSUES
- `run_round_robin.py` must stop defining its own verification chain and import the canonical module.
- Merkle roots must be serialized and parsed as `sha256:<hex>` to match A5.
- Signed mode must either gain real verification support or be explicitly removed/deferred from the v1 contract.
tokens used
104,215
### FINDING_1
- **CATEGORY**: Specification
- **SEVERITY**: BLOCKING
- **DESCRIPTION**: A7 is not implemented. [run_round_robin.py](/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/run_round_robin.py#L250) still defines its own `VerificationChain`, and it still uses legacy string-concatenation hashing at [run_round_robin.py](/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/run_round_robin.py#L222) and duplicate-last Merkle logic at [run_round_robin.py](/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/run_round_robin.py#L229). That leaves two incompatible implementations in the repo, so the bench runner will not actually exercise the new canonical module.
- **FIX**: Remove the inline helpers/class from `run_round_robin.py`, import `VerificationChain` from `bench/verification_chain.py`, and add a regression test that fails if the runner reintroduces a local chain class.
- **CONSTRAINT_CLASS**: HARD

### FINDING_2
- **CATEGORY**: Specification
- **SEVERITY**: BLOCKING
- **DESCRIPTION**: A5 says serialized Merkle roots must be `sha256:<hex>`, but the module emits bare hex instead at [verification_chain.py](/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/verification_chain.py#L428) and [verification_chain.py](/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/verification_chain.py#L465), and the verifier/CLI parse bare hex at [verification_chain.py](/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/verification_chain.py#L471) and [verification_chain.py](/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/verification_chain.py#L636). The tests currently lock in the wrong format at [test_verification_chain.py](/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/tests/test_verification_chain.py#L264) and [test_verification_chain.py](/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/tests/test_verification_chain.py#L297).
- **FIX**: Serialize roots with `sha256_digest(root_bytes)`, parse them with `_digest_bytes`, update CLI help/messages, and rewrite the affected tests to expect the prefixed form.
- **CONSTRAINT_CLASS**: HARD

### FINDING_3
- **CATEGORY**: Correctness
- **SEVERITY**: IMPORTANT
- **DESCRIPTION**: Epoch data is persisted but not verified. `verify_chain()` ignores `_epochs` entirely at [verification_chain.py](/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/verification_chain.py#L434), so a falsified stored epoch root or `record_count` is accepted. Separately, `build_inclusion_proof()` always uses the full current record set at [verification_chain.py](/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/verification_chain.py#L458), so after later appends it cannot rebuild a proof for an earlier sealed epoch.
- **FIX**: Add epoch verification that recomputes each stored epoch root from the recorded cutoff, and add an epoch-bound proof API such as `build_inclusion_proof(index, epoch_index)` so proofs can target historical sealed epochs.
- **CONSTRAINT_CLASS**: HARD

### FINDING_4
- **CATEGORY**: Correctness
- **SEVERITY**: BLOCKING
- **DESCRIPTION**: Signed mode is write-only. Records are signed at [verification_chain.py](/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/verification_chain.py#L396), but neither `verify_chain()` nor `verify_record()` checks signatures at [verification_chain.py](/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/verification_chain.py#L434) and [verification_chain.py](/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/verification_chain.py#L446). `Verifier` exists at [verification_chain.py](/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/verification_chain.py#L111) but is unused. In practice, corrupting a record signature still leaves `verify_chain()` green.
- **FIX**: Either implement public signature verification now, or remove/defer the authenticated-signing claim for v1. The clean fix is `verify_record_signature()` plus optional signature checking in `verify_record()`/`verify_chain()`, with tests for valid signature, corrupted signature, wrong key, and missing signature.
- **CONSTRAINT_CLASS**: HARD

### FINDING_5
- **CATEGORY**: Correctness
- **SEVERITY**: IMPORTANT
- **DESCRIPTION**: Proof verification is not robust against malformed input. `rfc9162_verify_inclusion()` assumes every proof step has valid hex and required keys at [verification_chain.py](/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/verification_chain.py#L279), so malformed proofs raise exceptions instead of returning `False`. The same problem propagates through `verify_inclusion_proof()` at [verification_chain.py](/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/verification_chain.py#L468) and `_cli_verify_proof()` at [verification_chain.py](/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/verification_chain.py#L629).
- **FIX**: Treat malformed proof structures, bad hex, and invalid roots as verification failure, not uncaught exceptions. The CLI should convert those cases into a clean stderr message and a non-zero exit code.
- **CONSTRAINT_CLASS**: HARD

### FINDING_6
- **CATEGORY**: Test Coverage
- **SEVERITY**: IMPORTANT
- **DESCRIPTION**: A8 is only partially covered. The adopted test plan says the runner should import the module instead of defining its own class, but [test_verification_chain.py](/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/tests/test_verification_chain.py) never exercises `run_round_robin.py`, so the A7/A8 regression slipped through. The suite also misses the highest-value negative cases around the actual gaps above: signature tampering, epoch tampering, historical-epoch proofs, malformed proof/root input, and the specific attack you called out of swapping stored `chain_hash` values between records.
- **FIX**: Add runner-integration coverage, plus negative tests for signature corruption, swapped `chain_hash` fields, tampered epoch metadata, malformed proofs, and proofs built against historical epochs.
- **CONSTRAINT_CLASS**: HARD

### FINDING_7
- **CATEGORY**: Integration
- **SEVERITY**: MINOR
- **DESCRIPTION**: `__all__` at [verification_chain.py](/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/verification_chain.py#L55) omits `Signer` and `Verifier`, even though signing is part of the advertised feature set and those classes are defined at [verification_chain.py](/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/verification_chain.py#L89) and [verification_chain.py](/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/verification_chain.py#L111).
- **FIX**: Export `Signer` and `Verifier` if signed mode remains public in v1. If signing is deferred, remove the public-facing signing surface instead of leaving it half-exposed.
- **CONSTRAINT_CLASS**: SOFT

### SUMMARY
Not ready for integration yet. A1-A4 and A6 are mostly in good shape, JSON save/load preserves the persisted record and epoch data, and Gemini’s four actionable documentation findings are incorporated in [verification_chain.py](/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/verification_chain.py). The blockers are the unintegrated runner, the A5 root-format drift, and the fact that signed mode is claimed but not actually verified.

I also ran the test suite with `python3 -m unittest bench.tests.test_verification_chain`. The logic tests mostly passed, but 13 file-based tests could not run in this sandbox because there is no usable writable temp directory here, so I treated those errors as environment-limited rather than product findings.

### BLOCKING_ISSUES
- `run_round_robin.py` must stop defining its own verification chain and import the canonical module.
- Merkle roots must be serialized and parsed as `sha256:<hex>` to match A5.
- Signed mode must either gain real verification support or be explicitly removed/deferred from the v1 contract.
