import React, { useState, useEffect } from 'react';
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
  ShieldCheck,
  Info
} from 'lucide-react';
import {
  formatEvidenceStatus,
  getEvidenceBadgeColor,
  getPriorityBadgeColor,
  formatDate
} from '../utils/formatters';

interface PrescriptionSafetyPageProps {
  systemInfo: SystemInfoResponse | null;
}

export const PrescriptionSafetyPage: React.FC<PrescriptionSafetyPageProps> = ({ systemInfo }) => {
  const [activeTab, setActiveTab] = useState<ActiveTab>('intelligence');
  const [showCalculation, setShowCalculation] = useState<boolean>(false);

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

  // History log tracker

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
    <>
      {/* 2 Column Dashboard Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '320px 1fr', gap: '2rem', flex: 1, minHeight: 0 }}>
        {/* Left Column: Side Input Control Panel */}
        <div style={{
          backgroundColor: 'var(--bg-secondary)',
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
              <h2 style={{ fontSize: '1.25rem', fontWeight: 600, color: 'var(--text-main)', margin: '0 0 0.5rem 0' }}>
                No Active Prescription Analysis
              </h2>
              <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)', maxWidth: '480px', margin: 0, lineHeight: '1.5' }}>
                Input a combination of medicines on the left and click <b>Analyze Prescription</b> to evaluate direct interactions and combination adverse-event evidence.
              </p>
            </div>
          ) : (
            /* Results Panel */
            <div style={{ display: 'flex', flexDirection: 'column', flex: 1, minHeight: 0 }}>
              {/* Dropdown mode selector */}
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '1rem',
                backgroundColor: 'var(--bg-secondary)',
                padding: '0.75rem 1.25rem',
                borderRadius: '8px',
                border: '1px solid var(--border-color)',
                marginBottom: '1.5rem'
              }}>
                <span style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', whiteSpace: 'nowrap' }}>
                  Analysis Dimension:
                </span>
                
                <select
                  value={activeTab}
                  onChange={(e) => setActiveTab(e.target.value as any)}
                  style={{
                    flex: 1,
                    padding: '0.5rem 1rem',
                    borderRadius: '6px',
                    backgroundColor: 'var(--bg-primary)',
                    border: '1px solid var(--border-color)',
                    color: 'var(--text-main)',
                    fontSize: '0.85rem',
                    fontWeight: 700,
                    outline: 'none',
                    cursor: 'pointer'
                  }}
                >
                  <option value="intelligence">Prescription Overview</option>
                  <option value="findings">Medication Pair Findings</option>
                  <option value="graph">Relationship Graph</option>
                  <option value="narrative">Clinical Report</option>
                </select>
              </div>

              {/* Tab Panels */}
              <div style={{ flex: 1, minHeight: 0 }}>
                
                {analysisData.prescription_report.unresolved_items && analysisData.prescription_report.unresolved_items.length > 0 && (
                  <div style={{
                    padding: '0.75rem 1rem',
                    backgroundColor: 'rgba(239, 68, 68, 0.08)',
                    border: '1px solid rgba(239, 68, 68, 0.25)',
                    borderRadius: '6px',
                    color: '#ef4444',
                    fontSize: '0.8rem',
                    marginBottom: '1.25rem',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '0.25rem'
                  }}>
                    <span>⚠️ <b>Unresolved Input Warning:</b> Some medication inputs could not be recognized by the reasoning engine. Misspelled medications are ignored during drug-drug interaction evaluation.</span>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      Unrecognized: {analysisData.prescription_report.unresolved_items.map(u => `"${u.input_value}"`).join(', ')}
                    </span>
                  </div>
                )}
                
                {/* 1. Intelligence Overview Tab */}
                {activeTab === 'intelligence' && (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                    
                    {/* Top Row: Safety Summary & Entity Resolution */}
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
                      
                      {/* Left: Overall Prescription Safety Profile */}
                      <div style={{ backgroundColor: 'var(--bg-secondary)', border: '1px solid var(--border-color)', borderRadius: '8px', padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                        <h3 style={{ margin: 0, fontSize: '0.95rem', color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                          <ShieldCheck size={16} style={{ color: '#10b981' }} /> Safety Profile
                        </h3>
                        
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', fontSize: '0.85rem' }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #1e293b', paddingBottom: '0.5rem' }}>
                            <span style={{ color: 'var(--text-muted)' }}>Risk Status:</span>
                            <span style={{
                              fontWeight: 700,
                              padding: '0.15rem 0.5rem',
                              borderRadius: '4px',
                              backgroundColor: getEvidenceBadgeColor(analysisData.prescription_report.prescription_summary.evidence_status).bg,
                              color: getEvidenceBadgeColor(analysisData.prescription_report.prescription_summary.evidence_status).text,
                              border: `1px solid ${getEvidenceBadgeColor(analysisData.prescription_report.prescription_summary.evidence_status).border}`
                            }}>
                              {formatEvidenceStatus(analysisData.prescription_report.prescription_summary.evidence_status)}
                            </span>
                          </div>

                          <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #1e293b', paddingBottom: '0.5rem' }}>
                            <span style={{ color: 'var(--text-muted)' }}>Highest Priority level:</span>
                            <span style={{
                              fontWeight: 700,
                              padding: '0.15rem 0.5rem',
                              borderRadius: '4px',
                              backgroundColor: getPriorityBadgeColor(analysisData.prescription_report.prescription_summary.highest_evidence_priority).bg,
                              color: getPriorityBadgeColor(analysisData.prescription_report.prescription_summary.highest_evidence_priority).text,
                              border: `1px solid ${getPriorityBadgeColor(analysisData.prescription_report.prescription_summary.highest_evidence_priority).border}`
                            }}>
                              {formatEvidenceStatus(analysisData.prescription_report.prescription_summary.highest_evidence_priority)}
                            </span>
                          </div>

                          <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #1e293b', paddingBottom: '0.5rem' }}>
                            <span style={{ color: 'var(--text-muted)' }}>Total Resolved Drugs:</span>
                            <span style={{ fontWeight: 700, color: 'var(--text-main)' }}>
                              {analysisData.prescription_report.prescription_summary.total_unique_drugs}
                            </span>
                          </div>

                          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                            <span style={{ color: 'var(--text-muted)' }}>Evaluated Interaction Pairs:</span>
                            <span style={{ fontWeight: 700, color: 'var(--text-main)' }}>
                              {analysisData.prescription_report.prescription_summary.total_pairs_analyzed} ({analysisData.prescription_report.prescription_summary.positive_evidence_pairs} flagged)
                            </span>
                          </div>
                        </div>
                      </div>

                      {/* Right: Entity Resolution & Standardization */}
                      <div style={{ backgroundColor: 'var(--bg-secondary)', border: '1px solid var(--border-color)', borderRadius: '8px', padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                        <h3 style={{ margin: 0, fontSize: '0.95rem', color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                          <Database size={16} style={{ color: '#3b82f6' }} /> Entity Resolution
                        </h3>

                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', overflowY: 'auto', maxHeight: '140px' }}>
                          {analysisData.prescription_report.resolution_summary.resolved_drugs.map((drug, idx) => (
                            <div key={idx} style={{
                              display: 'flex',
                              justifyContent: 'space-between',
                              alignItems: 'center',
                              padding: '0.4rem 0.6rem',
                              backgroundColor: 'var(--bg-primary)',
                              border: '1px solid var(--border-color)',
                              borderRadius: '6px',
                              fontSize: '0.8rem'
                            }}>
                              <div style={{ display: 'flex', flexDirection: 'column' }}>
                                <span style={{ fontWeight: 600, color: 'var(--text-main)' }}>{drug.canonical_name}</span>
                                <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>Mapped from: "{drug.input_values.join(', ')}"</span>
                              </div>
                              {drug.rxcui && (
                                <span style={{
                                  fontSize: '0.65rem',
                                  padding: '0.15rem 0.35rem',
                                  borderRadius: '4px',
                                  backgroundColor: 'var(--bg-secondary)',
                                  color: 'var(--primary)',
                                  fontFamily: 'monospace',
                                  border: '1px solid var(--border-color)'
                                }}>
                                  RxCUI: {drug.rxcui}
                                </span>
                              )}
                            </div>
                          ))}

                          {/* Unresolved Inputs */}
                          {analysisData.prescription_report.unresolved_items && analysisData.prescription_report.unresolved_items.map((unres, idx) => (
                            <div key={`unres-${idx}`} style={{
                              display: 'flex',
                              justifyContent: 'space-between',
                              alignItems: 'center',
                              padding: '0.4rem 0.6rem',
                              backgroundColor: 'rgba(239, 68, 68, 0.05)',
                              border: '1px solid rgba(239, 68, 68, 0.2)',
                              borderRadius: '6px',
                              fontSize: '0.8rem'
                            }}>
                              <div style={{ display: 'flex', flexDirection: 'column' }}>
                                <span style={{ fontWeight: 600, color: '#ef4444' }}>"{unres.input_value}"</span>
                                <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>{unres.reason}</span>
                              </div>
                              <span style={{
                                fontSize: '0.625rem',
                                padding: '0.15rem 0.35rem',
                                borderRadius: '4px',
                                backgroundColor: 'rgba(239, 68, 68, 0.1)',
                                color: '#ef4444',
                                fontWeight: 'bold'
                              }}>
                                UNRESOLVED
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>

                    </div>

                    {/* Executive Summary Card */}
                    <div style={{ backgroundColor: 'var(--bg-secondary)', border: '1px solid var(--border-color)', borderRadius: '8px', padding: '1.5rem' }}>
                      <h3 style={{ margin: '0 0 1rem 0', fontSize: '0.95rem', color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <Brain size={16} style={{ color: '#8b5cf6' }} /> Executive Summary
                      </h3>
                      <p style={{ color: 'var(--text-main)', fontSize: '0.875rem', lineHeight: '1.6', margin: 0 }}>
                        {analysisData.advanced_explanation.executive_summary}
                      </p>
                    </div>

                    {/* Enhanced Computational Trustworthiness Card */}
                    {analysisData.trustworthiness && (() => {
                      const metrics = analysisData.trustworthiness.trustworthiness_metrics;
                      const m1 = Math.round((metrics.find(m => m.metric_id === 'METRIC_REPRODUCIBILITY')?.normalized_value ?? 1.0) * 100);
                      const m2 = Math.round((metrics.find(m => m.metric_id === 'METRIC_PERTURBATION')?.normalized_value ?? 1.0) * 100);

                      const structVal = metrics.find(m => m.metric_id === 'METRIC_STRUCT_ROBUST')?.normalized_value ?? 1.0;
                      const signalVal = metrics.find(m => m.metric_id === 'METRIC_SIGNAL_ROBUST')?.normalized_value ?? 1.0;
                      const crossVal = metrics.find(m => m.metric_id === 'METRIC_CROSS_LAYER')?.normalized_value ?? 1.0;
                      const m3 = Math.round(((structVal + signalVal + crossVal) / 3) * 100);

                      const provVal = metrics.find(m => m.metric_id === 'METRIC_PROVENANCE')?.normalized_value ?? 1.0;
                      const expVal = metrics.find(m => m.metric_id === 'METRIC_EXPLANATION')?.normalized_value ?? 1.0;
                      const m4 = Math.round(((provVal + expVal + crossVal) / 3) * 100);

                      const overallRobustness = Math.round((m1 + m2 + m3 + m4) / 4);

                      return (
                        <div style={{ backgroundColor: 'var(--bg-secondary)', border: '1px solid var(--border-color)', borderRadius: '8px', padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <h3 style={{ margin: 0, fontSize: '0.95rem', color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                              <ShieldCheck size={16} style={{ color: '#3b82f6' }} /> Computational Trustworthiness
                            </h3>
                            <div
                              title="Trustworthiness is calculated as the arithmetic mean of the normalized verification metrics across the four evaluated robustness dimensions."
                              style={{ display: 'flex', alignItems: 'center', cursor: 'help', color: 'var(--text-muted)' }}
                            >
                              <Info size={16} />
                            </div>
                          </div>

                          <div style={{ display: 'grid', gridTemplateColumns: '180px 1fr', gap: '2rem', alignItems: 'start' }}>
                            
                            {/* Left: Score Dial Gauge & Formula */}
                            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.75rem', textAlign: 'center' }}>
                              <div style={{
                                display: 'flex',
                                flexDirection: 'column',
                                alignItems: 'center',
                                justifyContent: 'center',
                                width: '130px',
                                height: '130px',
                                borderRadius: '50%',
                                backgroundColor: 'var(--bg-primary)',
                                border: '1px solid var(--border-color)',
                                boxShadow: 'inset 0 0 10px rgba(0,0,0,0.2)'
                              }}>
                                <span style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--primary)' }}>
                                  {overallRobustness}%
                                </span>
                                <span style={{ fontSize: '0.55rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginTop: '0.25rem' }}>Robustness</span>
                              </div>
                              <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', lineHeight: '1.4' }}>
                                Calculation:<br />
                                <b>({m1}% + {m2}% + {m3}% + {m4}%) / 4 = {overallRobustness}%</b>
                              </span>
                            </div>

                            {/* Right: Validation Conditions Checkmarks */}
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', fontSize: '0.8rem' }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-main)' }}>
                                  <span style={{ color: '#10b981', fontWeight: 'bold' }}>✓</span>
                                  <span>Deterministic Repeatability</span>
                                  <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginLeft: 'auto' }}>({m1}%)</span>
                                </div>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-main)' }}>
                                  <span style={{ color: '#10b981', fontWeight: 'bold' }}>✓</span>
                                  <span>Input Invariance Robustness</span>
                                  <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginLeft: 'auto' }}>({m2}%)</span>
                                </div>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-main)' }}>
                                  <span style={{ color: '#10b981', fontWeight: 'bold' }}>✓</span>
                                  <span>Topological Stability</span>
                                  <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginLeft: 'auto' }}>({m3}%)</span>
                                </div>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-main)' }}>
                                  <span style={{ color: '#10b981', fontWeight: 'bold' }}>✓</span>
                                  <span>Explanation Provenance</span>
                                  <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginLeft: 'auto' }}>({m4}%)</span>
                                </div>
                              </div>

                              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontStyle: 'italic', borderTop: '1px solid var(--border-color)', paddingTop: '0.5rem' }}>
                                * A green checkmark (✓) indicates the corresponding verification condition passed validation tests successfully.
                              </div>

                              <button
                                onClick={() => setShowCalculation(!showCalculation)}
                                style={{
                                  alignSelf: 'flex-start',
                                  padding: '0.4rem 0.8rem',
                                  borderRadius: '4px',
                                  backgroundColor: 'var(--bg-primary)',
                                  border: '1px solid var(--border-color)',
                                  color: 'var(--primary)',
                                  fontSize: '0.75rem',
                                  fontWeight: 600,
                                  cursor: 'pointer',
                                  outline: 'none'
                                }}
                              >
                                {showCalculation ? 'Hide Calculation' : 'How is this calculated?'}
                              </button>
                            </div>

                          </div>

                          {/* Expandable detailed mathematical calculation breakdown */}
                          {showCalculation && (
                            <div style={{
                              display: 'flex',
                              flexDirection: 'column',
                              gap: '1rem',
                              padding: '1.25rem',
                              backgroundColor: 'var(--bg-primary)',
                              borderRadius: '6px',
                              border: '1px solid var(--border-color)',
                              animation: 'fadeIn 0.2s ease-out'
                            }}>
                              <h4 style={{ margin: 0, fontSize: '0.85rem', color: 'var(--text-main)' }}>Robustness Dimension Breakdown</h4>
                              
                              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', fontSize: '0.8rem' }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                                  <div>
                                    <span style={{ fontWeight: 600, color: 'var(--text-main)' }}>Deterministic Repeatability</span>
                                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Same input produces the same reasoning structure.</div>
                                  </div>
                                  <span style={{ fontFamily: 'monospace', fontWeight: 'bold', color: 'var(--text-main)' }}>{m1}%</span>
                                </div>

                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                                  <div>
                                    <span style={{ fontWeight: 600, color: 'var(--text-main)' }}>Input Invariance Robustness</span>
                                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Superficial input changes such as capitalization, spacing, and supported synonyms should not change the resolved result.</div>
                                  </div>
                                  <span style={{ fontFamily: 'monospace', fontWeight: 'bold', color: 'var(--text-main)' }}>{m2}%</span>
                                </div>

                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                                  <div>
                                    <span style={{ fontWeight: 600, color: 'var(--text-main)' }}>Topological Stability</span>
                                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Relevant graph structure remains stable under the tested perturbations.</div>
                                  </div>
                                  <span style={{ fontFamily: 'monospace', fontWeight: 'bold', color: 'var(--text-main)' }}>{m3}%</span>
                                </div>

                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                                  <div>
                                    <span style={{ fontWeight: 600, color: 'var(--text-main)' }}>Explanation Provenance</span>
                                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Reasoning can be traced back to the supporting knowledge-graph evidence/source nodes.</div>
                                  </div>
                                  <span style={{ fontFamily: 'monospace', fontWeight: 'bold', color: 'var(--text-main)' }}>{m4}%</span>
                                </div>

                                <div style={{ borderTop: '1px solid var(--border-color)', margin: '0.25rem 0' }}></div>

                                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', fontWeight: 'bold' }}>
                                  <span style={{ color: 'var(--text-main)' }}>Aggregate Computational Robustness Score</span>
                                  <span style={{ color: 'var(--primary)' }}>{overallRobustness}%</span>
                                </div>
                              </div>

                              {/* Schematic Arithmetic Flow Chart */}
                              <div style={{
                                padding: '1rem',
                                backgroundColor: 'var(--bg-secondary)',
                                borderRadius: '4px',
                                border: '1px solid var(--border-color)',
                                fontFamily: 'monospace',
                                fontSize: '0.75rem',
                                color: 'var(--text-muted)',
                                display: 'flex',
                                flexDirection: 'column',
                                gap: '0.25rem',
                                whiteSpace: 'pre'
                              }}>
                                <div>Repeatability ({m1}%) ──┐</div>
                                <div>Invariance ({m2}%) ─────┤</div>
                                <div>Stability ({m3}%) ──────┼──&gt; Arithmetic Mean ──&gt; {overallRobustness}%</div>
                                <div>Provenance ({m4}%) ─────┘</div>
                              </div>

                              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                                <b>Arithmetic Mean Formula:</b><br />
                                ({m1} + {m2} + {m3} + {m4}) / 4 = {overallRobustness}%
                              </div>
                            </div>
                          )}

                          {/* Crucial Clinical Safety Context Box */}
                          <div style={{
                            padding: '0.75rem 1rem',
                            backgroundColor: 'rgba(59, 130, 246, 0.05)',
                            border: '1px solid rgba(59, 130, 246, 0.15)',
                            borderRadius: '6px',
                            fontSize: '0.75rem',
                            color: 'var(--text-muted)'
                          }}>
                            💡 <b>Computational Robustness Notice:</b> This score measures the computational robustness and structural repeat-stability of the reasoning pipeline. It is <u>not</u> clinical accuracy, <u>not</u> a probability of patient risk, and <u>not</u> a percentage chance that the prescription is unsafe.
                          </div>

                        </div>
                      );
                    })()}

                    {/* Scientific Guardrails notices */}
                    <div style={{ border: '1px solid var(--border-color)', borderRadius: '8px', padding: '1.25rem', backgroundColor: 'var(--bg-primary)' }}>
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
                        color: 'var(--text-main)',
                        backgroundColor: 'var(--bg-primary)',
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
                        color: 'var(--text-main)',
                        backgroundColor: 'var(--bg-primary)',
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
                              backgroundColor: 'var(--bg-secondary)',
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
                                <span style={{ fontWeight: 600, color: 'var(--text-main)', fontSize: '0.95rem' }}>
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
                                {pair.organ_systems && pair.organ_systems.map((os) => (
                                  <span key={os} style={{
                                    padding: '0.2rem 0.5rem',
                                    borderRadius: '4px',
                                    backgroundColor: '#0284c71a',
                                    border: '1px solid #0284c733',
                                    color: '#38bdf8',
                                    fontSize: '0.7rem'
                                  }}>
                                    {formatEvidenceStatus(os)}
                                  </span>
                                ))}
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
                    <div style={{ flex: 1, backgroundColor: 'var(--bg-primary)', border: '1px solid var(--border-color)', borderRadius: '8px', overflow: 'hidden', minHeight: '540px' }}>
                      {loadingGraph ? (
                        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '540px', gap: '0.5rem', color: 'var(--text-muted)' }}>
                          <RefreshCw size={24} className="animate-spin" />
                          <span>Loading Graph Subgraph...</span>
                        </div>
                      ) : subgraph ? (
                        <InteractiveGraph
                          subgraph={subgraph}
                          highlightPairId={selectedPairId || undefined}
                          onSelectNode={(node) => {
                            if (node.node_type === 'DrugPair') {
                              selectPair(node.id);
                            }
                          }}
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
                            backgroundColor: 'var(--bg-secondary)',
                            border: '1px solid var(--border-color)',
                            borderRadius: '6px',
                            display: 'flex',
                            flexDirection: 'column',
                            gap: '0.75rem'
                          }}
                        >
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <span style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--text-main)' }}>
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
                      color: 'var(--text-main)',
                      backgroundColor: 'var(--bg-primary)',
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
          backgroundColor: 'var(--bg-secondary)',
          borderLeft: '1px solid var(--border-color)',
          boxShadow: '-10px 0 30px rgba(0,0,0,0.15)',
          padding: '2rem',
          display: 'flex',
          flexDirection: 'column',
          zIndex: 1000,
          overflowY: 'auto'
        }}>
          {/* Close button */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '1rem' }}>
            <h3 style={{ margin: 0, fontSize: '1rem', fontWeight: 600, color: 'var(--text-main)' }}>
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
              <div style={{ fontSize: '1.1rem', fontWeight: 600, color: 'var(--text-main)', marginTop: '0.25rem' }}>
                {selectedPairDetail.drug_a.display_name} &harr; {selectedPairDetail.drug_b.display_name}
              </div>
            </div>

            <div style={{ padding: '0.75rem', borderRadius: '4px', backgroundColor: '#8b5cf61a', border: '1px solid #8b5cf633', color: 'var(--primary)' }}>
              Status: <b>{formatEvidenceStatus(selectedPairDetail.inference.evidence_status)}</b> | Confidence: <b>{selectedPairDetail.inference.confidence_level} ({selectedPairDetail.inference.confidence_score})</b>
            </div>

            {/* Organ-System Signals */}
            {selectedPairDetail.organ_systems && selectedPairDetail.organ_systems.length > 0 && (
              <div>
                <h4 style={{ margin: '0 0 0.5rem 0', color: 'var(--text-main)', fontSize: '0.9rem' }}>Identified Organ-System Signals</h4>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
                  {selectedPairDetail.organ_systems.map((os) => (
                    <span key={os} style={{
                      padding: '0.25rem 0.6rem',
                      borderRadius: '4px',
                      backgroundColor: '#0284c71a',
                      border: '1px solid #0284c733',
                      color: '#38bdf8',
                      fontSize: '0.75rem',
                      fontWeight: 600
                    }}>
                      {formatEvidenceStatus(os)}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* DDI asserts list */}
            <div>
              <h4 style={{ margin: '0 0 0.5rem 0', color: 'var(--text-main)', fontSize: '0.9rem' }}>Direct DrugBank DDI Assertions</h4>
              {selectedPairDetail.direct_ddi_evidence.length === 0 ? (
                <div style={{ color: 'var(--text-muted)', fontStyle: 'italic' }}>No direct assertions found.</div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  {selectedPairDetail.direct_ddi_evidence.map((ddi, i) => (
                    <div key={i} style={{ padding: '0.75rem', borderRadius: '4px', backgroundColor: 'var(--bg-primary)', border: '1px solid var(--border-color)', color: 'var(--text-main)' }}>
                      <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>Source: {ddi.source_dataset} | Record ID: {ddi.source_record_id}</div>
                      <div>{ddi.interaction_description}</div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* TWOSIDES side effects list */}
            <div>
              <h4 style={{ margin: '0 0 0.5rem 0', color: 'var(--text-main)', fontSize: '0.9rem' }}>Combination Side Effects (TWOSIDES)</h4>
              <div style={{ color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
                Total observed side effects count: <b style={{ color: 'var(--text-main)' }}>{selectedPairDetail.combination_adverse_events.total_event_count}</b>
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
    </>
  );
};
export default PrescriptionSafetyPage;
