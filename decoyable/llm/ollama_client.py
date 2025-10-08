"""
Ollama client for local AI inference with Llama 3.1.
100% free, runs on user's machine, no API costs!
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
import httpx


class OllamaClient:
    """
    Client for Ollama-hosted local LLMs (Llama 3.1, CodeLlama, etc.)
    
    Ollama provides free local AI inference without any API costs.
    Users just need to install Ollama and download models.
    
    Installation:
        curl -fsSL https://ollama.com/install.sh | sh
        ollama pull llama3.1:8b
    
    Features:
    - 100% free (no API costs)
    - Runs locally (privacy-friendly)
    - Fast inference (GPU acceleration)
    - No internet required after model download
    """
    
    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = None,
        timeout: float = 60.0
    ):
        """
        Initialize Ollama client.
        
        Args:
            base_url: Ollama API endpoint (default: localhost:11434)
            model: Model to use (auto-detects best available model if None)
            timeout: Request timeout in seconds
        """
        self.base_url = base_url
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)
        
        # Auto-detect best available model if not specified
        if model is None:
            self.model = self._detect_best_model()
        else:
            self.model = model
        
        # Check if Ollama is available
        self.available = self._check_availability()
        
        if not self.available:
            self.logger.info("Ollama not available. Install: curl -fsSL https://ollama.com/install.sh | sh")
        else:
            self.logger.info(f"✓ Ollama available with model: {self.model}")
    
    def _detect_best_model(self) -> str:
        """
        Auto-detect the best available Ollama model.
        
        Priority order:
        1. gemma3:12b (best quality Gemma model)
        2. llama3.1:70b (best Llama model)
        3. llama3.1:8b (good Llama model)
        4. gemma3:4b (lightweight Gemma)
        5. codellama:7b (code-focused)
        """
        try:
            response = httpx.get(f"{self.base_url}/api/tags", timeout=2.0)
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m.get("name", "") for m in models]
                
                # Check in priority order
                priority = [
                    "gemma3:12b",
                    "llama3.1:70b",
                    "llama3.1:8b",
                    "gemma3:4b",
                    "codellama:7b",
                    "llama3:8b",
                    "gemma:7b"
                ]
                
                for preferred in priority:
                    if any(preferred in name for name in model_names):
                        self.logger.info(f"✓ Auto-detected best model: {preferred}")
                        return preferred
                
                # If none of the preferred models, use first available
                if model_names:
                    self.logger.info(f"✓ Using first available model: {model_names[0]}")
                    return model_names[0]
        except Exception as e:
            self.logger.debug(f"Could not detect Ollama models: {e}")
        
        # Default fallback
        return "llama3.1:8b"
    
    def _check_availability(self) -> bool:
        """Check if Ollama is running and model is available."""
        try:
            response = httpx.get(f"{self.base_url}/api/tags", timeout=2.0)
            if response.status_code == 200:
                models = response.json().get("models", [])
                # Check if our preferred model is available
                model_names = [m.get("name", "") for m in models]
                return any(self.model in name for name in model_names)
            return False
        except Exception:
            return False
    
    async def analyze_security(
        self,
        code: str,
        context: Optional[Dict[str, Any]] = None,
        task: str = "security_analysis"
    ) -> Optional[Dict[str, Any]]:
        """
        Analyze code for security vulnerabilities using local AI.
        
        Args:
            code: Code snippet to analyze
            context: Additional context (file path, framework, etc.)
            task: Type of analysis (security_analysis, threat_prediction, etc.)
        
        Returns:
            Analysis results or None if Ollama unavailable
        """
        if not self.available:
            return None
        
        try:
            # Build prompt based on task
            system_prompt = self._get_system_prompt(task)
            user_prompt = self._build_user_prompt(code, context, task)
            
            # Call Ollama API
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": f"{system_prompt}\n\n{user_prompt}",
                        "stream": False,
                        "format": "json",
                        "options": {
                            "temperature": 0.3,  # Lower for more consistent results
                            "top_p": 0.9,
                        }
                    },
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    response_text = result.get("response", "{}")
                    
                    # Parse JSON response
                    try:
                        # Clean up response text (remove markdown code blocks if present)
                        cleaned_text = response_text.strip()
                        if cleaned_text.startswith("```json"):
                            cleaned_text = cleaned_text.split("```json")[1]
                            cleaned_text = cleaned_text.split("```")[0].strip()
                        elif cleaned_text.startswith("```"):
                            cleaned_text = cleaned_text.split("```")[1]
                            cleaned_text = cleaned_text.split("```")[0].strip()
                        
                        parsed = json.loads(cleaned_text)
                        
                        # Add metadata
                        parsed["_provider"] = "ollama"
                        parsed["_model"] = self.model
                        parsed["_local"] = True
                        parsed["_cost"] = 0.0
                        
                        return parsed
                        
                    except json.JSONDecodeError as je:
                        self.logger.warning(f"Failed to parse Ollama JSON response: {je}")
                        self.logger.debug(f"Response text: {response_text[:200]}...")
                        
                        # Return structured fallback
                        return {
                            "vulnerabilities": [],
                            "risk_score": 50,
                            "summary": "Could not parse AI response",
                            "recommendations": ["Please review manually"],
                            "_provider": "ollama",
                            "_model": self.model,
                            "_local": True,
                            "_cost": 0.0,
                            "_parse_error": True,
                            "_raw_response": response_text[:500]
                        }
                else:
                    self.logger.error(f"Ollama API error: {response.status_code}")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Ollama analysis failed: {e}", exc_info=True)
            return None
    
    def _get_system_prompt(self, task: str) -> str:
        """Get system prompt for specific task."""
        prompts = {
            "security_analysis": """You are a cybersecurity expert specializing in code security analysis.
Analyze the provided code for security vulnerabilities including:
- SQL injection
- Command injection
- XSS (Cross-Site Scripting)
- Path traversal
- Insecure deserialization
- Authentication/authorization issues
- Hardcoded secrets

Return results in JSON format with: vulnerabilities (array), risk_level (low/medium/high/critical), recommendations (array).""",

            "threat_prediction": """You are a threat intelligence analyst predicting potential attack vectors.
Analyze the code and predict:
- Most likely attack vectors
- Probability of exploitation (0-100)
- Time to exploitation estimate
- Attacker skill level required

Return results in JSON format with: predictions (array), overall_risk_score (0-1000), confidence (0-100).""",

            "adaptive_honeypot": """You are a deception expert designing adaptive honeypots.
Based on the attacker behavior and code analysis, recommend:
- Honeypot complexity level (basic/intermediate/advanced/elite)
- Fake endpoints to deploy
- Realistic decoy data
- Deceptive responses

Return results in JSON format with: honeypot_config, decoy_endpoints (array), deception_tactics (array).""",

            "behavioral_analysis": """You are analyzing code execution patterns for anomalies.
Identify unusual patterns including:
- Unexpected function calls
- Abnormal resource access
- Suspicious network activity
- Timing anomalies

Return results in JSON format with: anomalies (array), severity (low/medium/high), confidence (0-100)."""
        }
        
        return prompts.get(task, prompts["security_analysis"])
    
    def _build_user_prompt(
        self,
        code: str,
        context: Optional[Dict[str, Any]],
        task: str
    ) -> str:
        """Build user prompt with code and context."""
        prompt_parts = []
        
        if context:
            prompt_parts.append("Context:")
            if "file_path" in context:
                prompt_parts.append(f"File: {context['file_path']}")
            if "framework" in context:
                prompt_parts.append(f"Framework: {context['framework']}")
            if "language" in context:
                prompt_parts.append(f"Language: {context['language']}")
            prompt_parts.append("")
        
        prompt_parts.append("Code to analyze:")
        prompt_parts.append("```")
        prompt_parts.append(code)
        prompt_parts.append("```")
        prompt_parts.append("")
        prompt_parts.append("Analyze this code and return your findings in JSON format.")
        
        return "\n".join(prompt_parts)
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        format_json: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Chat with Ollama using conversation history.
        
        Args:
            messages: List of {"role": "user/assistant/system", "content": "..."}
            format_json: Whether to request JSON format output
        
        Returns:
            Response dict or None if unavailable
        """
        if not self.available:
            return None
        
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "model": self.model,
                    "messages": messages,
                    "stream": False
                }
                
                if format_json:
                    payload["format"] = "json"
                
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json=payload,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result.get("message", {}).get("content", "")
                    
                    if format_json:
                        try:
                            return json.loads(content)
                        except json.JSONDecodeError:
                            return {"raw_response": content}
                    else:
                        return {"response": content}
                else:
                    return None
                    
        except Exception as e:
            self.logger.error(f"Ollama chat failed: {e}")
            return None
    
    def get_available_models(self) -> List[str]:
        """Get list of available models in Ollama."""
        try:
            response = httpx.get(f"{self.base_url}/api/tags", timeout=2.0)
            if response.status_code == 200:
                models = response.json().get("models", [])
                return [m.get("name", "") for m in models]
            return []
        except Exception:
            return []
    
    def get_info(self) -> Dict[str, Any]:
        """Get client information and status."""
        return {
            "provider": "ollama",
            "base_url": self.base_url,
            "model": self.model,
            "available": self.available,
            "local": True,
            "cost": 0.0,
            "requires_api_key": False,
            "available_models": self.get_available_models() if self.available else []
        }


# Example usage
async def example_usage():
    """Example of using OllamaClient."""
    client = OllamaClient()
    
    if client.available:
        code = '''
        def get_user(user_id):
            query = "SELECT * FROM users WHERE id = %s" % user_id
            return db.execute(query)
        '''
        
        result = await client.analyze_security(
            code=code,
            context={"file_path": "app.py", "framework": "flask"}
        )
        
        if result:
            print("Security Analysis Results:")
            print(json.dumps(result, indent=2))
    else:
        print("Ollama not available. Install with:")
        print("  curl -fsSL https://ollama.com/install.sh | sh")
        print("  ollama pull llama3.1:8b")
