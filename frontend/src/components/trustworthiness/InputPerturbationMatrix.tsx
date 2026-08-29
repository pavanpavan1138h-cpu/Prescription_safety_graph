import React from 'react';
import { Card } from '../common/Card';
import { InputPerturbationResult } from '../../types/api';
import { Check, X, ShieldAlert } from 'lucide-react';

interface InputPerturbationMatrixProps {
  perturbations: InputPerturbationResult[];
}

export const InputPerturbationMatrix: React.FC<InputPerturbationMatrixProps> = ({ perturbations }) => {
  return (
    <Card title="Input Perturbation Invariance Matrix" subtitle="Verifies analytical outputs remain invariant under metadata/normalization modifications">
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
        
        {perturbations.length === 0 ? (
          <div style={{ padding: '1rem', color: 'var(--text-muted)', fontStyle: 'italic', fontSize: '0.8rem' }}>
            No input perturbation results available.
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.8rem' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid #1e293b', textAlign: 'left' }}>
                  <th style={{ padding: '0.6rem 0.5rem', color: 'var(--text-muted)' }}>ID</th>
                  <th style={{ padding: '0.6rem 0.5rem', color: 'var(--text-muted)' }}>Perturbation Type</th>
                  <th style={{ padding: '0.6rem 0.5rem', color: 'var(--text-muted)' }}>Status</th>
                  <th style={{ padding: '0.6rem 0.5rem', color: 'var(--text-muted)' }}>Baseline Signature</th>
                  <th style={{ padding: '0.6rem 0.5rem', color: 'var(--text-muted)' }}>Perturbed Signature</th>
                </tr>
              </thead>
              <tbody>
                {perturbations.map((p, idx) => {
                  const isInvariant = p.classification === 'INVARIANT';
                  return (
                    <tr key={`${p.perturbation_id}-${idx}`} style={{ borderBottom: '1px solid #0f1222' }}>
                      <td style={{ padding: '0.75rem 0.5rem', fontFamily: 'var(--font-mono)', color: '#94a3b8' }}>
                        {p.perturbation_id}
                      </td>
                      <td style={{ padding: '0.75rem 0.5rem', fontWeight: 500, color: '#fff' }}>
                        {p.perturbation_type.replace(/_/g, ' ')}
                      </td>
                      <td style={{ padding: '0.75rem 0.5rem' }}>
                        <span style={{
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '0.25rem',
                          fontSize: '0.7rem',
                          fontWeight: 700,
                          padding: '0.15rem 0.4rem',
                          borderRadius: '3px',
                          backgroundColor: isInvariant ? '#10b98115' : '#f59e0b15',
                          color: isInvariant ? '#10b981' : '#fbbf24',
                          border: `1px solid ${isInvariant ? '#10b98133' : '#f59e0b33'}`
                        }}>
                          {isInvariant ? <Check size={12} /> : <X size={12} />}
                          {p.classification}
                        </span>
                      </td>
                      <td style={{ padding: '0.75rem 0.5rem', fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>
                        {p.baseline_signature.slice(0, 8)}...
                      </td>
                      <td style={{ padding: '0.75rem 0.5rem', fontFamily: 'var(--font-mono)', color: isInvariant ? 'var(--text-muted)' : '#f87171' }}>
                        {p.perturbed_signature.slice(0, 8)}...
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}

      </div>
    </Card>
  );
};
