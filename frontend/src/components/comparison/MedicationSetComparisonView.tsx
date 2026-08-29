import React from 'react';
import { Card } from '../common/Card';
import { MedicationSetComparison } from '../../types/api';

interface MedicationSetComparisonViewProps {
  medComparison: MedicationSetComparison;
}

export const MedicationSetComparisonView: React.FC<MedicationSetComparisonViewProps> = ({
  medComparison
}) => {
  return (
    <Card title="Medication Set Composition Delta" subtitle="Visual breakdown of overlapping medications vs unique medications between comparisons">
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
        {/* Shared medications */}
        <div>
          <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', display: 'block', marginBottom: '0.4rem' }}>
            Shared Medications ({medComparison.shared_drugs.length})
          </span>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
            {medComparison.shared_drugs.length === 0 ? (
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontStyle: 'italic' }}>None</span>
            ) : (
              medComparison.shared_drugs.map((drug) => (
                <span
                  key={`shared-${drug}`}
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
                  {drug}
                </span>
              ))
            )}
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
          {/* A only */}
          <div style={{ padding: '0.75rem', borderRadius: '6px', backgroundColor: '#ef44440a', border: '1px solid #ef444422' }}>
            <span style={{ fontSize: '0.75rem', fontWeight: 600, color: '#f87171', display: 'block', marginBottom: '0.4rem' }}>
              Present in A Only ({medComparison.a_only_drugs.length})
            </span>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
              {medComparison.a_only_drugs.length === 0 ? (
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontStyle: 'italic' }}>None</span>
              ) : (
                medComparison.a_only_drugs.map((drug) => (
                  <span
                    key={`a-only-${drug}`}
                    style={{
                      fontSize: '0.75rem',
                      fontWeight: 600,
                      backgroundColor: '#ef44441a',
                      border: '1px solid #ef444433',
                      color: '#fca5a5',
                      padding: '0.2rem 0.5rem',
                      borderRadius: '4px'
                    }}
                  >
                    {drug}
                  </span>
                ))
              )}
            </div>
          </div>

          {/* B only */}
          <div style={{ padding: '0.75rem', borderRadius: '6px', backgroundColor: '#22c55e0a', border: '1px solid #22c55e22' }}>
            <span style={{ fontSize: '0.75rem', fontWeight: 600, color: '#4ade80', display: 'block', marginBottom: '0.4rem' }}>
              Present in B Only ({medComparison.b_only_drugs.length})
            </span>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
              {medComparison.b_only_drugs.length === 0 ? (
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontStyle: 'italic' }}>None</span>
              ) : (
                medComparison.b_only_drugs.map((drug) => (
                  <span
                    key={`b-only-${drug}`}
                    style={{
                      fontSize: '0.75rem',
                      fontWeight: 600,
                      backgroundColor: '#22c55e1a',
                      border: '1px solid #22c55e33',
                      color: '#86efac',
                      padding: '0.2rem 0.5rem',
                      borderRadius: '4px'
                    }}
                  >
                    {drug}
                  </span>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </Card>
  );
};
