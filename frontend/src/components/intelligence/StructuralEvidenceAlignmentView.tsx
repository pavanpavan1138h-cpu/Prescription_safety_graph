import React from 'react';
import { Card } from '../common/Card';
import { StructuralEvidenceAlignment } from '../../types/api';
import { getStructuralContributionColor, formatEvidenceStatus } from '../../utils/formatters';

interface StructuralEvidenceAlignmentViewProps {
  alignment: StructuralEvidenceAlignment;
}

export const StructuralEvidenceAlignmentView: React.FC<StructuralEvidenceAlignmentViewProps> = ({
  alignment
}) => {
  return (
    <Card title="Structural Hub & Evidence Alignment" subtitle="Cross-references network centrality rankings (Phase 8) against direct evidence participation ranks (Phase 9)">
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
        {/* Global Alignment Row */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          <div>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.25rem' }}>Global Correlation Category</span>
            <span style={{
              padding: '0.4rem 0.8rem',
              borderRadius: '4px',
              backgroundColor: getStructuralContributionColor(alignment.alignment_level).bg,
              border: `1px solid ${getStructuralContributionColor(alignment.alignment_level).border}`,
              color: getStructuralContributionColor(alignment.alignment_level).text,
              fontWeight: 600,
              fontSize: '0.9rem',
              display: 'inline-block'
            }}>
              {alignment.alignment_level.replace(/_/g, ' ')}
            </span>
          </div>

          <p style={{ margin: 0, fontSize: '0.8rem', color: 'var(--text-muted)', lineHeight: '1.4' }}>
            {alignment.explanation}
          </p>
        </div>

        {/* Tabular ranking list */}
        <div style={{ overflowX: 'auto', borderTop: '1px solid #1e293b', paddingTop: '1rem' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-color)', textAlign: 'left', color: '#fff' }}>
                <th style={{ padding: '0.5rem 0.25rem' }}>Medication</th>
                <th style={{ padding: '0.5rem 0.25rem', textAlign: 'center' }}>Centrality Rank</th>
                <th style={{ padding: '0.5rem 0.25rem', textAlign: 'center' }}>Evidence Rank</th>
                <th style={{ padding: '0.5rem 0.25rem', textAlign: 'center' }}>Theme Rank</th>
                <th style={{ padding: '0.5rem 0.25rem', textAlign: 'center' }}>Conv Rank</th>
                <th style={{ padding: '0.5rem 0.25rem', textAlign: 'center' }}>Alignment Score</th>
              </tr>
            </thead>
            <tbody>
              {alignment.drug_alignment_profiles.map((profile) => (
                <tr key={profile.drug_id} style={{ borderBottom: '1px solid #1e293b' }}>
                  <td style={{ padding: '0.75rem 0.25rem', fontWeight: 600, color: '#fff' }}>
                    {profile.display_name}
                  </td>
                  <td style={{ padding: '0.75rem 0.25rem', textAlign: 'center', fontWeight: 600, color: '#8b5cf6' }}>
                    #{profile.structural_rank}
                  </td>
                  <td style={{ padding: '0.75rem 0.25rem', textAlign: 'center' }}>
                    #{profile.evidence_participation_rank}
                  </td>
                  <td style={{ padding: '0.75rem 0.25rem', textAlign: 'center' }}>
                    #{profile.theme_participation_rank}
                  </td>
                  <td style={{ padding: '0.75rem 0.25rem', textAlign: 'center' }}>
                    #{profile.convergent_evidence_rank}
                  </td>
                  <td style={{ padding: '0.75rem 0.25rem', textAlign: 'center', fontWeight: 600, color: getStructuralContributionColor(profile.alignment_level).text }}>
                    {profile.alignment_score}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </Card>
  );
};
