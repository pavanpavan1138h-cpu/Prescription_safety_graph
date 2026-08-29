import React, { useState } from 'react';
import { Card } from '../common/Card';
import { CounterfactualResult } from '../../types/api';
import { getStructuralContributionColor } from '../../utils/formatters';
import { Eye, ShieldAlert } from 'lucide-react';

interface CounterfactualExplorerProps {
  results: CounterfactualResult[];
}

export const CounterfactualExplorer: React.FC<CounterfactualExplorerProps> = ({
  results
}) => {
  const [selectedDrugId, setSelectedDrugId] = useState<string>(results[0]?.drug_id || '');

  const activeResult = results.find((r) => r.drug_id === selectedDrugId);

  return (
    <Card title="Structural Counterfactual Exclusions" subtitle="Computationally simulate the removal of a medication to measure its network structural impact">
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        {/* Selector Dropdown */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 500 }}>
            Select Medication tocomputationally exclude:
          </label>
          <select
            value={selectedDrugId}
            onChange={(e) => setSelectedDrugId(e.target.value)}
            style={{
              padding: '0.75rem',
              borderRadius: '6px',
              backgroundColor: '#0f1222',
              border: '1px solid var(--border-color)',
              color: '#fff',
              fontSize: '0.9rem',
              outline: 'none',
              cursor: 'pointer'
            }}
          >
            {results.map((r) => (
              <option key={r.drug_id} value={r.drug_id}>
                {r.display_name}
              </option>
            ))}
          </select>
        </div>

        {activeResult ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            {/* Header info */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem', borderBottom: '1px solid #1e293b', paddingBottom: '0.75rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Eye size={16} style={{ color: '#3b82f6' }} />
                <span style={{ fontSize: '0.95rem', fontWeight: 600, color: '#fff' }}>
                  Simulation: Excluding {activeResult.display_name}
                </span>
              </div>

              <span style={{
                padding: '0.25rem 0.6rem',
                borderRadius: '4px',
                backgroundColor: getStructuralContributionColor(activeResult.contribution_level).bg,
                border: `1px solid ${getStructuralContributionColor(activeResult.contribution_level).border}`,
                color: getStructuralContributionColor(activeResult.contribution_level).text,
                fontSize: '0.75rem',
                fontWeight: 600
              }}>
                {activeResult.contribution_level.replace(/_/g, ' ')}
              </span>
            </div>

            {/* Metrics cards grid */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1rem' }}>
              <div style={{ padding: '1rem', borderRadius: '6px', backgroundColor: '#0f1222', border: '1px solid var(--border-color)', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textAlign: 'center' }}>Edges Impact</span>
                <span style={{ fontSize: '1.5rem', fontWeight: 700, color: '#ef4444', margin: '0.25rem 0' }}>
                  -{activeResult.structural_delta}
                </span>
                <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                  Before: {activeResult.original_edge_count} | Remaining: {activeResult.remaining_edge_count}
                </span>
              </div>

              <div style={{ padding: '1rem', borderRadius: '6px', backgroundColor: '#0f1222', border: '1px solid var(--border-color)', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textAlign: 'center' }}>Convergent Edges Removed</span>
                <span style={{ fontSize: '1.5rem', fontWeight: 700, color: '#f97316', margin: '0.25rem 0' }}>
                  -{activeResult.convergent_edges_removed}
                </span>
                <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                  High-priority channels removed
                </span>
              </div>

              <div style={{ padding: '1rem', borderRadius: '6px', backgroundColor: '#0f1222', border: '1px solid var(--border-color)', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textAlign: 'center' }}>Connected Clusters Delta</span>
                <span style={{ fontSize: '1.5rem', fontWeight: 700, color: '#fff', margin: '0.25rem 0' }}>
                  {activeResult.clusters_before} &rarr; {activeResult.clusters_after}
                </span>
                <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                  Largest Cluster: {activeResult.largest_cluster_before} &rarr; {activeResult.largest_cluster_after}
                </span>
              </div>
            </div>

            {/* Explanation Narrative */}
            <div style={{
              display: 'flex',
              alignItems: 'flex-start',
              gap: '0.75rem',
              padding: '0.75rem 1rem',
              borderRadius: '4px',
              backgroundColor: '#1e293b50',
              border: '1px solid var(--border-color)',
              fontSize: '0.825rem',
              color: 'var(--text-muted)',
              lineHeight: '1.4'
            }}>
              <ShieldAlert size={16} style={{ flexShrink: 0, marginTop: '2px', color: '#3b82f6' }} />
              <div>
                {activeResult.explanation}
              </div>
            </div>
          </div>
        ) : (
          <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontStyle: 'italic' }}>
            No simulation results available.
          </div>
        )}
      </div>
    </Card>
  );
};
