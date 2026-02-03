# Python Naming Conventions (PEP 8)

## Overview
Consistent naming makes code readable and maintainable. Follow PEP 8 style guide.

## Naming Styles

### Variables and Functions
```python
# ✅ snake_case for variables and functions
user_name = "John"
total_count = 42

def calculate_total_price(items):
    return sum(item.price for item in items)

# ❌ Avoid
userName = "John"  # camelCase
TotalCount = 42    # PascalCase
def CalculatePrice(): pass  # PascalCase
```

### Classes
```python
# ✅ PascalCase for classes
class UserAccount:
    pass

class DatabaseConnection:
    pass

# ❌ Avoid
class user_account: pass  # snake_case
class database_connection: pass
```

### Constants
```python
# ✅ UPPER_CASE for constants
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30
API_BASE_URL = "https://api.example.com"

# ❌ Avoid
max_retries = 3  # Not clear it's a constant
MaxRetries = 3   # Wrong case
```

### Private Members
```python
# ✅ Single underscore for internal use
class MyClass:
    def __init__(self):
        self._internal_var = 42  # Internal, can be accessed
        self.__private_var = 100  # Name mangled

    def _internal_method(self):  # Internal method
        pass
```

## Descriptive Names

### ❌ Poor Names
```python
def f(x, y):
    z = x + y
    if z > 100:
        a = z * 2
        return a
    return z

data = [1, 2, 3]
temp = process(data)
```

### ✅ Good Names
```python
def calculate_discounted_price(original_price, discount_percent):
    final_price = original_price - (original_price * discount_percent / 100)
    if final_price > 100:
        shipping_included_price = final_price + 20
        return shipping_included_price
    return final_price

customer_ids = [1, 2, 3]
validated_customers = validate_customer_ids(customer_ids)
```

## Length Guidelines

- **1 character**: Only for counters (i, j, k) in short loops
- **2-3 characters**: Avoid except for standard abbreviations (id, db, ui)
- **4-20 characters**: Ideal range for most names
- **>20 characters**: Only if truly necessary for clarity

## Boolean Names

```python
# ✅ Use is_, has_, can_, should_ prefixes
is_valid = True
has_permission = check_permission()
can_delete = user.is_admin()
should_retry = error_count < MAX_RETRIES

# ❌ Avoid ambiguous names
valid = True  # Verb or adjective?
permission = True  # What about it?
```

## Function Names

```python
# ✅ Verbs or verb phrases
def fetch_user_data():
    pass

def calculate_tax(amount):
    pass

def validate_email(email):
    pass

# ❌ Avoid nouns for functions
def user_data():  # Should be get_user_data or fetch_user_data
    pass
```

