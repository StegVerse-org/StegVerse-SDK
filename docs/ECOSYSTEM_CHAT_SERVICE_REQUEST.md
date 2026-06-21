# Ecosystem Chat Service Request

## Purpose

This document records the accepted request body shapes for `POST /api/ecosystem-chat`.

## Legacy body

The service still accepts the original Site payload directly:

```text
fields
manifest
receipt_window
```

## Binding-aware envelope

The service also accepts an envelope:

```text
payload
destination_config
```

`payload` contains the original three-layer Site payload.

`destination_config` is optional and may contain:

```text
destination_name
destination_type
```

## Supported destination type

```text
master-records
local-test
```

## Boundary

A ready destination binding does not perform a write.

Default issuer and write behavior remain fail-closed unless explicit implementations are injected.
