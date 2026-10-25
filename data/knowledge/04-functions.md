# Functions — Arguments, Scope, Lambda, and Recursion

Source: https://docs.python.org/3/tutorial/controlflow.html#defining-functions

## Defining and Calling Functions

```python
def greet(name: str) -> str:
    """Return a greeting string."""
    return f"Hello, {name}!"

print(greet("Alice"))  # Hello, Alice!
```

A `def` statement creates a function object. Calling a function with `()` executes its body.

## Return Values

Functions without an explicit `return` return `None`. Functions can return multiple values as a tuple:

```python
def min_max(numbers):
    return min(numbers), max(numbers)

lo, hi = min_max([3, 1, 4, 1, 5, 9])
print(lo, hi)  # 1 9
```

## Argument Types

### Positional Arguments

```python
def add(a, b):
    return a + b

add(3, 5)   # 8
```

### Default Arguments

Defaults are evaluated once at function definition time:

```python
def repeat(s, n=3):
    return s * n

repeat("ha")     # "hahaha"
repeat("ha", 2)  # "haha"
```

**Common Mistake — Mutable Default Arguments:**

```python
# BUG: list is created once; all calls share it
def append_to(item, lst=[]):
    lst.append(item)
    return lst

append_to(1)  # [1]
append_to(2)  # [1, 2] — not [2]!

# Fix: use None as default
def append_to(item, lst=None):
    if lst is None:
        lst = []
    lst.append(item)
    return lst
```

### Keyword Arguments

```python
def connect(host, port=5432, ssl=True):
    print(f"Connecting to {host}:{port} ssl={ssl}")

connect("db.example.com")
connect("db.example.com", port=3306, ssl=False)
connect(port=3306, host="db.example.com")  # order doesn't matter
```

### *args — Variable Positional Arguments

```python
def total(*args):
    return sum(args)

total(1, 2, 3, 4)   # 10
total()              # 0
```

### **kwargs — Variable Keyword Arguments

```python
def display(**kwargs):
    for key, value in kwargs.items():
        print(f"{key}: {value}")

display(name="Alice", age=30, city="London")
```

### Combining Argument Types

Order must be: positional, *args, keyword-only, **kwargs.

```python
def complex_func(pos1, pos2, *args, kw_only, **kwargs):
    print(pos1, pos2, args, kw_only, kwargs)

complex_func(1, 2, 3, 4, kw_only="must", extra="value")
# 1 2 (3, 4) must {'extra': 'value'}
```

### Positional-only parameters (Python 3.8+)

Use `/` to mark positional-only:

```python
def magnitude(x, y, /, z=0):
    return (x**2 + y**2 + z**2) ** 0.5

magnitude(3, 4)       # OK
magnitude(x=3, y=4)   # TypeError — x,y are positional-only
```

## Scope — LEGB Rule

Python resolves names in order: **L**ocal → **E**nclosing → **G**lobal → **B**uilt-in.

```python
x = "global"

def outer():
    x = "enclosing"

    def inner():
        x = "local"
        print(x)   # local

    inner()
    print(x)       # enclosing

outer()
print(x)           # global
```

### global and nonlocal

```python
counter = 0

def increment():
    global counter   # modify global
    counter += 1

increment()
print(counter)  # 1

def make_counter():
    count = 0
    def increment():
        nonlocal count  # modify enclosing scope variable
        count += 1
        return count
    return increment

c = make_counter()
print(c())  # 1
print(c())  # 2
```

## Lambda Functions

Anonymous, single-expression functions:

```python
square = lambda x: x**2
add    = lambda x, y: x + y

print(square(5))   # 25
print(add(3, 4))   # 7

# Typical use: as a key for sorting
pairs = [(1, "b"), (2, "a"), (3, "c")]
pairs.sort(key=lambda pair: pair[1])
print(pairs)  # [(2, 'a'), (1, 'b'), (3, 'c')]
```

Lambdas cannot contain statements (assignment, loops, etc.). For anything complex, use a named function.

## Recursion

A function that calls itself. Must have a **base case** to avoid infinite recursion.

```python
def factorial(n: int) -> int:
    if n == 0:
        return 1           # base case
    return n * factorial(n - 1)   # recursive case

print(factorial(5))  # 120
```

```python
def fibonacci(n: int) -> int:
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

# Memoized version for performance
from functools import lru_cache

@lru_cache(maxsize=None)
def fib(n: int) -> int:
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)

print(fib(50))  # 12586269025
```

Python's default recursion limit is 1000 (`sys.getrecursionlimit()`). Deep recursion is better replaced with iteration in Python.

## Higher-Order Functions

Functions that accept or return other functions:

```python
def apply(func, value):
    return func(value)

print(apply(str.upper, "hello"))  # HELLO

# Built-in higher-order functions
nums = [1, 2, 3, 4, 5]
print(list(map(lambda x: x**2, nums)))       # [1, 4, 9, 16, 25]
print(list(filter(lambda x: x % 2, nums)))   # [1, 3, 5]

from functools import reduce
product = reduce(lambda a, b: a * b, nums)   # 120
```

## Type Hints

```python
def clamp(value: float, lo: float, hi: float) -> float:
    """Clamp value to [lo, hi]."""
    return max(lo, min(value, hi))

from typing import Optional, Union, Callable

def parse(text: str) -> Optional[int]:
    try:
        return int(text)
    except ValueError:
        return None
```

Type hints are not enforced at runtime but improve IDE support and `mypy` static analysis.

## Docstrings

```python
def divide(a: float, b: float) -> float:
    """
    Divide a by b.

    Args:
        a: Numerator.
        b: Denominator (must not be zero).

    Returns:
        The result of a / b.

    Raises:
        ZeroDivisionError: If b is zero.

    Examples:
        >>> divide(10, 2)
        5.0
    """
    if b == 0:
        raise ZeroDivisionError("b must not be zero")
    return a / b
```

## Common Errors

```python
# UnboundLocalError: local variable referenced before assignment
total = 0
def bad_increment():
    total += 1   # UnboundLocalError — total is treated as local
# Fix: declare global total, or pass total as argument and return it

# RecursionError: max depth exceeded
def count_down(n):
    return count_down(n - 1)   # no base case → RecursionError

# TypeError: missing required argument
def greet(name):
    return f"Hi, {name}"
greet()   # TypeError: greet() missing 1 required positional argument
```

## Frequently Asked Questions

**Q: What is the difference between a function and a method?**
A method is a function defined inside a class and typically takes `self` as the first argument. A regular function is defined at the module level.

**Q: Can Python functions return multiple values?**
Yes — they return a tuple. `a, b = func()` unpacks it.

**Q: What is `*args` used for?**
`*args` lets a function accept any number of positional arguments, collected as a tuple.

**Q: When should I use lambda instead of def?**
Use lambda for short, single-expression functions passed as arguments. Prefer named `def` for anything with logic, multiple lines, or reuse.
