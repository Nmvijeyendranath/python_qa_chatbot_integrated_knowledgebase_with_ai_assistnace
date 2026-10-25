# Control Flow — Conditionals, Loops, and Comprehensions

Source: https://docs.python.org/3/tutorial/controlflow.html

## if / elif / else

```python
score = 85

if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
elif score >= 70:
    grade = "C"
else:
    grade = "F"

print(grade)  # B
```

A condition is any expression that evaluates to `True` or `False`. Indentation (4 spaces) defines the block — Python uses no braces.

## Ternary (Conditional) Expression

```python
x = 10
label = "even" if x % 2 == 0 else "odd"
print(label)  # even
```

## match / case (Python 3.10+)

Structural pattern matching:

```python
command = "quit"

match command:
    case "quit":
        print("Exiting")
    case "help":
        print("Showing help")
    case _:
        print(f"Unknown command: {command}")
```

Matching with guards and capturing:

```python
point = (0, 5)

match point:
    case (0, 0):
        print("Origin")
    case (x, 0):
        print(f"On x-axis at {x}")
    case (0, y):
        print(f"On y-axis at {y}")
    case (x, y):
        print(f"Point at ({x}, {y})")
```

## for Loops

Iterate over any iterable:

```python
fruits = ["apple", "banana", "cherry"]
for fruit in fruits:
    print(fruit)
```

`range()` for numeric iteration:

```python
for i in range(5):       # 0 1 2 3 4
    print(i)

for i in range(2, 10, 2):  # 2 4 6 8
    print(i)

for i in range(10, 0, -1): # 10 9 8 ... 1
    print(i)
```

`enumerate()` to get index and value together:

```python
for i, fruit in enumerate(fruits, start=1):
    print(f"{i}: {fruit}")
# 1: apple
# 2: banana
# 3: cherry
```

`zip()` to iterate multiple iterables in parallel:

```python
names = ["Alice", "Bob"]
scores = [95, 87]
for name, score in zip(names, scores):
    print(f"{name}: {score}")
```

## while Loops

```python
count = 0
while count < 5:
    print(count)
    count += 1
```

`while True` with `break`:

```python
while True:
    data = input("Enter 'quit' to stop: ")
    if data == "quit":
        break
    print(f"You entered: {data}")
```

## break, continue, pass

```python
# break exits the loop immediately
for i in range(10):
    if i == 5:
        break
    print(i)  # 0 1 2 3 4

# continue skips to the next iteration
for i in range(10):
    if i % 2 == 0:
        continue
    print(i)  # 1 3 5 7 9

# pass is a no-op placeholder
for i in range(5):
    pass  # do nothing (valid empty block)
```

## for / else and while / else

The `else` clause on a loop runs when the loop completes without hitting `break`:

```python
def find_prime(n):
    for divisor in range(2, n):
        if n % divisor == 0:
            print(f"{n} is not prime (divisible by {divisor})")
            break
    else:
        print(f"{n} is prime")

find_prime(7)   # 7 is prime
find_prime(10)  # 10 is not prime (divisible by 2)
```

## List Comprehensions

Concise way to create lists:

```python
squares = [x**2 for x in range(10)]
# [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]

evens = [x for x in range(20) if x % 2 == 0]
# [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]

# Nested comprehension (flattening a 2D list)
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
flat = [x for row in matrix for x in row]
# [1, 2, 3, 4, 5, 6, 7, 8, 9]
```

## Dict and Set Comprehensions

```python
# Dict comprehension
word_lengths = {word: len(word) for word in ["apple", "fig", "banana"]}
# {'apple': 5, 'fig': 3, 'banana': 6}

# Set comprehension (unique vowels in a string)
vowels = {ch for ch in "programming" if ch in "aeiou"}
# {'o', 'i', 'a'}
```

## Generator Expressions

Like list comprehensions but lazy (one element at a time):

```python
total = sum(x**2 for x in range(1_000_000))  # memory-efficient

# Don't create the full list when you only need the sum
```

## Common Mistakes

```python
# Modifying a list while iterating over it — unpredictable behaviour
items = [1, 2, 3, 4, 5]
for item in items:
    if item % 2 == 0:
        items.remove(item)  # BUG — skips elements
# Correct: iterate over a copy or use a comprehension
items = [item for item in items if item % 2 != 0]

# Off-by-one with range
for i in range(1, 11):  # correct: includes 10
    pass

# Forgetting that range is exclusive of the stop value
print(list(range(5)))   # [0, 1, 2, 3, 4] — 5 is NOT included
```

## Frequently Asked Questions

**Q: What is the difference between `break` and `continue`?**
`break` exits the entire loop. `continue` skips the rest of the current iteration and moves to the next one.

**Q: When should I use a list comprehension vs. a for loop?**
Use comprehensions for simple transformations/filters of iterables. Use for loops when the logic is complex, when you need early exit (`break`/`return`), or when you have side effects to manage.

**Q: Does Python have a `do-while` loop?**
No. Emulate it with `while True: ... if condition: break`.
