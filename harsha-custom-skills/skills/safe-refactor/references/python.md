# Python Refactoring Patterns

Patterns specific to Python including Django, Flask, and FastAPI.

## Table of Contents

1. [Modernization Patterns](#modernization)
2. [Type Safety Patterns](#type-safety)
3. [Structural Patterns](#structural)
4. [Testing Patterns](#testing)
5. [Automation Tools](#tools)

---

## Modernization

### 1. dict → dataclasses
**Risk: Low**
```python
# Before
user = {'name': 'Alice', 'age': 30, 'email': 'alice@example.com'}

# After
from dataclasses import dataclass

@dataclass
class User:
    name: str
    age: int
    email: str
```
- Use `frozen=True` for immutability; `slots=True` for memory efficiency (3.10+)
- Safety: Check hashability if used as dict keys; verify JSON serialization still works
- Anti-pattern: Don't use for data that's naturally dynamic/schemaless

### 2. os.path → pathlib
**Risk: Very Low**
```python
# Before
import os
path = os.path.join(os.path.expanduser('~'), 'documents', 'file.txt')
exists = os.path.exists(path)

# After
from pathlib import Path
path = Path.home() / 'documents' / 'file.txt'
exists = path.exists()
```
- Safety: Verify on both Unix and Windows if cross-platform

### 3. % / .format() → f-strings
**Risk: Low** (requires Python 3.6+)
```python
# Before: "Hello %s, age %d" % (name, age)
# Before: "Hello {}, age {}".format(name, age)
# After:  f"Hello {name}, age {age}"
```
- Safety: Watch for format spec edge cases (alignment, precision)
- Watch: Logging uses lazy formatting: `logger.info("x=%s", x)` — don't convert these

### 4. bare except → specific exceptions
**Risk: Low**
```python
# Before
try:
    risky_operation()
except:
    pass

# After
try:
    risky_operation()
except (ValueError, IOError) as e:
    logger.warning("Operation failed: %s", e)
```
- Critical: `except:` catches SystemExit, KeyboardInterrupt — always be specific
- Safety: Audit what exceptions the code actually raises

### 5. Manual file handling → context managers
**Risk: Very Low**
```python
# Before
f = open('file.txt')
data = f.read()
f.close()

# After
with open('file.txt') as f:
    data = f.read()
```
- Safety: Guaranteed cleanup even on exceptions

### 6. print debugging → logging
**Risk: Low**
```python
# Before: print(f"DEBUG: user={user}")
# After:
import logging
logger = logging.getLogger(__name__)
logger.debug("user=%s", user)
```
- Safety: Don't convert print statements that are intended user output
- Watch: Use `%s` formatting in logging (lazy evaluation), NOT f-strings

---

## Type Safety

### 7. Add Type Annotations
**Risk: Medium** (gradual adoption recommended)
```python
# Before
def calculate_total(items, tax_rate):
    return sum(i['price'] for i in items) * (1 + tax_rate)

# After
def calculate_total(items: list[dict[str, float]], tax_rate: float) -> float:
    return sum(i['price'] for i in items) * (1 + tax_rate)
```
- Strategy: Start with public API boundaries, then internals
- Use `from __future__ import annotations` for forward references (3.7+)
- Use `list[int]` instead of `List[int]` (3.9+)
- Validate with mypy: `mypy --strict [path]`

### 8. Class with __init__ + one method → function
**Risk: Low**
```python
# Before
class DataProcessor:
    def __init__(self, data):
        self.data = data
    def process(self):
        return [x * 2 for x in self.data]

# After
def process_data(data: list[int]) -> list[int]:
    return [x * 2 for x in data]
```
- When: No state persistence needed; no inheritance; single responsibility
- Safety: Verify no code instantiates and stores the object

---

## Structural

### 9. Global State → Dependency Injection
**Risk: Medium**
```python
# Before
config = load_config()  # global
def process():
    return config.timeout  # hidden dependency

# After
def process(config: Config) -> int:
    return config.timeout
```
- Safety: Audit all call sites; ensure initialization order is correct
- Frameworks: Django settings are a special case — don't inject those

### 10. Nested Functions → Modules
**Risk: Low**
- When functions grow beyond 3 levels of nesting, extract inner functions
- Move utility functions to separate modules for reusability

### 11. Star Imports → Explicit Imports
**Risk: Low**
```python
# Before: from module import *
# After:  from module import SpecificClass, specific_function
```
- Safety: Run tests; some star imports bring in needed names implicitly

### 12. requests → httpx (for async)
**Risk: Medium**
```python
# Before: import requests; response = requests.get(url)
# After:  async with httpx.AsyncClient() as client: response = await client.get(url)
```
- Only when: Project needs async capabilities
- Safety: httpx has sync mode too — can migrate incrementally

---

## Testing

### 13. unittest → pytest
**Risk: Low-Medium**
```python
# Before
class TestCalc(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(1, 2), 3)

# After
def test_add():
    assert add(1, 2) == 3
```
- pytest auto-discovers unittest classes, so migration can be gradual
- Replace setUp/tearDown with fixtures
- Safety: Run full suite before and after

---

## Tools

| Tool | Purpose | Command |
|------|---------|---------|
| pyupgrade | Syntax modernization | `pyupgrade --py310-plus *.py` |
| ruff | Fast linting + fixing | `ruff check --fix .` |
| black | Code formatting | `black .` |
| isort | Import sorting | `isort .` |
| mypy | Type checking | `mypy --strict .` |
| radon | Complexity metrics | `radon cc . -s -n C` |
| vulture | Dead code detection | `vulture .` |

Recommended order: `ruff check --fix` → `black` → `isort` → `mypy`
