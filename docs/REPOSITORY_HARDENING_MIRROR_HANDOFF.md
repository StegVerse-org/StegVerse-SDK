# Repository Hardening Mirror Handoff

Updated: 2026-08-28T07:54:00-05:00

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

User-provided GitHub repository screenshots at 2026-08-28 07:54 -05:00 visibly show:

```text
main branch protection: NOT ENABLED
GitHub repository banner: "Your main branch isn't protected"
Deployments: pypi environment shows FAILED status
repository: public
open pull requests: 1
```

Direct live repository inspection confirms:

```text
current main: d42448d88169a70f22b7e50d5add5d51773d7765
current package version in pyproject.toml: 1.2.0
PyPI Trusted Publishing workflow: .github/workflows/release.yml
trusted publishing source implementation: MERGED
SDK 1.2.0 successor source candidate: VALIDATED_MERGED_RELEASE_PENDING
open PR #94: draft neutral current-basis transition manifest
```

The red GitHub `pypi` deployment indicator is evidence of a failed environment deployment, but it is not by itself proof that the current 1.2.0 successor publication was attempted. The current successor handoff still records v1.2.0 tag/release/PyPI publication as not yet verified/published.

## Required hardening

### 1. Protect `main`

Required repository-setting outcome:

- prohibit force-pushes;
- prohibit branch deletion;
- require pull request before merge;
- require required status checks for the SDK validation lanes appropriate to the repository;
- require branch to be up to date before merge where compatible with the active workflow;
- preserve administrator emergency recovery without weakening ordinary merge policy;
- do not make GitHub a StegVerse runtime/release authority.

This is a GitHub repository setting. It cannot be completed by source mutation alone.

### 2. Reconcile failed `pypi` deployment

Before retrying publication:

1. identify the exact failed deployment/workflow run and release/tag identity;
2. classify failure as build/identity, environment protection, OIDC/Trusted Publisher mapping, or PyPI rejection;
3. do not rerun against moving `main`;
4. do not create or retarget a historical tag;
5. only publish an exact TV/TVC-authorized release coordinate;
6. verify wheel + sdist hashes and Trusted Publisher provenance after publication.

Canonical publication transport remains `.github/workflows/release.yml`. No static PyPI token is authorized.

## Current blockers

```text
BLOCKER-A: main branch protection requires GitHub repository settings mutation
BLOCKER-B: exact failed pypi deployment run has not yet been identified from retained machine evidence
BLOCKER-C: SDK 1.2.0 successor release remains TV/TVC-authority gated
```

## Non-goals / invariants

```text
source validation != release
workflow success != runtime authority
GitHub deployment != StegVerse activation
PyPI publication != governance activation
generic GitHub credential substitution: PROHIBITED
static PyPI token: PROHIBITED
tag retargeting: PROHIBITED
```

## Completion gates

```text
main branch protection: ENABLED + VERIFIED
required checks: CONFIGURED + VERIFIED
failed pypi deployment: EXACT RUN IDENTIFIED + ROOT CAUSE RECORDED
publication retry: ONLY IF TV/TVC-AUTHORIZED EXACT RELEASE EXISTS
published package: exact wheel/sdist hashes + Trusted Publisher provenance VERIFIED
handoff: updated with exact evidence
```

## Cross-repository propagation after release readiness

When this lane reaches release/tag readiness, verify pertinent release/hardening state is reflected where applicable in:

```text
StegVerse-Labs/Site
GCAT-BCAT-Engine/Publisher
StegVerse-Labs/admissibility-wiki
StegVerse-002/stegguardian-wiki
```

Do not duplicate runtime or release authority in those repositories.
