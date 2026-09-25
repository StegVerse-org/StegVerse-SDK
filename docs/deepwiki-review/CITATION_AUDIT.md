# SDK DeepWiki citation audit — source-review evidence only

Date: 2026-09-25. Existing owner: `ECOSYSTEM-OPEN-SOURCE-STRATEGY-001`; COSV `20010010100000`. This audit concerns unreviewed external generated documentation, not an open-source release, developer-wiki re-publication, or runtime proof.

## Exact retained input
- GitHub Actions [run 36104137361](https://github.com/StegVerse-org/StegVerse-SDK/actions/runs/36104137361) / [artifact 10850037472](https://github.com/StegVerse-org/StegVerse-SDK/actions/runs/36104137361/artifacts/10850037472).
- `read_wiki_contents.md`: 328,247 bytes; SHA-256 `a729d9b0f487f785b0e8f92006f303e8520e3593b6eb6c4c5de43273daa72087`.
- `read_wiki_structure.md`: 1,667 bytes; SHA-256 `4a4799202b41399ed7478de98bc8dd2bbaaf7e8be072b893c4be43aa25d831df`.
- The official returned structure and full text contain matching 38 page titles; this says nothing about correctness of generated claims or current source revision.

## Citation defect breakdown from original captured bytes
- **659** total literal `]()` occurrences. Original raw input retained, not rewritten.
- **640** matches of simple bracketed Markdown labels `[label]()`; 527 distinct raw labels.
- **599** match strict numeric `path.ext:N` or `path.ext:N-M` labels (117 distinct raw file paths, including anomalous leading slash paths). These are **candidate** source locators, not verified source links.
- **41** remaining simple labels include bare file paths, function symbols, composite/disjoint ranges, malformed snippets, and placeholders.
- **19** more occurrences do not match the bounded simple-label syntax; these include malformed inline-code/diagram fragments or composite syntax. Their surrounding Markdown must be parsed with context; naive global substitution risks corrupting diagrams or prose.
- Existing separate static tally found empty targets in 31 of 38 page sections. Counts depend on the exact matcher; these groupings partition all 659 literal occurrences.

## Repair requirements (not yet satisfied)
1. Read the exact SDK source tree and source-file bytes from an identified immutable Git commit; do **not** assume DeepWiki's generated references match today's main or this PR.
2. For each numeric source locator, normalize safe repository-relative paths, reject traversal/ambiguous leading-slash paths, confirm file existence and every referenced line boundary, then create URL-encoded `https://github.com/StegVerse-org/StegVerse-SDK/blob/<verified-SHA>/<path>#Lstart-Lend` links. Confirm semantic claim alignment rather than treating valid line numbers as verification.
3. Resolve function symbols against actual definitions, composite line ranges explicitly, and Markdown code/diagram malformed cases by contextual review. Never silently convert ambiguous labels into apparently verified links.
4. Produce a per-citation mapping of page, occurrence, original label/context, candidate path, pinned revision, validated line span, disposition and reason. Preserve original exact-source export, original hashes and a distinct corrected review output with its hash.
5. Fail publication if **any** empty citation target, broken path, unverifiable assertion, incomplete page, licensing/provenance issue, or unresolved source mismatch remains. A successful citation rewrite alone does not approve copyright reuse or source correctness.
6. After review, integrate only approved content through the existing SDK-owned wiki builder and its normal PR/main-only Pages process. Do not install a partial `.devin/wiki.json` (38 captured pages exceed the documented 30-page standard explicit selection limit).

**Disposition:** ORIGINAL_CAPTURE_VERIFIED; 659_EMPTY_TARGETS_CLASSIFIED; NUMERIC_CANDIDATES_NOT_YET_SOURCE_VALIDATED; IMPORT_AND_PUBLICATION_BLOCKED. This note is an audit of generated source references, not evidence of a completed source-level fact check or a release.
