import React from 'react';
import { Shield, Sparkles, Network, RefreshCw, Layers, ArrowRight, Activity, BookOpen } from 'lucide-react';
import { Card } from '../components/common/Card';

interface HomePageProps {
  onStartAnalysis: () => void;
  systemInfo: any;
}

export const HomePage: React.FC<HomePageProps> = ({ onStartAnalysis, systemInfo }) => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2.5rem', maxWidth: '1200px', margin: '0 auto', width: '100%', padding: '1rem 0' }} className="animate-fade-in">
      
      {/* Hero Section */}
      <div style={{
        textAlign: 'center',
        padding: '3rem 2rem',
        borderRadius: '16px',
        background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(59, 130, 246, 0.05) 100%)',
        border: '1px solid var(--border-color)',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: '1rem'
      }}>
        <div style={{
          padding: '0.75rem',
          borderRadius: '50%',
          backgroundColor: 'rgba(139, 92, 246, 0.15)',
          border: '1px solid rgba(139, 92, 246, 0.3)',
          width: 'fit-content'
        }}>
          <Shield size={40} style={{ color: '#8b5cf6' }} />
        </div>
        
        <h1 style={{
          fontSize: '2.5rem',
          fontWeight: 800,
          color: 'var(--text-main)',
          letterSpacing: '-0.03em',
          margin: '0.5rem 0 0 0',
          lineHeight: '1.2'
        }}>
          Biomedical Knowledge Graph & Clinical Safety Platform
        </h1>

        <p style={{
          fontSize: '1.05rem',
          color: 'var(--text-muted)',
          maxWidth: '750px',
          lineHeight: '1.6',
          margin: 0
        }}>
          A deterministic clinical intelligence engine operating over an integrated network of <b>68k+ nodes</b> and <b>4.9M+ edges</b>. Resolution layer mapping DrugBank, TWOSIDES, and RxNorm source databases for advanced polypharmacy audit-ready evaluations.
        </p>

        <button
          onClick={onStartAnalysis}
          style={{
            marginTop: '1.5rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            padding: '0.75rem 1.75rem',
            borderRadius: '8px',
            backgroundColor: 'var(--primary)',
            color: '#fff',
            fontSize: '0.95rem',
            fontWeight: 700,
            cursor: 'pointer',
            border: 'none',
            boxShadow: '0 4px 12px var(--primary-glow)',
            transition: 'transform 0.2s ease'
          }}
        >
          Open Safety Dashboard <ArrowRight size={16} />
        </button>
      </div>

      {/* Network Scale metrics */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.5rem' }}>
        
        <Card title="Knowledge Graph Nodes" subtitle="Collapsed canonical entities count">
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginTop: '0.5rem' }}>
            <div style={{ padding: '0.5rem', borderRadius: '6px', backgroundColor: 'rgba(59, 130, 246, 0.1)' }}>
              <Network size={24} style={{ color: '#3b82f6' }} />
            </div>
            <div>
              <span style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--text-main)', display: 'block' }}>
                {systemInfo ? systemInfo.graph_nodes.toLocaleString() : '68,223'}
              </span>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Drugs, side effects, & drug pairs</span>
            </div>
          </div>
        </Card>

        <Card title="KG Linkage Edges" subtitle="DDI & observational surveillance links">
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginTop: '0.5rem' }}>
            <div style={{ padding: '0.5rem', borderRadius: '6px', backgroundColor: 'rgba(16, 185, 129, 0.1)' }}>
              <Activity size={24} style={{ color: '#10b981' }} />
            </div>
            <div>
              <span style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--text-main)', display: 'block' }}>
                {systemInfo ? systemInfo.graph_edges.toLocaleString() : '4,969,811'}
              </span>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>FDA Labels & spontaneous pharmacovigilance reports</span>
            </div>
          </div>
        </Card>

        <Card title="KG Core Integrity" subtitle="Clean resolved entities index">
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginTop: '0.5rem' }}>
            <div style={{ padding: '0.5rem', borderRadius: '6px', backgroundColor: 'rgba(245, 158, 11, 0.1)' }}>
              <BookOpen size={24} style={{ color: '#f59e0b' }} />
            </div>
            <div>
              <span style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--text-main)', display: 'block' }}>
                1,836 Canonical Drugs
              </span>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Successfully integrated across biomedical sources</span>
            </div>
          </div>
        </Card>

      </div>

      {/* Flagship Intelligence Phases Section */}
      <div>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '1.25rem', letterSpacing: '-0.02em' }}>
          Analytical Intelligence Layers
        </h2>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem' }}>
          
          <div style={{ padding: '1.5rem', borderRadius: '12px', border: '1px solid var(--border-color)', backgroundColor: 'var(--bg-secondary)', display: 'flex', gap: '1rem' }}>
            <div style={{ color: '#a855f7', marginTop: '0.2rem' }}><Shield size={20} /></div>
            <div>
              <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-main)', margin: '0 0 0.5rem 0' }}>Multi-Channel Pairwise Safety Reasoning</h3>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', lineHeight: '1.5', margin: 0 }}>
                Synthesizes regulatory safety labels and co-occurrence pharmacovigilance observations to classify pairs into explicit evidence states.
              </p>
            </div>
          </div>

          <div style={{ padding: '1.5rem', borderRadius: '12px', border: '1px solid var(--border-color)', backgroundColor: 'var(--bg-secondary)', display: 'flex', gap: '1rem' }}>
            <div style={{ color: '#3b82f6', marginTop: '0.2rem' }}><Network size={20} /></div>
            <div>
              <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-main)', margin: '0 0 0.5rem 0' }}>Structural Graph Centrality</h3>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', lineHeight: '1.5', margin: 0 }}>
                Computes topological centrality scores and cluster structures to identify the high-risk hub medications in complex prescriptions.
              </p>
            </div>
          </div>

          <div style={{ padding: '1.5rem', borderRadius: '12px', border: '1px solid var(--border-color)', backgroundColor: 'var(--bg-secondary)', display: 'flex', gap: '1rem' }}>
            <div style={{ color: '#10b981', marginTop: '0.2rem' }}><Sparkles size={20} /></div>
            <div>
              <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-main)', margin: '0 0 0.5rem 0' }}>Traceable Provenance Lineages</h3>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', lineHeight: '1.5', margin: 0 }}>
                Maps clinical conclusions directly back to execution proof-nodes. Audit-ready explainability for healthcare administrators.
              </p>
            </div>
          </div>

        </div>
      </div>

    </div>
  );
};
