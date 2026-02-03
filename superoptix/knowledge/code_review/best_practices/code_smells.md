# Code Smells and Refactoring

## Overview
Code smells are indicators of potential problems in code. They don't prevent code from working but make it harder to maintain.

## Common Code Smells

### 1. Duplicated Code (DRY Violation)

#### ❌ Duplicated Logic
```python
def calculate_price_with_tax(price):
    tax = price * 0.1
    total = price + tax
    return total

def calculate_discounted_price_with_tax(price, discount):
    discounted_price = price - (price * discount)
    tax = discounted_price * 0.1  # Tax calculation duplicated!
    total = discounted_price + tax
    return total
```

#### ✅ Extract Common Logic
```python
def apply_tax(price, tax_rate=0.1):
    return price * (1 + tax_rate)

def calculate_price_with_tax(price):
    return apply_tax(price)

def calculate_discounted_price_with_tax(price, discount):
    discounted_price = price * (1 - discount)
    return apply_tax(discounted_price)
```

### 2. Long Method (God Function)

#### ❌ Too Many Responsibilities
```python
def process_order(order_data):
    # Validate
    if not order_data.get('customer_id'):
        raise ValueError("Missing customer")
    if not order_data.get('items'):
        raise ValueError("No items")
    
    # Calculate
    subtotal = sum(item['price'] * item['qty'] for item in order_data['items'])
    tax = subtotal * 0.1
    total = subtotal + tax
    
    # Save
    db.insert('orders', order_data)
    
    # Email
    send_email(order_data['customer_email'], f"Order total: ${total}")
    
    # Inventory
    for item in order_data['items']:
        update_inventory(item['id'], -item['qty'])
    
    return total
```

#### ✅ Split into Focused Functions
```python
def validate_order(order_data):
    if not order_data.get('customer_id'):
        raise ValueError("Missing customer")
    if not order_data.get('items'):
        raise ValueError("No items")

def calculate_order_total(items):
    subtotal = sum(item['price'] * item['qty'] for item in items)
    tax = subtotal * 0.1
    return subtotal + tax

def update_inventory_for_order(items):
    for item in items:
        update_inventory(item['id'], -item['qty'])

def process_order(order_data):
    validate_order(order_data)
    total = calculate_order_total(order_data['items'])
    db.insert('orders', {**order_data, 'total': total})
    send_confirmation_email(order_data['customer_email'], total)
    update_inventory_for_order(order_data['items'])
    return total
```

### 3. Large Class (God Object)

Signs:
- Too many methods (>20)
- Too many fields (>10)
- Multiple responsibilities

**Refactor**: Split into multiple classes with single responsibilities

### 4. Long Parameter List

#### ❌ Too Many Parameters
```python
def create_user(name, email, phone, address, city, state, zip, country, age, gender):
    pass  # Hard to call, easy to mix up order
```

#### ✅ Use Data Class or Dict
```python
from dataclasses import dataclass

@dataclass
class UserData:
    name: str
    email: str
    phone: str
    address: str
    city: str
    state: str
    zip: str
    country: str
    age: int
    gender: str

def create_user(user_data: UserData):
    pass  # Much cleaner!
```

### 5. Magic Numbers

#### ❌ Unexplained Constants
```python
def calculate_shipping(weight):
    if weight < 5:
        return weight * 2.5
    elif weight < 20:
        return weight * 2.0
    else:
        return weight * 1.5 + 10
```

#### ✅ Named Constants
```python
LIGHT_PACKAGE_THRESHOLD = 5
MEDIUM_PACKAGE_THRESHOLD = 20
LIGHT_RATE = 2.5
MEDIUM_RATE = 2.0
HEAVY_RATE = 1.5
HEAVY_BASE_FEE = 10

def calculate_shipping(weight):
    if weight < LIGHT_PACKAGE_THRESHOLD:
        return weight * LIGHT_RATE
    elif weight < MEDIUM_PACKAGE_THRESHOLD:
        return weight * MEDIUM_RATE
    else:
        return weight * HEAVY_RATE + HEAVY_BASE_FEE
```

### 6. Comments as Deodorant

#### ❌ Explaining Bad Code
```python
# Loop through all items and find duplicates by comparing each item with every other item
def f(x):
    r = []
    for i in range(len(x)):
        for j in range(len(x)):
            if i != j and x[i] == x[j] and x[i] not in r:
                r.append(x[i])
    return r
```

#### ✅ Self-Documenting Code
```python
def find_duplicate_items(items):
    """Returns list of items that appear more than once."""
    from collections import Counter
    item_counts = Counter(items)
    return [item for item, count in item_counts.items() if count > 1]
```

## Refactoring Techniques

1. **Extract Method** - Break long methods into smaller ones
2. **Extract Class** - Move related fields/methods to new class
3. **Rename** - Use descriptive names
4. **Introduce Parameter Object** - Group parameters into object
5. **Replace Magic Number with Constant** - Name your constants
6. **Simplify Conditional** - Extract complex conditions to methods

## When to Refactor

- Before adding new features
- When fixing bugs in messy code
- During code review
- When code becomes hard to understand
- **Not**: Right before deployment!

