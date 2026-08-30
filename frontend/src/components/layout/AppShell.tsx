import React from 'react';
import { Database, Shield, Sun, Moon, Home, LayoutDashboard, Info } from 'lucide-react';
import { SystemInfoResponse } from '../../types/api';

interface AppShellProps {
  systemInfo: SystemInfoResponse | null;
  currentPage: 'home' | 'dashboard' | 'about';
  onPageChange: (page: 'home' | 'dashboard' | 'about') => void;
  isLightTheme: boolean;
  onThemeToggle: () => void;
  children: React.ReactNode;
}

export const AppShell: React.FC<AppShellProps> = ({
  systemInfo,
  currentPage,
  onPageChange,
  isLightTheme,
  onThemeToggle,
  children
}) => {
  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', backgroundColor: 'var(--bg-primary)' }}>
      {/* Top Navbar */}
      <header style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '0.75rem 2rem',
        borderBottom: '1px solid var(--border-color)',
        backgroundColor: 'var(--bg-secondary)',
        position: 'sticky',
        top: 0,
        zIndex: 50
      }}>
        
        {/* Left Side: Brand Logo and Title */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <Shield style={{ color: '#8b5cf6', width: 28, height: 28 }} />
          <div>
            <h1 style={{ margin: 0, fontSize: '1.15rem', fontWeight: 700, letterSpacing: '-0.025em', color: 'var(--text-main)' }}>
              Prescription Safety Graph Engine
            </h1>
            <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
              Entity-Resolved Multi-Drug Network Reasoning
            </span>
          </div>
        </div>

        {/* Center: SPA Page Navigation Tabs */}
        <nav style={{ display: 'flex', gap: '0.5rem' }}>
          <button
            onClick={() => onPageChange('home')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
              padding: '0.5rem 1rem',
              borderRadius: '6px',
              fontSize: '0.8rem',
              fontWeight: 600,
              cursor: 'pointer',
              border: 'none',
              backgroundColor: currentPage === 'home' ? 'var(--primary-glow)' : 'transparent',
              color: currentPage === 'home' ? 'var(--primary)' : 'var(--text-muted)'
            }}
          >
            <Home size={15} /> Home
          </button>
          
          <button
            onClick={() => onPageChange('dashboard')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
              padding: '0.5rem 1rem',
              borderRadius: '6px',
              fontSize: '0.8rem',
              fontWeight: 600,
              cursor: 'pointer',
              border: 'none',
              backgroundColor: currentPage === 'dashboard' ? 'var(--primary-glow)' : 'transparent',
              color: currentPage === 'dashboard' ? 'var(--primary)' : 'var(--text-muted)'
            }}
          >
            <LayoutDashboard size={15} /> Dashboard
          </button>

          <button
            onClick={() => onPageChange('about')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
              padding: '0.5rem 1rem',
              borderRadius: '6px',
              fontSize: '0.8rem',
              fontWeight: 600,
              cursor: 'pointer',
              border: 'none',
              backgroundColor: currentPage === 'about' ? 'var(--primary-glow)' : 'transparent',
              color: currentPage === 'about' ? 'var(--primary)' : 'var(--text-muted)'
            }}
          >
            <Info size={15} /> About
          </button>
        </nav>

        {/* Right Side: Theme Toggle & KG Status info */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
          
          {/* Light/Dark Toggle Button */}
          <button
            onClick={onThemeToggle}
            title={isLightTheme ? "Switch to Dark Mode" : "Switch to Light Mode"}
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              width: '36px',
              height: '36px',
              borderRadius: '50%',
              border: '1px solid var(--border-color)',
              backgroundColor: 'transparent',
              color: 'var(--text-main)',
              cursor: 'pointer',
              outline: 'none'
            }}
          >
            {isLightTheme ? <Moon size={18} /> : <Sun size={18} />}
          </button>

          {systemInfo && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem', fontSize: '0.75rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: 'var(--text-muted)' }}>
                <Database size={13} />
                <span>KG Version: <b style={{ color: 'var(--text-main)' }}>{systemInfo.api_version}</b></span>
              </div>
              <div style={{ color: 'var(--text-muted)' }}>
                Nodes: <b style={{ color: 'var(--text-main)' }}>{systemInfo.graph_nodes.toLocaleString()}</b>
              </div>
              <div style={{ color: 'var(--text-muted)' }}>
                Edges: <b style={{ color: 'var(--text-main)' }}>{systemInfo.graph_edges.toLocaleString()}</b>
              </div>
            </div>
          )}
        </div>
      </header>

      {/* Main Content Area */}
      <main style={{ flex: 1, padding: '1.5rem 2rem', display: 'flex', flexDirection: 'column' }}>
        {children}
      </main>
    </div>
  );
};
