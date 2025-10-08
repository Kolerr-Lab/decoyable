"""
Intelligent AI model router with automatic fallback.
Priority: Ollama → OpenAI → Claude → Phi-3 → Pattern-based

This ensures DECOYABLE always works, even without any AI provider configured.
"""

import os
import logging
from typing import Dict, Any, Optional, List
from enum import Enum

from decoyable.llm.ollama_client import OllamaClient


class AIProvider(Enum):
    """Available AI providers in priority order."""
    OLLAMA = "ollama"          # Priority 1: Local, free
    OPENAI = "openai"          # Priority 2: Cloud, paid
    CLAUDE = "claude"          # Priority 3: Cloud, paid
    PHI3_LOCAL = "phi3_local"  # Priority 4: Local fallback
    PATTERN = "pattern"        # Priority 5: Always works


class AIModelRouter:
    """
    Intelligent router that selects the best available AI model.
    
    Priority Order:
    1. Ollama + Llama 3.1 (local, free, best quality)
    2. OpenAI GPT-4 (if API key available)
    3. Anthropic Claude (if API key available)
    4. Phi-3 local (lightweight fallback)
    5. Pattern-based (no AI, always works)
    
    Features:
    - Auto-detection of available providers
    - Graceful fallback if provider fails
    - Cost tracking (local = $0)
    - Privacy-aware (prefers local)
    """
    
    def __init__(self):
        """Initialize router and detect available providers."""
        self.logger = logging.getLogger(__name__)
        self.providers = self._detect_available_providers()
        self.active_provider = self.providers[0] if self.providers else AIProvider.PATTERN
        
        self.logger.info(f"✓ AI Router initialized with {len(self.providers)} provider(s)")
        self.logger.info(f"  Active: {self.active_provider.value}")
        
        # Initialize clients
        self.ollama_client = None
        self.openai_client = None
        self.claude_client = None
        self.phi3_client = None
        
        self._initialize_clients()
    
    def _detect_available_providers(self) -> List[AIProvider]:
        """
        Detect which AI providers are available on this system.
        
        Returns:
            List of available providers in priority order
        """
        available = []
        
        # Check Ollama (Priority 1)
        if self._check_ollama():
            available.append(AIProvider.OLLAMA)
            self.logger.info("  ✓ Ollama available (LOCAL, FREE)")
        else:
            self.logger.info("  ✗ Ollama not found (install: https://ollama.com)")
        
        # Check OpenAI API key (Priority 2)
        if os.getenv("OPENAI_API_KEY"):
            available.append(AIProvider.OPENAI)
            self.logger.info("  ✓ OpenAI API key found (CLOUD, PAID)")
        else:
            self.logger.debug("  ✗ OpenAI API key not set")
        
        # Check Anthropic API key (Priority 3)
        if os.getenv("ANTHROPIC_API_KEY"):
            available.append(AIProvider.CLAUDE)
            self.logger.info("  ✓ Anthropic API key found (CLOUD, PAID)")
        else:
            self.logger.debug("  ✗ Anthropic API key not set")
        
        # Phi-3 local (Priority 4) - Check if transformers installed
        try:
            import transformers
            available.append(AIProvider.PHI3_LOCAL)
            self.logger.info("  ✓ Phi-3 available (LOCAL, FREE)")
        except ImportError:
            self.logger.debug("  ✗ Transformers not installed (pip install transformers)")
        
        # Pattern-based always available (Priority 5)
        available.append(AIProvider.PATTERN)
        self.logger.info("  ✓ Pattern-based analysis (ALWAYS AVAILABLE)")
        
        return available
    
    def _check_ollama(self) -> bool:
        """Quick check if Ollama is running."""
        try:
            import httpx
            response = httpx.get("http://localhost:11434/api/tags", timeout=1.0)
            return response.status_code == 200
        except Exception:
            return False
    
    def _initialize_clients(self):
        """Initialize clients for available providers."""
        if AIProvider.OLLAMA in self.providers:
            self.ollama_client = OllamaClient()
        
        if AIProvider.OPENAI in self.providers:
            try:
                from decoyable.llm.providers.openai_provider import OpenAIProvider
                self.openai_client = OpenAIProvider()
                self.logger.info("  ✓ OpenAI client initialized")
            except Exception as e:
                self.logger.warning(f"Failed to init OpenAI: {e}")
                self.openai_client = None
        
        if AIProvider.CLAUDE in self.providers:
            try:
                from decoyable.llm.providers.anthropic_provider import AnthropicProvider
                self.claude_client = AnthropicProvider()
                self.logger.info("  ✓ Claude client initialized")
            except Exception as e:
                self.logger.warning(f"Failed to init Claude: {e}")
                self.claude_client = None
        
        if AIProvider.PHI3_LOCAL in self.providers:
            try:
                from decoyable.llm.phi3_local import Phi3LocalClient
                self.phi3_client = Phi3LocalClient()
            except Exception as e:
                self.logger.warning(f"Failed to init Phi-3: {e}")
    
    async def analyze(
        self,
        code: str,
        context: Optional[Dict[str, Any]] = None,
        task: str = "security_analysis",
        prefer_local: bool = True
    ) -> Dict[str, Any]:
        """
        Analyze code using the best available AI model.
        
        Args:
            code: Code to analyze
            context: Additional context
            task: Type of analysis
            prefer_local: Prefer local models over cloud (privacy)
        
        Returns:
            Analysis results with metadata about provider used
        """
        # Try providers in priority order
        for provider in self.providers:
            if prefer_local and provider in [AIProvider.OPENAI, AIProvider.CLAUDE]:
                # Skip cloud providers if local preference set
                continue
            
            try:
                result = await self._analyze_with_provider(
                    provider, code, context, task
                )
                if result:
                    return result
            except Exception as e:
                self.logger.warning(f"Provider {provider.value} failed: {e}")
                continue
        
        # Final fallback: pattern-based (always works)
        return self._analyze_with_patterns(code, context)
    
    async def _analyze_with_provider(
        self,
        provider: AIProvider,
        code: str,
        context: Optional[Dict[str, Any]],
        task: str
    ) -> Optional[Dict[str, Any]]:
        """Analyze with specific provider."""
        if provider == AIProvider.OLLAMA and self.ollama_client:
            result = await self.ollama_client.analyze_security(code, context, task)
            if result:
                result["_provider"] = "ollama"
                result["_local"] = True
                result["_cost"] = 0.0
            return result
        
        elif provider == AIProvider.OPENAI and self.openai_client:
            result = self.openai_client.analyze_security(code, context, task)
            return result
        
        elif provider == AIProvider.CLAUDE and self.claude_client:
            result = self.claude_client.analyze_security(code, context, task)
            return result
        
        elif provider == AIProvider.PHI3_LOCAL and self.phi3_client:
            result = await self.phi3_client.analyze(code, context, task)
            if result:
                result["_provider"] = "phi3_local"
                result["_local"] = True
                result["_cost"] = 0.0
            return result
        
        return None
    
    def _analyze_with_patterns(
        self,
        code: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Fallback pattern-based analysis (no AI required).
        Always works, never fails.
        """
        vulnerabilities = []
        
        # Simple pattern matching
        if "SELECT" in code and ("%" in code or "+" in code or "f\"" in code):
            vulnerabilities.append({
                "type": "SQL_INJECTION",
                "severity": "HIGH",
                "confidence": 0.75,
                "line": None,
                "description": "Potential SQL injection detected"
            })
        
        if "os.system" in code or "subprocess.run" in code and "shell=True" in code:
            vulnerabilities.append({
                "type": "COMMAND_INJECTION",
                "severity": "CRITICAL",
                "confidence": 0.80,
                "line": None,
                "description": "Potential command injection detected"
            })
        
        if "eval(" in code or "exec(" in code:
            vulnerabilities.append({
                "type": "CODE_INJECTION",
                "severity": "CRITICAL",
                "confidence": 0.90,
                "line": None,
                "description": "Dangerous eval/exec usage detected"
            })
        
        return {
            "vulnerabilities": vulnerabilities,
            "risk_level": "high" if vulnerabilities else "low",
            "confidence": 0.70,
            "_provider": "pattern-based",
            "_local": True,
            "_cost": 0.0,
            "_ai": False
        }
    
    def _build_prompt(
        self,
        code: str,
        context: Optional[Dict[str, Any]],
        task: str
    ) -> str:
        """Build prompt for cloud providers."""
        parts = ["Analyze this code for security vulnerabilities:\n"]
        
        if context:
            parts.append(f"Context: {context}\n")
        
        parts.append(f"Code:\n```\n{code}\n```\n")
        parts.append("Return findings in JSON format.")
        
        return "".join(parts)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current router status and available providers."""
        return {
            "active_provider": self.active_provider.value,
            "available_providers": [p.value for p in self.providers],
            "total_providers": len(self.providers),
            "local_available": any(
                p in [AIProvider.OLLAMA, AIProvider.PHI3_LOCAL]
                for p in self.providers
            ),
            "cloud_available": any(
                p in [AIProvider.OPENAI, AIProvider.CLAUDE]
                for p in self.providers
            ),
            "clients": {
                "ollama": self.ollama_client is not None,
                "openai": self.openai_client is not None,
                "claude": self.claude_client is not None,
                "phi3": self.phi3_client is not None
            }
        }
    
    def print_status(self):
        """Print human-readable status."""
        print("\n" + "="*60)
        print("🤖 AI MODEL ROUTER STATUS".center(60))
        print("="*60)
        
        status = self.get_status()
        
        print(f"\n✓ Active Provider: {status['active_provider'].upper()}")
        print(f"  Total Available: {status['total_providers']}/5 providers")
        
        print("\n📊 Provider Status:")
        for i, provider in enumerate(self.providers, 1):
            icon = "🆓" if provider in [AIProvider.OLLAMA, AIProvider.PHI3_LOCAL, AIProvider.PATTERN] else "💰"
            location = "LOCAL" if provider in [AIProvider.OLLAMA, AIProvider.PHI3_LOCAL, AIProvider.PATTERN] else "CLOUD"
            print(f"  {i}. {icon} {provider.value.upper():15} [{location}]")
        
        if not status['local_available']:
            print("\n💡 TIP: Install Ollama for free local AI:")
            print("   curl -fsSL https://ollama.com/install.sh | sh")
            print("   ollama pull llama3.1:8b")
        
        print("="*60 + "\n")


# Singleton instance
_router_instance = None


def get_router() -> AIModelRouter:
    """Get or create singleton router instance."""
    global _router_instance
    if _router_instance is None:
        _router_instance = AIModelRouter()
    return _router_instance
