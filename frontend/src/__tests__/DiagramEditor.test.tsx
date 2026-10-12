import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { DiagramEditor } from '../components/DiagramEditor';

describe('DiagramEditor Component', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn().mockImplementation((url: string) => {
      if (url.includes('/api/diagrams/compile')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({
            svg: '<svg viewBox="0 0 100 100"><text>Mock SVG</text></svg>',
            html: '<html></html>',
            lint_report: { is_compliant: true, score: 100, violations: [], editorial_stats: {}, summary: 'Pass' }
          })
        });
      }
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve([])
      });
    }));
  });

  it('renders studio controls and parameters form', async () => {
    render(<DiagramEditor />);
    expect(screen.getByText('Diagram Design & Vector Studio')).toBeInTheDocument();
    expect(screen.getByText('Diagram Type Grammar')).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByText('Save Diagram')).toBeInTheDocument();
    });
  });
});
