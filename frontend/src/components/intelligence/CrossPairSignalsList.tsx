import React from 'react';
import { Card } from '../common/Card';
import { CrossPairSignalGroup, EvidenceTheme } from '../../types/api';
import { getStructuralContributionColor, formatEvidenceStatus } from '../../utils/formatters';

interface CrossPairSignalsListProps {
  signals: CrossPairSignalGroup[];
  themes: EvidenceTheme[];
}

export const CrossPairSignalsList: React.FC<CrossPairSignalsListProps> = ({
  signals,
  themes
}) => {
  const getThemeName = (themeId: string): string => {
    const t = themes.find((x) => x.theme_id === themeId);
    return t ? formatEvidenceStatus(t.theme_name) : themeId;
  };

  return (
    <Card title="Cross-Pair Signal Convergence & Reinforcement" subtitle="Recurring multi-pair combinations reinforcing the same standardized adverse-event mapping themes">
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {signals.length === 0 ? (
          <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontStyle: 'italic', padding: '1rem 0' }}>
            No convergent cross-pair safety signal groups identified.
          </div>
        ) : (
          signals.map((group) => {
            const badge = getStructuralContributionColor(group.reinforcement_level);
            return (
              <div
                key={group.group_id}
                style={{
                  padding: '1.25rem',
                  borderRadius: '6px',
                  backgroundColor: '#0f1222',
                  border: '1px solid var(--border-color)',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '0.75rem'
                }}
              >
                {/* Header row */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <span style={{
                      fontSize: '0.85rem',
                      fontWeight: 700,
                      color: '#8b5cf6',
                      backgroundColor: '#8b5cf61a',
                      padding: '0.15rem 0.4rem',
                      borderRadius: '4px'
                    }}>
                      {group.group_id}
                    </span>
                    <span style={{ fontSize: '0.9rem', fontWeight: 600, color: '#fff' }}>
                      {getThemeName(group.theme_id)}
                    </span>
                  </div>

                  <span style={{
                    padding: '0.25rem 0.6rem',
                    borderRadius: '4px',
                    backgroundColor: badge.bg,
                    border: `1px solid ${badge.border}`,
                    color: badge.text,
                    fontSize: '0.75rem',
                    fontWeight: 600
                  }}>
                    {group.reinforcement_level.replace(/_/g, ' ')}
                  </span>
                </div>

                {/* Score stats */}
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))',
                  gap: '0.75rem',
                  fontSize: '0.8rem',
                  color: 'var(--text-muted)',
                  borderTop: '1px solid #1e293b',
                  borderBottom: '1px solid #1e293b',
                  padding: '0.4rem 0'
                }}>
                  <div>
                    Reinforcement Score: <b style={{ color: '#fff' }}>{group.reinforcement_score} / 1.0</b>
                  </div>
                  <div>
                    Supporting Pairs: <b style={{ color: '#fff' }}>{group.supporting_pairs.length}</b>
                  </div>
                  <div>
                    Convergent Pairs: <b style={{ color: '#fff' }}>{group.convergent_pair_count}</b>
                  </div>
                  <div>
                    Channels: <b style={{ color: '#fff' }}>{group.channel_distribution.join(' + ')}</b>
                  </div>
                </div>

                {/* Pairs list detail */}
                <div style={{ fontSize: '0.775rem', color: 'var(--text-muted)', lineHeight: '1.4' }}>
                  Supporting combinations: <b style={{ color: '#fff' }}>{group.supporting_pairs.join(', ')}</b>
                </div>

                {/* Participating drugs */}
                <div style={{ fontSize: '0.775rem', color: 'var(--text-muted)', lineHeight: '1.4' }}>
                  Participating medications: <b style={{ color: '#fff' }}>{group.participating_drugs.join(', ')}</b>
                </div>
              </div>
            );
          })
        )}
      </div>
    </Card>
  );
};
