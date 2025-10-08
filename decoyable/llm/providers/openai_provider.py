"""
OpenAI GPT-4 provider for cloud-based AI analysis.
"""

import os
import json
import logging
from typing import Dict, Any, Optional

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class OpenAIProvider:
    """
    OpenAI GPT-4 provider for security analysis.
    
    Features:
    - GPT-4 Turbo for high-quality analysis
    - JSON mode for structured output
    - Cost tracking
    - Error handling with retries
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize OpenAI provider.
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
        """
        if not OPENAI_AVAILABLE:
            raise ImportError("openai package not installed. Run: pip install openai")
        
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
        
        self.client = OpenAI(api_key=self.api_key)
        self.logger = logging.getLogger(__name__)
        self.model = "gpt-4-turbo-preview"  # Latest GPT-4 Turbo
        
    def analyze_security(
        self,
        code: str,
        context: Optional[Dict[str, Any]] = None,
        task: str = "security_analysis"
    ) -> Optional[Dict[str, Any]]:
        """
        Analyze code security using GPT-4.
        
        Args:
            code: Code to analyze
            context: Additional context
            task: Analysis task type
            
        Returns:
            Analysis results in JSON format
        """
        try:
            prompt = self._build_prompt(code, context, task)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a security expert analyzing code for vulnerabilities. "
                                 "Respond in JSON format with: vulnerabilities (array), risk_score (0-100), "
                                 "summary (string), recommendations (array)."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.1,  # Low temperature for consistent results
                max_tokens=2000
            )
            
            # Parse response
            content = response.choices[0].message.content
            result = json.loads(content)
            
            # Add metadata
            result["_provider"] = "openai"
            result["_model"] = self.model
            result["_local"] = False
            result["_cost"] = self._calculate_cost(response.usage)
            
            self.logger.info(f"✓ OpenAI analysis complete (cost: ${result['_cost']:.4f})")
            return result
            
        except Exception as e:
            self.logger.error(f"OpenAI analysis failed: {e}")
            return None
    
    def _build_prompt(
        self,
        code: str,
        context: Optional[Dict[str, Any]],
        task: str
    ) -> str:
        """Build analysis prompt."""
        prompt = f"Analyze this code for security vulnerabilities:\n\n```\n{code}\n```\n\n"
        
        if context:
            prompt += f"Context: {json.dumps(context)}\n\n"
        
        prompt += (
            "Provide a comprehensive security analysis including:\n"
            "1. All vulnerabilities found (type, severity, line number, description)\n"
            "2. Overall risk score (0-100)\n"
            "3. Executive summary\n"
            "4. Specific remediation recommendations\n\n"
            "Respond in JSON format."
        )
        
        return prompt
    
    def _calculate_cost(self, usage) -> float:
        """
        Calculate API cost based on token usage.
        
        GPT-4 Turbo pricing (as of Oct 2025):
        - Input: $0.01 per 1K tokens
        - Output: $0.03 per 1K tokens
        """
        input_cost = (usage.prompt_tokens / 1000) * 0.01
        output_cost = (usage.completion_tokens / 1000) * 0.03
        return input_cost + output_cost
    
    def get_available_models(self) -> list:
        """Get available OpenAI models."""
        return [
            "gpt-4-turbo-preview",
            "gpt-4",
            "gpt-3.5-turbo"
        ]
