from typing import Optional, Callable, Any

QuestionaryFactory = Callable[[], Any]

class QuestionaryProvider:
    def __init__(self):
        self._factory: Optional[QuestionaryFactory] = None
        self._cached = None

    def set_factory(self, factory: QuestionaryFactory) -> None:
        self._factory = factory
        self._cached = None

    def get_questionary(self):
        if self._factory is not None:
            if self._cached is None:
                self._cached = self._factory()
            return self._cached
        # fallback to importing questionary lazily
        try:
            import questionary
            return questionary
        except Exception:
            raise RuntimeError("questionary not available and no factory injected")

    def clear_factory(self):
        self._factory = None
        self._cached = None

_provider = QuestionaryProvider()

def set_questionary_factory(factory: QuestionaryFactory) -> None:
    _provider.set_factory(factory)

def get_questionary():
    return _provider.get_questionary()

def clear_questionary_factory():
    _provider.clear_factory()
