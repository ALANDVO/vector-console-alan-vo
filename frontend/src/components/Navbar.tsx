import React from 'react';
import { useAuth } from '../context/AuthContext';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab }) => {
  const { user, switchRole } = useAuth();

  return (
    <header className="header-banner">
      <div className="header-inner">
        <div className="logo-section">
          <span className="logo-badge">V</span>
          <div>
            <h1 className="brand-title">Vector Console</h1>
            <p className="brand-subtitle">Editorial Diagram Synthesis & AI Evaluation · Alan Vo</p>
          </div>
        </div>

        <nav className="nav-tabs" aria-label="Main Navigation">
          <button
            className={`nav-btn ${activeTab === 'studio' ? 'active' : ''}`}
            onClick={() => setActiveTab('studio')}
          >
            Diagram Studio
          </button>
          <button
            className={`nav-btn ${activeTab === 'linter' ? 'active' : ''}`}
            onClick={() => setActiveTab('linter')}
          >
            Design Linter
          </button>
          <button
            className={`nav-btn ${activeTab === 'benchmark' ? 'active' : ''}`}
            onClick={() => setActiveTab('benchmark')}
          >
            AI Evaluation
          </button>
          <button
            className={`nav-btn ${activeTab === 'advisory' ? 'active' : ''}`}
            onClick={() => setActiveTab('advisory')}
          >
            Design Advisor
          </button>
          <button
            className={`nav-btn ${activeTab === 'audit' ? 'active' : ''}`}
            onClick={() => setActiveTab('audit')}
          >
            Audit Log
          </button>
        </nav>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          {user?.is_demo && (
            <span className="badge badge-accent">Demo Mode</span>
          )}

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Role:</span>
            <select
              className="form-select"
              style={{ padding: '0.2rem 0.5rem', fontSize: '0.75rem', width: 'auto' }}
              value={user?.role || 'analyst'}
              onChange={(e) => switchRole(e.target.value as 'viewer' | 'analyst' | 'admin')}
            >
              <option value="viewer">Viewer (Read-only)</option>
              <option value="analyst">Analyst (Editor)</option>
              <option value="admin">Admin (Full)</option>
            </select>
          </div>
        </div>
      </div>
    </header>
  );
};
