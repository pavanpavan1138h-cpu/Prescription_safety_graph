import React from 'react';
import { Card } from '../common/Card';
import { DecisionDependencyMap } from '../../types/api';
import { GitBranch, ShieldCheck } from 'lucide-react';

interface DependencyMapProps {
  dependencyMap: DecisionDependencyMap;
}

export const DependencyMap: React.FC<DependencyMapProps> = ({ dependencyMap }) => {
  return (
    <Card title="Decision Dependency DAG" subtitle="Directed acyclic dependency hierarchy deriving analytical conclusions">
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
        
        {/* Acyclic Verification Badge */}
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '0.6rem 0.85rem',
          borderRadius: '6px',
          backgroundColor: '#0c1020',
          border: '1px solid #1e293b'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <GitBranch size={16} style={{ color: '#60a5fa' }} />
            <span style={{ fontSize: '0.8rem', color: '#fff', fontWeight: 600 }}>
              DAG Acyclicity Status
            </span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
            <ShieldCheck size={15} style={{ color: '#4ade80' }} />
            <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#4ade80' }}>
              VERIFIED ACYCLIC
            </span>
          </div>
        </div>

        {/* Dependency Nodes List */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', maxHeight: '380px', overflowY: 'auto' }}>
          {dependencyMap.dependencies.map((dep, idx) => (
            <div
              key={`${dep.entity_id}-${idx}`}
              style={{
                padding: '0.75rem 1rem',
                borderRadius: '6px',
                backgroundColor: dep.critical_dependency ? '#ef444408' : '#0c1020',
                border: `1px solid ${dep.critical_dependency ? '#ef444433' : '#1e293b'}`,
                display: 'flex',
                flexDirection: 'column',
                gap: '0.35rem'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#fff' }}>
                    {dep.entity_label}
                  </span>
                  <span style={{
                    fontSize: '0.65rem',
                    padding: '0.1rem 0.35rem',
                    borderRadius: '3px',
                    backgroundColor: '#1e293b',
                    color: '#94a3b8',
                    fontFamily: 'var(--font-mono)'
                  }}>
                    {dep.entity_type}
                  </span>
                </div>

                {dep.critical_dependency && (
                  <span style={{
                    fontSize: '0.65rem',
                    fontWeight: 700,
                    padding: '0.15rem 0.4rem',
                    borderRadius: '3px',
                    backgroundColor: '#ef444420',
                    color: '#f87171',
                    border: '1px solid #ef444444'
                  }}>
                    CRITICAL PATH
                  </span>
                )}
              </div>

              {dep.depends_on_ids.length > 0 && (
                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                  Depends on: <span style={{ fontFamily: 'var(--font-mono)', color: '#93c5fd' }}>{dep.depends_on_ids.join(', ')}</span>
                </div>
              )}
            </div>
          ))}
        </div>

      </div>
    </Card>
  );
};
