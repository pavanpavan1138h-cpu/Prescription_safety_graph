import React from 'react';
import { AlertTriangle } from 'lucide-react';

interface ContextualGuardrailProps {
  warningText?: string;
}

export const ContextualGuardrail: React.FC<ContextualGuardrailProps> = ({
  warningText = "This analysis computationally changes the graph context for structural and evidential comparison only. It does not recommend discontinuing, removing, substituting, or modifying any medication. Changes observed between scenarios describe changes in available graph-derived evidence, not changes in actual patient risk or clinical outcome."
}) => {
  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      gap: '0.75rem',
      padding: '1rem 1.25rem',
      borderRadius: '6px',
      backgroundColor: '#f973161a',
      border: '1px solid #f9731633',
      color: '#ffedd5',
      fontSize: '0.85rem',
      lineHeight: '1.4',
      margin: '0 0 1.5rem 0'
    }}>
      <AlertTriangle size={18} style={{ flexShrink: 0, color: '#f97316' }} />
      <div>
        <strong style={{ fontWeight: 600 }}>Clinical Stability Guardrail:</strong> {warningText}
      </div>
    </div>
  );
};
