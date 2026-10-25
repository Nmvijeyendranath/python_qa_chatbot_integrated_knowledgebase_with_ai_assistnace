# Exceptions, Error Handling, and Debugging

Source: https://docs.python.org/3/tutorial/errors.html

## Exception Hierarchy

Python exceptions form a class hierarchy. All exceptions inherit from `BaseException`; most inherit from `Exception`.

```
BaseException
├── SystemExit
├── KeyboardInterrupt
├── GeneratorExit
└── Exception
    ├── ArithmeticError
    │   ├── ZeroDivisionError
    │   ├── OverflowError
    │   └── FloatingPointError
    ├── AttributeError
    ├── EOFError
    ├── ImportError
    │   └── ModuleNotFoundError
    ├── LookupError
    │   ├── IndexError
    │   └── KeyError
    ├── NameError
    │   └── UnboundLocalError
    ├── OSError
    │   ├── FileNotFoundError
    │   ├── PermissionError
    │   └── TimeoutError
    ├── RuntimeError
    │   └── RecursionError
    ├── StopIteration
    ├── TypeError
    ├── ValueError
    │   └── UnicodeDecodeError
    └── Warning
```

## try / except / else / finally

```python
try:
    result = 10 / 0
except ZeroDivisionError as e:
    print(f"Error: {e}")    # Error: division by zero
else:
    print("No exception occurred")   # runs only if no exception
finally:
    print("Always runs (cleanup)")   # always runs
```

### Catching Multiple Exceptions

```python
def parse_int(s: str) -> int:
    try:
        return int(s)
    except (ValueError, TypeError) as e:
        print(f"Cannot convert {s!r}: {e}")
        return 0

# Specific to general — order matters
try:
    data = {}
    value = data["key"]
except KeyError:
    print("Key missing")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Catching All Exceptions

```python
try:
    risky_operation()
except Exception as e:
    # Catches all non-system-exiting exceptions
    print(f"Error: {e}")
    raise   # re-raises the original exception
```

Do not use `except:` (bare except) — it catches `SystemExit` and `KeyboardInterrupt`, making it hard to stop the program.

## raise

```python
def set_age(age: int):
    if not isinstance(age, int):
        raise TypeError(f"age must be int, got {type(age).__name__}")
    if age < 0 or age > 150:
        raise ValueError(f"age must be 0–150, got {age}")
    return age

# Re-raise with additional context (exception chaining)
try:
    value = int("abc")
except ValueError as e:
    raise RuntimeError("Failed to parse configuration") from e
```

## Custom Exceptions

```python
class AppError(Exception):
    """Base exception for this application."""

class ValidationError(AppError):
    def __init__(self, field: str, message: str):
        super().__init__(f"Validation failed for '{field}': {message}")
        self.field   = field
        self.message = message

class DatabaseError(AppError):
    pass


try:
    raise ValidationError("email", "must contain @")
except ValidationError as e:
    print(e)          # Validation failed for 'email': must contain @
    print(e.field)    # email
```

## Common Built-in Exceptions

| Exception              | When it Occurs                                   |
|------------------------|--------------------------------------------------|
| `SyntaxError`          | Invalid Python syntax (at parse time)            |
| `IndentationError`     | Wrong indentation                                |
| `TypeError`            | Wrong type for operation                         |
| `ValueError`           | Right type, wrong value (e.g., `int("abc")`)     |
| `NameError`            | Variable or name not defined                     |
| `UnboundLocalError`    | Local variable referenced before assignment      |
| `AttributeError`       | Object has no such attribute                     |
| `IndexError`           | Sequence index out of range                      |
| `KeyError`             | Dict key not found                               |
| `FileNotFoundError`    | File or directory does not exist                 |
| `ImportError`          | Module cannot be imported                        |
| `ModuleNotFoundError`  | Module does not exist                            |
| `ZeroDivisionError`    | Division or modulo by zero                       |
| `RecursionError`       | Max recursion depth exceeded                     |
| `StopIteration`        | Iterator exhausted                               |
| `MemoryError`          | Out of memory                                    |
| `OverflowError`        | Numeric result too large (float)                 |

## Exception Examples and Fixes

```python
# NameError
print(undefined_var)   # NameError: name 'undefined_var' is not defined
# Fix: define the variable first

# TypeError
"2" + 2   # TypeError: can only concatenate str (not "int") to str
# Fix: int("2") + 2  or  "2" + str(2)

# IndexError
lst = [1, 2, 3]
lst[10]   # IndexError: list index out of range
# Fix: check len(lst) > 10, or use lst[-1] for last element

# KeyError
d = {"a": 1}
d["b"]   # KeyError: 'b'
# Fix: d.get("b", default)  or  "b" in d

# AttributeError
n = 42
n.upper()   # AttributeError: 'int' object has no attribute 'upper'
# Fix: str(n).upper()

# ValueError
int("3.14")  # ValueError: invalid literal for int() with base 10: '3.14'
# Fix: int(float("3.14"))

# FileNotFoundError
open("nonexistent.txt")   # FileNotFoundError: [Errno 2] No such file or directory
# Fix: check os.path.exists(path) first, or use try/except

# RecursionError
def f(): return f()
f()   # RecursionError: maximum recursion depth exceeded
# Fix: add a base case, or convert recursion to iteration
```

## Debugging Techniques

### print Debugging

```python
def buggy(x, y):
    print(f"DEBUG: x={x!r}, y={y!r}")   # temporary print
    return x / y
```

### assert Statements

```python
def divide(a, b):
    assert b != 0, f"b must not be zero; got {b}"
    return a / b

# Run with: python -O script.py  → disables asserts
```

### pdb — Python Debugger

```python
import pdb

def compute(x):
    pdb.set_trace()   # or breakpoint() in Python 3.7+
    result = x * 2
    return result

# pdb commands:
# n (next), s (step into), c (continue), q (quit)
# p expr (print expression), l (list source), w (where stack)
```

### logging Module

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s"
)
logger = logging.getLogger(__name__)

logger.debug("Debug information")
logger.info("Informational message")
logger.warning("Warning: something unexpected")
logger.error("Error occurred")
logger.exception("Error with traceback", exc_info=True)
```

### traceback Module

```python
import traceback

try:
    1 / 0
except Exception:
    traceback.print_exc()   # prints full traceback
    tb_str = traceback.format_exc()   # as string
```

## Context Managers for Safe Resource Handling

```python
# Files
with open("data.txt", "r") as f:
    content = f.read()
# file automatically closed even if an exception occurs

# Multiple context managers
with open("src.txt") as src, open("dst.txt", "w") as dst:
    dst.write(src.read())

# contextlib.suppress — silently ignore specified exceptions
from contextlib import suppress
with suppress(FileNotFoundError):
    os.remove("maybe_exists.txt")
```

## Frequently Asked Questions

**Q: What is the difference between `raise` and `raise e`?**
Bare `raise` re-raises the current exception with its original traceback. `raise e` creates a new exception with a shortened traceback, losing the original chain (unless you use `raise new from e`).

**Q: When should I use custom exceptions?**
When your library/application has domain-specific failure conditions that callers need to handle differently. Always derive from `Exception` (or a suitable subclass), not from `BaseException` directly.

**Q: What does `except Exception as e` capture that `except:` does not?**
Both capture most exceptions. `except:` additionally captures `SystemExit`, `KeyboardInterrupt`, and `GeneratorExit`, which typically should not be silenced. Always prefer `except Exception` or more specific types.

**Q: What happens if an exception occurs inside `finally`?**
It replaces the original exception. Be cautious with code that can raise inside `finally`. Use `suppress()` or explicit try/except inside finally for cleanup code that might fail.
