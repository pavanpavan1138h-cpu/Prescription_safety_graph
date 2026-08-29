import React from 'react';
import { Card } from '../common/Card';
import { PrescriptionTrustworthinessProfile } from '../../types/api';
import { Gauge, CheckSquare, Layers, HelpCircle } from 'lucide-react';

interface TrustworthinessOverviewProps {
  profile: PrescriptionTrustworthinessProfile;
}

export const TrustworthinessOverview: React.FC<TrustworthinessOverviewProps> = ({ profile }) => {
  const overallMetric = profile.trustworthiness_metrics.find(m => m.metric_id === 'METRIC_REPRODUCIBILITY') || profile.trustworthiness_metrics[0];
  const totalScore = profile.trustworthiness_metrics.reduce((acc, m) => acc + m.normalized_value, 0) / profile.trustworthiness_metrics.length;
  const overallPercent = Math.round(totalScore * 100);

  const getScoreColor = (score: number) => {
    if (score >= 0.80) return '#3b82f6'; // Sleek dark blue
    if (score >= 0.60) return '#10b981'; // Green
    if (score >= 0.40) return '#f59e0b'; // Amber
    return '#ef4444'; // Red
  };

  return (
    <Card title="Computational Trustworthiness Evaluation" subtitle="Audit matrix analyzing deterministic reproducibility and stability metrics">
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.5rem' }}>
        
        {/* Score Dial Column */}
        <div style={{
          padding: '1.25rem',
          borderRadius: '8px',
          backgroundColor: '#0c1020',
          border: '1px solid #1e293b',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          textAlign: 'center',
          gap: '1rem'
        }}>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>
            Overall Robustness Level
          </span>

          <div style={{
            width: '120px',
            height: '120px',
            borderRadius: '50%',
            border: `6px solid ${getScoreColor(totalScore)}33`,
            borderTopColor: getScoreColor(totalScore),
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexDirection: 'column'
          }}>
            <span style={{ fontSize: '1.8rem', fontWeight: 800, color: '#fff' }}>
              {overallPercent}%
            </span>
            <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>Score Index</span>
          </div>

          <span style={{
            fontSize: '0.75rem',
            fontWeight: 700,
            padding: '0.2rem 0.6rem',
            borderRadius: '4px',
            backgroundColor: `${getScoreColor(totalScore)}15`,
            color: getScoreColor(totalScore),
            border: `1px solid ${getScoreColor(totalScore)}33`
          }}>
            {profile.overall_trustworthiness_level.replace(/_/g, ' ')}
          </span>
        </div>

        {/* Detailed Breakdown Column */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 650, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Robustness Weight Breakdown
          </span>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            {profile.trustworthiness_metrics.map((m, idx) => {
              const valPercent = Math.round(m.normalized_value * 100);
              return (
                <div key={`${m.metric_id}-${idx}`} style={{ padding: '0.6rem 0.85rem', borderRadius: '6px', backgroundColor: '#090b14', border: '1px solid #1e293b' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', marginBottom: '0.35rem' }}>
                    <span style={{ color: '#fff', fontWeight: 500 }}>{m.metric_name}</span>
                    <span style={{ color: '#93c5fd', fontWeight: 600 }}>{valPercent}%</span>
                  </div>
                  <div style={{ height: '4px', borderRadius: '2px', backgroundColor: '#1e293b', overflow: 'hidden' }}>
                    <div style={{ height: '100%', width: `${valPercent}%`, backgroundColor: getScoreColor(m.normalized_value) }} />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

      </div>
    </Card>
  );
};
