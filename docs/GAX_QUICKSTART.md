# GAX Quickstart

Generated: `2026-06-14`

## Import

```python
from stegverse.admissibility_exchange import build_gax_exchange
from stegverse.admissibility_exchange import verify_gax_exchange
from stegverse.admissibility_exchange import export_gax_json
from stegverse.admissibility_exchange import load_gax_json
```

## Minimal round trip

```python
exchange = build_gax_exchange(bundle)
payload = export_gax_json(exchange)
loaded = load_gax_json(payload)
assert verify_gax_exchange(loaded) is True
```

## Schema

```text
schemas/admissibility/gax-exchange.schema.json
```

## Example

```bash
python examples/admissibility_exchange_check.py
```

## Notes

GAX is the JSON exchange wrapper for a Governed Admissibility Bundle.

It is intended for Site and SDK import/export compatibility.
