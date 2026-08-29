import React from 'react';
import { Card } from '../common/Card';
import { PrescriptionLongitudinalProfile } from '../../types/api';

interface LongitudinalOverviewProps {
  profile: PrescriptionLongitudinalProfile;
}

export const LongitudinalOverview: React.FC<LongitudinalOverviewProps> = ({ profile }) => {
  const getScoreColor = (level: string) => {
    switch (level) {
      case 'HIGH_CONTINUITY': return '#10b981';
      case 'GRADUAL_EVOLUTION': return '#3b82f6';
      case 'MAJOR_ANALYTICAL_TRANSITION': return '#f59e0b';
      default: return '#ef4444';
    }
  };

  return (
    <Card title="Prescription History Evolution Overview" subtitle="General parameters of ordered analysis history">
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1.25rem' }}>
        
        <div style={{ padding: '1rem', borderRadius: '6px', backgroundColor: '#0c1020', border: '1px solid #1e293b' }}>
          <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', display: 'block', textTransform: 'uppercase', fontWeight: 600 }}>Total snapshots</span>
          <span style={{ fontSize: '1.6rem', fontWeight: 800, color: '#fff', display: 'block', marginTop: '0.25rem' }}>
            {profile.timeline.length}
          </span>
        </div>

        <div style={{ padding: '1rem', borderRadius: '6px', backgroundColor: '#0c1020', border: '1px solid #1e293b' }}>
          <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', display: 'block', textTransform: 'uppercase', fontWeight: 600 }}>Evolution classification</span>
          <span style={{
            fontSize: '0.85rem',
            fontWeight: 700,
            color: getScoreColor(profile.overall_evolution_level),
            display: 'block',
            marginTop: '0.6rem',
            padding: '0.2rem 0.5rem',
            borderRadius: '4px',
            backgroundColor: `${getScoreColor(profile.overall_evolution_level)}10`,
            border: `1px solid ${getScoreColor(profile.overall_evolution_level)}33`,
            textAlign: 'center'
          }}>
            {profile.overall_evolution_level.replace(/_/g, ' ')}
          </span>
        </div>

        <div style={{ padding: '1rem', borderRadius: '6px', backgroundColor: '#0c1020', border: '1px solid #1e293b' }}>
          <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', display: 'block', textTransform: 'uppercase', fontWeight: 600 }}>Major change points</span>
          <span style={{ fontSize: '1.6rem', fontWeight: 800, color: '#fff', display: 'block', marginTop: '0.25rem' }}>
            {profile.change_points.length}
          </span>
        </div>

        <div style={{ padding: '1rem', borderRadius: '6px', backgroundColor: '#0c1020', border: '1px solid #1e293b' }}>
          <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', display: 'block', textTransform: 'uppercase', fontWeight: 600 }}>Entity persistence tracks</span>
          <span style={{ fontSize: '1.6rem', fontWeight: 800, color: '#fff', display: 'block', marginTop: '0.25rem' }}>
            {profile.persistence_profiles.length}
          </span>
        </div>

      </div>
    </Card>
  );
};
