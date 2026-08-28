"""
prescription_pair_generator.py

Deterministic Combination Generator for Phase 6.
Generates all unique unordered pairs for a set of canonical drug IDs.
Ensures exactly N(N-1)/2 pairs with 0 self-pairs and 0 duplicate pairs.
"""

from typing import List, Dict
from itertools import combinations
from prescription_schema import PrescriptionPair

class PrescriptionPairGenerator:
    @staticmethod
    def generate_pairs(canonical_drug_ids: List[str], drug_name_map: Dict[str, str]) -> List[PrescriptionPair]:
        """
        Generates deterministic, unique, unordered pairs for N canonical drug IDs.
        Expected pair count = N * (N - 1) / 2.
        """
        unique_ids = list(dict.fromkeys(canonical_drug_ids)) # preserve ordering and guarantee uniqueness
        n = len(unique_ids)
        if n < 2:
            return []

        pairs: List[PrescriptionPair] = []
        pair_idx = 1

        for d1, d2 in combinations(unique_ids, 2):
            name_1 = drug_name_map.get(d1, d1)
            name_2 = drug_name_map.get(d2, d2)
            
            # Deterministic canonical pair key sorted by ID
            sorted_tuple = sorted([d1, d2])
            canonical_key = f"{sorted_tuple[0]}__{sorted_tuple[1]}"

            pairs.append(PrescriptionPair(
                pair_index=pair_idx,
                drug_a_id=d1,
                drug_b_id=d2,
                drug_a_name=name_1,
                drug_b_name=name_2,
                canonical_pair_key=canonical_key
            ))
            pair_idx += 1

        return pairs
