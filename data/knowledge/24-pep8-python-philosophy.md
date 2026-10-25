# Python Philosophy, PEP 8, and Pythonic Idioms

Sources:
- PEP 8 — Style Guide for Python Code: https://peps.python.org/pep-0008/
- PEP 20 — The Zen of Python: https://peps.python.org/pep-0020/
- PEP 257 — Docstring Conventions: https://peps.python.org/pep-0257/
- Python Tutorial — Coding Style: https://docs.python.org/3/tutorial/controlflow.html#intermezzo-coding-style
- Real Python — How to Write Beautiful Python Code With PEP 8: https://realpython.com/python-pep8/

## The Zen of Python (PEP 20)

Python's design philosophy emphasizes readability, simplicity, and explicitness. You can read the guiding aphorisms directly in any Python interpreter by typing `import this`:

Key principles of PEP 20:
- **"Beautiful is better than ugly."** Code should be visually clean and pleasant to read.
- **"Explicit is better than implicit."** Do not hide behavior; make dependencies and transformations obvious.
- **"Simple is better than complex."** Strive for straightforward logic over convoluted architectures.
- **"Complex is better than complicated."** If complexity is unavoidable, keep it modular and understandable.
- **"Readability counts."** Code is read much more often than it is written.
- **"Special cases aren't special enough to break the rules."** Consistency is paramount.
- **"There should be one-- and preferably only one --obvious way to do it."** Avoid redundant language features.
- **"If the implementation is hard to explain, it's a bad idea."**

## PEP 8 — The Official Style Guide

PEP 8 is the primary standard for formatting and structuring Python code.

### 1. Code Layout and Indentation
- **Indentation**: Use exactly **4 spaces** per indentation level. Never mix tabs and spaces.
- **Line Length**: Limit lines to a maximum of **79 characters** for code, and **72 characters** for docstrings and comments.
- **Blank Lines**:
  - Surround top-level function and class definitions with **two blank lines**.
  - Method definitions inside a class are surrounded by a **single blank line**.
  - Use blank lines sparingly inside functions to indicate logical sections.

### 2. Naming Conventions

| Identifier | Convention | Example | Notes |
|---|---|---|---|
| **Packages and Modules** | Short, all-lowercase, no underscores | `numpy`, `email`, `qa_chatbot` | Underscores allowed if needed for readability in modules. |
| **Classes** | PascalCase (CapWords) | `DataTransformer`, `UserAccount` | Same for exception classes (should end in `Error`). |
| **Functions & Methods** | snake_case | `calculate_total()`, `get_user_by_id()` | Lowercase with words separated by underscores. |
| **Variables & Attributes** | snake_case | `user_count`, `active_session` | Descriptive, readable names. |
| **Constants** | UPPER_CASE_SNAKE | `MAX_CONNECTIONS`, `DEFAULT_TIMEOUT` | Defined at module level. |
| **Internal/Private** | Leading underscore | `_internal_cache`, `_calculate()` | Signals non-public API; ignored by `from module import *`. |
| **Name Mangling** | Double leading underscore | `__private_attr` | Mangled to `_ClassName__private_attr` to prevent accidental subclass collision. |
| **Special/Magic** | Dunder (double leading & trailing) | `__init__`, `__str__`, `__len__` | Reserved for language protocols; do not invent your own dunders. |

### 3. Imports Formatting and Ordering
Imports should always be at the top of the file, immediately after module comments and docstrings. Group imports in the following order, separated by a blank line:

```python
# 1. Standard library imports
import os
import sys
from pathlib import Path

# 2. Related third-party imports
import numpy as np
import pandas as pd
from fastapi import FastAPI

# 3. Local application/library specific imports
from qa_chatbot.core import Retriever
from qa_chatbot.llm import create_provider
```

Avoid wildcard imports (`from math import *`), as they pollute the local namespace and obscure where symbols originated.

## Pythonic Idioms: EAFP vs. LBYL

Python strongly favors the **EAFP** philosophy over **LBYL**:

### EAFP: "Easier to Ask for Forgiveness than Permission"
Assume an operation will succeed and catch the exception if it fails. This is the idiomatic Python approach:

```python
# Pythonic (EAFP) — cleaner, faster in happy path, thread-safe:
try:
    value = mapping[key]
except KeyError:
    value = default_value
```

### LBYL: "Look Before You Leap"
Exhaustively checking preconditions before performing an action (common in C and Java):

```python
# Un-Pythonic (LBYL) — checks key twice, vulnerable to race conditions:
if key in mapping:
    value = mapping[key]
else:
    value = default_value
```

## Pythonic Truthiness

Python evaluates empty containers, zero values, and `None` as falsy in boolean contexts. Avoid comparing explicitly with empty lists or `len() == 0`:

```python
# Pythonic:
items = []
if not items:
    print("List is empty")

# Un-Pythonic:
if len(items) == 0:
    print("List is empty")
```

## Frequently Asked Questions

**Q: What is PEP 8 and why is it important in Python?**
PEP 8 is Python's official style guide. It ensures visual consistency, clarity, and readability across Python codebases worldwide. Adhering to PEP 8 makes code easier to read, maintain, and collaborate on.

**Q: What is The Zen of Python (PEP 20)?**
The Zen of Python is a set of 19 guiding principles written by Tim Peters that influence the design of Python itself and the coding philosophy of Python developers. It advocates for explicitness, simplicity, readability, and pragmatism.

**Q: What is the difference between EAFP and LBYL in Python?**
EAFP (Easier to Ask for Forgiveness than Permission) assumes an operation works and catches exceptions if it doesn't, which is idiomatic and thread-safe in Python. LBYL (Look Before You Leap) explicitly checks preconditions before attempting an action.

**Q: What are the main naming conventions in PEP 8?**
Functions, methods, and variables use `snake_case`. Classes use `PascalCase`. Constants use `UPPER_CASE_SNAKE`. Modules use short lowercase names. Non-public attributes use a leading underscore `_name`.
