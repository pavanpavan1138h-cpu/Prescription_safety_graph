import React from 'react';
import { Card } from '../common/Card';
import { PersistenceProfile } from '../../types/api';

interface PersistenceViewProps {
  profiles: PersistenceProfile[];
}

export const PersistenceView: React.FC<PersistenceViewProps> = ({ profiles }) => {
  const getBadgeStyle = (level: string) => {
    switch (level) {
      case 'HIGHLY_PERSISTENT':
        return { bg: '#10b98115', text: '#34d399', border: '#10b98133' };
      case 'PERSISTENT':
        return { bg: '#3b82f615', text: '#60a5fa', border: '#3b82f633' };
      case 'MODERATELY_PERSISTENT':
        return { bg: '#f59e0b15', text: '#fbbf24', border: '#f59e0b33' };
      default:
        return { bg: '#ef444415', text: '#f87171', border: '#ef444433' };
    }
  };

  return (
    <Card title="Entity Persistence Profiles" subtitle="Presence ratios and longest consecutive runs over analysis history">
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', maxHeight: '400px', overflowY: 'auto' }}>
        
        {profiles.length === 0 ? (
          <div style={{ padding: '1rem', color: 'var(--text-muted)', fontStyle: 'italic', fontSize: '0.8rem' }}>
            No persistence tracks found.
          </div>
        ) : (
          profiles.map((p, idx) => {
            const b = getBadgeStyle(p.persistence_level);
            return (
              <div
                key={`${p.entity_id}-${idx}`}
                style={{
                  padding: '1rem',
                  borderRadius: '6px',
                  backgroundColor: '#0c1020',
                  border: '1px solid #1e293b',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '0.5rem'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <span style={{ fontSize: '0.9rem', fontWeight: 700, color: '#fff' }}>
                      {p.entity_id.replace('THEME_', '')}
                    </span>
                    <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)', marginLeft: '0.5rem' }}>
                      ({p.entity_type})
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
                    {p.persistence_level.replace(/_/g, ' ')}
                  </span>
                </div>

                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.7rem', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>
                    <span>Presence Ratio</span>
                    <span>{Math.round(p.presence_ratio * 100)}%</span>
                  </div>
                  <div style={{ height: '4px', borderRadius: '2px', backgroundColor: '#1e293b', overflow: 'hidden' }}>
                    <div style={{ height: '100%', width: `${p.presence_ratio * 100}%`, backgroundColor: b.text }} />
                  </div>
                </div>

                <div style={{ display: 'flex', gap: '1rem', fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                  <div>First Seen Snapshot: <b style={{ color: '#fff' }}>#{p.first_seen_index + 1}</b></div>
                  <div>Last Seen Snapshot: <b style={{ color: '#fff' }}>#{p.last_seen_index + 1}</b></div>
                  <div>Max Run: <b style={{ color: '#fff' }}>{p.longest_consecutive_run} snap</b></div>
                </div>

              </div>
            );
          })
        )}

      </div>
    </Card>
  );
};
