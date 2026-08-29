import React from 'react';
import { Card } from '../common/Card';
import { CrossLayerConsistencyProfile } from '../../types/api';

interface CrossLayerConsistencyViewProps {
  consistency: CrossLayerConsistencyProfile;
}

export const CrossLayerConsistencyView: React.FC<CrossLayerConsistencyViewProps> = ({ consistency }) => {
  const getBadgeStyle = (level: string) => {
    switch (level) {
      case 'CONSISTENT_CONVERGENCE':
        return { bg: '#3b82f615', text: '#60a5fa', border: '#3b82f633' };
      case 'MULTI_DIMENSIONAL_ANALYTICAL_DISTRIBUTION':
        return { bg: '#10b98115', text: '#34d399', border: '#10b98133' };
      default:
        return { bg: '#f59e0b15', text: '#fbbf24', border: '#f59e0b33' };
    }
  };

  const b = getBadgeStyle(consistency.consistency_level);

  return (
    <Card title="Cross-Layer Analytical Consistency" subtitle="Verifies matching entities across structural, evidential, and explanation layers">
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.2rem' }}>
        
        {/* Consistency Classification Info */}
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
            <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Consistency Level</span>
            <span style={{ fontSize: '0.9rem', fontWeight: 700, color: '#fff', display: 'block', marginTop: '0.2rem' }}>
              {consistency.consistency_level.replace(/_/g, ' ')}
            </span>
          </div>

          <span style={{
            fontSize: '0.65rem',
            fontWeight: 700,
            padding: '0.2rem 0.5rem',
            borderRadius: '4px',
            backgroundColor: b.bg,
            color: b.text,
            border: `1px solid ${b.border}`
          }}>
            {consistency.consistency_level}
          </span>
        </div>

        {/* Narrative Explanation */}
        <div style={{ fontSize: '0.8rem', lineHeight: '1.5', color: '#cbd5e1', padding: '0.75rem 1rem', borderRadius: '4px', backgroundColor: '#090b14', border: '1px solid #1e293b' }}>
          {consistency.explanation}
        </div>

        {/* Breakdown of layers */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1rem', marginTop: '0.25rem' }}>
          
          <div style={{ padding: '0.75rem', borderRadius: '6px', backgroundColor: '#0c1020', border: '1px solid #1e293b' }}>
            <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.25rem' }}>Phase 8 Structural hubs</span>
            <span style={{ fontSize: '0.8rem', fontWeight: 600, color: '#fff' }}>
              {consistency.structural_dominant_participants.join(', ') || 'None'}
            </span>
          </div>

          <div style={{ padding: '0.75rem', borderRadius: '6px', backgroundColor: '#0c1020', border: '1px solid #1e293b' }}>
            <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.25rem' }}>Phase 9 Evidence hubs</span>
            <span style={{ fontSize: '0.8rem', fontWeight: 600, color: '#fff' }}>
              {consistency.evidence_dominant_participants.join(', ') || 'None'}
            </span>
          </div>

          <div style={{ padding: '0.75rem', borderRadius: '6px', backgroundColor: '#0c1020', border: '1px solid #1e293b' }}>
            <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.25rem' }}>Phase 10 Dependency hubs</span>
            <span style={{ fontSize: '0.8rem', fontWeight: 600, color: '#fff' }}>
              {consistency.dependency_dominant_participants.join(', ') || 'None'}
            </span>
          </div>

          <div style={{ padding: '0.75rem', borderRadius: '6px', backgroundColor: '#0c1020', border: '1px solid #1e293b' }}>
            <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.25rem' }}>Phase 11 Primary contributors</span>
            <span style={{ fontSize: '0.8rem', fontWeight: 600, color: '#fff' }}>
              {consistency.primary_contributors.join(', ') || 'None'}
            </span>
          </div>

        </div>

      </div>
    </Card>
  );
};
