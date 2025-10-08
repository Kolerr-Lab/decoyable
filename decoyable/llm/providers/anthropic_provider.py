"""
Anthropic Claude provider for cloud-based AI analysis.
"""

import os
import json
import logging
from typing import Dict, Any, Optional

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


class AnthropicProvider:
    """
    Anthropic Claude provider for security analysis.
    
    Features:
    - Claude 3 Opus for high-quality analysis
    - Large context window (200K tokens)
    - Cost tracking
    - Error handling with retries
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Anthropic provider.
        
        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
        """
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("anthropic package not installed. Run: pip install anthropic")
        
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key not found. Set ANTHROPIC_API_KEY environment variable.")
        
        self.client = Anthropic(api_key=self.api_key)
        self.logger = logging.getLogger(__name__)
        self.model = "claude-3-opus-20240229"  # Latest Claude 3 Opus
        
    def analyze_security(
        self,
        code: str,
        context: Optional[Dict[str, Any]] = None,
        task: str = "security_analysis"
    ) -> Optional[Dict[str, Any]]:
        """
        Analyze code security using Claude.
        
        Args:
            code: Code to analyze
            context: Additional context
            task: Analysis task type
            
        Returns:
            Analysis results in JSON format
        """
        try:
            prompt = self._build_prompt(code, context, task)
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.1,  # Low temperature for consistent results
                system="You are a security expert analyzing code for vulnerabilities. "
                       "Respond in JSON format with: vulnerabilities (array), risk_score (0-100), "
                       "summary (string), recommendations (array).",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # Parse response
            content = response.content[0].text
            
            # Extract JSON from response (Claude may wrap it in markdown)
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            result = json.loads(content)
            
            # Add metadata
            result["_provider"] = "claude"
            result["_model"] = self.model
            result["_local"] = False
            result["_cost"] = self._calculate_cost(response.usage)
            
            self.logger.info(f"✓ Claude analysis complete (cost: ${result['_cost']:.4f})")
            return result
            
        except Exception as e:
            self.logger.error(f"Claude analysis failed: {e}")
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
            "Respond in JSON format only, no additional text."
        )
        
        return prompt
    
    def _calculate_cost(self, usage) -> float:
        """
        Calculate API cost based on token usage.
        
        Claude 3 Opus pricing (as of Oct 2025):
        - Input: $0.015 per 1K tokens
        - Output: $0.075 per 1K tokens
        """
        input_cost = (usage.input_tokens / 1000) * 0.015
        output_cost = (usage.output_tokens / 1000) * 0.075
        return input_cost + output_cost
    
    def get_available_models(self) -> list:
        """Get available Claude models."""
        return [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307"
        ]
