# Adjudication, 10 pairs

Same defect (S), different (D), or cannot tell (?).

**1.** *(exp47)*
- **A:** `check_sibling_admissibility` penalizes models for carrying forward valid alternatives across rounds. When `prior_round_alternatives` is provided, it scores the current alternative against ALL prior-round alternatives.
- **B:** The cross-round recidivism check in `check_sibling_admissibility` falsely penalizes models for fixing previously rejected alternatives. When a model adds a missing contrast statement to a prior alternative, `parse_contrast_statement` strips the new ...

**2.** *(exp44)*
- **A:** `EvidenceStore.export_bundle()` (lines ≈231‑266) computes the bundle’s `merkle_root` by hashing *all* raw chain records into a single RFC 9162 tree, asserting that this tree is “always” the one used by `build_inclusion_proof()`. The comment (`# must match ...
- **B:** `EvidenceStore.verify_bundle` provides no cryptographic authentication because it does not validate the bundle's Merkle root against any trusted anchor.

**3.** *(exp48)*
- **A:** CH-29 says independent relative uncertainty components 0.42%, 0.28%, and 0.15% are combined by arithmetic addition to give 0.85%. Independent uncertainty components should be combined in quadrature/root-sum-square, not by simple addition, unless a ...
- **B:** CH-29 states three independent uncertainty components (0.42%, 0.28%, 0.15%) "because the components are independent they are combined by arithmetic addition, giving 0.85 per cent." This inverts the correct rule: independent components combine in quadrature ...

**4.** *(exp44)*
- **A:** `EvidenceStore.verify_bundle()` accepts a bundle record whose `chain_hash` is missing, as long as the supplied proof verifies. Location: `bench/evidence.py`, method `EvidenceStore.verify_bundle`.
- **B:** `EvidenceStore.verify_bundle` verifies the inclusion proofs against `bundle.merkle_root`, which is provided by the bundle itself. It never checks if this root matches the trusted chain's root.

**5.** *(exp44)*
- **A:** `EvidenceStore.verify()` caches only “verifier was ever supplied”, not which verifier/configuration was supplied. Location: `bench/evidence.py`, method `EvidenceStore.verify`.
- **B:** `CONFIRM C0028` — `EvidenceStore.verify_bundle()` verifies inclusion proofs against the `bundle.merkle_root` supplied by the bundle itself, but it does not authenticate that root against the local/trusted `EvidenceStore` chain. Location: ...

**6.** *(exp45)*
- **A:** In `ImmuneMemory.load`, missing `source_hash` in the JSON file combined with a caller-supplied `expected_hash` does not invalidate memory, allowing stale data to be loaded.
- **B:** `ImmuneMemory.load` fails to initialize `source_hash` when returning a fresh instance (C0001), fails to invalidate when `stored_hash` is missing (C0002, C0006), and crashes with `AttributeError` if the JSON root is not a dictionary (e.g., `[]`).

**7.** *(exp48)*
- **A:** CH-27 claims that injecting argon into the ammonia converter at constant volume and constant temperature shifts equilibrium toward ammonia because total pressure rises. This is wrong for an ideal gas mixture at constant V and T.
- **B:** CH-27 claims that "Injecting argon into the converter at constant volume and constant temperature ... produces an equilibrium shift toward ammonia, and the argon bleed is therefore used as a fine trim on converter yield." This is a classic Le Chatelier error.

**8.** *(exp49)*
- **A:** EN-36 gives an infeasible and non-optimal LP-2 vertex. Location: section 7, EN-36.
- **B:** Logic error in the constrained-design optimisation in EN-36. The reported optimal vertex for LP-2 is `x1 = 120, x2 = 40, x3 = 80 kN`.

**9.** *(exp49)*
- **A:** EN-41 reports `p = 0.021` for a two-sample t-test comparing the two weld hardness sets, but the stated data give approximately `p = 0.090`, not significant at the 0.05 level. Location: section 8, EN-41.
- **B:** EN-41 claims a two-sample t-test on the procedure-A vs procedure-B hardness sets gives p=0.021, "significant at the 0.05 level," and specifies procedure A for load-bearing welds on that basis. Recomputed with the printed data (A=[318,325,311,329,316,322], ...

**10.** *(exp48)*
- **A:** In CH-27, it is claimed that injecting argon at constant volume and temperature shifts the equilibrium toward ammonia. Adding an inert gas at constant volume increases total pressure but does not change the partial pressures of the reacting gases, so there ...
- **B:** CH-27 states that injecting argon into the ammonia converter at constant volume and constant temperature shifts equilibrium toward ammonia because total pressure rises. This is wrong for an inert gas at constant V and T.
