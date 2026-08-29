import React from 'react';
import { Card } from '../common/Card';
import { LongitudinalChangePoint } from '../../types/api';
import { RefreshCw } from 'lucide-react';

interface ChangePointViewProps {
  changePoints: LongitudinalChangePoint[];
}

export const ChangePointView: React.FC<ChangePointViewProps> = ({ changePoints }) => {
  const getBadgeStyle = (level: string) => {
    switch (level) {
      case 'COMPOSITE_CHANGE_POINT':
        return { bg: '#ef444415', text: '#f87171', border: '#ef444433' };
      case 'MAJOR_CHANGE':
        return { bg: '#f59e0b15', text: '#fbbf24', border: '#f59e0b33' };
      case 'MODERATE_CHANGE':
        return { bg: '#3b82f615', text: '#60a5fa', border: '#3b82f633' };
      default:
        return { bg: '#1e293b', text: '#94a3b8', border: '#1e293b' };
    }
  };

  return (
    <Card title="Timeline Transition Change-Points" subtitle="Aggregate computational shifts between adjacent analytical states">
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', maxHeight: '400px', overflowY: 'auto' }}>
        
        {changePoints.length === 0 ? (
          <div style={{ padding: '1rem', color: 'var(--text-muted)', fontStyle: 'italic', fontSize: '0.8rem' }}>
            No transition transitions logged.
          </div>
        ) : (
          changePoints.map((cp, idx) => {
            const b = getBadgeStyle(cp.change_level);
            return (
              <div
                key={idx}
                style={{
                  padding: '1.25rem',
                  borderRadius: '6px',
                  backgroundColor: '#0c1020',
                  border: '1px solid #1e293b',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '0.75rem'
                }}
              >
                {/* Header */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: '0.9rem', fontWeight: 700, color: '#fff', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                    Snapshot #{cp.from_snapshot_index + 1} <RefreshCw size={12} style={{ color: 'var(--text-muted)' }} /> Snapshot #{cp.to_snapshot_index + 1}
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
                    {cp.change_level.replace(/_/g, ' ')} (Score: {cp.aggregate_change_score.toFixed(2)})
                  </span>
                </div>

                {/* Weights Bar Grid */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: '0.6rem', fontSize: '0.7rem' }}>
                  
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-muted)', marginBottom: '0.15rem' }}>
                      <span>Meds Set Delta</span>
                      <span>{Math.round(cp.medication_set_change * 100)}%</span>
                    </div>
                    <div style={{ height: '3px', backgroundColor: '#1e293b', borderRadius: '1px' }}>
                      <div style={{ height: '100%', width: `${cp.medication_set_change * 100}%`, backgroundColor: '#3b82f6' }} />
                    </div>
                  </div>

                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-muted)', marginBottom: '0.15rem' }}>
                      <span>Structural Delta</span>
                      <span>{Math.round(cp.structural_change * 100)}%</span>
                    </div>
                    <div style={{ height: '3px', backgroundColor: '#1e293b', borderRadius: '1px' }}>
                      <div style={{ height: '100%', width: `${cp.structural_change * 100}%`, backgroundColor: '#10b981' }} />
                    </div>
                  </div>

                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-muted)', marginBottom: '0.15rem' }}>
                      <span>Evidential Delta</span>
                      <span>{Math.round(cp.signal_change * 100)}%</span>
                    </div>
                    <div style={{ height: '3px', backgroundColor: '#1e293b', borderRadius: '1px' }}>
                      <div style={{ height: '100%', width: `${cp.signal_change * 100}%`, backgroundColor: '#a855f7' }} />
                    </div>
                  </div>

                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-muted)', marginBottom: '0.15rem' }}>
                      <span>Stability Delta</span>
                      <span>{Math.round(cp.stability_change * 100)}%</span>
                    </div>
                    <div style={{ height: '3px', backgroundColor: '#1e293b', borderRadius: '1px' }}>
                      <div style={{ height: '100%', width: `${cp.stability_change * 100}%`, backgroundColor: '#f59e0b' }} />
                    </div>
                  </div>

                </div>

                {cp.contributing_dimensions.length > 0 && (
                  <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>
                    Contributing Dimensions: <b style={{ color: '#fff' }}>{cp.contributing_dimensions.join(', ')}</b>
                  </div>
                )}

              </div>
            );
          })
        )}

      </div>
    </Card>
  );
};
