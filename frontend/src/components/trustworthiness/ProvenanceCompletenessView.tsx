import React from 'react';
import { Card } from '../common/Card';
import { ProvenanceCompletenessProfile } from '../../types/api';

interface ProvenanceCompletenessViewProps {
  provenance: ProvenanceCompletenessProfile;
}

export const ProvenanceCompletenessView: React.FC<ProvenanceCompletenessViewProps> = ({ provenance }) => {
  const covPercent = Math.round(provenance.traceability_coverage * 100);

  return (
    <Card title="Evidentiary Provenance Completeness & Depth" subtitle="Re-evaluates Phase 11 coverage statistics to verify auditability">
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.2rem' }}>
        
        {/* Coverage Header */}
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
            <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Completeness Level</span>
            <span style={{ fontSize: '0.9rem', fontWeight: 700, color: '#fff', display: 'block', marginTop: '0.2rem' }}>
              {provenance.completeness_level.replace(/_/g, ' ')}
            </span>
          </div>

          <div style={{ textAlign: 'right' }}>
            <span style={{ fontSize: '1.4rem', fontWeight: 800, color: '#60a5fa' }}>
              {covPercent}% Coverage
            </span>
          </div>
        </div>

        {/* Breakdown details */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1rem' }}>
          
          <div style={{ padding: '0.75rem', borderRadius: '6px', backgroundColor: '#090b14', border: '1px solid #1e293b' }}>
            <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.25rem' }}>Average Provenance Depth</span>
            <span style={{ fontSize: '0.95rem', fontWeight: 700, color: '#fff' }}>
              {provenance.average_provenance_depth} Layers
            </span>
          </div>

          <div style={{ padding: '0.75rem', borderRadius: '6px', backgroundColor: '#090b14', border: '1px solid #1e293b' }}>
            <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.25rem' }}>Orphaned component nodes</span>
            <span style={{ fontSize: '0.95rem', fontWeight: 700, color: provenance.orphaned_component_count > 0 ? '#f87171' : '#4ade80' }}>
              {provenance.orphaned_component_count}
            </span>
          </div>

          <div style={{ padding: '0.75rem', borderRadius: '6px', backgroundColor: '#090b14', border: '1px solid #1e293b' }}>
            <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.25rem' }}>Cross-Layer Traceability</span>
            <span style={{ fontSize: '0.8rem', fontWeight: 600, color: '#93c5fd' }}>
              {provenance.cross_layer_traceability.replace(/_/g, ' ')}
            </span>
          </div>

        </div>

      </div>
    </Card>
  );
};
