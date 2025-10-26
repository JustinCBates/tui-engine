from typing import Any, Dict

from .core.page_base import PageBase
from .integration.questionary_bridge import QuestionaryBridge


class Page(PageBase):
    """Higher-level Page with a runtime `run()` that executes prompts.

    This class extends the foundational Core Page (which intentionally
    leaves `run()` unimplemented) and wires a simple QuestionaryBridge to
    execute components added to the page.
    """

    def run(self) -> Dict[str, Any]:
        bridge = QuestionaryBridge(self.state)
        bridge.run(self.components)
        # Return flattened state for convenience
        try:
            return self.state.get_all_state()
        except Exception:
            # Fallback to a simple dict if PageState doesn't implement
            # get_all_state
            return {}
