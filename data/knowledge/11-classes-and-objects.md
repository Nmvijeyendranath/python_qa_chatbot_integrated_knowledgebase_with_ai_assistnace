# Python Classes, Objects, and Object Construction
Source: https://docs.python.org/3/tutorial/classes.html
Object model reference: https://docs.python.org/3/reference/datamodel.html

## Class versus object

A **class** is a user-defined type: it describes the attributes and behavior its instances expose. An **object** (or instance) is a concrete value created from a class. Each instance has its own identity and may hold its own state. In Python, classes are objects too: ordinary class statements create class objects, usually using the metaclass `type`.

```python
class User:
    account_type = "standard"  # class attribute shared by instances

    def __init__(self, name: str):
        self.name = name        # instance attribute

    def greeting(self) -> str:  # instance method
        return f"Hello, {self.name}"

ada = User("Ada")
grace = User("Grace")
print(ada.greeting())             # Hello, Ada
print(ada.name, grace.name)       # Ada Grace
print(ada.account_type)           # standard (found on the class)
```

Instance attribute lookup checks the instance and then its class and base classes. Assigning `ada.account_type = "admin"` creates an instance attribute that shadows the class attribute; it does not change `grace.account_type`. Avoid mutable class attributes for per-instance state: a list or dictionary on the class is shared by all instances unless an instance shadows it.

## What happens when you call a class

A call such as `obj = Widget(value)` roughly follows this order:

1. Python calls `Widget.__new__(Widget, value)` to obtain an instance.
2. If `__new__` returns an instance of `Widget` (or a subclass), Python calls `Widget.__init__(that_instance, value)` to initialize it.
3. The expression evaluates to the returned instance.

`__new__` is responsible for **creating/choosing and returning** the object. `__init__` configures an object that already exists; it does not allocate it and must return `None`. For an ordinary class, inherit `object.__new__` and implement `__init__` only when the instance needs initialization. This is the normal case.

```python
class Rectangle:
    def __init__(self, width: float, height: float):
        self.width = width       # configure the already-created instance
        self.height = height

r = Rectangle(3, 4)              # object.__new__ creates it, then __init__ runs
print(r.width * r.height)        # 12
```

## `__new__` versus `__init__`

| | `__new__(cls, ...)` | `__init__(self, ...)` |
|---|---|---|
| Runs | First, during a class call | After `__new__` returns an instance of the class |
| Receives | The class (`cls`) | The newly returned instance (`self`) |
| Job | Return an instance; control allocation or choose/reuse an object | Set up or validate the instance's mutable state |
| Typical use | Rarely overridden for ordinary user classes | The common place to initialize instance attributes |
| Return value | Must return the object to use | Must return `None` |

The method named `__new__` is treated as a static method by Python's data model; when overridden, define it with `cls` as its first parameter and return an instance, commonly through `super().__new__(cls, ...)`. Do not call `__init__` manually as a substitute for construction.

## When should you actually override `__new__`?

Override `__new__` when construction itself must control which object is created, especially:

- **Subclassing an immutable built-in** such as `str`, `int`, or `tuple`. Its value is fixed at creation time, so transform or validate the value in `__new__` before returning the immutable object.
- **Returning a cached or canonical instance** (interning/flyweight patterns) when identity reuse is genuinely required and its lifecycle is carefully managed.
- **Advanced framework or metaclass work** where class/object creation itself must be customized. For a metaclass, `__new__` creates a *class object*, which is a different, more advanced use of the object model.

A practical immutable-subclass example:

```python
class Uppercase(str):
    def __new__(cls, value: str):
        # str is immutable: create its final value here.
        return super().__new__(cls, value.upper())

word = Uppercase("hello")
print(word)                       # HELLO
print(isinstance(word, str))     # True
```

An `__init__` method cannot change the underlying string value after the `str` object has been created. For ordinary mutable classes like `Rectangle`, `User`, or a service object, `__init__` is the correct place for state setup; overriding `__new__` adds complexity without benefit.

### Singleton and caching caution

A singleton sometimes overrides `__new__` to return a previously created instance, but this is rarely the best default. Python still calls `__init__` when the returned object is an instance of the class, so repeated construction may reinitialize that shared instance. Global singleton state also complicates tests, concurrency, and dependency management. Prefer a module-level instance or explicit dependency injection unless identity reuse is a real requirement. If you do implement a cache, handle initialization idempotently and consider thread safety.

## `self`, `cls`, and method binding

`self` and `cls` are conventions, not keywords. When `obj.method(x)` calls a normal instance method, Python binds `obj` as the first argument. A `classmethod` binds the class as `cls`, so it is useful for alternative constructors that should work for subclasses. A `staticmethod` receives neither automatically.

```python
class UserId:
    def __init__(self, value: int):
        self.value = value

    @classmethod
    def from_text(cls, text: str):
        return cls(int(text))            # respects a subclass of UserId

    @staticmethod
    def is_valid(value: int) -> bool:
        return value > 0
```

## Identity, equality, and mutability

Identity answers “is this the same object?” and is checked with `is`; equality answers “do these objects compare as equal?” and is checked with `==` (which can be customized with `__eq__`). Two distinct instances can be equal. Use `is None` to check for `None`; do not use `is` to compare strings or numbers. Mutable instances can change state while keeping the same identity.

```python
first = [1, 2]
second = [1, 2]
print(first == second)  # True: equal contents
print(first is second)  # False: distinct list objects
alias = first
print(alias is first)   # True: same object
```

## Inheritance, `super()`, and method resolution

A subclass inherits behavior and may override it. `super()` follows Python's method resolution order (MRO); it is not simply a hard-coded call to one named parent. In cooperative multiple inheritance, each participating method should call `super()` consistently so the MRO chain can run once.

Use inheritance for a genuine “is-a” relationship. Prefer composition (“has-a”) when an object can delegate to another object without claiming to be its subtype.

## Common class/object pitfalls

- Forgetting `self` in an instance method causes a call-signature error.
- Putting a mutable per-instance default at class scope shares it across every instance; create a fresh list/dict in `__init__` or use `dataclasses.field(default_factory=...)`.
- `__init__` is not a constructor that returns the new object; `__new__` supplies the object.
- Returning a non-instance from `__new__` means `__init__` for that class is not called.
- Overriding `__eq__` without considering `__hash__` can make instances unsuitable as dictionary keys; equal objects must have equal hashes, and mutable value objects generally should not be hashable.
- Creating singletons through `__new__` without guarding repeat initialization can reset state on each call.

## Further official reading

- Tutorial on classes: https://docs.python.org/3/tutorial/classes.html
- Data model and special method lookup: https://docs.python.org/3/reference/datamodel.html
- `object.__new__` and `object.__init__`: https://docs.python.org/3/reference/datamodel.html#object.__new__
