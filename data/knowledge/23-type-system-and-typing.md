# Python Type System — Dynamic, Strong, Duck Typing, and Type Hints

Sources:
- Official Python Documentation — typing: https://docs.python.org/3/library/typing.html
- Python Tutorial — Function Annotations: https://docs.python.org/3/tutorial/controlflow.html#function-annotations
- PEP 484 — Type Hints: https://peps.python.org/pep-0484/
- PEP 544 — Protocols (Structural Subtyping): https://peps.python.org/pep-0544/
- Real Python — Python Type Checking: https://realpython.com/python-type-checking/

## Fundamentals of Python's Type System

Python's type system is characterized by three core principles:

1. **Dynamically Typed**: Types are associated with **values/objects** at runtime, not with variable identifiers. You do not declare a variable's type when creating it, and a variable can be rebound to an object of a completely different type at any time:
   ```python
   x = 42        # x references an int
   x = "hello"   # x now references a str (valid in Python)
   ```

2. **Strongly Typed**: Python does not automatically coerce types across incompatible operations. An explicit conversion is required:
   ```python
   # In a weakly typed language (e.g. JavaScript), "4" + 2 results in "42".
   # In Python:
   result = "4" + 2  # Raises TypeError: can only concatenate str to str, not "int"
   ```

3. **Duck Typed**: Python prioritizes what an object can do (its methods and attributes) rather than its explicit class hierarchy. The famous adage is: *"If it walks like a duck and quacks like a duck, it's a duck."*
   ```python
   def serialize(stream):
       # Doesn't care if stream is a file, StringIO, or socket,
       # as long as it implements a write() method!
       stream.write("data")
   ```

## Nominal Typing vs. Structural Subtyping

Python supports both nominal and structural polymorphism:

### 1. Nominal Typing via Abstract Base Classes (ABCs)
With nominal typing, compatibility is determined by explicit inheritance. Python provides the `abc` module and `collections.abc`:

```python
from abc import ABC, abstractmethod

class Database(ABC):
    @abstractmethod
    def connect(self) -> None:
        pass

class PostgresDB(Database):
    def connect(self) -> None:
        print("Connected to Postgres")

# Checked via isinstance():
db = PostgresDB()
print(isinstance(db, Database))  # True
```

### 2. Structural Subtyping via Protocols (PEP 544)
Introduced in Python 3.8, `typing.Protocol` allows **static duck typing**. A class is considered a valid subtype if it implements the required attributes/methods, without needing to explicitly inherit from the Protocol:

```python
from typing import Protocol

class Renderable(Protocol):
    def render(self) -> str:
        ...

class Button:
    def render(self) -> str:
        return "<button>Click</button>"

# Button is compatible with Renderable without inheriting from it!
def draw(component: Renderable) -> None:
    print(component.render())

draw(Button())  # Type checker passes!
```

## Type Hints and Annotations (PEP 484)

Starting in Python 3.5+, type hints allow developers to annotate variables, function parameters, and return types.

### Runtime Behavior: Annotations Are Non-Enforcing Metadata
A fundamental rule in Python: **type hints do not enforce types at runtime and do not cause type errors during execution**.
- Python parses annotations and stores them in the `__annotations__` dictionary of the module, class, or function.
- Python does not validate that arguments match their annotations when the function is called.
- Type enforcement is performed ahead-of-time by static analysis tools like **mypy**, **pyright**, or IDE language servers.

```python
def multiply(a: int, b: int) -> int:
    return a * b

# Python executes this without error at runtime, even though arguments are strings!
print(multiply("hello", 3))  # "hellohellohello"
print(multiply.__annotations__)  # {'a': <class 'int'>, 'b': <class 'int'>, 'return': <class 'int'>}
```

### Modern Python Type Hinting Syntax (Python 3.10+)

```python
from typing import Any, Callable, Literal, Optional

# Union types using the pipe operator (|)
def fetch_user(user_id: int | str) -> dict[str, Any] | None:
    pass

# Built-in generic types (list, dict, tuple, set) directly in lowercase:
scores: list[float] = [98.5, 91.2]
lookup: dict[str, list[int]] = {"evens": [2, 4, 6]}

# Literal types for exact allowed values:
Mode = Literal["r", "w", "a"]

# Callable types: Callable[[ArgTypes], ReturnType]
def execute_task(callback: Callable[[int], bool]) -> None:
    pass
```

## Frequently Asked Questions

**Q: Is Python statically or dynamically typed?**
Python is dynamically and strongly typed. Types belong to runtime objects rather than variable names. Variables can be freely rebound to objects of different types, but operations between incompatible types (such as adding a string to an integer) require explicit conversion.

**Q: What is duck typing in Python?**
Duck typing is a programming style where an object's suitability is determined by the presence of certain methods and properties, rather than its inheritance from a specific class. If an object has the required interface, Python code works with it regardless of its exact type.

**Q: Do type hints in Python affect runtime performance or enforce types?**
No. Type hints in standard Python are purely metadata stored in `__annotations__`. CPython ignores them during bytecode execution, meaning there is zero runtime performance penalty and no runtime type enforcement. Type validation is performed by static tools like `mypy` or runtime libraries like `pydantic`.

**Q: What is the difference between Abstract Base Classes (ABCs) and Protocols in Python?**
ABCs require explicit inheritance (nominal typing), where a class must explicitly inherit from the ABC to satisfy `isinstance()` checks. Protocols (PEP 544) provide structural subtyping (static duck typing), where any class that implements the required methods and attributes automatically satisfies the type checker without explicit inheritance.
