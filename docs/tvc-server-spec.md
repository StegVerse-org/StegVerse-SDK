TVC (TrustVaultController) Server Specification
=================================================

This document defines the TVC endpoint that the tvc-ephemeral.yml
workflow calls to request short-lived secrets.

Endpoint: POST /v1/issue

Headers:
Content-Type: application/json
X-TV-Identity: 

Request Body:
{
"identity": {
"repo": "StegVerse-org/StegVerse-SDK",
"run_id": "123456789",
"actor": "StegVerse",
"timestamp": "2026-04-29T12:30:00Z",
"secret_type": "pypi",
"ttl": 600
},
"secret_type": "pypi",
"ttl_seconds": 600
}

TVC Policy Engine validates:
1. TV identity signature is valid and not revoked
2. Repo is in allowlist for requested secret_type
3. Actor has release permissions for this repo
4. Requested TTL <= max_policy_ttl (default 3600s)
5. Rate limit not exceeded for this repo/actor

Response (200 OK):
{
"secret": "pypi-xxxxxxxxxxxx",
"token_id": "tvc_abc123def456",
"expiry": "2026-04-29T12:40:00Z",
"type": "pypi",
"scope": "StegVerse-org/StegVerse-SDK"
}

Response (403 Forbidden):
{
"error": "Policy denied",
"reason": "Repo not in allowlist for secret_type pypi",
"token_id": "tvc_denied_abc123"
}

Response (401 Unauthorized):
{
"error": "Invalid TV identity",
"reason": "Signature verification failed"
}

Secret Lifecycle:
- Minted on request
- Stored in-memory only (no persistence)
- Auto-revoked at expiry
- Manual revoke via DELETE /v1/revoke/:token_id

Audit Log (per request):
- token_id
- repo
- actor
- secret_type
- timestamp
- outcome (success/denied/error)
- expiry

Supported secret_type values:
- pypi      → PyPI API token
- github    → GitHub PAT with contents:write
- npm       → npm publish token
- docker    → Docker Hub token
- aws       → AWS STS temporary credentials
- gcp       → GCP service account key
- azure     → Azure service principal

Deployment Notes:
- TVC should run in an isolated environment (not on GitHub Actions)
- TV identity keys are managed by TV (TrustVault) repo
- TVC must have access to a secure secret store (HashiCorp Vault, AWS Secrets Manager, etc.)
- TVC endpoint should be behind TLS 1.3 minimum
