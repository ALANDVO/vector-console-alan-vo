import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { BenchmarkDashboard } from '../components/BenchmarkDashboard';

describe('BenchmarkDashboard Component', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn().mockImplementation((url: string) => {
      if (url.includes('/api/eval/latest')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({
            total_samples: 20,
            passed_samples: 20,
            pass_rate: 100.0,
            category_scores: {
              cloud_containment: { total: 5, passed: 5, pass_rate: 100.0, average_score: 95.0 },
              ai_ml_architectures: { total: 5, passed: 5, pass_rate: 100.0, average_score: 98.0 }
            },
            baseline_comparison: {
              baseline_pass_rate: 20.0,
              baseline_average_score: 76.8,
              common_baseline_failures: ['Drop shadow filters in 65% of samples']
            },
            executed_at: '2026-10-12T10:00:00Z'
          })
        });
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
    }));
  });

  it('renders benchmark metrics and category stats', async () => {
    render(<BenchmarkDashboard />);
    await waitFor(() => {
      expect(screen.getByText('AI/ML Coding Agent Diagram Evaluation Benchmark')).toBeInTheDocument();
      expect(screen.getAllByText('100.0%').length).toBeGreaterThanOrEqual(1);
      expect(screen.getByText('CLOUD CONTAINMENT')).toBeInTheDocument();
    });
  });
});
