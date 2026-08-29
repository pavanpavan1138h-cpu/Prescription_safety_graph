import React from 'react';
import { Card } from '../common/Card';
import { SourceProvenanceRecord } from '../../types/api';
import { Database, CheckCircle, XCircle } from 'lucide-react';

interface ProvenanceTimelineProps {
  provenanceRecords: SourceProvenanceRecord[];
}

export const ProvenanceTimeline: React.FC<ProvenanceTimelineProps> = ({ provenanceRecords }) => {
  return (
    <Card title="Grounded Source Provenance" subtitle="Audit log of underlying knowledge graph assertions and clinical datasets">
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', maxHeight: '420px', overflowY: 'auto' }}>
        {provenanceRecords.length === 0 ? (
          <div style={{ padding: '1rem', color: 'var(--text-muted)', fontStyle: 'italic', fontSize: '0.8rem' }}>
            No source provenance records available.
          </div>
        ) : (
          provenanceRecords.map((rec, idx) => (
            <div
              key={`${rec.source_id}-${idx}`}
              style={{
                padding: '0.9rem 1rem',
                borderRadius: '6px',
                backgroundColor: '#0c1020',
                border: '1px solid #1e293b',
                display: 'flex',
                flexDirection: 'column',
                gap: '0.4rem'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <Database size={15} style={{ color: '#60a5fa' }} />
                  <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#fff' }}>
                    {rec.dataset_name}
                  </span>
                  <span style={{
                    fontSize: '0.65rem',
                    padding: '0.1rem 0.35rem',
                    borderRadius: '3px',
                    backgroundColor: '#1e293b',
                    color: '#94a3b8',
                    fontFamily: 'var(--font-mono)'
                  }}>
                    {rec.record_type}
                  </span>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                  {rec.is_available ? (
                    <>
                      <CheckCircle size={14} style={{ color: '#4ade80' }} />
                      <span style={{ fontSize: '0.7rem', color: '#4ade80', fontWeight: 600 }}>GROUNDED</span>
                    </>
                  ) : (
                    <>
                      <XCircle size={14} style={{ color: '#94a3b8' }} />
                      <span style={{ fontSize: '0.7rem', color: '#94a3b8', fontWeight: 600 }}>UNAVAILABLE</span>
                    </>
                  )}
                </div>
              </div>

              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', lineHeight: '1.4' }}>
                {rec.description}
              </div>

              {rec.external_identifier && (
                <div style={{
                  fontSize: '0.7rem',
                  fontFamily: 'var(--font-mono)',
                  color: '#93c5fd',
                  backgroundColor: '#111827',
                  padding: '0.2rem 0.4rem',
                  borderRadius: '4px',
                  alignSelf: 'flex-start'
                }}>
                  Ref: {rec.external_identifier}
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </Card>
  );
};
