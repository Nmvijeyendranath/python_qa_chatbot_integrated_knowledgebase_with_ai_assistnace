# Iterators, Generators, Decorators, Context Managers, and Type Hints

Source: https://docs.python.org/3/howto/functional.html

## Iterators

An **iterator** is any object with `__iter__()` and `__next__()` methods.

```python
# Using an iterator manually
lst = [1, 2, 3]
it = iter(lst)      # creates iterator
print(next(it))     # 1
print(next(it))     # 2
print(next(it))     # 3
next(it)            # StopIteration raised

# Custom iterator class
class Countdown:
    def __init__(self, start):
        self.current = start

    def __iter__(self):
        return self

    def __next__(self):
        if self.current <= 0:
            raise StopIteration
        self.current -= 1
        return self.current + 1

for n in Countdown(3):
    print(n)   # 3 2 1
```

## Generators

Generators produce values lazily using `yield`. They are memory-efficient for large sequences.

```python
def countdown(n):
    while n > 0:
        yield n
        n -= 1

for num in countdown(5):
    print(num)   # 5 4 3 2 1

# Generator as iterator
gen = countdown(3)
print(next(gen))   # 3
print(next(gen))   # 2
```

### Generator Expressions

```python
# List — creates all values immediately
squares_list = [x**2 for x in range(1_000_000)]

# Generator — creates values on demand
squares_gen = (x**2 for x in range(1_000_000))

# Generators work with sum, min, max, any, all, etc.
total = sum(x**2 for x in range(1_000_000))
```

### yield from

```python
def chain(*iterables):
    for iterable in iterables:
        yield from iterable   # delegates to sub-generator

list(chain([1, 2], [3, 4], [5]))  # [1, 2, 3, 4, 5]
```

### Send and Two-way Communication

```python
def accumulator():
    total = 0
    while True:
        value = yield total   # receive value, yield running total
        if value is None:
            break
        total += value

gen = accumulator()
next(gen)           # prime the generator
print(gen.send(10)) # 10
print(gen.send(20)) # 30
print(gen.send(5))  # 35
```

## itertools — Standard Library

```python
import itertools

# Infinite iterators
count   = itertools.count(1, 2)         # 1 3 5 7 ...
cycle   = itertools.cycle([1, 2, 3])    # 1 2 3 1 2 3 ...
repeat  = itertools.repeat(0, times=3)  # 0 0 0

# Finite iterators
list(itertools.chain([1, 2], [3, 4]))     # [1, 2, 3, 4]
list(itertools.islice(count, 5))          # [1, 3, 5, 7, 9]
list(itertools.takewhile(lambda x: x<4, [1,2,3,4,5]))  # [1,2,3]
list(itertools.dropwhile(lambda x: x<4, [1,2,3,4,5]))  # [4,5]
list(itertools.compress([1,2,3,4], [1,0,1,0]))          # [1,3]

# Combinatoric iterators
list(itertools.permutations("ABC", 2))  # [('A','B'),('A','C'),...]
list(itertools.combinations("ABC", 2))  # [('A','B'),('A','C'),('B','C')]
list(itertools.product([0,1], repeat=3)) # 8 tuples (2^3)
```

## Decorators

A decorator is a function that wraps another function to extend its behaviour.

```python
import functools

def my_decorator(func):
    @functools.wraps(func)   # preserves __name__, __doc__
    def wrapper(*args, **kwargs):
        print(f"Before {func.__name__}")
        result = func(*args, **kwargs)
        print(f"After {func.__name__}")
        return result
    return wrapper

@my_decorator
def greet(name):
    print(f"Hello, {name}")

greet("Alice")
# Before greet
# Hello, Alice
# After greet
```

### Decorator with Arguments

```python
def repeat(n):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(n):
                func(*args, **kwargs)
        return wrapper
    return decorator

@repeat(3)
def say_hi():
    print("Hi!")

say_hi()  # Hi! Hi! Hi!
```

### Built-in Decorators

```python
class MyClass:
    @staticmethod
    def static_method(): ...     # no self or cls

    @classmethod
    def class_method(cls): ...   # receives class

    @property
    def value(self): ...         # getter

    @value.setter
    def value(self, v): ...      # setter

    @functools.cached_property   # Python 3.8+ — memoized property
    def expensive(self): ...
```

### Common Decorators from `functools`

```python
from functools import lru_cache, cache, wraps

# lru_cache: memoization with bounded size
@lru_cache(maxsize=128)
def fib(n):
    if n <= 1: return n
    return fib(n-1) + fib(n-2)

# cache: unbounded memoization (Python 3.9+)
@cache
def factorial(n):
    if n <= 1: return 1
    return n * factorial(n-1)
```

## Context Managers

Context managers implement `__enter__` and `__exit__` for setup/teardown.

```python
# Using contextlib.contextmanager
from contextlib import contextmanager

@contextmanager
def managed_resource(name):
    print(f"Acquiring {name}")
    try:
        yield name   # provide the resource
    finally:
        print(f"Releasing {name}")

with managed_resource("database connection") as conn:
    print(f"Using {conn}")

# Class-based context manager
class Timer:
    import time as _time

    def __enter__(self):
        self.start = self._time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.elapsed = self._time.perf_counter() - self.start
        print(f"Elapsed: {self.elapsed:.3f}s")
        return False   # don't suppress exceptions

with Timer() as t:
    sum(range(1_000_000))
# Elapsed: 0.023s
```

## Type Hints

Python's type annotation syntax (PEP 484). Not enforced at runtime.

```python
# Built-in types
def greet(name: str) -> str:
    return f"Hello, {name}"

def total(numbers: list[int]) -> int:
    return sum(numbers)

# Optional (value or None)
from typing import Optional
def find(lst: list[int], target: int) -> Optional[int]:
    try:
        return lst.index(target)
    except ValueError:
        return None

# Union (Python 3.10+ supports X | Y syntax)
def process(value: int | str) -> str:
    return str(value)

# Callable
from typing import Callable
def apply(func: Callable[[int], int], x: int) -> int:
    return func(x)

# TypeVar for generics
from typing import TypeVar, Sequence
T = TypeVar("T")

def first(seq: Sequence[T]) -> T:
    return seq[0]

# Type aliases
Vector = list[float]
Matrix = list[Vector]

# Protocols (structural subtyping)
from typing import Protocol

class Drawable(Protocol):
    def draw(self) -> None: ...
```

### Using mypy for Static Type Checking

```bash
pip install mypy
mypy src/   # type-check all files in src/
```

## Frequently Asked Questions

**Q: What is the difference between a generator and a list comprehension?**
A list comprehension evaluates all values immediately and stores them in memory. A generator evaluates one value at a time on demand, using much less memory for large sequences.

**Q: What does `@functools.wraps(func)` do?**
It copies the wrapped function's `__name__`, `__doc__`, and other metadata to the wrapper, so the decorator remains transparent to introspection tools.

**Q: What is the difference between `@property` and a regular method?**
A `@property` is accessed like an attribute (`obj.value`), not called like a method (`obj.value()`). It enables computed attributes with validation.

**Q: Can a generator be used more than once?**
No. A generator is exhausted after one traversal. Create a new generator object to iterate again.
