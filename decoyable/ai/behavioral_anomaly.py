"""
Behavioral Anomaly Detection System

Detects zero-day exploits and unknown vulnerabilities through
behavioral analysis and pattern recognition. Monitors execution
patterns, resource access, and system behavior to catch anomalies.
"""

import asyncio
import logging
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class BehaviorBaseline:
    """Baseline behavior profile for normal operations."""

    function_call_patterns: Dict[str, float]
    resource_access_patterns: Dict[str, float]
    network_patterns: Dict[str, float]
    execution_time_avg: float
    execution_time_std: float
    memory_usage_avg: float
    memory_usage_std: float
    error_rate: float
    timestamp: datetime


@dataclass
class AnomalyDetection:
    """Represents a detected behavioral anomaly."""

    anomaly_type: str
    severity: str
    confidence: float
    description: str
    detected_patterns: List[str]
    deviation_score: float
    baseline_comparison: Dict[str, Any]
    timestamp: datetime
    recommended_actions: List[str]
    potential_zero_day: bool


class BehavioralAnomalyDetector:
    """
    Zero-day detection through behavioral analysis.

    Monitors code execution patterns and detects anomalies that may
    indicate unknown exploits or sophisticated attacks.
    """

    def __init__(self, sensitivity: float = 0.75):
        """
        Initialize behavioral anomaly detector.

        Args:
            sensitivity: Detection sensitivity (0.0 to 1.0). Higher = more sensitive
        """
        self.sensitivity = sensitivity
        self.baselines: Dict[str, BehaviorBaseline] = {}
        self.execution_history = defaultdict(lambda: deque(maxlen=1000))
        self.anomaly_history: List[AnomalyDetection] = []
        self.learning_mode = True
        self.learning_sample_count = defaultdict(int)
        self.min_learning_samples = 100

        logger.info(f"Behavioral Anomaly Detector initialized (sensitivity: {sensitivity})")

    async def record_execution(self, execution_data: Dict[str, Any]) -> None:
        """
        Record execution data for baseline learning.

        Args:
            execution_data: Execution metrics and patterns
        """
        component = execution_data.get("component", "unknown")
        self.execution_history[component].append(
            {
                "timestamp": datetime.now(),
                "function_calls": execution_data.get("function_calls", []),
                "resource_access": execution_data.get("resource_access", []),
                "network_calls": execution_data.get("network_calls", []),
                "execution_time": execution_data.get("execution_time", 0.0),
                "memory_usage": execution_data.get("memory_usage", 0.0),
                "errors": execution_data.get("errors", []),
                "syscalls": execution_data.get("syscalls", []),
            }
        )

        self.learning_sample_count[component] += 1

        # Auto-build baseline after sufficient samples
        if (
            self.learning_mode
            and self.learning_sample_count[component] >= self.min_learning_samples
            and component not in self.baselines
        ):
            await self.build_baseline(component)

    async def build_baseline(self, component: str) -> BehaviorBaseline:
        """
        Build behavioral baseline from historical data.

        Args:
            component: Component identifier

        Returns:
            Baseline behavior profile
        """
        if component not in self.execution_history or len(self.execution_history[component]) < 10:
            raise ValueError(f"Insufficient data to build baseline for {component}")

        history = list(self.execution_history[component])

        # Analyze function call patterns
        function_call_freq = defaultdict(int)
        for record in history:
            for func in record.get("function_calls", []):
                function_call_freq[func] += 1

        total_calls = sum(function_call_freq.values())
        function_patterns = {func: count / total_calls for func, count in function_call_freq.items()}

        # Analyze resource access patterns
        resource_access_freq = defaultdict(int)
        for record in history:
            for resource in record.get("resource_access", []):
                resource_access_freq[resource] += 1

        total_access = sum(resource_access_freq.values()) or 1
        resource_patterns = {resource: count / total_access for resource, count in resource_access_freq.items()}

        # Analyze network patterns
        network_freq = defaultdict(int)
        for record in history:
            for net_call in record.get("network_calls", []):
                network_freq[net_call] += 1

        total_network = sum(network_freq.values()) or 1
        network_patterns = {call: count / total_network for call, count in network_freq.items()}

        # Calculate execution time statistics
        exec_times = [r.get("execution_time", 0.0) for r in history]
        exec_time_avg = np.mean(exec_times)
        exec_time_std = np.std(exec_times)

        # Calculate memory usage statistics
        memory_usage = [r.get("memory_usage", 0.0) for r in history]
        memory_avg = np.mean(memory_usage)
        memory_std = np.std(memory_usage)

        # Calculate error rate
        total_errors = sum(len(r.get("errors", [])) for r in history)
        error_rate = total_errors / len(history)

        baseline = BehaviorBaseline(
            function_call_patterns=function_patterns,
            resource_access_patterns=resource_patterns,
            network_patterns=network_patterns,
            execution_time_avg=exec_time_avg,
            execution_time_std=exec_time_std,
            memory_usage_avg=memory_avg,
            memory_usage_std=memory_std,
            error_rate=error_rate,
            timestamp=datetime.now(),
        )

        self.baselines[component] = baseline
        logger.info(f"Built baseline for {component} from {len(history)} samples")

        return baseline

    async def detect_anomaly(self, execution_data: Dict[str, Any]) -> Optional[AnomalyDetection]:
        """
        Detect behavioral anomalies in execution data.

        Args:
            execution_data: Current execution metrics

        Returns:
            Anomaly detection if found, None otherwise
        """
        component = execution_data.get("component", "unknown")

        # Skip detection if no baseline exists
        if component not in self.baselines:
            await self.record_execution(execution_data)
            return None

        baseline = self.baselines[component]

        # Record execution for future learning
        await self.record_execution(execution_data)

        # Check multiple anomaly indicators
        anomalies_detected = []
        deviation_scores = []

        # 1. Function call pattern anomaly
        func_anomaly = await self._detect_function_call_anomaly(execution_data, baseline)
        if func_anomaly:
            anomalies_detected.append(func_anomaly)
            deviation_scores.append(func_anomaly["deviation"])

        # 2. Resource access anomaly
        resource_anomaly = await self._detect_resource_access_anomaly(execution_data, baseline)
        if resource_anomaly:
            anomalies_detected.append(resource_anomaly)
            deviation_scores.append(resource_anomaly["deviation"])

        # 3. Network behavior anomaly
        network_anomaly = await self._detect_network_anomaly(execution_data, baseline)
        if network_anomaly:
            anomalies_detected.append(network_anomaly)
            deviation_scores.append(network_anomaly["deviation"])

        # 4. Execution time anomaly
        time_anomaly = await self._detect_execution_time_anomaly(execution_data, baseline)
        if time_anomaly:
            anomalies_detected.append(time_anomaly)
            deviation_scores.append(time_anomaly["deviation"])

        # 5. Memory usage anomaly
        memory_anomaly = await self._detect_memory_anomaly(execution_data, baseline)
        if memory_anomaly:
            anomalies_detected.append(memory_anomaly)
            deviation_scores.append(memory_anomaly["deviation"])

        # 6. Error rate spike
        error_anomaly = await self._detect_error_anomaly(execution_data, baseline)
        if error_anomaly:
            anomalies_detected.append(error_anomaly)
            deviation_scores.append(error_anomaly["deviation"])

        # If no anomalies detected
        if not anomalies_detected:
            return None

        # Calculate aggregate deviation score
        avg_deviation = np.mean(deviation_scores)
        max_deviation = max(deviation_scores)

        # Determine severity
        if max_deviation >= 8.0 or len(anomalies_detected) >= 4:
            severity = "CRITICAL"
            potential_zero_day = True
        elif max_deviation >= 5.0 or len(anomalies_detected) >= 3:
            severity = "HIGH"
            potential_zero_day = True
        elif max_deviation >= 3.0 or len(anomalies_detected) >= 2:
            severity = "MEDIUM"
            potential_zero_day = False
        else:
            severity = "LOW"
            potential_zero_day = False

        # Calculate confidence
        confidence = min(0.95, (avg_deviation / 10.0) * (len(anomalies_detected) / 6.0))

        # Generate description
        anomaly_types = [a["type"] for a in anomalies_detected]
        description = f"Detected {len(anomalies_detected)} behavioral anomalies: {', '.join(anomaly_types)}"

        # Compile detected patterns
        detected_patterns = []
        for anomaly in anomalies_detected:
            detected_patterns.extend(anomaly.get("patterns", []))

        # Generate baseline comparison
        baseline_comparison = {
            "expected_behavior": {
                "avg_execution_time": baseline.execution_time_avg,
                "avg_memory_usage": baseline.memory_usage_avg,
                "typical_functions": list(baseline.function_call_patterns.keys())[:10],
            },
            "observed_behavior": {
                "execution_time": execution_data.get("execution_time", 0.0),
                "memory_usage": execution_data.get("memory_usage", 0.0),
                "function_calls": execution_data.get("function_calls", [])[:10],
            },
            "deviations": [{"type": a["type"], "score": a["deviation"], "details": a.get("details", "")} for a in anomalies_detected],
        }

        # Generate recommendations
        recommendations = self._generate_anomaly_recommendations(anomalies_detected, severity, potential_zero_day)

        anomaly_detection = AnomalyDetection(
            anomaly_type=", ".join(anomaly_types),
            severity=severity,
            confidence=confidence,
            description=description,
            detected_patterns=detected_patterns,
            deviation_score=avg_deviation,
            baseline_comparison=baseline_comparison,
            timestamp=datetime.now(),
            recommended_actions=recommendations,
            potential_zero_day=potential_zero_day,
        )

        # Record anomaly
        self.anomaly_history.append(anomaly_detection)

        logger.warning(f"🚨 Anomaly detected: {severity} - {description} (confidence: {confidence:.1%})")

        return anomaly_detection

    async def _detect_function_call_anomaly(
        self, execution_data: Dict[str, Any], baseline: BehaviorBaseline
    ) -> Optional[Dict[str, Any]]:
        """Detect unusual function call patterns."""
        current_calls = execution_data.get("function_calls", [])

        if not current_calls:
            return None

        # Check for unknown functions
        unknown_functions = [func for func in current_calls if func not in baseline.function_call_patterns]

        # Check for unusual call frequencies
        call_freq = defaultdict(int)
        for func in current_calls:
            call_freq[func] += 1

        unusual_frequencies = []
        for func, count in call_freq.items():
            expected_freq = baseline.function_call_patterns.get(func, 0.0)
            actual_freq = count / len(current_calls)

            if expected_freq > 0 and actual_freq > expected_freq * 3:
                unusual_frequencies.append(func)

        if unknown_functions or unusual_frequencies:
            deviation = len(unknown_functions) + len(unusual_frequencies)

            return {
                "type": "unusual_function_calls",
                "deviation": deviation,
                "patterns": unknown_functions + unusual_frequencies,
                "details": f"{len(unknown_functions)} unknown functions, {len(unusual_frequencies)} unusual frequencies",
            }

        return None

    async def _detect_resource_access_anomaly(
        self, execution_data: Dict[str, Any], baseline: BehaviorBaseline
    ) -> Optional[Dict[str, Any]]:
        """Detect unusual resource access patterns."""
        current_access = execution_data.get("resource_access", [])

        if not current_access:
            return None

        # Check for unauthorized or unusual resource access
        unknown_resources = [res for res in current_access if res not in baseline.resource_access_patterns]

        # Check for sensitive resources
        sensitive_patterns = ["etc/passwd", "etc/shadow", "/proc/", "registry", "credential", "private_key"]
        sensitive_access = [res for res in current_access if any(pattern in res.lower() for pattern in sensitive_patterns)]

        if unknown_resources or sensitive_access:
            deviation = len(unknown_resources) * 2 + len(sensitive_access) * 3

            return {
                "type": "unusual_resource_access",
                "deviation": deviation,
                "patterns": unknown_resources + sensitive_access,
                "details": f"{len(unknown_resources)} unknown resources, {len(sensitive_access)} sensitive resources",
            }

        return None

    async def _detect_network_anomaly(
        self, execution_data: Dict[str, Any], baseline: BehaviorBaseline
    ) -> Optional[Dict[str, Any]]:
        """Detect unusual network behavior."""
        current_network = execution_data.get("network_calls", [])

        if not current_network:
            return None

        # Check for unknown network destinations
        unknown_calls = [call for call in current_network if call not in baseline.network_patterns]

        # Check for suspicious patterns
        suspicious_patterns = ["0.0.0.0", "127.0.0.1", "localhost", "169.254", "10.", "192.168", "pastebin", "raw.githubusercontent"]
        suspicious_calls = [call for call in current_network if any(pattern in call.lower() for pattern in suspicious_patterns)]

        if unknown_calls or suspicious_calls:
            deviation = len(unknown_calls) + len(suspicious_calls) * 2

            return {
                "type": "unusual_network_behavior",
                "deviation": deviation,
                "patterns": unknown_calls + suspicious_calls,
                "details": f"{len(unknown_calls)} unknown destinations, {len(suspicious_calls)} suspicious patterns",
            }

        return None

    async def _detect_execution_time_anomaly(
        self, execution_data: Dict[str, Any], baseline: BehaviorBaseline
    ) -> Optional[Dict[str, Any]]:
        """Detect unusual execution time."""
        exec_time = execution_data.get("execution_time", 0.0)

        if exec_time == 0.0:
            return None

        # Calculate z-score (standard deviations from mean)
        if baseline.execution_time_std > 0:
            z_score = abs((exec_time - baseline.execution_time_avg) / baseline.execution_time_std)
        else:
            z_score = 0.0

        # Flag if more than 3 standard deviations
        threshold = 3.0 / self.sensitivity

        if z_score > threshold:
            deviation = z_score

            return {
                "type": "execution_time_anomaly",
                "deviation": deviation,
                "patterns": [f"{exec_time:.2f}s (expected: {baseline.execution_time_avg:.2f}s)"],
                "details": f"Execution time {z_score:.1f} standard deviations from baseline",
            }

        return None

    async def _detect_memory_anomaly(
        self, execution_data: Dict[str, Any], baseline: BehaviorBaseline
    ) -> Optional[Dict[str, Any]]:
        """Detect unusual memory usage."""
        memory_usage = execution_data.get("memory_usage", 0.0)

        if memory_usage == 0.0:
            return None

        # Calculate z-score
        if baseline.memory_usage_std > 0:
            z_score = abs((memory_usage - baseline.memory_usage_avg) / baseline.memory_usage_std)
        else:
            z_score = 0.0

        threshold = 3.0 / self.sensitivity

        if z_score > threshold:
            deviation = z_score

            return {
                "type": "memory_usage_anomaly",
                "deviation": deviation,
                "patterns": [f"{memory_usage:.2f}MB (expected: {baseline.memory_usage_avg:.2f}MB)"],
                "details": f"Memory usage {z_score:.1f} standard deviations from baseline",
            }

        return None

    async def _detect_error_anomaly(
        self, execution_data: Dict[str, Any], baseline: BehaviorBaseline
    ) -> Optional[Dict[str, Any]]:
        """Detect unusual error rates."""
        errors = execution_data.get("errors", [])
        current_error_count = len(errors)

        # Compare to baseline error rate
        if current_error_count > baseline.error_rate * 5:  # 5x normal error rate
            deviation = current_error_count / (baseline.error_rate or 1.0)

            return {
                "type": "error_rate_spike",
                "deviation": deviation,
                "patterns": errors[:5],  # Show first 5 errors
                "details": f"{current_error_count} errors (baseline: {baseline.error_rate:.1f})",
            }

        return None

    def _generate_anomaly_recommendations(
        self, anomalies: List[Dict[str, Any]], severity: str, potential_zero_day: bool
    ) -> List[str]:
        """Generate recommended actions for detected anomalies."""
        recommendations = []

        if potential_zero_day:
            recommendations.append("⚠️ POTENTIAL ZERO-DAY EXPLOIT - Immediate investigation required")
            recommendations.append("Quarantine affected component and collect forensic data")

        if severity in ["CRITICAL", "HIGH"]:
            recommendations.append("Isolate affected systems immediately")
            recommendations.append("Enable enhanced logging and monitoring")

        # Specific recommendations based on anomaly types
        anomaly_types = {a["type"] for a in anomalies}

        if "unusual_function_calls" in anomaly_types:
            recommendations.append("Review and validate all function call sequences")

        if "unusual_resource_access" in anomaly_types:
            recommendations.append("Audit file system and resource access permissions")
            recommendations.append("Check for unauthorized data exfiltration")

        if "unusual_network_behavior" in anomaly_types:
            recommendations.append("Monitor network traffic for command & control patterns")
            recommendations.append("Block suspicious network destinations")

        if "execution_time_anomaly" in anomaly_types or "memory_usage_anomaly" in anomaly_types:
            recommendations.append("Analyze for resource exhaustion attacks")
            recommendations.append("Check for cryptocurrency mining or DoS attempts")

        if "error_rate_spike" in anomaly_types:
            recommendations.append("Review error logs for exploitation attempts")
            recommendations.append("Check for fuzzing or brute-force attacks")

        recommendations.append("Update threat intelligence and behavioral baselines")
        recommendations.append("Conduct security incident response assessment")

        return recommendations

    async def get_anomaly_report(self, timeframe: timedelta = timedelta(hours=24)) -> Dict[str, Any]:
        """
        Generate anomaly detection report.

        Args:
            timeframe: Time window for report

        Returns:
            Anomaly report summary
        """
        cutoff_time = datetime.now() - timeframe
        recent_anomalies = [a for a in self.anomaly_history if a.timestamp >= cutoff_time]

        if not recent_anomalies:
            return {
                "summary": "No anomalies detected in timeframe",
                "timeframe": str(timeframe),
                "total_anomalies": 0,
            }

        # Group by severity
        by_severity = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for anomaly in recent_anomalies:
            by_severity[anomaly.severity] += 1

        # Count potential zero-days
        zero_day_count = sum(1 for a in recent_anomalies if a.potential_zero_day)

        return {
            "summary": f"Detected {len(recent_anomalies)} behavioral anomalies",
            "timeframe": str(timeframe),
            "total_anomalies": len(recent_anomalies),
            "potential_zero_days": zero_day_count,
            "by_severity": by_severity,
            "most_recent": {
                "type": recent_anomalies[-1].anomaly_type,
                "severity": recent_anomalies[-1].severity,
                "timestamp": recent_anomalies[-1].timestamp.isoformat(),
            }
            if recent_anomalies
            else None,
            "learning_status": {
                "baselines_created": len(self.baselines),
                "total_executions_recorded": sum(len(h) for h in self.execution_history.values()),
            },
        }
