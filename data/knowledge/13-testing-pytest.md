# Testing with pytest

Source: https://docs.pytest.org/en/stable/

## Why Test?

Automated tests catch regressions, document expected behaviour, and give you confidence to refactor. pytest is the standard Python testing framework.

```bash
pip install pytest
pytest              # discover and run all tests
pytest -v           # verbose output
pytest tests/test_math.py  # specific file
pytest -k "addition"       # filter by keyword
pytest -x           # stop on first failure
pytest --tb=short   # shorter traceback
```

## Test Discovery Conventions

- Test files: `test_*.py` or `*_test.py`
- Test functions: `test_*`
- Test classes: `Test*` (no `__init__` method)

## Basic Tests

```python
# tests/test_math_utils.py

def add(a, b):
    return a + b

def divide(a, b):
    if b == 0:
        raise ZeroDivisionError("Cannot divide by zero")
    return a / b

# ---- tests ----

def test_add_integers():
    assert add(2, 3) == 5

def test_add_negative():
    assert add(-1, -1) == -2

def test_add_floats():
    assert abs(add(0.1, 0.2) - 0.3) < 1e-10   # floating-point tolerance

def test_divide_normal():
    assert divide(10, 2) == 5.0

def test_divide_by_zero():
    import pytest
    with pytest.raises(ZeroDivisionError, match="Cannot divide by zero"):
        divide(10, 0)
```

## Fixtures

Fixtures provide reusable setup (and teardown) for tests:

```python
import pytest

@pytest.fixture
def sample_list():
    """Provide a fresh list for every test that requests it."""
    return [1, 2, 3, 4, 5]

@pytest.fixture
def temp_file(tmp_path):
    """Create a temporary file using the built-in tmp_path fixture."""
    f = tmp_path / "data.txt"
    f.write_text("Hello, pytest!")
    return f

def test_sum(sample_list):
    assert sum(sample_list) == 15

def test_file_content(temp_file):
    assert temp_file.read_text() == "Hello, pytest!"
```

### Fixture Scope

```python
@pytest.fixture(scope="module")   # created once per module
def database_connection():
    conn = create_connection()
    yield conn       # provides the value; code after yield is teardown
    conn.close()     # runs after all tests in the module

@pytest.fixture(scope="session")  # created once per test session
def shared_resource():
    return expensive_setup()
```

## Parametrize — Data-Driven Tests

```python
import pytest

@pytest.mark.parametrize("a, b, expected", [
    (2, 3, 5),
    (-1, 1, 0),
    (0, 0, 0),
    (100, -50, 50),
])
def test_add_parametrized(a, b, expected):
    assert add(a, b) == expected

# Multiple parametrize decorators → Cartesian product
@pytest.mark.parametrize("x", [1, 2, 3])
@pytest.mark.parametrize("y", [10, 20])
def test_multiply(x, y):
    assert x * y == y * x
```

## Mocking

Use `unittest.mock` to replace dependencies (APIs, databases, files) with controlled fakes:

```python
from unittest.mock import Mock, MagicMock, patch

def get_data_from_api(url):
    import urllib.request
    with urllib.request.urlopen(url) as r:
        return r.read().decode()

# Patch the network call
def test_get_data(monkeypatch):
    def fake_urlopen(url):
        mock = MagicMock()
        mock.__enter__ = lambda self: self
        mock.__exit__ = Mock(return_value=False)
        mock.read.return_value = b"fake response"
        return mock

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    result = get_data_from_api("http://example.com")
    assert result == "fake response"

# Using patch as decorator
from unittest.mock import patch

@patch("mymodule.requests.get")
def test_api_call(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"key": "value"}

    result = my_function()
    assert result["key"] == "value"
    mock_get.assert_called_once()
```

## Assertions

```python
# Basic equality and comparison
assert x == 5
assert x != 0
assert x > 3

# Containers
assert "hello" in result
assert len(lst) == 3
assert d == {"a": 1, "b": 2}

# Approximate float comparisons
import pytest
assert result == pytest.approx(3.14, abs=1e-2)
assert result == pytest.approx(expected, rel=1e-5)

# Exceptions
with pytest.raises(ValueError):
    int("abc")

with pytest.raises(ValueError, match=r"invalid literal"):
    int("abc")

# Warnings
with pytest.warns(DeprecationWarning):
    old_function()

# Logging
def test_logs_warning(caplog):
    import logging
    with caplog.at_level(logging.WARNING):
        my_function()
    assert "Expected warning" in caplog.text
```

## Marks and Skipping

```python
import pytest

@pytest.mark.skip(reason="Feature not implemented yet")
def test_future_feature():
    ...

@pytest.mark.skipif(sys.platform == "win32", reason="Linux only")
def test_linux_specific():
    ...

@pytest.mark.xfail(reason="Known bug #123")
def test_known_failure():
    assert buggy_function() == expected

@pytest.mark.slow
def test_large_dataset():
    ...  # run with: pytest -m slow
```

## conftest.py

A `conftest.py` file in the test directory provides fixtures and plugins to all tests in its directory and subdirectories:

```python
# tests/conftest.py
import pytest
from myapp import create_app, get_db

@pytest.fixture(scope="session")
def app():
    app = create_app({"TESTING": True, "DATABASE": ":memory:"})
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def db(app):
    with app.app_context():
        db = get_db()
        yield db
```

## Coverage

```bash
pip install pytest-cov

pytest --cov=src --cov-report=term-missing
pytest --cov=src --cov-report=html   # generates htmlcov/index.html
```

## Evaluation: Writing Good Tests

Good tests are:
- **Fast**: mock external calls; use in-memory databases
- **Isolated**: each test independent; no shared mutable state
- **Readable**: test name describes what is being verified
- **Deterministic**: same result every run (seed randoms, freeze time)
- **Focused**: one logical assertion per test when possible

```python
# Descriptive test name
def test_user_cannot_login_with_wrong_password():
    ...

# Arrange-Act-Assert structure
def test_discount_applied_for_premium_users():
    # Arrange
    user = User(tier="premium")
    cart = Cart([Item("book", price=20.0)])

    # Act
    total = cart.checkout(user)

    # Assert
    assert total == pytest.approx(16.0)  # 20% discount
```

## Common pytest Mistakes

```python
# Missing the assert keyword
def test_bad():
    result = add(2, 3)
    result == 5   # BUG: always passes — no assert!

# Correct:
def test_good():
    assert add(2, 3) == 5

# Sharing mutable state between tests
shared_list = []  # shared module-level list — dangerous!
def test_a():
    shared_list.append(1)
def test_b():
    assert shared_list == []   # fails if test_a ran first!

# Fix: use a fixture to provide fresh state
@pytest.fixture
def fresh_list():
    return []
```

## Frequently Asked Questions

**Q: What is the difference between `assert` and `pytest.raises`?**
Plain `assert` tests a condition is true. `pytest.raises` is a context manager that tests whether a specific exception is raised.

**Q: What is the difference between a fixture and a helper function?**
Fixtures are automatically injected by pytest based on parameter name, support scope and teardown, and are composable. Helper functions are called manually.

**Q: How do I run only tests that failed last time?**
`pytest --lf` (last failed) re-runs only the tests that failed in the previous run. `pytest --ff` runs failed tests first.

**Q: When should I use `monkeypatch` vs `unittest.mock.patch`?**
`monkeypatch` is pytest's fixture for patching attributes/environment; it automatically undoes changes after the test. `patch` is from the standard library and works as a decorator or context manager. Both work; `monkeypatch` integrates more naturally with pytest fixtures.
