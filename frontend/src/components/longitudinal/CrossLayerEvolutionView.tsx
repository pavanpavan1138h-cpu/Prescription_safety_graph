import React from 'react';
import { Card } from '../common/Card';
import { CrossLayerEvolutionProfile } from '../../types/api';

interface CrossLayerEvolutionViewProps {
  crossLayer: CrossLayerEvolutionProfile;
}

export const CrossLayerEvolutionView: React.FC<CrossLayerEvolutionViewProps> = ({ crossLayer }) => {
  return (
    <Card title="Cross-Layer Evolution Alignment" subtitle="Correlates topological changes with evidentiary shifts across transition timeline">
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.2rem' }}>
        
        {/* Classification Header */}
        <div style={{
          padding: '1rem',
          borderRadius: '6px',
          backgroundColor: '#0c1020',
          border: '1px solid #1e293b',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <div>
            <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Alignment Level</span>
            <span style={{ fontSize: '0.9rem', fontWeight: 700, color: '#fff', display: 'block', marginTop: '0.2rem' }}>
              {crossLayer.classification.replace(/_/g, ' ')}
            </span>
          </div>

          <span style={{
            fontSize: '0.65rem',
            fontWeight: 700,
            padding: '0.2rem 0.5rem',
            borderRadius: '4px',
            backgroundColor: '#3b82f615',
            color: '#60a5fa',
            border: '1px solid #3b82f633'
          }}>
            {crossLayer.classification}
          </span>
        </div>

        {/* Narrative Description */}
        <div style={{ fontSize: '0.8rem', lineHeight: '1.5', color: '#cbd5e1', padding: '0.75rem 1rem', borderRadius: '4px', backgroundColor: '#090b14', border: '1px solid #1e293b' }}>
          {crossLayer.explanation}
        </div>

        {/* Transition logs alignments list */}
        <div>
          <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600, display: 'block', marginBottom: '0.5rem' }}>
            Transition Alignment Logs
          </span>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
            {crossLayer.cross_layer_transition_alignment.length === 0 ? (
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontStyle: 'italic', padding: '0.4rem' }}>
                No multi-layer transition occurrences logged.
              </div>
            ) : (
              crossLayer.cross_layer_transition_alignment.map((log, idx) => (
                <div key={idx} style={{
                  padding: '0.6rem 0.75rem',
                  borderRadius: '4px',
                  backgroundColor: '#090b14',
                  border: '1px solid #1e293b',
                  fontSize: '0.75rem',
                  color: '#93c5fd'
                }}>
                  {log}
                </div>
              ))
            )}
          </div>
        </div>

      </div>
    </Card>
  );
};
