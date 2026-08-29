import React from 'react';
import { Card } from '../common/Card';
import { EvidenceConcentrationProfile } from '../../types/api';
import { formatEvidenceStatus } from '../../utils/formatters';

interface ConcentrationAnalysisProps {
  profile: EvidenceConcentrationProfile;
}

export const ConcentrationAnalysis: React.FC<ConcentrationAnalysisProps> = ({
  profile
}) => {
  const getConcentrationDescription = (type: string): string => {
    switch (type) {
      case 'CENTRALIZED_EVIDENCE':
        return "Concentrated around a single medication hub. This medication participates in the vast majority of combinations showing safety findings.";
      case 'CLUSTER_CONCENTRATED_EVIDENCE':
        return "Concentrated inside a single connected subgraph/cluster. The safety interactions are dense inside a specific sub-group of medications.";
      case 'DISTRIBUTED_EVIDENCE':
        return "Distributed evenly across independent regions of the network without any single drug dominating the safety profile.";
      case 'MIXED_EVIDENCE_DISTRIBUTION':
        return "Mixed distribution, combining centralized drug hubs with isolated independent combination safety channels.";
      case 'SPARSE_EVIDENCE':
        return "Sparse safety graph edges. Too few combinations show safety findings to establish a recurring structural pattern.";
      case 'NO_EVIDENCE_CONCENTRATION':
      default:
        return "No safety findings identified in the prescription combination graph.";
    }
  };

  return (
    <Card title="Evidence Concentration Profile" subtitle="Measures whether safety findings are centralized around a specific medication or distributed across the network">
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
        {/* Concentration badge */}
        <div>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.25rem' }}>Evidence Distribution Pattern</span>
          <span style={{
            padding: '0.4rem 0.8rem',
            borderRadius: '4px',
            backgroundColor: '#3b82f61a',
            border: '1px solid #3b82f633',
            color: '#93c5fd',
            fontWeight: 600,
            fontSize: '0.9rem',
            display: 'inline-block'
          }}>
            {formatEvidenceStatus(profile.concentration_type)}
          </span>
        </div>

        {/* Narrative Description */}
        <div style={{
          padding: '1rem',
          borderRadius: '6px',
          backgroundColor: '#0f1222',
          border: '1px solid var(--border-color)',
          fontSize: '0.85rem',
          color: '#fff',
          lineHeight: '1.5'
        }}>
          {getConcentrationDescription(profile.concentration_type)}
        </div>

        {/* Share bars */}
        {profile.dominant_drug_id && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              <span>Dominant Drug: <b>{profile.dominant_drug_id}</b></span>
              <span>{Math.round(profile.dominant_drug_share * 100)}% share</span>
            </div>
            <div style={{ height: '6px', borderRadius: '3px', backgroundColor: '#1e293b', overflow: 'hidden' }}>
              <div style={{
                height: '100%',
                width: `${profile.dominant_drug_share * 100}%`,
                backgroundColor: '#3b82f6',
                borderRadius: '3px'
              }} />
            </div>
          </div>
        )}

        {profile.dominant_cluster_id && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              <span>Dominant Cluster: <b>{profile.dominant_cluster_id}</b></span>
              <span>{Math.round(profile.dominant_cluster_edge_share * 100)}% share</span>
            </div>
            <div style={{ height: '6px', borderRadius: '3px', backgroundColor: '#1e293b', overflow: 'hidden' }}>
              <div style={{
                height: '100%',
                width: `${profile.dominant_cluster_edge_share * 100}%`,
                backgroundColor: '#8b5cf6',
                borderRadius: '3px'
              }} />
            </div>
          </div>
        )}

        {/* Edge Coverage */}
        <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', borderTop: '1px solid #1e293b', paddingTop: '0.75rem' }}>
          Edge Coverage Density: <b style={{ color: '#fff' }}>{Math.round(profile.edge_coverage_ratio * 100)}%</b> of possible pairs show active safety evidence.
        </div>
      </div>
    </Card>
  );
};
