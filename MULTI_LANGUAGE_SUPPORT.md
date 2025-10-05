# DECOYABLE Multi-Language Support

## 🌍 Can DECOYABLE Work with Other Languages?

**Short Answer: YES! DECOYABLE can work with multiple languages, with varying levels of support.**

---

## 📊 Current Language Support Status

### 🟢 **Full Support (Python)**

DECOYABLE is **primarily built for Python** and provides **complete, comprehensive scanning**:

✅ **Secret Detection** - Hardcoded API keys, passwords, tokens
✅ **Dependency Analysis** - PyPI packages, vulnerabilities, missing deps
✅ **SAST (Static Analysis)** - SQL injection, XSS, command injection, path traversal
✅ **AI-Powered Analysis** - 8 AI systems (predictive threats, anomaly detection, exploit chains)
✅ **Auto-Fix** - Automated vulnerability remediation
✅ **Real-time Scanning** - VS Code extension integration
✅ **Honeypot Defense** - Active attack detection and response

**Why Python First?**
- DECOYABLE itself is written in Python
- Rich ecosystem for security tools
- Large enterprise user base
- Comprehensive AST (Abstract Syntax Tree) support

---

### 🟡 **Partial Support (Multi-Language)**

DECOYABLE can **scan other languages** with **language-agnostic features**:

#### **Supported Languages (VS Code Extension)**
1. **JavaScript** (`.js`)
2. **TypeScript** (`.ts`)
3. **Java** (`.java`)
4. **C/C++** (`.cpp`, `.c`)
5. **PHP** (`.php`)
6. **Ruby** (`.rb`)
7. **Go** (`.go`)
8. **Rust** (`.rs`)

#### **What Works Cross-Language?**

✅ **Secret Detection** (Universal)
- API keys, tokens, passwords in any text file
- Pattern-based detection (regex)
- Works across **ALL languages**
- No AST parsing needed

✅ **File Scanning** (Universal)
- Reads any text-based source file
- Detects hardcoded credentials
- Finds suspicious patterns

✅ **Basic Pattern Matching** (Universal)
- SQL injection patterns in strings
- Command injection patterns
- Path traversal attempts
- Works in comments and strings across languages

---

### 🔴 **Limited Support (Language-Specific Features)**

Some features require **language-specific parsers**:

❌ **Dependency Analysis** - Currently Python-only
- Requires `requirements.txt`, `setup.py`, `pyproject.toml` parsing
- **Future**: Can be extended to `package.json` (Node), `pom.xml` (Java), `Gemfile` (Ruby), `go.mod` (Go)

❌ **Advanced SAST** - Python AST-based
- Deep code flow analysis
- Function call tracking
- Variable taint analysis
- **Future**: Can use language-specific parsers

❌ **Auto-Fix** - Python patterns only
- Currently fixes Python-specific patterns
- **Future**: Can be extended with language-specific transformations

---

## 🎯 Language-by-Language Breakdown

### **JavaScript / Node.js**

**Current Support:**
✅ Secret detection (API keys, tokens)
✅ Pattern-based vulnerability detection
✅ VS Code extension integration

**What Can Be Added:**
- 🔄 `package.json` dependency scanning
- 🔄 NPM vulnerability database integration
- 🔄 JavaScript AST parsing for SAST
- 🔄 Auto-fix for JS-specific patterns

**Example Detection:**
```javascript
// ✅ DETECTS: Hardcoded secrets
const API_KEY = "sk-1234567890abcdef";

// ✅ DETECTS: SQL injection patterns
const query = `SELECT * FROM users WHERE id = ${userId}`;

// ⚠️ LIMITED: No dependency analysis yet
// package.json vulnerabilities not scanned
```

---

### **Java**

**Current Support:**
✅ Secret detection (API keys, JDBC passwords)
✅ Pattern-based vulnerability detection
✅ VS Code extension integration

**What Can Be Added:**
- 🔄 `pom.xml` / `build.gradle` dependency scanning
- 🔄 Maven Central vulnerability database
- 🔄 Java AST parsing for SAST
- 🔄 Spring Security configuration analysis

**Example Detection:**
```java
// ✅ DETECTS: Hardcoded credentials
String apiKey = "sk-1234567890abcdef";
String dbPassword = "admin123";

// ✅ DETECTS: SQL injection patterns
String query = "SELECT * FROM users WHERE name = '" + userName + "'";

// ⚠️ LIMITED: No Maven/Gradle analysis yet
```

---

### **Ruby**

**Current Support:**
✅ Secret detection (API keys, Rails secrets)
✅ Pattern-based vulnerability detection
✅ VS Code extension integration

**What Can Be Added:**
- 🔄 `Gemfile` / `Gemfile.lock` dependency scanning
- 🔄 RubyGems vulnerability database
- 🔄 Ruby AST parsing for Rails-specific issues
- 🔄 Auto-fix for Ruby patterns

**Example Detection:**
```ruby
# ✅ DETECTS: Hardcoded secrets
api_key = "sk-1234567890abcdef"
secret_token = "my_secret_123"

# ✅ DETECTS: SQL injection patterns
query = "SELECT * FROM users WHERE name = '#{user_name}'"

# ⚠️ LIMITED: No Gemfile analysis yet
```

---

### **Go**

**Current Support:**
✅ Secret detection (API keys, tokens)
✅ Pattern-based vulnerability detection
✅ VS Code extension integration

**What Can Be Added:**
- 🔄 `go.mod` / `go.sum` dependency scanning
- 🔄 Go vulnerability database integration
- 🔄 Go AST parsing for concurrency issues
- 🔄 Auto-fix for Go patterns

**Example Detection:**
```go
// ✅ DETECTS: Hardcoded credentials
const apiKey = "sk-1234567890abcdef"
dbPassword := "admin123"

// ✅ DETECTS: Command injection
cmd := exec.Command("sh", "-c", userInput)

// ⚠️ LIMITED: No go.mod analysis yet
```

---

## 🚀 How to Use DECOYABLE with Other Languages

### **1. Secret Detection (Works Now)**

```bash
# Scan any codebase for secrets
decoyable scan secrets /path/to/java/project
decoyable scan secrets /path/to/node/project
decoyable scan secrets /path/to/go/project

# Works with ANY text-based files
decoyable scan secrets /path/to/ruby/app
```

**What It Finds:**
- Hardcoded API keys (AWS, GitHub, OpenAI, etc.)
- Database passwords
- JWT tokens
- Private keys
- OAuth secrets
- Service credentials

---

### **2. Pattern-Based SAST (Works Now)**

```bash
# Basic vulnerability patterns in any language
decoyable scan sast /path/to/project

# Looks for:
# - SQL injection patterns
# - Command injection patterns
# - Path traversal attempts
# - XSS patterns
# - Hardcoded credentials
```

**What It Detects:**
- String concatenation in SQL queries
- Shell command construction
- File path manipulation
- Eval/exec patterns
- Weak cryptography usage

---

### **3. VS Code Extension (Multi-Language)**

The VS Code extension **already supports 10 languages**:

```json
{
  "decoyable.scanOnSave": true,
  "decoyable.supportedLanguages": [
    "python", "javascript", "typescript",
    "java", "cpp", "c", "php", "ruby",
    "go", "rust"
  ]
}
```

**Features Available:**
- ✅ Real-time secret detection
- ✅ On-save scanning
- ✅ Diagnostics panel
- ✅ Quick fix suggestions
- ✅ Security issue highlighting

---

## 🔮 Roadmap: Full Multi-Language Support

### **v1.1.0 - JavaScript/Node.js Support**
- ✅ `package.json` dependency scanning
- ✅ NPM audit integration
- ✅ JavaScript AST parsing
- ✅ Auto-fix for JS patterns

### **v1.2.0 - Java Support**
- ✅ Maven (`pom.xml`) scanning
- ✅ Gradle (`build.gradle`) scanning
- ✅ OWASP Dependency Check integration
- ✅ Java AST parsing

### **v1.3.0 - Go Support**
- ✅ `go.mod` dependency scanning
- ✅ Go vulnerability database
- ✅ Go AST parsing
- ✅ Concurrency issue detection

### **v1.4.0 - Ruby Support**
- ✅ `Gemfile` dependency scanning
- ✅ Bundler audit integration
- ✅ Rails-specific security checks
- ✅ Ruby AST parsing

### **v2.0.0 - Universal Language Support**
- ✅ Polyglot project scanning
- ✅ Multi-language dependency graphs
- ✅ Cross-language vulnerability correlation
- ✅ Language-agnostic AI analysis

---

## 💡 Current Workarounds for Other Languages

### **Option 1: Use Secret Detection Only**
```bash
# Works perfectly for any language
decoyable scan secrets /path/to/any/project
```

### **Option 2: Use Pattern-Based SAST**
```bash
# Basic vulnerability patterns
decoyable scan sast /path/to/any/project
```

### **Option 3: Use VS Code Extension**
```typescript
// Install extension
code --install-extension vscode-extension/decoyable-security-1.0.0.vsix

// Enable for your language
"decoyable.scanOnSave": true
```

### **Option 4: Custom Integration**
```python
# Use DECOYABLE's API
import requests

# Call secret scanner
response = requests.post("http://localhost:8000/api/v1/scan/secrets", json={
    "path": "/path/to/java/project",
    "recursive": true
})

print(response.json())
```

---

## 🎓 How to Extend DECOYABLE for Your Language

### **Step 1: Add Language-Specific Scanner**

```python
# decoyable/scanners/java_scanner.py
from pathlib import Path
from typing import List, Dict

class JavaScanner:
    def scan_dependencies(self, path: Path) -> List[Dict]:
        """Scan pom.xml or build.gradle"""
        # Parse Maven/Gradle files
        # Check vulnerability databases
        # Return issues
        pass
```

### **Step 2: Register Scanner**

```python
# decoyable/core/registry.py
from decoyable.scanners.java_scanner import JavaScanner

registry.register_scanner("java", JavaScanner())
```

### **Step 3: Add Language Patterns**

```python
# decoyable/patterns/java_patterns.py
JAVA_VULNERABILITY_PATTERNS = {
    "sql_injection": r"Statement\.execute\(.*\+.*\)",
    "path_traversal": r"new File\(.*\+.*\)",
    # ... more patterns
}
```

---

## 📊 Feature Comparison Matrix

| Feature | Python | JavaScript | Java | Ruby | Go | Other |
|---------|--------|------------|------|------|----|----- |
| **Secret Detection** | ✅ Full | ✅ Full | ✅ Full | ✅ Full | ✅ Full | ✅ Full |
| **Pattern-Based SAST** | ✅ Full | ✅ Good | ✅ Good | ✅ Good | ✅ Good | ✅ Basic |
| **Dependency Scanning** | ✅ Full | 🔄 Planned | 🔄 Planned | 🔄 Planned | 🔄 Planned | ❌ No |
| **Advanced SAST** | ✅ Full | 🔄 Planned | 🔄 Planned | 🔄 Planned | 🔄 Planned | ❌ No |
| **Auto-Fix** | ✅ Full | 🔄 Planned | 🔄 Planned | 🔄 Planned | 🔄 Planned | ❌ No |
| **AI Analysis** | ✅ Full | ✅ Partial | ✅ Partial | ✅ Partial | ✅ Partial | ✅ Partial |
| **VS Code Integration** | ✅ Full | ✅ Full | ✅ Full | ✅ Full | ✅ Full | ✅ Full |

Legend:
- ✅ Full: Complete implementation
- ✅ Partial: Limited functionality available
- ✅ Good: Works well with some limitations
- 🔄 Planned: On roadmap
- ❌ No: Not supported

---

## 🎯 Real-World Usage Examples

### **Example 1: Java Spring Boot Project**

```bash
# What works NOW
$ decoyable scan secrets src/main/java/
Found 3 hardcoded secrets:
  - AWS_ACCESS_KEY in ApplicationConfig.java:45
  - DB_PASSWORD in DataSourceConfig.java:67
  - API_SECRET in RestController.java:23

# What will work in v1.2.0
$ decoyable scan deps pom.xml
Found 5 vulnerable dependencies:
  - log4j 2.14.0 (CVE-2021-44228)
  - spring-security 5.3.0 (CVE-2021-22112)
```

### **Example 2: Node.js Express App**

```bash
# What works NOW
$ decoyable scan secrets src/
Found 2 hardcoded secrets:
  - JWT_SECRET in config.js:12
  - MONGODB_URI in database.js:5

# What will work in v1.1.0
$ decoyable scan deps package.json
Found 8 vulnerable packages:
  - express 4.16.0 (8 vulnerabilities)
  - mongoose 5.7.0 (2 vulnerabilities)
```

### **Example 3: Go Microservice**

```bash
# What works NOW
$ decoyable scan secrets cmd/
Found 1 hardcoded secret:
  - API_TOKEN in main.go:34

# What will work in v1.3.0
$ decoyable scan deps go.mod
Found 3 vulnerable modules:
  - github.com/gin-gonic/gin v1.6.0 (CVE-2020-28483)
```

---

## ✨ Summary

### **YES, DECOYABLE Can Work with Other Languages!**

**Right Now (v1.0.5):**
✅ Secret detection works perfectly across **ALL languages**
✅ Pattern-based SAST works for **basic vulnerabilities**
✅ VS Code extension supports **10 languages**
✅ AI analysis provides **universal insights**

**Coming Soon (v1.1-1.4):**
🔄 Full dependency scanning for JavaScript, Java, Ruby, Go
🔄 Language-specific AST parsing
🔄 Advanced SAST for each language
🔄 Auto-fix for language-specific patterns

**Long Term (v2.0):**
🚀 Universal language support
🚀 Polyglot project analysis
🚀 Cross-language vulnerability correlation

---

## 🤝 Contributing Language Support

Want to add support for your favorite language? We welcome contributions!

**Steps:**
1. Fork the repository
2. Create a scanner for your language
3. Add vulnerability patterns
4. Write tests
5. Submit a pull request

**Resources:**
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [Developer Guide](https://github.com/Kolerr-Lab/supper-decoyable/wiki)
- [Scanner API Reference](https://github.com/Kolerr-Lab/supper-decoyable/wiki/Scanner-API)

---

## 📞 Questions?

- **General**: https://github.com/Kolerr-Lab/supper-decoyable/discussions
- **Feature Requests**: https://github.com/Kolerr-Lab/supper-decoyable/issues
- **Email**: lab.kolerr@kolerr.com
- **Support**: https://buymeacoffee.com/rickykolerr

---

**🛡️ DECOYABLE** - Security scanning for **every language**, starting with Python! 🌍
