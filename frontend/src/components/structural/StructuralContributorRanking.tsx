import React from 'react';
import { Card } from '../common/Card';
import { DrugStructuralProfile } from '../../types/api';
import { getStructuralContributionColor } from '../../utils/formatters';

interface StructuralContributorRankingProps {
  contributors: DrugStructuralProfile[];
}

export const StructuralContributorRanking: React.FC<StructuralContributorRankingProps> = ({
  contributors
}) => {
  return (
    <Card title="Structural Contributor Centrality Ranks" subtitle="Rankings of medications by their structural participation weight within the prescription network">
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {contributors.map((profile) => {
          const badgeStyle = getStructuralContributionColor(profile.structural_contribution_level);
          return (
            <div
              key={profile.drug_id}
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
              {/* Top Row: Rank, Name, Level Badge */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  <span style={{
                    fontSize: '1rem',
                    fontWeight: 700,
                    color: '#8b5cf6',
                    backgroundColor: '#8b5cf61a',
                    padding: '0.2rem 0.5rem',
                    borderRadius: '4px',
                    minWidth: '28px',
                    textAlign: 'center'
                  }}>
                    #{profile.centrality_rank}
                  </span>
                  <span style={{ fontSize: '0.95rem', fontWeight: 600, color: '#fff' }}>
                    {profile.display_name}
                  </span>
                </div>

                <span style={{
                  padding: '0.25rem 0.6rem',
                  borderRadius: '4px',
                  backgroundColor: badgeStyle.bg,
                  border: `1px solid ${badgeStyle.border}`,
                  color: badgeStyle.text,
                  fontSize: '0.75rem',
                  fontWeight: 600
                }}>
                  {profile.structural_contribution_level.replace(/_/g, ' ')}
                </span>
              </div>

              {/* Stats row */}
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))',
                gap: '0.75rem',
                fontSize: '0.8rem',
                color: 'var(--text-muted)',
                padding: '0.5rem 0',
                borderTop: '1px solid #1e293b',
                borderBottom: '1px solid #1e293b'
              }}>
                <div>
                  Evidence Degree: <b style={{ color: '#fff' }}>{profile.evidence_degree}</b>
                </div>
                <div>
                  Weighted Degree: <b style={{ color: '#fff' }}>{profile.weighted_evidence_degree}</b>
                </div>
                <div>
                  Betweenness Centrality: <b style={{ color: '#fff' }}>{profile.betweenness_centrality}</b>
                </div>
                <div>
                  Evidence Diversity: <b style={{ color: '#fff' }}>{profile.evidence_channel_diversity} / 3</b>
                </div>
              </div>

              {/* Explanation Narrative */}
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', lineHeight: '1.4' }}>
                {profile.explanation}
              </div>
            </div>
          );
        })}
      </div>
    </Card>
  );
};
