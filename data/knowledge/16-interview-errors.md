# Python Interview Questions and Common Errors Reference

Source: https://docs.python.org/3/

## Frequently Asked Python Interview Questions

### Q: What is the difference between a list and a tuple?
Lists are mutable (can be changed after creation); tuples are immutable. Lists use `[]`; tuples use `()`. Tuples are faster for iteration and can be used as dictionary keys or set members since they are hashable (provided all their elements are hashable).

```python
lst   = [1, 2, 3]    # mutable
tup   = (1, 2, 3)    # immutable
lst[0] = 99          # OK
tup[0] = 99          # TypeError: 'tuple' object does not support item assignment

# Tuple as dict key
d = {(0, 0): "origin"}   # OK
d = {[0, 0]: "origin"}   # TypeError: unhashable type: 'list'
```

### Q: What is the GIL (Global Interpreter Lock)?
The GIL is a mutex in CPython that allows only one thread to execute Python bytecode at a time. It prevents true parallelism for CPU-bound threads in CPython.

```python
# CPU-bound: use multiprocessing, not threading
from multiprocessing import Pool

def cpu_task(n):
    return sum(i**2 for i in range(n))

with Pool(4) as pool:
    results = pool.map(cpu_task, [100_000] * 4)

# I/O-bound: threading works fine (GIL released during I/O)
import threading

def download(url):
    import urllib.request
    urllib.request.urlretrieve(url, "file.html")

threads = [threading.Thread(target=download, args=(url,)) for url in urls]
for t in threads: t.start()
for t in threads: t.join()
```

### Q: What is the difference between `deepcopy` and shallow copy?

```python
import copy

original = [[1, 2], [3, 4]]

shallow = original.copy()       # or list(original) or original[:]
deep    = copy.deepcopy(original)

shallow[0].append(99)
print(original[0])   # [1, 2, 99]  — affected by shallow copy mutation

deep[0].append(99)
print(original[0])   # [1, 2, 99]  — NOT affected by deep copy mutation
```

### Q: What is a generator and why use it?

```python
# List comprehension — all values in memory immediately
squares_list = [x**2 for x in range(1_000_000)]  # uses ~8 MB

# Generator expression — one value at a time
squares_gen  = (x**2 for x in range(1_000_000))  # uses ~100 bytes

# Generator function
def infinite_counter(start=0):
    while True:
        yield start
        start += 1

counter = infinite_counter()
print(next(counter))  # 0
print(next(counter))  # 1
```

### Q: What are Python's magic/dunder methods?
Methods with double underscores on both sides (`__init__`, `__str__`, `__len__`, etc.) that Python calls implicitly in response to operators and built-in functions.

```python
class Box:
    def __init__(self, width, height):
        self.width, self.height = width, height

    def __repr__(self):
        return f"Box({self.width}, {self.height})"

    def __add__(self, other):
        return Box(self.width + other.width, self.height + other.height)

    def __len__(self):
        return self.width * self.height   # area

b1 = Box(2, 3)
b2 = Box(4, 5)
print(b1 + b2)  # Box(6, 8)
print(len(b1))  # 6
```

### Q: What is the difference between `__new__` and `__init__`?
`__new__` allocates and returns a new instance. `__init__` initialises an existing instance. You rarely override `__new__` unless implementing a singleton, immutable subclass, or metaclass.

```python
class Singleton:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

a = Singleton()
b = Singleton()
print(a is b)   # True — same object
```

### Q: What is a closure?

```python
def make_multiplier(n):
    def multiplier(x):
        return x * n   # n is a free variable from enclosing scope
    return multiplier

double = make_multiplier(2)
triple = make_multiplier(3)
print(double(5))  # 10
print(triple(5))  # 15

# Check the closure
print(double.__closure__[0].cell_contents)  # 2
```

### Q: What is the difference between `@staticmethod` and `@classmethod`?

```python
class MyClass:
    class_var = "shared"

    @staticmethod
    def static_method(x):
        # No access to class or instance; just a regular function in class namespace
        return x * 2

    @classmethod
    def class_method(cls):
        # cls is the class (or subclass when inherited)
        return cls.class_var

print(MyClass.static_method(5))   # 10
print(MyClass.class_method())     # "shared"
```

### Q: How does Python's memory management work?
Python uses reference counting as the primary mechanism. When an object's reference count reaches zero, it is immediately freed. A cyclic garbage collector handles reference cycles. `gc` module controls and inspects it.

```python
import gc
import sys

lst = [1, 2, 3]
print(sys.getrefcount(lst))   # 2 (lst + getrefcount arg)

gc.collect()   # force cycle collection
gc.disable()   # disable cycle collector (rare)
```

### Q: What is `*args` and `**kwargs`?

```python
def func(*args, **kwargs):
    print(args)    # tuple of positional arguments
    print(kwargs)  # dict of keyword arguments

func(1, 2, 3, name="Alice", age=30)
# (1, 2, 3)
# {'name': 'Alice', 'age': 30}

# Unpacking into a function call
def add(a, b, c):
    return a + b + c

nums = [1, 2, 3]
print(add(*nums))       # 6

opts = {"a": 1, "b": 2, "c": 3}
print(add(**opts))      # 6
```

## Common Python Errors and Fixes

### SyntaxError

```python
# Missing colon
if x > 0
    print(x)
# SyntaxError: expected ':'
# Fix: if x > 0:

# Mismatched brackets
result = (1 + 2
# SyntaxError: '(' was never closed

# Invalid assignment in condition
if x = 5:   # SyntaxError — use == for comparison, := for walrus
```

### IndentationError

```python
def greet():
print("hello")   # IndentationError: expected an indented block
# Fix: add 4-space indent

# Mixed tabs and spaces
def func():
	x = 1   # tab
    y = 2   # spaces — TabError
# Fix: use spaces only; run: python -tt script.py to detect
```

### TypeError

```python
"age: " + 30        # TypeError: can only concatenate str (not "int") to str
# Fix: "age: " + str(30)  or  f"age: {30}"

len(42)             # TypeError: object of type 'int' has no len()
# Fix: len(str(42))

None + 1            # TypeError: unsupported operand type(s)
# Fix: check for None before operating
```

### ValueError

```python
int("3.14")    # ValueError: invalid literal for int() with base 10: '3.14'
# Fix: int(float("3.14"))

int("")        # ValueError: invalid literal for int() with base 10: ''
# Fix: guard with if text.strip(): int(text)

[1,2,3].index(99)  # ValueError: 99 is not in list
# Fix: check "if 99 in lst" first, or use try/except
```

### AttributeError

```python
n = 42
n.upper()          # AttributeError: 'int' object has no attribute 'upper'
# Fix: str(n).upper()

lst = None
lst.append(1)      # AttributeError: 'NoneType' object has no attribute 'append'
# Fix: ensure lst is initialised to []

import numpy       # wrong — should be import numpy as np
numpy.array([1])   # OK (but numpy.np is common)
```

### NameError and UnboundLocalError

```python
print(undefined)   # NameError: name 'undefined' is not defined

# UnboundLocalError
total = 0
def add(x):
    total += x   # UnboundLocalError: local variable 'total' referenced before assignment
# Fix: declare "global total" inside add(), or pass total as argument

# Common gotcha with default mutable
def func():
    if False:
        x = 1
    print(x)  # UnboundLocalError if branch never ran
```

### RecursionError

```python
def f(n):
    return f(n - 1)   # no base case → RecursionError

# Fix: add base case
def f(n):
    if n <= 0:
        return 0
    return f(n - 1)

# Check and increase limit (rarely needed)
import sys
sys.setrecursionlimit(10_000)
```

## Practical Debugging Scenarios

### Debugging an unexpected None return

```python
# Forgetting return
def double(x):
    result = x * 2   # calculated but not returned

print(double(5))   # None
# Fix: add return result
```

### Debugging list mutation side effects

```python
def clear_first(lst):
    lst.clear()   # mutates the original!

my_list = [1, 2, 3]
clear_first(my_list)
print(my_list)   # []  — unexpected
# Fix: work on a copy: lst = lst.copy(); lst.clear()
```

### Debugging late binding in closures

```python
# Bug: all functions capture the same variable i
funcs = [lambda: i for i in range(5)]
print([f() for f in funcs])   # [4, 4, 4, 4, 4] — all return 4

# Fix: use default argument to capture current value
funcs = [lambda i=i: i for i in range(5)]
print([f() for f in funcs])   # [0, 1, 2, 3, 4]
```
