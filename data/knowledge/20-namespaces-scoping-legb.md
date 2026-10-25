# Python Namespaces and Scoping — The LEGB Rule

Sources:
- Official Python Documentation: https://docs.python.org/3/reference/executionmodel.html#naming-and-binding
- Python Tutorial — Scopes and Namespaces: https://docs.python.org/3/tutorial/classes.html#python-scopes-and-namespaces
- Real Python — Python Scope & the LEGB Rule: https://realpython.com/python-scope-legb-rule/

## What is a Namespace?

A **namespace** in Python is a mapping from symbolic variable names (identifiers) to objects. Under the hood, most namespaces are implemented as standard Python **dictionaries** (`dict`).

There are three major namespace lifecycles:
1. **Built-in Namespace**: Created when the Python interpreter starts up and remains alive until exit. Contains built-in functions (`print`, `len`, `range`, `isinstance`) and exception classes (`ValueError`, `KeyError`).
2. **Global Namespace**: Created when a module is read or imported. Remains alive until the interpreter terminates.
3. **Local Namespace**: Created when a function or method is called, and deleted when the function returns or raises an uncaught exception.

## The LEGB Scoping Rule

When a variable name is referenced inside Python code, Python searches through scopes sequentially in a strict order known as the **LEGB rule**:

```
 ┌────────────────────────────────────────────────────────┐
 │  Local (L)                                             │
 │  Names assigned inside the current function/lambda     │
 │    ┌──────────────────────────────────────────────────┐│
 │    │  Enclosing (E)                                   ││
 │    │  Names in local scopes of enclosing functions    ││
 │    │    ┌────────────────────────────────────────────┐││
 │    │    │  Global (G)                                │││
 │    │    │  Names defined at module top level         │││
 │    │    │    ┌──────────────────────────────────────┐│││
 │    │    │    │  Built-in (B)                        ││││
 │    │    │    │  len(), range(), str(), int(), etc.  ││││
 │    │    │    └──────────────────────────────────────┘│││
 │    │    └────────────────────────────────────────────┘││
 │    └──────────────────────────────────────────────────┘│
 └────────────────────────────────────────────────────────┘
```

1. **L — Local**: Names assigned in any way within a function body or lambda expression, and not declared global in that function.
2. **E — Enclosing**: Names in the local scope of any statically enclosing function definitions (outer functions), from innermost to outermost.
3. **G — Global (Module)**: Names assigned at the top-level of a module file, or declared with `global` within a `def`.
4. **B — Built-in**: Names preassigned in the `builtins` module.

If Python does not find the name in any of the four scopes, it raises a `NameError: name '...' is not defined`.

## Name Binding Operations

In Python, names are bound by specific operations:
- Assignment: `x = 10`
- Function definition: `def my_func(): pass` (binds `my_func`)
- Class definition: `class MyClass: pass` (binds `MyClass`)
- Import: `import math`, `from os import path` (binds `math` or `path`)
- Function parameters in the header
- `for` loop target variable: `for item in items:` (binds `item`)
- Exception handler target: `except Exception as err:` (binds `err`)
- Context manager target: `with open(...) as f:` (binds `f`)

Important note: `if`, `while`, `for`, and `try` blocks **do not create new local scopes** in Python. A variable assigned inside an `if` block is still in the surrounding function or module scope.

## Modifying Scopes: `global` and `nonlocal`

By default, any variable assigned inside a function is treated as a **local variable**. If you want to modify a variable in an outer scope, you must use scope declaration keywords:

### The `global` Statement
Tells Python that the specified identifier belongs to the top-level **module namespace**, bypassing the local and enclosing scopes:

```python
counter = 0

def increment():
    global counter
    counter += 1  # Modifies the module-level 'counter'

increment()
print(counter)  # 1
```

### The `nonlocal` Statement
Introduced in Python 3, `nonlocal` tells Python that the identifier refers to a variable in the **nearest enclosing function scope** (excluding global and built-in scopes). It is essential for stateful closures:

```python
def make_counter():
    count = 0  # Enclosing scope variable
    
    def step():
        nonlocal count
        count += 1
        return count
        
    return step

counter_a = make_counter()
print(counter_a())  # 1
print(counter_a())  # 2
```

## Closures and Lexical Scoping

A **closure** is a function that retains access to variables from its enclosing lexical scope even after the outer function has completed execution and left the call stack.

CPython implements closures using **cell objects** (`__closure__` attribute):

```python
def make_multiplier(factor):
    def multiply(n):
        return n * factor  # 'factor' is captured in a cell
    return multiply

double = make_multiplier(2)
print(double(5))                 # 10
print(double.__closure__[0].cell_contents)  # 2
```

## Introspection: `locals()`, `globals()`, and `vars()`

Python provides built-in functions to inspect namespaces at runtime:
- `globals()`: Returns a reference to the current module's dictionary namespace.
- `locals()`: Returns a dictionary of the current local scope's variables. In functions, modifying this dictionary does not change actual local variables because CPython stores locals in an optimized array (`LOAD_FAST`).
- `vars(obj)`: Returns the `__dict__` attribute of a module, class, or instance.
- `dir(obj)`: Returns an alphabetized list of valid attributes for the given object or current scope.

## Frequently Asked Questions

**Q: How do namespaces and scopes work in Python?**
A namespace is a dictionary mapping identifier names to objects in memory. A scope is the textual region of a Python program where a namespace is directly accessible. When looking up names, Python searches scopes hierarchically from inside out.

**Q: What is the LEGB rule in Python?**
LEGB stands for Local, Enclosing, Global, Built-in. It is the sequence in which Python searches namespaces to resolve a variable name. It checks Local function variables first, then Enclosing closures, then Global module-level variables, and finally Built-in names.

**Q: What is the difference between `global` and `nonlocal` in Python?**
`global` binds a variable to the module's top-level namespace. `nonlocal` binds a variable to the nearest outer enclosing function's local scope (used in nested functions and closures) without affecting the global namespace.

**Q: Do `for` loops or `if` statements create their own scope in Python?**
No. In Python, only functions, classes, modules, and comprehensions create new scopes. Blocks like `if`, `while`, `for`, and `try` do not create local scopes; variables created inside them remain accessible outside the block.
