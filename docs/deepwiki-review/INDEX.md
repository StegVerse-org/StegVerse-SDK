# DeepWiki public SDK export — retained review inventory

Captured 2026-09-25T06:43Z by the source-only pull-request evidence workflow [run 36104137361](https://github.com/StegVerse-org/StegVerse-SDK/actions/runs/36104137361) from official unauthenticated `read_wiki_structure` and `read_wiki_contents` MCP calls. [Review artifact 10850037472](https://github.com/StegVerse-org/StegVerse-SDK/actions/runs/36104137361/artifacts/10850037472) includes raw JSON and Markdown tool results, manifest and SHA-256 records. It is temporary Actions evidence, not yet a reviewed or copied SDK source document. Source repo: `StegVerse-org/StegVerse-SDK`.

The read-only export returned **38 distinct page sections matching all 38 headings in the returned page tree** (eight root pages and thirty nested pages; zero missing, extra or duplicate titles within the returned dataset). This establishes internal export consistency, not independent completeness of the online service beyond its own returned structure. Captured `read_wiki_contents.md`: 328247 bytes, SHA-256 `a729d9b0f487f785b0e8f92006f303e8520e3593b6eb6c4c5de43273daa72087`. Captured `read_wiki_structure.md`: 1667 bytes, SHA-256 `4a4799202b41399ed7478de98bc8dd2bbaaf7e8be072b893c4be43aa25d831df`.

## Current generated page tree (verbatim titles)

1. Overview
   - Getting Started and Installation
   - Governance Model and Authority Boundaries
   - Repository Map
2. Manifest Pipeline
   - Manifest Builder and Ingress Contract
   - Route Resolution and Manifest Execution
     - Purpose-Bound Worker Processor
     - Atomic Task Worker and Invariance Seam
     - Runtimes: Sovereign, Diagnostic, State Transition
   - Universal Entry and Transition Tables
3. Evaluator and Governance Subsystems
   - Evaluator Governance Posture Manifests
   - Governance Reference Graph (GRG)
   - Evaluator Contract, Consoles and CLIs
   - Evaluation Boundary and Non-Interference
   - Admissibility and AdmittedCode
4. Core SDK Library
   - Client, Intents and Receipts
   - Safety Stack and GCAT/BCAT
   - LLM Adapter and Governed LLM Flows
   - Ecosystem Chat Pipeline
   - External Framework Adapters and Bridges
5. Public Inspection and Return Path
   - Public Inspection Entry and Runtime
   - Publisher Return Binding and Materialization
   - Governance Navigation and Portable Governance Exchange
6. Experiments and Non-Authorizing Reviews
   - Micro-Node and Stage-1 Reviews
   - Cross-Framework Current Basis and Formal Testing Routes
   - Demos, Examples and Fixtures
7. Validation, Evidence and Release Engineering
   - CI Workflows and Non-Authorizing Validation
   - Verification Scripts and Test Suite
   - System Boundary Evidence and Activation
   - Release Governance and Packaging
   - Task Records, Mirror Handoffs and Downstream Propagation
8. Glossary

## Exact current configuration decision

Current official DeepWiki `.devin/wiki.json` requires both `repo_notes` and explicit `pages`, and generates only enumerated pages. Standard limit is **30 pages**, whereas this captured page tree has **38**. Do **not** install a partial config or regenerate in a way that drops eight pages. Prefer keeping automatic planning unchanged and preserving this complete exported dataset as review evidence, then add reviewed pages to the already existing SDK-owned `sdk.stegverse.org` builder with new source provenance and tests. No Devin app installation, subscription, private repo access or external publication mutation required.

## Boundaries before approved import

- The Actions workflow's `contents: read` does not modify repository source or Pages. The export's `publication_allowed` is false.
- Audit title/section retention, code-link accuracy, potential third-party generation reuse terms, SHA-256 and current source revision before copying any generated material into official public docs.
- The existing official SDK wiki remains canonical, already served from repository-local exact-source builder and main-only Pages workflow.
- No local generated wiki content is treated as Master Records custody, InTr/far-side execution evidence, propagation readback or source release authorization.

## Markdown link-integrity review finding

Static inspection of the captured raw Markdown found **659 occurrences of the empty Markdown target `]()` spread across 31 of 38 page sections**. A more restrictive simple bracket matcher found 640 empty link expressions, 580 of which match a simple `path.ext:first-last` source-line reference. The rest include source symbols, composite line ranges and formatted labels and require explicit mapping. These are generated citation-link integrity defects, not proof that the underlying cited source is absent. **Do not publish the raw 38-page export unchanged.** A reviewed import must rewrite citation targets to SHA-pinned canonical GitHub source links where resolvable, fail or flag unresolved citations, validate every resulting link and retain the original raw export + hash for comparison.
