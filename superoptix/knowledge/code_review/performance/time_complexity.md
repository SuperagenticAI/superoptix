# Time Complexity and Performance Optimization

## Overview
Understanding algorithmic complexity helps write efficient code. Big O notation describes how runtime grows with input size.

## Common Time Complexities

| Complexity | Name | Example |
|------------|------|---------|
| O(1) | Constant | Array access, hash table lookup |
| O(log n) | Logarithmic | Binary search |
| O(n) | Linear | Single loop, array traversal |
| O(n log n) | Linearithmic | Efficient sorting (merge sort, quick sort) |
| O(n²) | Quadratic | Nested loops |
| O(2ⁿ) | Exponential | Recursive fibonacci |

## Common Performance Issues

### ❌ Nested Loops (O(n²))
```python
# Finding duplicates - SLOW for large lists
def find_duplicates(items):
    duplicates = []
    for i in range(len(items)):
        for j in range(len(items)):  # Nested loop!
            if i != j and items[i] == items[j]:
                if items[i] not in duplicates:
                    duplicates.append(items[i])
    return duplicates
```

### ✅ Using Set (O(n))
```python
# Finding duplicates - FAST
from collections import Counter

def find_duplicates(items):
    counts = Counter(items)
    return [item for item, count in counts.items() if count > 1]
```

### ❌ List Concatenation in Loop
```python
# String building - SLOW (creates new string each time)
result = ""
for item in items:
    result += str(item)  # O(n²) due to string immutability
```

### ✅ Using Join
```python
# String building - FAST
result = "".join(str(item) for item in items)  # O(n)
```

### ❌ Repeated Computation
```python
# Computing same value repeatedly
def process_items(items):
    for item in items:
        if item > len(items) / 2:  # len() called every iteration!
            process(item)
```

### ✅ Cache Computation
```python
# Compute once, reuse
def process_items(items):
    threshold = len(items) / 2  # Computed once
    for item in items:
        if item > threshold:
            process(item)
```

## Data Structure Selection

### Lists vs Sets
```python
# ❌ Membership check in list: O(n)
if item in my_list:  # Slow for large lists
    pass

# ✅ Membership check in set: O(1)
if item in my_set:  # Fast even for large sets
    pass
```

### Lists vs Deques
```python
# ❌ Inserting at front of list: O(n)
my_list.insert(0, item)  # Shifts all elements

# ✅ Inserting at front of deque: O(1)
from collections import deque
my_deque.appendleft(item)  # Constant time
```

## Space-Time Tradeoffs

Sometimes using more memory improves speed:

```python
# Fibonacci with memoization
from functools import lru_cache

@lru_cache(maxsize=None)
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
# Without cache: O(2ⁿ)
# With cache: O(n)
```

## Performance Tips

1. **Avoid premature optimization** - Profile first
2. **Use built-in functions** - Usually optimized in C
3. **Choose right data structures** - Set for membership, dict for lookups
4. **Minimize nested loops** - Often indicates O(n²) or worse
5. **Cache expensive computations** - Trade space for time
6. **Use generators** - For large datasets, avoid loading all in memory

