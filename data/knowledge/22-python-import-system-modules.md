# Python Import System — Modules, Packages, and Search Mechanics

Sources:
- Official Python Documentation — The Import System: https://docs.python.org/3/reference/import.html
- Python Tutorial — Modules: https://docs.python.org/3/tutorial/modules.html
- Standard Library — sys: https://docs.python.org/3/library/sys.html
- Real Python — Python Modules and Packages: https://realpython.com/python-modules-packages/

## How the Import System Works Behind the Scenes

When you write `import foo` or `from foo import bar`, Python executes a multi-step sequence to discover, compile, and initialize the requested code:

```
import foo
   │
   ▼
1. Check `sys.modules` Cache ──(Found?)──► Return cached module
   │ (Not found)
   ▼
2. Finders (`sys.meta_path`)
   Search paths in `sys.path` to locate the source file or compiled `.pyc`
   │ (Located)
   ▼
3. Loaders (`importlib`)
   Allocate module object, compile to bytecode, cache in `sys.modules`
   │
   ▼
4. Execute Module Code
   Run the module body from top to bottom in a new dictionary namespace
   │
   ▼
5. Bind Variable Name
   Bind `foo` in the importing caller's namespace
```

### 1. `sys.modules` — The Module Cache
`sys.modules` is a dictionary mapping module names to loaded module objects. Whenever a module is imported:
- If the name already exists in `sys.modules`, Python immediately returns the cached module object.
- **Modules are only executed once per Python process!** Subsequent `import` statements in other files simply retrieve the cached reference from `sys.modules`.
- To force re-execution, use `importlib.reload(module)`.

### 2. `sys.path` — The Module Search Path
When a module is not already cached in `sys.modules`, Python searches through the directories listed in `sys.path` in order:
1. The directory containing the input script (or current working directory if interactive).
2. Directories listed in the `PYTHONPATH` environment variable.
3. Standard library directories (e.g., `lib/python3.13`).
4. Third-party packages installed in `site-packages` (managed by `pip`).

```python
import sys
for p in sys.path:
    print(p)
```

## Modules vs. Packages

### 1. Module
A **module** is simply a single Python file with a `.py` extension containing definitions, functions, classes, and executable statements.

### 2. Regular Package
A **regular package** is a directory that contains Python modules and an `__init__.py` file:
```
my_package/
│── __init__.py
│── core.py
└── utils.py
```
- When `my_package` is imported, Python automatically executes `__init__.py`.
- `__init__.py` initializes package-level variables and controls what is exposed when importing `from my_package import *` via `__all__ = ["core", "utils"]`.

### 3. Namespace Package (PEP 420)
Since Python 3.3, directories without an `__init__.py` file are treated as **namespace packages**. This allows a single logical package to be split across different directories or zip files on `sys.path`.

## Absolute vs. Relative Imports

- **Absolute Imports**: Specify the full path from the project's root or installed packages. Recommended by PEP 8 for clarity:
  ```python
  from my_package.utils import format_text
  ```
- **Relative Imports**: Use leading dots to reference modules relative to the current module's position within a package:
  ```python
  from . import utils          # Sibling module
  from ..core import engine    # Parent package module
  ```
  Note: Relative imports only work inside packages (where `__name__` has a package prefix). Running a relative-import module directly with `python module.py` raises `ImportError: attempted relative import with no known parent package`. Run with `python -m package.module` instead.

## The Role of `if __name__ == "__main__":`

Every module in Python has a built-in string attribute called `__name__`:
- When a file is executed directly from the terminal (`python script.py`), Python sets `__name__ = "__main__"`.
- When a file is imported by another module (`import script`), Python sets `__name__ = "script"`.

```python
def main():
    print("Application running directly")

# This guard prevents the block from executing when imported as a library:
if __name__ == "__main__":
    main()
```

## Circular Imports: Causes and Solutions

A **circular import** occurs when Module A imports Module B, and Module B imports Module A (either directly or indirectly).

### Why it causes errors
When Module A is executing its top-level code and hits `import B`, execution of A pauses while B is loaded. If B tries to access an attribute from A that hasn't been defined yet, Python raises:
`AttributeError: partially initialized module 'A' has no attribute 'X'` or `ImportError: cannot import name 'X'`.

### Best Solutions:
1. **Refactor shared logic**: Move shared functions, models, or constants into a separate third module (e.g., `common.py` or `models.py`) imported by both.
2. **Import the module instead of the symbol**: Use `import A; A.foo()` instead of `from A import foo`. This defers the attribute lookup until runtime rather than compile/import time.
3. **Import inside function scope (deferred import)**: Move `import B` inside the specific function that uses it, deferring the import until after module initialization is complete.

## Frequently Asked Questions

**Q: How does Python's import system work?**
When Python encounters an `import` statement, it first checks `sys.modules` to see if the module has already been loaded. If not, it uses finders to search directories in `sys.path`. Once located, loaders read the file, compile it into bytecode, execute it in a new dictionary namespace, store the resulting module object in `sys.modules`, and bind the module name to the calling scope.

**Q: Why are Python modules only imported once?**
CPython caches every imported module in `sys.modules`. Any subsequent imports across any file in the application simply retrieve the existing module object from the cache, preventing redundant execution, improving performance, and preserving singleton module state.

**Q: What is the difference between a module and a package in Python?**
A module is a single `.py` file containing Python code. A package is a directory of modules that provides a hierarchical namespace, traditionally identified by containing an `__init__.py` file.

**Q: What causes circular import errors in Python and how do you fix them?**
Circular imports occur when two modules depend on each other. If module B tries to use attributes from module A while module A is still midway through importing B, partially initialized module errors occur. You can fix this by refactoring shared dependencies into a third independent module, importing the module name instead of individual attributes, or moving the import inside a function.
