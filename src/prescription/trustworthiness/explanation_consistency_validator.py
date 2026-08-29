from typing import Any, List
from src.prescription.trustworthiness.trustworthiness_schema import ExplanationConsistencyProfile

class ExplanationConsistencyValidator:
    @staticmethod
    def validate_explanations(
        explainability_profile: Any,
        evidence_summary: Any
    ) -> ExplanationConsistencyProfile:
        """
        Validates narrative claims against actual structured results.
        """
        claims_checked = 0
        claims_supported = 0
        unsupported_claims: List[str] = []

        if not explainability_profile or not hasattr(explainability_profile, "structured_claims"):
            return ExplanationConsistencyProfile(
                claims_checked=0,
                claims_supported=0,
                unsupported_claims=[],
                consistency_ratio=1.0,
                classification="FULLY_CONSISTENT"
            )

        claims = getattr(explainability_profile, "structured_claims", []) or []
        for claim in claims:
            claims_checked += 1
            is_valid = True
            
            # Retrieve fields
            claim_id = getattr(claim, "claim_id", "")
            claim_type = getattr(claim, "claim_type", "")
            claim_text = getattr(claim, "claim_text", "")
            
            # Simple template rule checks
            if "MULTI_PAIR" in str(claim_type):
                # Expect convergent_evidence_pairs to be >= 2 if present
                if evidence_summary:
                    convergent_pairs = getattr(evidence_summary, "convergent_evidence_pairs", 0)
                    if convergent_pairs < 2:
                        is_valid = False
            elif "NO_EVIDENCED" in str(claim_type) or "GUARDRAIL" in str(claim_type):
                # Guardrails/Caveats are always supported by definition
                is_valid = True
            
            if is_valid:
                claims_supported += 1
            else:
                unsupported_claims.append(f"{claim_id}: {claim_text}")

        ratio = claims_supported / max(claims_checked, 1)
        
        if ratio == 1.0:
            classification = "FULLY_CONSISTENT"
        elif ratio >= 0.80:
            classification = "MOSTLY_CONSISTENT"
        elif ratio >= 0.50:
            classification = "PARTIALLY_INCONSISTENT"
        else:
            classification = "INCONSISTENT"

        return ExplanationConsistencyProfile(
            claims_checked=claims_checked,
            claims_supported=claims_supported,
            unsupported_claims=unsupported_claims,
            consistency_ratio=round(ratio, 3),
            classification=classification
        )
