"""Small PromptSession adapter to allow legacy blocking prompts without a full Application."""

from typing import Any, Optional


class PromptSessionAdapter:
    def __init__(self, session_factory: Optional[Any] = None) -> None:
        self._factory = session_factory

    def prompt(self, *args: Any, **kwargs: Any) -> Any:
        # Lazy import to avoid hard dependency during headless tests
        if self._factory is not None:
            session = self._factory()
            return session.prompt(*args, **kwargs)
        try:
            from prompt_toolkit import PromptSession
            session = PromptSession()
            return session.prompt(*args, **kwargs)
        except Exception:
            raise RuntimeError("prompt_toolkit.PromptSession is not available")
