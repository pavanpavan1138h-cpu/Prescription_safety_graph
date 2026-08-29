import React from 'react';
import { Card } from '../common/Card';
import { SignalDelta } from '../../types/api';
import { formatEvidenceStatus } from '../../utils/formatters';

interface SignalDeltaViewProps {
  signalDelta: SignalDelta;
}

export const SignalDeltaView: React.FC<SignalDeltaViewProps> = ({ signalDelta }) => {
  const getThemeChangeBadge = (type: string) => {
    switch (type) {
      case 'THEME_EMERGED':
        return { bg: '#22c55e1a', text: '#4ade80', border: '#22c55e33', label: 'Emerged' };
      case 'THEME_DISAPPEARED':
        return { bg: '#ef44441a', text: '#f87171', border: '#ef444433', label: 'Disappeared' };
      case 'REINFORCEMENT_INCREASED':
        return { bg: '#3b82f61a', text: '#60a5fa', border: '#3b82f633', label: 'Reinforcement Increased' };
      case 'REINFORCEMENT_DECREASED':
        return { bg: '#f973161a', text: '#fdba74', border: '#f9731633', label: 'Reinforcement Decreased' };
      default:
        return { bg: '#1e293b', text: '#e2e8f0', border: 'transparent', label: 'Preserved' };
    }
  };

  return (
    <Card title="Clinical Signal Theme Differences" subtitle="Details changes in evidence themes, concentration distributions, and structural rank correlation values">
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
        
        {/* Concentration & Alignment Diffs */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
          {/* Concentration */}
          <div style={{
            padding: '0.75rem 1rem',
            borderRadius: '6px',
            backgroundColor: '#0f1222',
            border: `1px solid ${signalDelta.concentration_changed ? '#f9731633' : 'var(--border-color)'}`
          }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.25rem' }}>Evidence Concentration Profile</span>
            <span style={{ fontSize: '0.85rem', color: '#fff', fontWeight: 600 }}>
              {formatEvidenceStatus(signalDelta.concentration_type_a)} → {formatEvidenceStatus(signalDelta.concentration_type_b)}
            </span>
          </div>

          {/* Alignment */}
          <div style={{
            padding: '0.75rem 1rem',
            borderRadius: '6px',
            backgroundColor: '#0f1222',
            border: `1px solid ${signalDelta.alignment_changed ? '#f9731633' : 'var(--border-color)'}`
          }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.25rem' }}>Structural-Evidence Alignment</span>
            <span style={{ fontSize: '0.85rem', color: '#fff', fontWeight: 600 }}>
              {formatEvidenceStatus(signalDelta.alignment_level_a)} → {formatEvidenceStatus(signalDelta.alignment_level_b)}
            </span>
          </div>
        </div>

        {/* Themes Delta Table */}
        <div>
          <span style={{ fontSize: '0.80rem', fontWeight: 600, color: 'var(--text-muted)', display: 'block', marginBottom: '0.6rem' }}>
            Clinical Safety Themes Transitions
          </span>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', maxHeight: '350px', overflowY: 'auto' }}>
            {signalDelta.theme_comparisons.length === 0 ? (
              <div style={{ fontStyle: 'italic', fontSize: '0.8rem', color: 'var(--text-muted)', padding: '1rem' }}>
                No clinical safety themes detected in either prescription state.
              </div>
            ) : (
              signalDelta.theme_comparisons.map((tc) => {
                const b = getThemeChangeBadge(tc.change_type);
                return (
                  <div
                    key={tc.theme_name}
                    style={{
                      padding: '1rem',
                      borderRadius: '6px',
                      backgroundColor: '#0c1020',
                      border: '1px solid #1e293b',
                      display: 'flex',
                      flexDirection: 'column',
                      gap: '0.5rem'
                    }}
                  >
                    {/* Top Row */}
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#fff' }}>
                        {formatEvidenceStatus(tc.theme_name)}
                      </span>
                      <span style={{
                        fontSize: '0.7rem',
                        fontWeight: 700,
                        padding: '0.15rem 0.4rem',
                        borderRadius: '4px',
                        backgroundColor: b.bg,
                        color: b.text,
                        border: `1px solid ${b.border}`
                      }}>
                        {b.label}
                      </span>
                    </div>

                    {/* Diffs */}
                    <div style={{
                      display: 'grid',
                      gridTemplateColumns: '1fr 1fr',
                      fontSize: '0.75rem',
                      color: 'var(--text-muted)',
                      borderTop: '1px solid #1e293b',
                      paddingTop: '0.5rem',
                      gap: '0.5rem'
                    }}>
                      <div>
                        Reinforcement score: <b>{tc.reinforcement_score_a.toFixed(1)}</b> → <b>{tc.reinforcement_score_b.toFixed(1)}</b>
                      </div>
                      <div>
                        Reinforcement Level: <b>{formatEvidenceStatus(tc.reinforcement_level_a)}</b> → <b>{formatEvidenceStatus(tc.reinforcement_level_b)}</b>
                      </div>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>

      </div>
    </Card>
  );
};
