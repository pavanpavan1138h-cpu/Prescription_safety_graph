"""
src/prescription/structural/prescription_structural_analyzer.py

Orchestrates structural analysis, clustering, topologies, drug profiles, and counterfactuals.
"""

from datetime import datetime
from src.prescription.structural.prescription_network_schema import PrescriptionStructuralAnalysis, NetworkSummary
from src.prescription.structural.prescription_network_builder import PrescriptionNetworkBuilder
from src.prescription.structural.evidence_cluster_engine import EvidenceClusterEngine
from src.prescription.structural.topology_classifier import TopologyClassifier
from src.prescription.structural.drug_participation_analyzer import DrugParticipationAnalyzer
from src.prescription.structural.counterfactual_engine import CounterfactualEngine
from src.prescription.structural.structural_interpretation_engine import StructuralInterpretationEngine
from src.prescription.structural.structural_metrics import calculate_density
from src.prescription.schemas import PrescriptionSafetyReport

class PrescriptionStructuralAnalyzer:
    @staticmethod
    def analyze(report: PrescriptionSafetyReport) -> PrescriptionStructuralAnalysis:
        """
        Orchestrates the entire Phase 8 network structural safety analysis pipeline.
        Consumes Phase 6 safety report outputs.
        """
        # 1. Build the network object
        network = PrescriptionNetworkBuilder.build_network(report)
        
        # 2. Detect evidence clusters and isolated components
        clusters = EvidenceClusterEngine.detect_clusters(network)
        
        # 3. Classify network topologies
        topology = TopologyClassifier.classify(network, clusters)
        
        # 4. Generate drug participation and centrality profiles
        profiles = DrugParticipationAnalyzer.analyze(network, clusters)
        
        # 5. Run computational exclusions (counterfactual analysis)
        counterfactuals = CounterfactualEngine.run_analysis(network, clusters)
        
        # 6. Build the safe clinical structural interpretation narrative
        interpretation = StructuralInterpretationEngine.generate(
            network, topology, clusters, profiles, counterfactuals
        )
        
        # 7. Compile network-wide summary statistics
        total_drugs = len(network.nodes)
        active_clusters = [c for c in clusters if not c.is_isolated]
        isolated_drugs = [c for c in clusters if c.is_isolated]
        total_possible = (total_drugs * (total_drugs - 1)) // 2 if total_drugs > 1 else 0
        
        conv_count = sum(1 for e in network.edges.values() if e.evidence_status == "CONVERGENT_SAFETY_EVIDENCE")
        ddi_count = sum(1 for e in network.edges.values() if e.evidence_status == "DDI_EVIDENCE_ONLY")
        event_count = sum(1 for e in network.edges.values() if e.evidence_status == "COMBINATION_EVENT_EVIDENCE_ONLY")
        
        largest_size = len(active_clusters[0].drug_ids) if active_clusters else 0
        density = calculate_density(total_drugs, len(network.edges))
        
        summary = NetworkSummary(
            total_prescription_drugs=total_drugs,
            evidence_connected_drugs=total_drugs - len(isolated_drugs),
            structurally_isolated_drugs=len(isolated_drugs),
            total_possible_pairs=total_possible,
            evidence_supported_pairs=len(network.edges),
            network_density=round(density, 3),
            connected_cluster_count=len(active_clusters),
            largest_cluster_size=largest_size,
            convergent_edge_count=conv_count,
            ddi_only_edge_count=ddi_count,
            combination_event_edge_count=event_count
        )
        
        return PrescriptionStructuralAnalysis(
            analysis_id=report.prescription_id,
            generated_at=datetime.now().isoformat(),
            network_summary=summary,
            topology=topology,
            clusters=clusters,
            drug_structural_profiles=profiles,
            ranked_structural_contributors=profiles,
            counterfactual_results=counterfactuals,
            original_network=network,
            structural_interpretation=interpretation
        )
