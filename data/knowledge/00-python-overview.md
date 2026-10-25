# Python Language Overview
Source: https://docs.python.org/3/tutorial/introduction.html

## What Python is
Python is a high-level, general-purpose programming language. It is dynamically typed, and its readable syntax supports scripting, automation, web services, scientific computing, data analysis, and application development. The Python language is specified independently of any one implementation; CPython is the most widely used implementation.

## Why people use Python
Python emphasizes readable code and a large standard library. It supports procedural, object-oriented, and functional programming styles. The package ecosystem adds tools for web development, testing, data processing, machine learning, and scientific work.

## How a Python program runs
A developer writes source code, usually in a `.py` file. The Python implementation parses and executes it. CPython compiles source to bytecode and runs that bytecode on its virtual machine; it may cache bytecode in `__pycache__`. Python can run a script from a terminal or execute statements interactively in the REPL.

```python
print("Hello, Python!")
```

Run a file from a terminal with `python hello.py` (on some systems, use `python3 hello.py`). The exact command depends on how Python is installed.

## A tiny example

```python
def greet(name: str) -> str:
    return f"Hello, {name}!"

print(greet("Ada"))
```

This example defines a function, accepts a string argument, returns a formatted string, and prints the result.

## Official tutorial
The official Python tutorial introduces the language, its data structures, control flow, functions, modules, exceptions, classes, and virtual environments: https://docs.python.org/3/tutorial/
