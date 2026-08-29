import React from 'react';
import { Card } from '../common/Card';
import { PrescriptionComparativeIntelligenceProfile } from '../../types/api';
import { getStructuralContributionColor, formatEvidenceStatus } from '../../utils/formatters';

interface ComparisonOverviewProps {
  profile: PrescriptionComparativeIntelligenceProfile;
}

export const ComparisonOverview: React.FC<ComparisonOverviewProps> = ({ profile }) => {
  const badge = getStructuralContributionColor(profile.summary.global_delta_interpretation);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      
      {/* Top executive bar */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '1.5rem'
      }}>
        {/* Global Delta Interpretation */}
        <Card title="Global Delta Interpretation" subtitle="High-level classification of computational variance">
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <span style={{
              padding: '0.4rem 0.8rem',
              borderRadius: '4px',
              backgroundColor: badge.bg,
              border: `1px solid ${badge.border}`,
              color: badge.text,
              fontWeight: 700,
              fontSize: '0.95rem',
              display: 'inline-block',
              alignSelf: 'flex-start'
            }}>
              {profile.summary.global_delta_interpretation.replace(/_/g, ' ')}
            </span>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Determined by computing total reclassifications, structural shifts, and reinforcement deltas.
            </span>
          </div>
        </Card>

        {/* Preserved Characteristics */}
        <Card title="Preserved Snapshot Properties" subtitle="Network features that remained unchanged between comparisons">
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
            {profile.preserved_characteristics.length === 0 ? (
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontStyle: 'italic' }}>
                No network properties were preserved. The graph layouts are structurally distinct.
              </span>
            ) : (
              profile.preserved_characteristics.map((char, index) => (
                <span
                  key={`preserved-${index}`}
                  style={{
                    fontSize: '0.75rem',
                    fontWeight: 600,
                    backgroundColor: '#1e293b',
                    border: '1px solid var(--border-color)',
                    color: '#e2e8f0',
                    padding: '0.2rem 0.5rem',
                    borderRadius: '4px'
                  }}
                >
                  {char}
                </span>
              ))
            )}
          </div>
        </Card>
      </div>

      {/* Structured Major Changes Panel (Addition 2) */}
      <Card title="Structured Major Changes Log" subtitle="Deterministic classifications of the largest clinical and structural differences">
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {profile.major_changes.length === 0 ? (
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontStyle: 'italic', padding: '1rem 0' }}>
              No major computational differences detected.
            </div>
          ) : (
            profile.major_changes.map((mc, index) => {
              let categoryColor = '#3b82f6';
              if (mc.category === 'EVIDENCE') categoryColor = '#a855f7';
              if (mc.category === 'SIGNAL') categoryColor = '#ec4899';
              if (mc.category === 'STABILITY') categoryColor = '#f97316';

              return (
                <div
                  key={`change-${index}`}
                  style={{
                    padding: '1rem',
                    borderRadius: '6px',
                    backgroundColor: '#0c1020',
                    border: '1px solid #1e293b',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '0.4rem'
                  }}
                >
                  {/* Category and Change type */}
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <span style={{
                        fontSize: '0.7rem',
                        fontWeight: 700,
                        backgroundColor: `${categoryColor}1a`,
                        color: categoryColor,
                        padding: '0.15rem 0.4rem',
                        borderRadius: '4px'
                      }}>
                        {mc.category}
                      </span>
                      <span style={{ fontSize: '0.8rem', fontWeight: 600, color: '#fff' }}>
                        {mc.change_type.replace(/_/g, ' ')}
                      </span>
                    </div>

                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      Magnitude: <b>{Math.round(mc.magnitude * 100)}%</b>
                    </span>
                  </div>

                  {/* Description */}
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    {mc.description}
                  </div>

                  {/* Affected Entities */}
                  {mc.affected_entities.length > 0 && (
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
                      Affected: <code style={{ color: '#93c5fd', fontFamily: 'var(--font-mono)' }}>{mc.affected_entities.join(', ')}</code>
                    </div>
                  )}
                </div>
              );
            })
          )}
        </div>
      </Card>

    </div>
  );
};
