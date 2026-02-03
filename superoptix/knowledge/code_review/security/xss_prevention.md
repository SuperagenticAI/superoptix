# Cross-Site Scripting (XSS) Prevention

## Overview
XSS attacks occur when untrusted data is included in web pages without proper validation or escaping, allowing attackers to execute malicious scripts.

## Types of XSS

1. **Reflected XSS** - Immediate response from server
2. **Stored XSS** - Malicious script stored in database
3. **DOM-based XSS** - Client-side script manipulation

## Common Patterns

### ❌ Vulnerable Code
```python
# Flask - Direct HTML rendering
@app.route('/search')
def search():
    query = request.args.get('q')
    return f"<h1>Results for: {query}</h1>"  # VULNERABLE!

# JavaScript - Direct DOM manipulation
document.getElementById('output').innerHTML = userInput;  // VULNERABLE!
```

### ✅ Secure Code
```python
# Flask - Use template escaping
from flask import render_template_string, escape

@app.route('/search')
def search():
    query = escape(request.args.get('q'))
    return render_template_string("<h1>Results for: {{ query }}</h1>", query=query)

# JavaScript - Use textContent instead of innerHTML
document.getElementById('output').textContent = userInput;  // SAFE
```

## Best Practices

1. **Always escape output** - Never trust user input
2. **Use framework protections** - Modern frameworks auto-escape
3. **Content Security Policy (CSP)** - Restrict script sources
4. **Validate input** - Whitelist allowed characters
5. **Use HTTP-only cookies** - Prevent JavaScript access to cookies

## OWASP Ranking
#3 in OWASP Top 10

