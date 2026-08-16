from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from stegverse.public_inspection import validate_public_inspection_request


def validate(payload: dict) -> None:
    """Validate with the same implementation used by the SDK runtime."""
    validate_public_inspection_request(payload)


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: validate_public_inspection_request.py <request.json>", file=sys.stderr)
        return 2
    path = Path(argv[1])
    payload = json.loads(path.read_text(encoding="utf-8"))
    validate(payload)
    print(f"PASS {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
