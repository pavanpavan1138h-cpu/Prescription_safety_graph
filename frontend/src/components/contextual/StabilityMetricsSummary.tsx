import React from 'react';
import { Card } from '../common/Card';
import { EvidenceStabilityScore, ContextSensitivity } from '../../types/api';
import { getStructuralContributionColor, formatEvidenceStatus } from '../../utils/formatters';

interface StabilityMetricsSummaryProps {
  stability: EvidenceStabilityScore;
  sensitivity: ContextSensitivity;
  globalLevel: string;
}

export const StabilityMetricsSummary: React.FC<StabilityMetricsSummaryProps> = ({
  stability,
  sensitivity,
  globalLevel
}) => {
  const badge = getStructuralContributionColor(globalLevel);

  return (
    <Card title="Contextual Stability Metrics" subtitle="Quantifies the sensitivity of findings to prescription composition changes">
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        {/* Global Stability Level */}
        <div>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.25rem' }}>Global Interpretation Stability</span>
          <span style={{
            padding: '0.4rem 0.8rem',
            borderRadius: '4px',
            backgroundColor: badge.bg,
            border: `1px solid ${badge.border}`,
            color: badge.text,
            fontWeight: 600,
            fontSize: '0.9rem',
            display: 'inline-block'
          }}>
            {globalLevel.replace(/_/g, ' ')}
          </span>
        </div>

        {/* Meters */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
          {/* Evidence Stability */}
          <div style={{
            padding: '1rem',
            borderRadius: '6px',
            backgroundColor: '#0f1222',
            border: '1px solid var(--border-color)',
            display: 'flex',
            flexDirection: 'column',
            gap: '0.5rem'
          }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Evidence Stability</span>
            <span style={{ fontSize: '1.5rem', fontWeight: 700, color: '#3b82f6' }}>
              {Math.round(stability.overall_stability_score * 100)}%
            </span>
            <div style={{ height: '4px', borderRadius: '2px', backgroundColor: '#1e293b', overflow: 'hidden' }}>
              <div style={{
                height: '100%',
                width: `${stability.overall_stability_score * 100}%`,
                backgroundColor: '#3b82f6'
              }} />
            </div>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: '0.25rem', display: 'flex', flexDirection: 'column', gap: '0.2rem' }}>
              <span>Pairs Preserved: {Math.round(stability.pair_preservation_ratio * 100)}%</span>
              <span>Convergent Preserved: {Math.round(stability.convergent_preservation_ratio * 100)}%</span>
              <span>Themes Preserved: {Math.round(stability.theme_preservation_ratio * 100)}%</span>
            </div>
          </div>

          {/* Context Sensitivity */}
          <div style={{
            padding: '1rem',
            borderRadius: '6px',
            backgroundColor: '#0f1222',
            border: '1px solid var(--border-color)',
            display: 'flex',
            flexDirection: 'column',
            gap: '0.5rem'
          }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Context Sensitivity</span>
            <span style={{ fontSize: '1.5rem', fontWeight: 700, color: '#f97316' }}>
              {Math.round(sensitivity.overall_sensitivity_score * 100)}%
            </span>
            <div style={{ height: '4px', borderRadius: '2px', backgroundColor: '#1e293b', overflow: 'hidden' }}>
              <div style={{
                height: '100%',
                width: `${sensitivity.overall_sensitivity_score * 100}%`,
                backgroundColor: '#f97316'
              }} />
            </div>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: '0.25rem', display: 'flex', flexDirection: 'column', gap: '0.2rem' }}>
              <span>Status changes in: {Math.round(sensitivity.status_change_rate * 100)}%</span>
              <span>Topology changes in: {Math.round(sensitivity.topology_change_rate * 100)}%</span>
              <span>Dominant theme changes in: {Math.round(sensitivity.theme_change_rate * 100)}%</span>
            </div>
          </div>
        </div>
      </div>
    </Card>
  );
};
