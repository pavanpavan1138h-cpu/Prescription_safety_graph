import React from 'react';
import { Card } from '../common/Card';
import { ContributionProfile } from '../../types/api';

interface ContributorRankingProps {
  contributors: ContributionProfile[];
}

export const ContributorRanking: React.FC<ContributorRankingProps> = ({ contributors }) => {
  const getBadgeStyle = (level: string) => {
    switch (level) {
      case 'PRIMARY_CONTRIBUTOR':
        return { bg: '#ef444415', text: '#f87171', border: '#ef444433' };
      case 'MAJOR_CONTRIBUTOR':
        return { bg: '#f9731615', text: '#fdba74', border: '#f9731633' };
      case 'SUPPORTING_CONTRIBUTOR':
        return { bg: '#3b82f615', text: '#60a5fa', border: '#3b82f633' };
      case 'MINOR_CONTRIBUTOR':
        return { bg: '#a855f715', text: '#c084fc', border: '#a855f733' };
      default:
        return { bg: '#1e293b', text: '#94a3b8', border: 'transparent' };
    }
  };

  return (
    <Card title="Multi-Layer Decision Contributors" subtitle="Quantifies decision weight across pairwise reasoning, structure, and contextual stability">
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', maxHeight: '420px', overflowY: 'auto' }}>
        {contributors.length === 0 ? (
          <div style={{ padding: '1rem', color: 'var(--text-muted)', fontStyle: 'italic', fontSize: '0.8rem' }}>
            No contributor profiles available.
          </div>
        ) : (
          contributors.map((c, idx) => {
            const b = getBadgeStyle(c.contribution_level);
            return (
              <div
                key={`${c.entity_id}-${idx}`}
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
                {/* Header Row */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                    <span style={{
                      fontSize: '0.75rem',
                      fontWeight: 700,
                      color: 'var(--text-muted)',
                      fontFamily: 'var(--font-mono)'
                    }}>
                      #{idx + 1}
                    </span>
                    <span style={{ fontSize: '0.9rem', fontWeight: 600, color: '#fff' }}>
                      {c.entity_label}
                    </span>
                    <span style={{
                      fontSize: '0.65rem',
                      padding: '0.1rem 0.35rem',
                      borderRadius: '3px',
                      backgroundColor: '#1e293b',
                      color: '#94a3b8',
                      fontFamily: 'var(--font-mono)'
                    }}>
                      {c.entity_type}
                    </span>
                  </div>

                  <span style={{
                    fontSize: '0.7rem',
                    fontWeight: 700,
                    padding: '0.2rem 0.5rem',
                    borderRadius: '4px',
                    backgroundColor: b.bg,
                    color: b.text,
                    border: `1px solid ${b.border}`
                  }}>
                    {c.contribution_level.replace(/_/g, ' ')}
                  </span>
                </div>

                {/* Score and Explanation */}
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', lineHeight: '1.4' }}>
                  {c.explanation}
                </div>

                {/* Multi-Layer Metrics Grid */}
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(4, 1fr)',
                  gap: '0.5rem',
                  marginTop: '0.25rem',
                  borderTop: '1px solid #1e293b',
                  paddingTop: '0.5rem',
                  fontSize: '0.7rem',
                  color: 'var(--text-muted)'
                }}>
                  <div>
                    Direct: <b style={{ color: '#fff' }}>{Math.round(c.direct_decision_contribution * 100)}%</b>
                  </div>
                  <div>
                    Evidence: <b style={{ color: '#fff' }}>{Math.round(c.evidence_coverage * 100)}%</b>
                  </div>
                  <div>
                    Cross-Layer: <b style={{ color: '#fff' }}>{Math.round(c.cross_layer_participation * 100)}%</b>
                  </div>
                  <div>
                    Overall Score: <b style={{ color: '#60a5fa' }}>{c.overall_contribution_score.toFixed(2)}</b>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </Card>
  );
};
