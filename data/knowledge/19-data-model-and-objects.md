# Python Data Model — Objects, Identity, Mutability, and References

Sources:
- Official Python Documentation: https://docs.python.org/3/reference/datamodel.html
- Python Tutorial — Data Structures: https://docs.python.org/3/tutorial/datastructures.html
- Real Python — Python's Object Model: https://realpython.com/python-variables/
- Real Python — Mutable vs Immutable: https://realpython.com/pointers-in-python/

## The Python Data Model: "Everything is an Object"

In Python, all data is represented by **objects** or by relations between objects. Every object in Python has three fundamental attributes:

1. **Identity**: An integer identifying the object's unique memory address during its lifetime. Retrieved using `id(obj)`.
2. **Type**: Dictates the values the object can hold and the operations it supports (e.g., `int`, `str`, `list`). Retrieved using `type(obj)`. An object's type is completely unchangeable once created.
3. **Value**: The data content held by the object. An object whose value can change is **mutable**; an object whose value cannot change is **immutable**.

```python
x = [1, 2, 3]
print(id(x))    # Memory address integer (e.g., 140234892348)
print(type(x))  # <class 'list'>
print(x)        # [1, 2, 3] (value)
```

## Variable Assignment as Name Binding

A critical conceptual difference between Python and languages like C or Java is that **Python variables are not memory "boxes" containing values**. Instead, a variable is merely a **symbolic name (reference) bound to an object in heap memory**.

```python
a = [1, 2, 3]
b = a          # 'b' references the exact same list object as 'a'
b.append(4)
print(a)       # [1, 2, 3, 4] -> Both names reflect the mutation!
print(a is b)  # True (identical memory address)
```

## Identity (`is`) vs. Equality (`==`)

- **`==` (Value Equality)**: Calls the object's `__eq__()` magic method to check if two objects represent equivalent data values.
- **`is` (Identity Comparison)**: Checks if two variables point to the **exact same memory location** (`id(a) == id(b)`).

```python
list1 = [1, 2, 3]
list2 = [1, 2, 3]

print(list1 == list2)  # True: values are equal
print(list1 is list2)  # False: two distinct list objects in memory

# Always use 'is' for None, True, and False singletons:
if x is None:
    pass
```

## Mutable vs. Immutable Types

Understanding mutability is essential for avoiding unexpected bugs and side effects in Python.

| Type | Mutability | Modifying Behavior |
|---|---|---|
| `int`, `float`, `complex`, `bool` | **Immutable** | Operations like `x += 1` create a new number object and rebind `x`. |
| `str` | **Immutable** | Methods like `s.upper()` or concatenation return brand new string objects. |
| `tuple` | **Immutable** | Elements cannot be added, removed, or replaced. Note: if a tuple contains a mutable object (like a list), that nested object can still mutate! |
| `frozenset`, `bytes` | **Immutable** | Fixed sets and byte buffers. |
| `list` | **Mutable** | `append()`, `extend()`, `sort()`, and item assignment modify the list in place without changing `id()`. |
| `dict` | **Mutable** | Keys and values can be added, updated, or removed in place. |
| `set` | **Mutable** | Elements can be added or removed in place. |
| `bytearray` | **Mutable** | In-place mutable sequence of bytes. |

### Integer and String Interning
CPython optimizes memory and execution speed by pre-allocating small objects:
- **Small integer cache**: CPython pre-allocates all integers from `-5` to `256` at startup. Any reference to these numbers shares the same singleton object:
  ```python
  x = 250
  y = 250
  print(x is y)  # True (interned)

  a = 1000
  b = 1000
  print(a is b)  # False (distinct objects outside cache)
  ```
- **String interning**: Identifiers and string literals matching identifier syntax are automatically interned to speed up dictionary lookups.

## Argument Passing: Pass-by-Object-Reference

Python uses **call-by-sharing** (also known as *pass-by-object-reference*). Function parameters receive references to the passed objects:

1. **Rebinding a parameter** inside a function only alters the local reference, not the caller's variable:
   ```python
   def reassign(val):
       val = [99]  # Rebinds local name 'val' to a new list object

   data = [1, 2]
   reassign(data)
   print(data)  # Still [1, 2] (original reference unchanged)
   ```

2. **Mutating a parameter in place** alters the underlying object shared with the caller:
   ```python
   def mutate(val):
       val.append(99)  # Modifies the shared list object in place

   data = [1, 2]
   mutate(data)
   print(data)  # [1, 2, 99] (caller sees the mutation!)
   ```

## Shallow Copy vs. Deep Copy

When duplicating mutable compound objects (like lists of lists or dictionaries containing objects):

- **Shallow Copy** (`copy.copy(obj)` or `obj.copy()` or `list[:]`): Creates a new outer container, but inserts references to the existing child objects.
- **Deep Copy** (`copy.deepcopy(obj)`): Recursively creates a new outer container and completely clones all nested children objects.

```python
import copy

original = [[1, 2], [3, 4]]
shallow = copy.copy(original)
deep = copy.deepcopy(original)

original[0].append(99)
print(shallow)  # [[1, 2, 99], [3, 4]] -> affected by child mutation!
print(deep)     # [[1, 2], [3, 4]]     -> completely isolated!
```

## Frequently Asked Questions

**Q: How does Python's data model work?**
Python's data model treats all data as objects. Every object has an identity (`id`), a type (`type`), and a value. Variables in Python are not typed storage containers; they are dynamic names (pointers) bound to objects residing on the heap.

**Q: What does "everything is an object" mean in Python?**
In Python, functions, modules, classes, integers, strings, and types themselves are first-class objects subclassing `object`. They all possess attributes, methods, memory addresses, and type references, and can be passed as arguments, returned from functions, and assigned to variables.

**Q: What is the difference between mutable and immutable objects?**
Mutable objects (such as `list`, `dict`, `set`) allow altering their content in-place without changing their memory address (`id()`). Immutable objects (such as `int`, `float`, `str`, `tuple`) cannot have their internal values changed after creation; any modification produces a newly allocated object.

**Q: Is Python pass-by-value or pass-by-reference?**
Python is neither; it uses "pass-by-object-reference" (or "call-by-sharing"). Arguments are passed by object reference. If a function mutates a mutable passed object in-place, the caller sees the change. If the function reassigns the parameter name, it rebinds only the local name without affecting the caller.

**Q: What is the difference between `is` and `==` in Python?**
`==` checks for value equality by invoking `__eq__()`, comparing whether two objects represent equivalent content. `is` checks for object identity, comparing whether both references point to the exact same location in memory (`id(a) == id(b)`).
