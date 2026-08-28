"""
src/advanced_intelligence_engines.py

Implementation of:
1. PrescriptionComplexityEngine
2. DrugParticipationEngine
3. CrossPairEventConvergenceEngine
4. EvidencePatternEngine
5. ReviewPrioritizationEngine
6. UncertaintyEngine
7. ContextRequirementsEngine
8. AdvancedExplanationEngine
"""

import logging
from typing import List, Dict, Tuple, Set, Optional
from collections import defaultdict

from prescription_schema import PrescriptionSafetyReport
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from prescription_reasoning import PrescriptionSafetyReasoner
from advanced_intelligence_schema import (
    ComplexityCategory,
    PrescriptionComplexityProfile,
    DrugParticipationCategory,
    DrugParticipationProfile,
    EventConvergenceCategory,
    AdverseEventConvergenceItem,
    PatternType,
    EvidencePatternItem,
    ReviewPriorityTier,
    ReviewPriorityFinding,
    UncertaintyCategory,
    UncertaintyProfile,
    ClinicalContextRequirement,
    AdvancedExplanationSummary,
    AdvancedPrescriptionIntelligenceReport
)

logger = logging.getLogger(__name__)

class PrescriptionComplexityEngine:
    @staticmethod
    def analyze(report: PrescriptionSafetyReport) -> PrescriptionComplexityProfile:
        n_drugs = report.evidence_summary.unique_canonical_drugs
        n_pairs = report.evidence_summary.total_analyzed_pairs
        pos_pairs = report.evidence_summary.pairs_with_evidence
        conv_pairs = report.evidence_summary.convergent_evidence_pairs
        unres_count = report.evidence_summary.unresolved_items_count

        # Participating drugs count
        participating_drugs = set()
        drug_pos_counts = defaultdict(int)
        for p in report.pair_results:
            if p.get("evidence_status") != "NO_DIRECT_GRAPH_EVIDENCE":
                da = p.get("drug_a_id")
                db = p.get("drug_b_id")
                if da and db:
                    participating_drugs.add(da)
                    participating_drugs.add(db)
                    drug_pos_counts[da] += 1
                    drug_pos_counts[db] += 1

        part_count = len(participating_drugs)
        max_part_ratio = 0.0
        if pos_pairs > 0 and drug_pos_counts:
            max_part_ratio = max(drug_pos_counts.values()) / pos_pairs

        # Deterministic Complexity Score [0.0 - 10.0]
        score = (n_drugs * 0.5) + (pos_pairs * 1.5) + (conv_pairs * 2.0) + (unres_count * 0.8)
        
        if score >= 8.0 or n_drugs >= 6:
            cat = ComplexityCategory.VERY_HIGH_COMPLEXITY
        elif score >= 5.0 or (n_drugs >= 4 and pos_pairs >= 2):
            cat = ComplexityCategory.HIGH_COMPLEXITY
        elif score >= 2.0 or pos_pairs >= 1:
            cat = ComplexityCategory.MODERATE_COMPLEXITY
        else:
            cat = ComplexityCategory.LOW_COMPLEXITY

        explanation = (
            f"Prescription has {n_drugs} resolved drugs ({n_pairs} pairs), "
            f"{pos_pairs} positive evidence pairs ({conv_pairs} convergent), "
            f"with {part_count} drugs actively participating in safety signals."
        )

        return PrescriptionComplexityProfile(
            complexity_category=cat,
            unique_drugs_count=n_drugs,
            generated_pairs_count=n_pairs,
            positive_pairs_count=pos_pairs,
            convergent_pairs_count=conv_pairs,
            participating_drugs_count=part_count,
            max_single_drug_participation_ratio=round(max_part_ratio, 3),
            unresolved_inputs_count=unres_count,
            complexity_score=round(score, 2),
            explanation=explanation
        )


class DrugParticipationEngine:
    @staticmethod
    def analyze(report: PrescriptionSafetyReport) -> List[DrugParticipationProfile]:
        profiles = []
        total_pos_pairs = report.evidence_summary.pairs_with_evidence

        for d_part in report.drug_participation:
            did = d_part.internal_drug_id
            name = d_part.display_name
            tot_p = d_part.total_pairs_involved
            pos_p = d_part.evidence_supported_pairs
            conv_p = d_part.convergent_pairs

            # Count DDI & Event specific participations
            ddi_count = d_part.ddi_only_pairs + d_part.convergent_pairs
            evt_count = d_part.combination_event_pairs + d_part.convergent_pairs

            findings_ratio = (pos_p / total_pos_pairs) if total_pos_pairs > 0 else 0.0
            concentration = (pos_p / tot_p) if tot_p > 0 else 0.0

            if findings_ratio >= 0.6 and pos_p >= 2:
                cat = DrugParticipationCategory.PRIMARY_SIGNAL_PARTICIPANT
                exp = f"{name} is central to {pos_p}/{total_pos_pairs} positive prescription findings ({conv_p} convergent)."
            elif pos_p >= 2 or (pos_p == 1 and tot_p == 1):
                cat = DrugParticipationCategory.RECURRING_SIGNAL_PARTICIPANT
                exp = f"{name} participates in {pos_p} evidence-supported pair combinations."
            elif pos_p == 1:
                cat = DrugParticipationCategory.LIMITED_SIGNAL_PARTICIPANT
                exp = f"{name} is involved in 1 single evidence-supported combination."
            else:
                cat = DrugParticipationCategory.NO_DIRECT_SIGNAL_PARTICIPATION
                exp = f"{name} has no positive evidence findings in evaluated pairs."

            profiles.append(DrugParticipationProfile(
                internal_drug_id=did,
                display_name=name,
                participation_category=cat,
                total_evaluated_pairs=tot_p,
                positive_evidence_pairs=pos_p,
                convergent_evidence_pairs=conv_p,
                ddi_participation_count=ddi_count,
                event_participation_count=evt_count,
                prescription_findings_ratio=round(findings_ratio, 3),
                relative_evidence_concentration=round(concentration, 3),
                explanation=exp
            ))

        profiles.sort(key=lambda x: (x.positive_evidence_pairs, x.convergent_evidence_pairs), reverse=True)
        return profiles


class CrossPairEventConvergenceEngine:
    @staticmethod
    def analyze(report: PrescriptionSafetyReport, reasoner: Optional["PrescriptionSafetyReasoner"] = None) -> List[AdverseEventConvergenceItem]:
        event_to_pairs = defaultdict(list)
        event_to_drugs = defaultdict(set)
        
        drug_names = {d.resolved_internal_drug_id: d.display_name for d in report.resolution_summary.resolved_drugs if d.resolved_internal_drug_id}

        for p in report.pair_results:
            pair_key = f"{p['drug_a_id']}+{p['drug_b_id']}"
            da_id = p["drug_a_id"]
            db_id = p["drug_b_id"]

            if reasoner and p.get("events_present"):
                bundle = reasoner.safety_engine.retriever.retrieve_pair_evidence(da_id, db_id)
                for se in bundle.side_effect_records:
                    sename = se.side_effect_name.strip()
                    event_to_pairs[sename].append(pair_key)
                    event_to_drugs[sename].add(da_id)
                    event_to_drugs[sename].add(db_id)

        items = []
        for sename, pairs in event_to_pairs.items():
            pair_count = len(set(pairs))
            d_ids = list(event_to_drugs[sename])
            d_names = [drug_names.get(did, did) for did in d_ids]

            if pair_count >= 3:
                cat = EventConvergenceCategory.STRONG_EVENT_CONVERGENCE
                exp = f"Adverse event '{sename}' recurs across {pair_count} distinct drug pairs across {len(d_ids)} medications."
            elif pair_count == 2:
                cat = EventConvergenceCategory.MODERATE_EVENT_CONVERGENCE
                exp = f"Adverse event '{sename}' shared across 2 distinct evaluated drug pairs."
            else:
                cat = EventConvergenceCategory.ISOLATED_EVENT_SIGNAL
                exp = f"Adverse event '{sename}' observed in 1 isolated drug pair combination."

            items.append(AdverseEventConvergenceItem(
                side_effect_name=sename,
                side_effect_id=None,
                participating_pairs_count=pair_count,
                participating_pair_keys=list(set(pairs)),
                participating_drug_ids=d_ids,
                participating_drug_names=d_names,
                convergence_category=cat,
                explanation=exp
            ))

        items.sort(key=lambda x: x.participating_pairs_count, reverse=True)
        return items


class EvidencePatternEngine:
    @staticmethod
    def analyze(
        report: PrescriptionSafetyReport,
        part_profiles: List[DrugParticipationProfile],
        event_conv_items: List[AdverseEventConvergenceItem]
    ) -> List[EvidencePatternItem]:
        patterns = []
        pattern_idx = 1
        drug_names = {d.resolved_internal_drug_id: d.display_name for d in report.resolution_summary.resolved_drugs if d.resolved_internal_drug_id}

        # Pattern 1: Convergent Evidence Cluster
        conv_pairs = [p for p in report.pair_results if p.get("evidence_status") == "CONVERGENT_SAFETY_EVIDENCE"]
        if conv_pairs:
            pair_ids = [f"PAIR_{p['drug_a_id']}__{p['drug_b_id']}" for p in conv_pairs]
            d_ids = list(set([p['drug_a_id'] for p in conv_pairs] + [p['drug_b_id'] for p in conv_pairs]))
            patterns.append(EvidencePatternItem(
                pattern_id=f"PAT_{pattern_idx:03d}",
                pattern_type=PatternType.CONVERGENT_EVIDENCE_CLUSTER,
                title="Convergent Multi-Channel Evidence Cluster",
                supporting_pair_ids=pair_ids,
                supporting_drug_ids=d_ids,
                supporting_drug_names=[drug_names.get(did, did) for did in d_ids],
                evidence_counts={"convergent_pairs": len(conv_pairs)},
                rule_fired="RULE_PAT_CONVERGENT_CLUSTER",
                explanation=f"{len(conv_pairs)} pair(s) demonstrate both direct DrugBank DDI assertions and TWOSIDES combination adverse events.",
                provenance_edge_ids=[f"DDI_{p['drug_a_id']}_{p['drug_b_id']}" for p in conv_pairs]
            ))
            pattern_idx += 1

        # Pattern 2: Central Drug Signal Pattern
        primary_parts = [dp for dp in part_profiles if dp.participation_category == DrugParticipationCategory.PRIMARY_SIGNAL_PARTICIPANT]
        for pp in primary_parts:
            sup_pairs = [f"PAIR_{p['drug_a_id']}__{p['drug_b_id']}" for p in report.pair_results if (p['drug_a_id'] == pp.internal_drug_id or p['drug_b_id'] == pp.internal_drug_id) and p.get("evidence_status") != "NO_DIRECT_GRAPH_EVIDENCE"]
            patterns.append(EvidencePatternItem(
                pattern_id=f"PAT_{pattern_idx:03d}",
                pattern_type=PatternType.CENTRAL_DRUG_SIGNAL_PATTERN,
                title=f"Central Signal Hub: {pp.display_name}",
                supporting_pair_ids=sup_pairs,
                supporting_drug_ids=[pp.internal_drug_id],
                supporting_drug_names=[pp.display_name],
                evidence_counts={"participating_positive_pairs": pp.positive_evidence_pairs},
                rule_fired="RULE_PAT_CENTRAL_HUB",
                explanation=f"{pp.display_name} is the central participant in {pp.positive_evidence_pairs} positive evidence pairs.",
                provenance_edge_ids=sup_pairs
            ))
            pattern_idx += 1

        # Pattern 3: Event Convergence Pattern
        shared_events = [e for e in event_conv_items if e.participating_pairs_count >= 2]
        if shared_events:
            all_pair_keys = set()
            for se in shared_events[:5]:
                all_pair_keys.update(se.participating_pair_keys)
            patterns.append(EvidencePatternItem(
                pattern_id=f"PAT_{pattern_idx:03d}",
                pattern_type=PatternType.EVENT_CONVERGENCE_PATTERN,
                title="Cross-Pair Adverse Event Convergence",
                supporting_pair_ids=list(all_pair_keys),
                supporting_drug_ids=list(set([d for se in shared_events for d in se.participating_drug_ids])),
                supporting_drug_names=list(set([d for se in shared_events for d in se.participating_drug_names])),
                evidence_counts={"shared_adverse_events": len(shared_events)},
                rule_fired="RULE_PAT_EVENT_CONVERGENCE",
                explanation=f"{len(shared_events)} adverse-event concepts recur across multiple independent drug pair pathways.",
                provenance_edge_ids=list(all_pair_keys)
            ))
            pattern_idx += 1

        # Pattern 4: Identity Uncertainty Pattern
        if report.resolution_summary.unresolved_inputs:
            patterns.append(EvidencePatternItem(
                pattern_id=f"PAT_{pattern_idx:03d}",
                pattern_type=PatternType.IDENTITY_UNCERTAINTY_PATTERN,
                title="Medication Identity Uncertainty",
                supporting_pair_ids=[],
                supporting_drug_ids=[],
                supporting_drug_names=report.resolution_summary.unresolved_inputs,
                evidence_counts={"unresolved_inputs": len(report.resolution_summary.unresolved_inputs)},
                rule_fired="RULE_PAT_IDENTITY_UNCERTAINTY",
                explanation=f"{len(report.resolution_summary.unresolved_inputs)} medication(s) could not be resolved to knowledge graph entities.",
                provenance_edge_ids=[]
            ))
            pattern_idx += 1

        # Pattern 5: Limited Evidence Coverage Pattern
        no_ev_count = report.evidence_summary.no_direct_evidence_pairs
        if no_ev_count == report.evidence_summary.total_analyzed_pairs and report.evidence_summary.total_analyzed_pairs > 0:
            patterns.append(EvidencePatternItem(
                pattern_id=f"PAT_{pattern_idx:03d}",
                pattern_type=PatternType.LIMITED_EVIDENCE_COVERAGE,
                title="No Direct Graph Evidence Observed",
                supporting_pair_ids=[f"PAIR_{p['drug_a_id']}__{p['drug_b_id']}" for p in report.pair_results],
                supporting_drug_ids=report.resolution_summary.canonical_drug_ids,
                supporting_drug_names=[drug_names.get(did, did) for did in report.resolution_summary.canonical_drug_ids],
                evidence_counts={"no_evidence_pairs": no_ev_count},
                rule_fired="RULE_PAT_NO_DIRECT_EVIDENCE",
                explanation="None of the evaluated drug pairs contain direct assertions in DrugBank or TWOSIDES in the frozen graph.",
                provenance_edge_ids=[]
            ))
            pattern_idx += 1

        return patterns


class ReviewPrioritizationEngine:
    @staticmethod
    def analyze(
        report: PrescriptionSafetyReport,
        part_profiles: List[DrugParticipationProfile],
        event_conv_items: List[AdverseEventConvergenceItem]
    ) -> List[ReviewPriorityFinding]:
        findings = []
        drug_pos_map = {dp.internal_drug_id: dp.positive_evidence_pairs for dp in part_profiles}
        drug_names = {d.resolved_internal_drug_id: d.display_name for d in report.resolution_summary.resolved_drugs if d.resolved_internal_drug_id}

        for idx, p in enumerate(report.pair_results, 1):
            pair_id = f"PAIR_{p['drug_a_id']}__{p['drug_b_id']}"
            da_name = drug_names.get(p['drug_a_id'], p['drug_a_id'])
            db_name = drug_names.get(p['drug_b_id'], p['drug_b_id'])
            
            reasons = []
            score = 0.0

            # 1. Channel Convergence
            if p.get("evidence_status") == "CONVERGENT_SAFETY_EVIDENCE":
                score += 4.0
                reasons.append("Pair exhibits dual-channel convergence (DrugBank DDI + TWOSIDES adverse events).")
            elif p.get("evidence_status") == "DDI_EVIDENCE_ONLY":
                score += 2.5
                reasons.append("Direct DrugBank pharmacokinetic/pharmacodynamic interaction assertion exists.")
            elif p.get("evidence_status") == "COMBINATION_EVENT_EVIDENCE_ONLY":
                score += 1.5
                reasons.append("Observed TWOSIDES combination adverse events present.")
            else:
                reasons.append("No direct interaction or combination evidence found in knowledge graph.")

            # 2. Centrality / Multi-pair involvement
            if drug_pos_map.get(p['drug_a_id'], 0) >= 2 or drug_pos_map.get(p['drug_b_id'], 0) >= 2:
                score += 2.0
                reasons.append("One or both medications participate repeatedly in other prescription findings.")

            # 3. Cross-Pair Adverse Event Overlap
            pair_key = f"{p['drug_a_id']}+{p['drug_b_id']}"
            recurring_events = [e for e in event_conv_items if pair_key in e.participating_pair_keys and e.participating_pairs_count >= 2]
            if recurring_events:
                score += 1.5
                reasons.append(f"Pair shares {len(recurring_events)} recurring adverse event concepts with other pairs.")

            # 4. Score to Tier Mapping
            if score >= 6.0:
                tier = ReviewPriorityTier.IMMEDIATE_REVIEW_PRIORITY
            elif score >= 4.0:
                tier = ReviewPriorityTier.HIGH_REVIEW_PRIORITY
            elif score >= 2.5:
                tier = ReviewPriorityTier.MODERATE_REVIEW_PRIORITY
            elif score >= 1.0:
                tier = ReviewPriorityTier.ROUTINE_EVIDENCE_REVIEW
            else:
                tier = ReviewPriorityTier.LIMITED_EVIDENCE_REVIEW

            findings.append(ReviewPriorityFinding(
                finding_id=f"REV_{idx:03d}",
                pair_id=pair_id,
                drug_a_name=da_name,
                drug_b_name=db_name,
                review_priority=tier,
                review_score=round(score, 2),
                deterministic_reasons=reasons,
                evidence_status=p.get("evidence_status", "NO_DIRECT_GRAPH_EVIDENCE"),
                confidence_score=p.get("confidence_score", 0.0),
                inference_id=f"INF_{p['drug_a_id']}_{p['drug_b_id']}",
                supporting_edge_ids=[f"DDI_{p['drug_a_id']}_{p['drug_b_id']}"] if p.get("ddi_present") else []
            ))

        findings.sort(key=lambda x: x.review_score, reverse=True)
        return findings


class UncertaintyEngine:
    @staticmethod
    def analyze(report: PrescriptionSafetyReport) -> UncertaintyProfile:
        cats = []
        has_id_unc = len(report.resolution_summary.unresolved_inputs) > 0
        unres = report.resolution_summary.unresolved_inputs
        unmapped_rx = [d.original_input for d in report.resolution_summary.resolved_drugs if d.resolved_internal_drug_id and not d.rxcui]
        
        if has_id_unc:
            cats.append(UncertaintyCategory.IDENTITY_UNCERTAINTY)

        single_ch_pairs = report.evidence_summary.ddi_only_pairs + report.evidence_summary.combination_event_only_pairs
        if single_ch_pairs > 0:
            cats.append(UncertaintyCategory.SINGLE_CHANNEL_EVIDENCE_LIMITATION)

        no_ev_pairs = report.evidence_summary.no_direct_evidence_pairs
        if no_ev_pairs > 0:
            cats.append(UncertaintyCategory.GRAPH_ABSENCE_LIMITATION)

        obs_pairs = report.evidence_summary.convergent_evidence_pairs + report.evidence_summary.combination_event_only_pairs
        if obs_pairs > 0:
            cats.append(UncertaintyCategory.OBSERVATIONAL_ASSOCIATION_LIMITATION)

        if has_id_unc or no_ev_pairs > 0:
            unc_level = "MODERATE_UNCERTAINTY"
        elif single_ch_pairs > 0:
            unc_level = "LOW_TO_MODERATE_UNCERTAINTY"
        else:
            unc_level = "LOW_GRAPH_UNCERTAINTY"

        narrative = (
            f"Evaluated with {len(cats)} structured uncertainty factors. "
            f"Unresolved inputs: {len(unres)}, Unmapped RxNorm: {len(unmapped_rx)}, "
            f"Single-channel pairs: {single_ch_pairs}, No-evidence pairs: {no_ev_pairs}."
        )

        return UncertaintyProfile(
            uncertainty_categories=cats,
            has_identity_uncertainty=has_id_unc,
            unresolved_input_names=unres,
            unmapped_rxnorm_drugs=unmapped_rx,
            single_channel_only_pairs=single_ch_pairs,
            unsupported_pairs_count=no_ev_pairs,
            uncertainty_level=unc_level,
            explanation_narrative=narrative
        )


class ContextRequirementsEngine:
    @staticmethod
    def get_requirements() -> List[ClinicalContextRequirement]:
        return [
            ClinicalContextRequirement(
                context_category="Dosage & Strength",
                description="Specific dose (e.g., 100mg BID) modulates pharmacokinetic exposure and interaction magnitude.",
                why_it_matters="Drug-drug interaction risk is dose-dependent.",
                is_available_in_graph=False,
                is_evaluated_by_system=False
            ),
            ClinicalContextRequirement(
                context_category="Administration Timing",
                description="Sequential vs simultaneous administration intervals.",
                why_it_matters="Staggered dosing can mitigate chelation, absorption interference, or peak concentration overlaps.",
                is_available_in_graph=False,
                is_evaluated_by_system=False
            ),
            ClinicalContextRequirement(
                context_category="Renal & Hepatic Function",
                description="Glomerular filtration rate (eGFR) and liver enzyme function profiles.",
                why_it_matters="Organ clearance impairment amplifies systemic toxicity and interaction severity.",
                is_available_in_graph=False,
                is_evaluated_by_system=False
            ),
            ClinicalContextRequirement(
                context_category="Patient Comorbidities & Demographics",
                description="Patient age, pregnancy status, QT prolongation history, and existing conditions.",
                why_it_matters="Clinical susceptibility varies significantly across patient populations.",
                is_available_in_graph=False,
                is_evaluated_by_system=False
            )
        ]


class AdvancedExplanationEngine:
    @staticmethod
    def generate(
        report: PrescriptionSafetyReport,
        complexity: PrescriptionComplexityProfile,
        patterns: List[EvidencePatternItem],
        priorities: List[ReviewPriorityFinding],
        uncertainty: UncertaintyProfile
    ) -> AdvancedExplanationSummary:
        exec_sum = (
            f"Prescription analyzed with {complexity.complexity_category.value} complexity. "
            f"Identified {len(patterns)} evidence patterns across {complexity.positive_pairs_count} positive pairs. "
            f"Highest review priority: {priorities[0].review_priority.value if priorities else 'NONE'}."
        )

        key_find = "; ".join([f"{p.drug_a_name}+{p.drug_b_name} ({p.review_priority.value})" for p in priorities[:3]])
        pat_sum = "; ".join([p.title for p in patterns])

        guardrails = [
            "This decision-support analysis reflects structured knowledge graph evidence from DrugBank, TWOSIDES, and RxNorm.",
            "Review priority reflects graph density and evidence convergence, NOT patient-specific risk probability or clinical severity.",
            "Observational adverse event associations from TWOSIDES do not establish biological causality.",
            "Absence of direct evidence in the knowledge graph does not establish clinical safety.",
            "This platform does not replace licensed medical judgement or patient-specific pharmacokinetic evaluation."
        ]

        return AdvancedExplanationSummary(
            executive_summary=exec_sum,
            key_findings_summary=key_find or "No positive findings requiring prioritization.",
            prescription_patterns_summary=pat_sum or "No multi-pair patterns detected.",
            uncertainty_summary=uncertainty.explanation_narrative,
            scientific_guardrails=guardrails
        )
