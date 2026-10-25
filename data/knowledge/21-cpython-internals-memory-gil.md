# CPython Internals — Memory Management, Garbage Collection, and the GIL

Sources:
- Official Python Documentation — Garbage Collector: https://docs.python.org/3/library/gc.html
- Python C API — Memory Management: https://docs.python.org/3/c-api/memory.html
- Python Glossary — Global Interpreter Lock (GIL): https://docs.python.org/3/glossary.html#term-global-interpreter-lock
- Real Python — Python Memory Management: https://realpython.com/python-memory-management/
- Real Python — What is the Python Global Interpreter Lock (GIL)?: https://realpython.com/python-gil/

## CPython Memory Architecture

In standard CPython, memory management is structured in multiple layers to prevent operating system overhead and heap fragmentation:

```
┌────────────────────────────────────────────────────────┐
│ Layer 3: Object-specific allocators (int, str, dict)   │
├────────────────────────────────────────────────────────┤
│ Layer 2: Python Small Object Allocator (pymalloc)      │
│   Arenas (256 KB) -> Pools (4 KB) -> Blocks (<= 512 B) │
├────────────────────────────────────────────────────────┤
│ Layer 1: Python Raw Memory Allocator (malloc / free)   │
├────────────────────────────────────────────────────────┤
│ Layer 0: OS Virtual Memory / C Runtime Heap            │
└────────────────────────────────────────────────────────┘
```

### PyMalloc: Small Object Allocator
Because Python programs constantly create and destroy thousands of small objects, repeatedly calling the OS `malloc()` would cause severe heap fragmentation. CPython uses **pymalloc** for allocations $\le 512$ bytes:
- **Arenas**: Large chunks of 256 KB memory allocated from the OS heap.
- **Pools**: 4 KB subdivisions within an arena, dedicated to objects of a single fixed size class (e.g., 32-byte blocks).
- **Blocks**: The actual memory slot holding a Python object.

Large allocations ($> 512$ bytes) bypass pymalloc and go directly to the standard C library `malloc()`.

## Memory Reclamation: Reference Counting

CPython's primary memory management system is **reference counting**. Every Python object structure (`PyObject` in C) includes an internal counter field named `ob_refcnt`:
- When an object is created or assigned to a new variable name, its reference count increases.
- When an object is passed into a function, added to a container (list, dict), or referenced, its count increases.
- When a variable name goes out of scope, is reassigned, or deleted with `del`, its count decreases.
- **Immediate Deallocation**: The exact instant `ob_refcnt` drops to zero, the object's memory is deallocated immediately. There is no waiting for a collection pause.

You can check an object's reference count using `sys.getrefcount(obj)` (note: passing the object to `getrefcount()` increases its count by 1 temporarily):

```python
import sys

x = [1, 2, 3]
print(sys.getrefcount(x))  # 2 (x + argument to getrefcount)

y = x
print(sys.getrefcount(x))  # 3 (x + y + argument)

del y
print(sys.getrefcount(x))  # 2
```

## The Cyclic Garbage Collector (`gc` Module)

While reference counting is fast and deterministic, it has one major limitation: **it cannot detect reference cycles (circular references)**.

```python
# A circular reference:
class Node:
    def __init__(self):
        self.partner = None

a = Node()
b = Node()
a.partner = b
b.partner = a

del a
del b
# 'a' and 'b' still point to each other! Their ref counts are 1, but they are unreachable!
```

To solve this, CPython includes a secondary **cyclic garbage collector** managed via the `gc` module:
- It only inspects container objects (lists, tuples, dicts, custom class instances) that can hold references to other objects. Non-container types (integers, strings) are never tracked.
- It uses a **tri-color marking algorithm** to find unreachable groups of objects that reference each other.

### Generational Collection
The cyclic GC categorizes objects into **three generations (0, 1, and 2)** based on survival age:
- **Generation 0**: Newly allocated container objects. Collected most frequently.
- **Generation 1**: Objects that have survived a Gen 0 collection.
- **Generation 2**: Long-lived objects that have survived Gen 1 collections. Collected least frequently.

The collection threshold can be checked with `gc.get_threshold()` (typically `(700, 10, 10)`). When allocations exceed deallocations by 700 in Generation 0, a collection is triggered.

```python
import gc

print(gc.get_threshold())  # (700, 10, 10)
unreachable = gc.collect()  # Manually run full collection
print(f"Collected {unreachable} unreachable cyclic objects")
```

## The Global Interpreter Lock (GIL)

### What is the GIL?
The **Global Interpreter Lock (GIL)** is a mutex (mutual exclusion lock) used by CPython to prevent multiple native OS threads from executing Python bytecode simultaneously.

### Why does Python have the GIL?
1. **Thread safety for reference counting**: Because every variable access or container operation modifies `ob_refcnt`, without the GIL, every single reference count operation would require its own mutex lock, causing catastrophic performance overhead for single-threaded code.
2. **Easy C extension integration**: Third-party C libraries can easily interface with Python objects without needing complex fine-grained locking.
3. **Simplicity**: Single-threaded execution speed and language implementation simplicity.

### Concurrency Implications: CPU-Bound vs. I/O-Bound

| Concurrency Model | CPU-Bound Performance (Math, ML, Compression) | I/O-Bound Performance (Network requests, Disk I/O, DB queries) |
|---|---|---|
| **Python `threading`** | **No speedup** (only 1 thread runs Python bytecode at a time due to GIL; context switching may even slow it down). | **Excellent speedup** (threads automatically release the GIL while waiting for network/socket/file operations). |
| **`multiprocessing`** | **True parallelism across all CPU cores** (spawns separate OS processes, each with its own independent Python interpreter, memory space, and GIL). | Good, but incurs process spawning and IPC (inter-process communication) serialization overhead. |
| **`asyncio`** | **No parallelism** (single-threaded cooperative event loop). | **Superb scalability** (handles tens of thousands of concurrent network connections with minimal memory overhead). |

### Releasing the GIL
The GIL is automatically released during:
- Blocking I/O operations (`socket.recv`, file reads/writes, `time.sleep`).
- Heavy numerical calculations in C extensions like **NumPy**, SciPy, or PyTorch, allowing multi-core C/Fortran routines to run in true parallel.

### Python 3.13 Free-Threaded Mode (PEP 703)
Python 3.13 introduced experimental support for running CPython without the GIL (free-threaded builds). This replaces the global lock with mimalloc-based thread-local allocators and biased reference counting, allowing true multi-core parallel Python threads.

## Frequently Asked Questions

**Q: How does Python manage memory?**
Python uses a two-pronged memory management system:
1. **Reference Counting**: Primary mechanism. Every object tracks how many references point to it and is instantly freed when its count drops to zero.
2. **Cyclic Garbage Collector**: Secondary mechanism. A generational GC runs periodically to detect and reclaim isolated circular reference cycles that reference counting alone cannot collect.
Additionally, CPython uses `pymalloc` to allocate memory in pools and arenas to avoid OS heap fragmentation for small objects.

**Q: What is the GIL (Global Interpreter Lock) in Python and why does it exist?**
The GIL is a mutex in CPython that ensures only one native OS thread executes Python bytecode at any given moment. It exists primarily to safeguard CPython's memory management and reference counting from race conditions, and to maximize single-threaded execution performance and simplify C library extensions.

**Q: Why doesn't multithreading speed up CPU-bound tasks in Python?**
Because the GIL serializes execution of Python bytecode across all threads. Even on a machine with 16 CPU cores, only one thread can execute Python instructions at a time. For CPU-bound tasks, use the `multiprocessing` module or release the GIL in C/C++ extensions or NumPy.

**Q: When should you use `threading` vs `multiprocessing` in Python?**
Use `threading` or `asyncio` for **I/O-bound** tasks (such as downloading web pages, reading files, or calling APIs) where threads release the GIL during network wait. Use `multiprocessing` for **CPU-bound** tasks (such as data processing, machine learning training, or image manipulation) to distribute workloads across multiple CPU cores.
