import React from 'react';
import { ShieldAlert } from 'lucide-react';

interface LongitudinalGuardrailProps {
  warningText?: string;
}

export const LongitudinalGuardrail: React.FC<LongitudinalGuardrailProps> = ({
  warningText = "This longitudinal evaluation describes how the computational analytical profile changes across available prescription snapshots. It does not establish clinical progression, patient improvement or deterioration, medication efficacy, therapeutic superiority, patient safety, or medical correctness, and it does not recommend adding, removing, discontinuing, substituting, or modifying medication therapy."
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
        <strong style={{ fontWeight: 600 }}>Safety Invariance Guardrail:</strong> {warningText}
      </div>
    </div>
  );
};
