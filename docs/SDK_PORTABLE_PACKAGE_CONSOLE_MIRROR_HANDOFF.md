# SDK Portable Package Console Mirror Handoff

## Goal

`SDK-PORTABLE-PACKAGE-CONSOLE-001`

Extend the existing public no-account StegVerse SDK console with a bounded portable-package distribution/install surface for StegVerse S and NS Micro-Ecosystem packages.

This is a new goal. It does not reopen or reset completed `SDK-PUBLIC-CONSOLE-001` or other released SDK goals.

## Source of truth

```text
organization: StegVerse-org
repository: StegVerse-SDK
branch: feat/portable-package-console-v0
parent_handoff: SDK_MIRROR_HANDOFF.md
credential_authority: TV/TVC
GitHub_token_runtime_authority: NONE
non-TV/TVC_secret_required: FALSE
```

Canonical package production currently belongs to the active StegCore micro-ecosystem workstream:

```text
StegVerse-Labs/StegCore
sdk/portable_package_catalog.v1.json
tools/build_portable_ecosystem_package.py
docs/STEGVERSE_SDK_PORTABLE_DISTRIBUTION.md
```

The SDK console consumes/verifies distributable packages; it does not become the canonical StegGate evaluator or Node Sovereign membership authority.

## Required deployment choice

Every portable implementation is explicitly one of:

```text
S  = StegVerse S Ecosystem / Sovereign
NS = StegVerse NS Ecosystem / Node Sovereign profile
```

No default is permitted.

Installing NS does not create Node Sovereign membership.

## Initial console surface

```text
stegverse portable list
stegverse portable inspect --deployment-class S|NS
stegverse portable verify --archive <package.zip>
stegverse portable install --archive <package.zip> --destination <directory>
stegverse portable download --deployment-class S|NS --output <path>
```

`download` must fail closed until an exact governed release artifact/URL and expected archive hash are present in the SDK package catalog. No guessed GitHub URL, latest-release alias, or mutable download target is allowed.

`install` must:

1. verify `PACKAGE_RECEIPT.json` before extraction;
2. verify the archive's deployment class is S or NS;
3. verify every packaged file hash/size against the receipt;
4. reject path traversal and overwrite by default;
5. reject any receipt that claims provider-account or non-TV/TVC-secret requirements;
6. reject any NS package that claims installation itself grants node membership;
7. produce an installation receipt;
8. never execute the installed package as a side effect of installation.

## Authority boundary

```text
SDK package download != governance authority
SDK package install != activation
SDK package install != Node Sovereign membership
NS profile selection != Node Sovereign membership
package hash verification != StegGate ALLOW
package source identity != execution authority
GitHub/release hosting != runtime authority
wallet signing authority: USER_ONLY
broadcast authority: USER_ONLY
protected credential authority: TV/TVC
```

## Activation states

```text
HANDOFF_INSTALLED
PORTABLE_CATALOG_INSTALLED
LOCAL_VERIFY_IMPLEMENTED
LOCAL_INSTALL_IMPLEMENTED
DOWNLOAD_FAIL_CLOSED_WITHOUT_RELEASE
CLI_WIRED
TESTED
HOSTED_VALIDATED
MERGED
RELEASE_ARTIFACT_BOUND
DOWNLOAD_ACTIVE
```

Do not collapse these states.

## Initial collision scope

```text
docs/SDK_PORTABLE_PACKAGE_CONSOLE_MIRROR_HANDOFF.md
stegverse/portable_packages.py
stegverse/cli.py
tests/test_portable_packages.py
docs/SDK_CONSOLE.md
```

## Remaining work

1. Implement the portable package catalog and exact-receipt verifier.
2. Implement safe local installation with no execution side effect.
3. Add fail-closed download behavior for packages lacking governed exact release artifacts.
4. Wire the new `portable` command into the existing SDK CLI.
5. Add focused tests.
6. Validate in repository CI.
7. After the StegCore package PR is merged/released, bind exact immutable S/NS package artifacts and hashes.
8. Only then activate remote console download.
9. Preserve SDK early-access/community usage evidence for later product-lifecycle decisions.
10. Coordinate verified contribution receipts with `StegVerse-Labs/stegfin-governance` without rewarding installation/enrollment alone.

## Current claim

```yaml
task_id: SDK-PORTABLE-PACKAGE-CONSOLE-001
claim_state: CLAIMED_FOR_IMPLEMENTATION
branch: feat/portable-package-console-v0
parallel_safety: DISTINCT_NEW_CONSOLE_SUBCOMMAND
release_condition: focused tests and repository CI pass; exact remote package binding remains separately gated
```
