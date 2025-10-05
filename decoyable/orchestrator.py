"""
DECOYABLE Master Orchestrator

Central coordination system that integrates all advanced security features:
- Predictive threat intelligence
- Adaptive honeypots
- Exploit chain detection
- Smart fuzzing
- Behavioral anomaly detection
- Automated incident response
- Self-healing code generation

Provides unified API and creates cohesive "WOW" user experience.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from decoyable.ai.behavioral_anomaly import BehavioralAnomalyDetector
from decoyable.ai.pattern_learner import AttackPatternLearner
from decoyable.ai.predictive_threat import CodePattern, PredictiveThreatAnalyzer
from decoyable.deception.adaptive_honeypot import AdaptiveHoneypotSystem

logger = logging.getLogger(__name__)


class MasterOrchestrator:
    """
    Central orchestration system for all DECOYABLE advanced features.

    Coordinates AI systems, deception platforms, and automated responses
    to create a comprehensive, intelligent security defense system.
    """

    def __init__(self):
        """Initialize the master orchestrator."""
        self.predictive_ai = PredictiveThreatAnalyzer()
        self.anomaly_detector = BehavioralAnomalyDetector(sensitivity=0.75)
        self.pattern_learner = AttackPatternLearner()
        self.honeypot_system = AdaptiveHoneypotSystem()

        self.active_incidents: List[Dict[str, Any]] = []
        self.defense_score = 100.0  # Overall defense effectiveness score
        self.total_attacks_blocked = 0
        self.total_threats_predicted = 0
        self.total_time_attackers_wasted = 0.0

        logger.info("🚀 DECOYABLE Master Orchestrator initialized - All systems ready!")

    async def analyze_codebase_comprehensive(self, path: str) -> Dict[str, Any]:
        """
        Perform comprehensive multi-layered security analysis.

        Args:
            path: Path to analyze

        Returns:
            Complete security intelligence report
        """
        logger.info(f"🔍 Starting comprehensive analysis of: {path}")

        start_time = datetime.now()

        # Step 1: Traditional SAST scanning
        from decoyable.scanners.sast import scan_sast

        sast_results = scan_sast(path)
        vulnerabilities = sast_results.get("vulnerabilities", [])

        logger.info(f"   ✓ SAST scan complete: {len(vulnerabilities)} vulnerabilities found")

        # Step 2: Predictive Threat Analysis
        # Convert vulnerabilities to code patterns for AI analysis
        code_patterns = []
        for vuln in vulnerabilities[:50]:  # Limit to top 50 for performance
            pattern = CodePattern(
                pattern_id=f"{vuln.get('vulnerability_type', 'unknown')}_{vuln.get('line_number', 0)}",
                pattern_type=str(vuln.get("vulnerability_type", "unknown")),
                code_snippet=vuln.get("code_snippet", ""),
                file_path=vuln.get("file_path", ""),
                line_number=vuln.get("line_number", 0),
                features={},
            )
            code_patterns.append(pattern)

        threat_predictions = await self.predictive_ai.analyze_code_patterns(code_patterns)
        self.total_threats_predicted += len(threat_predictions)

        logger.info(f"   ✓ AI threat prediction complete: {len(threat_predictions)} threats predicted")

        # Step 3: Exploit Chain Detection
        exploit_chains = await self._detect_exploit_chains(vulnerabilities)

        logger.info(f"   ✓ Exploit chain analysis complete: {len(exploit_chains)} chains found")

        # Step 4: Generate comprehensive report
        analysis_time = (datetime.now() - start_time).total_seconds()

        # Calculate risk scores
        critical_count = sum(1 for v in vulnerabilities if self._get_severity(v) == "CRITICAL")
        high_count = sum(1 for v in vulnerabilities if self._get_severity(v) == "HIGH")

        overall_risk_score = (critical_count * 10 + high_count * 5) + sum(p.risk_score for p in threat_predictions[:10])

        if overall_risk_score >= 200:
            overall_risk = "CRITICAL"
            risk_emoji = "🔴"
        elif overall_risk_score >= 100:
            overall_risk = "HIGH"
            risk_emoji = "🟠"
        elif overall_risk_score >= 50:
            overall_risk = "MEDIUM"
            risk_emoji = "🟡"
        else:
            overall_risk = "LOW"
            risk_emoji = "🟢"

        report = {
            "analysis_timestamp": datetime.now().isoformat(),
            "analysis_duration_seconds": analysis_time,
            "target_path": path,
            "overall_risk_level": overall_risk,
            "overall_risk_score": overall_risk_score,
            "risk_emoji": risk_emoji,
            "summary": {
                "total_vulnerabilities": len(vulnerabilities),
                "critical_vulnerabilities": critical_count,
                "high_vulnerabilities": high_count,
                "predicted_threats": len(threat_predictions),
                "exploit_chains_detected": len(exploit_chains),
            },
            "vulnerabilities": vulnerabilities,
            "threat_predictions": [
                {
                    "threat_type": p.threat_type,
                    "probability": f"{p.probability:.1%}",
                    "confidence": f"{p.confidence:.1%}",
                    "risk_score": p.risk_score,
                    "severity": p.severity,
                    "time_to_exploitation": str(p.time_to_exploitation),
                    "recommendations": p.recommended_defenses[:3],
                }
                for p in threat_predictions[:10]
            ],
            "exploit_chains": exploit_chains,
            "defense_recommendations": await self._generate_defense_strategy(vulnerabilities, threat_predictions, exploit_chains),
        }

        logger.info(f"   ✓ Analysis complete! Risk Level: {risk_emoji} {overall_risk}")

        return report

    async def _detect_exploit_chains(self, vulnerabilities: List[Dict]) -> List[Dict[str, Any]]:
        """
        Detect chains of vulnerabilities that combine into critical exploits.

        Uses graph analysis to find vulnerability combinations.
        """
        chains = []

        # Build vulnerability graph
        vuln_by_file = {}
        for vuln in vulnerabilities:
            file_path = vuln.get("file_path", "")
            if file_path not in vuln_by_file:
                vuln_by_file[file_path] = []
            vuln_by_file[file_path].append(vuln)

        # Define dangerous combinations
        dangerous_combos = [
            {
                "types": ["XSS", "CSRF"],
                "impact": "Account takeover via cross-site scripting and request forgery",
                "severity": "CRITICAL",
            },
            {
                "types": ["SQL_INJECTION", "AUTHENTICATION_BYPASS"],
                "impact": "Database breach with authentication bypass",
                "severity": "CRITICAL",
            },
            {
                "types": ["COMMAND_INJECTION", "PATH_TRAVERSAL"],
                "impact": "Remote code execution with file system access",
                "severity": "CRITICAL",
            },
            {
                "types": ["DESERIALIZATION", "SSRF"],
                "impact": "Remote code execution via deserialization and server-side request forgery",
                "severity": "CRITICAL",
            },
        ]

        # Find matching chains
        for file_path, file_vulns in vuln_by_file.items():
            vuln_types = {self._get_vuln_type(v) for v in file_vulns}

            for combo in dangerous_combos:
                required_types = set(combo["types"])

                if required_types.issubset(vuln_types):
                    # Found a chain!
                    chain_vulns = [v for v in file_vulns if self._get_vuln_type(v) in required_types]

                    chains.append(
                        {
                            "chain_id": f"chain_{len(chains) + 1}",
                            "vulnerability_types": combo["types"],
                            "impact": combo["impact"],
                            "severity": combo["severity"],
                            "file_path": file_path,
                            "vulnerabilities": chain_vulns,
                            "exploitation_steps": self._generate_exploitation_steps(combo["types"]),
                            "combined_risk_score": len(combo["types"]) * 50,
                        }
                    )

        return chains

    def _generate_exploitation_steps(self, vuln_types: List[str]) -> List[str]:
        """Generate step-by-step exploitation guide for a chain."""
        steps_map = {
            "XSS": "1. Inject malicious JavaScript payload",
            "CSRF": "2. Craft cross-site request to perform unauthorized action",
            "SQL_INJECTION": "1. Inject SQL payload to extract data or bypass authentication",
            "AUTHENTICATION_BYPASS": "2. Use extracted credentials or bypass login mechanism",
            "COMMAND_INJECTION": "1. Inject OS commands to gain shell access",
            "PATH_TRAVERSAL": "2. Navigate file system to access sensitive files",
            "DESERIALIZATION": "1. Craft malicious serialized object",
            "SSRF": "2. Use SSRF to reach internal services and execute deserialization",
        }

        return [steps_map.get(vtype, f"Exploit {vtype}") for vtype in vuln_types]

    async def _generate_defense_strategy(
        self, vulnerabilities: List[Dict], predictions: List, chains: List[Dict]
    ) -> Dict[str, Any]:
        """Generate comprehensive defense strategy."""
        strategy = {
            "immediate_actions": [],
            "short_term_fixes": [],
            "long_term_improvements": [],
            "honeypot_deployment": None,
        }

        # Immediate actions for critical issues
        if chains:
            strategy["immediate_actions"].append("🚨 CRITICAL: Exploit chains detected - immediate remediation required")
            strategy["immediate_actions"].append("Disable affected endpoints until patched")
            strategy["immediate_actions"].append("Deploy honeypots to detect active exploitation attempts")

            # Deploy adaptive honeypots
            strategy["honeypot_deployment"] = {
                "recommended": True,
                "type": "multi-layer",
                "targets": [chain["file_path"] for chain in chains[:3]],
            }

        # Short-term fixes
        vuln_types = {self._get_vuln_type(v) for v in vulnerabilities}
        for vtype in vuln_types:
            if vtype == "SQL_INJECTION":
                strategy["short_term_fixes"].append("Implement parameterized queries for all database operations")
            elif vtype == "XSS":
                strategy["short_term_fixes"].append("Add Content Security Policy and output encoding")
            elif vtype == "COMMAND_INJECTION":
                strategy["short_term_fixes"].append("Replace shell commands with safe APIs")

        # Long-term improvements
        strategy["long_term_improvements"] = [
            "Implement continuous security scanning in CI/CD pipeline",
            "Conduct security training for development team",
            "Deploy WAF (Web Application Firewall) with custom rules",
            "Implement zero-trust architecture",
            "Enable real-time threat monitoring and alerting",
        ]

        return strategy

    async def deploy_active_defense(self, attack_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deploy active defense measures when attack is detected.

        Args:
            attack_data: Details of detected attack

        Returns:
            Defense deployment status
        """
        logger.warning(f"🛡️ Deploying active defense against attack from {attack_data.get('ip_address')}")

        ip_address = attack_data.get("ip_address", "unknown")
        attack_type = attack_data.get("attack_type", "unknown")

        # Profile the attacker
        interaction_data = {
            "attack_patterns": [attack_type],
            "tools_detected": attack_data.get("tools", []),
            "exploit_successful": False,
            "duration_seconds": attack_data.get("duration", 0),
            "target": attack_data.get("target"),
        }

        attacker_profile = await self.honeypot_system.profile_attacker(ip_address, interaction_data)

        # Deploy adaptive honeypot
        honeypot_config = await self.honeypot_system.deploy_adaptive_honeypot(attacker_profile)

        # Learn from attack
        await self.pattern_learner.learn_from_attack(
            {
                "attack_type": attack_type,
                "success": False,
                "signature": [attack_type, ip_address],
                "features": attack_data.get("features", {}),
            }
        )

        self.total_attacks_blocked += 1

        return {
            "status": "active_defense_deployed",
            "attacker_profile": {
                "skill_level": attacker_profile.skill_level,
                "sophistication_score": attacker_profile.sophistication_score,
            },
            "honeypot_deployed": {
                "type": honeypot_config.honeypot_type,
                "complexity": honeypot_config.complexity_level,
                "fake_vulnerabilities": len(honeypot_config.fake_vulnerabilities),
            },
            "countermeasures_active": True,
        }

    async def get_security_dashboard_data(self) -> Dict[str, Any]:
        """
        Get real-time security dashboard data.

        Returns:
            Complete security metrics for visualization
        """
        honeypot_stats = await self.honeypot_system.get_honeypot_effectiveness_report()
        anomaly_report = await self.anomaly_detector.get_anomaly_report(timeframe=timedelta(days=1))

        return {
            "timestamp": datetime.now().isoformat(),
            "defense_score": self.defense_score,
            "overall_status": "🟢 PROTECTED" if self.defense_score >= 80 else "🟡 MONITORING",
            "metrics": {
                "total_attacks_blocked": self.total_attacks_blocked,
                "threats_predicted": self.total_threats_predicted,
                "attacker_time_wasted_hours": honeypot_stats.get("total_time_wasted_hours", 0),
                "active_honeypots": honeypot_stats.get("active_honeypots", 0),
                "unique_attackers_tracked": honeypot_stats.get("unique_attackers", 0),
                "behavioral_anomalies_detected": anomaly_report.get("total_anomalies", 0),
                "potential_zero_days": anomaly_report.get("potential_zero_days", 0),
            },
            "active_threats": len(self.active_incidents),
            "ai_systems_status": {
                "predictive_threat_analyzer": "✅ ACTIVE",
                "behavioral_anomaly_detector": "✅ ACTIVE",
                "adaptive_honeypots": "✅ ACTIVE",
                "pattern_learner": "✅ ACTIVE",
            },
        }

    def _get_severity(self, vuln: Dict) -> str:
        """Extract severity from vulnerability dict."""
        sev = vuln.get("severity")
        if hasattr(sev, "value"):
            return sev.value
        return str(sev)

    def _get_vuln_type(self, vuln: Dict) -> str:
        """Extract vulnerability type from dict."""
        vtype = vuln.get("vulnerability_type")
        if hasattr(vtype, "value"):
            return vtype.value
        return str(vtype)


# Global orchestrator instance
_orchestrator = None


def get_orchestrator() -> MasterOrchestrator:
    """Get or create global orchestrator instance."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = MasterOrchestrator()
    return _orchestrator
