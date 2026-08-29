import React from 'react';
import { Card } from '../common/Card';
import { StabilityDelta } from '../../types/api';
import { getStructuralContributionColor } from '../../utils/formatters';

interface StabilityDeltaViewProps {
  stabilityDelta: StabilityDelta;
}

export const StabilityDeltaView: React.FC<StabilityDeltaViewProps> = ({
  stabilityDelta
}) => {
  const sd = stabilityDelta;
  const badge = getStructuralContributionColor(sd.stability_change_type);

  return (
    <Card title="Contextual Stability Comparison" subtitle="Compares how sensitive aggregate interpretations are to controlled snapshot perturbations">
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        
        {/* Global Stability Level Delta */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem' }}>
          <div>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block' }}>Interpretation Stability Shift</span>
            <span style={{ fontSize: '0.85rem', color: '#fff', fontWeight: 600, marginTop: '0.2rem', display: 'block' }}>
              {sd.interpretation_stability_a.replace(/_/g, ' ')} → {sd.interpretation_stability_b.replace(/_/g, ' ')}
            </span>
          </div>

          <span style={{
            padding: '0.3rem 0.6rem',
            borderRadius: '4px',
            backgroundColor: badge.bg,
            border: `1px solid ${badge.border}`,
            color: badge.text,
            fontWeight: 700,
            fontSize: '0.75rem'
          }}>
            {sd.stability_change_type.replace(/_/g, ' ')}
          </span>
        </div>

        {/* Meters */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.25rem' }}>
          
          {/* Evidence Stability Score Gauge */}
          <div style={{
            padding: '1rem',
            borderRadius: '6px',
            backgroundColor: '#0f1222',
            border: '1px solid var(--border-color)',
            display: 'flex',
            flexDirection: 'column',
            gap: '0.5rem'
          }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Evidence Stability Delta</span>
            <span style={{ fontSize: '1.4rem', fontWeight: 700, color: '#3b82f6' }}>
              {Math.round(sd.stability_score_a * 100)}% → {Math.round(sd.stability_score_b * 100)}%
            </span>
            <div style={{ height: '4px', borderRadius: '2px', backgroundColor: '#1e293b', overflow: 'hidden' }}>
              <div style={{
                height: '100%',
                width: `${sd.stability_score_b * 100}%`,
                backgroundColor: '#3b82f6'
              }} />
            </div>
            <span style={{ fontSize: '0.7rem', color: sd.stability_score_delta >= 0 ? '#4ade80' : '#f87171' }}>
              Score Delta: {sd.stability_score_delta >= 0 ? `+${sd.stability_score_delta.toFixed(2)}` : sd.stability_score_delta.toFixed(2)}
            </span>
          </div>

          {/* Context Sensitivity Score Gauge */}
          <div style={{
            padding: '1rem',
            borderRadius: '6px',
            backgroundColor: '#0f1222',
            border: '1px solid var(--border-color)',
            display: 'flex',
            flexDirection: 'column',
            gap: '0.5rem'
          }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Context Sensitivity Delta</span>
            <span style={{ fontSize: '1.4rem', fontWeight: 700, color: '#f97316' }}>
              {Math.round(sd.sensitivity_score_a * 100)}% → {Math.round(sd.sensitivity_score_b * 100)}%
            </span>
            <div style={{ height: '4px', borderRadius: '2px', backgroundColor: '#1e293b', overflow: 'hidden' }}>
              <div style={{
                height: '100%',
                width: `${sd.sensitivity_score_b * 100}%`,
                backgroundColor: '#f97316'
              }} />
            </div>
            <span style={{ fontSize: '0.7rem', color: sd.sensitivity_score_delta <= 0 ? '#4ade80' : '#f87171' }}>
              Sensitivity Delta: {sd.sensitivity_score_delta >= 0 ? `+${sd.sensitivity_score_delta.toFixed(2)}` : sd.sensitivity_score_delta.toFixed(2)}
            </span>
          </div>

        </div>

      </div>
    </Card>
  );
};
