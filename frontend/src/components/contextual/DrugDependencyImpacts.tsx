import React from 'react';
import { Card } from '../common/Card';
import { DrugDependencyImpact } from '../../types/api';
import { getStructuralContributionColor } from '../../utils/formatters';

interface DrugDependencyImpactsProps {
  dependencies: DrugDependencyImpact[];
}

export const DrugDependencyImpacts: React.FC<DrugDependencyImpactsProps> = ({
  dependencies
}) => {
  return (
    <Card title="Medication Evidence Dependency Impacts" subtitle="Quantifies the evidence loss and structural delta when individual drugs are excluded">
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {dependencies.length === 0 ? (
          <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontStyle: 'italic', padding: '1rem 0' }}>
            No medication dependency impacts computed.
          </div>
        ) : (
          dependencies.map((dep) => {
            const badge = getStructuralContributionColor(dep.dependency_level);
            return (
              <div
                key={dep.drug_id}
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
                {/* Header */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem' }}>
                  <span style={{ fontSize: '0.9rem', fontWeight: 600, color: '#fff' }}>
                    {dep.display_name}
                  </span>
                  <span style={{
                    padding: '0.2rem 0.5rem',
                    borderRadius: '4px',
                    backgroundColor: badge.bg,
                    border: `1px solid ${badge.border}`,
                    color: badge.text,
                    fontSize: '0.7rem',
                    fontWeight: 600
                  }}>
                    {dep.dependency_level.replace(/_/g, ' ')}
                  </span>
                </div>

                {/* Score slider display */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    <span>Dependency Impact Score:</span>
                    <span style={{ fontWeight: 600, color: '#fff' }}>{dep.dependency_score} / 1.0</span>
                  </div>
                  <div style={{ height: '5px', borderRadius: '2.5px', backgroundColor: '#1e293b', overflow: 'hidden' }}>
                    <div style={{
                      height: '100%',
                      width: `${dep.dependency_score * 100}%`,
                      backgroundColor: badge.text
                    }} />
                  </div>
                </div>

                {/* Grid breakdowns */}
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(3, 1fr)',
                  gap: '0.5rem',
                  fontSize: '0.7rem',
                  color: 'var(--text-muted)',
                  borderTop: '1px solid #1e293b',
                  paddingTop: '0.5rem'
                }}>
                  <div>
                    Edge Loss: <b style={{ color: '#fff' }}>{Math.round(dep.edge_loss_ratio * 100)}%</b>
                  </div>
                  <div>
                    Theme Loss: <b style={{ color: '#fff' }}>{Math.round(dep.theme_loss_ratio * 100)}%</b>
                  </div>
                  <div>
                    Connectivity Loss: <b style={{ color: '#fff' }}>{Math.round(dep.structural_connectivity_loss_ratio * 100)}%</b>
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
