"""Enhanced Progress Indicator Adapter for TUI Engine with Questionary Integration.

This module provides sophisticated progress tracking widgets that support various
display modes, step tracking, ETA calculation, and professional styling integration.

Key Features:
- Multiple display modes (bar, percentage, spinner, steps)
- ETA calculation and time tracking
- Step-based progress with custom labels
- Customizable progress bars with themes
- Real-time updates and animation
- Professional styling with TUI Engine themes
- Task completion callbacks
- Progress history and statistics
- Backward compatibility with legacy widgets

Author: TUI Engine Team
License: MIT
"""

import time
import threading
from typing import Any, Optional, Union, Callable, Dict, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

try:
    import questionary
    from prompt_toolkit.shortcuts import prompt
    from prompt_toolkit.formatted_text import HTML
    from prompt_toolkit.application import get_app
    QUESTIONARY_AVAILABLE = True
except ImportError:
    QUESTIONARY_AVAILABLE = False


class ProgressMode(Enum):
    """Progress display modes."""
    BAR = "bar"                    # Classic progress bar
    PERCENTAGE = "percentage"      # Percentage display
    SPINNER = "spinner"           # Animated spinner
    STEPS = "steps"               # Step-based progress
    DETAILED = "detailed"         # Combined bar + percentage + ETA
    MINIMAL = "minimal"           # Minimal text display


class ProgressState(Enum):
    """Progress states."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ERROR = "error"


@dataclass
class ProgressStep:
    """Individual progress step configuration."""
    
    # Step identification
    id: str
    label: str
    description: Optional[str] = None
    
    # Progress tracking
    weight: float = 1.0  # Relative weight of this step
    completed: bool = False
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    # Status and metadata
    status: str = "pending"  # pending, active, completed, error
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def start(self):
        """Mark step as started."""
        self.status = "active"
        self.start_time = datetime.now()
    
    def complete(self):
        """Mark step as completed."""
        self.status = "completed"
        self.completed = True
        self.end_time = datetime.now()
    
    def fail(self, error_message: str = ""):
        """Mark step as failed."""
        self.status = "error"
        self.error_message = error_message
        self.end_time = datetime.now()
    
    def get_duration(self) -> Optional[timedelta]:
        """Get step duration if completed."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None


@dataclass
class ProgressConfig:
    """Configuration for progress display and behavior."""
    
    # Display configuration
    mode: ProgressMode = ProgressMode.BAR
    bar_width: int = 40
    bar_fill_char: str = "█"
    bar_empty_char: str = "░"
    show_percentage: bool = True
    show_eta: bool = True
    show_rate: bool = False
    
    # Animation configuration
    spinner_chars: List[str] = field(default_factory=lambda: ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"])
    animation_delay: float = 0.1
    
    # Progress calculation
    auto_eta: bool = True
    smooth_eta: bool = True
    eta_window_size: int = 10
    
    # Formatting
    percentage_precision: int = 1
    rate_unit: str = "items/sec"
    time_format: str = "auto"  # auto, seconds, minutes, hours
    
    # Colors and styling
    completed_color: str = "green"
    remaining_color: str = "dark_gray"
    text_color: str = "white"
    error_color: str = "red"
    
    # Behavior
    auto_refresh: bool = True
    refresh_rate: float = 0.5  # seconds
    hide_on_complete: bool = False


class ProgressCalculator:
    """Utility class for progress calculations and ETA estimation."""
    
    def __init__(self, config: ProgressConfig):
        """Initialize progress calculator.
        
        Args:
            config: Progress configuration
        """
        self.config = config
        self.start_time = None
        self.progress_history = []
        self.eta_samples = []
    
    def start_tracking(self):
        """Start progress tracking."""
        self.start_time = datetime.now()
        self.progress_history = []
        self.eta_samples = []
    
    def update_progress(self, current: Union[int, float], total: Union[int, float]):
        """Update progress tracking.
        
        Args:
            current: Current progress value
            total: Total progress value
        """
        now = datetime.now()
        progress_ratio = current / total if total > 0 else 0
        
        self.progress_history.append({
            'time': now,
            'current': current,
            'total': total,
            'ratio': progress_ratio
        })
        
        # Limit history size
        if len(self.progress_history) > 1000:
            self.progress_history = self.progress_history[-500:]
    
    def calculate_eta(self, current: Union[int, float], total: Union[int, float]) -> Optional[timedelta]:
        """Calculate estimated time to completion.
        
        Args:
            current: Current progress value
            total: Total progress value
            
        Returns:
            Estimated time to completion or None if cannot calculate
        """
        if not self.config.auto_eta or not self.start_time or current <= 0:
            return None
        
        now = datetime.now()
        elapsed = now - self.start_time
        progress_ratio = current / total if total > 0 else 0
        
        if progress_ratio <= 0:
            return None
        
        if self.config.smooth_eta and len(self.progress_history) >= 2:
            # Use recent progress rate for smoother ETA
            recent_samples = self.progress_history[-self.config.eta_window_size:]
            if len(recent_samples) >= 2:
                time_diff = (recent_samples[-1]['time'] - recent_samples[0]['time']).total_seconds()
                progress_diff = recent_samples[-1]['ratio'] - recent_samples[0]['ratio']
                
                if time_diff > 0 and progress_diff > 0:
                    rate = progress_diff / time_diff
                    remaining_progress = 1.0 - progress_ratio
                    eta_seconds = remaining_progress / rate
                    return timedelta(seconds=eta_seconds)
        
        # Fallback to simple linear projection
        total_estimated = elapsed.total_seconds() / progress_ratio
        remaining_seconds = total_estimated - elapsed.total_seconds()
        
        if remaining_seconds > 0:
            return timedelta(seconds=remaining_seconds)
        
        return None
    
    def calculate_rate(self, current: Union[int, float]) -> Optional[float]:
        """Calculate current processing rate.
        
        Args:
            current: Current progress value
            
        Returns:
            Rate in items per second or None if cannot calculate
        """
        if not self.start_time:
            return None
        
        elapsed = (datetime.now() - self.start_time).total_seconds()
        if elapsed > 0:
            return current / elapsed
        
        return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive progress statistics.
        
        Returns:
            Dictionary containing progress statistics
        """
        if not self.start_time:
            return {}
        
        now = datetime.now()
        elapsed = now - self.start_time
        
        stats = {
            'start_time': self.start_time,
            'current_time': now,
            'elapsed': elapsed,
            'total_samples': len(self.progress_history)
        }
        
        if self.progress_history:
            latest = self.progress_history[-1]
            stats.update({
                'current_progress': latest['current'],
                'total_progress': latest['total'],
                'progress_ratio': latest['ratio'],
                'rate': self.calculate_rate(latest['current'])
            })
        
        return stats


class ProgressRenderer:
    """Handles rendering of progress displays in different modes."""
    
    def __init__(self, config: ProgressConfig):
        """Initialize progress renderer.
        
        Args:
            config: Progress configuration
        """
        self.config = config
        self.spinner_index = 0
        
    def render_bar(self, progress_ratio: float) -> str:
        """Render progress bar.
        
        Args:
            progress_ratio: Progress ratio (0.0 to 1.0)
            
        Returns:
            Rendered progress bar string
        """
        filled_width = int(progress_ratio * self.config.bar_width)
        empty_width = self.config.bar_width - filled_width
        
        filled_bar = self.config.bar_fill_char * filled_width
        empty_bar = self.config.bar_empty_char * empty_width
        
        return f"[{filled_bar}{empty_bar}]"
    
    def render_percentage(self, progress_ratio: float) -> str:
        """Render percentage display.
        
        Args:
            progress_ratio: Progress ratio (0.0 to 1.0)
            
        Returns:
            Rendered percentage string
        """
        percentage = progress_ratio * 100
        precision = self.config.percentage_precision
        return f"{percentage:.{precision}f}%"
    
    def render_spinner(self) -> str:
        """Render animated spinner.
        
        Returns:
            Current spinner character
        """
        char = self.config.spinner_chars[self.spinner_index]
        self.spinner_index = (self.spinner_index + 1) % len(self.config.spinner_chars)
        return char
    
    def render_eta(self, eta: Optional[timedelta]) -> str:
        """Render ETA display.
        
        Args:
            eta: Estimated time to completion
            
        Returns:
            Rendered ETA string
        """
        if eta is None:
            return "ETA: --:--"
        
        total_seconds = int(eta.total_seconds())
        
        if self.config.time_format == "auto":
            if total_seconds < 60:
                return f"ETA: {total_seconds}s"
            elif total_seconds < 3600:
                minutes = total_seconds // 60
                seconds = total_seconds % 60
                return f"ETA: {minutes}m {seconds}s"
            else:
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                return f"ETA: {hours}h {minutes}m"
        elif self.config.time_format == "seconds":
            return f"ETA: {total_seconds}s"
        elif self.config.time_format == "minutes":
            minutes = total_seconds / 60
            return f"ETA: {minutes:.1f}m"
        elif self.config.time_format == "hours":
            hours = total_seconds / 3600
            return f"ETA: {hours:.2f}h"
        
        return f"ETA: {total_seconds}s"
    
    def render_rate(self, rate: Optional[float]) -> str:
        """Render processing rate display.
        
        Args:
            rate: Processing rate
            
        Returns:
            Rendered rate string
        """
        if rate is None:
            return f"Rate: -- {self.config.rate_unit}"
        
        if rate < 0.01:
            return f"Rate: {rate:.3f} {self.config.rate_unit}"
        elif rate < 1:
            return f"Rate: {rate:.2f} {self.config.rate_unit}"
        elif rate < 100:
            return f"Rate: {rate:.1f} {self.config.rate_unit}"
        else:
            return f"Rate: {rate:.0f} {self.config.rate_unit}"
    
    def render_steps(self, steps: List[ProgressStep], current_step: int) -> str:
        """Render step-based progress.
        
        Args:
            steps: List of progress steps
            current_step: Current step index
            
        Returns:
            Rendered steps string
        """
        if not steps:
            return "No steps defined"
        
        lines = []
        for i, step in enumerate(steps):
            if i < current_step:
                status = "✓"
                style = self.config.completed_color
            elif i == current_step:
                status = "►"
                style = self.config.text_color
            else:
                status = "○"
                style = self.config.remaining_color
            
            line = f"{status} {step.label}"
            if step.description and i == current_step:
                line += f" - {step.description}"
            
            lines.append(line)
        
        return "\n".join(lines)
    
    def render_complete(self, mode: ProgressMode, **kwargs) -> str:
        """Render complete progress display.
        
        Args:
            mode: Progress display mode
            **kwargs: Additional rendering parameters
            
        Returns:
            Complete rendered progress string
        """
        if mode == ProgressMode.BAR:
            progress_ratio = kwargs.get('progress_ratio', 0.0)
            bar = self.render_bar(progress_ratio)
            
            parts = [bar]
            
            if self.config.show_percentage:
                parts.append(self.render_percentage(progress_ratio))
            
            if self.config.show_eta and 'eta' in kwargs:
                parts.append(self.render_eta(kwargs['eta']))
            
            if self.config.show_rate and 'rate' in kwargs:
                parts.append(self.render_rate(kwargs['rate']))
            
            return " ".join(parts)
        
        elif mode == ProgressMode.PERCENTAGE:
            progress_ratio = kwargs.get('progress_ratio', 0.0)
            return self.render_percentage(progress_ratio)
        
        elif mode == ProgressMode.SPINNER:
            spinner = self.render_spinner()
            message = kwargs.get('message', 'Processing...')
            return f"{spinner} {message}"
        
        elif mode == ProgressMode.STEPS:
            steps = kwargs.get('steps', [])
            current_step = kwargs.get('current_step', 0)
            return self.render_steps(steps, current_step)
        
        elif mode == ProgressMode.DETAILED:
            progress_ratio = kwargs.get('progress_ratio', 0.0)
            bar = self.render_bar(progress_ratio)
            percentage = self.render_percentage(progress_ratio)
            
            parts = [bar, percentage]
            
            if 'eta' in kwargs:
                parts.append(self.render_eta(kwargs['eta']))
            
            if 'rate' in kwargs:
                parts.append(self.render_rate(kwargs['rate']))
            
            current = kwargs.get('current', 0)
            total = kwargs.get('total', 100)
            parts.append(f"({current}/{total})")
            
            return " ".join(parts)
        
        elif mode == ProgressMode.MINIMAL:
            progress_ratio = kwargs.get('progress_ratio', 0.0)
            percentage = self.render_percentage(progress_ratio)
            message = kwargs.get('message', '')
            
            if message:
                return f"{percentage} - {message}"
            else:
                return percentage
        
        return "Unknown mode"


class EnhancedProgressAdapter:
    """Enhanced progress adapter with professional styling and advanced features."""
    
    def __init__(self,
                 message: str = "Progress:",
                 total: Union[int, float] = 100,
                 mode: Union[str, ProgressMode] = ProgressMode.BAR,
                 style: str = 'professional_blue',
                 show_percentage: bool = True,
                 show_eta: bool = True,
                 show_rate: bool = False,
                 auto_refresh: bool = True,
                 steps: Optional[List[Dict[str, Any]]] = None,
                 completion_callback: Optional[Callable] = None):
        """Initialize enhanced progress adapter.
        
        Args:
            message: Progress message to display
            total: Total progress value
            mode: Progress display mode
            style: Theme style to use
            show_percentage: Whether to show percentage
            show_eta: Whether to show ETA
            show_rate: Whether to show processing rate
            auto_refresh: Whether to auto-refresh display
            steps: List of progress steps
            completion_callback: Callback when progress completes
        """
        if not QUESTIONARY_AVAILABLE:
            raise ImportError("Questionary is required for EnhancedProgressAdapter. Install with: pip install questionary")
        
        self.message = message
        self.total = total
        self.current = 0
        self.style = style
        self.completion_callback = completion_callback
        
        # Convert mode to enum if string
        if isinstance(mode, str):
            self.mode = ProgressMode(mode)
        else:
            self.mode = mode
        
        # Create configuration
        self.config = ProgressConfig(
            mode=self.mode,
            show_percentage=show_percentage,
            show_eta=show_eta,
            show_rate=show_rate,
            auto_refresh=auto_refresh
        )
        
        # Initialize components
        self.calculator = ProgressCalculator(self.config)
        self.renderer = ProgressRenderer(self.config)
        
        # Progress state
        self.state = ProgressState.NOT_STARTED
        self.start_time = None
        self.end_time = None
        
        # Steps management
        self.steps = []
        self.current_step = 0
        if steps:
            self.setup_steps(steps)
        
        # Threading for auto-refresh
        self._refresh_thread = None
        self._stop_refresh = False
        
        # Load TUI Engine themes
        self._load_themes()
    
    def _load_themes(self):
        """Load TUI Engine themes for styling."""
        try:
            from tui_engine.questionary_adapter import QuestionaryStyleAdapter
            
            # Create style adapter with theme name
            self.style_adapter = QuestionaryStyleAdapter(self.style)
            self._themes_available = True
        except ImportError:
            self._themes_available = False
    
    def setup_steps(self, steps_data: List[Dict[str, Any]]):
        """Setup progress steps.
        
        Args:
            steps_data: List of step dictionaries
        """
        self.steps = []
        for i, step_data in enumerate(steps_data):
            step = ProgressStep(
                id=step_data.get('id', f'step_{i}'),
                label=step_data.get('label', f'Step {i+1}'),
                description=step_data.get('description'),
                weight=step_data.get('weight', 1.0)
            )
            self.steps.append(step)
        
        self.current_step = 0
        
        # Adjust mode for steps
        if self.steps and self.mode == ProgressMode.BAR:
            self.mode = ProgressMode.STEPS
            self.config.mode = ProgressMode.STEPS
    
    def start(self):
        """Start progress tracking."""
        self.state = ProgressState.IN_PROGRESS
        self.start_time = datetime.now()
        self.calculator.start_tracking()
        
        if self.steps:
            self.steps[0].start()
        
        if self.config.auto_refresh:
            self._start_refresh_thread()
    
    def update(self, current: Optional[Union[int, float]] = None, message: Optional[str] = None):
        """Update progress.
        
        Args:
            current: New current progress value
            message: Updated message
        """
        if current is not None:
            self.current = min(current, self.total)
            self.calculator.update_progress(self.current, self.total)
        
        if message is not None:
            self.message = message
        
        # Check if completed
        if self.current >= self.total:
            self.complete()
    
    def increment(self, amount: Union[int, float] = 1, message: Optional[str] = None):
        """Increment progress by amount.
        
        Args:
            amount: Amount to increment
            message: Updated message
        """
        self.update(self.current + amount, message)
    
    def next_step(self, message: Optional[str] = None):
        """Move to next step.
        
        Args:
            message: Message for the new step
        """
        if not self.steps:
            return
        
        # Complete current step
        if self.current_step < len(self.steps):
            self.steps[self.current_step].complete()
        
        # Move to next step
        self.current_step += 1
        
        if self.current_step < len(self.steps):
            self.steps[self.current_step].start()
            if message:
                self.steps[self.current_step].description = message
        else:
            # All steps completed
            self.complete()
    
    def fail_current_step(self, error_message: str = ""):
        """Mark current step as failed.
        
        Args:
            error_message: Error message
        """
        if self.steps and self.current_step < len(self.steps):
            self.steps[self.current_step].fail(error_message)
            self.state = ProgressState.ERROR
    
    def pause(self):
        """Pause progress tracking."""
        self.state = ProgressState.PAUSED
        self._stop_refresh = True
    
    def resume(self):
        """Resume progress tracking."""
        if self.state == ProgressState.PAUSED:
            self.state = ProgressState.IN_PROGRESS
            if self.config.auto_refresh:
                self._start_refresh_thread()
    
    def complete(self):
        """Mark progress as completed."""
        self.state = ProgressState.COMPLETED
        self.end_time = datetime.now()
        self.current = self.total
        self._stop_refresh = True
        
        # Complete any remaining steps
        for i in range(self.current_step, len(self.steps)):
            if not self.steps[i].completed:
                self.steps[i].complete()
        
        if self.completion_callback:
            try:
                self.completion_callback(self)
            except Exception:
                pass  # Don't let callback errors affect progress
    
    def cancel(self):
        """Cancel progress tracking."""
        self.state = ProgressState.CANCELLED
        self._stop_refresh = True
    
    def get_progress_ratio(self) -> float:
        """Get progress ratio (0.0 to 1.0).
        
        Returns:
            Progress ratio
        """
        if self.total <= 0:
            return 0.0
        return min(self.current / self.total, 1.0)
    
    def get_eta(self) -> Optional[timedelta]:
        """Get estimated time to completion.
        
        Returns:
            ETA or None if cannot calculate
        """
        return self.calculator.calculate_eta(self.current, self.total)
    
    def get_rate(self) -> Optional[float]:
        """Get processing rate.
        
        Returns:
            Rate or None if cannot calculate
        """
        return self.calculator.calculate_rate(self.current)
    
    def get_elapsed_time(self) -> Optional[timedelta]:
        """Get elapsed time since start.
        
        Returns:
            Elapsed time or None if not started
        """
        if self.start_time:
            end_time = self.end_time or datetime.now()
            return end_time - self.start_time
        return None
    
    def render(self) -> str:
        """Render current progress display.
        
        Returns:
            Rendered progress string
        """
        progress_ratio = self.get_progress_ratio()
        
        render_kwargs = {
            'progress_ratio': progress_ratio,
            'current': self.current,
            'total': self.total,
            'message': self.message
        }
        
        if self.config.show_eta:
            render_kwargs['eta'] = self.get_eta()
        
        if self.config.show_rate:
            render_kwargs['rate'] = self.get_rate()
        
        if self.mode == ProgressMode.STEPS:
            render_kwargs['steps'] = self.steps
            render_kwargs['current_step'] = self.current_step
        
        return self.renderer.render_complete(self.mode, **render_kwargs)
    
    def _start_refresh_thread(self):
        """Start auto-refresh thread."""
        if self._refresh_thread is not None:
            self._stop_refresh = True
            if self._refresh_thread.is_alive():
                self._refresh_thread.join()
        
        self._stop_refresh = False
        self._refresh_thread = threading.Thread(target=self._refresh_loop, daemon=True)
        self._refresh_thread.start()
    
    def _refresh_loop(self):
        """Auto-refresh loop."""
        while not self._stop_refresh and self.state == ProgressState.IN_PROGRESS:
            # In a real implementation, this would update the display
            # For now, we just track timing
            time.sleep(self.config.refresh_rate)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive progress statistics.
        
        Returns:
            Dictionary containing progress statistics
        """
        stats = self.calculator.get_statistics()
        
        stats.update({
            'state': self.state.value,
            'progress_ratio': self.get_progress_ratio(),
            'current': self.current,
            'total': self.total,
            'message': self.message,
            'mode': self.mode.value,
            'elapsed_time': self.get_elapsed_time(),
            'eta': self.get_eta(),
            'rate': self.get_rate()
        })
        
        if self.steps:
            stats['steps'] = {
                'total_steps': len(self.steps),
                'current_step': self.current_step,
                'completed_steps': sum(1 for step in self.steps if step.completed),
                'step_details': [
                    {
                        'id': step.id,
                        'label': step.label,
                        'status': step.status,
                        'duration': step.get_duration()
                    }
                    for step in self.steps
                ]
            }
        
        return stats
    
    def change_theme(self, new_style: str) -> bool:
        """Change the widget theme.
        
        Args:
            new_style: New theme style name
            
        Returns:
            True if theme was changed successfully
        """
        if self._themes_available:
            try:
                from tui_engine.questionary_adapter import QuestionaryStyleAdapter
                self.style_adapter = QuestionaryStyleAdapter(new_style)
                self.style = new_style
                return True
            except ImportError:
                return False
        return False
    
    def is_questionary_enhanced(self) -> bool:
        """Check if this adapter uses Questionary enhancements.
        
        Returns:
            True if using Questionary, False for legacy mode
        """
        return True
    
    def __str__(self) -> str:
        """String representation of the adapter."""
        return f"<EnhancedProgressAdapter state='{self.state.value}' progress='{self.get_progress_ratio():.1%}'>"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return self.__str__()


class ProgressAdapter:
    """Backward-compatible progress adapter that can work with or without Questionary.
    
    This adapter provides a unified interface that automatically chooses between
    enhanced Questionary-based functionality and legacy widget integration.
    """
    
    def __init__(self, widget=None, **kwargs):
        """Initialize progress adapter with automatic mode detection.
        
        Args:
            widget: If provided, uses legacy mode with existing widget
            **kwargs: Arguments passed to enhanced adapter or legacy configuration
        """
        self.widget = widget
        self._is_legacy = widget is not None
        
        if self._is_legacy:
            # Legacy mode - work with existing widget
            self._legacy_init(**kwargs)
        else:
            # Enhanced mode - use Questionary if available
            if QUESTIONARY_AVAILABLE:
                try:
                    self._enhanced_adapter = EnhancedProgressAdapter(**kwargs)
                    self._is_enhanced = True
                except Exception as e:
                    # Fall back to legacy if enhanced mode fails
                    self._is_enhanced = False
                    self._legacy_init(**kwargs)
            else:
                # No Questionary - use legacy mode
                self._is_enhanced = False
                self._legacy_init(**kwargs)
    
    def _legacy_init(self, **kwargs):
        """Initialize legacy mode configuration."""
        self.total = kwargs.get('total', 100)
        self.current = 0
        self.message = kwargs.get('message', 'Progress:')
        self.state = ProgressState.NOT_STARTED
        self.start_time = None
        self.end_time = None
        
        # Simple progress tracking for legacy mode
        self.progress_history = []
    
    def start(self):
        """Start progress tracking."""
        if hasattr(self, '_enhanced_adapter') and self._is_enhanced:
            self._enhanced_adapter.start()
        else:
            # Legacy start
            self.state = ProgressState.IN_PROGRESS
            self.start_time = datetime.now()
    
    def update(self, current: Optional[Union[int, float]] = None, message: Optional[str] = None):
        """Update progress."""
        if hasattr(self, '_enhanced_adapter') and self._is_enhanced:
            self._enhanced_adapter.update(current, message)
        else:
            # Legacy update
            if current is not None:
                self.current = min(current, self.total)
            if message is not None:
                self.message = message
            
            # Record progress
            self.progress_history.append({
                'time': datetime.now(),
                'current': self.current,
                'total': self.total
            })
            
            # Check completion
            if self.current >= self.total:
                self.complete()
    
    def increment(self, amount: Union[int, float] = 1, message: Optional[str] = None):
        """Increment progress by amount."""
        if hasattr(self, '_enhanced_adapter') and self._is_enhanced:
            self._enhanced_adapter.increment(amount, message)
        else:
            # Legacy increment
            self.update(self.current + amount, message)
    
    def complete(self):
        """Mark progress as completed."""
        if hasattr(self, '_enhanced_adapter') and self._is_enhanced:
            self._enhanced_adapter.complete()
        else:
            # Legacy complete
            self.state = ProgressState.COMPLETED
            self.end_time = datetime.now()
            self.current = self.total
    
    def get_progress_ratio(self) -> float:
        """Get progress ratio (0.0 to 1.0)."""
        if hasattr(self, '_enhanced_adapter') and self._is_enhanced:
            return self._enhanced_adapter.get_progress_ratio()
        else:
            # Legacy calculation
            if self.total <= 0:
                return 0.0
            return min(self.current / self.total, 1.0)
    
    def get_elapsed_time(self) -> Optional[timedelta]:
        """Get elapsed time since start."""
        if hasattr(self, '_enhanced_adapter') and self._is_enhanced:
            return self._enhanced_adapter.get_elapsed_time()
        else:
            # Legacy calculation
            if self.start_time:
                end_time = self.end_time or datetime.now()
                return end_time - self.start_time
            return None
    
    def render(self) -> str:
        """Render current progress display."""
        if hasattr(self, '_enhanced_adapter') and self._is_enhanced:
            return self._enhanced_adapter.render()
        else:
            # Legacy render - simple percentage
            progress_ratio = self.get_progress_ratio()
            percentage = progress_ratio * 100
            return f"{self.message} {percentage:.1f}%"
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive progress statistics."""
        if hasattr(self, '_enhanced_adapter') and self._is_enhanced:
            return self._enhanced_adapter.get_statistics()
        else:
            # Legacy statistics
            return {
                'state': self.state.value,
                'progress_ratio': self.get_progress_ratio(),
                'current': self.current,
                'total': self.total,
                'message': self.message,
                'elapsed_time': self.get_elapsed_time(),
                'use_questionary': False,
                'legacy_widget': self.widget is not None
            }
    
    def change_theme(self, new_style: str) -> bool:
        """Change the widget theme."""
        if hasattr(self, '_enhanced_adapter') and self._is_enhanced:
            return self._enhanced_adapter.change_theme(new_style)
        else:
            # Legacy mode doesn't support theme changes
            return False
    
    def is_questionary_enhanced(self) -> bool:
        """Check if this adapter uses Questionary enhancements."""
        return hasattr(self, '_enhanced_adapter') and self._is_enhanced
    
    def __str__(self) -> str:
        """String representation of the adapter."""
        if hasattr(self, '_enhanced_adapter') and self._is_enhanced:
            return str(self._enhanced_adapter)
        else:
            return f"<ProgressAdapter widget='{self.widget}' progress='{self.get_progress_ratio():.1%}'>"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return self.__str__()


# Convenience functions for creating common progress scenarios

def create_simple_progress(message: str = "Progress:",
                          total: Union[int, float] = 100,
                          show_percentage: bool = True,
                          **kwargs) -> ProgressAdapter:
    """Create a simple progress bar.
    
    Args:
        message: Progress message
        total: Total progress value
        show_percentage: Whether to show percentage
        **kwargs: Additional arguments passed to ProgressAdapter
        
    Returns:
        Configured ProgressAdapter for simple progress tracking
    """
    return ProgressAdapter(
        message=message,
        total=total,
        mode='bar',
        show_percentage=show_percentage,
        show_eta=False,
        show_rate=False,
        **kwargs
    )


def create_detailed_progress(message: str = "Processing:",
                           total: Union[int, float] = 100,
                           show_eta: bool = True,
                           show_rate: bool = True,
                           **kwargs) -> ProgressAdapter:
    """Create a detailed progress display.
    
    Args:
        message: Progress message
        total: Total progress value
        show_eta: Whether to show ETA
        show_rate: Whether to show processing rate
        **kwargs: Additional arguments passed to ProgressAdapter
        
    Returns:
        Configured ProgressAdapter for detailed progress tracking
    """
    return ProgressAdapter(
        message=message,
        total=total,
        mode='detailed',
        show_percentage=True,
        show_eta=show_eta,
        show_rate=show_rate,
        **kwargs
    )


def create_step_progress(steps: List[Dict[str, Any]],
                        message: str = "Step Progress:",
                        **kwargs) -> ProgressAdapter:
    """Create a step-based progress tracker.
    
    Args:
        steps: List of step definitions
        message: Progress message
        **kwargs: Additional arguments passed to ProgressAdapter
        
    Returns:
        Configured ProgressAdapter for step-based progress tracking
    """
    return ProgressAdapter(
        message=message,
        mode='steps',
        steps=steps,
        total=len(steps),
        **kwargs
    )


def create_spinner_progress(message: str = "Loading...",
                           **kwargs) -> ProgressAdapter:
    """Create a spinner progress indicator.
    
    Args:
        message: Progress message
        **kwargs: Additional arguments passed to ProgressAdapter
        
    Returns:
        Configured ProgressAdapter for spinner display
    """
    return ProgressAdapter(
        message=message,
        mode='spinner',
        show_percentage=False,
        show_eta=False,
        show_rate=False,
        **kwargs
    )


def create_download_progress(filename: str = "file",
                           total_bytes: int = 0,
                           **kwargs) -> ProgressAdapter:
    """Create a file download progress tracker.
    
    Args:
        filename: Name of file being downloaded
        total_bytes: Total file size in bytes
        **kwargs: Additional arguments passed to ProgressAdapter
        
    Returns:
        Configured ProgressAdapter for download tracking
    """
    return ProgressAdapter(
        message=f"Downloading {filename}:",
        total=total_bytes,
        mode='detailed',
        show_percentage=True,
        show_eta=True,
        show_rate=True,
        **kwargs
    )


# Export public interface
__all__ = [
    'ProgressAdapter',
    'EnhancedProgressAdapter',
    'ProgressMode',
    'ProgressState',
    'ProgressStep',
    'ProgressConfig',
    'ProgressCalculator',
    'ProgressRenderer',
    'create_simple_progress',
    'create_detailed_progress',
    'create_step_progress',
    'create_spinner_progress',
    'create_download_progress'
]