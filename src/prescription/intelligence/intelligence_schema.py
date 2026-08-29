from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict

class EvidenceThemeType(Enum):
    CARDIAC_ELECTROPHYSIOLOGY_SIGNAL = "CARDIAC_ELECTROPHYSIOLOGY_SIGNAL"
    HEMODYNAMIC_SIGNAL = "HEMODYNAMIC_SIGNAL"
    NEUROLOGICAL_SIGNAL = "NEUROLOGICAL_SIGNAL"
    RESPIRATORY_SIGNAL = "RESPIRATORY_SIGNAL"
    GASTROINTESTINAL_SIGNAL = "GASTROINTESTINAL_SIGNAL"
    RENAL_SIGNAL = "RENAL_SIGNAL"
    HEPATIC_SIGNAL = "HEPATIC_SIGNAL"
    HEMATOLOGICAL_SIGNAL = "HEMATOLOGICAL_SIGNAL"
    METABOLIC_SIGNAL = "METABOLIC_SIGNAL"
    IMMUNOLOGICAL_SIGNAL = "IMMUNOLOGICAL_SIGNAL"
    DERMATOLOGICAL_SIGNAL = "DERMATOLOGICAL_SIGNAL"
    MUSCULOSKELETAL_SIGNAL = "MUSCULOSKELETAL_SIGNAL"
    GENERAL_SYSTEMIC_SIGNAL = "GENERAL_SYSTEMIC_SIGNAL"
    UNKNOWN_OR_UNMAPPED_THEME = "UNKNOWN_OR_UNMAPPED_THEME"

class ReinforcementLevel(Enum):
    LIMITED_REINFORCEMENT = "LIMITED_REINFORCEMENT"
    EMERGING_REINFORCEMENT = "EMERGING_REINFORCEMENT"
    MODERATE_REINFORCEMENT = "MODERATE_REINFORCEMENT"
    STRONG_REINFORCEMENT = "STRONG_REINFORCEMENT"

class EvidenceConcentrationType(Enum):
    NO_EVIDENCE_CONCENTRATION = "NO_EVIDENCE_CONCENTRATION"
    SPARSE_EVIDENCE = "SPARSE_EVIDENCE"
    CENTRALIZED_EVIDENCE = "CENTRALIZED_EVIDENCE"
    CLUSTER_CONCENTRATED_EVIDENCE = "CLUSTER_CONCENTRATED_EVIDENCE"
    DISTRIBUTED_EVIDENCE = "DISTRIBUTED_EVIDENCE"
    MIXED_EVIDENCE_DISTRIBUTION = "MIXED_EVIDENCE_DISTRIBUTION"

class AlignmentLevel(Enum):
    HIGH_ALIGNMENT = "HIGH_ALIGNMENT"
    MODERATE_ALIGNMENT = "MODERATE_ALIGNMENT"
    LOW_ALIGNMENT = "LOW_ALIGNMENT"
    NO_MEANINGFUL_ALIGNMENT = "NO_MEANINGFUL_ALIGNMENT"

@dataclass
class EvidenceTheme:
    theme_id: str
    theme_name: str
    description: str
    mapped_events: List[str] = field(default_factory=list)
    supporting_pairs: List[str] = field(default_factory=list)
    participating_drugs: List[str] = field(default_factory=list)
    supporting_evidence_count: int = 0
    convergent_pair_count: int = 0
    source_channels: List[str] = field(default_factory=list)

@dataclass
class CrossPairSignalGroup:
    group_id: str
    theme_id: str
    supporting_pairs: List[str] = field(default_factory=list)
    participating_drugs: List[str] = field(default_factory=list)
    supporting_events: List[str] = field(default_factory=list)
    channel_distribution: List[str] = field(default_factory=list)
    convergent_pair_count: int = 0
    reinforcement_score: float = 0.0
    reinforcement_level: ReinforcementLevel = ReinforcementLevel.LIMITED_REINFORCEMENT

@dataclass
class EvidenceConcentrationProfile:
    concentration_type: EvidenceConcentrationType
    edge_coverage_ratio: float = 0.0
    dominant_drug_id: Optional[str] = None
    dominant_drug_share: float = 0.0
    dominant_cluster_id: Optional[str] = None
    dominant_cluster_edge_share: float = 0.0

@dataclass
class DrugAlignmentProfile:
    drug_id: str
    display_name: str
    structural_rank: int
    evidence_participation_rank: int
    theme_participation_rank: int
    convergent_evidence_rank: int
    alignment_score: float
    alignment_level: AlignmentLevel

@dataclass
class StructuralEvidenceAlignment:
    alignment_level: AlignmentLevel
    explanation: str
    drug_alignment_profiles: List[DrugAlignmentProfile] = field(default_factory=list)

@dataclass
class EvidenceIntelligenceSummary:
    major_theme_count: int
    reinforced_signal_group_count: int
    dominant_theme: Optional[str]
    dominant_evidence_concentration: EvidenceConcentrationType
    strongest_reinforcement_level: ReinforcementLevel
    highest_alignment_level: AlignmentLevel
    overall_intelligence_pattern: str

@dataclass
class PrescriptionEvidenceIntelligenceProfile:
    analysis_id: str
    generated_at: str
    themes: List[EvidenceTheme] = field(default_factory=list)
    signal_groups: List[CrossPairSignalGroup] = field(default_factory=list)
    concentration_profile: Optional[EvidenceConcentrationProfile] = None
    structural_evidence_alignment: Optional[StructuralEvidenceAlignment] = None
    summary: Optional[EvidenceIntelligenceSummary] = None
    narrative: str = ""
    guardrails: List[str] = field(default_factory=list)
