import React from 'react';
import { Card } from '../common/Card';

interface LongitudinalNarrativeProps {
  narrative: string;
}

export const LongitudinalNarrative: React.FC<LongitudinalNarrativeProps> = ({ narrative }) => {
  return (
    <Card title="Longitudinal Evolution Narrative Summary" subtitle="Deterministic narrative describing computational changes over snapshots sequence">
      <div style={{
        padding: '1.25rem',
        borderRadius: '6px',
        backgroundColor: '#0c1020',
        border: '1px solid #1e293b',
        fontSize: '0.85rem',
        lineHeight: '1.6',
        color: '#e2e8f0',
        whiteSpace: 'pre-line'
      }}>
        {narrative}
      </div>
    </Card>
  );
};
