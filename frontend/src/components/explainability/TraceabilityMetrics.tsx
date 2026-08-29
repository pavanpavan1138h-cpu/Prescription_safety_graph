import React from 'react';
import { Card } from '../common/Card';
import { TraceabilityProfile } from '../../types/api';
import { CheckCircle2, AlertCircle, Layers } from 'lucide-react';

interface TraceabilityMetricsProps {
  traceability: TraceabilityProfile;
}

export const TraceabilityMetrics: React.FC<TraceabilityMetricsProps> = ({ traceability }) => {
  const covPercent = Math.round(traceability.traceability_coverage_score * 100);
  const isHighCoverage = covPercent >= 80;

  return (
    <Card title="Evidentiary Traceability & Provenance Metrics" subtitle="Quantifies the reverse computational grounding of derived conclusions">
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
        
        {/* Coverage Header */}
        <div style={{
          padding: '1.25rem',
          borderRadius: '6px',
          backgroundColor: '#0c1020',
          border: `1px solid ${isHighCoverage ? '#3b82f644' : '#f59e0b44'}`,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
              {isHighCoverage ? (
                <CheckCircle2 size={18} style={{ color: '#60a5fa' }} />
              ) : (
                <AlertCircle size={18} style={{ color: '#fbbf24' }} />
              )}
              <span style={{ fontSize: '0.9rem', fontWeight: 600, color: '#fff' }}>
                Traceability Coverage Ratio
              </span>
            </div>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              {traceability.traceable_components_count} of {traceability.total_components_evaluated} components fully grounded in graph assertions
            </span>
          </div>

          <div style={{ textAlign: 'right' }}>
            <span style={{ fontSize: '1.8rem', fontWeight: 800, color: isHighCoverage ? '#60a5fa' : '#fbbf24' }}>
              {covPercent}%
            </span>
          </div>
        </div>

        {/* Progress Bar */}
        <div style={{ height: '6px', borderRadius: '3px', backgroundColor: '#1e293b', overflow: 'hidden' }}>
          <div style={{
            height: '100%',
            width: `${covPercent}%`,
            backgroundColor: isHighCoverage ? '#3b82f6' : '#f59e0b'
          }} />
        </div>

        {/* Breakdown Grid */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
          gap: '1rem'
        }}>
          <div style={{ padding: '0.75rem 1rem', borderRadius: '6px', backgroundColor: '#0f1222', border: '1px solid var(--border-color)' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block' }}>Average Lineage Depth</span>
            <span style={{ fontSize: '1.1rem', fontWeight: 700, color: '#fff', marginTop: '0.2rem', display: 'block' }}>
              {traceability.average_provenance_depth} Layers
            </span>
          </div>

          <div style={{ padding: '0.75rem 1rem', borderRadius: '6px', backgroundColor: '#0f1222', border: '1px solid var(--border-color)' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block' }}>Max Provenance Depth</span>
            <span style={{ fontSize: '1.1rem', fontWeight: 700, color: '#fff', marginTop: '0.2rem', display: 'block' }}>
              {traceability.max_provenance_depth} Layers
            </span>
          </div>

          <div style={{ padding: '0.75rem 1rem', borderRadius: '6px', backgroundColor: '#0f1222', border: '1px solid var(--border-color)' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block' }}>Cross-Layer Classification</span>
            <span style={{ fontSize: '0.8rem', fontWeight: 600, color: '#93c5fd', marginTop: '0.35rem', display: 'block' }}>
              {traceability.cross_layer_traceability.replace(/_/g, ' ')}
            </span>
          </div>

          <div style={{ padding: '0.75rem 1rem', borderRadius: '6px', backgroundColor: '#0f1222', border: '1px solid var(--border-color)' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block' }}>Orphaned / Unresolved Nodes</span>
            <span style={{ fontSize: '1.1rem', fontWeight: 700, color: traceability.orphaned_components_count > 0 ? '#f87171' : '#4ade80', marginTop: '0.2rem', display: 'block' }}>
              {traceability.orphaned_components_count}
            </span>
          </div>
        </div>

      </div>
    </Card>
  );
};
