import React from 'react';
import { AlertCircle } from 'lucide-react';

interface IntelligenceGuardrailProps {
  guardrailText?: string;
}

export const IntelligenceGuardrail: React.FC<IntelligenceGuardrailProps> = ({
  guardrailText = "The synthesized clinical safety themes and cross-pair reinforcement groups represent graph evidence density and repetitions within the ingested surveillance datasets. This profile is not a clinical prediction of patient safety or a recommendation to modify, substitute, or discontinue patient drug therapies."
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
      <AlertCircle size={18} style={{ flexShrink: 0, color: '#eab308' }} />
      <div>
        <strong style={{ fontWeight: 600 }}>Clinical Intelligence Guardrail:</strong> {guardrailText}
      </div>
    </div>
  );
};
