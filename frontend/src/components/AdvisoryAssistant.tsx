import React, { useState } from 'react';
import { AdvisoryResponse } from '../types/api';
import { api } from '../api/client';

export const AdvisoryAssistant: React.FC = () => {
  const [query, setQuery] = useState<string>('How should I structure an Azure AKS cluster with Azure SQL using private endpoints?');
  const [response, setResponse] = useState<AdvisoryResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const handleAsk = async () => {
    try {
      setIsLoading(true);
      const res = await api.getAdvisory(query);
      setResponse(res);
    } catch {
      // Ignored
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <div style={{ marginBottom: '1.25rem' }}>
        <h2 style={{ fontSize: '1.35rem', fontWeight: 800 }}>Editorial Design & Grammar Advisor</h2>
        <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>
          Opt-in, advisory assistance grounded strictly in verified diagram specifications and honest-data rules
        </p>
      </div>

      <div className="grid-2">
        <div className="card">
          <h3 className="card-title">Advisory Query</h3>
          <p className="card-desc">Ask design critiques, cloud containment grammar questions, or dataviz encoding rules</p>

          <div className="form-group">
            <textarea
              className="form-textarea"
              rows={5}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Enter your design or architecture query..."
            />
          </div>

          <button className="btn btn-primary" onClick={handleAsk} disabled={isLoading}>
            {isLoading ? 'Consulting Advisor...' : 'Request Advisory Critique'}
          </button>

          <div style={{ marginTop: '1.25rem', paddingTop: '0.75rem', borderTop: '1px solid var(--border-color)', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            <p><strong>Configurable Providers:</strong> OpenAI-compatible, Anthropic messages, Gemini, Ollama.</p>
            <p><strong>Offline Deterministic Core:</strong> Fully functional offline without any LLM key required.</p>
          </div>
        </div>

        <div className="card">
          <h3 className="card-title">Advisory Output</h3>
          <p className="card-desc">Grounded critique (labeled advisory, never fabricating facts)</p>

          {response ? (
            <div>
              <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.75rem' }}>
                <span className="badge badge-accent">ADVISORY ONLY</span>
                <span className="badge badge-success">PROVIDER: {response.provider.toUpperCase()}</span>
                <span className="badge badge-warning">MODEL: {response.model}</span>
              </div>

              {response.error ? (
                <div style={{ padding: '0.75rem', background: 'var(--error-tint)', color: 'var(--error)', borderRadius: '4px', fontSize: '0.825rem' }}>
                  {response.error}
                </div>
              ) : (
                <div style={{ padding: '0.75rem', background: 'var(--bg-surface)', borderRadius: '4px', fontSize: '0.825rem', lineHeight: 1.6, whiteSpace: 'pre-wrap' }}>
                  {response.content}
                </div>
              )}
            </div>
          ) : (
            <div className="empty-state">
              <p>Submit a query to view design advisor feedback.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
