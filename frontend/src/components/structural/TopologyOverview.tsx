import React from 'react';
import { Card } from '../common/Card';
import { NetworkSummary, TopologyClassification, StructuralInterpretation } from '../../types/api';
import { formatEvidenceStatus } from '../../utils/formatters';

interface TopologyOverviewProps {
  summary: NetworkSummary;
  topology: TopologyClassification;
  interpretation: StructuralInterpretation;
}

export const TopologyOverview: React.FC<TopologyOverviewProps> = ({
  summary,
  topology,
  interpretation
}) => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <Card title="Prescription Network Topology" subtitle="Global structure and connectivity classification of Graph findings">
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          {/* Topology Badges */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            <div>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.25rem' }}>Primary Topology</span>
              <span style={{
                padding: '0.4rem 0.8rem',
                borderRadius: '4px',
                backgroundColor: '#8b5cf61a',
                border: '1px solid #8b5cf633',
                color: '#c4b5fd',
                fontWeight: 600,
                fontSize: '0.9rem',
                display: 'inline-block'
              }}>
                {formatEvidenceStatus(topology.primary_topology)}
              </span>
            </div>
            
            {topology.secondary_characteristics.length > 0 && (
              <div>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.25rem' }}>Secondary Characteristics</span>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem' }}>
                  {topology.secondary_characteristics.map((c, i) => (
                    <span key={i} style={{
                      padding: '0.2rem 0.5rem',
                      borderRadius: '4px',
                      backgroundColor: '#1e293b',
                      border: '1px solid var(--border-color)',
                      color: '#94a3b8',
                      fontSize: '0.75rem'
                    }}>
                      {formatEvidenceStatus(c)}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>

          <div style={{
            padding: '1rem',
            borderRadius: '6px',
            backgroundColor: '#0f1222',
            border: '1px solid var(--border-color)',
            fontSize: '0.85rem',
            color: '#fff',
            lineHeight: '1.5'
          }}>
            {interpretation.network_connectivity_narration}
          </div>
        </div>
      </Card>

      {/* Grid of statistics */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
        <div style={{ backgroundColor: '#0c0f1d', border: '1px solid var(--border-color)', borderRadius: '6px', padding: '1rem', display: 'flex', flexDirection: 'column' }}>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Drugs Count</span>
          <span style={{ fontSize: '1.5rem', fontWeight: 700, color: '#fff', margin: '0.25rem 0' }}>{summary.total_prescription_drugs}</span>
          <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
            Connected: <b style={{ color: '#fff' }}>{summary.evidence_connected_drugs}</b> | Isolated: <b style={{ color: '#fff' }}>{summary.structurally_isolated_drugs}</b>
          </span>
        </div>

        <div style={{ backgroundColor: '#0c0f1d', border: '1px solid var(--border-color)', borderRadius: '6px', padding: '1rem', display: 'flex', flexDirection: 'column' }}>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Evidence Density</span>
          <span style={{ fontSize: '1.5rem', fontWeight: 700, color: '#fff', margin: '0.25rem 0' }}>{summary.network_density}</span>
          <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
            Pairs with evidence: <b style={{ color: '#fff' }}>{summary.evidence_supported_pairs}</b> / {summary.total_possible_pairs}
          </span>
        </div>

        <div style={{ backgroundColor: '#0c0f1d', border: '1px solid var(--border-color)', borderRadius: '6px', padding: '1rem', display: 'flex', flexDirection: 'column' }}>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Connected Clusters</span>
          <span style={{ fontSize: '1.5rem', fontWeight: 700, color: '#fff', margin: '0.25rem 0' }}>{summary.connected_cluster_count}</span>
          <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
            Largest Cluster size: <b style={{ color: '#fff' }}>{summary.largest_cluster_size}</b> drugs
          </span>
        </div>

        <div style={{ backgroundColor: '#0c0f1d', border: '1px solid var(--border-color)', borderRadius: '6px', padding: '1rem', display: 'flex', flexDirection: 'column' }}>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Evidence Channels</span>
          <span style={{ fontSize: '1.5rem', fontWeight: 700, color: '#fff', margin: '0.25rem 0' }}>{summary.evidence_supported_pairs}</span>
          <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
            Conv: <b style={{ color: '#fff' }}>{summary.convergent_edge_count}</b> | DDI: <b style={{ color: '#fff' }}>{summary.ddi_only_edge_count}</b> | Event: <b style={{ color: '#fff' }}>{summary.combination_event_edge_count}</b>
          </span>
        </div>
      </div>
    </div>
  );
};
