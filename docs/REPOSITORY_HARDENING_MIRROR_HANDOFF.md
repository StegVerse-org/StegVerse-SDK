# Repository Hardening Mirror Handoff

Updated: 2026-08-28T08:00:00-05:00

## Source of truth

```text
organization: StegVerse-org
repository: StegVerse-SDK
canonical_branch: main
tracking_branch: ops/repository-hardening-20260828
goal_id: SDK-REPOSITORY-HARDENING-001
credential_authority: TV/TVC
GitHub runtime authority: NONE
```

Live repository state and this handoff supersede chat-only claims for this hardening lane.

## Observed state

User-provided GitHub repository screenshots at 2026-08-28 07:54 and 08:00 -05:00 show:

```text
main branch protection: NOT ENABLED
GitHub repository banner: "Your main branch isn't protected"
repository: public
pypi environment: one failed deployment
failed deployment tag shown by GitHub: v1.0.4
failed deployment date shown by GitHub: Apr 29
failed deployment workflow shown by GitHub: StegVerse SDK Validation (Optional Hosted) #37
deployment title begins: Bump version from 1.0.2 to 1....
```

Direct live repository inspection confirms:

```text
current main: d42448d88169a70f22b7e50d5add5d51773d7765
current package version in pyproject.toml: 1.2.0
PyPI Trusted Publishing workflow: .github/workflows/release.yml
trusted publishing source implementation: MERGED
SDK 1.2.0 successor source candidate: VALIDATED_MERGED_RELEASE_PENDING
open evaluator draft PR #94 remains independent
hardening PR #95 tracks this lane
```

## Historical failed pypi deployment reconciliation

The failed deployment is now identified as a historical April 29 release attempt, not the current 1.2.0 successor lane.

```text
Git tag: v1.0.4
tag target commit: ec8846311462651d69daaf4ec0d4b049100b3f8e
tag target commit message: Bump version from 1.0.2 to 1.0.3
pyproject.toml at v1.0.4 declares project.version = 1.0.3
historical workflow at v1.0.4: .github/workflows/sdk-demo-test.yml
historical workflow pypi job: OIDC publisher bound to environment pypi
```

This proves an exact tag/package identity defect at the failed release coordinate:

```text
release tag identity: 1.0.4
package artifact identity: 1.0.3
identity relation: MISMATCH
```

The historical workflow lacked the current exact tag/package-version guard. It could therefore build a 1.0.3 distribution from a v1.0.4 tag and pass that artifact set to the pypi job. This is sufficient to classify the old deployment as release-identity-invalid without treating it as evidence about the current 1.2.0 lane.

Do not retry, repair, or retarget v1.0.4. Historical tags remain immutable evidence.

The current .github/workflows/release.yml already contains a fail-closed tag/package identity check, exact tag materialization, exact wheel+sdist verification, OIDC Trusted Publishing, and no static PyPI token path. Therefore the historical failure does not require a current source-code hotfix.

## Remaining hardening

### Protect main

- prohibit force-pushes;
- prohibit branch deletion;
- require pull request before merge;
- require appropriate status checks;
- verify branch policy after configuration;
- do not make GitHub a StegVerse runtime or release authority.

This is a GitHub repository-setting mutation and cannot be truthfully completed by source mutation alone.

### Current 1.2.0 publication boundary

Only publish the exact TV/TVC-authorized immutable successor coordinate. Do not derive release identity from moving main, reuse historical tags, or retarget v1.0.4. After publication retain exact wheel/sdist SHA-256 and verify Trusted Publisher provenance.

## Current blockers

```text
BLOCKER-A: main branch protection requires GitHub repository settings mutation
BLOCKER-B: SDK 1.2.0 successor release remains TV/TVC-authority gated
```

Resolved investigation:

```text
RESOLVED-B: failed pypi deployment identified as historical v1.0.4
RESOLVED-C: historical defect proven: tag v1.0.4 -> package 1.0.3
RESOLVED-D: current trusted publisher workflow already guards exact tag/package identity
```

## Completion gates

```text
main branch protection: ENABLED + VERIFIED
required checks: CONFIGURED + VERIFIED
failed pypi deployment: IDENTIFIED
historical root cause class: RECORDED
current release publication: ONLY IF TV/TVC-AUTHORIZED EXACT RELEASE EXISTS
published package: exact wheel/sdist hashes + Trusted Publisher provenance VERIFIED
```

## Cross-repository propagation after release readiness

When release/tag readiness is reached, verify pertinent state where applicable in StegVerse-Labs/Site, GCAT-BCAT-Engine/Publisher, StegVerse-Labs/admissibility-wiki, and StegVerse-002/stegguardian-wiki. Do not duplicate runtime or release authority.

## PyPI project-side observation — 2026-08-28T08:12:00-05:00

User-provided authenticated PyPI project screenshots show the managed project `stegverse-sdk` currently has seven published releases. Visible releases include:

```text
1.0.13 — Apr 29, 2026 — 2 files (1 wheel, 1 source)
1.0.12 — Apr 29, 2026 — 2 files (1 wheel, 1 source)
1.0.11 — Apr 29, 2026 — 2 files (1 wheel, 1 source)
1.0.9  — Apr 29, 2026 — 2 files (1 wheel, 1 source)
1.0.8  — Apr 29, 2026 — 2 files (1 wheel, 1 source)
1.0.7  — Apr 29, 2026
```

This confirms the PyPI project itself exists, is accessible to the project owner, and historically accepted wheel+source uploads after the failed v1.0.4 GitHub deployment. Therefore the historical red deployment does not indicate a permanently broken PyPI project.

The screenshots also confirm that 1.2.0 is not yet present in the managed release list. Current remediation remains to execute the exact authorized 1.2.0 Trusted Publisher release path and verify provenance; there is no reason to repair or delete the historical v1.0.4 deployment record.

Next manual inspection surface, if needed, is the PyPI project `Publishing` page to verify the Trusted Publisher mapping still exactly names:

```text
owner/repository: StegVerse-org/StegVerse-SDK
workflow filename: release.yml
environment: pypi
```

Do not create a new publisher mapping if an exact matching mapping already exists.
