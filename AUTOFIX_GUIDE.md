# DECOYABLE Auto-Fix Feature - Complete Guide

## 🛠️ How Auto-Fix Works

The DECOYABLE auto-fix feature automatically remediates security vulnerabilities found during scanning. It uses pattern matching and intelligent code transformation to fix common security issues.

---

## 📋 Command Syntax

```bash
# Basic usage (requires confirmation)
decoyable fix --scan-results results.json --confirm

# Auto-approve all fixes (no confirmation)
decoyable fix --scan-results results.json --auto-approve

# Specify scan results file
decoyable fix --scan-results /path/to/scan_results.json --confirm
```

---

## 🔧 Supported Fix Types

### 1. **Hardcoded Secrets → Environment Variables**

**Before:**
```python
API_KEY = "sk-1234567890abcdef"
SECRET_TOKEN = "my_secret_token_123"
DATABASE_PASSWORD = "supersecret"
```

**After:**
```python
API_KEY = os.getenv("API_KEY", "")
SECRET_TOKEN = os.getenv("SECRET_TOKEN", "")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD", "")
```

**How it works:**
- Detects patterns: `VARIABLE = "value"` or `VARIABLE = 'value'`
- Replaces with `os.getenv("VARIABLE", "")`
- Requires "hardcoded" and "secret" in issue title

---

### 2. **Weak Cryptography (MD5 → SHA-256)**

**Before:**
```python
import hashlib

def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()

hash_value = hashlib.md5(data).digest()
```

**After:**
```python
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

hash_value = hashlib.sha256(data).digest()
```

**How it works:**
- Searches for "md5" in code (case-insensitive)
- Replaces with "sha256" or "SHA256"
- Triggered by "md5" or "weak crypto" in issue title

---

### 3. **Insecure Random → Secrets Module**

**Before:**
```python
import random

def generate_token():
    chars = "abcdefghijklmnopqrstuvwxyz0123456789"
    return ''.join(random.choice(chars) for _ in range(32))
```

**After:**
```python
import secrets

def generate_token():
    chars = "abcdefghijklmnopqrstuvwxyz0123456789"
    return ''.join(secrets.choice(chars) for _ in range(32))
```

**How it works:**
- Detects `random.choice()` usage
- Replaces `random.` with `secrets.`
- Triggered by "insecure random" or "weak random" in issue title

---

### 4. **Command Injection → IP Validation**

**Before:**
```python
import subprocess

def block_ip(ip_addr):
    cmd = f"iptables -A INPUT -s {ip_addr} -j DROP"
    subprocess.run(cmd, shell=True)
```

**After:**
```python
import subprocess
import ipaddress

def block_ip(ip_addr):
    ipaddress.ip_address(ip_addr)  # Validates IP format
    cmd = f"iptables -A INPUT -s {ip_addr} -j DROP"
    subprocess.run(cmd, shell=True)
```

**How it works:**
- Detects subprocess calls with IP addresses
- Inserts `ipaddress.ip_address()` validation before subprocess call
- Triggered by "command injection" in issue title

---

## 🎯 Complete Workflow Example

### Step 1: Scan Your Code

```bash
# Scan and save results to JSON
decoyable scan all . --format json > scan_results.json
```

### Step 2: Review Issues (Optional)

```bash
# View the scan results
cat scan_results.json
```

**Example output:**
```json
{
  "issues": [
    {
      "file": "app.py",
      "line": 15,
      "type": "secret",
      "severity": "high",
      "title": "Hardcoded secret detected: API_KEY"
    },
    {
      "file": "utils.py",
      "line": 42,
      "type": "crypto",
      "severity": "medium",
      "title": "Weak cryptography: MD5 usage"
    }
  ]
}
```

### Step 3: Apply Fixes

```bash
# Apply fixes with confirmation
decoyable fix --scan-results scan_results.json --confirm

# Or auto-approve all fixes
decoyable fix --scan-results scan_results.json --auto-approve
```

**Output:**
```
INFO: Found 2 issues to fix
INFO: Fixing 1 issues in app.py
INFO: Fixed: Hardcoded secret detected: API_KEY
INFO: Updated file: app.py
INFO: Fixing 1 issues in utils.py
INFO: Fixed: Weak cryptography: MD5 usage
INFO: Updated file: utils.py
INFO: Fixed 2 out of 2 issues
```

---

## 🔍 How the Fix Logic Works

### Internal Process Flow

1. **Load Scan Results**
   - Reads JSON file with security issues
   - Validates format and structure

2. **Group Issues by File**
   - Organizes issues per file for efficient processing
   - Prevents multiple file reads

3. **For Each File:**
   - Read file content into memory
   - Split into lines for line-based fixes
   - Apply fixes based on issue patterns

4. **Pattern Matching**
   ```python
   def _apply_fix_to_issue(self, lines, issue):
       title = issue.get("title", "").lower()
       line_num = issue.get("line", 0) - 1  # 0-based indexing
       
       # Check issue type and apply appropriate fix
       if "hardcoded" in title and "secret" in title:
           # Fix hardcoded secrets
       elif "md5" in title or "weak crypto" in title:
           # Fix weak cryptography
       elif "insecure random" in title:
           # Fix insecure random
       # ... more patterns
   ```

5. **Write Back**
   - Only writes if content changed
   - Respects confirmation flags

---

## ⚙️ Configuration Options

### `--scan-results` (Required)
Path to JSON file containing scan results.

**Example:**
```bash
decoyable fix --scan-results ./results.json
```

### `--auto-approve` (Optional)
Apply all fixes without confirmation. Includes low severity issues.

**Example:**
```bash
decoyable fix --scan-results results.json --auto-approve
```

### `--confirm` (Optional)
Prompt before applying each fix (default behavior).

**Example:**
```bash
decoyable fix --scan-results results.json --confirm
```

---

## 🛡️ Safety Features

1. **Severity Filtering**
   - Low severity issues skipped unless `--auto-approve`
   - Medium/High severity issues processed by default

2. **File Validation**
   - Checks if files exist before attempting fixes
   - Skips missing files with warning

3. **Content Preservation**
   - Only writes back if content actually changed
   - Original formatting preserved where possible

4. **Error Handling**
   - Graceful failure per file
   - Continues processing other files on error
   - Detailed logging of failures

---

## 💡 Best Practices

### 1. Always Scan First
```bash
# Good: Scan → Review → Fix
decoyable scan all . > results.json
cat results.json  # Review
decoyable fix --scan-results results.json --confirm
```

### 2. Use Version Control
```bash
# Commit before auto-fixing
git add .
git commit -m "Before auto-fix"
decoyable fix --scan-results results.json --auto-approve
git diff  # Review changes
```

### 3. Test After Fixing
```bash
# Apply fixes
decoyable fix --scan-results results.json --auto-approve

# Run tests to ensure nothing broke
pytest

# Scan again to verify fixes
decoyable scan all .
```

### 4. Review Changes
```bash
# See what was changed
git diff

# Or use your IDE's diff viewer
code --diff app.py.backup app.py
```

---

## 🎓 Advanced Usage

### Custom Fix Pipeline

```bash
#!/bin/bash
# advanced-fix.sh - Complete fix pipeline

echo "🔍 Step 1: Scanning codebase..."
decoyable scan all . --format json > scan_results.json

echo "📊 Step 2: Analyzing results..."
issues=$(jq '.issues | length' scan_results.json)
echo "Found $issues issues"

if [ $issues -gt 0 ]; then
    echo "🛠️ Step 3: Creating backup..."
    tar -czf backup-$(date +%Y%m%d-%H%M%S).tar.gz .
    
    echo "🔧 Step 4: Applying fixes..."
    decoyable fix --scan-results scan_results.json --auto-approve
    
    echo "✅ Step 5: Verifying fixes..."
    decoyable scan all . --format json > scan_results_after.json
    
    issues_after=$(jq '.issues | length' scan_results_after.json)
    fixed=$((issues - issues_after))
    
    echo "✨ Fixed $fixed out of $issues issues!"
else
    echo "✅ No issues found!"
fi
```

---

## 🔬 Technical Implementation

### Fix Function Signature

```python
async def run_fix_command(self, args: argparse.Namespace) -> int:
    """
    Apply automated fixes for security issues.
    
    Args:
        args: Command line arguments containing:
            - scan_results: Path to JSON scan results
            - auto_approve: Skip confirmation
            - confirm: Prompt for confirmation
    
    Returns:
        0 if successful, 1 if errors occurred
    """
```

### Fix Application Logic

```python
def _apply_fix_to_issue(self, lines: list[str], issue: Dict[str, Any]) -> bool:
    """
    Apply a fix for a specific issue.
    
    Args:
        lines: File content as list of lines
        issue: Issue dictionary with type, line, title, severity
    
    Returns:
        True if fix was successfully applied, False otherwise
    """
```

---

## 📈 Performance Characteristics

- **Speed**: ~100-500 issues/second (depending on issue complexity)
- **Memory**: Loads one file at a time into memory
- **Disk I/O**: One read + one write per modified file
- **Safety**: Validates before writing, skips on errors

---

## 🚨 Limitations

1. **Pattern-Based**: Only fixes known patterns
2. **Line-Based**: Works on individual lines (no multi-line fixes yet)
3. **No Syntax Checking**: Doesn't validate Python syntax after fix
4. **Limited Context**: Doesn't understand full code semantics
5. **Manual Review Recommended**: Always review auto-generated fixes

---

## 🎯 Future Enhancements

- [ ] AI-powered context-aware fixes using LLM
- [ ] Multi-line fix support
- [ ] Syntax validation after fixes
- [ ] Interactive fix mode with previews
- [ ] Undo/rollback functionality
- [ ] Custom fix patterns via config
- [ ] Fix quality scoring
- [ ] Integration with Git for automatic commits

---

## 📞 Support

- **Issues**: https://github.com/Kolerr-Lab/supper-decoyable/issues
- **Documentation**: See [README.md](README.md)
- **Email**: lab.kolerr@kolerr.com

---

**🛡️ DECOYABLE** - Making your code more secure, automatically! ✨
