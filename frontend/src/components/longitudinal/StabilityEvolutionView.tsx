import React from 'react';
import { Card } from '../common/Card';
import { StabilityEvolutionProfile } from '../../types/api';
import { ArrowRight } from 'lucide-react';

interface StabilityEvolutionViewProps {
  stability: StabilityEvolutionProfile;
}

export const StabilityEvolutionView: React.FC<StabilityEvolutionViewProps> = ({ stability }) => {
  return (
    <Card title="Contextual Stability Evolution" subtitle="Tracks sensitivity deviations across available prescription snapshots sequence">
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.2rem' }}>
        
        {/* Header summary */}
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
            <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Stability Trend</span>
            <span style={{ fontSize: '1rem', fontWeight: 700, color: '#fff', display: 'block', marginTop: '0.2rem' }}>
              {stability.classification.replace(/_/g, ' ')}
            </span>
          </div>

          <div style={{ textAlign: 'right' }}>
            <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', display: 'block' }}>State Changes</span>
            <span style={{ fontSize: '1.2rem', fontWeight: 800, color: '#fbbf24' }}>
              {stability.transition_count}
            </span>
          </div>
        </div>

        {/* State sequence */}
        <div>
          <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600, display: 'block', marginBottom: '0.5rem' }}>
            Stability State Sequence
          </span>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', overflowX: 'auto', padding: '0.25rem 0' }}>
            {stability.stability_sequence.map((state, idx) => (
              <React.Fragment key={idx}>
                <div style={{
                  padding: '0.5rem 0.75rem',
                  borderRadius: '4px',
                  backgroundColor: '#0c1020',
                  border: '1px solid #1e293b',
                  fontSize: '0.75rem',
                  color: state.includes('CONTEXT_SENSITIVE') ? '#fbbf24' : '#10b981',
                  fontWeight: 650,
                  whiteSpace: 'nowrap'
                }}>
                  {state.replace(/_/g, ' ')}
                </div>
                {idx < stability.stability_sequence.length - 1 && (
                  <ArrowRight size={14} style={{ color: 'var(--text-muted)', flexShrink: 0 }} />
                )}
              </React.Fragment>
            ))}
          </div>
        </div>

        {/* Sensitivity scores */}
        <div>
          <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600, display: 'block', marginBottom: '0.5rem' }}>
            Sensitivity Index Progression
          </span>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
            {stability.sensitivity_sequence.map((sens, idx) => (
              <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', padding: '0.4rem 0.6rem', backgroundColor: '#090b14', borderRadius: '4px' }}>
                <span style={{ color: 'var(--text-muted)' }}>Snapshot #{idx + 1} Sensitivity</span>
                <span style={{ color: '#fff', fontWeight: 600 }}>{Math.round(sens * 100)}%</span>
              </div>
            ))}
          </div>
        </div>

      </div>
    </Card>
  );
};
