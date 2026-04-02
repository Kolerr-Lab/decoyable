# Decoyable

**Application security platform with adaptive deception defense.**  
Scan for secrets, SAST vulnerabilities, and CVEs — then deploy self-learning honeypots that profile and waste attackers' time.

[![CI](https://github.com/Kolerr-Lab/decoyable/actions/workflows/ci.yml/badge.svg)](https://github.com/Kolerr-Lab/decoyable/actions)
[![PyPI](https://img.shields.io/pypi/v/decoyable.svg)](https://pypi.org/project/decoyable/)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://python.org)
[![License: BUSL-1.1](https://img.shields.io/badge/license-BUSL--1.1-orange.svg)](LICENSE)
[![Security](https://img.shields.io/badge/security-policy-informational.svg)](SECURITY.md)

---

## What it does

Most security tools stop at detection. Decoyable adds an active layer: after scanning your code, it can deploy adaptive honeypots that recognize attacker skill level (script kiddie → intermediate → advanced → elite), serve increasingly realistic decoys, and feed all activity into an AI threat intelligence pipeline.

**Scan layer:**
- Secrets scanner — AWS, GitHub, Slack, Google, and custom credential patterns; false-positive reduction via confidence scoring
- SAST — 13 vulnerability classes: SQL injection, XSS, command injection, path traversal, SSRF, XXE, insecure deserialization, weak crypto, eval usage, and more
- Dependency auditing — CVE lookup against the full dependency tree

**Defense layer:**
- Adaptive honeypots — decoy configuration mutates based on observed attacker tooling and behavior
- Attacker profiling — builds `AttackerProfile` objects tracking skill level, tools used, persistence score, and time-to-detection
- AI threat classification — routes through Ollama → OpenAI → Claude → Phi-3 → rule-based fallback; always works without an API key
- Kafka streaming — high-volume attack events pushed to configurable topics for SIEM integration

---

## Quick start

```bash
pip install decoyable

# Scan the current directory
decoyable scan all

# Start the API + honeypot stack
docker compose up -d
curl http://localhost:8000/api/v1/health
```

---

## Scan coverage

| Category | What's detected |
|---|---|
| **Secrets** | AWS Access Key / Secret, GitHub tokens (`ghp_`, `gho_`, `ghs_`, legacy), Slack (`xox*`), Google API Key, custom patterns |
| **SAST** | SQL injection, XSS, command injection, path traversal, SSRF, XXE, insecure deserialization, weak crypto, `eval()`, insecure HTTP, debug flags, hardcoded credentials, insecure random |
| **Dependencies** | Known CVEs in third-party packages, with severity and remediation |
| **Configuration** | Debug mode enabled in production, plaintext secrets in environment |

Findings include file path, line number, CWE ID, severity, confidence score, and remediation guidance.

---

## CLI reference

```bash
decoyable scan secrets                      # credential and token detection
decoyable scan sast                         # static vulnerability analysis
decoyable scan deps                         # dependency CVE audit
decoyable scan all                          # all three in sequence
decoyable scan all --format json            # structured output
decoyable ai-analyze . --dashboard          # AI threat summary with recommendations
```

---

## REST API

Start the server:

```bash
uvicorn decoyable.api.service:app --host 0.0.0.0 --port 8000
```

Core endpoints:

```
GET  /api/v1/health
POST /api/v1/scan/all        {"path": "/workspace/myapp"}
POST /api/v1/scan/secrets
POST /api/v1/scan/sast
POST /api/v1/scan/deps
GET  /api/v1/results
```

Authentication uses JWT bearer tokens or API keys. Rate limiting and CORS are configurable via environment variables.

---

## VS Code extension

The bundled extension (`vscode-extension/`) provides inline diagnostics on file save, a findings panel, and one-click navigation to vulnerable lines. Install locally:

```bash
cd vscode-extension
npm install
npx vsce package
code --install-extension decoyable-*.vsix
```

---

## Architecture

```
decoyable/
├── api/           FastAPI app — routers, JWT/API-key auth, rate limiting
├── core/          Config, logging, service registry, task orchestration
├── scanners/      Secrets, SAST, dependency scanners (async, DI-based)
├── deception/     Adaptive honeypot engine — profiles attackers, mutates decoys
├── defense/       IP blocking, behavioral anomaly detection
├── llm/           Model router: Ollama → OpenAI → Claude → Phi-3 → rule-based
├── ai/            Predictive threat intelligence, pattern learning
└── streaming/     Kafka producer/consumer for real-time event pipelines
```

**Infrastructure:** PostgreSQL (findings storage) · Redis (cache, task queue) · Kafka (event streaming) · Prometheus (metrics) · Docker Compose

**AI model priority** — Decoyable selects the best available provider at startup and falls back automatically:

```
1. Ollama + Llama 3.1   — local, free, preferred
2. OpenAI GPT-4         — if OPENAI_API_KEY is set
3. Anthropic Claude     — if ANTHROPIC_API_KEY is set
4. Phi-3 local          — lightweight local fallback
5. Pattern-based        — no LLM required, always available
```

---

## Deployment

### Docker Compose (recommended)

```bash
cp .env.template .env        # fill in SECRET_KEY, JWT_SECRET_KEY, DATABASE_URL
docker compose up -d
```

Services started: `api`, `worker`, `postgres`, `redis`, `kafka`, `prometheus`, `grafana`

### From source

```bash
git clone https://github.com/Kolerr-Lab/decoyable.git
cd decoyable
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.template .env        # configure environment
uvicorn decoyable.api.service:app --reload
```

---

## Configuration reference

```bash
cp .env.template .env
```

| Variable | Required | Description |
|---|---|---|
| `SECRET_KEY` | Yes | Application secret (min 32 chars) |
| `JWT_SECRET_KEY` | Yes | JWT signing key (min 32 chars) |
| `DATABASE_URL` | Yes | PostgreSQL DSN (`postgresql://user@host/db`) |
| `REDIS_URL` | Yes | Redis DSN (`redis://:pass@host:6379/0`) |
| `ALLOWED_ORIGINS` | Yes | Comma-separated CORS origins — no wildcards in production |
| `ALLOWED_HOSTS` | Yes | Comma-separated trusted hostnames |
| `HONEYPOT_ENABLED` | No | Enable adaptive honeypot engine (default: `true`) |
| `DECOY_PORTS` | No | Ports to expose as decoys (default: `9001,2222`) |
| `KAFKA_ENABLED` | No | Enable Kafka event streaming (default: `false`) |
| `OPENAI_API_KEY` | No | OpenAI key — enables GPT-4 threat analysis |
| `ANTHROPIC_API_KEY` | No | Anthropic key — Claude fallback provider |
| `SCANNERS_MIN_CONFIDENCE` | No | Minimum confidence threshold for findings (default: `0.8`) |
| `SCANNERS_SEVERITY_THRESHOLD` | No | Minimum severity to report: `LOW`, `MEDIUM`, `HIGH`, `CRITICAL` |

Full variable reference: [`.env.template`](.env.template)

---

## Security

Decoyable follows responsible disclosure. Report vulnerabilities via [SECURITY.md](SECURITY.md).

Test files under `tests/` contain intentional vulnerable patterns used for scanner validation. These are excluded from distributed packages.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for environment setup, branching strategy, and the pull request process.

---

## License

Business Source License 1.1 — see [LICENSE](LICENSE) for terms.  
Licensor: Kolerr Lab (Ricky Anh Nguyen) · Change Date: April 1, 2030 · Change License: Apache 2.0

