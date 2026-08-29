import React from 'react';
import { Card } from '../common/Card';
import { StructuralRobustnessProfile } from '../../types/api';
import { GitBranch } from 'lucide-react';

interface StructuralRobustnessViewProps {
  structure: StructuralRobustnessProfile;
}

export const StructuralRobustnessView: React.FC<StructuralRobustnessViewProps> = ({ structure }) => {
  const topoPercent = Math.round(structure.topology_persistence_ratio * 100);
  const clusterPercent = Math.round(structure.cluster_persistence_ratio * 100);
  const centralPercent = Math.round(structure.central_participant_persistence * 100);

  return (
    <Card title="Structural Topology Invariance & Persistence" subtitle="Tracks the persistence of graph structures across perturbation scenarios">
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.2rem' }}>
        
        {/* Topology Classification Info */}
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
            <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Baseline Topology</span>
            <span style={{ fontSize: '1rem', fontWeight: 700, color: '#fff', display: 'block', marginTop: '0.2rem' }}>
              {structure.baseline_topology.replace(/_/g, ' ')}
            </span>
          </div>

          <span style={{
            fontSize: '0.75rem',
            fontWeight: 700,
            padding: '0.2rem 0.5rem',
            borderRadius: '4px',
            backgroundColor: '#3b82f615',
            color: '#60a5fa',
            border: '1px solid #3b82f633'
          }}>
            {structure.robustness_level.replace(/_/g, ' ')}
          </span>
        </div>

        {/* Persistence Metrics */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          
          {/* Topo Persistence */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: '0.35rem' }}>
              <span style={{ color: '#fff', fontWeight: 500 }}>Topology Type Persistence</span>
              <span style={{ color: '#60a5fa', fontWeight: 600 }}>{topoPercent}%</span>
            </div>
            <div style={{ height: '5px', borderRadius: '3px', backgroundColor: '#1e293b', overflow: 'hidden' }}>
              <div style={{ height: '100%', width: `${topoPercent}%`, backgroundColor: '#3b82f6' }} />
            </div>
          </div>

          {/* Cluster Persistence */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: '0.35rem' }}>
              <span style={{ color: '#fff', fontWeight: 500 }}>Cluster Persistence Score</span>
              <span style={{ color: '#10b981', fontWeight: 600 }}>{clusterPercent}%</span>
            </div>
            <div style={{ height: '5px', borderRadius: '3px', backgroundColor: '#1e293b', overflow: 'hidden' }}>
              <div style={{ height: '100%', width: `${clusterPercent}%`, backgroundColor: '#10b981' }} />
            </div>
          </div>

          {/* Hub Persistence */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: '0.35rem' }}>
              <span style={{ color: '#fff', fontWeight: 500 }}>Hub Participant Persistence</span>
              <span style={{ color: '#a855f7', fontWeight: 600 }}>{centralPercent}%</span>
            </div>
            <div style={{ height: '5px', borderRadius: '3px', backgroundColor: '#1e293b', overflow: 'hidden' }}>
              <div style={{ height: '100%', width: `${centralPercent}%`, backgroundColor: '#a855f7' }} />
            </div>
          </div>

        </div>

      </div>
    </Card>
  );
};
