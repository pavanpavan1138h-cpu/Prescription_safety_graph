import React, { useState } from 'react';
import { PrescriptionTrustworthinessProfile } from '../../types/api';
import { TrustworthinessGuardrail } from './TrustworthinessGuardrail';
import { TrustworthinessOverview } from './TrustworthinessOverview';
import { ReproducibilityProfileView } from './ReproducibilityProfileView';
import { InputPerturbationMatrix } from './InputPerturbationMatrix';
import { StructuralRobustnessView } from './StructuralRobustnessView';
import { SignalRobustnessView } from './SignalRobustnessView';
import { CrossLayerConsistencyView } from './CrossLayerConsistencyView';
import { ProvenanceCompletenessView } from './ProvenanceCompletenessView';
import { ExplanationConsistencyView } from './ExplanationConsistencyView';
import { TrustworthinessNarrative } from './TrustworthinessNarrative';
import { Activity, ShieldCheck, Database, RefreshCw, Layers } from 'lucide-react';

interface PrescriptionTrustworthinessTabProps {
  trustworthiness: PrescriptionTrustworthinessProfile;
}

export const PrescriptionTrustworthinessTab: React.FC<PrescriptionTrustworthinessTabProps> = ({ trustworthiness }) => {
  const [subView, setSubView] = useState<'overview' | 'reproducibility' | 'perturbations' | 'structure' | 'signals' | 'layers'>('overview');

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      
      {/* 1. Guardrail disclaimer banner */}
      <TrustworthinessGuardrail />

      {/* 2. Top level overview metrics card */}
      <TrustworthinessOverview profile={trustworthiness} />

      {/* 3. Navigation Bar */}
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
          <ShieldCheck size={15} /> Overview & Executive Summary
        </button>

        <button
          onClick={() => setSubView('reproducibility')}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem',
            padding: '0.4rem 0.8rem',
            borderRadius: '4px',
            fontSize: '0.8rem',
            fontWeight: 600,
            cursor: 'pointer',
            backgroundColor: subView === 'reproducibility' ? '#1e293b' : 'transparent',
            color: subView === 'reproducibility' ? '#60a5fa' : 'var(--text-muted)',
            border: 'none'
          }}
        >
          <RefreshCw size={15} /> Repeat Repeatability
        </button>

        <button
          onClick={() => setSubView('perturbations')}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem',
            padding: '0.4rem 0.8rem',
            borderRadius: '4px',
            fontSize: '0.8rem',
            fontWeight: 600,
            cursor: 'pointer',
            backgroundColor: subView === 'perturbations' ? '#1e293b' : 'transparent',
            color: subView === 'perturbations' ? '#60a5fa' : 'var(--text-muted)',
            border: 'none'
          }}
        >
          <Activity size={15} /> Input Invariance Matrix
        </button>

        <button
          onClick={() => setSubView('structure')}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem',
            padding: '0.4rem 0.8rem',
            borderRadius: '4px',
            fontSize: '0.8rem',
            fontWeight: 600,
            cursor: 'pointer',
            backgroundColor: subView === 'structure' ? '#1e293b' : 'transparent',
            color: subView === 'structure' ? '#60a5fa' : 'var(--text-muted)',
            border: 'none'
          }}
        >
          <Layers size={15} /> Structural Topology Stability
        </button>

        <button
          onClick={() => setSubView('signals')}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem',
            padding: '0.4rem 0.8rem',
            borderRadius: '4px',
            fontSize: '0.8rem',
            fontWeight: 600,
            cursor: 'pointer',
            backgroundColor: subView === 'signals' ? '#1e293b' : 'transparent',
            color: subView === 'signals' ? '#60a5fa' : 'var(--text-muted)',
            border: 'none'
          }}
        >
          <Activity size={15} /> Evidence Signals persistence
        </button>

        <button
          onClick={() => setSubView('layers')}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem',
            padding: '0.4rem 0.8rem',
            borderRadius: '4px',
            fontSize: '0.8rem',
            fontWeight: 600,
            cursor: 'pointer',
            backgroundColor: subView === 'layers' ? '#1e293b' : 'transparent',
            color: subView === 'layers' ? '#60a5fa' : 'var(--text-muted)',
            border: 'none'
          }}
        >
          <Database size={15} /> Cross-Layer Alignment
        </button>
      </div>

      {/* 4. Active Sub-View Panels */}
      <div>
        {subView === 'overview' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            <TrustworthinessNarrative narrative={trustworthiness.executive_summary} />
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.5rem' }}>
              <ProvenanceCompletenessView provenance={trustworthiness.provenance_completeness} />
              <ExplanationConsistencyView explanation={trustworthiness.explanation_consistency} />
            </div>
          </div>
        )}

        {subView === 'reproducibility' && (
          <ReproducibilityProfileView reproducibility={trustworthiness.reproducibility_profile} />
        )}

        {subView === 'perturbations' && (
          <InputPerturbationMatrix perturbations={trustworthiness.input_perturbation_results} />
        )}

        {subView === 'structure' && (
          <StructuralRobustnessView structure={trustworthiness.structural_robustness} />
        )}

        {subView === 'signals' && (
          <SignalRobustnessView signals={trustworthiness.signal_robustness_profiles} />
        )}

        {subView === 'layers' && (
          <CrossLayerConsistencyView consistency={trustworthiness.cross_layer_consistency} />
        )}
      </div>

    </div>
  );
};
