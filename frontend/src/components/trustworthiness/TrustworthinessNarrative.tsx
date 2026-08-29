import React from 'react';
import { Card } from '../common/Card';

interface TrustworthinessNarrativeProps {
  narrative: string;
}

export const TrustworthinessNarrative: React.FC<TrustworthinessNarrativeProps> = ({ narrative }) => {
  return (
    <Card title="Computational Trust Evaluation Summary" subtitle="Executive narrative summarizing audit results">
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
