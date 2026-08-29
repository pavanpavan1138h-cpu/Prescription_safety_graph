from typing import List, Callable, Any
from src.prescription.trustworthiness.trustworthiness_schema import (
    InputPerturbationResult,
    InputPerturbationType,
    PerturbationResultType
)
from src.prescription.trustworthiness.reproducibility_engine import ReproducibilityEngine

class PerturbationEngine:
    @staticmethod
    def evaluate_perturbations(
        baseline_meds: List[str],
        baseline_report: Any,
        analyze_func: Callable[[List[str]], Any]
    ) -> List[InputPerturbationResult]:
        """
        Runs medication name variations (permutations, casing, whitespace, duplicates)
        through the normalization and analysis pipeline to verify invariance of the output.
        """
        results: List[InputPerturbationResult] = []
        baseline_hash = ReproducibilityEngine.generate_canonical_hash(baseline_report)

        # Helper to generate results
        def run_test(pert_type: InputPerturbationType, pert_id: str, meds: List[str]):
            try:
                perturbed_report = analyze_func(meds)
                perturbed_hash = ReproducibilityEngine.generate_canonical_hash(perturbed_report)
                
                if perturbed_hash == baseline_hash:
                    classification = PerturbationResultType.INVARIANT
                    changed = []
                    invariant = ["canonical_signature"]
                else:
                    classification = PerturbationResultType.MINOR_OUTPUT_VARIATION
                    changed = ["canonical_signature"]
                    invariant = []
                
                results.append(InputPerturbationResult(
                    perturbation_id=pert_id,
                    perturbation_type=pert_type,
                    baseline_signature=baseline_hash,
                    perturbed_signature=perturbed_hash,
                    invariant_components=invariant,
                    changed_components=changed,
                    classification=classification
                ))
            except Exception:
                results.append(InputPerturbationResult(
                    perturbation_id=pert_id,
                    perturbation_type=pert_type,
                    baseline_signature=baseline_hash,
                    perturbed_signature="FAILED",
                    invariant_components=[],
                    changed_components=["pipeline_failure"],
                    classification=PerturbationResultType.FAILED_NORMALIZATION
                ))

        # Test Case 1: Medication Order Permutation
        if len(baseline_meds) > 1:
            run_test(
                InputPerturbationType.MEDICATION_ORDER_PERMUTATION,
                "PERT_ORDER_001",
                list(reversed(baseline_meds))
            )

        # Test Case 2: Case Normalization Variation
        upper_meds = [m.upper() for m in baseline_meds]
        run_test(
            InputPerturbationType.CASE_NORMALIZATION_VARIATION,
            "PERT_CASE_001",
            upper_meds
        )

        # Test Case 3: Whitespace Variation
        spaced_meds = [f"  {m}  " for m in baseline_meds]
        run_test(
            InputPerturbationType.WHITESPACE_VARIATION,
            "PERT_SPACE_001",
            spaced_meds
        )

        # Test Case 4: Duplicate Input Variation
        if len(baseline_meds) > 0:
            dup_meds = baseline_meds + [baseline_meds[0]]
            run_test(
                InputPerturbationType.DUPLICATE_INPUT_VARIATION,
                "PERT_DUP_001",
                dup_meds
            )

        return results
