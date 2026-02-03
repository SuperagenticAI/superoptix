# Python Error Handling Best Practices

## Overview
Proper error handling makes code robust, maintainable, and user-friendly. Python provides powerful exception handling mechanisms.

## Best Practices

### ❌ Poor Error Handling
```python
# No error handling
def read_file(filename):
    file = open(filename, 'r')
    data = file.read()
    file.close()
    return data

# Catching all exceptions
try:
    data = process_data()
except:  # TOO BROAD!
    pass
```

### ✅ Good Error Handling
```python
# Context manager (recommended)
def read_file(filename):
    try:
        with open(filename, 'r') as file:
            return file.read()
    except FileNotFoundError:
        logger.error(f"File not found: {filename}")
        raise
    except IOError as e:
        logger.error(f"Error reading file: {e}")
        raise

# Specific exception handling
try:
    data = process_data()
except ValueError as e:
    logger.error(f"Invalid data: {e}")
    return default_value
except KeyError as e:
    logger.error(f"Missing key: {e}")
    return {}
```

## Key Principles

1. **Be specific** - Catch specific exceptions, not bare `except:`
2. **Use context managers** - `with` statement for resources
3. **Don't silence errors** - Log before suppressing
4. **Fail fast** - Raise exceptions early for invalid state
5. **Clean up resources** - Use `finally` or context managers
6. **Provide context** - Include helpful error messages

## Exception Hierarchy

```
BaseException
├── SystemExit
├── KeyboardInterrupt
└── Exception
    ├── ValueError
    ├── TypeError
    ├── KeyError
    ├── FileNotFoundError
    └── ...
```

## Common Patterns

### File Operations
```python
with open(filename, 'r') as file:
    data = file.read()
# File automatically closed, even if exception occurs
```

### Network Requests
```python
try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
except requests.Timeout:
    logger.error("Request timed out")
except requests.HTTPError as e:
    logger.error(f"HTTP error: {e.response.status_code}")
```

### Database Operations
```python
try:
    with db.transaction():
        db.execute(query)
        db.commit()
except DatabaseError:
    db.rollback()
    logger.error("Transaction failed")
    raise
```

