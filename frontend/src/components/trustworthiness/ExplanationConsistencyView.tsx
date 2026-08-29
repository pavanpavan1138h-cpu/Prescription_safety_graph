import React from 'react';
import { Card } from '../common/Card';
import { ExplanationConsistencyProfile } from '../../types/api';
import { ShieldCheck, AlertCircle } from 'lucide-react';

interface ExplanationConsistencyViewProps {
  explanation: ExplanationConsistencyProfile;
}

export const ExplanationConsistencyView: React.FC<ExplanationConsistencyViewProps> = ({ explanation }) => {
  const isConsistent = explanation.consistency_ratio === 1.0;

  return (
    <Card title="Explanation Claim Consistency" subtitle="Validates natural language explanation claims against safety reports">
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.2rem' }}>
        
        {/* Status Header */}
        <div style={{
          padding: '1rem',
          borderRadius: '6px',
          backgroundColor: isConsistent ? '#10b9810a' : '#f59e0b0a',
          border: `1px solid ${isConsistent ? '#10b98133' : '#f59e0b33'}`,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            {isConsistent ? (
              <ShieldCheck size={18} style={{ color: '#10b981' }} />
            ) : (
              <AlertCircle size={18} style={{ color: '#fbbf24' }} />
            )}
            <div>
              <span style={{ fontSize: '0.9rem', fontWeight: 700, color: '#fff', display: 'block' }}>
                Explanation Claims: {explanation.classification.replace(/_/g, ' ')}
              </span>
              <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                {explanation.claims_supported} of {explanation.claims_checked} narrative assertions verified
              </span>
            </div>
          </div>

          <div style={{ textAlign: 'right' }}>
            <span style={{ fontSize: '1.4rem', fontWeight: 850, color: isConsistent ? '#10b981' : '#fbbf24' }}>
              {Math.round(explanation.consistency_ratio * 100)}%
            </span>
          </div>
        </div>

        {/* Unsupported claims list */}
        {explanation.unsupported_claims.length > 0 && (
          <div>
            <span style={{ fontSize: '0.75rem', color: '#f87171', fontWeight: 650, display: 'block', marginBottom: '0.5rem' }}>
              Mismatched / Unverified Narrative Assertions ({explanation.unsupported_claims.length})
            </span>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              {explanation.unsupported_claims.map((claim, idx) => (
                <div key={idx} style={{
                  padding: '0.75rem',
                  borderRadius: '6px',
                  backgroundColor: '#ef444405',
                  border: '1px solid #ef444422',
                  fontSize: '0.8rem',
                  color: '#fca5a5',
                  lineHeight: '1.4'
                }}>
                  {claim}
                </div>
              ))}
            </div>
          </div>
        )}

      </div>
    </Card>
  );
};
