# SDK Demo Pipeline Test

Headless validation that the StegVerse SDK -> demo-suite -> runner pipeline works end-to-end.

## What This Tests

| Test | Validates |
|------|-----------|
| SDK Installation | `pip install stegverse-sdk` works |
| Core Imports | `submit_intent`, `StegVerseLLMAdapter`, `govern_llm_output` importable |
| Demo Submission | SDK can submit intents to demo-suite |
| LLM Governance | Adapter correctly classifies LLM output as ALLOW/DENY/FAIL_CLOSED |
| Confidence Visibility | SDK can retrieve confidence scores and reconstruction data |
| Full Pipeline | All 5 modes run successfully with >=95% confidence |
| Mobile Trigger | Workflow can be started from GitHub Mobile app |

## How to Run

### From GitHub Mobile (While with kids)

1. Open GitHub app
2. Go to `StegVerse-org/StegVerse-SDK` -> Actions
3. Select "SDK Demo Pipeline Test"
4. Tap "Run workflow"
5. Choose test level: `quick`, `standard`, or `full`
6. Tap "Run workflow"
7. Wait for notification (2-5 minutes)

### From Desktop

```bash
gh workflow run sdk-demo-test.yml --repo StegVerse-org/StegVerse-SDK -f test_level=full
```

## Test Levels

| Level | Duration | What It Checks |
|-------|----------|---------------|
| `quick` | 30 seconds | Install + import |
| `standard` | 2 minutes | Install + demo call + confidence |
| `full` | 5 minutes | All modes + reconstruction + replay |

## Success Criteria

- [ ] SDK installs without errors
- [ ] All core imports succeed
- [ ] Demo intent submits successfully
- [ ] LLM governance returns valid decision
- [ ] Confidence score >= 95% for full mode
- [ ] Reconstruction data present
- [ ] All 5 modes pass

## Failure Handling

If any test fails:
1. Check `test_report.json` artifact
2. Review logs for specific failure
3. File issue with `sdk-demo-failure` label
4. StegVerse-Healer auto-attempts repair (if configured)

## Schedule

Runs automatically every 6 hours. Results posted to StegDB.
