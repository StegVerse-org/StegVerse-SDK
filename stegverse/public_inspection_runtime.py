"""Canonical public-inspection runtime.

The default execution path is sovereign/local and therefore cannot be blocked by a
third-party host. Hosted HTTP transport remains available separately through
`stegverse.production_validation_runtime` when explicitly desired.
"""
from .sovereign_validation_runtime import *  # noqa: F401,F403
from .sovereign_validation_runtime import main

if __name__ == "__main__":
    raise SystemExit(main())
