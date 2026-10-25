# Comprehensive Python Error Handling and Common Errors Guide

Source: https://docs.python.org/3/tutorial/errors.html
Source: https://docs.python.org/3/library/exceptions.html

## Understanding Errors in Python: Syntax Errors vs Exceptions

Python differentiates between two primary kinds of errors:

1. **Syntax Errors (Parsing Errors)**: Detected by the Python parser before code execution begins. They occur when code violates Python grammar rules (e.g., missing colons, unbalanced parentheses, invalid keywords).
2. **Exceptions (Runtime Errors)**: Occur while the program is running, even if the syntax is valid. When an unhandled exception occurs, Python halts execution and prints a traceback detailing where and why the error happened.

```python
# Syntax Error: Detected at parse time before any line executes
# if x == 10  <-- SyntaxError: expected ':'

# Exception: Syntax is valid, but fails at runtime
x = 10
# y = x / 0   <-- ZeroDivisionError: division by zero
```

## The Complete Built-in Exception Hierarchy

Every built-in exception in Python derives from `BaseException`. Normal application errors inherit from `Exception`.

```text
BaseException
├── BaseExceptionGroup
├── GeneratorExit
├── KeyboardInterrupt (Ctrl+C termination)
├── SystemExit (sys.exit())
└── Exception (Base for all user and non-fatal runtime errors)
    ├── ArithmeticError
    │   ├── FloatingPointError
    │   ├── OverflowError (number exceeds hardware limit)
    │   └── ZeroDivisionError (division or modulo by zero)
    ├── AssertionError (assert statement fails)
    ├── AttributeError (attribute or method does not exist)
    ├── BufferError
    ├── EOFError (input() hits unexpected end of stream)
    ├── ImportError
    │   └── ModuleNotFoundError (import statement fails)
    ├── LookupError
    │   ├── IndexError (sequence index out of range)
    │   └── KeyError (mapping key not found)
    ├── MemoryError (out of memory)
    ├── NameError
    │   └── UnboundLocalError (local variable referenced before assignment)
    ├── OSError (operating system error)
    │   ├── FileExistsError
    │   ├── FileNotFoundError (file or directory does not exist)
    │   ├── InterruptedError
    │   ├── IsADirectoryError
    │   ├── NotADirectoryError
    │   ├── PermissionError (access denied)
    │   └── TimeoutError
    ├── ReferenceError (weak reference target is dead)
    ├── RuntimeError
    │   ├── NotImplementedError
    │   └── RecursionError (maximum recursion depth exceeded)
    ├── StopAsyncIteration
    ├── StopIteration (iterator is exhausted)
    ├── SyntaxError
    │   └── IndentationError
    │       └── TabError (inconsistent mixing of tabs and spaces)
    ├── SystemError
    ├── TypeError (operation applied to inappropriate type)
    ├── ValueError (operation received correct type but inappropriate value)
    │   └── UnicodeError
    └── Warning
```

## Common Python Errors, Causes, and Solutions

### 1. TypeError

**Cause**: An operation or function is applied to an object of inappropriate type.

**Common Scenarios**:
- Concatenating string with integer: `'Score: ' + 10`
- Subscripting an object that does not support indexing: `None[0]` or `42['key']`
- Calling a non-callable object: `data = 10; data()`
- Passing wrong number of arguments to a function: `func() takes 2 positional arguments but 3 were given`

**Fix & Example**:
```python
# Bad: TypeError: can only concatenate str (not "int") to str
# message = "Count: " + 5

# Good: Convert to string or use f-string
count = 5
message = f"Count: {count}"

# Handling NoneType TypeError defensively
def get_first_item(items: list | None) -> str | None:
    if items is None:
        return None
    return items[0] if items else None
```

### 2. ValueError

**Cause**: A function receives an argument that has the right type but an inappropriate value.

**Common Scenarios**:
- Converting invalid string to number: `int("abc")` or `float("xyz")`
- Unpacking mismatch: `a, b = [1, 2, 3]` (too many values to unpack) or `a, b, c = [1, 2]` (not enough values)
- Invalid list method argument: `my_list.remove("missing_item")`

**Fix & Example**:
```python
# Handling invalid integer input
user_input = "not_a_number"
try:
    number = int(user_input)
except ValueError:
    number = 0

# Safe tuple unpacking using asterisk (*)
data = [1, 2, 3, 4, 5]
first, *middle, last = data  # first=1, middle=[2,3,4], last=5
```

### 3. AttributeError

**Cause**: Trying to access an attribute or method that does not exist on an object.

**Common Scenarios**:
- Accessing attribute on `None`: `'NoneType' object has no attribute 'group'` (e.g., regex `re.search` failed to match)
- Misspelled method name: `my_list.add(5)` instead of `my_list.append(5)`
- Using string methods on bytes or dictionary methods on lists

**Fix & Example**:
```python
import re

text = "User ID: 1042"
match = re.search(r"User ID:\s*(\d+)", text)

# Bad: match.group(1) directly without checking can cause AttributeError if no match
# Good: Check if match is not None
if match is not None:
    user_id = match.group(1)
else:
    user_id = "default"

# Using getattr() with fallback default
obj = object()
value = getattr(obj, "custom_field", "fallback_default")
```

### 4. KeyError vs IndexError

**Cause**:
- `KeyError`: Looking up a non-existent key in a dictionary or mapping.
- `IndexError`: Accessing a sequence (list, tuple, string) with an index outside its valid bounds.

**Fix & Example**:
```python
# KeyError Prevention:
user_data = {"name": "Alice"}

# 1. Using .get() with a default value
role = user_data.get("role", "viewer")

# 2. Using setdefault()
user_data.setdefault("login_count", 0)

# 3. Using collections.defaultdict
from collections import defaultdict
counts = defaultdict(int)
counts["python"] += 1  # No KeyError, defaults to 0

# IndexError Prevention:
items = ["apple", "banana"]

# Check length before indexing:
index = 5
if 0 <= index < len(items):
    item = items[index]
else:
    item = "default"

# Or use slicing (slices never raise IndexError):
sub = items[5:10]  # returns empty list [] instead of raising IndexError
```

### 5. NameError and UnboundLocalError

**Cause**:
- `NameError`: An identifier (variable or function name) is referenced before it has been defined in local, enclosing, global, or built-in scope.
- `UnboundLocalError`: A local variable is assigned inside a function, which causes Python to treat the variable as local for the entire function, but it is read before the assignment line.

**Fix & Example**:
```python
# UnboundLocalError Scenario:
count = 0

def increment_bad():
    # count += 1  # Raises UnboundLocalError because 'count' is local (due to assignment) but read first
    pass

def increment_good():
    global count
    count += 1
    return count

# For nested closures, use 'nonlocal':
def make_counter():
    val = 0
    def tick():
        nonlocal val
        val += 1
        return val
    return tick
```

### 6. FileNotFoundError, PermissionError, and OSError

**Cause**: File system issues when opening, reading, or writing files.

**Fix & Example**:
```python
from pathlib import Path

path = Path("config/settings.json")

# Best practice: use pathlib with try/except
try:
    content = path.read_text(encoding="utf-8")
except FileNotFoundError:
    print(f"File {path} does not exist.")
    content = "{}"
except PermissionError:
    print(f"Insufficient permissions to read {path}.")
except OSError as e:
    print(f"OS file system error: {e}")
```

### 7. RecursionError and Infinite Loops

**Cause**: A recursive function calls itself without hitting a valid base case, exceeding `sys.getrecursionlimit()` (default 1,000).

**Fix & Example**:
```python
# Bad: No base case
def countdown_bad(n):
    return countdown_bad(n - 1)  # RecursionError: maximum recursion depth exceeded

# Good: Clear base case
def countdown_good(n):
    if n <= 0:
        return 0
    return n + countdown_good(n - 1)
```

## The try / except / else / finally Lifecycle

Python provides a 4-part exception control structure:

- `try`: Code that might raise an exception.
- `except`: Handles one or more specific exception types.
- `else`: Executes **only** if the `try` block completed without raising any exception.
- `finally`: Executes **always**, regardless of whether an exception occurred, was caught, or was re-raised. Ideal for resource cleanup.

```python
def process_data_file(filepath: str) -> bool:
    file_handle = None
    try:
        file_handle = open(filepath, "r", encoding="utf-8")
        data = file_handle.read()
        parsed = int(data.strip())
    except FileNotFoundError:
        print(f"Error: {filepath} was not found.")
        return False
    except ValueError as e:
        print(f"Error: Invalid content in {filepath}: {e}")
        return False
    else:
        # Runs ONLY when no exceptions occurred in try
        print(f"Success! Processed value: {parsed}")
        return True
    finally:
        # ALWAYS runs, ensuring cleanup happens
        if file_handle is not None and not file_handle.closed:
            file_handle.close()
            print("File handle safely closed.")
```

## Exception Chaining and `raise ... from`

Exception chaining connects an original error to a higher-level exception, preserving the root-cause traceback.

### Explicit Chaining (`from exc`)
```python
class DatabaseError(Exception):
    """Raised when database query fails."""

def fetch_user_record(user_id: int):
    try:
        # Low-level connection attempt
        raise ConnectionRefusedError("Database port 5432 unreachable")
    except ConnectionRefusedError as exc:
        # Chain the low-level exception as the cause
        raise DatabaseError(f"Could not fetch user {user_id}") from exc
```

### Suppressing Context (`from None`)
When a low-level error is an implementation detail you want to hide:
```python
def parse_positive_number(text: str) -> int:
    try:
        val = int(text)
        if val <= 0:
            raise ValueError("Must be positive")
        return val
    except ValueError:
        # Suppresses the original traceback to show only the clean error
        raise ValueError(f"Invalid positive integer: {text!r}") from None
```

## Modern Exception Groups and `except*` (Python 3.11+)

Python 3.11 introduced `ExceptionGroup` and the `except*` syntax for concurrent and batch operations where multiple exceptions can occur simultaneously (such as in `asyncio.TaskGroup`).

```python
# Raising an ExceptionGroup
def run_concurrent_tasks():
    raise ExceptionGroup(
        "Batch job failures",
        [
            ValueError("Bad parameter value"),
            TypeError("Wrong argument type"),
            FileNotFoundError("Config file missing"),
        ]
    )

# Catching with except* splits the group by type
try:
    run_concurrent_tasks()
except* ValueError as eg:
    print(f"Handled ValueErrors: {eg.exceptions}")
except* (FileNotFoundError, OSError) as eg:
    print(f"Handled File/OS errors: {eg.exceptions}")
except* Exception as eg:
    print(f"Handled other errors: {eg.exceptions}")
```

## Creating Custom Exception Classes

Best practices for writing custom exceptions:
1. Always inherit from `Exception` (never `BaseException`).
2. Provide a descriptive default message and support custom error attributes.
3. Organize related exceptions into a domain-specific hierarchy.

```python
class AppError(Exception):
    """Base exception for all application errors."""

class ValidationError(AppError):
    """Raised when input validation fails."""
    def __init__(self, message: str, field: str, error_code: str = "INVALID"):
        super().__init__(f"[{field}] {message} (Code: {error_code})")
        self.field = field
        self.error_code = error_code

class AuthenticationError(AppError):
    """Raised when authentication credentials fail."""

# Usage
def validate_username(username: str):
    if len(username) < 3:
        raise ValidationError("Username must be at least 3 characters", field="username", error_code="TOO_SHORT")
```

## EAFP vs LBYL: Pythonic Exception Handling

Python strongly encourages **EAFP** (*Easier to Ask for Forgiveness than Permission*) over **LBYL** (*Look Before You Leap*).

```python
# LBYL (Look Before You Leap):
# Checking keys or existence in advance (prone to race conditions in concurrent code)
if "key" in data and isinstance(data["key"], int):
    val = data["key"]
else:
    val = 0

# EAFP (Easier to Ask for Forgiveness than Permission) — Pythonic:
try:
    val = int(data["key"])
except (KeyError, TypeError, ValueError):
    val = 0
```

## Debugging and Traceback Inspection

### 1. Built-in `breakpoint()`
Insert `breakpoint()` directly into code to drop into Python's interactive `pdb` debugger:
```python
def compute_ratio(a: int, b: int) -> float:
    # breakpoint()  # Pauses execution here; use 'n' (next), 's' (step), 'c' (continue), 'p variable'
    return a / b
```

### 2. Logging Tracebacks
Never swallow exceptions silently. Log them with full traceback details:
```python
import logging

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

try:
    result = 10 / 0
except ZeroDivisionError:
    # logger.exception automatically logs traceback information
    logger.exception("An error occurred during calculation")
```

### 3. Reading Python Tracebacks
Tracebacks are read **from bottom to top**:
- The **last line** tells you the exception type and specific error description.
- The lines directly above show the call stack, with the most recent frame at the bottom pointing to the exact file and line number where the exception occurred.
