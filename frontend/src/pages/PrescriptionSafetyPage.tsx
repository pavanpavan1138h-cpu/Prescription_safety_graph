import React, { useState, useEffect } from 'react';
import { AppShell } from '../components/layout/AppShell';
import { MedicationInput } from '../components/prescription/MedicationInput';
import { usePrescriptionAnalysis } from '../hooks/usePrescriptionAnalysis';
import { useGraphData } from '../hooks/useGraphData';
import { prescriptionApi } from '../api/client';
import { SystemInfoResponse } from '../types/api';
import { ActiveTab } from '../types/ui';

// Structural components (Phase 8)
import { StructuralGuardrail } from '../components/structural/StructuralGuardrail';
import { TopologyOverview } from '../components/structural/TopologyOverview';
import { StructuralContributorRanking } from '../components/structural/StructuralContributorRanking';
import { EvidenceClusters } from '../components/structural/EvidenceClusters';
import { CounterfactualExplorer } from '../components/structural/CounterfactualExplorer';

// Intelligence components (Phase 9)
import { IntelligenceGuardrail } from '../components/intelligence/IntelligenceGuardrail';
import { SignalThemesOverview } from '../components/intelligence/SignalThemesOverview';
import { CrossPairSignalsList } from '../components/intelligence/CrossPairSignalsList';
import { ConcentrationAnalysis } from '../components/intelligence/ConcentrationAnalysis';
import { StructuralEvidenceAlignmentView } from '../components/intelligence/StructuralEvidenceAlignmentView';

// Contextual components (Phase 10)
import { ContextualGuardrail } from '../components/contextual/ContextualGuardrail';
import { ScenarioProfilesList } from '../components/contextual/ScenarioProfilesList';
import { StabilityMetricsSummary } from '../components/contextual/StabilityMetricsSummary';
import { DrugDependencyImpacts } from '../components/contextual/DrugDependencyImpacts';
import { SignalPersistenceList } from '../components/contextual/SignalPersistenceList';

// Comparative components (Phase 11)
import { ComparativeGuardrail } from '../components/comparison/ComparativeGuardrail';
import { ComparisonInputPanel } from '../components/comparison/ComparisonInputPanel';
import { MedicationSetComparisonView } from '../components/comparison/MedicationSetComparisonView';
import { ComparisonOverview } from '../components/comparison/ComparisonOverview';
import { EvidenceDeltaView } from '../components/comparison/EvidenceDeltaView';
import { StructuralDeltaView } from '../components/comparison/StructuralDeltaView';
import { SignalDeltaView } from '../components/comparison/SignalDeltaView';
import { StabilityDeltaView } from '../components/comparison/StabilityDeltaView';
import { ComparisonNarrative } from '../components/comparison/ComparisonNarrative';

// Explainability component (Phase 11)
import { PrescriptionExplainabilityTab } from '../components/explainability/PrescriptionExplainabilityTab';

// Trustworthiness component (Phase 12)
import { PrescriptionTrustworthinessTab } from '../components/trustworthiness/PrescriptionTrustworthinessTab';

// Longitudinal component (Phase 13)
import { PrescriptionLongitudinalTab } from '../components/longitudinal/PrescriptionLongitudinalTab';

import { Card } from '../components/common/Card';

// Interactive Graph component
import { InteractiveGraph } from '../components/graph/InteractiveGraph';

// Icon imports
import {
  Shield,
  FileText,
  Network,
  Share2,
  LineChart,
  Brain,
  ChevronRight,
  Database,
  ArrowRightLeft,
  Search,
  BookOpen,
  RefreshCw,
  Sparkles,
  FileCheck,
  ShieldCheck
} from 'lucide-react';
import {
  formatEvidenceStatus,
  getEvidenceBadgeColor,
  getPriorityBadgeColor,
  formatDate
} from '../utils/formatters';

export const PrescriptionSafetyPage: React.FC = () => {
  const [systemInfo, setSystemInfo] = useState<SystemInfoResponse | null>(null);
  const [activeTab, setActiveTab] = useState<ActiveTab>('intelligence');

  const {
    medications,
    addMedication,
    removeMedication,
    analysisData,
    loading,
    errorMsg,
    runAnalysis,
    resetAnalysis,
    selectedPairId,
    selectedPairDetail,
    loadingPairDetail,
    selectPair,
    closePairDetail
  } = usePrescriptionAnalysis();

  // Load graph hook when analysis becomes available
  const {
    graphType,
    setGraphType,
    subgraph,
    loading: loadingGraph,
    sideEffectLimit,
    setSideEffectLimit
  } = useGraphData(analysisData?.prescription_report.metadata.analysis_id, selectedPairId);

  const [analysisHistory, setAnalysisHistory] = useState<Array<{ id: string; medications: string[] }>>([]);
  const [comparisonProfile, setComparisonProfile] = useState<any | null>(null);
  const [loadingComparison, setLoadingComparison] = useState(false);
  const [comparisonError, setComparisonError] = useState<string | null>(null);
  const [activeComparisonTab, setActiveComparisonTab] = useState<'overview' | 'evidence' | 'structure' | 'signals' | 'stability'>('overview');

  useEffect(() => {
    prescriptionApi.getSystemInfo().then(setSystemInfo).catch(console.error);
  }, []);

  useEffect(() => {
    if (analysisData) {
      const rxId = analysisData.prescription_report.metadata.analysis_id;
      const rxMeds = analysisData.prescription_report.resolution_summary.resolved_drugs.map(
        (d) => d.canonical_name
      );
      setAnalysisHistory((prev) => {
        if (prev.some((item) => item.id === rxId)) return prev;
        return [...prev, { id: rxId, medications: rxMeds }];
      });
    }
  }, [analysisData]);

  const [longitudinalProfile, setLongitudinalProfile] = useState<any | null>(null);
  const [loadingLongitudinal, setLoadingLongitudinal] = useState(false);
  const [longitudinalError, setLongitudinalError] = useState<string | null>(null);

  useEffect(() => {
    if (analysisHistory.length >= 2) {
      setLoadingLongitudinal(true);
      setLongitudinalError(null);
      const aids = analysisHistory.map((h) => h.id);
      prescriptionApi.triggerLongitudinalAnalysis(aids)
        .then(({ longitudinal_id }) => prescriptionApi.getLongitudinalProfile(longitudinal_id))
        .then((profile) => {
          setLongitudinalProfile(profile);
        })
        .catch((err) => {
          setLongitudinalError(err?.message || 'Failed to resolve longitudinal evolution.');
        })
        .finally(() => {
          setLoadingLongitudinal(false);
        });
    }
  }, [analysisHistory]);

  const handleCompare = async (idA: string, idB: string) => {
    setLoadingComparison(true);
    setComparisonError(null);
    try {
      const profile = await prescriptionApi.comparePrescriptions(idA, idB);
      setComparisonProfile(profile);
      setActiveComparisonTab('overview');
    } catch (err: any) {
      setComparisonError(err?.message || 'Failed to compare snapshots.');
    } finally {
      setLoadingComparison(false);
    }
  };

  // Whenever analysis loads, automatically switch to findings/intelligence
  useEffect(() => {
    if (analysisData) {
      setActiveTab('intelligence');
    }
  }, [analysisData]);

  return (
    <AppShell systemInfo={systemInfo}>
      {/* 2 Column Dashboard Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '320px 1fr', gap: '2rem', flex: 1, minHeight: 0 }}>
        {/* Left Column: Side Input Control Panel */}
        <div style={{
          backgroundColor: '#0c0f1d',
          border: '1px solid var(--border-color)',
          borderRadius: '8px',
          padding: '1.5rem',
          height: 'fit-content',
          display: 'flex',
          flexDirection: 'column',
          gap: '1.5rem'
        }}>
          <MedicationInput
            medications={medications}
            onAddMedication={addMedication}
            onRemoveMedication={removeMedication}
            onAnalyze={runAnalysis}
            onReset={resetAnalysis}
            loading={loading}
          />
          
          {errorMsg && (
            <div style={{ padding: '0.75rem', borderRadius: '4px', backgroundColor: '#ef44441a', border: '1px solid #ef444433', color: '#fca5a5', fontSize: '0.8rem' }}>
              {errorMsg}
            </div>
          )}
        </div>

        {/* Right Column: Tab View panel */}
        <div style={{ display: 'flex', flexDirection: 'column', minHeight: 0 }}>
          {!analysisData ? (
            /* Empty State */
            <div style={{
              flex: 1,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              border: '2px dashed var(--border-color)',
              borderRadius: '8px',
              padding: '4rem 2rem',
              textAlign: 'center'
            }}>
              <Brain size={48} style={{ color: '#4b5563', marginBottom: '1rem' }} />
              <h2 style={{ fontSize: '1.25rem', fontWeight: 600, color: '#fff', margin: '0 0 0.5rem 0' }}>
                No Active Prescription Analysis
              </h2>
              <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)', maxWidth: '480px', margin: 0, lineHeight: '1.5' }}>
                Input a combination of medicines on the left and click <b>Analyze Prescription</b> to evaluate direct interactions and combination adverse-event evidence.
              </p>
            </div>
          ) : (
            /* Results Panel */
            <div style={{ display: 'flex', flexDirection: 'column', flex: 1, minHeight: 0 }}>
              {/* Tab Header Controls */}
              <div style={{
                display: 'flex',
                gap: '1.5rem',
                borderBottom: '1px solid var(--border-color)',
                marginBottom: '1.5rem',
                overflowX: 'auto',
                paddingBottom: '0.25rem'
              }}>
                {(
                  [
                    { id: 'intelligence', label: 'Intelligence Overview', icon: Brain },
                    { id: 'explainability', label: 'Traceability & Explainability (Phase 11)', icon: FileCheck },
                    { id: 'trustworthiness', label: 'Computational Trustworthiness (Phase 12)', icon: ShieldCheck },
                    { id: 'longitudinal', label: 'Prescription Evolution (Phase 13)', icon: RefreshCw },
                    { id: 'structure', label: 'Structural Safety (Phase 8)', icon: Network },
                    { id: 'synthesis', label: 'Evidence Synthesis (Phase 9)', icon: Sparkles },
                    { id: 'contextual', label: 'Contextual Stability (Phase 10)', icon: RefreshCw },
                    { id: 'comparison', label: 'Comparative Intelligence', icon: ArrowRightLeft },
                    { id: 'findings', label: 'Pairwise Findings', icon: Shield },
                    { id: 'graph', label: 'Interactive Graph', icon: Share2 },
                    { id: 'convergence', label: 'Event Convergence', icon: LineChart },
                    { id: 'narrative', label: 'Clinical Report', icon: FileText }
                  ] as const
                ).map((tab) => {
                  const Icon = tab.icon;
                  const isActive = activeTab === tab.id;
                  return (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      style={{
                        padding: '0.5rem 0.25rem',
                        fontSize: '0.85rem',
                        fontWeight: 600,
                        backgroundColor: 'transparent',
                        border: 'none',
                        borderBottom: isActive ? '2px solid #8b5cf6' : '2px solid transparent',
                        color: isActive ? '#fff' : 'var(--text-muted)',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem',
                        whiteSpace: 'nowrap',
                        outline: 'none',
                        transition: 'all 0.15s ease'
                      }}
                    >
                      <Icon size={16} />
                      <span>{tab.label}</span>
                    </button>
                  );
                })}
              </div>

              {/* Tab Panels */}
              <div style={{ flex: 1, minHeight: 0 }}>
                
                {/* 1. Intelligence Overview Tab */}
                {activeTab === 'intelligence' && (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                    {/* Executive Summary Card */}
                    <div style={{ backgroundColor: '#0c0f1d', border: '1px solid var(--border-color)', borderRadius: '8px', padding: '1.5rem' }}>
                      <h3 style={{ margin: '0 0 1rem 0', fontSize: '0.95rem', color: '#fff', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <Brain size={16} style={{ color: '#8b5cf6' }} /> Executive Summary
                      </h3>
                      <p style={{ color: '#fff', fontSize: '0.875rem', lineHeight: '1.6', margin: 0 }}>
                        {analysisData.advanced_explanation.executive_summary}
                      </p>
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
                      {/* Left: Complexity profile */}
                      <div style={{ backgroundColor: '#0c0f1d', border: '1px solid var(--border-color)', borderRadius: '8px', padding: '1.5rem' }}>
                        <h3 style={{ margin: '0 0 1rem 0', fontSize: '0.95rem', color: '#fff' }}>Complexity Profile</h3>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', fontSize: '0.85rem' }}>
                          <div>Complexity Category: <b style={{ color: '#fff' }}>{analysisData.complexity_profile.complexity_category}</b></div>
                          <div>Complexity Score: <b style={{ color: '#fff' }}>{analysisData.complexity_profile.complexity_score} / 10</b></div>
                          <div style={{ color: 'var(--text-muted)', lineHeight: '1.4' }}>{analysisData.complexity_profile.explanation}</div>
                        </div>
                      </div>

                      {/* Right: Key Findings */}
                      <div style={{ backgroundColor: '#0c0f1d', border: '1px solid var(--border-color)', borderRadius: '8px', padding: '1.5rem' }}>
                        <h3 style={{ margin: '0 0 1rem 0', fontSize: '0.95rem', color: '#fff' }}>Key Prioritizations</h3>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', fontSize: '0.85rem' }}>
                          <div>Review Findings: <b style={{ color: '#fff' }}>{analysisData.advanced_explanation.key_findings_summary}</b></div>
                          <div>Uncertainty Status: <b style={{ color: '#fff' }}>{analysisData.uncertainty_profile.uncertainty_level}</b></div>
                          <div style={{ color: 'var(--text-muted)', lineHeight: '1.4' }}>{analysisData.uncertainty_profile.explanation_narrative}</div>
                        </div>
                      </div>
                    </div>

                    {/* Scientific Guardrails notices */}
                    <div style={{ border: '1px solid var(--border-color)', borderRadius: '8px', padding: '1.25rem', backgroundColor: '#0f1222' }}>
                      <h4 style={{ margin: '0 0 0.75rem 0', fontSize: '0.8rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-muted)' }}>
                        Analysis Limits & Caveats
                      </h4>
                      <ul style={{ margin: 0, paddingLeft: '1.25rem', fontSize: '0.8rem', color: 'var(--text-muted)', display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                        {analysisData.advanced_explanation.scientific_guardrails.map((g, i) => (
                          <li key={i}>{g}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                )}

                {/* 2. Phase 8 Structural Safety Tab */}
                {activeTab === 'structure' && analysisData.structural_analysis && (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                    {/* Clinical Alert Guardrail Banner */}
                    <StructuralGuardrail warningText={analysisData.structural_analysis.structural_interpretation.clinical_warning} />

                    {/* 2 Column sub-layout for Phase 8 metrics */}
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
                      {/* Left: Global Topology & Counterfactual Removal Selectors */}
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                        <TopologyOverview
                          summary={analysisData.structural_analysis.network_summary}
                          topology={analysisData.structural_analysis.topology}
                          interpretation={analysisData.structural_analysis.structural_interpretation}
                        />
                        <CounterfactualExplorer results={analysisData.structural_analysis.counterfactual_results} />
                      </div>

                      {/* Right: Centrality Rank & Cluster list */}
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                        <StructuralContributorRanking contributors={analysisData.structural_analysis.ranked_structural_contributors} />
                        <EvidenceClusters
                          clusters={analysisData.structural_analysis.clusters}
                          profiles={analysisData.structural_analysis.drug_structural_profiles}
                        />
                      </div>
                    </div>
                  </div>
                )}

                {/* 2.5 Phase 9 Evidence Synthesis Tab */}
                {activeTab === 'synthesis' && analysisData.evidence_intelligence && (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                    {/* Clinical Alert Guardrail Banner */}
                    <IntelligenceGuardrail guardrailText={analysisData.evidence_intelligence.guardrails[0]} />

                    {/* 2 Column sub-layout for Phase 9 metrics */}
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
                      {/* Left: Themes overview & concentration profile */}
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                        <SignalThemesOverview themes={analysisData.evidence_intelligence.themes} />
                        {analysisData.evidence_intelligence.concentration_profile && (
                          <ConcentrationAnalysis profile={analysisData.evidence_intelligence.concentration_profile} />
                        )}
                      </div>

                      {/* Right: Cross-pair convergence & alignment rankings */}
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                        <CrossPairSignalsList
                          signals={analysisData.evidence_intelligence.signal_groups}
                          themes={analysisData.evidence_intelligence.themes}
                        />
                        {analysisData.evidence_intelligence.structural_evidence_alignment && (
                          <StructuralEvidenceAlignmentView alignment={analysisData.evidence_intelligence.structural_evidence_alignment} />
                        )}
                      </div>
                    </div>

                    {/* Executive Clinical Synthesis narrative */}
                    <Card title="Executive Clinical Synthesis Report" subtitle="Template-assembled narrative safety summary">
                      <pre style={{
                        whiteSpace: 'pre-wrap',
                        fontFamily: 'var(--font-mono)',
                        fontSize: '0.85rem',
                        lineHeight: '1.6',
                        color: '#e2e8f0',
                        backgroundColor: '#0f1222',
                        padding: '1.5rem',
                        borderRadius: '6px',
                        border: '1px solid var(--border-color)',
                        margin: 0
                      }}>
                        {analysisData.evidence_intelligence.narrative}
                      </pre>
                    </Card>
                  </div>
                )}

                {/* 2.75 Phase 10 Contextual Stability Tab */}
                {activeTab === 'contextual' && analysisData.contextual_stability && (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                    {/* Clinical Alert Guardrail Banner */}
                    <ContextualGuardrail warningText={analysisData.contextual_stability.guardrails[0]} />

                    {/* 2 Column sub-layout for Phase 10 metrics */}
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
                      {/* Left: Metrics summary & Scenarios list */}
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                        <StabilityMetricsSummary
                          stability={analysisData.contextual_stability.evidence_stability}
                          sensitivity={analysisData.contextual_stability.context_sensitivity}
                          globalLevel={analysisData.contextual_stability.interpretation_stability}
                        />
                        <ScenarioProfilesList scenarios={analysisData.contextual_stability.scenarios} />
                      </div>

                      {/* Right: Drug dependencies & Signal persistence list */}
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                        <DrugDependencyImpacts dependencies={analysisData.contextual_stability.drug_dependencies} />
                        <SignalPersistenceList persistences={analysisData.contextual_stability.signal_persistences} />
                      </div>
                    </div>

                    {/* Executive Contextual Stability narrative */}
                    <Card title="Executive Contextual Stability Report" subtitle="Template-assembled narrative perturbation analysis summary">
                      <pre style={{
                        whiteSpace: 'pre-wrap',
                        fontFamily: 'var(--font-mono)',
                        fontSize: '0.85rem',
                        lineHeight: '1.6',
                        color: '#e2e8f0',
                        backgroundColor: '#0f1222',
                        padding: '1.5rem',
                        borderRadius: '6px',
                        border: '1px solid var(--border-color)',
                        margin: 0
                      }}>
                        {analysisData.contextual_stability.summary_narrative}
                      </pre>
                    </Card>
                  </div>
                )}

                {/* 2.85 Phase 11 Comparative Intelligence Tab */}
                {activeTab === 'comparison' && (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                    <ComparisonInputPanel
                      availableAnalyses={analysisHistory}
                      onCompare={handleCompare}
                      loading={loadingComparison}
                    />

                    {comparisonError && (
                      <div style={{
                        padding: '1rem',
                        borderRadius: '6px',
                        backgroundColor: '#ef44440f',
                        border: '1px solid #ef444433',
                        color: '#f87171',
                        fontSize: '0.85rem'
                      }}>
                        {comparisonError}
                      </div>
                    )}

                    {comparisonProfile && (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                        {/* Clinical Warning Banner */}
                        <ComparativeGuardrail warningText={comparisonProfile.guardrails[0]} />

                        {/* Medication Set Composition Diffs */}
                        <MedicationSetComparisonView medComparison={comparisonProfile.medication_set_comparison} />

                        {/* Inner Comparative Tabs Header */}
                        <div style={{
                          display: 'flex',
                          gap: '1rem',
                          borderBottom: '1px solid #1e293b',
                          marginBottom: '0.5rem',
                          paddingBottom: '0.2rem',
                          overflowX: 'auto'
                        }}>
                          {(['overview', 'evidence', 'structure', 'signals', 'stability'] as const).map((tab) => (
                            <button
                              key={`inner-comp-tab-${tab}`}
                              onClick={() => setActiveComparisonTab(tab)}
                              style={{
                                padding: '0.4rem 0.8rem',
                                fontSize: '0.8rem',
                                fontWeight: 600,
                                backgroundColor: activeComparisonTab === tab ? '#1e293b' : 'transparent',
                                border: 'none',
                                borderRadius: '4px',
                                color: activeComparisonTab === tab ? '#fff' : 'var(--text-muted)',
                                cursor: 'pointer'
                              }}
                            >
                              {tab.toUpperCase()}
                            </button>
                          ))}
                        </div>

                        {/* Inner Tab Panels */}
                        {activeComparisonTab === 'overview' && (
                          <ComparisonOverview profile={comparisonProfile} />
                        )}

                        {activeComparisonTab === 'evidence' && (
                          <EvidenceDeltaView evidenceDelta={comparisonProfile.evidence_delta} />
                        )}

                        {activeComparisonTab === 'structure' && (
                          <StructuralDeltaView structuralDelta={comparisonProfile.structural_delta} />
                        )}

                        {activeComparisonTab === 'signals' && (
                          <SignalDeltaView signalDelta={comparisonProfile.signal_delta} />
                        )}

                        {activeComparisonTab === 'stability' && (
                          <StabilityDeltaView stabilityDelta={comparisonProfile.stability_delta} />
                        )}

                        {/* Template narrative card */}
                        <ComparisonNarrative narrative={comparisonProfile.narrative} />
                      </div>
                    )}
                  </div>
                )}

                {/* 3. Pairwise Findings Tab */}
                {activeTab === 'findings' && (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                    {analysisData.prescription_report.pair_results.length === 0 ? (
                      <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                        No drug combinations evaluated.
                      </div>
                    ) : (
                      analysisData.prescription_report.pair_results.map((pair) => {
                        const badgeColor = getEvidenceBadgeColor(pair.evidence_status);
                        const priorityColor = getPriorityBadgeColor(pair.evidence_priority);
                        return (
                          <div
                            key={pair.pair_id}
                            onClick={() => selectPair(pair.pair_id)}
                            style={{
                              padding: '1.25rem',
                              backgroundColor: '#0c0f1d',
                              border: '1px solid var(--border-color)',
                              borderRadius: '6px',
                              cursor: 'pointer',
                              display: 'flex',
                              justifyContent: 'space-between',
                              alignItems: 'center',
                              transition: 'transform 0.15s ease, border-color 0.15s ease'
                            }}
                          >
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                                <span style={{ fontWeight: 600, color: '#fff', fontSize: '0.95rem' }}>
                                  {pair.drug_a_name} &harr; {pair.drug_b_name}
                                </span>
                              </div>
                              <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                                <span style={{
                                  padding: '0.2rem 0.5rem',
                                  borderRadius: '4px',
                                  backgroundColor: badgeColor.bg,
                                  border: `1px solid ${badgeColor.border}`,
                                  color: badgeColor.text,
                                  fontSize: '0.7rem'
                                }}>
                                  {formatEvidenceStatus(pair.evidence_status)}
                                </span>
                                <span style={{
                                  padding: '0.2rem 0.5rem',
                                  borderRadius: '4px',
                                  backgroundColor: priorityColor.bg,
                                  border: `1px solid ${priorityColor.border}`,
                                  color: priorityColor.text,
                                  fontSize: '0.7rem'
                                }}>
                                  {formatEvidenceStatus(pair.evidence_priority)}
                                </span>
                              </div>
                            </div>

                            <ChevronRight size={18} style={{ color: 'var(--text-muted)' }} />
                          </div>
                        );
                      })
                    )}
                  </div>
                )}

                {/* 4. Interactive Graph Tab */}
                {activeTab === 'graph' && (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', height: '100%' }}>
                    {/* Graph Type Selector */}
                    <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
                      <button
                        onClick={() => setGraphType('overview')}
                        style={{
                          padding: '0.4rem 0.8rem',
                          borderRadius: '4px',
                          backgroundColor: graphType === 'overview' ? '#8b5cf6' : '#1e293b',
                          color: '#fff',
                          border: 'none',
                          fontSize: '0.8rem',
                          cursor: 'pointer'
                        }}
                      >
                        Prescription Overview
                      </button>
                      <button
                        onClick={() => setGraphType('pair')}
                        disabled={!selectedPairId}
                        style={{
                          padding: '0.4rem 0.8rem',
                          borderRadius: '4px',
                          backgroundColor: graphType === 'pair' ? '#8b5cf6' : '#1e293b',
                          color: '#fff',
                          border: 'none',
                          fontSize: '0.8rem',
                          cursor: selectedPairId ? 'pointer' : 'not-allowed',
                          opacity: selectedPairId ? 1 : 0.5
                        }}
                      >
                        Focused Pair Evidence
                      </button>
                      <button
                        onClick={() => setGraphType('provenance')}
                        disabled={!selectedPairId}
                        style={{
                          padding: '0.4rem 0.8rem',
                          borderRadius: '4px',
                          backgroundColor: graphType === 'provenance' ? '#8b5cf6' : '#1e293b',
                          color: '#fff',
                          border: 'none',
                          fontSize: '0.8rem',
                          cursor: selectedPairId ? 'pointer' : 'not-allowed',
                          opacity: selectedPairId ? 1 : 0.5
                        }}
                      >
                        Inference Provenance
                      </button>

                      {/* Side effect limit slider (only for overview) */}
                      {graphType === 'overview' && (
                        <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                          <span>Side Effect Limit: <b>{sideEffectLimit}</b></span>
                          <input
                            type="range"
                            min="1"
                            max="15"
                            value={sideEffectLimit}
                            onChange={(e) => setSideEffectLimit(parseInt(e.target.value))}
                            style={{ cursor: 'pointer' }}
                          />
                        </div>
                      )}
                    </div>

                    {/* Cytoscape Graph Container */}
                    <div style={{ flex: 1, backgroundColor: '#090b14', border: '1px solid var(--border-color)', borderRadius: '8px', overflow: 'hidden', minHeight: '540px' }}>
                      {loadingGraph ? (
                        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '540px', gap: '0.5rem', color: 'var(--text-muted)' }}>
                          <RefreshCw size={24} className="animate-spin" />
                          <span>Loading Graph Subgraph...</span>
                        </div>
                      ) : subgraph ? (
                        <InteractiveGraph
                          subgraph={subgraph}
                          highlightPairId={selectedPairId || undefined}
                          onSelectNode={(node) => console.log('Selected node:', node)}
                        />
                      ) : (
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '540px', color: 'var(--text-muted)' }}>
                          Graph data unavailable.
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* 5. Adverse Event Convergence Tab */}
                {activeTab === 'convergence' && (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                    {analysisData.event_convergence_items.length === 0 ? (
                      <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                        No shared adverse events detected across evaluated drug pairs.
                      </div>
                    ) : (
                      analysisData.event_convergence_items.map((item, idx) => (
                        <div
                          key={idx}
                          style={{
                            padding: '1.25rem',
                            backgroundColor: '#0c0f1d',
                            border: '1px solid var(--border-color)',
                            borderRadius: '6px',
                            display: 'flex',
                            flexDirection: 'column',
                            gap: '0.75rem'
                          }}
                        >
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <span style={{ fontSize: '0.95rem', fontWeight: 600, color: '#fff' }}>
                              Event: {item.side_effect_name}
                            </span>
                            <span style={{
                              padding: '0.2rem 0.5rem',
                              borderRadius: '4px',
                              backgroundColor: item.convergence_category === 'STRONG_EVENT_CONVERGENCE' ? '#ef44441a' : '#f973161a',
                              border: `1px solid ${item.convergence_category === 'STRONG_EVENT_CONVERGENCE' ? '#ef444433' : '#f9731633'}`,
                              color: item.convergence_category === 'STRONG_EVENT_CONVERGENCE' ? '#fca5a5' : '#fdba74',
                              fontSize: '0.7rem',
                              fontWeight: 600
                            }}>
                              {formatEvidenceStatus(item.convergence_category)}
                            </span>
                          </div>
                          
                          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                            Shared across <b style={{ color: '#fff' }}>{item.participating_pairs_count}</b> pairs involving <b style={{ color: '#fff' }}>{item.participating_drug_names.join(', ')}</b>.
                          </div>

                          <div style={{ fontSize: '#0.85rem', color: 'var(--text-muted)', fontStyle: 'italic', lineHeight: '1.4' }}>
                            {item.explanation}
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                )}

                {/* 6. Clinical Report Tab */}
                {activeTab === 'narrative' && (
                  <Card title="Executive Clinical Narrative Report" subtitle="Deterministically assembled consultation analysis summary">
                    <pre style={{
                      whiteSpace: 'pre-wrap',
                      fontFamily: 'var(--font-mono)',
                      fontSize: '0.85rem',
                      lineHeight: '1.6',
                      color: '#e2e8f0',
                      backgroundColor: '#0f1222',
                      padding: '1.5rem',
                      borderRadius: '6px',
                      border: '1px solid var(--border-color)',
                      margin: 0
                    }}>
                      {analysisData.prescription_report.clinical_narrative_report}
                    </pre>
                  </Card>
                )}

                {/* 7. Explainability & Traceability Tab (Phase 11) */}
                {activeTab === 'explainability' && (
                  <div>
                    {analysisData.explainability ? (
                      <PrescriptionExplainabilityTab explainability={analysisData.explainability} />
                    ) : (
                      <Card title="Explainability Profile" subtitle="Reverse computational provenance">
                        <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem', padding: '1rem 0' }}>
                          No explainability profile currently loaded. Run an analysis to view machine-readable lineage.
                        </div>
                      </Card>
                    )}
                  </div>
                )}

                {/* 8. Trustworthiness & Robustness Tab (Phase 12) */}
                {activeTab === 'trustworthiness' && (
                  <div>
                    {analysisData.trustworthiness ? (
                      <PrescriptionTrustworthinessTab trustworthiness={analysisData.trustworthiness} />
                    ) : (
                      <Card title="Computational Trustworthiness Profile" subtitle="Robustness & repeat run evaluation matrix">
                        <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem', padding: '1rem 0' }}>
                          No trustworthiness profile currently loaded. Run an analysis to view the evaluation laboratory.
                        </div>
                      </Card>
                    )}
                  </div>
                )}

                {/* 9. Longitudinal Evolution Tab (Phase 13) */}
                {activeTab === 'longitudinal' && (
                  <div>
                    {loadingLongitudinal && (
                      <Card title="Prescription Evolution" subtitle="Re-evaluating historical states">
                        <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem', padding: '1rem 0' }}>
                          Re-evaluating analysis history timeline, computing persistences and transitional change points...
                        </div>
                      </Card>
                    )}
                    {longitudinalError && (
                      <Card title="Prescription Evolution" subtitle="Re-evaluating historical states">
                        <div style={{ color: '#f87171', fontSize: '0.85rem', padding: '1rem 0' }}>
                          Error: {longitudinalError}
                        </div>
                      </Card>
                    )}
                    {!loadingLongitudinal && !longitudinalError && (
                      longitudinalProfile ? (
                        <PrescriptionLongitudinalTab longitudinal={longitudinalProfile} />
                      ) : (
                        <Card title="Prescription Evolution Laboratory" subtitle="Sequence of analyzed snapshots">
                          <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem', padding: '1rem 0' }}>
                            No longitudinal history has been compiled yet. Run advanced analyses for at least two different medication sets to view the evolution trace.
                          </div>
                        </Card>
                      )
                    )}
                  </div>
                )}

              </div>
            </div>
          )}
        </div>
      </div>

      {/* Drilldown inspector drawer modal (for findings click details) */}
      {selectedPairDetail && (
        <div style={{
          position: 'fixed',
          top: 0,
          right: 0,
          width: '540px',
          height: '100vh',
          backgroundColor: '#090b14',
          borderLeft: '1px solid var(--border-color)',
          boxShadow: '-10px 0 30px rgba(0,0,0,0.5)',
          padding: '2rem',
          display: 'flex',
          flexDirection: 'column',
          zIndex: 1000,
          overflowY: 'auto'
        }}>
          {/* Close button */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '1rem' }}>
            <h3 style={{ margin: 0, fontSize: '1rem', fontWeight: 600, color: '#fff' }}>
              Pair Evidence Details
            </h3>
            <button
              onClick={closePairDetail}
              style={{
                backgroundColor: 'transparent',
                border: 'none',
                color: 'var(--text-muted)',
                fontSize: '1.25rem',
                cursor: 'pointer'
              }}
            >
              &times;
            </button>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', fontSize: '0.85rem' }}>
            <div>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Evaluating</span>
              <div style={{ fontSize: '1.1rem', fontWeight: 600, color: '#fff', marginTop: '0.25rem' }}>
                {selectedPairDetail.drug_a.display_name} &harr; {selectedPairDetail.drug_b.display_name}
              </div>
            </div>

            <div style={{ padding: '0.75rem', borderRadius: '4px', backgroundColor: '#8b5cf61a', border: '1px solid #8b5cf633', color: '#c4b5fd' }}>
              Status: <b>{formatEvidenceStatus(selectedPairDetail.inference.evidence_status)}</b> | Confidence: <b>{selectedPairDetail.inference.confidence_level} ({selectedPairDetail.inference.confidence_score})</b>
            </div>

            {/* DDI asserts list */}
            <div>
              <h4 style={{ margin: '0 0 0.5rem 0', color: '#fff', fontSize: '0.9rem' }}>Direct DrugBank DDI Assertions</h4>
              {selectedPairDetail.direct_ddi_evidence.length === 0 ? (
                <div style={{ color: 'var(--text-muted)', fontStyle: 'italic' }}>No direct assertions found.</div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  {selectedPairDetail.direct_ddi_evidence.map((ddi, i) => (
                    <div key={i} style={{ padding: '0.75rem', borderRadius: '4px', backgroundColor: '#0f1222', border: '1px solid var(--border-color)', color: '#fff' }}>
                      <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>Source: {ddi.source_dataset} | Record ID: {ddi.source_record_id}</div>
                      <div>{ddi.interaction_description}</div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* TWOSIDES side effects list */}
            <div>
              <h4 style={{ margin: '0 0 0.5rem 0', color: '#fff', fontSize: '0.9rem' }}>Combination Side Effects (TWOSIDES)</h4>
              <div style={{ color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
                Total observed side effects count: <b style={{ color: '#fff' }}>{selectedPairDetail.combination_adverse_events.total_event_count}</b>
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem', maxHeight: '180px', overflowY: 'auto' }}>
                {selectedPairDetail.combination_adverse_events.observed_events.slice(0, 40).map((se, i) => (
                  <span key={i} style={{
                    padding: '0.2rem 0.5rem',
                    borderRadius: '4px',
                    backgroundColor: '#ef44441a',
                    border: '1px solid #ef444433',
                    color: '#fca5a5',
                    fontSize: '0.75rem'
                  }}>
                    {se.side_effect_name}
                  </span>
                ))}
                {selectedPairDetail.combination_adverse_events.observed_events.length > 40 && (
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', alignSelf: 'center', marginLeft: '0.25rem' }}>
                    + {selectedPairDetail.combination_adverse_events.observed_events.length - 40} more...
                  </span>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </AppShell>
  );
};
export default PrescriptionSafetyPage;
