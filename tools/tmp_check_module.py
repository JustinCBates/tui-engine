import importlib

m1 = importlib.import_module("questionary_extended.core.component")
print("m1 module:", m1)
print("m1 has questionary:", hasattr(m1, "questionary"))
try:
    m2 = importlib.import_module("src.questionary_extended.core.component")
    print("m2 module:", m2)
    print("m2 has questionary:", hasattr(m2, "questionary"))
except Exception as e:
    print("loading src.* path failed:", e)
