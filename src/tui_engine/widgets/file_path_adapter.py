"""FilePathAdapter: Enhanced file path selection widget with Questionary integration.

This adapter implements ValueWidgetProtocol and provides advanced file path selection
functionality with professional styling, file browser integration, path validation,
extension filtering, and directory navigation.

Features:
- Professional themes and styling through QuestionaryStyleAdapter
- Interactive file browser with directory navigation
- File extension filtering and validation
- Path completion and validation
- Directory creation and management
- Multiple selection modes (files, directories, or both)
- Backward compatibility with existing TUI Engine components
"""
from __future__ import annotations

from typing import Any, Callable, Optional, Union, List, Dict, Set
from pathlib import Path
import os
import glob
import stat
import logging
from datetime import datetime

from .protocols import ValueWidgetProtocol

# Import Questionary and related components
try:
    import questionary
    from ..questionary_adapter import QuestionaryStyleAdapter
    from ..themes import TUIEngineThemes
    QUESTIONARY_AVAILABLE = True
except ImportError:
    QUESTIONARY_AVAILABLE = False
    logging.warning("Questionary not available, falling back to basic file path functionality")


class FileSystemNavigator:
    """Advanced file system navigation and filtering."""
    
    def __init__(
        self,
        base_path: Union[str, Path] = ".",
        allowed_extensions: Optional[Set[str]] = None,
        show_hidden: bool = False,
        files_only: bool = False,
        dirs_only: bool = False,
        follow_symlinks: bool = True
    ):
        """Initialize file system navigator.
        
        Args:
            base_path: Base directory for navigation
            allowed_extensions: Set of allowed file extensions (e.g., {'.py', '.txt'})
            show_hidden: Whether to show hidden files/directories
            files_only: Only show files (not directories)
            dirs_only: Only show directories (not files)
            follow_symlinks: Whether to follow symbolic links
        """
        self.base_path = Path(base_path).resolve()
        self.current_path = self.base_path
        self.allowed_extensions = allowed_extensions or set()
        self.show_hidden = show_hidden
        self.files_only = files_only
        self.dirs_only = dirs_only
        self.follow_symlinks = follow_symlinks
        
        # Ensure base path exists
        if not self.base_path.exists():
            raise ValueError(f"Base path does not exist: {self.base_path}")
        if not self.base_path.is_dir():
            raise ValueError(f"Base path is not a directory: {self.base_path}")
    
    def list_current_directory(self) -> List[Dict[str, Any]]:
        """List contents of current directory with metadata.
        
        Returns:
            List of file/directory info dictionaries
        """
        items = []
        
        try:
            # Add parent directory option if not at base
            if self.current_path != self.base_path:
                items.append({
                    'name': '..',
                    'display_name': '📁 .. (Parent Directory)',
                    'path': self.current_path.parent,
                    'is_dir': True,
                    'is_parent': True,
                    'size': 0,
                    'modified': None
                })
            
            # List directory contents
            for item in self.current_path.iterdir():
                try:
                    # Skip hidden files if not requested
                    if not self.show_hidden and item.name.startswith('.'):
                        continue
                    
                    # Handle symbolic links
                    if item.is_symlink() and not self.follow_symlinks:
                        continue
                    
                    is_dir = item.is_dir()
                    is_file = item.is_file()
                    
                    # Apply file/directory filters
                    if self.files_only and not is_file:
                        continue
                    if self.dirs_only and not is_dir:
                        continue
                    
                    # Apply extension filter for files
                    if is_file and self.allowed_extensions:
                        if item.suffix.lower() not in self.allowed_extensions:
                            continue
                    
                    # Get file metadata
                    try:
                        stat_info = item.stat()
                        size = stat_info.st_size if is_file else 0
                        modified = datetime.fromtimestamp(stat_info.st_mtime)
                    except (OSError, PermissionError):
                        size = 0
                        modified = None
                    
                    # Create display name with icon
                    if is_dir:
                        icon = "📁"
                        display_name = f"{icon} {item.name}/"
                    else:
                        icon = self._get_file_icon(item.suffix)
                        display_name = f"{icon} {item.name}"
                    
                    items.append({
                        'name': item.name,
                        'display_name': display_name,
                        'path': item,
                        'is_dir': is_dir,
                        'is_file': is_file,
                        'is_parent': False,
                        'size': size,
                        'modified': modified,
                        'extension': item.suffix.lower() if is_file else None
                    })
                    
                except (PermissionError, OSError) as e:
                    logging.debug(f"Skipping inaccessible item {item}: {e}")
                    continue
            
            # Sort items: directories first, then files, both alphabetically
            items.sort(key=lambda x: (
                not x['is_parent'],  # Parent directory first
                not x['is_dir'],     # Directories before files
                x['name'].lower()    # Alphabetical order
            ))
            
        except (PermissionError, OSError) as e:
            logging.error(f"Cannot list directory {self.current_path}: {e}")
        
        return items
    
    def navigate_to(self, path: Union[str, Path]) -> bool:
        """Navigate to a specific path.
        
        Args:
            path: Path to navigate to
            
        Returns:
            True if navigation successful, False otherwise
        """
        try:
            target_path = Path(path).resolve()
            
            # Ensure path is within base path for security
            if not self._is_within_base_path(target_path):
                logging.warning(f"Path outside base directory: {target_path}")
                return False
            
            if target_path.exists() and target_path.is_dir():
                self.current_path = target_path
                return True
            
        except (OSError, PermissionError) as e:
            logging.error(f"Cannot navigate to {path}: {e}")
        
        return False
    
    def navigate_up(self) -> bool:
        """Navigate to parent directory."""
        if self.current_path != self.base_path:
            return self.navigate_to(self.current_path.parent)
        return False
    
    def create_directory(self, name: str) -> bool:
        """Create a new directory in current path.
        
        Args:
            name: Name of directory to create
            
        Returns:
            True if creation successful, False otherwise
        """
        try:
            new_dir = self.current_path / name
            
            # Validate directory name
            if not self._is_valid_filename(name):
                return False
            
            if new_dir.exists():
                logging.warning(f"Directory already exists: {new_dir}")
                return False
            
            new_dir.mkdir(parents=False, exist_ok=False)
            return True
            
        except (OSError, PermissionError) as e:
            logging.error(f"Cannot create directory {name}: {e}")
            return False
    
    def get_path_completions(self, partial_path: str) -> List[str]:
        """Get path completions for a partial path.
        
        Args:
            partial_path: Partial path to complete
            
        Returns:
            List of possible completions
        """
        try:
            # Handle absolute vs relative paths
            if os.path.isabs(partial_path):
                search_path = Path(partial_path)
            else:
                search_path = self.current_path / partial_path
            
            # Get parent directory and filename pattern
            if search_path.is_dir():
                parent_dir = search_path
                pattern = "*"
            else:
                parent_dir = search_path.parent
                pattern = search_path.name + "*"
            
            # Ensure parent exists and is accessible
            if not parent_dir.exists() or not parent_dir.is_dir():
                return []
            
            # Find matching items
            completions = []
            for item in parent_dir.glob(pattern):
                try:
                    # Apply filters
                    if not self.show_hidden and item.name.startswith('.'):
                        continue
                    
                    if item.is_dir():
                        if not self.files_only:
                            rel_path = item.relative_to(self.current_path)
                            completions.append(str(rel_path) + "/")
                    elif item.is_file():
                        if not self.dirs_only:
                            if not self.allowed_extensions or item.suffix.lower() in self.allowed_extensions:
                                rel_path = item.relative_to(self.current_path)
                                completions.append(str(rel_path))
                                
                except (ValueError, OSError):
                    continue
            
            return sorted(completions)[:50]  # Limit results
            
        except (OSError, PermissionError):
            return []
    
    def validate_path(self, path: Union[str, Path]) -> tuple[bool, str]:
        """Validate a file path.
        
        Args:
            path: Path to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            path_obj = Path(path)
            
            # Check if path exists
            if not path_obj.exists():
                return False, f"Path does not exist: {path}"
            
            # Check if within base path
            if not self._is_within_base_path(path_obj.resolve()):
                return False, f"Path outside allowed directory: {path}"
            
            # Check file/directory type constraints
            if self.files_only and not path_obj.is_file():
                return False, f"Expected a file, got directory: {path}"
            
            if self.dirs_only and not path_obj.is_dir():
                return False, f"Expected a directory, got file: {path}"
            
            # Check extension constraints
            if path_obj.is_file() and self.allowed_extensions:
                if path_obj.suffix.lower() not in self.allowed_extensions:
                    allowed = ", ".join(sorted(self.allowed_extensions))
                    return False, f"File extension not allowed. Allowed: {allowed}"
            
            return True, ""
            
        except (OSError, PermissionError) as e:
            return False, f"Cannot access path: {e}"
    
    def get_current_path_info(self) -> Dict[str, Any]:
        """Get information about current path."""
        try:
            stat_info = self.current_path.stat()
            return {
                'path': str(self.current_path),
                'relative_path': str(self.current_path.relative_to(self.base_path)),
                'name': self.current_path.name,
                'is_base': self.current_path == self.base_path,
                'parent_exists': self.current_path.parent.exists(),
                'is_writable': os.access(self.current_path, os.W_OK),
                'item_count': len(list(self.current_path.iterdir())),
                'size': stat_info.st_size,
                'modified': datetime.fromtimestamp(stat_info.st_mtime)
            }
        except (OSError, PermissionError):
            return {
                'path': str(self.current_path),
                'relative_path': '',
                'name': self.current_path.name,
                'is_base': False,
                'parent_exists': False,
                'is_writable': False,
                'item_count': 0,
                'size': 0,
                'modified': None
            }
    
    def _get_file_icon(self, extension: str) -> str:
        """Get icon for file extension."""
        icon_map = {
            '.py': '🐍', '.js': '📜', '.ts': '📘', '.html': '🌐', '.css': '🎨',
            '.json': '📋', '.xml': '📄', '.yaml': '⚙️', '.yml': '⚙️',
            '.txt': '📝', '.md': '📖', '.rst': '📖', '.log': '📊',
            '.jpg': '🖼️', '.png': '🖼️', '.gif': '🖼️', '.svg': '🎯',
            '.mp4': '🎬', '.avi': '🎬', '.mp3': '🎵', '.wav': '🎵',
            '.zip': '📦', '.tar': '📦', '.gz': '📦', '.rar': '📦',
            '.exe': '⚙️', '.sh': '💻', '.bat': '💻', '.cmd': '💻'
        }
        return icon_map.get(extension.lower(), '📄')
    
    def _is_within_base_path(self, path: Path) -> bool:
        """Check if path is within base path."""
        try:
            path.resolve().relative_to(self.base_path.resolve())
            return True
        except ValueError:
            return False
    
    def _is_valid_filename(self, name: str) -> bool:
        """Check if filename is valid."""
        if not name or name in ('.', '..'):
            return False
        
        # Check for invalid characters
        invalid_chars = '<>:"/\\|?*'
        if any(char in name for char in invalid_chars):
            return False
        
        # Check for reserved names (Windows)
        reserved_names = {'CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4',
                         'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2',
                         'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'}
        if name.upper() in reserved_names:
            return False
        
        return True


class EnhancedFilePathAdapter(ValueWidgetProtocol):
    """Enhanced file path adapter with Questionary integration and file browser.
    
    This class provides advanced file path selection functionality with:
    - Professional theme integration
    - Interactive file browser
    - Path validation and completion
    - Extension filtering
    - Directory navigation
    """
    
    def __init__(
        self,
        message: str = "Select file:",
        style: Union[str, dict] = 'professional_blue',
        base_path: Union[str, Path] = ".",
        allowed_extensions: Optional[List[str]] = None,
        show_hidden: bool = False,
        files_only: bool = False,
        dirs_only: bool = False,
        create_dirs: bool = False,
        follow_symlinks: bool = True,
        validator: Optional[Callable[[str], Union[bool, str]]] = None,
        **kwargs
    ):
        """Initialize enhanced file path adapter.
        
        Args:
            message: Prompt message
            style: Theme name or custom style dict
            base_path: Base directory for file selection
            allowed_extensions: List of allowed file extensions
            show_hidden: Whether to show hidden files
            files_only: Only allow file selection
            dirs_only: Only allow directory selection
            create_dirs: Allow creating new directories
            follow_symlinks: Whether to follow symbolic links
            validator: Custom validation function
            **kwargs: Additional arguments for underlying widget
        """
        self.message = message
        self.base_path = Path(base_path)
        self.create_dirs = create_dirs
        self.validator = validator
        self.kwargs = kwargs
        
        # Initialize file system navigator
        ext_set = set(allowed_extensions) if allowed_extensions else None
        self.navigator = FileSystemNavigator(
            base_path=base_path,
            allowed_extensions=ext_set,
            show_hidden=show_hidden,
            files_only=files_only,
            dirs_only=dirs_only,
            follow_symlinks=follow_symlinks
        )
        
        # Initialize style adapter
        self.style_adapter = None
        self.current_theme = style
        if QUESTIONARY_AVAILABLE:
            self.style_adapter = QuestionaryStyleAdapter()
            if isinstance(style, str):
                self.style_adapter.set_theme(style)
        
        # Initialize widget state
        self._widget = None
        self._current_value = ""
        self._create_widget()
        
        # Adapter protocol attributes
        self._tui_path: str | None = None
        self._tui_focusable: bool = True
        self.element = None
    
    def _create_widget(self):
        """Create the underlying file path widget."""
        if not QUESTIONARY_AVAILABLE:
            # Fallback to basic implementation
            self._widget = None
            return
        
        try:
            # Get style for Questionary
            style = None
            if self.style_adapter:
                style = self.style_adapter.get_questionary_style()
            
            # Create path selection choices
            choices = self._get_current_choices()
            
            # Create Questionary select widget for file browser
            self._widget = questionary.select(
                message=self.message,
                choices=choices,
                style=style,
                **self.kwargs
            )
            
        except Exception as e:
            logging.warning(f"Failed to create Questionary file path widget: {e}")
            self._widget = None
    
    def _get_current_choices(self) -> List[questionary.Choice]:
        """Get current directory choices for Questionary."""
        if not QUESTIONARY_AVAILABLE:
            return []
        
        choices = []
        items = self.navigator.list_current_directory()
        
        # Add current path info as disabled choice
        path_info = self.navigator.get_current_path_info()
        current_path = path_info['relative_path'] or '.'
        choices.append(questionary.Choice(
            title=f"📍 Current: {current_path}",
            value=None,
            disabled=True
        ))
        
        # Add separator
        if items:
            choices.append(questionary.Separator())
        
        # Add directory items
        for item in items:
            choices.append(questionary.Choice(
                title=item['display_name'],
                value=item
            ))
        
        # Add option to enter path manually
        choices.append(questionary.Separator())
        choices.append(questionary.Choice(
            title="⌨️  Enter path manually",
            value={'manual_entry': True}
        ))
        
        # Add option to create directory if enabled
        if self.create_dirs and not self.navigator.files_only:
            choices.append(questionary.Choice(
                title="📁+ Create new directory",
                value={'create_directory': True}
            ))
        
        return choices
    
    def _handle_selection(self, selection: Any) -> Optional[str]:
        """Handle file browser selection.
        
        Args:
            selection: Selected item from file browser
            
        Returns:
            Selected path or None to continue browsing
        """
        if selection is None:
            return None
        
        # Handle special actions
        if isinstance(selection, dict):
            if selection.get('manual_entry'):
                return self._manual_path_entry()
            elif selection.get('create_directory'):
                return self._create_directory_dialog()
        
        # Handle file/directory selection
        if selection['is_parent']:
            # Navigate to parent directory
            self.navigator.navigate_up()
            self._refresh_widget()
            return None
        elif selection['is_dir']:
            # Navigate into directory
            self.navigator.navigate_to(selection['path'])
            self._refresh_widget()
            return None
        else:
            # File selected
            relative_path = selection['path'].relative_to(self.navigator.base_path)
            return str(relative_path)
    
    def _manual_path_entry(self) -> Optional[str]:
        """Handle manual path entry."""
        if not QUESTIONARY_AVAILABLE:
            return None
        
        try:
            # Get current path for default
            current_rel = self.navigator.current_path.relative_to(self.navigator.base_path)
            default_path = str(current_rel) if str(current_rel) != '.' else ''
            
            # Create autocomplete function
            def path_completer(text: str) -> List[str]:
                return self.navigator.get_path_completions(text)
            
            # Create path input widget
            style = None
            if self.style_adapter:
                style = self.style_adapter.get_questionary_style()
            
            result = questionary.autocomplete(
                message="Enter file path:",
                choices=path_completer,
                default=default_path,
                style=style
            ).ask()
            
            if result:
                # Validate the entered path
                full_path = self.navigator.base_path / result
                is_valid, error_msg = self.navigator.validate_path(full_path)
                
                if is_valid:
                    return result
                else:
                    # Show error and return to browser
                    questionary.print(f"❌ Error: {error_msg}", style="red")
                    return None
            
        except Exception as e:
            logging.error(f"Manual path entry failed: {e}")
        
        return None
    
    def _create_directory_dialog(self) -> Optional[str]:
        """Handle directory creation dialog."""
        if not QUESTIONARY_AVAILABLE:
            return None
        
        try:
            style = None
            if self.style_adapter:
                style = self.style_adapter.get_questionary_style()
            
            # Get directory name
            dir_name = questionary.text(
                message="Enter directory name:",
                style=style
            ).ask()
            
            if dir_name:
                if self.navigator.create_directory(dir_name):
                    questionary.print(f"✅ Created directory: {dir_name}", style="green")
                    # Refresh the widget to show new directory
                    self._refresh_widget()
                else:
                    questionary.print(f"❌ Failed to create directory: {dir_name}", style="red")
            
        except Exception as e:
            logging.error(f"Directory creation failed: {e}")
        
        return None
    
    def _refresh_widget(self):
        """Refresh the widget with current directory contents."""
        if self._widget and QUESTIONARY_AVAILABLE:
            try:
                # Update choices
                choices = self._get_current_choices()
                self._widget.choices = choices
            except Exception as e:
                logging.debug(f"Widget refresh failed: {e}")
    
    def focus(self) -> None:
        """Focus the file path widget."""
        if self._widget is None:
            return
        
        if hasattr(self._widget, "focus") and callable(self._widget.focus):
            try:
                self._widget.focus()
            except Exception:
                pass
    
    def _tui_sync(self) -> str | None:
        """Read the current value from the wrapped widget and return it."""
        return self._current_value
    
    def get_value(self) -> str:
        """Get the current selected path."""
        return self._current_value
    
    def set_value(self, value: Any) -> None:
        """Set the current path value."""
        self._current_value = str(value) if value is not None else ""
        
        # Try to navigate to the path's directory
        if self._current_value:
            try:
                path_obj = self.navigator.base_path / self._current_value
                if path_obj.exists():
                    if path_obj.is_dir():
                        self.navigator.navigate_to(path_obj)
                    else:
                        self.navigator.navigate_to(path_obj.parent)
                    self._refresh_widget()
            except Exception:
                pass
    
    def browse_for_path(self) -> Optional[str]:
        """Launch interactive file browser.
        
        Returns:
            Selected path or None if cancelled
        """
        if not QUESTIONARY_AVAILABLE:
            return self._fallback_path_selection()
        
        try:
            while True:
                # Update widget choices
                self._refresh_widget()
                
                # Get user selection
                selection = self._widget.ask()
                
                if selection is None:
                    # User cancelled
                    return None
                
                # Handle the selection
                result = self._handle_selection(selection)
                if result is not None:
                    self._current_value = result
                    return result
                
                # Continue browsing (result was None)
                
        except (KeyboardInterrupt, EOFError):
            return None
        except Exception as e:
            logging.error(f"File browser failed: {e}")
            return self._fallback_path_selection()
    
    def _fallback_path_selection(self) -> Optional[str]:
        """Fallback path selection when Questionary is not available."""
        try:
            # Simple text input fallback
            path = input(f"{self.message} ")
            if path:
                is_valid, error_msg = self.navigator.validate_path(self.navigator.base_path / path)
                if is_valid:
                    return path
                else:
                    print(f"Error: {error_msg}")
        except (KeyboardInterrupt, EOFError):
            pass
        return None
    
    def validate_current_path(self) -> tuple[bool, str]:
        """Validate the current path value."""
        if not self._current_value:
            return False, "No path selected"
        
        full_path = self.navigator.base_path / self._current_value
        is_valid, error_msg = self.navigator.validate_path(full_path)
        
        if is_valid and self.validator:
            try:
                result = self.validator(self._current_value)
                if isinstance(result, bool):
                    return result, "" if result else "Custom validation failed"
                elif isinstance(result, str):
                    return len(result) == 0, result
                else:
                    return bool(result), "" if result else "Custom validation failed"
            except Exception as e:
                return False, f"Validation error: {e}"
        
        return is_valid, error_msg
    
    def get_path_completions(self, partial_path: str) -> List[str]:
        """Get path completions for partial path."""
        return self.navigator.get_path_completions(partial_path)
    
    def navigate_to_directory(self, path: Union[str, Path]) -> bool:
        """Navigate to a specific directory."""
        return self.navigator.navigate_to(path)
    
    def get_current_directory_info(self) -> Dict[str, Any]:
        """Get information about current directory."""
        return self.navigator.get_current_path_info()
    
    def list_current_directory(self) -> List[Dict[str, Any]]:
        """List contents of current directory."""
        return self.navigator.list_current_directory()
    
    def change_theme(self, theme_name: str):
        """Change the current theme."""
        if not QUESTIONARY_AVAILABLE or not self.style_adapter:
            return
        
        self.current_theme = theme_name
        self.style_adapter.set_theme(theme_name)
        self._create_widget()
    
    def set_message(self, message: str):
        """Update the prompt message."""
        self.message = message
        self._create_widget()
    
    def enable_validation(self, validator: Callable[[str], Union[bool, str]]):
        """Enable custom path validation."""
        self.validator = validator
    
    def disable_validation(self):
        """Disable custom validation."""
        self.validator = None
    
    def is_questionary_enhanced(self) -> bool:
        """Check if Questionary enhancement is active."""
        return QUESTIONARY_AVAILABLE and self._widget is not None
    
    def get_widget_info(self) -> dict:
        """Get comprehensive widget information."""
        path_info = self.navigator.get_current_path_info()
        return {
            'use_questionary': self.is_questionary_enhanced(),
            'has_validator': self.validator is not None,
            'current_value': self._current_value,
            'theme': self.current_theme,
            'message': self.message,
            'base_path': str(self.navigator.base_path),
            'current_directory': path_info['path'],
            'files_only': self.navigator.files_only,
            'dirs_only': self.navigator.dirs_only,
            'allowed_extensions': list(self.navigator.allowed_extensions) if self.navigator.allowed_extensions else None,
            'show_hidden': self.navigator.show_hidden,
            'create_dirs': self.create_dirs
        }
    
    @property
    def ptk_widget(self) -> Any:
        """Get the underlying prompt-toolkit widget."""
        return self._widget
    
    def __repr__(self) -> str:
        """String representation of the adapter."""
        return f"<EnhancedFilePathAdapter message='{self.message}' value='{self._current_value}' base='{self.navigator.base_path}'>"


class FilePathAdapter(ValueWidgetProtocol):
    """Backward-compatible FilePathAdapter that automatically uses enhanced features when available.
    
    This class maintains full backward compatibility while providing access to enhanced
    file browser features when they're available and beneficial.
    """
    
    # runtime contract attributes
    _tui_path: str | None = None
    _tui_focusable: bool = True
    
    def __init__(self, widget: Any | None = None, element: Any | None = None, **kwargs):
        """Initialize FilePathAdapter with backward compatibility.
        
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
                    self._enhanced_adapter = EnhancedFilePathAdapter(**kwargs)
                    self._widget = self._enhanced_adapter.ptk_widget
                except Exception as e:
                    logging.warning(f"Failed to create enhanced file path adapter, falling back to basic: {e}")
    
    def focus(self) -> None:
        """Focus the file path widget."""
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
            # common attribute names for path widgets
            for attr in ['text', 'value', 'current_value', 'path']:
                if hasattr(w, attr):
                    return getattr(w, attr)
        except Exception:
            pass
        
        return self._current_value
    
    def get_value(self) -> str:
        """Get the current path value."""
        if self._enhanced_adapter:
            return self._enhanced_adapter.get_value()
        
        return self._current_value
    
    def set_value(self, value: Any) -> None:
        """Set the path value."""
        if self._enhanced_adapter:
            self._enhanced_adapter.set_value(value)
            return
        
        self._current_value = str(value) if value is not None else ""
        
        # Update underlying widget
        w = self._widget
        if w is None:
            return
        
        try:
            for attr in ['text', 'value', 'current_value', 'path']:
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
    def browse_for_path(self) -> Optional[str]:
        """Launch interactive file browser (enhanced feature)."""
        if self._enhanced_adapter:
            return self._enhanced_adapter.browse_for_path()
        return None
    
    def get_path_completions(self, partial_path: str) -> List[str]:
        """Get path completions (enhanced feature)."""
        if self._enhanced_adapter:
            return self._enhanced_adapter.get_path_completions(partial_path)
        return []
    
    def validate_current_path(self) -> tuple[bool, str]:
        """Validate current path (enhanced feature)."""
        if self._enhanced_adapter:
            return self._enhanced_adapter.validate_current_path()
        return True, ""
    
    def navigate_to_directory(self, path: Union[str, Path]) -> bool:
        """Navigate to directory (enhanced feature)."""
        if self._enhanced_adapter:
            return self._enhanced_adapter.navigate_to_directory(path)
        return False
    
    def get_current_directory_info(self) -> Dict[str, Any]:
        """Get current directory info (enhanced feature)."""
        if self._enhanced_adapter:
            return self._enhanced_adapter.get_current_directory_info()
        return {}
    
    def list_current_directory(self) -> List[Dict[str, Any]]:
        """List current directory (enhanced feature)."""
        if self._enhanced_adapter:
            return self._enhanced_adapter.list_current_directory()
        return []
    
    def change_theme(self, theme_name: str):
        """Change the current theme (enhanced feature)."""
        if self._enhanced_adapter:
            self._enhanced_adapter.change_theme(theme_name)
    
    def set_message(self, message: str):
        """Update the prompt message (enhanced feature)."""
        if self._enhanced_adapter:
            self._enhanced_adapter.set_message(message)
    
    def enable_validation(self, validator: Callable[[str], Union[bool, str]]):
        """Enable validation (enhanced feature)."""
        if self._enhanced_adapter:
            self._enhanced_adapter.enable_validation(validator)
    
    def disable_validation(self):
        """Disable validation (enhanced feature)."""
        if self._enhanced_adapter:
            self._enhanced_adapter.disable_validation()
    
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
            'base_path': '.',
            'legacy_mode': self._legacy_mode
        }
    
    def __repr__(self) -> str:
        """String representation of the adapter."""
        if self._enhanced_adapter:
            return repr(self._enhanced_adapter)
        return f"<FilePathAdapter widget={self._widget!r} value='{self._current_value}'>"


# Convenience functions for creating file path widgets

def create_file_selector(
    message: str = "Select file:",
    base_path: Union[str, Path] = ".",
    extensions: Optional[List[str]] = None,
    style: str = 'professional_blue',
    **kwargs
) -> FilePathAdapter:
    """Create a FilePathAdapter for file selection.
    
    Args:
        message: Prompt message
        base_path: Base directory for selection
        extensions: List of allowed file extensions
        style: Theme name for styling
        **kwargs: Additional arguments
        
    Returns:
        FilePathAdapter configured for file selection
    """
    return FilePathAdapter(
        message=message,
        base_path=base_path,
        allowed_extensions=extensions,
        files_only=True,
        style=style,
        **kwargs
    )


def create_directory_selector(
    message: str = "Select directory:",
    base_path: Union[str, Path] = ".",
    allow_create: bool = True,
    style: str = 'professional_blue',
    **kwargs
) -> FilePathAdapter:
    """Create a FilePathAdapter for directory selection.
    
    Args:
        message: Prompt message
        base_path: Base directory for selection
        allow_create: Allow creating new directories
        style: Theme name for styling
        **kwargs: Additional arguments
        
    Returns:
        FilePathAdapter configured for directory selection
    """
    return FilePathAdapter(
        message=message,
        base_path=base_path,
        dirs_only=True,
        create_dirs=allow_create,
        style=style,
        **kwargs
    )


def create_config_file_selector(
    message: str = "Select configuration file:",
    base_path: Union[str, Path] = ".",
    style: str = 'professional_blue',
    **kwargs
) -> FilePathAdapter:
    """Create a FilePathAdapter for configuration file selection.
    
    Args:
        message: Prompt message
        base_path: Base directory for selection
        style: Theme name for styling
        **kwargs: Additional arguments
        
    Returns:
        FilePathAdapter configured for config files
    """
    config_extensions = ['.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf']
    
    return FilePathAdapter(
        message=message,
        base_path=base_path,
        allowed_extensions=config_extensions,
        files_only=True,
        style=style,
        **kwargs
    )


def create_image_file_selector(
    message: str = "Select image file:",
    base_path: Union[str, Path] = ".",
    style: str = 'professional_blue',
    **kwargs
) -> FilePathAdapter:
    """Create a FilePathAdapter for image file selection.
    
    Args:
        message: Prompt message
        base_path: Base directory for selection
        style: Theme name for styling
        **kwargs: Additional arguments
        
    Returns:
        FilePathAdapter configured for image files
    """
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.tiff']
    
    return FilePathAdapter(
        message=message,
        base_path=base_path,
        allowed_extensions=image_extensions,
        files_only=True,
        style=style,
        **kwargs
    )


def create_source_file_selector(
    message: str = "Select source file:",
    base_path: Union[str, Path] = ".",
    language: Optional[str] = None,
    style: str = 'professional_blue',
    **kwargs
) -> FilePathAdapter:
    """Create a FilePathAdapter for source code file selection.
    
    Args:
        message: Prompt message
        base_path: Base directory for selection
        language: Programming language (e.g., 'python', 'javascript')
        style: Theme name for styling
        **kwargs: Additional arguments
        
    Returns:
        FilePathAdapter configured for source files
    """
    language_extensions = {
        'python': ['.py', '.pyx', '.pyi'],
        'javascript': ['.js', '.jsx', '.mjs'],
        'typescript': ['.ts', '.tsx'],
        'java': ['.java'],
        'c': ['.c', '.h'],
        'cpp': ['.cpp', '.cxx', '.cc', '.hpp', '.hxx'],
        'csharp': ['.cs'],
        'go': ['.go'],
        'rust': ['.rs'],
        'php': ['.php'],
        'ruby': ['.rb'],
        'swift': ['.swift'],
        'kotlin': ['.kt', '.kts']
    }
    
    if language and language.lower() in language_extensions:
        extensions = language_extensions[language.lower()]
    else:
        # All common source file extensions
        extensions = [ext for exts in language_extensions.values() for ext in exts]
    
    return FilePathAdapter(
        message=message,
        base_path=base_path,
        allowed_extensions=extensions,
        files_only=True,
        style=style,
        **kwargs
    )