# pandas Fundamentals and Data Manipulation

Source: https://pandas.pydata.org/docs/user_guide/index.html

## What is pandas?

pandas is the standard Python library for tabular and time-series data analysis. Its core objects are:
- **`Series`**: 1D labelled array
- **`DataFrame`**: 2D labelled table (like a spreadsheet or SQL table)

```bash
pip install pandas
```

```python
import pandas as pd
print(pd.__version__)
```

## Series

```python
# From a list
s = pd.Series([10, 20, 30, 40], name="sales")
print(s)
# 0    10
# 1    20
# 2    30
# 3    40
# Name: sales, dtype: int64

# Custom index
s = pd.Series({"a": 1, "b": 2, "c": 3})
print(s["b"])    # 2
print(s[["a", "c"]])  # slice by label

# Vectorised operations work like NumPy
print(s * 2)    # a:2, b:4, c:6
print(s[s > 1]) # b:2, c:3
```

## DataFrame

```python
data = {
    "name":  ["Alice", "Bob", "Charlie", "Diana"],
    "age":   [30, 25, 35, 28],
    "score": [88.5, 72.0, 95.3, 61.8],
    "city":  ["London", "Paris", "London", "Berlin"],
}
df = pd.DataFrame(data)
print(df)
#       name  age  score    city
# 0    Alice   30   88.5  London
# 1      Bob   25   72.0   Paris
# 2  Charlie   35   95.3  London
# 3    Diana   28   61.8  Berlin
```

### DataFrame Attributes and Info

```python
print(df.shape)        # (4, 4)
print(df.dtypes)       # column data types
print(df.info())       # memory, nulls, dtypes
print(df.describe())   # numeric summary statistics
print(df.columns.tolist())  # ['name', 'age', 'score', 'city']
print(df.index)        # RangeIndex(start=0, stop=4, step=1)
```

## Selecting Data

```python
# Select column (returns Series)
print(df["name"])
print(df.name)          # same, but [] preferred

# Select multiple columns (returns DataFrame)
print(df[["name", "score"]])

# .loc — label-based indexing
print(df.loc[0])              # row 0 by index label
print(df.loc[0, "name"])      # specific cell
print(df.loc[1:3, ["name", "age"]])  # rows 1-3, two columns

# .iloc — position-based indexing
print(df.iloc[0])             # first row
print(df.iloc[0, 0])          # first row, first column
print(df.iloc[:2, 1:3])       # first 2 rows, columns 1-2

# Boolean filtering
london = df[df["city"] == "London"]
high   = df[df["score"] > 80]
query  = df[(df["age"] > 25) & (df["score"] > 70)]   # & not and

# .query() — SQL-like string
result = df.query("age > 25 and city == 'London'")
```

## Adding and Modifying Data

```python
# Add column
df["grade"]  = df["score"].apply(lambda s: "A" if s >= 90 else ("B" if s >= 75 else "C"))
df["senior"] = df["age"] > 30

# Modify with loc
df.loc[0, "score"] = 91.0

# .assign() — method chaining friendly
df = df.assign(score_norm=df["score"] / df["score"].max())
```

## Handling Missing Data

```python
import numpy as np
df = pd.DataFrame({"a": [1, np.nan, 3], "b": [4, 5, np.nan]})

df.isnull()           # bool DataFrame of NaN locations
df.isnull().sum()     # count NaN per column
df.dropna()           # drop rows with any NaN
df.dropna(subset=["a"])  # drop only if "a" is NaN
df.fillna(0)          # replace NaN with 0
df.fillna(df.mean(numeric_only=True))  # fill with column mean
df["a"].interpolate() # interpolate missing values
```

## GroupBy — Split-Apply-Combine

```python
df = pd.DataFrame({
    "city":  ["London", "Paris", "London", "Berlin", "Paris"],
    "sales": [200, 150, 300, 100, 250],
    "units": [10, 8, 15, 5, 12],
})

# Group by city and aggregate
grouped = df.groupby("city")["sales"].sum()
print(grouped)
# city
# Berlin    100
# London    500
# Paris     400

# Multiple aggregations
agg = df.groupby("city").agg(
    total_sales=("sales", "sum"),
    avg_units=("units", "mean"),
    count=("sales", "count"),
)
print(agg)
```

## Sorting, Filtering, and Ranking

```python
df.sort_values("score", ascending=False)         # sort by column
df.sort_values(["city", "age"], ascending=[True, False])

df.nlargest(3, "score")    # top 3 rows by score
df.nsmallest(2, "age")     # bottom 2 rows by age

df["rank"] = df["score"].rank(ascending=False).astype(int)
```

## Joining and Merging DataFrames

```python
employees = pd.DataFrame({
    "id":   [1, 2, 3],
    "name": ["Alice", "Bob", "Charlie"],
    "dept_id": [10, 20, 10],
})
departments = pd.DataFrame({
    "dept_id": [10, 20, 30],
    "dept":    ["Engineering", "Marketing", "Sales"],
})

# SQL-style join
merged = pd.merge(employees, departments, on="dept_id", how="left")
print(merged)

# Concatenate vertically
batch1 = df.iloc[:2]
batch2 = df.iloc[2:]
combined = pd.concat([batch1, batch2], ignore_index=True)
```

## Apply and Vectorised Operations

```python
df["score_scaled"] = (df["score"] - df["score"].mean()) / df["score"].std()

# .apply() — element-wise or row/column-wise
df["grade"] = df["score"].apply(lambda x: "Pass" if x >= 50 else "Fail")

# Row-wise apply (axis=1)
df["summary"] = df.apply(lambda row: f"{row['name']} ({row['city']})", axis=1)

# Faster: vectorised string operations
df["name_upper"] = df["name"].str.upper()
df["name_len"]   = df["name"].str.len()
df["city_short"] = df["city"].str[:3]
```

## Reading and Writing Files

```python
# CSV
df = pd.read_csv("data.csv", sep=",", encoding="utf-8", parse_dates=["date"])
df.to_csv("output.csv", index=False)

# Excel
df = pd.read_excel("data.xlsx", sheet_name="Sheet1")
df.to_excel("output.xlsx", sheet_name="Results", index=False)

# JSON
df = pd.read_json("data.json")
df.to_json("output.json", orient="records", indent=2)

# SQL
from sqlalchemy import create_engine
engine = create_engine("sqlite:///mydb.db")
df = pd.read_sql("SELECT * FROM employees", engine)
df.to_sql("results", engine, if_exists="replace", index=False)

# Parquet (efficient column storage)
df.to_parquet("data.parquet")
df = pd.read_parquet("data.parquet")
```

## Common pandas Mistakes

```python
# Chained indexing (SettingWithCopyWarning)
df["a"][0] = 99         # BAD — may not modify original
df.loc[0, "a"] = 99     # GOOD — use .loc always

# Iterating rows with iterrows (very slow)
for i, row in df.iterrows():   # slow!
    df.at[i, "result"] = row["a"] * 2

# Fast: vectorised operations
df["result"] = df["a"] * 2

# Forgetting inplace vs return
df.sort_values("score")    # does NOT modify df
df = df.sort_values("score")  # correct
df.sort_values("score", inplace=True)  # also correct

# Using + to concatenate DataFrames (deprecated for Series)
combined = pd.concat([df1, df2])  # correct
```

## Frequently Asked Questions

**Q: What is the difference between `.loc` and `.iloc`?**
`.loc` is label-based (uses index values). `.iloc` is position-based (uses integer positions 0, 1, 2…). Both are inclusive at the end for `.loc` but exclusive for `.iloc` slices.

**Q: How do I reset the index after filtering?**
`df = df[condition].reset_index(drop=True)` — `drop=True` prevents the old index from becoming a column.

**Q: How do I convert a column's dtype?**
`df["col"] = df["col"].astype(float)` or `pd.to_numeric(df["col"], errors="coerce")` to handle bad values.

**Q: What is the best way to iterate over a DataFrame?**
Avoid iteration when possible — use vectorised operations. For row-wise logic, `.apply(func, axis=1)` is cleaner. For maximum performance, use NumPy operations on `df.values`.
