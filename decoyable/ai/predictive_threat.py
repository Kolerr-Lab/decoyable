"""
Predictive Threat Intelligence System

Uses machine learning to predict attack patterns and vulnerabilities
before they are exploited. Analyzes code patterns, historical data,
and threat intelligence to provide proactive security recommendations.

Now powered by multi-tier AI: Ollama → OpenAI → Claude → Phi-3 → Pattern-based
"""

import asyncio
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from decoyable.llm.model_router import get_router

logger = logging.getLogger(__name__)


@dataclass
class ThreatPrediction:
    """Represents a predicted security threat."""

    threat_type: str
    probability: float
    confidence: float
    risk_score: float
    affected_components: List[str]
    attack_vectors: List[str]
    recommended_defenses: List[str]
    time_to_exploitation: Optional[timedelta]
    severity: str
    evidence: List[str]
    timestamp: datetime


@dataclass
class CodePattern:
    """Represents a code pattern for analysis."""

    pattern_id: str
    pattern_type: str
    code_snippet: str
    file_path: str
    line_number: int
    features: Dict[str, Any]


class PredictiveThreatAnalyzer:
    """
    ML-based predictive threat intelligence system.

    Analyzes code patterns, historical vulnerabilities, and attack trends
    to predict future security threats before they occur.
    """

    def __init__(self, model_path: Optional[Path] = None):
        """
        Initialize the predictive threat analyzer.

        Args:
            model_path: Optional path to pre-trained ML model
        """
        self.model_path = model_path
        self.threat_patterns = self._load_threat_patterns()
        self.historical_data = []
        self.attack_signatures = {}
        self.prediction_cache = {}
        self._initialized = False
        
        # Initialize AI router for intelligent predictions
        self.ai_router = get_router()
        self.ai_enabled = len(self.ai_router.providers) > 1  # More than just pattern-based

        if self.ai_enabled:
            logger.info(f"✓ Predictive Threat Analyzer initialized with AI ({self.ai_router.active_provider.value})")
        else:
            logger.info("Predictive Threat Analyzer initialized (pattern-based mode)")

    def _load_threat_patterns(self) -> Dict[str, Any]:
        """Load known threat patterns and signatures."""
        return {
            "sql_injection": {
                "keywords": ["execute", "cursor", "SELECT", "INSERT", "UPDATE", "DELETE", "WHERE"],
                "risk_factors": ["string concatenation", "user input", "dynamic queries"],
                "base_probability": 0.65,
                "severity_multiplier": 1.8,
            },
            "xss": {
                "keywords": ["innerHTML", "outerHTML", "document.write", "eval", "dangerouslySetInnerHTML"],
                "risk_factors": ["user input", "DOM manipulation", "unsanitized output"],
                "base_probability": 0.55,
                "severity_multiplier": 1.5,
            },
            "command_injection": {
                "keywords": ["os.system", "subprocess", "exec", "eval", "shell=True"],
                "risk_factors": ["user input", "shell commands", "unsanitized parameters"],
                "base_probability": 0.75,
                "severity_multiplier": 2.0,
            },
            "path_traversal": {
                "keywords": ["open", "read", "write", "../", "..\\", "file_path"],
                "risk_factors": ["user input", "file operations", "path construction"],
                "base_probability": 0.45,
                "severity_multiplier": 1.3,
            },
            "deserialization": {
                "keywords": ["pickle.loads", "yaml.load", "json.loads", "deserialize"],
                "risk_factors": ["untrusted data", "remote input", "file uploads"],
                "base_probability": 0.70,
                "severity_multiplier": 1.7,
            },
            "authentication_bypass": {
                "keywords": ["login", "authenticate", "password", "session", "token"],
                "risk_factors": ["weak validation", "hardcoded credentials", "missing checks"],
                "base_probability": 0.60,
                "severity_multiplier": 1.9,
            },
            "sensitive_data_exposure": {
                "keywords": ["api_key", "secret", "password", "token", "credentials"],
                "risk_factors": ["logging", "error messages", "public storage"],
                "base_probability": 0.50,
                "severity_multiplier": 1.6,
            },
        }

    async def analyze_code_patterns(self, code_patterns: List[CodePattern]) -> List[ThreatPrediction]:
        """
        Analyze code patterns and predict potential threats.

        Args:
            code_patterns: List of code patterns to analyze

        Returns:
            List of threat predictions with probabilities
        """
        predictions = []

        for pattern in code_patterns:
            # Extract features from code pattern
            features = await self._extract_features(pattern)

            # Predict threats for each pattern
            for threat_type, threat_config in self.threat_patterns.items():
                prediction = await self._predict_threat(pattern, threat_type, threat_config, features)

                if prediction and prediction.probability > 0.3:  # Threshold for reporting
                    predictions.append(prediction)

        # Sort by risk score
        predictions.sort(key=lambda x: x.risk_score, reverse=True)

        logger.info(f"Generated {len(predictions)} threat predictions")
        return predictions

    async def _extract_features(self, pattern: CodePattern) -> Dict[str, float]:
        """Extract ML features from code pattern."""
        features = {
            "has_user_input": 0.0,
            "has_string_concat": 0.0,
            "has_dynamic_eval": 0.0,
            "has_external_call": 0.0,
            "has_file_operation": 0.0,
            "complexity_score": 0.0,
            "input_validation": 0.0,
            "error_handling": 0.0,
        }

        code = pattern.code_snippet.lower()

        # Detect user input handling
        if any(term in code for term in ["input(", "request.", "argv", "args", "params"]):
            features["has_user_input"] = 1.0

        # Detect string concatenation
        if any(op in code for op in [" + ", " += ", "f\"{", ".format("]):
            features["has_string_concat"] = 1.0

        # Detect dynamic evaluation
        if any(term in code for term in ["eval(", "exec(", "compile("]):
            features["has_dynamic_eval"] = 1.0

        # Detect external calls
        if any(term in code for term in ["requests.", "urllib", "http", "api"]):
            features["has_external_call"] = 1.0

        # Detect file operations
        if any(term in code for term in ["open(", "read(", "write(", "file"]):
            features["has_file_operation"] = 1.0

        # Calculate complexity
        features["complexity_score"] = min(1.0, len(code.split("\n")) / 50.0)

        # Check for input validation
        if any(term in code for term in ["validate", "sanitize", "escape", "filter"]):
            features["input_validation"] = 1.0

        # Check for error handling
        if any(term in code for term in ["try:", "except", "catch", "error"]):
            features["error_handling"] = 1.0

        return features

    async def _predict_threat(
        self,
        pattern: CodePattern,
        threat_type: str,
        threat_config: Dict[str, Any],
        features: Dict[str, float],
    ) -> Optional[ThreatPrediction]:
        """
        Predict specific threat for a code pattern.
        Uses AI if available, otherwise falls back to heuristics.
        """
        code = pattern.code_snippet.lower()

        # Check if pattern contains threat-related keywords
        keyword_matches = sum(1 for keyword in threat_config["keywords"] if keyword.lower() in code)

        if keyword_matches == 0:
            return None

        # If AI is available, use it for enhanced predictions
        if self.ai_enabled:
            try:
                ai_result = await self.ai_router.analyze(
                    code=pattern.code_snippet,
                    context={
                        "file_path": pattern.file_path,
                        "threat_type": threat_type,
                        "features": features
                    },
                    task="threat_prediction",
                    prefer_local=True  # Prefer free local models
                )
                
                if ai_result and "predictions" in ai_result:
                    # Use AI-enhanced prediction
                    return self._parse_ai_prediction(
                        ai_result, pattern, threat_type, threat_config
                    )
            except Exception as e:
                logger.warning(f"AI prediction failed, falling back to heuristics: {e}")

        # Fallback to heuristic-based prediction
        return await self._predict_threat_heuristic(
            pattern, threat_type, threat_config, features, code, keyword_matches
        )
    
    def _parse_ai_prediction(
        self,
        ai_result: Dict[str, Any],
        pattern: CodePattern,
        threat_type: str,
        threat_config: Dict[str, Any]
    ) -> Optional[ThreatPrediction]:
        """Parse AI prediction results into ThreatPrediction object."""
        predictions = ai_result.get("predictions", [])
        
        # Find prediction matching our threat type
        for pred in predictions:
            if pred.get("threat_type", "").lower() == threat_type.lower():
                probability = pred.get("probability", 0.5)
                confidence = ai_result.get("confidence", 85) / 100.0
                
                return ThreatPrediction(
                    threat_type=threat_type,
                    probability=probability,
                    confidence=confidence,
                    risk_score=probability * threat_config["severity_multiplier"] * 100,
                    affected_components=[pattern.file_path],
                    attack_vectors=pred.get("attack_vectors", []),
                    recommended_defenses=pred.get("defenses", []),
                    time_to_exploitation=timedelta(days=pred.get("tte_days", 7)),
                    severity=pred.get("severity", "MEDIUM"),
                    evidence=[pattern.code_snippet],
                    timestamp=datetime.now()
                )
        
        return None
    
    async def _predict_threat_heuristic(
        self,
        pattern: CodePattern,
        threat_type: str,
        threat_config: Dict[str, Any],
        features: Dict[str, float],
        code: str,
        keyword_matches: int
    ) -> Optional[ThreatPrediction]:
        """Heuristic-based threat prediction (fallback)."""
        # Calculate base probability
        base_prob = threat_config["base_probability"]
        keyword_score = min(1.0, keyword_matches / len(threat_config["keywords"]))

        # Adjust probability based on risk factors
        risk_factor_score = 0.0
        matched_risk_factors = []

        for risk_factor in threat_config["risk_factors"]:
            if risk_factor.lower() in code:
                risk_factor_score += 0.2
                matched_risk_factors.append(risk_factor)

        # Calculate feature-based score
        feature_score = (
            features["has_user_input"] * 0.3
            + features["has_string_concat"] * 0.2
            + features["has_dynamic_eval"] * 0.3
            - features["input_validation"] * 0.3
            - features["error_handling"] * 0.1
        )

        # Combine scores
        probability = min(0.95, base_prob * keyword_score + risk_factor_score + feature_score * 0.2)

        # Calculate confidence (based on evidence strength)
        confidence = min(0.95, (keyword_score + min(1.0, len(matched_risk_factors) * 0.3)) / 1.5)

        # Calculate risk score
        severity_multiplier = threat_config["severity_multiplier"]
        risk_score = probability * confidence * severity_multiplier * 100

        # Determine severity
        if risk_score >= 80:
            severity = "CRITICAL"
        elif risk_score >= 60:
            severity = "HIGH"
        elif risk_score >= 40:
            severity = "MEDIUM"
        else:
            severity = "LOW"

        # Generate recommendations
        recommendations = self._generate_recommendations(threat_type, matched_risk_factors)

        # Estimate time to exploitation
        time_to_exploit = self._estimate_exploitation_time(probability, confidence)

        # Build evidence list
        evidence = [
            f"Found {keyword_matches} threat-related keywords",
            f"Matched {len(matched_risk_factors)} risk factors: {', '.join(matched_risk_factors)}",
        ]

        if features["has_user_input"] > 0:
            evidence.append("Code handles user input without visible validation")
        if features["input_validation"] == 0:
            evidence.append("No input validation detected")
        if features["error_handling"] == 0:
            evidence.append("Lacks error handling")

        return ThreatPrediction(
            threat_type=threat_type,
            probability=probability,
            confidence=confidence,
            risk_score=risk_score,
            affected_components=[pattern.file_path],
            attack_vectors=self._identify_attack_vectors(threat_type),
            recommended_defenses=recommendations,
            time_to_exploitation=time_to_exploit,
            severity=severity,
            evidence=evidence,
            timestamp=datetime.now(),
        )

    def _generate_recommendations(self, threat_type: str, risk_factors: List[str]) -> List[str]:
        """Generate defense recommendations for threat type."""
        recommendations = {
            "sql_injection": [
                "Use parameterized queries or prepared statements",
                "Implement input validation and sanitization",
                "Use ORM frameworks with built-in protections",
                "Apply principle of least privilege for database access",
            ],
            "xss": [
                "Implement Content Security Policy (CSP)",
                "Use output encoding/escaping for user data",
                "Sanitize HTML input with allowlisting",
                "Use secure frameworks with auto-escaping",
            ],
            "command_injection": [
                "Avoid shell=True in subprocess calls",
                "Use parameterized command execution",
                "Validate and whitelist all inputs",
                "Use safe APIs instead of shell commands",
            ],
            "path_traversal": [
                "Validate and sanitize file paths",
                "Use absolute paths with whitelist",
                "Implement chroot or sandboxing",
                "Restrict file system access",
            ],
            "deserialization": [
                "Avoid deserializing untrusted data",
                "Use safe serialization formats (JSON)",
                "Implement signature verification",
                "Validate deserialized object types",
            ],
            "authentication_bypass": [
                "Implement multi-factor authentication",
                "Use secure session management",
                "Apply rate limiting and account lockout",
                "Conduct regular security audits",
            ],
            "sensitive_data_exposure": [
                "Encrypt sensitive data at rest and in transit",
                "Implement proper access controls",
                "Remove sensitive data from logs and errors",
                "Use environment variables for secrets",
            ],
        }

        return recommendations.get(threat_type, ["Implement security best practices", "Conduct code review"])

    def _identify_attack_vectors(self, threat_type: str) -> List[str]:
        """Identify potential attack vectors for threat type."""
        vectors = {
            "sql_injection": ["Direct SQL injection", "Second-order injection", "Blind SQL injection"],
            "xss": ["Reflected XSS", "Stored XSS", "DOM-based XSS"],
            "command_injection": ["Direct command injection", "Argument injection", "Environment manipulation"],
            "path_traversal": ["Directory traversal", "File inclusion", "Arbitrary file access"],
            "deserialization": ["Remote code execution", "Object injection", "Type confusion"],
            "authentication_bypass": ["Credential stuffing", "Session hijacking", "Token manipulation"],
            "sensitive_data_exposure": ["Information disclosure", "Data leakage", "Credential exposure"],
        }

        return vectors.get(threat_type, ["Unknown attack vector"])

    def _estimate_exploitation_time(self, probability: float, confidence: float) -> timedelta:
        """Estimate time until likely exploitation."""
        # High probability + high confidence = imminent threat
        urgency_score = probability * confidence

        if urgency_score >= 0.8:
            return timedelta(hours=24)  # Critical: within 24 hours
        elif urgency_score >= 0.6:
            return timedelta(days=7)  # High: within a week
        elif urgency_score >= 0.4:
            return timedelta(days=30)  # Medium: within a month
        else:
            return timedelta(days=90)  # Low: within 3 months

    async def predict_attack_probability(self, file_path: str, vulnerabilities: List[Dict]) -> Dict[str, Any]:
        """
        Predict overall attack probability for a file.

        Args:
            file_path: Path to analyze
            vulnerabilities: Known vulnerabilities in the file

        Returns:
            Attack probability analysis
        """
        # Convert vulnerabilities to code patterns
        patterns = []
        for vuln in vulnerabilities:
            pattern = CodePattern(
                pattern_id=f"{vuln.get('vulnerability_type', 'unknown')}_{vuln.get('line_number', 0)}",
                pattern_type=vuln.get("vulnerability_type", "unknown"),
                code_snippet=vuln.get("code_snippet", ""),
                file_path=file_path,
                line_number=vuln.get("line_number", 0),
                features={},
            )
            patterns.append(pattern)

        # Get predictions
        predictions = await self.analyze_code_patterns(patterns)

        # Aggregate results
        if not predictions:
            return {
                "file_path": file_path,
                "overall_risk": "LOW",
                "attack_probability": 0.0,
                "predictions": [],
            }

        # Calculate aggregate metrics
        max_probability = max(p.probability for p in predictions)
        avg_confidence = np.mean([p.confidence for p in predictions])
        total_risk_score = sum(p.risk_score for p in predictions)

        # Determine overall risk
        if total_risk_score >= 200:
            overall_risk = "CRITICAL"
        elif total_risk_score >= 120:
            overall_risk = "HIGH"
        elif total_risk_score >= 60:
            overall_risk = "MEDIUM"
        else:
            overall_risk = "LOW"

        return {
            "file_path": file_path,
            "overall_risk": overall_risk,
            "attack_probability": max_probability,
            "average_confidence": avg_confidence,
            "total_risk_score": total_risk_score,
            "threat_count": len(predictions),
            "predictions": [
                {
                    "threat_type": p.threat_type,
                    "probability": p.probability,
                    "confidence": p.confidence,
                    "risk_score": p.risk_score,
                    "severity": p.severity,
                    "attack_vectors": p.attack_vectors,
                    "recommendations": p.recommended_defenses,
                    "time_to_exploitation": str(p.time_to_exploitation),
                    "evidence": p.evidence,
                }
                for p in predictions
            ],
        }

    async def learn_from_attack(self, attack_data: Dict[str, Any]) -> None:
        """
        Learn from real attack data to improve predictions.

        Args:
            attack_data: Data from actual attack incident
        """
        self.historical_data.append(
            {
                "timestamp": datetime.now(),
                "attack_type": attack_data.get("attack_type"),
                "success": attack_data.get("success", False),
                "features": attack_data.get("features", {}),
            }
        )

        # Update attack signatures
        attack_type = attack_data.get("attack_type")
        if attack_type:
            if attack_type not in self.attack_signatures:
                self.attack_signatures[attack_type] = []

            self.attack_signatures[attack_type].append(attack_data)

            # Update threat patterns based on new data
            if len(self.attack_signatures[attack_type]) >= 10:
                await self._update_threat_patterns(attack_type)

        logger.info(f"Learned from {attack_type} attack. Total historical attacks: {len(self.historical_data)}")

    async def _update_threat_patterns(self, attack_type: str) -> None:
        """Update threat patterns based on historical attack data."""
        if attack_type not in self.threat_patterns:
            return

        signatures = self.attack_signatures[attack_type]
        success_rate = sum(1 for s in signatures if s.get("success", False)) / len(signatures)

        # Adjust base probability based on success rate
        if success_rate > 0.7:
            self.threat_patterns[attack_type]["base_probability"] = min(
                0.95, self.threat_patterns[attack_type]["base_probability"] * 1.2
            )

        logger.info(f"Updated threat pattern for {attack_type}. Success rate: {success_rate:.2%}")

    async def generate_threat_report(self, predictions: List[ThreatPrediction]) -> Dict[str, Any]:
        """
        Generate comprehensive threat intelligence report.

        Args:
            predictions: List of threat predictions

        Returns:
            Formatted threat report
        """
        if not predictions:
            return {
                "summary": "No significant threats predicted",
                "risk_level": "LOW",
                "total_threats": 0,
                "recommendations": [],
            }

        # Group by severity
        by_severity = {"CRITICAL": [], "HIGH": [], "MEDIUM": [], "LOW": []}
        for pred in predictions:
            by_severity[pred.severity].append(pred)

        # Find most urgent threat
        most_urgent = min(predictions, key=lambda p: p.time_to_exploitation)

        # Compile unique recommendations
        all_recommendations = set()
        for pred in predictions:
            all_recommendations.update(pred.recommended_defenses)

        return {
            "summary": f"Identified {len(predictions)} potential security threats",
            "risk_level": predictions[0].severity if predictions else "LOW",
            "total_threats": len(predictions),
            "by_severity": {
                "critical": len(by_severity["CRITICAL"]),
                "high": len(by_severity["HIGH"]),
                "medium": len(by_severity["MEDIUM"]),
                "low": len(by_severity["LOW"]),
            },
            "most_urgent_threat": {
                "type": most_urgent.threat_type,
                "probability": most_urgent.probability,
                "time_to_exploitation": str(most_urgent.time_to_exploitation),
            },
            "recommendations": list(all_recommendations)[:10],
            "detailed_predictions": [
                {
                    "threat_type": p.threat_type,
                    "severity": p.severity,
                    "probability": f"{p.probability:.1%}",
                    "confidence": f"{p.confidence:.1%}",
                    "risk_score": f"{p.risk_score:.1f}",
                }
                for p in predictions[:10]
            ],
        }
