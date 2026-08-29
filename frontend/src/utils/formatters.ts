export const formatEvidenceStatus = (status: string): string => {
  if (!status) return 'Unknown';
  return status
    .replace(/_/g, ' ')
    .toLowerCase()
    .replace(/\b[a-z]/g, (letter) => letter.toUpperCase());
};

export const getEvidenceBadgeColor = (status: string): { bg: string; text: string; border: string } => {
  switch (status) {
    case 'CONVERGENT_SAFETY_EVIDENCE':
      return { bg: '#8b5cf61a', text: '#c4b5fd', border: '#8b5cf633' };
    case 'DDI_EVIDENCE_ONLY':
      return { bg: '#3b82f61a', text: '#93c5fd', border: '#3b82f633' };
    case 'COMBINATION_EVENT_EVIDENCE_ONLY':
      return { bg: '#eab3081a', text: '#fde047', border: '#eab30833' };
    case 'NO_DIRECT_GRAPH_EVIDENCE':
    default:
      return { bg: '#64748b1a', text: '#94a3b8', border: '#64748b33' };
  }
};

export const getPriorityBadgeColor = (priority: string): { bg: string; text: string; border: string } => {
  switch (priority) {
    case 'CRITICAL_EVIDENCE_PRIORITY':
    case 'IMMEDIATE_REVIEW_PRIORITY':
      return { bg: '#ef44441a', text: '#fca5a5', border: '#ef444433' };
    case 'HIGH_EVIDENCE_PRIORITY':
    case 'HIGH_REVIEW_PRIORITY':
      return { bg: '#f973161a', text: '#fdba74', border: '#f9731633' };
    case 'MODERATE_EVIDENCE_PRIORITY':
    case 'MODERATE_REVIEW_PRIORITY':
      return { bg: '#eab3081a', text: '#fde047', border: '#eab30833' };
    case 'LIMITED_EVIDENCE_PRIORITY':
    case 'ROUTINE_EVIDENCE_REVIEW':
      return { bg: '#3b82f61a', text: '#93c5fd', border: '#3b82f633' };
    case 'NO_EVIDENCE_PRIORITY':
    case 'LIMITED_EVIDENCE_REVIEW':
    default:
      return { bg: '#64748b1a', text: '#94a3b8', border: '#64748b33' };
  }
};

export const getStructuralContributionColor = (level: string): { bg: string; text: string; border: string } => {
  switch (level) {
    case 'HIGH_STRUCTURAL_CONTRIBUTION':
    case 'HIGH_STRUCTURAL_IMPACT':
      return { bg: '#8b5cf61a', text: '#c4b5fd', border: '#8b5cf633' };
    case 'MODERATE_STRUCTURAL_CONTRIBUTION':
    case 'MODERATE_STRUCTURAL_IMPACT':
      return { bg: '#3b82f61a', text: '#93c5fd', border: '#3b82f633' };
    case 'LOW_STRUCTURAL_CONTRIBUTION':
    case 'LOW_STRUCTURAL_IMPACT':
      return { bg: '#eab3081a', text: '#fde047', border: '#eab30833' };
    case 'MINIMAL_STRUCTURAL_CONTRIBUTION':
    case 'NO_STRUCTURAL_IMPACT':
    default:
      return { bg: '#64748b1a', text: '#94a3b8', border: '#64748b33' };
  }
};

export const formatDate = (isoString: string): string => {
  try {
    return new Date(isoString).toLocaleString();
  } catch {
    return isoString;
  }
};
