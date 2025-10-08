"""
Phi-3 local client for lightweight AI inference.
Fallback option when Ollama is not available.

Phi-3 is Microsoft's small language model that runs on laptops.
- 3.8B parameters (small and fast)
- MIT license (fully open-source)
- Good quality for security tasks
- Runs on CPU (no GPU required)
"""

import logging
from typing import Dict, Any, Optional
import json


class Phi3LocalClient:
    """
    Client for running Phi-3 locally using Transformers.
    
    This is a lightweight fallback when Ollama is not available.
    Phi-3 is small enough to run on most laptops.
    
    Installation:
        pip install transformers torch
    
    First run will download ~7GB model (one-time)
    """
    
    def __init__(self, model_name: str = "microsoft/Phi-3-mini-4k-instruct"):
        """
        Initialize Phi-3 client.
        
        Args:
            model_name: HuggingFace model ID
        """
        self.model_name = model_name
        self.logger = logging.getLogger(__name__)
        self.available = False
        self.model = None
        self.tokenizer = None
        
        try:
            self._load_model()
            self.available = True
            self.logger.info(f"✓ Phi-3 loaded: {model_name}")
        except Exception as e:
            self.logger.warning(f"Phi-3 not available: {e}")
            self.logger.info("Install with: pip install transformers torch")
    
    def _load_model(self):
        """Load Phi-3 model and tokenizer."""
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            import torch
            
            self.logger.info("Loading Phi-3 model (first run may take a few minutes)...")
            
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True
            )
            
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto",
                trust_remote_code=True
            )
            
            self.model.eval()  # Set to evaluation mode
            
        except ImportError:
            raise ImportError("transformers and torch not installed")
        except Exception as e:
            raise RuntimeError(f"Failed to load Phi-3: {e}")
    
    async def analyze(
        self,
        code: str,
        context: Optional[Dict[str, Any]] = None,
        task: str = "security_analysis"
    ) -> Optional[Dict[str, Any]]:
        """
        Analyze code using Phi-3.
        
        Args:
            code: Code to analyze
            context: Additional context
            task: Type of analysis
        
        Returns:
            Analysis results or None if unavailable
        """
        if not self.available:
            return None
        
        try:
            prompt = self._build_prompt(code, context, task)
            
            # Tokenize
            inputs = self.tokenizer(prompt, return_tensors="pt")
            
            if self.model.device.type == "cuda":
                inputs = {k: v.cuda() for k, v in inputs.items()}
            
            # Generate response
            import torch
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=512,
                    temperature=0.3,
                    top_p=0.9,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    use_cache=False  # Disable cache to avoid DynamicCache issues
                )
            
            # Decode response
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract JSON from response
            result = self._extract_json(response)
            
            if result:
                result["_provider"] = "phi3_local"
                result["_model"] = "phi-3"
                result["_local"] = True
                result["_cost"] = 0.0
                return result
            else:
                return {
                    "vulnerabilities": [],
                    "risk_score": 50,
                    "summary": "Could not parse Phi-3 response",
                    "recommendations": ["Please review manually"],
                    "_provider": "phi3_local",
                    "_model": "phi-3",
                    "_local": True,
                    "_cost": 0.0,
                    "_parse_error": True,
                    "_raw_response": response[:500]
                }
        
        except Exception as e:
            self.logger.error(f"Phi-3 analysis failed: {e}", exc_info=True)
            self.logger.error(f"Phi-3 analysis failed: {e}")
            return None
    
    def _build_prompt(
        self,
        code: str,
        context: Optional[Dict[str, Any]],
        task: str
    ) -> str:
        """Build prompt for Phi-3."""
        system_prompts = {
            "security_analysis": "You are a security expert analyzing code for vulnerabilities.",
            "threat_prediction": "You are a threat analyst predicting attack vectors.",
            "behavioral_analysis": "You are analyzing code execution patterns for anomalies."
        }
        
        system = system_prompts.get(task, system_prompts["security_analysis"])
        
        parts = [f"<|system|>\n{system}<|end|>\n"]
        parts.append("<|user|>\n")
        
        if context:
            parts.append(f"Context: {json.dumps(context)}\n\n")
        
        parts.append(f"Analyze this code for security issues:\n```\n{code}\n```\n")
        parts.append("Return findings in JSON format.<|end|>\n")
        parts.append("<|assistant|>\n")
        
        return "".join(parts)
    
    def _extract_json(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract JSON from model response."""
        try:
            # Try to find JSON in response
            start = text.find("{")
            end = text.rfind("}") + 1
            
            if start != -1 and end > start:
                json_str = text[start:end]
                return json.loads(json_str)
            
            return None
        except json.JSONDecodeError:
            return None
    
    def get_info(self) -> Dict[str, Any]:
        """Get client information."""
        return {
            "provider": "phi3_local",
            "model": self.model_name,
            "available": self.available,
            "local": True,
            "cost": 0.0,
            "requires_api_key": False,
            "device": str(self.model.device) if self.model else "unknown"
        }
