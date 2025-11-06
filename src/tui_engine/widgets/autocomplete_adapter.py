"""AutocompleteAdapter: Enhanced autocomplete widget with Questionary integration.

This adapter implements ValueWidgetProtocol and provides intelligent text completion
functionality with professional styling, fuzzy matching, dynamic suggestions,
and advanced completion features.

Features:
- Professional themes and styling through QuestionaryStyleAdapter
- Intelligent fuzzy matching with configurable algorithms
- Dynamic suggestion loading and caching
- Multi-source completion (static lists, functions, APIs)
- Real-time filtering and ranking
- Backward compatibility with existing TUI Engine text inputs
- Advanced completion modes (prefix, substring, fuzzy)
"""
from __future__ import annotations

from typing import Any, Callable, Optional, Union, List, Tuple, Dict, Iterable
import logging
import re
import difflib
from functools import lru_cache

from .protocols import ValueWidgetProtocol

# Import Questionary and related components
try:
    import questionary
    from ..questionary_adapter import QuestionaryStyleAdapter
    from ..themes import TUIEngineThemes
    QUESTIONARY_AVAILABLE = True
except ImportError:
    QUESTIONARY_AVAILABLE = False
    logging.warning("Questionary not available, falling back to basic autocomplete functionality")


class CompletionEngine:
    """Advanced completion engine with multiple matching algorithms."""
    
    def __init__(
        self,
        case_sensitive: bool = False,
        fuzzy_threshold: float = 0.6,
        max_results: int = 10,
        prefer_prefix: bool = True
    ):
        """Initialize completion engine.
        
        Args:
            case_sensitive: Whether matching is case sensitive
            fuzzy_threshold: Minimum similarity score for fuzzy matches (0.0-1.0)
            max_results: Maximum number of results to return
            prefer_prefix: Whether to prefer prefix matches over fuzzy matches
        """
        self.case_sensitive = case_sensitive
        self.fuzzy_threshold = fuzzy_threshold
        self.max_results = max_results
        self.prefer_prefix = prefer_prefix
    
    def complete(
        self, 
        query: str, 
        candidates: List[str], 
        algorithm: str = "smart"
    ) -> List[Tuple[str, float]]:
        """Complete a query against candidate strings.
        
        Args:
            query: Input query to complete
            candidates: List of candidate completion strings
            algorithm: Completion algorithm ("prefix", "substring", "fuzzy", "smart")
            
        Returns:
            List of (completion, score) tuples sorted by relevance
        """
        if not query.strip():
            return [(candidate, 1.0) for candidate in candidates[:self.max_results]]
        
        query_processed = query if self.case_sensitive else query.lower()
        results = []
        
        for candidate in candidates:
            candidate_processed = candidate if self.case_sensitive else candidate.lower()
            score = self._calculate_score(query_processed, candidate_processed, algorithm)
            
            if score > 0:
                results.append((candidate, score))
        
        # Sort by score (descending) and limit results
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:self.max_results]
    
    def _calculate_score(self, query: str, candidate: str, algorithm: str) -> float:
        """Calculate relevance score for a candidate."""
        if algorithm == "prefix":
            return self._prefix_score(query, candidate)
        elif algorithm == "substring":
            return self._substring_score(query, candidate)
        elif algorithm == "fuzzy":
            return self._fuzzy_score(query, candidate)
        elif algorithm == "smart":
            return self._smart_score(query, candidate)
        else:
            return self._smart_score(query, candidate)
    
    def _prefix_score(self, query: str, candidate: str) -> float:
        """Calculate prefix match score."""
        if candidate.startswith(query):
            # Exact prefix match - score based on how much of candidate is matched
            return len(query) / len(candidate)
        return 0.0
    
    def _substring_score(self, query: str, candidate: str) -> float:
        """Calculate substring match score."""
        if query in candidate:
            # Substring match - prefer earlier positions and exact matches
            pos = candidate.find(query)
            position_bonus = (len(candidate) - pos) / len(candidate)
            coverage = len(query) / len(candidate)
            return (coverage * 0.7) + (position_bonus * 0.3)
        return 0.0
    
    def _fuzzy_score(self, query: str, candidate: str) -> float:
        """Calculate fuzzy match score using sequence matching."""
        matcher = difflib.SequenceMatcher(None, query, candidate)
        similarity = matcher.ratio()
        
        if similarity >= self.fuzzy_threshold:
            return similarity
        return 0.0
    
    def _smart_score(self, query: str, candidate: str) -> float:
        """Smart scoring that combines multiple algorithms."""
        # Try prefix first (highest priority)
        prefix_score = self._prefix_score(query, candidate)
        if prefix_score > 0:
            return prefix_score + 0.5  # Bonus for prefix matches
        
        # Try substring matching
        substring_score = self._substring_score(query, candidate)
        if substring_score > 0:
            return substring_score + 0.2  # Bonus for substring matches
        
        # Fall back to fuzzy matching
        fuzzy_score = self._fuzzy_score(query, candidate)
        if fuzzy_score >= self.fuzzy_threshold:
            return fuzzy_score
        
        return 0.0


class EnhancedAutocompleteAdapter(ValueWidgetProtocol):
    """Enhanced Autocomplete adapter with Questionary integration and intelligent completion.
    
    This class provides advanced autocomplete functionality with:
    - Professional theme integration
    - Multiple completion sources and algorithms
    - Dynamic suggestion loading
    - Real-time filtering and ranking
    - Caching and performance optimization
    """
    
    def __init__(
        self,
        message: str = "Enter value:",
        style: Union[str, dict] = 'professional_blue',
        completions: Optional[Union[List[str], Callable[[str], List[str]]]] = None,
        completion_sources: Optional[List[Callable[[str], List[str]]]] = None,
        algorithm: str = "smart",
        case_sensitive: bool = False,
        fuzzy_threshold: float = 0.6,
        max_results: int = 10,
        min_input_length: int = 1,
        cache_completions: bool = True,
        cache_size: int = 128,
        validator: Optional[Callable[[str], Union[bool, str]]] = None,
        placeholder: str = "",
        **kwargs
    ):
        """Initialize enhanced autocomplete adapter.
        
        Args:
            message: Input prompt message
            style: Theme name or custom style dict
            completions: Static list of completions or function to generate them
            completion_sources: List of completion source functions
            algorithm: Completion algorithm ("prefix", "substring", "fuzzy", "smart")
            case_sensitive: Whether matching is case sensitive
            fuzzy_threshold: Minimum similarity for fuzzy matches
            max_results: Maximum number of completion results
            min_input_length: Minimum input length before showing completions
            cache_completions: Whether to cache completion results
            cache_size: Maximum number of cached completion results
            validator: Function to validate final input
            placeholder: Placeholder text
            **kwargs: Additional arguments for underlying widget
        """
        self.message = message
        self.completions = completions
        self.completion_sources = completion_sources or []
        self.algorithm = algorithm
        self.min_input_length = min_input_length
        self.cache_completions = cache_completions
        self.validator = validator
        self.placeholder = placeholder
        self.kwargs = kwargs
        
        # Initialize completion engine
        self.completion_engine = CompletionEngine(
            case_sensitive=case_sensitive,
            fuzzy_threshold=fuzzy_threshold,
            max_results=max_results
        )
        
        # Initialize style adapter
        self.style_adapter = None
        self.current_theme = style
        if QUESTIONARY_AVAILABLE:
            self.style_adapter = QuestionaryStyleAdapter()
            if isinstance(style, str):
                self.style_adapter.set_theme(style)
        
        # Initialize widget
        self._widget = None
        self._current_value = ""
        self._cached_completions = {}
        if cache_completions:
            self._get_completions_cached = lru_cache(maxsize=cache_size)(self._get_completions_uncached)
        else:
            self._get_completions_cached = self._get_completions_uncached
        
        self._create_widget()
        
        # Adapter protocol attributes
        self._tui_path: str | None = None
        self._tui_focusable: bool = True
        self.element = None
    
    def _create_widget(self):
        """Create the underlying autocomplete widget."""
        if not QUESTIONARY_AVAILABLE:
            # Fallback to basic implementation
            self._widget = None
            return
        
        try:
            # Get style for Questionary
            style = None
            if self.style_adapter:
                style = self.style_adapter.get_questionary_style()
            
            # Create completion function for Questionary
            def get_completions_for_questionary(text: str) -> List[str]:
                if len(text) < self.min_input_length:
                    return []
                
                completions = self._get_completions_cached(text)
                # Return just the completion strings (Questionary doesn't need scores)
                return [completion for completion, score in completions]
            
            # Create Questionary autocomplete widget
            self._widget = questionary.autocomplete(
                message=self.message,
                choices=get_completions_for_questionary,
                default=self._current_value,
                style=style,
                **self.kwargs
            )
            
        except Exception as e:
            logging.warning(f"Failed to create Questionary autocomplete widget: {e}")
            self._widget = None
    
    def _get_completions_uncached(self, query: str) -> List[Tuple[str, float]]:
        """Get completions for a query without caching."""
        all_candidates = set()
        
        # Get static completions
        if self.completions:
            if callable(self.completions):
                try:
                    static_completions = self.completions(query)
                    all_candidates.update(static_completions)
                except Exception as e:
                    logging.warning(f"Error getting static completions: {e}")
            else:
                all_candidates.update(self.completions)
        
        # Get completions from sources
        for source in self.completion_sources:
            try:
                source_completions = source(query)
                all_candidates.update(source_completions)
            except Exception as e:
                logging.warning(f"Error getting completions from source: {e}")
        
        # Use completion engine to rank results
        candidates = list(all_candidates)
        return self.completion_engine.complete(query, candidates, self.algorithm)
    
    def focus(self) -> None:
        """Focus the autocomplete widget."""
        if self._widget is None:
            return
        
        if hasattr(self._widget, "focus") and callable(self._widget.focus):
            try:
                self._widget.focus()
            except Exception:
                pass
    
    def _tui_sync(self) -> str | None:
        """Read the current value from the wrapped widget and return it."""
        if self._widget is None:
            return self._current_value
        
        try:
            # For Questionary widgets
            if hasattr(self._widget, 'default'):
                return self._widget.default
            
            # Common attribute names
            for attr in ['text', 'value', 'current_value']:
                if hasattr(self._widget, attr):
                    return getattr(self._widget, attr)
                    
        except Exception:
            pass
        
        return self._current_value
    
    def get_value(self) -> str:
        """Get the current input value."""
        return self._current_value
    
    def set_value(self, value: Any) -> None:
        """Set the input value."""
        self._current_value = str(value) if value is not None else ""
        
        # Update underlying widget
        if self._widget is None:
            return
        
        try:
            # For Questionary widgets, update default
            if hasattr(self._widget, 'default'):
                self._widget.default = self._current_value
                return
            
            # Try common attribute names
            for attr in ['text', 'value', 'current_value']:
                if hasattr(self._widget, attr):
                    setattr(self._widget, attr, self._current_value)
                    return
                    
        except Exception:
            pass
    
    def get_completions(self, query: str) -> List[Tuple[str, float]]:
        """Get ranked completions for a query.
        
        Args:
            query: Input query to complete
            
        Returns:
            List of (completion, score) tuples
        """
        if len(query) < self.min_input_length:
            return []
        
        return self._get_completions_cached(query)
    
    def add_completion_source(self, source: Callable[[str], List[str]]):
        """Add a new completion source function."""
        self.completion_sources.append(source)
        self._clear_cache()
    
    def remove_completion_source(self, source: Callable[[str], List[str]]):
        """Remove a completion source function."""
        if source in self.completion_sources:
            self.completion_sources.remove(source)
            self._clear_cache()
    
    def set_static_completions(self, completions: Union[List[str], Callable[[str], List[str]]]):
        """Set or update static completions."""
        self.completions = completions
        self._clear_cache()
    
    def _clear_cache(self):
        """Clear completion cache."""
        if hasattr(self._get_completions_cached, 'cache_clear'):
            self._get_completions_cached.cache_clear()
        self._cached_completions.clear()
    
    def update_completion_settings(
        self, 
        algorithm: Optional[str] = None,
        case_sensitive: Optional[bool] = None,
        fuzzy_threshold: Optional[float] = None,
        max_results: Optional[int] = None
    ):
        """Update completion engine settings."""
        if algorithm is not None:
            self.algorithm = algorithm
        
        if case_sensitive is not None:
            self.completion_engine.case_sensitive = case_sensitive
        
        if fuzzy_threshold is not None:
            self.completion_engine.fuzzy_threshold = fuzzy_threshold
        
        if max_results is not None:
            self.completion_engine.max_results = max_results
        
        self._clear_cache()
    
    def validate_input(self, value: str) -> Tuple[bool, str]:
        """Validate the input value.
        
        Args:
            value: Value to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if self.validator is None:
            return True, ""
        
        try:
            result = self.validator(value)
            if isinstance(result, bool):
                return result, "" if result else "Invalid input"
            elif isinstance(result, str):
                return len(result) == 0, result
            else:
                return bool(result), "" if result else "Invalid input"
        except Exception as e:
            return False, f"Validation error: {e}"
    
    def change_theme(self, theme_name: str):
        """Change the current theme and recreate widget."""
        if not QUESTIONARY_AVAILABLE or not self.style_adapter:
            return
        
        self.current_theme = theme_name
        self.style_adapter.set_theme(theme_name)
        self._create_widget()
        
        # Restore current value
        if self._current_value:
            self.set_value(self._current_value)
    
    def set_message(self, message: str):
        """Update the prompt message."""
        self.message = message
        self._create_widget()
    
    def set_placeholder(self, placeholder: str):
        """Update the placeholder text."""
        self.placeholder = placeholder
        self._create_widget()
    
    def enable_validation(self, validator: Callable[[str], Union[bool, str]]):
        """Enable input validation."""
        self.validator = validator
    
    def disable_validation(self):
        """Disable input validation."""
        self.validator = None
    
    def get_completion_stats(self) -> Dict[str, Any]:
        """Get statistics about completion performance."""
        cache_info = None
        if hasattr(self._get_completions_cached, 'cache_info'):
            cache_info = self._get_completions_cached.cache_info()
        
        return {
            'completion_sources': len(self.completion_sources),
            'has_static_completions': self.completions is not None,
            'algorithm': self.algorithm,
            'case_sensitive': self.completion_engine.case_sensitive,
            'fuzzy_threshold': self.completion_engine.fuzzy_threshold,
            'max_results': self.completion_engine.max_results,
            'min_input_length': self.min_input_length,
            'cache_enabled': self.cache_completions,
            'cache_info': cache_info
        }
    
    def is_questionary_enhanced(self) -> bool:
        """Check if Questionary enhancement is active."""
        return QUESTIONARY_AVAILABLE and self._widget is not None
    
    def get_style_adapter(self) -> Optional[QuestionaryStyleAdapter]:
        """Get the style adapter instance."""
        return self.style_adapter
    
    def get_widget_info(self) -> dict:
        """Get comprehensive widget information."""
        return {
            'use_questionary': self.is_questionary_enhanced(),
            'has_validator': self.validator is not None,
            'current_value': self._current_value,
            'theme': self.current_theme,
            'message': self.message,
            'placeholder': self.placeholder,
            'algorithm': self.algorithm,
            'completion_sources': len(self.completion_sources),
            'min_input_length': self.min_input_length,
            'cache_enabled': self.cache_completions
        }
    
    @property
    def ptk_widget(self) -> Any:
        """Get the underlying prompt-toolkit widget."""
        return self._widget
    
    def __repr__(self) -> str:
        """String representation of the adapter."""
        return f"<EnhancedAutocompleteAdapter message='{self.message}' value='{self._current_value}' sources={len(self.completion_sources)}>"


class AutocompleteAdapter(ValueWidgetProtocol):
    """Backward-compatible AutocompleteAdapter that automatically uses enhanced features when available.
    
    This class maintains full backward compatibility while providing access to enhanced
    Questionary features when they're available and beneficial.
    """
    
    # runtime contract attributes
    _tui_path: str | None = None
    _tui_focusable: bool = True
    
    def __init__(self, widget: Any | None = None, element: Any | None = None, **kwargs):
        """Initialize AutocompleteAdapter with backward compatibility.
        
        Args:
            widget: Legacy widget object (for backward compatibility)
            element: Element object (for backward compatibility)
            **kwargs: Additional arguments for enhanced functionality
        """
        self.element = element
        
        # If we have a legacy widget, use traditional behavior
        if widget is not None:
            self._widget = widget
            self._enhanced_adapter = None
            self._legacy_mode = True
            self._current_value = ""
        else:
            # Use enhanced adapter for new functionality
            self._enhanced_adapter = None
            self._widget = None
            self._legacy_mode = False
            self._current_value = ""
            
            # Try to create enhanced adapter if Questionary is available
            if QUESTIONARY_AVAILABLE and kwargs:
                try:
                    self._enhanced_adapter = EnhancedAutocompleteAdapter(**kwargs)
                    self._widget = self._enhanced_adapter.ptk_widget
                except Exception as e:
                    logging.warning(f"Failed to create enhanced autocomplete adapter, falling back to basic: {e}")

    def focus(self) -> None:
        """Focus the autocomplete widget."""
        if self._enhanced_adapter:
            self._enhanced_adapter.focus()
            return
        
        w = self._widget
        if w is None:
            return
        if hasattr(w, "focus") and callable(w.focus):
            try:
                w.focus()
            except Exception:
                pass

    def _tui_sync(self) -> str | None:
        """Read the current value from the wrapped widget and return it."""
        if self._enhanced_adapter:
            return self._enhanced_adapter._tui_sync()
        
        w = self._widget
        if w is None:
            return self._current_value
        
        try:
            # common attribute names for text widgets
            for attr in ['text', 'value', 'current_value']:
                if hasattr(w, attr):
                    return getattr(w, attr)
        except Exception:
            pass
        
        return self._current_value

    def get_value(self) -> str:
        """Get the current input value."""
        if self._enhanced_adapter:
            return self._enhanced_adapter.get_value()
        
        return self._current_value

    def set_value(self, value: Any) -> None:
        """Set the input value."""
        if self._enhanced_adapter:
            self._enhanced_adapter.set_value(value)
            return
        
        self._current_value = str(value) if value is not None else ""
        
        # Update underlying widget
        w = self._widget
        if w is None:
            return
        
        try:
            for attr in ['text', 'value', 'current_value']:
                if hasattr(w, attr):
                    setattr(w, attr, self._current_value)
                    return
        except Exception:
            pass
    
    @property
    def ptk_widget(self) -> Any:
        """Get the underlying prompt-toolkit widget."""
        return self._widget
    
    # Enhanced functionality delegation (when available)
    def get_completions(self, query: str) -> List[Tuple[str, float]]:
        """Get ranked completions for a query (enhanced feature)."""
        if self._enhanced_adapter:
            return self._enhanced_adapter.get_completions(query)
        return []
    
    def add_completion_source(self, source: Callable[[str], List[str]]):
        """Add a completion source (enhanced feature)."""
        if self._enhanced_adapter:
            self._enhanced_adapter.add_completion_source(source)
    
    def remove_completion_source(self, source: Callable[[str], List[str]]):
        """Remove a completion source (enhanced feature)."""
        if self._enhanced_adapter:
            self._enhanced_adapter.remove_completion_source(source)
    
    def set_static_completions(self, completions: Union[List[str], Callable[[str], List[str]]]):
        """Set static completions (enhanced feature)."""
        if self._enhanced_adapter:
            self._enhanced_adapter.set_static_completions(completions)
    
    def update_completion_settings(self, **kwargs):
        """Update completion settings (enhanced feature)."""
        if self._enhanced_adapter:
            self._enhanced_adapter.update_completion_settings(**kwargs)
    
    def validate_input(self, value: str) -> Tuple[bool, str]:
        """Validate input (enhanced feature)."""
        if self._enhanced_adapter:
            return self._enhanced_adapter.validate_input(value)
        return True, ""
    
    def change_theme(self, theme_name: str):
        """Change the current theme (enhanced feature)."""
        if self._enhanced_adapter:
            self._enhanced_adapter.change_theme(theme_name)
    
    def set_message(self, message: str):
        """Update the prompt message (enhanced feature)."""
        if self._enhanced_adapter:
            self._enhanced_adapter.set_message(message)
    
    def set_placeholder(self, placeholder: str):
        """Update placeholder text (enhanced feature)."""
        if self._enhanced_adapter:
            self._enhanced_adapter.set_placeholder(placeholder)
    
    def enable_validation(self, validator: Callable[[str], Union[bool, str]]):
        """Enable validation (enhanced feature)."""
        if self._enhanced_adapter:
            self._enhanced_adapter.enable_validation(validator)
    
    def disable_validation(self):
        """Disable validation (enhanced feature)."""
        if self._enhanced_adapter:
            self._enhanced_adapter.disable_validation()
    
    def get_completion_stats(self) -> Dict[str, Any]:
        """Get completion statistics (enhanced feature)."""
        if self._enhanced_adapter:
            return self._enhanced_adapter.get_completion_stats()
        return {
            'completion_sources': 0,
            'algorithm': 'none',
            'legacy_mode': True
        }
    
    def is_questionary_enhanced(self) -> bool:
        """Check if Questionary enhancement is active."""
        return self._enhanced_adapter is not None and self._enhanced_adapter.is_questionary_enhanced()
    
    def get_widget_info(self) -> dict:
        """Get comprehensive widget information."""
        if self._enhanced_adapter:
            return self._enhanced_adapter.get_widget_info()
        return {
            'use_questionary': False,
            'has_validator': False,
            'current_value': self._current_value,
            'theme': 'default',
            'completion_sources': 0,
            'algorithm': 'none',
            'legacy_mode': self._legacy_mode
        }

    def __repr__(self) -> str:  # pragma: no cover - trivial
        """String representation of the adapter."""
        if self._enhanced_adapter:
            return repr(self._enhanced_adapter)
        return f"<AutocompleteAdapter widget={self._widget!r} value='{self._current_value}'>"


# Convenience functions for creating autocomplete widgets

def create_autocomplete(
    message: str = "Enter value:",
    completions: Optional[List[str]] = None,
    style: str = 'professional_blue',
    algorithm: str = "smart",
    **kwargs
) -> AutocompleteAdapter:
    """Create an AutocompleteAdapter with enhanced features.
    
    Args:
        message: Input prompt message
        completions: Static list of completions
        style: Theme name for styling
        algorithm: Completion algorithm
        **kwargs: Additional arguments for EnhancedAutocompleteAdapter
        
    Returns:
        AutocompleteAdapter with enhanced features when available
    """
    return AutocompleteAdapter(
        message=message,
        completions=completions,
        style=style,
        algorithm=algorithm,
        **kwargs
    )


def create_file_autocomplete(
    message: str = "Enter filename:",
    base_path: str = ".",
    extensions: Optional[List[str]] = None,
    **kwargs
) -> AutocompleteAdapter:
    """Create an autocomplete adapter for file paths.
    
    Args:
        message: Input prompt message
        base_path: Base directory for file completion
        extensions: List of file extensions to include
        **kwargs: Additional arguments
        
    Returns:
        AutocompleteAdapter configured for file completion
    """
    import os
    import glob
    
    def file_completion_source(query: str) -> List[str]:
        """Generate file completions."""
        try:
            # Combine base path with query
            search_path = os.path.join(base_path, query + "*")
            matches = glob.glob(search_path)
            
            results = []
            for match in matches:
                rel_path = os.path.relpath(match, base_path)
                
                # Filter by extensions if specified
                if extensions:
                    _, ext = os.path.splitext(rel_path)
                    if ext.lower() not in [e.lower() for e in extensions]:
                        continue
                
                results.append(rel_path)
            
            return results[:50]  # Limit results
        except Exception:
            return []
    
    return AutocompleteAdapter(
        message=message,
        completion_sources=[file_completion_source],
        algorithm="prefix",
        **kwargs
    )


def create_command_autocomplete(
    message: str = "Enter command:",
    commands: Optional[List[str]] = None,
    **kwargs
) -> AutocompleteAdapter:
    """Create an autocomplete adapter for commands.
    
    Args:
        message: Input prompt message
        commands: List of available commands
        **kwargs: Additional arguments
        
    Returns:
        AutocompleteAdapter configured for command completion
    """
    import shutil
    
    def system_command_source(query: str) -> List[str]:
        """Get system commands starting with query."""
        if not query:
            return []
        
        # Get common system commands
        common_commands = [
            'ls', 'cd', 'pwd', 'mkdir', 'rmdir', 'rm', 'cp', 'mv',
            'cat', 'less', 'head', 'tail', 'grep', 'find', 'which',
            'ps', 'top', 'kill', 'chmod', 'chown', 'tar', 'zip',
            'git', 'python', 'pip', 'npm', 'docker', 'curl', 'wget'
        ]
        
        # Filter commands that start with query
        matches = [cmd for cmd in common_commands if cmd.startswith(query)]
        
        # Also check if command exists in PATH
        try:
            if shutil.which(query):
                matches.insert(0, query)
        except Exception:
            pass
        
        return matches[:20]
    
    all_commands = commands or []
    
    return AutocompleteAdapter(
        message=message,
        completions=all_commands,
        completion_sources=[system_command_source],
        algorithm="prefix",
        **kwargs
    )