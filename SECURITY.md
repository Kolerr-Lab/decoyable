# Security Policy for DECOYABLE

## Purpose
This project includes test files that intentionally use dangerous patterns (such as `os.system`, `subprocess` with `shell=True`, `eval`, and `exec`) for the purpose of testing, demonstration, and validation of security scanners. **These patterns are NOT present in production code.**

## Test Files
- All files in the `tests/` directory may contain code that would be considered a security risk in production.
- These files are used to:
  - Demonstrate detection of vulnerabilities
  - Validate the effectiveness of DECOYABLE's scanners and defenses
  - Provide regression tests for auto-fix and remediation features

## Production Code
- All production modules are reviewed to ensure no unsafe patterns are present.
- Dangerous patterns are only present in test files and are never shipped in deployment or production builds.

## Excluding Test Files from Production
- The `tests/` directory is excluded from all deployment and distribution packages (see MANIFEST.in and setup configuration).
- Only production code is included in PyPI and Docker releases.

## Reporting Security Issues
If you believe you have found a security vulnerability in DECOYABLE, please report it via the [GitHub Issues page](https://github.com/Kolerr-Lab/supper-decoyable/issues) or contact the maintainers directly.

---

**DECOYABLE: Security is our top priority.**
