"""Compatibility shim package for prompt-toolkit fallbacks.

Expose small helpers to obtain prompt-toolkit widgets or safe fallbacks.
"""

from .ptk_shims import maybe_checkboxlist, maybe_radiolist

__all__ = ["maybe_checkboxlist", "maybe_radiolist"]
