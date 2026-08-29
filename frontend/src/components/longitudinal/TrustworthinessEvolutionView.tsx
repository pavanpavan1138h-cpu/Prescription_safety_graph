import React from 'react';
import { Card } from '../common/Card';
import { TrustworthinessEvolutionProfile } from '../../types/api';
import { TrendingUp, TrendingDown, RefreshCw } from 'lucide-react';

interface TrustworthinessEvolutionViewProps {
  trustworthiness: TrustworthinessEvolutionProfile;
}

export const TrustworthinessEvolutionView: React.FC<TrustworthinessEvolutionViewProps> = ({ trustworthiness }) => {
  const getBadgeStyle = (level: string) => {
    switch (level) {
      case 'CONSISTENTLY_HIGH':
      case 'IMPROVING':
        return { bg: '#10b98115', text: '#34d399', border: '#10b98133' };
      case 'DECLINING':
        return { bg: '#ef444415', text: '#f87171', border: '#ef444433' };
      default:
        return { bg: '#1e293b', text: '#94a3b8', border: '#1e293b' };
    }
  };

  const b = getBadgeStyle(trustworthiness.classification);

  return (
    <Card title="Computational Trustworthiness Evolution" subtitle="Monitors repeat consistency indexes and score delta history">
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.2rem' }}>
        
        {/* Trend summary header */}
        <div style={{
          padding: '1rem',
          borderRadius: '6px',
          backgroundColor: '#0c1020',
          border: '1px solid #1e293b',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <div>
            <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Trust Progression</span>
            <span style={{ fontSize: '1rem', fontWeight: 700, color: '#fff', display: 'block', marginTop: '0.2rem' }}>
              {trustworthiness.classification.replace(/_/g, ' ')}
            </span>
          </div>

          <span style={{
            fontSize: '0.65rem',
            fontWeight: 700,
            padding: '0.2rem 0.5rem',
            borderRadius: '4px',
            backgroundColor: b.bg,
            color: b.text,
            border: `1px solid ${b.border}`
          }}>
            {trustworthiness.classification}
          </span>
        </div>

        {/* Breakdown parameters */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: '1rem' }}>
          
          <div style={{ padding: '0.75rem', borderRadius: '6px', backgroundColor: '#090b14', border: '1px solid #1e293b' }}>
            <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.25rem' }}>Mean Trust Score</span>
            <span style={{ fontSize: '1.1rem', fontWeight: 800, color: '#fff' }}>
              {Math.round(trustworthiness.mean_score * 100)}%
            </span>
          </div>

          <div style={{ padding: '0.75rem', borderRadius: '6px', backgroundColor: '#090b14', border: '1px solid #1e293b' }}>
            <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.25rem' }}>Score Volatility</span>
            <span style={{ fontSize: '1.1rem', fontWeight: 800, color: '#93c5fd' }}>
              {trustworthiness.score_volatility.toFixed(3)}
            </span>
          </div>

        </div>

        {/* Score Sequence chart grid */}
        <div>
          <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600, display: 'block', marginBottom: '0.5rem' }}>
            Score Progression Sequence
          </span>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
            {trustworthiness.score_sequence.map((score, idx) => (
              <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', padding: '0.4rem 0.6rem', backgroundColor: '#090b14', borderRadius: '4px' }}>
                <span style={{ color: 'var(--text-muted)' }}>Snapshot #{idx + 1} ({trustworthiness.level_sequence[idx]?.replace(/_/g, ' ') || 'Moderate'})</span>
                <span style={{ color: '#60a5fa', fontWeight: 650 }}>{Math.round(score * 100)}%</span>
              </div>
            ))}
          </div>
        </div>

      </div>
    </Card>
  );
};
