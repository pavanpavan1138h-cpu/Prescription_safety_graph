import React from 'react';
import { Card } from '../common/Card';
import { ScenarioProfile } from '../../types/api';
import { formatEvidenceStatus, getEvidenceBadgeColor } from '../../utils/formatters';

interface ScenarioProfilesListProps {
  scenarios: ScenarioProfile[];
}

export const ScenarioProfilesList: React.FC<ScenarioProfilesListProps> = ({ scenarios }) => {
  return (
    <Card title="Evaluated Contextual Scenarios" subtitle="Overview of network structural changes under controlled medication exclusions">
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', maxHeight: '520px', overflowY: 'auto' }}>
        {scenarios.map((scen) => {
          const badge = getEvidenceBadgeColor(scen.prescription_status);
          const isBaseline = scen.scenario_type === 'BASELINE';

          return (
            <div
              key={scen.scenario_id}
              style={{
                padding: '1.25rem',
                borderRadius: '6px',
                backgroundColor: isBaseline ? '#0c1020' : '#0f1222',
                border: `1px solid ${isBaseline ? '#3b82f644' : 'var(--border-color)'}`,
                display: 'flex',
                flexDirection: 'column',
                gap: '0.75rem'
              }}
            >
              {/* Top row */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <span style={{
                    fontSize: '0.75rem',
                    fontWeight: 700,
                    color: isBaseline ? '#3b82f6' : 'var(--text-muted)',
                    backgroundColor: isBaseline ? '#3b82f61a' : '#1e293b',
                    padding: '0.15rem 0.4rem',
                    borderRadius: '4px'
                  }}>
                    {isBaseline ? "BASELINE" : "VARIANT"}
                  </span>
                  <span style={{ fontSize: '0.9rem', fontWeight: 600, color: '#fff' }}>
                    {isBaseline ? "Baseline Analysis" : `Excluding: ${scen.excluded_drugs.join(', ')}`}
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
                  {formatEvidenceStatus(scen.prescription_status)}
                </span>
              </div>

              {/* Grid of stats */}
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))',
                gap: '0.75rem',
                fontSize: '0.75rem',
                color: 'var(--text-muted)',
                paddingTop: '0.25rem',
                borderTop: '1px solid #1e293b'
              }}>
                <div>
                  Surviving Edges: <b style={{ color: '#fff' }}>{scen.surviving_edges_count}</b>
                </div>
                <div>
                  Convergent Edges: <b style={{ color: '#fff' }}>{scen.surviving_convergent_edges_count}</b>
                </div>
                <div>
                  Active Themes: <b style={{ color: '#fff' }}>{scen.surviving_themes_count}</b>
                </div>
                <div>
                  Topology: <b style={{ color: '#fff' }}>{formatEvidenceStatus(scen.topology_classification)}</b>
                </div>
              </div>

              {/* Dominant theme */}
              {scen.dominant_theme && (
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  Dominant theme: <span style={{ color: '#fca5a5' }}>{formatEvidenceStatus(scen.dominant_theme)}</span>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </Card>
  );
};
