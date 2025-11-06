"""
Editor adapter for TUI Engine with Questionary integration.

This module provides a comprehensive text editor interface with advanced features:
- Multi-line text editing with full cursor control
- Syntax highlighting for multiple programming languages
- Line numbers with optional highlighting
- Search and replace functionality with regex support
- Auto-indentation and smart formatting
- Undo/redo operations with history management
- Professional styling with theme integration
- Multiple editing modes (insert, overwrite, readonly)

Classes:
    EditorMode: Enum for editing modes
    SyntaxHighlighter: Syntax highlighting engine
    SearchOptions: Search and replace configuration
    EditorHistory: Undo/redo management
    EditorRenderer: Text rendering with highlighting
    EnhancedEditorAdapter: Feature-rich text editor
    EditorAdapter: Backward-compatible wrapper

Dependencies:
    - questionary: For interactive prompts
    - prompt_toolkit: For advanced text editing
    - pygments: For syntax highlighting (optional)
    - re: For search and replace
    - typing: For type hints
"""

import re
import sys
from enum import Enum
from typing import Dict, List, Optional, Tuple, Union, Any, Callable, Pattern
from dataclasses import dataclass, field
from pathlib import Path
import questionary
from prompt_toolkit import print_formatted_text
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.application import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.document import Document
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import HSplit, VSplit, Window
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.widgets import TextArea, Frame
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.styles import Style

# Optional syntax highlighting support
try:
    from pygments import highlight
    from pygments.lexers import get_lexer_by_name, guess_lexer
    from pygments.formatters import TerminalFormatter
    from pygments.util import ClassNotFound
    PYGMENTS_AVAILABLE = True
except ImportError:
    PYGMENTS_AVAILABLE = False

# Import TUI Engine components
try:
    from ..themes import TUIEngineThemes
    from ..style_adapter import QuestionaryStyleAdapter
except ImportError:
    # Fallback for testing
    class TUIEngineThemes:
        @staticmethod
        def get_theme(variant: str) -> Dict[str, Any]:
            return {}
    
    class QuestionaryStyleAdapter:
        @staticmethod
        def convert_style(theme: Dict[str, Any]) -> Any:
            return None


class EditorMode(Enum):
    """Text editor modes."""
    INSERT = "insert"
    OVERWRITE = "overwrite"
    READONLY = "readonly"
    VISUAL = "visual"


class EditorLanguage(Enum):
    """Supported syntax highlighting languages."""
    PLAIN = "plain"
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    HTML = "html"
    CSS = "css"
    JSON = "json"
    YAML = "yaml"
    MARKDOWN = "markdown"
    SQL = "sql"
    BASH = "bash"
    C = "c"
    CPP = "cpp"
    JAVA = "java"
    GO = "go"
    RUST = "rust"


@dataclass
class SearchOptions:
    """Search and replace configuration."""
    case_sensitive: bool = False
    regex: bool = False
    whole_word: bool = False
    wrap_around: bool = True
    highlight_all: bool = True
    replace_all: bool = False


@dataclass
class EditorPosition:
    """Cursor position in the editor."""
    line: int = 0
    column: int = 0
    
    def __str__(self) -> str:
        return f"{self.line + 1}:{self.column + 1}"


@dataclass
class EditorSelection:
    """Text selection in the editor."""
    start: EditorPosition
    end: EditorPosition
    text: str = ""


class EditorHistory:
    """Manages undo/redo operations for the editor."""
    
    def __init__(self, max_history: int = 100):
        """
        Initialize editor history.
        
        Args:
            max_history: Maximum number of operations to remember
        """
        self.max_history = max_history
        self.history: List[Tuple[str, str]] = []  # (action, content)
        self.current_index = -1
        self.saved_index = -1
    
    def add_operation(self, action: str, content: str):
        """Add an operation to history."""
        # Remove any redo history if we're adding a new operation
        if self.current_index < len(self.history) - 1:
            self.history = self.history[:self.current_index + 1]
        
        # Add new operation
        self.history.append((action, content))
        self.current_index = len(self.history) - 1
        
        # Limit history size
        if len(self.history) > self.max_history:
            self.history.pop(0)
            self.current_index -= 1
            if self.saved_index >= 0:
                self.saved_index -= 1
    
    def can_undo(self) -> bool:
        """Check if undo is possible."""
        return self.current_index >= 0
    
    def can_redo(self) -> bool:
        """Check if redo is possible."""
        return self.current_index < len(self.history) - 1
    
    def undo(self) -> Optional[Tuple[str, str]]:
        """Undo the last operation."""
        if self.can_undo():
            operation = self.history[self.current_index]
            self.current_index -= 1
            return operation
        return None
    
    def redo(self) -> Optional[Tuple[str, str]]:
        """Redo the next operation."""
        if self.can_redo():
            self.current_index += 1
            return self.history[self.current_index]
        return None
    
    def mark_saved(self):
        """Mark the current state as saved."""
        self.saved_index = self.current_index
    
    def is_modified(self) -> bool:
        """Check if content has been modified since last save."""
        return self.current_index != self.saved_index


class SyntaxHighlighter:
    """Provides syntax highlighting for various programming languages."""
    
    def __init__(self, language: EditorLanguage = EditorLanguage.PLAIN):
        """
        Initialize syntax highlighter.
        
        Args:
            language: Programming language for highlighting
        """
        self.language = language
        self.lexer = None
        self.formatter = None
        
        if PYGMENTS_AVAILABLE and language != EditorLanguage.PLAIN:
            try:
                self.lexer = get_lexer_by_name(language.value)
                self.formatter = TerminalFormatter()
            except ClassNotFound:
                pass  # Fall back to plain text
    
    def highlight_text(self, text: str) -> str:
        """
        Apply syntax highlighting to text.
        
        Args:
            text: Text to highlight
            
        Returns:
            Highlighted text with ANSI codes
        """
        if not self.lexer or not self.formatter:
            return text
        
        try:
            return highlight(text, self.lexer, self.formatter).rstrip('\n')
        except Exception:
            return text  # Fall back to plain text on error
    
    def highlight_line(self, line: str, line_number: int) -> FormattedText:
        """
        Highlight a single line for prompt-toolkit.
        
        Args:
            line: Line text
            line_number: Line number (0-based)
            
        Returns:
            FormattedText for prompt-toolkit
        """
        if not self.lexer:
            return [('', line)]
        
        try:
            # Simple highlighting for now - can be enhanced
            if self.language == EditorLanguage.PYTHON:
                return self._highlight_python_line(line)
            elif self.language == EditorLanguage.JAVASCRIPT:
                return self._highlight_javascript_line(line)
            else:
                return [('', line)]
        except Exception:
            return [('', line)]
    
    def _highlight_python_line(self, line: str) -> FormattedText:
        """Highlight Python syntax."""
        result = []
        
        # Keywords
        keywords = {'def', 'class', 'if', 'else', 'elif', 'for', 'while', 'try', 'except', 'import', 'from', 'return'}
        
        # Simple tokenization
        tokens = re.findall(r'\w+|[^\w\s]|\s+', line)
        
        for token in tokens:
            if token in keywords:
                result.append(('class:keyword', token))
            elif token.startswith('#'):
                result.append(('class:comment', token))
            elif token.startswith('"') or token.startswith("'"):
                result.append(('class:string', token))
            elif token.isdigit():
                result.append(('class:number', token))
            else:
                result.append(('', token))
        
        return result
    
    def _highlight_javascript_line(self, line: str) -> FormattedText:
        """Highlight JavaScript syntax."""
        result = []
        
        # Keywords
        keywords = {'function', 'var', 'let', 'const', 'if', 'else', 'for', 'while', 'return', 'class', 'import', 'export'}
        
        # Simple tokenization
        tokens = re.findall(r'\w+|[^\w\s]|\s+', line)
        
        for token in tokens:
            if token in keywords:
                result.append(('class:keyword', token))
            elif token.startswith('//'):
                result.append(('class:comment', token))
            elif token.startswith('"') or token.startswith("'") or token.startswith('`'):
                result.append(('class:string', token))
            elif token.isdigit():
                result.append(('class:number', token))
            else:
                result.append(('', token))
        
        return result
    
    @classmethod
    def detect_language(cls, filename: str, content: str = "") -> EditorLanguage:
        """
        Detect programming language from filename or content.
        
        Args:
            filename: File name
            content: File content
            
        Returns:
            Detected language
        """
        if not filename:
            return EditorLanguage.PLAIN
        
        # Extension mapping
        ext_map = {
            '.py': EditorLanguage.PYTHON,
            '.js': EditorLanguage.JAVASCRIPT,
            '.ts': EditorLanguage.TYPESCRIPT,
            '.html': EditorLanguage.HTML,
            '.htm': EditorLanguage.HTML,
            '.css': EditorLanguage.CSS,
            '.json': EditorLanguage.JSON,
            '.yaml': EditorLanguage.YAML,
            '.yml': EditorLanguage.YAML,
            '.md': EditorLanguage.MARKDOWN,
            '.sql': EditorLanguage.SQL,
            '.sh': EditorLanguage.BASH,
            '.bash': EditorLanguage.BASH,
            '.c': EditorLanguage.C,
            '.cpp': EditorLanguage.CPP,
            '.cc': EditorLanguage.CPP,
            '.java': EditorLanguage.JAVA,
            '.go': EditorLanguage.GO,
            '.rs': EditorLanguage.RUST,
        }
        
        path = Path(filename)
        extension = path.suffix.lower()
        
        return ext_map.get(extension, EditorLanguage.PLAIN)


class EditorRenderer:
    """Renders editor content with line numbers and highlighting."""
    
    def __init__(
        self,
        show_line_numbers: bool = True,
        tab_size: int = 4,
        theme_variant: str = "professional_blue"
    ):
        """
        Initialize editor renderer.
        
        Args:
            show_line_numbers: Whether to show line numbers
            tab_size: Number of spaces per tab
            theme_variant: Theme for styling
        """
        self.show_line_numbers = show_line_numbers
        self.tab_size = tab_size
        self.theme_variant = theme_variant
        
        # Get theme and style
        self.theme = TUIEngineThemes.get_theme(theme_variant)
        self.style = QuestionaryStyleAdapter.convert_style(self.theme)
    
    def render_content(
        self,
        lines: List[str],
        current_line: int = 0,
        selection: Optional[EditorSelection] = None,
        search_matches: List[Tuple[int, int, int]] = None
    ) -> str:
        """
        Render editor content with line numbers and highlighting.
        
        Args:
            lines: Text lines
            current_line: Current cursor line
            selection: Current selection
            search_matches: Search match positions (line, start, end)
            
        Returns:
            Rendered content
        """
        if not lines:
            lines = [""]
        
        result = []
        max_line_num = len(lines)
        line_num_width = len(str(max_line_num))
        
        for i, line in enumerate(lines):
            # Convert tabs to spaces
            display_line = line.expandtabs(self.tab_size)
            
            # Line number
            if self.show_line_numbers:
                line_num = str(i + 1).rjust(line_num_width)
                if i == current_line:
                    line_prefix = f"\033[36m{line_num}\033[0m │ "  # Cyan for current line
                else:
                    line_prefix = f"\033[90m{line_num}\033[0m │ "  # Gray for other lines
            else:
                line_prefix = ""
            
            # Highlight current line
            if i == current_line:
                if display_line.strip():
                    line_content = f"\033[100m{display_line}\033[0m"  # Dark gray background
                else:
                    line_content = f"\033[100m \033[0m"  # Show empty line
            else:
                line_content = display_line
            
            # Apply search highlighting
            if search_matches:
                for match_line, start, end in search_matches:
                    if match_line == i:
                        # Highlight search match
                        before = line_content[:start]
                        match = line_content[start:end]
                        after = line_content[end:]
                        line_content = f"{before}\033[43m\033[30m{match}\033[0m{after}"  # Yellow background
            
            result.append(f"{line_prefix}{line_content}")
        
        return "\n".join(result)
    
    def render_status_line(
        self,
        filename: str,
        position: EditorPosition,
        mode: EditorMode,
        modified: bool = False,
        language: EditorLanguage = EditorLanguage.PLAIN
    ) -> str:
        """
        Render status line with file info.
        
        Args:
            filename: Current filename
            position: Cursor position
            mode: Editor mode
            modified: Whether file is modified
            language: Current language
            
        Returns:
            Status line string
        """
        # File info
        file_info = filename or "[No Name]"
        if modified:
            file_info += " [+]"
        
        # Position info
        pos_info = f"{position}"
        
        # Mode info
        mode_info = mode.value.upper()
        
        # Language info
        lang_info = language.value.upper()
        
        # Create status line
        left_side = f" {file_info} │ {lang_info} │ {mode_info}"
        right_side = f"{pos_info} "
        
        # Calculate padding
        terminal_width = 80  # Default width
        try:
            import shutil
            terminal_width = shutil.get_terminal_size().columns
        except Exception:
            pass
        
        padding = terminal_width - len(left_side) - len(right_side)
        if padding < 0:
            padding = 0
        
        status_line = f"\033[44m\033[37m{left_side}{' ' * padding}{right_side}\033[0m"  # Blue background
        return status_line


class EnhancedEditorAdapter:
    """
    Enhanced text editor with comprehensive editing features.
    
    Features:
    - Multi-line text editing with full cursor control
    - Syntax highlighting for multiple languages
    - Line numbers with current line highlighting
    - Search and replace with regex support
    - Undo/redo operations
    - Multiple editing modes
    - Professional styling with themes
    - File operations (load/save)
    """
    
    def __init__(
        self,
        content: str = "",
        filename: str = "",
        language: Optional[EditorLanguage] = None,
        mode: EditorMode = EditorMode.INSERT,
        show_line_numbers: bool = True,
        tab_size: int = 4,
        auto_indent: bool = True,
        theme_variant: str = "professional_blue",
        **kwargs
    ):
        """
        Initialize the enhanced editor.
        
        Args:
            content: Initial content
            filename: File name (used for language detection)
            language: Programming language for syntax highlighting
            mode: Initial editing mode
            show_line_numbers: Whether to show line numbers
            tab_size: Number of spaces per tab
            auto_indent: Whether to auto-indent new lines
            theme_variant: Theme for styling
            **kwargs: Additional arguments
        """
        self.content = content
        self.filename = filename
        self.mode = mode
        self.show_line_numbers = show_line_numbers
        self.tab_size = tab_size
        self.auto_indent = auto_indent
        self.theme_variant = theme_variant
        
        # Detect language if not specified
        if language is None:
            self.language = SyntaxHighlighter.detect_language(filename, content)
        else:
            self.language = language
        
        # Initialize components
        self.highlighter = SyntaxHighlighter(self.language)
        self.renderer = EditorRenderer(show_line_numbers, tab_size, theme_variant)
        self.history = EditorHistory()
        
        # Editor state
        self.lines = content.split('\n') if content else ['']
        self.position = EditorPosition(0, 0)
        self.selection: Optional[EditorSelection] = None
        self.search_matches: List[Tuple[int, int, int]] = []
        self.modified = False
        
        # Create text area for prompt-toolkit
        self.text_area = TextArea(
            text=content,
            multiline=True,
            wrap_lines=False,
            read_only=(mode == EditorMode.READONLY),
            lexer=PygmentsLexer(self.highlighter.lexer.__class__) if self.highlighter.lexer else None
        )
        
        # Set up key bindings
        self.bindings = self._create_key_bindings()
    
    def _create_key_bindings(self) -> KeyBindings:
        """Create key bindings for the editor."""
        bindings = KeyBindings()
        
        # Save file
        @bindings.add('c-s')
        def save_file(event):
            self.save_to_file()
        
        # Search
        @bindings.add('c-f')
        def search(event):
            self.show_search_dialog()
        
        # Replace
        @bindings.add('c-h')
        def replace(event):
            self.show_replace_dialog()
        
        # Undo
        @bindings.add('c-z')
        def undo(event):
            self.undo()
        
        # Redo
        @bindings.add('c-y')
        def redo(event):
            self.redo()
        
        # Go to line
        @bindings.add('c-g')
        def go_to_line(event):
            self.show_goto_dialog()
        
        return bindings
    
    def edit_text(self) -> Optional[str]:
        """
        Start interactive text editing.
        
        Returns:
            Edited text or None if cancelled
        """
        try:
            # Create application layout
            layout = Layout(
                HSplit([
                    Frame(
                        body=self.text_area,
                        title=self.filename or "Text Editor"
                    ),
                    Window(
                        content=FormattedTextControl(
                            text=lambda: self._get_status_text()
                        ),
                        height=1
                    )
                ])
            )
            
            # Create application
            app = Application(
                layout=layout,
                key_bindings=self.bindings,
                full_screen=True,
                mouse_support=True
            )
            
            # Run the application
            app.run()
            
            # Get final content
            result = self.text_area.text
            self.content = result
            self.lines = result.split('\n')
            
            return result
            
        except KeyboardInterrupt:
            return None
    
    def _get_status_text(self) -> FormattedText:
        """Get status line text."""
        doc = self.text_area.document
        line = doc.cursor_position_row + 1
        col = doc.cursor_position_col + 1
        
        status_parts = [
            ('class:status', f' {self.filename or "[No Name]"}'),
            ('class:status', f' │ {self.language.value.upper()}'),
            ('class:status', f' │ {self.mode.value.upper()}'),
            ('class:status', f' │ Line {line}, Col {col}'),
        ]
        
        if self.modified:
            status_parts.insert(1, ('class:status.modified', ' [+]'))
        
        return status_parts
    
    def search_text(self, pattern: str, options: SearchOptions) -> List[Tuple[int, int, int]]:
        """
        Search for text in the editor.
        
        Args:
            pattern: Search pattern
            options: Search options
            
        Returns:
            List of matches (line, start, end)
        """
        matches = []
        
        # Prepare search pattern
        if options.regex:
            try:
                if options.case_sensitive:
                    regex = re.compile(pattern)
                else:
                    regex = re.compile(pattern, re.IGNORECASE)
            except re.error:
                return matches  # Invalid regex
        else:
            # Escape special characters for literal search
            escaped_pattern = re.escape(pattern)
            if options.whole_word:
                escaped_pattern = r'\b' + escaped_pattern + r'\b'
            
            if options.case_sensitive:
                regex = re.compile(escaped_pattern)
            else:
                regex = re.compile(escaped_pattern, re.IGNORECASE)
        
        # Search through lines
        for line_idx, line in enumerate(self.lines):
            for match in regex.finditer(line):
                matches.append((line_idx, match.start(), match.end()))
        
        self.search_matches = matches
        return matches
    
    def replace_text(
        self,
        pattern: str,
        replacement: str,
        options: SearchOptions
    ) -> int:
        """
        Replace text in the editor.
        
        Args:
            pattern: Search pattern
            replacement: Replacement text
            options: Search options
            
        Returns:
            Number of replacements made
        """
        matches = self.search_text(pattern, options)
        if not matches:
            return 0
        
        replacements = 0
        
        if options.replace_all:
            # Replace all matches
            for line_idx, start, end in reversed(matches):  # Reverse to maintain indices
                line = self.lines[line_idx]
                new_line = line[:start] + replacement + line[end:]
                self.lines[line_idx] = new_line
                replacements += 1
        else:
            # Replace only first match
            if matches:
                line_idx, start, end = matches[0]
                line = self.lines[line_idx]
                new_line = line[:start] + replacement + line[end:]
                self.lines[line_idx] = new_line
                replacements = 1
        
        if replacements > 0:
            self.content = '\n'.join(self.lines)
            self.modified = True
            self.history.add_operation("replace", self.content)
        
        return replacements
    
    def show_search_dialog(self):
        """Show search dialog."""
        try:
            search_term = questionary.text(
                "Search for:",
                style=self.renderer.style
            ).ask()
            
            if search_term:
                case_sensitive = questionary.confirm(
                    "Case sensitive?",
                    default=False,
                    style=self.renderer.style
                ).ask()
                
                use_regex = questionary.confirm(
                    "Use regular expressions?",
                    default=False,
                    style=self.renderer.style
                ).ask()
                
                options = SearchOptions(
                    case_sensitive=case_sensitive,
                    regex=use_regex,
                    highlight_all=True
                )
                
                matches = self.search_text(search_term, options)
                print(f"Found {len(matches)} matches")
                
        except KeyboardInterrupt:
            pass
    
    def show_replace_dialog(self):
        """Show replace dialog."""
        try:
            search_term = questionary.text(
                "Search for:",
                style=self.renderer.style
            ).ask()
            
            if not search_term:
                return
            
            replacement = questionary.text(
                "Replace with:",
                style=self.renderer.style
            ).ask()
            
            if replacement is None:
                return
            
            replace_all = questionary.confirm(
                "Replace all occurrences?",
                default=False,
                style=self.renderer.style
            ).ask()
            
            options = SearchOptions(
                case_sensitive=False,
                regex=False,
                replace_all=replace_all
            )
            
            count = self.replace_text(search_term, replacement, options)
            print(f"Replaced {count} occurrences")
            
        except KeyboardInterrupt:
            pass
    
    def show_goto_dialog(self):
        """Show go to line dialog."""
        try:
            line_input = questionary.text(
                f"Go to line (1-{len(self.lines)}):",
                validate=lambda x: x.isdigit() and 1 <= int(x) <= len(self.lines),
                style=self.renderer.style
            ).ask()
            
            if line_input:
                line_num = int(line_input) - 1  # Convert to 0-based
                self.position.line = line_num
                self.position.column = 0
                
                # Update text area cursor
                if hasattr(self.text_area, 'buffer'):
                    self.text_area.buffer.cursor_position = \
                        self.text_area.buffer.document.translate_row_col_to_index(line_num, 0)
                
        except KeyboardInterrupt:
            pass
    
    def undo(self) -> bool:
        """Undo the last operation."""
        operation = self.history.undo()
        if operation:
            action, content = operation
            self.content = content
            self.lines = content.split('\n')
            self.text_area.text = content
            return True
        return False
    
    def redo(self) -> bool:
        """Redo the next operation."""
        operation = self.history.redo()
        if operation:
            action, content = operation
            self.content = content
            self.lines = content.split('\n')
            self.text_area.text = content
            return True
        return False
    
    def load_from_file(self, filename: str) -> bool:
        """
        Load content from a file.
        
        Args:
            filename: File to load
            
        Returns:
            True if successful
        """
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.content = content
            self.lines = content.split('\n')
            self.filename = filename
            self.language = SyntaxHighlighter.detect_language(filename, content)
            self.highlighter = SyntaxHighlighter(self.language)
            self.modified = False
            self.history = EditorHistory()  # Reset history
            
            return True
            
        except Exception as e:
            print(f"Error loading file: {e}")
            return False
    
    def save_to_file(self, filename: Optional[str] = None) -> bool:
        """
        Save content to a file.
        
        Args:
            filename: File to save to (uses current filename if None)
            
        Returns:
            True if successful
        """
        target_file = filename or self.filename
        if not target_file:
            return False
        
        try:
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(self.content)
            
            self.filename = target_file
            self.modified = False
            self.history.mark_saved()
            
            return True
            
        except Exception as e:
            print(f"Error saving file: {e}")
            return False
    
    def get_content(self) -> str:
        """Get current editor content."""
        return self.content
    
    def set_content(self, content: str):
        """Set editor content."""
        self.content = content
        self.lines = content.split('\n')
        self.text_area.text = content
        self.modified = True
        self.history.add_operation("set_content", content)
    
    def get_selection(self) -> Optional[str]:
        """Get selected text."""
        if hasattr(self.text_area, 'buffer') and self.text_area.buffer.selection_state:
            return self.text_area.buffer.copy_selection()
        return None
    
    def insert_text(self, text: str):
        """Insert text at current position."""
        if hasattr(self.text_area, 'buffer'):
            self.text_area.buffer.insert_text(text)
            self.content = self.text_area.text
            self.lines = self.content.split('\n')
            self.modified = True
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get editor statistics."""
        lines = len(self.lines)
        chars = len(self.content)
        words = len(self.content.split())
        
        # Count non-empty lines
        non_empty_lines = sum(1 for line in self.lines if line.strip())
        
        return {
            'lines': lines,
            'non_empty_lines': non_empty_lines,
            'characters': chars,
            'characters_no_spaces': len(self.content.replace(' ', '')),
            'words': words,
            'language': self.language.value,
            'mode': self.mode.value,
            'modified': self.modified,
            'filename': self.filename
        }


class EditorAdapter:
    """
    Backward-compatible Editor adapter for TUI Engine.
    
    This adapter provides compatibility with existing TUI Engine code while
    offering enhanced functionality through the EnhancedEditorAdapter.
    
    For new code, consider using EnhancedEditorAdapter directly for
    access to all features and better type safety.
    """
    
    def __init__(
        self,
        widget: Optional[Any] = None,
        enhanced: bool = True,
        **kwargs
    ):
        """
        Initialize Editor adapter.
        
        Args:
            widget: Original TUI Engine widget (for compatibility)
            enhanced: Whether to use enhanced features
            **kwargs: Additional arguments passed to enhanced adapter
        """
        self.widget = widget
        self.enhanced = enhanced
        
        if self.enhanced:
            # Use enhanced adapter
            self.adapter = EnhancedEditorAdapter(**kwargs)
        else:
            # Basic implementation for legacy compatibility
            self.content = kwargs.get('content', '')
            self.filename = kwargs.get('filename', '')
    
    def edit(self) -> Optional[str]:
        """
        Edit text and return result.
        
        Returns:
            Edited text or None if cancelled
        """
        if self.enhanced:
            return self.adapter.edit_text()
        else:
            # Basic text input
            try:
                result = questionary.text(
                    "Enter text:",
                    default=self.content,
                    multiline=True
                ).ask()
                
                if result is not None:
                    self.content = result
                
                return result
                
            except KeyboardInterrupt:
                return None
    
    def get_content(self) -> str:
        """Get current content."""
        if self.enhanced:
            return self.adapter.get_content()
        else:
            return self.content
    
    def set_content(self, content: str):
        """Set content."""
        if self.enhanced:
            self.adapter.set_content(content)
        else:
            self.content = content
    
    def load_file(self, filename: str) -> bool:
        """Load content from file."""
        if self.enhanced:
            return self.adapter.load_from_file(filename)
        else:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    self.content = f.read()
                    self.filename = filename
                return True
            except Exception:
                return False
    
    def save_file(self, filename: Optional[str] = None) -> bool:
        """Save content to file."""
        if self.enhanced:
            return self.adapter.save_to_file(filename)
        else:
            target_file = filename or self.filename
            if not target_file:
                return False
            try:
                with open(target_file, 'w', encoding='utf-8') as f:
                    f.write(self.content)
                return True
            except Exception:
                return False
    
    def __repr__(self) -> str:
        """String representation."""
        if self.enhanced:
            return f"<EditorAdapter enhanced=True adapter={self.adapter}>"
        else:
            return f"<EditorAdapter enhanced=False widget={self.widget}>"


# Convenience functions for common editor scenarios
def edit_text(
    content: str = "",
    filename: str = "",
    language: Optional[EditorLanguage] = None,
    theme_variant: str = "professional_blue"
) -> Optional[str]:
    """
    Quick text editing function.
    
    Args:
        content: Initial content
        filename: File name
        language: Programming language
        theme_variant: Theme to use
        
    Returns:
        Edited text or None if cancelled
    """
    editor = EnhancedEditorAdapter(
        content=content,
        filename=filename,
        language=language,
        theme_variant=theme_variant
    )
    
    return editor.edit_text()


def edit_file(
    filename: str,
    theme_variant: str = "professional_blue"
) -> Optional[str]:
    """
    Edit a file directly.
    
    Args:
        filename: File to edit
        theme_variant: Theme to use
        
    Returns:
        Edited content or None if cancelled
    """
    editor = EnhancedEditorAdapter(theme_variant=theme_variant)
    
    if editor.load_from_file(filename):
        result = editor.edit_text()
        if result is not None:
            editor.save_to_file()
        return result
    
    return None


def create_new_file(
    filename: str,
    template: str = "",
    theme_variant: str = "professional_blue"
) -> Optional[str]:
    """
    Create and edit a new file.
    
    Args:
        filename: New file name
        template: Initial template content
        theme_variant: Theme to use
        
    Returns:
        Created content or None if cancelled
    """
    editor = EnhancedEditorAdapter(
        content=template,
        filename=filename,
        theme_variant=theme_variant
    )
    
    result = editor.edit_text()
    if result is not None:
        editor.save_to_file()
    
    return result


# Export all public classes and functions
__all__ = [
    'EditorMode',
    'EditorLanguage',
    'SearchOptions',
    'EditorPosition',
    'EditorSelection',
    'EditorHistory',
    'SyntaxHighlighter',
    'EditorRenderer',
    'EnhancedEditorAdapter',
    'EditorAdapter',
    'edit_text',
    'edit_file',
    'create_new_file'
]