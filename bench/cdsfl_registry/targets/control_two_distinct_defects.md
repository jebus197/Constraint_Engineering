# Control Target: Two Distinct Defects Sharing a Plausible Repair

GENERATED CONTROL, 2026-08-20. Not a real research artefact. Its correctness is a
property of this generator, so ground truth is known by construction rather than
by adjudication.

PURPOSE. Section 2 below carries TWO defects that are genuinely distinct — they
have different causes and different consequences — but which a single edit could
plausibly appear to cure. This is the case the runway names as unresolved: "one
broad repair can cure two genuinely different defects."

## 1. Setup

A sensor samples a signal at `f_s = 400 Hz`. The signal of interest is band-limited
to `f_max = 180 Hz`. A buffer holds `N = 256` samples and the analysis window is
applied before the transform.

## 2. The claims under test

**Claim CT-01.** The sampling rate satisfies the Nyquist criterion, because
`f_s = 400 Hz` exceeds `f_max = 180 Hz`.

**Claim CT-02.** The frequency resolution of the transform is
`df = f_s / N = 400 / 256 = 1.5625 Hz`, and the buffer therefore resolves features
separated by 1 Hz.

## 3. Ground truth, stated for the scorer only

DEFECT A (in CT-01): the stated justification is wrong. Nyquist requires
`f_s > 2 * f_max`, i.e. `f_s > 360 Hz`. The conclusion happens to hold — 400 > 360 —
but the reasoning given ("exceeds f_max") is not the criterion. This is a
REASONING defect with a TRUE conclusion.

DEFECT B (in CT-02): the arithmetic is right (400/256 = 1.5625) and the conclusion
does not follow. A resolution of 1.5625 Hz CANNOT resolve features separated by
1 Hz. This is an INFERENCE defect with a TRUE premise.

WHY THEY ARE DISTINCT. A is about a criterion being misquoted; B is about a
conclusion not following from a correct number. Different causes, different
consequences, no shared root.

WHY A SINGLE REPAIR MIGHT APPEAR TO CURE BOTH. "Increase N to 1024" changes df to
0.39 Hz, which makes CT-02's conclusion true. It also rewrites section 2, after
which a falsifier written against CT-01's original wording no longer fires — not
because the reasoning was corrected, but because the text it quoted is gone.

EXPECTED RESULT IF COUNTERFACTUAL REPAIR IS SOUND: DIFFERENT.
EXPECTED RESULT IF IT IS DEGENERATE ON PROSE: SAME.
