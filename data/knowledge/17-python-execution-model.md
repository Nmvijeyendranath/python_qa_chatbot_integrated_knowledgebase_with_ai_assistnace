# Python Execution Model — How Python Actually Runs

Sources:
- Official Python Documentation: https://docs.python.org/3/reference/executionmodel.html
- Python Tutorial: https://docs.python.org/3/tutorial/interpreter.html
- Python Glossary: https://docs.python.org/3/glossary.html
- Real Python: https://realpython.com/cpython-source-code-guide/

## How Python Actually Runs

Python is commonly described as an "interpreted" language, but under the hood, standard Python (CPython) is both **compiled** and **interpreted**. When you execute a Python script or command, CPython executes it through a multi-stage pipeline:

```
Source Code (.py)
       │
       ▼ (Lexical Analysis & Parsing)
Abstract Syntax Tree (AST)
       │
       ▼ (Bytecode Compilation)
Bytecode (.pyc / code objects)
       │
       ▼ (Evaluation Loop / ceval.c)
Python Virtual Machine (PVM)
       │
       ▼ (Machine Instructions)
CPU / Operating System
```

### Stage 1: Lexical Analysis and Tokenization
The CPython tokenizer (`Parser/tokenizer.c` or the `tokenize` module) reads the raw source code text and breaks it into discrete units called **tokens** (keywords, identifiers, literals, operators, `NEWLINE`, `INDENT`, `DEDENT`).

### Stage 2: Parsing and Abstract Syntax Tree (AST)
The parser transforms the stream of tokens into a tree data structure called an **Abstract Syntax Tree (AST)** according to Python's PEG grammar (`Grammar/python.gram`). The AST represents the syntactic structure of the program independent of formatting and whitespace. You can inspect this tree using the standard library `ast` module:

```python
import ast
tree = ast.parse("x = 10 + 20")
print(ast.dump(tree, indent=2))
```

### Stage 3: Bytecode Compilation
CPython's compiler traverses the AST and generates **bytecode**, which is an intermediate, platform-independent instruction set. Bytecode is stored in a **code object** (`types.CodeType`). A code object contains:
- `co_code`: the raw bytecode bytes.
- `co_varnames`: names of local variables.
- `co_consts`: literal constants used in the code block.
- `co_names`: global names and attribute names referenced.

You can inspect the bytecode using the standard library `dis` module:

```python
import dis

def add(a, b):
    return a + b

dis.dis(add)
```

Example bytecode disassembly:
```
  2           0 RESUME                   0
              2 LOAD_FAST                0 (a)
              4 LOAD_FAST                1 (b)
              6 BINARY_OP                0 (+)
             10 RETURN_VALUE
```

### Stage 4: Bytecode Caching (`.pyc` and `__pycache__`)
When a Python module is imported, CPython automatically writes the compiled bytecode to disk inside a `__pycache__/` directory with the `.pyc` extension (e.g., `module.cpython-313.pyc`).
- The `.pyc` file contains a header with a magic number (indicating the Python version) and a timestamp or hash of the original `.py` source file.
- If the source file has not changed since the last run, CPython skips the parsing and compilation stages entirely and loads the cached bytecode directly into memory.
- Note: Top-level scripts executed directly (e.g., `python main.py`) are not cached to `.pyc` by default, but imported modules always are.

### Stage 5: Execution by the Python Virtual Machine (PVM)
The Python Virtual Machine (PVM) is the execution engine of CPython. It is not an actual hardware emulator (like VMware or VirtualBox); rather, it is a stack-based virtual machine written in C.
The core of the PVM is the bytecode evaluation loop located in `Python/ceval.c`. It sequentially pops instructions from the code object and operates on an internal value stack:
1. Pushing and popping objects onto the evaluation stack (`LOAD_FAST`, `LOAD_GLOBAL`, `STORE_FAST`).
2. Invoking C functions for operators (`BINARY_OP`, `COMPARE_OP`).
3. Calling functions and creating new call frames (`CALL`, `RETURN_VALUE`).

## CPython vs Other Python Implementations

"Python" is a language specification. CPython is the standard reference implementation written in C:

| Implementation | Written In | Execution Engine | Key Characteristics |
|---|---|---|---|
| **CPython** | C | Stack-based PVM | Reference implementation; supports C extensions; contains the GIL. |
| **PyPy** | RPython | JIT (Just-In-Time) Compiler | Compiles hot bytecode loops directly to native x86/ARM machine code; often 4x-10x faster for long-running CPU loops. |
| **Jython** | Java | JVM (Java Virtual Machine) | Compiles Python to Java bytecode; seamlessly integrates with Java classes; no GIL. |
| **IronPython** | C# | .NET CLR (Common Language Runtime) | Integrates with Microsoft .NET libraries. |
| **MicroPython** | C | Lightweight VM | Designed for microcontrollers and embedded systems with minimal RAM. |

## Ways to Run Python Code

Python provides several execution modes:

1. **Script Mode**:
   ```bash
   python script.py
   ```
   Runs the file directly from top to bottom. The module is assigned the special name `__name__ = "__main__"`.

2. **Module Mode**:
   ```bash
   python -m package.module
   ```
   Searches `sys.path` for the module or package, compiles it, and runs it as top-level code. Essential for executing modules that rely on package-relative imports.

3. **Interactive REPL (Read-Eval-Print Loop)**:
   ```bash
   python
   ```
   Reads user input line-by-line, compiles each statement on the fly, evaluates it in the current global namespace, and prints any non-None expression results.

4. **Inline Command**:
   ```bash
   python -c "import sys; print(sys.version)"
   ```
   Executes a string command directly from the shell without requiring a file.

## Frequently Asked Questions

**Q: How does Python actually run?**
Python executes code in two main phases: compilation and interpretation. First, the CPython interpreter reads the `.py` source code, breaks it into tokens, and compiles it into an Abstract Syntax Tree (AST), which is then translated into platform-independent intermediate instructions called **bytecode**. Second, the Python Virtual Machine (PVM)—a stack-based evaluation engine written in C—executes this bytecode instruction by instruction on the CPU.

**Q: Is Python compiled or interpreted?**
Python is both. Python code is never executed directly as raw text; it is always first compiled into bytecode (stored in `.pyc` files in `__pycache__`). That bytecode is then interpreted and executed by the Python Virtual Machine (PVM).

**Q: What is the Python Virtual Machine (PVM)?**
The PVM is the runtime engine of CPython. It is a stack-oriented evaluation loop in C (`ceval.c`) that iterates through bytecode instructions, allocates memory, calls underlying C functions and system libraries, and manages object lifecycles.

**Q: What is the difference between Python and CPython?**
Python is the programming language specification (syntax, keywords, grammar, standard library definitions). CPython is the official, default implementation of Python written in C, maintained by the Python Software Foundation (PSF).

**Q: What happens when you execute `python script.py`?**
1. The OS starts the `python` executable process.
2. CPython initializes its runtime environment (built-in types, `sys.modules`, `__builtin__` functions, memory allocators).
3. `script.py` is read into memory, tokenized, parsed into an AST, and compiled into bytecode code objects.
4. A new execution frame (`PyFrameObject`) is created with `__name__` set to `"__main__"`.
5. The PVM evaluation loop executes the bytecode from top to bottom until completion or an unhandled exception occurs.
