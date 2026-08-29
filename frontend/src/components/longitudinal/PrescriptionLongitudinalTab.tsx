import React, { useState } from 'react';
import { PrescriptionLongitudinalProfile } from '../../types/api';
import { LongitudinalGuardrail } from './LongitudinalGuardrail';
import { LongitudinalOverview } from './LongitudinalOverview';
import { SnapshotTimeline } from './SnapshotTimeline';
import { PersistenceView } from './PersistenceView';
import { EmergenceView } from './EmergenceView';
import { DisappearanceView } from './DisappearanceView';
import { ChangePointView } from './ChangePointView';
import { StructuralEvolutionView } from './StructuralEvolutionView';
import { SignalEvolutionView } from './SignalEvolutionView';
import { StabilityEvolutionView } from './StabilityEvolutionView';
import { TrustworthinessEvolutionView } from './TrustworthinessEvolutionView';
import { CrossLayerEvolutionView } from './CrossLayerEvolutionView';
import { LongitudinalNarrative } from './LongitudinalNarrative';
import { ShieldCheck, Calendar, Eye, Layers, TrendingUp, Radio } from 'lucide-react';

interface PrescriptionLongitudinalTabProps {
  longitudinal: PrescriptionLongitudinalProfile;
}

export const PrescriptionLongitudinalTab: React.FC<PrescriptionLongitudinalTabProps> = ({ longitudinal }) => {
  const [subView, setSubView] = useState<'overview' | 'timeline' | 'persistence' | 'transitions' | 'tracks'>('overview');

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      
      {/* 1. Guardrail disclaimer */}
      <LongitudinalGuardrail />

      {/* 2. Top Overview Cards */}
      <LongitudinalOverview profile={longitudinal} />

      {/* 3. Navigation menu buttons */}
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
          <ShieldCheck size={15} /> Evolution Narrative
        </button>

        <button
          onClick={() => setSubView('timeline')}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem',
            padding: '0.4rem 0.8rem',
            borderRadius: '4px',
            fontSize: '0.8rem',
            fontWeight: 600,
            cursor: 'pointer',
            backgroundColor: subView === 'timeline' ? '#1e293b' : 'transparent',
            color: subView === 'timeline' ? '#60a5fa' : 'var(--text-muted)',
            border: 'none'
          }}
        >
          <Calendar size={15} /> Snapshot Timeline
        </button>

        <button
          onClick={() => setSubView('persistence')}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem',
            padding: '0.4rem 0.8rem',
            borderRadius: '4px',
            fontSize: '0.8rem',
            fontWeight: 600,
            cursor: 'pointer',
            backgroundColor: subView === 'persistence' ? '#1e293b' : 'transparent',
            color: subView === 'persistence' ? '#60a5fa' : 'var(--text-muted)',
            border: 'none'
          }}
        >
          <Eye size={15} /> Entity Persistence
        </button>

        <button
          onClick={() => setSubView('transitions')}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem',
            padding: '0.4rem 0.8rem',
            borderRadius: '4px',
            fontSize: '0.8rem',
            fontWeight: 600,
            cursor: 'pointer',
            backgroundColor: subView === 'transitions' ? '#1e293b' : 'transparent',
            color: subView === 'transitions' ? '#60a5fa' : 'var(--text-muted)',
            border: 'none'
          }}
        >
          <Layers size={15} /> Change Points & Transitions
        </button>

        <button
          onClick={() => setSubView('tracks')}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem',
            padding: '0.4rem 0.8rem',
            borderRadius: '4px',
            fontSize: '0.8rem',
            fontWeight: 600,
            cursor: 'pointer',
            backgroundColor: subView === 'tracks' ? '#1e293b' : 'transparent',
            color: subView === 'tracks' ? '#60a5fa' : 'var(--text-muted)',
            border: 'none'
          }}
        >
          <TrendingUp size={15} /> Multi-Layer Tracks
        </button>
      </div>

      {/* 4. Sub-View Panels mounting point */}
      <div>
        {subView === 'overview' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            <LongitudinalNarrative narrative={longitudinal.longitudinal_summary} />
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(285px, 1fr))', gap: '1.5rem' }}>
              <EmergenceView emergences={longitudinal.emergence_events} />
              <DisappearanceView disappearances={longitudinal.disappearance_events} />
            </div>
          </div>
        )}

        {subView === 'timeline' && (
          <SnapshotTimeline timeline={longitudinal.timeline} />
        )}

        {subView === 'persistence' && (
          <PersistenceView profiles={longitudinal.persistence_profiles} />
        )}

        {subView === 'transitions' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            <ChangePointView changePoints={longitudinal.change_points} />
            <CrossLayerEvolutionView crossLayer={longitudinal.cross_layer_evolution} />
          </div>
        )}

        {subView === 'tracks' && (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem' }}>
            <StructuralEvolutionView structure={longitudinal.structural_evolution} />
            <SignalEvolutionView signals={longitudinal.signal_evolution} />
            <StabilityEvolutionView stability={longitudinal.stability_evolution} />
            <TrustworthinessEvolutionView trustworthiness={longitudinal.trustworthiness_evolution} />
          </div>
        )}
      </div>

    </div>
  );
};
