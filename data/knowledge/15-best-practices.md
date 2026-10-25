# Python Best Practices, PEP 8, and Common Errors

Source: https://peps.python.org/pep-0008/

## PEP 8 — Python Style Guide

PEP 8 is the official style guide for Python code. Following it makes code more readable and maintainable.

### Indentation

```python
# GOOD: 4 spaces per level (never tabs)
def function():
    if True:
        do_something()
        for i in range(10):
            process(i)

# BAD: 2 spaces or inconsistent
def function():
  if True:
    do_something()
```

### Line Length

- Maximum **79 characters** per line (72 for docstrings/comments)
- Use implicit continuation inside brackets, or backslash for long expressions

```python
# Implicit continuation — preferred
result = (first_value
          + second_value
          + third_value)

# Long function signature
def long_function_name(
    arg1,
    arg2,
    arg3,
    *args,
    keyword_arg=None,
):
    pass

# Long string
message = (
    "This is a very long string that is split "
    "across multiple lines using implicit "
    "concatenation."
)
```

### Naming Conventions

| Identifier      | Convention          | Example              |
|-----------------|---------------------|----------------------|
| Variable        | `snake_case`        | `user_count`         |
| Function        | `snake_case`        | `get_user_name()`    |
| Constant        | `UPPER_SNAKE_CASE`  | `MAX_CONNECTIONS`    |
| Class           | `PascalCase`        | `UserAccount`        |
| Private attr    | `_single_leading`   | `_internal_value`    |
| Name mangled    | `__double_leading`  | `__private_attr`     |
| Module          | `snake_case`        | `data_loader.py`     |
| Package         | `lowercase`         | `mypackage/`         |

```python
# GOOD
MAX_SIZE = 100
user_name = "Alice"

def calculate_area(radius: float) -> float:
    return 3.14159 * radius ** 2

class UserProfile:
    def __init__(self, name: str):
        self.name = name
        self._cached_data = {}   # private convention

# BAD
MaxSize = 100           # looks like class name
userName = "Alice"      # camelCase — not Pythonic
```

### Blank Lines

- 2 blank lines around top-level functions and classes
- 1 blank line between methods inside a class
- Sparingly inside functions to group logical sections

### Imports

```python
# Standard library first, then third-party, then local — each group separated
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from mypackage import utilities
from mypackage.models import User

# AVOID: wildcard imports
from module import *   # pollutes namespace

# AVOID: multiple imports on one line
import os, sys   # bad style (acceptable but not recommended)
```

### Whitespace in Expressions

```python
# GOOD
x = 5
d = {"key": value}
lst[1:3]
func(arg, kwarg=value)
x == y

# BAD
x=5
d = {"key" : value}
lst[ 1 : 3 ]
func(arg ,kwarg = value)
x  ==  y
```

### Comments and Docstrings

```python
# Comments explain WHY, not WHAT
# Correct: using binary instead of hex for readability
flags = 0b00001111

# Avoid obvious comments:
x = x + 1  # increment x by 1  ← useless

# Block comments — full sentence, one space after #
# Process each record in the batch. Skip records that are already
# marked as completed.

# Inline comments — sparingly, two spaces before #
result = compute(x)  # expensive, cache if possible

# Docstrings for all public functions, classes, and modules
def compute_mean(values: list[float]) -> float:
    """Return the arithmetic mean of a non-empty list of floats.

    Args:
        values: A non-empty list of numeric values.

    Returns:
        The mean value as a float.

    Raises:
        ValueError: If values is empty.
    """
    if not values:
        raise ValueError("values must not be empty")
    return sum(values) / len(values)
```

## Code Quality Tools

```bash
# Linting and style
pip install ruff        # fast linter + formatter (replaces flake8, isort)
ruff check src/
ruff format src/

# Static type checking
pip install mypy
mypy src/

# Security
pip install bandit
bandit -r src/

# Code coverage
pip install pytest-cov
pytest --cov=src
```

## Common Python Antipatterns and Fixes

### Antipattern 1: Bare `except`

```python
# BAD
try:
    do_something()
except:
    pass   # silences everything including KeyboardInterrupt

# GOOD
try:
    do_something()
except Exception as e:
    logger.error("Unexpected error: %s", e)
```

### Antipattern 2: Mutable Default Arguments

```python
# BAD
def add_item(item, lst=[]):   # same list across all calls!
    lst.append(item)
    return lst

# GOOD
def add_item(item, lst=None):
    if lst is None:
        lst = []
    lst.append(item)
    return lst
```

### Antipattern 3: String Concatenation in Loops

```python
# BAD — O(n²)
result = ""
for word in words:
    result += word + " "

# GOOD — O(n)
result = " ".join(words)
```

### Antipattern 4: `range(len(x))` Iteration

```python
# BAD — C-style loop
for i in range(len(names)):
    print(names[i])

# GOOD — Pythonic
for name in names:
    print(name)

# GOOD — when you need index
for i, name in enumerate(names):
    print(i, name)
```

### Antipattern 5: Not Using Context Managers

```python
# BAD — file may not be closed on exception
f = open("data.txt")
data = f.read()
f.close()

# GOOD
with open("data.txt") as f:
    data = f.read()
```

### Antipattern 6: Type Checking with `type()` Instead of `isinstance()`

```python
# BAD — doesn't handle subclasses
if type(x) == int:
    ...

# GOOD
if isinstance(x, int):
    ...

if isinstance(x, (int, float)):   # check multiple types
    ...
```

### Antipattern 7: Using `==` Instead of `is` for `None`

```python
# BAD
if x == None:   # triggers __eq__, may have false positives

# GOOD
if x is None:   # identity check — always correct
if x is not None:
```

### Antipattern 8: Catching Too Broad an Exception

```python
# BAD — hides programming errors
try:
    process(data)
except Exception:
    print("Something went wrong")

# GOOD — be specific
try:
    process(data)
except ValueError as e:
    print(f"Invalid input: {e}")
except IOError as e:
    print(f"File error: {e}")
```

## Python Coding Best Practices

1. **Prefer readability over cleverness** — code is read far more often than it is written.
2. **Write small, focused functions** — a function should do one thing.
3. **Use meaningful names** — `process_payment` not `pp`, `user_age` not `ua`.
4. **Fail early and loudly** — validate inputs at the start of a function.
5. **Avoid premature optimisation** — profile first, optimise where needed.
6. **Write tests** — untested code is legacy code.
7. **Use type hints** — they document intent and enable static analysis.
8. **Prefer composition over inheritance** — compose simple objects instead of deep hierarchies.
9. **Don't repeat yourself (DRY)** — abstract repeated logic.
10. **Keep imports at the top of the module**.

## Frequently Asked Questions

**Q: What does `if __name__ == "__main__":` do?**
It guards module-level code from running when the module is imported. Code inside this block only executes when the file is run directly with `python script.py`.

**Q: How do I make a variable "private" in Python?**
Python has no true private access. By convention, prefix with a single underscore (`_name`) to signal "internal use only". Double underscore (`__name`) enables name mangling, making it harder (not impossible) to access from outside the class.

**Q: What is `*args` and `**kwargs` really?**
`*args` collects extra positional arguments into a tuple. `**kwargs` collects extra keyword arguments into a dict. They are useful for forwarding arguments and writing flexible decorators.

**Q: When should I use `map()` and `filter()` instead of comprehensions?**
Comprehensions are generally more readable and Pythonic. Use `map()`/`filter()` when you already have a named function to pass (avoids a redundant lambda). For new code, prefer comprehensions.
