# Decoyable

> Open-source application security platform — secrets detection, SAST, dependency auditing, and active deception defense.

[![CI](https://github.com/Kolerr-Lab/decoyable/actions/workflows/ci.yml/badge.svg)](https://github.com/Kolerr-Lab/decoyable/actions)
[![License: BUSL-1.1](https://img.shields.io/badge/license-BUSL--1.1-orange.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![PyPI](https://img.shields.io/pypi/v/decoyable.svg)](https://pypi.org/project/decoyable/)
[![Security Policy](https://img.shields.io/badge/security-policy-informational.svg)](SECURITY.md)

---

## Overview

Decoyable is a security scanning and active defense platform built for engineering teams that need production-grade threat detection without operational complexity. It runs as a CLI tool, a REST API, or a VS Code extension.

- **Secrets scanning** — detects API keys, tokens, and credentials before they reach version control
- **SAST** — identifies injection, traversal, and logic vulnerabilities across Python codebases
- **Dependency auditing** — flags known CVEs in third-party packages
- **Active defense** — adaptive honeypots and AI-driven threat classification

---

## Installation

### PyPI

```bash
pip install decoyable
```

### Docker

```bash
docker compose up -d
curl http://localhost:8000/api/v1/health
```

### From source

```bash
git clone https://github.com/Kolerr-Lab/decoyable.git
cd decoyable
pip install -r requirements.txt
python -m decoyable.core.main --help
```

---

## Usage

### CLI

```bash
# Scan for hardcoded secrets
decoyable scan secrets

# Static analysis
decoyable scan sast

# Dependency CVEs
decoyable scan deps

# Full scan
decoyable scan all

# AI-powered analysis with active defense recommendations
decoyable ai-analyze . --dashboard
```

### REST API

```bash
# Start the API server
uvicorn decoyable.api.service:app --reload

# Endpoints
GET  /api/v1/health
POST /api/v1/scan/all
POST /api/v1/scan/secrets
GET  /api/v1/results
```

### VS Code Extension

Install from the `vscode-extension/` directory. The extension provides inline security diagnostics, real-time scanning on file save, and an integrated issues panel.

---

## Architecture

```
decoyable/
├── api/          # FastAPI application, routers, auth, rate limiting
├── core/         # Configuration, logging, database, task queue
├── scanners/     # Secrets, SAST, dependency, behavioral scanners
├── deception/    # Adaptive honeypot engine
├── defense/      # LLM-based attack analysis and IP blocking
├── llm/          # Multi-provider LLM router (OpenAI, Claude, Ollama)
├── ai/           # Predictive threat intelligence
└── streaming/    # Kafka integration for real-time event pipelines
```

Infrastructure: PostgreSQL · Redis · Kafka · Prometheus · Docker

---

## Configuration

Copy `.env.template` to `.env` and set required values:

```bash
cp .env.template .env
```

Key environment variables:

| Variable | Description |
|---|---|
| `SECRET_KEY` | Application secret key (min 32 chars) |
| `JWT_SECRET_KEY` | JWT signing key (min 32 chars) |
| `DATABASE_URL` | PostgreSQL connection string |
| `REDIS_URL` | Redis connection string |
| `ALLOWED_ORIGINS` | Comma-separated CORS origins |

---

## Security

Decoyable follows responsible disclosure. See [SECURITY.md](SECURITY.md) for the vulnerability reporting process.

Test files under `tests/` intentionally include vulnerable code patterns for scanner validation purposes. These patterns are not present in production code or distributed packages.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, branching conventions, and the pull request process.

---

## License

Business Source License 1.1 — see [LICENSE](LICENSE) for terms.  
Licensor: Kolerr Lab (Ricky Anh Nguyen) · Change Date: April 1, 2030 · Change License: Apache 2.0

