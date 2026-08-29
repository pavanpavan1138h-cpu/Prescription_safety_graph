import React from 'react';
import { Card } from '../common/Card';
import { StructuralEvolutionProfile } from '../../types/api';
import { ArrowRight } from 'lucide-react';

interface StructuralEvolutionViewProps {
  structure: StructuralEvolutionProfile;
}

export const StructuralEvolutionView: React.FC<StructuralEvolutionViewProps> = ({ structure }) => {
  return (
    <Card title="Structural Topology Evolution Trace" subtitle="Tracks network configuration shifts over analysis snapshots sequence">
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.2rem' }}>
        
        {/* Topology Classification Header */}
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
            <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Structural Classification</span>
            <span style={{ fontSize: '1rem', fontWeight: 700, color: '#fff', display: 'block', marginTop: '0.2rem' }}>
              {structure.classification.replace(/_/g, ' ')}
            </span>
          </div>

          <div style={{ textAlign: 'right' }}>
            <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', display: 'block' }}>Topology Changes</span>
            <span style={{ fontSize: '1.2rem', fontWeight: 800, color: '#3b82f6' }}>
              {structure.topology_transition_count}
            </span>
          </div>
        </div>

        {/* Topology Sequence */}
        <div>
          <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600, display: 'block', marginBottom: '0.5rem' }}>
            Topology Sequence
          </span>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', overflowX: 'auto', padding: '0.25rem 0' }}>
            {structure.topology_sequence.map((topo, idx) => (
              <React.Fragment key={idx}>
                <div style={{
                  padding: '0.5rem 0.75rem',
                  borderRadius: '4px',
                  backgroundColor: '#0c1020',
                  border: '1px solid #1e293b',
                  fontSize: '0.75rem',
                  color: '#fff',
                  fontWeight: 600,
                  whiteSpace: 'nowrap'
                }}>
                  {topo.replace(/_/g, ' ')}
                </div>
                {idx < structure.topology_sequence.length - 1 && (
                  <ArrowRight size={14} style={{ color: 'var(--text-muted)', flexShrink: 0 }} />
                )}
              </React.Fragment>
            ))}
          </div>
        </div>

        {/* Central Participants Sequence */}
        <div>
          <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600, display: 'block', marginBottom: '0.5rem' }}>
            Central Participants History
          </span>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
            {structure.central_participant_sequence.map((participants, idx) => (
              <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', padding: '0.4rem 0.6rem', backgroundColor: '#090b14', borderRadius: '4px' }}>
                <span style={{ color: 'var(--text-muted)' }}>Snapshot #{idx + 1} Hubs</span>
                <span style={{ color: '#fff', fontWeight: 600 }}>{participants.join(', ') || 'None'}</span>
              </div>
            ))}
          </div>
        </div>

      </div>
    </Card>
  );
};
