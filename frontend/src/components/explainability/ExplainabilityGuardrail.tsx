import React from 'react';
import { ShieldAlert } from 'lucide-react';

interface ExplainabilityGuardrailProps {
  warningText?: string;
}

export const ExplainabilityGuardrail: React.FC<ExplainabilityGuardrailProps> = ({
  warningText = "This explanation describes how the computational system derived its analytical outputs from available graph evidence. It is not a clinical recommendation and does not recommend adding, removing, discontinuing, substituting, or modifying medication therapy."
}) => {
  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      gap: '0.75rem',
      padding: '1rem 1.25rem',
      borderRadius: '6px',
      backgroundColor: '#3b82f615',
      border: '1px solid #3b82f633',
      color: '#bfdbfe',
      fontSize: '0.85rem',
      lineHeight: '1.4',
      margin: '0 0 1.5rem 0'
    }}>
      <ShieldAlert size={18} style={{ flexShrink: 0, color: '#60a5fa' }} />
      <div>
        <strong style={{ fontWeight: 600 }}>Explainability & Traceability Guardrail:</strong> {warningText}
      </div>
    </div>
  );
};
