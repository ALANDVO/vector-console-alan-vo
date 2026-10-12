import React, { useState, useEffect } from 'react';
import { AuditItem } from '../types/api';
import { api } from '../api/client';

export const AuditLogView: React.FC = () => {
  const [logs, setLogs] = useState<AuditItem[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [filterAction, setFilterAction] = useState<string>('');

  const loadLogs = async () => {
    try {
      setIsLoading(true);
      const items = await api.listAuditLogs(filterAction || undefined);
      setLogs(items);
    } catch {
      // Handled
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadLogs();
  }, [filterAction]);

  return (
    <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <div>
          <h2 className="card-title">Immutable Audit Trail</h2>
          <p className="card-desc">Persistent record of mutations, evaluations, and state changes</p>
        </div>

        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <select
            className="form-select"
            style={{ width: '160px', fontSize: '0.8rem' }}
            value={filterAction}
            onChange={(e) => setFilterAction(e.target.value)}
          >
            <option value="">All Actions</option>
            <option value="CREATE">CREATE</option>
            <option value="UPDATE">UPDATE</option>
            <option value="RUN_EVAL">RUN_EVAL</option>
            <option value="DELETE">DELETE</option>
          </select>
          <button className="btn btn-sm" onClick={loadLogs}>Refresh</button>
        </div>
      </div>

      {isLoading ? (
        <p style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>Loading audit trail...</p>
      ) : logs.length === 0 ? (
        <div className="empty-state">
          <p>No audit log events recorded yet.</p>
        </div>
      ) : (
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.8rem' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid var(--border-color)', textAlign: 'left', background: 'var(--bg-surface)' }}>
              <th style={{ padding: '0.5rem 0.75rem' }}>Timestamp (UTC)</th>
              <th style={{ padding: '0.5rem 0.75rem' }}>Actor</th>
              <th style={{ padding: '0.5rem 0.75rem' }}>Action</th>
              <th style={{ padding: '0.5rem 0.75rem' }}>Resource</th>
              <th style={{ padding: '0.5rem 0.75rem' }}>Details</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((log) => (
              <tr key={log.id} style={{ borderBottom: '1px solid var(--border-color)' }}>
                <td className="mono" style={{ padding: '0.5rem 0.75rem', color: 'var(--text-muted)' }}>
                  {new Date(log.timestamp).toISOString()}
                </td>
                <td style={{ padding: '0.5rem 0.75rem', fontWeight: 600 }}>{log.actor}</td>
                <td style={{ padding: '0.5rem 0.75rem' }}>
                  <span className={`badge ${log.action === 'RUN_EVAL' ? 'badge-accent' : 'badge-success'}`}>
                    {log.action}
                  </span>
                </td>
                <td className="mono" style={{ padding: '0.5rem 0.75rem' }}>
                  {log.resource_type}:{log.resource_id.slice(0, 8)}
                </td>
                <td className="mono" style={{ padding: '0.5rem 0.75rem', fontSize: '0.725rem' }}>
                  {JSON.stringify(log.details)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};
