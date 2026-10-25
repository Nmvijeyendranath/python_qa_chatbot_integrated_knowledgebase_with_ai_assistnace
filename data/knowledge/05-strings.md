# Strings and String Formatting

Source: https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str

## String Basics

Strings are immutable sequences of Unicode characters.

```python
s1 = 'single quotes'
s2 = "double quotes"
s3 = """triple-quoted
multiline string"""
s4 = r"raw string — backslashes not processed: \n \t"
s5 = b"bytes literal"         # bytes, not str
```

Strings are immutable: `s[0] = 'x'` raises `TypeError`.

## String Indexing and Slicing

```python
s = "Python"
print(s[0])    # P
print(s[-1])   # n
print(s[1:4])  # yth
print(s[::-1]) # nohtyP (reversed)
```

## String Methods

```python
s = "  Hello, World!  "

s.strip()          # "Hello, World!"  — remove leading/trailing whitespace
s.lstrip()         # "Hello, World!  "
s.rstrip()         # "  Hello, World!"
s.upper()          # "  HELLO, WORLD!  "
s.lower()          # "  hello, world!  "
s.title()          # "  Hello, World!  "
s.capitalize()     # "  hello, world!  " — only first char capitalised

s = "Hello, World!"
s.replace("World", "Python")  # "Hello, Python!"
s.find("World")               # 7  (index of first occurrence)
s.find("xyz")                 # -1 (not found)
s.index("World")              # 7  (raises ValueError if not found)
s.startswith("Hello")         # True
s.endswith("!")               # True
s.count("l")                  # 3

# Split and join
"a,b,c".split(",")            # ['a', 'b', 'c']
"hello world".split()         # ['hello', 'world'] (on any whitespace)
",".join(["a", "b", "c"])     # "a,b,c"

# Check content
"abc123".isalpha()    # False
"abc".isalpha()       # True
"123".isdigit()       # True
"abc123".isalnum()    # True
"   ".isspace()       # True
```

## String Formatting

### f-strings (Python 3.6+) — Preferred

```python
name = "Alice"
age  = 30
pi   = 3.14159

print(f"Name: {name}, Age: {age}")
# Name: Alice, Age: 30

print(f"Pi = {pi:.2f}")     # Pi = 3.14
print(f"{age:05d}")          # 00030
print(f"{1234567:,}")        # 1,234,567
print(f"{0.75:.0%}")         # 75%

# Expressions inside f-strings
print(f"{2 ** 10}")          # 1024
print(f"{name!r}")           # 'Alice' (repr)
print(f"{name!s}")           # Alice  (str)
print(f"{name!a}")           # 'Alice' (ascii)

# Self-documenting (Python 3.8+) — prints name and value
x = 42
print(f"{x = }")             # x = 42
```

### str.format()

```python
"{} has {} items".format("cart", 5)          # "cart has 5 items"
"{name} is {age}".format(name="Bob", age=25) # "Bob is 25"
"{0:>10}".format("right")                    # "     right"
"{0:.3f}".format(3.14159)                    # "3.142"
```

### % Formatting (legacy)

```python
"Hello, %s! You are %d." % ("Alice", 30)    # old-style, avoid in new code
```

## Format Specification Mini-Language

```python
value = 12345.6789

f"{value:>15.2f}"    # right-align, 15 wide, 2 decimal places
f"{value:<15.2f}"    # left-align
f"{value:^15.2f}"    # centre-align
f"{value:015.2f}"    # zero-pad
f"{value:+.2f}"      # show sign (+12345.68)
f"{value:e}"         # scientific notation: 1.234568e+04
f"{value:g}"         # compact representation

n = 255
f"{n:b}"   # binary:  11111111
f"{n:o}"   # octal:   377
f"{n:x}"   # hex:     ff
f"{n:X}"   # hex upper: FF
f"{n:#x}"  # with prefix: 0xff
```

## Multi-line Strings and Escapes

```python
# Common escape sequences
print("Line 1\nLine 2")   # newline
print("Tab\there")         # tab
print("Quote: \"hi\"")    # escaped quote
print("Backslash: \\")    # backslash

# Raw strings ignore backslashes (useful for regex and Windows paths)
import re
pattern = re.compile(r"\d+\.\d+")   # r"..." avoids double-escaping

path = r"C:\Users\Alice\Documents"  # Windows path
```

## String Operations and Concatenation

```python
# Concatenation
greeting = "Hello" + ", " + "World!"

# Repetition
separator = "-" * 40

# Concatenating many strings efficiently
parts = ["one", "two", "three"]
result = "".join(parts)    # GOOD
result = ""
for p in parts:
    result += p            # BAD for large loops — O(n²) copies

# Checking substrings
print("Python" in "I love Python")   # True
print("Java" not in "I love Python") # True
```

## String Encoding and Bytes

```python
s = "café"
b = s.encode("utf-8")    # bytes
print(b)                  # b'caf\xc3\xa9'

decoded = b.decode("utf-8")   # back to str
print(decoded)                 # café

# Common encodings: utf-8, ascii, latin-1, utf-16
```

## textwrap, string Module

```python
import textwrap
long = "This is a very long line that needs to be wrapped."
print(textwrap.fill(long, width=30))

import string
print(string.ascii_lowercase)  # abcdefghijklmnopqrstuvwxyz
print(string.digits)           # 0123456789
print(string.punctuation)      # !"#$%&'()*+,-./:;<=>?@[\]^_`{|}~
```

## Common Errors

```python
# TypeError: can only concatenate str (not "int") to str
name = "Alice"
age  = 30
print(name + " is " + age)   # TypeError
# Fix:
print(name + " is " + str(age))
print(f"{name} is {age}")    # preferred

# IndexError on empty string
s = ""
print(s[0])  # IndexError: string index out of range

# AttributeError: str object has no attribute 'append'
s = "hello"
s.append("!")  # AttributeError — strings are immutable
s += "!"       # correct — creates a new string
```

## Frequently Asked Questions

**Q: What is the difference between `str.find()` and `str.index()`?**
Both return the index of a substring. `find()` returns -1 if not found; `index()` raises `ValueError`.

**Q: How do I check if a string is a palindrome?**
`s == s[::-1]` — compare the string to its reverse.

**Q: How do I split a string by multiple delimiters?**
Use `re.split(r'[,;:\s]+', text)` from the `re` module.

**Q: Why is `"" + string * 1000` slow?**
String concatenation with `+` in a loop creates a new string each time: O(n²). Use `"".join(list_of_strings)` instead.
