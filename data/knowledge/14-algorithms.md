# Algorithms, Sorting, Searching, and Time Complexity

Source: https://docs.python.org/3/howto/sorting.html

## Time and Space Complexity (Big-O Notation)

Big-O describes how runtime or memory usage grows as input size n increases.

| Notation     | Name         | Example                          |
|--------------|--------------|----------------------------------|
| O(1)         | Constant     | dict lookup, list indexing       |
| O(log n)     | Logarithmic  | binary search                    |
| O(n)         | Linear       | list scan, linear search         |
| O(n log n)   | Linearithmic | Timsort, merge sort              |
| O(n²)        | Quadratic    | bubble sort, nested loops        |
| O(2ⁿ)        | Exponential  | brute-force combinations         |
| O(n!)        | Factorial    | brute-force permutations         |

## Python Built-in Complexity Reference

```
list.append()          O(1) amortised
list.pop()             O(1)  — from end
list.pop(0)            O(n)  — avoid; use collections.deque
list.insert(i, x)      O(n)
list.index(x)          O(n)
x in list              O(n)
x in set / dict        O(1) average
dict[key] / dict.get() O(1) average
sorted()               O(n log n)
list.sort()            O(n log n)
```

## Sorting Algorithms

### Python's Built-in Sort (Timsort)

```python
lst = [5, 2, 8, 1, 9, 3]

# Sort in place
lst.sort()           # ascending
lst.sort(reverse=True)

# Return new sorted list
s = sorted(lst)                           # ascending
s = sorted(lst, reverse=True)             # descending
s = sorted(lst, key=abs)                  # sort by absolute value
s = sorted(lst, key=lambda x: -x)        # descending via key

# Sort objects
people = [("Bob", 30), ("Alice", 25), ("Charlie", 35)]
people.sort(key=lambda p: p[1])          # sort by age
people.sort(key=lambda p: (-p[1], p[0])) # age desc, name asc

from operator import itemgetter, attrgetter
people.sort(key=itemgetter(1))    # same as lambda p: p[1]
```

### Bubble Sort (educational)

```python
def bubble_sort(lst: list) -> list:
    n = len(lst)
    lst = lst.copy()
    for i in range(n):
        swapped = False
        for j in range(n - i - 1):
            if lst[j] > lst[j + 1]:
                lst[j], lst[j + 1] = lst[j + 1], lst[j]
                swapped = True
        if not swapped:
            break   # already sorted — early exit
    return lst

# Time: O(n²) worst/average, O(n) best; Space: O(1)
```

### Merge Sort

```python
def merge_sort(lst: list) -> list:
    if len(lst) <= 1:
        return lst
    mid   = len(lst) // 2
    left  = merge_sort(lst[:mid])
    right = merge_sort(lst[mid:])
    return _merge(left, right)

def _merge(left: list, right: list) -> list:
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i]); i += 1
        else:
            result.append(right[j]); j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result

# Time: O(n log n); Space: O(n)
```

### Quick Sort

```python
def quick_sort(lst: list) -> list:
    if len(lst) <= 1:
        return lst
    pivot = lst[len(lst) // 2]
    left  = [x for x in lst if x < pivot]
    mid   = [x for x in lst if x == pivot]
    right = [x for x in lst if x > pivot]
    return quick_sort(left) + mid + quick_sort(right)

# Time: O(n log n) average, O(n²) worst; Space: O(n) extra
```

## Searching Algorithms

### Linear Search

```python
def linear_search(lst: list, target) -> int:
    """Return index of target, or -1 if not found. O(n)."""
    for i, item in enumerate(lst):
        if item == target:
            return i
    return -1
```

### Binary Search

Requires a **sorted** list. O(log n).

```python
def binary_search(lst: list, target) -> int:
    """Return index of target, or -1 if not found."""
    lo, hi = 0, len(lst) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if lst[mid] == target:
            return mid
        elif lst[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1

# Using the standard library
import bisect
lst = [1, 3, 5, 7, 9]
i = bisect.bisect_left(lst, 5)    # 2
i = bisect.bisect_right(lst, 5)   # 3
bisect.insort(lst, 6)             # insert maintaining sort order
```

## Recursion and Dynamic Programming

### Fibonacci — Naive vs. Memoised

```python
# Naive: O(2ⁿ)
def fib_naive(n: int) -> int:
    if n <= 1: return n
    return fib_naive(n - 1) + fib_naive(n - 2)

# Memoised: O(n) time, O(n) space
from functools import lru_cache

@lru_cache(maxsize=None)
def fib_memo(n: int) -> int:
    if n <= 1: return n
    return fib_memo(n - 1) + fib_memo(n - 2)

# Iterative: O(n) time, O(1) space — best for large n
def fib_iter(n: int) -> int:
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a

print(fib_iter(50))   # 12586269025
```

### 0/1 Knapsack (DP table)

```python
def knapsack(weights, values, capacity):
    n = len(weights)
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for w in range(capacity + 1):
            if weights[i-1] <= w:
                dp[i][w] = max(dp[i-1][w], dp[i-1][w - weights[i-1]] + values[i-1])
            else:
                dp[i][w] = dp[i-1][w]
    return dp[n][capacity]

# O(n × capacity) time and space
```

## Stack, Queue, and Deque

```python
from collections import deque

# Stack (LIFO) — use a list
stack = []
stack.append(1)   # push
stack.append(2)
top = stack.pop() # pop — O(1) from end

# Queue (FIFO) — use deque for O(1) popleft
queue = deque()
queue.append(1)         # enqueue
queue.append(2)
front = queue.popleft() # dequeue — O(1)

# Priority Queue (min-heap)
import heapq
h = []
heapq.heappush(h, (3, "low"))
heapq.heappush(h, (1, "high"))
heapq.heappush(h, (2, "medium"))
priority, task = heapq.heappop(h)   # (1, 'high')
```

## Graph Algorithms

```python
from collections import deque

graph = {
    "A": ["B", "C"],
    "B": ["D", "E"],
    "C": ["F"],
    "D": [], "E": [], "F": [],
}

# Breadth-First Search (BFS) — O(V + E)
def bfs(graph, start):
    visited = set([start])
    queue   = deque([start])
    order   = []
    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    return order

# Depth-First Search (DFS) — O(V + E)
def dfs(graph, node, visited=None):
    if visited is None:
        visited = set()
    visited.add(node)
    result = [node]
    for neighbor in graph[node]:
        if neighbor not in visited:
            result.extend(dfs(graph, neighbor, visited))
    return result
```

## Frequently Asked Questions

**Q: When should I use a list vs. a deque?**
Use `list` when you need random access and append/pop from the right. Use `collections.deque` when you need efficient append/pop from both ends (e.g., queues, sliding windows).

**Q: Why is Python's sort O(n log n) guaranteed?**
Python uses Timsort, a hybrid of merge sort and insertion sort. It exploits natural runs in real-world data and guarantees O(n log n) worst case and O(n) for already-sorted input.

**Q: How do I sort a dictionary by value?**
`sorted(d.items(), key=lambda item: item[1])` returns a list of (key, value) pairs sorted by value. To get a dict back: `dict(sorted(d.items(), key=lambda item: item[1]))`.

**Q: What is the time complexity of `in` for different containers?**
`x in list`: O(n) — linear scan. `x in set`: O(1) average — hash lookup. `x in dict`: O(1) average — hash lookup on keys.
