# Card Shuffling Navigation Demo

This demo showcases a card-based navigation interface where users can navigate between cards using actual Page Up/Down keys with automatic screen clearing and reprinting.

## Features

- **Direct Key Interception**: Captures Page Up/Down keys directly without prompting
- **Screen Management**: Automatically clears screen and reprints header + current card
- **Card Navigation**: 5 cards with descriptive content, only one visible at a time
- **Wrap-around Navigation**: Moving past the last card goes to first, and vice versa
- **Integration Ready**: Built on TUI engine architecture for easy extension

## Files

### `pagekey_demo.py`
Simple standalone demo demonstrating pure Page Up/Down key navigation:
- Direct key capture using `termios` and `tty`
- Screen clearing and reprinting on each navigation event
- No navigation prompts - just automatic card switching
- Clean minimal implementation for testing key capture

### `card_shuffling_demo.py`
Full-featured demo with TUI engine integration:
- Complete card shuffling navigation system
- Page Up/Down key interception with screen management
- Additional features: run cards, show results, number key shortcuts
- Integration with TUI engine architecture (Page, Assembly classes)

### `simple_demo.py`
Original prompt-based navigation demo:
- Menu-driven navigation system
- Uses text prompts for user input
- Demonstrates basic TUI engine usage patterns
- Good for understanding core concepts

## Usage

### Quick Test (Direct Key Navigation)
```bash
cd examples/card_shuffling_navigation
python3 pagekey_demo.py
```

**Controls:**
- **Page Up**: Previous card (with automatic screen clear/reprint)
- **Page Down**: Next card (with automatic screen clear/reprint) 
- **Q**: Quit demo

### Full Demo (Enhanced Features)
```bash
cd examples/card_shuffling_navigation
python3 card_shuffling_demo.py
```

**Controls:**
- **Page Up**: Previous card (automatic screen management)
- **Page Down**: Next card (automatic screen management)
- **R**: Run current card (collect integer input)
- **S**: Show all collected results
- **1-5**: Jump directly to specific card
- **Q**: Quit demo

### Legacy Demo (Prompt-based)
```bash
cd examples/card_shuffling_navigation
python3 simple_demo.py
```

## Technical Implementation

### Key Interception
The demos use `termios` and `tty` modules to capture raw keyboard input:

```python
def get_key():
    """Get a single keypress from the terminal."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
        ch = sys.stdin.read(1)
        
        # Handle escape sequences (Page Up/Down)
        if ch == '\x1b':  # ESC sequence
            ch += sys.stdin.read(2)
            # Page Up/Down have longer sequences
        
        return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
```

### Screen Management
Each navigation event triggers:
1. Screen clearing (`clear` command)
2. Header reprinting
3. Current card display
4. Navigation status update

### Key Codes
- **Page Up**: `\x1b[5~`
- **Page Down**: `\x1b[6~`
- **Regular keys**: Single character (e.g., 'q', 'r', '1'-'5')

## Card Themes

1. 🏠 **Personal Information** - Basic personal details
2. 💼 **Professional Details** - Work experience information  
3. 🎓 **Education Level** - Educational background
4. 🌟 **Preferences** - Personal preferences and ratings
5. 🎯 **Goals & Targets** - Objectives and targets

## Requirements

- Linux/Unix terminal environment
- Python 3.6+
- Terminal that supports Page Up/Down key detection
- `termios` and `tty` modules (standard on Unix systems)

## Troubleshooting

**Page Up/Down not working?**
- Ensure you're using a compatible terminal (most modern terminals support this)
- Try testing in different terminal applications
- Verify terminal sends proper escape sequences

**Demo not clearing screen?**
- Check if `clear` command is available on your system
- Modify `clear_screen()` function for Windows compatibility