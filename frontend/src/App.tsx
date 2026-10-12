import React, { useState } from 'react';
import { AuthProvider } from './context/AuthContext';
import { Navbar } from './components/Navbar';
import { DiagramEditor } from './components/DiagramEditor';
import { LinterPanel } from './components/LinterPanel';
import { BenchmarkDashboard } from './components/BenchmarkDashboard';
import { AdvisoryAssistant } from './components/AdvisoryAssistant';
import { AuditLogView } from './components/AuditLogView';

export const AppContent: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>('studio');

  return (
    <div className="app-container">
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />

      <main className="main-content">
        {activeTab === 'studio' && <DiagramEditor />}
        {activeTab === 'linter' && <LinterPanel />}
        {activeTab === 'benchmark' && <BenchmarkDashboard />}
        {activeTab === 'advisory' && <AdvisoryAssistant />}
        {activeTab === 'audit' && <AuditLogView />}
      </main>

      <footer style={{ borderTop: '1px solid var(--border-color)', background: 'var(--bg-main)', padding: '1.25rem', marginTop: 'auto' }}>
        <div style={{ maxWidth: '1440px', margin: '0 auto', display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
          <span>Vector Console · Alan Vo &lt;alanvo@gmail.com&gt; · GitHub ALANDVO</span>
          <span>Editorial Diagram Design for Coding Agents & LLMs · Self-contained SVG · No shadows</span>
        </div>
      </footer>
    </div>
  );
};

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
};

export default App;
