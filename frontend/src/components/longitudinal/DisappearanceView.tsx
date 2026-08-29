import React from 'react';
import { Card } from '../common/Card';
import { DisappearanceEvent } from '../../types/api';

interface DisappearanceViewProps {
  disappearances: DisappearanceEvent[];
}

export const DisappearanceView: React.FC<DisappearanceViewProps> = ({ disappearances }) => {
  return (
    <Card title="Evidentiary Disappearance Log" subtitle="Timeline logging entities that disappeared during snapshot transitions">
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', maxHeight: '400px', overflowY: 'auto' }}>
        
        {disappearances.length === 0 ? (
          <div style={{ padding: '1.25rem', color: 'var(--text-muted)', fontStyle: 'italic', fontSize: '0.8rem', textAlign: 'center', backgroundColor: '#090b14', borderRadius: '6px', border: '1px solid #1e293b' }}>
            No disappearance transitions logged. All entities remained present.
          </div>
        ) : (
          disappearances.map((d, idx) => (
            <div
              key={`${d.entity_id}-${idx}`}
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
                  {d.entity_id.replace('THEME_', '')}
                </span>
                <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)', marginLeft: '0.5rem' }}>
                  ({d.entity_type})
                </span>
                <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', display: 'block', marginTop: '0.2rem' }}>
                  Disappearance Point: <b style={{ color: '#f87171' }}>Snapshot #{d.disappearance_index + 1}</b> (Subsequent absence ratio: {Math.round(d.post_disappearance_absence_ratio * 100)}%)
                </span>
              </div>

              <span style={{
                fontSize: '0.65rem',
                fontWeight: 700,
                padding: '0.2rem 0.5rem',
                borderRadius: '4px',
                backgroundColor: '#ef444415',
                color: '#f87171',
                border: '1px solid #ef444433'
              }}>
                {d.classification.replace(/_/g, ' ')}
              </span>

            </div>
          ))
        )}

      </div>
    </Card>
  );
};
