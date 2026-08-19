#!/usr/bin/env python3
"""Compatibility shim for legacy setuptools invocations.

Package metadata is defined canonically in pyproject.toml. Keeping this shim
metadata-free prevents setup.py and PEP 517 builds from advertising different
versions, dependencies, Python requirements, or console entry points.
"""

from setuptools import setup


if __name__ == "__main__":
    setup()
