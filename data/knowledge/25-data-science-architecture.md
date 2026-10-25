# Data Science Architecture — NumPy, pandas, and scikit-learn Internals

Sources:
- NumPy Documentation: https://numpy.org/doc/stable/
- pandas Documentation: https://pandas.pydata.org/docs/
- scikit-learn Documentation: https://scikit-learn.org/stable/

## NumPy Architecture and the `ndarray`

NumPy is the foundational library for scientific computing in Python. Standard Python lists store arrays of pointers to individual `PyObject` structures scattered across memory. In contrast, NumPy's `ndarray` stores homogeneous data in a **contiguous block of raw memory**.

```
Python List:    [ ptr ] ──► [ PyObject: int 10 ]
                [ ptr ] ──► [ PyObject: int 20 ]
                [ ptr ] ──► [ PyObject: int 30 ]  (High pointer overhead, cache misses)

NumPy ndarray:  [ 10 | 20 | 30 ]                  (Contiguous raw bytes, cache locality)
```

### Components of an `ndarray`
1. **Data Buffer**: A continuous memory block containing raw bytes.
2. **dtype**: Describes how each element's bytes are interpreted (e.g. `int32`, `float64`).
3. **shape**: A tuple representing array dimensions (e.g., `(3, 4)` for a 3x4 matrix).
4. **strides**: A tuple of byte steps required to move to the next item along each dimension.

### Memory Layout: C-Order vs. Fortran-Order
- **C-contiguous (Row-major)**: Last index changes fastest. Row elements are adjacent in memory (default in C and NumPy).
- **Fortran-contiguous (Column-major)**: First index changes fastest. Column elements are adjacent in memory (default in Fortran and MATLAB).

### Why NumPy is Fast:
- **Vectorization and SIMD**: Loops run in compiled C/Fortran routines utilizing CPU Single Instruction Multiple Data (SIMD) registers.
- **Cache Locality**: Elements sit side-by-side in CPU L1/L2 cache lines, drastically reducing memory latency.
- **Bypassing the GIL**: NumPy releases the GIL during heavy matrix computations, enabling multi-threaded C libraries (BLAS/LAPACK/OpenBLAS/MKL) to run across all CPU cores.

### Broadcasting Rules
Broadcasting allows NumPy to perform element-wise arithmetic on arrays of different shapes without copying data. Two dimensions are compatible if:
1. They are equal, or
2. One of them is 1.

```python
import numpy as np

A = np.ones((3, 1))  # 3 rows, 1 col
B = np.ones((1, 4))  # 1 row, 4 cols
C = A + B            # Broadcasts to (3, 4) with zero data copying!
```

### Views vs. Copies
- **Slicing creates a VIEW**: `sub = arr[1:3]` shares the underlying memory buffer with `arr`. Modifying `sub` directly mutates `arr`!
- **Fancy/Boolean indexing creates a COPY**: `sub = arr[[0, 2]]` allocates new independent memory.

## pandas Architecture: Series, DataFrames, and Indexes

pandas builds on NumPy to provide labeled, relational, and heterogeneous data analysis tools.

### 1. Data Structures
- **`Series`**: A one-dimensional labeled array capable of holding any data type. Combines a 1D NumPy array or ExtensionArray with an explicit `Index`.
- **`DataFrame`**: A two-dimensional tabular data structure with labeled axes (rows and columns). It is essentially a dictionary of `Series` objects sharing a common `Index`.

### 2. The `Index` Object
The `Index` is an immutable, hashable sequence of labels (row or column names).
- Enables automatic **data alignment**: When performing operations between two DataFrames or Series, pandas automatically aligns rows and columns by their index labels, not merely their positional order.
- Supports hierarchical labeling via `MultiIndex`.

### 3. Internal Storage: BlockManager vs. ArrayManager
Internally, pandas groups columns of identical primitive data types into 2D NumPy arrays called **Blocks** managed by the `BlockManager`:
- A DataFrame with three `float64` columns and two `int64` columns stores them as one 2D float block and one 2D int block.
- This design optimizes memory and enables fast bulk operations, though modern pandas is transitioning toward `ArrayManager` for 1D column independence.

## scikit-learn Architecture: The Unified Estimator API

scikit-learn defines a standard, highly composable object-oriented interface for machine learning:

```
┌────────────────────────────────────────────────────────┐
│ Estimator: fit(X, y)                                   │
│   Learns parameters from training data.                │
├────────────────────────────────────────────────────────┤
│ Transformer: transform(X) / fit_transform(X, y)        │
│   Transforms features (scaling, encoding, selection).  │
├────────────────────────────────────────────────────────┤
│ Predictor: predict(X) / predict_proba(X)               │
│   Generates predictions for unseen data.               │
└────────────────────────────────────────────────────────┘
```

### Core Design Principles:
1. **Consistency**: All algorithms share identical method signatures. A linear regression model and a gradient boosting regressor are instantiated and trained with the exact same `model.fit(X, y)` and `model.predict(X)` calls.
2. **Inspection**: Learned parameters are stored as public attributes ending with an underscore (e.g., `model.coef_`, `model.intercept_`, `model.classes_`).
3. **Stateless Transformations via Pipelines**: The `Pipeline` object chains preprocessing transformers and a final estimator into a single composite estimator:
   ```python
   from sklearn.pipeline import Pipeline
   from sklearn.preprocessing import StandardScaler
   from sklearn.linear_model import LogisticRegression

   pipeline = Pipeline([
       ("scaler", StandardScaler()),
       ("classifier", LogisticRegression())
   ])

   pipeline.fit(X_train, y_train)
   predictions = pipeline.predict(X_test)
   ```
   Pipelines prevent **data leakage** by ensuring test data is never used during transformer fitting.

## Frequently Asked Questions

**Q: Why is NumPy so much faster than standard Python lists?**
NumPy stores elements in a contiguous block of memory with a single uniform C data type, avoiding Python object pointer overhead and dynamic type dispatch. Computations are executed via compiled C routines utilizing CPU cache locality and SIMD vectorization.

**Q: What is the difference between a view and a copy in NumPy?**
A view is an alternative window into the exact same memory buffer (created by basic slicing `arr[1:4]`). Changing data in a view changes the original array. A copy (created by `.copy()` or fancy integer/boolean indexing) allocates brand new memory completely independent of the original array.

**Q: How does pandas ensure data alignment?**
pandas uses immutable `Index` objects for rows and columns. When performing arithmetic or joins between two Series or DataFrames, pandas aligns elements based on matching index labels rather than array positions, automatically filling non-overlapping labels with `NaN`.

**Q: What is scikit-learn's Estimator API?**
scikit-learn's Estimator API is a uniform design pattern where every machine learning model implements `fit(X, y)` to learn parameters, transformers implement `transform(X)`, and predictors implement `predict(X)`. Learned parameters are always exposed as public attributes ending with an underscore (e.g., `coef_`).
