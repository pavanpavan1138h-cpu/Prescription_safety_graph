import React from 'react';
import { ShieldAlert } from 'lucide-react';

interface TrustworthinessGuardrailProps {
  warningText?: string;
}

export const TrustworthinessGuardrail: React.FC<TrustworthinessGuardrailProps> = ({
  warningText = "This evaluation measures the computational robustness, consistency, traceability, and reproducibility of the analytical system. It does not establish clinical correctness, patient safety, therapeutic superiority, or medical certainty, and it does not recommend adding, removing, discontinuing, substituting, or modifying medication therapy."
}) => {
  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      gap: '0.75rem',
      padding: '1rem 1.25rem',
      borderRadius: '6px',
      backgroundColor: '#f59e0b15',
      border: '1px solid #f59e0b33',
      color: '#fef3c7',
      fontSize: '0.85rem',
      lineHeight: '1.4',
      margin: '0 0 1.5rem 0'
    }}>
      <ShieldAlert size={18} style={{ flexShrink: 0, color: '#fbbf24' }} />
      <div>
        <strong style={{ fontWeight: 600 }}>Ethical & Safety Invariance Guardrail:</strong> {warningText}
      </div>
    </div>
  );
};
