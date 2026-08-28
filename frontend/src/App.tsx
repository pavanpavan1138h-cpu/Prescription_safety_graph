import React, { useState, useEffect } from 'react';
import {
  prescriptionApi,
  SubgraphResponse,
  AdvancedPrescriptionAnalysisResponse
} from './api/client';
import { InteractiveGraph } from './components/InteractiveGraph';
import {
  PrescriptionAnalysisResponse,
  PairDetailResponse,
  SystemInfoResponse
} from './types/api';
import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  Database,
  FileText,
  HelpCircle,
  Info,
  Layers,
  Network,
  Plus,
  Search,
  ShieldAlert,
  Trash2,
  X,
  ExternalLink,
  ChevronRight,
  GitFork,
  Share2,
  Sparkles,
  Zap,
  Clock,
  Compass
} from 'lucide-react';

export default function App() {
  const [medications, setMedications] = useState<string[]>([
    'cyclosporine',
    'fluconazole',
    'phentermine'
  ]);
  const [inputVal, setInputVal] = useState('');
  const [loading, setLoading] = useState(false);
  const [systemInfo, setSystemInfo] = useState<SystemInfoResponse | null>(null);
  const [report, setReport] = useState<PrescriptionAnalysisResponse | null>(null);
  const [advReport, setAdvReport] = useState<AdvancedPrescriptionAnalysisResponse | null>(null);
  const [selectedPair, setSelectedPair] = useState<PairDetailResponse | null>(null);
  const [overviewGraph, setOverviewGraph] = useState<SubgraphResponse | null>(null);
  const [pairGraph, setPairGraph] = useState<SubgraphResponse | null>(null);
  const [provenanceGraph, setProvenanceGraph] = useState<SubgraphResponse | null>(null);
  const [drillLoading, setDrillLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'intelligence' | 'findings' | 'graph' | 'explorer' | 'participation' | 'convergence' | 'narrative'>('intelligence');
  const [filterType, setFilterType] = useState<string>('ALL');
  const [searchSE, setSearchSE] = useState('');
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  useEffect(() => {
    prescriptionApi.getSystemInfo()
      .then(setSystemInfo)
      .catch(err => console.error('Failed to load system info:', err));
  }, []);

  const handleAddMedication = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputVal.trim()) return;
    setMedications([...medications, inputVal.trim()]);
    setInputVal('');
  };

  const handleRemoveMedication = (index: number) => {
    setMedications(medications.filter((_, i) => i !== index));
  };

  const handleAnalyze = async () => {
    if (medications.length === 0) {
      setErrorMsg('Please add at least one medication to analyze.');
      return;
    }
    setErrorMsg(null);
    setLoading(true);
    setReport(null);
    setAdvReport(null);
    setSelectedPair(null);
    setOverviewGraph(null);
    try {
      const advData = await prescriptionApi.analyzePrescriptionAdvanced(medications);
      setAdvReport(advData);
      setReport(advData.prescription_report);
      // Fetch overview subgraph
      try {
        const graphData = await prescriptionApi.getPrescriptionGraph(advData.prescription_report.metadata.analysis_id, 5);
        setOverviewGraph(graphData);
      } catch (gErr) {
        console.warn('Subgraph load deferred:', gErr);
      }
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to analyze prescription.');
    } finally {
      setLoading(false);
    }
  };

  const handleInspectPair = async (pairId: string) => {
    if (!report) return;
    setDrillLoading(true);
    setPairGraph(null);
    setProvenanceGraph(null);
    try {
      const data = await prescriptionApi.getPairDetail(report.metadata.analysis_id, pairId);
      setSelectedPair(data);
      // Fetch focused pair graph and provenance graph
      try {
        const pGraph = await prescriptionApi.getPairEvidenceGraph(report.metadata.analysis_id, pairId, 25);
        setPairGraph(pGraph);
        const provGraph = await prescriptionApi.getProvenanceGraph(report.metadata.analysis_id, pairId);
        setProvenanceGraph(provGraph);
      } catch (err) {
        console.warn('Pair graph error:', err);
      }
    } catch (err: any) {
      alert('Failed to load pair details: ' + err.message);
    } finally {
      setDrillLoading(false);
    }
  };

  const getPriorityBadgeClass = (priority: string) => {
    switch (priority) {
      case 'CRITICAL_EVIDENCE_PRIORITY': return 'badge-critical';
      case 'HIGH_EVIDENCE_PRIORITY': return 'badge-critical';
      case 'MODERATE_EVIDENCE_PRIORITY': return 'badge-moderate';
      case 'LIMITED_EVIDENCE_PRIORITY': return 'badge-limited';
      default: return 'badge-none';
    }
  };

  const getStatusBadgeClass = (status: string) => {
    switch (status) {
      case 'CONVERGENT_SAFETY_EVIDENCE': return 'badge-critical';
      case 'DDI_EVIDENCE_ONLY': return 'badge-moderate';
      case 'COMBINATION_EVENT_EVIDENCE_ONLY': return 'badge-limited';
      case 'NO_DIRECT_GRAPH_EVIDENCE': return 'badge-none';
      default: return 'badge-neutral';
    }
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Top Navbar */}
      <header style={{
        borderBottom: '1px solid var(--border-color)',
        background: 'rgba(11, 15, 23, 0.85)',
        backdropFilter: 'blur(12px)',
        position: 'sticky',
        top: 0,
        zIndex: 50,
        padding: '14px 32px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            width: '36px',
            height: '36px',
            borderRadius: '8px',
            background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 0 16px var(--primary-glow)'
          }}>
            <Network size={20} color="#fff" />
          </div>
          <div>
            <h1 style={{ fontSize: '1.15rem', fontWeight: 700, letterSpacing: '-0.02em' }}>
              Prescription Safety Graph
            </h1>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Deterministic Evidence & Provenance Explorer
            </p>
          </div>
        </div>

        {systemInfo && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '20px', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Database size={14} color="#3b82f6" />
              <span><b>{systemInfo.graph_nodes.toLocaleString()}</b> Nodes</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Layers size={14} color="#8b5cf6" />
              <span><b>{systemInfo.graph_edges.toLocaleString()}</b> Edges</span>
            </div>
            <span className="badge badge-neutral" style={{ fontSize: '0.7rem' }}>
              v{systemInfo.api_version} READY
            </span>
          </div>
        )}
      </header>

      {/* Main Container */}
      <main style={{ flex: 1, padding: '32px', maxWidth: '1400px', margin: '0 auto', width: '100%' }}>
        {/* Banner Guardrail */}
        <div className="glass-panel" style={{
          padding: '12px 18px',
          marginBottom: '28px',
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          borderLeft: '4px solid #3b82f6'
        }}>
          <Info size={18} color="#3b82f6" style={{ flexShrink: 0 }} />
          <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
            <b>Scientific Scope:</b> This platform evaluates structured knowledge graph evidence from DrugBank, TWOSIDES, and RxNorm. 
            <i> Evidence priority reflects graph density, not patient-specific clinical severity. Absence of graph evidence does not establish safety.</i>
          </p>
        </div>

        {/* Input & Controller Section */}
        <div style={{ display: 'grid', gridTemplateColumns: '380px 1fr', gap: '28px', alignItems: 'start' }}>
          {/* Medication Input Card */}
          <div className="glass-panel" style={{ padding: '24px' }}>
            <h2 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Activity size={18} color="#3b82f6" />
              Prescription Input
            </h2>

            <form onSubmit={handleAddMedication} style={{ display: 'flex', gap: '8px', marginBottom: '16px' }}>
              <input
                type="text"
                value={inputVal}
                onChange={e => setInputVal(e.target.value)}
                placeholder="Name, RxCUI, DB ID, CID..."
                style={{
                  flex: 1,
                  background: 'rgba(0,0,0,0.3)',
                  border: '1px solid var(--border-color)',
                  borderRadius: '8px',
                  padding: '8px 12px',
                  color: '#fff',
                  fontSize: '0.85rem'
                }}
              />
              <button
                type="submit"
                style={{
                  background: '#1e293b',
                  border: '1px solid var(--border-color)',
                  borderRadius: '8px',
                  padding: '8px 14px',
                  color: '#fff',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                  fontSize: '0.85rem'
                }}
              >
                <Plus size={16} /> Add
              </button>
            </form>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '20px', maxHeight: '240px', overflowY: 'auto' }}>
              {medications.map((med, idx) => (
                <div
                  key={idx}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    background: 'rgba(255,255,255,0.03)',
                    padding: '6px 12px',
                    borderRadius: '6px',
                    border: '1px solid var(--border-color)',
                    fontSize: '0.85rem'
                  }}
                >
                  <span className="mono">{med}</span>
                  <button
                    onClick={() => handleRemoveMedication(idx)}
                    style={{ background: 'none', border: 'none', color: 'var(--text-dim)', cursor: 'pointer' }}
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              ))}
            </div>

            {errorMsg && (
              <div style={{
                background: 'var(--status-critical-bg)',
                border: '1px solid rgba(239, 68, 68, 0.3)',
                color: '#fca5a5',
                padding: '8px 12px',
                borderRadius: '6px',
                fontSize: '0.8rem',
                marginBottom: '16px'
              }}>
                {errorMsg}
              </div>
            )}

            <button
              onClick={handleAnalyze}
              disabled={loading}
              style={{
                width: '100%',
                background: 'linear-gradient(135deg, #2563eb, #7c3aed)',
                border: 'none',
                borderRadius: '8px',
                padding: '12px',
                color: '#fff',
                fontWeight: 600,
                fontSize: '0.9rem',
                cursor: loading ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                boxShadow: '0 4px 14px var(--primary-glow)'
              }}
            >
              {loading ? (
                <>
                  <div style={{ width: '16px', height: '16px', border: '2px solid #fff', borderTopColor: 'transparent', borderRadius: '50%', animation: 'spin 0.8s linear infinite' }} />
                  Evaluating Knowledge Graph...
                </>
              ) : (
                <>
                  <Network size={18} />
                  Analyze Prescription Safety
                </>
              )}
            </button>
          </div>

          {/* Report Display Area */}
          <div>
            {!report && !loading && (
              <div className="glass-panel" style={{ padding: '48px', textAlign: 'center' }}>
                <Network size={48} color="#3b82f6" style={{ margin: '0 auto 16px', opacity: 0.6 }} />
                <h3 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '8px' }}>
                  No Prescription Analyzed Yet
                </h3>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', maxWidth: '420px', margin: '0 auto' }}>
                  Add medication names or identifiers on the left and click <b>Analyze Prescription Safety</b> to evaluate pairwise interaction and adverse-event evidence across 4.97M graph edges.
                </p>
              </div>
            )}

            {report && (
              <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
                {/* Resolution and Input Summary Cards */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px' }}>
                  <div className="glass-panel" style={{ padding: '16px' }}>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Unique Canonical Drugs</span>
                    <h3 style={{ fontSize: '1.4rem', fontWeight: 700, marginTop: '4px' }}>
                      {report.prescription_summary.total_unique_drugs}
                    </h3>
                    <span style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>
                      {report.resolution_summary.duplicate_count} duplicates collapsed
                    </span>
                  </div>

                  <div className="glass-panel" style={{ padding: '16px' }}>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Analyzed Drug Pairs</span>
                    <h3 style={{ fontSize: '1.4rem', fontWeight: 700, marginTop: '4px' }}>
                      {report.prescription_summary.total_pairs_analyzed}
                    </h3>
                    <span style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>
                      {report.prescription_summary.positive_evidence_pairs} with direct evidence
                    </span>
                  </div>

                  <div className="glass-panel" style={{ padding: '16px' }}>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Overall Evidence Status</span>
                    <div style={{ marginTop: '8px' }}>
                      <span className={`badge ${getStatusBadgeClass(report.prescription_summary.evidence_status)}`}>
                        {report.prescription_summary.evidence_status}
                      </span>
                    </div>
                  </div>

                  <div className="glass-panel" style={{ padding: '16px' }}>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Highest Priority Tier</span>
                    <div style={{ marginTop: '8px' }}>
                      <span className={`badge ${getPriorityBadgeClass(report.prescription_summary.highest_evidence_priority)}`}>
                        {report.prescription_summary.highest_evidence_priority}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Resolution Feedback Alert if Unresolved Items Exist */}
                {report.unresolved_items.length > 0 && (
                  <div style={{
                    background: 'var(--status-moderate-bg)',
                    border: '1px solid rgba(245, 158, 11, 0.3)',
                    padding: '12px 18px',
                    borderRadius: '8px',
                    fontSize: '0.85rem',
                    color: '#fcd34d',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '10px'
                  }}>
                    <AlertTriangle size={18} />
                    <span>
                      <b>Unresolved Medication Notice:</b> {report.unresolved_items.length} submitted item(s) (
                      {report.unresolved_items.map(u => u.input_value).join(', ')}
                      ) could not be resolved to graph entities and were excluded from pairwise analysis.
                    </span>
                  </div>
                )}

                {/* Navigation Tabs */}
                <div style={{ display: 'flex', borderBottom: '1px solid var(--border-color)', gap: '8px', overflowX: 'auto' }}>
                  <button
                    onClick={() => setActiveTab('intelligence')}
                    style={{
                      padding: '10px 16px',
                      background: 'none',
                      border: 'none',
                      borderBottom: activeTab === 'intelligence' ? '2px solid #8b5cf6' : '2px solid transparent',
                      color: activeTab === 'intelligence' ? '#c4b5fd' : 'var(--text-muted)',
                      fontWeight: 600,
                      cursor: 'pointer',
                      fontSize: '0.85rem',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px'
                    }}
                  >
                    <Sparkles size={16} color="#8b5cf6" /> Clinical Intelligence & Patterns {advReport && `(${advReport.evidence_patterns.length})`}
                  </button>

                  <button
                    onClick={() => setActiveTab('findings')}
                    style={{
                      padding: '10px 16px',
                      background: 'none',
                      border: 'none',
                      borderBottom: activeTab === 'findings' ? '2px solid #3b82f6' : '2px solid transparent',
                      color: activeTab === 'findings' ? '#fff' : 'var(--text-muted)',
                      fontWeight: 600,
                      cursor: 'pointer',
                      fontSize: '0.85rem',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px'
                    }}
                  >
                    <ShieldAlert size={16} /> Prioritized Findings ({report.prioritized_findings.length})
                  </button>

                  <button
                    onClick={() => setActiveTab('graph')}
                    style={{
                      padding: '10px 16px',
                      background: 'none',
                      border: 'none',
                      borderBottom: activeTab === 'graph' ? '2px solid #3b82f6' : '2px solid transparent',
                      color: activeTab === 'graph' ? '#fff' : 'var(--text-muted)',
                      fontWeight: 600,
                      cursor: 'pointer',
                      fontSize: '0.85rem',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px'
                    }}
                  >
                    <Network size={16} /> Interactive Knowledge Graph
                  </button>

                  <button
                    onClick={() => setActiveTab('convergence')}
                    style={{
                      padding: '10px 16px',
                      background: 'none',
                      border: 'none',
                      borderBottom: activeTab === 'convergence' ? '2px solid #3b82f6' : '2px solid transparent',
                      color: activeTab === 'convergence' ? '#fff' : 'var(--text-muted)',
                      fontWeight: 600,
                      cursor: 'pointer',
                      fontSize: '0.85rem',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px'
                    }}
                  >
                    <Share2 size={16} /> Event Convergence {advReport && `(${advReport.event_convergence_items.length})`}
                  </button>

                  <button
                    onClick={() => setActiveTab('explorer')}
                    style={{
                      padding: '10px 16px',
                      background: 'none',
                      border: 'none',
                      borderBottom: activeTab === 'explorer' ? '2px solid #3b82f6' : '2px solid transparent',
                      color: activeTab === 'explorer' ? '#fff' : 'var(--text-muted)',
                      fontWeight: 600,
                      cursor: 'pointer',
                      fontSize: '0.85rem',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px'
                    }}
                  >
                    <Layers size={16} /> All Pairs Explorer ({report.pair_results.length})
                  </button>

                  <button
                    onClick={() => setActiveTab('participation')}
                    style={{
                      padding: '10px 16px',
                      background: 'none',
                      border: 'none',
                      borderBottom: activeTab === 'participation' ? '2px solid #3b82f6' : '2px solid transparent',
                      color: activeTab === 'participation' ? '#fff' : 'var(--text-muted)',
                      fontWeight: 600,
                      cursor: 'pointer',
                      fontSize: '0.85rem',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px'
                    }}
                  >
                    <Activity size={16} /> Drug Participation ({report.drug_participation.length})
                  </button>

                  <button
                    onClick={() => setActiveTab('narrative')}
                    style={{
                      padding: '10px 16px',
                      background: 'none',
                      border: 'none',
                      borderBottom: activeTab === 'narrative' ? '2px solid #3b82f6' : '2px solid transparent',
                      color: activeTab === 'narrative' ? '#fff' : 'var(--text-muted)',
                      fontWeight: 600,
                      cursor: 'pointer',
                      fontSize: '0.85rem',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px'
                    }}
                  >
                    <FileText size={16} /> Clinical Report Narrative
                  </button>
                </div>

                {/* TAB 0: ADVANCED CLINICAL INTELLIGENCE & PATTERNS */}
                {activeTab === 'intelligence' && advReport && (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                    {/* Complexity & Intelligence Summary Card */}
                    <div className="glass-panel" style={{ padding: '20px', borderLeft: '4px solid #8b5cf6' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                          <Zap size={18} color="#8b5cf6" />
                          <h3 style={{ fontSize: '1.05rem', fontWeight: 700 }}>Prescription Complexity Profile</h3>
                        </div>
                        <span className="badge badge-critical" style={{ background: 'rgba(139, 92, 246, 0.2)', color: '#c4b5fd', border: '1px solid #8b5cf6' }}>
                          {advReport.complexity_profile.complexity_category} (Score: {advReport.complexity_profile.complexity_score})
                        </span>
                      </div>
                      <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>
                        {advReport.complexity_profile.explanation}
                      </p>
                    </div>

                    {/* Detected Evidence Patterns Grid */}
                    <div>
                      <h4 style={{ fontSize: '0.95rem', fontWeight: 600, marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <Sparkles size={16} color="#8b5cf6" /> Detected Evidence & Structural Patterns ({advReport.evidence_patterns.length})
                      </h4>
                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '14px' }}>
                        {advReport.evidence_patterns.map((pat, idx) => (
                          <div key={idx} className="glass-panel" style={{ padding: '16px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                              <span className="badge badge-limited" style={{ fontSize: '0.7rem' }}>{pat.pattern_type}</span>
                              <span className="mono" style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>{pat.pattern_id}</span>
                            </div>
                            <h5 style={{ fontSize: '0.95rem', fontWeight: 600 }}>{pat.title}</h5>
                            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{pat.explanation}</p>
                            {pat.supporting_drug_names.length > 0 && (
                              <div style={{ fontSize: '0.75rem', color: '#93c5fd', marginTop: '4px' }}>
                                <b>Involved Drugs:</b> {pat.supporting_drug_names.join(', ')}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Review Prioritization Engine Card */}
                    <div className="glass-panel" style={{ padding: '20px' }}>
                      <h4 style={{ fontSize: '0.95rem', fontWeight: 600, marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <ShieldAlert size={16} color="#ef4444" /> Deterministic Review Prioritization
                      </h4>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                        {advReport.review_priorities.map((rp, idx) => (
                          <div key={idx} style={{ padding: '12px', background: 'rgba(255,255,255,0.02)', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                              <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>{rp.drug_a_name} + {rp.drug_b_name}</span>
                              <span className={`badge ${getPriorityBadgeClass(rp.review_priority)}`}>{rp.review_priority} (Score: {rp.review_score})</span>
                            </div>
                            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                              {rp.deterministic_reasons.map((r, i) => (
                                <div key={i}>• {r}</div>
                              ))}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Uncertainty & Context Requirements */}
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                      <div className="glass-panel" style={{ padding: '16px' }}>
                        <h4 style={{ fontSize: '0.85rem', fontWeight: 600, color: '#fcd34d', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                          <AlertTriangle size={15} /> Structured Uncertainty Model
                        </h4>
                        <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '10px' }}>
                          {advReport.uncertainty_profile.explanation_narrative}
                        </p>
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                          {advReport.uncertainty_profile.uncertainty_categories.map((c, i) => (
                            <span key={i} className="badge badge-neutral" style={{ fontSize: '0.65rem' }}>{c}</span>
                          ))}
                        </div>
                      </div>

                      <div className="glass-panel" style={{ padding: '16px' }}>
                        <h4 style={{ fontSize: '0.85rem', fontWeight: 600, color: '#93c5fd', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                          <Compass size={15} /> Required Clinical Parameters (Out-of-Graph)
                        </h4>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', fontSize: '0.75rem', color: 'var(--text-dim)' }}>
                          {advReport.clinical_context_requirements.map((req, i) => (
                            <div key={i}><b>• {req.context_category}:</b> {req.why_it_matters}</div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* TAB CONVERGENCE: CROSS-PAIR ADVERSE EVENT CONVERGENCE */}
                {activeTab === 'convergence' && advReport && (
                  <div className="glass-panel" style={{ padding: '20px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                      <h3 style={{ fontSize: '0.95rem', fontWeight: 600 }}>Cross-Pair Adverse Event Convergence Concepts ({advReport.event_convergence_items.length})</h3>
                      <input
                        type="text"
                        placeholder="Filter adverse events..."
                        value={searchSE}
                        onChange={e => setSearchSE(e.target.value)}
                        style={{
                          background: 'rgba(0,0,0,0.3)',
                          border: '1px solid var(--border-color)',
                          borderRadius: '6px',
                          padding: '4px 10px',
                          fontSize: '0.75rem',
                          color: '#fff'
                        }}
                      />
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '10px' }}>
                      {advReport.event_convergence_items
                        .filter(ec => ec.side_effect_name.toLowerCase().includes(searchSE.toLowerCase()))
                        .map((ec, i) => (
                          <div key={i} style={{ padding: '10px 14px', background: 'rgba(255,255,255,0.02)', borderRadius: '6px', border: '1px solid var(--border-color)' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                              <span style={{ fontWeight: 600, fontSize: '0.85rem' }}>{ec.side_effect_name}</span>
                              <span className="badge badge-limited" style={{ fontSize: '0.65rem' }}>{ec.convergence_category}</span>
                            </div>
                            <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>
                              Participates across <b>{ec.participating_pairs_count}</b> drug pair(s) involving: {ec.participating_drug_names.join(', ')}
                            </div>
                          </div>
                        ))}
                    </div>
                  </div>
                )}

                {/* TAB 1: PRIORITIZED FINDINGS */}
                {activeTab === 'findings' && (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                    {report.prioritized_findings.map((f, i) => (
                      <div
                        key={i}
                        className="glass-panel"
                        style={{
                          padding: '20px',
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center',
                          transition: 'all 0.2s ease',
                          borderLeft: `4px solid ${f.priority === 'CRITICAL_EVIDENCE_PRIORITY' ? '#ef4444' : '#3b82f6'}`
                        }}
                      >
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', maxWidth: '75%' }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                            <span className={`badge ${getPriorityBadgeClass(f.priority)}`}>
                              {f.priority}
                            </span>
                            <span className={`badge ${getStatusBadgeClass(f.evidence_status)}`}>
                              {f.evidence_status}
                            </span>
                            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                              Confidence: <b>{(f.confidence.score * 100).toFixed(0)}%</b> ({f.confidence.level})
                            </span>
                          </div>

                          <h4 style={{ fontSize: '1.05rem', fontWeight: 600 }}>
                            {f.drug_a.name} <span style={{ color: 'var(--text-dim)' }}>+</span> {f.drug_b.name}
                          </h4>

                          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                            {f.summary_narrative}
                          </p>

                          <div style={{ display: 'flex', gap: '16px', fontSize: '0.75rem', color: 'var(--text-dim)', marginTop: '4px' }}>
                            <span>DrugBank Assertions: <b>{f.ddi_record_count}</b></span>
                            <span>TWOSIDES Adverse Events: <b>{f.adverse_event_count}</b></span>
                          </div>
                        </div>

                        <button
                          onClick={() => handleInspectPair(f.pair_id)}
                          style={{
                            background: '#1e293b',
                            border: '1px solid var(--border-color)',
                            borderRadius: '6px',
                            padding: '8px 14px',
                            color: '#93c5fd',
                            cursor: 'pointer',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '6px',
                            fontSize: '0.85rem',
                            fontWeight: 500
                          }}
                        >
                          Inspect Evidence <ChevronRight size={14} />
                        </button>
                      </div>
                    ))}
                  </div>
                )}

                {/* TAB 2: INTERACTIVE KNOWLEDGE GRAPH */}
                {activeTab === 'graph' && (
                  <div>
                    {overviewGraph ? (
                      <InteractiveGraph
                        subgraph={overviewGraph}
                        onSelectNode={(n) => console.log('Selected Node:', n)}
                        onSelectEdge={(e) => console.log('Selected Edge:', e)}
                        height="580px"
                      />
                    ) : (
                      <div className="glass-panel" style={{ padding: '32px', textAlign: 'center' }}>
                        <p style={{ color: 'var(--text-muted)' }}>Loading prescription visualization network...</p>
                      </div>
                    )}
                  </div>
                )}

                {/* TAB 3: ALL PAIRS EXPLORER */}
                {activeTab === 'explorer' && (
                  <div className="glass-panel" style={{ padding: '20px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                      <h3 style={{ fontSize: '0.95rem', fontWeight: 600 }}>All Evaluated Combinations</h3>
                      <div style={{ display: 'flex', gap: '8px' }}>
                        {['ALL', 'CONVERGENT', 'DDI', 'EVENTS', 'NO_EVIDENCE'].map(f => (
                          <button
                            key={f}
                            onClick={() => setFilterType(f)}
                            style={{
                              padding: '4px 10px',
                              borderRadius: '4px',
                              border: '1px solid var(--border-color)',
                              background: filterType === f ? '#3b82f6' : 'transparent',
                              color: '#fff',
                              fontSize: '0.75rem',
                              cursor: 'pointer'
                            }}
                          >
                            {f}
                          </button>
                        ))}
                      </div>
                    </div>

                    <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
                      <thead>
                        <tr style={{ borderBottom: '1px solid var(--border-color)', textAlign: 'left', color: 'var(--text-muted)' }}>
                          <th style={{ padding: '8px 12px' }}>Drug Pair</th>
                          <th style={{ padding: '8px 12px' }}>Evidence Status</th>
                          <th style={{ padding: '8px 12px' }}>Priority</th>
                          <th style={{ padding: '8px 12px' }}>Confidence</th>
                          <th style={{ padding: '8px 12px', textAlign: 'right' }}>Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {report.pair_results
                          .filter(pr => {
                            if (filterType === 'CONVERGENT') return pr.evidence_status === 'CONVERGENT_SAFETY_EVIDENCE';
                            if (filterType === 'DDI') return pr.evidence_status === 'DDI_EVIDENCE_ONLY';
                            if (filterType === 'EVENTS') return pr.evidence_status === 'COMBINATION_EVENT_EVIDENCE_ONLY';
                            if (filterType === 'NO_EVIDENCE') return pr.evidence_status === 'NO_DIRECT_GRAPH_EVIDENCE';
                            return true;
                          })
                          .map((pr, idx) => (
                            <tr key={idx} style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                              <td style={{ padding: '10px 12px', fontWeight: 500 }}>
                                {pr.drug_a_name} <span style={{ color: 'var(--text-dim)' }}>+</span> {pr.drug_b_name}
                              </td>
                              <td style={{ padding: '10px 12px' }}>
                                <span className={`badge ${getStatusBadgeClass(pr.evidence_status)}`} style={{ fontSize: '0.65rem' }}>
                                  {pr.evidence_status}
                                </span>
                              </td>
                              <td style={{ padding: '10px 12px' }}>
                                <span className={`badge ${getPriorityBadgeClass(pr.evidence_priority)}`} style={{ fontSize: '0.65rem' }}>
                                  {pr.evidence_priority}
                                </span>
                              </td>
                              <td style={{ padding: '10px 12px', color: 'var(--text-muted)' }}>
                                {(pr.confidence_score * 100).toFixed(0)}%
                              </td>
                              <td style={{ padding: '10px 12px', textAlign: 'right' }}>
                                <button
                                  onClick={() => handleInspectPair(pr.pair_id)}
                                  style={{
                                    background: 'none',
                                    border: 'none',
                                    color: '#60a5fa',
                                    cursor: 'pointer',
                                    fontSize: '0.8rem'
                                  }}
                                >
                                  Details →
                                </button>
                              </td>
                            </tr>
                          ))}
                      </tbody>
                    </table>
                  </div>
                )}

                {/* TAB 4: DRUG PARTICIPATION */}
                {activeTab === 'participation' && (
                  <div className="glass-panel" style={{ padding: '20px' }}>
                    <h3 style={{ fontSize: '0.95rem', fontWeight: 600, marginBottom: '16px' }}>
                      Drug Participation Distribution
                    </h3>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                      {report.drug_participation.map((dp, i) => (
                        <div key={i} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '8px 12px', background: 'rgba(255,255,255,0.02)', borderRadius: '6px' }}>
                          <div>
                            <span style={{ fontWeight: 600 }}>{dp.drug_name}</span>
                            <span className="mono" style={{ fontSize: '0.75rem', color: 'var(--text-dim)', marginLeft: '8px' }}>
                              ({dp.drug_id})
                            </span>
                          </div>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '16px', fontSize: '0.8rem' }}>
                            <span>Total Pairs: <b>{dp.total_pairs}</b></span>
                            <span>With Evidence: <b>{dp.pairs_with_evidence}</b></span>
                            <span>Convergent: <b>{dp.convergent_evidence_pairs}</b></span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* TAB 5: NARRATIVE REPORT */}
                {activeTab === 'narrative' && (
                  <div className="glass-panel" style={{ padding: '24px' }}>
                    <h3 style={{ fontSize: '0.95rem', fontWeight: 600, marginBottom: '12px' }}>
                      Generated Clinical Safety Narrative
                    </h3>
                    <pre style={{
                      background: 'rgba(0,0,0,0.4)',
                      padding: '16px',
                      borderRadius: '8px',
                      fontFamily: 'var(--font-mono)',
                      fontSize: '0.8rem',
                      lineHeight: 1.6,
                      color: '#d1d5db',
                      whiteSpace: 'pre-wrap'
                    }}>
                      {report.clinical_narrative_report}
                    </pre>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* MODAL: PAIR EVIDENCE & PROVENANCE INSPECTOR */}
        {selectedPair && (
          <div style={{
            position: 'fixed',
            inset: 0,
            background: 'rgba(0,0,0,0.75)',
            backdropFilter: 'blur(8px)',
            zIndex: 100,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '24px'
          }}>
            <div className="glass-panel animate-fade-in" style={{
              width: '100%',
              maxWidth: '1000px',
              maxHeight: '90vh',
              overflowY: 'auto',
              padding: '28px',
              position: 'relative'
            }}>
              <button
                onClick={() => setSelectedPair(null)}
                style={{
                  position: 'absolute',
                  top: '20px',
                  right: '20px',
                  background: 'none',
                  border: 'none',
                  color: 'var(--text-muted)',
                  cursor: 'pointer'
                }}
              >
                <X size={20} />
              </button>

              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                <span className={`badge ${getStatusBadgeClass(selectedPair.inference.evidence_status)}`}>
                  {selectedPair.inference.evidence_status}
                </span>
                <span className={`badge ${getPriorityBadgeClass(selectedPair.inference.evidence_priority)}`}>
                  {selectedPair.inference.evidence_priority}
                </span>
              </div>

              <h2 style={{ fontSize: '1.3rem', fontWeight: 700, marginBottom: '20px' }}>
                {selectedPair.drug_a.display_name} <span style={{ color: 'var(--text-dim)' }}>+</span> {selectedPair.drug_b.display_name}
              </h2>

              {/* Pair Evidence Interactive Graph View */}
              {pairGraph && (
                <div style={{ marginBottom: '24px' }}>
                  <h4 style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <Network size={14} color="#3b82f6" /> Evidence Subgraph Visualizer
                  </h4>
                  <InteractiveGraph subgraph={pairGraph} height="360px" />
                </div>
              )}

              {/* Multi-Hop Graph Paths & Reasoning Trace */}
              <div style={{ marginBottom: '24px' }}>
                <h4 style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <GitFork size={14} color="#3b82f6" /> Multi-Hop Reasoning Trace & Graph Traversal
                </h4>
                <div style={{ background: 'rgba(0,0,0,0.3)', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                  <div style={{ fontSize: '0.8rem', color: '#93c5fd', marginBottom: '6px' }}>
                    Rule Fired: <b className="mono">{selectedPair.inference.rule_fired}</b>
                  </div>
                  {selectedPair.provenance_trace.graph_paths.map((p, i) => (
                    <div key={i} className="mono" style={{ fontSize: '0.75rem', color: '#a5f3fc', padding: '2px 0' }}>
                      {p}
                    </div>
                  ))}
                  <div style={{ marginTop: '8px', borderTop: '1px solid rgba(255,255,255,0.06)', paddingTop: '8px' }}>
                    {selectedPair.provenance_trace.confidence_reasons.map((r, i) => (
                      <div key={i} style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>• {r}</div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Provenance Graph View */}
              {provenanceGraph && (
                <div style={{ marginBottom: '24px' }}>
                  <h4 style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <Share2 size={14} color="#8b5cf6" /> Auditable Decision & Dataset Provenance Trace
                  </h4>
                  <InteractiveGraph subgraph={provenanceGraph} height="280px" />
                </div>
              )}

              {/* Channel 1: DrugBank Evidence */}
              <div style={{ marginBottom: '24px' }}>
                <h4 style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '8px' }}>
                  Channel 1: DrugBank Directed DDI Assertions ({selectedPair.direct_ddi_evidence.length})
                </h4>
                {selectedPair.direct_ddi_evidence.length === 0 ? (
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>No direct DrugBank DDI assertion in current graph.</p>
                ) : (
                  selectedPair.direct_ddi_evidence.map((d, i) => (
                    <div key={i} style={{ background: 'rgba(59, 130, 246, 0.05)', border: '1px solid rgba(59, 130, 246, 0.2)', padding: '12px', borderRadius: '8px', marginBottom: '8px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: '#93c5fd', marginBottom: '4px' }}>
                        <span className="mono">{d.edge_id}</span>
                        <span className="mono">{d.direction}</span>
                      </div>
                      <p style={{ fontSize: '0.85rem' }}>{d.interaction_description}</p>
                    </div>
                  ))
                )}
              </div>

              {/* Channel 2: TWOSIDES Adverse Events */}
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                  <h4 style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-muted)' }}>
                    Channel 2: TWOSIDES Observed Combination Adverse Events ({selectedPair.combination_adverse_events.total_event_count})
                  </h4>
                  <input
                    type="text"
                    placeholder="Filter adverse events..."
                    value={searchSE}
                    onChange={e => setSearchSE(e.target.value)}
                    style={{
                      background: 'rgba(0,0,0,0.3)',
                      border: '1px solid var(--border-color)',
                      borderRadius: '6px',
                      padding: '4px 8px',
                      fontSize: '0.75rem',
                      color: '#fff'
                    }}
                  />
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '6px', maxHeight: '180px', overflowY: 'auto', background: 'rgba(0,0,0,0.2)', padding: '8px', borderRadius: '8px' }}>
                  {selectedPair.combination_adverse_events.observed_events
                    .filter(se => se.side_effect_name.toLowerCase().includes(searchSE.toLowerCase()))
                    .slice(0, 100)
                    .map((se, i) => (
                      <div key={i} style={{ fontSize: '0.75rem', padding: '4px 8px', background: 'rgba(255,255,255,0.02)', borderRadius: '4px' }}>
                        • {se.side_effect_name}
                      </div>
                    ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
