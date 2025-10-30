"""Default helpers: DefaultApplier and DependencyMap

These utilities provide simple, well-tested helpers for applying defaults
and constructing values on-demand in a thread-safe way. They support both
sync and async factory callables (async factories will be awaited).
"""
from __future__ import annotations

import asyncio
import threading
from typing import Any, Callable, Optional


class DependencyMap:
    """A small thread-safe mapping that supports atomic set-if-absent.

    Usage:
        m = DependencyMap()
        v = m.set_if_absent('k', lambda: compute())
    """

    def __init__(self) -> None:
        self._map: dict[Any, Any] = {}
        self._lock = threading.Lock()

    def get(self, key: Any, default: Any = None) -> Any:
        return self._map.get(key, default)

    def set(self, key: Any, value: Any) -> None:
        with self._lock:
            self._map[key] = value

    def set_if_absent(self, key: Any, factory: Callable[[], Any]) -> Any:
        """Atomically set value for key using factory if not present.

        If another thread sets the key concurrently, the existing value is
        returned and the factory result discarded.
        """
        with self._lock:
            if key in self._map:
                return self._map[key]
            val = factory()
            self._map[key] = val
            return val


class DefaultApplier:
    """Apply defaults into mapping-like objects using factories.

    Supports sync factories and async factories (a coroutine function).
    When an async factory is provided, DefaultApplier will run it using
    `asyncio.get_event_loop().run_until_complete` when required.
    """

    def __init__(self, target: dict[Any, Any]) -> None:
        self._target = target
        self._lock = threading.Lock()

    def apply(self, key: Any, factory: Callable[[], Any]) -> Any:
        """Ensure `key` exists in the target. If missing, call factory and set.

        If factory is a coroutine function or returns a coroutine, it will be
        awaited before setting.
        """
        # Fast-path without lock for existing key
        if key in self._target:
            return self._target[key]

        with self._lock:
            if key in self._target:
                return self._target[key]

            result = factory()
            # If factory returned a coroutine, await it
            if asyncio.iscoroutine(result):
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # Running inside existing loop; create task and wait
                        coro = result
                        fut = asyncio.run_coroutine_threadsafe(coro, loop)
                        result = fut.result()
                    else:
                        result = loop.run_until_complete(result)
                except RuntimeError:
                    # No running loop; use new loop
                    result = asyncio.new_event_loop().run_until_complete(result)

            self._target[key] = result
            return result
