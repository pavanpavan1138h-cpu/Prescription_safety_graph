from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional

class SnapshotPositionType(str, Enum):
    BASELINE = "BASELINE"
    INTERMEDIATE = "INTERMEDIATE"
    LATEST = "LATEST"

class PersistenceLevel(str, Enum):
    HIGHLY_PERSISTENT = "HIGHLY_PERSISTENT"
    PERSISTENT = "PERSISTENT"
    MODERATELY_PERSISTENT = "MODERATELY_PERSISTENT"
    INTERMITTENT = "INTERMITTENT"
    NON_PERSISTENT = "NON_PERSISTENT"
    INSUFFICIENT_HISTORY = "INSUFFICIENT_HISTORY"

class EmergenceClassification(str, Enum):
    NEWLY_EMERGED = "NEWLY_EMERGED"
    TRANSIENTLY_EMERGED = "TRANSIENTLY_EMERGED"
    PERSISTENTLY_EMERGED = "PERSISTENTLY_EMERGED"
    RECURRENTLY_EMERGED = "RECURRENTLY_EMERGED"
    NOT_EMERGED = "NOT_EMERGED"

class DisappearanceClassification(str, Enum):
    TEMPORARILY_ABSENT = "TEMPORARILY_ABSENT"
    PERSISTENTLY_DISAPPEARED = "PERSISTENTLY_DISAPPEARED"
    RECURRENTLY_PRESENT = "RECURRENTLY_PRESENT"
    NOT_DISAPPEARED = "NOT_DISAPPEARED"

class ChangePointLevel(str, Enum):
    NO_SIGNIFICANT_CHANGE = "NO_SIGNIFICANT_CHANGE"
    MINOR_CHANGE = "MINOR_CHANGE"
    MODERATE_CHANGE = "MODERATE_CHANGE"
    MAJOR_CHANGE = "MAJOR_CHANGE"
    COMPOSITE_CHANGE_POINT = "COMPOSITE_CHANGE_POINT"

class StructuralEvolutionLevel(str, Enum):
    STRUCTURALLY_STABLE = "STRUCTURALLY_STABLE"
    GRADUAL_STRUCTURAL_EVOLUTION = "GRADUAL_STRUCTURAL_EVOLUTION"
    STRUCTURAL_RECONFIGURATION = "STRUCTURAL_RECONFIGURATION"
    HIGH_STRUCTURAL_VOLATILITY = "HIGH_STRUCTURAL_VOLATILITY"
    INSUFFICIENT_STRUCTURAL_HISTORY = "INSUFFICIENT_STRUCTURAL_HISTORY"

class SignalEvolutionLevel(str, Enum):
    SIGNAL_STABLE = "SIGNAL_STABLE"
    SIGNAL_STRENGTHENING = "SIGNAL_STRENGTHENING"
    SIGNAL_WEAKENING = "SIGNAL_WEAKENING"
    SIGNAL_RECONFIGURATION = "SIGNAL_RECONFIGURATION"
    SIGNAL_VOLATILITY = "SIGNAL_VOLATILITY"
    INSUFFICIENT_SIGNAL_HISTORY = "INSUFFICIENT_SIGNAL_HISTORY"

class StabilityEvolutionLevel(str, Enum):
    CONSISTENTLY_STABLE = "CONSISTENTLY_STABLE"
    STABLE_TO_CONTEXT_SENSITIVE = "STABLE_TO_CONTEXT_SENSITIVE"
    CONTEXT_SENSITIVE_TO_STABLE = "CONTEXT_SENSITIVE_TO_STABLE"
    FLUCTUATING_STABILITY = "FLUCTUATING_STABILITY"
    INSUFFICIENT_LONGITUDINAL_CONTEXT = "INSUFFICIENT_LONGITUDINAL_CONTEXT"

class TrustworthinessEvolutionLevel(str, Enum):
    CONSISTENTLY_HIGH = "CONSISTENTLY_HIGH"
    IMPROVING = "IMPROVING"
    DECLINING = "DECLINING"
    VOLATILE = "VOLATILE"
    CONSISTENTLY_LIMITED = "CONSISTENTLY_LIMITED"
    INSUFFICIENT_HISTORY = "INSUFFICIENT_HISTORY"

class LongitudinalEvolutionLevel(str, Enum):
    HIGH_CONTINUITY = "HIGH_CONTINUITY"
    GRADUAL_EVOLUTION = "GRADUAL_EVOLUTION"
    MAJOR_ANALYTICAL_TRANSITION = "MAJOR_ANALYTICAL_TRANSITION"
    HIGH_ANALYTICAL_VOLATILITY = "HIGH_ANALYTICAL_VOLATILITY"
    INSUFFICIENT_LONGITUDINAL_CONTEXT = "INSUFFICIENT_LONGITUDINAL_CONTEXT"

@dataclass
class PrescriptionSnapshotReference:
    analysis_id: str
    prescription_id: str
    snapshot_timestamp: str
    sequence_index: int
    position_type: SnapshotPositionType
    medications: List[str] = field(default_factory=list)

@dataclass
class PersistenceProfile:
    entity_id: str
    entity_type: str
    presence_ratio: float
    longest_consecutive_run: int
    first_seen_index: int
    last_seen_index: int
    persistence_level: PersistenceLevel

@dataclass
class EmergenceEvent:
    entity_id: str
    entity_type: str
    emergence_index: int
    previously_absent_count: int
    post_emergence_persistence: float
    classification: EmergenceClassification

@dataclass
class DisappearanceEvent:
    entity_id: str
    entity_type: str
    disappearance_index: int
    previously_present_count: int
    post_disappearance_absence_ratio: float
    classification: DisappearanceClassification

@dataclass
class LongitudinalChangePoint:
    from_snapshot_index: int
    to_snapshot_index: int
    structural_change: float
    signal_change: float
    stability_change: float
    trustworthiness_change: float
    medication_set_change: float
    aggregate_change_score: float
    change_level: ChangePointLevel
    contributing_dimensions: List[str] = field(default_factory=list)

@dataclass
class StructuralEvolutionProfile:
    topology_sequence: List[str]
    density_sequence: List[float]
    central_participant_sequence: List[List[str]]
    cluster_count_sequence: List[int]
    topology_transition_count: int
    structural_change_points: List[int]
    classification: StructuralEvolutionLevel

@dataclass
class SignalEvolutionProfile:
    theme_id: str
    presence_sequence: List[bool]
    reinforcement_sequence: List[float]
    rank_sequence: List[int]
    persistence_ratio: float
    classification: SignalEvolutionLevel
    emergence_events: List[EmergenceEvent] = field(default_factory=list)
    disappearance_events: List[DisappearanceEvent] = field(default_factory=list)

@dataclass
class StabilityEvolutionProfile:
    stability_sequence: List[str]
    sensitivity_sequence: List[float]
    transition_count: int
    classification: StabilityEvolutionLevel

@dataclass
class TrustworthinessEvolutionProfile:
    score_sequence: List[float]
    level_sequence: List[str]
    score_delta_sequence: List[float]
    mean_score: float
    score_volatility: float
    classification: TrustworthinessEvolutionLevel

@dataclass
class CrossLayerEvolutionProfile:
    structural_persistence: float
    signal_persistence: float
    stability_persistence: float
    provenance_persistence: float
    trustworthiness_persistence: float
    cross_layer_transition_alignment: List[str] = field(default_factory=list)
    classification: str = ""
    explanation: str = ""

@dataclass
class PrescriptionLongitudinalProfile:
    timeline: List[PrescriptionSnapshotReference]
    persistence_profiles: List[PersistenceProfile]
    emergence_events: List[EmergenceEvent]
    disappearance_events: List[DisappearanceEvent]
    change_points: List[LongitudinalChangePoint]
    structural_evolution: StructuralEvolutionProfile
    signal_evolution: List[SignalEvolutionProfile]
    stability_evolution: StabilityEvolutionProfile
    trustworthiness_evolution: TrustworthinessEvolutionProfile
    cross_layer_evolution: CrossLayerEvolutionProfile
    overall_evolution_level: LongitudinalEvolutionLevel
    longitudinal_summary: str
    guardrails: List[str]
