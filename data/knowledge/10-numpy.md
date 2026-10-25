# NumPy Fundamentals

Source: https://numpy.org/doc/stable/user/absolute_beginners.html

## What is NumPy?

NumPy is the foundational library for numerical computing in Python. It provides:
- `ndarray`: a fast, fixed-type N-dimensional array
- Vectorised mathematical operations (no slow Python loops)
- Broadcasting rules for operations on arrays of different shapes
- Linear algebra, Fourier transforms, and random number generation

```bash
pip install numpy
```

```python
import numpy as np
print(np.__version__)
```

## Creating Arrays

```python
# From Python lists
a = np.array([1, 2, 3, 4])           # 1D array, dtype=int64
b = np.array([[1.0, 2.0], [3.0, 4.0]])  # 2D (matrix)

# Factory functions
np.zeros((3, 4))         # 3×4 array of 0.0
np.ones((2, 3))          # 2×3 array of 1.0
np.eye(4)                # 4×4 identity matrix
np.full((2, 2), 7)       # 2×2 filled with 7
np.arange(0, 10, 2)      # [0 2 4 6 8] (like range but returns array)
np.linspace(0, 1, 5)     # [0. 0.25 0.5 0.75 1.0]

# Random arrays
rng = np.random.default_rng(seed=42)   # recommended RNG (NumPy 1.17+)
rng.random((2, 3))       # uniform [0, 1)
rng.integers(0, 10, (3,))# random ints in [0, 10)
rng.standard_normal((3,))# standard normal (μ=0, σ=1)
```

## Array Attributes

```python
a = np.arange(24).reshape(2, 3, 4)

print(a.ndim)    # 3 (number of dimensions)
print(a.shape)   # (2, 3, 4)
print(a.size)    # 24 (total elements)
print(a.dtype)   # int64 (or int32 on Windows)
print(a.itemsize)# 8 (bytes per element)
print(a.nbytes)  # 192
```

## Indexing and Slicing

```python
a = np.array([[1, 2, 3],
              [4, 5, 6],
              [7, 8, 9]])

print(a[1, 2])      # 6
print(a[0])         # [1 2 3]   — first row
print(a[:, 1])      # [2 5 8]   — second column
print(a[1:3, 0:2])  # [[4 5], [7 8]]

# Boolean indexing
print(a[a > 5])     # [6 7 8 9]
a[a < 4] = 0        # set elements < 4 to 0
```

**Important:** Slices return views (not copies). Modifying the slice modifies the original.

```python
b = a[1:, :]    # view
b[0, 0] = 99    # also changes a!
c = a[1:, :].copy()   # force a copy
```

## Vectorised Operations

```python
a = np.array([1, 2, 3, 4])
b = np.array([10, 20, 30, 40])

print(a + b)    # [11 22 33 44]
print(a * 2)    # [2 4 6 8]
print(a ** 2)   # [1 4 9 16]
print(np.sqrt(a))   # [1. 1.41 1.73 2.]
print(np.exp(a))    # [2.72 7.39 20.09 54.60]
print(np.log(a))    # [0. 0.69 1.10 1.39]

# Comparison (returns bool array)
print(a > 2)    # [False False True True]
print(np.all(a > 0))  # True
print(np.any(a > 3))  # True
```

## Broadcasting

NumPy operations on arrays with different shapes apply broadcasting rules:

```python
a = np.array([[1, 2, 3],
              [4, 5, 6]])     # shape (2, 3)
b = np.array([10, 20, 30])   # shape (3,)

print(a + b)
# [[11 22 33]
#  [14 25 36]]  — b is broadcast across rows

# Scalar broadcast
print(a * 2)    # every element multiplied by 2
```

Broadcasting rules: dimensions are compared from the right; a size-1 dimension stretches to match.

## Aggregation Functions

```python
a = np.array([[1, 2, 3],
              [4, 5, 6]])

print(np.sum(a))          # 21
print(np.sum(a, axis=0))  # [5 7 9]  — column sums
print(np.sum(a, axis=1))  # [6 15]   — row sums
print(np.mean(a))         # 3.5
print(np.std(a))          # standard deviation
print(np.var(a))          # variance
print(np.min(a))          # 1
print(np.max(a))          # 6
print(np.argmin(a))       # 0 (flat index of minimum)
print(np.argmax(a))       # 5 (flat index of maximum)
print(np.cumsum(a))       # [1 3 6 10 15 21]
```

## Reshaping and Stacking

```python
a = np.arange(12)

b = a.reshape(3, 4)      # 3×4
c = a.reshape(2, 2, 3)   # 2×2×3
d = b.flatten()           # always returns copy
e = b.ravel()             # returns view when possible

# Stacking
x = np.array([1, 2, 3])
y = np.array([4, 5, 6])

np.vstack([x, y])   # [[1 2 3], [4 5 6]]  — vertical (row) stack
np.hstack([x, y])   # [1 2 3 4 5 6]       — horizontal (column) stack
np.concatenate([x, y], axis=0)   # [1 2 3 4 5 6]

# Splitting
np.hsplit(np.arange(6), 3)  # [array([0,1]), array([2,3]), array([4,5])]
```

## Linear Algebra

```python
A = np.array([[1, 2], [3, 4]])
B = np.array([[5, 6], [7, 8]])

np.dot(A, B)           # matrix product
A @ B                  # same, cleaner syntax
np.linalg.det(A)       # determinant: -2.0
np.linalg.inv(A)       # inverse matrix
np.linalg.eig(A)       # eigenvalues and eigenvectors
eigenvalues, eigenvectors = np.linalg.eig(A)

np.linalg.solve(A, np.array([1, 2]))  # solve Ax = b
np.linalg.norm(A)      # Frobenius norm
np.trace(A)            # sum of diagonal: 5
A.T                    # transpose
```

## Data Types (dtype)

```python
a = np.array([1, 2, 3], dtype=np.float32)  # 32-bit float
b = np.array([1, 2, 3], dtype=np.int8)     # 8-bit signed int

# Common dtypes
# int8, int16, int32, int64
# uint8, uint16, uint32, uint64
# float16, float32, float64 (default)
# complex64, complex128
# bool_

# Casting
c = a.astype(np.int64)
```

## Saving and Loading Arrays

```python
a = np.arange(12).reshape(3, 4)

# NumPy binary format
np.save("array.npy", a)
b = np.load("array.npy")

# Multiple arrays
np.savez("arrays.npz", x=a, y=a*2)
data = np.load("arrays.npz")
print(data["x"])

# Text format
np.savetxt("array.csv", a, delimiter=",", fmt="%d")
c = np.loadtxt("array.csv", delimiter=",")
```

## Common NumPy Mistakes

```python
# Mistake 1: Python list vs NumPy array arithmetic
lst = [1, 2, 3]
print(lst * 2)          # [1, 2, 3, 1, 2, 3] — list repetition!
arr = np.array([1, 2, 3])
print(arr * 2)          # [2 4 6] — element-wise multiplication

# Mistake 2: Modifying a view modifies the original
a = np.arange(5)
b = a[1:3]
b[0] = 99
print(a)   # [0 99 2 3 4] — a was changed!
# Fix: b = a[1:3].copy()

# Mistake 3: Wrong axis in aggregation
a = np.array([[1, 2], [3, 4]])
print(np.sum(a, axis=0))  # [4 6] — sum of columns
print(np.sum(a, axis=1))  # [3 7] — sum of rows

# Mistake 4: Integer division losing precision
a = np.array([1, 2, 3])
print(a / 2)    # [0.5 1.  1.5] — float
print(a // 2)   # [0 1 1]       — floor division
```

## Frequently Asked Questions

**Q: Why is NumPy so much faster than plain Python loops?**
NumPy arrays are contiguous blocks of typed C data. Operations are implemented in optimised C/Fortran code with SIMD instructions. Python loops are interpreted one element at a time.

**Q: What is the difference between `np.array` and `np.asarray`?**
`np.array` always creates a new array. `np.asarray` returns the input unchanged if it is already a compatible array (no copy).

**Q: How do I select rows where a column satisfies a condition?**
Use boolean indexing: `data[data[:, 0] > 5]` selects all rows where column 0 > 5.

**Q: What does `reshape(-1, 1)` do?**
The `-1` means "infer this dimension". `reshape(-1, 1)` turns a 1D array of n elements into a column vector of shape (n, 1).
