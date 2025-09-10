import sys
import os

print("Python:", sys.version)
print("Executable:", sys.executable)
print("Venv active:", os.environ.get('VIRTUAL_ENV', ''))

# Ensure we are not importing from global site-packages
print("sys.path (first 5):")
for p in sys.path[:5]:
    print(" -", p)

# Quick imports
try:
    import pydantic
    print("pydantic:", pydantic.__version__)
except Exception as e:
    print("pydantic import FAILED:", e)

try:
    import swisseph as swe
    print("pyswisseph: OK")
except Exception as e:
    print("pyswisseph import FAILED:", e)

# Probe fastapi just in case
try:
    import fastapi
    print("fastapi:", fastapi.__version__)
except Exception as e:
    print("fastapi import FAILED:", e)
