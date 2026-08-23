# Sampling and Resolution Note: 400 Hz Acquisition Chain

A short technical note for review.

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
