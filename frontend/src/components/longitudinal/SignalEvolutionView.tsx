import React from 'react';
import { Card } from '../common/Card';
import { SignalEvolutionProfile } from '../../types/api';
import { Check, X } from 'lucide-react';

interface SignalEvolutionViewProps {
  signals: SignalEvolutionProfile[];
}

export const SignalEvolutionView: React.FC<SignalEvolutionViewProps> = ({ signals }) => {
  const getBadgeStyle = (level: string) => {
    switch (level) {
      case 'SIGNAL_STRENGTHENING':
        return { bg: '#10b98115', text: '#34d399', border: '#10b98133' };
      case 'SIGNAL_WEAKENING':
        return { bg: '#ef444415', text: '#f87171', border: '#ef444433' };
      case 'SIGNAL_RECONFIGURATION':
        return { bg: '#3b82f615', text: '#60a5fa', border: '#3b82f633' };
      default:
        return { bg: '#1e293b', text: '#94a3b8', border: '#1e293b' };
    }
  };

  return (
    <Card title="Evidentiary Signals Evolution History" subtitle="Tracks evidence theme significance levels over history sequence">
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', maxHeight: '400px', overflowY: 'auto' }}>
        
        {signals.length === 0 ? (
          <div style={{ padding: '1rem', color: 'var(--text-muted)', fontStyle: 'italic', fontSize: '0.8rem' }}>
            No evidence signals tracks found.
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
                {/* Header */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: '0.95rem', fontWeight: 700, color: '#fff' }}>
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

                {/* Presence timeline dots row */}
                <div>
                  <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.35rem' }}>
                    Presence Timeline Sequence
                  </span>

                  <div style={{ display: 'flex', gap: '0.4rem' }}>
                    {sig.presence_sequence.map((present, sIdx) => (
                      <div
                        key={sIdx}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '0.2rem',
                          padding: '0.25rem 0.5rem',
                          borderRadius: '4px',
                          backgroundColor: present ? '#10b98115' : '#ef444415',
                          border: `1px solid ${present ? '#10b98133' : '#ef444433'}`,
                          fontSize: '0.65rem',
                          color: present ? '#34d399' : '#f87171'
                        }}
                      >
                        {present ? <Check size={10} /> : <X size={10} />} Snap #{sIdx + 1}
                      </div>
                    ))}
                  </div>
                </div>

                {/* Additional stats */}
                <div style={{ display: 'flex', gap: '1rem', fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                  <div>Persistence Ratio: <b style={{ color: '#fff' }}>{Math.round(sig.persistence_ratio * 100)}%</b></div>
                  <div>Final Reinforcement: <b style={{ color: '#fff' }}>{sig.reinforcement_sequence[sig.reinforcement_sequence.length - 1].toFixed(2)}</b></div>
                </div>

              </div>
            );
          })
        )}

      </div>
    </Card>
  );
};
