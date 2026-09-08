"""
Reputation System

Reputation tracking and scoring for Vireo agents.

Author: Serhii (serhohro)
License: Apache 2.0
Version: 3.0.0
"""

from __future__ import annotations

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Set, Tuple
from datetime import datetime, timedelta
import math

from ..errors import VireoIdentityError


class ReputationEventType(Enum):
    """Types of reputation events."""
    # Positive events
    SUCCESS = "success"
    COMPLETION = "completion"
    VERIFIED = "verified"
    TRUSTED = "trusted"
    HELPFUL = "helpful"
    ACCURATE = "accurate"
    EFFICIENT = "efficient"
    
    # Negative events
    FAILURE = "failure"
    ERROR = "error"
    TIMEOUT = "timeout"
    INVALID = "invalid"
    MALICIOUS = "malicious"
    UNVERIFIED = "unverified"
    INEFFICIENT = "inefficient"
    
    # Neutral events
    ATTEMPT = "attempt"
    QUERY = "query"
    OBSERVATION = "observation"


class ReputationFactor(Enum):
    """Factors that affect reputation."""
    ACCURACY = "accuracy"
    RELIABILITY = "reliability"
    EFFICIENCY = "efficiency"
    TRUSTWORTHINESS = "trustworthiness"
    COOPERATION = "cooperation"
    EXPERIENCE = "experience"
    CONSISTENCY = "consistency"


@dataclass
class ReputationEvent:
    """A single reputation event."""
    id: str
    entity_id: str
    event_type: ReputationEventType
    factor: ReputationFactor
    weight: float
    timestamp: datetime
    description: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_positive(self) -> bool:
        """Check if event is positive."""
        return self.event_type in [
            ReputationEventType.SUCCESS,
            ReputationEventType.COMPLETION,
            ReputationEventType.VERIFIED,
            ReputationEventType.TRUSTED,
            ReputationEventType.HELPFUL,
            ReputationEventType.ACCURATE,
            ReputationEventType.EFFICIENT,
        ]
    
    def is_negative(self) -> bool:
        """Check if event is negative."""
        return self.event_type in [
            ReputationEventType.FAILURE,
            ReputationEventType.ERROR,
            ReputationEventType.TIMEOUT,
            ReputationEventType.INVALID,
            ReputationEventType.MALICIOUS,
            ReputationEventType.UNVERIFIED,
            ReputationEventType.INEFFICIENT,
        ]
    
    def get_score_change(self) -> float:
        """Get the score change for this event."""
        if self.is_positive():
            return self.weight * 0.1
        elif self.is_negative():
            return -self.weight * 0.15
        else:
            return 0.0


@dataclass
class ReputationScore:
    """Reputation score for an entity."""
    entity_id: str
    score: float
    level: str
    total_events: int
    positive_events: int
    negative_events: int
    last_update: datetime
    factors: Dict[ReputationFactor, float]
    confidence: float
    
    def __post_init__(self):
        self.level = self._calculate_level()
    
    def _calculate_level(self) -> str:
        """Calculate reputation level based on score."""
        if self.score >= 0.9:
            return "excellent"
        elif self.score >= 0.7:
            return "good"
        elif self.score >= 0.5:
            return "average"
        elif self.score >= 0.3:
            return "poor"
        else:
            return "untrustworthy"
    
    def is_reliable(self, threshold: float = 0.5) -> bool:
        """Check if score is reliable."""
        return self.score >= threshold
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "entity_id": self.entity_id,
            "score": self.score,
            "level": self.level,
            "total_events": self.total_events,
            "positive_events": self.positive_events,
            "negative_events": self.negative_events,
            "last_update": self.last_update.isoformat(),
            "factors": {f.value: v for f, v in self.factors.items()},
            "confidence": self.confidence,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ReputationScore:
        return cls(
            entity_id=data["entity_id"],
            score=data["score"],
            level=data["level"],
            total_events=data["total_events"],
            positive_events=data["positive_events"],
            negative_events=data["negative_events"],
            last_update=datetime.fromisoformat(data["last_update"]),
            factors={
                ReputationFactor.from_string(f): v
                for f, v in data.get("factors", {}).items()
            },
            confidence=data.get("confidence", 0.5),
        )


class ReputationCalculator:
    """Calculates reputation scores."""
    
    def __init__(self):
        self._factor_weights = {
            ReputationFactor.ACCURACY: 0.25,
            ReputationFactor.RELIABILITY: 0.20,
            ReputationFactor.EFFICIENCY: 0.15,
            ReputationFactor.TRUSTWORTHINESS: 0.20,
            ReputationFactor.COOPERATION: 0.10,
            ReputationFactor.EXPERIENCE: 0.05,
            ReputationFactor.CONSISTENCY: 0.05,
        }
        self._decay_rate = 0.01  # Decay per day
        self._min_events_for_reliable = 10
    
    def calculate_score(self, events: List[ReputationEvent]) -> ReputationScore:
        """Calculate reputation score from events."""
        if not events:
            # No events - neutral score
            return ReputationScore(
                entity_id="unknown",
                score=0.5,
                level="unknown",
                total_events=0,
                positive_events=0,
                negative_events=0,
                last_update=datetime.now(datetime.timezone.utc),
                factors={f: 0.5 for f in ReputationFactor},
                confidence=0.1,
            )
        
        entity_id = events[0].entity_id
        total_events = len(events)
        positive_events = sum(1 for e in events if e.is_positive())
        negative_events = sum(1 for e in events if e.is_negative())
        
        # Calculate factor scores
        factor_scores = {f: 0.5 for f in ReputationFactor}
        factor_counts = {f: 0 for f in ReputationFactor}
        
        for event in events:
            factor = event.factor
            if factor in factor_scores:
                # Update factor score with weighted average
                old_score = factor_scores[factor]
                count = factor_counts[factor]
                new_score = (old_score * count + self._event_score(event)) / (count + 1)
                factor_scores[factor] = new_score
                factor_counts[factor] = count + 1
        
        # Weighted average of factor scores
        weighted_score = 0.0
        total_weight = 0.0
        for factor, score in factor_scores.items():
            weight = self._factor_weights.get(factor, 0.1)
            weighted_score += score * weight
            total_weight += weight
        
        if total_weight > 0:
            base_score = weighted_score / total_weight
        else:
            base_score = 0.5
        
        # Apply time decay
        now = datetime.now(datetime.timezone.utc)
        latest_event = max(e.timestamp for e in events)
        days_since = (now - latest_event).total_seconds() / 86400
        decay_factor = max(0.1, 1.0 - (days_since * self._decay_rate))
        
        # Adjust for positive/negative ratio
        if total_events > 0:
            ratio = positive_events / total_events
            # Shift score based on ratio (0.5 is neutral)
            ratio_adjustment = (ratio - 0.5) * 0.3
            adjusted_score = base_score + ratio_adjustment
        else:
            adjusted_score = base_score
        
        # Apply decay
        final_score = max(0.0, min(1.0, adjusted_score * decay_factor))
        
        # Calculate confidence
        confidence = min(1.0, total_events / self._min_events_for_reliable)
        
        return ReputationScore(
            entity_id=entity_id,
            score=final_score,
            level="unknown",
            total_events=total_events,
            positive_events=positive_events,
            negative_events=negative_events,
            last_update=latest_event,
            factors=factor_scores,
            confidence=confidence,
        )
    
    def _event_score(self, event: ReputationEvent) -> float:
        """Get the score contribution of a single event."""
        if event.is_positive():
            return 0.5 + (event.weight * 0.4)
        elif event.is_negative():
            return 0.5 - (event.weight * 0.4)
        else:
            return 0.5


class ReputationStorage:
    """Storage interface for reputation data."""
    
    def save_event(self, event: ReputationEvent) -> None:
        raise NotImplementedError
    
    def get_events(self, entity_id: str, limit: Optional[int] = None) -> List[ReputationEvent]:
        raise NotImplementedError
    
    def get_score(self, entity_id: str) -> Optional[ReputationScore]:
        raise NotImplementedError
    
    def save_score(self, score: ReputationScore) -> None:
        raise NotImplementedError
    
    def delete_entity(self, entity_id: str) -> bool:
        raise NotImplementedError


class InMemoryReputationStorage(ReputationStorage):
    """In-memory reputation storage."""
    
    def __init__(self):
        self._events: Dict[str, List[ReputationEvent]] = {}
        self._scores: Dict[str, ReputationScore] = {}
    
    def save_event(self, event: ReputationEvent) -> None:
        if event.entity_id not in self._events:
            self._events[event.entity_id] = []
        self._events[event.entity_id].append(event)
    
    def get_events(self, entity_id: str, limit: Optional[int] = None) -> List[ReputationEvent]:
        events = self._events.get(entity_id, [])
        if limit:
            return events[-limit:]
        return events
    
    def get_score(self, entity_id: str) -> Optional[ReputationScore]:
        return self._scores.get(entity_id)
    
    def save_score(self, score: ReputationScore) -> None:
        self._scores[score.entity_id] = score
    
    def delete_entity(self, entity_id: str) -> bool:
        if entity_id in self._events:
            del self._events[entity_id]
        if entity_id in self._scores:
            del self._scores[entity_id]
        return True


class ReputationSystem:
    """
    Comprehensive reputation system.
    
    Tracks and manages reputation for Vireo agents.
    """
    
    def __init__(
        self,
        storage: Optional[ReputationStorage] = None,
        calculator: Optional[ReputationCalculator] = None,
    ):
        self.storage = storage or InMemoryReputationStorage()
        self.calculator = calculator or ReputationCalculator()
        self._event_id_counter = 0
    
    def record_event(
        self,
        entity_id: str,
        event_type: ReputationEventType,
        factor: ReputationFactor = ReputationFactor.RELIABILITY,
        weight: float = 1.0,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ReputationEvent:
        """Record a reputation event."""
        self._event_id_counter += 1
        
        event = ReputationEvent(
            id=f"evt-{self._event_id_counter}",
            entity_id=entity_id,
            event_type=event_type,
            factor=factor,
            weight=weight,
            timestamp=datetime.now(datetime.timezone.utc),
            description=description,
            metadata=metadata or {},
        )
        
        self.storage.save_event(event)
        
        # Update score
        self._update_score(entity_id)
        
        return event
    
    def _update_score(self, entity_id: str) -> None:
        """Update reputation score for an entity."""
        events = self.storage.get_events(entity_id)
        if events:
            score = self.calculator.calculate_score(events)
            self.storage.save_score(score)
    
    def get_score(self, entity_id: str) -> Optional[ReputationScore]:
        """Get reputation score for an entity."""
        score = self.storage.get_score(entity_id)
        if not score:
            # Try to calculate
            events = self.storage.get_events(entity_id)
            if events:
                score = self.calculator.calculate_score(events)
                self.storage.save_score(score)
        return score
    
    def get_reputation(self, entity_id: str) -> Dict[str, Any]:
        """Get complete reputation information."""
        score = self.get_score(entity_id)
        events = self.storage.get_events(entity_id)
        
        if not score:
            return {
                "entity_id": entity_id,
                "score": 0.5,
                "level": "unknown",
                "total_events": len(events) if events else 0,
                "events": [e.__dict__ for e in events[-10:]] if events else [],
            }
        
        return {
            "entity_id": score.entity_id,
            "score": score.score,
            "level": score.level,
            "total_events": score.total_events,
            "positive_events": score.positive_events,
            "negative_events": score.negative_events,
            "confidence": score.confidence,
            "factors": {f.value: v for f, v in score.factors.items()},
            "recent_events": [e.__dict__ for e in events[-10:]] if events else [],
        }
    
    def is_trusted(self, entity_id: str, threshold: float = 0.6) -> bool:
        """Check if entity is trusted based on reputation."""
        score = self.get_score(entity_id)
        if not score:
            return False
        return score.score >= threshold
    
    def get_top_reputed(self, limit: int = 10) -> List[ReputationScore]:
        """Get entities with highest reputation."""
        # In-memory implementation
        # For production, this would be a database query
        return []
    
    def add_external_reputation(self, entity_id: str, source: str, score: float) -> None:
        """
        Add external reputation information.
        
        Integrates reputation from external sources.
        """
        # Record as a special event
        self.record_event(
            entity_id=entity_id,
            event_type=ReputationEventType.OBSERVATION,
            factor=ReputationFactor.TRUSTWORTHINESS,
            weight=score,
            description=f"External reputation from {source}",
            metadata={"source": source, "external_score": score},
        )
    
    def clear_entity(self, entity_id: str) -> bool:
        """Clear all reputation data for an entity."""
        return self.storage.delete_entity(entity_id)