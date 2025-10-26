import importlib
import traceback

try:
    m = importlib.import_module("questionary_extended")
    print("Imported", m)
    print("Has Page:", hasattr(m, "Page"))
    print("All caps:", [n for n in dir(m) if n[0].isupper()])
except Exception:
    traceback.print_exc()
