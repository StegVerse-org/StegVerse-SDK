# Ecosystem Chat Deployment Readiness

## Purpose

This manifest records the current hosted-service readiness state for Ecosystem Chat SDK intake.

## Service command

```bash
python scripts/run_ecosystem_chat_service.py
```

## WSGI callable

```text
stegverse.ecosystem_chat_wsgi:application
```

## Endpoint path

```text
POST /api/ecosystem-chat
```

## Current response sections

```text
intake
receipt_decision
record_export
```

## Ready components

```text
Site browser form: complete
SDK intake validator: installed
SDK backend handler: installed
SDK HTTP adapter: installed
SDK pipeline: installed
SDK pipeline HTTP adapter: installed
Local runner: installed
WSGI callable: installed
```

## Pending components

```text
Hosted service target: not selected
Receipt issuer: not installed
External record persistence: not installed
```

## Activation boundary

The local runner may be used to verify request and response shape.

The WSGI callable may be mounted by a selected hosted service target.

Production activation requires a hosted service target and governed receipt issuer.
