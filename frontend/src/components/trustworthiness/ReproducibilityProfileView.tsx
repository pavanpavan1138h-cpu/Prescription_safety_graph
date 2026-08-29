import React from 'react';
import { Card } from '../common/Card';
import { ReproducibilityProfile } from '../../types/api';
import { RefreshCw, CheckCircle, AlertTriangle } from 'lucide-react';

interface ReproducibilityProfileViewProps {
  reproducibility: ReproducibilityProfile;
}

export const ReproducibilityProfileView: React.FC<ReproducibilityProfileViewProps> = ({ reproducibility }) => {
  const isMatch = reproducibility.deterministic_match_ratio === 1.0;

  return (
    <Card title="Deterministic Repeat-Run Verification" subtitle="Asserts binary payload reproducibility over identical knowledge graph queries">
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.2rem' }}>
        
        {/* Status Header */}
        <div style={{
          padding: '1rem 1.25rem',
          borderRadius: '6px',
          backgroundColor: isMatch ? '#06b6d40a' : '#ef44440a',
          border: `1px solid ${isMatch ? '#06b6d433' : '#ef444433'}`,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            {isMatch ? (
              <CheckCircle size={18} style={{ color: '#06b6d4' }} />
            ) : (
              <AlertTriangle size={18} style={{ color: '#f87171' }} />
            )}
            <div>
              <span style={{ fontSize: '0.9rem', fontWeight: 600, color: '#fff', display: 'block' }}>
                Reproducibility: {reproducibility.classification.replace(/_/g, ' ')}
              </span>
              <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                Identical repeats matching baseline canonical output payload
              </span>
            </div>
          </div>

          <div style={{ textAlign: 'right' }}>
            <span style={{ fontSize: '1.5rem', fontWeight: 800, color: isMatch ? '#06b6d4' : '#f87171' }}>
              {Math.round(reproducibility.deterministic_match_ratio * 100)}%
            </span>
          </div>
        </div>

        {/* Signature details */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
          <div>
            <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Baseline Hash Signature</span>
            <div style={{
              marginTop: '0.2rem',
              padding: '0.6rem 0.85rem',
              borderRadius: '4px',
              backgroundColor: '#0c0f1d',
              border: '1px solid #1e293b',
              fontSize: '0.75rem',
              fontFamily: 'var(--font-mono)',
              color: '#3b82f6',
              wordBreak: 'break-all'
            }}>
              {reproducibility.baseline_signature}
            </div>
          </div>

          {reproducibility.repeat_run_signatures.map((sig, i) => (
            <div key={i}>
              <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Repeat Run #{i + 1} Signature</span>
              <div style={{
                marginTop: '0.2rem',
                padding: '0.6rem 0.85rem',
                borderRadius: '4px',
                backgroundColor: '#0c0f1d',
                border: '1px solid #1e293b',
                fontSize: '0.75rem',
                fontFamily: 'var(--font-mono)',
                color: sig === reproducibility.baseline_signature ? '#10b981' : '#f87171',
                wordBreak: 'break-all'
              }}>
                {sig}
              </div>
            </div>
          ))}
        </div>

      </div>
    </Card>
  );
};
