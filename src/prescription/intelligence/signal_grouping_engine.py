from typing import Dict, List, Set, Optional, Any, Tuple
from collections import defaultdict
from src.prescription.schemas import PrescriptionSafetyReport
from src.prescription.intelligence.intelligence_schema import EvidenceTheme, CrossPairSignalGroup, EvidenceThemeType, ReinforcementLevel
from src.prescription.intelligence.evidence_theme_mapper import EvidenceThemeMapper

class SignalGroupingEngine:
    @staticmethod
    def analyze(report: PrescriptionSafetyReport, reasoner: Any) -> Tuple[List[EvidenceTheme], List[CrossPairSignalGroup]]:
        # Map to accumulate raw data per theme
        # theme_str -> dict of fields
        theme_data = defaultdict(lambda: {
            "mapped_events": set(),
            "supporting_pairs": set(),
            "participating_drugs": set(),
            "supporting_evidence_count": 0,
            "convergent_pair_count": 0,
            "source_channels": set()
        })

        # Process each pair
        for p in report.pair_results:
            da_id = p["drug_a_id"]
            db_id = p["drug_b_id"]
            status = p.get("evidence_status")
            pair_key = p.get("canonical_pair_key", f"PAIR_{da_id}__{db_id}")
            is_conv = (status == "CONVERGENT_SAFETY_EVIDENCE")

            # Check if events are present
            if p.get("events_present") and reasoner:
                try:
                    bundle = reasoner.safety_engine.retriever.retrieve_pair_evidence(da_id, db_id)
                    for se in bundle.side_effect_records:
                        se_name = se.side_effect_name.strip()
                        theme_type = EvidenceThemeMapper.map_event_to_theme(se_name)
                        t_str = theme_type.value

                        # Update theme accumulators
                        t_acc = theme_data[t_str]
                        t_acc["mapped_events"].add(se_name)
                        t_acc["supporting_pairs"].add(pair_key)
                        t_acc["participating_drugs"].add(da_id)
                        t_acc["participating_drugs"].add(db_id)
                        t_acc["supporting_evidence_count"] += 1
                        t_acc["source_channels"].add("twosides")
                        if is_conv:
                            t_acc["convergent_pair_count"] += 1
                except Exception as e:
                    print(f"Error retrieving pair evidence for {da_id} & {db_id}: {e}")

            # Also check if DDI is present, which adds channels but not side effects
            if p.get("ddi_present"):
                # DDI is mapped to theme if we have combination side effects mapping,
                # but if we just want to know channel, we can check if that pair exists in any theme.
                # Since DDI is a separate channel, if a pair has both, the channel list will have 'drugbank' + 'twosides'.
                pass

        # Convert accumulated data to EvidenceTheme list
        themes: List[EvidenceTheme] = []
        signal_groups: List[CrossPairSignalGroup] = []

        theme_index = 1
        group_index = 1

        # We want to iterate through all EvidenceThemeType values to ensure clean results,
        # but only instantiate themes that have supporting evidence.
        for t_type in EvidenceThemeType:
            t_str = t_type.value
            if t_str in theme_data:
                t_acc = theme_data[t_str]
                
                # Check for DDI channel addition
                source_channels_list = list(t_acc["source_channels"])
                # For each supporting pair, check if DDI was present to add 'drugbank'
                for p_key in t_acc["supporting_pairs"]:
                    # Find p in report.pair_results
                    match_p = next((x for x in report.pair_results if x.get("canonical_pair_key") == p_key or f"PAIR_{x['drug_a_id']}__{x['drug_b_id']}" == p_key), None)
                    if match_p and match_p.get("ddi_present"):
                        if "drugbank" not in source_channels_list:
                            source_channels_list.append("drugbank")

                theme_obj = EvidenceTheme(
                    theme_id=f"THEME_{theme_index:03d}",
                    theme_name=t_str,
                    description=EvidenceThemeMapper.get_description_for_theme(t_type),
                    mapped_events=sorted(list(t_acc["mapped_events"])),
                    supporting_pairs=sorted(list(t_acc["supporting_pairs"])),
                    participating_drugs=sorted(list(t_acc["participating_drugs"])),
                    supporting_evidence_count=t_acc["supporting_evidence_count"],
                    convergent_pair_count=t_acc["convergent_pair_count"],
                    source_channels=sorted(source_channels_list)
                )
                themes.append(theme_obj)
                theme_index += 1

                # Generate CrossPairSignalGroup for mapped themes (excluding UNKNOWN)
                if t_type != EvidenceThemeType.UNKNOWN_OR_UNMAPPED_THEME:
                    group_obj = CrossPairSignalGroup(
                        group_id=f"SG_{group_index:03d}",
                        theme_id=theme_obj.theme_id,
                        supporting_pairs=theme_obj.supporting_pairs,
                        participating_drugs=theme_obj.participating_drugs,
                        supporting_events=theme_obj.mapped_events,
                        channel_distribution=theme_obj.source_channels,
                        convergent_pair_count=theme_obj.convergent_pair_count,
                        reinforcement_score=0.0, # Will be set by reinforcement engine
                        reinforcement_level=ReinforcementLevel.LIMITED_REINFORCEMENT
                    )
                    signal_groups.append(group_obj)
                    group_index += 1

        return themes, signal_groups
