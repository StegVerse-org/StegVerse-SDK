# Ecosystem Chat Local Runner

## Purpose

This note records the local runner for the Ecosystem Chat SDK pipeline.

## Command

```bash
python scripts/run_ecosystem_chat_service.py
```

The runner is event-bounded, not a resident service: it handles `--max-requests` requests (default `1`) and exits with a JSON receipt. `--max-requests 0` is an explicit local-verification mode only. `--bind`/`--port` select the loopback address (default `127.0.0.1:8080`).

## Local endpoint

```text
http://127.0.0.1:8080/api/ecosystem-chat
```

## Result sections

```text
intake
receipt_decision
record_export
```

## Current limits

```text
receipt_id: null
external_write_complete: false
```
