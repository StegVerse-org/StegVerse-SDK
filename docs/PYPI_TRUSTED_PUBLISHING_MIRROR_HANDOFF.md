# PyPI Trusted Publishing Mirror Handoff

## Source of truth

```text
organization: StegVerse-org
repository: StegVerse-SDK
implementation_branch: feat/pypi-trusted-publishing
base_commit: ed30b6439d755b23d029f5806801a18e3f418e64
credential_authority: TV/TVC
PyPI publisher: GitHub OIDC Trusted Publisher
PyPI project: stegverse-sdk
PyPI trusted workflow: .github/workflows/release.yml
GitHub environment: pypi
GitHub token runtime authority: NONE
static PyPI token required: FALSE
```

## Goal

Add a narrowly scoped publication lane for an already-approved, already-tagged SDK release. The lane may publish the exact wheel/sdist artifact set to the existing PyPI `stegverse-sdk` project through PyPI Trusted Publishing. It must not choose a version, create or move a tag, create a GitHub release, modify source, grant StegVerse runtime authority, receive TV/TVC protected values, or use a long-lived PyPI token.

## Authority separation

```text
source implementation/review -> feature branch + PR
release candidate selection -> external/sovereign release process
tag creation -> external/sovereign release process
GitHub release creation -> external/sovereign release process
package build validation -> non-authorizing GitHub build job
PyPI publication -> exact tagged release only, OIDC, protected `pypi` environment
StegVerse runtime authority -> NONE
TV/TVC secret authority -> unchanged
```

The PyPI OIDC credential is a short-lived artifact-publication credential for the exact release job. It is not a StegVerse runtime/control-plane credential and does not satisfy any governed activation predicate.

## Publication contract

The trusted workflow must:

1. Trigger only from a GitHub `release.published` event.
2. Require a tag of the form `vX.Y.Z`.
3. Materialize the exact tag source anonymously rather than using a repository write token.
4. Require the tag version to equal `project.version` in `pyproject.toml`.
5. Build exactly one wheel and one source distribution.
6. Run package metadata and install smoke checks before publication.
7. Transfer only built distributions into an isolated publish job.
8. Give `id-token: write` only to the publish job.
9. Bind the publish job to GitHub environment `pypi`.
10. Publish through `pypa/gh-action-pypi-publish` Trusted Publishing with no password/token input.
11. Never create/move tags, push source, create a GitHub release, or select a different version.

## Branch / merge / release rule

This implementation MUST NOT be developed directly on `main`.

```text
feat/pypi-trusted-publishing
-> focused validation
-> pull request
-> complete/green branch head
-> merge
-> exact merged commit recorded
-> release tag created only after merge and release-set verification
-> GitHub release published for exact tag
-> protected `pypi` environment approval
-> PyPI Trusted Publishing
-> published version/files/hashes verified
```

No moving-main substitution is allowed for a release candidate. Existing PyPI releases are immutable and must not be replaced.

## Current external configuration

User-provided PyPI evidence confirms an active Trusted Publisher mapping:

```text
repository: StegVerse-org/StegVerse-SDK
workflow: release.yml
environment: pypi
project: stegverse-sdk
```

This repository work must match that identity exactly. Whether the GitHub `pypi` environment has reviewer protection configured is a separate GitHub repository setting and must be verified before production publication.

## Completion condition

Source implementation is complete only when the branch contains the trusted workflow plus deterministic contract tests and the PR branch-head validation passes. Production publication is complete only after a post-merge exact tag/release invokes the protected environment, PyPI accepts the exact artifacts, and published PyPI metadata/files/hashes are independently verified.
