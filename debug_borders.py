#!/usr/bin/env python3
"""Border alignment analysis"""

examples = [
    "┌─ 🏠 Personal Information ─┐",
    "│                          │", 
    "└──────────────────────────┘",
    "",
    "┌─ 🎯 Goals & Targets ─┐",
    "│                     │",
    "└─────────────────────┘"
]

print("Border alignment analysis:")
print("=" * 50)

for i, line in enumerate(examples):
    if line:
        print(f"Line {i+1}: Length {len(line)} chars")
        print(f"  Content: '{line}'")
        
        if line.startswith('┌'):
            print("  TOP BORDER")
        elif line.startswith('│'):
            inner_content = line[1:-1]  # Remove side borders
            print(f"  SIDE BORDER - Inner: '{inner_content}' ({len(inner_content)} chars)")
        elif line.startswith('└'):
            inner_content = line[1:-1]  # Remove corners
            print(f"  BOTTOM BORDER - Inner: '{inner_content}' ({len(inner_content)} chars)")
        print()