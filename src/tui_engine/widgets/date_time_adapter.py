"""DateTimeAdapter: Enhanced date/time selection widget with Questionary integration.

This adapter implements ValueWidgetProtocol and provides advanced date/time selection
functionality with professional styling, timezone support, format validation,
and calendar integration.

Features:
- Professional themes and styling through QuestionaryStyleAdapter
- Interactive date/time pickers with calendar views
- Timezone support and conversion
- Multiple date/time format validation
- Relative date parsing ("tomorrow", "next week", etc.)
- Range validation and constraints
- Backward compatibility with existing TUI Engine components
"""
from __future__ import annotations

from typing import Any, Callable, Optional, Union, List, Dict, Tuple
from datetime import datetime, date, time, timezone, timedelta
from dateutil import parser as date_parser, tz
import calendar
import re
import logging

from .protocols import ValueWidgetProtocol

# Import Questionary and related components
try:
    import questionary
    from ..questionary_adapter import QuestionaryStyleAdapter
    from ..themes import TUIEngineThemes
    QUESTIONARY_AVAILABLE = True
except ImportError:
    QUESTIONARY_AVAILABLE = False
    logging.warning("Questionary not available, falling back to basic date/time functionality")


class DateTimeParser:
    """Advanced date/time parsing with multiple format support."""
    
    def __init__(self):
        """Initialize date/time parser with common formats."""
        self.date_formats = [
            "%Y-%m-%d",           # 2025-11-05
            "%d/%m/%Y",           # 05/11/2025
            "%m/%d/%Y",           # 11/05/2025
            "%d-%m-%Y",           # 05-11-2025
            "%m-%d-%Y",           # 11-05-2025
            "%Y/%m/%d",           # 2025/11/05
            "%d.%m.%Y",           # 05.11.2025
            "%B %d, %Y",          # November 05, 2025
            "%b %d, %Y",          # Nov 05, 2025
            "%d %B %Y",           # 05 November 2025
            "%d %b %Y",           # 05 Nov 2025
        ]
        
        self.time_formats = [
            "%H:%M",              # 14:30
            "%H:%M:%S",           # 14:30:45
            "%I:%M %p",           # 02:30 PM
            "%I:%M:%S %p",        # 02:30:45 PM
        ]
        
        self.datetime_formats = []
        # Generate combined date/time formats
        for date_fmt in self.date_formats:
            for time_fmt in self.time_formats:
                self.datetime_formats.extend([
                    f"{date_fmt} {time_fmt}",
                    f"{date_fmt}T{time_fmt}",
                ])
        
        # Relative date patterns
        self.relative_patterns = {
            r'today': lambda: datetime.now().date(),
            r'tomorrow': lambda: datetime.now().date() + timedelta(days=1),
            r'yesterday': lambda: datetime.now().date() - timedelta(days=1),
            r'next week': lambda: datetime.now().date() + timedelta(weeks=1),
            r'last week': lambda: datetime.now().date() - timedelta(weeks=1),
            r'next month': lambda: self._add_months(datetime.now().date(), 1),
            r'last month': lambda: self._add_months(datetime.now().date(), -1),
            r'next year': lambda: datetime.now().date().replace(year=datetime.now().year + 1),
            r'last year': lambda: datetime.now().date().replace(year=datetime.now().year - 1),
            r'in (\d+) days?': lambda m: datetime.now().date() + timedelta(days=int(m.group(1))),
            r'(\d+) days? ago': lambda m: datetime.now().date() - timedelta(days=int(m.group(1))),
            r'in (\d+) weeks?': lambda m: datetime.now().date() + timedelta(weeks=int(m.group(1))),
            r'(\d+) weeks? ago': lambda m: datetime.now().date() - timedelta(weeks=int(m.group(1))),
        }
    
    def parse_date(self, date_str: str) -> Optional[date]:
        """Parse a date string into a date object.
        
        Args:
            date_str: String representation of date
            
        Returns:
            Parsed date object or None if parsing fails
        """
        if not date_str or not date_str.strip():
            return None
        
        date_str = date_str.strip().lower()
        
        # Try relative date parsing first
        for pattern, func in self.relative_patterns.items():
            match = re.match(pattern, date_str)
            if match:
                try:
                    if callable(func):
                        if match.groups():
                            return func(match)
                        else:
                            return func()
                except Exception:
                    continue
        
        # Try explicit format parsing
        for fmt in self.date_formats:
            try:
                parsed = datetime.strptime(date_str, fmt.lower())
                return parsed.date()
            except ValueError:
                continue
        
        # Try dateutil parser as fallback
        try:
            parsed = date_parser.parse(date_str, fuzzy=True)
            return parsed.date()
        except (ValueError, TypeError):
            pass
        
        return None
    
    def parse_time(self, time_str: str) -> Optional[time]:
        """Parse a time string into a time object.
        
        Args:
            time_str: String representation of time
            
        Returns:
            Parsed time object or None if parsing fails
        """
        if not time_str or not time_str.strip():
            return None
        
        time_str = time_str.strip()
        
        # Try explicit format parsing
        for fmt in self.time_formats:
            try:
                parsed = datetime.strptime(time_str, fmt)
                return parsed.time()
            except ValueError:
                continue
        
        # Try dateutil parser as fallback
        try:
            parsed = date_parser.parse(time_str, fuzzy=True)
            return parsed.time()
        except (ValueError, TypeError):
            pass
        
        return None
    
    def parse_datetime(self, datetime_str: str, default_tz: Optional[timezone] = None) -> Optional[datetime]:
        """Parse a datetime string into a datetime object.
        
        Args:
            datetime_str: String representation of datetime
            default_tz: Default timezone if none specified
            
        Returns:
            Parsed datetime object or None if parsing fails
        """
        if not datetime_str or not datetime_str.strip():
            return None
        
        datetime_str = datetime_str.strip()
        
        # Try explicit format parsing
        for fmt in self.datetime_formats:
            try:
                parsed = datetime.strptime(datetime_str, fmt)
                if default_tz and parsed.tzinfo is None:
                    parsed = parsed.replace(tzinfo=default_tz)
                return parsed
            except ValueError:
                continue
        
        # Try dateutil parser as fallback
        try:
            parsed = date_parser.parse(datetime_str, fuzzy=True)
            if default_tz and parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=default_tz)
            return parsed
        except (ValueError, TypeError):
            pass
        
        return None
    
    def format_date(self, date_obj: date, format_str: str = "%Y-%m-%d") -> str:
        """Format a date object as string.
        
        Args:
            date_obj: Date object to format
            format_str: Format string
            
        Returns:
            Formatted date string
        """
        try:
            return date_obj.strftime(format_str)
        except Exception:
            return str(date_obj)
    
    def format_time(self, time_obj: time, format_str: str = "%H:%M") -> str:
        """Format a time object as string.
        
        Args:
            time_obj: Time object to format
            format_str: Format string
            
        Returns:
            Formatted time string
        """
        try:
            return time_obj.strftime(format_str)
        except Exception:
            return str(time_obj)
    
    def format_datetime(self, datetime_obj: datetime, format_str: str = "%Y-%m-%d %H:%M") -> str:
        """Format a datetime object as string.
        
        Args:
            datetime_obj: Datetime object to format
            format_str: Format string
            
        Returns:
            Formatted datetime string
        """
        try:
            return datetime_obj.strftime(format_str)
        except Exception:
            return str(datetime_obj)
    
    def _add_months(self, date_obj: date, months: int) -> date:
        """Add months to a date, handling month overflow."""
        try:
            year = date_obj.year
            month = date_obj.month + months
            
            while month > 12:
                year += 1
                month -= 12
            while month < 1:
                year -= 1
                month += 12
            
            # Handle day overflow (e.g., Jan 31 + 1 month)
            day = min(date_obj.day, calendar.monthrange(year, month)[1])
            
            return date(year, month, day)
        except Exception:
            return date_obj


class CalendarGenerator:
    """Generate calendar views for date selection."""
    
    def __init__(self, locale: str = 'en_US'):
        """Initialize calendar generator.
        
        Args:
            locale: Locale for calendar formatting
        """
        self.locale = locale
        
    def generate_month_calendar(
        self, 
        year: int, 
        month: int, 
        selected_date: Optional[date] = None,
        today: Optional[date] = None
    ) -> List[str]:
        """Generate a month calendar view.
        
        Args:
            year: Year to display
            month: Month to display (1-12)
            selected_date: Currently selected date to highlight
            today: Today's date to highlight
            
        Returns:
            List of calendar lines
        """
        if today is None:
            today = datetime.now().date()
        
        cal = calendar.monthcalendar(year, month)
        month_name = calendar.month_name[month]
        
        lines = []
        
        # Header
        lines.append(f"📅 {month_name} {year}")
        lines.append("   Mo Tu We Th Fr Sa Su")
        
        # Calendar days
        for week in cal:
            week_line = "   "
            for day in week:
                if day == 0:
                    week_line += "   "
                else:
                    day_date = date(year, month, day)
                    
                    # Format day with special indicators
                    if selected_date and day_date == selected_date:
                        day_str = f"[{day:2d}]"  # Selected
                    elif day_date == today:
                        day_str = f"({day:2d})"  # Today
                    else:
                        day_str = f" {day:2d} "
                    
                    week_line += day_str
            
            lines.append(week_line)
        
        # Legend
        lines.append("")
        lines.append("   [DD] Selected  (DD) Today")
        
        return lines
    
    def get_month_choices(self, year: int, selected_month: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get month choices for selection.
        
        Args:
            year: Year for month selection
            selected_month: Currently selected month
            
        Returns:
            List of month choice dictionaries
        """
        choices = []
        
        for month in range(1, 13):
            month_name = calendar.month_name[month]
            display_name = f"{month:2d}. {month_name}"
            
            if selected_month == month:
                display_name = f"➤ {display_name}"
            
            choices.append({
                'name': display_name,
                'value': month,
                'selected': selected_month == month
            })
        
        return choices
    
    def get_year_choices(self, current_year: int, range_years: int = 10) -> List[Dict[str, Any]]:
        """Get year choices for selection.
        
        Args:
            current_year: Current year
            range_years: Number of years before/after current
            
        Returns:
            List of year choice dictionaries
        """
        choices = []
        
        start_year = current_year - range_years
        end_year = current_year + range_years
        
        for year in range(start_year, end_year + 1):
            display_name = str(year)
            
            if year == current_year:
                display_name = f"➤ {display_name}"
            
            choices.append({
                'name': display_name,
                'value': year,
                'selected': year == current_year
            })
        
        return choices


class TimezoneManager:
    """Manage timezones and conversions."""
    
    def __init__(self):
        """Initialize timezone manager."""
        self.common_timezones = [
            ('UTC', 'UTC'),
            ('US/Eastern', 'Eastern Time'),
            ('US/Central', 'Central Time'),
            ('US/Mountain', 'Mountain Time'),
            ('US/Pacific', 'Pacific Time'),
            ('Europe/London', 'London'),
            ('Europe/Paris', 'Paris'),
            ('Europe/Berlin', 'Berlin'),
            ('Europe/Rome', 'Rome'),
            ('Asia/Tokyo', 'Tokyo'),
            ('Asia/Shanghai', 'Shanghai'),
            ('Asia/Kolkata', 'Mumbai'),
            ('Australia/Sydney', 'Sydney'),
            ('America/New_York', 'New York'),
            ('America/Los_Angeles', 'Los Angeles'),
            ('America/Chicago', 'Chicago'),
            ('America/Denver', 'Denver'),
        ]
    
    def get_timezone(self, tz_name: str) -> Optional[timezone]:
        """Get timezone object by name.
        
        Args:
            tz_name: Timezone name
            
        Returns:
            Timezone object or None if not found
        """
        try:
            return tz.gettz(tz_name)
        except Exception:
            return None
    
    def get_local_timezone(self) -> timezone:
        """Get local timezone."""
        try:
            return tz.tzlocal()
        except Exception:
            return timezone.utc
    
    def convert_timezone(
        self, 
        dt: datetime, 
        from_tz: Optional[timezone] = None, 
        to_tz: Optional[timezone] = None
    ) -> datetime:
        """Convert datetime between timezones.
        
        Args:
            dt: Datetime to convert
            from_tz: Source timezone (default: local)
            to_tz: Target timezone (default: UTC)
            
        Returns:
            Converted datetime
        """
        if from_tz is None:
            from_tz = self.get_local_timezone()
        if to_tz is None:
            to_tz = timezone.utc
        
        try:
            # Add timezone if naive
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=from_tz)
            
            # Convert timezone
            return dt.astimezone(to_tz)
        except Exception:
            return dt
    
    def get_timezone_choices(self) -> List[Dict[str, Any]]:
        """Get common timezone choices.
        
        Returns:
            List of timezone choice dictionaries
        """
        choices = []
        
        for tz_name, display_name in self.common_timezones:
            try:
                tz_obj = self.get_timezone(tz_name)
                if tz_obj:
                    # Get current offset
                    now = datetime.now(tz_obj)
                    offset = now.strftime('%z')
                    
                    full_display = f"{display_name} ({offset})"
                    
                    choices.append({
                        'name': full_display,
                        'value': tz_name,
                        'timezone': tz_obj,
                        'offset': offset
                    })
            except Exception:
                continue
        
        return choices


class EnhancedDateTimeAdapter(ValueWidgetProtocol):
    """Enhanced DateTime adapter with Questionary integration and calendar support.
    
    This class provides advanced date/time selection functionality with:
    - Professional theme integration
    - Interactive calendar and time pickers
    - Timezone support and conversion
    - Multiple format validation
    - Range constraints and validation
    """
    
    def __init__(
        self,
        message: str = "Select date/time:",
        style: Union[str, dict] = 'professional_blue',
        mode: str = 'datetime',  # 'date', 'time', 'datetime'
        format_str: Optional[str] = None,
        default_value: Optional[Union[str, datetime, date, time]] = None,
        timezone_aware: bool = False,
        default_timezone: Optional[str] = None,
        min_date: Optional[Union[str, date, datetime]] = None,
        max_date: Optional[Union[str, date, datetime]] = None,
        allow_relative: bool = True,
        validator: Optional[Callable[[Union[datetime, date, time]], Union[bool, str]]] = None,
        **kwargs
    ):
        """Initialize enhanced datetime adapter.
        
        Args:
            message: Prompt message
            style: Theme name or custom style dict
            mode: Selection mode ('date', 'time', 'datetime')
            format_str: Custom format string for display
            default_value: Default date/time value
            timezone_aware: Whether to handle timezones
            default_timezone: Default timezone name
            min_date: Minimum allowed date
            max_date: Maximum allowed date
            allow_relative: Allow relative date parsing
            validator: Custom validation function
            **kwargs: Additional arguments for underlying widget
        """
        self.message = message
        self.mode = mode.lower()
        self.timezone_aware = timezone_aware
        self.allow_relative = allow_relative
        self.validator = validator
        self.kwargs = kwargs
        
        # Initialize format strings
        self.format_str = format_str or self._get_default_format()
        
        # Initialize parsers and managers
        self.date_parser = DateTimeParser()
        self.calendar_gen = CalendarGenerator()
        self.timezone_mgr = TimezoneManager()
        
        # Handle default timezone
        self.default_timezone = None
        if timezone_aware and default_timezone:
            self.default_timezone = self.timezone_mgr.get_timezone(default_timezone)
        if not self.default_timezone and timezone_aware:
            self.default_timezone = self.timezone_mgr.get_local_timezone()
        
        # Parse and store constraints
        self.min_date = self._parse_constraint(min_date)
        self.max_date = self._parse_constraint(max_date)
        
        # Initialize current value
        self._current_value = self._parse_default_value(default_value)
        
        # Initialize style adapter
        self.style_adapter = None
        self.current_theme = style
        if QUESTIONARY_AVAILABLE:
            self.style_adapter = QuestionaryStyleAdapter()
            if isinstance(style, str):
                self.style_adapter.set_theme(style)
        
        # Initialize widget
        self._widget = None
        self._create_widget()
        
        # Adapter protocol attributes
        self._tui_path: str | None = None
        self._tui_focusable: bool = True
        self.element = None
    
    def _get_default_format(self) -> str:
        """Get default format string based on mode."""
        formats = {
            'date': '%Y-%m-%d',
            'time': '%H:%M',
            'datetime': '%Y-%m-%d %H:%M'
        }
        return formats.get(self.mode, '%Y-%m-%d %H:%M')
    
    def _parse_constraint(self, constraint: Optional[Union[str, date, datetime]]) -> Optional[date]:
        """Parse date constraint."""
        if constraint is None:
            return None
        
        if isinstance(constraint, date):
            return constraint
        elif isinstance(constraint, datetime):
            return constraint.date()
        elif isinstance(constraint, str):
            parsed = self.date_parser.parse_date(constraint)
            return parsed
        
        return None
    
    def _parse_default_value(self, default: Optional[Union[str, datetime, date, time]]) -> Optional[Union[datetime, date, time]]:
        """Parse default value based on mode."""
        if default is None:
            return None
        
        if isinstance(default, str):
            if self.mode == 'date':
                return self.date_parser.parse_date(default)
            elif self.mode == 'time':
                return self.date_parser.parse_time(default)
            else:  # datetime
                return self.date_parser.parse_datetime(default, self.default_timezone)
        
        # Return as-is if already correct type
        if self.mode == 'date' and isinstance(default, date):
            return default
        elif self.mode == 'time' and isinstance(default, time):
            return default
        elif self.mode == 'datetime' and isinstance(default, datetime):
            return default
        
        return None
    
    def _create_widget(self):
        """Create the underlying datetime widget."""
        if not QUESTIONARY_AVAILABLE:
            # Fallback to basic implementation
            self._widget = None
            return
        
        try:
            # Get style for Questionary
            style = None
            if self.style_adapter:
                style = self.style_adapter.get_questionary_style()
            
            # Create appropriate widget based on mode
            if self.mode == 'date':
                self._widget = self._create_date_widget(style)
            elif self.mode == 'time':
                self._widget = self._create_time_widget(style)
            else:  # datetime
                self._widget = self._create_datetime_widget(style)
            
        except Exception as e:
            logging.warning(f"Failed to create Questionary datetime widget: {e}")
            self._widget = None
    
    def _create_date_widget(self, style) -> Any:
        """Create date selection widget."""
        if not QUESTIONARY_AVAILABLE:
            return None
        
        choices = [
            questionary.Choice("📅 Use calendar picker", value='calendar'),
            questionary.Choice("⌨️  Enter date manually", value='manual'),
        ]
        
        if self.allow_relative:
            choices.append(questionary.Choice("🔄 Enter relative date", value='relative'))
        
        return questionary.select(
            message=self.message,
            choices=choices,
            style=style,
            **self.kwargs
        )
    
    def _create_time_widget(self, style) -> Any:
        """Create time selection widget."""
        if not QUESTIONARY_AVAILABLE:
            return None
        
        choices = [
            questionary.Choice("🕐 Enter time manually", value='manual'),
            questionary.Choice("⏰ Select from common times", value='common'),
        ]
        
        return questionary.select(
            message=self.message,
            choices=choices,
            style=style,
            **self.kwargs
        )
    
    def _create_datetime_widget(self, style) -> Any:
        """Create datetime selection widget."""
        if not QUESTIONARY_AVAILABLE:
            return None
        
        choices = [
            questionary.Choice("📅 Date and time picker", value='picker'),
            questionary.Choice("⌨️  Enter datetime manually", value='manual'),
        ]
        
        if self.allow_relative:
            choices.append(questionary.Choice("🔄 Enter relative datetime", value='relative'))
        
        if self.timezone_aware:
            choices.append(questionary.Choice("🌍 Include timezone", value='timezone'))
        
        return questionary.select(
            message=self.message,
            choices=choices,
            style=style,
            **self.kwargs
        )
    
    def _handle_calendar_picker(self) -> Optional[date]:
        """Handle interactive calendar picker."""
        if not QUESTIONARY_AVAILABLE:
            return None
        
        try:
            # Start with current date or today
            current_date = self._current_value if isinstance(self._current_value, date) else datetime.now().date()
            selected_year = current_date.year
            selected_month = current_date.month
            selected_day = current_date.day
            
            style = self.style_adapter.get_questionary_style() if self.style_adapter else None
            
            while True:
                # Year selection
                year_choices = self.calendar_gen.get_year_choices(selected_year, 5)
                year_choices_q = [
                    questionary.Choice(choice['name'], value=choice['value'])
                    for choice in year_choices
                ]
                
                selected_year = questionary.select(
                    message="Select year:",
                    choices=year_choices_q,
                    style=style
                ).ask()
                
                if selected_year is None:
                    return None
                
                # Month selection
                month_choices = self.calendar_gen.get_month_choices(selected_year, selected_month)
                month_choices_q = [
                    questionary.Choice(choice['name'], value=choice['value'])
                    for choice in month_choices
                ]
                
                selected_month = questionary.select(
                    message="Select month:",
                    choices=month_choices_q,
                    style=style
                ).ask()
                
                if selected_month is None:
                    continue
                
                # Show calendar and day selection
                calendar_lines = self.calendar_gen.generate_month_calendar(
                    selected_year, selected_month, 
                    date(selected_year, selected_month, selected_day) if selected_day <= calendar.monthrange(selected_year, selected_month)[1] else None
                )
                
                # Display calendar
                print("\n".join(calendar_lines))
                
                # Day input
                max_day = calendar.monthrange(selected_year, selected_month)[1]
                day_result = questionary.text(
                    message=f"Enter day (1-{max_day}):",
                    default=str(min(selected_day, max_day)),
                    style=style
                ).ask()
                
                if day_result is None:
                    continue
                
                try:
                    selected_day = int(day_result)
                    if 1 <= selected_day <= max_day:
                        return date(selected_year, selected_month, selected_day)
                    else:
                        questionary.print(f"❌ Day must be between 1 and {max_day}", style="red")
                except ValueError:
                    questionary.print("❌ Please enter a valid day number", style="red")
                
        except Exception as e:
            logging.error(f"Calendar picker failed: {e}")
            return None
    
    def _handle_manual_input(self, input_type: str = 'datetime') -> Optional[Union[datetime, date, time]]:
        """Handle manual date/time input."""
        if not QUESTIONARY_AVAILABLE:
            return None
        
        try:
            style = self.style_adapter.get_questionary_style() if self.style_adapter else None
            
            # Get current value as default
            default_str = ""
            if self._current_value:
                if input_type == 'date' and isinstance(self._current_value, date):
                    default_str = self.date_parser.format_date(self._current_value, self.format_str)
                elif input_type == 'time' and isinstance(self._current_value, time):
                    default_str = self.date_parser.format_time(self._current_value, self.format_str)
                elif input_type == 'datetime' and isinstance(self._current_value, datetime):
                    default_str = self.date_parser.format_datetime(self._current_value, self.format_str)
            
            # Create input prompt with format hints
            format_hints = {
                'date': "Format: YYYY-MM-DD, DD/MM/YYYY, or 'today', 'tomorrow'",
                'time': "Format: HH:MM, HH:MM:SS, or 2:30 PM",
                'datetime': "Format: YYYY-MM-DD HH:MM or relative date + time"
            }
            
            hint = format_hints.get(input_type, format_hints['datetime'])
            
            result = questionary.text(
                message=f"Enter {input_type} ({hint}):",
                default=default_str,
                style=style
            ).ask()
            
            if result is None:
                return None
            
            # Parse the input
            if input_type == 'date':
                return self.date_parser.parse_date(result)
            elif input_type == 'time':
                return self.date_parser.parse_time(result)
            else:  # datetime
                return self.date_parser.parse_datetime(result, self.default_timezone)
                
        except Exception as e:
            logging.error(f"Manual input failed: {e}")
            return None
    
    def _handle_common_times(self) -> Optional[time]:
        """Handle common time selection."""
        if not QUESTIONARY_AVAILABLE:
            return None
        
        try:
            style = self.style_adapter.get_questionary_style() if self.style_adapter else None
            
            # Common times
            common_times = [
                ("09:00", "9:00 AM"),
                ("10:00", "10:00 AM"),
                ("11:00", "11:00 AM"),
                ("12:00", "12:00 PM (Noon)"),
                ("13:00", "1:00 PM"),
                ("14:00", "2:00 PM"),
                ("15:00", "3:00 PM"),
                ("16:00", "4:00 PM"),
                ("17:00", "5:00 PM"),
                ("18:00", "6:00 PM"),
                ("19:00", "7:00 PM"),
                ("20:00", "8:00 PM"),
                ("21:00", "9:00 PM"),
                ("22:00", "10:00 PM"),
            ]
            
            choices = [
                questionary.Choice(display, value=time_str)
                for time_str, display in common_times
            ]
            
            choices.append(questionary.Choice("⌨️  Enter custom time", value='custom'))
            
            result = questionary.select(
                message="Select time:",
                choices=choices,
                style=style
            ).ask()
            
            if result is None:
                return None
            elif result == 'custom':
                return self._handle_manual_input('time')
            else:
                return self.date_parser.parse_time(result)
                
        except Exception as e:
            logging.error(f"Common time selection failed: {e}")
            return None
    
    def _handle_timezone_selection(self) -> Optional[datetime]:
        """Handle timezone-aware datetime selection."""
        if not QUESTIONARY_AVAILABLE:
            return None
        
        try:
            style = self.style_adapter.get_questionary_style() if self.style_adapter else None
            
            # First get the datetime
            dt = self._handle_manual_input('datetime')
            if dt is None:
                return None
            
            # Make sure it's a datetime object
            if isinstance(dt, date) and not isinstance(dt, datetime):
                dt = datetime.combine(dt, time())
            
            # Then select timezone
            tz_choices = self.timezone_mgr.get_timezone_choices()
            choices = [
                questionary.Choice(choice['name'], value=choice['value'])
                for choice in tz_choices
            ]
            
            selected_tz_name = questionary.select(
                message="Select timezone:",
                choices=choices,
                style=style
            ).ask()
            
            if selected_tz_name is None:
                return dt
            
            # Apply timezone
            selected_tz = self.timezone_mgr.get_timezone(selected_tz_name)
            if selected_tz and dt.tzinfo is None:
                dt = dt.replace(tzinfo=selected_tz)
            
            return dt
            
        except Exception as e:
            logging.error(f"Timezone selection failed: {e}")
            return None
    
    def select_datetime(self) -> Optional[Union[datetime, date, time]]:
        """Launch interactive datetime selection.
        
        Returns:
            Selected datetime/date/time or None if cancelled
        """
        if not QUESTIONARY_AVAILABLE:
            return self._fallback_input()
        
        try:
            # Get selection method
            selection = self._widget.ask() if self._widget else None
            
            if selection is None:
                return None
            
            result = None
            
            if selection == 'calendar':
                result = self._handle_calendar_picker()
            elif selection == 'manual':
                result = self._handle_manual_input(self.mode)
            elif selection == 'relative':
                result = self._handle_manual_input(self.mode)
            elif selection == 'common':
                result = self._handle_common_times()
            elif selection == 'picker':
                # Combined date and time picker
                date_result = self._handle_calendar_picker()
                if date_result:
                    time_result = self._handle_common_times()
                    if time_result:
                        result = datetime.combine(date_result, time_result)
                        if self.timezone_aware and self.default_timezone:
                            result = result.replace(tzinfo=self.default_timezone)
            elif selection == 'timezone':
                result = self._handle_timezone_selection()
            
            # Validate result
            if result and self._validate_value(result):
                self._current_value = result
                return result
            
            return None
            
        except (KeyboardInterrupt, EOFError):
            return None
        except Exception as e:
            logging.error(f"DateTime selection failed: {e}")
            return self._fallback_input()
    
    def _fallback_input(self) -> Optional[Union[datetime, date, time]]:
        """Fallback input when Questionary is not available."""
        try:
            prompt = f"{self.message} "
            if self.mode == 'date':
                prompt += "(YYYY-MM-DD): "
            elif self.mode == 'time':
                prompt += "(HH:MM): "
            else:
                prompt += "(YYYY-MM-DD HH:MM): "
            
            user_input = input(prompt)
            
            if not user_input.strip():
                return None
            
            # Parse input
            if self.mode == 'date':
                result = self.date_parser.parse_date(user_input)
            elif self.mode == 'time':
                result = self.date_parser.parse_time(user_input)
            else:
                result = self.date_parser.parse_datetime(user_input, self.default_timezone)
            
            if result and self._validate_value(result):
                self._current_value = result
                return result
            else:
                print("❌ Invalid date/time format or out of range")
                
        except (KeyboardInterrupt, EOFError):
            pass
        
        return None
    
    def _validate_value(self, value: Union[datetime, date, time]) -> bool:
        """Validate datetime value against constraints."""
        try:
            # Convert to date for range checking
            check_date = None
            if isinstance(value, date):
                check_date = value
            elif isinstance(value, datetime):
                check_date = value.date()
            
            # Check date range constraints
            if check_date:
                if self.min_date and check_date < self.min_date:
                    return False
                if self.max_date and check_date > self.max_date:
                    return False
            
            # Custom validator
            if self.validator:
                result = self.validator(value)
                if isinstance(result, bool):
                    return result
                elif isinstance(result, str):
                    return len(result) == 0
                else:
                    return bool(result)
            
            return True
            
        except Exception:
            return False
    
    def focus(self) -> None:
        """Focus the datetime widget."""
        if self._widget is None:
            return
        
        if hasattr(self._widget, "focus") and callable(self._widget.focus):
            try:
                self._widget.focus()
            except Exception:
                pass
    
    def _tui_sync(self) -> str | None:
        """Read the current value from the wrapped widget and return it."""
        if self._current_value is None:
            return None
        
        # Format current value as string
        try:
            if isinstance(self._current_value, date) and not isinstance(self._current_value, datetime):
                return self.date_parser.format_date(self._current_value, self.format_str)
            elif isinstance(self._current_value, time):
                return self.date_parser.format_time(self._current_value, self.format_str)
            elif isinstance(self._current_value, datetime):
                return self.date_parser.format_datetime(self._current_value, self.format_str)
        except Exception:
            pass
        
        return str(self._current_value)
    
    def get_value(self) -> Optional[Union[datetime, date, time]]:
        """Get the current datetime value."""
        return self._current_value
    
    def set_value(self, value: Any) -> None:
        """Set the datetime value."""
        if value is None:
            self._current_value = None
            return
        
        # Parse value based on type and mode
        if isinstance(value, (datetime, date, time)):
            self._current_value = value
        elif isinstance(value, str):
            if self.mode == 'date':
                self._current_value = self.date_parser.parse_date(value)
            elif self.mode == 'time':
                self._current_value = self.date_parser.parse_time(value)
            else:
                self._current_value = self.date_parser.parse_datetime(value, self.default_timezone)
        else:
            self._current_value = None
    
    def get_formatted_value(self, format_str: Optional[str] = None) -> str:
        """Get formatted string representation of current value.
        
        Args:
            format_str: Custom format string (uses default if None)
            
        Returns:
            Formatted datetime string
        """
        if self._current_value is None:
            return ""
        
        fmt = format_str or self.format_str
        
        try:
            if isinstance(self._current_value, date) and not isinstance(self._current_value, datetime):
                return self.date_parser.format_date(self._current_value, fmt)
            elif isinstance(self._current_value, time):
                return self.date_parser.format_time(self._current_value, fmt)
            elif isinstance(self._current_value, datetime):
                return self.date_parser.format_datetime(self._current_value, fmt)
        except Exception:
            pass
        
        return str(self._current_value)
    
    def validate_current_value(self) -> Tuple[bool, str]:
        """Validate the current value.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if self._current_value is None:
            return False, "No date/time selected"
        
        if not self._validate_value(self._current_value):
            return False, "Date/time is out of allowed range or invalid"
        
        return True, ""
    
    def set_constraints(
        self, 
        min_date: Optional[Union[str, date, datetime]] = None,
        max_date: Optional[Union[str, date, datetime]] = None
    ):
        """Update date constraints.
        
        Args:
            min_date: Minimum allowed date
            max_date: Maximum allowed date
        """
        if min_date is not None:
            self.min_date = self._parse_constraint(min_date)
        if max_date is not None:
            self.max_date = self._parse_constraint(max_date)
    
    def convert_timezone(self, target_timezone: str) -> bool:
        """Convert current datetime to different timezone.
        
        Args:
            target_timezone: Target timezone name
            
        Returns:
            True if conversion successful
        """
        if not self.timezone_aware or not isinstance(self._current_value, datetime):
            return False
        
        try:
            target_tz = self.timezone_mgr.get_timezone(target_timezone)
            if target_tz:
                self._current_value = self.timezone_mgr.convert_timezone(
                    self._current_value, 
                    to_tz=target_tz
                )
                return True
        except Exception:
            pass
        
        return False
    
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
    
    def enable_validation(self, validator: Callable[[Union[datetime, date, time]], Union[bool, str]]):
        """Enable custom validation."""
        self.validator = validator
    
    def disable_validation(self):
        """Disable custom validation."""
        self.validator = None
    
    def is_questionary_enhanced(self) -> bool:
        """Check if Questionary enhancement is active."""
        return QUESTIONARY_AVAILABLE and self._widget is not None
    
    def get_widget_info(self) -> dict:
        """Get comprehensive widget information."""
        return {
            'use_questionary': self.is_questionary_enhanced(),
            'has_validator': self.validator is not None,
            'current_value': self.get_formatted_value(),
            'theme': self.current_theme,
            'message': self.message,
            'mode': self.mode,
            'format_str': self.format_str,
            'timezone_aware': self.timezone_aware,
            'allow_relative': self.allow_relative,
            'min_date': str(self.min_date) if self.min_date else None,
            'max_date': str(self.max_date) if self.max_date else None,
            'default_timezone': str(self.default_timezone) if self.default_timezone else None
        }
    
    @property
    def ptk_widget(self) -> Any:
        """Get the underlying prompt-toolkit widget."""
        return self._widget
    
    def __repr__(self) -> str:
        """String representation of the adapter."""
        value_str = self.get_formatted_value() or 'None'
        return f"<EnhancedDateTimeAdapter mode='{self.mode}' value='{value_str}'>"


class DateTimeAdapter(ValueWidgetProtocol):
    """Backward-compatible DateTimeAdapter that automatically uses enhanced features when available.
    
    This class maintains full backward compatibility while providing access to enhanced
    datetime picker features when they're available and beneficial.
    """
    
    # runtime contract attributes
    _tui_path: str | None = None
    _tui_focusable: bool = True
    
    def __init__(self, widget: Any | None = None, element: Any | None = None, **kwargs):
        """Initialize DateTimeAdapter with backward compatibility.
        
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
            self._current_value = None
        else:
            # Use enhanced adapter for new functionality
            self._enhanced_adapter = None
            self._widget = None
            self._legacy_mode = False
            self._current_value = None
            
            # Try to create enhanced adapter if Questionary is available
            if QUESTIONARY_AVAILABLE and kwargs:
                try:
                    self._enhanced_adapter = EnhancedDateTimeAdapter(**kwargs)
                    self._widget = self._enhanced_adapter.ptk_widget
                except Exception as e:
                    logging.warning(f"Failed to create enhanced datetime adapter, falling back to basic: {e}")
    
    def focus(self) -> None:
        """Focus the datetime widget."""
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
            return str(self._current_value) if self._current_value else None
        
        try:
            # common attribute names for datetime widgets
            for attr in ['text', 'value', 'current_value', 'datetime']:
                if hasattr(w, attr):
                    return str(getattr(w, attr))
        except Exception:
            pass
        
        return str(self._current_value) if self._current_value else None
    
    def get_value(self) -> Optional[Union[datetime, date, time]]:
        """Get the current datetime value."""
        if self._enhanced_adapter:
            return self._enhanced_adapter.get_value()
        
        return self._current_value
    
    def set_value(self, value: Any) -> None:
        """Set the datetime value."""
        if self._enhanced_adapter:
            self._enhanced_adapter.set_value(value)
            return
        
        self._current_value = value
        
        # Update underlying widget
        w = self._widget
        if w is None:
            return
        
        try:
            for attr in ['text', 'value', 'current_value', 'datetime']:
                if hasattr(w, attr):
                    setattr(w, attr, value)
                    return
        except Exception:
            pass
    
    @property
    def ptk_widget(self) -> Any:
        """Get the underlying prompt-toolkit widget."""
        return self._widget
    
    # Enhanced functionality delegation (when available)
    def select_datetime(self) -> Optional[Union[datetime, date, time]]:
        """Launch interactive datetime selection (enhanced feature)."""
        if self._enhanced_adapter:
            return self._enhanced_adapter.select_datetime()
        return None
    
    def get_formatted_value(self, format_str: Optional[str] = None) -> str:
        """Get formatted value (enhanced feature)."""
        if self._enhanced_adapter:
            return self._enhanced_adapter.get_formatted_value(format_str)
        return str(self._current_value) if self._current_value else ""
    
    def validate_current_value(self) -> Tuple[bool, str]:
        """Validate current value (enhanced feature)."""
        if self._enhanced_adapter:
            return self._enhanced_adapter.validate_current_value()
        return True, ""
    
    def set_constraints(self, min_date=None, max_date=None):
        """Set date constraints (enhanced feature)."""
        if self._enhanced_adapter:
            self._enhanced_adapter.set_constraints(min_date, max_date)
    
    def convert_timezone(self, target_timezone: str) -> bool:
        """Convert timezone (enhanced feature)."""
        if self._enhanced_adapter:
            return self._enhanced_adapter.convert_timezone(target_timezone)
        return False
    
    def change_theme(self, theme_name: str):
        """Change theme (enhanced feature)."""
        if self._enhanced_adapter:
            self._enhanced_adapter.change_theme(theme_name)
    
    def set_message(self, message: str):
        """Update message (enhanced feature)."""
        if self._enhanced_adapter:
            self._enhanced_adapter.set_message(message)
    
    def enable_validation(self, validator):
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
            'current_value': str(self._current_value) if self._current_value else '',
            'theme': 'default',
            'mode': 'datetime',
            'legacy_mode': self._legacy_mode
        }
    
    def __repr__(self) -> str:
        """String representation of the adapter."""
        if self._enhanced_adapter:
            return repr(self._enhanced_adapter)
        return f"<DateTimeAdapter widget={self._widget!r} value='{self._current_value}'>"


# Convenience functions for creating datetime widgets

def create_date_picker(
    message: str = "Select date:",
    default_value: Optional[Union[str, date]] = None,
    min_date: Optional[Union[str, date]] = None,
    max_date: Optional[Union[str, date]] = None,
    style: str = 'professional_blue',
    **kwargs
) -> DateTimeAdapter:
    """Create a DateTimeAdapter for date selection.
    
    Args:
        message: Prompt message
        default_value: Default date value
        min_date: Minimum allowed date
        max_date: Maximum allowed date
        style: Theme name for styling
        **kwargs: Additional arguments
        
    Returns:
        DateTimeAdapter configured for date selection
    """
    return DateTimeAdapter(
        message=message,
        mode='date',
        default_value=default_value,
        min_date=min_date,
        max_date=max_date,
        style=style,
        **kwargs
    )


def create_time_picker(
    message: str = "Select time:",
    default_value: Optional[Union[str, time]] = None,
    style: str = 'professional_blue',
    **kwargs
) -> DateTimeAdapter:
    """Create a DateTimeAdapter for time selection.
    
    Args:
        message: Prompt message
        default_value: Default time value
        style: Theme name for styling
        **kwargs: Additional arguments
        
    Returns:
        DateTimeAdapter configured for time selection
    """
    return DateTimeAdapter(
        message=message,
        mode='time',
        default_value=default_value,
        style=style,
        **kwargs
    )


def create_datetime_picker(
    message: str = "Select date and time:",
    default_value: Optional[Union[str, datetime]] = None,
    timezone_aware: bool = False,
    default_timezone: Optional[str] = None,
    min_date: Optional[Union[str, date]] = None,
    max_date: Optional[Union[str, date]] = None,
    style: str = 'professional_blue',
    **kwargs
) -> DateTimeAdapter:
    """Create a DateTimeAdapter for datetime selection.
    
    Args:
        message: Prompt message
        default_value: Default datetime value
        timezone_aware: Whether to handle timezones
        default_timezone: Default timezone name
        min_date: Minimum allowed date
        max_date: Maximum allowed date
        style: Theme name for styling
        **kwargs: Additional arguments
        
    Returns:
        DateTimeAdapter configured for datetime selection
    """
    return DateTimeAdapter(
        message=message,
        mode='datetime',
        default_value=default_value,
        timezone_aware=timezone_aware,
        default_timezone=default_timezone,
        min_date=min_date,
        max_date=max_date,
        style=style,
        **kwargs
    )


def create_birthday_picker(
    message: str = "Enter your birthday:",
    style: str = 'professional_blue',
    **kwargs
) -> DateTimeAdapter:
    """Create a DateTimeAdapter for birthday selection.
    
    Args:
        message: Prompt message
        style: Theme name for styling
        **kwargs: Additional arguments
        
    Returns:
        DateTimeAdapter configured for birthday selection
    """
    # Set reasonable constraints for birthdays
    today = datetime.now().date()
    min_date = date(today.year - 120, 1, 1)  # 120 years ago
    max_date = today  # Can't be born in the future
    
    return DateTimeAdapter(
        message=message,
        mode='date',
        min_date=min_date,
        max_date=max_date,
        style=style,
        **kwargs
    )


def create_event_scheduler(
    message: str = "Schedule event:",
    timezone_aware: bool = True,
    style: str = 'professional_blue',
    **kwargs
) -> DateTimeAdapter:
    """Create a DateTimeAdapter for event scheduling.
    
    Args:
        message: Prompt message
        timezone_aware: Whether to handle timezones
        style: Theme name for styling
        **kwargs: Additional arguments
        
    Returns:
        DateTimeAdapter configured for event scheduling
    """
    # Events are typically in the future
    min_date = datetime.now().date()
    
    return DateTimeAdapter(
        message=message,
        mode='datetime',
        timezone_aware=timezone_aware,
        min_date=min_date,
        allow_relative=True,
        style=style,
        **kwargs
    )


def create_log_timestamp_picker(
    message: str = "Select log timestamp:",
    timezone_aware: bool = True,
    style: str = 'professional_blue',
    **kwargs
) -> DateTimeAdapter:
    """Create a DateTimeAdapter for log timestamp selection.
    
    Args:
        message: Prompt message
        timezone_aware: Whether to handle timezones
        style: Theme name for styling
        **kwargs: Additional arguments
        
    Returns:
        DateTimeAdapter configured for log timestamps
    """
    # Logs are typically in the past, within reasonable range
    today = datetime.now().date()
    min_date = today - timedelta(days=365)  # 1 year back
    max_date = today + timedelta(days=1)    # Allow tomorrow for different timezones
    
    return DateTimeAdapter(
        message=message,
        mode='datetime',
        timezone_aware=timezone_aware,
        min_date=min_date,
        max_date=max_date,
        format_str='%Y-%m-%d %H:%M:%S',
        style=style,
        **kwargs
    )