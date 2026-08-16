"""Canonical public-inspection runtime.

The default execution path is sovereign/local and therefore cannot be blocked by a
third-party host. Hosted HTTP transport remains available separately through
`stegverse.production_validation_runtime` when explicitly desired.

New governed runs bind the installed production release set into exact-run evidence;
replay and reconstruction report the original release set alongside the current one.
"""
from .versioned_sovereign_runtime import *  # noqa: F401,F403
from .versioned_sovereign_runtime import main

if __name__ == "__main__":
    raise SystemExit(main())
