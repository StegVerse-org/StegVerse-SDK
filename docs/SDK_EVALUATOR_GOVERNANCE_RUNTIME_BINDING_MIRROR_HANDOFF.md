# SDK Evaluator Governance Runtime Binding Mirror Handoff

Goal Task ID: `SDK-EVALUATOR-GOVERNANCE-POSTURE-MANIFEST-001`
Repository: `StegVerse-org/StegVerse-SDK`
Status: `ACTIVE_IMPLEMENTATION`

The evaluator-safe manifest builder is merged. Remaining work is the one-command runtime binding.

Required runtime sequence:

```text
source-native data
+ governance processor request
+ evaluator preregistration metadata
+ non-authorizing SDK posture request
-> canonical ingress manifest
-> canonical governance transition request
-> authoritative Interlock/InTr posture resolver callback
-> exact task + payload SHA-256 + transition-request SHA-256 binding verified by SDK
-> governance execution
-> returned InTr posture projection + normal governance result
```

The SDK must never calculate authoritative automatic/effective posture. The runtime callback is supplied by Interlock/InTr. Missing resolver when a posture request is present fails closed. Evaluator declaration remains outside governance decision evidence.

Manual work: None.
