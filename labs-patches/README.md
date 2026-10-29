# Labs patches prepared by Claude for StegVerse-Labs/.github

Claude sessions cannot push to `StegVerse-Labs/.github`, which is a dot-named repository. This branch carries patches for an LLM with Labs write access to apply with `git am`. This branch is never merged. authority_effect NONE.

| Patch | Applies on | Purpose | Coordination |
|---|---|---|---|
| 0002 | Labs main | Synthetic assessment demo docs (#3370) | KV checkpoints |
| 0003 | Labs main `62391b0` | Fixes the InTr `sdk-manifest-ingress` binding owner: `StegVerse-Labs/StegVerse-SDK` becomes `StegVerse-org/StegVerse-SDK` | StegVerse-org/StegVerse-SDK#566 |
| 0004 | Labs main `62391b0` (after #3372) | Collision evaluator guards every owner-held checkout state | StegVerse-org/StegVerse-SDK#556 |
| 0005 | PR #3375 head `45a670b` | Protocol v1 negatives run through the real `receive()`; expectations are generated from real output; spec gaps are recorded honestly; adds the non-gating n9 case | StegVerse-org/StegVerse-SDK#556 |

Verify with `sha256sum -c SHA256SUMS` before applying.
