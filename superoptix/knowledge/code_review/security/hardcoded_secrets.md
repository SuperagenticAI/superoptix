# Hardcoded Secrets and Credentials

## Overview
Hardcoded credentials in source code pose severe security risks. They can be easily discovered through version control, decompilation, or source code leaks.

## Common Patterns to Avoid

### ❌ Vulnerable Code
```python
# Hardcoded API keys
API_KEY = "sk-1234567890abcdef"
AWS_SECRET = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"

# Hardcoded passwords
PASSWORD = "admin123"
DB_PASS = "MySecretPassword!"

# Hardcoded tokens
AUTH_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### ✅ Secure Code
```python
# Use environment variables
import os
API_KEY = os.environ.get('API_KEY')
AWS_SECRET = os.environ.get('AWS_SECRET_ACCESS_KEY')

# Use configuration files (not committed to git)
from config import get_secret
PASSWORD = get_secret('db_password')

# Use secret management services
from vault import get_secret
AUTH_TOKEN = get_secret('auth_token')
```

## Best Practices

1. **Use environment variables** - Store secrets outside code
2. **Secret management systems** - AWS Secrets Manager, HashiCorp Vault, Azure Key Vault
3. **Never commit .env files** - Add to .gitignore
4. **Rotate credentials regularly** - Change secrets periodically
5. **Use different secrets per environment** - Dev, staging, prod should have unique secrets
6. **Audit secret access** - Log and monitor who accesses secrets

## Detection Keywords

- "password =", "PASSWORD ="
- "api_key =", "API_KEY ="
- "secret =", "SECRET ="
- "token =", "TOKEN ="
- Long alphanumeric strings in assignments
- "sk-", "AWS", "Bearer" prefixes

## Impact
- **Severity**: CRITICAL
- **CVSS Score**: 9.0+
- Can lead to complete system compromise

