import React, { useState } from 'react';
import { LintReport } from '../types/api';
import { api } from '../api/client';

const SAMPLES = {
  clean: `<svg viewBox="0 0 800 500" class="editorial-diagram">
  <style>text { font-family: ui-sans-serif; } .mono { font-family: ui-monospace; }</style>
  <rect x="30" y="30" width="740" height="440" rx="4" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1"/>
  <rect x="60" y="60" width="200" height="80" rx="3" fill="#ffffff" stroke="#0284c7" stroke-width="1.5"/>
  <text x="75" y="95" font-size="14" font-weight="600" fill="#0f172a">Inference Node 01</text>
  <text x="75" y="120" font-size="11" class="mono" fill="#475569">Latency: 14.2ms</text>
</svg>`,
  shadow_slop: `<svg viewBox="0 0 800 500">
  <defs>
    <filter id="slop-shadow">
      <feDropShadow dx="4" dy="4" stdDeviation="5" flood-color="black" flood-opacity="0.4"/>
    </filter>
  </defs>
  <rect filter="url(#slop-shadow)" x="50" y="50" width="300" height="150" fill="#3b82f6"/>
  <text x="70" y="100" fill="white">Mermaid Drop Shadow Slop</text>
</svg>`,
  paas_subnet_violation: `<svg viewBox="0 0 800 500">
  <rect x="20" y="20" width="760" height="460" fill="#f8fafc" stroke="#94a3b8"/>
  <rect data-azure-node="sql-prod" data-azure-service="azure_sql" data-azure-zone="subnet-app" x="50" y="50" width="160" height="60" fill="white" stroke="red"/>
  <text x="60" y="80">Azure SQL inside Subnet (Illegal)</text>
</svg>`
};

export const LinterPanel: React.FC = () => {
  const [svgInput, setSvgInput] = useState<string>(SAMPLES.clean);
  const [report, setReport] = useState<LintReport | null>(null);
  const [isLinting, setIsLinting] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string>('');

  const handleRunLint = async () => {
    try {
      setIsLinting(true);
      setErrorMsg('');
      const res = await api.lintSvg(svgInput);
      setReport(res);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Linting failed';
      setErrorMsg(msg);
    } finally {
      setIsLinting(false);
    }
  };

  const loadSample = (key: keyof typeof SAMPLES) => {
    setSvgInput(SAMPLES[key]);
    setReport(null);
  };

  return (
    <div>
      <div style={{ marginBottom: '1.25rem' }}>
        <h2 style={{ fontSize: '1.35rem', fontWeight: 800 }}>Design Linter & Structural Verification</h2>
        <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>
          Static analysis enforcing no shadows, single-accent ink ramps, monospace numbers, and Azure containment rules
        </p>
      </div>

      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem' }}>
        <button className="btn btn-sm" onClick={() => loadSample('clean')}>
          Load Clean Editorial Sample
        </button>
        <button className="btn btn-sm" onClick={() => loadSample('shadow_slop')}>
          Load Drop-Shadow Anti-Pattern
        </button>
        <button className="btn btn-sm" onClick={() => loadSample('paas_subnet_violation')}>
          Load PaaS Subnet Violation
        </button>
      </div>

      <div className="grid-2">
        <div className="card">
          <h3 className="card-title">SVG Source Input</h3>
          <p className="card-desc">Paste arbitrary SVG output from coding agents or design tools</p>

          <div className="form-group">
            <textarea
              className="form-textarea mono"
              rows={14}
              value={svgInput}
              onChange={(e) => setSvgInput(e.target.value)}
              style={{ fontSize: '0.8rem', resize: 'vertical' }}
            />
          </div>

          <button className="btn btn-primary" onClick={handleRunLint} disabled={isLinting}>
            {isLinting ? 'Analyzing...' : 'Run Static Lint Analysis'}
          </button>
          {errorMsg && <p style={{ color: 'var(--error)', marginTop: '0.5rem', fontSize: '0.8rem' }}>{errorMsg}</p>}
        </div>

        <div className="card">
          <h3 className="card-title">Linter Diagnostics Report</h3>
          <p className="card-desc">Quantitative compliance score and actionable fix instructions</p>

          {report ? (
            <div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem', padding: '0.75rem', background: report.is_compliant ? 'var(--success-tint)' : 'var(--error-tint)', borderRadius: '4px', border: `1px solid ${report.is_compliant ? 'var(--success)' : 'var(--error)'}` }}>
                <div>
                  <span style={{ fontSize: '1.25rem', fontWeight: 800, color: report.is_compliant ? 'var(--success)' : 'var(--error)' }}>
                    Score: {report.score.toFixed(1)} / 100
                  </span>
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-main)', marginTop: '0.2rem' }}>{report.summary}</p>
                </div>
                <span className={`badge ${report.is_compliant ? 'badge-success' : 'badge-error'}`}>
                  {report.is_compliant ? 'COMPLIANT' : 'VIOLATIONS'}
                </span>
              </div>

              {report.violations.length > 0 ? (
                <div>
                  <h4 style={{ fontSize: '0.85rem', fontWeight: 700, marginBottom: '0.5rem' }}>Identified Rule Defects:</h4>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                    {report.violations.map((v, idx) => (
                      <div
                        key={idx}
                        style={{
                          padding: '0.6rem 0.75rem',
                          borderRadius: '4px',
                          background: v.severity === 'error' ? 'var(--error-tint)' : 'var(--warning-tint)',
                          border: `1px solid ${v.severity === 'error' ? 'var(--error)' : 'var(--warning)'}`,
                          fontSize: '0.8rem'
                        }}
                      >
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.2rem' }}>
                          <span className="mono" style={{ fontWeight: 700, color: v.severity === 'error' ? 'var(--error)' : 'var(--warning)' }}>
                            [{v.rule_id}]
                          </span>
                          <span style={{ textTransform: 'uppercase', fontSize: '0.7rem', fontWeight: 700 }}>
                            {v.severity}
                          </span>
                        </div>
                        <p style={{ color: 'var(--text-main)' }}>{v.message}</p>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <div style={{ textAlign: 'center', padding: '2rem 1rem', color: 'var(--success)' }}>
                  <p style={{ fontWeight: 700 }}>100% Editorial Quality Verified</p>
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Clean vector edges, honest proportion encoding, and valid viewBox geometry.</p>
                </div>
              )}
            </div>
          ) : (
            <div className="empty-state">
              <p>Click "Run Static Lint Analysis" to inspect SVG rules.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
