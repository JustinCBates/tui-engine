import threading
from typing import Any, Dict

class PageState:
    def __init__(self):
        self._values: Dict[str, Any] = {}
        self._meta: Dict[str, Any] = {}
        self._lock = threading.Lock()

    def get(self, key: str, default: Any = None) -> Any:
        return self._values.get(key, default)

    def set(self, key: str, value: Any) -> None:
        with self._lock:
            self._values[key] = value

    def has(self, key: str) -> bool:
        return key in self._values

    def set_if_absent(self, key: str, value: Any) -> bool:
        """Atomically set value if absent. Return True if set."""
        with self._lock:
            if key in self._values:
                return False
            self._values[key] = value
            return True

    def snapshot(self) -> Dict[str, Any]:
        with self._lock:
            return {"values": dict(self._values), "meta": dict(self._meta)}

    def apply_snapshot(self, snapshot: Dict[str, Any]) -> None:
        with self._lock:
            self._values.update(snapshot.get("values", {}))
            self._meta.update(snapshot.get("meta", {}))
