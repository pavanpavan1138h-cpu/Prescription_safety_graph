import React from 'react';
import { Card } from '../common/Card';
import { ClusterMetrics, DrugStructuralProfile } from '../../types/api';

interface EvidenceClustersProps {
  clusters: ClusterMetrics[];
  profiles: DrugStructuralProfile[];
}

export const EvidenceClusters: React.FC<EvidenceClustersProps> = ({
  clusters,
  profiles
}) => {
  // Helper to map drug ID to display name
  const getDrugName = (drugId: string): string => {
    const prof = profiles.find((p) => p.drug_id === drugId);
    return prof ? prof.display_name : drugId;
  };

  const activeClusters = clusters.filter(c => !c.is_isolated);
  const isolatedDrugs = clusters.filter(c => c.is_isolated);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <Card title="Detected Evidence Clusters" subtitle="Connected groups of medications where safety findings exist internally">
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {activeClusters.length === 0 ? (
            <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontStyle: 'italic', padding: '1rem 0' }}>
              No connected evidence clusters detected.
            </div>
          ) : (
            activeClusters.map((cluster) => (
              <div
                key={cluster.cluster_id}
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
                {/* Header info */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem' }}>
                  <span style={{ fontSize: '0.9rem', fontWeight: 600, color: '#fff' }}>
                    {cluster.cluster_id} ({cluster.drug_ids.length} Medications)
                  </span>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                    Edges: <b style={{ color: '#fff' }}>{cluster.edge_count}</b> | Density: <b style={{ color: '#fff' }}>{cluster.density}</b>
                  </div>
                </div>

                {/* Drug Chips inside cluster */}
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem', padding: '0.25rem 0' }}>
                  {cluster.drug_ids.map((drugId) => (
                    <span
                      key={drugId}
                      style={{
                        padding: '0.25rem 0.6rem',
                        borderRadius: '4px',
                        backgroundColor: '#1e293b',
                        border: '1px solid var(--border-color)',
                        fontSize: '0.8rem',
                        color: '#fff'
                      }}
                    >
                      {getDrugName(drugId)}
                    </span>
                  ))}
                </div>

                {/* Edge composition stats */}
                <div style={{ display: 'flex', gap: '1rem', fontSize: '0.75rem', color: 'var(--text-muted)', borderTop: '1px solid #1e293b', paddingTop: '0.5rem' }}>
                  <span>Convergent Edges: <b style={{ color: '#fff' }}>{cluster.convergent_edge_count}</b></span>
                  <span>DDI Edges: <b style={{ color: '#fff' }}>{cluster.ddi_only_edge_count}</b></span>
                  <span>Event Edges: <b style={{ color: '#fff' }}>{cluster.combination_event_edge_count}</b></span>
                </div>
              </div>
            ))
          )}
        </div>
      </Card>

      {/* Structurally Isolated List */}
      {isolatedDrugs.length > 0 && (
        <Card title="Structurally Isolated Medications" subtitle="Medications in the prescription with no direct safety graph edges identified">
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
            {isolatedDrugs.map((c) => (
              <span
                key={c.cluster_id}
                style={{
                  padding: '0.4rem 0.8rem',
                  borderRadius: '4px',
                  backgroundColor: '#161e2e',
                  border: '1px solid #2563eb33',
                  color: '#93c5fd',
                  fontSize: '0.85rem',
                  fontWeight: 500
                }}
              >
                {getDrugName(c.drug_ids[0])}
              </span>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
};
