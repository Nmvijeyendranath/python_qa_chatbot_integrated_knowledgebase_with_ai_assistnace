# File Handling, Modules, Packages, and Virtual Environments

Source: https://docs.python.org/3/tutorial/inputoutput.html

## Reading and Writing Files

```python
# Write a file
with open("data.txt", "w", encoding="utf-8") as f:
    f.write("Hello, World!\n")
    f.writelines(["Line 2\n", "Line 3\n"])

# Read entire file
with open("data.txt", "r", encoding="utf-8") as f:
    content = f.read()
    print(content)

# Read line by line (memory-efficient for large files)
with open("data.txt") as f:
    for line in f:
        print(line.strip())

# Read all lines into a list
with open("data.txt") as f:
    lines = f.readlines()   # includes newline characters
```

### File Modes

| Mode | Meaning                                      |
|------|----------------------------------------------|
| `r`  | Read (default). File must exist.             |
| `w`  | Write. Creates or truncates file.            |
| `a`  | Append. Creates if not exists.               |
| `x`  | Exclusive create. Fails if file exists.      |
| `b`  | Binary mode (combine: `rb`, `wb`)            |
| `+`  | Update (read+write) mode (combine: `r+`)     |

### pathlib — Modern File Path Handling

```python
from pathlib import Path

p = Path("data") / "output" / "result.csv"   # cross-platform path
p.parent.mkdir(parents=True, exist_ok=True)  # create directories

p.write_text("a,b,c\n1,2,3\n", encoding="utf-8")
text = p.read_text(encoding="utf-8")

print(p.name)       # result.csv
print(p.stem)       # result
print(p.suffix)     # .csv
print(p.parent)     # data/output
print(p.exists())   # True
print(p.is_file())  # True
print(p.stat().st_size)  # file size in bytes

# Glob for matching files
for csv_file in Path("data").glob("**/*.csv"):
    print(csv_file)
```

### JSON, CSV, and Binary Files

```python
import json

data = {"name": "Alice", "scores": [95, 87, 92]}

# Write JSON
with open("data.json", "w") as f:
    json.dump(data, f, indent=2)

# Read JSON
with open("data.json") as f:
    loaded = json.load(f)

# From/to string
json_str = json.dumps(data)
parsed   = json.loads(json_str)

# CSV
import csv

rows = [["name", "age"], ["Alice", 30], ["Bob", 25]]
with open("people.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(rows)

with open("people.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(row["name"], row["age"])

# Binary
with open("image.png", "rb") as f:
    data = f.read()
```

## Modules

A module is a `.py` file. Import it with `import`:

```python
# math_utils.py
def add(a, b):
    return a + b

PI = 3.14159
```

```python
# main.py
import math_utils
print(math_utils.add(1, 2))  # 3
print(math_utils.PI)         # 3.14159

# Import specific names
from math_utils import add, PI
print(add(1, 2))             # 3

# Alias
import math_utils as mu
print(mu.add(1, 2))

# Import all (avoid in production code — pollutes namespace)
from math_utils import *
```

### `if __name__ == "__main__":`

```python
# script.py
def compute(n):
    return n ** 2

if __name__ == "__main__":
    # This block runs only when the file is executed directly,
    # not when it is imported as a module.
    print(compute(5))
```

### Standard Library Modules

```python
import os
import sys
import re
import json
import math
import random
import datetime
import time
import collections
import itertools
import functools
import pathlib
import subprocess
import threading
import logging
import unittest
import argparse
import shutil
import tempfile
import hashlib
import urllib.request
import http.client
```

## Packages

A package is a directory with an `__init__.py` file:

```
mypackage/
├── __init__.py
├── utils.py
└── subpkg/
    ├── __init__.py
    └── helpers.py
```

```python
# Importing from a package
from mypackage import utils
from mypackage.subpkg import helpers
from mypackage.utils import some_function
```

### `__init__.py`

Controls what `from mypackage import *` exports and can expose a public API:

```python
# mypackage/__init__.py
from .utils import some_function
from .subpkg.helpers import helper_fn

__all__ = ["some_function", "helper_fn"]
```

## pip — Package Manager

```bash
# Install a package
pip install requests

# Install specific version
pip install requests==2.31.0

# Install from requirements file
pip install -r requirements.txt

# Generate requirements file
pip freeze > requirements.txt

# Upgrade
pip install --upgrade requests

# Uninstall
pip uninstall requests

# Show installed packages
pip list
pip show requests
```

## Virtual Environments

Isolate project dependencies:

```bash
# Create
python -m venv .venv

# Activate (Windows PowerShell)
.venv\Scripts\Activate.ps1

# Activate (Windows CMD)
.venv\Scripts\activate.bat

# Activate (Linux/macOS)
source .venv/bin/activate

# Deactivate
deactivate

# Install in virtual env
pip install fastapi uvicorn

# Check Python location
which python   # or: where python (Windows)
```

### pyproject.toml (Modern Standard)

```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "my-package"
version = "1.0.0"
requires-python = ">=3.10"
dependencies = [
    "fastapi>=0.110",
    "httpx>=0.27",
]

[project.optional-dependencies]
dev = ["pytest>=8", "ruff", "mypy"]

[project.scripts]
my-tool = "my_package.cli:main"
```

## Environment Variables

```python
import os
from dotenv import load_dotenv  # pip install python-dotenv

load_dotenv()   # loads .env file into environment

api_key = os.getenv("API_KEY")          # None if missing
api_key = os.getenv("API_KEY", "dev")   # default if missing
api_key = os.environ["API_KEY"]         # KeyError if missing
```

## Common Errors

```python
# ModuleNotFoundError
import nonexistent_module   # ModuleNotFoundError: No module named 'nonexistent_module'
# Fix: pip install package-name in your virtual environment

# ImportError: circular imports
# a.py imports b.py and b.py imports a.py at module level → ImportError
# Fix: move the import inside the function, or refactor to avoid the cycle

# FileNotFoundError
open("missing.txt")   # FileNotFoundError: [Errno 2] No such file or directory
# Fix: check Path("missing.txt").exists() first

# PermissionError
open("/etc/shadow", "w")   # PermissionError: [Errno 13] Permission denied
```

## Frequently Asked Questions

**Q: What is the difference between `import module` and `from module import name`?**
`import module` imports the module object; you access names via `module.name`. `from module import name` imports the name directly into the current namespace.

**Q: Should I use `requirements.txt` or `pyproject.toml`?**
Modern projects should use `pyproject.toml` (PEP 517/518/621). `requirements.txt` is still common for deployment pinning. Both can coexist.

**Q: What is the difference between a module and a package?**
A module is a single `.py` file. A package is a directory containing an `__init__.py` and one or more modules/sub-packages.

**Q: How do I share data between modules?**
The cleanest approach is to pass data explicitly through function parameters and return values. A module-level constant is acceptable for truly shared configuration.
