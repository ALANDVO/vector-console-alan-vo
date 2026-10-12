import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { LinterPanel } from '../components/LinterPanel';

describe('LinterPanel Component', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn().mockImplementation((url: string) => {
      if (url.includes('/api/lint/svg')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({
            is_compliant: false,
            score: 75.0,
            violations: [
              { rule_id: 'no-drop-shadows', severity: 'error', message: 'Drop shadow detected' }
            ],
            editorial_stats: {},
            summary: '1 violation'
          })
        });
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
    }));
  });

  it('renders linter controls and sample buttons', () => {
    render(<LinterPanel />);
    expect(screen.getByText('Design Linter & Structural Verification')).toBeInTheDocument();
    expect(screen.getByText('Load Clean Editorial Sample')).toBeInTheDocument();
    expect(screen.getByText('Load Drop-Shadow Anti-Pattern')).toBeInTheDocument();
    expect(screen.getByText('Run Static Lint Analysis')).toBeInTheDocument();
  });

  it('runs lint analysis on user trigger and displays diagnostics', async () => {
    render(<LinterPanel />);
    const runBtn = screen.getByText('Run Static Lint Analysis');
    fireEvent.click(runBtn);

    await waitFor(() => {
      expect(screen.getByText(/Score: 75\.0/)).toBeInTheDocument();
      expect(screen.getByText('Drop shadow detected')).toBeInTheDocument();
    });
  });
});
