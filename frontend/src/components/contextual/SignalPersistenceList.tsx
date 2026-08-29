import React from 'react';
import { Card } from '../common/Card';
import { SignalPersistence } from '../../types/api';
import { getStructuralContributionColor, formatEvidenceStatus } from '../../utils/formatters';

interface SignalPersistenceListProps {
  persistences: SignalPersistence[];
}

export const SignalPersistenceList: React.FC<SignalPersistenceListProps> = ({
  persistences
}) => {
  return (
    <Card title="Clinical Signal Theme Persistence" subtitle="Identifies which safety themes remain persistent across variant contexts vs context-sensitive triggers">
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
        {persistences.length === 0 ? (
          <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontStyle: 'italic', padding: '1rem 0' }}>
            No persistent safety signal themes detected.
          </div>
        ) : (
          persistences.map((sp) => {
            const badge = getStructuralContributionColor(sp.persistence_level);
            return (
              <div
                key={sp.theme_name}
                style={{
                  padding: '1rem',
                  borderRadius: '6px',
                  backgroundColor: '#0f1222',
                  border: '1px solid var(--border-color)',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  flexWrap: 'wrap',
                  gap: '0.5rem'
                }}
              >
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.2rem' }}>
                  <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#fff' }}>
                    {formatEvidenceStatus(sp.theme_name)}
                  </span>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    Persistence score: <b>{Math.round(sp.persistence_score * 100)}%</b> of scenarios
                  </span>
                </div>

                <span style={{
                  padding: '0.2rem 0.5rem',
                  borderRadius: '4px',
                  backgroundColor: badge.bg,
                  border: `1px solid ${badge.border}`,
                  color: badge.text,
                  fontSize: '0.7rem',
                  fontWeight: 600
                }}>
                  {sp.persistence_level.replace(/_/g, ' ')}
                </span>
              </div>
            );
          })
        )}
      </div>
    </Card>
  );
};
