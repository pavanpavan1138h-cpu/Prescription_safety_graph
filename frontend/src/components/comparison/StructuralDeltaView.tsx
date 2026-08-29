import React from 'react';
import { Card } from '../common/Card';
import { StructuralDelta } from '../../types/api';
import { ArrowUp, ArrowDown, Minus } from 'lucide-react';
import { formatEvidenceStatus } from '../../utils/formatters';

interface StructuralDeltaViewProps {
  structuralDelta: StructuralDelta;
}

export const StructuralDeltaView: React.FC<StructuralDeltaViewProps> = ({
  structuralDelta
}) => {
  const sd = structuralDelta;

  return (
    <Card title="Structural Network Topology Comparison" subtitle="Highlights changes in graph parameters, clusters, and medication centrality positions">
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        
        {/* Structural Delta Magnitude Card */}
        <div style={{
          padding: '1.25rem',
          borderRadius: '6px',
          backgroundColor: '#0c1020',
          border: '1px solid #3b82f644',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <div>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'block' }}>Structural Delta Magnitude</span>
            <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Quantifies the net restructuring delta of the graph layout</span>
          </div>
          <span style={{ fontSize: '1.75rem', fontWeight: 800, color: '#3b82f6' }}>
            {Math.round(sd.structural_delta_magnitude * 100)}%
          </span>
        </div>

        {/* Param Diffs Grid */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
          gap: '1rem'
        }}>
          {/* Nodes */}
          <div style={{ padding: '0.75rem', borderRadius: '6px', backgroundColor: '#0f1222', border: '1px solid var(--border-color)' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block' }}>Node count (Medications)</span>
            <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#fff', marginTop: '0.25rem' }}>
              {sd.node_count_a} → {sd.node_count_b}{' '}
              <span style={{ fontSize: '0.8rem', color: sd.node_count_delta >= 0 ? '#4ade80' : '#f87171' }}>
                ({sd.node_count_delta >= 0 ? `+${sd.node_count_delta}` : sd.node_count_delta})
              </span>
            </div>
          </div>

          {/* Edges */}
          <div style={{ padding: '0.75rem', borderRadius: '6px', backgroundColor: '#0f1222', border: '1px solid var(--border-color)' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block' }}>Edge count (Evidence edges)</span>
            <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#fff', marginTop: '0.25rem' }}>
              {sd.edge_count_a} → {sd.edge_count_b}{' '}
              <span style={{ fontSize: '0.8rem', color: sd.edge_count_delta >= 0 ? '#4ade80' : '#f87171' }}>
                ({sd.edge_count_delta >= 0 ? `+${sd.edge_count_delta}` : sd.edge_count_delta})
              </span>
            </div>
          </div>

          {/* Density */}
          <div style={{ padding: '0.75rem', borderRadius: '6px', backgroundColor: '#0f1222', border: '1px solid var(--border-color)' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block' }}>Network density</span>
            <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#fff', marginTop: '0.25rem' }}>
              {sd.density_a.toFixed(3)} → {sd.density_b.toFixed(3)}{' '}
              <span style={{ fontSize: '0.8rem', color: sd.density_delta >= 0 ? '#4ade80' : '#f87171' }}>
                ({sd.density_delta >= 0 ? `+${sd.density_delta.toFixed(3)}` : sd.density_delta.toFixed(3)})
              </span>
            </div>
          </div>

          {/* Clusters */}
          <div style={{ padding: '0.75rem', borderRadius: '6px', backgroundColor: '#0f1222', border: '1px solid var(--border-color)' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block' }}>Connected Clusters</span>
            <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#fff', marginTop: '0.25rem' }}>
              {sd.cluster_count_a} → {sd.cluster_count_b}{' '}
              <span style={{ fontSize: '0.8rem', color: sd.cluster_count_delta <= 0 ? '#4ade80' : '#f87171' }}>
                ({sd.cluster_count_delta >= 0 ? `+${sd.cluster_count_delta}` : sd.cluster_count_delta})
              </span>
            </div>
          </div>
        </div>

        {/* Topology & Hub */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
          <div style={{ padding: '0.75rem 1rem', borderRadius: '6px', backgroundColor: '#0f1222', border: '1px solid var(--border-color)' }}>
            <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.25rem' }}>Topology Classification</span>
            <span style={{ fontSize: '0.85rem', color: '#fff', fontWeight: 600 }}>
              {formatEvidenceStatus(sd.topology_a)} → {formatEvidenceStatus(sd.topology_b)}
            </span>
          </div>

          <div style={{ padding: '0.75rem 1rem', borderRadius: '6px', backgroundColor: '#0f1222', border: '1px solid var(--border-color)' }}>
            <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.25rem' }}>Dominant Hub Medication</span>
            <span style={{ fontSize: '0.85rem', color: '#fff', fontWeight: 600 }}>
              {sd.dominant_drug_a || 'None'} → {sd.dominant_drug_b || 'None'}
            </span>
          </div>
        </div>

        {/* Centrality Rank Movement List */}
        <div>
          <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', display: 'block', marginBottom: '0.6rem' }}>
            Medication Centrality Rank Movements (Shift in graph centrality)
          </span>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', maxHeight: '250px', overflowY: 'auto' }}>
            {sd.rank_comparisons.map((rc) => {
              const hasRankA = rc.rank_a !== null;
              const hasRankB = rc.rank_b !== null;
              const delta = rc.rank_delta;

              let icon = <Minus size={14} style={{ color: 'var(--text-muted)' }} />;
              let deltaColor = 'var(--text-muted)';
              let deltaText = 'Unchanged';

              if (delta !== null) {
                if (delta < 0) {
                  // Rank A was 4 (lower), Rank B is 2 (higher centrality hub) -> delta is negative, which means centrality INCREASED!
                  icon = <ArrowUp size={14} style={{ color: '#4ade80' }} />;
                  deltaColor = '#4ade80';
                  deltaText = `Up +${Math.abs(delta)}`;
                } else if (delta > 0) {
                  icon = <ArrowDown size={14} style={{ color: '#f87171' }} />;
                  deltaColor = '#f87171';
                  deltaText = `Down -${delta}`;
                }
              }

              return (
                <div
                  key={rc.drug_id}
                  style={{
                    padding: '0.6rem 0.75rem',
                    borderRadius: '4px',
                    backgroundColor: '#0c1020',
                    border: '1px solid #1e293b',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    fontSize: '0.75rem'
                  }}
                >
                  <span style={{ fontWeight: 600, color: '#fff' }}>{rc.display_name}</span>
                  
                  <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                    <span style={{ color: 'var(--text-muted)' }}>
                      Rank: {hasRankA ? `#${rc.rank_a}` : 'N/A'} → {hasRankB ? `#${rc.rank_b}` : 'N/A'}
                    </span>
                    
                    {hasRankA && hasRankB ? (
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.2rem', color: deltaColor, fontWeight: 700 }}>
                        {icon}
                        <span>{deltaText}</span>
                      </div>
                    ) : (
                      <span style={{ color: 'var(--text-muted)', fontStyle: 'italic' }}>
                        {!hasRankA ? 'Added' : 'Removed'}
                      </span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

      </div>
    </Card>
  );
};
