import React from 'react';
import { ExplanationGraph } from '../../types/api';
import { Card } from '../common/Card';
import { GitCommit, ArrowDown } from 'lucide-react';

interface ExplanationGraphViewProps {
  graph: ExplanationGraph;
}

export const ExplanationGraphView: React.FC<ExplanationGraphViewProps> = ({ graph }) => {
  const getNodeColor = (type: string) => {
    switch (type) {
      case 'FINAL_INTERPRETATION':
        return '#3b82f6';
      case 'SIGNAL_THEME':
        return '#a855f7';
      case 'STRUCTURAL_RESULT':
        return '#06b6d4';
      case 'PAIR_REASONING_RESULT':
        return '#f59e0b';
      case 'DRUG_ENTITY':
        return '#10b981';
      case 'SOURCE_RECORD':
        return '#64748b';
      default:
        return '#6b7280';
    }
  };

  return (
    <Card title="Reverse Derivation Lineage Graph" subtitle="Machine-readable computational provenance from final outcome to grounded source assertions">
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        
        {/* Graph Meta */}
        <div style={{ display: 'flex', gap: '1.5rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
          <div>Total Derivation Nodes: <b style={{ color: '#fff' }}>{graph.nodes.length}</b></div>
          <div>Derivation Edges: <b style={{ color: '#fff' }}>{graph.edges.length}</b></div>
          <div>Root Interpretations: <b style={{ color: '#60a5fa' }}>{graph.root_node_ids.length}</b></div>
        </div>

        {/* Linear Derivation Trace View */}
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '0.75rem',
          maxHeight: '440px',
          overflowY: 'auto',
          padding: '0.5rem'
        }}>
          {graph.nodes.map((n, idx) => {
            const color = getNodeColor(n.node_type);
            const outgoingEdges = graph.edges.filter(e => e.source_node_id === n.node_id);

            return (
              <div
                key={`${n.node_id}-${idx}`}
                style={{
                  padding: '0.9rem 1.1rem',
                  borderRadius: '6px',
                  backgroundColor: '#0c1020',
                  border: `1px solid ${color}33`,
                  borderLeft: `4px solid ${color}`,
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '0.4rem'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <GitCommit size={15} style={{ color }} />
                    <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#fff' }}>
                      {n.label}
                    </span>
                  </div>

                  <span style={{
                    fontSize: '0.65rem',
                    padding: '0.15rem 0.4rem',
                    borderRadius: '3px',
                    backgroundColor: `${color}20`,
                    color,
                    fontWeight: 600
                  }}>
                    {n.phase_origin}
                  </span>
                </div>

                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  {n.description}
                </div>

                {outgoingEdges.length > 0 && (
                  <div style={{
                    marginTop: '0.25rem',
                    paddingTop: '0.4rem',
                    borderTop: '1px solid #1e293b',
                    fontSize: '0.7rem',
                    color: 'var(--text-muted)',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '0.2rem'
                  }}>
                    {outgoingEdges.map((e, eIdx) => (
                      <div key={eIdx} style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                        <ArrowDown size={12} style={{ color: '#60a5fa' }} />
                        <span style={{ color: '#94a3b8' }}>{e.relationship_type.replace(/_/g, ' ')}:</span>
                        <span style={{ fontFamily: 'var(--font-mono)', color: '#93c5fd' }}>{e.target_node_id}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>

      </div>
    </Card>
  );
};
