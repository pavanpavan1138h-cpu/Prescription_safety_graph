import React from 'react';
import { Card } from '../components/common/Card';
import { BookOpen, ShieldAlert, GitBranch, Layers, ShieldCheck } from 'lucide-react';

export const AboutPage: React.FC = () => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem', maxWidth: '1000px', margin: '0 auto', width: '100%', padding: '1rem 0' }} className="animate-fade-in">
      
      {/* 1. Header */}
      <div>
        <h1 style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--text-main)', letterSpacing: '-0.02em', margin: 0 }}>
          About the Safety Intelligence Engine
        </h1>
        <p style={{ fontSize: '0.95rem', color: 'var(--text-muted)', marginTop: '0.5rem', lineHeight: '1.5' }}>
          Details regarding graph construction methodologies, evidence channels, and scientific safety guidelines.
        </p>
      </div>

      {/* 2. Knowledge Graph integration sources */}
      <Card title="Integrated Clinical Knowledge Bases" subtitle="Multi-source relational framework mapping FDA labels and surveillance database observations">
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          
          <div style={{ display: 'flex', gap: '1rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '1rem' }}>
            <div style={{ color: '#8b5cf6', flexShrink: 0 }}><BookOpen size={20} /></div>
            <div>
              <strong style={{ fontSize: '0.9rem', color: 'var(--text-main)', display: 'block', marginBottom: '0.25rem' }}>
                DrugBank Database
              </strong>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', lineHeight: '1.5', margin: 0 }}>
                Regulatory assertions for FDA-approved drug-drug interactions. Focuses on established clinical pharmacology, pharmacokinetic constraints (enzymatic inhibitors/inducers), and labeled precautions.
              </p>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '1rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '1rem' }}>
            <div style={{ color: '#06b6d4', flexShrink: 0 }}><GitBranch size={20} /></div>
            <div>
              <strong style={{ fontSize: '0.9rem', color: 'var(--text-main)', display: 'block', marginBottom: '0.25rem' }}>
                TWOSIDES Spontaneous Reports
              </strong>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', lineHeight: '1.5', margin: 0 }}>
                Observational pharmacovigilance reports tracking synergistic combination side effects that appear when multiple drugs are administered simultaneously (collating over 63k combinations).
              </p>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '1rem' }}>
            <div style={{ color: '#f59e0b', flexShrink: 0 }}><Layers size={20} /></div>
            <div>
              <strong style={{ fontSize: '0.9rem', color: 'var(--text-main)', display: 'block', marginBottom: '0.25rem' }}>
                RxNorm Identity Crosswalk
              </strong>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', lineHeight: '1.5', margin: 0 }}>
                Standardized terminology mapping RxCUIs, DrugBank IDs, generic and brand chemical synonyms to resolve identity aliases to canonical entities, collapsing duplicates.
              </p>
            </div>
          </div>

        </div>
      </Card>

      {/* 3. The Clinical Intelligence Pipeline Architecture */}
      <Card title="Clinical Intelligence Pipeline Architecture" subtitle="How data progresses from raw text to structured longitudinal change metrics">
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', fontSize: '0.8rem', color: 'var(--text-muted)', lineHeight: '1.6' }}>
          <div>
            <h4 style={{ color: 'var(--text-main)', fontWeight: 700, margin: '0 0 0.5rem 0' }}>Data Ingestion & Integration</h4>
            <ul style={{ paddingLeft: '1.25rem', display: 'flex', flexDirection: 'column', gap: '0.3rem' }}>
              <li>Raw dataset ingestion and database freezing.</li>
              <li>RxNorm semantic crosswalk identity resolution.</li>
              <li>Multi-source edge linkage and reification.</li>
              <li>Binary serialization for high-speed sub-millisecond retrieval.</li>
            </ul>
          </div>
          <div>
            <h4 style={{ color: 'var(--text-main)', fontWeight: 700, margin: '0 0 0.5rem 0' }}>Rule Engine & API Delivery</h4>
            <ul style={{ paddingLeft: '1.25rem', display: 'flex', flexDirection: 'column', gap: '0.3rem' }}>
              <li>Pairwise rule inference and categorization.</li>
              <li>Polypharmacy aggregator and narrative generation.</li>
              <li>High-concurrency REST API delivery with Interactive Cytoscape subgraphs.</li>
            </ul>
          </div>
          <div>
            <h4 style={{ color: 'var(--text-main)', fontWeight: 700, margin: '0 0 0.5rem 0' }}>Analytical Decision Support</h4>
            <ul style={{ paddingLeft: '1.25rem', display: 'flex', flexDirection: 'column', gap: '0.3rem' }}>
              <li>Complexity classification, prioritizing, and convergence analysis.</li>
              <li>Evidentiary signal grouping and toxicological reinforcement.</li>
              <li>Perturbation modeling and contextual sensitivity checks.</li>
            </ul>
          </div>
          <div>
            <h4 style={{ color: 'var(--text-main)', fontWeight: 700, margin: '0 0 0.5rem 0' }}>Traceability & Auditing</h4>
            <ul style={{ paddingLeft: '1.25rem', display: 'flex', flexDirection: 'column', gap: '0.3rem' }}>
              <li>Provenance mapping with machine-readable proof JSON exports.</li>
              <li>Computational trustworthiness validation and robustness scoring.</li>
              <li>Longitudinal evolution tracing and change-point detection.</li>
            </ul>
          </div>
        </div>
      </Card>

      {/* 4. Safety Guardrails Disclaimer Box */}
      <div style={{
        display: 'flex',
        alignItems: 'flex-start',
        gap: '1rem',
        padding: '1.5rem',
        borderRadius: '12px',
        backgroundColor: 'rgba(239, 68, 68, 0.08)',
        border: '1px solid rgba(239, 68, 68, 0.25)'
      }}>
        <ShieldAlert size={24} style={{ color: '#ef4444', flexShrink: 0, marginTop: '0.1rem' }} />
        <div>
          <h4 style={{ margin: '0 0 0.5rem 0', fontSize: '0.9rem', fontWeight: 700, color: '#fca5a5' }}>
            Clinical Safety & Governance Guardrails
          </h4>
          <p style={{ margin: 0, fontSize: '0.8rem', color: '#f87171', lineHeight: '1.5' }}>
            This platform is an evidence-grounded clinical decision support tool designed for researchers and clinical audits. It does NOT diagnose patients, prescribe medication, or replace licensed clinical judgment. The priority levels and safety indexes reflect the density and alignment of evidence within the underlying frozen database, not patient-specific clinical severity or probability of harm.
          </p>
        </div>
      </div>

    </div>
  );
};
