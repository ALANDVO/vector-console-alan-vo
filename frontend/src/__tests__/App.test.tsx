import { render, screen } from '@testing-library/react';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import App from '../App';

describe('App Component', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn().mockImplementation((url: string) => {
      if (url.includes('/api/auth/me')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({
            sub: 'test-user',
            email: 'alanvo@gmail.com',
            name: 'Alan Vo',
            role: 'analyst',
            csrf_token: 'test-csrf-token',
            is_demo: true
          })
        });
      }
      if (url.includes('/api/diagrams/compile')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({
            svg: '<svg viewBox="0 0 100 100"><rect x="0" y="0" width="50" height="50"/></svg>',
            html: '<!DOCTYPE html><html></html>',
            lint_report: { is_compliant: true, score: 100, violations: [], editorial_stats: {}, summary: 'Pass' }
          })
        });
      }
      if (url.includes('/api/diagrams')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve([])
        });
      }
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({})
      });
    }));
  });

  it('renders application brand title and navigation tabs', async () => {
    render(<App />);
    expect(screen.getByText('Vector Console')).toBeInTheDocument();
    expect(screen.getByText('Diagram Studio')).toBeInTheDocument();
    expect(screen.getByText('Design Linter')).toBeInTheDocument();
    expect(screen.getByText('AI Evaluation')).toBeInTheDocument();
  });

  it('renders footer with author and email metadata', () => {
    render(<App />);
    expect(screen.getByText(/Alan Vo <alanvo@gmail\.com>/)).toBeInTheDocument();
  });
});
