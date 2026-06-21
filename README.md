# STEGVERSE SDK

![PyPI](https://img.shields.io/pypi/v/stegverse-sdk)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![Build](https://github.com/StegVerse-org/StegVerse-SDK/actions/workflows/validate.yml/badge.svg)
![License](https://img.shields.io/github/license/StegVerse-org/StegVerse-SDK)

> Execution is not assumed. Execution is admitted.

StegVerse verifies every action **before** it happens and produces cryptographic proof of that decision.

---

## WHAT IT DOES

You propose an action  
→ StegVerse evaluates it  
→ Decision: **ALLOW | DENY | DEFER**  
→ If allowed: execution + receipt

Every executed action produces a verifiable receipt.

---

## ECOSYSTEM CHAT SDK INTAKE

The SDK now includes a pre-backend intake validator, transport-free backend handler, and HTTP adapter for the completed Site Ecosystem Chat form gateway.

```python
from stegverse.ecosystem_chat_http import handle_ecosystem_chat_http

status, response = handle_ecosystem_chat_http(
    "POST",
    "/api/ecosystem-chat",
    request_body,
)
```

The adapter accepts the Site three-layer payload only when `fields`, `manifest`, and `receipt_window` remain distinct and internally consistent. In this stage, `receipt_id` remains `None`; receipt issuance is not installed in the Site-facing intake path.
