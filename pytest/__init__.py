"""Minimal local pytest compatibility package for route artifact CI.

This repository's route-artifact workflow invokes `python -m pytest`.
The local runner in `pytest.__main__` supports the simple test functions used by
this repository when external pytest is not installed by the workflow.
"""
