# Object-Oriented Programming in Python

Source: https://docs.python.org/3/tutorial/classes.html

## Classes and Objects

A class is a blueprint for objects. Objects are instances of classes.

```python
class Dog:
    """Represents a dog."""

    species = "Canis lupus familiaris"   # class attribute

    def __init__(self, name: str, age: int):
        """Initialize instance attributes."""
        self.name = name   # instance attribute
        self.age  = age

    def bark(self) -> str:
        return f"{self.name} says: Woof!"

    def __repr__(self) -> str:
        return f"Dog(name={self.name!r}, age={self.age})"

    def __str__(self) -> str:
        return f"{self.name} ({self.age} years old)"


d = Dog("Buddy", 3)
print(d.bark())   # Buddy says: Woof!
print(repr(d))    # Dog(name='Buddy', age=3)
print(str(d))     # Buddy (3 years old)
print(d.species)  # Canis lupus familiaris
print(Dog.species)# Canis lupus familiaris
```

## Instance, Class, and Static Methods

```python
class Circle:
    PI = 3.14159

    def __init__(self, radius: float):
        self.radius = radius

    def area(self) -> float:
        """Instance method — accesses instance (self)."""
        return Circle.PI * self.radius ** 2

    @classmethod
    def from_diameter(cls, diameter: float) -> "Circle":
        """Class method — alternative constructor, accesses class (cls)."""
        return cls(diameter / 2)

    @staticmethod
    def is_valid_radius(r: float) -> bool:
        """Static method — no access to instance or class."""
        return r > 0


c1 = Circle(5)
print(c1.area())                     # 78.53975
c2 = Circle.from_diameter(10)
print(c2.radius)                     # 5.0
print(Circle.is_valid_radius(-1))    # False
```

## Inheritance

```python
class Animal:
    def __init__(self, name: str):
        self.name = name

    def speak(self) -> str:
        raise NotImplementedError("Subclasses must implement speak()")

    def __str__(self) -> str:
        return self.name


class Dog(Animal):
    def speak(self) -> str:
        return f"{self.name}: Woof!"


class Cat(Animal):
    def speak(self) -> str:
        return f"{self.name}: Meow!"


animals = [Dog("Rex"), Cat("Whiskers"), Dog("Buddy")]
for animal in animals:
    print(animal.speak())
# Rex: Woof!
# Whiskers: Meow!
# Buddy: Woof!
```

### Calling the Parent Class

```python
class Vehicle:
    def __init__(self, make: str, model: str):
        self.make  = make
        self.model = model

class Car(Vehicle):
    def __init__(self, make: str, model: str, doors: int):
        super().__init__(make, model)   # call parent __init__
        self.doors = doors

c = Car("Toyota", "Corolla", 4)
print(c.make, c.model, c.doors)  # Toyota Corolla 4
```

### isinstance and issubclass

```python
print(isinstance(c, Car))      # True
print(isinstance(c, Vehicle))  # True — inheritance chain
print(issubclass(Car, Vehicle))# True
```

## Multiple Inheritance and MRO

```python
class A:
    def hello(self):
        return "Hello from A"

class B(A):
    def hello(self):
        return "Hello from B"

class C(A):
    def hello(self):
        return "Hello from C"

class D(B, C):   # inherits from both B and C
    pass

d = D()
print(d.hello())           # Hello from B
print(D.__mro__)           # Method Resolution Order: D → B → C → A → object
```

Python uses **C3 linearisation** (MRO) to resolve method calls consistently.

## Special (Dunder) Methods

```python
class Vector:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __add__(self, other: "Vector") -> "Vector":
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Vector") -> "Vector":
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> "Vector":
        return Vector(self.x * scalar, self.y * scalar)

    def __abs__(self) -> float:
        return (self.x**2 + self.y**2) ** 0.5

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Vector):
            return NotImplemented
        return self.x == other.x and self.y == other.y

    def __repr__(self) -> str:
        return f"Vector({self.x}, {self.y})"

    def __len__(self) -> int:
        return 2   # a 2D vector always has 2 components


v1 = Vector(1, 2)
v2 = Vector(3, 4)
print(v1 + v2)     # Vector(4, 6)
print(abs(v2))     # 5.0
print(len(v1))     # 2
```

Common dunder methods:

| Method           | Triggered by                    |
|------------------|---------------------------------|
| `__init__`       | `obj = Class(...)`              |
| `__repr__`       | `repr(obj)`, debugger           |
| `__str__`        | `str(obj)`, `print(obj)`        |
| `__len__`        | `len(obj)`                      |
| `__getitem__`    | `obj[key]`                      |
| `__setitem__`    | `obj[key] = value`              |
| `__contains__`   | `value in obj`                  |
| `__iter__`       | `for x in obj`                  |
| `__eq__`         | `obj == other`                  |
| `__lt__`         | `obj < other`                   |
| `__hash__`       | `hash(obj)`, dict/set keys      |
| `__enter__/exit` | `with obj:`                     |
| `__call__`       | `obj()`                         |

## Properties

```python
class Temperature:
    def __init__(self, celsius: float):
        self._celsius = celsius

    @property
    def celsius(self) -> float:
        return self._celsius

    @celsius.setter
    def celsius(self, value: float):
        if value < -273.15:
            raise ValueError("Temperature below absolute zero")
        self._celsius = value

    @property
    def fahrenheit(self) -> float:
        return self._celsius * 9/5 + 32


t = Temperature(100)
print(t.celsius)     # 100
print(t.fahrenheit)  # 212.0
t.celsius = -300     # ValueError
```

## Abstract Base Classes

```python
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self) -> float:
        ...

    @abstractmethod
    def perimeter(self) -> float:
        ...

class Rectangle(Shape):
    def __init__(self, w: float, h: float):
        self.w = w
        self.h = h

    def area(self) -> float:
        return self.w * self.h

    def perimeter(self) -> float:
        return 2 * (self.w + self.h)

r = Rectangle(4, 5)
print(r.area())       # 20
# Shape()            # TypeError: Can't instantiate abstract class
```

## Dataclasses (Python 3.7+)

```python
from dataclasses import dataclass, field

@dataclass
class Point:
    x: float
    y: float
    z: float = 0.0

@dataclass(order=True)
class Employee:
    name: str
    salary: float
    department: str = "Engineering"
    skills: list = field(default_factory=list)

    def give_raise(self, amount: float):
        self.salary += amount

emp = Employee("Alice", 80000.0)
emp.give_raise(5000)
print(emp)   # Employee(name='Alice', salary=85000.0, department='Engineering', skills=[])
```

`@dataclass` automatically generates `__init__`, `__repr__`, and `__eq__`.

## Common OOP Mistakes

```python
# Forgetting self
class Counter:
    count = 0
    def increment():   # Missing self — TypeError when called on instance
        count += 1

# Modifying mutable class attribute through instance
class Config:
    options = []   # shared among all instances!

c1 = Config()
c2 = Config()
c1.options.append("dark_mode")  # mutates class attribute
print(c2.options)   # ['dark_mode'] — unexpected!
# Fix: move initialization to __init__:
#   self.options = []

# Not calling super().__init__() in subclasses with __init__
```

## Frequently Asked Questions

**Q: What is the difference between `__str__` and `__repr__`?**
`__repr__` is for developers — unambiguous, ideally `eval()`-able. `__str__` is for end users — readable. `print()` uses `__str__`; the REPL/debugger uses `__repr__`.

**Q: What does `self` refer to?**
`self` is a convention (could be any name) for the first argument of instance methods. Python passes the calling instance automatically.

**Q: What is the difference between a class attribute and an instance attribute?**
Class attributes are shared among all instances. Instance attributes are unique per instance and set via `self.attr = value` in `__init__`.

**Q: What is duck typing?**
"If it walks like a duck and quacks like a duck, it's a duck." Python checks whether an object has the required methods/attributes at call time, not at definition time. No explicit interface declaration is needed.


**Q: What is the difference between `__new__` and `__init__`, and when should I override `__new__`?**
`__new__(cls, ...)` runs first and returns the object; `__init__(self, ...)` runs afterward to initialize that object and must return `None`. For ordinary classes, use `__init__`. Override `__new__` mainly when constructing an immutable subtype such as `str`, `int`, or `tuple`, or for a carefully designed cache/flyweight or advanced metaclass. For an immutable `str` subclass, transform the value in `__new__` because `__init__` cannot change the string after it is created. Singletons are possible with `__new__` but are usually unnecessary and can accidentally reinitialize shared state. See `11-classes-and-objects.md` for examples and caveats.
