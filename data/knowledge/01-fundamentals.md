# Python Fundamentals — Variables, Data Types, and Operators

Source: https://docs.python.org/3/library/stdtypes.html

## Overview

Python is a dynamically typed, interpreted, high-level, general-purpose programming language. Variables are created by assignment and do not require explicit type declarations.

## Variables and Assignment

A variable is a name that refers to a value stored in memory.

```python
x = 10          # integer
name = "Alice"  # string
pi = 3.14159    # float
active = True   # bool
nothing = None  # NoneType
```

Variable names must start with a letter or underscore, cannot start with a digit, and cannot be Python keywords.

Multiple assignment on one line:

```python
a, b, c = 1, 2, 3
x = y = z = 0
```

## Built-in Data Types

| Category   | Types                           |
|------------|---------------------------------|
| Numeric    | `int`, `float`, `complex`       |
| Text       | `str`                           |
| Sequence   | `list`, `tuple`, `range`        |
| Mapping    | `dict`                          |
| Set        | `set`, `frozenset`              |
| Boolean    | `bool`                          |
| Binary     | `bytes`, `bytearray`            |
| None       | `NoneType`                      |

Use `type()` to inspect a value's type:

```python
print(type(42))       # <class 'int'>
print(type(3.14))     # <class 'float'>
print(type("hello"))  # <class 'str'>
print(type([1,2,3]))  # <class 'list'>
print(type(True))     # <class 'bool'>
```

## Integers

Python integers have arbitrary precision (no overflow):

```python
big = 10 ** 100   # googol — no overflow
print(big)

n = 0b1010   # binary literal   → 10
n = 0o12     # octal literal    → 10
n = 0xA      # hex literal      → 10
```

## Floats

IEEE 754 double-precision. Watch out for floating-point representation:

```python
print(0.1 + 0.2)        # 0.30000000000000004
print(0.1 + 0.2 == 0.3) # False — comparison is unsafe

import math
print(math.isclose(0.1 + 0.2, 0.3))  # True — use this instead
```

## Complex Numbers

```python
z = 2 + 3j
print(z.real)  # 2.0
print(z.imag)  # 3.0
print(abs(z))  # 3.605551275...
```

## Booleans

`bool` is a subclass of `int`. `True == 1` and `False == 0`.

```python
print(True + True)  # 2
print(bool(0))      # False
print(bool(""))     # False
print(bool([]))     # False
print(bool("hi"))   # True
print(bool(42))     # True
```

Falsy values: `None`, `False`, `0`, `0.0`, `""`, `[]`, `{}`, `()`, `set()`.

## Type Conversion (Casting)

```python
int("42")      # 42
float("3.14")  # 3.14
str(100)       # "100"
bool(1)        # True
list("abc")    # ['a', 'b', 'c']
```

Common error — `int()` does not accept float strings:

```python
int("3.14")   # ValueError: invalid literal for int() with base 10
int(float("3.14"))  # 3  — correct approach
```

## Arithmetic Operators

| Operator | Operation        | Example       | Result |
|----------|------------------|---------------|--------|
| `+`      | Addition         | `5 + 3`       | `8`    |
| `-`      | Subtraction      | `5 - 3`       | `2`    |
| `*`      | Multiplication   | `5 * 3`       | `15`   |
| `/`      | Division (float) | `7 / 2`       | `3.5`  |
| `//`     | Floor division   | `7 // 2`      | `3`    |
| `%`      | Modulo           | `7 % 2`       | `1`    |
| `**`     | Exponentiation   | `2 ** 8`      | `256`  |

```python
print(7 / 2)    # 3.5
print(7 // 2)   # 3    ← truncates toward negative infinity
print(-7 // 2)  # -4   ← not -3!
print(7 % 2)    # 1
print(-7 % 2)   # 1    ← sign follows divisor in Python
```

## Comparison Operators

```python
x = 5
print(x == 5)   # True
print(x != 3)   # True
print(x > 3)    # True
print(x < 10)   # True
print(x >= 5)   # True
print(x <= 4)   # False
```

Chained comparisons work naturally:

```python
1 < x < 10   # True
```

## Logical Operators

`and`, `or`, `not` use short-circuit evaluation:

```python
print(True and False)   # False
print(True or False)    # True
print(not True)         # False

# Short circuit
x = None
print(x or "default")  # "default"
print(x and x.upper()) # None — avoids AttributeError
```

## Bitwise Operators

```python
a, b = 0b1100, 0b1010   # 12 and 10
print(bin(a & b))   # 0b1000  (AND)
print(bin(a | b))   # 0b1110  (OR)
print(bin(a ^ b))   # 0b0110  (XOR)
print(bin(~a))      # -0b1101 (NOT)
print(bin(a << 1))  # 0b11000 (left shift)
print(bin(a >> 1))  # 0b110   (right shift)
```

## Identity and Membership Operators

```python
a = [1, 2, 3]
b = a
c = [1, 2, 3]

print(a is b)    # True — same object
print(a is c)    # False — different objects, same value
print(a == c)    # True — same value

print(2 in a)    # True
print(5 not in a)# True
```

**Common Mistake:** Use `==` to compare values; use `is` only for identity (e.g., `x is None`).

## Augmented Assignment

```python
x = 10
x += 5   # x = x + 5  → 15
x -= 3   # x = x - 3  → 12
x *= 2   # x = x * 2  → 24
x //= 5  # x = x // 5 → 4
x **= 3  # x = x ** 3 → 64
```

## Walrus Operator (Python 3.8+)

The `:=` assignment expression assigns and returns a value in one step:

```python
import re
data = "Name: Alice"
if m := re.search(r"Name: (\w+)", data):
    print(m.group(1))  # Alice

# Useful in while loops
while chunk := input("Enter text (empty to quit): "):
    print(f"You typed: {chunk}")
```

## Frequently Asked Questions

**Q: What is the difference between `==` and `is`?**
`==` compares values (equality). `is` compares object identity (same memory address). Small integers (-5 to 256) and interned strings may share identity, but relying on this is implementation-specific.

**Q: Why does `-7 // 2` give `-4` and not `-3`?**
Python's floor division always rounds toward negative infinity, unlike C-style truncation toward zero.

**Q: Is Python pass-by-value or pass-by-reference?**
Neither exactly — Python uses "pass-by-object-reference". Immutable objects (int, str, tuple) behave like pass-by-value; mutable objects (list, dict) behave like pass-by-reference.
