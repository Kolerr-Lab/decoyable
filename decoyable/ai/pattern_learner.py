"""
Attack Pattern Learning System

Machine learning component that learns from attack patterns,
builds predictive models, and improves detection over time.
"""

import asyncio
import json
import logging
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class AttackPattern:
    """Represents a learned attack pattern."""

    pattern_id: str
    attack_type: str
    signature: List[str]
    frequency: int
    success_rate: float
    first_seen: datetime
    last_seen: datetime
    variants: List[Dict[str, Any]]
    countermeasures: List[str]


class AttackPatternLearner:
    """
    ML-based attack pattern learning system.

    Learns from observed attacks to improve detection and prediction.
    """

    def __init__(self, model_dir: Optional[Path] = None):
        """
        Initialize attack pattern learner.

        Args:
            model_dir: Directory to store learned models
        """
        self.model_dir = model_dir or Path("./models/attack_patterns")
        self.model_dir.mkdir(parents=True, exist_ok=True)

        self.patterns: Dict[str, AttackPattern] = {}
        self.attack_sequences: List[List[str]] = []
        self.pattern_graph: Dict[str, Set[str]] = defaultdict(set)
        self.learning_rate = 0.1

        logger.info("Attack Pattern Learner initialized")

    async def learn_from_attack(self, attack_data: Dict[str, Any]) -> None:
        """
        Learn from a single attack instance.

        Args:
            attack_data: Attack details and metadata
        """
        attack_type = attack_data.get("attack_type", "unknown")
        success = attack_data.get("success", False)
        signature_elements = attack_data.get("signature", [])

        # Generate pattern ID
        pattern_id = self._generate_pattern_id(signature_elements)

        # Update or create pattern
        if pattern_id in self.patterns:
            pattern = self.patterns[pattern_id]
            pattern.frequency += 1
            pattern.last_seen = datetime.now()

            # Update success rate
            new_success_rate = pattern.success_rate * (1 - self.learning_rate) + (
                1.0 if success else 0.0
            ) * self.learning_rate
            pattern.success_rate = new_success_rate

            # Add variant
            pattern.variants.append(
                {
                    "timestamp": datetime.now(),
                    "success": success,
                    "details": attack_data.get("details", {}),
                }
            )

        else:
            # Create new pattern
            self.patterns[pattern_id] = AttackPattern(
                pattern_id=pattern_id,
                attack_type=attack_type,
                signature=signature_elements,
                frequency=1,
                success_rate=1.0 if success else 0.0,
                first_seen=datetime.now(),
                last_seen=datetime.now(),
                variants=[{"timestamp": datetime.now(), "success": success}],
                countermeasures=[],
            )

        # Record attack sequence for pattern analysis
        self.attack_sequences.append(signature_elements)

        # Update pattern graph (attack chains)
        for i in range(len(signature_elements) - 1):
            self.pattern_graph[signature_elements[i]].add(signature_elements[i + 1])

        logger.info(f"Learned attack pattern: {attack_type} (ID: {pattern_id})")

    def _generate_pattern_id(self, signature: List[str]) -> str:
        """Generate unique pattern ID from signature."""
        import hashlib

        signature_str = "|".join(sorted(signature))
        return hashlib.sha256(signature_str.encode()).hexdigest()[:16]

    async def identify_pattern(self, attack_signature: List[str]) -> Optional[AttackPattern]:
        """
        Identify if attack matches known pattern.

        Args:
            attack_signature: Attack signature elements

        Returns:
            Matching pattern if found
        """
        pattern_id = self._generate_pattern_id(attack_signature)

        return self.patterns.get(pattern_id)

    async def predict_next_step(self, current_sequence: List[str]) -> List[Tuple[str, float]]:
        """
        Predict likely next steps in an attack sequence.

        Args:
            current_sequence: Current attack sequence

        Returns:
            List of (next_step, probability) tuples
        """
        if not current_sequence:
            return []

        last_step = current_sequence[-1]

        if last_step not in self.pattern_graph:
            return []

        # Count occurrences of next steps
        next_steps = Counter()

        for seq in self.attack_sequences:
            if last_step in seq:
                idx = seq.index(last_step)
                if idx + 1 < len(seq):
                    next_steps[seq[idx + 1]] += 1

        # Calculate probabilities
        total = sum(next_steps.values())
        predictions = [(step, count / total) for step, count in next_steps.items()]

        # Sort by probability
        predictions.sort(key=lambda x: x[1], reverse=True)

        return predictions[:5]  # Top 5 predictions

    async def get_trending_patterns(self, timeframe: timedelta = timedelta(days=7)) -> List[AttackPattern]:
        """
        Get trending attack patterns in timeframe.

        Args:
            timeframe: Time window to analyze

        Returns:
            List of trending patterns
        """
        cutoff = datetime.now() - timeframe

        trending = [p for p in self.patterns.values() if p.last_seen >= cutoff]

        # Sort by frequency
        trending.sort(key=lambda x: x.frequency, reverse=True)

        return trending[:10]

    async def export_model(self) -> Dict[str, Any]:
        """Export learned model for sharing or backup."""
        return {
            "patterns": {
                pid: {
                    "pattern_id": p.pattern_id,
                    "attack_type": p.attack_type,
                    "signature": p.signature,
                    "frequency": p.frequency,
                    "success_rate": p.success_rate,
                    "first_seen": p.first_seen.isoformat(),
                    "last_seen": p.last_seen.isoformat(),
                }
                for pid, p in self.patterns.items()
            },
            "pattern_count": len(self.patterns),
            "total_attacks_learned": sum(p.frequency for p in self.patterns.values()),
            "export_timestamp": datetime.now().isoformat(),
        }

    async def import_model(self, model_data: Dict[str, Any]) -> None:
        """Import learned model from external source."""
        imported_count = 0

        for pid, pdata in model_data.get("patterns", {}).items():
            if pid not in self.patterns:
                self.patterns[pid] = AttackPattern(
                    pattern_id=pdata["pattern_id"],
                    attack_type=pdata["attack_type"],
                    signature=pdata["signature"],
                    frequency=pdata["frequency"],
                    success_rate=pdata["success_rate"],
                    first_seen=datetime.fromisoformat(pdata["first_seen"]),
                    last_seen=datetime.fromisoformat(pdata["last_seen"]),
                    variants=[],
                    countermeasures=[],
                )
                imported_count += 1

        logger.info(f"Imported {imported_count} attack patterns")
