from typing import Any, Callable, Dict, List, Tuple


class EventBus:
    def __init__(self) -> None:
        self._subs: Dict[str, List[Callable[[Any], None]]] = {}

    def publish(self, topic: str, payload: Any = None) -> None:
        for h in list(self._subs.get(topic, [])):
            try:
                h(payload)
            except Exception:
                # swallow exceptions for now; adapter may log
                pass

    def subscribe(self, topic: str, handler: Callable[[Any], None]) -> Tuple[str, Callable[[Any], None]]:
        self._subs.setdefault(topic, []).append(handler)
        return (topic, handler)

    def unsubscribe(self, token: Tuple[str, Callable[[Any], None]]) -> None:
        topic, handler = token
        if topic in self._subs and handler in self._subs[topic]:
            self._subs[topic].remove(handler)
