# Data Structures — Lists, Tuples, Sets, Dictionaries, and Slicing

Source: https://docs.python.org/3/tutorial/datastructures.html

## Lists

Lists are ordered, mutable sequences that allow duplicates.

```python
fruits = ["apple", "banana", "cherry"]
mixed  = [1, "two", 3.0, True, None]
nested = [[1, 2], [3, 4]]
empty  = []
```

### Common List Operations

```python
fruits = ["apple", "banana", "cherry"]

# Access
print(fruits[0])    # apple
print(fruits[-1])   # cherry (negative indexing from end)

# Modify
fruits[1] = "mango"
print(fruits)       # ['apple', 'mango', 'cherry']

# Length
print(len(fruits))  # 3

# Membership
print("apple" in fruits)  # True
```

### List Methods

```python
lst = [3, 1, 4, 1, 5, 9, 2, 6]

lst.append(7)         # add to end
lst.insert(0, 0)      # insert at index 0
lst.extend([8, 9])    # add multiple elements

lst.remove(1)         # remove first occurrence of value 1
popped = lst.pop()    # remove and return last element
popped = lst.pop(2)   # remove and return element at index 2

lst.sort()                        # sort in place
lst.sort(key=lambda x: -x)        # sort descending
sorted_copy = sorted(lst)         # returns new sorted list

lst.reverse()         # reverse in place
lst.index(9)          # index of first occurrence
lst.count(1)          # count occurrences
lst.clear()           # remove all elements
copy = lst.copy()     # shallow copy
```

### List Slicing

`list[start:stop:step]` — stop is exclusive.

```python
lst = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

print(lst[2:5])     # [2, 3, 4]
print(lst[:3])      # [0, 1, 2]
print(lst[7:])      # [7, 8, 9]
print(lst[::2])     # [0, 2, 4, 6, 8]  every second
print(lst[::-1])    # [9, 8, 7, ..., 0] reversed
print(lst[-3:])     # [7, 8, 9] last three
print(lst[1:8:3])   # [1, 4, 7]

# Slice assignment
lst[1:4] = [10, 20, 30]
print(lst)          # [0, 10, 20, 30, 4, 5, 6, 7, 8, 9]
```

### Copying Lists

```python
original = [[1, 2], [3, 4]]

# Shallow copy — nested lists still share references
shallow = original.copy()         # or original[:]  or list(original)
shallow[0].append(99)
print(original[0])  # [1, 2, 99]  ← affected

# Deep copy — fully independent
import copy
deep = copy.deepcopy(original)
deep[0].append(99)
print(original[0])  # [1, 2]  ← not affected
```

## Tuples

Tuples are ordered, **immutable** sequences. Use parentheses (or no brackets):

```python
point = (3, 5)
rgb   = (255, 128, 0)
single = (42,)   # comma required for single-element tuple
empty  = ()

# Packing and unpacking
x, y = point
print(x, y)      # 3 5

# Extended unpacking
first, *rest = [1, 2, 3, 4, 5]
print(first)  # 1
print(rest)   # [2, 3, 4, 5]

# Swapping variables
a, b = 1, 2
a, b = b, a
print(a, b)   # 2 1
```

Tuples are faster than lists for read-only data and can be used as dictionary keys or set members (lists cannot).

```python
# Named tuples for readable, self-documenting code
from collections import namedtuple
Point = namedtuple("Point", ["x", "y"])
p = Point(3, 5)
print(p.x, p.y)   # 3 5
print(p[0])        # 3
```

## Sets

Sets are unordered collections of unique, hashable elements.

```python
s = {1, 2, 3, 3, 4}
print(s)          # {1, 2, 3, 4}  — duplicates removed

empty_set = set()  # NOT {} — that's an empty dict!
```

### Set Operations

```python
a = {1, 2, 3, 4}
b = {3, 4, 5, 6}

print(a | b)   # {1,2,3,4,5,6}  union
print(a & b)   # {3, 4}          intersection
print(a - b)   # {1, 2}          difference (in a not b)
print(a ^ b)   # {1,2,5,6}       symmetric difference

# Methods
a.add(5)
a.discard(99)   # no error if missing
a.remove(1)     # KeyError if missing
a.update({7, 8})
print(a.issubset({1,2,3,4,5,6,7,8}))   # True
print(a.issuperset({3, 4}))             # True
print(a.isdisjoint({10, 11}))           # True
```

`frozenset` is an immutable set (hashable, can be a dict key):

```python
fs = frozenset([1, 2, 3])
d = {fs: "value"}   # valid
```

## Dictionaries

Dicts map unique, hashable keys to values. **Ordered by insertion** since Python 3.7.

```python
person = {"name": "Alice", "age": 30, "city": "London"}
empty  = {}
```

### Common Dict Operations

```python
d = {"a": 1, "b": 2, "c": 3}

# Access
print(d["a"])         # 1
print(d.get("z"))     # None (no KeyError)
print(d.get("z", 0))  # 0 (default value)

# Modify
d["d"] = 4
d.update({"e": 5, "f": 6})

# Delete
del d["a"]
popped = d.pop("b")           # removes and returns
last   = d.popitem()          # removes last inserted pair

# Check membership
print("c" in d)   # True — checks keys only
```

### Iterating Dicts

```python
d = {"x": 10, "y": 20, "z": 30}

for key in d:                    # keys
    print(key)

for key, value in d.items():     # key-value pairs
    print(f"{key} = {value}")

for value in d.values():         # values only
    print(value)
```

### Dict Comprehensions and Merging

```python
squares = {x: x**2 for x in range(1, 6)}
# {1: 1, 2: 4, 3: 9, 4: 16, 5: 25}

# Filter
even_squares = {k: v for k, v in squares.items() if v % 2 == 0}

# Merge dicts (Python 3.9+)
a = {"x": 1}
b = {"y": 2}
merged = a | b       # {x:1, y:2}
a |= b               # in-place merge

# Merge (Python 3.5+)
merged = {**a, **b}  # unpack and merge
```

### defaultdict, Counter, OrderedDict

```python
from collections import defaultdict, Counter, OrderedDict

# defaultdict: missing keys get a default value
word_count = defaultdict(int)
for word in "the quick brown fox jumps over the fox".split():
    word_count[word] += 1

# Counter: most_common(), arithmetic
c = Counter("abracadabra")
print(c.most_common(3))  # [('a', 5), ('b', 2), ('r', 2)]

# OrderedDict: insertion order preserved (already default in 3.7+)
# Still useful for move_to_end() and equality checks that consider order
```

## Comparing Data Structures

| Feature          | list | tuple | set | dict |
|------------------|------|-------|-----|------|
| Ordered          | ✓    | ✓     | ✗   | ✓    |
| Mutable          | ✓    | ✗     | ✓   | ✓    |
| Duplicates OK    | ✓    | ✓     | ✗   | keys: ✗ |
| Indexable        | ✓    | ✓     | ✗   | by key |
| Hashable         | ✗    | ✓*    | ✗   | ✗   |

*Only tuples containing hashable elements are hashable.

## Common Errors

```python
# IndexError
lst = [1, 2, 3]
print(lst[5])       # IndexError: list index out of range

# KeyError
d = {"a": 1}
print(d["z"])       # KeyError: 'z'
# Fix: use d.get("z") or "z" in d check

# TypeError: unhashable type
s = set()
s.add([1, 2])       # TypeError: unhashable type: 'list'
# Fix: use tuple instead
s.add((1, 2))       # OK

# Mutating a list while iterating
items = [1, 2, 3, 4]
for i in items:
    if i == 2:
        items.remove(i)  # Bug: skips 3
# Fix: iterate over a copy: for i in items[:]:
```

## Frequently Asked Questions

**Q: When should I use a tuple instead of a list?**
Use tuples for heterogeneous, fixed-length data (coordinates, records, function return values). Use lists for homogeneous, variable-length collections.

**Q: Why can't I use a list as a dictionary key?**
Dictionary keys must be hashable. Lists are mutable and therefore not hashable. Use a tuple instead.

**Q: What is the time complexity of common operations?**
- list index/assign: O(1), append: O(1) amortised, insert/delete at middle: O(n)
- dict/set lookup, insert, delete: O(1) average
- list `in` check: O(n); set/dict `in` check: O(1)
