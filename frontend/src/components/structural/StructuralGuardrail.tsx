import React from 'react';
import { AlertTriangle } from 'lucide-react';

interface StructuralGuardrailProps {
  warningText?: string;
}

export const StructuralGuardrail: React.FC<StructuralGuardrailProps> = ({
  warningText = "This is a structural counterfactual analysis and is not a recommendation to discontinue, remove, substitute, or modify medication therapy."
}) => {
  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      gap: '0.75rem',
      padding: '1rem 1.25rem',
      borderRadius: '6px',
      backgroundColor: '#ca8a041a',
      border: '1px solid #ca8a0433',
      color: '#fde047',
      fontSize: '0.85rem',
      lineHeight: '1.4',
      margin: '0 0 1.5rem 0'
    }}>
      <AlertTriangle size={18} style={{ flexShrink: 0, color: '#eab308' }} />
      <div>
        <strong style={{ fontWeight: 600 }}>Clinical Guardrail Notice:</strong> {warningText}
      </div>
    </div>
  );
};
