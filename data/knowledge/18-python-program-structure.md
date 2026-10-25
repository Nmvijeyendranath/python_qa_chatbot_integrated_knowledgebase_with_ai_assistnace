# Python Program Structure — Syntax, Statements, and Execution Units

Sources:
- Official Python Documentation: https://docs.python.org/3/reference/lexical_analysis.html
- Language Reference — Simple Statements: https://docs.python.org/3/reference/simple_stmts.html
- Language Reference — Compound Statements: https://docs.python.org/3/reference/compound_stmts.html
- Python Tutorial — First Steps: https://docs.python.org/3/tutorial/introduction.html

## Basic Structure of a Python Program

A Python program is constructed from one or more logical lines of code grouped into **code blocks**. Unlike languages that use curly braces `{}` or keywords like `begin`/`end` to delimit blocks, Python uses indentation (whitespace) to define code structure.

### 1. Physical Lines vs. Logical Lines

- **Physical line**: A sequence of characters terminated by an end-of-line sequence (e.g., `\n` on Unix, `\r\n` on Windows).
- **Logical line**: A single syntactic statement in Python. A logical line can span multiple physical lines.

#### Implicit Line Joining
Lines enclosed within parentheses `()`, square brackets `[]`, or curly braces `{}` can be split across multiple physical lines without using a backslash. This is the recommended PEP 8 approach for long lines:

```python
# Implicit line joining (clean, recommended)
numbers = [
    1, 2, 3,
    4, 5, 6
]

result = calculate_metrics(
    temperature=72.5,
    pressure=101.3,
    humidity=0.45
)
```

#### Explicit Line Joining
Two or more physical lines may be joined into a logical line using a backslash character (`\`):

```python
total = 100 + \
        200 + \
        300
```

### 2. Indentation Semantics (INDENT and DEDENT)

Python's lexical analyzer (lexer) maintains an internal stack of indentation levels:
1. When encountering a line indented more than the current level, the lexer generates an `INDENT` token.
2. When the indentation level decreases, the lexer generates one or more `DEDENT` tokens.
3. Python requires consistent indentation within the same block. PEP 8 specifies **4 spaces per indentation level** and forbids mixing tabs and spaces.

```python
def check_status(value):      # Block 1 starts
    if value > 0:             # INDENT: Block 2 starts
        print("Positive")     # INDENT: Block 3
    else:                     # DEDENT then INDENT: Block 4
        print("Non-positive") # Inside Block 4
    print("Done")             # DEDENT: back in Block 1
```

### 3. Expressions vs. Statements

Understanding the distinction between expressions and statements is essential to Python's structure:

| Feature | Expression | Statement |
|---|---|---|
| **Definition** | A piece of code that evaluates to a value. | A complete unit of execution that performs an action or controls flow. |
| **Returns a value?** | Yes (always returns an object reference). | No (cannot be assigned to a variable). |
| **Examples** | `5 + 3`, `x > 10`, `math.sqrt(16)`, `[x * 2 for x in items]`, `lambda x: x + 1` | `x = 5`, `if condition:`, `for x in seq:`, `def func():`, `import os`, `return x` |
| **Can be embedded?** | Can be used inside statements, arguments, or other expressions. | Cannot be passed as a function argument or placed on the RHS of assignment. |

Note: Python 3.8 introduced the "walrus operator" (`:=`), also called an **assignment expression**, which allows assignment inside an expression:
```python
if (n := len(items)) > 10:
    print(f"List is too long: {n} items")
```

### 4. Simple Statements vs. Compound Statements

#### Simple Statements
A simple statement is comprised within a single logical line. Several simple statements may occur on a single line separated by semicolons (though PEP 8 discourages this):
- **Assignment**: `x = 42`
- **Expression statement**: `print("Hello")`
- **Control**: `return`, `break`, `continue`, `pass`, `yield`
- **Module and scope**: `import math`, `global total`, `nonlocal counter`
- **Assertion**: `assert x > 0, "x must be positive"`
- **Deletion**: `del items[0]`

#### Compound Statements
Compound statements contain and control the execution of other statements (groups of statements). They consist of one or more "clauses" followed by an indented suite of statements:
- `if ... elif ... else`
- `while ... else`
- `for ... in ... else`
- `try ... except ... else ... finally`
- `with ... as ...` (context managers)
- `def func(...):` (function definition)
- `class MyClass:` (class definition)
- `match ... case:` (pattern matching introduced in Python 3.10)

### 5. Code Blocks and Execution Units

A **code block** is a piece of Python program text executed as a single unit. In CPython, each code block corresponds to a single code object:
- A Python module file (`.py`).
- A function body or lambda expression.
- A class definition body.
- A script passed via the `-c` command-line option.
- A single interactive command entered into the REPL.

When a code block executes, Python allocates an **execution frame** (`PyFrameObject`) on the call stack containing the local namespace, reference to global namespace, and evaluation stack.

## Frequently Asked Questions

**Q: What is the basic structure of a Python program?**
A Python program consists of modules, code blocks, statements, and expressions organized hierarchically. It uses logical lines separated by indentation levels (`INDENT` and `DEDENT` tokens) to structure nested control flow and function/class bodies instead of braces or explicit keywords.

**Q: What is the difference between an expression and a statement in Python?**
An expression evaluates to an object/value and can be used anywhere a value is expected (e.g. `2 + 2`, `func(x)`). A statement represents an action or structure (e.g. `x = 5`, `for item in items:`, `return`) and cannot be assigned or passed as an argument.

**Q: How does Python handle indentation and line structure?**
Python treats whitespace at the beginning of a line as syntax. The tokenizer uses a stack to compare indentation depth, emitting `INDENT` when indentation increases and `DEDENT` when it decreases. PEP 8 standardizes on 4 spaces per indentation level.

**Q: What is a code block in Python?**
A code block is a distinct syntactic unit that compiles into its own code object and runs within its own execution frame with its own local scope. Modules, function bodies, and class definitions are the three primary types of code blocks in Python.
