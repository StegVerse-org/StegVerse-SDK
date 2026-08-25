# StegVerse SDK 1.2.0

This release candidate freezes the public governance-interlock and POST_RETURN proof surface on top of executable source commit `3f63bd965d9cfe871e85eb938295f40726ed96b7`.

Key contained capabilities:

- portable interlock transition and reciprocal return contracts;
- reference participant terminal/successor receipt binding;
- SDK -> SPE -> canonical StegGate standing bridge;
- one-command POST_RETURN production-proof runner;
- portable governance verification/exchange;
- installed governed-dependency alignment that fails closed when release coordinates disagree with the installed SDK wheel.

The governed-test executable dependencies are frozen to:

- `StegVerse-Labs/StegCore@124ea6b53ff79db8f514cacf1aab295f03cacf74`
- `Data-Continuation/core-lite@72bdb0f110031ccc2cd98b8ebb7c22b1ab7326f8`
- `master-records/orchestration@3dae8832a167359612a15ccfde99a9f22b77fc8a`

Authority boundaries are unchanged: SDK authority is NONE; SPE standing does not authorize execution; canonical StegGate remains the admissibility/consequence boundary; Master Records remains custody/reconstruction only; release and credential authority remain TV/TVC only.

This file and the package-version change are release metadata. They do not by themselves create a tag, GitHub release, PyPI publication, runtime activation, or TV/TVC release authorization.
