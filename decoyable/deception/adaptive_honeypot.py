"""
Adaptive Honeypot System

Self-learning honeypots that evolve based on attacker behavior.
Adjusts complexity, creates custom fake vulnerabilities, and
wastes sophisticated attackers' time with realistic decoys.
"""

import asyncio
import ipaddress
import logging
import random
import subprocess
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


@dataclass
class AttackerProfile:
    """Profile of an attacker based on observed behavior."""

    attacker_id: str
    ip_address: str
    skill_level: str  # "script_kiddie", "intermediate", "advanced", "elite"
    attack_patterns: List[str]
    tools_used: List[str]
    persistence_score: float
    sophistication_score: float
    first_seen: datetime
    last_seen: datetime
    total_interactions: int
    successful_exploits: int
    time_invested: timedelta
    targets_attempted: Set[str]


@dataclass
class HoneypotConfiguration:
    """Configuration for a honeypot instance."""

    honeypot_id: str
    honeypot_type: str
    complexity_level: str
    fake_vulnerabilities: List[Dict[str, Any]]
    decoy_services: List[str]
    interaction_rules: Dict[str, Any]
    learning_enabled: bool


class AdaptiveHoneypotSystem:
    """
    Self-learning honeypot system that adapts to attackers.

    Creates customized traps based on attacker skill level and behavior.
    """

    def __init__(self):
        """Initialize adaptive honeypot system."""
        self.active_honeypots: Dict[str, HoneypotConfiguration] = {}
        self.attacker_profiles: Dict[str, AttackerProfile] = {}
        self.interaction_history: List[Dict[str, Any]] = []
        self.learning_enabled = True

        logger.info("Adaptive Honeypot System initialized")

    async def profile_attacker(self, ip_address: str, interaction_data: Dict[str, Any]) -> AttackerProfile:
        """
        Profile an attacker based on their behavior.

        Args:
            ip_address: Attacker IP address
            interaction_data: Details of interaction

        Returns:
            Attacker profile with skill level and characteristics
        """
        attacker_id = f"attacker_{ip_address.replace('.', '_')}"

        # Get existing profile or create new one
        if attacker_id in self.attacker_profiles:
            profile = self.attacker_profiles[attacker_id]
            profile.last_seen = datetime.now()
            profile.total_interactions += 1

            # Update patterns and tools
            new_patterns = interaction_data.get("attack_patterns", [])
            profile.attack_patterns.extend(new_patterns)
            profile.attack_patterns = list(set(profile.attack_patterns))  # Remove duplicates

            new_tools = interaction_data.get("tools_detected", [])
            profile.tools_used.extend(new_tools)
            profile.tools_used = list(set(profile.tools_used))

            # Update targets
            target = interaction_data.get("target")
            if target:
                profile.targets_attempted.add(target)

            # Update success count
            if interaction_data.get("exploit_successful"):
                profile.successful_exploits += 1

        else:
            # Create new profile
            profile = AttackerProfile(
                attacker_id=attacker_id,
                ip_address=ip_address,
                skill_level="unknown",
                attack_patterns=interaction_data.get("attack_patterns", []),
                tools_used=interaction_data.get("tools_detected", []),
                persistence_score=0.0,
                sophistication_score=0.0,
                first_seen=datetime.now(),
                last_seen=datetime.now(),
                total_interactions=1,
                successful_exploits=1 if interaction_data.get("exploit_successful") else 0,
                time_invested=timedelta(seconds=interaction_data.get("duration_seconds", 0)),
                targets_attempted={interaction_data.get("target")} if interaction_data.get("target") else set(),
            )

        # Calculate scores and skill level
        await self._calculate_attacker_scores(profile, interaction_data)
        profile.skill_level = await self._determine_skill_level(profile)

        self.attacker_profiles[attacker_id] = profile

        logger.info(f"Attacker profiled: {attacker_id} - Skill: {profile.skill_level}")

        return profile

    async def _calculate_attacker_scores(self, profile: AttackerProfile, interaction: Dict[str, Any]) -> None:
        """Calculate attacker sophistication and persistence scores."""
        # Sophistication score (0-1)
        sophistication_indicators = {
            "custom_exploits": 0.3,
            "0day_attempts": 0.4,
            "advanced_evasion": 0.3,
            "automated_tools": 0.1,
            "manual_exploitation": 0.2,
            "multiple_vectors": 0.2,
            "lateral_movement": 0.3,
            "privilege_escalation": 0.3,
        }

        sophistication = 0.0
        for indicator, weight in sophistication_indicators.items():
            if interaction.get(indicator, False):
                sophistication += weight

        # Update rolling average
        profile.sophistication_score = (profile.sophistication_score * 0.7) + (sophistication * 0.3)

        # Persistence score (0-1)
        session_duration = interaction.get("duration_seconds", 0)
        persistence = min(1.0, session_duration / 3600)  # Normalize to 1 hour

        profile.persistence_score = (profile.persistence_score * 0.7) + (persistence * 0.3)

    async def _determine_skill_level(self, profile: AttackerProfile) -> str:
        """Determine attacker skill level from profile."""
        # Script kiddie: low sophistication, uses known tools
        if profile.sophistication_score < 0.3 and len(profile.tools_used) <= 2:
            return "script_kiddie"

        # Intermediate: moderate sophistication, some manual work
        elif profile.sophistication_score < 0.6:
            return "intermediate"

        # Advanced: high sophistication, custom exploits
        elif profile.sophistication_score < 0.8:
            return "advanced"

        # Elite: very high sophistication, 0-days, advanced techniques
        else:
            return "elite"

    async def deploy_adaptive_honeypot(self, attacker_profile: AttackerProfile) -> HoneypotConfiguration:
        """
        Deploy honeypot tailored to attacker's skill level.

        Args:
            attacker_profile: Profile of the attacker

        Returns:
            Honeypot configuration
        """
        skill = attacker_profile.skill_level

        if skill == "script_kiddie":
            config = await self._deploy_basic_honeypot(attacker_profile)
        elif skill == "intermediate":
            config = await self._deploy_intermediate_honeypot(attacker_profile)
        elif skill == "advanced":
            config = await self._deploy_advanced_honeypot(attacker_profile)
        else:  # elite
            config = await self._deploy_elite_honeypot(attacker_profile)

        self.active_honeypots[config.honeypot_id] = config

        logger.info(f"Deployed {skill} honeypot: {config.honeypot_id}")

        return config

    async def _deploy_basic_honeypot(self, profile: AttackerProfile) -> HoneypotConfiguration:
        """Deploy basic honeypot for script kiddies."""
        return HoneypotConfiguration(
            honeypot_id=f"basic_{profile.attacker_id}_{datetime.now().timestamp()}",
            honeypot_type="basic",
            complexity_level="low",
            fake_vulnerabilities=[
                {
                    "type": "sql_injection",
                    "endpoint": "/api/login",
                    "difficulty": "trivial",
                    "payload_detector": "' OR '1'='1",
                },
                {
                    "type": "xss",
                    "endpoint": "/api/comment",
                    "difficulty": "trivial",
                    "payload_detector": "<script>alert",
                },
                {
                    "type": "directory_traversal",
                    "endpoint": "/api/file",
                    "difficulty": "easy",
                    "payload_detector": "../",
                },
            ],
            decoy_services=["fake_admin_panel", "fake_database", "fake_backup_files"],
            interaction_rules={
                "response_delay": "immediate",
                "fake_success": True,
                "data_returned": "fake_credentials",
                "trap_obvious": True,
            },
            learning_enabled=True,
        )

    async def _deploy_intermediate_honeypot(self, profile: AttackerProfile) -> HoneypotConfiguration:
        """Deploy intermediate honeypot for moderate attackers."""
        return HoneypotConfiguration(
            honeypot_id=f"intermediate_{profile.attacker_id}_{datetime.now().timestamp()}",
            honeypot_type="intermediate",
            complexity_level="medium",
            fake_vulnerabilities=[
                {
                    "type": "authentication_bypass",
                    "endpoint": "/api/admin",
                    "difficulty": "medium",
                    "requires": ["session_manipulation", "timing_attack"],
                },
                {
                    "type": "insecure_deserialization",
                    "endpoint": "/api/import",
                    "difficulty": "medium",
                    "payload_detector": "pickle",
                },
                {
                    "type": "ssrf",
                    "endpoint": "/api/fetch",
                    "difficulty": "medium",
                    "internal_network": "172.16.0.0/16",
                },
            ],
            decoy_services=[
                "fake_internal_api",
                "fake_jenkins",
                "fake_git_repo",
                "fake_docker_registry",
            ],
            interaction_rules={
                "response_delay": "realistic",
                "fake_success": False,  # Make them work for it
                "data_returned": "partial_data",
                "trap_obvious": False,
                "escalation_path": True,
            },
            learning_enabled=True,
        )

    async def _deploy_advanced_honeypot(self, profile: AttackerProfile) -> HoneypotConfiguration:
        """Deploy advanced honeypot for sophisticated attackers."""
        return HoneypotConfiguration(
            honeypot_id=f"advanced_{profile.attacker_id}_{datetime.now().timestamp()}",
            honeypot_type="advanced",
            complexity_level="high",
            fake_vulnerabilities=[
                {
                    "type": "race_condition",
                    "endpoint": "/api/transaction",
                    "difficulty": "hard",
                    "requires": ["precise_timing", "multi_threading"],
                },
                {
                    "type": "type_confusion",
                    "endpoint": "/api/process",
                    "difficulty": "hard",
                    "language_specific": "python",
                },
                {
                    "type": "logic_flaw",
                    "endpoint": "/api/workflow",
                    "difficulty": "very_hard",
                    "requires": ["deep_understanding", "custom_exploit"],
                },
            ],
            decoy_services=[
                "fake_kubernetes_cluster",
                "fake_database_cluster",
                "fake_vault_server",
                "fake_ci_cd_pipeline",
                "fake_monitoring_system",
            ],
            interaction_rules={
                "response_delay": "variable",
                "fake_success": False,
                "data_returned": "encrypted",
                "trap_obvious": False,
                "escalation_path": True,
                "lateral_movement_allowed": True,
                "forensics_collection": "detailed",
            },
            learning_enabled=True,
        )

    async def _deploy_elite_honeypot(self, profile: AttackerProfile) -> HoneypotConfiguration:
        """Deploy elite honeypot for expert attackers - maximum time waste."""
        return HoneypotConfiguration(
            honeypot_id=f"elite_{profile.attacker_id}_{datetime.now().timestamp()}",
            honeypot_type="elite",
            complexity_level="extreme",
            fake_vulnerabilities=[
                {
                    "type": "custom_protocol_vuln",
                    "endpoint": "proprietary_service:8443",
                    "difficulty": "extreme",
                    "requires": ["reverse_engineering", "custom_fuzzing", "0day_development"],
                },
                {
                    "type": "cryptographic_weakness",
                    "endpoint": "/api/crypto",
                    "difficulty": "extreme",
                    "requires": ["crypto_analysis", "timing_attacks"],
                },
                {
                    "type": "kernel_exploit",
                    "endpoint": "system_level",
                    "difficulty": "extreme",
                    "requires": ["kernel_knowledge", "memory_corruption"],
                },
            ],
            decoy_services=[
                "fake_research_network",
                "fake_classified_system",
                "fake_payment_processor",
                "fake_backup_datacenter",
                "fake_security_operations_center",
                "fake_threat_intel_platform",
            ],
            interaction_rules={
                "response_delay": "realistic_distributed",
                "fake_success": False,
                "data_returned": "realistic_sensitive",
                "trap_obvious": False,
                "escalation_path": True,
                "lateral_movement_allowed": True,
                "forensics_collection": "comprehensive",
                "counter_intelligence": True,  # Feed false data about defenses
                "time_sink": "maximum",  # Waste as much attacker time as possible
            },
            learning_enabled=True,
        )

    async def record_interaction(self, honeypot_id: str, interaction_data: Dict[str, Any]) -> None:
        """Record interaction with honeypot for learning."""
        self.interaction_history.append(
            {
                "honeypot_id": honeypot_id,
                "timestamp": datetime.now(),
                "attacker_ip": interaction_data.get("attacker_ip"),
                "action": interaction_data.get("action"),
                "exploit_attempted": interaction_data.get("exploit_attempted"),
                "success": interaction_data.get("success", False),
                "data_accessed": interaction_data.get("data_accessed"),
                "duration": interaction_data.get("duration_seconds"),
            }
        )

        # Learn from interaction if enabled
        if self.learning_enabled:
            await self._learn_from_interaction(honeypot_id, interaction_data)

    async def _learn_from_interaction(self, honeypot_id: str, interaction: Dict[str, Any]) -> None:
        """Learn and adapt from honeypot interaction."""
        honeypot = self.active_honeypots.get(honeypot_id)
        if not honeypot:
            return

        # Update honeypot configuration based on effectiveness
        effectiveness = interaction.get("time_spent", 0) / 60  # minutes

        if effectiveness > 30:  # Very effective (>30 min)
            logger.info(f"Honeypot {honeypot_id} highly effective - keeping configuration")
        elif effectiveness < 5:  # Not effective (<5 min)
            logger.warning(f"Honeypot {honeypot_id} not effective - considering adaptation")
            # Could trigger redeployment with different config

    async def get_honeypot_effectiveness_report(self) -> Dict[str, Any]:
        """Generate report on honeypot effectiveness."""
        if not self.interaction_history:
            return {"status": "No interactions recorded"}

        total_interactions = len(self.interaction_history)
        total_time_wasted = sum(i.get("duration", 0) for i in self.interaction_history)

        # Group by attacker
        by_attacker = {}
        for interaction in self.interaction_history:
            ip = interaction.get("attacker_ip")
            if ip:
                if ip not in by_attacker:
                    by_attacker[ip] = []
                by_attacker[ip].append(interaction)

        return {
            "total_interactions": total_interactions,
            "unique_attackers": len(by_attacker),
            "total_time_wasted_hours": total_time_wasted / 3600,
            "avg_time_per_interaction_minutes": (total_time_wasted / total_interactions / 60) if total_interactions > 0 else 0,
            "active_honeypots": len(self.active_honeypots),
            "honeypot_types": {
                "basic": sum(1 for h in self.active_honeypots.values() if h.honeypot_type == "basic"),
                "intermediate": sum(1 for h in self.active_honeypots.values() if h.honeypot_type == "intermediate"),
                "advanced": sum(1 for h in self.active_honeypots.values() if h.honeypot_type == "advanced"),
                "elite": sum(1 for h in self.active_honeypots.values() if h.honeypot_type == "elite"),
            },
        }

    async def generate_decoy_credentials(self, realism_level: str = "high") -> Dict[str, str]:
        """
        Generate fake but realistic-looking credentials.

        Args:
            realism_level: Level of realism (low, medium, high)

        Returns:
            Fake credentials
        """
        if realism_level == "high":
            # Highly realistic credentials
            usernames = ["admin", "administrator", "root", "system", "sa", "backup_admin"]
            domains = ["internal", "corp", "prod", "admin", "secure"]

            username = f"{random.choice(usernames)}_{random.choice(domains)}"
            # Generate realistic-looking but fake password
            password = f"{random.choice(['P@ssw0rd', 'Admin', 'Secret'])}{''.join(random.choices('0123456789', k=4))}"

            return {
                "username": username,
                "password": password,
                "api_key": f"sk_live_{''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=32))}",
                "token": f"eyJ{''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=128))}",
            }
        else:
            # Obvious fake credentials
            return {
                "username": "admin",
                "password": "password123",
                "api_key": "fake_api_key",
                "token": "fake_token",
            }
