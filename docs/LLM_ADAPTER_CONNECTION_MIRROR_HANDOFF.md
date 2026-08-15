# SDK LLM Adapter Connection Mirror Handoff

## Identity

```text
goal_id: SDK-LLM-ADAPTER-CONNECTION-010
originating_goal: cloned SDK users can select Connect my LLM and bind their user-controlled LLM to StegVerse through the canonical LLM-adapter
repository: StegVerse-org/StegVerse-SDK
branch: main
canonical_adapter: StegVerse-org/LLM-adapter
adapter_surface: /user-llm
credential_authority: TV/TVC
GitHub token runtime authority: NONE
non-TV/TVC secret/token required: FALSE
```

## Installed source

```text
stegverse/llm_connection.py
stegverse/llm_connect_cli.py
stegverse/sdk_surfaces.py
pyproject.toml
tests/test_llm_connection.py
docs/CONNECT_MY_LLM.md
tasks/SDK-LLM-ADAPTER-CONNECTION-010.json
claims/SDK-LLM-ADAPTER-CONNECTION-010.json
```

Implementation commits:

```text
d2c5f679d9878783a06eece2edf4c950cb53db34 adapter binding/discovery/descriptor/submission helper
8fbc16dfbfbed9e299765de9ed7c55d11f3d0465 interactive/noninteractive connect CLI
4b8c77d983ecd509b5f14920db4cc1252871fac5 console entry point
3ce858df10461467556b60732d8916af22e521b9 SDK help/surface registry
1e453dfce20bc2027e37e15d3922b4e821702c5d focused tests
16bd42b9362279a4ee476f557af660c319aa258e user procedure
```

## User path

```text
python -m pip install -e .
stegverse surfaces
stegverse help-surface "connect my llm"
stegverse-connect-llm
```

The connector discovers or probes the existing adapter health/readiness/capabilities/activation-proof endpoints and writes a credential-free descriptor. Every StegVerse submission from the connected LLM is bound to:

```text
POST <adapter-base>/v1/user-llm/requests
```

Invariant:

```text
ALL_LLM_SUBMISSIONS_ENTER_STEGVERSE_THROUGH_LLM_ADAPTER
```

MCP remains a separate capability/tool transport; it does not replace the LLM-adapter model boundary.

## Secret and authority boundary

The SDK recursively rejects secret/token-shaped descriptor and payload fields. It accepts no provider API key, password, Authorization header, provider token, GitHub token, private key, or generic credential map. Protected credential authority remains TV/TVC.

Connection success does not grant StegGate admission, provider execution, publication authority, Master Records custody, or product activation.

## Validation state

```text
source installed on main: YES
source inspection: COMPLETE
focused tests installed: YES
focused tests executed: NOT YET PROVEN
hosted workflow run for implementation head: NONE OBSERVED
exact cloned-SDK install/CLI/adapter handshake: PENDING
```

No workflow pass is claimed. The task remains `IMPLEMENTED_PENDING_EXECUTED_VALIDATION` until a credential-free machine lane runs `tests/test_llm_connection.py` and one exact CLI handshake against the adapter `/user-llm` surface.

## Collision / ownership

The SDK owns only connection discovery, help/CLI, non-secret descriptor persistence, and request-envelope construction. `StegVerse-org/LLM-adapter` remains the adapter/runtime owner; StegCore remains governance authority; TV/TVC remains credential/route authority; Master Records remains custody/reconstruction authority.

## Continuation

```text
SDK validation/task: tasks/SDK-LLM-ADAPTER-CONNECTION-010.json
adapter portable surface: StegVerse-org/LLM-adapter/llm_adapter/user_llm_service.py
Ecosystem Chat runtime: StegVerse-org/LLM-adapter#18
VACC runtime: StegVerse-org/LLM-adapter#90
SDK release: tasks/SDK-SOVEREIGN-RELEASE-ACTIVATION-004.json
```

Release/package activation must include these commits and remain TV/TVC-authorized; GitHub Actions and GitHub tokens receive no release/runtime authority.

## Completion accounting

```text
developed files: 8/8
scaffolding/stubs: 0
missing required files: 0
source integration: COMPLETE
executed validation: 0/2 required proofs
package/release activation: PENDING
```
