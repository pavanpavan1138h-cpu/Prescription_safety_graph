import React from 'react';
import { Card } from '../common/Card';
import { EmergenceEvent } from '../../types/api';

interface EmergenceViewProps {
  emergences: EmergenceEvent[];
}

export const EmergenceView: React.FC<EmergenceViewProps> = ({ emergences }) => {
  return (
    <Card title="Evidentiary Emergence Log" subtitle="Timeline logging newly appeared drug or theme entities">
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', maxHeight: '400px', overflowY: 'auto' }}>
        
        {emergences.length === 0 ? (
          <div style={{ padding: '1.25rem', color: 'var(--text-muted)', fontStyle: 'italic', fontSize: '0.8rem', textAlign: 'center', backgroundColor: '#090b14', borderRadius: '6px', border: '1px solid #1e293b' }}>
            No emergence transitions logged. All entities remained present or were already present in baseline snapshots.
          </div>
        ) : (
          emergences.map((e, idx) => (
            <div
              key={`${e.entity_id}-${idx}`}
              style={{
                padding: '1rem',
                borderRadius: '6px',
                backgroundColor: '#0c1020',
                border: '1px solid #1e293b',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
              }}
            >
              <div>
                <span style={{ fontSize: '0.85rem', fontWeight: 700, color: '#fff' }}>
                  {e.entity_id.replace('THEME_', '')}
                </span>
                <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)', marginLeft: '0.5rem' }}>
                  ({e.entity_type})
                </span>
                <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', display: 'block', marginTop: '0.2rem' }}>
                  Emergence Point: <b style={{ color: '#60a5fa' }}>Snapshot #{e.emergence_index + 1}</b> (Post-emergence persistence: {Math.round(e.post_emergence_persistence * 100)}%)
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
                {e.classification.replace(/_/g, ' ')}
              </span>

            </div>
          ))
        )}

      </div>
    </Card>
  );
};
