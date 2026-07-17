"""Minimal local pytest compatibility package for repository CI.

This package intentionally implements only the pytest surface used by the
repository's self-contained test runner. It does not claim full pytest
compatibility.
"""
from __future__ import annotations

import re
from contextlib import AbstractContextManager
from dataclasses import dataclass
from typing import Any, Callable, Iterable


@dataclass
class _RaisesContext(AbstractContextManager["_RaisesContext"]):
    expected_exception: type[BaseException] | tuple[type[BaseException], ...]
    match: str | None = None
    value: BaseException | None = None

    def __enter__(self) -> "_RaisesContext":
        return self

    def __exit__(self, exc_type, exc, traceback) -> bool:
        if exc is None:
            raise AssertionError(
                f"DID NOT RAISE {self.expected_exception!r}"
            )
        if not isinstance(exc, self.expected_exception):
            return False
        if self.match is not None and re.search(self.match, str(exc)) is None:
            raise AssertionError(
                f"exception message {str(exc)!r} does not match {self.match!r}"
            )
        self.value = exc
        return True


def raises(
    expected_exception: type[BaseException] | tuple[type[BaseException], ...],
    *,
    match: str | None = None,
) -> _RaisesContext:
    return _RaisesContext(expected_exception=expected_exception, match=match)


class _Mark:
    def parametrize(
        self,
        argnames: str | Iterable[str],
        argvalues: Iterable[Any],
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        if isinstance(argnames, str):
            names = tuple(name.strip() for name in argnames.split(",") if name.strip())
        else:
            names = tuple(argnames)
        if not names:
            raise ValueError("parametrize requires at least one argument name")

        values = list(argvalues)

        def decorator(function: Callable[..., Any]) -> Callable[..., Any]:
            existing = list(getattr(function, "_pytest_parametrize", []))
            existing.append((names, values))
            setattr(function, "_pytest_parametrize", existing)
            return function

        return decorator


mark = _Mark()

__all__ = ["mark", "raises"]
