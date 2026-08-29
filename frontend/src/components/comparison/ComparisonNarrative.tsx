import React from 'react';
import { Card } from '../common/Card';

interface ComparisonNarrativeProps {
  narrative: string;
}

export const ComparisonNarrative: React.FC<ComparisonNarrativeProps> = ({ narrative }) => {
  return (
    <Card title="Executive Comparative Summary" subtitle="Template-assembled narrative explanation of computational deltas">
      <pre style={{
        whiteSpace: 'pre-wrap',
        fontFamily: 'var(--font-mono)',
        fontSize: '0.85rem',
        lineHeight: '1.6',
        color: '#e2e8f0',
        backgroundColor: '#0f1222',
        padding: '1.5rem',
        borderRadius: '6px',
        border: '1px solid var(--border-color)',
        margin: 0
      }}>
        {narrative}
      </pre>
    </Card>
  );
};
