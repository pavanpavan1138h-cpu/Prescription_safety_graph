import React, { useState } from 'react';
import { Card } from '../common/Card';
import { EvidenceDelta, PairComparison } from '../../types/api';
import { formatEvidenceStatus, getEvidenceBadgeColor } from '../../utils/formatters';

interface EvidenceDeltaViewProps {
  evidenceDelta: EvidenceDelta;
}

export const EvidenceDeltaView: React.FC<EvidenceDeltaViewProps> = ({ evidenceDelta }) => {
  const [filter, setFilter] = useState<string>('ALL');

  const getChangeBadgeColor = (type: string) => {
    switch (type) {
      case 'NEW_EVIDENCE':
        return { bg: '#22c55e1a', text: '#4ade80', border: '#22c55e33' };
      case 'REMOVED_EVIDENCE':
        return { bg: '#ef44441a', text: '#f87171', border: '#ef444433' };
      case 'EVIDENCE_RECLASSIFIED':
        return { bg: '#a855f71a', text: '#c084fc', border: '#a855f733' };
      default:
        return { bg: '#1e293b', text: '#e2e8f0', border: 'transparent' };
    }
  };

  const filtered = evidenceDelta.pair_comparisons.filter((p) => {
    if (filter === 'ALL') return true;
    if (filter === 'RECLASSIFIED') return p.change_type === 'EVIDENCE_RECLASSIFIED';
    if (filter === 'ADDED') return p.change_type === 'NEW_EVIDENCE';
    if (filter === 'REMOVED') return p.change_type === 'REMOVED_EVIDENCE';
    return true;
  });

  return (
    <Card title="Pairwise Evidence Changes" subtitle="Tracks additions, removals, and status reclassifications of drug-pair interactions">
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {/* Filters and counters */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.75rem' }}>
          {/* Counters */}
          <div style={{ display: 'flex', gap: '0.75rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            <span>Added: <b style={{ color: '#4ade80' }}>{evidenceDelta.added_pairs_count}</b></span>
            <span>Removed: <b style={{ color: '#f87171' }}>{evidenceDelta.removed_pairs_count}</b></span>
            <span>Reclassified: <b style={{ color: '#c084fc' }}>{evidenceDelta.reclassified_pairs_count}</b></span>
            <span>Preserved: <b style={{ color: '#e2e8f0' }}>{evidenceDelta.preserved_pairs_count}</b></span>
          </div>

          {/* Selector */}
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            style={{
              padding: '0.3rem 0.6rem',
              borderRadius: '4px',
              backgroundColor: '#0c1020',
              border: '1px solid var(--border-color)',
              color: '#fff',
              fontSize: '0.75rem',
              cursor: 'pointer'
            }}
          >
            <option value="ALL">Show All ({evidenceDelta.pair_comparisons.length})</option>
            <option value="ADDED">Added Only ({evidenceDelta.added_pairs_count})</option>
            <option value="REMOVED">Removed Only ({evidenceDelta.removed_pairs_count})</option>
            <option value="RECLASSIFIED">Reclassified Only ({evidenceDelta.reclassified_pairs_count})</option>
          </select>
        </div>

        {/* List Table */}
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.8rem', minWidth: '550px' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-color)', textAlign: 'left', color: 'var(--text-muted)' }}>
                <th style={{ padding: '0.5rem' }}>Drug Combination</th>
                <th style={{ padding: '0.5rem' }}>Status in Snapshot A</th>
                <th style={{ padding: '0.5rem' }}>Status in Snapshot B</th>
                <th style={{ padding: '0.5rem', textAlign: 'right' }}>Change Classification</th>
              </tr>
            </thead>
            <tbody>
              {filtered.length === 0 ? (
                <tr>
                  <td colSpan={4} style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)', fontStyle: 'italic' }}>
                    No pairwise changes match the selected filter.
                  </td>
                </tr>
              ) : (
                filtered.map((item) => {
                  const bA = getEvidenceBadgeColor(item.evidence_status_a);
                  const bB = getEvidenceBadgeColor(item.evidence_status_b);
                  const ch = getChangeBadgeColor(item.change_type);

                  return (
                    <tr key={item.canonical_pair_key} style={{ borderBottom: '1px solid #1e293b' }}>
                      <td style={{ padding: '0.75rem 0.5rem', fontWeight: 600, color: '#fff' }}>
                        {item.drug_a_name} + {item.drug_b_name}
                      </td>
                      <td style={{ padding: '0.75rem 0.5rem' }}>
                        <span style={{
                          fontSize: '0.7rem',
                          padding: '0.15rem 0.4rem',
                          borderRadius: '4px',
                          backgroundColor: bA.bg,
                          color: bA.text,
                          border: `1px solid ${bA.border}`
                        }}>
                          {formatEvidenceStatus(item.evidence_status_a)}
                        </span>
                      </td>
                      <td style={{ padding: '0.75rem 0.5rem' }}>
                        <span style={{
                          fontSize: '0.7rem',
                          padding: '0.15rem 0.4rem',
                          borderRadius: '4px',
                          backgroundColor: bB.bg,
                          color: bB.text,
                          border: `1px solid ${bB.border}`
                        }}>
                          {formatEvidenceStatus(item.evidence_status_b)}
                        </span>
                      </td>
                      <td style={{ padding: '0.75rem 0.5rem', textAlign: 'right' }}>
                        <span style={{
                          fontSize: '0.7rem',
                          fontWeight: 700,
                          padding: '0.15rem 0.4rem',
                          borderRadius: '4px',
                          backgroundColor: ch.bg,
                          color: ch.text,
                          border: `1px solid ${ch.border}`
                        }}>
                          {item.change_type.replace(/_/g, ' ')}
                        </span>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </Card>
  );
};
