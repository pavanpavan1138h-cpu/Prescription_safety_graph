import React from 'react';
import { Database, Shield } from 'lucide-react';
import { SystemInfoResponse } from '../../types/api';

interface AppShellProps {
  systemInfo: SystemInfoResponse | null;
  children: React.ReactNode;
}

export const AppShell: React.FC<AppShellProps> = ({ systemInfo, children }) => {
  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', backgroundColor: 'var(--bg-primary)' }}>
      {/* Top Navbar */}
      <header style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '1rem 2rem',
        borderBottom: '1px solid var(--border-color)',
        backgroundColor: '#0c0f1d'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <Shield style={{ color: '#8b5cf6', width: 28, height: 28 }} />
          <div>
            <h1 style={{ margin: 0, fontSize: '1.25rem', fontWeight: 700, letterSpacing: '-0.025em', color: '#fff' }}>
              Antigravity Prescription Safety Engine
            </h1>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Entity-Resolved Multi-Drug Pairwise & Network Reasoning
            </span>
          </div>
        </div>

        {systemInfo && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem', fontSize: '0.8rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-muted)' }}>
              <Database size={14} />
              <span>KG Version: <b style={{ color: '#fff' }}>{systemInfo.api_version}</b></span>
            </div>
            <div style={{ color: 'var(--text-muted)' }}>
              Nodes: <b style={{ color: '#fff' }}>{systemInfo.graph_nodes.toLocaleString()}</b>
            </div>
            <div style={{ color: 'var(--text-muted)' }}>
              Edges: <b style={{ color: '#fff' }}>{systemInfo.graph_edges.toLocaleString()}</b>
            </div>
          </div>
        )}
      </header>

      {/* Main Content Area */}
      <main style={{ flex: 1, padding: '2rem', display: 'flex', flexDirection: 'column' }}>
        {children}
      </main>
    </div>
  );
};
