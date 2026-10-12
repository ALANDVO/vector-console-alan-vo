import React, { useState, useEffect } from 'react';
import { EvalSummary } from '../types/api';
import { api } from '../api/client';

export const BenchmarkDashboard: React.FC = () => {
  const [summary, setSummary] = useState<EvalSummary | null>(null);
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string>('');

  const loadLatest = async () => {
    try {
      const data = await api.getLatestBenchmark();
      setSummary(data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to fetch benchmark';
      setErrorMsg(msg);
    }
  };

  const handleRunBenchmark = async () => {
    try {
      setIsRunning(true);
      setErrorMsg('');
      const data = await api.runBenchmark();
      setSummary(data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Benchmark run error';
      setErrorMsg(msg);
    } finally {
      setIsRunning(false);
    }
  };

  useEffect(() => {
    loadLatest();
  }, []);

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
        <div>
          <h2 style={{ fontSize: '1.35rem', fontWeight: 800 }}>AI/ML Coding Agent Diagram Evaluation Benchmark</h2>
          <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>
            Empirical evaluation comparing unconstrained LLM vector synthesis against Vector Console guided grammar
          </p>
        </div>

        <button className="btn btn-primary" onClick={handleRunBenchmark} disabled={isRunning}>
          {isRunning ? 'Running 20 Evaluation Samples...' : 'Execute Benchmark Suite'}
        </button>
      </div>

      {errorMsg && (
        <div style={{ background: 'var(--error-tint)', color: 'var(--error)', padding: '0.75rem', borderRadius: '4px', marginBottom: '1rem', border: '1px solid var(--error)' }}>
          {errorMsg}
        </div>
      )}

      {summary && (
        <div>
          {/* Top Summary Metrics */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem', marginBottom: '1.25rem' }}>
            <div className="card" style={{ padding: '1rem', textAlign: 'center' }}>
              <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                Benchmark Size
              </span>
              <p className="mono" style={{ fontSize: '1.75rem', fontWeight: 800, marginTop: '0.25rem', color: 'var(--text-main)' }}>
                {summary.total_samples}
              </p>
              <span style={{ fontSize: '0.725rem', color: 'var(--text-muted)' }}>Labeled Tasks</span>
            </div>

            <div className="card" style={{ padding: '1rem', textAlign: 'center' }}>
              <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                Vector Console Pass Rate
              </span>
              <p className="mono" style={{ fontSize: '1.75rem', fontWeight: 800, marginTop: '0.25rem', color: 'var(--success)' }}>
                {summary.pass_rate.toFixed(1)}%
              </p>
              <span style={{ fontSize: '0.725rem', color: 'var(--success)' }}>{summary.passed_samples} / {summary.total_samples} Passed</span>
            </div>

            <div className="card" style={{ padding: '1rem', textAlign: 'center' }}>
              <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                Raw LLM Baseline Pass
              </span>
              <p className="mono" style={{ fontSize: '1.75rem', fontWeight: 800, marginTop: '0.25rem', color: 'var(--error)' }}>
                {summary.baseline_comparison.baseline_pass_rate.toFixed(1)}%
              </p>
              <span style={{ fontSize: '0.725rem', color: 'var(--text-muted)' }}>Unconstrained Output</span>
            </div>

            <div className="card" style={{ padding: '1rem', textAlign: 'center' }}>
              <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                Baseline Avg Score
              </span>
              <p className="mono" style={{ fontSize: '1.75rem', fontWeight: 800, marginTop: '0.25rem', color: 'var(--warning)' }}>
                {summary.baseline_comparison.baseline_average_score.toFixed(1)}
              </p>
              <span style={{ fontSize: '0.725rem', color: 'var(--text-muted)' }}>Out of 100</span>
            </div>
          </div>

          {/* Category Breakdown Table */}
          <div className="card">
            <h3 className="card-title">Category Breakdown (Empirical Results)</h3>
            <p className="card-desc">Performance across 4 core diagram domains with reproducible verification</p>

            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.825rem' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border-color)', textAlign: 'left', background: 'var(--bg-surface)' }}>
                  <th style={{ padding: '0.6rem 0.75rem' }}>Category</th>
                  <th style={{ padding: '0.6rem 0.75rem' }}>Samples</th>
                  <th style={{ padding: '0.6rem 0.75rem' }}>Passed</th>
                  <th style={{ padding: '0.6rem 0.75rem' }}>Guided Pass Rate</th>
                  <th style={{ padding: '0.6rem 0.75rem' }}>Average Quality Score</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(summary.category_scores).map(([cat, stats]) => (
                  <tr key={cat} style={{ borderBottom: '1px solid var(--border-color)' }}>
                    <td style={{ padding: '0.6rem 0.75rem', fontWeight: 600 }}>{cat.replace(/_/g, ' ').toUpperCase()}</td>
                    <td className="mono" style={{ padding: '0.6rem 0.75rem' }}>{stats.total}</td>
                    <td className="mono" style={{ padding: '0.6rem 0.75rem' }}>{stats.passed}</td>
                    <td style={{ padding: '0.6rem 0.75rem' }}>
                      <span className="badge badge-success">{stats.pass_rate.toFixed(1)}%</span>
                    </td>
                    <td className="mono" style={{ padding: '0.6rem 0.75rem' }}>{stats.average_score.toFixed(1)} / 100</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Diagnostic Failure Analysis */}
          <div className="card">
            <h3 className="card-title">Empirical Defect Analysis of Unconstrained LLM Baselines</h3>
            <p className="card-desc">Observed failure modes in raw agent generation without Vector Console grammars</p>

            <ul style={{ paddingLeft: '1.25rem', fontSize: '0.825rem', display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
              {summary.baseline_comparison.common_baseline_failures.map((f, i) => (
                <li key={i} style={{ color: 'var(--text-main)' }}>{f}</li>
              ))}
            </ul>

            <div style={{ marginTop: '1rem', paddingTop: '0.75rem', borderTop: '1px solid var(--border-color)', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              <span>Reproducible CLI execution: </span>
              <code className="mono" style={{ background: 'var(--bg-surface)', padding: '0.15rem 0.4rem', borderRadius: '3px' }}>
                PYTHONPATH=backend python3 -m app.services.eval_suite
              </code>
              <span style={{ marginLeft: '1rem' }}>Last evaluated: {summary.executed_at}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
