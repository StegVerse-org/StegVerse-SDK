# Generated-documentation and optional dependency rights — scoped decision record

**Existing owner:** `ECOSYSTEM-OPEN-SOURCE-STRATEGY-001` / COSV `20010010100000`. **Scope:** source and rights verification for the existing SDK developer wiki only. This is not a new license grant, advice that a copyright chain is complete, or authority to deploy generated pages.

## External DeepWiki documentation

The exact 38-page public MCP capture is retained **only as review evidence**, SHA-256 `a729d9b0f487f785b0e8f92006f303e8520e3593b6eb6c4c5de43273daa72087`. The corresponding quarantine-only copy omits all 46 broken link targets and downgrades 613 other source candidates to nonlinks. Neither file belongs in the public SDK Pages builder without a separate authorization.

[Cognition's Platform Terms of Service, June 30, 2026, section 3.1](https://cognition.com/legal/platform-terms-of-service) give the customer the assigned output from **their** inputs, while expressly withholding rights to outputs made for other customers. The terms do not identify StegVerse as the legally entitled customer for the automatically indexed public DeepWiki SDK pages and do not provide a general redistribution license for pages anyone can read via the public MCP. The 38-page content therefore remains `RIGHTS_UNKNOWN_NO_REPUBLICATION`. If reuse of its actual prose/diagrams is sought, resolve which legal entity holds the output rights and obtain permission covering republication, modification and distribution. Do not infer rights from anonymous MCP accessibility, public GitHub source or similarity to source.

A separate, newly authored [first-party exact-source SDK guide](FIRST_PARTY_SOURCE_GUIDE.md) and [three source-drift explanations](CURRENT_SOURCE_DRIFT_CORRECTIONS.md) may continue through the **existing** SDK documentation owner. Their factual code references need line and semantic review, and independent contributor or contractual rights issues must be resolved before new distribution. Neither this source-only review nor a successful test alone authorizes a Pages deployment.

## Existing MIT grant is source-specific

The SDK [root MIT license](https://github.com/StegVerse-org/StegVerse-SDK/blob/main/LICENSE) names StegVerse, 2026, and [`pyproject.toml`](https://github.com/StegVerse-org/StegVerse-SDK/blob/main/pyproject.toml) declares MIT. Preserve existing grants and notices. Repository control, this license declaration and successful workflow results do not independently prove the full contributor chain, third-party imported-file licensing or owner release authorization.

## Pinned optional test dependencies — unresolved redistribution evidence

`pyproject.toml` declares these Git-pinned dependencies in optional groups, distinct from its ordinary PyPI dependencies:

| Optional group | Dependency | Pinned revision | LICENSE read at this exact ref | Decision |
| --- | --- | --- | --- | --- |
| governed-test | `StegVerse-Labs/StegCore` | `ef38410505b0ef3e84148892b1d6e3cdef20f300` | Connected GitHub file read returned 404 | `UNKNOWN`, not proof no license exists |
| governed-test | `Data-Continuation/core-lite` | `72bdb0f110031ccc2cd98b8ebb7c22b1ab7326f8` | Read returned 404 | `UNKNOWN` |
| governed-test | `master-records/orchestration` | `03312236c115bc814024d700810391340648601f` | Read returned 404 | `UNKNOWN` |
| manifold-test | `StegVerse-Labs/StegCore` | `99397392462b8e39a510ec6d9e543551270bd402` | Read returned 404 | `UNKNOWN` |

A 404 can mean an inaccessible revision, private repository, missing root LICENSE at that path or insufficient permission. **Do not** reclassify a 404 as evidence of absent redistribution restrictions. Required follow-up through each existing source owner: recover each exact referenced commit, inspect the applicable license at that commit and file scope, audit vendored imports/transitive dependencies and assess redistribution of the proposed actual package. Optional groups need not block documentation-only first-party explanations of SDK core code, but they do block a claim that all SDK optional-dependency rights are cleared.

## Ordinary published Python dependency licenses (current upstream observations)

The connected GitHub source at the present upstream default branches exposes the following root LICENSE files. This is **narrow license-text discovery**, not an SBOM at the eventual resolved installation versions or proof of all vendored/transitive rights:

| SDK direct requirement | Public upstream license text observed | Exact GitHub LICENSE blob SHA | Remaining condition |
| --- | --- | --- | --- |
| `requests>=2.28.0` | Apache License 2.0 in `psf/requests` | `67db8588217f266eb561f75fae738656325deac9` | Preserve applicable copyright, license, notice and patent terms for the actually installed distribution. |
| `pyyaml>=6.0` | MIT license in `yaml/pyyaml` | `2f1b8e15e5627d92f0521605c9870bc8e5505cb4` | Preserve copyright and permission notice for redistributed copies/substantial portions. |
| `python-dotenv>=0.19.0` | BSD-style three-clause text in `theskumar/python-dotenv` | `3a97119010ac82e15e917a69b7b8f9f59b5a4601` | Retain copyright, conditions and disclaimer for redistributed source/binary forms. |

These results clear only the **upstream current root-license identification step** for ordinary direct dependencies. They do not authorize bundling an unresolved version or every optional Git dependency. `python-dotenv` current upstream package metadata identifies BSD-3-Clause and newer Python-version requirements; the SDK still declares Python `>=3.9` and an open-ended `python-dotenv>=0.19.0`, so the final resolver and compatibility matrix must be tested against target Python runtimes. No blanket installation-compatibility or third-party rights clearance is claimed.

## Dispositions

- `DENY:THIRD_PARTY_GENERATED_WIKI_REPUBLICATION_RIGHTS_UNVERIFIED`: keep original and derivative as unimported review evidence. Correct by attributable license/grant and exact approved material inventory.
- `DENY:OPTIONAL_PINNED_DEPENDENCY_RIGHTS_UNVERIFIED`: do not package or license the optional bundles as uniformly MIT. Correct under their existing source owners.
- `REVIEW:NEW_FIRST_PARTY_SOURCE_GUIDE`: independent prose can progress through the existing SDK owner, exact-source tests and publication review, **without** carrying in the generated page text.
- `UNKNOWN:FULL_CONTRIBUTOR_TITLE_AND_PUBLICATION_AUTHORITY`: source audit, contributor rights and any relevant legal sign-off remain separate from GitHub CI and the historical already-published SDK wiki.

No duplicate runtime, ledger, publication authority, device or task owner is introduced.
