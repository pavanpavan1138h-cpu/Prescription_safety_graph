import React from 'react';
import { ShieldAlert } from 'lucide-react';

interface ComparativeGuardrailProps {
  warningText?: string;
}

export const ComparativeGuardrail: React.FC<ComparativeGuardrailProps> = ({
  warningText = "This comparison describes differences between computational evidence states and does not determine whether one prescription is safer, better, or clinically preferable than another. It does not recommend adding, removing, discontinuing, substituting, or modifying medication therapy."
}) => {
  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      gap: '0.75rem',
      padding: '1rem 1.25rem',
      borderRadius: '6px',
      backgroundColor: '#ef44441a',
      border: '1px solid #ef444433',
      color: '#fee2e2',
      fontSize: '0.85rem',
      lineHeight: '1.4',
      margin: '0 0 1.5rem 0'
    }}>
      <ShieldAlert size={18} style={{ flexShrink: 0, color: '#ef4444' }} />
      <div>
        <strong style={{ fontWeight: 600 }}>Clinical Guardrail Notice:</strong> {warningText}
      </div>
    </div>
  );
};
