# Connect my LLM

The SDK connects a user-controlled LLM through the canonical `StegVerse-org/LLM-adapter` user-LLM surface. The SDK does not accept provider API keys, passwords, Authorization headers, GitHub tokens, generic credential maps, or other protected secrets. Protected credential authority remains TV/TVC.

## 1. Install the cloned SDK

```bash
python -m pip install -e .
```

Discover the surface:

```bash
stegverse surfaces
stegverse help-surface "connect my llm"
```

## 2. Start or locate the canonical LLM-adapter user-LLM surface

The connector can discover these local development locations automatically:

```text
http://127.0.0.1:8080
http://127.0.0.1:8000/user-llm
http://127.0.0.1:18080/user-llm
```

An operator may instead provide an admitted adapter URL explicitly. The URL is connection metadata, not a credential.

The canonical adapter surface exposes:

```text
GET  /healthz
GET  /readyz
GET  /v1/user-llm/capabilities
GET  /v1/user-llm/activation-proof
POST /v1/user-llm/requests
```

## 3. Connect

Interactive/local discovery:

```bash
stegverse-connect-llm
```

Explicit non-interactive example:

```bash
stegverse-connect-llm \
  --adapter-url http://127.0.0.1:8000/user-llm \
  --user-id local-user \
  --llm-id my-llm \
  --provider ollama \
  --model llama3.2
```

The command probes health, readiness, capabilities, and the adapter activation proof. A `CONNECTED` result is returned only when the adapter reports:

```text
health.status = OK
readiness.state = READY
activation.state = ACTIVATED
authority_attached != true
```

The SDK then writes a credential-free descriptor under:

```text
.stegverse/llm-connections/<connection-id>.json
```

The descriptor contains the adapter endpoint, user/LLM/provider/model identity metadata, non-authorizing scopes, and the exact submission endpoint. It contains no secret.

## 4. Route every StegVerse submission through the adapter

The connection descriptor establishes this invariant:

```text
ALL_LLM_SUBMISSIONS_ENTER_STEGVERSE_THROUGH_LLM_ADAPTER
```

The connected LLM first discovers bounded capabilities at:

```text
GET <adapter-base>/v1/user-llm/capabilities
```

Every StegVerse request from that LLM is sent to:

```text
POST <adapter-base>/v1/user-llm/requests
```

Request shape:

```json
{
  "identity": {
    "user_id": "local-user",
    "llm_id": "my-llm",
    "provider": "ollama",
    "model": "llama3.2",
    "scopes": ["demo:read"]
  },
  "route": "demo_test_suite",
  "action": "inspect",
  "payload": {
    "question": "show the public StegVerse test surface"
  }
}
```

The SDK helper `stegverse.llm_connection.build_submission()` builds the same shape and rejects secret/token-shaped payload fields before submission.

## Boundaries

A successful connection proves only that a user-controlled LLM can reach the canonical adapter surface with a credential-free identity descriptor. It does not prove or grant StegGate admission, consequence execution, provider authority, publication authority, Master Records custody, or public product activation.

MCP remains a separate tool/capability transport. If an LLM is connected to StegVerse, its StegVerse submissions use the LLM-adapter boundary even if that LLM also exposes MCP tools.
