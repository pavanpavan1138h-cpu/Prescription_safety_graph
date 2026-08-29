import React, { useState } from 'react';
import { PrescriptionExplainabilityProfile } from '../../types/api';
import { ExplainabilityGuardrail } from './ExplainabilityGuardrail';
import { TraceabilityMetrics } from './TraceabilityMetrics';
import { ContributorRanking } from './ContributorRanking';
import { ProvenanceTimeline } from './ProvenanceTimeline';
import { DependencyMap } from './DependencyMap';
import { ExplanationOverview } from './ExplanationOverview';
import { ExplanationGraphView } from './ExplanationGraphView';
import { FileText, Award, Database, GitFork, Network } from 'lucide-react';

interface PrescriptionExplainabilityTabProps {
  explainability: PrescriptionExplainabilityProfile;
}

export const PrescriptionExplainabilityTab: React.FC<PrescriptionExplainabilityTabProps> = ({ explainability }) => {
  const [subView, setSubView] = useState<'overview' | 'contributors' | 'provenance' | 'dependencies' | 'graph'>('overview');

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      
      {/* 1. Scientific & Ethical Guardrail Banner */}
      <ExplainabilityGuardrail />

      {/* 2. Top-Level Traceability Metrics Bar */}
      <TraceabilityMetrics traceability={explainability.traceability_profile} />

      {/* 3. Sub-navigation tabs */}
      <div style={{
        display: 'flex',
        gap: '0.5rem',
        borderBottom: '1px solid #1e293b',
        paddingBottom: '0.5rem',
        overflowX: 'auto'
      }}>
        <button
          onClick={() => setSubView('overview')}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem',
            padding: '0.4rem 0.8rem',
            borderRadius: '4px',
            fontSize: '0.8rem',
            fontWeight: 600,
            cursor: 'pointer',
            backgroundColor: subView === 'overview' ? '#1e293b' : 'transparent',
            color: subView === 'overview' ? '#60a5fa' : 'var(--text-muted)',
            border: 'none'
          }}
        >
          <FileText size={15} /> Derivation & Claims
        </button>

        <button
          onClick={() => setSubView('contributors')}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem',
            padding: '0.4rem 0.8rem',
            borderRadius: '4px',
            fontSize: '0.8rem',
            fontWeight: 600,
            cursor: 'pointer',
            backgroundColor: subView === 'contributors' ? '#1e293b' : 'transparent',
            color: subView === 'contributors' ? '#60a5fa' : 'var(--text-muted)',
            border: 'none'
          }}
        >
          <Award size={15} /> Contributor Rankings ({explainability.contribution_profiles.length})
        </button>

        <button
          onClick={() => setSubView('provenance')}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem',
            padding: '0.4rem 0.8rem',
            borderRadius: '4px',
            fontSize: '0.8rem',
            fontWeight: 600,
            cursor: 'pointer',
            backgroundColor: subView === 'provenance' ? '#1e293b' : 'transparent',
            color: subView === 'provenance' ? '#60a5fa' : 'var(--text-muted)',
            border: 'none'
          }}
        >
          <Database size={15} /> Grounded Provenance ({explainability.provenance_records.length})
        </button>

        <button
          onClick={() => setSubView('dependencies')}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem',
            padding: '0.4rem 0.8rem',
            borderRadius: '4px',
            fontSize: '0.8rem',
            fontWeight: 600,
            cursor: 'pointer',
            backgroundColor: subView === 'dependencies' ? '#1e293b' : 'transparent',
            color: subView === 'dependencies' ? '#60a5fa' : 'var(--text-muted)',
            border: 'none'
          }}
        >
          <GitFork size={15} /> Decision DAG
        </button>

        <button
          onClick={() => setSubView('graph')}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem',
            padding: '0.4rem 0.8rem',
            borderRadius: '4px',
            fontSize: '0.8rem',
            fontWeight: 600,
            cursor: 'pointer',
            backgroundColor: subView === 'graph' ? '#1e293b' : 'transparent',
            color: subView === 'graph' ? '#60a5fa' : 'var(--text-muted)',
            border: 'none'
          }}
        >
          <Network size={15} /> Explanation Graph ({explainability.explanation_graph.nodes.length} Nodes)
        </button>
      </div>

      {/* 4. Active Sub-View Content */}
      <div>
        {subView === 'overview' && (
          <ExplanationOverview
            narrative={explainability.narrative}
            structuredClaims={explainability.structured_claims}
          />
        )}

        {subView === 'contributors' && (
          <ContributorRanking contributors={explainability.contribution_profiles} />
        )}

        {subView === 'provenance' && (
          <ProvenanceTimeline provenanceRecords={explainability.provenance_records} />
        )}

        {subView === 'dependencies' && (
          <DependencyMap dependencyMap={explainability.dependency_map} />
        )}

        {subView === 'graph' && (
          <ExplanationGraphView graph={explainability.explanation_graph} />
        )}
      </div>

    </div>
  );
};
