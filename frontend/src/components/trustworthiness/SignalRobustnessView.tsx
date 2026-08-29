import React from 'react';
import { Card } from '../common/Card';
import { SignalRobustnessProfile } from '../../types/api';
import { Radio } from 'lucide-react';

interface SignalRobustnessViewProps {
  signals: SignalRobustnessProfile[];
}

export const SignalRobustnessView: React.FC<SignalRobustnessViewProps> = ({ signals }) => {
  const getBadgeStyle = (level: string) => {
    switch (level) {
      case 'HIGHLY_ROBUST_SIGNAL':
        return { bg: '#3b82f615', text: '#60a5fa', border: '#3b82f633' };
      case 'ROBUST_SIGNAL':
        return { bg: '#10b98115', text: '#34d399', border: '#10b98133' };
      case 'MODERATELY_SENSITIVE_SIGNAL':
        return { bg: '#f59e0b15', text: '#fbbf24', border: '#f59e0b33' };
      default:
        return { bg: '#ef444415', text: '#f87171', border: '#ef444433' };
    }
  };

  return (
    <Card title="Evidentiary Signal Robustness Profiles" subtitle="Evaluates persistence rates of evidence themes under subset perturbations">
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', maxHeight: '400px', overflowY: 'auto' }}>
        
        {signals.length === 0 ? (
          <div style={{ padding: '1rem', color: 'var(--text-muted)', fontStyle: 'italic', fontSize: '0.8rem' }}>
            No signal robustness profiles available.
          </div>
        ) : (
          signals.map((sig, idx) => {
            const b = getBadgeStyle(sig.classification);
            return (
              <div
                key={`${sig.theme_id}-${idx}`}
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
                {/* Header Row */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: '0.9rem', fontWeight: 600, color: '#fff' }}>
                    Theme: {sig.theme_id.replace('THEME_', '')}
                  </span>

                  <span style={{
                    fontSize: '0.65rem',
                    fontWeight: 700,
                    padding: '0.2rem 0.5rem',
                    borderRadius: '4px',
                    backgroundColor: b.bg,
                    color: b.text,
                    border: `1px solid ${b.border}`
                  }}>
                    {sig.classification.replace(/_/g, ' ')}
                  </span>
                </div>

                {/* Progress bar */}
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.7rem', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>
                    <span>Scenario Presence Ratio</span>
                    <span>{Math.round(sig.scenario_presence_ratio * 100)}%</span>
                  </div>
                  <div style={{ height: '4px', borderRadius: '2px', backgroundColor: '#1e293b', overflow: 'hidden' }}>
                    <div style={{ height: '100%', width: `${sig.scenario_presence_ratio * 100}%`, backgroundColor: b.text }} />
                  </div>
                </div>

                <div style={{ display: 'flex', gap: '1rem', fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                  <div>Baseline Present: <b style={{ color: '#fff' }}>{sig.baseline_present ? 'YES' : 'NO'}</b></div>
                  <div>Reinforcement Stability: <b style={{ color: '#fff' }}>{sig.reinforcement_stability.toFixed(2)}</b></div>
                </div>
              </div>
            );
          })
        )}

      </div>
    </Card>
  );
};
