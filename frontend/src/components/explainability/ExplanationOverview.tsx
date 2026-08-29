import React from 'react';
import { Card } from '../common/Card';
import { StructuredExplanationClaim } from '../../types/api';
import { FileText, Check, X } from 'lucide-react';

interface ExplanationOverviewProps {
  narrative: string;
  structuredClaims: StructuredExplanationClaim[];
}

export const ExplanationOverview: React.FC<ExplanationOverviewProps> = ({ narrative, structuredClaims }) => {
  return (
    <Card title="Analytical Derivation & Claim Audit" subtitle="Natural language synthesis and audited structured claims">
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
        
        {/* Narrative Box */}
        <div style={{
          padding: '1.25rem',
          borderRadius: '6px',
          backgroundColor: '#0c1020',
          border: '1px solid #1e293b',
          fontSize: '0.85rem',
          lineHeight: '1.6',
          color: '#e2e8f0',
          whiteSpace: 'pre-line'
        }}>
          {narrative}
        </div>

        {/* Structured Claims List */}
        {structuredClaims.length > 0 && (
          <div>
            <div style={{
              fontSize: '0.8rem',
              fontWeight: 700,
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
              color: 'var(--text-muted)',
              marginBottom: '0.6rem'
            }}>
              Audited Analytical Claims ({structuredClaims.length})
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              {structuredClaims.map((claim, idx) => (
                <div
                  key={`${claim.claim_id}-${idx}`}
                  style={{
                    padding: '0.75rem 1rem',
                    borderRadius: '6px',
                    backgroundColor: '#0c1020',
                    border: `1px solid ${claim.is_supported ? '#3b82f633' : '#f59e0b33'}`,
                    display: 'flex',
                    alignItems: 'flex-start',
                    gap: '0.75rem'
                  }}
                >
                  <div style={{ marginTop: '0.15rem' }}>
                    {claim.is_supported ? (
                      <Check size={16} style={{ color: '#60a5fa' }} />
                    ) : (
                      <X size={16} style={{ color: '#f59e0b' }} />
                    )}
                  </div>

                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.2rem' }}>
                      <span style={{ fontSize: '0.7rem', fontFamily: 'var(--font-mono)', color: '#94a3b8' }}>
                        {claim.claim_id}
                      </span>
                      <span style={{
                        fontSize: '0.65rem',
                        padding: '0.1rem 0.35rem',
                        borderRadius: '3px',
                        backgroundColor: '#1e293b',
                        color: '#93c5fd'
                      }}>
                        {claim.claim_type}
                      </span>
                    </div>
                    <div style={{ fontSize: '0.8rem', color: '#fff' }}>
                      {claim.claim_text}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

      </div>
    </Card>
  );
};
