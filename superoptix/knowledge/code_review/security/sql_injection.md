# SQL Injection Prevention

## Overview
SQL injection is one of the most critical web application vulnerabilities. It occurs when untrusted data is sent to an interpreter as part of a command or query.

## Common Patterns

### ❌ Vulnerable Code
```python
# String concatenation - NEVER DO THIS
query = "SELECT * FROM users WHERE username = '" + username + "'"
db.execute(query)

# String formatting - STILL VULNERABLE
query = f"SELECT * FROM users WHERE id = {user_id}"
db.execute(query)
```

### ✅ Secure Code
```python
# Parameterized queries - ALWAYS USE THIS
query = "SELECT * FROM users WHERE username = ?"
db.execute(query, (username,))

# Or using named parameters
query = "SELECT * FROM users WHERE username = :username"
db.execute(query, {"username": username})
```

## Best Practices

1. **Always use parameterized queries** - Never concatenate user input into SQL
2. **Use ORM frameworks** - SQLAlchemy, Django ORM provide automatic protection
3. **Validate input** - Even with parameterization, validate input types
4. **Principle of least privilege** - Database users should have minimal permissions
5. **Use stored procedures** - When appropriate, stored procedures can add security

## Detection Patterns

Look for:
- String concatenation with `+` or `f"{}"` in SQL queries
- `.format()` method used with SQL
- User input directly in query strings
- Dynamic table or column names from user input

## OWASP Reference
Ranked #1 in OWASP Top 10 Web Application Security Risks

